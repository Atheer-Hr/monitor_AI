import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('school_system.db')
c = conn.cursor()

# تحميل أسماء الطلاب
students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
student_list = [s[0] for s in students]

st.title("🎉 وحدة الأنشطة المدرسية")

# ✅ تسجيل نشاط جديد
st.subheader("➕ تسجيل نشاط مدرسي")

date = st.date_input("تاريخ النشاط", value=datetime.today())
title = st.text_input("عنوان النشاط")
activity_type = st.selectbox("نوع النشاط", ["إذاعة", "مسابقة", "رحلة", "حملة", "اجتماع", "أخرى"])
location = st.text_input("الموقع")
target_group = st.selectbox("الفئة المستهدفة", ["جميع الطلاب", "صف معين", "مجموعة محددة"])
description = st.text_area("وصف النشاط")
selected_participants = st.multiselect("الطلاب المشاركون", student_list)
submit = st.button("تسجيل النشاط")

if submit and title:
    participants_str = ", ".join(selected_participants)
    c.execute("INSERT INTO activity_log (date, title, type, location, target_group, description, participants) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (date.strftime("%Y-%m-%d"), title, activity_type, location, target_group, description, participants_str))
    conn.commit()

    # تنبيه داخلي
    alert_msg = f"🎉 نشاط جديد: {title} ({activity_type}) بتاريخ {date.strftime('%Y-%m-%d')} في {location}"
    c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
              ("", date.strftime("%Y-%m-%d"), "نشاط", alert_msg))
    conn.commit()

    st.success("✅ تم تسجيل النشاط والتنبيه بنجاح")

# ✅ عرض الأنشطة السابقة
st.subheader("📋 الأنشطة المسجلة")
activities = c.execute("SELECT date, title, type, location, target_group, description FROM activity_log ORDER BY date DESC").fetchall()
for a in activities:
    st.markdown(f"📅 {a[0]} | 🎯 {a[1]} | 🗂️ النوع: {a[2]}")
    st.markdown(f"📍 الموقع: {a[3]} | 👥 الفئة: {a[4]}")
    st.write(f"✏️ {a[5]}")
    st.markdown("---")

# ✅ تحليل حسب النوع
st.subheader("📊 تحليل الأنشطة حسب النوع")
stats = c.execute("SELECT type, COUNT(*) FROM activity_log GROUP BY type").fetchall()
if stats:
    df_stats = pd.DataFrame(stats, columns=["النوع", "عدد الأنشطة"])
    st.bar_chart(df_stats.set_index("النوع"))

# ✅ توليد تقرير
st.subheader("📤 توليد تقرير الأنشطة")
if st.button("تحميل التقرير"):
    df = pd.read_sql("SELECT * FROM activity_log", conn)
    df.to_excel("تقرير_الأنشطة.xlsx", index=False)
    with open("تقرير_الأنشطة.xlsx", "rb") as f:
        st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الأنشطة.xlsx")
