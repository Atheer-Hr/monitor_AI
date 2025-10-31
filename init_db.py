import sqlite3
import hashlib

def initialize_database():
    conn = sqlite3.connect("school_system.db")
    c = conn.cursor()

    # ✅ إنشاء الجداول
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        class TEXT,
        guardian_phone TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        category TEXT,
        note TEXT,
        severity TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bus_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        arrival_time TEXT,
        departure_time TEXT,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        source TEXT,
        message TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS absence_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        class TEXT,
        reason TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS inspection_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        location TEXT,
        category TEXT,
        note TEXT,
        related_student TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        title TEXT,
        type TEXT,
        location TEXT,
        target_group TEXT,
        description TEXT,
        participants TEXT
    )''')

    # ✅ إضافة بيانات تجريبية للطلاب (اختياري)
    sample_students = [
        ("محمد", "رابع", "0500000001"),
        ("سارة", "رابع", "0500000002"),
        ("خالد", "خامس", "0500000003")
    ]
    c.executemany("INSERT OR IGNORE INTO students (name, class, guardian_phone) VALUES (?, ?, ?)", sample_students)

    conn.commit()
    conn.close()
