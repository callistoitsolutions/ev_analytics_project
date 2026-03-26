# etl/mysql_uploader.py
"""
Dual-mode database layer
-------------------------
Priority 1 – MySQL   : if  config/config.yaml exists AND PyMySQL + SQLAlchemy
                        are installed, connect to the MySQL server defined there.
Priority 2 – SQLite  : otherwise fall back to a local  ev_data.db  file that
                        lives next to this module.  Zero config, zero install.

The public API is the same either way:
    upload_to_mysql(df)   → int   (rows written)
    load_from_db()        → DataFrame
    get_row_count()       → int

MySQL config/config.yaml expected shape:
    database:
        host:     localhost
        user:     root
        password: secret
        name:     ev_project
"""

import os
import sqlite3
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_DB_PATH    = os.path.join(_THIS_DIR, "ev_data.db")          # SQLite fallback
_CONFIG     = os.path.join(os.path.dirname(_THIS_DIR), "config", "config.yaml")

# Columns we actually persist (whitelist – keeps the table tidy)
_ALLOWED_COLUMNS = [
    "VehicleID", "Manufacturer", "Model", "Segment",
    "BatterykWh", "Rangekm", "PriceINR", "City",
    "UsageType", "LocationType", "ChargingTimeHours",
    "EnergykWh", "OperatingCostINR", "RevenueINR", "ProfitINR",
]

# ---------------------------------------------------------------------------
# Engine detection
# ---------------------------------------------------------------------------

def _try_mysql_engine():
    """
    Return a SQLAlchemy engine if config.yaml + dependencies are available.
    Returns None otherwise (caller falls back to SQLite).
    """
    if not os.path.exists(_CONFIG):
        return None
    try:
        import yaml                                  # noqa: F401
        from sqlalchemy import create_engine         # noqa: F401
    except ImportError:
        return None

    try:
        import yaml
        from sqlalchemy import create_engine
        with open(_CONFIG, "r") as f:
            cfg = yaml.safe_load(f)
        db = cfg["database"]
        url = (
            f"mysql+pymysql://{db['user']}:{db['password']}"
            f"@{db['host']}:{db.get('port', 3306)}/{db['name']}"
        )
        engine = create_engine(url, pool_pre_ping=True)
        # Quick smoke-test: can we actually connect?
        with engine.connect():
            pass
        return engine
    except Exception:
        return None


# ---------------------------------------------------------------------------
# SQLite helpers (fallback)
# ---------------------------------------------------------------------------

_SQLITE_CREATE = """
CREATE TABLE IF NOT EXISTS ev_vehicles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID           TEXT,
    Manufacturer        TEXT,
    Model               TEXT,
    Segment             TEXT,
    BatterykWh          REAL,
    Rangekm             REAL,
    PriceINR            REAL,
    City                TEXT,
    UsageType           TEXT,
    LocationType        TEXT,
    ChargingTimeHours   REAL,
    EnergykWh           REAL,
    OperatingCostINR    REAL,
    RevenueINR          REAL,
    ProfitINR           REAL
);
"""


def _sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(_SQLITE_CREATE)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def upload_to_mysql(df: pd.DataFrame) -> int:
    """
    Persist the dataframe.

    * MySQL path  : DELETE existing rows first (idempotent re-upload), then
                    INSERT.  This matches the behaviour the user's original code
                    expected.
    * SQLite path : REPLACE all rows (drop + insert) so repeated saves of the
                    same file don't create duplicates.

    Returns the number of rows written.
    """
    if df.empty:
        raise ValueError("Cannot upload an empty dataframe.")

    # Keep only whitelisted columns that exist
    cols = [c for c in _ALLOWED_COLUMNS if c in df.columns]
    df_save = df[cols].copy()

    engine = _try_mysql_engine()

    # ── MySQL ─────────────────────────────────────────────────────
    if engine is not None:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM ev_data"))
            conn.commit()
        df_save.to_sql("ev_data", engine, if_exists="append", index=False)
        return len(df_save)

    # ── SQLite fallback ───────────────────────────────────────────
    conn = _sqlite_conn()
    try:
        conn.execute("DELETE FROM ev_vehicles;")   # clear old data
        conn.commit()
        df_save.to_sql("ev_vehicles", conn, if_exists="append", index=False)
        conn.commit()
        return len(df_save)
    finally:
        conn.close()


def load_from_db() -> pd.DataFrame:
    """
    Read all rows back from whichever backend is available.
    Returns an empty DataFrame with canonical columns if nothing is stored yet.
    """
    engine = _try_mysql_engine()

    # ── MySQL ─────────────────────────────────────────────────────
    if engine is not None:
        try:
            df = pd.read_sql_query("SELECT * FROM ev_data;", engine)
            df.drop(columns=["id"], errors="ignore", inplace=True)
            return df
        except Exception:
            return pd.DataFrame(columns=_ALLOWED_COLUMNS)

    # ── SQLite fallback ───────────────────────────────────────────
    if not os.path.exists(_DB_PATH):
        return pd.DataFrame(columns=_ALLOWED_COLUMNS)

    conn = _sqlite_conn()
    try:
        df = pd.read_sql_query("SELECT * FROM ev_vehicles;", conn)
        df.drop(columns=["id"], errors="ignore", inplace=True)
        return df
    except Exception:
        return pd.DataFrame(columns=_ALLOWED_COLUMNS)
    finally:
        conn.close()


def get_row_count() -> int:
    """Total rows currently stored."""
    engine = _try_mysql_engine()

    if engine is not None:
        try:
            result = pd.read_sql_query("SELECT COUNT(*) as cnt FROM ev_data;", engine)
            return int(result["cnt"].iloc[0])
        except Exception:
            return 0

    if not os.path.exists(_DB_PATH):
        return 0

    conn = _sqlite_conn()
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM ev_vehicles;")
        return cursor.fetchone()[0]
    except Exception:
        return 0
    finally:
        conn.close()