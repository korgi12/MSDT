import aiohttp
import re
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from constants import BOT_TOKEN, WEATHER_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Константы
API_URLS = {
    "current_weather": "http://api.openweathermap.org/data/2.5/weather",
    "forecast": "http://api.openweathermap.org/data/2.5/forecast",
}
WEATHER_PARAMS = {
    "appid": WEATHER_API_KEY,
    "units": "metric",
    "lang": "ru",
}


# Универсальная функция для запросов к API OpenWeather
async def fetch_weather_data(url: str, params: dict) -> Optional[dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"Ошибка API {url}: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе {url}: {e}")
    return None


# Получение текущей погоды
async def get_weather(lat: Optional[float] = None, lon: Optional[float] = None, city_name: Optional[str] = None) -> str:
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


# Получение прогноза погоды
async def get_forecast(city_name: str) -> str:
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


# Клавиатура с быстрыми действиями
def get_weather_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Отправить геопозицию", request_location=True))
    keyboard.add(KeyboardButton("Узнать погоду по городу"))
    keyboard.add(KeyboardButton("Прогноз на 5 дней"))
    return keyboard


# Обработчики сообщений
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я могу рассказать тебе о погоде. Выбери действие:",
        reply_markup=get_weather_keyboard(),
    )


@dp.message_handler(content_types=ContentType.LOCATION)
async def handle_location(message: types.Message):
    if message.location:
        weather_info = await get_weather(lat=message.location.latitude, lon=message.location.longitude)
        await message.reply(weather_info)


@dp.message_handler(content_types=ContentType.TEXT)
async def handle_text(message: types.Message):
    user_input = message.text.strip().lower()
    forecast_match = re.match(r"прогноз\s+(.+)", user_input, re.IGNORECASE)

    if user_input == "узнать погоду по городу":
        await message.reply("Введите название города, чтобы узнать погоду.")
    elif user_input == "прогноз на 5 дней":
        await message.reply("Введите название города для получения прогноза на 5 дней.")
    elif forecast_match:
        city_name = forecast_match.group(1).strip()
        forecast_info = await get_forecast(city_name)
        await message.reply(forecast_info)
    else:
        city_name = message.text.strip()
        weather_info = await get_weather(city_name=city_name)
        await message.reply(weather_info)


@dp.message_handler()
async def handle_unknown(message: types.Message):
    await message.reply("Я понимаю только команды /start, геопозицию и названия городов.")


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)