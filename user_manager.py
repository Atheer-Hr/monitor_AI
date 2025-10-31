import streamlit as st
import sqlite3
from utils import hash_password

def run_user_manager_module(conn):
    c = conn.cursor()

    st.title("👥 إدارة المستخدمين")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    role = st.selectbox("الدور", ["مدير", "مشرفة", "معلمة", "موجهة طلابية"])
    add_btn = st.button("➕ إضافة مستخدم")

    if add_btn and username and password:
        try:
            c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                      (username, hash_password(password), role))
            conn.commit()
            st.success("✅ تم إضافة المستخدم")
        except:
            st.warning("⚠️ اسم المستخدم موجود مسبقًا")

    # عرض المستخدمين
    st.subheader("📋 قائمة المستخدمين")
    users = c.execute("SELECT username, role FROM users").fetchall()
    for u in users:
        st.markdown(f"👤 {u[0]} | 🎓 الدور: {u[1]}")
