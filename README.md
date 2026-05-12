# Big Event Calendar

A global calendar database that tracks confirmed major events across all domains, auto-scrapes news for validation, and provides a beautiful dark-mode calendar frontend.

**Live Demo**: https://mrlmrml.github.io/big-event-calendar/

## Features

- **8 Event Categories**: Sports, Space & Science, Politics & Diplomacy, Technology, Culture & Entertainment, Economics & Business, Humanitarian & Social, Astronomy & Natural
- **26 Countries**: Tiered by geopolitical significance (political influence, military power, geopolitical importance, economy)
- **Auto-Scraping**: Runs every 6 hours, pulling from official sources and cross-validating with journalistic sources
- **Source Tiering**: Official sources (Tier 1) confirmed immediately, journalistic sources (Tier 3) labeled "potential" until corroborated
- **Beautiful Frontend**: Dark-mode calendar UI with Year/Month/Week/List views
- **Export**: Export to .ics (iCal), .csv, .json formats
- **CLI**: Full command-line interface for power users

## Quick Start

```bash
# Clone the skill
git clone https://github.com/MRLMRML/big-event-calendar.git ~/.opencode/skills/big-event-calendar

# Install dependencies
cd ~/.opencode/skills/big-event-calendar
pip install -r requirements.txt

# Start the server
python scripts/serve.py
```

Open http://localhost:8080 in your browser.

## Installation

### OpenCode

```bash
opencode skill install big-event-calendar
```

### Claude Code / OpenClaw

Copy the skill to the skills directory:

```bash
cp -r big-event-calendar ~/.opencode/skills/
```

## Usage

### Via Skill Commands

```
"What big events are coming up?"
"Show me June 2026"
"What space events this year?"
"Add FIFA World Cup on June 12"
"Scrape latest sports events"
"Export my calendar"
```

### Via CLI

```bash
# Query events
python scripts/cli.py list
python scripts/cli.py list --month 2026-06
python scripts/cli.py list --category sports
python scripts/cli.py list --country US
python scripts/cli.py search "world cup"

# Manage events
python scripts/cli.py add --title "SpaceX Launch" --date 2026-03-15 --category space
python scripts/cli.py edit evt_123 --date 2026-03-20
python scripts/cli.py delete evt_123

# Scraper
python scripts/cli.py scrape
python scripts/cli.py scrape --category space
python scripts/cli.py scrape --country US

# Export
python scripts/cli.py export --format ics
python scripts/cli.py export --format csv
python scripts/cli.py export --month 2026-06 --format ics

# Server
python scripts/cli.py serve
python scripts/cli.py serve --port 9090

# Statistics
python scripts/cli.py stats
```

### Via Web UI

1. Start the server: `python scripts/serve.py`
2. Open http://localhost:8080
3. Use the toolbar to switch views (Year/Month/Week/List)
4. Use filters to narrow by category, country, or status
5. Click any event to see details
6. Use Export button to download calendar

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  SKILL LAYER (SKILL.md)                                         │
│  Trigger detection → Command routing → Response formatting       │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  QUERY ENGINE   │  │  SCRAPE ENGINE  │  │  ENTRY ENGINE   │
│  Date/Category  │  │  6h scheduler   │  │  Manual add     │
│  Country/Search │  │  Source fetch   │  │  Edit/Delete    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         └────────────────────┼────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DATA LAYER (events.json)                                        │
│  Events database with full history and change tracking           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER (index.html)                                     │
│  Year / Month / Week / List views with filters and search        │
└─────────────────────────────────────────────────────────────────┘
```

## Source Validation

Events go through a validation pipeline:

```
News Article Retrieved
         │
    ┌────┴────┐
    ▼         ▼
 Tier 1    Tier 3
(Official) (Journalistic)
    │         │
    ▼         ▼
 Store as   Store as
"confirmed" "potential"
    │         │
    │         ▼
    │    Cross-Check (≥3 sources?)
    │         │
    │    ┌────┴────┐
    │    ▼         ▼
    │  Yes        No
    │    │         │
    │    ▼         ▼
    │  Promote   Keep as
    │  to        "potential"
    │ "confirmed"
    │    │
    └────┴───→ Final Status
```

## Configuration

Edit `config.json` to customize:

```json
{
  "scheduler": {
    "interval_hours": 6,
    "tier1_priority": true
  },
  "scraper": {
    "request_timeout": 30,
    "max_retries": 3,
    "confirmed_threshold": 0.8
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License
# Cache bust Tue May 12 13:01:13 CST 2026
