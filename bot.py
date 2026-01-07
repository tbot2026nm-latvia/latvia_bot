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

# =========================
# USER STATES (oddiy usul)
# =========================
user_data = {}

# =========================
# START / RULES
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    text = (
        "🔐 *XAVFSIZLIK VA FOYDALANISH QOIDALARI*\n\n"
        "• Ushbu bot faqat xabardor qilish uchun xizmat qiladi\n"
        "• Noto‘g‘ri ma’lumot kiritish javobgarligi foydalanuvchiga tegishli\n"
        "• Pasport ma’lumotlari faqat tekshiruv uchun ishlatiladi\n\n"
        "Davom etish uchun rozilik bildiring 👇"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Roziman", callback_data="agree"),
        InlineKeyboardButton("❌ Rad etaman", callback_data="decline")
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

# =========================
# AGREEMENT
# =========================
@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {}
    await callback.message.answer("✍️ Ismingizni kiriting:")
    user_data[callback.from_user.id]["step"] = "first_name"

@dp.callback_query_handler(lambda c: c.data == "decline")
async def decline(callback: types.CallbackQuery):
    await callback.message.answer("❌ Roziliksiz botdan foydalanib bo‘lmaydi.")
    await callback.answer()

# =========================
# REGISTRATION STEPS
# =========================
@dp.message_handler(lambda m: m.from_user.id in user_data)
async def registration(message: types.Message):
    uid = message.from_user.id
    step = user_data[uid].get("step")

    if step == "first_name":
        user_data[uid]["first_name"] = message.text
        user_data[uid]["step"] = "last_name"
        await message.answer("✍️ Familiyangizni kiriting:")

    elif step == "last_name":
        user_data[uid]["last_name"] = message.text
        user_data[uid]["step"] = "phone"

        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))

        await message.answer(
            "📱 Telefon raqamingizni *Telegram orqali* yuboring:",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif step == "phone":
        if not message.contact:
            await message.answer("❗ Iltimos, telefonni *tugma orqali* yuboring.")
            return

        user_data[uid]["phone"] = message.contact.phone_number
        user_data[uid]["step"] = "passport"

        await message.answer(
            "🛂 Pasportingizni JPG formatda yuboring\n"
            "📏 Hajmi 1 MB dan oshmasin",
            reply_markup=types.ReplyKeyboardRemove()
        )

    elif step == "passport":
        if not message.photo:
            await message.answer("❗ Faqat JPG rasm yuboring.")
            return

        photo = message.photo[-1]
        if photo.file_size > 1_000_000:
            await message.answer("❗ Fayl hajmi 1 MB dan katta.")
            return

        user_data[uid]["passport_file_id"] = photo.file_id
        user_data[uid]["step"] = "done"

        await message.answer(
            "✅ *Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!*\n\n"
            "Endi bot orqali holatingizni kuzatishingiz mumkin.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# =========================
# MODERN CLASSIC MENU
# =========================
def main_menu():
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(
        InlineKeyboardButton("🟧 📊 Navbat holati", callback_data="queue"),
        InlineKeyboardButton("🟩 📅 Taxminiy sana", callback_data="date"),
        InlineKeyboardButton("🟧 🔔 Kuzatuv holati", callback_data="monitor"),
        InlineKeyboardButton("🟩 👤 Mening ma’lumotlarim", callback_data="profile"),
    )
    menu.add(
        InlineKeyboardButton("⚙️ Yordam", callback_data="help")
    )
    return menu

# =========================
# MENU ACTIONS
# =========================
@dp.callback_query_handler(lambda c: c.data == "queue")
async def queue_status(callback: types.CallbackQuery):
    await callback.message.answer("📊 Sizning navbatingiz: *hisoblanmoqda*")

@dp.callback_query_handler(lambda c: c.data == "date")
async def expected_date(callback: types.CallbackQuery):
    await callback.message.answer("📅 Taxminiy sana: *aniqlanmoqda*")

@dp.callback_query_handler(lambda c: c.data == "monitor")
async def monitor_status(callback: types.CallbackQuery):
    await callback.message.answer("🔔 Kuzatuv faol holatda")

@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(callback: types.CallbackQuery):
    data = user_data.get(callback.from_user.id, {})
    text = (
        f"👤 *Profilingiz*\n\n"
        f"Ism: {data.get('first_name')}\n"
        f"Familiya: {data.get('last_name')}\n"
        f"Telefon: {data.get('phone')}"
    )
    await callback.message.answer(text, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_menu(callback: types.CallbackQuery):
    await callback.message.answer("ℹ️ Yordam bo‘limi (keyin to‘ldiriladi)")

# =========================
# START BOT
# =========================
if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)
