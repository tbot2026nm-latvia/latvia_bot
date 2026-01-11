import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from services.db import connect_db
from services.monitor import monitor_loop

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await connect_db()          # 1️⃣ DB
    asyncio.create_task(monitor_loop())  # 2️⃣ MONITOR

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
