from homeassistant.config_entries import ConfigEntry

from custom_components.speiseplaner import async_setup_entry, async_unload_entry
from custom_components.speiseplaner.const import DOMAIN, PLATFORMS
from helpers import FakeHass


async def test_async_setup_entry_initialisiert_storage_und_services():
    hass = FakeHass()
    entry = ConfigEntry(entry_id="entry1")

    result = await async_setup_entry(hass, entry)

    assert result is True
    assert "entry1" in hass.data[DOMAIN]
    assert "add_rezept" in hass.services.registered
    assert hass.config_entries.forwarded == [(entry, PLATFORMS)]
    assert len(hass.http.registered_static_paths) == 1


async def test_async_setup_entry_registriert_frontend_nur_einmal():
    hass = FakeHass()

    await async_setup_entry(hass, ConfigEntry(entry_id="entry1"))
    await async_setup_entry(hass, ConfigEntry(entry_id="entry1"))  # simuliert einen Reload

    assert len(hass.http.registered_static_paths) == 1


async def test_async_unload_entry_entfernt_storage_bei_erfolg():
    hass = FakeHass()
    entry = ConfigEntry(entry_id="entry1")
    await async_setup_entry(hass, entry)

    result = await async_unload_entry(hass, entry)

    assert result is True
    assert "entry1" not in hass.data[DOMAIN]
    assert hass.config_entries.unloaded == [(entry, PLATFORMS)]


async def test_async_unload_entry_behaelt_storage_bei_fehlschlag():
    hass = FakeHass()
    entry = ConfigEntry(entry_id="entry1")
    await async_setup_entry(hass, entry)
    hass.config_entries.unload_result = False

    result = await async_unload_entry(hass, entry)

    assert result is False
    assert "entry1" in hass.data[DOMAIN]
