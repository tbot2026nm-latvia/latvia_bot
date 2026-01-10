from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states import Register

router = Router()

@router.message(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    text = (
        "🛡 Xavfsizlik va foydalanish qoidalari\n\n"
        "Ushbu bot Latviyaning VFS / Elchixona navbatlarini kuzatish uchun yaratilgan.\n\n"
        "🔒 Siz kiritgan shaxsiy ma’lumotlar (ism, telefon, pasport):\n"
        "• faqat navbat monitoringi uchun ishlatiladi\n"
        "• uchinchi shaxslarga berilmaydi\n"
        "• faqat Admin tomonidan ko‘riladi\n"
        "❗ Yolg‘on yoki boshqa shaxs nomidan ro‘yxatdan o‘tish taqiqlanadi.\n"
        "❗ Bitta odam – bitta ro‘yxat.\n"
        "Admin tasdiqlamaguncha bot funksiyalari yopiq bo‘ladi.\n"
        "Ma’lumotlaringiz faqat admin ko‘radi.\n\n"
        "Davom etish orqali ushbu qoidalarga rozilik bildirasiz.\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "[ ✅ Roziman ]\n"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="✅ Roziman", callback_data="agree")]]
    )

    await message.answer(text, reply_markup=kb)
    await state.set_state(Register.waiting_agreement)

@router.callback_query(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("👤 Ismingizni kiriting:")
    await state.set_state(Register.first_name)
