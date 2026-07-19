import json
import os

from .config import FAVORITES_FILE, SETTINGS_FILE


def load_settings():
    default_settings = {
        "temperature_unit": "celsius",
        "light_theme": False
    }

    if not os.path.exists(SETTINGS_FILE):
        return default_settings

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)

        if isinstance(settings, dict):
            default_settings.update(settings)

        return default_settings

    except Exception:
        return default_settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []

    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return sorted(set(str(city).strip() for city in data if str(city).strip()))

    except Exception:
        pass

    return []


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
        json.dump(sorted(set(favorites)), file, indent=4, ensure_ascii=False)
