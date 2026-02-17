"""
SQLAlchemy model for the pitches table.

Maps all 167 Trackman CSV columns as individual database columns,
plus metadata columns for upload tracking and timestamps.
"""

from datetime import datetime, timezone
from app.extensions import db


class Pitch(db.Model):
    __tablename__ = 'pitches'

    __table_args__ = (
        db.Index('ix_pitches_pitcher_date', 'pitcher_id', 'date'),
        db.Index('ix_pitches_batter_date', 'batter_id', 'date'),
        db.Index('ix_pitches_game_inning', 'game_id', 'inning', 'top_bottom'),
        db.Index('ix_pitches_pitcher_pitch_type', 'pitcher_id', 'tagged_pitch_type'),
        db.Index('ix_pitches_pitcher_team_date', 'pitcher_team', 'date'),
    )

    # ── Primary key & metadata ────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    upload_log_id = db.Column(db.Integer, db.ForeignKey('upload_logs.id'), index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Game context ──────────────────────────────────────────────
    pitch_no = db.Column(db.Integer)
    date = db.Column(db.Date, index=True)
    time = db.Column(db.String(20))
    pa_of_inning = db.Column(db.Integer)
    pitch_of_pa = db.Column(db.Integer)

    # ── Pitcher info ──────────────────────────────────────────────
    pitcher = db.Column(db.String(100))
    pitcher_id = db.Column(db.Integer, index=True)
    pitcher_throws = db.Column(db.String(5))
    pitcher_team = db.Column(db.String(50))

    # ── Batter info ───────────────────────────────────────────────
    batter = db.Column(db.String(100))
    batter_id = db.Column(db.Integer, index=True)
    batter_side = db.Column(db.String(5))
    batter_team = db.Column(db.String(50))

    # ── Situation ─────────────────────────────────────────────────
    pitcher_set = db.Column(db.String(20))
    inning = db.Column(db.Integer)
    top_bottom = db.Column(db.String(10))
    outs = db.Column(db.Integer)
    balls = db.Column(db.Integer)
    strikes = db.Column(db.Integer)

    # ── Pitch classification ──────────────────────────────────────
    tagged_pitch_type = db.Column(db.String(30))
    auto_pitch_type = db.Column(db.String(30))
    pitch_call = db.Column(db.String(30))
    k_or_bb = db.Column(db.String(20))
    tagged_hit_type = db.Column(db.String(30))

    # ── Play result ───────────────────────────────────────────────
    play_result = db.Column(db.String(30))
    outs_on_play = db.Column(db.Integer)
    runs_scored = db.Column(db.Integer)
    notes = db.Column(db.Text)

    # ── Pitch release / movement ──────────────────────────────────
    rel_speed = db.Column(db.Float)
    vert_rel_angle = db.Column(db.Float)
    horz_rel_angle = db.Column(db.Float)
    spin_rate = db.Column(db.Float)
    spin_axis = db.Column(db.Float)
    tilt = db.Column(db.String(10))
    rel_height = db.Column(db.Float)
    rel_side = db.Column(db.Float)
    extension = db.Column(db.Float)
    vert_break = db.Column(db.Float)
    induced_vert_break = db.Column(db.Float)
    horz_break = db.Column(db.Float)

    # ── Plate location ────────────────────────────────────────────
    plate_loc_height = db.Column(db.Float)
    plate_loc_side = db.Column(db.Float)
    zone_speed = db.Column(db.Float)
    vert_appr_angle = db.Column(db.Float)
    horz_appr_angle = db.Column(db.Float)
    zone_time = db.Column(db.Float)

    # ── Hit data ──────────────────────────────────────────────────
    exit_speed = db.Column(db.Float)
    angle = db.Column(db.Float)
    direction = db.Column(db.Float)
    hit_spin_rate = db.Column(db.Float)
    position_at_110_x = db.Column(db.Float)
    position_at_110_y = db.Column(db.Float)
    position_at_110_z = db.Column(db.Float)
    distance = db.Column(db.Float)
    last_tracked_distance = db.Column(db.Float)
    bearing = db.Column(db.Float)
    hang_time = db.Column(db.Float)

    # ── PFX / initial conditions ──────────────────────────────────
    pfx_x = db.Column(db.Float)
    pfx_z = db.Column(db.Float)
    x0 = db.Column(db.Float)
    y0 = db.Column(db.Float)
    z0 = db.Column(db.Float)
    vx0 = db.Column(db.Float)
    vy0 = db.Column(db.Float)
    vz0 = db.Column(db.Float)
    ax0 = db.Column(db.Float)
    ay0 = db.Column(db.Float)
    az0 = db.Column(db.Float)

    # ── Game metadata ─────────────────────────────────────────────
    home_team = db.Column(db.String(50))
    away_team = db.Column(db.String(50))
    stadium = db.Column(db.String(100))
    level = db.Column(db.String(30))
    league = db.Column(db.String(30))
    game_id = db.Column(db.String(100), db.ForeignKey('games.game_id'), index=True)
    pitch_uid = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # ── Advanced pitch metrics ────────────────────────────────────
    effective_velo = db.Column(db.Float)
    max_height = db.Column(db.Float)
    measured_duration = db.Column(db.Float)
    speed_drop = db.Column(db.Float)

    # ── Last measured positions ───────────────────────────────────
    pitch_last_measured_x = db.Column(db.Float)
    pitch_last_measured_y = db.Column(db.Float)
    pitch_last_measured_z = db.Column(db.Float)

    # ── Contact position ──────────────────────────────────────────
    contact_position_x = db.Column(db.Float)
    contact_position_y = db.Column(db.Float)
    contact_position_z = db.Column(db.Float)

    # ── UID / timestamps ──────────────────────────────────────────
    game_uid = db.Column(db.String(64))
    utc_date = db.Column(db.Date)
    utc_time = db.Column(db.String(20))
    local_date_time = db.Column(db.String(40))
    utc_date_time = db.Column(db.String(40))

    # ── Auto classification ───────────────────────────────────────
    auto_hit_type = db.Column(db.String(30))
    system = db.Column(db.String(30))

    # ── Foreign IDs ───────────────────────────────────────────────
    home_team_foreign_id = db.Column(db.Integer)
    away_team_foreign_id = db.Column(db.Integer)
    game_foreign_id = db.Column(db.String(64))

    # ── Catcher info ──────────────────────────────────────────────
    catcher = db.Column(db.String(100))
    catcher_id = db.Column(db.Integer)
    catcher_throws = db.Column(db.String(5))
    catcher_team = db.Column(db.String(50))

    # ── Play ID ───────────────────────────────────────────────────
    play_id = db.Column(db.String(64))

    # ── Pitch trajectory coefficients ─────────────────────────────
    pitch_trajectory_xc0 = db.Column(db.Float)
    pitch_trajectory_xc1 = db.Column(db.Float)
    pitch_trajectory_xc2 = db.Column(db.Float)
    pitch_trajectory_yc0 = db.Column(db.Float)
    pitch_trajectory_yc1 = db.Column(db.Float)
    pitch_trajectory_yc2 = db.Column(db.Float)
    pitch_trajectory_zc0 = db.Column(db.Float)
    pitch_trajectory_zc1 = db.Column(db.Float)
    pitch_trajectory_zc2 = db.Column(db.Float)

    # ── Hit spin axis ─────────────────────────────────────────────
    hit_spin_axis = db.Column(db.Float)

    # ── Hit trajectory X coefficients ─────────────────────────────
    hit_trajectory_xc0 = db.Column(db.Float)
    hit_trajectory_xc1 = db.Column(db.Float)
    hit_trajectory_xc2 = db.Column(db.Float)
    hit_trajectory_xc3 = db.Column(db.Float)
    hit_trajectory_xc4 = db.Column(db.Float)
    hit_trajectory_xc5 = db.Column(db.Float)
    hit_trajectory_xc6 = db.Column(db.Float)
    hit_trajectory_xc7 = db.Column(db.Float)
    hit_trajectory_xc8 = db.Column(db.Float)

    # ── Hit trajectory Y coefficients ─────────────────────────────
    hit_trajectory_yc0 = db.Column(db.Float)
    hit_trajectory_yc1 = db.Column(db.Float)
    hit_trajectory_yc2 = db.Column(db.Float)
    hit_trajectory_yc3 = db.Column(db.Float)
    hit_trajectory_yc4 = db.Column(db.Float)
    hit_trajectory_yc5 = db.Column(db.Float)
    hit_trajectory_yc6 = db.Column(db.Float)
    hit_trajectory_yc7 = db.Column(db.Float)
    hit_trajectory_yc8 = db.Column(db.Float)

    # ── Hit trajectory Z coefficients ─────────────────────────────
    hit_trajectory_zc0 = db.Column(db.Float)
    hit_trajectory_zc1 = db.Column(db.Float)
    hit_trajectory_zc2 = db.Column(db.Float)
    hit_trajectory_zc3 = db.Column(db.Float)
    hit_trajectory_zc4 = db.Column(db.Float)
    hit_trajectory_zc5 = db.Column(db.Float)
    hit_trajectory_zc6 = db.Column(db.Float)
    hit_trajectory_zc7 = db.Column(db.Float)
    hit_trajectory_zc8 = db.Column(db.Float)

    # ── Catcher throw / pop time ──────────────────────────────────
    throw_speed = db.Column(db.Float)
    pop_time = db.Column(db.Float)
    exchange_time = db.Column(db.Float)
    time_to_base = db.Column(db.Float)

    # ── Catcher catch position ────────────────────────────────────
    catch_position_x = db.Column(db.Float)
    catch_position_y = db.Column(db.Float)
    catch_position_z = db.Column(db.Float)

    # ── Throw position ────────────────────────────────────────────
    throw_position_x = db.Column(db.Float)
    throw_position_y = db.Column(db.Float)
    throw_position_z = db.Column(db.Float)

    # ── Base position ─────────────────────────────────────────────
    base_position_x = db.Column(db.Float)
    base_position_y = db.Column(db.Float)
    base_position_z = db.Column(db.Float)

    # ── Throw trajectory coefficients ─────────────────────────────
    throw_trajectory_xc0 = db.Column(db.Float)
    throw_trajectory_xc1 = db.Column(db.Float)
    throw_trajectory_xc2 = db.Column(db.Float)
    throw_trajectory_yc0 = db.Column(db.Float)
    throw_trajectory_yc1 = db.Column(db.Float)
    throw_trajectory_yc2 = db.Column(db.Float)
    throw_trajectory_zc0 = db.Column(db.Float)
    throw_trajectory_zc1 = db.Column(db.Float)
    throw_trajectory_zc2 = db.Column(db.Float)

    # ── Confidence scores ─────────────────────────────────────────
    pitch_release_confidence = db.Column(db.Float)
    pitch_location_confidence = db.Column(db.Float)
    pitch_movement_confidence = db.Column(db.Float)
    hit_launch_confidence = db.Column(db.Float)
    hit_landing_confidence = db.Column(db.Float)
    catcher_throw_catch_confidence = db.Column(db.Float)
    catcher_throw_release_confidence = db.Column(db.Float)
    catcher_throw_location_confidence = db.Column(db.Float)

    def __repr__(self):
        return f'<Pitch {self.pitch_uid}: {self.pitcher} #{self.pitch_no}>'
