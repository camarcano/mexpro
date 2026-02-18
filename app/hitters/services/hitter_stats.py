"""Aggregate pitch-level data into batting statistics."""

from sqlalchemy import func, case, distinct
from app.extensions import db
from app.models.pitch import Pitch
from app.utils.baseball_metrics import (
    calculate_batting_average, calculate_obp, calculate_slg, calculate_ops,
    calculate_iso, calculate_hard_hit_pct, calculate_contact_pct, pct
)


def _effective_batter_key():
    """SQL expression: coalesce batter_id with batter name for batters
    that have no Trackman ID."""
    return func.coalesce(Pitch.batter_id, Pitch.batter)


class HitterStatsService:

    @staticmethod
    def get_leaderboard(filters=None):
        """Return hitter leaderboard data for AG Grid.

        Each row = one batter with aggregated stats.
        Groups by coalesce(batter_id, batter_name) so batters with
        null batter_id still appear.
        """
        filters = filters or {}

        batter_key = _effective_batter_key()

        # Base query: group by batter key
        q = db.session.query(
            Pitch.batter_id,
            Pitch.batter,
            Pitch.batter_side,
            Pitch.batter_team,
            func.count(distinct(Pitch.game_id)).label('games'),
            # PA = completed plate appearances
            func.sum(case((
                (Pitch.play_result.isnot(None)) &
                (Pitch.play_result != 'Undefined') |
                (Pitch.k_or_bb.isnot(None)) &
                (Pitch.k_or_bb != 'Undefined'),
                1
            ), else_=0)).label('pa'),
            # Walks, HBP, SF for AB calculation
            func.sum(case((Pitch.k_or_bb == 'Walk', 1),
                          else_=0)).label('bb'),
            func.sum(case((Pitch.play_result == 'HitByPitch', 1),
                          else_=0)).label('hbp'),
            func.sum(case((Pitch.play_result == 'Sacrifice', 1),
                          else_=0)).label('sf'),
            # Hits by type
            func.sum(case((Pitch.play_result == 'Single', 1),
                          else_=0)).label('singles'),
            func.sum(case((Pitch.play_result == 'Double', 1),
                          else_=0)).label('doubles'),
            func.sum(case((Pitch.play_result == 'Triple', 1),
                          else_=0)).label('triples'),
            func.sum(case((Pitch.play_result == 'HomeRun', 1),
                          else_=0)).label('hr'),
            # Strikeouts
            func.sum(case((Pitch.k_or_bb == 'Strikeout', 1),
                          else_=0)).label('k'),
            # Contact quality
            func.avg(case((Pitch.exit_speed.isnot(None), Pitch.exit_speed))
                     ).label('avg_ev'),
            func.max(Pitch.exit_speed).label('max_ev'),
            func.avg(case((Pitch.angle.isnot(None), Pitch.angle))
                     ).label('avg_la'),
            func.sum(case((Pitch.exit_speed >= 95, 1),
                          else_=0)).label('hard_hits'),
            func.sum(case((Pitch.pitch_call == 'InPlay', 1),
                          else_=0)).label('bip'),
            # Swing metrics
            func.sum(case((Pitch.pitch_call.in_([
                'StrikeSwinging', 'FoulBall', 'FoulBallNotFieldable',
                'FoulBallFieldable', 'InPlay', 'FoulTip'
            ]), 1), else_=0)).label('swings'),
            func.sum(case((Pitch.pitch_call == 'StrikeSwinging', 1),
                          else_=0)).label('whiffs'),
        ).group_by(batter_key, Pitch.batter,
                   Pitch.batter_side, Pitch.batter_team)

        # Apply filters
        if filters.get('team'):
            q = q.filter(Pitch.batter_team == filters['team'])
        if filters.get('start_date'):
            q = q.filter(Pitch.date >= filters['start_date'])
        if filters.get('end_date'):
            q = q.filter(Pitch.date <= filters['end_date'])
        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()
        result = []

        for row in rows:
            ab = row.pa - row.bb - row.hbp - row.sf
            h = row.singles + row.doubles + row.triples + row.hr
            tb = (row.singles + (2 * row.doubles) +
                  (3 * row.triples) + (4 * row.hr))

            avg = calculate_batting_average(h, ab)
            obp = calculate_obp(h, row.bb, row.hbp, ab, row.sf)
            slg = calculate_slg(tb, ab)
            ops_val = calculate_ops(obp, slg)

            result.append({
                'batter_id': row.batter_id,
                'name': row.batter,
                'bats': row.batter_side,
                'team': row.batter_team,
                'g': row.games,
                'pa': row.pa,
                'ab': ab,
                'h': h,
                '1b': row.singles,
                '2b': row.doubles,
                '3b': row.triples,
                'hr': row.hr,
                'bb': row.bb,
                'k': row.k,
                'avg': avg,
                'obp': obp,
                'slg': slg,
                'ops': ops_val,
                'iso': calculate_iso(slg, avg),
                'k_pct': pct(row.k, row.pa),
                'bb_pct': pct(row.bb, row.pa),
                'hard_hit_pct': calculate_hard_hit_pct(
                    row.hard_hits, row.bip),
                'contact_pct': calculate_contact_pct(row.swings, row.whiffs),
                'avg_ev': round(row.avg_ev, 1) if row.avg_ev else None,
                'max_ev': round(row.max_ev, 1) if row.max_ev else None,
                'avg_la': round(row.avg_la, 1) if row.avg_la else None,
            })

        # Filter out batters with < 1 PA
        result = [r for r in result if r['pa'] >= 1]
        return result

    @staticmethod
    def get_batter_summary(batter_id):
        """Get basic summary info for a batter by ID."""
        # Query for player info from most recent pitch
        row = db.session.query(
            Pitch.batter_id,
            Pitch.batter,
            Pitch.batter_side,
            Pitch.batter_team,
            func.count(distinct(Pitch.game_id)).label('games'),
            func.count(Pitch.id).label('pitch_count'),
        ).filter(
            Pitch.batter_id == batter_id
        ).group_by(
            Pitch.batter_id,
            Pitch.batter,
            Pitch.batter_side,
            Pitch.batter_team
        ).first()

        if not row:
            return None

        return {
            'trackman_id': row.batter_id,
            'name': row.batter,
            'bats': row.batter_side,
            'team': row.batter_team,
            'game_count': row.games,
            'pitch_count': row.pitch_count,
        }

    @staticmethod
    def get_batter_summary_by_name(batter_name):
        """Get basic summary info for a batter by name (no Trackman ID)."""
        row = db.session.query(
            Pitch.batter,
            Pitch.batter_side,
            Pitch.batter_team,
            func.count(distinct(Pitch.game_id)).label('games'),
            func.count(Pitch.id).label('pitch_count'),
        ).filter(
            Pitch.batter == batter_name,
            Pitch.batter_id.is_(None)
        ).group_by(
            Pitch.batter,
            Pitch.batter_side,
            Pitch.batter_team
        ).first()

        if not row:
            return None

        return {
            'name': row.batter,
            'bats': row.batter_side,
            'team': row.batter_team,
            'game_count': row.games,
            'pitch_count': row.pitch_count,
        }

    @staticmethod
    def get_batter_splits(batter_id, filters=None):
        """Get batting stats split by pitcher handedness (vs LHP, vs RHP)."""
        filters = filters or {}

        splits = {}
        for hand in ['Left', 'Right']:
            q = db.session.query(
                func.sum(case((
                    (Pitch.play_result.isnot(None)) &
                    (Pitch.play_result != 'Undefined') |
                    (Pitch.k_or_bb.isnot(None)) &
                    (Pitch.k_or_bb != 'Undefined'),
                    1
                ), else_=0)).label('pa'),
                func.sum(case((Pitch.k_or_bb == 'Walk', 1),
                              else_=0)).label('bb'),
                func.sum(case((Pitch.play_result == 'HitByPitch', 1),
                              else_=0)).label('hbp'),
                func.sum(case((Pitch.play_result == 'Sacrifice', 1),
                              else_=0)).label('sf'),
                func.sum(case((Pitch.play_result == 'Single', 1),
                              else_=0)).label('singles'),
                func.sum(case((Pitch.play_result == 'Double', 1),
                              else_=0)).label('doubles'),
                func.sum(case((Pitch.play_result == 'Triple', 1),
                              else_=0)).label('triples'),
                func.sum(case((Pitch.play_result == 'HomeRun', 1),
                              else_=0)).label('hr'),
                func.sum(case((Pitch.k_or_bb == 'Strikeout', 1),
                              else_=0)).label('k'),
                func.avg(case((Pitch.exit_speed.isnot(None),
                               Pitch.exit_speed))).label('avg_ev'),
            ).filter(
                Pitch.batter_id == batter_id,
                Pitch.pitcher_throws == hand
            )

            if filters.get('game_id'):
                q = q.filter(Pitch.game_id == filters['game_id'])

            row = q.first()
            if row and row.pa:
                ab = row.pa - row.bb - row.hbp - row.sf
                h = row.singles + row.doubles + row.triples + row.hr
                tb = (row.singles + (2 * row.doubles) +
                      (3 * row.triples) + (4 * row.hr))

                avg = calculate_batting_average(h, ab)
                obp = calculate_obp(h, row.bb, row.hbp, ab, row.sf)
                slg = calculate_slg(tb, ab)

                splits[hand] = {
                    'pa': row.pa,
                    'ab': ab,
                    'h': h,
                    'hr': row.hr,
                    'bb': row.bb,
                    'k': row.k,
                    'avg': avg,
                    'obp': obp,
                    'slg': slg,
                    'ops': calculate_ops(obp, slg),
                    'avg_ev': round(row.avg_ev, 1) if row.avg_ev else None,
                }

        return {'vs_lhp': splits.get('Left'), 'vs_rhp': splits.get('Right')}

    @staticmethod
    def get_batter_splits_by_name(batter_name, filters=None):
        """Get batting splits for name-identified batter."""
        filters = filters or {}

        splits = {}
        for hand in ['Left', 'Right']:
            q = db.session.query(
                func.sum(case((
                    (Pitch.play_result.isnot(None)) &
                    (Pitch.play_result != 'Undefined') |
                    (Pitch.k_or_bb.isnot(None)) &
                    (Pitch.k_or_bb != 'Undefined'),
                    1
                ), else_=0)).label('pa'),
                func.sum(case((Pitch.k_or_bb == 'Walk', 1),
                              else_=0)).label('bb'),
                func.sum(case((Pitch.play_result == 'HitByPitch', 1),
                              else_=0)).label('hbp'),
                func.sum(case((Pitch.play_result == 'Sacrifice', 1),
                              else_=0)).label('sf'),
                func.sum(case((Pitch.play_result == 'Single', 1),
                              else_=0)).label('singles'),
                func.sum(case((Pitch.play_result == 'Double', 1),
                              else_=0)).label('doubles'),
                func.sum(case((Pitch.play_result == 'Triple', 1),
                              else_=0)).label('triples'),
                func.sum(case((Pitch.play_result == 'HomeRun', 1),
                              else_=0)).label('hr'),
                func.sum(case((Pitch.k_or_bb == 'Strikeout', 1),
                              else_=0)).label('k'),
                func.avg(case((Pitch.exit_speed.isnot(None),
                               Pitch.exit_speed))).label('avg_ev'),
            ).filter(
                Pitch.batter == batter_name,
                Pitch.batter_id.is_(None),
                Pitch.pitcher_throws == hand
            )

            if filters.get('game_id'):
                q = q.filter(Pitch.game_id == filters['game_id'])

            row = q.first()
            if row and row.pa:
                ab = row.pa - row.bb - row.hbp - row.sf
                h = row.singles + row.doubles + row.triples + row.hr
                tb = (row.singles + (2 * row.doubles) +
                      (3 * row.triples) + (4 * row.hr))

                avg = calculate_batting_average(h, ab)
                obp = calculate_obp(h, row.bb, row.hbp, ab, row.sf)
                slg = calculate_slg(tb, ab)

                splits[hand] = {
                    'pa': row.pa,
                    'ab': ab,
                    'h': h,
                    'hr': row.hr,
                    'bb': row.bb,
                    'k': row.k,
                    'avg': avg,
                    'obp': obp,
                    'slg': slg,
                    'ops': calculate_ops(obp, slg),
                    'avg_ev': round(row.avg_ev, 1) if row.avg_ev else None,
                }

        return {'vs_lhp': splits.get('Left'), 'vs_rhp': splits.get('Right')}

    @staticmethod
    def get_batter_contact_quality(batter_id, filters=None):
        """Get exit velocity and launch angle data for charts."""
        filters = filters or {}

        q = db.session.query(
            Pitch.exit_speed,
            Pitch.angle,
            Pitch.play_result,
            Pitch.tagged_hit_type,
        ).filter(
            Pitch.batter_id == batter_id,
            Pitch.exit_speed.isnot(None),
            Pitch.angle.isnot(None)
        )

        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()

        return [{
            'exit_speed': row.exit_speed,
            'launch_angle': row.angle,
            'result': row.play_result,
            'hit_type': row.tagged_hit_type,
        } for row in rows]

    @staticmethod
    def get_batter_contact_quality_by_name(batter_name, filters=None):
        """Get contact quality data for name-identified batter."""
        filters = filters or {}

        q = db.session.query(
            Pitch.exit_speed,
            Pitch.angle,
            Pitch.play_result,
            Pitch.tagged_hit_type,
        ).filter(
            Pitch.batter == batter_name,
            Pitch.batter_id.is_(None),
            Pitch.exit_speed.isnot(None),
            Pitch.angle.isnot(None)
        )

        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()

        return [{
            'exit_speed': row.exit_speed,
            'launch_angle': row.angle,
            'result': row.play_result,
            'hit_type': row.tagged_hit_type,
        } for row in rows]
