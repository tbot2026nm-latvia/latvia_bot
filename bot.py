import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
