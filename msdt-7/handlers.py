import re

from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

from services import get_weather, get_forecast


def get_weather_keyboard():
    """
    Создание клавиатуры для взаимодействия с пользователем.

    :return: Объект клавиатуры с кнопками.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Отправить геопозицию", request_location=True))
    keyboard.add(KeyboardButton("Узнать погоду по городу"))
    keyboard.add(KeyboardButton("Прогноз на 5 дней"))
    return keyboard


async def send_welcome(message: types.Message):
    """
    Обработчик команды /start.
    """
    await message.reply(
        "Привет! Я могу рассказать тебе о погоде. Выбери действие:",
        reply_markup=get_weather_keyboard(),
    )


async def handle_location(message: types.Message):
    """
    Обработчик геопозиции от пользователя.
    """
    if message.location:
        weather_info = await get_weather(lat=message.location.latitude, lon=message.location.longitude)
        await message.reply(weather_info)


async def handle_text(message: types.Message):
    """
    Обработчик текстовых сообщений от пользователя.
    """
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


async def handle_unknown(message: types.Message):
    """
    Обработчик неизвестных сообщений.
    """
    await message.reply("Я понимаю только команды /start, геопозицию и названия городов.")


def register_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для бота.
    """
    dp.register_message_handler(send_welcome, commands=["start"])
    dp.register_message_handler(handle_location, content_types=ContentType.LOCATION)
    dp.register_message_handler(handle_text, content_types=ContentType.TEXT)
    dp.register_message_handler(handle_unknown)