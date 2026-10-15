"""Web scraper: collects product listings from a paginated e-commerce site."""
import logging
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import config

log = logging.getLogger(__name__)


def build_session() -> requests.Session:
    """Create a session with automatic retries and exponential backoff."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": config.USER_AGENT})
    return session


def parse_products(html: str, scraped_at: str) -> list[dict]:
    """Extract product records from one listing page's HTML."""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for card in soup.select("article.product_pod"):
        link = card.h3.a
        price_tag = card.select_one("p.price_color")
        rating_tag = card.select_one("p.star-rating")
        stock_tag = card.select_one("p.availability")
        records.append({
            "title": link.get("title") if link else None,
            "price": price_tag.get_text() if price_tag else None,
            "rating": rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else None,
            "availability": stock_tag.get_text() if stock_tag else None,
            "product_url": urljoin(config.SITE_ROOT, link["href"]) if link else None,
            "scraped_at": scraped_at,
        })
    return records


def scrape(max_pages: Optional[int] = None) -> pd.DataFrame:
    """Scrape all listing pages and return the raw (uncleaned) data."""
    max_pages = max_pages or config.MAX_PAGES
    session = build_session()
    scraped_at = datetime.now().isoformat(timespec="seconds")
    all_records: list[dict] = []

    for page in range(1, max_pages + 1):
        url = config.BASE_URL.format(page)
        try:
            resp = session.get(url, timeout=config.TIMEOUT_SEC)
            if resp.status_code == 404:
                log.info("Page %d not found - reached the end.", page)
                break
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.error("Failed on page %d: %s", page, exc)
            continue

        records = parse_products(resp.text, scraped_at)
        all_records.extend(records)
        log.info("Page %d: %d products (total %d)", page, len(records), len(all_records))
        time.sleep(config.REQUEST_DELAY_SEC)

    return pd.DataFrame(all_records)
