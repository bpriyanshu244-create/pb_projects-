import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import cleaner, exporter

RAW = Path(__file__).parent.parent / "data" / "sample_raw.csv"


@pytest.fixture
def result():
    return cleaner.clean(pd.read_csv(RAW))


def test_duplicates_removed(result):
    df, report = result
    assert report["duplicates_removed"] == 1
    assert df["product_url"].is_unique


def test_missing_required_dropped(result):
    df, report = result
    assert report["dropped_missing_required"] == 2   # no title, unparseable price
    assert df["title"].notna().all() and df["price"].notna().all()


def test_price_is_numeric(result):
    df, _ = result
    assert pd.api.types.is_float_dtype(df["price"])
    assert df.loc[df["title"] == "A Light in the Attic", "price"].iloc[0] == 51.77


def test_text_standardized_and_rating_filled(result):
    df, _ = result
    assert "A Light in the Attic" in df["title"].values
    assert df["rating"].notna().all()


def test_stock_flag(result):
    df, _ = result
    assert not df.loc[df["title"] == "Out of Print Gem", "in_stock"].iloc[0]


def test_sql_export_is_idempotent(result, tmp_path):
    df, _ = result
    db = tmp_path / "t.db"
    exporter.to_sql(df, db)
    exporter.to_sql(df, db)                           # run twice, same day
    count = sqlite3.connect(db).execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == len(df)
