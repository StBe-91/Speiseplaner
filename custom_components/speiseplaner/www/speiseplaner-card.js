class SpeiseplanerBaseCard extends HTMLElement {
  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = config || {};
    this._ensureShadowRoot();
    this._render();
  }

  connectedCallback() {
    this._ensureShadowRoot();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._fetchData();
    } else {
      this._maybeRefetch();
    }
  }

  getCardSize() {
    return 6;
  }

  _ensureShadowRoot() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
    }
  }

  async _fetchData() {
    if (!this._hass) return;
    try {
      this._data = await this._hass.callWS({ type: "speiseplaner/data" });
      this._error = null;
    } catch (err) {
      this._error = "Speiseplaner-Daten konnten nicht geladen werden.";
    }
    this._watchedStates = this._captureWatchedStates();
    this._render();
  }

  _captureWatchedStates() {
    const ids = [
      "sensor.speiseplaner_heute",
      "calendar.speiseplaner",
      "todo.speiseplaner_einkaufsliste",
    ];
    const out = {};
    for (const id of ids) {
      const st = this._hass.states[id];
      out[id] = st ? st.last_changed : null;
    }
    return out;
  }

  _maybeRefetch() {
    if (!this._watchedStates) return;
    const current = this._captureWatchedStates();
    const changed = Object.keys(current).some(
      (id) => current[id] !== this._watchedStates[id]
    );
    if (changed) {
      this._fetchData();
    }
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("speiseplaner", service, data);
      await this._fetchData();
    } catch (err) {
      this._error = (err && err.message) || "Aktion fehlgeschlagen.";
      this._render();
    }
  }

  _escape(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
  }

  _bindForm(root, name, buildCall) {
    const form = root.querySelector(`form[data-form='${name}']`);
    if (!form) return;
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const data = new FormData(form);
      const { service, payload } = buildCall(data, form);
      this._callService(service, payload);
    });
  }

  _bindDeleteButtons(root, action, service, idField) {
    root.querySelectorAll(`button[data-action='${action}']`).forEach((btn) => {
      btn.addEventListener("click", () =>
        this._callService(service, { [idField]: btn.dataset.id })
      );
    });
  }

  _render() {
    if (!this.shadowRoot) return;

    if (!this._data) {
      this.shadowRoot.innerHTML =
        this._baseStyles() +
        `<ha-card header="${this._cardTitle()}"><div class="content">Lade…</div></ha-card>`;
      return;
    }

    this.shadowRoot.innerHTML =
      this._baseStyles() +
      `<ha-card header="${this._cardTitle()}">
        ${this._error ? `<div class="error">${this._escape(this._error)}</div>` : ""}
        <div class="content">
          ${this._renderContent()}
        </div>
      </ha-card>`;

    this._attachListeners(this.shadowRoot);
  }

  _cardTitle() {
    return "Speiseplaner";
  }

  _renderContent() {
    return "";
  }

  _attachListeners(_root) {}

  _baseStyles() {
    return `<style>
      :host { display: block; }
      .content { padding: 8px 16px 16px; }
      form { margin-bottom: 12px; }
      .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
      input, select, textarea, button {
        font: inherit; color: var(--primary-text-color);
        background: var(--card-background-color, #fff);
        border: 1px solid var(--divider-color, #ccc); border-radius: 4px; padding: 6px 8px;
      }
      textarea { width: 100%; min-height: 60px; box-sizing: border-box; }
      button[type="submit"], button[data-action] { cursor: pointer; }
      button[data-action="add_zutat_row"] { margin: 4px 0 8px; }
      .zutat-row { display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
      ul.list { list-style: none; margin: 0; padding: 0; }
      ul.list li {
        display: flex; justify-content: space-between; align-items: center;
        padding: 6px 0; border-bottom: 1px solid var(--divider-color, #eee);
        gap: 8px;
      }
      ul.list li.empty, p.empty { color: var(--secondary-text-color); border-bottom: none; }
      .zutaten-liste { font-size: 12px; color: var(--secondary-text-color); }
      details.gruppe { margin-bottom: 8px; }
      details.gruppe summary {
        cursor: pointer; font-weight: 500; padding: 6px 0;
        color: var(--primary-text-color);
      }
      details.erledigt summary { color: var(--secondary-text-color); }
      .error {
        margin: 0 16px; padding: 8px; border-radius: 4px;
        background: var(--error-color, #db4437); color: white;
      }
      button[data-action^="delete"] {
        background: none; border: none; color: var(--secondary-text-color);
        font-size: 16px; padding: 0 4px;
      }
    </style>`;
  }
}

// -- Speiseplan-Karte -------------------------------------------------------

class SpeiseplanerSpeiseplanCard extends SpeiseplanerBaseCard {
  _cardTitle() {
    return "Speiseplan";
  }

  _rezeptName(id) {
    const rezept = this._data.rezepte.find((r) => r.id === id);
    return rezept ? rezept.name : "Unbekanntes Rezept";
  }

