from custom_components.speiseplaner.config_flow import (
    SpeiseplanerConfigFlow,
    SpeiseplanerOptionsFlow,
)
from custom_components.speiseplaner.const import DOMAIN
from custom_components.speiseplaner.storage import SpeiseplanerStorage
from helpers import FakeHass


def make_options_flow(kategorien=None):
    hass = FakeHass()
    storage = SpeiseplanerStorage(hass=object())
    storage.data["kategorien"] = kategorien or []
    hass.data[DOMAIN] = {"entry1": storage}

    flow = SpeiseplanerOptionsFlow()
    flow.hass = hass
    flow.config_entry = type("Entry", (), {"entry_id": "entry1"})()
    return flow, storage


def test_async_get_options_flow_gibt_options_flow_zurueck():
    result = SpeiseplanerConfigFlow.async_get_options_flow(config_entry=None)

    assert isinstance(result, SpeiseplanerOptionsFlow)


async def test_init_schritt_zeigt_menue_mit_allen_aktionen():
    flow, _ = make_options_flow()

    result = await flow.async_step_init()

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert set(result["menu_options"]) == {
        "kategorie_hinzufuegen",
        "kategorie_bearbeiten",
        "kategorie_loeschen",
    }


# -- Kategorie hinzufügen -------------------------------------------------


async def test_hinzufuegen_zeigt_formular_ohne_eingabe():
    flow, _ = make_options_flow()

    result = await flow.async_step_kategorie_hinzufuegen()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorie_hinzufuegen"
    assert result["data_schema"] is not None


async def test_hinzufuegen_legt_neue_kategorie_an_und_kehrt_zum_menue_zurueck():
    flow, storage = make_options_flow(
        kategorien=[{"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True}]
    )

    result = await flow.async_step_kategorie_hinzufuegen(
        user_input={"name": "Grillzubehör", "autoeinkauf": False}
    )

    assert result["type"] == "menu"
    assert len(storage.data["kategorien"]) == 2
    neue = next(k for k in storage.data["kategorien"] if k["name"] == "Grillzubehör")
    assert neue["autoeinkauf"] is False
    assert neue["id"]


async def test_hinzufuegen_vergibt_eindeutige_ids():
    flow, storage = make_options_flow(kategorien=[])

    await flow.async_step_kategorie_hinzufuegen(user_input={"name": "Erste", "autoeinkauf": True})
    await flow.async_step_kategorie_hinzufuegen(user_input={"name": "Zweite", "autoeinkauf": True})

    ids = [k["id"] for k in storage.data["kategorien"]]
    assert len(ids) == len(set(ids)) == 2


# -- Kategorie bearbeiten (umbenennen) ------------------------------------


async def test_bearbeiten_bricht_ab_ohne_kategorien():
    flow, _ = make_options_flow(kategorien=[])

    result = await flow.async_step_kategorie_bearbeiten()

    assert result["type"] == "abort"
    assert result["reason"] == "keine_kategorien"


async def test_bearbeiten_zeigt_formular_mit_kategorie_auswahl():
    flow, _ = make_options_flow(
        kategorien=[{"id": "eigene-uuid", "name": "Selbstgemachtes", "autoeinkauf": False}]
    )

    result = await flow.async_step_kategorie_bearbeiten()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorie_bearbeiten"


async def test_bearbeiten_leitet_zum_formular_weiter_und_uebernimmt_aenderungen():
    flow, storage = make_options_flow(
        kategorien=[{"id": "eigene-uuid", "name": "Selbstgemachtes", "autoeinkauf": False}]
    )

    zwischenschritt = await flow.async_step_kategorie_bearbeiten(
        user_input={"kategorie_id": "eigene-uuid"}
    )
    assert zwischenschritt["type"] == "form"
    assert zwischenschritt["step_id"] == "kategorie_bearbeiten_formular"

    ergebnis = await flow.async_step_kategorie_bearbeiten_formular(
        user_input={"name": "Selbstgemachtes (neu)", "autoeinkauf": True}
    )

    assert ergebnis["type"] == "menu"
    kategorie = storage.find("kategorien", "eigene-uuid")
    assert kategorie["name"] == "Selbstgemachtes (neu)"
    assert kategorie["autoeinkauf"] is True


async def test_bearbeiten_funktioniert_gleich_fuer_standard_und_eigene_kategorien():
    flow, storage = make_options_flow(
        kategorien=[
            {"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True},
            {"id": "eigene-uuid", "name": "Selbstgemachtes", "autoeinkauf": False},
        ]
    )

    await flow.async_step_kategorie_bearbeiten(user_input={"kategorie_id": "getraenke"})
    await flow.async_step_kategorie_bearbeiten_formular(
        user_input={"name": "Getränke & Softdrinks", "autoeinkauf": True}
    )

    kategorie = storage.find("kategorien", "getraenke")
    assert kategorie["name"] == "Getränke & Softdrinks"


# -- Kategorie löschen -----------------------------------------------------


async def test_loeschen_bricht_ab_ohne_kategorien():
    flow, _ = make_options_flow(kategorien=[])

    result = await flow.async_step_kategorie_loeschen()

    assert result["type"] == "abort"
    assert result["reason"] == "keine_kategorien"


async def test_loeschen_zeigt_formular_ohne_eingabe():
    flow, _ = make_options_flow(
        kategorien=[{"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True}]
    )

    result = await flow.async_step_kategorie_loeschen()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorie_loeschen"


async def test_loeschen_entfernt_ausgewaehlte_kategorien_egal_welcher_herkunft():
    flow, storage = make_options_flow(
        kategorien=[
            {"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True},
            {"id": "eigene-uuid", "name": "Selbstgemachtes", "autoeinkauf": False},
            {"id": "obst_gemuese", "name": "🥦 Obst & Gemüse", "autoeinkauf": True},
        ]
    )

    result = await flow.async_step_kategorie_loeschen(
        user_input={"kategorien": ["getraenke", "eigene-uuid"]}
    )

    assert result["type"] == "menu"
    ids = {k["id"] for k in storage.data["kategorien"]}
    assert ids == {"obst_gemuese"}


async def test_loeschen_ohne_auswahl_laesst_alles_unangetastet():
    flow, storage = make_options_flow(
        kategorien=[{"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True}]
    )

    await flow.async_step_kategorie_loeschen(user_input={"kategorien": []})

    assert len(storage.data["kategorien"]) == 1
