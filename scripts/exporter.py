"""Export events to .ics, .csv, .json formats."""

import csv
import json
import io
from datetime import datetime
from scripts.utils import load_events, logger


def export_ics(events: list[dict] = None, month: str = None, category: str = None) -> str:
    db = load_events()
    all_events = events or db.get("events", [])

    if month:
        all_events = [e for e in all_events if e.get("start_date", "").startswith(month)]
    if category:
        all_events = [e for e in all_events if e.get("category") == category]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Big Event Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Big Events",
        "X-WR-TIMEZONE:UTC",
    ]

    for event in all_events:
        start = _date_to_ics(event.get("start_date", ""))
        end = _date_to_ics(event.get("end_date", event.get("start_date", "")))

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{_escape_ics(event.get('title', ''))}",
            f"DESCRIPTION:{_escape_ics(event.get('description', ''))}",
            f"CATEGORIES:{event.get('category', '').upper()}",
            f"STATUS:{_ics_status(event.get('status', ''))}",
            f"UID:{event.get('id', '')}@bigeventcalendar",
            f"LAST-MODIFIED:{_datetime_to_ics(event.get('updated_at', ''))}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def export_csv(events: list[dict] = None, month: str = None, category: str = None) -> str:
    db = load_events()
    all_events = events or db.get("events", [])

    if month:
        all_events = [e for e in all_events if e.get("start_date", "").startswith(month)]
    if category:
        all_events = [e for e in all_events if e.get("category") == category]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Title", "Category", "Country", "Region", "Start Date",
        "End Date", "Status", "Description", "Official Source", "Tags"
    ])

    for event in all_events:
        official = event.get("official_source", {})
        writer.writerow([
            event.get("id", ""),
            event.get("title", ""),
            event.get("category", ""),
            event.get("country", ""),
            event.get("region", ""),
            event.get("start_date", ""),
            event.get("end_date", ""),
            event.get("status", ""),
            event.get("description", "")[:200],
            official.get("url", "") if official else "",
            ", ".join(event.get("tags", [])),
        ])

    return output.getvalue()


def export_json(events: list[dict] = None, month: str = None, category: str = None, pretty: bool = True) -> str:
    db = load_events()
    all_events = events or db.get("events", [])

    if month:
        all_events = [e for e in all_events if e.get("start_date", "").startswith(month)]
    if category:
        all_events = [e for e in all_events if e.get("category") == category]

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "total_events": len(all_events),
        "filters": {
            "month": month,
            "category": category
        },
        "events": all_events
    }

    return json.dumps(export_data, indent=2 if pretty else None, ensure_ascii=False)


def _date_to_ics(date_str: str) -> str:
    if not date_str:
        return datetime.utcnow().strftime("%Y%m%d")
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return dt.strftime("%Y%m%d")
        except ValueError:
            return datetime.utcnow().strftime("%Y%m%d")


def _datetime_to_ics(dt_str: str) -> str:
    if not dt_str:
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except ValueError:
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def _escape_ics(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_status(status: str) -> str:
    mapping = {
        "confirmed": "CONFIRMED",
        "tentative": "TENTATIVE",
        "cancelled": "CANCELLED",
    }
    return mapping.get(status, "TENTATIVE")
