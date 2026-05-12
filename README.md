# Big Event Calendar 📅

A global calendar database that tracks confirmed major events across all domains — sports, space, politics, technology, culture, economics, entertainment, humanitarian, and astronomy. Auto-scrapes news for validation, provides predictive analysis, and presents everything in a beautiful dark-mode calendar frontend.

**Live Demo**: https://mrlmrml.github.io/big-event-calendar/

## Features

- **9 Event Categories**: Sports ⚽, Space 🚀, Politics 🏛️, Technology 💻, Culture 🎭, Economics 💰, Entertainment 🎮, Humanitarian 🕊️, Astronomy 🔭
- **73+ Events**: Covering major global events with predictive analysis for high-impact events
- **China-Focused**: 22 Chinese events including traditional festivals, political events, tech conferences, and shopping festivals
- **Source Validation**: Official sources confirmed immediately, journalistic sources labeled "potential" until corroborated
- **Predictive Analysis**: High-impact events include scenario analysis; uncertain events include if/then predictions
- **Multi-View Calendar**: Year, Month, Week, and List views with smooth transitions
- **Dark Mode**: Elegant dark theme with category-specific color coding
- **Export**: Export to .ics (iCal), .csv, .json formats
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile screens

## Event Categories

| Category | Icon | Color | Examples |
|----------|------|-------|----------|
| Sports | ⚽ | Orange | FIFA World Cup, Olympics, Grand Slams |
| Space | 🚀 | Purple | SpaceX launches, NASA missions |
| Politics | 🏛️ | Green | G7, NATO, elections, summits |
| Technology | 💻 | Cyan | CES, WWDC, MWC |
| Culture | 🎭 | Pink | Oscars, Cannes, festivals |
| Economics | 💰 | Gold | Davos, Fed decisions |
| Entertainment | 🎮 | Magenta | E3, Gamescom, esports |
| Humanitarian | 🕊️ | Red | UN days, health summits |
| Astronomy | 🔭 | Violet | Eclipses, meteor showers |

## Quick Start

```bash
# Clone the skill
git clone https://github.com/MRLMRML/big-event-calendar.git ~/.opencode/skills/big-event-calendar

# Install dependencies
cd ~/.opencode/skills/big-event-calendar
pip install -r requirements.txt

# Start the server
python3 scripts/serve.py
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
python3 scripts/cli.py list
python3 scripts/cli.py list --month 2026-06
python3 scripts/cli.py list --category sports
python3 scripts/cli.py list --country CN
python3 scripts/cli.py search "world cup"

# Manage events
python3 scripts/cli.py add --title "SpaceX Launch" --date 2026-03-15 --category space
python3 scripts/cli.py edit evt_123 --date 2026-03-20
python3 scripts/cli.py delete evt_123

# Scraper
python3 scripts/cli.py scrape
python3 scripts/cli.py scrape --category space

# Export
python3 scripts/cli.py export --format ics
python3 scripts/cli.py export --format csv

# Server
python3 scripts/cli.py serve
python3 scripts/cli.py serve --port 9090

# Statistics
python3 scripts/cli.py stats
```

### Via Web UI

1. Start the server: `python3 scripts/serve.py`
2. Open http://localhost:8080
3. Use the toolbar to switch views (Year/Month/Week/List)
4. Use filters to narrow by category, country, or status
5. Click any event to see details and predictions
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
│  Events database with predictions and change tracking            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER (index.html)                                     │
│  Year / Month / Week / List views with filters and search        │
└─────────────────────────────────────────────────────────────────┘
```

## Prediction Logic

Events have different prediction types based on their nature:

| Event Type | Prediction Format | Example |
|------------|-------------------|---------|
| **Confirmed, High Impact** | `analysis` with multiple scenarios | G7 Summit, US Midterms |
| **Uncertain Events** | `if_happens` / `if_not` | SpaceX Starship, Artemis III |
| **Holidays/Fixed Events** | `null` (no prediction needed) | Christmas, Spring Festival |

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

## File Structure

```
big-event-calendar/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── config.json                 # Global configuration
├── requirements.txt            # Python dependencies
├── data/
│   ├── events.json            # Event database (73+ events)
│   ├── categories.json        # Category definitions
│   ├── countries.json         # Country definitions + tiers
│   └── sources.json           # Source registry
├── scripts/
│   ├── scraper.py             # Scraper orchestrator
│   ├── validator.py           # Cross-validation engine
│   ├── scheduler.py           # 6-hour cron scheduler
│   ├── serve.py               # Local web server
│   ├── cli.py                 # CLI interface
│   └── exporter.py            # Export to .ics/.csv/.json
├── scrapers/
│   ├── base.py                # Base scraper class
│   ├── sports.py              # Sports scraper
│   ├── space.py               # Space scraper
│   └── ...                    # Other category scrapers
└── frontend/
    ├── index.html             # Main page
    ├── css/                   # Stylesheets
    ├── js/                    # JavaScript modules
    └── assets/icons/          # SVG icons
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License
