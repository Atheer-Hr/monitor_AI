import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils import hash_password

# الاتصال بقاعدة البيانات
def run_dashboard_module(conn):
    c = conn.cursor()
# إعداد الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# تسجيل الدخول
if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")
    login_btn = st.sidebar.button("دخول")

    if login_btn and username and password:
        user = c.execute("SELECT role FROM users WHERE username = ? AND password_hash = ?",
                        (username, hash_password(password))).fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user[0]
            st.sidebar.success(f"✅ مرحبًا {username} ({user[0]})")
        else:
            st.sidebar.error("❌ بيانات الدخول غير صحيحة")
    st.stop()
else:
    st.sidebar.success(f"✅ مرحبًا {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.experimental_rerun()

# تغيير كلمة المرور
st.sidebar.title("🔑 تغيير كلمة المرور")
new_pass = st.sidebar.text_input("كلمة المرور الجديدة", type="password")
confirm_pass = st.sidebar.text_input("تأكيد كلمة المرور", type="password")
change_btn = st.sidebar.button("تغيير")

if change_btn and new_pass and confirm_pass:
    if new_pass == confirm_pass:
        c.execute("UPDATE users SET password_hash = ? WHERE username = ?",
                (hash_password(new_pass), st.session_state.username))
        conn.commit()
        st.sidebar.success("✅ تم تغيير كلمة المرور")
    else:
        st.sidebar.error("❌ كلمة المرور غير متطابقة")

# التبويبات
st.set_page_config(page_title="لوحة التحكم", layout="wide")
st.title("📊 لوحة التحكم الرئيسية")

tabs = st.tabs([
    "👩‍🎓 إدارة الطلاب",
    "📘 سجل الملاحظات",
    "🚌 وحدة الباص",
    "📆 الغياب",
    "🕵️‍♀️ الجولات",
    "📣 التنبيهات",
    "📈 التحليلات"
    "⚠️ التصعيدات الإدارية"
    "🎉 الأنشطة المدرسية"
    "📝 المهام اليومية"
])

# 👩‍🎓 إدارة الطلاب
with tabs[0]:
    st.subheader("👩‍🎓 إدارة الطلاب")
    name = st.text_input("اسم الطالب")
    class_name = st.selectbox("الصف الدراسي", ["تمهيدي", "أول", "ثاني", "ثالث", "رابع"])
    guardian_phone = st.text_input("رقم ولي الأمر")
    if st.button("إضافة الطالب"):
        try:
            c.execute("INSERT INTO students (name, class, guardian_phone) VALUES (?, ?, ?)", (name, class_name, guardian_phone))
            conn.commit()
            st.success("✅ تم إضافة الطالب")
        except:
            st.warning("⚠️ الطالب موجود مسبقًا")

    st.markdown("---")
    st.subheader("📋 قائمة الطلاب")
    students = c.execute("SELECT name, class, guardian_phone FROM students ORDER BY class, name").fetchall()
    df = pd.DataFrame(students, columns=["الاسم", "الصف", "رقم ولي الأمر"])
    st.dataframe(df, use_container_width=True)

# 📘 سجل الملاحظات
with tabs[1]:
    st.subheader("📘 سجل الملاحظات")
    students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
    student_list = [s[0] for s in students]
    student_name = st.selectbox("اختر الطالب", student_list)
    category = st.selectbox("نوع الملاحظة", ["سلوكية", "صحية"])
    note = st.text_area("وصف الملاحظة")
    if st.button("تسجيل الملاحظة"):
        severity = "تحتاج متابعة" if any(w in note for w in ['قلق', 'تعب', 'إغماء']) else "عادية"
        c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                (student_name, datetime.today().strftime("%Y-%m-%d"), category, note, severity))
        conn.commit()
        st.success("✅ تم التسجيل")

# 🚌 وحدة الباص
with tabs[2]:
    st.subheader("🚌 وحدة الباص")
    logs = c.execute("SELECT student_name, date, arrival_time, status FROM bus_log ORDER BY date DESC").fetchall()
    df = pd.DataFrame(logs, columns=["الطالب", "التاريخ", "وقت الوصول", "الحالة"])
    st.dataframe(df, use_container_width=True)

