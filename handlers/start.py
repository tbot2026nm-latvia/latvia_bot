from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("👋 Xush kelibsiz!\nRo‘yxatdan o‘tish uchun /register ni bosing")
