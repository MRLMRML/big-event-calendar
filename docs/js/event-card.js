const EventCard = {
  createCompact(event) {
    const card = document.createElement("div");
    card.className = `event-card event-card-compact cat-${event.category}`;
    card.innerHTML = `
      <span class="event-card-status ${event.status}"></span>
      ${this._escapeHtml(event.title || "Untitled")}
    `;
    card.addEventListener("click", (e) => {
      e.stopPropagation();
      State.selectEvent(event);
    });
    return card;
  },

  createWeek(event) {
    const card = document.createElement("div");
    card.className = `event-card event-card-week cat-${event.category}`;
    card.innerHTML = `
      <span class="event-card-status ${event.status}"></span>
      ${this._escapeHtml(event.title || "Untitled")}
    `;
    card.addEventListener("click", (e) => {
      e.stopPropagation();
      State.selectEvent(event);
    });
    return card;
  },

  createFull(event) {
    const card = document.createElement("div");
    card.className = `event-card cat-${event.category}`;
    card.style.padding = "var(--space-sm) var(--space-md)";

    const catColor = Utils.getCategoryColor(event.category);

    card.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-xs);">
        <span class="event-card-status ${event.status}"></span>
        <span style="font-size: 0.6875rem; color: ${catColor};">${Utils.getCategoryName(event.category)}</span>
        <span style="font-size: 0.6875rem; color: var(--text-muted); margin-left: auto;">${Utils.getCountryFlag(event.country)}</span>
      </div>
      <div style="font-weight: 600; margin-bottom: 2px;">${this._escapeHtml(event.title || "Untitled")}</div>
      <div style="font-size: 0.625rem; color: var(--text-muted);">${Utils.formatDateShort(event.start_date)}</div>
    `;

    card.addEventListener("click", (e) => {
      e.stopPropagation();
      State.selectEvent(event);
    });

    return card;
  },

  _escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
};
