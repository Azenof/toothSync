"""
test_friend_tests.py
Tests for appointment status updates, search/filtering, and patient directory.
"""

import sys
import unittest
from datetime import datetime

import unittest.mock as mock
sys.modules["tkinter"] = mock.MagicMock()
sys.modules["tkinter.ttk"] = mock.MagicMock()
sys.modules["tkinter.messagebox"] = mock.MagicMock()
sys.modules["tkinter.simpledialog"] = mock.MagicMock()

from toothsync import (
    make_record,
    filter_records,
    get_unique_patients,
)


class TestAppointmentStatusUpdates(unittest.TestCase):

    def setUp(self):
        self.records = [
            make_record(name="Alice", uid="a-1", status="pending"),
            make_record(name="Bob",   uid="b-2", status="pending"),
            make_record(name="Carol", uid="c-3", status="completed"),
        ]

    def _complete(self, rid):
        for r in self.records:
            if r["id"] == rid:
                r["status"] = "completed"

    def _delete(self, rid):
        self.records = [r for r in self.records if r["id"] != rid]

    def test_complete_changes_status(self):
        self._complete("a-1")
        rec = next(r for r in self.records if r["id"] == "a-1")
        self.assertEqual(rec["status"], "completed")

    def test_complete_does_not_affect_others(self):
        self._complete("a-1")
        rec = next(r for r in self.records if r["id"] == "b-2")
        self.assertEqual(rec["status"], "pending")

    def test_delete_removes_record(self):
        self._delete("b-2")
        ids = [r["id"] for r in self.records]
        self.assertTrue("b-2" not in ids)

    def test_delete_preserves_remaining(self):
        self._delete("b-2")
        self.assertEqual(len(self.records), 2)

    def test_delete_nonexistent_id_is_safe(self):
        self._delete("x-999")
        self.assertEqual(len(self.records), 3)

    def test_complete_already_completed_is_idempotent(self):
        self._complete("c-3")
        rec = next(r for r in self.records if r["id"] == "c-3")
        self.assertEqual(rec["status"], "completed")


class TestSearchAndFiltering(unittest.TestCase):

    def setUp(self):
        self.records = [
            make_record("Eleanor Vance", "(555) 234-5678", date="2026-06-20", treatment="Checkup",   uid="r1"),
            make_record("Marcus Brody",  "(555) 987-6543", date="2026-06-21", treatment="Cleaning",  uid="r2"),
            make_record("Sarah Connor",  "(555) 543-2109", date="2026-06-21", treatment="Root Canal", uid="r3"),
            make_record("Eleanor Smith", "(555) 000-0000", date="2026-06-22", treatment="Filling",   uid="r4"),
        ]

    def test_empty_query_returns_all(self):
        self.assertEqual(len(filter_records(self.records)), 4)

    def test_search_by_name(self):
        result = filter_records(self.records, query="eleanor")
        self.assertEqual(len(result), 2)

    def test_search_by_phone(self):
        result = filter_records(self.records, query="987")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["patientName"], "Marcus Brody")

    def test_search_case_insensitive(self):
        result = filter_records(self.records, query="SARAH")
        self.assertEqual(len(result), 1)

    def test_search_no_match_returns_empty(self):
        result = filter_records(self.records, query="xyz_no_match")
        self.assertEqual(result, [])

    def test_filter_by_date(self):
        result = filter_records(self.records, date_filter="2026-06-21")
        self.assertEqual(len(result), 2)

    def test_filter_by_treatment(self):
        result = filter_records(self.records, treatment_filter="Cleaning")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["patientName"], "Marcus Brody")

    def test_filter_all_treatments(self):
        result = filter_records(self.records, treatment_filter="All")
        self.assertEqual(len(result), 4)

    def test_combined_date_and_treatment_filter(self):
        result = filter_records(self.records, date_filter="2026-06-21", treatment_filter="Root Canal")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "r3")

    def test_results_sorted_by_date_then_time(self):
        result = filter_records(self.records)
        dates = [r["date"] for r in result]
        self.assertEqual(dates, sorted(dates))


class TestPatientDirectory(unittest.TestCase):

    def setUp(self):
        self.records = [
            make_record("Alice Green",  uid="1"),
            make_record("Alice Green",  uid="2"),
            make_record("Bob Martin",   uid="3"),
            make_record("alice green",  uid="4"),
        ]

    def test_deduplication_case_insensitive(self):
        patients = get_unique_patients(self.records)
        self.assertEqual(len(patients), 2)

    def test_visit_count_is_accurate(self):
        patients = get_unique_patients(self.records)
        self.assertEqual(patients["alice green"]["count"], 3)

    def test_single_patient_has_count_one(self):
        patients = get_unique_patients(self.records)
        self.assertEqual(patients["bob martin"]["count"], 1)

    def test_empty_records_returns_empty_directory(self):
        self.assertEqual(get_unique_patients([]), {})

    def test_patient_contact_info_preserved(self):
        patients = get_unique_patients(self.records)
        self.assertEqual(patients["alice green"]["phone"], "(555) 000-0001")


if __name__ == "__main__":
    unittest.main(verbosity=2)
