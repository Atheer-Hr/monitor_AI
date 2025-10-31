import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# إعدادات البوت
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# إعدادات أخرى مستقبلية
DB_PATH = os.getenv("DB_PATH", "school_system.db")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
