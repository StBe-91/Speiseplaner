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

        return self.async_show_form(
            step_id="kategorien",
            data_schema=_kategorien_schema(vorausgewaehlt=list(DEFAULT_KATEGORIE_IDS)),
        )

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

    Struktur für zukünftige Erweiterungen: async_step_init zeigt ein Menü an.
    Neuen Options-Bereich hinzufügen:
      1. Eintrag (id + Bezeichnung) in menu_options und in strings.json/
         translations/*.json unter options.step.init.menu_options ergänzen.
      2. Eine Methode async_step_<id> ergänzen, die ein Formular zeigt und
         mit self.async_create_entry(title="", data={}) abschließt.
    Mehr Vorwissen ist dafür nicht nötig - die Menü-Navigation läuft automatisch.
    """

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["kategorien"])

    async def async_step_kategorien(self, user_input=None):
        storage = self.hass.data[DOMAIN][self.config_entry.entry_id]

        if user_input is not None:
            ausgewaehlt = set(user_input.get("kategorien", []))
            aktuelle = {
                k["id"] for k in storage.data["kategorien"] if k["id"] in DEFAULT_KATEGORIE_IDS
            }
            for kategorie in DEFAULT_KATEGORIEN:
                kategorie_id = kategorie["id"]
                if kategorie_id in ausgewaehlt and kategorie_id not in aktuelle:
                    storage.data["kategorien"].append(dict(kategorie))
                elif kategorie_id not in ausgewaehlt and kategorie_id in aktuelle:
                    storage.remove("kategorien", kategorie_id)
            await storage.async_save()
            return self.async_create_entry(title="", data={})

        aktuelle = [
            k["id"] for k in storage.data["kategorien"] if k["id"] in DEFAULT_KATEGORIE_IDS
        ]
        return self.async_show_form(
            step_id="kategorien",
            data_schema=_kategorien_schema(vorausgewaehlt=aktuelle),
        )


def _kategorien_schema(vorausgewaehlt: List[str]) -> vol.Schema:
    optionen = {k["id"]: k["name"] for k in DEFAULT_KATEGORIEN}
    return vol.Schema(
        {
            vol.Optional("kategorien", default=vorausgewaehlt): cv.multi_select(optionen),
        }
    )
