"""
Trackman CSV column mapping and type definitions.

Maps all 167 Trackman CSV columns (CamelCase) to snake_case Python/DB
column names with type information for parsing and validation.
"""

# Maps each CSV column header (CamelCase) to its snake_case DB column name.
TRACKMAN_COLUMN_MAP = {
    # ── Game context ──────────────────────────────────────────────
    "PitchNo": "pitch_no",
    "Date": "date",
    "Time": "time",
    "PAofInning": "pa_of_inning",
    "PitchofPA": "pitch_of_pa",

    # ── Pitcher info ──────────────────────────────────────────────
    "Pitcher": "pitcher",
    "PitcherId": "pitcher_id",
    "PitcherThrows": "pitcher_throws",
    "PitcherTeam": "pitcher_team",

    # ── Batter info ───────────────────────────────────────────────
    "Batter": "batter",
    "BatterId": "batter_id",
    "BatterSide": "batter_side",
    "BatterTeam": "batter_team",

    # ── Situation ─────────────────────────────────────────────────
    "PitcherSet": "pitcher_set",
    "Inning": "inning",
    "Top/Bottom": "top_bottom",
    "Outs": "outs",
    "Balls": "balls",
    "Strikes": "strikes",

    # ── Pitch classification ──────────────────────────────────────
    "TaggedPitchType": "tagged_pitch_type",
    "AutoPitchType": "auto_pitch_type",
    "PitchCall": "pitch_call",
    "KorBB": "k_or_bb",
    "TaggedHitType": "tagged_hit_type",

    # ── Play result ───────────────────────────────────────────────
    "PlayResult": "play_result",
    "OutsOnPlay": "outs_on_play",
    "RunsScored": "runs_scored",
    "Notes": "notes",

    # ── Pitch release / movement ──────────────────────────────────
    "RelSpeed": "rel_speed",
    "VertRelAngle": "vert_rel_angle",
    "HorzRelAngle": "horz_rel_angle",
    "SpinRate": "spin_rate",
    "SpinAxis": "spin_axis",
    "Tilt": "tilt",
    "RelHeight": "rel_height",
    "RelSide": "rel_side",
    "Extension": "extension",
    "VertBreak": "vert_break",
    "InducedVertBreak": "induced_vert_break",
    "HorzBreak": "horz_break",

    # ── Plate location ────────────────────────────────────────────
    "PlateLocHeight": "plate_loc_height",
    "PlateLocSide": "plate_loc_side",
    "ZoneSpeed": "zone_speed",
    "VertApprAngle": "vert_appr_angle",
    "HorzApprAngle": "horz_appr_angle",
    "ZoneTime": "zone_time",

    # ── Hit data ──────────────────────────────────────────────────
    "ExitSpeed": "exit_speed",
    "Angle": "angle",
    "Direction": "direction",
    "HitSpinRate": "hit_spin_rate",
    "PositionAt110X": "position_at_110_x",
    "PositionAt110Y": "position_at_110_y",
    "PositionAt110Z": "position_at_110_z",
    "Distance": "distance",
    "LastTrackedDistance": "last_tracked_distance",
    "Bearing": "bearing",
    "HangTime": "hang_time",

    # ── PFX / initial conditions ──────────────────────────────────
    "pfxx": "pfx_x",
    "pfxz": "pfx_z",
    "x0": "x0",
    "y0": "y0",
    "z0": "z0",
    "vx0": "vx0",
    "vy0": "vy0",
    "vz0": "vz0",
    "ax0": "ax0",
    "ay0": "ay0",
    "az0": "az0",

    # ── Game metadata ─────────────────────────────────────────────
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "Stadium": "stadium",
    "Level": "level",
    "League": "league",
    "GameID": "game_id",
    "PitchUID": "pitch_uid",

    # ── Advanced pitch metrics ────────────────────────────────────
    "EffectiveVelo": "effective_velo",
    "MaxHeight": "max_height",
    "MeasuredDuration": "measured_duration",
    "SpeedDrop": "speed_drop",

    # ── Last measured positions ───────────────────────────────────
    "PitchLastMeasuredX": "pitch_last_measured_x",
    "PitchLastMeasuredY": "pitch_last_measured_y",
    "PitchLastMeasuredZ": "pitch_last_measured_z",

    # ── Contact position ──────────────────────────────────────────
    "ContactPositionX": "contact_position_x",
    "ContactPositionY": "contact_position_y",
    "ContactPositionZ": "contact_position_z",

    # ── UID / timestamps ──────────────────────────────────────────
    "GameUID": "game_uid",
    "UTCDate": "utc_date",
    "UTCTime": "utc_time",
    "LocalDateTime": "local_date_time",
    "UTCDateTime": "utc_date_time",

    # ── Auto classification ───────────────────────────────────────
    "AutoHitType": "auto_hit_type",
    "System": "system",

    # ── Foreign IDs ───────────────────────────────────────────────
    "HomeTeamForeignID": "home_team_foreign_id",
    "AwayTeamForeignID": "away_team_foreign_id",
    "GameForeignID": "game_foreign_id",

    # ── Catcher info ──────────────────────────────────────────────
    "Catcher": "catcher",
    "CatcherId": "catcher_id",
    "CatcherThrows": "catcher_throws",
    "CatcherTeam": "catcher_team",

    # ── Play ID ───────────────────────────────────────────────────
    "PlayID": "play_id",

    # ── Pitch trajectory coefficients ─────────────────────────────
    "PitchTrajectoryXc0": "pitch_trajectory_xc0",
    "PitchTrajectoryXc1": "pitch_trajectory_xc1",
    "PitchTrajectoryXc2": "pitch_trajectory_xc2",
    "PitchTrajectoryYc0": "pitch_trajectory_yc0",
    "PitchTrajectoryYc1": "pitch_trajectory_yc1",
    "PitchTrajectoryYc2": "pitch_trajectory_yc2",
    "PitchTrajectoryZc0": "pitch_trajectory_zc0",
    "PitchTrajectoryZc1": "pitch_trajectory_zc1",
    "PitchTrajectoryZc2": "pitch_trajectory_zc2",

    # ── Hit spin axis ─────────────────────────────────────────────
    "HitSpinAxis": "hit_spin_axis",

    # ── Hit trajectory X coefficients ─────────────────────────────
    "HitTrajectoryXc0": "hit_trajectory_xc0",
    "HitTrajectoryXc1": "hit_trajectory_xc1",
    "HitTrajectoryXc2": "hit_trajectory_xc2",
    "HitTrajectoryXc3": "hit_trajectory_xc3",
    "HitTrajectoryXc4": "hit_trajectory_xc4",
    "HitTrajectoryXc5": "hit_trajectory_xc5",
    "HitTrajectoryXc6": "hit_trajectory_xc6",
    "HitTrajectoryXc7": "hit_trajectory_xc7",
    "HitTrajectoryXc8": "hit_trajectory_xc8",

    # ── Hit trajectory Y coefficients ─────────────────────────────
    "HitTrajectoryYc0": "hit_trajectory_yc0",
    "HitTrajectoryYc1": "hit_trajectory_yc1",
    "HitTrajectoryYc2": "hit_trajectory_yc2",
    "HitTrajectoryYc3": "hit_trajectory_yc3",
    "HitTrajectoryYc4": "hit_trajectory_yc4",
    "HitTrajectoryYc5": "hit_trajectory_yc5",
    "HitTrajectoryYc6": "hit_trajectory_yc6",
    "HitTrajectoryYc7": "hit_trajectory_yc7",
    "HitTrajectoryYc8": "hit_trajectory_yc8",

    # ── Hit trajectory Z coefficients ─────────────────────────────
    "HitTrajectoryZc0": "hit_trajectory_zc0",
    "HitTrajectoryZc1": "hit_trajectory_zc1",
    "HitTrajectoryZc2": "hit_trajectory_zc2",
    "HitTrajectoryZc3": "hit_trajectory_zc3",
    "HitTrajectoryZc4": "hit_trajectory_zc4",
    "HitTrajectoryZc5": "hit_trajectory_zc5",
    "HitTrajectoryZc6": "hit_trajectory_zc6",
    "HitTrajectoryZc7": "hit_trajectory_zc7",
    "HitTrajectoryZc8": "hit_trajectory_zc8",

    # ── Catcher throw / pop time ──────────────────────────────────
    "ThrowSpeed": "throw_speed",
    "PopTime": "pop_time",
    "ExchangeTime": "exchange_time",
    "TimeToBase": "time_to_base",

    # ── Catcher catch position ────────────────────────────────────
    "CatchPositionX": "catch_position_x",
    "CatchPositionY": "catch_position_y",
    "CatchPositionZ": "catch_position_z",

    # ── Throw position ────────────────────────────────────────────
    "ThrowPositionX": "throw_position_x",
    "ThrowPositionY": "throw_position_y",
    "ThrowPositionZ": "throw_position_z",

    # ── Base position ─────────────────────────────────────────────
    "BasePositionX": "base_position_x",
    "BasePositionY": "base_position_y",
    "BasePositionZ": "base_position_z",

    # ── Throw trajectory coefficients ─────────────────────────────
    "ThrowTrajectoryXc0": "throw_trajectory_xc0",
    "ThrowTrajectoryXc1": "throw_trajectory_xc1",
    "ThrowTrajectoryXc2": "throw_trajectory_xc2",
    "ThrowTrajectoryYc0": "throw_trajectory_yc0",
    "ThrowTrajectoryYc1": "throw_trajectory_yc1",
    "ThrowTrajectoryYc2": "throw_trajectory_yc2",
    "ThrowTrajectoryZc0": "throw_trajectory_zc0",
    "ThrowTrajectoryZc1": "throw_trajectory_zc1",
    "ThrowTrajectoryZc2": "throw_trajectory_zc2",

    # ── Confidence scores ─────────────────────────────────────────
    "PitchReleaseConfidence": "pitch_release_confidence",
    "PitchLocationConfidence": "pitch_location_confidence",
    "PitchMovementConfidence": "pitch_movement_confidence",
    "HitLaunchConfidence": "hit_launch_confidence",
    "HitLandingConfidence": "hit_landing_confidence",
    "CatcherThrowCatchConfidence": "catcher_throw_catch_confidence",
    "CatcherThrowReleaseConfidence": "catcher_throw_release_confidence",
    "CatcherThrowLocationConfidence": "catcher_throw_location_confidence",
}

