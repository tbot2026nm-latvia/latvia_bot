import os
import asyncio
import hashlib
import requests

from aiogram import Bot, Dispatcher, executor, types

# =====================
# TOKEN
# =====================

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

# =====================
# MONITOR FUNCTION
# =====================

async def monitor_site():
    global _last_hash

    await asyncio.sleep(10)  # bot ishga tushishini kutadi

    while True:
        try:
            r = requests.get(URL_TO_MONITOR, timeout=15)
            text = r.text
            current_hash = hashlib.md5(text.encode()).hexdigest()

            if _last_hash and current_hash != _last_hash:
                for chat_id in subscribers:
                    try:
                        await bot.send_message(
                            chat_id,
                            "⚠️ Saytda o‘zgarish aniqlandi!"
                        )
                    except:
                        pass

            _last_hash = current_hash

        except Exception as e:
            print("Monitoring xato:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# =====================
# STARTUP
# =====================

async def on_startup(dp):
    asyncio.create_task(monitor_site())
    print("✅ Bot va monitoring ishga tushdi")

# =====================
# MAIN
# =====================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
