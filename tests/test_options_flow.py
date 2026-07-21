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


async def test_init_schritt_zeigt_menue_mit_kategorien():
    flow, _ = make_options_flow()

    result = await flow.async_step_init()

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert "kategorien" in result["menu_options"]


async def test_kategorien_schritt_zeigt_formular_ohne_eingabe():
    flow, _ = make_options_flow()

    result = await flow.async_step_kategorien()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorien"
    assert result["data_schema"] is not None


async def test_kategorien_schritt_aktiviert_neue_standardkategorie():
    flow, storage = make_options_flow(kategorien=[])

    result = await flow.async_step_kategorien(user_input={"kategorien": ["getraenke"]})

    assert result["type"] == "create_entry"
    ids = [k["id"] for k in storage.data["kategorien"]]
    assert ids == ["getraenke"]


async def test_kategorien_schritt_deaktiviert_abgewaehlte_standardkategorie():
    flow, storage = make_options_flow(
        kategorien=[
            {"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True},
            {"id": "obst_gemuese", "name": "🥦 Obst & Gemüse", "autoeinkauf": True},
        ]
    )

    result = await flow.async_step_kategorien(user_input={"kategorien": ["obst_gemuese"]})

    assert result["type"] == "create_entry"
    ids = {k["id"] for k in storage.data["kategorien"]}
    assert ids == {"obst_gemuese"}


async def test_kategorien_schritt_laesst_eigene_kategorien_unangetastet():
    flow, storage = make_options_flow(
        kategorien=[
            {"id": "eigene-uuid", "name": "Selbstgemachtes", "autoeinkauf": False},
            {"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True},
        ]
    )

    result = await flow.async_step_kategorien(user_input={"kategorien": []})

    assert result["type"] == "create_entry"
    ids = {k["id"] for k in storage.data["kategorien"]}
    assert ids == {"eigene-uuid"}
