"""Pitch movement profile data for visualization."""

from sqlalchemy import case, and_
from app.extensions import db
from app.models.pitch import Pitch


def _effective_pitch_type():
    """Prefer tagged_pitch_type, fall back to auto_pitch_type."""
    return case(
        (and_(
            Pitch.tagged_pitch_type.isnot(None),
            Pitch.tagged_pitch_type != 'Undefined',
        ), Pitch.tagged_pitch_type),
        else_=Pitch.auto_pitch_type,
    )


def get_pitch_profiles(pitcher_id=None, pitcher_name=None, filters=None):
    """
    Get pitch movement data for profile plots (HB vs IVB).

    Returns dict with 'overall', 'vs_rhh', 'vs_lhh' keys,
    each containing a list of pitch dicts with:
    pitch_type, horz_break, induced_vert_break, rel_speed.
    """
    filters = filters or {}

    if pitcher_id is not None:
        pitcher_filters = [Pitch.pitcher_id == pitcher_id]
    else:
        pitcher_filters = [
            Pitch.pitcher == pitcher_name,
            Pitch.pitcher_id.is_(None)
        ]

    ept = _effective_pitch_type()

    # Query all pitches with movement data
    q = db.session.query(
        ept.label('pitch_type'),
        Pitch.horz_break,
        Pitch.induced_vert_break,
        Pitch.rel_speed,
        Pitch.spin_rate,
        Pitch.batter_side,
    ).filter(
        *pitcher_filters,
        ept.isnot(None),
        ept != 'Undefined',
        Pitch.horz_break.isnot(None),
        Pitch.induced_vert_break.isnot(None),
        Pitch.rel_speed.isnot(None),
    )

    if filters.get('game_id'):
        q = q.filter(Pitch.game_id == filters['game_id'])
    if filters.get('start_date'):
        q = q.filter(Pitch.date >= filters['start_date'])
    if filters.get('end_date'):
        q = q.filter(Pitch.date <= filters['end_date'])

    rows = q.all()

    # Organize by split
    result = {
        'overall': [],
        'vs_rhh': [],
        'vs_lhh': [],
    }

    for row in rows:
        pitch_data = {
            'pitch_type': row.pitch_type,
            'horz_break': row.horz_break,
            'induced_vert_break': row.induced_vert_break,
            'rel_speed': row.rel_speed,
            'spin_rate': row.spin_rate,
        }
        result['overall'].append(pitch_data)

        if row.batter_side == 'Right':
            result['vs_rhh'].append(pitch_data)
        elif row.batter_side == 'Left':
            result['vs_lhh'].append(pitch_data)

    return result
