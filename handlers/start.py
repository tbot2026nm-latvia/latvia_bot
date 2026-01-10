from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

RULES_TEXT = """
🛡 <b>Xavfsizlik va foydalanish qoidalari</b>

Ushbu bot Latviyaning VFS / Elchixona navbatlarini kuzatish uchun yaratilgan.

🔐 Siz kiritgan shaxsiy ma’lumotlar (ism, telefon, pasport):
• faqat navbat monitoringi uchun ishlatiladi
• uchinchi shaxslarga berilmaydi
• faqat admin tomonidan ko‘riladi

❗ Yolg‘on ma’lumot berish taqiqlanadi  
❗ Bitta odam – bitta ro‘yxat  

Admin tasdiqlamaguncha bot funksiyalari yopiq bo‘ladi.

Davom etish orqali ushbu qoidalarga rozilik bildirasiz.
"""

def agree_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Roziman", callback_data="agree_rules")]
    ])

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(RULES_TEXT, reply_markup=agree_kb())

@router.callback_query(lambda c: c.data == "agree_rules")
async def agreed(call: CallbackQuery):
    await call.message.edit_text(
        "🎉 <b>Xush kelibsiz!</b>\n\n"
        "Ro‘yxatdan o‘tish uchun quyidagi tugmani bosing.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ro‘yxatdan o‘tish", callback_data="start_register")]
        ])
    )
    await call.answer()
