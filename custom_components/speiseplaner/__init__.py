from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .frontend import async_register_static_paths
from .services import async_setup_services
from .storage import SpeiseplanerStorage
from .websocket_api import async_setup_websocket_api

FRONTEND_SETUP_DONE = f"{DOMAIN}_frontend_setup_done"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    storage = SpeiseplanerStorage(hass)
    await storage.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = storage

    await async_setup_services(hass, storage)

    # WebSocket-Kommando und statische Karten-Datei nur einmal registrieren,
    # da Home Assistant nur eine Instanz dieser Integration zulässt, ein
    # Reload aber async_setup_entry erneut aufruft.
    if not hass.data.get(FRONTEND_SETUP_DONE):
        hass.data[FRONTEND_SETUP_DONE] = True
        async_setup_websocket_api(hass)
        await async_register_static_paths(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
