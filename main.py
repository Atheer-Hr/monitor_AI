import streamlit as st
import os
import sqlite3
from init_db import initialize_database

# ✅ إنشاء قاعدة البيانات إذا لم تكن موجودة
if not os.path.exists("school_system.db"):
    initialize_database()

# ✅ الاتصال بقاعدة البيانات
conn = sqlite3.connect("school_system.db")

# ✅ إعداد القائمة الجانبية
st.sidebar.title("📚 قائمة الوحدات")
page = st.sidebar.selectbox("اختر الوحدة", [
    "🏠 الصفحة الرئيسية",
    "📆 تسجيل الغياب",
    "🆘 الحالات الطارئة",
    "📘 سجل الملاحظات",
    "🧠 الوكيل الذكي التربوي"
])

# ✅ توجيه حسب الوحدة المختارة
if page == "🏠 الصفحة الرئيسية":
    st.title("📚 نظام التنبيهات المدرسي الذكي")
    st.markdown("""
    مرحبًا بك في نظام التوجيه والارشاد الذكي
    
    يمكنك اختيار الوحدة التي ترغب في إدارتها من القائمة الجانبية.
    
    **الوحدات المتاحة:**
    - تسجيل الغياب
    - الحالات الطارئة
    - سجل الملاحظات
    - الوكيل الذكي التربوي (تحليل وتوصيات)
    """)
    
elif page == "📆 تسجيل الغياب":
    from absence import run_absence_module
    run_absence_module(conn)

elif page == "🆘 الحالات الطارئة":
    from emergency import run_emergency_module
    run_emergency_module(conn)

elif page == "📘 سجل الملاحظات":
    from student_notes import run_notes_module
    run_notes_module(conn)

elif page == "🧠 الوكيل الذكي التربوي":
    from advisor_dashboard import run_advisor_module
    run_advisor_module(conn)
