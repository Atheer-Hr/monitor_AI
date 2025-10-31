import sqlite3

def initialize_database():
    conn = sqlite3.connect("school_system.db")
    c = conn.cursor()

    # إنشاء جدول الطلاب
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            class TEXT,
            guardian_phone TEXT
        )
    ''')

    # إضافة بيانات تجريبية (اختياري)
    sample_students = [
        ("محمد", "رابع", "0500000001"),
        ("سارة", "رابع", "0500000002"),
        ("خالد", "خامس", "0500000003")
    ]
    c.executemany("INSERT INTO students (name, class, guardian_phone) VALUES (?, ?, ?)", sample_students)

    conn.commit()
    conn.close()
