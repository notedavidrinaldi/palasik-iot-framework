# palasik/core/context.py

class PalasikContext:
    """
    Shared runtime context untuk seluruh komponen PALASIK.
    Digunakan untuk menyimpan konfigurasi, state, dan resource runtime.
    """

    def __init__(self):
        self.config = {}
        self.state = {}
        self.resources = {}

    def set_config(self, key, value):
        self.config[key] = value

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def register_resource(self, name, resource):
        self.resources[name] = resource

    def get_resource(self, name):
        return self.resources.get(name)
