from aiogram import Router
from aiogram.types import Message

router = Router()
ADMIN_ID = 123456789   # <-- bu yerga O‘ZINGNING Telegram ID'ingni yoz

@router.message()
async def admin_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👮 Admin panel: Hamma narsa ishlayapti.")
