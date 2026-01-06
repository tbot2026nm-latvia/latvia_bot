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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

subscribers = set()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum!\n"
        "Bu test bot.\n\n"
        "/subscribe — obuna bo‘lish\n"
        "/unsubscribe — chiqish"
    )

@dp.message_handler(commands=["subscribe"])
async def subscribe(message: types.Message):
    subscribers.add(message.from_user.id)
    await message.answer("Siz kuzatuvga qo‘shildingiz ✅")

@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe(message: types.Message):
    subscribers.discard(message.from_user.id)
    await message.answer("Siz ro‘yxatdan chiqdingiz ❌")

async def monitor():
    if not URL_TO_MONITOR:
        print("⚠️ URL_TO_MONITOR berilmagan")
        return

    print(f"🔍 Monitoring boshlandi: {URL_TO_MONITOR}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL_TO_MONITOR, timeout=10) as resp:
                    if resp.status != 200:
                        for user_id in subscribers:
                            await bot.send_message(
                                user_id,
                                f"⚠️ Sayt ishlamayapti!\nStatus: {resp.status}"
                            )
            except Exception as e:
                for user_id in subscribers:
                    await bot.send_message(
                        user_id,
                        f"❌ Saytga ulanib bo‘lmadi:\n{e}"
                    )
            await asyncio.sleep(60)  # 1 daqiqa

async def on_startup(dp):
    print("✅ BOT ISHGA TUSHDI")
    asyncio.create_task(monitor())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
