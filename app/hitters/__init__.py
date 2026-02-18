"""Hitters blueprint for batting stats and analysis."""
from flask import Blueprint

bp = Blueprint('hitters', __name__)

from app.hitters import routes  # noqa: E402,F401
