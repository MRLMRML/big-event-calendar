import re
from datetime import datetime
from scrapers.base import BaseScraper, RawEvent
from scripts.utils import now_iso


class EconomicsScraper(BaseScraper):
    EVENT_PATTERNS = [
        r"(federal reserve|fed |ecb |boj |bank of england|rbi |pboc)",
        r"(interest rate|rate decision|monetary policy|fomc)",
        r"(davos|wef|world economic forum)",
        r"(gdp|inflation|cpi|unemployment|jobs report|nonfarm)",
        r"(ipo |initial public offering|listing|debut)",
        r"(bitcoin halving|halving|crypto summit)",
        r"(berkshire|hathaway|annual meeting|shareholder)",
        r"(trade deal|tariff|trade war|sanctions)",
    ]

    COUNTRY_MAP = {
        "federal reserve": "US", "fed ": "US", "fomc": "US",
        "ecb ": "FR", "european central": "FR",
        "boj ": "JP", "bank of japan": "JP",
        "bank of england": "GB", "boe ": "GB",
        "rbi ": "IN", "reserve bank of india": "IN",
        "pboc": "CN", "people's bank": "CN",
        "berkshire": "US",
        "davos": "CH",
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
                    category="economics",
                    country=self._detect_country(text, source),
                    region="global" if "davos" in text or "wef" in text else "national",
                    scope="global" if "davos" in text else "national",
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

        for item in soup.select("article, .event-card, .announcement"):
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
                    category="economics",
                    country=self._detect_country(title.lower(), source),
                    region="national",
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

    def _classify_event(self, text: str) -> str:
        if re.search(r"(fed |ecb |boj |interest rate|fomc|monetary)", text):
            return "central_bank"
        if re.search(r"(davos|wef|economic forum)", text):
            return "economic_summit"
        if re.search(r"(ipo |initial public offering|listing)", text):
            return "ipo"
        if re.search(r"(bitcoin|crypto|halving)", text):
            return "crypto"
        if re.search(r"(trade|tariff|sanctions)", text):
            return "trade"
        return "other"

    def _detect_country(self, text: str, source: dict) -> str:
        for keyword, code in self.COUNTRY_MAP.items():
            if keyword in text:
                return code

        source_countries = source.get("countries", ["global"])
        return source_countries[0] if source_countries else "global"
