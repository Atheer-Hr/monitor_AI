import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
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

def run_task_module(conn):
    c = conn.cursor()

    # إنشاء جدول المهام إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS task_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        title TEXT,
        assigned_to TEXT,
        status TEXT,
        notes TEXT
    )''')

    # إنشاء جدول الملاحظات إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        category TEXT,
        note TEXT,
        severity TEXT
    )''')

    conn.commit()

    # تحميل أسماء الطلاب
    students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
    student_list = [s[0] for s in students]
    student_list.insert(0, "غير مرتبط")

    st.title("📝 وحدة المهام اليومية")

    # ✅ تسجيل مهمة جديدة
    st.subheader("➕ تسجيل مهمة")
    date = st.date_input("تاريخ التنفيذ", value=datetime.today())
    title = st.text_input("عنوان المهمة")
    assigned_to = st.text_input("المسؤول عن التنفيذ")
    related_student = st.selectbox("هل المهمة مرتبطة بطالب؟", student_list)
    status = st.selectbox("الحالة", ["لم يبدأ", "جاري التنفيذ", "تم"])
    notes = st.text_area("ملاحظات إضافية")
    submit = st.button("تسجيل المهمة")

    if submit and title:
        c.execute("INSERT INTO task_log (date, title, assigned_to, status, notes) VALUES (?, ?, ?, ?, ?)",
                  (date.strftime("%Y-%m-%d"), title, assigned_to, status, notes))
        conn.commit()

        # إرسال تنبيه Telegram
        alert_msg = f"📝 مهمة جديدة: {title}\n📅 التاريخ: {date.strftime('%Y-%m-%d')}\n👤 المسؤول: {assigned_to}\n📌 الحالة: {status}"
        send_telegram_message(alert_msg)

        # ربط بسجل الطالب إذا مرتبط
        if related_student != "غير مرتبط":
            log_note = f"مهمة مرتبطة: {title} | ملاحظات: {notes}"
            c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                      (related_student, date.strftime("%Y-%m-%d"), "مهمة", log_note, "عادية"))
            conn.commit()

        st.success("✅ تم تسجيل المهمة والتنبيه وربطها بسجل الطالب")

    # ✅ عرض المهام حسب الحالة
    st.subheader("📋 عرض المهام حسب الحالة")
    selected_status = st.selectbox("اختر الحالة", ["جميع الحالات", "لم يبدأ", "جاري التنفيذ", "تم"])
    if selected_status == "جميع الحالات":
        tasks = c.execute("SELECT date, title, assigned_to, status, notes FROM task_log ORDER BY date DESC").fetchall()
    else:
        tasks = c.execute("SELECT date, title, assigned_to, status, notes FROM task_log WHERE status = ? ORDER BY date DESC", (selected_status,)).fetchall()

    if tasks:
        df = pd.DataFrame(tasks, columns=["التاريخ", "المهمة", "المسؤول", "الحالة", "ملاحظات"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد مهام بهذه الحالة.")

    # ✅ توليد تقرير
    st.subheader("📤 توليد تقرير المهام")
    if st.button("تحميل التقرير"):
        df = pd.read_sql("SELECT * FROM task_log", conn)
        df.to_excel("تقرير_المهام.xlsx", index=False)
        with open("تقرير_المهام.xlsx", "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_المهام.xlsx")
