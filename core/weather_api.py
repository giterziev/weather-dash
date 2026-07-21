import requests

from .config import GEOCODING_URL, FORECAST_URL, REQUEST_TIMEOUT


def get_coordinates(city_name):
    """Converts a city name into latitude and longitude using Open-Meteo Geocoding API."""

    params = {
        "name": city_name.strip(),
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        raise ValueError("Location not found. Please try another city name.")

    result = data["results"][0]

    return {
        "name": result.get("name", city_name),
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"]
    }


def get_weather(latitude, longitude):
    """Retrieves current weather, hourly data, and a 5-day forecast from Open-Meteo."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "weather_code,"
            "cloud_cover,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),
        "hourly": (
            "temperature_2m,"
            "weather_code,"
            "precipitation_probability,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "timezone": "auto",
        "forecast_days": 5
    }

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    return response.json()
