from datetime import datetime, timedelta

def analyze_student_profile(student_name, conn):
    c = conn.cursor()

    # ✅ إنشاء جدول الحالات الطارئة إذا لم يكن موجودًا
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        category TEXT,
        note TEXT,
        severity TEXT
    )''')
    conn.commit()


    today = datetime.today()
    last_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    # عدد الغياب آخر 30 يوم
    c.execute("SELECT COUNT(*) FROM absence_log WHERE student_name = ? AND date >= ?", (student_name, last_30))
    absence_count = c.fetchone()[0]

    # عدد الحالات الطارئة
    c.execute("SELECT type, COUNT(*) FROM emergency_log WHERE related_student = ? GROUP BY type", (student_name,))
    emergency_stats = dict(c.fetchall())

    # تصنيف الملاحظات
    c.execute("SELECT severity, COUNT(*) FROM logs WHERE student_name = ? GROUP BY severity", (student_name,))
    note_stats = dict(c.fetchall())

    # هل لديه تنبيهات تصعيد؟
    c.execute("SELECT COUNT(*) FROM alerts WHERE student_name = ? AND source = 'تصعيد'", (student_name,))
    escalations = c.fetchone()[0]

    # تحليل تربوي
    recommendations = []
    risk_level = "منخفضة"

    if absence_count >= 3:
        recommendations.append("📌 متابعة الغياب المتكرر والتواصل مع ولي الأمر")
        risk_level = "متوسطة"

    if "طارئة" in note_stats and note_stats["طارئة"] >= 2:
        recommendations.append("📌 جلسة إرشاد تربوي عاجلة")
        risk_level = "مرتفعة"

    if emergency_stats.get("سلوكية", 0) >= 2:
        recommendations.append("📌 تدخل سلوكي من المرشد الطلابي")
        risk_level = "مرتفعة"

    if escalations > 0:
        recommendations.append("📌 رفع الحالة للإدارة لاتخاذ إجراء رسمي")
        risk_level = "حرجة"

    return {
        "student": student_name,
        "absence": absence_count,
        "emergencies": emergency_stats,
        "notes": note_stats,
        "risk": risk_level,
        "recommendations": recommendations
    }
