from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mening holatim")],
            [KeyboardButton(text="📅 Navbatim")],
            [KeyboardButton(text="🆘 Yordam")]
        ],
        resize_keyboard=True
    )
    await msg.answer("Xush kelibsiz 🇱🇻 Latvia Bot", reply_markup=kb)
