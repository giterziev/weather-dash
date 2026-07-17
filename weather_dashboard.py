import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import threading
from datetime import datetime
import json
import os
import locale


# API CONFIGURATION
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10


# LOCAL APP FILES
APP_DIR = os.path.dirname(os.path.abspath(__file__))
FAVORITES_FILE = os.path.join(APP_DIR, "weather_favorites.json")
ICON_FILE = os.path.join(APP_DIR, "weather.ico")


# COUNTRY / REGION DEFAULTS
# Based on OS locale
DEFAULT_CITY_BY_COUNTRY = {
    "US": "Pittsburgh",
    "ES": "Madrid",
    "GB": "London",
    "UK": "London",
    "FR": "Paris",
    "DE": "Berlin",
    "IT": "Rome",
    "PT": "Lisbon",
    "NL": "Amsterdam",
    "BE": "Brussels",
    "PL": "Warsaw",
    "SE": "Stockholm",
    "NO": "Oslo",
    "DK": "Copenhagen",
    "FI": "Helsinki",
    "IE": "Dublin",
    "CA": "Ottawa",
    "MX": "Mexico City",
    "BR": "Brasilia",
    "AR": "Buenos Aires",
    "AU": "Canberra",
    "NZ": "Wellington",
    "JP": "Tokyo",
    "CN": "Beijing",
    "IN": "New Delhi",
    "BG": "Sofia",
}


# WEATHER CODE MAPPING
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


# HELPER FUNCTIONS
def get_default_city_from_os_region():
    """
    Attempts to choose a default city based on the OS locale.
    """

    try:
        current_locale = locale.getlocale()[0]

        if not current_locale:
            current_locale = locale.getdefaultlocale()[0]

        if current_locale and "_" in current_locale:
            country_code = current_locale.split("_")[-1].upper()
            return DEFAULT_CITY_BY_COUNTRY.get(country_code, "Madrid")

    except Exception:
        pass

    return "Madrid"


def load_favorites():
    """
    Loads favorite cities from local JSON file.
    """

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
    """
    Saves favorite cities to local JSON file.
    """

    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
            json.dump(sorted(set(favorites)), file, indent=4, ensure_ascii=False)

    except Exception as error:
        messagebox.showerror(
            "Favorites Error",
            f"Could not save favorites:\n{error}"
        )


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
        self.configure(bg="#101827")
        self.minsize(720, 580)

        self.window_width = 760
        self.window_height = 620

        self.favorites = load_favorites()

        self.set_app_icon()
        self.center_window()
        self.create_scrollable_layout()
        self.create_widgets()

        self.bind_mousewheel()

        default_city = get_default_city_from_os_region()
        self.city_entry.insert(0, default_city)

        # Auto-load weather shortly after startup
        self.after(250, self.search_weather)

    # ICON
    def set_app_icon(self):
        """
        Adds an icon if weather.ico exists in the same folder as the script.
        """

        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except Exception:
                pass

    def center_window(self):
        """
        Centers the main app window on startup.
        """

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (self.window_width / 2))
        y = int((screen_height / 2) - (self.window_height / 2))

        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    # LAYOUT
    def create_scrollable_layout(self):
        """
        Creates a scrollable canvas that contains the full dashboard.
        This solves the issue where the forecast is unreachable on smaller screens.
        """

        self.canvas = tk.Canvas(
            self,
            bg="#101827",
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#101827")

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_scrollable_frame
        )

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_scrollable_frame(self, event):
        """
        Keeps the inner frame width equal to the canvas width.
        This prevents awkward horizontal shrinking.
        """

        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mousewheel(self):
        """
        Enables mousewheel scrolling.
        """

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_mousewheel(self, event):

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # WIDGETS
    def create_widgets(self):
        self.main_frame = tk.Frame(self.scrollable_frame, bg="#101827")
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
        search_frame.pack(fill="x", pady=(0, 12))

        self.city_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 14),
            bg="#1E293B",
            fg="#F8FAFC",
            insertbackground="#F8FAFC",
            relief="flat"
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 12))

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

        # Favorites area
        favorites_frame = tk.Frame(self.main_frame, bg="#101827")
        favorites_frame.pack(fill="x", pady=(0, 18))

        favorites_label = tk.Label(
            favorites_frame,
            text="Favorites:",
            font=("Segoe UI", 10, "bold"),
            fg="#CBD5E1",
            bg="#101827"
        )
        favorites_label.pack(side="left", padx=(0, 8))

        self.favorites_combo = ttk.Combobox(
            favorites_frame,
            values=self.favorites,
            state="readonly",
            width=24
        )
        self.favorites_combo.pack(side="left", padx=(0, 8))
        self.favorites_combo.bind("<<ComboboxSelected>>", self.select_favorite)

        add_favorite_button = tk.Button(
            favorites_frame,
            text="Add",
            font=("Segoe UI", 9, "bold"),
            bg="#22C55E",
            fg="#052E16",
            activebackground="#16A34A",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=6,
            command=self.add_favorite
        )
        add_favorite_button.pack(side="left", padx=(0, 8))

        remove_favorite_button = tk.Button(
            favorites_frame,
            text="Remove",
            font=("Segoe UI", 9, "bold"),
            bg="#EF4444",
            fg="#450A0A",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=6,
            command=self.remove_favorite
        )
        remove_favorite_button.pack(side="left")

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
            text="Loading location...",
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

        # Weather detail cards
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
        self.forecast_frame.pack(fill="both", expand=True, pady=(0, 24))

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

    # FAVORITES
    def refresh_favorites_combo(self):
        self.favorites = sorted(set(self.favorites))
        self.favorites_combo["values"] = self.favorites

    def add_favorite(self):
        city = self.city_entry.get().strip()

        if not city:
            messagebox.showwarning("Missing city", "Please enter a city before adding it to favorites.")
            return

        if city not in self.favorites:
            self.favorites.append(city)
            self.refresh_favorites_combo()
            save_favorites(self.favorites)
            self.status_label.config(text=f"Added {city} to favorites.")
        else:
            self.status_label.config(text=f"{city} is already in favorites.")

    def remove_favorite(self):
        selected_city = self.favorites_combo.get().strip()

        if not selected_city:
            messagebox.showwarning("No favorite selected", "Please select a favorite city to remove.")
            return

        if selected_city in self.favorites:
            self.favorites.remove(selected_city)
            self.refresh_favorites_combo()
            self.favorites_combo.set("")
            save_favorites(self.favorites)
            self.status_label.config(text=f"Removed {selected_city} from favorites.")

    def select_favorite(self, event=None):
        selected_city = self.favorites_combo.get().strip()

        if selected_city:
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, selected_city)
            self.search_weather()

    # WEATHER LOADING
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

        update_time = current.get("time", "--")

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

        # Bring scroll position back to top after loading new weather
        self.canvas.yview_moveto(0)

    def show_error(self, message):
        self.status_label.config(text="Error loading weather data.")
        messagebox.showerror("Weather Dashboard Error", message)


if __name__ == "__main__":
    app = WeatherDashboard()
    app.mainloop()
