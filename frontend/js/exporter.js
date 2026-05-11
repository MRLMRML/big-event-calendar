const EventExporter = {
  exportAll(format = "ics") {
    const events = State.getFilteredEvents();
    let content, filename, mimeType;

    if (format === "ics") {
      content = this._toICS(events);
      filename = "big-events.ics";
      mimeType = "text/calendar";
    } else if (format === "csv") {
      content = this._toCSV(events);
      filename = "big-events.csv";
      mimeType = "text/csv";
    } else {
      content = JSON.stringify({ events, exported_at: new Date().toISOString() }, null, 2);
      filename = "big-events.json";
      mimeType = "application/json";
    }

    this._download(content, filename, mimeType);
  },

  exportSingle(eventId) {
    const event = State.events.find(e => e.id === eventId);
    if (!event) return;

    const content = this._toICS([event]);
    this._download(content, `${event.title || "event"}.ics`, "text/calendar");
  },

  _toICS(events) {
    const lines = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Big Event Calendar//EN",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      "X-WR-CALNAME:Big Events",
      "X-WR-TIMEZONE:UTC"
    ];

    events.forEach(event => {
      const start = this._dateToICS(event.start_date);
      const end = this._dateToICS(event.end_date || event.start_date);

      lines.push(
        "BEGIN:VEVENT",
        `DTSTART;VALUE=DATE:${start}`,
        `DTEND;VALUE=DATE:${end}`,
        `SUMMARY:${this._escapeICS(event.title || "")}`,
        `DESCRIPTION:${this._escapeICS(event.description || "")}`,
        `CATEGORIES:${(event.category || "").toUpperCase()}`,
        `STATUS:${event.status === "confirmed" ? "CONFIRMED" : "TENTATIVE"}`,
        `UID:${event.id}@bigeventcalendar`,
        "END:VEVENT"
      );
    });

    lines.push("END:VCALENDAR");
    return lines.join("\r\n");
  },

  _toCSV(events) {
    const headers = ["Date", "Title", "Category", "Country", "Status", "Description"];
    const rows = events.map(e => [
      e.start_date || "",
      `"${(e.title || "").replace(/"/g, '""')}"`,
      e.category || "",
      e.country || "global",
      e.status || "",
      `"${(e.description || "").replace(/"/g, '""').slice(0, 200)}"`
    ]);

    return [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
  },

  _dateToICS(dateStr) {
    if (!dateStr) return new Date().toISOString().slice(0, 10).replace(/-/g, "");
    return dateStr.replace(/-/g, "").slice(0, 8);
  },

  _escapeICS(text) {
    return (text || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
  },

  _download(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};
