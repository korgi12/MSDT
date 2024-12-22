import aiohttp
import logging

from typing import Optional
from constants import WEATHER_API_KEY

logger = logging.getLogger(__name__)

API_URLS = {
    "current_weather": "http://api.openweathermap.org/data/2.5/weather",
    "forecast": "http://api.openweathermap.org/data/2.5/forecast",
}
WEATHER_PARAMS = {
    "appid": WEATHER_API_KEY,
    "units": "metric",
    "lang": "ru",
}


async def fetch_weather_data(url: str, params: dict) -> Optional[dict]:
    """
    Универсальная функция для запросов к API OpenWeather.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"Ошибка API {url}: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе {url}: {e}")
    return None


async def get_weather(lat: Optional[float] = None, lon: Optional[float] = None, city_name: Optional[str] = None) -> str:
    """
    Получение текущей погоды.
    """
    params = WEATHER_PARAMS.copy()
    if city_name:
        params["q"] = city_name
    elif lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    else:
        return "Не указаны данные для поиска погоды."

    data = await fetch_weather_data(API_URLS["current_weather"], params)
    if not data:
        return "Не удалось получить данные о погоде."

    weather = data.get("weather", [{}])[0].get("description", "Неизвестно").capitalize()
    temp = data.get("main", {}).get("temp", "Неизвестно")
    city = data.get("name", "Неизвестный город")
    return f"Погода в {city}:\n{weather}, {temp}°C"


async def get_forecast(city_name: str) -> str:
    """
    Получение прогноза погоды.
    """
    params = WEATHER_PARAMS.copy()
    params["q"] = city_name

    data = await fetch_weather_data(API_URLS["forecast"], params)
    if not data:
        return "Не удалось получить данные о прогнозе."

    forecast_list = [
        f"{forecast.get('dt_txt', 'Неизвестно')}: "
        f"{forecast.get('weather', [{}])[0].get('description', 'Неизвестно').capitalize()}, "
        f"{forecast.get('main', {}).get('temp', 'Неизвестно')}°C"
        for forecast in data.get("list", [])[:10]
    ]
    return "\n".join(forecast_list) if forecast_list else "Прогноз не найден."