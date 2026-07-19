from homeassistant.helpers.entity import Entity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    storage = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SpeiseplanSensor(storage, entry.entry_id)])


class SpeiseplanSensor(Entity):
    _attr_name = "Speiseplaner Today"

    def __init__(self, storage, entry_id):
        self.storage = storage
        self._attr_unique_id = f"{entry_id}_today"

    @property
    def state(self):
        return "ready"

    @property
    def extra_state_attributes(self):
        return self.storage.data
