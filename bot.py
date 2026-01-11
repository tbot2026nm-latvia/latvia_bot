import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from services.db import connect_db
from services.monitor import monitor_loop
from handlers import start, register, menu, admin

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)

    await connect_db()
    asyncio.create_task(monitor_loop(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
