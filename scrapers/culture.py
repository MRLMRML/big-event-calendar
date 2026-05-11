import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class CultureScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(oscar|academy award|grammy|emmy|golden globe|bafta|palme d)",
        r"(cannes|venice|sundance|toronto|berlin film festival|tiff)",
        r"(met gala|burning man|coachella|glastonbury|lollapalooza)",
        r"(nobel|booker|pulitzer|turner prize|mercury prize)",
        r"(biennale|art basel|documenta|frieze)",
        r"(festival|ceremony|awards|gala|exhibition)",
    ]

    COUNTRY_MAP = {
        "oscar": "US", "grammy": "US", "emmy": "US", "golden globe": "US",
        "cannes": "FR", "venice": "IT", "berlin": "DE",
        "met gala": "US", "burning man": "US", "coachella": "US",
        "nobel": "SE", "booker": "GB", "bafta": "GB",
        "biennale": "IT", "art basel": "CH",
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
                    category="culture",
                    country=self._detect_country(text, source),
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

        for item in soup.select("article, .event-card, .festival-item"):
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
                    category="culture",
                    country=self._detect_country(title.lower(), source),
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
        if re.search(r"(oscar|grammy|emmy|golden globe|bafta|nobel|booker|pulitzer)", text):
            return "awards"
        if re.search(r"(cannes|venice|sundance|toronto|berlin|tiff|festival)", text):
            return "film_festival"
        if re.search(r"(coachella|glastonbury|lollapalooza|burning man|music)", text):
            return "music_festival"
        if re.search(r"(biennale|art basel|documenta|frieze|exhibition)", text):
            return "art_exhibition"
        return "other"

    def _detect_country(self, text: str, source: dict) -> str:
        for keyword, code in self.COUNTRY_MAP.items():
            if keyword in text:
                return code

        source_countries = source.get("countries", ["global"])
        return source_countries[0] if source_countries else "global"
