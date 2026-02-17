"""Aggregate pitch-level data into pitcher statistics."""

from sqlalchemy import func, case, distinct, and_
from app.extensions import db
from app.models.pitch import Pitch
from app.pitchers.services.pitch_metrics import (
    is_in_zone, ZONE_LEFT, ZONE_RIGHT, ZONE_BOTTOM, ZONE_TOP,
    PITCH_TYPE_GROUPS, get_pitch_group,
)
from app.utils.baseball_metrics import pct, rate


def _effective_pitch_type():
    """SQL expression: prefer tagged_pitch_type, fall back to auto_pitch_type."""
    return case(
        (and_(
            Pitch.tagged_pitch_type.isnot(None),
            Pitch.tagged_pitch_type != 'Undefined',
        ), Pitch.tagged_pitch_type),
        else_=Pitch.auto_pitch_type,
    )


def _effective_pitcher_key():
    """SQL expression: coalesce pitcher_id with a hash of pitcher name for
    pitchers that have no Trackman ID."""
    return func.coalesce(Pitch.pitcher_id, Pitch.pitcher)


class PitcherStatsService:

    @staticmethod
    def get_leaderboard(filters=None):
        """Return pitcher leaderboard data for AG Grid.

        Each row = one pitcher with aggregated stats.
        Groups by coalesce(pitcher_id, pitcher_name) so pitchers with
        null pitcher_id still appear.
        """
        filters = filters or {}

        pitcher_key = _effective_pitcher_key()

        # Base query: group by pitcher key
        q = db.session.query(
            Pitch.pitcher_id,
            Pitch.pitcher,
            Pitch.pitcher_throws,
            Pitch.pitcher_team,
            func.count(Pitch.id).label('total_pitches'),
            func.count(distinct(Pitch.game_id)).label('games'),
            # Batters faced (unique PA within same game/inning/PA)
            func.count(distinct(
                Pitch.pa_of_inning
            )).label('pa_raw'),
            # Strikeouts (K)
            func.sum(case((Pitch.k_or_bb == 'Strikeout', 1), else_=0)).label('strikeouts'),
            # Walks (BB)
            func.sum(case((Pitch.k_or_bb == 'Walk', 1), else_=0)).label('walks'),
            # Balls in play
            func.sum(case((Pitch.pitch_call == 'InPlay', 1), else_=0)).label('bip'),
            # Called strikes
            func.sum(case((Pitch.pitch_call == 'StrikeCalled', 1), else_=0)).label('called_strikes'),
            # Swinging strikes
            func.sum(case((Pitch.pitch_call == 'StrikeSwinging', 1), else_=0)).label('swinging_strikes'),
            # Fouls
            func.sum(case((Pitch.pitch_call.in_(['FoulBall', 'FoulBallNotFieldable', 'FoulBallFieldable', 'FoulTip']), 1), else_=0)).label('fouls'),
            # Swings (all types)
            func.sum(case((Pitch.pitch_call.in_([
                'StrikeSwinging', 'FoulBall', 'FoulBallNotFieldable',
                'FoulBallFieldable', 'InPlay', 'FoulTip'
            ]), 1), else_=0)).label('swings'),
            # In zone pitches
            func.sum(case((and_(
                Pitch.plate_loc_side.between(ZONE_LEFT, ZONE_RIGHT),
                Pitch.plate_loc_height.between(ZONE_BOTTOM, ZONE_TOP),
            ), 1), else_=0)).label('in_zone'),
            # Pitches with valid location
            func.sum(case((and_(
                Pitch.plate_loc_side.isnot(None),
                Pitch.plate_loc_height.isnot(None),
            ), 1), else_=0)).label('with_location'),
            # Ground balls
            func.sum(case((Pitch.tagged_hit_type == 'GroundBall', 1), else_=0)).label('ground_balls'),
            # Fly balls
            func.sum(case((Pitch.tagged_hit_type == 'FlyBall', 1), else_=0)).label('fly_balls'),
            # Line drives
            func.sum(case((Pitch.tagged_hit_type == 'LineDrive', 1), else_=0)).label('line_drives'),
            # Home runs
            func.sum(case((Pitch.play_result == 'HomeRun', 1), else_=0)).label('home_runs'),
            # Avg velocity
            func.avg(case((Pitch.rel_speed.isnot(None), Pitch.rel_speed))).label('avg_velo'),
            # Max velocity
            func.max(Pitch.rel_speed).label('max_velo'),
            # Avg spin rate
            func.avg(case((Pitch.spin_rate.isnot(None), Pitch.spin_rate))).label('avg_spin'),
        ).group_by(pitcher_key, Pitch.pitcher, Pitch.pitcher_throws, Pitch.pitcher_team)

        # Apply filters
        if filters.get('team'):
            q = q.filter(Pitch.pitcher_team == filters['team'])
        if filters.get('start_date'):
            q = q.filter(Pitch.date >= filters['start_date'])
        if filters.get('end_date'):
            q = q.filter(Pitch.date <= filters['end_date'])
        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()
        result = []

        for row in rows:
            total = row.total_pitches
            swings = row.swings or 0
            bip = row.bip or 0
            in_zone = row.in_zone or 0
            with_loc = row.with_location or 0
            csw = (row.called_strikes or 0) + (row.swinging_strikes or 0)

            # BF: count distinct plate appearances via last-pitch-of-PA
            # pa_raw from distinct pa_of_inning is a rough proxy;
            # more accurate: count pitches where at_bat_result or play_result is set
            bf = row.pa_raw or 0

            result.append({
                'pitcher_id': row.pitcher_id,
                'name': row.pitcher,
                'throws': row.pitcher_throws,
                'team': row.pitcher_team,
                'g': row.games,
                'bf': bf,
                'p': total,
                'k': row.strikeouts,
                'bb': row.walks,
                'k_pct': pct(row.strikeouts, total),
                'bb_pct': pct(row.walks, total),
                'csw_pct': pct(csw, total),
                'in_zone_pct': pct(in_zone, with_loc),
                'whiff_pct': pct(row.swinging_strikes, swings),
                'chase_pct': None,  # Requires separate subquery
                'gb_pct': pct(row.ground_balls, bip) if bip else None,
                'fb_pct': pct(row.fly_balls, bip) if bip else None,
                'hr': row.home_runs,
                'avg_velo': round(row.avg_velo, 1) if row.avg_velo else None,
                'max_velo': round(row.max_velo, 1) if row.max_velo else None,
                'avg_spin': round(row.avg_spin, 0) if row.avg_spin else None,
                'strike_pct': pct(csw + (row.fouls or 0) + bip, total),
            })

        return result

    @staticmethod
    def get_pitcher_arsenal(pitcher_id, filters=None):
        """Per-pitch-type breakdown for a specific pitcher."""
        return PitcherStatsService._get_arsenal(
            PitcherStatsService._build_pitcher_filter(pitcher_id=pitcher_id), filters)

    @staticmethod
    def _build_pitcher_filter(pitcher_id=None, pitcher_name=None):
        """Return a list of SQLAlchemy filter clauses for identifying a pitcher."""
        if pitcher_id is not None:
            return [Pitch.pitcher_id == pitcher_id]
        return [Pitch.pitcher == pitcher_name, Pitch.pitcher_id.is_(None)]

    @staticmethod
    def get_pitcher_usage_by_hand(pitcher_id, filters=None):
        """Pitch usage % split by batter hand (LHH vs RHH)."""
        return PitcherStatsService._get_usage_by_hand(
            PitcherStatsService._build_pitcher_filter(pitcher_id=pitcher_id), filters)

    @staticmethod
    def get_pitcher_usage_by_hand_by_name(pitcher_name, filters=None):
        """Pitch usage % by batter hand for name-identified pitcher."""
        return PitcherStatsService._get_usage_by_hand(
            PitcherStatsService._build_pitcher_filter(pitcher_name=pitcher_name), filters)

    @staticmethod
    def get_pitcher_arsenal_by_name(pitcher_name, filters=None):
        """Arsenal breakdown for a pitcher identified by name."""
        return PitcherStatsService._get_arsenal(
            PitcherStatsService._build_pitcher_filter(pitcher_name=pitcher_name), filters)

    @staticmethod
    def _get_usage_by_hand(pitcher_filters, filters=None):
        """Pitch usage % split by batter hand (LHH vs RHH).

        Uses effective pitch type for grouping.
        """
        filters = filters or {}

        ept = _effective_pitch_type()

        q = db.session.query(
            Pitch.batter_side,
            ept.label('pitch_type'),
            func.count(Pitch.id).label('count'),
        ).filter(
            *pitcher_filters,
            ept.isnot(None),
            ept != 'Undefined',
            Pitch.batter_side.isnot(None),
        ).group_by(Pitch.batter_side, ept)

        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()

        usage = {'Left': {}, 'Right': {}}
        totals = {'Left': 0, 'Right': 0}

        for row in rows:
            side = row.batter_side
            if side in usage:
                usage[side][row.pitch_type] = row.count
                totals[side] += row.count

        result = {}
        for side in ['Left', 'Right']:
            result[side] = []
            for pt, count in sorted(usage[side].items(), key=lambda x: -x[1]):
                result[side].append({
                    'pitch_type': pt,
                    'count': count,
                    'pct': pct(count, totals[side]),
                })

        return result

    @staticmethod
    def _get_arsenal(pitcher_filters, filters=None):
        """Per-pitch-type breakdown using effective pitch type."""
        filters = filters or {}

        ept = _effective_pitch_type()

        q = db.session.query(
            ept.label('pitch_type'),
            func.count(Pitch.id).label('count'),
            func.avg(Pitch.rel_speed).label('avg_velo'),
            func.min(Pitch.rel_speed).label('min_velo'),
            func.max(Pitch.rel_speed).label('max_velo'),
            func.avg(Pitch.spin_rate).label('avg_spin'),
            func.avg(Pitch.induced_vert_break).label('avg_ivb'),
            func.avg(Pitch.horz_break).label('avg_hb'),
            func.avg(Pitch.extension).label('avg_extension'),
            func.avg(Pitch.rel_height).label('avg_rel_height'),
            func.sum(case((and_(
                Pitch.plate_loc_side.between(ZONE_LEFT, ZONE_RIGHT),
                Pitch.plate_loc_height.between(ZONE_BOTTOM, ZONE_TOP),
            ), 1), else_=0)).label('in_zone'),
            func.sum(case((and_(
                Pitch.plate_loc_side.isnot(None),
                Pitch.plate_loc_height.isnot(None),
            ), 1), else_=0)).label('with_location'),
            func.sum(case((Pitch.pitch_call.in_([
                'StrikeSwinging', 'FoulBall', 'FoulBallNotFieldable',
                'FoulBallFieldable', 'InPlay', 'FoulTip'
            ]), 1), else_=0)).label('swings'),
            func.sum(case((Pitch.pitch_call == 'StrikeSwinging', 1), else_=0)).label('whiffs'),
            func.sum(case((Pitch.pitch_call.in_(['StrikeCalled', 'StrikeSwinging']), 1), else_=0)).label('csw'),
            func.sum(case((Pitch.pitch_call == 'InPlay', 1), else_=0)).label('bip'),
            func.avg(case((Pitch.pitch_call == 'InPlay', Pitch.exit_speed))).label('avg_ev'),
        ).filter(
            *pitcher_filters,
            ept.isnot(None),
            ept != 'Undefined',
        ).group_by(ept)

        if filters.get('start_date'):
            q = q.filter(Pitch.date >= filters['start_date'])
        if filters.get('end_date'):
            q = q.filter(Pitch.date <= filters['end_date'])
        if filters.get('game_id'):
            q = q.filter(Pitch.game_id == filters['game_id'])

        rows = q.all()
        total_pitches = sum(r.count for r in rows)

        result = []
        for row in rows:
            result.append({
                'pitch_type': row.pitch_type,
                'group': get_pitch_group(row.pitch_type),
                'count': row.count,
                'pct': pct(row.count, total_pitches),
                'avg_velo': round(row.avg_velo, 1) if row.avg_velo else None,
                'velo_range': f"{round(row.min_velo, 0):.0f}-{round(row.max_velo, 0):.0f}" if row.min_velo and row.max_velo else None,
                'avg_spin': round(row.avg_spin, 0) if row.avg_spin else None,
                'avg_ivb': round(row.avg_ivb, 1) if row.avg_ivb else None,
                'avg_hb': round(row.avg_hb, 1) if row.avg_hb else None,
                'extension': round(row.avg_extension, 1) if row.avg_extension else None,
                'rel_height': round(row.avg_rel_height, 1) if row.avg_rel_height else None,
                'in_zone_pct': pct(row.in_zone, row.with_location),
                'whiff_pct': pct(row.whiffs, row.swings),
                'csw_pct': pct(row.csw, row.count),
                'avg_ev': round(row.avg_ev, 1) if row.avg_ev else None,
            })

        result.sort(key=lambda x: x['count'], reverse=True)
        return result
