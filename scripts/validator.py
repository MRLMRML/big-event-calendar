"""Cross-validation engine for event verification."""

import hashlib
from datetime import datetime
from typing import Optional
from scrapers.base import RawEvent
from scripts.utils import (
    logger, now_iso, load_config, load_events, save_events,
    generate_event_id, get_category_info
)


class EventValidator:
    def __init__(self):
        self.config = load_config().get("scraper", {})
        self.confirmed_threshold = self.config.get("confirmed_threshold", 0.8)
        self.min_sources = self.config.get("min_sources_for_confirmation", 3)

    def calculate_confidence(self, sources: list[dict], source_tier: int) -> float:
        tier_scores = {1: 1.0, 2: 0.8, 3: 0.5, 4: 0.2}
        tier_score = tier_scores.get(source_tier, 0.2)

        source_count = len(sources)
        count_score = min(source_count / 3, 1.0)

        titles = [s.get("headline", "").lower() for s in sources]
        consistency = 1.0 if len(set(titles)) <= max(1, len(titles) // 2) else 0.5

        confidence = (tier_score * 0.5) + (count_score * 0.3) + (consistency * 0.2)
        return round(confidence, 2)

    def determine_status(self, event: RawEvent, existing_sources: list[dict] = None) -> str:
        sources = existing_sources or []

        if event.source_tier == 1:
            return "confirmed"

        if event.source_tier == 3:
            if len(sources) >= self.min_sources:
                return "confirmed"
            return "potential"

        return "rumor"

    def check_contradiction(self, new_event: RawEvent, existing_event: dict) -> bool:
        if new_event.start_date and existing_event.get("start_date"):
            if new_event.start_date != existing_event["start_date"]:
                return True

        if new_event.country != "global" and existing_event.get("country") != "global":
            if new_event.country != existing_event.get("country"):
                return True

        return False

    def find_duplicate(self, new_event: RawEvent, events: list[dict]) -> Optional[dict]:
        for existing in events:
            if existing.get("category") != new_event.category:
                continue

            if self._titles_match(new_event.title, existing.get("title", "")):
                return existing

            if (new_event.start_date == existing.get("start_date") and
                new_event.country == existing.get("country")):
                if self._titles_similar(new_event.title, existing.get("title", "")):
                    return existing

        return None

    def _titles_match(self, title1: str, title2: str) -> bool:
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        if t1 == t2:
            return True

        t1_words = set(t1.split())
        t2_words = set(t2.split())
        if len(t1_words) > 2 and len(t2_words) > 2:
            overlap = len(t1_words & t2_words) / max(len(t1_words), len(t2_words))
            return overlap > 0.7

        return False

    def _titles_similar(self, title1: str, title2: str) -> bool:
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        t1_words = set(t1.split())
        t2_words = set(t2.split())

        if len(t1_words) < 2 or len(t2_words) < 2:
            return False

        overlap = len(t1_words & t2_words) / max(len(t1_words), len(t2_words))
        return overlap > 0.5

    def validate_and_store(self, raw_events: list[RawEvent]) -> dict:
        db = load_events()
        events = db.get("events", [])
        stats = {"new": 0, "updated": 0, "skipped": 0, "confirmed": 0}

        for raw in raw_events:
            existing = self.find_duplicate(raw, events)

            if existing:
                updated = self._update_existing(existing, raw)
                if updated:
                    stats["updated"] += 1
                else:
                    stats["skipped"] += 1
            else:
                new_event = self._create_event(raw, events)
                events.append(new_event)
                stats["new"] += 1
                if new_event["status"] == "confirmed":
                    stats["confirmed"] += 1

        db["events"] = events
        db["metadata"]["total_events"] = len(events)
        db["metadata"]["last_scraped_at"] = now_iso()
        save_events(db)

        logger.info(f"Validation complete: {stats}")
        return stats

    def _create_event(self, raw: RawEvent, existing_events: list[dict]) -> dict:
        event_id = generate_event_id(
            raw.title, raw.start_date, raw.category, raw.country
        )

        source_entry = {
            "name": raw.source_name,
            "url": raw.source_url,
            "retrieved_at": now_iso(),
            "label": "corroborating" if raw.source_tier >= 3 else "confirmed",
            "headline": raw.headline
        }

        official_source = None
        if raw.source_tier == 1:
            official_source = {
                "name": raw.source_name,
                "url": raw.source_url,
                "verified_at": now_iso()
            }

        status = self.determine_status(raw)

        return {
            "id": event_id,
            "title": raw.title,
            "category": raw.category,
            "country": raw.country,
            "region": raw.region,
            "scope": raw.scope,
            "start_date": raw.start_date,
            "end_date": raw.end_date,
            "status": status,
            "description": raw.description,
            "official_source": official_source,
            "media_sources": [source_entry],
            "tags": raw.tags,
            "changes": [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "scraped_count": 1,
            "last_scraped_at": now_iso()
        }

    def _update_existing(self, existing: dict, new_raw: RawEvent) -> bool:
        changed = False

        new_source = {
            "name": new_raw.source_name,
            "url": new_raw.source_url,
            "retrieved_at": now_iso(),
            "label": "corroborating" if new_raw.source_tier >= 3 else "confirmed",
            "headline": new_raw.headline
        }

        source_urls = [s.get("url") for s in existing.get("media_sources", [])]
        if new_source["url"] not in source_urls:
            existing.setdefault("media_sources", []).append(new_source)
            changed = True

        if new_raw.source_tier == 1 and not existing.get("official_source"):
            existing["official_source"] = {
                "name": new_raw.source_name,
                "url": new_raw.source_url,
                "verified_at": now_iso()
            }
            existing["status"] = "confirmed"
            changed = True

        if existing["status"] == "potential":
            source_count = len(existing.get("media_sources", []))
            if source_count >= self.min_sources:
                existing["status"] = "confirmed"
                changed = True

        if new_raw.start_date and new_raw.start_date != existing.get("start_date"):
            existing.setdefault("changes", []).append({
                "field": "start_date",
                "old_value": existing.get("start_date"),
                "new_value": new_raw.start_date,
                "reason": "Date update from source",
                "changed_at": now_iso(),
                "source": new_raw.source_name
            })
            existing["start_date"] = new_raw.start_date
            changed = True

        if changed:
            existing["updated_at"] = now_iso()
            existing["scraped_count"] = existing.get("scraped_count", 0) + 1
            existing["last_scraped_at"] = now_iso()

        return changed
