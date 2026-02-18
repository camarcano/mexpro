from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager, csrf
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure required directories exist
    os.makedirs(app.config.get('CSV_UPLOAD_FOLDER', 'data/input'), exist_ok=True)
    os.makedirs(app.config.get('REPORT_CACHE_DIR', 'data/cache'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models so they are registered with SQLAlchemy
    from app.models import user, player, team, game, pitch, upload_log  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return user.User.query.get(int(user_id))

    # Team branding context processor
    @app.context_processor
    def inject_team_config():
        from app.utils.team_config import get_team_config
        return dict(team_config=get_team_config())

    # Make sessions permanent
    @app.before_request
    def make_session_permanent():
        from flask import session
        session.permanent = True

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.ingest import bp as ingest_bp
    app.register_blueprint(ingest_bp, url_prefix='/ingest')

    from app.pitchers import bp as pitchers_bp
    app.register_blueprint(pitchers_bp, url_prefix='/pitchers')

    from app.hitters import bp as hitters_bp
    app.register_blueprint(hitters_bp, url_prefix='/hitters')

    from app.stats import bp as stats_bp
    app.register_blueprint(stats_bp, url_prefix='/stats')

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from app.games import bp as games_bp
    app.register_blueprint(games_bp, url_prefix='/games')

    return app
