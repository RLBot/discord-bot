import json

from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / 'settings.json'


def load_settings():
    if not SETTINGS_PATH.exists():
        save_settings({})
        return load_settings()
    else:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)


def save_settings(settings):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
