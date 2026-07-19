import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

import requests

from .config import ICON_FILE
from .region import get_default_city_from_os_region
from .storage import load_settings, save_settings, load_favorites, save_favorites
from .themes import DARK_THEME, LIGHT_THEME
from .weather_api import get_coordinates, get_weather
from .weather_codes import WEATHER_CODES


class WeatherDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather Dashboard")
        self.window_width = 760
        self.window_height = 620
        self.minsize(720, 580)

        self.settings = load_settings()
        self.favorites = load_favorites()

        self.temperature_unit = tk.StringVar(value=self.settings["temperature_unit"])
        self.light_theme_enabled = tk.BooleanVar(value=self.settings["light_theme"])

        self.colors = LIGHT_THEME if self.light_theme_enabled.get() else DARK_THEME

        self.set_app_icon()
        self.center_window()
        self.create_settings_menu()
        self.create_scrollable_layout()
        self.create_widgets()
        self.bind_mousewheel()

        default_city = get_default_city_from_os_region()
        self.city_entry.insert(0, default_city)

        self.after(250, self.search_weather)

    # ICON
    def set_app_icon(self):
        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except Exception:
                pass

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (self.window_width / 2))
        y = int((screen_height / 2) - (self.window_height / 2))

        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    # SETTINGS MENU
    def create_settings_menu(self):
        menu_bar = tk.Menu(self)

        settings_menu = tk.Menu(menu_bar, tearoff=0)

        settings_menu.add_radiobutton(
            label="Celsius (°C)",
            variable=self.temperature_unit,
            value="celsius",
            command=self.change_temperature_unit
        )

        settings_menu.add_radiobutton(
            label="Fahrenheit (°F)",
            variable=self.temperature_unit,
            value="fahrenheit",
            command=self.change_temperature_unit
        )

        settings_menu.add_separator()

        settings_menu.add_checkbutton(
            label="Light theme",
            variable=self.light_theme_enabled,
            command=self.change_theme
        )

        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        self.config(menu=menu_bar)

    def change_temperature_unit(self):
        self.settings["temperature_unit"] = self.temperature_unit.get()

        try:
            save_settings(self.settings)
        except Exception as error:
            messagebox.showerror("Settings Error", f"Could not save settings:\n{error}")

        if self.city_entry.get().strip():
            self.search_weather()

    def change_theme(self):
        self.settings["light_theme"] = self.light_theme_enabled.get()

        try:
            save_settings(self.settings)
        except Exception as error:
            messagebox.showerror("Settings Error", f"Could not save settings:\n{error}")

        current_city = ""

        try:
            current_city = self.city_entry.get().strip()
        except Exception:
            pass

        self.rebuild_interface(current_city)

    def rebuild_interface(self, city):
        for widget in self.winfo_children():
            widget.destroy()

        self.colors = LIGHT_THEME if self.light_theme_enabled.get() else DARK_THEME
        self.configure(bg=self.colors["app_bg"])

        self.create_settings_menu()
        self.create_scrollable_layout()
        self.create_widgets()
        self.bind_mousewheel()

        if city:
            self.city_entry.insert(0, city)
            self.after(150, self.search_weather)

    # LAYOUT
    def create_scrollable_layout(self):
        self.canvas = tk.Canvas(
            self,
            bg=self.colors["app_bg"],
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

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["app_bg"])

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_scrollable_frame)

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_scrollable_frame(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mousewheel(self):
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

    # WIDGET
    def create_widgets(self):
        self.main_frame = tk.Frame(self.scrollable_frame, bg=self.colors["app_bg"])
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        title = tk.Label(
            self.main_frame,
            text="Weather Dashboard",
            font=("Segoe UI", 26, "bold"),
            fg=self.colors["text"],
            bg=self.colors["app_bg"]
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            self.main_frame,
            text="Search any city for current conditions and a 5-day forecast",
            font=("Segoe UI", 11),
            fg=self.colors["muted"],
            bg=self.colors["app_bg"]
        )
        subtitle.pack(anchor="w", pady=(4, 18))

        self.create_search_area()
        self.create_favorites_area()
        self.create_status_label()
        self.create_current_weather_card()
        self.create_forecast_section()

    def create_search_area(self):
        search_frame = tk.Frame(self.main_frame, bg=self.colors["app_bg"])
        search_frame.pack(fill="x", pady=(0, 12))

        self.city_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 14),
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["entry_fg"],
            relief="flat"
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 12))

        search_button = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["search_bg"],
            fg=self.colors["search_fg"],
            activebackground=self.colors["search_bg"],
            activeforeground=self.colors["search_fg"],
            relief="flat",
            padx=24,
            pady=10,
            command=self.search_weather
        )
        search_button.pack(side="right")

        self.city_entry.bind("<Return>", lambda event: self.search_weather())

    def create_favorites_area(self):
        favorites_frame = tk.Frame(self.main_frame, bg=self.colors["app_bg"])
        favorites_frame.pack(fill="x", pady=(0, 18))

        favorites_label = tk.Label(
            favorites_frame,
            text="Favorites:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["soft_text"],
            bg=self.colors["app_bg"]
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

        add_button = tk.Button(
            favorites_frame,
            text="Add",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["add_bg"],
            fg=self.colors["add_fg"],
            relief="flat",
            padx=14,
            pady=6,
            command=self.add_favorite
        )
        add_button.pack(side="left", padx=(0, 8))

        remove_button = tk.Button(
            favorites_frame,
            text="Remove",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["remove_bg"],
            fg=self.colors["remove_fg"],
            relief="flat",
            padx=14,
            pady=6,
            command=self.remove_favorite
        )
        remove_button.pack(side="left")

    def create_status_label(self):
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Segoe UI", 10),
            fg=self.colors["muted"],
            bg=self.colors["app_bg"]
        )
        self.status_label.pack(anchor="w", pady=(0, 12))

    def create_current_weather_card(self):
        self.current_card = tk.Frame(
            self.main_frame,
            bg=self.colors["card_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        self.current_card.pack(fill="x", pady=(0, 20))

        self.location_label = tk.Label(
            self.current_card,
            text="Loading location...",
            font=("Segoe UI", 18, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card_bg"]
        )
        self.location_label.pack(anchor="w", padx=22, pady=(20, 4))

        self.updated_label = tk.Label(
            self.current_card,
            text="Last updated: --",
            font=("Segoe UI", 9),
            fg=self.colors["muted"],
            bg=self.colors["card_bg"]
        )
        self.updated_label.pack(anchor="w", padx=22)

        current_content = tk.Frame(self.current_card, bg=self.colors["card_bg"])
        current_content.pack(fill="x", padx=22, pady=20)

        self.icon_label = tk.Label(
            current_content,
            text="☀️",
            font=("Segoe UI Emoji", 52),
            fg=self.colors["text"],
            bg=self.colors["card_bg"]
        )
        self.icon_label.pack(side="left", padx=(0, 20))

        temp_frame = tk.Frame(current_content, bg=self.colors["card_bg"])
        temp_frame.pack(side="left", fill="both", expand=True)

        self.temperature_label = tk.Label(
            temp_frame,
            text="--",
            font=("Segoe UI", 44, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card_bg"]
        )
        self.temperature_label.pack(anchor="w")

        self.condition_label = tk.Label(
            temp_frame,
            text="Search for a location",
            font=("Segoe UI", 15),
            fg=self.colors["soft_text"],
            bg=self.colors["card_bg"]
        )
        self.condition_label.pack(anchor="w")

        self.details_frame = tk.Frame(self.current_card, bg=self.colors["card_bg"])
        self.details_frame.pack(fill="x", padx=22, pady=(0, 22))

        self.feels_like_value = self.create_detail_card("Feels like", "--")
        self.humidity_value = self.create_detail_card("Humidity", "--")
        self.wind_value = self.create_detail_card("Wind", "--")
        self.cloud_value = self.create_detail_card("Cloud cover", "--")

    def create_detail_card(self, label_text, value_text):
        card = tk.Frame(self.details_frame, bg=self.colors["detail_bg"])
        card.pack(side="left", fill="x", expand=True, padx=5)

        label = tk.Label(
            card,
            text=label_text,
            font=("Segoe UI", 9),
            fg=self.colors["muted"],
            bg=self.colors["detail_bg"]
        )
        label.pack(anchor="w", padx=12, pady=(10, 2))

        value = tk.Label(
            card,
            text=value_text,
            font=("Segoe UI", 13, "bold"),
            fg=self.colors["text"],
            bg=self.colors["detail_bg"]
        )
        value.pack(anchor="w", padx=12, pady=(0, 10))

        return value

    def create_forecast_section(self):
        forecast_title = tk.Label(
            self.main_frame,
            text="5-Day Forecast",
            font=("Segoe UI", 17, "bold"),
            fg=self.colors["text"],
            bg=self.colors["app_bg"]
        )
        forecast_title.pack(anchor="w", pady=(0, 10))

        self.forecast_frame = tk.Frame(self.main_frame, bg=self.colors["app_bg"])
        self.forecast_frame.pack(fill="both", expand=True, pady=(0, 24))

        self.forecast_cards = []

        for _ in range(5):
            card = tk.Frame(
                self.forecast_frame,
                bg=self.colors["card_bg"],
                highlightbackground=self.colors["border"],
                highlightthickness=1
            )
            card.pack(side="left", fill="both", expand=True, padx=5)

            day_label = tk.Label(
                card,
                text="--",
                font=("Segoe UI", 11, "bold"),
                fg=self.colors["text"],
                bg=self.colors["card_bg"]
            )
            day_label.pack(pady=(16, 6))

            icon_label = tk.Label(
                card,
                text="☁️",
                font=("Segoe UI Emoji", 28),
                fg=self.colors["text"],
                bg=self.colors["card_bg"]
            )
            icon_label.pack()

            temp_label = tk.Label(
                card,
                text="-- / --",
                font=("Segoe UI", 11),
                fg=self.colors["soft_text"],
                bg=self.colors["card_bg"]
            )
            temp_label.pack(pady=(8, 4))

            rain_label = tk.Label(
                card,
                text="Rain: --",
                font=("Segoe UI", 9),
                fg=self.colors["muted"],
                bg=self.colors["card_bg"]
            )
            rain_label.pack(pady=(0, 14))

            self.forecast_cards.append({
                "day": day_label,
                "icon": icon_label,
                "temp": temp_label,
                "rain": rain_label
            })

    # TEMPERATURE FORMATTING
    def format_temperature(self, celsius_value):
        if celsius_value == "--" or celsius_value is None:
            return "--"

        try:
            celsius_value = float(celsius_value)

            if self.temperature_unit.get() == "fahrenheit":
                fahrenheit = (celsius_value * 9 / 5) + 32
                return f"{fahrenheit:.1f}°F"

            return f"{celsius_value:.1f}°C"

        except Exception:
            return "--"

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

            try:
                save_favorites(self.favorites)
                self.status_label.config(text=f"Added {city} to favorites.")
            except Exception as error:
                messagebox.showerror("Favorites Error", f"Could not save favorites:\n{error}")

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

            try:
                save_favorites(self.favorites)
                self.status_label.config(text=f"Removed {selected_city} from favorites.")
            except Exception as error:
                messagebox.showerror("Favorites Error", f"Could not save favorites:\n{error}")

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
            weather_data = get_weather(location["latitude"], location["longitude"])

            self.after(0, self.update_dashboard, location, weather_data)

        except requests.exceptions.Timeout:
            self.after(0, self.show_error, "The weather service took too long to respond.")

        except requests.exceptions.ConnectionError:
            self.after(0, self.show_error, "Could not connect to the weather service.")

        except requests.exceptions.HTTPError:
            self.after(0, self.show_error, "The weather service returned an error.")

        except ValueError as error:
            self.after(0, self.show_error, str(error))

        except Exception as error:
            self.after(0, self.show_error, f"Unexpected error: {error}")

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
        self.temperature_label.config(text=self.format_temperature(temperature))
        self.condition_label.config(text=condition)

        self.feels_like_value.config(text=self.format_temperature(feels_like))
        self.humidity_value.config(text=f"{humidity}%")
        self.wind_value.config(text=f"{wind_speed} km/h")
        self.cloud_value.config(text=f"{cloud_cover}%")

        for index, card in enumerate(self.forecast_cards):
            date_text = daily["time"][index]
            date_object = datetime.strptime(date_text, "%Y-%m-%d")
            day_name = date_object.strftime("%a")

            forecast_code = daily["weather_code"][index]
            _, forecast_icon = WEATHER_CODES.get(forecast_code, ("Unknown", "❔"))

            max_temp = daily["temperature_2m_max"][index]
            min_temp = daily["temperature_2m_min"][index]
            rain_probability = daily["precipitation_probability_max"][index]

            card["day"].config(text=day_name)
            card["icon"].config(text=forecast_icon)
            card["temp"].config(
                text=f"{self.format_temperature(max_temp)} / {self.format_temperature(min_temp)}"
            )
            card["rain"].config(text=f"Rain: {rain_probability}%")

        self.status_label.config(text="Weather data loaded successfully.")
        self.canvas.yview_moveto(0)

    def show_error(self, message):
        self.status_label.config(text="Error loading weather data.")
        messagebox.showerror("Weather Dashboard Error", message)
