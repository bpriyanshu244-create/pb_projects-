# Automated E-Commerce Data Scraper & Clean-Up Tool

An end-to-end data pipeline that **scrapes** product data from an e-commerce website, **cleans** it with
**Pandas**, and **exports** it to **CSV** and a **SQL (SQLite)** database — on a daily schedule, with no manual data entry.

**Tech stack:** Python · Requests · BeautifulSoup · Pandas · SQLite · Schedule · Pytest

## Pipeline

```
 Scrape (requests + BeautifulSoup)  →  Clean (Pandas)  →  Export (CSV + SQLite)  →  Daily scheduler
```

## Features

- **Robust scraping** – paginated crawling, retries with exponential backoff, request timeouts, polite delays, error logging
- **Data cleaning (Pandas)**
  - Handles missing values (drops unusable rows, imputes missing ratings with the median)
  - Removes duplicate products
  - Standardizes text (whitespace, casing), prices (`Â£51.77` → `51.77`), ratings (`"Three"` → `3`), stock status (→ boolean)
  - Produces a **cleaning report** (rows in/out, duplicates removed, etc.)
- **Dual export** – date-stamped CSV files and a SQLite table; re-running on the same day is **idempotent** (no duplicate rows)
- **Automation** – built-in daily scheduler (`--daily 09:00`)
- **Tested** – unit tests for cleaning logic and database export

## Project structure

```
ecom-scraper/
├── main.py              # CLI entry point + scheduler
├── src/
│   ├── config.py        # URLs, delays, paths
│   ├── scraper.py       # Web scraping
│   ├── cleaner.py       # Pandas cleaning pipeline
│   └── exporter.py      # CSV + SQL export
├── tests/test_cleaner.py
├── data/sample_raw.csv  # messy sample data for demo/tests
└── requirements.txt
```

## Setup & usage

```bash
pip install -r requirements.txt

python main.py --pages 3                        # quick scrape of 3 pages
python main.py                                  # scrape everything
python main.py --daily 09:00                    # run automatically every day at 09:00
python main.py --input-csv data/sample_raw.csv  # demo cleaning without internet
pytest                                          # run tests
```

Output is saved in `data/output/` (`products_YYYY-MM-DD.csv` and `products.db`).

### Query the database

```sql
SELECT title, price, rating FROM products WHERE in_stock = 1 ORDER BY price DESC LIMIT 10;
```

## Sample cleaning report

```
rows_in: 8 | dropped_missing_required: 2 | missing_ratings_filled: 1 | duplicates_removed: 1 | rows_out: 5
```

## Notes

Demo target is [books.toscrape.com](https://books.toscrape.com), a sandbox site built for practicing scraping.
Always check a site's `robots.txt` and Terms of Service before scraping real websites.
