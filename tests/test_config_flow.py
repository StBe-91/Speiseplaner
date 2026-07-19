from custom_components.speiseplaner.config_flow import SpeiseplanerConfigFlow


async def test_user_step_zeigt_formular_ohne_eingabe():
    flow = SpeiseplanerConfigFlow()

    result = await flow.async_step_user()

    assert result["type"] == "form"
    assert result["step_id"] == "user"


async def test_user_step_erstellt_eintrag_bei_bestaetigung():
    flow = SpeiseplanerConfigFlow()

    result = await flow.async_step_user(user_input={})

    assert result["type"] == "create_entry"
    assert result["title"] == "Speiseplaner"


async def test_user_step_bricht_ab_wenn_bereits_konfiguriert(monkeypatch):
    flow = SpeiseplanerConfigFlow()
    monkeypatch.setattr(flow, "_async_current_entries", lambda: [object()])

    result = await flow.async_step_user(user_input={})

    assert result["type"] == "abort"
    assert result["reason"] == "single_instance_allowed"
