"""Pitch type grouping and zone classification utilities."""

PITCH_TYPE_GROUPS = {
    'Fastball': ['Four-Seam', 'Fastball', 'Sinker', 'Two-Seam', 'Cutter'],
    'Breaking': ['Slider', 'Curveball', 'Sweeper', 'Slurve', 'Knuckle Curve'],
    'Offspeed': ['Changeup', 'Splitter', 'Knuckleball'],
}

# Reverse lookup: pitch type -> group
PITCH_TYPE_TO_GROUP = {}
for group, types in PITCH_TYPE_GROUPS.items():
    for t in types:
        PITCH_TYPE_TO_GROUP[t] = group


def get_pitch_group(pitch_type):
    """Return the pitch group (Fastball/Breaking/Offspeed) for a pitch type."""
    if not pitch_type:
        return 'Unknown'
    return PITCH_TYPE_TO_GROUP.get(pitch_type, 'Unknown')


# Strike zone boundaries (in feet, from catcher's perspective)
ZONE_LEFT = -0.83   # 10 inches from center
ZONE_RIGHT = 0.83
ZONE_BOTTOM = 1.5
ZONE_TOP = 3.5


def is_in_zone(plate_loc_side, plate_loc_height):
    """Check if a pitch is in the strike zone."""
    if plate_loc_side is None or plate_loc_height is None:
        return None
    return (ZONE_LEFT <= plate_loc_side <= ZONE_RIGHT and
            ZONE_BOTTOM <= plate_loc_height <= ZONE_TOP)


def is_swing(pitch_call):
    """Check if the pitch call represents a swing."""
    if not pitch_call:
        return False
    return pitch_call in (
        'StrikeSwinging', 'FoulBall', 'FoulBallNotFieldable',
        'FoulBallFieldable', 'InPlay', 'FoulTip',
    )


def is_whiff(pitch_call):
    """Check if the pitch call is a swing and miss."""
    return pitch_call == 'StrikeSwinging'


def is_called_strike(pitch_call):
    """Check if the pitch call is a called strike."""
    return pitch_call == 'StrikeCalled'


def is_csw(pitch_call):
    """Called Strike + Whiff (CSW)."""
    return pitch_call in ('StrikeCalled', 'StrikeSwinging')


def is_ball_in_play(pitch_call):
    """Check if the pitch was put in play."""
    return pitch_call == 'InPlay'
