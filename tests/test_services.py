import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.speiseplaner.services import async_setup_services
from custom_components.speiseplaner.storage import SpeiseplanerStorage
from helpers import FakeHass, FakeServiceCall


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


async def setup_services(storage):
    hass = FakeHass()
    await async_setup_services(hass, storage)
    return hass.services.registered


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


# -- update_rezept / delete_rezept ---------------------------------------


async def test_update_rezept_aktualisiert_felder():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["update_rezept"](
        FakeServiceCall(
            {
                "rezept_id": "r1",
                "name": "Lasagne (vegetarisch)",
                "portionen": 6,
                "zutaten": [
                    {"name": "Linsen", "anzahl": 400, "einheit": "g", "kategorie": "Fleisch"}
                ],
            }
        )
    )

    rezept = storage.data["rezepte"][0]
    assert rezept["name"] == "Lasagne (vegetarisch)"
    assert rezept["portionen"] == 6
    assert rezept["zutaten"][0]["name"] == "Linsen"


async def test_update_rezept_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["update_rezept"](
            FakeServiceCall(
                {"rezept_id": "unbekannt", "name": "X", "portionen": 1, "zutaten": []}
            )
        )


async def test_delete_rezept_entfernt_rezept():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["delete_rezept"](FakeServiceCall({"rezept_id": "r1"}))

    assert storage.data["rezepte"] == []


async def test_delete_rezept_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["delete_rezept"](FakeServiceCall({"rezept_id": "unbekannt"}))


async def test_delete_rezept_blockiert_wenn_im_speiseplan_eingeplant():
    storage = make_storage_mit_rezept()
    storage.data["speiseplan"] = [
        {"id": "s1", "datum": "2026-07-20", "rezept_id": "r1", "portionen": 4}
    ]
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["delete_rezept"](FakeServiceCall({"rezept_id": "r1"}))

    assert len(storage.data["rezepte"]) == 1


# -- update_speiseplaneintrag / delete_speiseplaneintrag -----------------


async def test_update_speiseplaneintrag_aktualisiert_felder():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)
    await services["add_speiseplaneintrag"](
        FakeServiceCall({"datum": "2026-07-20", "rezept_id": "r1", "portionen": 4})
    )
    speiseplaneintrag_id = storage.data["speiseplan"][0]["id"]

    await services["update_speiseplaneintrag"](
        FakeServiceCall(
            {
                "speiseplaneintrag_id": speiseplaneintrag_id,
                "datum": "2026-07-21",
                "rezept_id": "r1",
                "portionen": 2,
            }
        )
    )

    eintrag = storage.data["speiseplan"][0]
    assert eintrag["datum"] == "2026-07-21"
    assert eintrag["portionen"] == 2
    # Die ursprünglich für 4 Portionen hinzugefügte Menge bleibt unverändert,
    # da update_speiseplaneintrag die Einkaufsliste bewusst nicht nachzieht.
    assert storage.data["einkaufsliste"][0]["anzahl"] == 500


async def test_update_speiseplaneintrag_mit_unbekanntem_rezept_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)
    await services["add_speiseplaneintrag"](
        FakeServiceCall({"datum": "2026-07-20", "rezept_id": "r1", "portionen": 4})
    )
    speiseplaneintrag_id = storage.data["speiseplan"][0]["id"]

    with pytest.raises(ServiceValidationError):
        await services["update_speiseplaneintrag"](
            FakeServiceCall(
                {
                    "speiseplaneintrag_id": speiseplaneintrag_id,
                    "datum": "2026-07-21",
                    "rezept_id": "unbekannt",
                    "portionen": 2,
                }
            )
        )


async def test_delete_speiseplaneintrag_entfernt_eintrag():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)
    await services["add_speiseplaneintrag"](
        FakeServiceCall({"datum": "2026-07-20", "rezept_id": "r1", "portionen": 4})
    )
    speiseplaneintrag_id = storage.data["speiseplan"][0]["id"]

    await services["delete_speiseplaneintrag"](
        FakeServiceCall({"speiseplaneintrag_id": speiseplaneintrag_id})
    )

    assert storage.data["speiseplan"] == []
    # Die Einkaufsliste wird bewusst nicht zurückgerollt.
    assert len(storage.data["einkaufsliste"]) == 1


async def test_delete_speiseplaneintrag_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["delete_speiseplaneintrag"](
            FakeServiceCall({"speiseplaneintrag_id": "unbekannt"})
        )


# -- update_kategorie / delete_kategorie ----------------------------------


async def test_update_kategorie_aktualisiert_felder():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["update_kategorie"](
        FakeServiceCall({"kategorie_id": "k1", "name": "Fleisch & Fisch", "autoeinkauf": False})
    )

    kategorie = storage.data["kategorien"][0]
    assert kategorie["name"] == "Fleisch & Fisch"
    assert kategorie["autoeinkauf"] is False


async def test_update_kategorie_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["update_kategorie"](
            FakeServiceCall({"kategorie_id": "unbekannt", "name": "X", "autoeinkauf": True})
        )


async def test_delete_kategorie_entfernt_kategorie():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["delete_kategorie"](FakeServiceCall({"kategorie_id": "k1"}))

    assert storage.data["kategorien"] == []


async def test_delete_kategorie_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["delete_kategorie"](FakeServiceCall({"kategorie_id": "unbekannt"}))


# -- Einkaufsliste (manuell) ----------------------------------------------


async def test_add_einkaufsliste_eintrag_manuell():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["add_einkaufsliste_eintrag"](
        FakeServiceCall(
            {"name": "Toilettenpapier", "anzahl": 1, "einheit": "Packung", "kategorie": "Drogerie"}
        )
    )

    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["name"] == "Toilettenpapier"


async def test_add_einkaufsliste_eintrag_mergt_mit_bestehendem():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    await services["add_einkaufsliste_eintrag"](
        FakeServiceCall({"name": "Milch", "anzahl": 1, "einheit": "l"})
    )
    await services["add_einkaufsliste_eintrag"](
        FakeServiceCall({"name": "Milch", "anzahl": 2, "einheit": "l"})
    )

    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["anzahl"] == 3


async def test_delete_einkaufsliste_eintrag():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)
    await services["add_einkaufsliste_eintrag"](
        FakeServiceCall({"name": "Milch", "anzahl": 1, "einheit": "l"})
    )
    einkaufslisteneintrag_id = storage.data["einkaufsliste"][0]["id"]

    await services["delete_einkaufsliste_eintrag"](
        FakeServiceCall({"einkaufslisteneintrag_id": einkaufslisteneintrag_id})
    )

    assert storage.data["einkaufsliste"] == []


async def test_delete_einkaufsliste_eintrag_mit_unbekannter_id_wirft_fehler():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)

    with pytest.raises(ServiceValidationError):
        await services["delete_einkaufsliste_eintrag"](
            FakeServiceCall({"einkaufslisteneintrag_id": "unbekannt"})
        )


async def test_set_einkaufsliste_erledigt():
    storage = make_storage_mit_rezept()
    services = await setup_services(storage)
    await services["add_einkaufsliste_eintrag"](
        FakeServiceCall({"name": "Milch", "anzahl": 1, "einheit": "l"})
    )
    einkaufslisteneintrag_id = storage.data["einkaufsliste"][0]["id"]

    await services["set_einkaufsliste_erledigt"](
        FakeServiceCall({"einkaufslisteneintrag_id": einkaufslisteneintrag_id, "erledigt": True})
    )

    assert storage.data["einkaufsliste"][0]["erledigt"] is True
