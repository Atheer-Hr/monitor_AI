import streamlit as st
import sqlite3
import pandas as pd
from advisor_engine import analyze_student_profile

def run_advisor_module(conn):
    c = conn.cursor()

    students = c.execute("SELECT name FROM students ORDER BY name").fetchall()
    student_list = [s[0] for s in students]

    st.title("🧠 الوكيل الذكي التربوي")

    selected_student = st.selectbox("اختر الطالب لتحليل حالته", student_list)

    if selected_student:
        profile = analyze_student_profile(selected_student, conn)

        st.subheader(f"📊 تحليل تربوي للطالب: {selected_student}")
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

        # توليد تقرير Excel
        if st.button("📤 تحميل تقرير تربوي"):
            df = pd.DataFrame({
                "الطالب": [profile["student"]],
                "الغياب": [profile["absence"]],
                "الخطورة": [profile["risk"]],
                "التوصيات": ["؛ ".join(profile["recommendations"])]
            })
            df.to_excel("تقرير_تربوي.xlsx", index=False)
            with open("تقرير_تربوي.xlsx", "rb") as f:
                st.download_button("📥 تحميل التقرير", f, file_name="تقرير_تربوي.xlsx")
