import streamlit as st
import sqlite3
import hashlib

def run_user_manager_module(conn):
    c = conn.cursor()

    # ✅ إنشاء جدول المستخدمين إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')
    conn.commit()

    st.title("👥 قائمة المستخدمين")

    # 📋 عرض المستخدمين الحاليين
    users = c.execute("SELECT username, role FROM users").fetchall()
    if users:
        for u in users:
            st.markdown(f"👤 {u[0]} | 🛡️ الدور: {u[1]}")
    else:
        st.info("لا يوجد مستخدمون مسجلون بعد.")

    # ➕ إضافة مستخدم جديد
    st.subheader("➕ إضافة مستخدم")
    new_username = st.text_input("اسم المستخدم الجديد")
    new_password = st.text_input("كلمة المرور", type="password")
    new_role = st.selectbox("الدور", ["مشرف", "معلم", "وكيل", "مرشد"])

    if st.button("إضافة المستخدم"):
        if new_username and new_password:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            try:
                c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          (new_username, password_hash, new_role))
                conn.commit()
                st.success("✅ تم إضافة المستخدم بنجاح")
            except sqlite3.IntegrityError:
                st.warning("⚠️ اسم المستخدم موجود مسبقًا")
        else:
            st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")

    # 🗑️ حذف مستخدم
    st.subheader("🗑️ حذف مستخدم")
    usernames = [u[0] for u in users]
    selected_user = st.selectbox("اختر المستخدم للحذف", usernames)
    if st.button("حذف المستخدم"):
        c.execute("DELETE FROM users WHERE username = ?", (selected_user,))
        conn.commit()
        st.success(f"🗑️ تم حذف المستخدم {selected_user}")
