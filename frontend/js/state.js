const State = {
  currentYear: new Date().getFullYear(),
  currentMonth: new Date().getMonth(),
  currentWeek: 0,
  viewMode: "month",
  filters: {
    categories: {
      sports: true, space: true, politics: true, technology: true,
      culture: true, economics: true, humanitarian: true, astronomy: true
    },
    country: "all",
    status: "all",
    search: ""
  },
  selectedEvent: null,
  events: [],
  listeners: [],

  subscribe(fn) {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter(l => l !== fn);
    };
  },

  notify() {
    this.listeners.forEach(fn => fn(this));
  },

  setMonth(year, month) {
    this.currentYear = year;
    this.currentMonth = month;
    this.currentWeek = 0;
    this.notify();
  },

  prevMonth() {
    if (this.currentMonth === 0) {
      this.currentMonth = 11;
      this.currentYear--;
    } else {
      this.currentMonth--;
    }
    this.currentWeek = 0;
    this.notify();
  },

  nextMonth() {
    if (this.currentMonth === 11) {
      this.currentMonth = 0;
      this.currentYear++;
    } else {
      this.currentMonth++;
    }
    this.currentWeek = 0;
    this.notify();
  },

  goToday() {
    this.currentYear = new Date().getFullYear();
    this.currentMonth = new Date().getMonth();
    this.currentWeek = 0;
    this.notify();
  },

  setView(mode) {
    this.viewMode = mode;
    this.notify();
  },

  toggleCategory(cat) {
    this.filters.categories[cat] = !this.filters.categories[cat];
    this.notify();
  },

  setCountry(country) {
    this.filters.country = country;
    this.notify();
  },

  setStatus(status) {
    this.filters.status = status;
    this.notify();
  },

  setSearch(query) {
    this.filters.search = query;
    this.notify();
  },

  clearFilters() {
    Object.keys(this.filters.categories).forEach(k => {
      this.filters.categories[k] = true;
    });
    this.filters.country = "all";
    this.filters.status = "all";
    this.filters.search = "";
    this.notify();
  },

  selectEvent(event) {
    this.selectedEvent = event;
    this.notify();
  },

  closeEvent() {
    this.selectedEvent = null;
    this.notify();
  },

  setEvents(events) {
    this.events = events;
    this.notify();
  },

  getFilteredEvents() {
    return this.events.filter(event => {
      if (!this.filters.categories[event.category]) return false;
      if (this.filters.country !== "all") {
        const ec = event.country;
        if (Array.isArray(ec)) {
          if (!ec.includes(this.filters.country) && !ec.includes("global")) return false;
        } else {
          if (ec !== this.filters.country && ec !== "global") return false;
        }
      }
      if (this.filters.status !== "all" && event.status !== this.filters.status) return false;
      if (this.filters.search) {
        const q = this.filters.search.toLowerCase();
        const match = (event.title || "").toLowerCase().includes(q) ||
          (event.description || "").toLowerCase().includes(q) ||
          (event.tags || []).some(t => t.toLowerCase().includes(q));
        if (!match) return false;
      }
      return true;
    });
  },

  getMonthEvents() {
    const monthStr = `${this.currentYear}-${String(this.currentMonth + 1).padStart(2, "0")}`;
    return this.getFilteredEvents().filter(e => e.start_date && e.start_date.startsWith(monthStr));
  },

  getEventsForDate(dateStr) {
    return this.getFilteredEvents().filter(e => e.start_date === dateStr);
  }
};
