"""Base scraper class for all category scrapers."""

import time
import requests
import feedparser
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from scripts.utils import logger, now_iso, load_config


@dataclass
class RawEvent:
    title: str
    start_date: str
    end_date: Optional[str]
    category: str
    country: str
    region: str
    scope: str
    description: str
    source_name: str
    source_url: str
    source_tier: int
    source_type: str
    headline: Optional[str] = None
    location: Optional[str] = None
    tags: list = field(default_factory=list)
    raw_data: Optional[dict] = None


class BaseScraper(ABC):
    def __init__(self, category: str, sources: list):
        self.category = category
        self.sources = sources
        self.config = load_config().get("scraper", {})
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.get("user_agent", "BigEventCalendar/1.0")
        })

    def fetch_url(self, url: str, timeout: int = None) -> Optional[str]:
        timeout = timeout or self.config.get("request_timeout", 30)
        retries = self.config.get("max_retries", 3)

        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=timeout)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException as e:
                logger.warning(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(self.config.get("delay_between_requests", 2))

        return None

    def fetch_rss(self, url: str) -> list[dict]:
        try:
            feed = feedparser.parse(url)
            entries = []
            for entry in feed.entries[:20]:
                entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "tags": [t.get("term", "") for t in entry.get("tags", [])]
                })
            return entries
        except Exception as e:
            logger.error(f"RSS parse error for {url}: {e}")
            return []

    def parse_html(self, html: str, selectors: dict) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        result = {}
        for key, selector in selectors.items():
            el = soup.select_one(selector)
            result[key] = el.get_text(strip=True) if el else None
        return result

    def scrape_source(self, source: dict) -> list[RawEvent]:
        source_type = source.get("scraper_type", "web")
        url = source.get("rss_url") or source.get("url")

        if source_type == "rss":
            entries = self.fetch_rss(url)
            return self.parse_rss_entries(entries, source)
        else:
            html = self.fetch_url(url)
            if html:
                return self.parse_web_page(html, source)
            return []

    @abstractmethod
    def parse_rss_entries(self, entries: list[dict], source: dict) -> list[RawEvent]:
        pass

    @abstractmethod
    def parse_web_page(self, html: str, source: dict) -> list[RawEvent]:
        pass

    def scrape(self) -> list[RawEvent]:
        all_events = []
        for source in self.sources:
            if not source.get("active", True):
                continue
            logger.info(f"Scraping {source['name']} ({source['url']})")
            try:
                events = self.scrape_source(source)
                all_events.extend(events)
                logger.info(f"Found {len(events)} events from {source['name']}")
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")

            time.sleep(self.config.get("delay_between_requests", 2))

        return all_events
