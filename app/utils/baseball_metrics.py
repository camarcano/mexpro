"""Pure functions for computing baseball statistics."""


def calculate_era(earned_runs, ip_decimal):
    """ERA = (ER * 9) / IP"""
    if ip_decimal <= 0:
        return None
    return round((earned_runs * 9) / ip_decimal, 2)


def calculate_whip(walks, hits, ip_decimal):
    """WHIP = (BB + H) / IP"""
    if ip_decimal <= 0:
        return None
    return round((walks + hits) / ip_decimal, 2)


def calculate_fip(hr, bb, hbp, k, ip_decimal, fip_constant=3.10):
    """FIP = (13*HR + 3*(BB+HBP) - 2*K) / IP + FIP_CONSTANT"""
    if ip_decimal <= 0:
        return None
    numerator = 13 * hr + 3 * (bb + hbp) - 2 * k
    return round(numerator / ip_decimal + fip_constant, 2)


def calculate_batting_average(hits, at_bats):
    """AVG = H / AB"""
    if at_bats <= 0:
        return None
    return round(hits / at_bats, 3)


def calculate_obp(hits, walks, hbp, at_bats, sac_flies):
    """OBP = (H + BB + HBP) / (AB + BB + HBP + SF)"""
    denom = at_bats + walks + hbp + sac_flies
    if denom <= 0:
        return None
    return round((hits + walks + hbp) / denom, 3)


def calculate_slg(total_bases, at_bats):
    """SLG = TB / AB"""
    if at_bats <= 0:
        return None
    return round(total_bases / at_bats, 3)


def calculate_ops(obp, slg):
    """OPS = OBP + SLG"""
    if obp is None or slg is None:
        return None
    return round(obp + slg, 3)


def pct(numerator, denominator, decimals=1):
    """Calculate percentage, return None if denominator is 0."""
    if not denominator:
        return None
    return round((numerator / denominator) * 100, decimals)


def rate(numerator, denominator, decimals=3):
    """Calculate a rate stat, return None if denominator is 0."""
    if not denominator:
        return None
    return round(numerator / denominator, decimals)


def calculate_iso(slg, avg):
    """ISO (Isolated Power) = SLG - AVG"""
    if slg is None or avg is None:
        return None
    return round(slg - avg, 3)


def calculate_woba(singles, doubles, triples, hr, bb, hbp, ab,
                   bb_total, hbp_total, sf):
    """Simplified wOBA using standard weights (2023 values)."""
    # Weights: BB=0.69, HBP=0.72, 1B=0.88, 2B=1.24, 3B=1.56, HR=2.08
    numerator = (0.69 * bb + 0.72 * hbp + 0.88 * singles +
                 1.24 * doubles + 1.56 * triples + 2.08 * hr)
    denominator = ab + bb_total + sf + hbp_total
    if denominator <= 0:
        return None
    return round(numerator / denominator, 3)


def calculate_hard_hit_pct(hard_hits, balls_in_play):
    """Hard Hit% = balls with exit velo >= 95 mph / total balls in play."""
    if balls_in_play <= 0:
        return None
    return round((hard_hits / balls_in_play) * 100, 1)


def calculate_barrel_pct(barrels, batted_balls):
    """Barrel% = barrels / batted ball events.

    Barrel = specific EV/LA combinations (simplified: EV >= 98 mph, LA 26-30°)
    """
    if batted_balls <= 0:
        return None
    return round((barrels / batted_balls) * 100, 1)


def calculate_contact_pct(swings, whiffs):
    """Contact% = (swings - whiffs) / swings"""
    if swings <= 0:
        return None
    contact = swings - whiffs
    return round((contact / swings) * 100, 1)
