const CalendarList = {
  render(container) {
    container.innerHTML = "";

    const list = document.createElement("div");
    list.className = "calendar-list";

    const header = document.createElement("div");
    header.className = "list-header";
    header.innerHTML = `
      <div>Date</div>
      <div>Event</div>
      <div>Category</div>
      <div>Country</div>
      <div>Status</div>
    `;
    list.appendChild(header);

    const events = State.getFilteredEvents()
      .sort((a, b) => (a.start_date || "").localeCompare(b.start_date || ""));

    if (events.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.innerHTML = `
        <div class="empty-state-icon">📅</div>
        <div class="empty-state-title">No events found</div>
        <div class="empty-state-text">Try adjusting your filters or search query</div>
      `;
      list.appendChild(empty);
    } else {
      events.forEach(event => {
        const row = document.createElement("div");
        row.className = "list-row";
        row.addEventListener("click", () => State.selectEvent(event));

        const statusColor = Utils.getStatusColor(event.status);
        const catColor = Utils.getCategoryColor(event.category);

        row.innerHTML = `
          <div class="list-date">${Utils.formatDateShort(event.start_date)}</div>
          <div class="list-title">${event.title || "Untitled"}</div>
          <div class="list-category">
            <span class="dot" style="background: ${catColor}"></span>
            ${Utils.getCategoryName(event.category)}
          </div>
          <div class="list-country">${Utils.getCountryFlags(event.country)}</div>
          <div class="list-status" style="background: ${statusColor}22; color: ${statusColor}; border: 1px solid ${statusColor}44;">
            ${event.status || "unknown"}
          </div>
        `;

        list.appendChild(row);
      });
    }

    container.appendChild(list);
  }
};
