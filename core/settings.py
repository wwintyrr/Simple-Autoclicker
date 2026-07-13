import configparser
from pathlib import Path
from PySide6.QtCore import QObject, Signal

# settings singleton
class Settings(QObject):
    changed = Signal(str, str, object)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # ctor
    def __init__(self):
        super().__init__()

        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self.path = Path(__file__).resolve().parent.parent / "settings.ini"
        self.conf = configparser.ConfigParser()

        self.load()
    
    def load(self):
        if self.path.exists():
            self.conf.read(self.path)
        
        self._create_defaults()
        self.save()
    
    def save(self):
        with open(self.path, "w") as file:
            self.conf.write(file)
    
    # setters n getters
    def get(self, section, key):
        return self.conf[section][key]
    
    def get_int(self, section, key):
        return self.conf.getint(section, key)
    
    def get_float(self, section, key):
        return self.conf.getfloat(section, key)
    
    def get_bool(self, section, key):
        return self.conf.getboolean(section, key)
    
    def set(self, section, key, value):
        self.conf[section][key] = str(value)
        self.save()

        self.changed.emit(section, key, value)
    
    def set_int(self, section, key, value):
        self.set(section, key, int(value))
    
    def set_bool(self, section, key, value):
        self.set(section, key, "true" if value else "false")

    # internals
    def _create_defaults(self):
        defaults = {
            "Click": {
                "button": "left",
                "repeat": "true",
                "amount": "20",
                "at_mouse": "true",
                "at_pos_x": "0",
                "at_pos_y": "0"
            },

            "Overlay": {
                "enabled": "false",
                "opacity": "100"
            },

            "Speed": {
                "minutes": 0,
                "seconds": 1,
                "milliseconds": 0
            },

            "Keybinds": {
                "toggle": "f6",
                "kill": "esc",
                "overlay": "f5"
            }
        }

        for section, values in defaults.items():
            if section not in self.conf:
                self.conf[section] = values