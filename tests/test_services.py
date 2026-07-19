import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.speiseplaner.services import async_setup_services
from custom_components.speiseplaner.storage import SpeiseplanerStorage


class FakeServiceCall:
    def __init__(self, data):
        self.data = data


class FakeServices:
    def __init__(self):
        self.registered = {}

    def async_register(self, domain, service, handler, schema=None):
        self.registered[service] = handler


class FakeHass:
    def __init__(self):
        self.services = FakeServices()


def make_storage_mit_rezept():
    storage = SpeiseplanerStorage(hass=object())
    storage.data["kategorien"] = [{"id": "k1", "name": "Fleisch", "autoeinkauf": True}]
    storage.data["rezepte"] = [
        {
            "id": "r1",
            "name": "Lasagne",
            "portionen": 4,
            "zutaten": [
                {"name": "Hackfleisch", "anzahl": 500, "einheit": "g", "kategorie": "Fleisch"}
            ],
            "rezeptanleitung": "",
        }
    ]
    return storage


async def test_add_speiseplaneintrag_befuellt_einkaufsliste_skaliert():
    storage = make_storage_mit_rezept()
    hass = FakeHass()
    await async_setup_services(hass, storage)

    await hass.services.registered["add_speiseplaneintrag"](
        FakeServiceCall({"datum": "2026-07-20", "rezept_id": "r1", "portionen": 8})
    )

    assert len(storage.data["speiseplan"]) == 1
    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["anzahl"] == 1000  # 500g bei 4 Portionen -> 8 Portionen


async def test_add_speiseplaneintrag_mit_unbekanntem_rezept_wirft_fehler():
    storage = make_storage_mit_rezept()
    hass = FakeHass()
    await async_setup_services(hass, storage)

    with pytest.raises(ServiceValidationError):
        await hass.services.registered["add_speiseplaneintrag"](
            FakeServiceCall({"datum": "2026-07-20", "rezept_id": "unbekannt", "portionen": 4})
        )

    assert storage.data["speiseplan"] == []
    assert storage.data["einkaufsliste"] == []


async def test_add_rezept_speichert_zutaten_als_dicts():
    storage = SpeiseplanerStorage(hass=object())
    hass = FakeHass()
    await async_setup_services(hass, storage)

    await hass.services.registered["add_rezept"](
        FakeServiceCall(
            {
                "name": "Lasagne",
                "portionen": 4,
                "zutaten": [
                    {"name": "Hackfleisch", "anzahl": 500, "einheit": "g", "kategorie": "Fleisch"}
                ],
            }
        )
    )

    gespeicherte_zutaten = storage.data["rezepte"][0]["zutaten"]
    assert isinstance(gespeicherte_zutaten[0], dict)
    assert gespeicherte_zutaten[0]["name"] == "Hackfleisch"
