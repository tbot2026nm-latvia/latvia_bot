import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport TEXT,
            status TEXT DEFAULT 'pending'
        )
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            service TEXT,
            location TEXT,
            status TEXT DEFAULT 'waiting',
            last_checked TIMESTAMP,
            found BOOLEAN DEFAULT FALSE
        )
        """)

# USERS
async def create_user(**data):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
        """, data["telegram_id"], data["first_name"], data["last_name"], data["phone"], data["passport_file"])

async def update_user_status(uid, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET status=$1 WHERE telegram_id=$2", status, uid)

async def get_user(uid):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", uid)

# QUEUE
async def add_queue(uid, service, location):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO queue (user_id, service, location) VALUES ($1,$2,$3)", uid, service, location)

async def get_user_queue(uid):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM queue WHERE user_id=$1", uid)
