from homeassistant.components.websocket_api import ActiveConnection

from custom_components.speiseplaner.const import DOMAIN
from custom_components.speiseplaner.storage import SpeiseplanerStorage
from custom_components.speiseplaner.websocket_api import (
    async_setup_websocket_api,
    websocket_get_data,
)
from helpers import FakeHass


def test_websocket_get_data_liefert_storage_daten():
    hass = FakeHass()
    storage = SpeiseplanerStorage(hass=object())
    storage.data["rezepte"] = [{"id": "r1", "name": "Lasagne"}]
    hass.data[DOMAIN] = {"entry1": storage}
    connection = ActiveConnection()

    websocket_get_data(hass, connection, {"id": 1, "type": "speiseplaner/data"})

    assert connection.sent == [(1, storage.data)]


def test_async_setup_websocket_api_registriert_kommando():
    hass = FakeHass()

    async_setup_websocket_api(hass)

    # Reine Registrierungs-Funktion; kein Rückgabewert, darf nicht crashen.
    # Die eigentliche Registrierung läuft über das gestubte
    # homeassistant.components.websocket_api.async_register_command.
