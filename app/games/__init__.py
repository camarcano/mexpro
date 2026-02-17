from flask import Blueprint

bp = Blueprint('games', __name__, template_folder='templates')

from app.games import routes  # noqa: F401, E402
