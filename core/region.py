import locale


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
