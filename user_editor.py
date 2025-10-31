import streamlit as st
import sqlite3
from utils import hash_password

conn = sqlite3.connect('school_system.db')
c = conn.cursor()

st.title("🛠️ تعديل بيانات المستخدمين")

# التحقق من صلاحية المستخدم الحالي
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 يجب تسجيل الدخول أولًا")
    st.stop()

if st.session_state.role not in ["مدير", "موجهة طلابية"]:
    st.warning("🚫 لا تملك صلاحية تعديل المستخدمين")
    st.stop()

# تحميل قائمة المستخدمين
users = c.execute("SELECT username FROM users ORDER BY username").fetchall()
user_list = [u[0] for u in users]

selected_user = st.selectbox("اختر مستخدم لتعديله", user_list)

# عرض بيانات المستخدم المحدد
user_data = c.execute("SELECT role FROM users WHERE username = ?", (selected_user,)).fetchone()
current_role = user_data[0] if user_data else ""

new_role = st.selectbox("تعديل الدور", ["مدير", "مشرفة", "معلمة", "موجهة طلابية"], index=["مدير", "مشرفة", "معلمة", "موجهة طلابية"].index(current_role))
new_password = st.text_input("كلمة مرور جديدة (اختياري)", type="password")

if st.button("💾 حفظ التعديلات"):
    if new_password:
        c.execute("UPDATE users SET role = ?, password_hash = ? WHERE username = ?",
                  (new_role, hash_password(new_password), selected_user))
    else:
        c.execute("UPDATE users SET role = ? WHERE username = ?",
                  (new_role, selected_user))
    conn.commit()
    st.success("✅ تم تحديث بيانات المستخدم بنجاح")
