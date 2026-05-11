import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class PoliticsScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(election|vote|ballot|poll)",
        r"(summit|conference|assembly|convention)",
        r"(inauguration|swearing.?in)",
        r"(g7|g20|g8|nato|un |cop\d|apec|brics)",
        r"(treaty|agreement|accord|pact)",
        r"(sanction|embargo|tariff)",
        r"(presidential|parliamentary|congressional|senate)",
    ]

    def parse_rss_entries(self, entries: list[dict], source: dict) -> list[RawEvent]:
        events = []
        for entry in entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            if any(re.search(p, text, re.IGNORECASE) for p in self.EVENT_PATTERNS):
                event_type = self._classify_event(text)
                events.append(RawEvent(
                    title=title,
                    start_date=self._extract_date(entry),
                    end_date=None,
                    category="politics",
                    country=self._detect_country(text, source),
                    region="global" if any(k in text for k in ["un ", "nato", "g7", "g20"]) else "national",
                    scope="global" if any(k in text for k in ["un ", "nato", "g7", "g20"]) else "national",
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

        for item in soup.select("article, .event-item, .summit-card"):
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
                    category="politics",
                    country=self._detect_country(title.lower(), source),
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
        if re.search(r"(election|vote|ballot|poll)", text):
            return "election"
        if re.search(r"(summit|conference|assembly)", text):
            return "summit"
        if re.search(r"(inauguration|swearing)", text):
            return "inauguration"
        if re.search(r"(treaty|agreement|accord|pact)", text):
            return "treaty"
        if re.search(r"(sanction|embargo)", text):
            return "sanctions"
        return "other"

    def _detect_country(self, text: str, source: dict) -> str:
        country_keywords = {
            "US": ["washington", "white house", "congress", "senate", "biden", "trump"],
            "GB": ["london", "parliament", "downing", "uk ", "british"],
            "FR": ["paris", "élysée", "french", "macron"],
            "DE": ["berlin", "german", "merz", "scholz"],
            "CN": ["beijing", "china", "chinese", "xi jinping"],
            "RU": ["moscow", "kremlin", "russia", "putin"],
            "IN": ["delhi", "india", "indian", "modi"],
            "JP": ["tokyo", "japan", "japanese"],
        }
        for code, keywords in country_keywords.items():
            if any(k in text for k in keywords):
                return code

        source_countries = source.get("countries", ["global"])
        return source_countries[0] if source_countries else "global"
