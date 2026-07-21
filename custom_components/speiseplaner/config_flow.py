from typing import List

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .kategorien_defaults import DEFAULT_KATEGORIEN
from .storage import SpeiseplanerStorage


class SpeiseplanerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

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
