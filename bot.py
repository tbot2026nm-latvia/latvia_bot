import os
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# =====================
# CONFIG
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =====================
# STORAGE (oddiy xotira)
# =====================

users = {}  # chat_id -> data

# =====================
# KEYBOARDS
# =====================

agree_kb = ReplyKeyboardMarkup(resize_keyboard=True)
agree_kb.add(KeyboardButton("✅ Roziman"))

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("📅 Qabul sanasini kiritish"),
    KeyboardButton("⏰ Mening eslatmalarim"),
)
menu.add(
    KeyboardButton("📄 Hujjatlar ro‘yxati"),
    KeyboardButton("ℹ️ Qanday ishlaydi?"),
)
menu.add(
    KeyboardButton("❌ Kuzatuvni bekor qilish"),
)

skip_kb = ReplyKeyboardMarkup(resize_keyboard=True)
skip_kb.add(KeyboardButton("➡️ O‘tkazib yuborish"))

# =====================
# START
# =====================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users[message.chat.id] = {"step": "agree"}
    await message.answer(
        "🔐 XAVFSIZLIK VA TARTIB-QOIDALAR\n\n"
        "• Bot rasmiy VFS yoki elchixona EMAS\n"
        "• Login/parol so‘RAMAYDI\n"
        "• Bot navbat band qilmaydi\n"
        "• Ma’lumotlar faqat eslatma uchun ishlatiladi\n\n"
        "Davom etish uchun rozilik bildiring:",
        reply_markup=agree_kb
    )

# =====================
# AGREEMENT
# =====================

@dp.message_handler(text="✅ Roziman")
async def agree(message: types.Message):
    users[message.chat.id]["step"] = "first_name"
    await message.answer("Ismingizni kiriting:")

# =====================
# REGISTRATION FLOW
# =====================

@dp.message_handler(lambda m: m.chat.id in users)
async def registration(message: types.Message):
    user = users[message.chat.id]

    if user.get("step") == "first_name":
        user["first_name"] = message.text
        user["step"] = "last_name"
        await message.answer("Familiyangizni kiriting:")
        return

    if user.get("step") == "last_name":
        user["last_name"] = message.text
        user["step"] = "phone"
        await message.answer("Telefon raqamingizni kiriting:\n(+998901234567)")
        return

    if user.get("step") == "phone":
        user["phone"] = message.text
        user["step"] = "myid"
        await message.answer(
            "🪪 myID orqali tasdiqlash (tavsiya etiladi)\n\n"
            "👉 https://myid.uz\n\n"
            "Tasdiqlaganingizdan so‘ng yoki hozircha o‘tkazib yuborishingiz mumkin.",
            reply_markup=skip_kb
        )
        return

    if user.get("step") == "myid":
        user["myid"] = "skipped"
        user["step"] = "done"
        await message.answer(
            "✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!\n\n"
            "Endi menyudan foydalanishingiz mumkin.",
            reply_markup=menu
        )
        return

# =====================
# MENU HANDLERS
# =====================

@dp.message_handler(text="📅 Qabul sanasini kiritish")
async def set_date(message: types.Message):
    users[message.chat.id]["step"] = "date"
    await message.answer(
        "📅 Qabul sanasini kiriting:\n\n"
        "DD.MM.YYYY HH:MM\n"
        "Masalan: 15.04.2026 09:30"
    )

@dp.message_handler(lambda m: users.get(m.chat.id, {}).get("step") == "date")
async def save_date(message: types.Message):
    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        users[message.chat.id]["appointment"] = dt
        users[message.chat.id]["step"] = "done"

        await message.answer(
            f"✅ Qabul sanasi saqlandi:\n\n"
            f"📅 {dt.strftime('%d.%m.%Y')}\n"
            f"⏰ {dt.strftime('%H:%M')}",
            reply_markup=menu
        )
    except ValueError:
        await message.answer("❌ Sana formati noto‘g‘ri.")

@dp.message_handler(text="⏰ Mening eslatmalarim")
async def reminders(message: types.Message):
    user = users.get(message.chat.id)
    if not user or "appointment" not in user:
        await message.answer("❗ Qabul sanasi kiritilmagan.")
        return

    dt = user["appointment"]
    await message.answer(f"📅 Qabul sanangiz:\n{dt.strftime('%d.%m.%Y %H:%M')}")

@dp.message_handler(text="📄 Hujjatlar ro‘yxati")
async def docs(message: types.Message):
    await message.answer(
        "📄 HUJJATLAR (umumiy):\n"
        "• Pasport\n"
        "• Ariza\n"
        "• Rasm\n"
        "• Sug‘urta\n"
        "• To‘lov kvitansiyasi"
    )

@dp.message_handler(text="ℹ️ Qanday ishlaydi?")
async def info(message: types.Message):
    await message.answer(
        "Bot siz kiritgan qabul sanasiga qarab\n"
        "7 / 3 / 1 kun oldin eslatma yuboradi."
    )

@dp.message_handler(text="❌ Kuzatuvni bekor qilish")
async def cancel(message: types.Message):
    users.pop(message.chat.id, None)
    await message.answer("❌ Kuzatuv bekor qilindi.\n/start bilan qayta boshlang.")

# =====================
# REMINDER LOOP
# =====================

async def reminder_loop():
    while True:
        now = datetime.now()
        for chat_id, user in users.items():
            dt = user.get("appointment")
            if not dt:
                continue

            for days in [7, 3, 1]:
                key = f"reminded_{days}"
                if not user.get(key) and now + timedelta(days=days) >= dt > now:
                    await bot.send_message(
                        chat_id,
                        f"⏰ Eslatma!\n{days} kun qoldi.\n📅 {dt.strftime('%d.%m.%Y %H:%M')}"
                    )
                    user[key] = True
        await asyncio.sleep(3600)

# =====================
# START BOT
# =====================

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(reminder_loop())
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
