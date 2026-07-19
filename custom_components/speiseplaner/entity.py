from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SIGNAL_UPDATE


def build_device_info(entry_id: str) -> DeviceInfo:
    return DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="Speiseplaner")


class StorageUpdateMixin:
    """Lässt eine Entity auf das Dispatcher-Signal aus storage.async_save() reagieren,
    statt auf Polling zu warten (siehe SIGNAL_UPDATE in const.py)."""

    _attr_should_poll = False

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._handle_speiseplaner_update)
        )

    @callback
    def _handle_speiseplaner_update(self) -> None:
        self.async_write_ha_state()
