import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor

from constants import BOT_TOKEN, WEATHER_API_KEY

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Функция для запроса погоды
def get_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data.get("weather", [{}])[0].get("description", "Неизвестно")
        temp = data.get("main", {}).get("temp", "Неизвестно")
        city = data.get("name", "Неизвестный город")
        return f"Погода в {city}:\n{weather.capitalize()}, {temp}°C"
    else:
        return "Не удалось получить данные о погоде."


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне свою геопозицию, и я скажу тебе погоду.")


# Обработчик геопозиции
@dp.message_handler(content_types=ContentType.LOCATION)
async def handle_location(message: types.Message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        weather_info = get_weather(lat, lon)
        await message.reply(weather_info)


# Обработчик всех остальных сообщений
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("Я понимаю только команды /start и геопозицию!")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)