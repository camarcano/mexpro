"""Routes for hitter leaderboard and detail pages."""
from flask import render_template
from flask_login import login_required
from app.hitters import bp
from app.hitters.services.hitter_stats import HitterStatsService


@bp.route('/')
@login_required
def index():
    """Hitter leaderboard page."""
    return render_template('hitters/index.html', title='Hitter Leaderboard')


@bp.route('/<int:batter_id>')
@login_required
def detail(batter_id):
    """Hitter detail page by Trackman ID."""
    # Get player info
    player = HitterStatsService.get_batter_summary(batter_id)
    if not player:
        return render_template('errors/404.html'), 404

    return render_template(
        'hitters/detail.html',
        title=player['name'],
        player=player
    )


@bp.route('/by-name/<path:batter_name>')
@login_required
def detail_by_name(batter_name):
    """Hitter detail page by name (no Trackman ID)."""
    # Get player info
    player = HitterStatsService.get_batter_summary_by_name(batter_name)
    if not player:
        return render_template('errors/404.html'), 404

    return render_template(
        'hitters/detail_by_name.html',
        title=player['name'],
        player=player,
        batter_name=batter_name
    )
