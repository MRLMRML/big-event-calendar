const CalendarWeek = {
  render(container) {
    const year = State.currentYear;
    const month = State.currentMonth;
    const week = State.currentWeek;
    container.innerHTML = "";

    const weekDates = Utils.getWeekDates(year, month, week);
    const today = new Date().toISOString().slice(0, 10);

    const header = document.createElement("div");
    header.className = "week-header";

    const emptyHeader = document.createElement("div");
    emptyHeader.className = "week-header-cell";
    header.appendChild(emptyHeader);

    weekDates.forEach(dateStr => {
      const cell = document.createElement("div");
      cell.className = "week-header-cell";
      if (dateStr === today) cell.classList.add("today");

      const d = new Date(dateStr + "T00:00:00");
      cell.innerHTML = `
        <div style="font-size: 0.6875rem; color: var(--text-muted);">${d.toLocaleDateString("en-US", { weekday: "short" })}</div>
        <div style="font-size: 1rem; font-weight: 600;">${d.getDate()}</div>
      `;
      header.appendChild(cell);
    });

    container.appendChild(header);

    const body = document.createElement("div");
    body.className = "week-day";

    const labelCol = document.createElement("div");
    labelCol.className = "week-day-label";
    labelCol.textContent = "Events";
    body.appendChild(labelCol);

    weekDates.forEach(dateStr => {
      const cell = document.createElement("div");
      cell.className = "week-day-cell";
      if (dateStr === today) cell.classList.add("today");

      const dayEvents = State.getFilteredEvents().filter(e => e.start_date === dateStr);
      dayEvents.forEach(event => {
        const card = EventCard.createWeek(event);
        cell.appendChild(card);
      });

      body.appendChild(cell);
    });

    container.appendChild(body);
  }
};
