import tkinter as tk
from tkinter import messagebox
import requests
import threading
from datetime import datetime



# API config
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 10


# Open-Meteo weather_code values
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Severe thunderstorm with hail", "⛈️"),
}


# API functions
def get_coordinates(city_name):
    """
    Converts a city name into latitude and longitude using Open-Meteo Geocoding API.
    """

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
        "longitude": result["longitude"],
        "timezone": result.get("timezone", "auto")
    }


def get_weather(latitude, longitude):
    """
    Retrieves current weather and 5-day forecast from Open-Meteo.
    """

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


# GUI
class WeatherDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather Dashboard")
        self.geometry("760x620")
        self.minsize(720, 580)
        self.configure(bg="#101827")

        self.create_widgets()

    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self, bg="#101827")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        # Header
        header = tk.Frame(self.main_frame, bg="#101827")
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Weather Dashboard",
            font=("Segoe UI", 26, "bold"),
            fg="#F8FAFC",
            bg="#101827"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Search any city for current conditions and a 5-day forecast",
            font=("Segoe UI", 11),
            fg="#94A3B8",
            bg="#101827"
        )
        subtitle.pack(anchor="w", pady=(4, 18))

        # Search area
        search_frame = tk.Frame(self.main_frame, bg="#101827")
        search_frame.pack(fill="x", pady=(0, 20))

        self.city_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 14),
            bg="#1E293B",
            fg="#F8FAFC",
            insertbackground="#F8FAFC",
            relief="flat"
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 12))
        self.city_entry.insert(0, "Madrid")

        search_button = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 12, "bold"),
            bg="#38BDF8",
            fg="#0F172A",
            activebackground="#0EA5E9",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=24,
            pady=10,
            command=self.search_weather
        )
        search_button.pack(side="right")

        self.city_entry.bind("<Return>", lambda event: self.search_weather())

        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg="#101827"
        )
        self.status_label.pack(anchor="w", pady=(0, 12))

        # Current weather card
        self.current_card = tk.Frame(
            self.main_frame,
            bg="#1E293B",
            highlightbackground="#334155",
            highlightthickness=1
        )
        self.current_card.pack(fill="x", pady=(0, 20))

        self.location_label = tk.Label(
            self.current_card,
            text="Madrid, Spain",
            font=("Segoe UI", 18, "bold"),
            fg="#F8FAFC",
            bg="#1E293B"
        )
        self.location_label.pack(anchor="w", padx=22, pady=(20, 4))

        self.updated_label = tk.Label(
            self.current_card,
            text="Last updated: --",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#1E293B"
        )
        self.updated_label.pack(anchor="w", padx=22)

        current_content = tk.Frame(self.current_card, bg="#1E293B")
        current_content.pack(fill="x", padx=22, pady=20)

        self.icon_label = tk.Label(
            current_content,
            text="☀️",
            font=("Segoe UI Emoji", 52),
            fg="#F8FAFC",
            bg="#1E293B"
        )
        self.icon_label.pack(side="left", padx=(0, 20))

        temp_frame = tk.Frame(current_content, bg="#1E293B")
        temp_frame.pack(side="left", fill="both", expand=True)

        self.temperature_label = tk.Label(
            temp_frame,
            text="--°C",
            font=("Segoe UI", 44, "bold"),
            fg="#F8FAFC",
            bg="#1E293B"
        )
        self.temperature_label.pack(anchor="w")

        self.condition_label = tk.Label(
            temp_frame,
            text="Search for a location",
            font=("Segoe UI", 15),
            fg="#CBD5E1",
            bg="#1E293B"
        )
        self.condition_label.pack(anchor="w")

        # Details grid
        self.details_frame = tk.Frame(self.current_card, bg="#1E293B")
        self.details_frame.pack(fill="x", padx=22, pady=(0, 22))

        self.feels_like_value = self.create_detail_card("Feels like", "--")
        self.humidity_value = self.create_detail_card("Humidity", "--")
        self.wind_value = self.create_detail_card("Wind", "--")
        self.cloud_value = self.create_detail_card("Cloud cover", "--")

        # Forecast section
        forecast_title = tk.Label(
            self.main_frame,
            text="5-Day Forecast",
            font=("Segoe UI", 17, "bold"),
            fg="#F8FAFC",
            bg="#101827"
        )
        forecast_title.pack(anchor="w", pady=(0, 10))

        self.forecast_frame = tk.Frame(self.main_frame, bg="#101827")
        self.forecast_frame.pack(fill="both", expand=True)

        self.forecast_cards = []

        for _ in range(5):
            card = tk.Frame(
                self.forecast_frame,
                bg="#1E293B",
                highlightbackground="#334155",
                highlightthickness=1
            )
            card.pack(side="left", fill="both", expand=True, padx=5)

            day_label = tk.Label(
                card,
                text="--",
                font=("Segoe UI", 11, "bold"),
                fg="#F8FAFC",
                bg="#1E293B"
            )
            day_label.pack(pady=(16, 6))

            icon_label = tk.Label(
                card,
                text="☁️",
                font=("Segoe UI Emoji", 28),
                fg="#F8FAFC",
                bg="#1E293B"
            )
            icon_label.pack()

            temp_label = tk.Label(
                card,
                text="-- / --",
                font=("Segoe UI", 11),
                fg="#CBD5E1",
                bg="#1E293B"
            )
            temp_label.pack(pady=(8, 4))

            rain_label = tk.Label(
                card,
                text="Rain: --",
                font=("Segoe UI", 9),
                fg="#94A3B8",
                bg="#1E293B"
            )
            rain_label.pack(pady=(0, 14))

            self.forecast_cards.append({
                "day": day_label,
                "icon": icon_label,
                "temp": temp_label,
                "rain": rain_label
            })

    def create_detail_card(self, label_text, value_text):
        card = tk.Frame(self.details_frame, bg="#0F172A")
        card.pack(side="left", fill="x", expand=True, padx=5)

        label = tk.Label(
            card,
            text=label_text,
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#0F172A"
        )
        label.pack(anchor="w", padx=12, pady=(10, 2))

        value = tk.Label(
            card,
            text=value_text,
            font=("Segoe UI", 13, "bold"),
            fg="#F8FAFC",
            bg="#0F172A"
        )
        value.pack(anchor="w", padx=12, pady=(0, 10))

        return value

    def search_weather(self):
        city = self.city_entry.get().strip()

        if not city:
            messagebox.showwarning("Missing location", "Please enter a city name.")
            return

        self.status_label.config(text="Loading weather data...")

        thread = threading.Thread(
            target=self.load_weather_data,
            args=(city,),
            daemon=True
        )
        thread.start()

    def load_weather_data(self, city):
        try:
            location = get_coordinates(city)
            weather_data = get_weather(
                location["latitude"],
                location["longitude"]
            )

            self.after(0, self.update_dashboard, location, weather_data)

        except requests.exceptions.Timeout:
            self.after(
                0,
                self.show_error,
                "The weather service took too long to respond. Please try again."
            )

        except requests.exceptions.ConnectionError:
            self.after(
                0,
                self.show_error,
                "Could not connect to the weather service. Check your internet connection."
            )

        except requests.exceptions.HTTPError:
            self.after(
                0,
                self.show_error,
                "The weather service returned an error. Please try again later."
            )

        except ValueError as error:
            self.after(0, self.show_error, str(error))

        except Exception as error:
            self.after(
                0,
                self.show_error,
                f"Unexpected error: {error}"
            )

    def update_dashboard(self, location, weather_data):
        current = weather_data["current"]
        daily = weather_data["daily"]

        weather_code = current.get("weather_code", 0)
        condition, icon = WEATHER_CODES.get(weather_code, ("Unknown", "❔"))

        city = location["name"]
        country = location["country"]

        temperature = current.get("temperature_2m", "--")
        feels_like = current.get("apparent_temperature", "--")
        humidity = current.get("relative_humidity_2m", "--")
        wind_speed = current.get("wind_speed_10m", "--")
        cloud_cover = current.get("cloud_cover", "--")

        update_time = current.get("time", "")

        self.location_label.config(text=f"{city}, {country}")
        self.updated_label.config(text=f"Last updated: {update_time}")
        self.icon_label.config(text=icon)
        self.temperature_label.config(text=f"{temperature}°C")
        self.condition_label.config(text=condition)

        self.feels_like_value.config(text=f"{feels_like}°C")
        self.humidity_value.config(text=f"{humidity}%")
        self.wind_value.config(text=f"{wind_speed} km/h")
        self.cloud_value.config(text=f"{cloud_cover}%")

        for index, card in enumerate(self.forecast_cards):
            date_text = daily["time"][index]
            date_object = datetime.strptime(date_text, "%Y-%m-%d")
            day_name = date_object.strftime("%a")

            forecast_code = daily["weather_code"][index]
            forecast_condition, forecast_icon = WEATHER_CODES.get(
                forecast_code,
                ("Unknown", "❔")
            )

            max_temp = daily["temperature_2m_max"][index]
            min_temp = daily["temperature_2m_min"][index]
            rain_probability = daily["precipitation_probability_max"][index]

            card["day"].config(text=day_name)
            card["icon"].config(text=forecast_icon)
            card["temp"].config(text=f"{max_temp}° / {min_temp}°")
            card["rain"].config(text=f"Rain: {rain_probability}%")

        self.status_label.config(text="Weather data loaded successfully.")

    def show_error(self, message):
        self.status_label.config(text="Error loading weather data.")
        messagebox.showerror("Weather Dashboard Error", message)


if __name__ == "__main__":
    app = WeatherDashboard()
    app.mainloop()