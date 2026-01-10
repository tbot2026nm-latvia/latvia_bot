from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

WELCOME = """
✨ <b>LATVIA VFS MONITORING BOT</b>

Siz Latviyaning:
🇱🇻 Elchixona  
🇪🇺 VFS Global  
navbatlarini avtomatik kuzatish uchun rasmiy monitoring tizimiga ulandingiz.

────────────────────
🛡 Xavfsizlik va foydalanish qoidalari!

🔐 Siz kiritishingiz shart:
• ism familiya
• telefon raqam
• pasport "JPG" formatda

Faqat navbat monitoringi uchun ishlatiladi  
Uchinchi shaxslarga berilmaydi  
Faqat Admin tomonidan ko‘riladi  

❗ Soxta yoki boshqa bir shaxs nomidan ro‘yxatdan o‘tish taqiqlanadi  
❗ Bitta odam – bitta hisob  

Admin tasdiqlamaguncha tizim yopiq bo‘ladi.

────────────────────
Davom etish orqali siz ushbu shartlarga rozilik bildirasiz.
"""

def rules_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Roziman", callback_data="agree")],
        [InlineKeyboardButton(text="❌ Chiqish", callback_data="exit")]
    ])

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME, reply_markup=rules_keyboard())

@router.callback_query(lambda c: c.data == "agree")
async def agreed(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ro‘yxatdan o‘tish", callback_data="start_register")]
    ])

    await call.message.edit_text(
        "🎉 Xush kelibsiz!\n\n"
        "Siz tizimga kirdingiz.\n"
        "Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing.",
        reply_markup=kb
    )
    await call.answer()

@router.callback_query(lambda c: c.data == "exit")
async def exit_bot(call: CallbackQuery):
    await call.message.edit_text("🚪 Botdan chiqdingiz.")
    await call.answer()
