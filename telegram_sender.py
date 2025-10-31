import requests
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# قراءة البيانات من البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    """
    ترسل رسالة نصية إلى مجموعة Telegram عبر البوت
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ لم يتم العثور على بيانات البوت في البيئة")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        if result.get("ok"):
            print("✅ تم إرسال التنبيه بنجاح")
            return True
        else:
            print("❌ فشل في الإرسال:", result)
            return False
    except Exception as e:
        print("❌ خطأ في الاتصال:", e)
        return False
