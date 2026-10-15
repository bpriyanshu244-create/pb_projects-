"""Export cleaned data to CSV and a SQL database (SQLite)."""
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from . import config

log = logging.getLogger(__name__)


def to_csv(df: pd.DataFrame, out_dir: Path = config.OUTPUT_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = df["scrape_date"].iloc[0] if len(df) else "empty"
    path = out_dir / f"products_{stamp}.csv"
    df.to_csv(path, index=False)
    log.info("CSV saved: %s (%d rows)", path, len(df))
    return path


def to_sql(df: pd.DataFrame, db_path: Path = config.DB_PATH,
           table: str = config.TABLE_NAME) -> Path:
    """Append to SQLite; re-running on the same day replaces that day's rows (idempotent)."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out["scraped_at"] = out["scraped_at"].astype(str)
    out["scrape_date"] = out["scrape_date"].astype(object)
    for col in ["title", "availability", "product_url"]:
        out[col] = out[col].astype(object)
    out["rating"] = out["rating"].astype(object)
    with sqlite3.connect(db_path) as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if exists:
            dates = tuple(out["scrape_date"].unique())
            marks = ",".join("?" * len(dates))
            conn.execute(f"DELETE FROM {table} WHERE scrape_date IN ({marks})", dates)
        out.to_sql(table, conn, if_exists="append", index=False)
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_url ON {table}(product_url)")
    log.info("SQL saved: %s -> table '%s' (%d rows)", db_path, table, len(out))
    return db_path
