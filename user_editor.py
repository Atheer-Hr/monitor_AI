import requests

# بيانات البوت
BOT_TOKEN = "8340128767:AAFRvnKcEC45W3As2N3MkRlDIC7-S6rFhDk"
CHAT_ID = -5072820543  # معرف مجموعة "الموجه الذكي"

def send_telegram_message(message):
    """
    ترسل رسالة نصية إلى مجموعة Telegram عبر البوت
    """
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
