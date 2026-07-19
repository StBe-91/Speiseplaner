import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_setup_websocket_api(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, websocket_get_data)


@websocket_api.websocket_command({vol.Required("type"): "speiseplaner/data"})
@callback
def websocket_get_data(hass, connection, msg):
    entry_id = next(iter(hass.data[DOMAIN]))
    storage = hass.data[DOMAIN][entry_id]
    connection.send_result(msg["id"], storage.data)
