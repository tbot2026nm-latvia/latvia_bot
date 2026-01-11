import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

    # Users table
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport_file TEXT,
            status TEXT DEFAULT 'pending'
        )
        """)

        # Queue table
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


# =======================
# USERS
# =======================
async def create_user(telegram_id, first_name, last_name, phone, passport_file):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id, first_name, last_name, phone, passport_file)


async def update_user_status(user_id, status):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET status=$1 WHERE telegram_id=$2",
            status, user_id
        )


async def is_user_approved(user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT status FROM users WHERE telegram_id=$1", user_id
        )
        return row and row["status"] == "approved"


async def get_user(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id=$1", user_id
        )
