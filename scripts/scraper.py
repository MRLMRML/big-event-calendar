"""Main scraper orchestrator."""

from scrapers.base import RawEvent
from scrapers.sports import SportsScraper
from scrapers.space import SpaceScraper
from scrapers.politics import PoliticsScraper
from scrapers.technology import TechnologyScraper
from scrapers.culture import CultureScraper
from scrapers.economics import EconomicsScraper
from scrapers.humanitarian import HumanitarianScraper
from scrapers.astronomy import AstronomyScraper
from scripts.validator import EventValidator
from scripts.utils import logger, load_sources, load_config, now_iso


SCRAPER_MAP = {
    "sports": SportsScraper,
    "space": SpaceScraper,
    "politics": PoliticsScraper,
    "technology": TechnologyScraper,
    "culture": CultureScraper,
    "economics": EconomicsScraper,
    "humanitarian": HumanitarianScraper,
    "astronomy": AstronomyScraper,
}


def get_scraper_sources(category: str) -> list:
    all_sources = load_sources().get("sources", {})
    cat_sources = all_sources.get(category, {})
    sources = cat_sources.get("official", []) + cat_sources.get("journalistic", [])
    return sources


def scrape_category(category: str) -> list[RawEvent]:
    if category not in SCRAPER_MAP:
        logger.error(f"Unknown category: {category}")
        return []

    sources = get_scraper_sources(category)
    if not sources:
        logger.warning(f"No sources configured for {category}")
        return []

    scraper_cls = SCRAPER_MAP[category]
    scraper = scraper_cls(category, sources)
    return scraper.scrape()


def scrape_all(categories: list[str] = None) -> dict:
    target_categories = categories or list(SCRAPER_MAP.keys())
    all_raw_events = []

    for category in target_categories:
        logger.info(f"Scraping category: {category}")
        try:
            events = scrape_category(category)
            all_raw_events.extend(events)
            logger.info(f"Found {len(events)} raw events for {category}")
        except Exception as e:
            logger.error(f"Error scraping {category}: {e}")

    logger.info(f"Total raw events collected: {len(all_raw_events)}")

    validator = EventValidator()
    stats = validator.validate_and_store(all_raw_events)

    return stats


def scrape_country(country_code: str) -> dict:
    all_raw_events = []

    for category in SCRAPER_MAP.keys():
        sources = get_scraper_sources(category)
        country_sources = [
            s for s in sources
            if country_code in s.get("countries", []) or "global" in s.get("countries", [])
        ]

        if country_sources:
            scraper_cls = SCRAPER_MAP[category]
            scraper = scraper_cls(category, country_sources)
            events = scraper.scrape()
            all_raw_events.extend(events)

    validator = EventValidator()
    return validator.validate_and_store(all_raw_events)
