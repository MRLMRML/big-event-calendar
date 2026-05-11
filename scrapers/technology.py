import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class TechnologyScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(wwdc|google ?io|ces |mwc |e3 |gamescom|reinvent|build |gtc )",
        r"(keynote|launch event|product launch|unveil)",
        r"(iphone|pixel|galaxy|surface|playstation|xbox|switch)",
        r"(developer|conference|summit|expo)",
        r"(ai |artificial intelligence|machine learning|gpt|llm)",
    ]

    COMPANY_EVENTS = {
        "apple": "US", "google": "US", "microsoft": "US",
        "amazon": "US", "nvidia": "US", "meta": "US",
        "samsung": "KR", "sony": "JP", "huawei": "CN",
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
                    category="technology",
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

        for item in soup.select("article, .event-card, .conference-item"):
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
                    category="technology",
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
        if re.search(r"(conference|summit|expo|wwdc|io |ces |mwc )", text):
            return "conference"
        if re.search(r"(launch|unveil|announce|reveal)", text):
            return "product_launch"
        if re.search(r"(developer|sdk|api|framework)", text):
            return "developer_event"
        if re.search(r"(game|gaming|playstation|xbox|switch|steam)", text):
            return "gaming"
        if re.search(r"(ai |artificial intelligence|machine learning|gpt|llm)", text):
            return "ai"
        return "other"

    def _detect_country(self, text: str, source: dict) -> str:
        for company, code in self.COMPANY_EVENTS.items():
            if company in text:
                return code

        source_countries = source.get("countries", ["US"])
        return source_countries[0] if source_countries else "US"
