import os
import datetime
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"👋 Hello, {message.from_user.full_name}!")
    await message.answer("Send me a city name and I will send you the weather report! 🌦️")


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("📍 Just send the name of a city and I’ll tell you the weather there!")


@dp.message(F.text)
async def get_weather(message: Message):
    city_name = message.text.strip()
    code_to_emoji = {
        "Clear": "☀️ Clear",
        "Clouds": "☁️ Clouds",
        "Rain": "🌧️ Rain",
        "Drizzle": "🌦️ Drizzle",
        "Thunderstorm": "⚡ Thunderstorm",
        "Snow": "🌨️ Snow",
        "Mist": "🌫️ Mist"
    }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OWM_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            raise ValueError("City not found")

        city = data["name"]
        temp = data["main"]["temp"]
        description = data["weather"][0]["main"]
        weather_icon = code_to_emoji.get(description, "🔍 Unknown")

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]

        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length = sunset - sunrise

        await message.answer(
            f"🌆 <b>City:</b> {city}\n"
            f"🌡️ <b>Temperature:</b> {temp}°C {weather_icon}\n"
            f"💧 <b>Humidity:</b> {humidity}%\n"
            f"📈 <b>Pressure:</b> {pressure} hPa\n"
            f"💨 <b>Wind:</b> {wind_speed} m/s\n"
            f"🌅 <b>Sunrise:</b> {sunrise.strftime('%H:%M:%S')}\n"
            f"🌇 <b>Sunset:</b> {sunset.strftime('%H:%M:%S')}\n"
            f"🕓 <b>Day Length:</b> {length}"
        )
    except Exception as e:
        print("Error:", e)
        await message.answer("⚠️ Could not find the city. Please try again.")


async def main():
    print("🌤️ Weather bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
