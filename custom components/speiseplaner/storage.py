from homeassistant.helpers.storage import Store
from .const import STORAGE_KEY, STORAGE_VERSION


class SpeiseplanerStorage:
    def __init__(self, hass):
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.data = {"rezepte": [], "speiseplan": [], "kategorien": []}

    async def async_load(self):
        stored = await self.store.async_load()
        if stored:
            self.data = stored

    async def async_save(self):
        await self.store.async_save(self.data)