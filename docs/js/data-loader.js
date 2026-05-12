const DataLoader = {
  cache: null,
  cacheTime: null,
  CACHE_DURATION: 30000,
  isStatic: false,

  async loadEvents(params = {}) {
    const now = Date.now();
    if (this.cache && this.cacheTime && (now - this.cacheTime) < this.CACHE_DURATION) {
      return this._filterCached(params);
    }

    const bustCache = `?v=${Date.now()}`;
    try {
      const response = await fetch(`data/events.json${bustCache}`);
      const data = await response.json();
      this.cache = { events: data.events || [], total: (data.events || []).length, metadata: data.metadata || {} };
      this.isStatic = true;
    } catch (err2) {
      try {
        const response = await fetch(`/api/events${bustCache}`);
        if (!response.ok) throw new Error("API not available");
        const data = await response.json();
        this.cache = data;
        this.isStatic = false;
      } catch (err) {
        console.error("Failed to load events:", err);
        return { events: [], total: 0 };
      }
    }

    this.cacheTime = now;
    return this._filterCached(params);
  },

  _filterCached(params) {
    if (!this.cache) return { events: [], total: 0 };

    let events = [...this.cache.events];

    if (params.month) {
      events = events.filter(e => e.start_date && e.start_date.startsWith(params.month));
    }
    if (params.category) {
      events = events.filter(e => e.category === params.category);
    }
    if (params.country) {
      events = events.filter(e => e.country === params.country);
    }
    if (params.status) {
      events = events.filter(e => e.status === params.status);
    }
    if (params.search) {
      const q = params.search.toLowerCase();
      events = events.filter(e =>
        (e.title || "").toLowerCase().includes(q) ||
        (e.description || "").toLowerCase().includes(q) ||
        (e.tags || []).some(t => t.toLowerCase().includes(q))
      );
    }

    return { events, total: events.length };
  },

  invalidateCache() {
    this.cache = null;
    this.cacheTime = null;
  },

  async loadStats() {
    try {
      if (!this.isStatic) {
        const response = await fetch("/api/stats");
        if (response.ok) return await response.json();
      }
    } catch (err) {}

    const events = this.cache ? this.cache.events : [];
    const today = new Date().toISOString().slice(0, 10);
    const thisMonth = new Date().toISOString().slice(0, 7);

    const stats = {
      total: events.length,
      by_status: {},
      by_category: {},
      by_country: {},
      upcoming: 0,
      this_month: 0,
    };

    events.forEach(event => {
      stats.by_status[event.status] = (stats.by_status[event.status] || 0) + 1;
      stats.by_category[event.category] = (stats.by_category[event.category] || 0) + 1;
      stats.by_country[event.country] = (stats.by_country[event.country] || 0) + 1;
      if (event.start_date >= today) stats.upcoming++;
      if (event.start_date.startsWith(thisMonth)) stats.this_month++;
    });

    return stats;
  },

  async loadEvent(eventId) {
    try {
      if (!this.isStatic) {
        const response = await fetch(`/api/events/${eventId}`);
        if (response.ok) return await response.json();
      }
    } catch (err) {}

    if (this.cache) {
      return this.cache.events.find(e => e.id === eventId) || null;
    }
    return null;
  }
};
