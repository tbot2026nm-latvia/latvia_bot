async def main():
    bot = Bot(...)
    dp = Dispatcher()

    # handlerlar keyin qo‘shiladi

    await init_db()
    await dp.from aiogram.types import Message
from aiogram.filters import Command

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("✅ Bot ishlayapti. Keyingi bosqichga o‘tamiz.")
start_polling(bot)
