import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db, add_user, approve_user, reject_user, get_user
from states import RegisterState
from keyboards import rules_keyboard, phone_keyboard, admin_approve_keyboard, main_menu

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5266262372

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ================= START =================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "🔐 *XAVFSIZLIK VA BOT QOIDALARI*\n\n"
        "• Bot rasmiy elchixona emas\n"
        "• Ma’lumotlar tekshiruv uchun olinadi\n"
        "• Admin tasdiqlamaguncha davom etilmaydi\n\n"
        "Davom etish uchun rozilik bildiring 👇",
        parse_mode="Markdown",
        reply_markup=rules_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):
    await RegisterState.first_name.set()
    await callback.message.answer("✍️ Ismingizni kiriting:")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "decline")
async def decline(callback: types.CallbackQuery):
    await callback.message.answer("❌ Roziliksiz botdan foydalanib bo‘lmaydi.")
    await callback.answer()

# ================= REGISTRATION =================
@dp.message_handler(state=RegisterState.first_name)
async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await RegisterState.last_name.set()
    await message.answer("✍️ Familiyangizni kiriting:")

@dp.message_handler(state=RegisterState.last_name)
async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await RegisterState.phone.set()
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())

@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterState.phone)
async def phone(message: types.Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Faqat o‘zingizning raqamingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await RegisterState.passport.set()
    await message.answer("🛂 Pasport JPG yuklang (≤1MB):", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(content_types=types.ContentType.PHOTO, state=RegisterState.passport)
async def passport(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    if photo.file_size > 1_000_000:
        await message.answer("❌ Fayl 1MB dan katta.")
        return

    data = await state.get_data()
    user_payload = {
        "telegram_id": message.from_user.id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "phone": data["phone"],
        "passport": photo.file_id
    }

    await add_user(user_payload)
    await state.finish()

    await bot.send_message(
        ADMIN_ID,
        f"🆕 *Yangi foydalanuvchi*\n\n"
        f"{data['first_name']} {data['last_name']}\n"
        f"📞 {data['phone']}\n"
        f"🆔 {message.from_user.id}",
        parse_mode="Markdown",
        reply_markup=admin_approve_keyboard(message.from_user.id)
    )
    await bot.send_photo(ADMIN_ID, photo.file_id)

    await message.answer("⏳ Ma’lumotlaringiz admin tasdig‘iga yuborildi.")

# ================= ADMIN =================
@dp.callback_query_handler(lambda c: c.data.startswith("approve"))
async def approve(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[1])
    await approve_user(uid)
    await bot.send_message(uid, "✅ Tasdiqlandingiz!", reply_markup=main_menu())
    await callback.answer("Tasdiqlandi")

@dp.callback_query_handler(lambda c: c.data.startswith("reject"))
async def reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[1])
    await reject_user(uid)
    await bot.send_message(uid, "❌ Rad etildingiz.")
    await callback.answer("Rad etildi")

# ================= RUN =================
async def on_startup(dp):
    await init_db()
    print("✅ BOT ISHGA TUSHDI — FULL SYSTEM")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
