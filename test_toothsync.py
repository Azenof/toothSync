"""
Tests for data persistence and booking validation in ToothSync.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime

import unittest.mock as mock
sys.modules["tkinter"] = mock.MagicMock()
sys.modules["tkinter.ttk"] = mock.MagicMock()
sys.modules["tkinter.messagebox"] = mock.MagicMock()
sys.modules["tkinter.simpledialog"] = mock.MagicMock()

from toothsync import (
    TREATMENTS,
    TIMES,
    load_file,
    save_file,
    make_record,
    validate_booking,
)


class TestDataPersistence(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.path = self.tmp.name
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.path)

    def test_save_and_load_empty(self):
        save_file(self.path, [])
        self.assertEqual(load_file(self.path), [])

    def test_save_and_load_single_record(self):
        rec = make_record(name="Alice Smith", uid="u-1")
        save_file(self.path, [rec])
        loaded = load_file(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["patientName"], "Alice Smith")

    def test_save_multiple_records_preserves_order(self):
        recs = [make_record(name=f"Patient {i}", uid=f"u-{i}") for i in range(5)]
        save_file(self.path, recs)
        loaded = load_file(self.path)
        self.assertEqual([r["patientName"] for r in loaded],
                         [r["patientName"] for r in recs])

    def test_all_fields_persisted(self):
        rec = make_record(name="Bob Jones", phone="(555) 111-2222",
                          email="bob@clinic.com", date="2026-07-01",
                          time="10:00 AM", treatment="Root Canal",
                          notes="Nervous patient", status="pending", uid="u-99")
        save_file(self.path, [rec])
        loaded = load_file(self.path)[0]
        self.assertEqual(loaded["patientName"], "Bob Jones")
        self.assertEqual(loaded["phone"],       "(555) 111-2222")
        self.assertEqual(loaded["email"],       "bob@clinic.com")
        self.assertEqual(loaded["date"],        "2026-07-01")
        self.assertEqual(loaded["time"],        "10:00 AM")
        self.assertEqual(loaded["treatment"],   "Root Canal")
        self.assertEqual(loaded["notes"],       "Nervous patient")
        self.assertEqual(loaded["status"],      "pending")

    def test_overwrite_existing_file(self):
        save_file(self.path, [make_record(uid="old")])
        save_file(self.path, [make_record(uid="new1"), make_record(uid="new2")])
        loaded = load_file(self.path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["id"], "new1")


class TestBookingValidation(unittest.TestCase):

    GOOD = dict(name="Jane Doe", phone="(555) 123-4567",
                email="jane@example.com", date="2026-08-15",
                time="09:00 AM", treatment="Cleaning")

    def _v(self, **overrides):
        args = {**self.GOOD, **overrides}
        return validate_booking(**args)

    def test_valid_booking_has_no_errors(self):
        self.assertEqual(self._v(), [])

    def test_missing_name_fails(self):
        self.assertTrue(any("Name" in e for e in self._v(name="")))

    def test_missing_phone_fails(self):
        self.assertTrue(any("Phone" in e for e in self._v(phone="")))

    def test_missing_email_fails(self):
        self.assertTrue(any("Email" in e for e in self._v(email="")))

    def test_missing_date_fails(self):
        self.assertTrue(any("Date" in e for e in self._v(date="")))

    def test_unselected_time_fails(self):
        self.assertTrue(any("Time" in e for e in self._v(time="Select Time *")))

    def test_unselected_treatment_fails(self):
        self.assertTrue(any("Treatment" in e for e in self._v(treatment="Select Treatment *")))

    def test_invalid_date_format_fails(self):
        self.assertTrue(any("YYYY-MM-DD" in e for e in self._v(date="06/21/2026")))

    def test_invalid_date_format_text_fails(self):
        self.assertTrue(any("YYYY-MM-DD" in e for e in self._v(date="tomorrow")))

    def test_whitespace_name_fails(self):
        self.assertTrue(len(self._v(name="   ")) > 0)

    def test_multiple_missing_fields_returns_multiple_errors(self):
        errors = self._v(name="", phone="", email="")
        self.assertTrue(len(errors) >= 3)


class TestTreatmentAndTimeLists(unittest.TestCase):

    def test_all_expected_treatments_present(self):
        expected = {"Cleaning", "Checkup", "Extraction", "Root Canal", "Filling", "Orthodontic"}
        self.assertEqual(set(TREATMENTS), expected)

    def test_time_slots_cover_business_hours(self):
        self.assertTrue("08:00 AM" in TIMES)
        self.assertTrue("05:00 PM" in TIMES)
        self.assertEqual(len(TIMES), 10)

    def test_no_duplicate_treatments(self):
        self.assertEqual(len(TREATMENTS), len(set(TREATMENTS)))

    def test_no_duplicate_times(self):
        self.assertEqual(len(TIMES), len(set(TIMES)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
