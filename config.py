import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mexpro-dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'mexpro.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Team defaults (overridden by TeamConfig in DB)
    DEFAULT_TEAM_CODE = os.environ.get('TEAM_CODE', 'MEX')
    DEFAULT_TEAM_NAME = os.environ.get('TEAM_NAME', 'MexPro Baseball')
    DEFAULT_PRIMARY_COLOR = os.environ.get('PRIMARY_COLOR', '#1b2a4a')
    DEFAULT_SECONDARY_COLOR = os.environ.get('SECONDARY_COLOR', '#c8a415')
    DEFAULT_ACCENT_COLOR = os.environ.get('ACCENT_COLOR', '#ffffff')

    # Season
    SEASON_YEAR = int(os.environ.get('SEASON_YEAR', '2026'))

    # Trackman CSV
    CSV_UPLOAD_FOLDER = os.path.join(basedir, 'data', 'input')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    # Reports
    REPORT_CACHE_DIR = os.path.join(basedir, 'data', 'cache')
    HEATMAP_DPI = 100
    HEATMAP_FIGSIZE = (8, 8)

    # Pagination
    ITEMS_PER_PAGE = 25


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
