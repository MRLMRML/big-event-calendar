const EventDetail = {
  init() {
    this.overlay = document.getElementById("detail-overlay");
    this.panel = document.getElementById("detail-panel");

    this.overlay.addEventListener("click", () => State.closeEvent());

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && State.selectedEvent) {
        State.closeEvent();
      }
    });
  },

  render() {
    const event = State.selectedEvent;

    if (!event) {
      this.overlay.classList.remove("open");
      this.panel.classList.remove("open");
      return;
    }

    this.overlay.classList.add("open");
    this.panel.classList.add("open");

    const catColor = Utils.getCategoryColor(event.category);
    const statusColor = Utils.getStatusColor(event.status);
    const flags = Utils.getCountryFlags(event.country);
    const countryDisplay = Utils.getCountryDisplay(event.country);

    this.panel.innerHTML = `
      <div class="detail-header">
        <div>
          <div class="detail-title">${this._escapeHtml(event.title || "Untitled")}</div>
          <div class="detail-badges">
            <span class="detail-badge category" style="color: ${catColor}; border-color: ${catColor};">
              ${Utils.getCategoryName(event.category)}
            </span>
            <span class="detail-badge status" style="color: ${statusColor}; border-color: ${statusColor};">
              ${event.status || "unknown"}
            </span>
            ${event.country ? `
              <span class="detail-badge" style="color: var(--text-secondary); border-color: var(--border-default);">
                ${flags} ${countryDisplay}
              </span>
            ` : ""}
          </div>
        </div>
        <button class="detail-close" onclick="State.closeEvent()">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="detail-body">
        <div class="detail-section">
          <div class="detail-section-title">Date</div>
          <div class="detail-dates">
            <span>${Utils.formatDateFull(event.start_date)}</span>
            ${event.end_date && event.end_date !== event.start_date ? `
              <span class="detail-dates-separator">→</span>
              <span>${Utils.formatDateFull(event.end_date)}</span>
            ` : ""}
          </div>
          ${event.location ? `
            <div class="detail-location">
              <span>📍</span>
              <span>${this._escapeHtml(event.location)}</span>
            </div>
          ` : ""}
        </div>

        ${event.description ? `
          <div class="detail-section">
            <div class="detail-section-title">Description</div>
            <div class="detail-description">${this._escapeHtml(event.description)}</div>
          </div>
        ` : ""}

        ${event.official_source ? `
          <div class="detail-section">
            <div class="detail-section-title">Official Source</div>
            <div class="detail-sources">
              <div class="detail-source">
                <svg class="detail-source-icon official" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1l2 5h5l-4 3 1.5 5L8 11l-4.5 3L5 9 1 6h5z" fill="currentColor"/>
                </svg>
                <span class="detail-source-name">${this._escapeHtml(event.official_source.name || "")}</span>
                <span class="detail-source-label">Official</span>
              </div>
            </div>
          </div>
        ` : ""}

        ${(event.media_sources || []).length > 0 ? `
          <div class="detail-section">
            <div class="detail-section-title">Media Sources</div>
            <div class="detail-sources">
              ${event.media_sources.map(s => `
                <div class="detail-source">
                  <svg class="detail-source-icon corroborating" width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M5 8l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span class="detail-source-name">${this._escapeHtml(s.name || "")}</span>
                  <span class="detail-source-label">${s.label || "corroborating"}</span>
                </div>
              `).join("")}
            </div>
          </div>
        ` : ""}

        ${(event.changes || []).length > 0 ? `
          <div class="detail-section">
            <div class="detail-section-title">Change History</div>
            <div class="detail-changes">
              ${event.changes.map(c => `
                <div class="detail-change">
                  <span class="detail-change-date">${Utils.formatDateShort((c.changed_at || "").slice(0, 10))}</span>
                  <span>${c.field}: ${this._escapeHtml(String(c.old_value || ""))} → ${this._escapeHtml(String(c.new_value || ""))}</span>
                </div>
              `).join("")}
            </div>
          </div>
        ` : ""}

        ${(event.tags || []).length > 0 ? `
          <div class="detail-section">
            <div class="detail-section-title">Tags</div>
            <div style="display: flex; gap: var(--space-xs); flex-wrap: wrap;">
              ${event.tags.map(t => `
                <span style="padding: 3px 10px; background: var(--bg-tertiary); border-radius: var(--radius-full); font-size: 0.8125rem; color: var(--text-secondary);">
                  ${this._escapeHtml(t)}
                </span>
              `).join("")}
            </div>
          </div>
        ` : ""}

        ${event.predictions ? `
          <div class="detail-section">
            <div class="detail-section-title">Predictive Analysis</div>
            <div class="detail-predictions">
              <div style="display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm);">
                <span class="impact-badge ${event.predictions.impact_level || "medium"}">
                  ${(event.predictions.impact_level || "medium").toUpperCase()} IMPACT
                </span>
                ${(event.predictions.affected_sectors || []).length > 0 ? `
                  <div class="sectors-list">
                    ${event.predictions.affected_sectors.map(s => `
                      <span class="sector-tag">${this._escapeHtml(s)}</span>
                    `).join("")}
                  </div>
                ` : ""}
              </div>

              ${event.predictions.analysis ? `
                <div class="prediction-item">
                  <div class="prediction-icon neutral">◆</div>
                  <div>
                    <div class="prediction-label">Analysis</div>
                    <div class="prediction-text">${this._escapeHtml(event.predictions.analysis)}</div>
                  </div>
                </div>
              ` : ""}

              ${event.predictions.if_happens ? `
                <div class="prediction-item">
                  <div class="prediction-icon positive">✓</div>
                  <div>
                    <div class="prediction-label">If happens →</div>
                    <div class="prediction-text">${this._escapeHtml(event.predictions.if_happens)}</div>
                  </div>
                </div>
              ` : ""}

              ${event.predictions.if_not ? `
                <div class="prediction-item">
                  <div class="prediction-icon negative">✗</div>
                  <div>
                    <div class="prediction-label">If not →</div>
                    <div class="prediction-text">${this._escapeHtml(event.predictions.if_not)}</div>
                  </div>
                </div>
              ` : ""}
            </div>
          </div>
        ` : ""}
      </div>

      <div class="detail-footer">
        ${event.official_source && event.official_source.url ? `
          <a href="${event.official_source.url}" target="_blank" rel="noopener" class="btn btn-primary" style="text-decoration: none;">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M5 1H2a1 1 0 00-1 1v10a1 1 0 001 1h10a1 1 0 001-1V9M8 1h5v5M13 1L7 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Official Site
          </a>
        ` : ""}
        <button class="btn btn-ghost" onclick="EventExporter.exportSingle('${event.id}')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1v8M3 6l4 4 4-4M2 12h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Export
        </button>
      </div>
    `;
  },

  _escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
  }
};
