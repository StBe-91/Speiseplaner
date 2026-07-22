from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent

from .const import DOMAIN
from .entity import StorageUpdateMixin, build_device_info
from .mahlzeiten import MAHLZEIT_LABELS


async def async_setup_entry(hass, entry, async_add_entities):
    storage = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SpeiseplanCalendar(storage, entry.entry_id)])


class SpeiseplanCalendar(StorageUpdateMixin, CalendarEntity):
    _attr_name = "Speiseplaner"

    def __init__(self, storage, entry_id):
        self.storage = storage
        self._attr_unique_id = f"{entry_id}_speiseplan"
        self._attr_device_info = build_device_info(entry_id)

    def _build_event(self, eintrag: dict) -> CalendarEvent:
        rezept = self.storage.find("rezepte", eintrag["rezept_id"])
        name = rezept["name"] if rezept else "Unbekanntes Rezept"
        mahlzeit_label = MAHLZEIT_LABELS.get(eintrag.get("mahlzeit", ""))
        titel = f"{mahlzeit_label}: {name}" if mahlzeit_label else name
        tag = date.fromisoformat(eintrag["datum"])
        return CalendarEvent(
            start=tag,
            end=tag + timedelta(days=1),
            summary=f"{titel} ({eintrag['portionen']} Portionen)",
            uid=eintrag["id"],
        )

    def _all_events(self) -> list[CalendarEvent]:
        return [self._build_event(e) for e in self.storage.data["speiseplan"]]

    @property
    def event(self) -> CalendarEvent | None:
        heute = date.today()
        kommende = sorted(
            (e for e in self._all_events() if e.start >= heute),
            key=lambda e: e.start,
        )
        return kommende[0] if kommende else None

    async def async_get_events(
        self, hass, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        return [
            event
            for event in self._all_events()
            if start_date.date() <= event.start <= end_date.date()
        ]
