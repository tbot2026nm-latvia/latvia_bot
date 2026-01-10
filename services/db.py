import asyncpg
from config import DATABASE_URL

pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        passport_file TEXT,
        status TEXT DEFAULT 'pending'
    );
    """)
    print("✅ Database ulandi")

async def create_user(tg_id, first, last, phone, passport):
    await pool.execute("""
    INSERT INTO users(telegram_id, first_name, last_name, phone, passport_file)
    VALUES($1,$2,$3,$4,$5)
    ON CONFLICT (telegram_id) DO NOTHING
    """, tg_id, first, last, phone, passport)

async def get_pending():
    return await pool.fetch("SELECT * FROM users WHERE status='pending'")

async def approve(uid):
    await pool.execute("UPDATE users SET status='approved' WHERE telegram_id=$1", uid)

async def reject(uid):
    await pool.execute("DELETE FROM users WHERE telegram_id=$1", uid)
async def log_event(telegram_id, action):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO logs (telegram_id, action) VALUES ($1,$2)",
            telegram_id, action
        )

async def get_pending_users():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='pending'")

async def get_approved_users():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='approved'")

async def get_next_queue_number():
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT MAX(queue_number) FROM users")
        return (row[0] or 0) + 1

async def approve_user(user_id):
    async with pool.acquire() as conn:
        q = await get_next_queue_number()
        visit_date = "CURRENT_DATE + INTERVAL '1 day' * $1"
        await conn.execute(
            f"""
            UPDATE users 
            SET status='approved',
                queue_number=$1,
                visit_date={visit_date}
            WHERE telegram_id=$2
            """, q, user_id
        )
        return q
