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

import enum
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


def callback(func):
    return func


core.HomeAssistant = HomeAssistant
core.ServiceCall = ServiceCall
core.callback = callback

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
    _attr_should_poll = True

    @property
    def should_poll(self):
        return self._attr_should_poll

    def async_write_ha_state(self):
        pass

    def async_on_remove(self, func):
        pass


def DeviceInfo(**kwargs):
    return dict(kwargs)


helpers_storage.Store = Store
helpers_entity.Entity = Entity
helpers_entity.DeviceInfo = DeviceInfo
helpers.storage = helpers_storage
helpers.entity = helpers_entity
homeassistant.core = core
homeassistant.exceptions = exceptions
homeassistant.helpers = helpers

helpers_dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")


def async_dispatcher_connect(hass, signal, target):
    return lambda: None


def async_dispatcher_send(hass, signal, *args):
    pass


helpers_dispatcher.async_dispatcher_connect = async_dispatcher_connect
helpers_dispatcher.async_dispatcher_send = async_dispatcher_send
helpers.dispatcher = helpers_dispatcher

components = types.ModuleType("homeassistant.components")

sensor_module = types.ModuleType("homeassistant.components.sensor")


class SensorEntity(Entity):
    pass


sensor_module.SensorEntity = SensorEntity

calendar_module = types.ModuleType("homeassistant.components.calendar")


class CalendarEvent:
    def __init__(self, start, end, summary, description=None, uid=None, location=None):
        self.start = start
        self.end = end
        self.summary = summary
        self.description = description
        self.uid = uid
        self.location = location


class CalendarEntity(Entity):
    pass


calendar_module.CalendarEvent = CalendarEvent
calendar_module.CalendarEntity = CalendarEntity

todo_module = types.ModuleType("homeassistant.components.todo")


class TodoItemStatus(str, enum.Enum):
    NEEDS_ACTION = "needs_action"
    COMPLETED = "completed"


class TodoItem:
    def __init__(self, summary=None, uid=None, status=None, description=None, due=None):
        self.summary = summary
        self.uid = uid
        self.status = status
        self.description = description
        self.due = due


class TodoListEntityFeature(enum.IntFlag):
    CREATE_TODO_ITEM = 1
    DELETE_TODO_ITEM = 2
    UPDATE_TODO_ITEM = 4


class TodoListEntity(Entity):
    pass


todo_module.TodoItem = TodoItem
todo_module.TodoItemStatus = TodoItemStatus
todo_module.TodoListEntityFeature = TodoListEntityFeature
todo_module.TodoListEntity = TodoListEntity

websocket_api_module = types.ModuleType("homeassistant.components.websocket_api")


def websocket_command(schema):
    def decorator(func):
        func._ws_schema = schema
        return func

    return decorator


_registered_ws_commands = []


def async_register_command(hass, handler):
    _registered_ws_commands.append(handler)


class WebSocketConnection:
    def __init__(self):
        self.sent = []

    def send_result(self, msg_id, result=None):
        self.sent.append((msg_id, result))


websocket_api_module.websocket_command = websocket_command
websocket_api_module.async_register_command = async_register_command
websocket_api_module.ActiveConnection = WebSocketConnection

http_module = types.ModuleType("homeassistant.components.http")


class StaticPathConfig:
    def __init__(self, url_path, path, cache_headers=True):
        self.url_path = url_path
        self.path = path
        self.cache_headers = cache_headers


http_module.StaticPathConfig = StaticPathConfig

components.sensor = sensor_module
components.calendar = calendar_module
components.todo = todo_module
components.websocket_api = websocket_api_module
components.http = http_module
homeassistant.components = components

voluptuous = types.ModuleType("voluptuous")


def Required(key, **kwargs):
    return key


def Optional(key, **kwargs):
    return key


class Schema:
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema


def In(container):
    def validator(value):
        if value not in container:
            raise ValueError(f"{value} ist keine gültige Option")
        return value

    return validator


voluptuous.Required = Required
voluptuous.Optional = Optional
voluptuous.Schema = Schema
voluptuous.In = In

helpers_config_validation = types.ModuleType("homeassistant.helpers.config_validation")


def multi_select(options):
    def validator(selected):
        if not isinstance(selected, list):
            raise ValueError("multi_select erwartet eine Liste")
        for item in selected:
            if item not in options:
                raise ValueError(f"{item} ist keine gültige Option")
        return selected

    return validator


helpers_config_validation.multi_select = multi_select
helpers.config_validation = helpers_config_validation

config_entries = types.ModuleType("homeassistant.config_entries")


class ConfigEntry:
    def __init__(self, entry_id="entry_id"):
        self.entry_id = entry_id


class _FlowHandlerBase:
    def async_show_form(self, step_id, data_schema=None):
        return {"type": "form", "step_id": step_id, "data_schema": data_schema}

    def async_show_menu(self, step_id, menu_options):
        return {"type": "menu", "step_id": step_id, "menu_options": menu_options}

    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data}

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}


class ConfigFlow(_FlowHandlerBase):
    VERSION = 1

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.domain = domain

    def __init__(self):
        self.hass = None

    def _async_current_entries(self):
        return []


class OptionsFlow(_FlowHandlerBase):
    def __init__(self):
        self.hass = None
        self.config_entry = None


config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigFlow = ConfigFlow
config_entries.OptionsFlow = OptionsFlow
homeassistant.config_entries = config_entries

sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.exceptions", exceptions)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.storage", helpers_storage)
sys.modules.setdefault("homeassistant.helpers.entity", helpers_entity)
sys.modules.setdefault("homeassistant.helpers.dispatcher", helpers_dispatcher)
sys.modules.setdefault("homeassistant.helpers.config_validation", helpers_config_validation)
sys.modules.setdefault("homeassistant.config_entries", config_entries)
sys.modules.setdefault("homeassistant.components", components)
sys.modules.setdefault("homeassistant.components.sensor", sensor_module)
sys.modules.setdefault("homeassistant.components.calendar", calendar_module)
sys.modules.setdefault("homeassistant.components.todo", todo_module)
sys.modules.setdefault("homeassistant.components.websocket_api", websocket_api_module)
sys.modules.setdefault("homeassistant.components.http", http_module)
sys.modules.setdefault("voluptuous", voluptuous)
