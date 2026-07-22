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

  _shouldSkipRefetch() {
    return false;
  }

  _maybeRefetch() {
    if (this._shouldSkipRefetch()) return;
    if (!this._watchedStates) return;
    const current = this._captureWatchedStates();
    const changed = Object.keys(current).some(
      (id) => current[id] !== this._watchedStates[id]
    );
    if (changed) {
      this._fetchData();
    }
  }

  /** Ruft einen Service auf und lädt anschließend neu. Gibt true bei Erfolg,
   * false bei Fehler zurück (Fehlertext liegt danach in this._error). */
  async _callService(service, data) {
    try {
      await this._hass.callService("speiseplaner", service, data);
      await this._fetchData();
      return true;
    } catch (err) {
      this._error = (err && err.message) || "Aktion fehlgeschlagen.";
      this._render();
      return false;
    }
  }

  _escape(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
  }

  /** Sehr einfache Auszeichnung: Leerzeile = neuer Absatz, Zeilen mit '- '
   * oder '* ' am Anfang werden als Liste dargestellt. Bewusst kein volles
   * Markdown, um ohne externe Bibliothek auszukommen. */
  _renderMarkdownLite(text) {
    if (!text) return "";
    const bloecke = text.split(/\n\s*\n/);
    return bloecke
      .map((block) => {
        const zeilen = block
          .split("\n")
          .map((z) => z.trim())
          .filter((z) => z !== "");
        if (zeilen.length === 0) return "";
        const istListe = zeilen.every((z) => /^[-*]\s+/.test(z));
        if (istListe) {
          const items = zeilen
            .map((z) => `<li>${this._escape(z.replace(/^[-*]\s+/, ""))}</li>`)
            .join("");
          return `<ul>${items}</ul>`;
        }
        return `<p>${zeilen.map((z) => this._escape(z)).join("<br>")}</p>`;
      })
      .join("");
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
      .zutat-row { display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; align-items: center; }
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

  getCardSize() {
    return 8;
  }

  _shouldSkipRefetch() {
    return this._modalOpen === true;
  }

  _renderContent() {
    const zeilen =
      this._data.rezepte.map((r) => this._renderRezeptZeile(r)).join("") ||
      `<p class="empty">Noch keine Rezepte.</p>`;

    return `
      <div class="toolbar">
        <button class="fab-add" type="button" data-action="open_add_modal" title="Rezept hinzufügen">+</button>
      </div>
      <ul class="list rezept-liste">${zeilen}</ul>
      ${this._modalOpen ? this._renderModal() : ""}
    `;
  }

  _formatZeiten(rezept) {
    const teile = [];
    if (rezept.vorbereitungsdauer) teile.push(`Vorbereitung ${rezept.vorbereitungsdauer} min`);
    if (rezept.zubereitungsdauer) teile.push(`Zubereitung ${rezept.zubereitungsdauer} min`);
    return teile.join(" · ");
  }

  _renderRezeptZeile(rezept) {
    const zeiten = this._formatZeiten(rezept);
    return `
      <li class="rezept-zeile">
        <div class="rezept-kopf">
          <div>
            <strong>${this._escape(rezept.name)}</strong> (${rezept.portionen} Portionen)
            ${zeiten ? `<div class="zeiten">${this._escape(zeiten)}</div>` : ""}
          </div>
          <div class="aktionen">
            <button data-action="edit_rezept" data-id="${rezept.id}" title="Bearbeiten">✏️</button>
            <button data-action="delete_rezept" data-id="${rezept.id}" title="Löschen">✕</button>
          </div>
        </div>
        ${rezept.bild ? `<img class="rezept-bild" data-bild-id="${rezept.bild}" alt="">` : ""}
        <div class="zutaten-liste">${rezept.zutaten
          .map((z) => `${this._escape(z.name)} – ${z.anzahl} ${this._escape(z.einheit)}`)
          .join(", ")}</div>
        ${
          rezept.rezeptanleitung
            ? `<details class="anleitung">
                <summary>Zubereitung</summary>
                ${this._renderMarkdownLite(rezept.rezeptanleitung)}
              </details>`
            : ""
        }
      </li>
    `;
  }

  _kategorieOptionenHtml(ausgewaehlt) {
    return this._data.kategorien
      .map((k) => {
        const value = this._escape(k.name);
        const selected = k.name === ausgewaehlt ? " selected" : "";
        return `<option value="${value}"${selected}>${value}</option>`;
      })
      .join("");
  }

  _zutatRow(zutat) {
    return `
      <div class="zutat-eintrag">
        <div class="zutat-row">
          <input type="number" class="feld-klein" placeholder="Menge" step="any" data-zutat="anzahl" value="${
            zutat?.anzahl ?? ""
          }" required>
          <input type="text" class="feld-klein" placeholder="Einheit" data-zutat="einheit" value="${this._escape(
            zutat?.einheit || ""
          )}">
          <input type="text" placeholder="Zutat" data-zutat="name" value="${this._escape(
            zutat?.name || ""
          )}" required>
          <select data-zutat="kategorie">
            <option value="">Keine Kategorie</option>
            ${this._kategorieOptionenHtml(zutat?.kategorie || "")}
          </select>
          <button type="button" data-action="remove_zutat_row" title="Zutat entfernen">✕</button>
        </div>
        <hr class="zutat-trenner">
      </div>
    `;
  }

  _renderModal() {
    const rezept = this._editingRezept;
    const titel = rezept ? "Rezept bearbeiten" : "Rezept hinzufügen";
    const zutatenRows =
      rezept && rezept.zutaten.length
        ? rezept.zutaten.map((z) => this._zutatRow(z)).join("")
        : this._zutatRow();

    return `
      <div class="modal-overlay" data-modal>
        <div class="modal-box">
          <h2 class="modal-titel">${this._escape(titel)}</h2>
          ${this._error ? `<div class="error">${this._escape(this._error)}</div>` : ""}
          <form data-form="rezept-modal">
            <div class="feld-zeile">
              <input type="text" class="feld-voll" name="name" placeholder="Name" value="${this._escape(
                rezept?.name || ""
              )}" required>
            </div>
            <div class="feld-zeile">
              <span>Rezept für:</span>
              <input type="number" class="feld-mittel" name="portionen" min="1" value="${
                rezept?.portionen ?? 4
              }" required>
              <span>Portionen</span>
            </div>
            <div class="feld-zeile">
              <span>Vorbereitungszeit:</span>
              <input type="number" class="feld-mittel" name="vorbereitungsdauer" min="0" value="${
                rezept?.vorbereitungsdauer ?? 0
              }">
              <span>Minuten</span>
              <span>Zubereitungszeit:</span>
              <input type="number" class="feld-mittel" name="zubereitungsdauer" min="0" value="${
                rezept?.zubereitungsdauer ?? 0
              }">
              <span>Minuten</span>
            </div>
            <div class="bild-bereich">
              ${
                rezept?.bild
                  ? `<img class="bild-vorschau" data-bild-id="${rezept.bild}" alt="">
                     <label><input type="checkbox" name="bild_entfernen"> Bild entfernen</label>`
                  : ""
              }
              <label>${rezept?.bild ? "Bild ersetzen" : "Bild hinzufügen"}
                <input type="file" name="bild_datei" accept="image/*">
              </label>
            </div>
            <div data-zutaten>${zutatenRows}</div>
            <button type="button" data-action="add_zutat_row">weitere Zutat</button>
            <div class="feld-zeile">
              <h3>Zubereitung</h3>
            </div>
            <textarea name="rezeptanleitung"
              placeholder="Absätze durch Leerzeile trennen, Listenpunkte mit '- ' beginnen"
            >${this._escape(rezept?.rezeptanleitung || "")}</textarea>
            <div class="modal-aktionen">
              <button type="button" data-action="close_modal">Abbrechen</button>
              <button type="button" data-action="save_modal">Speichern</button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _attachListeners(root) {
    this._bindDeleteButtons(root, "delete_rezept", "delete_rezept", "rezept_id");
    this._signiereBilder(root);

    const addButton = root.querySelector("button[data-action='open_add_modal']");
    if (addButton) {
      addButton.addEventListener("click", () => this._openModal(null));
    }

    root.querySelectorAll("button[data-action='edit_rezept']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const rezept = this._data.rezepte.find((r) => r.id === btn.dataset.id) || null;
        this._openModal(rezept);
      });
    });

    if (!this._modalOpen) return;

    const overlay = root.querySelector("[data-modal]");
    if (overlay) {
      overlay.addEventListener("click", (ev) => {
        if (ev.target === overlay) this._closeModal();
      });
    }

    if (this._escHandler) {
      document.removeEventListener("keydown", this._escHandler);
    }
    this._escHandler = (ev) => {
      if (ev.key === "Escape") this._closeModal();
    };
    document.addEventListener("keydown", this._escHandler);

    const closeButton = root.querySelector("button[data-action='close_modal']");
    if (closeButton) {
      closeButton.addEventListener("click", () => this._closeModal());
    }

    const addZutatButton = root.querySelector("button[data-action='add_zutat_row']");
    if (addZutatButton) {
      addZutatButton.addEventListener("click", () => this._addZutatRow());
    }

    root.querySelectorAll("button[data-action='remove_zutat_row']").forEach((btn) => {
      btn.addEventListener("click", () => btn.closest(".zutat-eintrag").remove());
    });

    const saveButton = root.querySelector("button[data-action='save_modal']");
    if (saveButton) {
      saveButton.addEventListener("click", () => this._handleSave(root));
    }
  }

  disconnectedCallback() {
    if (this._escHandler) {
      document.removeEventListener("keydown", this._escHandler);
      this._escHandler = null;
    }
  }

  /** Löst signierte, kurzlebige URLs für Bilder auf (Bilder sind über die
   * HA-API nur mit gültigem Token abrufbar, ein <img src> ohne Signatur
   * würde mit 401 fehlschlagen). */
  async _signiereBilder(root) {
    const bilder = root.querySelectorAll("img[data-bild-id]");
    for (const img of bilder) {
      const bildId = img.dataset.bildId;
      try {
        const signiert = await this._hass.callWS({
          type: "auth/sign_path",
          path: `/api/image/serve/${bildId}/512x512`,
        });
        img.src = signiert.path;
      } catch (err) {
        // Bild bleibt ohne Vorschau, kein harter Fehler für die Karte.
      }
    }
  }

  _openModal(rezept) {
    this._editingRezept = rezept;
    this._modalOpen = true;
    this._error = null;
    this._render();
  }

  _closeModal() {
    this._modalOpen = false;
    this._editingRezept = null;
    this._error = null;
    this._render();
  }

  _addZutatRow() {
    const container = this.shadowRoot.querySelector("[data-zutaten]");
    const wrapper = document.createElement("div");
    wrapper.innerHTML = this._zutatRow();
    const eintrag = wrapper.firstElementChild;
    container.appendChild(eintrag);
    eintrag
      .querySelector("[data-action='remove_zutat_row']")
      .addEventListener("click", () => eintrag.remove());
  }

  async _hochladenBild(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await this._hass.fetchWithAuth("/api/image/upload", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      throw new Error("Bild-Upload fehlgeschlagen.");
    }
    const ergebnis = await response.json();
    return ergebnis.id;
  }

  async _handleSave(root) {
    const form = root.querySelector("form[data-form='rezept-modal']");
    const data = new FormData(form);

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

    let bild = this._editingRezept ? this._editingRezept.bild || "" : "";
    const entfernenCheckbox = form.querySelector("[name='bild_entfernen']");
    if (entfernenCheckbox && entfernenCheckbox.checked) {
      bild = "";
    }
    const bildDatei = form.querySelector("[name='bild_datei']").files[0];
    if (bildDatei) {
      try {
        bild = await this._hochladenBild(bildDatei);
      } catch (err) {
        this._error = "Bild-Upload fehlgeschlagen. Rezept wurde nicht gespeichert.";
        this._render();
        return;
      }
    }

    const payload = {
      name: data.get("name"),
      portionen: Number(data.get("portionen")),
      vorbereitungsdauer: Number(data.get("vorbereitungsdauer") || 0),
      zubereitungsdauer: Number(data.get("zubereitungsdauer") || 0),
      zutaten,
      rezeptanleitung: data.get("rezeptanleitung") || "",
      bild,
    };

    let service = "add_rezept";
    if (this._editingRezept) {
      service = "update_rezept";
      payload.rezept_id = this._editingRezept.id;
    }

    const erfolgreich = await this._callService(service, payload);
    if (erfolgreich) {
      this._closeModal();
    }
  }

  _baseStyles() {
    return (
      super._baseStyles() +
      `<style>
        .toolbar { display: flex; justify-content: flex-end; margin-bottom: 8px; }
        .fab-add {
          width: 36px; height: 36px; border-radius: 50%; font-size: 20px;
          line-height: 1; padding: 0; background: var(--primary-color, #03a9f4); color: white;
          border: none;
        }
        .rezept-liste li.rezept-zeile { display: block; }
        .rezept-kopf { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
        .aktionen { display: flex; gap: 4px; flex-shrink: 0; }
        .aktionen button { background: none; border: none; font-size: 16px; padding: 0 4px; }
        .zeiten { font-size: 12px; color: var(--secondary-text-color); }
        .rezept-bild {
          max-width: 100%; max-height: 160px; border-radius: 4px; margin: 6px 0;
          display: block; object-fit: cover;
        }
        details.anleitung summary { font-size: 13px; }
        details.anleitung ul { margin: 4px 0; padding-left: 20px; }
        details.anleitung p { margin: 4px 0; }
        .modal-overlay {
          position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5);
          display: flex; align-items: center; justify-content: center;
          z-index: 1000; padding: 16px; box-sizing: border-box;
        }
        .modal-box {
          background: var(--card-background-color, #fff); color: var(--primary-text-color);
          border-radius: 8px; padding: 16px; max-width: 480px; width: 100%;
          max-height: 90vh; overflow-y: auto; box-sizing: border-box;
        }
        .modal-titel { margin: 0 0 12px; font-size: 20px; }
        .feld-zeile { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
        .feld-zeile h3 { margin: 0; font-size: 15px; }
        .feld-voll { width: 100%; box-sizing: border-box; }
        .feld-mittel { width: 6ch; flex: 0 0 auto; }
        .feld-klein { width: 4ch; flex: 0 0 auto; }
        .bild-bereich { margin: 8px 0; display: flex; flex-direction: column; gap: 6px; }
        .bild-vorschau { max-width: 100%; max-height: 160px; border-radius: 4px; object-fit: cover; }
        .zutat-eintrag { margin-bottom: 4px; }
        .zutat-trenner { border: none; border-top: 1px solid var(--divider-color, #ddd); margin: 8px 0; }
        .modal-aktionen { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
        button[data-action='remove_zutat_row'] {
          background: none; border: none; color: var(--secondary-text-color); padding: 0 4px;
        }
      </style>`
    );
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
    description: "Rezepte mit Bild, Zeiten und formatierter Zubereitung verwalten.",
  },
  {
    type: "speiseplaner-einkaufsliste-card",
    name: "Speiseplaner: Einkaufsliste",
    description: "Kategorisierte Einkaufsliste anzeigen und abhaken.",
  }
);
