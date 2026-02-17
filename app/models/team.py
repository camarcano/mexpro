from datetime import datetime, timezone
from app.extensions import db


class TeamConfig(db.Model):
    __tablename__ = 'team_config'

    id = db.Column(db.Integer, primary_key=True)
    team_code = db.Column(db.String(20), unique=True, nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(30))
    city = db.Column(db.String(50))
    league = db.Column(db.String(50))
    primary_color = db.Column(db.String(7), default='#1a237e')
    secondary_color = db.Column(db.String(7), default='#ffd600')
    accent_color = db.Column(db.String(7), default='#ffffff')
    logo_filename = db.Column(db.String(100))
    is_main_team = db.Column(db.Boolean, default=False, index=True)
    season_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<TeamConfig {self.team_code}: {self.team_name}>'
