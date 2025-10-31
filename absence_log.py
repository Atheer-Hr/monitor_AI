import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from absence_report import generate_absence_report
from telegram_sender import send_telegram_message
from advisor_engine import analyze_student_profile

def run_absence_module(conn):
    c = conn.cursor()

    # ✅ إنشاء جدول الغياب إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS absence_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        class TEXT,
        reason TEXT
    )''')
    conn.commit()

    # تحميل الطلاب والصفوف
    students = c.execute("SELECT name, class FROM students ORDER BY class, name").fetchall()
    student_dict = {name: cls for name, cls in students}
    student_list = list(student_dict.keys())

    st.title("📆 وحدة تسجيل الغياب")

    # ✅ تصنيف الغياب حسب الكلمات المفتاحية
    def classify_absence(reason):
        reason = reason.lower()
        if any(word in reason for word in ['مرض', 'طوارئ', 'إغماء']):
            return 'صحي'
        elif any(word in reason for word in ['مشاغبة', 'رفض الحضور', 'هروب']):
            return 'سلوكي'
        else:
            return 'غير محدد'

    # ✅ توليد تنبيه تلقائي
    def generate_absence_alert(student_name, date, reason):
        return f"🔔 الطالب {student_name} غائب بتاريخ {date}، السبب: {reason}"

    # ➕ تسجيل غياب طالب
    st.subheader("➕ تسجيل غياب طالب")
    student_name = st.selectbox("اختر اسم الطالب", student_list)
    date = st.date_input("تاريخ الغياب", value=datetime.today())
    reason = st.text_area("سبب الغياب")
    submit = st.button("تسجيل الغياب")

    if submit and student_name:
        class_name = student_dict[student_name]
        absence_type = classify_absence(reason)

        # حفظ الغياب
        c.execute("INSERT INTO absence_log (student_name, date, class, reason) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), class_name, reason))
        conn.commit()

        # حفظ التنبيه
        alert_msg = generate_absence_alert(student_name, date.strftime("%Y-%m-%d"), reason)
        c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "غياب", alert_msg))
        conn.commit()

        # حفظ ملاحظة في سجل الطالب
        c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "غياب", reason, "تحتاج متابعة"))
        conn.commit()

        # إرسال تنبيه Telegram
        telegram_msg = f"📆 تنبيه: الطالب {student_name} غائب اليوم ({date.strftime('%Y-%m-%d')}). السبب: {reason}. الصف: {class_name}."
        send_telegram_message(telegram_msg)

        # حفظ تنبيه لولي الأمر بدون إرسال SMS
        guardian = c.execute("SELECT guardian_phone FROM students WHERE name = ?", (student_name,)).fetchone()
        guardian_phone = guardian[0] if guardian else "غير مسجل"

        parent_alert = f"📱 إشعار: الطالب {student_name} غائب اليوم ({date.strftime('%Y-%m-%d')}). السبب: {reason}. للتواصل: {guardian_phone}"
        c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                  (student_name, date.strftime("%Y-%m-%d"), "ولي الأمر", parent_alert))
        conn.commit()

        st.success("✅ تم تسجيل الغياب والتنبيه والملاحظة وإرسال الإشعارات بنجاح")

    # 📋 عرض الغياب حسب الصف والتاريخ
    st.subheader("📋 عرض الغياب حسب الصف والتاريخ")
    selected_class = st.selectbox("اختر الصف", sorted(set(student_dict.values())))
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
    st.subheader("📤 توليد تقرير Excel")
    if st.button("تحميل تقرير الغياب"):
        path = generate_absence_report()
        with open(path, "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الغياب.xlsx")

    # 📋 جدول الغياب حسب الصف والتاريخ
    st.subheader("📋 جدول الغياب حسب الصف والتاريخ")
    admin_class = st.selectbox("اختر الصف لعرض الجدول", sorted(set(student_dict.values())), key="admin_class")
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
    ORDER BY total DESC
    '''
    month_str = f"{selected_month:02d}"
    year_str = str(selected_year)
    monthly_stats = c.execute(monthly_query, (month_str, year_str)).fetchall()

    if monthly_stats:
        df_month = pd.DataFrame(monthly_stats, columns=["الصف", "عدد حالات الغياب"])
        st.bar_chart(df_month.set_index("الصف"))
    else:
        st.info("لا توجد بيانات غياب لهذا الشهر.")

    # 📣 تنبيهات موجهة لأولياء الأمور
    st.subheader("📣 تنبيهات موجهة لأولياء الأمور")
    alerts_query = '''
    SELECT date, student_name, message
    FROM alerts
    WHERE source = "ولي الأمر"
    ORDER BY date DESC
    '''
    alerts = c.execute(alerts_query).fetchall()

    for a in alerts:
        st.markdown(f"📅 {a[0]} | 👤 {a[1]}")
        st.write(f"{a[2]}")
        st.markdown("---")

    # 🧠 التحليل التربوي
    if st.button("🧠 عرض التحليل التربوي لهذا الطالب"):
        profile = analyze_student_profile(student_name, conn)
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
