import sqlite3

def create_db():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()

    # LOGIN TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    # STUDENT RECORD TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS academic_data(
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        full_name TEXT,
        gender TEXT,
        semester_score REAL,
        study_hours REAL,
        attendance REAL,
        prediction TEXT
    )""")

    conn.commit()
    conn.close()

create_db()
print("Database initialized successfully ✔")
