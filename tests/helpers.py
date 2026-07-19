class FakeServiceCall:
    def __init__(self, data):
        self.data = data


class FakeServices:
    def __init__(self):
        self.registered = {}

    def async_register(self, domain, service, handler, schema=None):
        self.registered[service] = handler


class FakeConfigEntries:
    def __init__(self):
        self.forwarded = []
        self.unloaded = []
        self.unload_result = True

    async def async_forward_entry_setups(self, entry, platforms):
        self.forwarded.append((entry, platforms))

    async def async_unload_platforms(self, entry, platforms):
        self.unloaded.append((entry, platforms))
        return self.unload_result


class FakeHass:
    def __init__(self):
        self.services = FakeServices()
        self.config_entries = FakeConfigEntries()
        self.data = {}
