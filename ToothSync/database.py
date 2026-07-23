import sqlite3
import os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(__file__), "toothsync.db")


def connect():
    return sqlite3.connect(DATABASE)


def create_database():
    conn = connect()
    cursor = conn.cursor()

    # Patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        created_at TEXT
    )
    """)

    # Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        treatment TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',

        FOREIGN KEY(patient_id)
        REFERENCES patients(id)
    )
    """)

    conn.commit()
    
    # Seed initial sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        today = datetime.now().strftime("%Y-%m-%d")
        seed_patients = [
            ("Eleanor Vance", "(555) 234-5678", "eleanor.v@example.com", "123 Hill House", today),
            ("Marcus Brody", "(555) 987-6543", "marcus.b@museum.org", "456 Museum Way", today),
            ("Sarah Connor", "(555) 543-2109", "sconnor@cyberdyne.net", "789 Resistance Rd", today),
        ]
        for p in seed_patients:
            cursor.execute("""
                INSERT INTO patients (name, phone, email, address, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, p)
            patient_id = cursor.lastrowid
            
            if p[0] == "Eleanor Vance":
                cursor.execute("""
                    INSERT INTO appointments (patient_id, date, time, treatment, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, today, "09:00 AM", "Checkup", "High sensitivity in molars.", "completed"))
            elif p[0] == "Marcus Brody":
                cursor.execute("""
                    INSERT INTO appointments (patient_id, date, time, treatment, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, today, "11:00 AM", "Cleaning", "Regular scale and polish.", "pending"))
            elif p[0] == "Sarah Connor":
                cursor.execute("""
                    INSERT INTO appointments (patient_id, date, time, treatment, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, today, "02:00 PM", "Root Canal", "Dental anxiety — offer nitrous oxide.", "pending"))

        conn.commit()
    conn.close()


# -------------------------
# PATIENT FUNCTIONS
# -------------------------


def add_patient(name, phone, email="", address=""):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients
    (name, phone, email, address, created_at)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        name,
        phone,
        email,
        address,
        datetime.now().strftime("%Y-%m-%d")
    ))

    patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id


def get_patients():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    ORDER BY name
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def search_patients(query):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    WHERE name LIKE ?
    OR phone LIKE ?
    """,
    (
        f"%{query}%",
        f"%{query}%"
    ))

    data = cursor.fetchall()

    conn.close()

    return data


# -------------------------
# APPOINTMENT FUNCTIONS
# -------------------------


def add_appointment(
        patient_id,
        date,
        time,
        treatment,
        notes=""
):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments
    (
    patient_id,
    date,
    time,
    treatment,
    notes
    )

    VALUES (?, ?, ?, ?, ?)

    """,
    (
        patient_id,
        date,
        time,
        treatment,
        notes
    ))

    conn.commit()
    conn.close()


def get_today_appointments():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    appointments.id,
    patients.name,
    patients.phone,
    appointments.time,
    appointments.treatment,
    appointments.status

    FROM appointments

    JOIN patients
    ON patients.id = appointments.patient_id

    WHERE appointments.date=?

    ORDER BY appointments.time

    """,
    (today,))

    data = cursor.fetchall()

    conn.close()

    return data


def delete_appointment(id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM appointments WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()


def complete_appointment(id):
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE appointments
    SET status='completed'
    WHERE id=?
    """,
    (id,))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Database created and initialized successfully.")
