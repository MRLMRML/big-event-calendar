const Search = {
  init() {
    this.input = document.getElementById("search-input");
    if (!this.input) return;

    this.input.addEventListener("input", Utils.debounce((e) => {
      State.setSearch(e.target.value);
    }, 300));

    this.input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.input.value = "";
        State.setSearch("");
        this.input.blur();
      }
    });
  },

  clear() {
    if (this.input) {
      this.input.value = "";
      State.setSearch("");
    }
  }
};
