from flask import render_template, abort
from flask_login import login_required
from app.pitchers import bp
from app.models.player import Player
from app.models.pitch import Pitch
from app.extensions import db
from sqlalchemy import func


@bp.route('/')
@login_required
def index():
    return render_template('pitchers/index.html')


@bp.route('/<int:pitcher_id>')
@login_required
def detail(pitcher_id):
    player = Player.query.filter_by(trackman_id=pitcher_id).first_or_404()

    pitch_count = Pitch.query.filter_by(pitcher_id=pitcher_id).count()
    games = db.session.query(func.count(func.distinct(Pitch.game_id))).filter(
        Pitch.pitcher_id == pitcher_id
    ).scalar()

    return render_template('pitchers/detail.html',
                           player=player,
                           pitch_count=pitch_count,
                           game_count=games)


@bp.route('/by-name/<path:pitcher_name>')
@login_required
def detail_by_name(pitcher_name):
    """Detail page for pitchers identified by name (no Trackman ID)."""
    # Find pitch data by pitcher name where pitcher_id is null
    pitch_count = Pitch.query.filter(
        Pitch.pitcher == pitcher_name,
        Pitch.pitcher_id.is_(None),
    ).count()
    if pitch_count == 0:
        abort(404)

    first_pitch = Pitch.query.filter(
        Pitch.pitcher == pitcher_name,
        Pitch.pitcher_id.is_(None),
    ).first()

    games = db.session.query(func.count(func.distinct(Pitch.game_id))).filter(
        Pitch.pitcher == pitcher_name,
        Pitch.pitcher_id.is_(None),
    ).scalar()

    # Build a pseudo-player object
    player = type('Player', (), {
        'trackman_id': None,
        'name': pitcher_name,
        'throws': first_pitch.pitcher_throws if first_pitch else None,
        'team': first_pitch.pitcher_team if first_pitch else None,
    })()

    return render_template('pitchers/detail_by_name.html',
                           player=player,
                           pitcher_name=pitcher_name,
                           pitch_count=pitch_count,
                           game_count=games)
