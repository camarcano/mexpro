from flask import jsonify, request
from flask_login import login_required
from app.stats import bp
from app.pitchers.services.pitcher_stats import PitcherStatsService
from app.pitchers.services.pitch_profiles import get_pitch_profiles
from app.hitters.services.hitter_stats import HitterStatsService


@bp.route('/api/pitching-leaderboard')
@login_required
def pitching_leaderboard_api():
    """JSON endpoint for AG Grid pitching leaderboard."""
    filters = {
        'team': request.args.get('team'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'game_id': request.args.get('game_id'),
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v}

    data = PitcherStatsService.get_leaderboard(filters)
    columns = _pitching_leaderboard_columns()
    return jsonify({'columns': columns, 'rows': data})


@bp.route('/api/pitcher/<int:pitcher_id>/arsenal')
@login_required
def pitcher_arsenal_api(pitcher_id):
    """JSON endpoint for pitcher arsenal breakdown."""
    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    data = PitcherStatsService.get_pitcher_arsenal(pitcher_id, filters)
    columns = _arsenal_columns()
    return jsonify({'columns': columns, 'rows': data})


@bp.route('/api/pitcher/<int:pitcher_id>/usage-by-hand')
@login_required
def pitcher_usage_by_hand_api(pitcher_id):
    """Pitch usage split by batter handedness."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = PitcherStatsService.get_pitcher_usage_by_hand(pitcher_id, filters)
    return jsonify(data)


@bp.route('/api/pitcher/by-name/<path:pitcher_name>/arsenal')
@login_required
def pitcher_arsenal_by_name_api(pitcher_name):
    """JSON endpoint for pitcher arsenal by name (no Trackman ID)."""
    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    data = PitcherStatsService.get_pitcher_arsenal_by_name(pitcher_name, filters)
    columns = _arsenal_columns()
    return jsonify({'columns': columns, 'rows': data})


@bp.route('/api/pitcher/by-name/<path:pitcher_name>/usage-by-hand')
@login_required
def pitcher_usage_by_hand_by_name_api(pitcher_name):
    """Pitch usage by name split by batter handedness."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = PitcherStatsService.get_pitcher_usage_by_hand_by_name(pitcher_name, filters)
    return jsonify(data)


@bp.route('/api/pitcher/<int:pitcher_id>/pitch-profiles')
@login_required
def pitcher_pitch_profiles_api(pitcher_id):
    """Pitch movement profiles for visualization."""
    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    data = get_pitch_profiles(pitcher_id=pitcher_id, filters=filters)
    return jsonify(data)


@bp.route('/api/pitcher/by-name/<path:pitcher_name>/pitch-profiles')
@login_required
def pitcher_pitch_profiles_by_name_api(pitcher_name):
    """Pitch movement profiles by name."""
    filters = {
        'game_id': request.args.get('game_id'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    filters = {k: v for k, v in filters.items() if v}

    data = get_pitch_profiles(pitcher_name=pitcher_name, filters=filters)
    return jsonify(data)


# ── Hitter API Endpoints ──────────────────────────────────────

@bp.route('/api/hitting-leaderboard')
@login_required
def hitting_leaderboard_api():
    """JSON endpoint for AG Grid hitting leaderboard."""
    filters = {
        'team': request.args.get('team'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'game_id': request.args.get('game_id'),
    }
    filters = {k: v for k, v in filters.items() if v}

    data = HitterStatsService.get_leaderboard(filters)
    columns = _hitting_leaderboard_columns()
    return jsonify({'columns': columns, 'rows': data})


@bp.route('/api/batter/<int:batter_id>/splits')
@login_required
def batter_splits_api(batter_id):
    """Batting splits by pitcher handedness (vs LHP, vs RHP)."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = HitterStatsService.get_batter_splits(batter_id, filters)
    return jsonify(data)


@bp.route('/api/batter/by-name/<path:batter_name>/splits')
@login_required
def batter_splits_by_name_api(batter_name):
    """Batting splits by name (no Trackman ID)."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = HitterStatsService.get_batter_splits_by_name(batter_name, filters)
    return jsonify(data)


@bp.route('/api/batter/<int:batter_id>/contact-quality')
@login_required
def batter_contact_quality_api(batter_id):
    """Exit velocity and launch angle data for charts."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = HitterStatsService.get_batter_contact_quality(batter_id, filters)
    return jsonify(data)


@bp.route('/api/batter/by-name/<path:batter_name>/contact-quality')
@login_required
def batter_contact_quality_by_name_api(batter_name):
    """Contact quality data by name (no Trackman ID)."""
    filters = {'game_id': request.args.get('game_id')}
    filters = {k: v for k, v in filters.items() if v}

    data = HitterStatsService.get_batter_contact_quality_by_name(
        batter_name, filters)
    return jsonify(data)


# ── Column Definitions ────────────────────────────────────────

def _pitching_leaderboard_columns():
    return [
        {'field': 'name', 'headerName': 'Pitcher', 'pinned': 'left', 'width': 180, 'cellStyle': {'cursor': 'pointer', 'color': 'var(--team-primary)', 'fontWeight': '600'}},
        {'field': 'throws', 'headerName': 'T', 'width': 50},
        {'field': 'team', 'headerName': 'Team', 'width': 90},
        {'field': 'g', 'headerName': 'G', 'width': 55, 'type': 'numericColumn'},
        {'field': 'bf', 'headerName': 'BF', 'width': 55, 'type': 'numericColumn'},
        {'field': 'p', 'headerName': 'P', 'width': 65, 'type': 'numericColumn'},
        {'field': 'k', 'headerName': 'K', 'width': 55, 'type': 'numericColumn'},
        {'field': 'bb', 'headerName': 'BB', 'width': 55, 'type': 'numericColumn'},
        {'field': 'k_pct', 'headerName': 'K%', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'bb_pct', 'headerName': 'BB%', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'k_bb_diff', 'headerName': 'K%-BB%', 'width': 75, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'csw_pct', 'headerName': 'CSW%', 'width': 70, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'in_zone_pct', 'headerName': 'Zone%', 'width': 70, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'whiff_pct', 'headerName': 'Whiff%', 'width': 75, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'strike_pct', 'headerName': 'Strike%', 'width': 75, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'gb_pct', 'headerName': 'GB%', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'hr', 'headerName': 'HR', 'width': 55, 'type': 'numericColumn'},
        {'field': 'avg_velo', 'headerName': 'Velo', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'max_velo', 'headerName': 'MaxVelo', 'width': 75, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'avg_spin', 'headerName': 'Spin', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'fixed0'},
    ]


def _arsenal_columns():
    return [
        {'field': 'pitch_type', 'headerName': 'Pitch', 'pinned': 'left', 'width': 130},
        {'field': 'group', 'headerName': 'Group', 'width': 90},
        {'field': 'count', 'headerName': '#', 'width': 55, 'type': 'numericColumn'},
        {'field': 'pct', 'headerName': 'P%', 'width': 60, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'avg_velo', 'headerName': 'Vel', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'velo_range', 'headerName': 'Range', 'width': 80},
        {'field': 'avg_spin', 'headerName': 'Spin', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'fixed0'},
        {'field': 'avg_ivb', 'headerName': 'IVB', 'width': 60, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'avg_hb', 'headerName': 'HB', 'width': 60, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'extension', 'headerName': 'Ext', 'width': 55, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'in_zone_pct', 'headerName': 'Zone%', 'width': 70, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'whiff_pct', 'headerName': 'Whiff%', 'width': 75, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'csw_pct', 'headerName': 'CSW%', 'width': 70, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'avg_ev', 'headerName': 'EV', 'width': 60, 'type': 'numericColumn', 'valueFormatter': 'fixed1'},
    ]


def _hitting_leaderboard_columns():
    return [
        {'field': 'name', 'headerName': 'Batter', 'pinned': 'left',
         'width': 180, 'cellStyle': {'cursor': 'pointer',
         'color': 'var(--team-primary)', 'fontWeight': '600'}},
        {'field': 'bats', 'headerName': 'B', 'width': 50},
        {'field': 'team', 'headerName': 'Team', 'width': 90},
        {'field': 'g', 'headerName': 'G', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'pa', 'headerName': 'PA', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'ab', 'headerName': 'AB', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'h', 'headerName': 'H', 'width': 55,
         'type': 'numericColumn'},
        {'field': '1b', 'headerName': '1B', 'width': 55,
         'type': 'numericColumn'},
        {'field': '2b', 'headerName': '2B', 'width': 55,
         'type': 'numericColumn'},
        {'field': '3b', 'headerName': '3B', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'hr', 'headerName': 'HR', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'bb', 'headerName': 'BB', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'k', 'headerName': 'K', 'width': 55,
         'type': 'numericColumn'},
        {'field': 'avg', 'headerName': 'AVG', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'fixed3'},
        {'field': 'obp', 'headerName': 'OBP', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'fixed3'},
        {'field': 'slg', 'headerName': 'SLG', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'fixed3'},
        {'field': 'ops', 'headerName': 'OPS', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'fixed3'},
        {'field': 'iso', 'headerName': 'ISO', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'fixed3'},
        {'field': 'k_pct', 'headerName': 'K%', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'bb_pct', 'headerName': 'BB%', 'width': 65,
         'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'hard_hit_pct', 'headerName': 'HardHit%', 'width': 80,
         'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'contact_pct', 'headerName': 'Contact%', 'width': 80,
         'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'avg_ev', 'headerName': 'AvgEV', 'width': 70,
         'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'max_ev', 'headerName': 'MaxEV', 'width': 70,
         'type': 'numericColumn', 'valueFormatter': 'fixed1'},
        {'field': 'avg_la', 'headerName': 'AvgLA', 'width': 70,
         'type': 'numericColumn', 'valueFormatter': 'fixed1'},
    ]
