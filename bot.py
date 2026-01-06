import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# =====================
# ENV
# =====================

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
# COMMANDS
# =====================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum!\n\n"
        "Bu monitoring bot.\n\n"
        "/subscribe — obuna bo‘lish\n"
        "/unsubscribe — chiqish\n"
        "/status — holatni tekshirish"
    )

@dp.message_handler(commands=["subscribe"])
async def subscribe(message: types.Message):
    subscribers.add(message.chat.id)
    await message.answer("Siz kuzatuvga qo‘shildingiz ✅")

@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe(message: types.Message):
    subscribers.discard(message.chat.id)
    await message.answer("Siz ro‘yxatdan chiqdingiz ❌")

@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    await message.answer("✅ Bot ishlayapti")

# =====================
# MONITOR (HOZIRCHA PASSIV)
# =====================

async def monitor():
    if not URL_TO_MONITOR:
        print("⚠️ URL_TO_MONITOR berilmagan")
        return

    print(f"👀 Monitoring boshlandi: {URL_TO_MONITOR}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL_TO_MONITOR) as resp:
                    print("🔎 Tekshirildi:", resp.status)
            except Exception as e:
                print("❌ Xato:", e)

            await asyncio.sleep(60)

# =====================
# MAIN
# =====================

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
