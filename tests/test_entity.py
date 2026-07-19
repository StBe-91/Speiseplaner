from custom_components.speiseplaner.calendar import SpeiseplanCalendar
from custom_components.speiseplaner.const import DOMAIN, SIGNAL_UPDATE
from custom_components.speiseplaner.entity import StorageUpdateMixin, build_device_info
from custom_components.speiseplaner.sensor import SpeiseplanHeuteSensor
from custom_components.speiseplaner.storage import SpeiseplanerStorage
from custom_components.speiseplaner.todo import EinkaufslisteTodoListEntity


def test_build_device_info_gruppiert_unter_einem_geraet():
    info = build_device_info("entry1")

    assert info["identifiers"] == {(DOMAIN, "entry1")}
    assert info["name"] == "Speiseplaner"


async def test_async_save_sendet_dispatcher_signal(monkeypatch):
    aufrufe = []
    monkeypatch.setattr(
        "custom_components.speiseplaner.storage.async_dispatcher_send",
        lambda hass, signal: aufrufe.append((hass, signal)),
    )
    hass = object()
    storage = SpeiseplanerStorage(hass=hass)

    await storage.async_save()

    assert aufrufe == [(hass, SIGNAL_UPDATE)]


async def test_mixin_verbindet_sich_mit_dispatcher_signal(monkeypatch):
    verbindungen = []

    def fake_connect(hass, signal, target):
        verbindungen.append((hass, signal, target))
        return lambda: None

    monkeypatch.setattr(
        "custom_components.speiseplaner.entity.async_dispatcher_connect", fake_connect
    )

    class DummyEntity(StorageUpdateMixin):
        def __init__(self):
            self.hass = "fake_hass"
            self.write_calls = 0

        def async_write_ha_state(self):
            self.write_calls += 1

        def async_on_remove(self, func):
            pass

    entity = DummyEntity()
    await entity.async_added_to_hass()

    assert len(verbindungen) == 1
    hass, signal, target = verbindungen[0]
    assert hass == "fake_hass"
    assert signal == SIGNAL_UPDATE

    target()
    assert entity.write_calls == 1


def test_entities_pollen_nicht_und_nutzen_das_mixin():
    storage = SpeiseplanerStorage(hass=object())

    for cls in (SpeiseplanHeuteSensor, SpeiseplanCalendar, EinkaufslisteTodoListEntity):
        assert issubclass(cls, StorageUpdateMixin)
        entity = cls(storage, "entry1")
        assert entity.should_poll is False
