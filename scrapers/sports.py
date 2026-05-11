import re
from datetime import datetime, timedelta
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import logger, now_iso


class SportsScraper(BaseScraper):
    SPORT_PATTERNS = {
        "olympics": r"(olympic|olympiad|summer games|winter games)",
        "world_cup": r"(world cup|fifa|copa am[eé]rica|euro \d{4})",
        "basketball": r"(nba finals|basketball|fiba)",
        "tennis": r"(grand slam|wimbledon|roland garros|us open|australian open)",
        "formula1": r"(formula 1|f1|grand prix)",
        "cricket": r"(cricket|icc|t20|ipl)",
        "rugby": r"(rugby|six nations)",
    }

    def parse_rss_entries(self, entries: list[dict], source: dict) -> list[RawEvent]:
        events = []
        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            for sport_type, pattern in self.SPORT_PATTERNS.items():
                if re.search(pattern, text, re.IGNORECASE):
                    event = RawEvent(
                        title=title,
                        start_date=self._extract_date(entry),
                        end_date=None,
                        category="sports",
                        country=self._guess_country(source, text),
                        region="global",
                        scope="global" if "world" in text or "olympic" in text else "national",
                        description=summary[:500],
                        source_name=source["name"],
                        source_url=entry.get("link", source["url"]),
                        source_tier=source.get("tier", 3),
                        source_type=source.get("type", "journalistic"),
                        headline=title,
                        tags=[sport_type]
                    )
                    events.append(event)
                    break

        return events

    def parse_web_page(self, html: str, source: dict) -> list[RawEvent]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        events = []

        for item in soup.select("article, .event-item, .schedule-item, .match-card"):
            title_el = item.select_one("h2, h3, .title, .event-name")
            date_el = item.select_one("time, .date, .event-date")
            desc_el = item.select_one("p, .description, .event-desc")

            if title_el:
                title = title_el.get_text(strip=True)
                date_str = date_el.get("datetime", "") if date_el else ""
                if not date_str and date_el:
                    date_str = date_el.get_text(strip=True)

                events.append(RawEvent(
                    title=title,
                    start_date=date_str or now_iso(),
                    end_date=None,
                    category="sports",
                    country=self._guess_country(source, title.lower()),
                    region="global",
                    scope="national",
                    description=desc_el.get_text(strip=True)[:500] if desc_el else "",
                    source_name=source["name"],
                    source_url=source["url"],
                    source_tier=source.get("tier", 3),
                    source_type=source.get("type", "journalistic"),
                    headline=title
                ))

        return events

    def _extract_date(self, entry: dict) -> str:
        published = entry.get("published", "")
        if published:
            try:
                return datetime.fromisoformat(published.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except ValueError:
                pass
        return datetime.now().strftime("%Y-%m-%d")

    def _guess_country(self, source: dict, text: str) -> str:
        country_hints = {
            "US": ["nba", "nfl", "mlb", "super bowl", "usa", "america"],
            "GB": ["premier league", "wimbledon", "england", "british"],
            "FR": ["tour de france", "roland garros", "french"],
            "DE": ["bundesliga", "german"],
            "IN": ["ipl", "cricket", "india"],
            "JP": ["j-league", "japan"],
            "BR": ["brasileirão", "brazil"],
            "IT": ["serie a", "italian"],
            "ES": ["la liga", "spain"],
        }
        for code, hints in country_hints.items():
            if any(h in text for h in hints):
                return code

        source_countries = source.get("countries", ["global"])
        return source_countries[0] if source_countries else "global"
