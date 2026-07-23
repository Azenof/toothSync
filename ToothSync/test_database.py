"""
test_database.py - Unit tests for ToothSync SQLite database operations.
"""

import os
import unittest
import sys

sys.path.insert(0, os.path.dirname(__file__))

import database

class TestToothSyncDatabase(unittest.TestCase):

    def setUp(self):
        # Backup or use test database path
        database.DATABASE = os.path.join(os.path.dirname(__file__), "test_toothsync.db")
        if os.path.exists(database.DATABASE):
            os.remove(database.DATABASE)
        database.create_database()

    def tearDown(self):
        if os.path.exists(database.DATABASE):
            os.remove(database.DATABASE)

    def test_add_and_get_patients(self):
        pid = database.add_patient("Test Patient", "(555) 000-1111", "test@example.com", "123 Main St")
        self.assertIsNotNone(pid)
        patients = database.get_patients()
        names = [p[1] for p in patients]
        self.assertIn("Test Patient", names)

    def test_search_patients(self):
        database.add_patient("John Doe", "(555) 123-4567")
        results = database.search_patients("John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "John Doe")

    def test_add_and_get_today_appointments(self):
        pid = database.add_patient("Jane Doe", "(555) 999-8888")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        database.add_appointment(pid, today, "10:00 AM", "Cleaning", "Regular checkup")
        
        appts = database.get_today_appointments()
        self.assertTrue(any(a[1] == "Jane Doe" for a in appts))

    def test_complete_and_delete_appointment(self):
        pid = database.add_patient("Alice Smith", "(555) 777-6666")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        database.add_appointment(pid, today, "03:00 PM", "Fillings")
        
        appts = database.get_today_appointments()
        app_id = [a[0] for a in appts if a[1] == "Alice Smith"][0]
        
        database.complete_appointment(app_id)
        appts_after_complete = database.get_today_appointments()
        completed_appt = [a for a in appts_after_complete if a[0] == app_id][0]
        self.assertEqual(completed_appt[5], "completed")

        database.delete_appointment(app_id)
        appts_after_delete = database.get_today_appointments()
        self.assertFalse(any(a[0] == app_id for a in appts_after_delete))

if __name__ == "__main__":
    unittest.main()
