# settings.py
import json
from pathlib import Path
from copy import deepcopy

SETTINGS_FILE = Path(__file__).parent / "settings.json"

DEFAULTS = {
    "serial": {
        "port": "COM9",
        "baudrate": 9600,
        "auto_connect": False
    },
    "notifications": {
        "enabled": True,
        "sound": True
    },
    "ui": {
        "theme": "dark",
        "sidebar_color": "#0b1220",   # default sidebar background
        "sidebar_width": 200,         # in pixels
        "sidebar_position": "left",   # "left" or "right"
        "map_scale_percent": 70       # how much of the main area the map takes (approx)
    }
}


class Settings:
    def __init__(self):
        self._file = SETTINGS_FILE
        self._data = deepcopy(DEFAULTS)
        self.load()

    def load(self):
        if self._file.exists():
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._merge(self._data, data)
            except Exception:
                # ignore corrupt files and keep defaults
                pass

    def save(self):
        try:
            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def _merge(self, base, new):
        for k, v in new.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    def get(self, *keys, default=None):
        d = self._data
        for k in keys:
            if not isinstance(d, dict) or k not in d:
                return default
            d = d[k]
        return d

    def set(self, value, *keys):
        if len(keys) == 0:
            return
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save()

    def as_dict(self):
        return deepcopy(self._data)


# single shared instance
settings = Settings()