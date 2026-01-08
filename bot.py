import os
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 5266262372

if not BOT_TOKEN or not DATABASE_URL:
    raise RuntimeError("BOT_TOKEN yoki DATABASE_URL yo‘q")

# =====================
# BOT & DB
# =====================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = None

# =====================
# FSM
# =====================
class RegisterFSM(StatesGroup):
    rules = State()
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()

# =====================
# STARTUP
# =====================
async def on_startup(dp):
    global db
    db = await asyncpg.connect(DATABASE_URL)
    print("✅ DB connected")
    print("✅ BOT ISHGA TUSHDI")

# =====================
# /start
# =====================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Roziman", callback_data="agree"))
    await message.answer(
        "🔐 *Xavfsizlik va qoidalar*\n\n"
        "• Maʼlumotlaringiz himoyalanadi\n"
        "• Passport faqat tekshiruv uchun\n"
        "• Admin tasdiqlamaguncha bot yopiq\n\n"
        "Davom etish uchun rozilik bering 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await RegisterFSM.rules.set()

# =====================
# AGREE
# =====================
@dp.callback_query_handler(lambda c: c.data == "agree", state=RegisterFSM.rules)
async def agree(call: types.CallbackQuery):
    await call.message.answer("👤 Ismingizni kiriting:")
    await RegisterFSM.first_name.set()

# =====================
# FIRST NAME
# =====================
@dp.message_handler(state=RegisterFSM.first_name)
async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("👤 Familiyangizni kiriting:")
    await RegisterFSM.last_name.set()

# =====================
# LAST NAME
# =====================
@dp.message_handler(state=RegisterFSM.last_name)
async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=kb)
    await RegisterFSM.phone.set()

# =====================
# PHONE (CONTACT MAJBURIY)
# =====================
@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterFSM.phone)
async def phone(message: types.Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Faqat o‘zingizning raqamingizni yuboring")
        return

    await state.update_data(phone=message.contact.phone_number)
    await message.answer(
        "🛂 Passport JPG faylini yuboring (≤1MB)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await RegisterFSM.passport.set()

# =====================
# PASSPORT
# =====================
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=RegisterFSM.passport)
async def passport(message: types.Message, state: FSMContext):
    doc = message.document

    if not doc.mime_type.startswith("image/") or doc.file_size > 1_000_000:
        await message.answer("❌ JPG va 1MB dan oshmasligi kerak")
        return

    data = await state.get_data()

    try:
        await db.execute("""
            INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (telegram_id) DO NOTHING
        """,
            message.from_user.id,
            data["first_name"],
            data["last_name"],
            data["phone"],
            doc.file_id
        )
    except Exception as e:
        print("DB ERROR:", e)
        await message.answer("❌ Xatolik yuz berdi")
        return

    await state.finish()

    await message.answer("⏳ Maʼlumotlaringiz yuborildi. Admin tasdiqlashini kuting.")

    await bot.send_message(
        ADMIN_ID,
        f"🆕 *Yangi foydalanuvchi*\n\n"
        f"👤 {data['first_name']} {data['last_name']}\n"
        f"📱 {data['phone']}\n"
        f"🆔 {message.from_user.id}\n\n"
        f"/approve {message.from_user.id}\n"
        f"/reject {message.from_user.id}",
        parse_mode="Markdown"
    )

# =====================
# ADMIN COMMANDS
# =====================
@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.get_args())
    await db.execute("UPDATE users SET status='approved' WHERE telegram_id=$1", uid)
    await bot.send_message(uid, "✅ Admin tomonidan tasdiqlandingiz")

@dp.message_handler(commands=["reject"])
async def reject(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.get_args())
    await db.execute("UPDATE users SET status='rejected' WHERE telegram_id=$1", uid)
    await bot.send_message(uid, "❌ Admin tomonidan rad etildingiz")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
