"""
EV Dashboard Setup Script
Run this to create all necessary files automatically
"""

import os

# Create etl directory
os.makedirs('elt', exist_ok=True)

# Create __init__.py
with open('elt/__init__.py', 'w') as f:
    f.write('''"""
ETL Package for EV Analytics Dashboard
"""

from .column_mapper import map_columns
from .data_cleaner import clean_data
from .mysql_uploader import upload_to_mysql, load_from_db, get_row_count

__all__ = [
    'map_columns',
    'clean_data', 
    'upload_to_mysql',
    'load_from_db',
    'get_row_count'
]
''')

print("✅ Created elt/__init__.py")

# Create column_mapper.py
with open('elt/column_mapper.py', 'w') as f:
    f.write('''import re
import pandas as pd

SYNONYM_MAP = {
    "vehicleid": "VehicleID", "vid": "VehicleID", "id": "VehicleID",
    "manufacturer": "Manufacturer", "brand": "Manufacturer", "make": "Manufacturer",
    "model": "Model", "segment": "Segment", "category": "Segment",
    "batterykwh": "BatterykWh", "battery": "BatterykWh",
    "rangekm": "Rangekm", "range": "Rangekm",
    "priceinr": "PriceINR", "price": "PriceINR", "exshowroompriceinr": "PriceINR",
    "city": "City", "location": "City",
    "usagetype": "UsageType", "usage": "UsageType",
    "locationtype": "LocationType", "customerlocationtype": "LocationType",
    "chargingtimehours": "ChargingTimeHours", "chargingtime": "ChargingTimeHours",
    "energykwh": "EnergykWh", "energyconsumedkwh": "EnergykWh",
    "operatingcostinr": "OperatingCostINR", "operatingcost": "OperatingCostINR",
    "revenueinr": "RevenueINR", "revenue": "RevenueINR",
    "profitinr": "ProfitINR", "profit": "ProfitINR",
}

CANONICAL_COLUMNS = [
    "VehicleID", "Manufacturer", "Model", "Segment",
    "BatterykWh", "Rangekm", "PriceINR", "City",
    "UsageType", "LocationType", "ChargingTimeHours",
    "EnergykWh", "OperatingCostINR", "RevenueINR", "ProfitINR",
]

def _normalise(name: str) -> str:
    return re.sub(r"[\\s_\\-\\.]+", "", str(name)).lower()

def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    already_canonical = set(df.columns) & set(CANONICAL_COLUMNS)
    rename_map = {}
    for col in df.columns:
        if col in already_canonical:
            continue
        norm = _normalise(col)
        target = SYNONYM_MAP.get(norm)
        if target and target not in already_canonical and target not in rename_map.values():
            rename_map[col] = target
    df.rename(columns=rename_map, inplace=True)
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df
''')

print("✅ Created elt/column_mapper.py")

# Create data_cleaner.py
with open('elt/data_cleaner.py', 'w') as f:
    f.write('''import pandas as pd

NUMERIC_COLUMNS = [
    "BatterykWh", "Rangekm", "PriceINR",
    "ChargingTimeHours", "EnergykWh",
    "OperatingCostINR", "RevenueINR", "ProfitINR",
]

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Strip whitespace
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.astype(str).str.strip())
    
    # Fill text columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")
        df[col] = df[col].replace({"nan": "Unknown", "<NA>": "Unknown"})
    
    # Fill numeric columns
    for col in df.select_dtypes(include="number").columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    
    # Coerce numeric
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
    
    # Calculate profit
    if "ProfitINR" not in df.columns or df["ProfitINR"].isna().all():
        if "RevenueINR" in df.columns and "OperatingCostINR" in df.columns:
            df["ProfitINR"] = df["RevenueINR"] - df["OperatingCostINR"]
    
    # Drop unusable rows
    df = df.dropna(subset=["Manufacturer", "Model"], how="all")
    mask = (df["Manufacturer"] == "Unknown") & (df["Model"] == "Unknown")
    df = df[~mask]
    
    df.reset_index(drop=True, inplace=True)
    return df
''')

