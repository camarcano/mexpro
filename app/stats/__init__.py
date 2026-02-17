from flask import Blueprint

bp = Blueprint('stats', __name__, template_folder='templates')

from app.stats import routes  # noqa: F401, E402
