---
name: big-event-calendar
description: >
  Global calendar of major events across 8 categories (sports, space, politics,
  technology, culture, economics, humanitarian, astronomy) and 26 countries.
  Auto-scrapes official news sources every 6 hours, cross-validates with
  journalistic sources, tracks changes, and presents everything in a beautiful
  dark-mode calendar UI. Use when asking about upcoming events, event schedules,
  "what's happening in June", Olympic dates, rocket launches, elections, award
  shows, economic decisions, eclipses, meteor showers, or any scheduled global
  event. Also use for adding events, checking event status, exporting calendars,
  browsing past events, or starting the calendar web server. Triggers on keywords
  like "event", "calendar", "schedule", "upcoming", "when is", "what's happening".
---

## What This Skill Does

Maintains a database of confirmed global events across 8 categories and 26 countries.
Scrapes official sources every 6 hours, cross-validates with journalistic sources,
and presents everything in a beautiful calendar UI.

## Architecture

```
User Request → SKILL.md → Scripts (Python) → events.json → Frontend (Web UI)
                              ↑
                         Scrapers (8 categories)
                              ↑
                    Official Sources + News Feeds
```

## Categories

| ID | Name | Color | Sources |
|----|------|-------|---------|
| sports | Sports | #FF6B35 | FIFA, Olympics, NBA, F1, ICC |
| space | Space & Science | #7B68EE | NASA, SpaceX, ESA, ISRO, JAXA |
| politics | Politics & Diplomacy | #2ECC71 | UN, White House, NATO, EU Council |
| technology | Technology | #00D4FF | Apple, Google, CES, MWC |
| culture | Culture & Entertainment | #FF69B4 | Oscars, Cannes, Grammy, Nobel |
| economics | Economics & Business | #FFD700 | Fed, ECB, BOJ, WEF |
| humanitarian | Humanitarian & Social | #FF4444 | WHO, UNICEF, Red Cross |
| astronomy | Astronomy & Natural | #9370DB | IMO, Time and Date, JWST |

## Country Tiers

- **Tier 1** (Global Powers): US, CN, RU, GB, FR, DE — scrape every 6h
- **Tier 2** (Major Powers): IN, JP, IL, SA, TR, BR, KR, AU, CA, IT — scrape every 6h
- **Tier 3** (Regional Powers): PK, ID, MX, NG, EG, AE, SG, PL, UA, IR — scrape every 12h

## Commands

### Query Events
- "What events are coming up?" → List next 30 days
- "Show me [month] [year]" → Month view
- "What [category] events this year?" → Filtered list
- "Events in [country]" → Country filter
- "Search for [keyword]" → Full-text search

### Manage Events
- "Add [event] on [date]" → Create event
- "Edit [event]" → Modify event
- "Delete [event]" → Remove event

### Scraper
- "Scrape latest events" → Manual scrape
- "Scrape [category]" → Category scrape
- "What changed recently?" → Change log

### Export
- "Export calendar" → Generate .ics
- "Export to CSV" → Generate .csv

### Server
- "Start the calendar server" → Launch frontend
- "Open the calendar" → Launch + open browser

## Source Validation

Events have a status lifecycle:
```
potential → confirmed → completed
    │           │
    ▼           ▼
 disputed    cancelled
```

- **Tier 1 (Official)**: Stored as "confirmed" immediately
- **Tier 3 (Journalistic)**: Stored as "potential" until corroborated
- **Cross-validation**: Requires ≥3 sources OR official source for "confirmed"

## File Structure

```
big-event-calendar/
├── SKILL.md                    # This file
├── README.md                   # Installation guide
├── config.json                 # Global configuration
├── requirements.txt            # Python dependencies
├── data/
│   ├── events.json            # Event database
│   ├── categories.json        # Category definitions
│   ├── countries.json         # Country definitions + tiers
│   └── sources.json           # Source registry
├── scripts/
│   ├── scraper.py             # Scraper orchestrator
│   ├── validator.py           # Cross-validation engine
│   ├── scheduler.py           # 6-hour cron scheduler
│   ├── serve.py               # Local web server
│   ├── cli.py                 # CLI interface
│   ├── exporter.py            # Export to .ics/.csv/.json
│   └── utils.py               # Shared utilities
├── scrapers/
│   ├── base.py                # Base scraper class
│   ├── sports.py              # Sports scraper
│   ├── space.py               # Space scraper
│   ├── politics.py            # Politics scraper
│   ├── technology.py          # Technology scraper
│   ├── culture.py             # Culture scraper
│   ├── economics.py           # Economics scraper
│   ├── humanitarian.py        # Humanitarian scraper
│   └── astronomy.py           # Astronomy scraper
└── frontend/
    ├── index.html             # Main page
    ├── css/                   # Stylesheets
    ├── js/                    # JavaScript modules
    └── assets/icons/          # SVG icons
```

## Installation

```bash
cd ~/.opencode/skills/big-event-calendar
pip install -r requirements.txt
python scripts/serve.py
```

Access at http://localhost:8080

## CLI Usage

```bash
python scripts/cli.py list                          # All events
python scripts/cli.py list --month 2026-06          # By month
python scripts/cli.py list --category sports         # By category
python scripts/cli.py search "world cup"             # Search
python scripts/cli.py add --title "Event" --date 2026-06-01 --category sports
python scripts/cli.py scrape                         # Manual scrape
python scripts/cli.py export --format ics            # Export
python scripts/cli.py serve                          # Start server
```
