import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

URL_TO_MONITOR = "https://example.com"  # hozircha test
CHECK_INTERVAL = 60  # sekund

_last_content = None

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

# =====================
# MONITOR FUNCTION
# =====================

async def monitor():
    global _last_content
    await bot.wait_until_ready()

    print(f"👀 Monitoring boshlandi: {URL_TO_MONITOR}")

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL_TO_MONITOR, timeout=15) as resp:
                    text = await resp.text()

            if _last_content and text != _last_content:
                for user_id in subscribers:
                    await bot.send_message(
                        user_id,
                        "⚠️ Saytda o‘zgarish aniqlandi!"
                    )

            _last_content = text

        except Exception as e:
            print("Monitoring xato:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# =====================
# START
# =====================

async def on_startup(dp):
    asyncio.create_task(monitor())

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
