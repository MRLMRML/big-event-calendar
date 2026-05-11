"""Shared utilities for Big Event Calendar."""

import json
import os
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "scraper.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("big-event-calendar")


def load_json(filepath: Path) -> dict:
    """Load JSON file safely."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {filepath}: {e}")
        return {}


def save_json(filepath: Path, data: dict, indent: int = 2) -> None:
    """Save JSON file with backup."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if file exists
    if filepath.exists():
        backup_path = filepath.with_suffix(".json.bak")
        try:
            backup_path.write_text(filepath.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def load_categories() -> dict:
    """Load categories configuration."""
    return load_json(DATA_DIR / "categories.json")


def load_countries() -> dict:
    """Load countries configuration."""
    return load_json(DATA_DIR / "countries.json")


def load_sources() -> dict:
    """Load sources configuration."""
    return load_json(DATA_DIR / "sources.json")


def load_config() -> dict:
    """Load global configuration."""
    return load_json(PROJECT_ROOT / "config.json")


def load_events() -> dict:
    """Load events database."""
    return load_json(DATA_DIR / "events.json")


def save_events(data: dict) -> None:
    """Save events database."""
    save_json(DATA_DIR / "events.json", data)


def generate_event_id(title: str, date: str, category: str, country: str = "global") -> str:
    """Generate a unique event ID."""
    # Normalize inputs
    title_slug = title.lower().strip().replace(" ", "_")[:30]
    country_code = country.lower()[:2]
    date_short = date.replace("-", "")[:8]

    # Create hash for uniqueness
    raw = f"{title}_{date}_{category}_{country}"
    hash_suffix = hashlib.md5(raw.encode()).hexdigest()[:6]

    return f"evt_{date_short}_{country_code}_{title_slug}_{hash_suffix}"


def now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    from dateutil.parser import parse
    try:
        return parse(date_str)
    except (ValueError, TypeError):
        return None


def format_date_display(date_str: str) -> str:
    """Format date for display."""
    dt = parse_date(date_str)
    if dt:
        return dt.strftime("%b %d, %Y")
    return date_str


def get_country_info(code: str) -> Optional[dict]:
    """Get country information by code."""
    countries = load_countries()
    for country in countries.get("countries", []):
        if country["code"] == code:
            return country
    return None


def get_category_info(category_id: str) -> Optional[dict]:
    """Get category information by ID."""
    categories = load_categories()
    for cat in categories.get("categories", []):
        if cat["id"] == category_id:
            return cat
    return None


def get_category_color(category_id: str) -> str:
    """Get category color."""
    cat = get_category_info(category_id)
    return cat["color"] if cat else "#888888"


def get_status_color(status: str) -> str:
    """Get status display color."""
    colors = {
        "confirmed": "#2ECC71",
        "potential": "#FFD700",
        "disputed": "#FF4444",
        "cancelled": "#555568",
        "completed": "#4A90D9",
        "rumor": "#888888"
    }
    return colors.get(status, "#888888")


def get_country_flag(code: str) -> str:
    """Get country flag emoji."""
    country = get_country_info(code)
    return country.get("flag_emoji", "") if country else ""
