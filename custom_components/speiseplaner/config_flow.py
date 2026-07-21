import uuid
from typing import List

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .kategorien_defaults import DEFAULT_KATEGORIEN
from .storage import SpeiseplanerStorage

DEFAULT_KATEGORIE_IDS = {k["id"] for k in DEFAULT_KATEGORIEN}


class SpeiseplanerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SpeiseplanerOptionsFlow()

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_kategorien()

    async def async_step_kategorien(self, user_input=None):
        if user_input is not None:
            await self._async_seed_kategorien(user_input.get("kategorien", []))
            return self.async_create_entry(title="Speiseplaner", data={})

        optionen = {k["id"]: k["name"] for k in DEFAULT_KATEGORIEN}
        schema = vol.Schema(
            {
                vol.Optional("kategorien", default=list(optionen)): cv.multi_select(optionen),
            }
        )
        return self.async_show_form(step_id="kategorien", data_schema=schema)

    async def _async_seed_kategorien(self, ausgewaehlte_ids: List[str]) -> None:
        self._storage = SpeiseplanerStorage(self.hass)
        await self._storage.async_load()
        self._storage.data["kategorien"] = [
            {"id": k["id"], "name": k["name"], "autoeinkauf": k["autoeinkauf"]}
            for k in DEFAULT_KATEGORIEN
            if k["id"] in ausgewaehlte_ids
        ]
        await self._storage.async_save()


class SpeiseplanerOptionsFlow(config_entries.OptionsFlow):
    """Options-Flow des Speiseplaners.

    Kategorien werden hier unabhängig von ihrer Herkunft (Standard-Auswahl bei
    der Einrichtung oder frei angelegt) einheitlich verwaltet - es gibt danach
    keinen Unterschied mehr zwischen beiden.

    Struktur für zukünftige, weitere Options-Bereiche: async_step_init zeigt
    ein Menü. Neuen Bereich hinzufügen:
      1. Eintrag (id + Bezeichnung) in menu_options und in strings.json/
         translations/*.json unter options.step.init.menu_options ergänzen.
      2. Eine oder mehrere Methoden async_step_<id> ergänzen, die ein
         Formular zeigen; zum Abschluss entweder self.async_create_entry(...)
         (schließt den Dialog) oder return await self.async_step_init()
         (zurück zum Menü, für mehrere Aktionen in einer Sitzung).
    Mehr Vorwissen ist dafür nicht nötig.
    """

    def _storage(self):
        return self.hass.data[DOMAIN][self.config_entry.entry_id]

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "kategorie_hinzufuegen",
                "kategorie_bearbeiten",
                "kategorie_loeschen",
            ],
        )

    async def async_step_kategorie_hinzufuegen(self, user_input=None):
        if user_input is not None:
            storage = self._storage()
            storage.data["kategorien"].append(
                {
                    "id": str(uuid.uuid4()),
                    "name": user_input["name"],
                    "autoeinkauf": user_input["autoeinkauf"],
                }
            )
            await storage.async_save()
            return await self.async_step_init()

        schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Optional("autoeinkauf", default=True): bool,
            }
        )
        return self.async_show_form(step_id="kategorie_hinzufuegen", data_schema=schema)

    async def async_step_kategorie_bearbeiten(self, user_input=None):
        storage = self._storage()
        if not storage.data["kategorien"]:
            return self.async_abort(reason="keine_kategorien")

        if user_input is not None:
            self._bearbeite_id = user_input["kategorie_id"]
            return await self.async_step_kategorie_bearbeiten_formular()

        optionen = {k["id"]: k["name"] for k in storage.data["kategorien"]}
        schema = vol.Schema({vol.Required("kategorie_id"): vol.In(optionen)})
        return self.async_show_form(step_id="kategorie_bearbeiten", data_schema=schema)

    async def async_step_kategorie_bearbeiten_formular(self, user_input=None):
        storage = self._storage()
        kategorie = storage.find("kategorien", self._bearbeite_id)

        if user_input is not None:
            kategorie["name"] = user_input["name"]
            kategorie["autoeinkauf"] = user_input["autoeinkauf"]
            await storage.async_save()
            return await self.async_step_init()

        schema = vol.Schema(
            {
                vol.Required("name", default=kategorie["name"]): str,
                vol.Optional("autoeinkauf", default=kategorie["autoeinkauf"]): bool,
            }
        )
        return self.async_show_form(
            step_id="kategorie_bearbeiten_formular", data_schema=schema
        )

    async def async_step_kategorie_loeschen(self, user_input=None):
        storage = self._storage()
        if not storage.data["kategorien"]:
            return self.async_abort(reason="keine_kategorien")

        if user_input is not None:
            for kategorie_id in user_input.get("kategorien", []):
                storage.remove("kategorien", kategorie_id)
            await storage.async_save()
            return await self.async_step_init()

        optionen = {k["id"]: k["name"] for k in storage.data["kategorien"]}
        schema = vol.Schema(
            {vol.Optional("kategorien", default=[]): cv.multi_select(optionen)}
        )
        return self.async_show_form(step_id="kategorie_loeschen", data_schema=schema)
