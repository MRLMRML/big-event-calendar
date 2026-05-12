const Utils = {
  formatDate(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  },

  formatDateShort(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  },

  formatDateFull(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  },

  getMonthName(year, month) {
    const d = new Date(year, month, 1);
    return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
  },

  getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
  },

  getFirstDayOfMonth(year, month) {
    return new Date(year, month, 1).getDay();
  },

  isToday(dateStr) {
    const today = new Date().toISOString().slice(0, 10);
    return dateStr === today;
  },

  isSameMonth(dateStr, year, month) {
    if (!dateStr) return false;
    const d = new Date(dateStr + "T00:00:00");
    return d.getFullYear() === year && d.getMonth() === month;
  },

  getWeekDates(year, month, week) {
    const firstDay = new Date(year, month, 1);
    const dayOfWeek = firstDay.getDay();
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - dayOfWeek + (week * 7));

    const dates = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(startDate);
      d.setDate(d.getDate() + i);
      dates.push(d.toISOString().slice(0, 10));
    }
    return dates;
  },

  getCategoryColor(category) {
    const colors = {
      sports: "#FF6B35",
      space: "#7B68EE",
      politics: "#2ECC71",
      technology: "#00D4FF",
      culture: "#FF69B4",
      economics: "#FFD700",
      humanitarian: "#FF4444",
      astronomy: "#9370DB",
      entertainment: "#E040FB"
    };
    return colors[category] || "#888888";
  },

  getCategoryName(category) {
    const names = {
      sports: "Sports",
      space: "Space & Science",
      politics: "Politics",
      technology: "Technology",
      culture: "Culture",
      economics: "Economics",
      humanitarian: "Humanitarian",
      astronomy: "Astronomy",
      entertainment: "Entertainment & Gaming"
    };
    return names[category] || category;
  },

  getStatusColor(status) {
    const colors = {
      confirmed: "#2ECC71",
      potential: "#FFD700",
      disputed: "#FF4444",
      cancelled: "#555568",
      completed: "#4A90D9"
    };
    return colors[status] || "#888888";
  },

  debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  },

  getCountryFlag(code) {
    if (!code || code === "global") return "🌍";
    const flags = {
      US: "🇺🇸", CN: "🇨🇳", RU: "🇷🇺", GB: "🇬🇧", FR: "🇫🇷", DE: "🇩🇪",
      IN: "🇮🇳", JP: "🇯🇵", IL: "🇮🇱", SA: "🇸🇦", TR: "🇹🇷", BR: "🇧🇷",
      KR: "🇰🇷", AU: "🇦🇺", CA: "🇨🇦", IT: "🇮🇹", PK: "🇵🇰", ID: "🇮🇩",
      MX: "🇲🇽", NG: "🇳🇬", EG: "🇪🇬", AE: "🇦🇪", SG: "🇸🇬", PL: "🇵🇱",
      UA: "🇺🇦", IR: "🇮🇷", SE: "🇸🇪", CH: "🇨🇭", AR: "🇦🇷", ZA: "🇿🇦"
    };
    return flags[code] || "🏳️";
  },

  getCountryFlags(countries) {
    if (!countries) return "🌍";
    if (typeof countries === "string") return this.getCountryFlag(countries);
    if (Array.isArray(countries)) {
      if (countries.includes("global")) return "🌍";
      return countries.map(c => this.getCountryFlag(c)).join("");
    }
    return "🌍";
  },

  getCountryDisplay(countries) {
    if (!countries) return "Global";
    if (typeof countries === "string") {
      return countries === "global" ? "Global" : this.getCountryName(countries);
    }
    if (Array.isArray(countries)) {
      if (countries.includes("global")) return "Global";
      return countries.map(c => this.getCountryName(c)).join(", ");
    }
    return "Global";
  },

  getCountryName(code) {
    const names = {
      US: "United States", CN: "China", RU: "Russia", GB: "United Kingdom",
      FR: "France", DE: "Germany", IN: "India", JP: "Japan", IL: "Israel",
      SA: "Saudi Arabia", TR: "Turkey", BR: "Brazil", KR: "South Korea",
      AU: "Australia", CA: "Canada", IT: "Italy", PK: "Pakistan", ID: "Indonesia",
      MX: "Mexico", NG: "Nigeria", EG: "Egypt", AE: "UAE", SG: "Singapore",
      PL: "Poland", UA: "Ukraine", IR: "Iran", global: "Global"
    };
    return names[code] || code;
  }
};
