from datetime import date, timedelta

from custom_components.speiseplaner.calendar import SpeiseplanCalendar
from custom_components.speiseplaner.storage import SpeiseplanerStorage


class FakeDatetime:
    """Minimales Ersatz-Objekt für die von async_get_events übergebenen Grenzen."""

    def __init__(self, d: date):
        self._d = d

    def date(self) -> date:
        return self._d


def make_storage():
    storage = SpeiseplanerStorage(hass=object())
    storage.data["rezepte"] = [{"id": "r1", "name": "Lasagne", "portionen": 4, "zutaten": [], "rezeptanleitung": ""}]
    return storage


def test_build_event_setzt_start_ende_und_zusammenfassung():
    storage = make_storage()
    storage.data["speiseplan"] = [{"id": "s1", "datum": "2026-07-20", "rezept_id": "r1", "portionen": 8}]
    kalender = SpeiseplanCalendar(storage, "entry1")

    events = kalender._all_events()

    assert len(events) == 1
    event = events[0]
    assert event.start == date(2026, 7, 20)
    assert event.end == date(2026, 7, 21)
    assert event.summary == "Lasagne (8 Portionen)"
    assert event.uid == "s1"


def test_build_event_mit_unbekanntem_rezept():
    storage = make_storage()
    storage.data["speiseplan"] = [{"id": "s1", "datum": "2026-07-20", "rezept_id": "unbekannt", "portionen": 2}]
    kalender = SpeiseplanCalendar(storage, "entry1")

    event = kalender._all_events()[0]

    assert event.summary == "Unbekanntes Rezept (2 Portionen)"


async def test_async_get_events_filtert_nach_zeitraum():
    storage = make_storage()
    storage.data["speiseplan"] = [
        {"id": "s1", "datum": "2026-07-18", "rezept_id": "r1", "portionen": 4},
        {"id": "s2", "datum": "2026-07-20", "rezept_id": "r1", "portionen": 4},
        {"id": "s3", "datum": "2026-07-25", "rezept_id": "r1", "portionen": 4},
    ]
    kalender = SpeiseplanCalendar(storage, "entry1")

    events = await kalender.async_get_events(
        hass=None,
        start_date=FakeDatetime(date(2026, 7, 19)),
        end_date=FakeDatetime(date(2026, 7, 21)),
    )

    assert [e.uid for e in events] == ["s2"]


def test_event_gibt_naechstes_kommendes_ereignis_zurueck():
    storage = make_storage()
    heute = date.today()
    storage.data["speiseplan"] = [
        {"id": "vergangen", "datum": (heute - timedelta(days=1)).isoformat(), "rezept_id": "r1", "portionen": 4},
        {"id": "spaeter", "datum": (heute + timedelta(days=5)).isoformat(), "rezept_id": "r1", "portionen": 4},
        {"id": "naechstes", "datum": (heute + timedelta(days=1)).isoformat(), "rezept_id": "r1", "portionen": 4},
    ]
    kalender = SpeiseplanCalendar(storage, "entry1")

    assert kalender.event.uid == "naechstes"


def test_event_gibt_none_zurueck_wenn_keine_eintraege():
    storage = make_storage()
    kalender = SpeiseplanCalendar(storage, "entry1")

    assert kalender.event is None
