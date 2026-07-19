from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .services import async_setup_services
from .storage import SpeiseplanerStorage


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    storage = SpeiseplanerStorage(hass)
    await storage.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = storage

    await async_setup_services(hass, storage)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
