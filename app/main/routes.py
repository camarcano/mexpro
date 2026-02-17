from flask import render_template
from flask_login import login_required
from app.main import bp
from app.extensions import db
from app.models.pitch import Pitch
from app.models.game import Game
from app.models.player import Player
from sqlalchemy import func, distinct


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    game_count = Game.query.count()
    pitch_count = Pitch.query.count()
    pitcher_count = db.session.query(func.count(distinct(
        func.coalesce(Pitch.pitcher_id, Pitch.pitcher)
    ))).scalar()
    batter_count = db.session.query(func.count(distinct(
        func.coalesce(Pitch.batter_id, Pitch.batter)
    ))).scalar()

    return render_template('dashboard.html',
                           game_count=game_count,
                           pitch_count=pitch_count,
                           pitcher_count=pitcher_count,
                           batter_count=batter_count)
