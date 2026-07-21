from custom_components.speiseplaner.config_flow import SpeiseplanerConfigFlow
from custom_components.speiseplaner.kategorien_defaults import DEFAULT_KATEGORIEN


def make_flow():
    flow = SpeiseplanerConfigFlow()
    flow.hass = object()
    return flow


async def test_user_step_delegiert_an_kategorien_schritt():
    flow = make_flow()

    result = await flow.async_step_user()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorien"


async def test_user_step_bricht_ab_wenn_bereits_konfiguriert(monkeypatch):
    flow = make_flow()
    monkeypatch.setattr(flow, "_async_current_entries", lambda: [object()])

    result = await flow.async_step_user()

    assert result["type"] == "abort"
    assert result["reason"] == "single_instance_allowed"


async def test_kategorien_schritt_zeigt_formular_ohne_eingabe():
    flow = make_flow()

    result = await flow.async_step_kategorien()

    assert result["type"] == "form"
    assert result["step_id"] == "kategorien"
    assert result["data_schema"] is not None


async def test_kategorien_schritt_saet_ausgewaehlte_kategorien():
    flow = make_flow()
    ausgewaehlt = ["obst_gemuese", "getraenke"]

    result = await flow.async_step_kategorien(user_input={"kategorien": ausgewaehlt})

    assert result["type"] == "create_entry"
    gespeichert = {k["id"]: k for k in flow._storage.data["kategorien"]}
    assert set(gespeichert) == set(ausgewaehlt)
    assert gespeichert["obst_gemuese"]["name"] == "🥦 Obst & Gemüse"
    assert gespeichert["obst_gemuese"]["autoeinkauf"] is True


async def test_kategorien_schritt_ohne_auswahl_legt_keine_kategorien_an():
    flow = make_flow()

    result = await flow.async_step_kategorien(user_input={"kategorien": []})

    assert result["type"] == "create_entry"
    assert flow._storage.data["kategorien"] == []


async def test_alle_standardkategorien_sind_ueber_die_auswahl_erreichbar():
    flow = make_flow()
    alle_ids = [k["id"] for k in DEFAULT_KATEGORIEN]

    await flow.async_step_kategorien(user_input={"kategorien": alle_ids})

    assert len(flow._storage.data["kategorien"]) == len(DEFAULT_KATEGORIEN)
