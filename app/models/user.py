from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class Permission:
    READ = 1
    UPLOAD = 2
    REPORTS = 4
    ADMIN = 8
    MANAGE_USERS = 16


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=0)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Viewer': Permission.READ,
            'Analyst': Permission.READ | Permission.UPLOAD | Permission.REPORTS,
            'Admin': Permission.READ | Permission.UPLOAD | Permission.REPORTS | Permission.ADMIN | Permission.MANAGE_USERS,
        }
        for name, perms in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name, permissions=perms)
            role.permissions = perms
            db.session.add(role)
        db.session.commit()

    def has_permission(self, perm):
        return self.permissions & perm == perm


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return f'<User {self.username}>'
