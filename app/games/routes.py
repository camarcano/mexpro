from flask import render_template
from flask_login import login_required
from app.games import bp
from app.models.game import Game


@bp.route('/')
@login_required
def index():
    games = Game.query.order_by(Game.date.desc()).all()
    return render_template('games/index.html', games=games)
