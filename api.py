import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ForecastError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class LocationSearchError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class WeatherValuesError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

API_KEY = os.getenv("API_KEY")

def get_weather(location_key):
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {"apikey": API_KEY, "details": True, "metric": True}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе погоды: {e}")
        raise ForecastError("Ошибка при запросе погоды. Проверьте подключение к интернету или доступность API.")

def parse_needed_values(weather_data):
    """Берет весь словарь от api, возвращает три интересующих значения по ключам:
    temperature, wind_speed, precipitation_probability
    Или None."""
       
    try:
        temperature = weather_data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
        wind_speed = weather_data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
        precipitation_probability = weather_data["DailyForecasts"][0]["Day"]["PrecipitationProbability"]
        return temperature, wind_speed, precipitation_probability
    except (KeyError, IndexError) as e:
        print("Ошибка при парсинге данных погоды:", e)
        raise WeatherValuesError("Ошибка при извлечении значений погоды.")

def get_location_key(city_name):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {"apikey": API_KEY, "q": city_name}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise LocationSearchError(f"Город '{city_name}' не найден.")
        return data[0]["Key"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе местоположения: {e}")
        raise LocationSearchError("Ошибка при запросе местоположения. Проверьте подключение к интернету или доступность API.")

def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35:
        return False
    if wind_speed > 50:
        return False
    if precipitation_probability > 70:
        return False
    return True