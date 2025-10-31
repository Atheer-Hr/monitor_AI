import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from init_db import initialize_database
from advisor_engine import analyze_student_profile

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
if not os.path.exists("school_system.db"):
    initialize_database()

# الاتصال بقاعدة البيانات الموحدة
conn = sqlite3.connect('school_system.db')
c = conn.cursor()

# تحميل أسماء الطلاب من جدول students
students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
student_list = [s[0] for s in students]

# تصنيف ذكي بسيط حسب الكلمات المفتاحية
def classify_severity(note):
    note = note.lower()
    if any(word in note for word in ['إغماء', 'نزيف', 'طارئة', 'إسعاف']):
        return 'طارئة'
    elif any(word in note for word in ['صداع', 'تعب', 'انعزال', 'قلق']):
        return 'تحتاج متابعة'
    else:
        return 'عادية'

# واجهة الإدخال
st.title("📘 سجل الملاحظات اليومية للطلاب")

student_name = st.selectbox("اختر اسم الطالب", student_list)
category = st.selectbox("نوع الملاحظة", ["سلوكية", "صحية"])
note = st.text_area("وصف الملاحظة")
date = st.date_input("التاريخ", value=datetime.today())
submit = st.button("تسجيل الملاحظة")

if submit and student_name and note:
    severity = classify_severity(note)
    c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
              (student_name, date.strftime("%Y-%m-%d"), category, note, severity))
    conn.commit()
    st.success(f"✅ تم تسجيل الملاحظة ({severity}) بنجاح")

# عرض سجل طالب معين
st.subheader("📂 عرض سجل طالب")
search_name = st.selectbox("اختر اسم الطالب لعرض سجله", student_list)
if search_name:
    results = c.execute("SELECT date, category, note, severity FROM logs WHERE student_name = ?", (search_name,)).fetchall()
    for r in results:
        st.markdown(f"📅 {r[0]} | 🗂️ {r[1]} | 🔍 التصنيف: {r[3]}")
        st.write(f"✏️ {r[2]}")
        st.markdown("---")

# عرض الملاحظات حسب التصنيف
st.subheader("📊 عرض الملاحظات حسب التصنيف")
selected_severity = st.selectbox("اختر التصنيف", ["الكل", "عادية", "تحتاج متابعة", "طارئة"])

if selected_severity == "الكل":
    results = c.execute("SELECT * FROM logs").fetchall()
else:
    results = c.execute("SELECT * FROM logs WHERE severity = ?", (selected_severity,)).fetchall()

for r in results:
    st.markdown(f"👤 {r[1]} | 📅 {r[2]} | 🗂️ {r[3]} | 🔍 التصنيف: {r[5]}")
    st.write(f"✏️ {r[4]}")
    st.markdown("---")

# توليد تقرير Excel
st.subheader("📤 توليد تقرير Excel")
if st.button("تحميل التقرير"):
    data = pd.read_sql("SELECT * FROM logs", conn)
    data.to_excel("تقرير_الطلاب.xlsx", index=False)
    with open("تقرير_الطلاب.xlsx", "rb") as f:
        st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الطلاب.xlsx")


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
