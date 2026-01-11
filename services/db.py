import asyncpg
import os

DB_URL = os.getenv("DATABASE_URL")

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DB_URL)
    print("✅ Database ulandi")


# =========================
# CREATE USER
# =========================
async def create_user(telegram_id, first_name, last_name, phone, passport_file):
    query = """
    INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file, status)
    VALUES ($1, $2, $3, $4, $5, 'pending')
    ON CONFLICT (telegram_id) DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        phone = EXCLUDED.phone,
        passport_file = EXCLUDED.passport_file,
        status = 'pending'
    """
    async with pool.acquire() as conn:
        await conn.execute(
            query,
            telegram_id,
            first_name,
            last_name,
            phone,
            passport_file,
        )


# =========================
# UPDATE STATUS
# =========================
async def set_user_status(telegram_id, status):
    query = """
    UPDATE users
    SET status = $1
    WHERE telegram_id = $2
    """
    async with pool.acquire() as conn:
        await conn.execute(query, status, telegram_id)


# =========================
# GET USER
# =========================
async def get_user(telegram_id):
    query = "SELECT * FROM users WHERE telegram_id = $1"
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, telegram_id)


# =========================
# CHECK APPROVED
# =========================
async def is_approved(telegram_id):
    query = "SELECT status FROM users WHERE telegram_id = $1"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, telegram_id)
        if not row:
            return False
        return row["status"] == "approved"