  _renderContent() {
    const eintraege = [...this._data.speiseplan].sort((a, b) =>
      a.datum.localeCompare(b.datum)
    );
    const rezeptOptionen = this._data.rezepte
      .map((r) => `<option value="${r.id}">${this._escape(r.name)}</option>`)
      .join("");

    const zeilen =
      eintraege
        .map(
          (e) => `
          <li>
            <span>${this._escape(e.datum)} — ${this._escape(
            this._rezeptName(e.rezept_id)
          )} (${e.portionen} Portionen)</span>
            <button data-action="delete_speiseplaneintrag" data-id="${e.id}" title="Löschen">✕</button>
          </li>`
        )
        .join("") || `<li class="empty">Noch keine Einträge.</li>`;

    return `
      <form data-form="speiseplaneintrag">
        <div class="row">
          <input type="date" name="datum" required>
          <select name="rezept_id" required>
            <option value="" disabled selected>Rezept wählen</option>
            ${rezeptOptionen}
          </select>
          <input type="number" name="portionen" min="1" value="4" required>
          <button type="submit">Hinzufügen</button>
        </div>
      </form>
      <ul class="list">${zeilen}</ul>
    `;
  }

  _attachListeners(root) {
    this._bindDeleteButtons(
      root,
      "delete_speiseplaneintrag",
      "delete_speiseplaneintrag",
      "speiseplaneintrag_id"
    );

    this._bindForm(root, "speiseplaneintrag", (data) => ({
      service: "add_speiseplaneintrag",
      payload: {
        datum: data.get("datum"),
        rezept_id: data.get("rezept_id"),
        portionen: Number(data.get("portionen")),
      },
    }));
  }
}

// -- Rezepte-Karte ------------------------------------------------------

class SpeiseplanerRezepteCard extends SpeiseplanerBaseCard {
  _cardTitle() {
    return "Rezepte";
  }

  _renderContent() {
    const kategorieOptionen = this._data.kategorien
      .map((k) => `<option value="${this._escape(k.name)}">${this._escape(k.name)}</option>`)
      .join("");

    const zeilen =
      this._data.rezepte
        .map(
          (r) => `
          <li>
            <div>
              <strong>${this._escape(r.name)}</strong> (${r.portionen} Portionen)
              <div class="zutaten-liste">${r.zutaten
                .map((z) => `${this._escape(z.name)} – ${z.anzahl} ${this._escape(z.einheit)}`)
                .join(", ")}</div>
            </div>
            <button data-action="delete_rezept" data-id="${r.id}" title="Löschen">✕</button>
          </li>`
        )
        .join("") || `<li class="empty">Noch keine Rezepte.</li>`;

    return `
      <form data-form="rezept">
        <div class="row">
          <input type="text" name="name" placeholder="Name" required>
          <input type="number" name="portionen" min="1" value="4" required>
        </div>
        <div data-zutaten>
          ${this._zutatRow(kategorieOptionen)}
        </div>
        <button type="button" data-action="add_zutat_row">+ Zutat</button>
        <textarea name="rezeptanleitung" placeholder="Zubereitung (optional)"></textarea>
        <button type="submit">Rezept speichern</button>
      </form>
      <ul class="list">${zeilen}</ul>
    `;
  }

  _zutatRow(kategorieOptionen) {
    return `
      <div class="zutat-row">
        <input type="text" placeholder="Zutat" data-zutat="name" required>
        <input type="number" placeholder="Menge" step="any" data-zutat="anzahl" required>
        <input type="text" placeholder="Einheit" data-zutat="einheit">
        <select data-zutat="kategorie">
          <option value="">Keine Kategorie</option>
          ${kategorieOptionen}
        </select>
      </div>
    `;
  }

  _addZutatRow() {
    const container = this.shadowRoot.querySelector("[data-zutaten]");
    const kategorieOptionen = this._data.kategorien
      .map((k) => `<option value="${this._escape(k.name)}">${this._escape(k.name)}</option>`)
      .join("");
    const wrapper = document.createElement("div");
    wrapper.innerHTML = this._zutatRow(kategorieOptionen);
    container.appendChild(wrapper.firstElementChild);
  }

  _attachListeners(root) {
    this._bindDeleteButtons(root, "delete_rezept", "delete_rezept", "rezept_id");

    const addZutatButton = root.querySelector("button[data-action='add_zutat_row']");
    if (addZutatButton) {
      addZutatButton.addEventListener("click", () => this._addZutatRow());
    }

    this._bindForm(root, "rezept", (data) => {
      const zutaten = [];
      root.querySelectorAll(".zutat-row").forEach((row) => {
        const name = row.querySelector("[data-zutat='name']").value.trim();
        if (!name) return;
        zutaten.push({
          name,
          anzahl: Number(row.querySelector("[data-zutat='anzahl']").value || 0),
          einheit: row.querySelector("[data-zutat='einheit']").value.trim(),
          kategorie: row.querySelector("[data-zutat='kategorie']").value,
        });
      });
      return {
        service: "add_rezept",
        payload: {
          name: data.get("name"),
          portionen: Number(data.get("portionen")),
          zutaten,
          rezeptanleitung: data.get("rezeptanleitung") || "",
        },
      };
    });
  }
}

