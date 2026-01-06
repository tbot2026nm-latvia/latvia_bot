import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL_TO_MONITOR = os.getenv("URL_TO_MONITOR")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

# =====================
# BOT
# =====================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

subscribers = set()

# =====================
# MONITOR SETTINGS
# =====================

URL_TO_MONITOR = "https://example.com/?test=1"  # 🔴 HOZIRCHA TEST URL
CHECK_INTERVAL = 60  # soniya

_last_hash = None

# =====================
# COMMANDS
# =====================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum!\n\n"
        "Bu monitoring bot.\n\n"
        "/subscribe — obuna bo‘lish\n"
        "/unsubscribe — chiqish"
    )

@dp.message_handler(commands=["subscribe"])
async def subscribe(message: types.Message):
    subscribers.add(message.chat.id)
    await message.answer("Siz kuzatuvga qo‘shildingiz ✅")

@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe(message: types.Message):
    subscribers.discard(message.chat.id)
    await message.answer("Siz ro‘yxatdan chiqdingiz ❌")

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
