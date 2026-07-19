from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .models import Rezept, Zutat


async def async_setup_entry(hass, entry, async_add_entities):
    pass


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    storage = hass.data[DOMAIN]["storage"]
    async_add_entities([SpeiseplanSensor(storage)])


class SpeiseplanSensor(Entity):
    def __init__(self, storage):
        self.storage = storage
        self._attr_name = "Speiseplaner Today"

    @property
    def state(self):
        return "ready"

    @property
    def extra_state_attributes(self):
        return self.storage.data