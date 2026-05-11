import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import logger, now_iso


class SpaceScraper(BaseScraper):
    LAUNCH_PATTERNS = [
        r"(launch|liftoff|blastoff|rocket)",
        r"(crew dragon|soyuz|starliner|artemis|starship)",
        r"(iss|space station|orbit)",
        r"(satellite|deployment|mission)",
        r"(mars|moon|lunar|deep space|jupiter|saturn)",
        r"(james webb|hubble|telescope)",
    ]

    def parse_rss_entries(self, entries: list[dict], source: dict) -> list[RawEvent]:
        events = []
        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            if any(re.search(p, text, re.IGNORECASE) for p in self.LAUNCH_PATTERNS):
                event_type = self._classify_event(text)
                events.append(RawEvent(
                    title=title,
                    start_date=self._extract_date(entry),
                    end_date=None,
                    category="space",
                    country=self._detect_country(source, text),
                    region="global",
                    scope="global" if "international" in text else "national",
                    description=summary[:500],
                    source_name=source["name"],
                    source_url=entry.get("link", source["url"]),
                    source_tier=source.get("tier", 3),
                    source_type=source.get("type", "journalistic"),
                    headline=title,
                    tags=[event_type]
                ))

        return events

    def parse_web_page(self, html: str, source: dict) -> list[RawEvent]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        events = []

        for item in soup.select("article, .launch-item, .mission-card, .event"):
            title_el = item.select_one("h2, h3, .title, .mission-name")
            date_el = item.select_one("time, .date, .launch-date")
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
                    category="space",
                    country=self._detect_country(source, title.lower()),
                    region="global",
                    scope="national",
                    description=desc_el.get_text(strip=True)[:500] if desc_el else "",
                    source_name=source["name"],
                    source_url=source["url"],
                    source_tier=source.get("tier", 3),
                    source_type=source.get("type", "journalistic"),
                    headline=title,
                    tags=[self._classify_event(title.lower())]
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
        if re.search(r"(launch|liftoff|blastoff)", text):
            return "rocket_launch"
        if re.search(r"(crew|astronaut|cosmonaut)", text):
            return "crewed_mission"
        if re.search(r"(satellite|deployment)", text):
            return "satellite"
        if re.search(r"(iss|space station)", text):
            return "space_station"
        if re.search(r"(mars|moon|deep space|jupiter|saturn)", text):
            return "deep_space"
        if re.search(r"(discover|found|detect)", text):
            return "discovery"
        return "other"

    def _detect_country(self, source: dict, text: str) -> str:
        agency_country = {
            "nasa": "US", "spacex": "US", "blue origin": "US",
            "roscosmos": "RU", "esa": "FR", "isro": "IN",
            "jaxa": "JP", "cnsa": "CN", "arianespace": "FR",
        }
        for agency, code in agency_country.items():
            if agency in text:
                return code

        source_countries = source.get("countries", ["global"])
        return source_countries[0] if source_countries else "global"
