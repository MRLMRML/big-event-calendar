const CalendarMonth = {
  render(container) {
    const year = State.currentYear;
    const month = State.currentMonth;
    container.innerHTML = "";

    const cal = document.createElement("div");
    cal.className = "calendar-month";

    const header = document.createElement("div");
    header.className = "month-header";
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    dayNames.forEach(d => {
      const cell = document.createElement("div");
      cell.className = "month-header-cell";
      cell.textContent = d;
      header.appendChild(cell);
    });
    cal.appendChild(header);

    const body = document.createElement("div");
    body.className = "month-body";

    const daysInMonth = Utils.getDaysInMonth(year, month);
    const firstDay = Utils.getFirstDayOfMonth(year, month);
    const today = new Date().toISOString().slice(0, 10);
    const monthStr = `${year}-${String(month + 1).padStart(2, "0")}`;

    const allEvents = State.getFilteredEvents().filter(e => {
      if (!e.start_date) return false;
      const end = e.end_date || e.start_date;
      const monthStart = `${monthStr}-01`;
      const monthEnd = `${monthStr}-${String(daysInMonth).padStart(2, "0")}`;
      return e.start_date <= monthEnd && end >= monthStart;
    });

    const allCells = [];
    const prevMonthDays = month === 0
      ? Utils.getDaysInMonth(year - 1, 11)
      : Utils.getDaysInMonth(year, month - 1);

    for (let i = firstDay - 1; i >= 0; i--) {
      const day = prevMonthDays - i;
      allCells.push({ day, dateStr: "", isOther: true });
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${monthStr}-${String(day).padStart(2, "0")}`;
      allCells.push({ day, dateStr, isOther: false });
    }

    const totalCells = firstDay + daysInMonth;
    const remaining = (7 - (totalCells % 7)) % 7;
    for (let i = 1; i <= remaining; i++) {
      allCells.push({ day: i, dateStr: "", isOther: true });
    }

    const weeks = [];
    for (let i = 0; i < allCells.length; i += 7) {
      weeks.push(allCells.slice(i, i + 7));
    }

    weeks.forEach((weekCells, weekIdx) => {
      const weekRow = document.createElement("div");
      weekRow.className = "month-week-row";

      const eventTrack = document.createElement("div");
      eventTrack.className = "month-event-track";

      const weekStart = weekCells.find(c => !c.isOther)?.dateStr || "";
      const weekEnd = [...weekCells].reverse().find(c => !c.isOther)?.dateStr || "";

      if (weekStart && weekEnd) {
        const weekEvents = allEvents.filter(e => {
          const end = e.end_date || e.start_date;
          const isMultiDay = end > e.start_date;
          return isMultiDay && e.start_date <= weekEnd && end >= weekStart;
        }).sort((a, b) => {
          const aLen = (a.end_date || a.start_date) > a.start_date ? 1 : 0;
          const bLen = (b.end_date || b.start_date) > b.start_date ? 1 : 0;
          return bLen - aLen;
        });

        const placed = [];
        weekEvents.forEach(event => {
          const row = this._findRow(placed, event, weekCells);
          placed.push({ event, row });

          const bar = this._createEventBar(event, weekCells, weekStart, weekEnd);
          if (bar) {
            bar.style.gridRow = row + 1;
            eventTrack.appendChild(bar);
          }
        });

        const maxRow = placed.length > 0 ? Math.max(...placed.map(p => p.row)) + 1 : 0;
        eventTrack.style.gridTemplateRows = `repeat(${Math.max(maxRow, 0)}, 22px)`;
      }

      const daysRow = document.createElement("div");
      daysRow.className = "month-days-row";

      weekCells.forEach(cell => {
        const dayEl = document.createElement("div");
        dayEl.className = "month-day-cell";
        if (cell.isOther) dayEl.classList.add("other-month");
        if (cell.dateStr === today) dayEl.classList.add("today");

        const dateLabel = document.createElement("div");
        dateLabel.className = "month-cell-date";
        dateLabel.textContent = cell.day;
        dayEl.appendChild(dateLabel);

        if (!cell.isOther && cell.dateStr) {
          const dayEvents = allEvents.filter(e => {
            const end = e.end_date || e.start_date;
            return e.start_date <= cell.dateStr && end >= cell.dateStr;
          });
          const singleDayEvents = dayEvents.filter(e => e.start_date === cell.dateStr && (!e.end_date || e.end_date === e.start_date));
          if (singleDayEvents.length > 0 && weekEventsWithBars(weekCells, allEvents).length < 3) {
            const eventsContainer = document.createElement("div");
            eventsContainer.className = "month-cell-events";
            singleDayEvents.slice(0, 2).forEach(event => {
              const card = EventCard.createCompact(event);
              eventsContainer.appendChild(card);
            });
            dayEl.appendChild(eventsContainer);
          }
        }

        daysRow.appendChild(dayEl);
      });

      weekRow.appendChild(eventTrack);
      weekRow.appendChild(daysRow);
      body.appendChild(weekRow);
    });

    cal.appendChild(body);
    container.appendChild(cal);
  },

  _findRow(placed, event, weekCells) {
    const weekStart = weekCells.find(c => !c.isOther)?.dateStr || "";
    const weekEnd = [...weekCells].reverse().find(c => !c.isOther)?.dateStr || "";
    const eventEnd = event.end_date || event.start_date;
    const barStart = event.start_date < weekStart ? weekStart : event.start_date;
    const barEnd = eventEnd > weekEnd ? weekEnd : eventEnd;

    const occupiedRows = new Set();
    placed.forEach(p => {
      const pEnd = p.event.end_date || p.event.start_date;
      const pStart = p.event.start_date < weekStart ? weekStart : p.event.start_date;
      const pEndClamped = pEnd > weekEnd ? weekEnd : pEnd;
      if (pStart <= barEnd && pEndClamped >= barStart) {
        occupiedRows.add(p.row);
      }
    });

    let row = 0;
    while (occupiedRows.has(row)) row++;
    return row;
  },

  _createEventBar(event, weekCells, weekStart, weekEnd) {
    const eventEnd = event.end_date || event.start_date;
    const barStart = event.start_date < weekStart ? weekStart : event.start_date;
    const barEnd = eventEnd > weekEnd ? weekEnd : eventEnd;

    let startIdx = -1;
    let endIdx = -1;
    for (let i = 0; i < weekCells.length; i++) {
      if (weekCells[i].dateStr === barStart) startIdx = i;
      if (weekCells[i].dateStr === barEnd) endIdx = i;
    }

    if (startIdx === -1) startIdx = 0;
    if (endIdx === -1) endIdx = 6;

    const isMultiDay = event.start_date !== eventEnd;
    const bar = document.createElement("div");
    bar.className = `event-bar cat-${event.category}`;
    if (isMultiDay) bar.classList.add("multi-day");

    bar.style.gridColumn = `${startIdx + 1} / ${endIdx + 2}`;

    const catColor = Utils.getCategoryColor(event.category);
    bar.innerHTML = `
      <span class="event-bar-status ${event.status}"></span>
      <span class="event-bar-title">${this._escapeHtml(event.title || "")}</span>
    `;

    bar.addEventListener("click", () => State.selectEvent(event));
    return bar;
  },

  _escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
};

function weekEventsWithBars(weekCells, allEvents) {
  const weekStart = weekCells.find(c => !c.isOther)?.dateStr || "";
  const weekEnd = [...weekCells].reverse().find(c => !c.isOther)?.dateStr || "";
  if (!weekStart || !weekEnd) return [];
  return allEvents.filter(e => {
    const end = e.end_date || e.start_date;
    return e.start_date <= weekEnd && end >= weekStart && (e.end_date || e.start_date) !== e.start_date;
  });
}
