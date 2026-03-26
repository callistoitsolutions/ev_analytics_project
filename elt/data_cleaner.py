# etl/data_cleaner.py
"""
Data-cleaning layer.

What it does (in order)
-----------------------
1. Strip whitespace from every string column.
2. Fill missing *text* columns with "Unknown".
3. Fill missing *numeric* columns with the column median.
4. Coerce known numeric columns to float so NaN-free ints don't break later.
5. Derive ProfitINR = RevenueINR − OperatingCostINR  (only if both exist;
   if ProfitINR was already supplied by the file it is kept as-is).
6. Drop rows where BOTH Manufacturer AND Model are still missing (truly
   unusable rows).
7. Reset index cleanly.
"""

import pandas as pd

# Columns that must be numeric in the final schema
NUMERIC_COLUMNS = [
    "BatterykWh", "Rangekm", "PriceINR",
    "ChargingTimeHours", "EnergykWh",
    "OperatingCostINR", "RevenueINR", "ProfitINR",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, fill, coerce and enrich. Returns a NEW dataframe."""
    df = df.copy()

    # ── 1. Strip whitespace from string columns ────────────────────
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.astype(str).str.strip())

    # ── 2. Fill missing text columns with "Unknown" ────────────────
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")
        # pandas NA in object cols can also show as the literal string "nan"
        df[col] = df[col].replace({"nan": "Unknown", "<NA>": "Unknown"})

    # ── 3. Fill missing numeric columns with median ────────────────
    for col in df.select_dtypes(include="number").columns:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # ── 4. Coerce known numeric columns to float ───────────────────
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # After coercion some rows may be NaN again → fill with median
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())

    # ── 5. Derive ProfitINR if not already present ─────────────────
    if "ProfitINR" not in df.columns or df["ProfitINR"].isna().all():
        if "RevenueINR" in df.columns and "OperatingCostINR" in df.columns:
            df["ProfitINR"] = df["RevenueINR"] - df["OperatingCostINR"]

    # ── 6. Drop rows where both Manufacturer AND Model are missing ──
    df = df.dropna(subset=["Manufacturer", "Model"], how="all")
    # Also drop rows that ended up as "Unknown" for BOTH
    mask = (df["Manufacturer"] == "Unknown") & (df["Model"] == "Unknown")
    df = df[~mask]

    # ── 7. Clean reset ──────────────────────────────────────────────
    df.reset_index(drop=True, inplace=True)
    return df