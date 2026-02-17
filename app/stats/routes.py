from flask import jsonify, request
from flask_login import login_required
from app.stats import bp
from app.pitchers.services.pitcher_stats import PitcherStatsService


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


def _pitching_leaderboard_columns():
    return [
        {'field': 'name', 'headerName': 'Pitcher', 'pinned': 'left', 'width': 180},
        {'field': 'throws', 'headerName': 'T', 'width': 50},
        {'field': 'team', 'headerName': 'Team', 'width': 90},
        {'field': 'g', 'headerName': 'G', 'width': 55, 'type': 'numericColumn'},
        {'field': 'bf', 'headerName': 'BF', 'width': 55, 'type': 'numericColumn'},
        {'field': 'p', 'headerName': 'P', 'width': 65, 'type': 'numericColumn'},
        {'field': 'k', 'headerName': 'K', 'width': 55, 'type': 'numericColumn'},
        {'field': 'bb', 'headerName': 'BB', 'width': 55, 'type': 'numericColumn'},
        {'field': 'k_pct', 'headerName': 'K%', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
        {'field': 'bb_pct', 'headerName': 'BB%', 'width': 65, 'type': 'numericColumn', 'valueFormatter': 'pct1'},
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
