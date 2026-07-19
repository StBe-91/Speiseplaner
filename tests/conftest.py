"""
Leichte Fake-Module für 'homeassistant'.

Auf diesem Rechner ist nur Python 3.14 verfügbar, das echte homeassistant-Paket
unterstützt aktuell offiziell nur bis Python 3.13. Diese Stubs bilden nur die
paar Symbole nach, die custom_components/speiseplaner tatsächlich importiert
(HomeAssistant, ServiceCall, ServiceValidationError, Store), damit die
Business-Logik ohne den echten HA-Kern getestet werden kann. Sobald eine
unterstützte Python-Version verfügbar ist, sollte hier stattdessen
pytest-homeassistant-custom-component verwendet werden.
"""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

homeassistant = types.ModuleType("homeassistant")

core = types.ModuleType("homeassistant.core")


class HomeAssistant:
    pass


class ServiceCall:
    def __init__(self, data=None):
        self.data = data or {}


core.HomeAssistant = HomeAssistant
core.ServiceCall = ServiceCall

exceptions = types.ModuleType("homeassistant.exceptions")


class HomeAssistantError(Exception):
    pass


class ServiceValidationError(HomeAssistantError):
    pass


exceptions.HomeAssistantError = HomeAssistantError
exceptions.ServiceValidationError = ServiceValidationError

helpers = types.ModuleType("homeassistant.helpers")
helpers_storage = types.ModuleType("homeassistant.helpers.storage")
helpers_entity = types.ModuleType("homeassistant.helpers.entity")


class Store:
    def __init__(self, hass, version, key):
        self.hass = hass
        self.version = version
        self.key = key

    async def async_load(self):
        return None

    async def async_save(self, data):
        pass


class Entity:
    pass


helpers_storage.Store = Store
helpers_entity.Entity = Entity
helpers.storage = helpers_storage
helpers.entity = helpers_entity
homeassistant.core = core
homeassistant.exceptions = exceptions
homeassistant.helpers = helpers

config_entries = types.ModuleType("homeassistant.config_entries")


class ConfigEntry:
    def __init__(self, entry_id="entry_id"):
        self.entry_id = entry_id


class ConfigFlow:
    VERSION = 1

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.domain = domain

    def __init__(self):
        self.hass = None

    def _async_current_entries(self):
        return []

    def async_show_form(self, step_id, data_schema=None):
        return {"type": "form", "step_id": step_id}

    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data}

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}


config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigFlow = ConfigFlow
homeassistant.config_entries = config_entries

sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.exceptions", exceptions)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.storage", helpers_storage)
sys.modules.setdefault("homeassistant.helpers.entity", helpers_entity)
sys.modules.setdefault("homeassistant.config_entries", config_entries)
