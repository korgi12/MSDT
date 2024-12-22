import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from constants import BOT_TOKEN, WEATHER_API_KEY

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Асинхронная функция для запроса текущей погоды
async def get_weather(lat=None, lon=None, city_name=None):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    if city_name:
        params["q"] = city_name
    elif lat and lon:
        params["lat"] = lat
        params["lon"] = lon

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                weather = data.get("weather", [{}])[0].get("description", "Неизвестно")
                temp = data.get("main", {}).get("temp", "Неизвестно")
                city = data.get("name", "Неизвестный город")
                return f"Погода в {city}:\n{weather.capitalize()}, {temp}°C"
            else:
                return "Не удалось получить данные о погоде."

# Асинхронная функция для запроса прогноза погоды
async def get_forecast(city_name):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                forecast_list = []
                for forecast in data.get("list", [])[:5]:  # 5 ближайших прогнозов
                    dt = forecast.get("dt_txt", "Неизвестно")
                    temp = forecast.get("main", {}).get("temp", "Неизвестно")
                    weather = forecast.get("weather", [{}])[0].get("description", "Неизвестно")
                    forecast_list.append(f"{dt}: {weather.capitalize()}, {temp}°C")
                return "\n".join(forecast_list)
            else:
                return f"Не удалось получить данные о прогнозе в {city_name}."

# Клавиатура с быстрыми действиями
weather_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
weather_keyboard.add(KeyboardButton("Отправить геопозицию", request_location=True))
weather_keyboard.add(KeyboardButton("Узнать погоду по городу"))
weather_keyboard.add(KeyboardButton("Прогноз на 5 дней"))

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я могу рассказать тебе о погоде. Выбери действие:",
        reply_markup=weather_keyboard
    )

# Обработчик геопозиции
@dp.message_handler(content_types=ContentType.LOCATION)
async def handle_location(message: types.Message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        weather_info = await get_weather(lat=lat, lon=lon)
        await message.reply(weather_info)

# Обработчик текста (поиск погоды по названию города)
@dp.message_handler(content_types=ContentType.TEXT)
async def handle_text(message: types.Message):
    user_input = message.text.strip().lower()

    if user_input == "узнать погоду по городу":
        await message.reply("Введите название города, чтобы узнать погоду.")
    elif user_input == "прогноз на 5 дней":
        await message.reply("Введите название города для получения прогноза на 5 дней.")
    else:
        city_name = message.text.strip()
        if len(city_name) > 0:
            if "прогноз" in user_input:
                forecast_info = await get_forecast(city_name)
                await message.reply(forecast_info)
            else:
                weather_info = await get_weather(city_name=city_name)
                await message.reply(weather_info)
        else:
            await message.reply("Я не понимаю ваш запрос. Попробуйте снова.")

# Обработчик всех остальных сообщений
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("Я понимаю только команды /start, геопозицию и названия городов.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)