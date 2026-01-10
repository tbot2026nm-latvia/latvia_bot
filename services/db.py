import asyncpg
from config import DATABASE_URL

pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ Database ulandi")

async def create_user(tg_id, first, last, phone, passport):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
        VALUES ($1,$2,$3,$4,$5)
        """, tg_id, first, last, phone, passport)

async def get_pending_users():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='pending'")

async def set_status(tg_id, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET status=$1 WHERE telegram_id=$2", status, tg_id)
