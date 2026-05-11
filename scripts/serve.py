"""Local web server for the calendar frontend."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from scripts.utils import load_events, load_categories, load_countries, logger, PROJECT_ROOT

app = Flask(__name__, static_folder=str(PROJECT_ROOT / "frontend"))
CORS(app)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/events")
def api_events():
    db = load_events()
    events = db.get("events", [])

    month = request.args.get("month")
    category = request.args.get("category")
    country = request.args.get("country")
    status = request.args.get("status")
    search = request.args.get("search", "").lower()

    if month:
        events = [e for e in events if e.get("start_date", "").startswith(month)]
    if category:
        events = [e for e in events if e.get("category") == category]
    if country:
        events = [e for e in events if e.get("country") == country]
    if status:
        events = [e for e in events if e.get("status") == status]
    if search:
        events = [
            e for e in events
            if search in e.get("title", "").lower()
            or search in e.get("description", "").lower()
            or search in " ".join(e.get("tags", [])).lower()
        ]

    events.sort(key=lambda e: e.get("start_date", ""))

    return jsonify({
        "events": events,
        "total": len(events),
        "metadata": db.get("metadata", {})
    })


@app.route("/api/events/<event_id>")
def api_event(event_id):
    db = load_events()
    for event in db.get("events", []):
        if event["id"] == event_id:
            return jsonify(event)
    return jsonify({"error": "Event not found"}), 404


@app.route("/api/categories")
def api_categories():
    data = load_categories()
    return jsonify(data)


@app.route("/api/countries")
def api_countries():
    data = load_countries()
    return jsonify(data)


@app.route("/api/stats")
def api_stats():
    db = load_events()
    events = db.get("events", [])

    stats = {
        "total": len(events),
        "by_status": {},
        "by_category": {},
        "by_country": {},
        "upcoming": 0,
        "this_month": 0,
    }

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    for event in events:
        status = event.get("status", "unknown")
        category = event.get("category", "unknown")
        country = event.get("country", "global")
        start = event.get("start_date", "")

        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        stats["by_country"][country] = stats["by_country"].get(country, 0) + 1

        if start >= today:
            stats["upcoming"] += 1
        if start.startswith(this_month):
            stats["this_month"] += 1

    return jsonify(stats)


def run_server(port=8080):
    logger.info(f"Starting server on port {port}")
    print(f"\n  Big Event Calendar running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
