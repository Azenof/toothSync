"""
database.py - Database access layer for ToothSync application using SQLite.
Includes chronological time sorting for 12-hour AM/PM appointment times.
"""

import sqlite3
import os
import shutil
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(__file__), "toothsync.db")

TIME_SORT_SQL = """
CASE
    WHEN appointments.time LIKE '%AM' THEN 
        CASE 
            WHEN CAST(substr(appointments.time, 1, 2) AS INTEGER) = 12 THEN 0 
            ELSE CAST(substr(appointments.time, 1, 2) AS INTEGER) 
        END
    WHEN appointments.time LIKE '%PM' THEN
        CASE 
            WHEN CAST(substr(appointments.time, 1, 2) AS INTEGER) = 12 THEN 12 
            ELSE CAST(substr(appointments.time, 1, 2) AS INTEGER) + 12 
        END
    ELSE 0
END ASC
"""


def connect():
    """Returns a sqlite3 connection to toothsync.db."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    """Creates SQLite tables if they do not exist."""
    conn = connect()
    cursor = conn.cursor()

    # Patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
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
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        treatment TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',

        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# PATIENT FUNCTIONS
# -------------------------

def add_patient(name, phone, email="", address=""):
    """Adds a new patient and returns the new patient_id."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients (name, phone, email, address, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
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


def update_patient(patient_id, name, phone, email="", address=""):
    """Updates an existing patient's details."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patients
    SET name = ?, phone = ?, email = ?, address = ?
    WHERE id = ?
    """, (name, phone, email, address, patient_id))

    conn.commit()
    conn.close()


def get_patients():
    """Fetches all registered patients ordered by name."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM patients ORDER BY name ASC
    """)

    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


def get_patient_by_id(patient_id):
    """Fetches a single patient record by ID."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return tuple(row) if row else None


def search_patients(query):
    """Searches patients by name, phone, or email."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM patients
    WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
    ORDER BY name ASC
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


# -------------------------
# APPOINTMENT FUNCTIONS
# -------------------------

def add_appointment(patient_id, date, time, treatment, notes=""):
    """Adds a new appointment for a patient."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments (patient_id, date, time, treatment, notes, status)
    VALUES (?, ?, ?, ?, ?, 'pending')
    """, (patient_id, date, time, treatment, notes))

    conn.commit()
    conn.close()


def get_today_appointments():
    """Fetches all appointments scheduled for today, sorted chronologically by time."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = connect()
    cursor = conn.cursor()

    query = f"""
    SELECT
        appointments.id,
        patients.name,
        patients.phone,
        appointments.date,
        appointments.time,
        appointments.treatment,
        appointments.notes,
        appointments.status,
        patients.id AS patient_id
    FROM appointments
    JOIN patients ON patients.id = appointments.patient_id
    WHERE appointments.date = ?
    ORDER BY {TIME_SORT_SQL}
    """

    cursor.execute(query, (today,))
    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


def get_upcoming_appointments():
    """Fetches all upcoming appointments (date >= today), sorted by date and time."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = connect()
    cursor = conn.cursor()

    query = f"""
    SELECT
        appointments.id,
        patients.name,
        patients.phone,
        appointments.date,
        appointments.time,
        appointments.treatment,
        appointments.notes,
        appointments.status,
        patients.id AS patient_id
    FROM appointments
    JOIN patients ON patients.id = appointments.patient_id
    WHERE appointments.date >= ?
    ORDER BY appointments.date ASC, {TIME_SORT_SQL}
    """

    cursor.execute(query, (today,))
    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


def get_all_appointments():
    """Fetches all appointments in system history, sorted by date DESC and time ASC."""
    conn = connect()
    cursor = conn.cursor()

    query = f"""
    SELECT
        appointments.id,
        patients.name,
        patients.phone,
        appointments.date,
        appointments.time,
        appointments.treatment,
        appointments.notes,
        appointments.status,
        patients.id AS patient_id
    FROM appointments
    JOIN patients ON patients.id = appointments.patient_id
    ORDER BY appointments.date DESC, {TIME_SORT_SQL}
    """

    cursor.execute(query)
    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


def get_patient_appointments(patient_id):
    """Fetches appointment history for a specific patient, sorted chronologically."""
    conn = connect()
    cursor = conn.cursor()

    query = f"""
    SELECT
        appointments.id,
        patients.name,
        patients.phone,
        appointments.date,
        appointments.time,
        appointments.treatment,
        appointments.notes,
        appointments.status,
        patients.id AS patient_id
    FROM appointments
    JOIN patients ON patients.id = appointments.patient_id
    WHERE appointments.patient_id = ?
    ORDER BY appointments.date DESC, {TIME_SORT_SQL}
    """

    cursor.execute(query, (patient_id,))
    data = [tuple(row) for row in cursor.fetchall()]
    conn.close()
    return data


def delete_appointment(id):
    """Deletes an appointment by ID."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def complete_appointment(id):
    """Marks an appointment status as completed."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET status = 'completed' WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def cancel_appointment(id):
    """Marks an appointment status as cancelled."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET status = 'cancelled' WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def backup_database(backup_dir=None):
    """Creates a timestamped backup copy of toothsync.db."""
    if not backup_dir:
        backup_dir = os.path.dirname(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"toothsync_backup_{timestamp}.db")
    shutil.copy2(DATABASE, backup_file)
    return backup_file


if __name__ == "__main__":
    create_database()
    print("ToothSync SQLite Database initialized cleanly with chronological time sorting.")