# Reverse map: snake_case -> CamelCase (for export)
REVERSE_COLUMN_MAP = {v: k for k, v in TRACKMAN_COLUMN_MAP.items()}

# Maps each snake_case column name to its Python type for parsing.
COLUMN_TYPES = {
    # ── Integer columns ───────────────────────────────────────────
    "pitch_no": "int",
    "pa_of_inning": "int",
    "pitch_of_pa": "int",
    "pitcher_id": "int",
    "batter_id": "int",
    "inning": "int",
    "outs": "int",
    "balls": "int",
    "strikes": "int",
    "outs_on_play": "int",
    "runs_scored": "int",
    "catcher_id": "int",
    "home_team_foreign_id": "int",
    "away_team_foreign_id": "int",

    # ── Date columns ──────────────────────────────────────────────
    "date": "date",
    "utc_date": "date",

    # ── String columns ────────────────────────────────────────────
    "time": "str",
    "pitcher": "str",
    "pitcher_throws": "str",
    "pitcher_team": "str",
    "batter": "str",
    "batter_side": "str",
    "batter_team": "str",
    "pitcher_set": "str",
    "top_bottom": "str",
    "tagged_pitch_type": "str",
    "auto_pitch_type": "str",
    "pitch_call": "str",
    "k_or_bb": "str",
    "tagged_hit_type": "str",
    "play_result": "str",
    "notes": "str",
    "tilt": "str",
    "home_team": "str",
    "away_team": "str",
    "stadium": "str",
    "level": "str",
    "league": "str",
    "game_id": "str",
    "pitch_uid": "str",
    "game_uid": "str",
    "utc_time": "str",
    "local_date_time": "str",
    "utc_date_time": "str",
    "auto_hit_type": "str",
    "system": "str",
    "game_foreign_id": "str",
    "catcher": "str",
    "catcher_throws": "str",
    "catcher_team": "str",
    "play_id": "str",

    # ── Float columns (pitch release / movement) ─────────────────
    "rel_speed": "float",
    "vert_rel_angle": "float",
    "horz_rel_angle": "float",
    "spin_rate": "float",
    "spin_axis": "float",
    "rel_height": "float",
    "rel_side": "float",
    "extension": "float",
    "vert_break": "float",
    "induced_vert_break": "float",
    "horz_break": "float",

    # ── Float columns (plate location) ────────────────────────────
    "plate_loc_height": "float",
    "plate_loc_side": "float",
    "zone_speed": "float",
    "vert_appr_angle": "float",
    "horz_appr_angle": "float",
    "zone_time": "float",

    # ── Float columns (hit data) ──────────────────────────────────
    "exit_speed": "float",
    "angle": "float",
    "direction": "float",
    "hit_spin_rate": "float",
    "position_at_110_x": "float",
    "position_at_110_y": "float",
    "position_at_110_z": "float",
    "distance": "float",
    "last_tracked_distance": "float",
    "bearing": "float",
    "hang_time": "float",

    # ── Float columns (PFX / initial conditions) ──────────────────
    "pfx_x": "float",
    "pfx_z": "float",
    "x0": "float",
    "y0": "float",
    "z0": "float",
    "vx0": "float",
    "vy0": "float",
    "vz0": "float",
    "ax0": "float",
    "ay0": "float",
    "az0": "float",

    # ── Float columns (advanced pitch metrics) ────────────────────
    "effective_velo": "float",
    "max_height": "float",
    "measured_duration": "float",
    "speed_drop": "float",

    # ── Float columns (last measured positions) ───────────────────
    "pitch_last_measured_x": "float",
    "pitch_last_measured_y": "float",
    "pitch_last_measured_z": "float",

    # ── Float columns (contact position) ──────────────────────────
    "contact_position_x": "float",
    "contact_position_y": "float",
    "contact_position_z": "float",

    # ── Float columns (pitch trajectory coefficients) ─────────────
    "pitch_trajectory_xc0": "float",
    "pitch_trajectory_xc1": "float",
    "pitch_trajectory_xc2": "float",
    "pitch_trajectory_yc0": "float",
    "pitch_trajectory_yc1": "float",
    "pitch_trajectory_yc2": "float",
    "pitch_trajectory_zc0": "float",
    "pitch_trajectory_zc1": "float",
    "pitch_trajectory_zc2": "float",

    # ── Float columns (hit spin axis) ─────────────────────────────
    "hit_spin_axis": "float",

    # ── Float columns (hit trajectory X) ──────────────────────────
    "hit_trajectory_xc0": "float",
    "hit_trajectory_xc1": "float",
    "hit_trajectory_xc2": "float",
    "hit_trajectory_xc3": "float",
    "hit_trajectory_xc4": "float",
    "hit_trajectory_xc5": "float",
    "hit_trajectory_xc6": "float",
    "hit_trajectory_xc7": "float",
    "hit_trajectory_xc8": "float",

    # ── Float columns (hit trajectory Y) ──────────────────────────
    "hit_trajectory_yc0": "float",
    "hit_trajectory_yc1": "float",
    "hit_trajectory_yc2": "float",
    "hit_trajectory_yc3": "float",
    "hit_trajectory_yc4": "float",
    "hit_trajectory_yc5": "float",
    "hit_trajectory_yc6": "float",
    "hit_trajectory_yc7": "float",
    "hit_trajectory_yc8": "float",

    # ── Float columns (hit trajectory Z) ──────────────────────────
    "hit_trajectory_zc0": "float",
    "hit_trajectory_zc1": "float",
    "hit_trajectory_zc2": "float",
    "hit_trajectory_zc3": "float",
    "hit_trajectory_zc4": "float",
    "hit_trajectory_zc5": "float",
    "hit_trajectory_zc6": "float",
    "hit_trajectory_zc7": "float",
    "hit_trajectory_zc8": "float",

    # ── Float columns (catcher throw / pop time) ──────────────────
    "throw_speed": "float",
    "pop_time": "float",
    "exchange_time": "float",
    "time_to_base": "float",

    # ── Float columns (catch position) ────────────────────────────
    "catch_position_x": "float",
    "catch_position_y": "float",
    "catch_position_z": "float",

    # ── Float columns (throw position) ────────────────────────────
    "throw_position_x": "float",
    "throw_position_y": "float",
    "throw_position_z": "float",

    # ── Float columns (base position) ─────────────────────────────
    "base_position_x": "float",
    "base_position_y": "float",
    "base_position_z": "float",

    # ── Float columns (throw trajectory coefficients) ─────────────
    "throw_trajectory_xc0": "float",
    "throw_trajectory_xc1": "float",
    "throw_trajectory_xc2": "float",
    "throw_trajectory_yc0": "float",
    "throw_trajectory_yc1": "float",
    "throw_trajectory_yc2": "float",
    "throw_trajectory_zc0": "float",
    "throw_trajectory_zc1": "float",
    "throw_trajectory_zc2": "float",

    # ── Float columns (confidence scores) ─────────────────────────
    "pitch_release_confidence": "float",
    "pitch_location_confidence": "float",
    "pitch_movement_confidence": "float",
    "hit_launch_confidence": "float",
    "hit_landing_confidence": "float",
    "catcher_throw_catch_confidence": "float",
    "catcher_throw_release_confidence": "float",
    "catcher_throw_location_confidence": "float",
}

# Columns that MUST be present in the CSV for it to be considered valid.
REQUIRED_COLUMNS = [
    "PitchNo",
    "Date",
    "Pitcher",
    "PitcherId",
    "PitcherThrows",
    "PitcherTeam",
    "Batter",
    "BatterId",
    "BatterSide",
    "BatterTeam",
    "Inning",
    "Top/Bottom",
    "Outs",
    "Balls",
    "Strikes",
    "PitchCall",
    "GameID",
    "PitchUID",
    "HomeTeam",
    "AwayTeam",
]
