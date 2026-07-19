# Weather Dash

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-0ea5e9)
![API](https://img.shields.io/badge/API-Open--Meteo-22c55e)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A simple desktop **Weather Dashboard** built with **Python** and **Tkinter**. The app retrieves current weather conditions and a 5-day forecast using the Open-Meteo weather API.

---
> [!IMPORTANT]
> Some of the code has been generated with Copilot.
> I've double-checked it and didn't see any time bombs or random connects to its Microslop overlords but still feel it should be clearly stated.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Execution](#execution)
- [Quick User Guide](#quick-user-guide)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- Current weather overview
- 5-day forecast
- Celsius and Fahrenheit toggle
- Dark theme and light theme toggle
- Persistant favorites & configs.
- OS-region-based default city instead of GPS-based

---

## Requirements

- Python 3.10 or newer recommended
- Requests library

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/giterziev/weather-dash
```

### 2. Navigate into the project folder

```bash
cd weather-dashboard
```

### 3. Create a virtual environment

#### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Execution

Run the app from the project root folder:

```bash
python weather_dashboard.py
```

---

## Quick User Guide

### Search for a city

1. Type a city name into the search box.
2. Press **Enter** or click **Search**.
3. The current weather and 5-day forecast will load automatically.

Example searches:

```text
Madrid
Pittsburgh
London
Sofia
Tokyo
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'requests'`

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Or install Requests directly:

```bash
python -m pip install requests
```

---

### Tkinter is missing on Linux

Install Tkinter through your package manager.

#### Ubuntu/Debian

```bash
sudo apt install python3-tk
```

#### Fedora

```bash
sudo dnf install python3-tkinter
```

---

### City not found

Try searching for a more specific city name. For example:

```text
Paris
Paris, Texas
Madrid
Madrid, Spain
```

---

## Future Improvements

Possible, but unlikely, next features:

- Hourly forecast section
- System tray support
- Auto-refresh weather data
- Search history
- Weather alerts
- Packaged Windows `.exe` using PyInstaller

---

## License

This project is provided under the MIT license.
