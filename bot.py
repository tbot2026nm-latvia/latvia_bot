import os
import asyncio
import hashlib
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# =====================
# ENV VARIABLES
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL_TO_MONITOR = os.getenv("URL_TO_MONITOR")
CHECK_INTERVAL = 60  # soniya

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

if not URL_TO_MONITOR:
    print("⚠️ URL_TO_MONITOR berilmagan — monitoring o‘chiq")
    URL_TO_MONITOR = None

# =====================
# BOT SETUP
# =====================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

subscribers = set()
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

# =====================
# MONITOR FUNCTION
# =====================

async def monitor():
    global _last_hash

    if not URL_TO_MONITOR:
        return

    print(f"👀 Monitoring boshlandi: {URL_TO_MONITOR}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL_TO_MONITOR, timeout=20) as resp:
                    text = await resp.text()
                    current_hash = hashlib.md5(text.encode()).hexdigest()

                    if _last_hash and current_hash != _last_hash:
                        print("⚠️ Saytda o‘zgarish aniqlandi")

                        for user_id in subscribers:
                            await bot.send_message(
                                user_id,
                                "⚠️ Saytda o‘zgarish aniqlandi!"
                            )

                    _last_hash = current_hash

            except Exception as e:
                print(f"❌ Monitoring xatosi: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

# =====================
# STARTUP
# =====================

async def on_startup(dp):
    print("✅ BOT ISHGA TUSHDI")
    asyncio.create_task(monitor())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)