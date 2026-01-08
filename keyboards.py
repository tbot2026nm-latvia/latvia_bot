from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def rules_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Roziman", callback_data="agree"))
    kb.add(InlineKeyboardButton("❌ Rad etaman", callback_data="decline"))
    return kb

def phone_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))
    return kb

def admin_approve_keyboard(user_id: int):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🟢 Tasdiqlash", callback_data=f"approve:{user_id}"),
        InlineKeyboardButton("🔴 Rad etish", callback_data=f"reject:{user_id}")
    )
    return kb

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🟧 📊 Navbatim", callback_data="queue"),
        InlineKeyboardButton("🟩 📅 Taxminiy sana", callback_data="date"),
        InlineKeyboardButton("🟧 👤 Profil", callback_data="profile"),
        InlineKeyboardButton("🟩 ℹ️ Yordam", callback_data="help"),
    )
    return kb
