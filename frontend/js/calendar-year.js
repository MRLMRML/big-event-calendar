const CalendarYear = {
  render(container) {
    const year = State.currentYear;
    container.innerHTML = "";

    const grid = document.createElement("div");
    grid.className = "calendar-year";

    for (let month = 0; month < 12; month++) {
      const monthEl = this._renderMonth(year, month);
      grid.appendChild(monthEl);
    }

    container.appendChild(grid);
  },

  _renderMonth(year, month) {
    const el = document.createElement("div");
    el.className = "year-month";
    el.addEventListener("click", () => {
      State.setMonth(year, month);
      State.setView("month");
    });

    const header = document.createElement("div");
    header.className = "year-month-header";
    header.textContent = Utils.getMonthName(year, month);
    el.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "year-month-grid";

    const daysInMonth = Utils.getDaysInMonth(year, month);
    const firstDay = Utils.getFirstDayOfMonth(year, month);
    const today = new Date().toISOString().slice(0, 10);
    const monthStr = `${year}-${String(month + 1).padStart(2, "0")}`;
    const monthEvents = State.getFilteredEvents().filter(e =>
      e.start_date && e.start_date.startsWith(monthStr)
    );

    const eventDates = new Set(monthEvents.map(e => e.start_date));

    for (let i = 0; i < firstDay; i++) {
      const empty = document.createElement("div");
      empty.className = "year-month-day";
      grid.appendChild(empty);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${monthStr}-${String(day).padStart(2, "0")}`;
      const dayEl = document.createElement("div");
      dayEl.className = "year-month-day";
      dayEl.textContent = day;

      if (dateStr === today) dayEl.classList.add("today");
      if (eventDates.has(dateStr)) dayEl.classList.add("has-event");

      grid.appendChild(dayEl);
    }

    el.appendChild(grid);
    return el;
  }
};
