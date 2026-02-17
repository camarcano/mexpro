"""Type coercion and validation for parsed Trackman DataFrames."""

import pandas as pd
from datetime import datetime
from app.utils.trackman_columns import COLUMN_TYPES


def coerce_types(df):
    """Apply type coercion to a DataFrame with snake_case columns.

    Converts string values from CSV to proper Python types based on
    COLUMN_TYPES mapping. Empty strings become None.

    Args:
        df: pandas DataFrame with snake_case column names.

    Returns:
        DataFrame with coerced types (object dtype, values are Python native types).
    """
    for col in df.columns:
        col_type = COLUMN_TYPES.get(col, 'str')

        if col_type == 'float':
            df[col] = df[col].apply(_to_float)
        elif col_type == 'int':
            df[col] = df[col].apply(_to_int)
        elif col_type == 'date':
            df[col] = df[col].apply(_to_date)
        else:
            # String: strip whitespace, empty -> None
            df[col] = df[col].apply(_to_str)

    return df


def _to_float(val):
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _to_int(val):
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _to_date(val):
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return None
    try:
        return datetime.strptime(val.strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _to_str(val):
    if val is None:
        return None
    val = str(val).strip()
    return val if val else None
