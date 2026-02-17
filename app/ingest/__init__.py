from flask import Blueprint

bp = Blueprint('ingest', __name__, template_folder='templates')

from app.ingest import routes  # noqa: F401, E402