# 📆 الغياب
with tabs[3]:
    st.subheader("📆 الغياب")
    selected_class = st.selectbox("اختر الصف", ["تمهيدي", "أول", "ثاني", "ثالث", "رابع"])
    selected_date = st.date_input("اختر التاريخ")
    absences = c.execute("SELECT student_name, reason FROM absence_log WHERE class = ? AND date = ?",
                        (selected_class, selected_date.strftime("%Y-%m-%d"))).fetchall()
    if absences:
        df = pd.DataFrame(absences, columns=["الطالب", "السبب"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد حالات غياب مسجلة.")

# 🕵️‍♀️ الجولات
with tabs[4]:
    st.subheader("🕵️‍♀️ الجولات التفقدية")
    inspections = c.execute("SELECT date, location, category, note FROM inspection_log ORDER BY date DESC").fetchall()
    df = pd.DataFrame(inspections, columns=["التاريخ", "الموقع", "النوع", "الملاحظة"])
    st.dataframe(df, use_container_width=True)

# 📣 التنبيهات
with tabs[5]:
    st.subheader("📣 التنبيهات")
    alerts = c.execute("SELECT date, student_name, source, message FROM alerts ORDER BY date DESC").fetchall()
    df = pd.DataFrame(alerts, columns=["التاريخ", "الطالب", "المصدر", "الرسالة"])
    st.dataframe(df, use_container_width=True)

# 📈 التحليلات
with tabs[6]:
    st.subheader("📈 التحليل الشهري للغياب")
    selected_month = st.selectbox("الشهر", list(range(1, 13)))
    selected_year = st.selectbox("السنة", list(range(2023, datetime.today().year + 1)))
    month_str = f"{selected_month:02d}"
    year_str = str(selected_year)
    stats = c.execute('''SELECT class, COUNT(*) FROM absence_log
                    WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
                    GROUP BY class''', (month_str, year_str)).fetchall()
    if stats:
        df = pd.DataFrame(stats, columns=["الصف", "عدد الغياب"])
        st.bar_chart(df.set_index("الصف"))
    else:
        st.info("لا توجد بيانات لهذا الشهر.")
    st.subheader("📤 توليد تقرير Excel للغياب")
    if st.button("تحميل تقرير الغياب"):
        data = pd.read_sql("SELECT * FROM absence_log", conn)
        data.to_excel("تقرير_الغياب.xlsx", index=False)
        st.success("✅ تم توليد التقرير بنجاح")
        st.download_button("⬇️ تحميل تقرير الغياب", data=open("تقرير_الغياب.xlsx", "rb").read(), file_name="تقرير_الغياب.xlsx")

        # ⚠️ التصعيدات الإدارية
with tabs[7]:
    st.subheader("⚠️ التصعيدات الإدارية")

    escalations = c.execute('''
        SELECT id, date, student_name, message
        FROM alerts
        WHERE source = "تصعيد"
        ORDER BY date DESC
    ''').fetchall()

    if escalations:
        for esc in escalations:
            st.markdown(f"📅 {esc[1]} | 👤 {esc[2]}")
            st.write(f"{esc[3]}")
            if st.button(f"📤 إرسال إلى الإدارة - {esc[0]}"):
                # هنا يمكن ربطه بإرسال فعلي أو تسجيل الإجراء
                c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                        (esc[2], esc[1], "إدارة", f"📨 تم إرسال التصعيد رقم {esc[0]} إلى الإدارة"))
                conn.commit()
                st.success("✅ تم إرسال التصعيد إلى الإدارة")
            st.markdown("---")
    else:
        st.info("لا توجد حالات تصعيد مسجلة حاليًا.")

# 🎉 الأنشطة المدرسية
with tabs[8]:
    st.subheader("🎉 الأنشطة المدرسية")

    activities = c.execute('''
        SELECT id, date, title, type, location, target_group, description, participants
        FROM activity_log
        ORDER BY date DESC
    ''').fetchall()

    if activities:
        for a in activities:
            st.markdown(f"📅 {a[1]} | 🎯 {a[2]} | 🗂️ النوع: {a[3]}")
            st.markdown(f"📍 الموقع: {a[4]} | 👥 الفئة: {a[5]}")
            st.write(f"✏️ {a[6]}")
            if a[7]:
                st.markdown(f"👤 المشاركون: {a[7]}")

            # زر إرسال التقرير للإدارة
            if st.button(f"📤 إرسال إلى الإدارة - نشاط رقم {a[0]}"):
                alert_msg = f"📨 تقرير نشاط: {a[2]} ({a[3]}) بتاريخ {a[1]} في {a[4]} - تم إرساله للإدارة"
                c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                        ("", a[1], "نشاط إداري", alert_msg))
                conn.commit()
                st.success("✅ تم إرسال تقرير النشاط إلى الإدارة")

            st.markdown("---")
    else:
        st.info("لا توجد أنشطة مسجلة حتى الآن.")

    # تحليل حسب النوع
    st.subheader("📊 تحليل الأنشطة حسب النوع")
    stats = c.execute("SELECT type, COUNT(*) FROM activity_log GROUP BY type").fetchall()
    if stats:
        df_stats = pd.DataFrame(stats, columns=["النوع", "عدد الأنشطة"])
        st.bar_chart(df_stats.set_index("النوع"))

# 📝 المهام اليومية
with tabs[9]:
    st.subheader("📝 المهام اليومية")

    tasks = c.execute('''
        SELECT date, title, assigned_to, status, notes
        FROM task_log
        ORDER BY date DESC
    ''').fetchall()

    if tasks:
        df = pd.DataFrame(tasks, columns=["التاريخ", "المهمة", "المسؤول", "الحالة", "ملاحظات"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد مهام مسجلة حتى الآن.")

    # تحليل حسب الحالة
    st.subheader("📊 تحليل المهام حسب الحالة")
    stats = c.execute("SELECT status, COUNT(*) FROM task_log GROUP BY status").fetchall()
    if stats:
        df_stats = pd.DataFrame(stats, columns=["الحالة", "عدد المهام"])
        st.bar_chart(df_stats.set_index("الحالة"))
