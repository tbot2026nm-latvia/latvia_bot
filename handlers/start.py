from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
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
