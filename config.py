import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CTA_URL   = os.getenv("CTA_URL",   "https://t.me/Katarina_t_s")
ADMIN_ID  = os.getenv("ADMIN_ID",  "")   # Telegram ID Катарины
