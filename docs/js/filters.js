const Filters = {
  init() {
    this.container = document.getElementById("filters-container");
    this.render();
  },

  render() {
    if (!this.container) return;

    const categories = [
      { id: "sports", name: "Sports", color: "#FF6B35" },
      { id: "space", name: "Space", color: "#7B68EE" },
      { id: "politics", name: "Politics", color: "#2ECC71" },
      { id: "technology", name: "Tech", color: "#00D4FF" },
      { id: "culture", name: "Culture", color: "#FF69B4" },
      { id: "economics", name: "Economics", color: "#FFD700" },
      { id: "humanitarian", name: "Humanitarian", color: "#FF4444" },
      { id: "astronomy", name: "Astronomy", color: "#9370DB" }
    ];

    const statuses = ["confirmed", "potential", "disputed"];

    this.container.innerHTML = `
      <div class="filter-group">
        <span class="filter-group-label">Categories</span>
        <div class="filter-chips">
          ${categories.map(cat => `
            <div class="filter-chip ${State.filters.categories[cat.id] ? "active" : "inactive"}"
                 style="${State.filters.categories[cat.id] ? `color: ${cat.color}; background: ${cat.color}15;` : ""}"
                 data-category="${cat.id}">
              <span class="chip-dot" style="background: ${cat.color}"></span>
              ${cat.name}
            </div>
          `).join("")}
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">Country</span>
        <div class="filter-select-wrapper">
          <select class="filter-select" id="filter-country">
            <option value="all" ${State.filters.country === "all" ? "selected" : ""}>All Countries</option>
            <option value="US" ${State.filters.country === "US" ? "selected" : ""}>🇺🇸 US</option>
            <option value="CN" ${State.filters.country === "CN" ? "selected" : ""}>🇨🇳 China</option>
            <option value="RU" ${State.filters.country === "RU" ? "selected" : ""}>🇷🇺 Russia</option>
            <option value="GB" ${State.filters.country === "GB" ? "selected" : ""}>🇬🇧 UK</option>
            <option value="FR" ${State.filters.country === "FR" ? "selected" : ""}>🇫🇷 France</option>
            <option value="DE" ${State.filters.country === "DE" ? "selected" : ""}>🇩🇪 Germany</option>
            <option value="IN" ${State.filters.country === "IN" ? "selected" : ""}>🇮🇳 India</option>
            <option value="JP" ${State.filters.country === "JP" ? "selected" : ""}>🇯🇵 Japan</option>
            <option value="global" ${State.filters.country === "global" ? "selected" : ""}>🌍 Global</option>
          </select>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">Status</span>
        <div class="filter-chips">
          ${statuses.map(s => `
            <div class="status-chip ${s} ${State.filters.status === s ? "" : "inactive"}"
                 data-status="${s}">
              ${s}
            </div>
          `).join("")}
          ${State.filters.status !== "all" ? `
            <div class="filter-clear" data-clear-status>Clear</div>
          ` : ""}
        </div>
      </div>

      <div class="filter-clear" data-clear-all>Clear all filters</div>
    `;

    this._bindEvents();
  },

  _bindEvents() {
    this.container.querySelectorAll("[data-category]").forEach(chip => {
      chip.addEventListener("click", () => {
        State.toggleCategory(chip.dataset.category);
      });
    });

    const countrySelect = this.container.querySelector("#filter-country");
    if (countrySelect) {
      countrySelect.addEventListener("change", (e) => {
        State.setCountry(e.target.value);
      });
    }

    this.container.querySelectorAll("[data-status]").forEach(chip => {
      chip.addEventListener("click", () => {
        const status = chip.dataset.status;
        State.setStatus(State.filters.status === status ? "all" : status);
      });
    });

    const clearStatus = this.container.querySelector("[data-clear-status]");
    if (clearStatus) {
      clearStatus.addEventListener("click", () => State.setStatus("all"));
    }

    const clearAll = this.container.querySelector("[data-clear-all]");
    if (clearAll) {
      clearAll.addEventListener("click", () => State.clearFilters());
    }
  }
};
