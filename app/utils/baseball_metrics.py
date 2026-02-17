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
    return round((13 * hr + 3 * (bb + hbp) - 2 * k) / ip_decimal + fip_constant, 2)


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
