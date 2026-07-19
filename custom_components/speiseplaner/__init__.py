from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .storage import SpeiseplanerStorage
from .services import async_setup_services


async def async_setup(hass: HomeAssistant, config: dict):
    storage = SpeiseplanerStorage(hass)
    await storage.async_load()

    hass.data[DOMAIN] = {
        "storage": storage
    }

    await async_setup_services(hass, storage)

    return True