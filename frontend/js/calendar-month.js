const CalendarMonth = {
  render(container) {
    const year = State.currentYear;
    const month = State.currentMonth;
    container.innerHTML = "";

    const cal = document.createElement("div");
    cal.className = "calendar-month";

    const header = document.createElement("div");
    header.className = "month-header";
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    days.forEach(d => {
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
    const monthEvents = State.getFilteredEvents().filter(e =>
      e.start_date && e.start_date.startsWith(monthStr)
    );

    const prevMonthDays = month === 0
      ? Utils.getDaysInMonth(year - 1, 11)
      : Utils.getDaysInMonth(year, month - 1);

    for (let i = firstDay - 1; i >= 0; i--) {
      const day = prevMonthDays - i;
      const cell = this._createCell(day, true, "", []);
      body.appendChild(cell);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${monthStr}-${String(day).padStart(2, "0")}`;
      const dayEvents = monthEvents.filter(e => e.start_date === dateStr);
      const isToday = dateStr === today;
      const cell = this._createCell(day, false, isToday ? "today" : "", dayEvents);
      body.appendChild(cell);
    }

    const totalCells = firstDay + daysInMonth;
    const remaining = (7 - (totalCells % 7)) % 7;
    for (let i = 1; i <= remaining; i++) {
      const cell = this._createCell(i, true, "", []);
      body.appendChild(cell);
    }

    cal.appendChild(body);
    container.appendChild(cal);
  },

  _createCell(day, isOtherMonth, extraClass, events) {
    const cell = document.createElement("div");
    cell.className = "month-cell";
    if (isOtherMonth) cell.classList.add("other-month");
    if (extraClass) cell.classList.add(extraClass);

    const dateLabel = document.createElement("div");
    dateLabel.className = "month-cell-date";
    dateLabel.textContent = day;
    cell.appendChild(dateLabel);

    if (events.length > 0) {
      const eventsContainer = document.createElement("div");
      eventsContainer.className = "month-cell-events";

      const maxShow = 3;
      events.slice(0, maxShow).forEach(event => {
        const card = EventCard.createCompact(event);
        eventsContainer.appendChild(card);
      });

      if (events.length > maxShow) {
        const more = document.createElement("div");
        more.className = "event-card event-card-compact";
        more.style.color = "var(--text-muted)";
        more.style.background = "var(--bg-tertiary)";
        more.style.borderLeftColor = "var(--text-muted)";
        more.textContent = `+${events.length - maxShow} more`;
        eventsContainer.appendChild(more);
      }

      cell.appendChild(eventsContainer);
    }

    return cell;
  }
};
