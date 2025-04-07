import datetime
import os

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from dotenv import load_dotenv

# Load environment variables from .env file (if used)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# /start command
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.full_name}!")
    await message.answer("Write me the name of the city and I will send you the weather report!")


# /help command
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Command list:",
            "/start - Start a dialogue",
            "/help - Get help")
    await message.answer("\n".join(text))


# Handling city input and fetching weather
@dp.message_handler()
async def get_weather_def(message: types.Message):
    code_to_emoji = {
        "Clear": "Clear ☀️",
        "Clouds": "Clouds ☁️",
        "Rain": "Rain 🌧️",
        "Drizzle": "Drizzle 🌧️",
        "Thunderstorm": "Thunderstorm ⚡",
        "Snow": "Snow 🌨️",
        "Mist": "Mist 🌫️"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={OWM_API_KEY}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        wd = code_to_emoji.get(weather_description, "Look out the window!")

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        day_length = sunset - sunrise

        await message.reply(
            f"🌆 City: {city}\n🌡️ Temp: {cur_weather}°C {wd}\n"
            f"💧 Humidity: {humidity}%\n📈 Pressure: {pressure} mmHg\n💨 Wind: {wind} m/s\n"
            f"🌅 Sunrise: {sunrise}\n🌇 Sunset: {sunset}\n🕓 Day Length: {day_length}"
        )
    except:
        await message.reply("⚠️ Could not find the city. Please check the name.")


# Bot start
if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp)
