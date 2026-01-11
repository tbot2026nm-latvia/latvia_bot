import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from services.db import connect_db

from handlers import start, register, admin, menu


async def main():
    # Bot
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routers
    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(admin.router)
    dp.include_router(menu.router)

    # Database
    await connect_db()

    print("✅ Database ulandi")
    print("🤖 Bot ishga tushdi")

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
