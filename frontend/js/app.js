const App = {
  async init() {
    EventDetail.init();
    Search.init();
    Filters.init();

    State.subscribe(() => this.render());
    this._bindNavControls();
    this._bindExportControls();

    await this.loadData();
    this.render();
  },

  async loadData() {
    const data = await DataLoader.loadEvents();
    State.setEvents(data.events || []);
    await this._loadStats();
  },

  async _loadStats() {
    const stats = await DataLoader.loadStats();
    const statsBar = document.getElementById("stats-bar");
    if (statsBar && stats.total !== undefined) {
      statsBar.innerHTML = `
        <div class="stat-item">
          <div class="stat-value">${stats.total || 0}</div>
          <div class="stat-label">Total Events</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${stats.upcoming || 0}</div>
          <div class="stat-label">Upcoming</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${stats.this_month || 0}</div>
          <div class="stat-label">This Month</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${Object.keys(stats.by_category || {}).length}</div>
          <div class="stat-label">Categories</div>
        </div>
      `;
    }
  },

  render() {
    this._updateMonthLabel();
    this._updateViewModes();
    Filters.render();
    EventDetail.render();

    const container = document.getElementById("calendar-container");
    if (!container) return;

    switch (State.viewMode) {
      case "year":
        CalendarYear.render(container);
        break;
      case "month":
        CalendarMonth.render(container);
        break;
      case "week":
        CalendarWeek.render(container);
        break;
      case "list":
        CalendarList.render(container);
        break;
    }
  },

  _updateMonthLabel() {
    const label = document.getElementById("month-label");
    if (!label) return;

    switch (State.viewMode) {
      case "year":
        label.textContent = State.currentYear;
        break;
      case "month":
        label.textContent = Utils.getMonthName(State.currentYear, State.currentMonth);
        break;
      case "week":
        const weekDates = Utils.getWeekDates(State.currentYear, State.currentMonth, State.currentWeek);
        const start = Utils.formatDateShort(weekDates[0]);
        const end = Utils.formatDateShort(weekDates[6]);
        label.textContent = `${start} – ${end}`;
        break;
      case "list":
        label.textContent = Utils.getMonthName(State.currentYear, State.currentMonth);
        break;
    }
  },

  _updateViewModes() {
    document.querySelectorAll(".view-mode").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.view === State.viewMode);
    });
  },

  _bindNavControls() {
    document.getElementById("btn-prev")?.addEventListener("click", () => State.prevMonth());
    document.getElementById("btn-next")?.addEventListener("click", () => State.nextMonth());
    document.getElementById("btn-today")?.addEventListener("click", () => State.goToday());

    document.querySelectorAll(".view-mode").forEach(btn => {
      btn.addEventListener("click", () => State.setView(btn.dataset.view));
    });

    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT") return;
      if (e.key === "ArrowLeft") State.prevMonth();
      if (e.key === "ArrowRight") State.nextMonth();
      if (e.key === "t") State.goToday();
    });
  },

  _bindExportControls() {
    document.getElementById("btn-export")?.addEventListener("click", () => {
      const format = prompt("Export format (ics, csv, json):", "ics");
      if (format && ["ics", "csv", "json"].includes(format)) {
        EventExporter.exportAll(format);
      }
    });
  }
};

document.addEventListener("DOMContentLoaded", () => App.init());
