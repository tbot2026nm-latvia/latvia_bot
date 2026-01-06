import os
import asyncio
import aiohttp
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# =====================
# ENV
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL_TO_MONITOR = os.getenv("URL_TO_MONITOR")  # KOYEB'DA QO‘YILADI
CHECK_INTERVAL = 60  # soniya

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

if not URL_TO_MONITOR:
    print("⚠️ URL_TO_MONITOR topilmadi (monitoring o‘chiq)")
else:
    print(f"🔍 Monitoring URL: {URL_TO_MONITOR}")

# =====================
# BOT
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
        "Monitoring bot ishga tushdi.\n\n"
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

    @dp.message_handler(commands=["status"])
async def status(message: types.Message):
    monitoring_status = ("YOQILGAN ✅" if URL_TO_MONITOR else "O‘CHIQ ❌")

    await message.answer(
        "📊 BOT HOLATI\n\n"
        f"🤖 Bot: ISHLAYAPTI\n"
        f"🔍 Monitoring: {monitoring_status}\n"
        f"👥 Obunachilar: {len(subscribers)} ta"
    )

# =====================
# MONITOR
# =====================

async def monitor():
    global _last_hash

    if not URL_TO_MONITOR:
        return

    print("🔍 Monitoring boshlandi")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL_TO_MONITOR, timeout=20) as response:
                    content = await response.text()
                    current_hash = hashlib.md5(content.encode()).hexdigest()

                    if _last_hash and current_hash != _last_hash:
                        print("🚨 O‘zgarish aniqlandi")

                        for chat_id in subscribers:
                            await bot.send_message(
                                chat_id,
                                "🚨 Saytda o‘zgarish aniqlandi!"
                            )

                    _last_hash = current_hash

            except Exception as e:
                print(f"⚠️ Xatolik: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

# =====================
# START
# =====================

async def on_startup(dp):
    print("✅ BOT ISHGA TUSHDI")
    asyncio.create_task(monitor())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
