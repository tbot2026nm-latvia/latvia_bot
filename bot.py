import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils import executor

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5266262372  # ✅ SIZNING TELEGRAM ID

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =====================
# STORAGE
# =====================
user_data = {}  # user_id -> dict

# =====================
# START
# =====================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    text = (
        "🔐 *XAVFSIZLIK VA FOYDALANISH QOIDALARI*\n\n"
        "• Bot rasmiy davlat yoki VFS tizimi emas\n"
        "• Login/parol so‘ramaydi\n"
        "• Ma’lumotlar tekshiruv uchun olinadi\n\n"
        "Davom etish uchun rozilik bildiring 👇"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Roziman", callback_data="agree"),
        InlineKeyboardButton("❌ Rad etaman", callback_data="decline")
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

# =====================
# AGREEMENT
# =====================
@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user_data[uid] = {"step": "first_name", "approved": False}
    await callback.message.answer("✍️ Ismingizni kiriting:")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "decline")
async def decline(callback: types.CallbackQuery):
    await callback.message.answer("❌ Roziliksiz botdan foydalanib bo‘lmaydi.")
    await callback.answer()

# =====================
# TEXT HANDLER
# =====================
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        return

    step = user_data[uid].get("step")

    if step == "first_name":
        user_data[uid]["first_name"] = message.text.strip()
        user_data[uid]["step"] = "last_name"
        await message.answer("✍️ Familiyangizni kiriting:")
        return

    if step == "last_name":
        user_data[uid]["last_name"] = message.text.strip()
        user_data[uid]["step"] = "phone"

        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))

        await message.answer(
            "📱 Telefon raqamingizni *tugma orqali* yuboring:",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return

# =====================
# PHONE HANDLER
# =====================
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        return
    if user_data[uid].get("step") != "phone":
        return

    user_data[uid]["phone"] = message.contact.phone_number
    user_data[uid]["step"] = "passport"

    await message.answer(
        "🛂 Pasportingizni yuboring:\n"
        "• JPG format\n"
        "• 1 MB dan oshmasin",
        reply_markup=types.ReplyKeyboardRemove()
    )

# =====================
# PASSPORT HANDLER
# =====================
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_passport(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        return
    if user_data[uid].get("step") != "passport":
        return

    photo = message.photo[-1]
    if photo.file_size > 1_000_000:
        await message.answer("❌ Rasm 1 MB dan katta. Qayta yuboring.")
        return

    user_data[uid]["passport"] = photo.file_id
    user_data[uid]["step"] = "waiting"

    data = user_data[uid]

    # ===== ADMIN MESSAGE =====
    admin_text = (
        "🆕 *YANGI FOYDALANUVCHI*\n\n"
        f"👤 Ism: {data['first_name']}\n"
        f"👤 Familiya: {data['last_name']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"🆔 Telegram ID: {uid}"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve:{uid}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{uid}")
    )

    await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=kb)
    await bot.send_photo(ADMIN_ID, data["passport"], caption="🛂 Pasport nusxasi")

    await message.answer(
        "⏳ *Ma’lumotlaringiz admin tomonidan tekshirilmoqda.*\n\n"
        "Tasdiqlangach, sizga xabar beriladi.",
        parse_mode="Markdown"
    )

# =====================
# ADMIN ACTIONS
# =====================
@dp.callback_query_handler(lambda c: c.data.startswith("approve:"))
async def approve_user(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    uid = int(callback.data.split(":")[1])
    if uid not in user_data:
        return

    user_data[uid]["approved"] = True
    user_data[uid]["step"] = "done"

    await bot.send_message(
        uid,
        "✅ *Admin tomonidan tasdiqlandingiz!*\n\n"
        "Endi bot menyusidan foydalanishingiz mumkin.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.message.edit_text("✅ Foydalanuvchi tasdiqlandi")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("reject:"))
async def reject_user(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    uid = int(callback.data.split(":")[1])
    user_data.pop(uid, None)

    await bot.send_message(
        uid,
        "❌ *Admin tomonidan rad etildingiz.*\n\n"
        "Ma’lumotlaringizni qayta tekshirib /start orqali qayta urinib ko‘ring.",
        parse_mode="Markdown"
    )

    await callback.message.edit_text("❌ Foydalanuvchi rad etildi")
    await callback.answer()

# =====================
# MENU
# =====================
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🟧 📊 Navbat holati", callback_data="queue"),
        InlineKeyboardButton("🟩 📅 Taxminiy sana", callback_data="date"),
        InlineKeyboardButton("🟧 🔔 Kuzatuv holati", callback_data="monitor"),
        InlineKeyboardButton("🟩 👤 Mening ma’lumotlarim", callback_data="profile"),
    )
    kb.add(InlineKeyboardButton("⚙️ Yordam", callback_data="help"))
    return kb

# =====================
# RUN
# =====================
if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
