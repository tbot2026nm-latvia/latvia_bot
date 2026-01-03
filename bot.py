import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # Serverga tokenni environment variable sifatida qo'yamiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

subscribers = set()

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Assalomu alaykum!\n"
        "Latviya vizosi uchun VFS navbat kuzatuvchi bot.\n\n"
        "➕ Kuzatishga qo‘shilish: /subscribe\n"
        "➖ Ro‘yxatdan chiqish: /unsubscribe"
    )

@dp.message(Command("subscribe"))
async def subscribe(m: Message):
    subscribers.add(m.from_user.id)
    await m.answer("Siz kuzatuvchilar ro‘yxatiga qo‘shildingiz.")

@dp.message(Command("unsubscribe"))
async def unsubscribe(m: Message):
    subscribers.discard(m.from_user.id)
    await m.answer("Siz ro'yxatdan o'chirildingiz.")

async def notify_all(text: str):
    for uid in list(subscribers):
        try:
            await bot.send_message(uid, text)
        except:
            pass

async def main():
    print("BOT ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
