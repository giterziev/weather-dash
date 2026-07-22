import os

# API CONFIGURATION
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10

# LOCAL APP FILES
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAVORITES_FILE = os.path.join(APP_DIR, "weather_favorites.json")
SETTINGS_FILE = os.path.join(APP_DIR, "weather_settings.json")
ICON_FILE = os.path.join(APP_DIR, "weather.ico")

# AUTO-REFRESH
REFRESH_INTERVAL_OPTIONS = [0, 5, 10, 15, 30, 60]
DEFAULT_REFRESH_INTERVAL_MINUTES = 15