// -- Einkaufsliste-Karte --------------------------------------------------

class SpeiseplanerEinkaufslisteCard extends SpeiseplanerBaseCard {
  _cardTitle() {
    return "Einkaufsliste";
  }

  _renderContent() {
    const offene = this._data.einkaufsliste.filter((e) => !e.erledigt);
    const erledigte = this._data.einkaufsliste.filter((e) => e.erledigt);
    const gruppen = this._gruppiereNachKategorie(offene);
    const kategorieOptionen = this._data.kategorien
      .map((k) => `<option value="${this._escape(k.name)}">${this._escape(k.name)}</option>`)
      .join("");

    const gruppenHtml =
      Object.entries(gruppen)
        .map(([kategorie, eintraege]) => this._renderGruppe(kategorie, eintraege))
        .join("") || `<p class="empty">Einkaufsliste ist leer.</p>`;

    const erledigtHtml = erledigte.length
      ? `<details class="gruppe erledigt">
          <summary>Erledigt (${erledigte.length})</summary>
          ${this._renderItems(erledigte)}
        </details>`
      : "";

    return `
      <form data-form="einkaufsliste_eintrag">
        <div class="row">
          <input type="text" name="name" placeholder="Artikel" required>
          <input type="number" name="anzahl" step="any" value="1" required>
          <input type="text" name="einheit" placeholder="Einheit">
          <select name="kategorie">
            <option value="">Keine Kategorie</option>
            ${kategorieOptionen}
          </select>
          <button type="submit">Hinzufügen</button>
        </div>
      </form>
      ${gruppenHtml}
      ${erledigtHtml}
    `;
  }

  _gruppiereNachKategorie(eintraege) {
    const gruppen = {};
    for (const eintrag of eintraege) {
      const key = eintrag.kategorie || "Ohne Kategorie";
      if (!gruppen[key]) gruppen[key] = [];
      gruppen[key].push(eintrag);
    }
    return gruppen;
  }

  _renderGruppe(kategorie, eintraege) {
    return `
      <details class="gruppe" open>
        <summary>${this._escape(kategorie)} (${eintraege.length})</summary>
        ${this._renderItems(eintraege)}
      </details>
    `;
  }

  _renderItems(eintraege) {
    const zeilen = eintraege
      .map((e) => {
        const menge = e.einheit
          ? ` (${e.anzahl} ${this._escape(e.einheit)})`
          : e.anzahl && e.anzahl !== 1
          ? ` (${e.anzahl})`
          : "";
        return `
          <li>
            <label>
              <input type="checkbox" data-action="toggle_erledigt" data-id="${e.id}" ${
          e.erledigt ? "checked" : ""
        }>
              ${this._escape(e.name)}${menge}
            </label>
            <button data-action="delete_einkaufsliste_eintrag" data-id="${e.id}" title="Löschen">✕</button>
          </li>`;
      })
      .join("");

    return `<ul class="list">${zeilen}</ul>`;
  }

  _attachListeners(root) {
    this._bindDeleteButtons(
      root,
      "delete_einkaufsliste_eintrag",
      "delete_einkaufsliste_eintrag",
      "einkaufslisteneintrag_id"
    );

    root.querySelectorAll("input[data-action='toggle_erledigt']").forEach((checkbox) => {
      checkbox.addEventListener("change", () =>
        this._callService("set_einkaufsliste_erledigt", {
          einkaufslisteneintrag_id: checkbox.dataset.id,
          erledigt: checkbox.checked,
        })
      );
    });

    this._bindForm(root, "einkaufsliste_eintrag", (data) => ({
      service: "add_einkaufsliste_eintrag",
      payload: {
        name: data.get("name"),
        anzahl: Number(data.get("anzahl")),
        einheit: data.get("einheit") || "",
        kategorie: data.get("kategorie") || "",
      },
    }));
  }
}

customElements.define("speiseplaner-speiseplan-card", SpeiseplanerSpeiseplanCard);
customElements.define("speiseplaner-rezepte-card", SpeiseplanerRezepteCard);
customElements.define("speiseplaner-einkaufsliste-card", SpeiseplanerEinkaufslisteCard);

window.customCards = window.customCards || [];
window.customCards.push(
  {
    type: "speiseplaner-speiseplan-card",
    name: "Speiseplaner: Speiseplan",
    description: "Speiseplan-Einträge anzeigen und bearbeiten.",
  },
  {
    type: "speiseplaner-rezepte-card",
    name: "Speiseplaner: Rezepte",
    description: "Rezepte anlegen und verwalten.",
  },
  {
    type: "speiseplaner-einkaufsliste-card",
    name: "Speiseplaner: Einkaufsliste",
    description: "Kategorisierte Einkaufsliste anzeigen und abhaken.",
  }
);
