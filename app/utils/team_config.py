from flask import current_app


def get_team_config():
    """Load main team config from DB, fallback to .env defaults."""
    try:
        from app.models.team import TeamConfig
        team = TeamConfig.query.filter_by(is_main_team=True).first()
        if team:
            return {
                'code': team.team_code,
                'name': team.team_name,
                'short_name': team.short_name or team.team_name,
                'city': team.city or '',
                'league': team.league or '',
                'primary_color': team.primary_color,
                'secondary_color': team.secondary_color,
                'accent_color': team.accent_color,
                'logo': team.logo_filename or 'team-logo.png',
                'season_year': team.season_year or current_app.config.get('SEASON_YEAR', 2026),
            }
    except Exception:
        pass

    return {
        'code': current_app.config.get('DEFAULT_TEAM_CODE', 'TEAM'),
        'name': current_app.config.get('DEFAULT_TEAM_NAME', 'My Team'),
        'short_name': current_app.config.get('DEFAULT_TEAM_NAME', 'My Team'),
        'city': '',
        'league': '',
        'primary_color': current_app.config.get('DEFAULT_PRIMARY_COLOR', '#1a237e'),
        'secondary_color': current_app.config.get('DEFAULT_SECONDARY_COLOR', '#ffd600'),
        'accent_color': current_app.config.get('DEFAULT_ACCENT_COLOR', '#ffffff'),
        'logo': 'team-logo.png',
        'season_year': current_app.config.get('SEASON_YEAR', 2026),
    }
