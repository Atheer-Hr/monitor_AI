import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, time
from bus_utils import check_status

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('school_system.db')
c = conn.cursor()

# إنشاء جدول إذا لم يكن موجودًا
c.execute('''CREATE TABLE IF NOT EXISTS bus_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    date TEXT,
    arrival_time TEXT,
    departure_time TEXT,
    status TEXT
)''')
conn.commit()

# تحميل أسماء الطلاب
students_df = pd.read_csv("students.csv")
student_list = students_df["اسم الطالب"].tolist()

# واجهة الإدخال
st.title("🚌 سجل حضور وانصراف طلاب الباص")

student_name = st.selectbox("اختر اسم الطالب", student_list)
date = st.date_input("التاريخ", value=datetime.today())
arrival_time = st.time_input("وقت الوصول", value=time(7, 30))
departure_time = st.time_input("وقت الانصراف", value=time(13, 0))
submit = st.button("تسجيل الحضور والانصراف")

if submit and student_name:
    status = check_status(arrival_time)
    c.execute("INSERT INTO bus_log (student_name, date, arrival_time, departure_time, status) VALUES (?, ?, ?, ?, ?)",
              (student_name, date.strftime("%Y-%m-%d"), arrival_time.strftime("%H:%M"), departure_time.strftime("%H:%M"), status))
    conn.commit()
    st.success(f"✅ تم تسجيل الطالب ({status})")

# عرض سجل طالب
st.subheader("📂 عرض سجل طالب في الباص")
search_name = st.selectbox("اختر اسم الطالب لعرض سجله", student_list)
if search_name:
    results = c.execute("SELECT date, arrival_time, departure_time, status FROM bus_log WHERE student_name = ?", (search_name,)).fetchall()
    for r in results:
        st.markdown(f"📅 {r[0]} | 🚪 وصول: {r[1]} | خروج: {r[2]} | 🟢 الحالة: {r[3]}")
        st.markdown("---")

# توليد تقرير
st.subheader("📤 توليد تقرير Excel")
if st.button("تحميل تقرير الباص"):
    from bus_report import generate_bus_report
    path = generate_bus_report()
    with open(path, "rb") as f:
        st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الباص.xlsx")

        from bus_utils import check_status, generate_alert

# سجل التنبيهات
c.execute('''CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    date TEXT,
    message TEXT
)''')
conn.commit()

# عند التسجيل
if submit and student_name:
    status = check_status(arrival_time)
    c.execute("INSERT INTO bus_log (student_name, date, arrival_time, departure_time, status) VALUES (?, ?, ?, ?, ?)",
              (student_name, date.strftime("%Y-%m-%d"), arrival_time.strftime("%H:%M"), departure_time.strftime("%H:%M"), status))
    conn.commit()

    # توليد التنبيه إذا متأخر
    if status == "متأخر":
        alert_msg = generate_alert(student_name, arrival_time)
        c.execute("INSERT INTO alerts (student_name, date, message) VALUES (?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), alert_msg))
        conn.commit()
        st.warning(alert_msg)
    else:
        st.success(f"✅ تم تسجيل الطالب ({status})")

        st.subheader("📣 التنبيهات اليومية")
alerts = c.execute("SELECT date, student_name, message FROM alerts ORDER BY date DESC").fetchall()
for a in alerts:
    st.markdown(f"📅 {a[0]} | 👤 {a[1]}")
    st.write(f"{a[2]}")
    st.markdown("---")

    # ربط بوحدة سجل الطالب
if status == "متأخر":
    note = "تأخر في الحضور عبر الباص"
    severity = "تحتاج متابعة"
    c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
              (student_name, date.strftime("%Y-%m-%d"), "سلوكية", note, severity))
    conn.commit()