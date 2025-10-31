import streamlit as st
import sqlite3

# الاتصال بقاعدة البيانات الموحدة
conn = sqlite3.connect('school_system.db')
c = conn.cursor()

# إنشاء جدول الطلاب إذا لم يكن موجودًا
c.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    class TEXT,
    guardian_phone TEXT
)''')
conn.commit()

st.title("👩‍🎓 إدارة بيانات الطلاب")

# ➕ إضافة طالب جديد
st.subheader("➕ إضافة طالب")
name = st.text_input("اسم الطالب")
class_name = st.selectbox("الصف الدراسي", ["تمهيدي", "أول", "ثاني", "ثالث", "رابع"])
guardian_phone = st.text_input("رقم ولي الأمر")
add_btn = st.button("إضافة الطالب")

if add_btn and name and guardian_phone:
    try:
        c.execute("INSERT INTO students (name, class, guardian_phone) VALUES (?, ?, ?)", (name, class_name, guardian_phone))
        conn.commit()
        st.success("✅ تم إضافة الطالب بنجاح")
    except sqlite3.IntegrityError:
        st.warning("⚠️ الطالب موجود مسبقًا")

# 📋 عرض الطلاب الحاليين
st.subheader("📋 قائمة الطلاب")
students = c.execute("SELECT id, name, class, guardian_phone FROM students ORDER BY class, name").fetchall()
for s in students:
    st.markdown(f"🆔 {s[0]} | 👤 {s[1]} | 🏫 الصف: {s[2]} | 📞 ولي الأمر: {s[3]}")

# 🗑️ حذف طالب
st.subheader("🗑️ حذف طالب")
student_names = [s[1] for s in students]
selected_to_delete = st.selectbox("اختر الطالب للحذف", student_names)
delete_btn = st.button("حذف الطالب")

if delete_btn:
    c.execute("DELETE FROM students WHERE name = ?", (selected_to_delete,))
    conn.commit()
    st.success(f"🗑️ تم حذف الطالب {selected_to_delete}")

# ✏️ تعديل بيانات طالب
st.subheader("✏️ تعديل بيانات طالب")
selected_to_edit = st.selectbox("اختر الطالب للتعديل", student_names)
new_name = st.text_input("الاسم الجديد", value=selected_to_edit)
new_class = st.selectbox("الصف الجديد", ["تمهيدي", "أول", "ثاني", "ثالث", "رابع"])
new_phone = st.text_input("رقم ولي الأمر الجديد")

edit_btn = st.button("تعديل البيانات")

if edit_btn and new_name and new_phone:
    c.execute("UPDATE students SET name = ?, class = ?, guardian_phone = ? WHERE name = ?",
              (new_name, new_class, new_phone, selected_to_edit))
    conn.commit()
    st.success(f"✏️ تم تعديل بيانات الطالب {selected_to_edit}")