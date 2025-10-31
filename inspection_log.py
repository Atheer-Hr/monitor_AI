import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

def run_inspection_module(conn):
    c = conn.cursor()

    # تحميل أسماء الطلاب
    students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
    student_list = [s[0] for s in students]
    student_list.insert(0, "غير مرتبط")

    st.title("🕵️‍♀️ وحدة الجولات التفقدية")

    # ✅ تسجيل جولة
    st.subheader("➕ تسجيل جولة جديدة")
    date = st.date_input("تاريخ الجولة", value=datetime.today())
    location = st.selectbox("الموقع", ["فصل", "دورة مياه", "ساحة", "ممر", "مقصف", "مكتب إداري"])
    category = st.selectbox("نوع الملاحظة", ["نظافة", "سلوك", "سلامة", "لا توجد ملاحظات"])
    note = st.text_area("تفاصيل الملاحظة")
    related_student = st.selectbox("هل الملاحظة مرتبطة بطالب؟", student_list)
    submit = st.button("تسجيل الجولة")

    if submit:
        c.execute("INSERT INTO inspection_log (date, location, category, note, related_student) VALUES (?, ?, ?, ?, ?)",
                  (date.strftime("%Y-%m-%d"), location, category, note, related_student))
        conn.commit()

        if category != "لا توجد ملاحظات":
            alert_msg = f"📍 جولة في {location} بتاريخ {date.strftime('%Y-%m-%d')} - ملاحظة: {note}"
            c.execute("INSERT INTO alerts (student_name, date, source, message) VALUES (?, ?, ?, ?)",
                      (related_student if related_student != "غير مرتبط" else "", date.strftime("%Y-%m-%d"), "جولة", alert_msg))
            conn.commit()

            if related_student != "غير مرتبط":
                c.execute("INSERT INTO logs (student_name, date, category, note, severity) VALUES (?, ?, ?, ?, ?)",
                          (related_student, date.strftime("%Y-%m-%d"), "جولة", note, "تحتاج متابعة"))
                conn.commit()

        st.success("✅ تم تسجيل الجولة والملاحظات بنجاح")

    # ✅ عرض الجولات السابقة
    st.subheader("📋 عرض الجولات السابقة")
    inspections = c.execute("SELECT date, location, category, note, related_student FROM inspection_log ORDER BY date DESC").fetchall()
    for i in inspections:
        st.markdown(f"📅 {i[0]} | 📍 {i[1]} | 🗂️ {i[2]}")
        if i[4] and i[4] != "غير مرتبط":
            st.markdown(f"👤 الطالب: {i[4]}")
        st.write(f"✏️ {i[3]}")
        st.markdown("---")

    # ✅ تحليل حسب الموقع
    st.subheader("📊 تحليل الجولات حسب الموقع")
    stats = c.execute("SELECT location, COUNT(*) FROM inspection_log GROUP BY location").fetchall()
    if stats:
        df_stats = pd.DataFrame(stats, columns=["الموقع", "عدد الجولات"])
        st.bar_chart(df_stats.set_index("الموقع"))

    # ✅ توليد تقرير
    st.subheader("📤 توليد تقرير الجولات")
    if st.button("تحميل التقرير"):
        df = pd.read_sql("SELECT * FROM inspection_log", conn)
        df.to_excel("تقرير_الجولات.xlsx", index=False)
        with open("تقرير_الجولات.xlsx", "rb") as f:
            st.download_button("📥 تحميل التقرير", f, file_name="تقرير_الجولات.xlsx")
