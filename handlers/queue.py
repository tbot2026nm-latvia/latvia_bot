from aiogram import Router
from aiogram.types import Message
from services.db import add_queue

router = Router()

@router.message(lambda m: m.text == "📊 Navbat qo‘shish")
async def add(msg: Message):
    loading = await msg.answer("🔍 Monitoringga qo‘shilmoqda...")

    await add_queue(msg.from_user.id, "Latvia VFS", "Tashkent")

    await loading.edit_text("⏳ Navbat kuzatilmoqda...\nStatus real-time yangilanadi.")
