import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class AstronomyScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(solar eclipse|lunar eclipse|eclipse)",
        r"(meteor shower|perseid|geminid|leonid|orionid)",
        r"(solstice|equinox|winter solstice|summer solstice)",
        r"(conjunction|opposition|alignment)",
        r"(comet|asteroid|near.?earth)",
        r"(aurora|borealis|northern lights)",
        r"(supermoon|blood moon|blue moon|harvest moon)",
    ]

    KNOWN_ANNUAL_EVENTS = {
        "perseid meteor shower": ("08-12", "imo.net"),
        "geminid meteor shower": ("12-13", "imo.net"),
        "leonid meteor shower": ("11-17", "imo.net"),
        "orionid meteor shower": ("10-21", "imo.net"),
        "summer solstice": ("06-21", "timeanddate.com"),
        "winter solstice": ("12-21", "timeanddate.com"),
        "spring equinox": ("03-20", "timeanddate.com"),
        "autumn equinox": ("09-22", "timeanddate.com"),
    }

    def parse_rss_entries(self, entries: list[dict], source: dict) -> list[RawEvent]:
        events = []
        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            if any(re.search(p, text, re.IGNORECASE) for p in self.EVENT_PATTERNS):
                events.append(RawEvent(
                    title=title,
                    start_date=self._extract_date(entry),
                    end_date=None,
                    category="astronomy",
                    country="global",
                    region="global",
                    scope="global",
                    description=summary[:500],
                    source_name=source["name"],
                    source_url=entry.get("link", source["url"]),
                    source_tier=source.get("tier", 3),
                    source_type=source.get("type", "journalistic"),
                    headline=title,
                    tags=[self._classify_event(text)]
                ))

        return events

    def parse_web_page(self, html: str, source: dict) -> list[RawEvent]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        events = []

        for item in soup.select("article, .event-card, .astronomy-event"):
            title_el = item.select_one("h2, h3, .title")
            date_el = item.select_one("time, .date")
            desc_el = item.select_one("p, .description")

            if title_el:
                title = title_el.get_text(strip=True)
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)

                events.append(RawEvent(
                    title=title,
                    start_date=date_str or now_iso(),
                    end_date=None,
                    category="astronomy",
                    country="global",
                    region="global",
                    scope="global",
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

    def _classify_event(self, text: str) -> str:
        if re.search(r"(solar eclipse)", text):
            return "solar_eclipse"
        if re.search(r"(lunar eclipse)", text):
            return "lunar_eclipse"
        if re.search(r"(meteor shower|perseid|geminid|leonid|orionid)", text):
            return "meteor_shower"
        if re.search(r"(solstice|equinox)", text):
            return "equinox"
        if re.search(r"(conjunction|opposition|alignment)", text):
            return "conjunction"
        if re.search(r"(comet|asteroid)", text):
            return "comet"
        return "other"
