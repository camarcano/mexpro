from datetime import datetime, timezone
from app.extensions import db


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    trackman_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    throws = db.Column(db.String(10))
    bats = db.Column(db.String(10))
    primary_position = db.Column(db.String(20))
    team = db.Column(db.String(20), index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Player {self.name} ({self.trackman_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'trackman_id': self.trackman_id,
            'name': self.name,
            'throws': self.throws,
            'bats': self.bats,
            'primary_position': self.primary_position,
            'team': self.team,
        }
