from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

WELCOME_TEXT = """
✨ <b>LATVIA VFS MONITORING BOT</b>

Siz Latviyaning:
🇱🇻 Elchixonasi
🇪🇺 VFS Global
navbatlarini avtomatik kuzatish tizimiga ulandingiz.

────────────────────
🛡 <b>Xavfsizlik va qoidalar</b>

Sizdan quyidagilar so‘raladi:
• Ism familiya  
• Telefon raqam  
• Pasport (foto)

Bu ma’lumotlar:
✔ Faqat monitoring uchun ishlatiladi  
✔ Uchinchi shaxslarga berilmaydi  
✔ Faqat admin ko‘radi  

❗ Soxta ma’lumot taqiqlanadi  
❗ Bitta odam – bitta hisob  

Admin tasdiqlamaguncha bot yopiq bo‘ladi.

────────────────────
Davom etish orqali ushbu shartlarga rozilik bildirasiz.
"""

def rules_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Roziman", callback_data="agree")],
        [InlineKeyboardButton(text="❌ Chiqish", callback_data="exit")]
    ])

@router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=rules_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "agree")
async def agree(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ro‘yxatdan o‘tish", callback_data="start_register")]
    ])

    await call.message.edit_text(
        "🎉 <b>Xush kelibsiz!</b>\n\n"
        "Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing.",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "exit")
async def exit_bot(call: CallbackQuery):
    await call.message.edit_text("🚪 Botdan chiqdingiz.")
    await call.answer()
