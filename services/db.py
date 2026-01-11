import sqlite3

DB_NAME = "database.db"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        passport_file TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


async def create_user(telegram_id, first_name, last_name, phone, passport_file):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users 
    (telegram_id, first_name, last_name, phone, passport_file, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (telegram_id, first_name, last_name, phone, passport_file, "pending"))

    conn.commit()
    conn.close()


async def update_user_status(telegram_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET status=? WHERE telegram_id=?",
        (status, telegram_id)
    )

    conn.commit()
    conn.close()


async def get_user_status(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM users WHERE telegram_id=?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None
