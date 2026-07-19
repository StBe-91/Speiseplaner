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


class Store:
    def __init__(self, hass, version, key):
        self.hass = hass
        self.version = version
        self.key = key

    async def async_load(self):
        return None

    async def async_save(self, data):
        pass


helpers_storage.Store = Store
helpers.storage = helpers_storage
homeassistant.core = core
homeassistant.exceptions = exceptions
homeassistant.helpers = helpers

sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.exceptions", exceptions)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.storage", helpers_storage)
