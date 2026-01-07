import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# =====================
# CONFIG
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHECK_URL = "https://visa.vfsglobal.com/uzb/ru/lva/book-an-appointment"
CHECK_INTERVAL = 90  # soniya

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

# =====================
# BOT INIT
# =====================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =====================
# STORAGE (oddiy, RAM)
# =====================

users = {}        # user_id -> data
subscribers = set()

# =====================
# KEYBOARDS
# =====================

contact_kb = ReplyKeyboardMarkup(resize_keyboard=True)
contact_kb.add(
    KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)
)

# =====================
# START
# =====================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users[message.from_user.id] = {}
    await message.answer("👋 Ismingizni kiriting:")

# =====================
# REGISTRATION FLOW
# =====================

@dp.message_handler(lambda m: m.from_user.id in users and "name" not in users[m.from_user.id])
async def get_name(message: types.Message):
    users[message.from_user.id]["name"] = message.text
    await message.answer("👤 Familiyangizni kiriting:")

@dp.message_handler(lambda m: m.from_user.id in users and "surname" not in users[m.from_user.id])
async def get_surname(message: types.Message):
    users[message.from_user.id]["surname"] = message.text
    await message.answer(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=contact_kb
    )

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_contact(message: types.Message):
    uid = message.from_user.id
    users[uid]["phone"] = message.contact.phone_number
    subscribers.add(uid)

    await message.answer(
        "✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!\n\n"
        "🔔 Endi slot ochilishi avtomatik kuzatiladi.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# =====================
# MONITORING
# =====================

async def monitor():
    await asyncio.sleep(10)
    print(f"👀 Monitoring boshlandi: {CHECK_URL}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(CHECK_URL, allow_redirects=False) as resp:
                    location = resp.headers.get("Location", "")

                    # Agar login sahifaga tashlamasa → SLOT BOR
                    if "login" not in location.lower():
                        print("🚨 SLOT OCHILDI!")

                        for uid in subscribers:
                            try:
                                await bot.send_message(
                                    uid,
                                    "🚨 SLOT OCHILDI!\n\n"
                                    "👉 Tezda saytga kiring:\n"
                                    "https://visa.vfsglobal.com/uzb/ru/lva/book-an-appointment"
                                )
                            except:
                                pass

                        await asyncio.sleep(600)  # spam bo‘lmasin
            except Exception as e:
                print("Monitoring error:", e)

            await asyncio.sleep(CHECK_INTERVAL)

# =====================
# STARTUP
# =====================

async def on_startup(dp):
    asyncio.create_task(monitor())

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
