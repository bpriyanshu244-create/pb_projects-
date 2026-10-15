"""Entry point.

Examples:
  python main.py                         # scrape all pages once
  python main.py --pages 3               # quick test run
  python main.py --daily 09:00           # run automatically every day at 09:00
  python main.py --input-csv data/sample_raw.csv   # skip scraping, clean a raw file
"""
import argparse
import logging
import time

import pandas as pd

from src import cleaner, exporter, scraper


def run_pipeline(pages=None, input_csv=None):
    raw = pd.read_csv(input_csv) if input_csv else scraper.scrape(max_pages=pages)
    if raw.empty:
        logging.warning("No data collected - aborting.")
        return
    clean_df, report = cleaner.clean(raw)
    exporter.to_csv(clean_df)
    exporter.to_sql(clean_df)
    print("\n=== Pipeline summary ===")
    for key, value in report.items():
        print(f"{key:28}: {value}")


def main():
    parser = argparse.ArgumentParser(description="E-commerce scraper & clean-up tool")
    parser.add_argument("--pages", type=int, help="limit number of pages")
    parser.add_argument("--daily", metavar="HH:MM", help="schedule a daily run")
    parser.add_argument("--input-csv", help="clean an existing raw CSV instead of scraping")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log")])

    if args.daily:
        import schedule
        schedule.every().day.at(args.daily).do(run_pipeline, pages=args.pages)
        logging.info("Scheduled daily run at %s. Press Ctrl+C to stop.", args.daily)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_pipeline(args.pages, args.input_csv)


if __name__ == "__main__":
    main()
