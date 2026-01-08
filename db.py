import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

    async with db_pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport_file_id TEXT,
            status TEXT DEFAULT 'pending',
            queue_number INTEGER,
            expected_date DATE,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

async def add_user(data: dict):
    async with db_pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file_id)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
        """,
        data["telegram_id"],
        data["first_name"],
        data["last_name"],
        data["phone"],
        data["passport"]
        )

async def approve_user(telegram_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT MAX(queue_number) FROM users WHERE status='approved'")
        next_queue = (row[0] or 0) + 1

        await conn.execute("""
        UPDATE users
        SET status='approved',
            queue_number=$1,
            expected_date = CURRENT_DATE + ($1 / 20)
        WHERE telegram_id=$2
        """, next_queue, telegram_id)

async def reject_user(telegram_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET status='rejected' WHERE telegram_id=$1",
            telegram_id
        )

async def get_pending_users():
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='pending'")

async def get_user(telegram_id: int):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id=$1",
            telegram_id
        )
