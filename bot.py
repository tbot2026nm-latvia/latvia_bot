import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =====================
# STORAGE
# =====================
user_data = {}

# =====================
# /START
# =====================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    text = (
        "🔐 *XAVFSIZLIK VA FOYDALANISH QOIDALARI*\n\n"
        "• Bot rasmiy tizim emas\n"
        "• Login/parol so‘ramaydi\n"
        "• Uchinchi shaxsga oshkor etilmaydi\n"
        "• Ma’lumotlar faqat kuzatuv uchun\n\n"
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
    user_data[uid] = {"step": "first_name"}
    await callback.message.answer("✍️ Ismingizni kiriting:")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "decline")
async def decline(callback: types.CallbackQuery):
    await callback.message.answer("❌ Roziliksiz botdan foydalanib bo‘lmaydi.")
    await callback.answer()

# =====================
# TEXT HANDLER (FAQAT TEXT)
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
        kb.add(
            KeyboardButton(
                "📱 Telefon raqamni yuborish",
                request_contact=True
            )
        )

        await message.answer(
            "📱 Telefon raqamingizni *tugma orqali* yuboring:",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return

# =====================
# PHONE HANDLER (CONTACT)
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
        "🛂 Pasportingizni yuboring:\n\n"
        "• JPG format\n"
        "• 1 MB dan oshmasin\n"
        "• Aniq ko‘rinsin",
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
    user_data[uid]["step"] = "done"

    await message.answer(
        "✅ *Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!*\n\n"
        "Endi menyudan foydalanishingiz mumkin.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

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
# MENU CALLBACKS
# =====================
@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(callback: types.CallbackQuery):
    d = user_data.get(callback.from_user.id, {})
    await callback.message.answer(
        f"👤 Profil\n\n"
        f"Ism: {d.get('first_name')}\n"
        f"Familiya: {d.get('last_name')}\n"
        f"Telefon: {d.get('phone')}"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_menu(callback: types.CallbackQuery):
    await callback.message.answer("ℹ️ Yordam bo‘limi")
    await callback.answer()

# =====================
# RUN
# =====================
if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
