"""Seed script: creates roles, admin user, and default team config."""

from app import create_app
from app.extensions import db
from app.models.user import Role, User
from app.models.team import TeamConfig


def seed():
    app = create_app()
    with app.app_context():
        # Create roles
        Role.insert_roles()
        print("Roles created.")

        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin_role = Role.query.filter_by(name='Admin').first()
            admin = User(
                username='admin',
                email='admin@mexpro.local',
                role_id=admin_role.id if admin_role else None,
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created (username: admin, password: admin).")
        else:
            print("Admin user already exists.")

        # Create or update default team config
        team = TeamConfig.query.filter_by(is_main_team=True).first()
        short = app.config['DEFAULT_TEAM_NAME'].split()[-1] if ' ' in app.config['DEFAULT_TEAM_NAME'] else app.config['DEFAULT_TEAM_NAME']
        if team is None:
            team = TeamConfig(
                team_code=app.config['DEFAULT_TEAM_CODE'],
                team_name=app.config['DEFAULT_TEAM_NAME'],
                short_name=short,
                primary_color=app.config['DEFAULT_PRIMARY_COLOR'],
                secondary_color=app.config['DEFAULT_SECONDARY_COLOR'],
                accent_color=app.config['DEFAULT_ACCENT_COLOR'],
                season_year=app.config['SEASON_YEAR'],
                is_main_team=True,
            )
            db.session.add(team)
            print(f"Default team created: {team.team_name}")
        else:
            team.team_code = app.config['DEFAULT_TEAM_CODE']
            team.team_name = app.config['DEFAULT_TEAM_NAME']
            team.short_name = short
            team.primary_color = app.config['DEFAULT_PRIMARY_COLOR']
            team.secondary_color = app.config['DEFAULT_SECONDARY_COLOR']
            team.accent_color = app.config['DEFAULT_ACCENT_COLOR']
            team.season_year = app.config['SEASON_YEAR']
            print(f"Main team updated: {team.team_name}")
        db.session.commit()


if __name__ == '__main__':
    seed()
