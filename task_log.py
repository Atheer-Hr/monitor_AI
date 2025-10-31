import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

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

st.title("📝 وحدة المهام اليومية")

# ✅ تسجيل مهمة جديدة
st.subheader("➕ تسجيل مهمة")

date = st.date_input("تاريخ التنفيذ", value=datetime.today())
title = st.text_input("عنوان المهمة")
assigned_to = st.text_input("المسؤول عن التنفيذ")
status = st.selectbox("الحالة", ["لم يبدأ", "جاري التنفيذ", "تم"])
notes = st.text_area("ملاحظات إضافية")
submit = st.button("تسجيل المهمة")

if submit and title:
    c.execute("INSERT INTO task_log (date, title, assigned_to, status, notes) VALUES (?, ?, ?, ?, ?)",
              (date.strftime("%Y-%m-%d"), title, assigned_to, status, notes))
    conn.commit()
    st.success("✅ تم تسجيل المهمة")

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