print("✅ Created elt/data_cleaner.py")

# Create mysql_uploader.py
with open('elt/mysql_uploader.py', 'w') as f:
    f.write('''import os
import sqlite3
import pandas as pd

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_THIS_DIR, "ev_data.db")
_CONFIG = os.path.join(os.path.dirname(_THIS_DIR), "config", "config.yaml")

_ALLOWED_COLUMNS = [
    "VehicleID", "Manufacturer", "Model", "Segment",
    "BatterykWh", "Rangekm", "PriceINR", "City",
    "UsageType", "LocationType", "ChargingTimeHours",
    "EnergykWh", "OperatingCostINR", "RevenueINR", "ProfitINR",
]

def _try_mysql_engine():
    if not os.path.exists(_CONFIG):
        return None
    try:
        import yaml
        from sqlalchemy import create_engine
        with open(_CONFIG, "r") as f:
            cfg = yaml.safe_load(f)
        db = cfg["database"]
        url = f"mysql+pymysql://{db['user']}:{db['password']}@{db['host']}:{db.get('port', 3306)}/{db['name']}"
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect():
            pass
        return engine
    except:
        return None

_SQLITE_CREATE = """
CREATE TABLE IF NOT EXISTS ev_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID TEXT, Manufacturer TEXT, Model TEXT, Segment TEXT,
    BatterykWh REAL, Rangekm REAL, PriceINR REAL, City TEXT,
    UsageType TEXT, LocationType TEXT, ChargingTimeHours REAL,
    EnergykWh REAL, OperatingCostINR REAL, RevenueINR REAL, ProfitINR REAL
);
"""

def _sqlite_conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(_SQLITE_CREATE)
    conn.commit()
    return conn

def upload_to_mysql(df: pd.DataFrame) -> int:
    if df.empty:
        raise ValueError("Cannot upload an empty dataframe.")
    cols = [c for c in _ALLOWED_COLUMNS if c in df.columns]
    df_save = df[cols].copy()
    engine = _try_mysql_engine()
    
    if engine is not None:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM ev_data"))
            conn.commit()
        df_save.to_sql("ev_data", engine, if_exists="append", index=False)
        return len(df_save)
    
    conn = _sqlite_conn()
    try:
        conn.execute("DELETE FROM ev_vehicles;")
        conn.commit()
        df_save.to_sql("ev_vehicles", conn, if_exists="append", index=False)
        conn.commit()
        return len(df_save)
    finally:
        conn.close()

def load_from_db() -> pd.DataFrame:
    engine = _try_mysql_engine()
    if engine is not None:
        try:
            df = pd.read_sql_query("SELECT * FROM ev_data;", engine)
            df.drop(columns=["id"], errors="ignore", inplace=True)
            return df
        except:
            return pd.DataFrame(columns=_ALLOWED_COLUMNS)
    if not os.path.exists(_DB_PATH):
        return pd.DataFrame(columns=_ALLOWED_COLUMNS)
    conn = _sqlite_conn()
    try:
        df = pd.read_sql_query("SELECT * FROM ev_vehicles;", conn)
        df.drop(columns=["id"], errors="ignore", inplace=True)
        return df
    except:
        return pd.DataFrame(columns=_ALLOWED_COLUMNS)
    finally:
        conn.close()

def get_row_count() -> int:
    engine = _try_mysql_engine()
    if engine is not None:
        try:
            result = pd.read_sql_query("SELECT COUNT(*) as cnt FROM ev_data;", engine)
            return int(result["cnt"].iloc[0])
        except:
            return 0
    if not os.path.exists(_DB_PATH):
        return 0
    conn = _sqlite_conn()
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM ev_vehicles;")
        return cursor.fetchone()[0]
    except:
        return 0
    finally:
        conn.close()
''')

print("✅ Created etl/mysql_uploader.py")

print("\n" + "="*50)
print("🎉 Setup Complete!")
print("="*50)
print("\nAll ETL files created successfully!")
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Upload your CSV/Excel file")
print("3. Click 'Save to Database'")
print("\n✅ No more warnings!")