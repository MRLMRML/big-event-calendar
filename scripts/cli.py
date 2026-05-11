"""CLI interface for Big Event Calendar."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from scripts.utils import load_events, load_categories, load_countries, save_events, now_iso, generate_event_id
from scripts.scraper import scrape_all, scrape_category
from scripts.exporter import export_ics, export_csv, export_json

console = Console()


@click.group()
def cli():
    pass


@cli.command()
@click.option("--month", help="Filter by month (YYYY-MM)")
@click.option("--category", help="Filter by category")
@click.option("--country", help="Filter by country code")
@click.option("--status", help="Filter by status")
@click.option("--limit", default=50, help="Max events to show")
def list(month, category, country, status, limit):
    db = load_events()
    events = db.get("events", [])

    if month:
        events = [e for e in events if e.get("start_date", "").startswith(month)]
    if category:
        events = [e for e in events if e.get("category") == category]
    if country:
        events = [e for e in events if e.get("country") == country]
    if status:
        events = [e for e in events if e.get("status") == status]

    events.sort(key=lambda e: e.get("start_date", ""))
    events = events[:limit]

    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return

    table = Table(title=f"Events ({len(events)} found)")
    table.add_column("Date", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Country", style="green")
    table.add_column("Status", style="yellow")

    for event in events:
        status_color = {
            "confirmed": "green",
            "potential": "yellow",
            "disputed": "red",
            "cancelled": "dim",
            "completed": "blue"
        }.get(event.get("status", ""), "white")

        table.add_row(
            event.get("start_date", "")[:10],
            event.get("title", "")[:50],
            event.get("category", ""),
            event.get("country", "global"),
            f"[{status_color}]{event.get('status', '')}[/{status_color}]"
        )

    console.print(table)


@cli.command()
@click.argument("query")
def search(query):
    db = load_events()
    events = db.get("events", [])
    query_lower = query.lower()

    results = [
        e for e in events
        if query_lower in e.get("title", "").lower()
        or query_lower in e.get("description", "").lower()
        or query_lower in " ".join(e.get("tags", [])).lower()
    ]

    if not results:
        console.print(f"[yellow]No events matching '{query}'[/yellow]")
        return

    table = Table(title=f"Search: '{query}' ({len(results)} results)")
    table.add_column("Date", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Status", style="yellow")

    for event in results[:20]:
        table.add_row(
            event.get("start_date", "")[:10],
            event.get("title", "")[:60],
            event.get("category", ""),
            event.get("status", "")
        )

    console.print(table)


@cli.command()
@click.option("--title", required=True, help="Event title")
@click.option("--date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", help="End date (YYYY-MM-DD)")
@click.option("--category", required=True, help="Category ID")
@click.option("--country", default="global", help="Country code")
@click.option("--description", default="", help="Event description")
def add(title, date, end_date, category, country, description):
    db = load_events()
    events = db.get("events", [])

    event_id = generate_event_id(title, date, category, country)

    for existing in events:
        if existing["id"] == event_id:
            console.print(f"[red]Event already exists: {event_id}[/red]")
            return

    new_event = {
        "id": event_id,
        "title": title,
        "category": category,
        "country": country,
        "region": "global",
        "scope": "national",
        "start_date": date,
        "end_date": end_date or date,
        "status": "confirmed",
        "description": description,
        "official_source": None,
        "media_sources": [],
        "tags": [],
        "changes": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "scraped_count": 0,
        "last_scraped_at": None
    }

    events.append(new_event)
    db["events"] = events
    db["metadata"]["total_events"] = len(events)
    save_events(db)

    console.print(f"[green]Event created: {event_id}[/green]")


@cli.command()
@click.argument("event_id")
@click.option("--title", help="New title")
@click.option("--date", help="New start date")
@click.option("--end-date", help="New end date")
@click.option("--status", help="New status")
@click.option("--description", help="New description")
def edit(event_id, title, date, end_date, status, description):
    db = load_events()
    events = db.get("events", [])

    for event in events:
        if event["id"] == event_id:
            changes = []
            if title:
                changes.append(("title", event["title"], title))
                event["title"] = title
            if date:
                changes.append(("start_date", event["start_date"], date))
                event["start_date"] = date
            if end_date:
                changes.append(("end_date", event["end_date"], end_date))
                event["end_date"] = end_date
            if status:
                changes.append(("status", event["status"], status))
                event["status"] = status
            if description:
                event["description"] = description

            for field, old_val, new_val in changes:
                event.setdefault("changes", []).append({
                    "field": field,
                    "old_value": old_val,
                    "new_value": new_val,
                    "reason": "Manual edit",
                    "changed_at": now_iso(),
                    "source": "cli"
                })

            event["updated_at"] = now_iso()
            save_events(db)
            console.print(f"[green]Event updated: {event_id}[/green]")
            return

    console.print(f"[red]Event not found: {event_id}[/red]")


@cli.command()
@click.argument("event_id")
@click.confirmation_option(prompt="Are you sure you want to delete this event?")
def delete(event_id):
    db = load_events()
    events = db.get("events", [])
    original_count = len(events)

    events = [e for e in events if e["id"] != event_id]

    if len(events) < original_count:
        db["events"] = events
        db["metadata"]["total_events"] = len(events)
        save_events(db)
        console.print(f"[green]Event deleted: {event_id}[/green]")
    else:
        console.print(f"[red]Event not found: {event_id}[/red]")


@cli.command()
@click.option("--all", "scrape_all_cats", is_flag=True, help="Scrape all categories")
@click.option("--category", help="Scrape specific category")
@click.option("--country", help="Scrape specific country")
def scrape(scrape_all_cats, category, country):
    if country:
        from scripts.scraper import scrape_country
        console.print(f"Scraping events for {country}...")
        stats = scrape_country(country)
    elif category:
        console.print(f"Scraping {category} events...")
        raw_events = scrape_category(category)
        from scripts.validator import EventValidator
        validator = EventValidator()
        stats = validator.validate_and_store(raw_events)
    else:
        console.print("Scraping all categories...")
        stats = scrape_all()

    console.print(f"[green]Scrape complete:[/green]")
    console.print(f"  New: {stats.get('new', 0)}")
    console.print(f"  Updated: {stats.get('updated', 0)}")
    console.print(f"  Skipped: {stats.get('skipped', 0)}")
    console.print(f"  Confirmed: {stats.get('confirmed', 0)}")


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["ics", "csv", "json"]), default="ics")
@click.option("--month", help="Filter by month (YYYY-MM)")
@click.option("--category", help="Filter by category")
@click.option("--output", "-o", help="Output file path")
def export(fmt, month, category, output):
    if fmt == "ics":
        content = export_ics(month=month, category=category)
    elif fmt == "csv":
        content = export_csv(month=month, category=category)
    else:
        content = export_json(month=month, category=category)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]Exported to {output}[/green]")
    else:
        click.echo(content)


@cli.command()
def stats():
    db = load_events()
    events = db.get("events", [])

    total = len(events)
    by_status = {}
    by_category = {}
    by_country = {}

    for event in events:
        status = event.get("status", "unknown")
        category = event.get("category", "unknown")
        country = event.get("country", "global")

        by_status[status] = by_status.get(status, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
        by_country[country] = by_country.get(country, 0) + 1

    console.print(Panel(f"[bold]Total Events: {total}[/bold]", title="Statistics"))

    table = Table(title="By Status")
    table.add_column("Status")
    table.add_column("Count", justify="right")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        table.add_row(status, str(count))
    console.print(table)

    table = Table(title="By Category")
    table.add_column("Category")
    table.add_column("Count", justify="right")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        table.add_row(cat, str(count))
    console.print(table)


@cli.command()
@click.option("--port", default=8080, help="Server port")
def serve(port):
    from scripts.serve import run_server
    run_server(port)


if __name__ == "__main__":
    cli()
