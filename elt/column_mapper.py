# etl/column_mapper.py
"""
Flexible column mapper.

Strategy
--------
1. Every incoming column name is normalised: lowered, all spaces/underscores/
   hyphens/dots removed.
2. That normalised key is looked up in SYNONYM_MAP → canonical name.
3. If a canonical name already exists in the dataframe it is NOT overwritten
   (so a file that already uses the standard names passes straight through).
4. After renaming, any still-missing canonical columns are added as NaN so the
   rest of the pipeline and dashboard never KeyError.

Canonical schema (what everything downstream expects)
-----------------------------------------------------
VehicleID | Manufacturer | Model | Segment | BatterykWh | Rangekm |
PriceINR  | City         | UsageType | LocationType |
ChargingTimeHours | EnergykWh | OperatingCostINR | RevenueINR | ProfitINR
"""

import re
import pandas as pd

# ---------------------------------------------------------------------------
# SYNONYM → CANONICAL mapping
# Keys   = normalised form  (lower, no spaces/underscores/hyphens/dots)
# Values = canonical column name the dashboard expects
# ---------------------------------------------------------------------------
SYNONYM_MAP = {
    # ── VehicleID ─────────────────────────────────────────────────────
    "vehicleid":            "VehicleID",
    "vid":                  "VehicleID",
    "carid":                "VehicleID",
    "evid":                 "VehicleID",
    "id":                   "VehicleID",

    # ── Manufacturer ──────────────────────────────────────────────────
    "manufacturer":         "Manufacturer",
    "brand":                "Manufacturer",
    "make":                 "Manufacturer",
    "company":              "Manufacturer",
    "maker":                "Manufacturer",
    "carmaker":             "Manufacturer",
    "automaker":            "Manufacturer",

    # ── Model ─────────────────────────────────────────────────────────
    "model":                "Model",
    "modelname":            "Model",
    "carmodel":             "Model",
    "evmodel":              "Model",
    "vehiclemodel":         "Model",

    # ── Segment ───────────────────────────────────────────────────────
    "segment":              "Segment",
    "category":             "Segment",
    "type":                 "Segment",
    "vehicletype":          "Segment",
    "vehiclesegment":       "Segment",
    "class":                "Segment",
    "bodytype":             "Segment",

    # ── BatterykWh ────────────────────────────────────────────────────
    "batterykwh":           "BatterykWh",
    "battery":              "BatterykWh",
    "batterysize":          "BatterykWh",
    "batterycapacity":      "BatterykWh",
    "kwh":                  "BatterykWh",
    "batteryunitkwh":       "BatterykWh",

    # ── Rangekm ───────────────────────────────────────────────────────
    "rangekm":              "Rangekm",
    "range":                "Rangekm",
    "rangeinkm":            "Rangekm",
    "evrange":              "Rangekm",
    "drivingrange":         "Rangekm",
    "rangeinkilometers":    "Rangekm",

    # ── PriceINR ──────────────────────────────────────────────────────
    "priceinr":             "PriceINR",
    "price":                "PriceINR",
    "exshowroompriceinr":   "PriceINR",
    "showroomprice":        "PriceINR",
    "listprice":            "PriceINR",
    "costprice":            "PriceINR",
    "mrp":                  "PriceINR",

    # ── City ──────────────────────────────────────────────────────────
    "city":                 "City",
    "location":             "City",
    "town":                 "City",
    "place":                "City",
    "registeredcity":       "City",

    # ── UsageType ─────────────────────────────────────────────────────
    "usagetype":            "UsageType",
    "usage":                "UsageType",
    "use":                  "UsageType",
    "purpose":              "UsageType",
    "vehicleuse":           "UsageType",

    # ── LocationType ──────────────────────────────────────────────────
    "locationtype":         "LocationType",
    "customerloctype":      "LocationType",
    "customerlocationtype": "LocationType",
    "areatype":             "LocationType",
    "urbanrural":           "LocationType",

    # ── ChargingTimeHours ─────────────────────────────────────────────
    "chargingtimehours":    "ChargingTimeHours",
    "chargingtime":         "ChargingTimeHours",
    "avgchargingtime":      "ChargingTimeHours",
    "avgchargingtimehours": "ChargingTimeHours",
    "chargetime":           "ChargingTimeHours",

    # ── EnergykWh ─────────────────────────────────────────────────────
    "energykwh":            "EnergykWh",
    "energyconsumedkwh":    "EnergykWh",
    "energyconsumption":    "EnergykWh",
    "energyused":           "EnergykWh",

    # ── OperatingCostINR ──────────────────────────────────────────────
    "operatingcostinr":     "OperatingCostINR",
    "operatingcost":        "OperatingCostINR",
    "opcost":               "OperatingCostINR",
    "maintenancecost":      "OperatingCostINR",
    "runcost":              "OperatingCostINR",
    "totalcost":            "OperatingCostINR",

    # ── RevenueINR ────────────────────────────────────────────────────
    "revenueinr":           "RevenueINR",
    "revenue":              "RevenueINR",
    "sales":                "RevenueINR",
    "salesinr":             "RevenueINR",
    "income":               "RevenueINR",
    "totalrevenue":         "RevenueINR",

    # ── ProfitINR ─────────────────────────────────────────────────────
    "profitinr":            "ProfitINR",
    "profit":               "ProfitINR",
    "netprofit":            "ProfitINR",
    "margin":               "ProfitINR",
    "profitmargin":         "ProfitINR",
}

# The full canonical set — used to pad missing columns with NaN
CANONICAL_COLUMNS = [
    "VehicleID", "Manufacturer", "Model", "Segment",
    "BatterykWh", "Rangekm", "PriceINR", "City",
    "UsageType", "LocationType", "ChargingTimeHours",
    "EnergykWh", "OperatingCostINR", "RevenueINR", "ProfitINR",
]


def _normalise(name: str) -> str:
    """Lower-case and strip spaces, underscores, hyphens, dots."""
    return re.sub(r"[\s_\-\.]+", "", str(name)).lower()


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename *any* reasonably-named EV column to the canonical schema.

    Returns a NEW dataframe (original is not mutated).
    """
    df = df.copy()

    # Canonical names already present → do NOT overwrite them
    already_canonical = set(df.columns) & set(CANONICAL_COLUMNS)

    rename_map = {}
    for col in df.columns:
        if col in already_canonical:
            continue                               # already correct
        norm = _normalise(col)
        target = SYNONYM_MAP.get(norm)
        if target and target not in already_canonical and target not in rename_map.values():
            rename_map[col] = target

    df.rename(columns=rename_map, inplace=True)

    # Pad any missing canonical columns with NaN
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    return df