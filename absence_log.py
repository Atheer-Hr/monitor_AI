import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from absence_report import generate_absence_report
from telegram_sender import send_telegram_message
from advisor_engine import analyze_student_profile

def run_absence_module(conn):
    c = conn.cursor()

    # ✅ إنشاء الجداول الضرورية
    c.execute('''CREATE TABLE IF NOT EXISTS absence_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        class TEXT,
        reason TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        source TEXT,
        message TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        class TEXT,
        stage TEXT,
        status TEXT,
        reason TEXT
    )''')

    conn.commit()

    st.title("📆 وحدة تسجيل الغياب")

    # تحميل الطلاب والصفوف
    students = c.execute("SELECT name, class, stage FROM students ORDER BY stage, class, name").fetchall()
    student_dict = {name: {"class": cls, "stage": stage} for name, cls, stage in students}
    student_list = list(student_dict.keys())

    # ✅ تصنيف الغياب حسب الكلمات المفتاحية
    def classify_absence(reason):
        reason = reason.lower()
        if any(word in reason for word in ['مرض', 'طوارئ', 'إغماء']):
            return 'صحي'
        elif any(word in reason for word in ['مشاغبة', 'رفض الحضور', 'هروب']):
            return 'سلوكي'
        else:
            return 'غير محدد'

    def generate_absence_alert(student_name, date, reason):
        return f"🔔 الطالب {student_name} غائب بتاريخ {date}، السبب: {reason}"

    # ➕ تسجيل غياب يدوي لطالب
    st.subheader("➕ تسجيل غياب يدوي لطالب")
    student_name = st.selectbox("اختر اسم الطالب", student_list)
    date = st.date_input("تاريخ الغياب", value=datetime.today())
    reason = st.text_area("سبب الغياب")
    submit = st.button("تسجيل الغياب")

    if submit and student_name:
        class_name = student_dict[student_name]["class"]
        absence_type = classify_absence(reason)

        c.execute("INSERT INTO absence_log (student_name, date, class, reason) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), class_name, reason))
        conn.commit()

        alert_msg = generate_absence_alert(student_name, date.strftime("%Y-%m-%d"), reason)
        c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "غياب", alert_msg))
        conn.commit()

        c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "غياب", reason, "تحتاج متابعة"))
        conn.commit()

        telegram_msg = f"📆 تنبيه: الطالب {student_name} غائب اليوم ({date.strftime('%Y-%m-%d')}). السبب: {reason}. الصف: {class_name}."
        send_telegram_message(telegram_msg)

        guardian = c.execute("SELECT guardian_phone FROM students WHERE name = ?", (student_name,)).fetchone()
        guardian_phone = guardian[0] if guardian else "غير مسجل"

        parent_alert = f"📱 إشعار: الطالب {student_name} غائب اليوم ({date.strftime('%Y-%m-%d')}). السبب: {reason}. للتواصل: {guardian_phone}"
        c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "ولي الأمر", parent_alert))
        conn.commit()

        st.success("✅ تم تسجيل الغياب والتنبيه والملاحظة وإرسال الإشعارات بنجاح")

    # ✅ تسجيل الحضور الجماعي حسب المرحلة والفصل
    st.subheader("🧾 تسجيل الحضور الجماعي")
    stages = sorted(set([info["stage"] for info in student_dict.values()]))
    selected_stage = st.selectbox("اختر المرحلة", stages)
    classes = sorted(set([info["class"] for info in student_dict.values() if info["stage"] == selected_stage]))
    selected_class = st.selectbox("اختر الصف", classes, key="attendance_class")
    attendance_date = st.date_input("تاريخ الحضور", key="attendance_date")

    filtered_students = [name for name, info in student_dict.items()
                         if info["class"] == selected_class and info["stage"] == selected_stage]

    attendance_data = {}
    for name in filtered_students:
        col1, col2 = st.columns([2, 3])
        with col1:
            status = st.selectbox(f"{name}", ["✅ حاضر", "❌ غائب"], key=f"status_{name}")
        with col2:
            reason = st.text_input(f"سبب الغياب ({name})", key=f"reason_{name}") if status == "❌ غائب" else ""
        attendance_data[name] = {"status": status, "reason": reason}

    if st.button("📌 تسجيل الحضور الجماعي"):
        for name, data in attendance_data.items():
            c.execute("INSERT INTO attendance_log (student_name, date, class, stage, status, reason) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, attendance_date.strftime("%Y-%m-%d"), selected_class, selected_stage, data["status"], data["reason"]))
        conn.commit()
        st.success("✅ تم تسجيل الحضور الجماعي بنجاح")

    # 📋 عرض الغياب حسب الصف والتاريخ
    st.subheader("📋 عرض الغياب حسب الصف والتاريخ")
    selected_class = st.selectbox("اختر الصف", sorted(set(student_dict[name]["class"] for name in student_list)))
    selected_date = st.date_input("اختر التاريخ لعرض الغياب")

    query = '''SELECT student_name, reason FROM absence_log WHERE class = ? AND date = ?'''
    results = c.execute(query, (selected_class, selected_date.strftime("%Y-%m-%d"))).fetchall()

    for r in results:
        st.markdown(f"👤 {r[0]} | 📄 السبب: {r[1]}")
        st.markdown("---")

    # 📈 تحليل إحصائي للغياب حسب الصف
    st.subheader("📈 تحليل الغياب حسب الصف")
    stats_query = '''SELECT date, COUNT(*) FROM absence_log WHERE class = ? GROUP BY date'''
    stats = c.execute(stats_query, (selected_class,)).fetchall()

    for s in stats:
        st.markdown(f"📅 {s[0]} | 👥 عدد الغياب: {s[1]}")

    # 📤 توليد تقرير Excel
    st.subheader("📤 تحميل تقرير الغياب")
    if st.button("تحميل تقرير الغياب"):
        path = generate_absence_report()
        with open(path, "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الغياب.xlsx")

    # 📋 جدول الغياب حسب الصف والتاريخ
    st.subheader("📋 جدول الغياب حسب الصف والتاريخ")
    admin_class = st.selectbox("اختر الصف لعرض الجدول", sorted(set(student_dict[name]["class"] for name in student_list)), key="admin_class")
    admin_date = st.date_input("اختر التاريخ", key="admin_date")

    admin_query = '''
    SELECT student_name, reason
    FROM absence_log
    WHERE class = ? AND date = ?
    ORDER BY student_name
    '''
    admin_results = c.execute(admin_query, (admin_class, admin_date.strftime("%Y-%m-%d"))).fetchall()

    if admin_results:
        df = pd.DataFrame(admin_results, columns=["اسم الطالب", "سبب الغياب"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد حالات غياب مسجلة لهذا اليوم.")

    # 📊 تحليل شهري للغياب
    st.subheader("📊 تحليل شهري للغياب")
    selected_month = st.selectbox("اختر شهرًا", list(range(1, 13)))
    selected_year = st.selectbox("اختر السنة", list(range(2023, datetime.today().year + 1)))

    monthly_query = '''
    SELECT class, COUNT(*) as total
    FROM absence_log
    WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
    GROUP BY class
