"""Pandas cleaning pipeline: missing values, duplicates, standardization."""
import logging
import re

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
REQUIRED_COLS = ["title", "price", "product_url"]


def _parse_price(value) -> float:
    """'Â£51.77' / '£51.77' / '$51.77' -> 51.77 (NaN if unparseable)."""
    if pd.isna(value):
        return np.nan
    match = re.search(r"\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else np.nan


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean_df, report) where report summarises every cleaning step."""
    report = {"rows_in": len(df)}
    df = df.copy()

    # 1. Standardize text: trim whitespace, collapse spaces, treat blanks as missing
    for col in ["title", "rating", "availability", "product_url"]:
        df[col] = (df[col].astype("string").str.strip()
                   .str.replace(r"\s+", " ", regex=True)
                   .replace("", pd.NA))

    # 2. Convert data types
    df["price"] = df["price"].map(_parse_price)
    df["rating"] = df["rating"].str.lower().map(RATING_MAP).astype("Float64")
    df["in_stock"] = df["availability"].str.contains("in stock", case=False, na=False)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")
    df["scrape_date"] = df["scraped_at"].dt.date.astype("string")

    # 3. Handle missing values
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLS)                  # unusable rows
    report["dropped_missing_required"] = before - len(df)

    report["missing_ratings_filled"] = int(df["rating"].isna().sum())
    df["rating"] = df["rating"].fillna(df["rating"].median()).round().astype("Int64")

    df["availability"] = df["availability"].fillna("Unknown")

    # 4. Remove duplicates (same product listed more than once)
    before = len(df)
    df = df.drop_duplicates(subset=["product_url"], keep="first")
    report["duplicates_removed"] = before - len(df)

    # 5. Remove invalid prices (negative / zero)
    before = len(df)
    df = df[df["price"] > 0]
    report["invalid_prices_removed"] = before - len(df)

    df = df.sort_values("title").reset_index(drop=True)
    report["rows_out"] = len(df)
    log.info("Cleaning report: %s", report)
    return df, report
