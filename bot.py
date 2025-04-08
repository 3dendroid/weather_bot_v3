import asyncio
import datetime
import logging
import os
from typing import Optional, Dict

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from cachetools import TTLCache
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")

if not BOT_TOKEN or not OWM_API_KEY:
    raise ValueError("Missing environment variables (BOT_TOKEN or OWM_API_KEY)")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Cache weather data for 10 minutes to reduce API calls
weather_cache = TTLCache(maxsize=1000, ttl=600)


# --- Weather Data Fetching ---
async def fetch_weather(city_name: str) -> Optional[Dict]:
    """Fetch weather data from OpenWeatherMap API."""
    if not city_name:
        return None

    # Check cache first
    cached_data = weather_cache.get(city_name.lower())
    if cached_data:
        return cached_data

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OWM_API_KEY}&units=metric"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

                if response.status != 200:
                    logger.error(f"API Error: {data.get('message', 'Unknown error')}")
                    return None

                weather_cache[city_name.lower()] = data  # Cache the result
                return data
    except Exception as e:
        logger.error(f"Failed to fetch weather: {e}")
        return None


# --- Weather Message Formatting ---
def format_weather_message(data: Dict) -> str:
    """Format weather data into a user-friendly message."""
    code_to_emoji = {
        "Clear": "☀️ Clear",
        "Clouds": "☁️ Clouds",
        "Rain": "🌧️ Rain",
        "Drizzle": "🌦️ Drizzle",
        "Thunderstorm": "⚡ Thunderstorm",
        "Snow": "🌨️ Snow",
        "Mist": "🌫️ Mist",
    }

    city = data["name"]
    temp = data["main"]["temp"]
    description = data["weather"][0]["main"]
    weather_icon = code_to_emoji.get(description, "🔍 Unknown")

    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind_speed = data["wind"]["speed"]

    sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S")
    sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")
    length = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
        data["sys"]["sunrise"])

    return (
        f"🌆 <b>City:</b> {city}\n"
        f"🌡️ <b>Temperature:</b> {temp}°C {weather_icon}\n"
        f"💧 <b>Humidity:</b> {humidity}%\n"
        f"📈 <b>Pressure:</b> {pressure} hPa\n"
        f"💨 <b>Wind:</b> {wind_speed} m/s\n"
        f"🌅 <b>Sunrise:</b> {sunrise}\n"
        f"🌇 <b>Sunset:</b> {sunset}\n"
        f"🕓 <b>Day Length:</b> {length}"
    )


# --- Bot Handlers ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"👋 Hello, {message.from_user.full_name}!")
    await message.answer("Send me a city name (e.g., <i>London</i>), and I'll fetch the weather! 🌦️")


@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "📍 <b>How to use this bot:</b>\n"
        "1. Send a city name (e.g., <i>Paris</i>)\n"
        "2. Get instant weather info! 🌤️\n\n"
        "⚠️ <i>Note: Only real city names work.</i>"
    )
    await message.answer(help_text)


@dp.message(F.text)
async def handle_city_input(message: Message):
    city_name = message.text.strip()

    if not city_name:
        await message.answer("⚠️ Please enter a valid city name.")
        return

    await message.answer(f"⏳ Fetching weather for <b>{city_name}</b>...")

    weather_data = await fetch_weather(city_name)

    if not weather_data:
        await message.answer("⚠️ Could not fetch weather. Is the city name correct?")
        return

    weather_message = format_weather_message(weather_data)
    await message.answer(weather_message)


# --- Main Execution ---
async def main():
    logger.info("🌤️ Weather bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
