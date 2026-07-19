from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

CARD_URL = f"/{DOMAIN}_static/speiseplaner-card.js"
CARD_PATH = Path(__file__).parent / "www" / "speiseplaner-card.js"


async def async_register_static_paths(hass: HomeAssistant) -> None:
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_PATH), False)]
    )
