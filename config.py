import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID is None:
    raise RuntimeError("ADMIN_ID environment variable is missing")
ADMIN_ID = int(ADMIN_ID)
