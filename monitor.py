import requests
import time
import hashlib
import os

URL = "https://www.vfsglobal.com/en/individuals/index.html"  # hozircha test URL
CHECK_INTERVAL = 60  # soniya

STATE_FILE = "page_state.txt"

def get_page_hash():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    content = r.text
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_last_hash():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()

def save_hash(h):
    with open(STATE_FILE, "w") as f:
        f.write(h)

def monitor():
    print("🔍 Sahifa kuzatuvi boshlandi")
    last_hash = load_last_hash()

    while True:
        try:
            current_hash = get_page_hash()

            if last_hash and current_hash != last_hash:
                print("⚠️ O‘zgarish aniqlandi!")
                # bu joyda keyin botga xabar yuboramiz
                save_hash(current_hash)
                last_hash = current_hash

            elif not last_hash:
                save_hash(current_hash)
                last_hash = current_hash
                print("📌 Boshlang‘ich holat saqlandi")

        except Exception as e:
            print("Xatolik:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
