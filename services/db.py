import asyncpg
from config import DATABASE_URL

db = None

async def connect_db():
    global db
    db = await asyncpg.create_pool(DATABASE_URL)

async def init_db():
    async with db.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport_file TEXT,
            status TEXT DEFAULT 'pending'
        )
        """)

async def add_user(tg_id, first, last, phone, passport):
    async with db.acquire() as conn:
        await conn.execute("""
            INSERT INTO users(telegram_id, first_name, last_name, phone, passport_file)
            VALUES($1,$2,$3,$4,$5)
            ON CONFLICT (telegram_id) DO NOTHING
        """, tg_id, first, last, phone, passport)

async def get_pending():
    async with db.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='pending'")

async def set_status(tg_id, status):
    async with db.acquire() as conn:
        await conn.execute("UPDATE users SET status=$1 WHERE telegram_id=$2", status, tg_id)

async def get_user(tg_id):
    async with db.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
