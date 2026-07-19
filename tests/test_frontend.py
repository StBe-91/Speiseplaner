from custom_components.speiseplaner.frontend import CARD_PATH, CARD_URL, async_register_static_paths
from helpers import FakeHass


async def test_async_register_static_paths_registriert_karte():
    hass = FakeHass()

    await async_register_static_paths(hass)

    assert len(hass.http.registered_static_paths) == 1
    config = hass.http.registered_static_paths[0]
    assert config.url_path == CARD_URL
    assert config.path == str(CARD_PATH)


def test_card_datei_existiert():
    assert CARD_PATH.exists()
