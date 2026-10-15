"""Central configuration for the scraper pipeline."""
from pathlib import Path

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"  # practice e-commerce site (scraping allowed)
SITE_ROOT = "https://books.toscrape.com/catalogue/"
MAX_PAGES = 50
REQUEST_DELAY_SEC = 1.0          # polite delay between requests
TIMEOUT_SEC = 15
USER_AGENT = "Mozilla/5.0 (compatible; EcomDataBot/1.0; +portfolio-project)"

OUTPUT_DIR = Path("data/output")
DB_PATH = OUTPUT_DIR / "products.db"
TABLE_NAME = "products"
