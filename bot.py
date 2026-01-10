import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from services.db import connect_db
from handlers import start, register, admin, menu

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(admin.router)
    dp.include_router(menu.router)

    await connect_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
pip install -r requirements.txt
python bot.py

from handlers import start, admin, menu
dp.include_router(start.router)
dp.include_router(admin.router)
dp.include_router(menu.router)
