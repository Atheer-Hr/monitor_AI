import streamlit as st
import sqlite3
import os
from init_db import initialize_database


# ✅ الاتصال بقاعدة البيانات الموحدة
conn = sqlite3.connect("school_system.db")

# ✅ إعداد واجهة التطبيق
st.set_page_config(page_title="نظام التنبيهات المدرسي الذكي", layout="wide")
st.sidebar.title("📚 قائمة الوحدات")

# ✅ اختيار الوحدة من القائمة الجانبية
page = st.sidebar.selectbox("اختر الوحدة", [
    "🏠 الصفحة الرئيسية",
    "📆 تسجيل الغياب",
    "🆘 الحالات الطارئة",
    "📘 سجل الملاحظات اليومية",
    "🚌 سجل الباص",
    "🧠 الوكيل الذكي التربوي",
    "🕵️‍♀️ الجولات التفقدية",
    "🎉 الأنشطة المدرسية",
    "📝 المهام اليومية",
    "👩‍🎓 إدارة بيانات الطلاب",
    "👥 إدارة المستخدمين",
    "📊 لوحة التحكم"
])

# ✅ توجيه حسب الوحدة المختارة
if page == "🏠 الصفحة الرئيسية":
    st.title("📚 نظام التنبيهات المدرسي الذكي")
    st.markdown("""
    مرحبًا بك في النظام الذكي لإدارة الغياب، الحالات الطارئة، الملاحظات، الباص، والتحليل التربوي.
    
    اختر الوحدة من القائمة الجانبية لبدء العمل.
    """)

elif page == "📆 تسجيل الغياب":
    from absence_log import run_absence_module
    run_absence_module(conn)

elif page == "🆘 الحالات الطارئة":
    from emergency_log import run_emergency_module
    run_emergency_module(conn)

elif page == "📘 سجل الملاحظات اليومية":
    from student_notes import run_notes_module
    run_notes_module(conn)

elif page == "🚌 سجل الباص":
    from bus_log import run_bus_module
    run_bus_module(conn)

elif page == "🧠 الوكيل الذكي التربوي":
    from advisor_dashboard import run_advisor_module
    run_advisor_module(conn)

elif page == "🕵️‍♀️ الجولات التفقدية":
    from inspection_log import run_inspection_module
    run_inspection_module(conn)

elif page == "🎉 الأنشطة المدرسية":
    from activity_log import run_activities_module
    run_activities_module(conn)

elif page == "📝 المهام اليومية":
    from task_log import run_task_module
    run_task_module(conn)

elif page == "👩‍🎓 إدارة بيانات الطلاب":
    from student_manager import run_student_module
    run_student_module(conn)

elif page == "👥 إدارة المستخدمين":
    from user_manager import run_user_module
    run_user_module(conn)

elif page == "📊 لوحة التحكم":
    from dashboard import run_dashboard_module
    run_dashboard_module(conn)
