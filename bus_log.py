import streamlit as st
import sqlite3
from datetime import datetime, time
from bus_utils import check_status, generate_alert
from bus_report import generate_bus_report

def run_bus_module(conn):
    c = conn.cursor()

    # إنشاء جدول الحضور والانصراف إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS bus_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        arrival_time TEXT,
        departure_time TEXT,
        status TEXT
    )''')

    # إنشاء جدول التنبيهات إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        source TEXT,
        message TEXT
    )''')

    conn.commit()

    # تحميل أسماء الطلاب من قاعدة البيانات
    students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
    student_list = [s[0] for s in students]

    st.title("🚌 سجل حضور وانصراف طلاب الباص")

    # واجهة الإدخال
    student_name = st.selectbox("اختر اسم الطالب", student_list)
    date = st.date_input("التاريخ", value=datetime.today())
    arrival_time = st.time_input("وقت الوصول", value=time(7, 30))
    departure_time = st.time_input("وقت الانصراف", value=time(13, 0))
    submit = st.button("تسجيل الحضور والانصراف")

    if submit and student_name:
        status = check_status(arrival_time)

        # حفظ السجل
        c.execute("INSERT INTO bus_log (student_name, date, arrival_time, departure_time, status) VALUES (?, ?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), arrival_time.strftime("%H:%M"), departure_time.strftime("%H:%M"), status))
        conn.commit()

        # توليد التنبيه إذا متأخر
        if status == "متأخر":
            alert_msg = generate_alert(student_name, arrival_time)
            c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                      (student_name, date.strftime("%Y-%m-%d"), "باص", alert_msg))
            conn.commit()
            st.warning(alert_msg)

            # ربط بسجل الطالب
            note = "تأخر في الحضور عبر الباص"
            severity = "تحتاج متابعة"
            c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                      (student_name, date.strftime("%Y-%m-%d"), "سلوكية", note, severity))
            conn.commit()
        else:
            st.success(f"✅ تم تسجيل الطالب ({status})")

    # عرض سجل طالب
    st.subheader("📂 عرض سجل طالب في الباص")
    search_name = st.selectbox("اختر اسم الطالب لعرض سجله", student_list, key="search_bus")
    if search_name:
        results = c.execute("SELECT date, arrival_time, departure_time, status FROM bus_log WHERE student_name = ?", (search_name,)).fetchall()
        for r in results:
            st.markdown(f"📅 {r[0]} | 🚪 وصول: {r[1]} | خروج: {r[2]} | 🟢 الحالة: {r[3]}")
            st.markdown("---")

    # توليد تقرير
    st.subheader("📤 توليد تقرير Excel")
    if st.button("تحميل تقرير الباص"):
        path = generate_bus_report()
        with open(path, "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الباص.xlsx")

    # عرض التنبيهات اليومية
    st.subheader("📣 التنبيهات اليومية")
    alerts = c.execute("SELECT date, student_name, message FROM alerts WHERE source = 'باص' ORDER BY date DESC").fetchall()
    for a in alerts:
        st.markdown(f"📅 {a[0]} | 👤 {a[1]}")
        st.write(f"{a[2]}")
        st.markdown("---")
