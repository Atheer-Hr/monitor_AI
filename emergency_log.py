import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from telegram_sender import send_telegram_message
from advisor_engine import analyze_student_profile

def run_emergency_module(conn):
    c = conn.cursor()

    # ✅ إنشاء الجداول الضرورية
    c.execute('''CREATE TABLE IF NOT EXISTS emergency_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        location TEXT,
        description TEXT,
        related_student TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        source TEXT,
        message TEXT
    )''')

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

    st.title("🆘 وحدة الحالات الطارئة")

    # ✅ تسجيل حالة طارئة
    st.subheader("🚨 تسجيل حالة طارئة")
    date = st.date_input("تاريخ الحالة", value=datetime.today())
    emergency_type = st.selectbox("نوع الحالة", ["صحية", "سلوكية", "أمنية", "أخرى"])
    location = st.text_input("الموقع")
    description = st.text_area("وصف الحالة")
    related_student = st.selectbox("هل الحالة مرتبطة بطالب؟", student_list)
    submit = st.button("تسجيل الحالة")

    if submit:
        # حفظ الحالة
        c.execute("INSERT INTO emergency_log (date, type, location, description, related_student) VALUES (?, ?, ?, ?, ?)",
                  (date.strftime("%Y-%m-%d"), emergency_type, location, description, related_student))
        conn.commit()

        # تنبيه داخلي
        alert_msg = f"🚨 حالة طارئة ({emergency_type}) في {location} بتاريخ {date.strftime('%Y-%m-%d')} - {description}"
        c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                  (related_student if related_student != "غير مرتبط" else "", date.strftime("%Y-%m-%d"), "طارئة", alert_msg))
        conn.commit()

        # إرسال Telegram
        telegram_msg = f"🚨 حالة طارئة ({emergency_type}) في {location} بتاريخ {date.strftime('%Y-%m-%d')}\n👤 الطالب: {related_student if related_student != 'غير مرتبط' else 'غير محدد'}\n✏️ {description}"
        send_telegram_message(telegram_msg)

        # ربط بسجل الطالب
        if related_student != "غير مرتبط":
            c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                      (related_student, date.strftime("%Y-%m-%d"), "طارئة", description, "طارئة"))
            conn.commit()

        st.success("✅ تم تسجيل الحالة والتنبيه بنجاح")

        # التحقق من عدد الحالات السابقة لنفس الطالب
        if related_student != "غير مرتبط":
            count_query = '''SELECT COUNT(*) FROM emergency_log WHERE related_student = ? AND type = ?'''
            count = c.execute(count_query, (related_student, emergency_type)).fetchone()[0]

            if count >= 3:
                escalation_msg = f"⚠️ تصعيد: الطالب {related_student} لديه {count} حالات طارئة من نوع ({emergency_type}). يرجى التدخل الإداري."
                c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                          (related_student, date.strftime("%Y-%m-%d"), "تصعيد", escalation_msg))
                conn.commit()
                send_telegram_message(escalation_msg)

    # ✅ عرض الحالات السابقة
    st.subheader("📋 الحالات المسجلة")
    records = c.execute("SELECT date, type, location, description, related_student FROM emergency_log ORDER BY date DESC").fetchall()
    for r in records:
        st.markdown(f"📅 {r[0]} | 🧭 {r[2]} | 🗂️ {r[1]}")
        if r[4] and r[4] != "غير مرتبط":
            st.markdown(f"👤 الطالب: {r[4]}")
        st.write(f"✏️ {r[3]}")
        st.markdown("---")

    # ✅ تحليل حسب النوع
    st.subheader("📊 تحليل الحالات حسب النوع")
    stats = c.execute("SELECT type, COUNT(*) FROM emergency_log GROUP BY type").fetchall()
    if stats:
        df_stats = pd.DataFrame(stats, columns=["النوع", "عدد الحالات"])
        st.bar_chart(df_stats.set_index("النوع"))

    # ✅ توليد تقرير
    st.subheader("📤 توليد تقرير Excel")
    if st.button("تحميل التقرير"):
        df = pd.read_sql("SELECT * FROM emergency_log", conn)
        df.to_excel("تقرير_الحالات_الطارئة.xlsx", index=False)
        with open("تقرير_الحالات_الطارئة.xlsx", "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الحالات_الطارئة.xlsx")

    # ✅ التحليل التربوي
    if related_student != "غير مرتبط" and st.button("🧠 عرض التحليل التربوي للطالب المرتبط"):
        profile = analyze_student_profile(related_student, conn)
        with st.expander("📊 التحليل التربوي"):
            st.markdown(f"🔍 درجة الخطورة: **{profile['risk']}**")
            st.markdown(f"📆 عدد حالات الغياب (آخر 30 يوم): {profile['absence']}")
            st.markdown("🆘 الحالات الطارئة:")
            for k, v in profile["emergencies"].items():
                st.markdown(f"- {k}: {v}")
            st.markdown("📘 تصنيف الملاحظات:")
            for k, v in profile["notes"].items():
                st.markdown(f"- {k}: {v}")
            st.subheader("📌 التوصيات التربوية:")
            for rec in profile["recommendations"]:
                st.markdown(f"- {rec}")
