from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

WELCOME = """
✨ LATVIA VFS MONITORING BOT

Siz Latviyaning:
🇱🇻 Elchixona  
🇪🇺 VFS Global  
navbatlarini avtomatik kuzatish tizimiga ulandingiz.

────────────────────
🛡 Xavfsizlik va foydalanish qoidalari

🔐 Sizdan so‘raladi:
• Ism familiya
• Telefon raqam
• Pasport JPG

Ma’lumotlar:
• Faqat navbat uchun ishlatiladi
• Uchinchi shaxslarga berilmaydi
• Faqat Admin ko‘radi

❗ Soxta ma’lumot taqiqlanadi  
❗ Bitta odam – bitta hisob  

Admin tasdiqlamaguncha tizim yopiq.

────────────────────
Davom etish orqali rozilik bildirasiz.
"""

def rules_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Roziman", callback_data="agree")],
            [InlineKeyboardButton(text="❌ Chiqish", callback_data="exit")]
        ]
    )

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME, reply_markup=rules_keyboard())

@router.callback_query(F.data == "agree")
async def agreed(call: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ro‘yxatdan o‘tish", callback_data="start_register")]
        ]
    )

    await call.message.edit_text(
        "🎉 Xush kelibsiz!\n\n"
        "Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing:",
        reply_markup=kb
    )
    await call.answer()

@router.callback_query(F.data == "exit")
async def exit_bot(call: CallbackQuery):
    await call.message.edit_text("🚪 Botdan chiqdingiz.")
    await call.answer()
