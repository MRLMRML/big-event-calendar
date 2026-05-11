import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class HumanitarianScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(world health|who |unicef|red cross|unhcr)",
        r"(refugee|displacement|humanitarian|crisis)",
        r"(world day|international day|awareness day)",
        r"(climate|cop\d|paris agreement|carbon)",
        r"(earth day|environment|sustainability)",
        r"(human rights|equality|gender|diversity)",
        r"(pandemic|epidemic|outbreak|health emergency)",
    ]

    KNOWN_ANNUAL_EVENTS = {
        "world health day": ("04-07", "WHO"),
        "world refugee day": ("06-20", "UNHCR"),
        "international women's day": ("03-08", "UN"),
        "earth day": ("04-22", "Earth Day Network"),
        "world environment day": ("06-05", "UNEP"),
        "human rights day": ("12-10", "UN"),
        "world aids day": ("12-01", "UNAIDS"),
        "world water day": ("03-22", "UN"),
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
                    category="humanitarian",
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

        for item in soup.select("article, .event-card, .day-item"):
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
                    category="humanitarian",
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
        if re.search(r"(health|who|pandemic|epidemic|outbreak)", text):
            return "health"
        if re.search(r"(refugee|displacement|unhcr)", text):
            return "un_day"
        if re.search(r"(climate|cop|paris|carbon|environment)", text):
            return "climate"
        if re.search(r"(rights|equality|gender|diversity)", text):
            return "human_rights"
        return "other"
