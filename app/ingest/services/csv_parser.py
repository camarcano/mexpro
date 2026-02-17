"""Parse Trackman CSV files and apply column name mapping."""

import pandas as pd
from app.utils.trackman_columns import TRACKMAN_COLUMN_MAP, REQUIRED_COLUMNS


def parse_trackman_csv(filepath):
    """Read a Trackman CSV and rename columns to snake_case.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pandas DataFrame with snake_case column names.

    Raises:
        ValueError: If required columns are missing.
    """
    df = pd.read_csv(filepath, dtype=str, keep_default_na=False)

    # Validate required columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Rename only columns that exist in the mapping
    rename_map = {k: v for k, v in TRACKMAN_COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Drop any columns not in the mapping (unknown/extra columns)
    known_cols = set(TRACKMAN_COLUMN_MAP.values())
    df = df[[col for col in df.columns if col in known_cols]]

    return df
