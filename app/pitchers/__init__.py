from flask import Blueprint

bp = Blueprint('pitchers', __name__, template_folder='templates')

from app.pitchers import routes  # noqa: F401, E402
