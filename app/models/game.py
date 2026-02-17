from datetime import datetime, timezone
from app.extensions import db


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    game_uid = db.Column(db.String(64), unique=True)
    date = db.Column(db.Date, index=True)
    home_team = db.Column(db.String(20), index=True)
    away_team = db.Column(db.String(20), index=True)
    stadium = db.Column(db.String(100))
    level = db.Column(db.String(30))
    league = db.Column(db.String(30))
    total_pitches = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    pitches = db.relationship('Pitch', backref='game', lazy='dynamic')

    def __repr__(self):
        return f'<Game {self.game_id}: {self.away_team} @ {self.home_team}>'
