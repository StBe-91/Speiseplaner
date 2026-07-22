from datetime import date

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .entity import StorageUpdateMixin, build_device_info
from .mahlzeiten import MAHLZEIT_LABELS


async def async_setup_entry(hass, entry, async_add_entities):
    storage = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SpeiseplanHeuteSensor(storage, entry.entry_id)])


class SpeiseplanHeuteSensor(StorageUpdateMixin, SensorEntity):
    _attr_name = "Speiseplaner Heute"

    def __init__(self, storage, entry_id):
        self.storage = storage
        self._attr_unique_id = f"{entry_id}_heute"
        self._attr_device_info = build_device_info(entry_id)

    def _heutige_eintraege(self) -> list[dict]:
        heute = date.today().isoformat()
        return [e for e in self.storage.data["speiseplan"] if e["datum"] == heute]

    @property
    def native_value(self) -> str:
        namen = []
        for eintrag in self._heutige_eintraege():
            rezept = self.storage.find("rezepte", eintrag["rezept_id"])
            name = rezept["name"] if rezept else "Unbekanntes Rezept"
            mahlzeit_label = MAHLZEIT_LABELS.get(eintrag.get("mahlzeit", ""))
            namen.append(f"{mahlzeit_label}: {name}" if mahlzeit_label else name)
        return ", ".join(namen) if namen else "Kein Eintrag"

    @property
    def extra_state_attributes(self) -> dict:
        return {"anzahl_eintraege": len(self._heutige_eintraege())}
