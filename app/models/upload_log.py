from datetime import datetime, timezone
from app.extensions import db


class UploadLog(db.Model):
    __tablename__ = 'upload_logs'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), index=True)
    game_id = db.Column(db.String(100))
    rows_total = db.Column(db.Integer, default=0)
    rows_imported = db.Column(db.Integer, default=0)
    rows_skipped = db.Column(db.Integer, default=0)
    rows_error = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')
    error_message = db.Column(db.Text)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)

    uploaded_by = db.relationship('User', backref='uploads')
    pitches = db.relationship('Pitch', backref='upload_log', lazy='dynamic')

    def __repr__(self):
        return f'<UploadLog {self.filename} [{self.status}]>'
