"""
booking.py - Appointment Booking Screen for ToothSync KivyMD Application
"""

import sys
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


class BookingScreen(MDScreen):
    def __init__(self, **kwargs):
        self.today = datetime.now().strftime("%Y-%m-%d")
        super().__init__(**kwargs)
        self.dialog = None
        self.patient_menu = None
        self.treatment_menu = None
        self.time_menu = None
        self.selected_patient_id = None

    def on_enter(self, *args):
        self.setup_menus()

    def setup_menus(self):
        """Build dropdown menus for Patient selection, Treatment, and Time slots."""
        # Patient Menu
        patients = database.get_patients()
        if not patients:
            patient_items = [{
                "text": "No patients found (Type name below)",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.patient_menu.dismiss(),
            }]
        else:
            patient_items = [
                {
                    "text": f"{p[1]} (#{p[0]}) - {p[2]}",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=p: self.select_patient(x),
                }
                for p in patients
            ]
        
        if hasattr(self, "ids") and "patient_field" in self.ids:
            self.patient_menu = MDDropdownMenu(
                caller=self.ids.patient_field,
                items=patient_items,
                width_mult=4,
            )

        # Treatment Menu
        treatments = [
            "Checkup & Examination",
            "Scaling & Cleaning",
            "Root Canal Treatment",
            "Dental Fillings",
            "Tooth Extraction",
            "Teeth Whitening",
            "Crown & Bridge Installation",
            "Orthodontic Consultation"
        ]
        treatment_items = [
            {
                "text": t,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=t: self.select_treatment(x),
            }
            for t in treatments
        ]
        if hasattr(self, "ids") and "treatment_field" in self.ids:
            self.treatment_menu = MDDropdownMenu(
                caller=self.ids.treatment_field,
                items=treatment_items,
                width_mult=4,
            )

        # Time Menu
        times = ["09:00 AM", "10:00 AM", "11:00 AM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
        time_items = [
            {
                "text": tm,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=tm: self.select_time(x),
            }
            for tm in times
        ]
        if hasattr(self, "ids") and "time_field" in self.ids:
            self.time_menu = MDDropdownMenu(
                caller=self.ids.time_field,
                items=time_items,
                width_mult=4,
            )

    def open_patient_menu(self):
        self.setup_menus()
        if self.patient_menu:
            self.patient_menu.open()

    def select_patient(self, patient_row):
        # patient_row: (id, name, phone, email, address, created_at)
        self.selected_patient_id = patient_row[0]
        self.ids.patient_field.text = f"{patient_row[1]} (#{patient_row[0]})"
        if self.patient_menu:
            self.patient_menu.dismiss()

    def select_treatment(self, treatment_str):
        self.ids.treatment_field.text = treatment_str
        if self.treatment_menu:
            self.treatment_menu.dismiss()

    def select_time(self, time_str):
        self.ids.time_field.text = time_str
        if self.time_menu:
            self.time_menu.dismiss()

    def set_today_date(self):
        self.ids.date_field.text = datetime.now().strftime("%Y-%m-%d")

    def submit_booking(self):
        patient_str = self.ids.patient_field.text.strip()
        date_str = self.ids.date_field.text.strip()
        time_str = self.ids.time_field.text.strip()
        treatment_str = self.ids.treatment_field.text.strip()
        notes_str = self.ids.notes_field.text.strip()

        if not patient_str:
            self.show_dialog("Error", "Please select or type a patient name.")
            return

        if not date_str:
            self.show_dialog("Error", "Please enter a valid date (YYYY-MM-DD).")
            return

        if not time_str:
            self.show_dialog("Error", "Please select an appointment time slot.")
            return

        if not treatment_str:
            self.show_dialog("Error", "Please select a treatment type.")
            return

        # If patient_id is not set from dropdown, find or create patient by name
        if not self.selected_patient_id:
            patients = database.get_patients()
            matched = [p for p in patients if p[1].lower() == patient_str.lower()]
            if matched:
                self.selected_patient_id = matched[0][0]
            else:
                # Add new patient
                self.selected_patient_id = database.add_patient(patient_str, "(555) 000-0000")

        # Insert appointment into database
        database.add_appointment(
            patient_id=self.selected_patient_id,
            date=date_str,
            time=time_str,
            treatment=treatment_str,
            notes=notes_str
        )

        app = App.get_running_app()
        if hasattr(app, "dashboard_screen"):
            app.dashboard_screen.refresh_dashboard()

        self.show_dialog("Success", f"Appointment successfully scheduled for {patient_str} on {date_str} at {time_str}!", success=True)

    def show_dialog(self, title, text, success=False):
        def on_close(x):
            self.dialog.dismiss()
            if success:
                self.clear_fields()

        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=on_close
                )
            ]
        )
        self.dialog.open()

    def clear_fields(self):
        self.selected_patient_id = None
        self.ids.patient_field.text = ""
        self.ids.date_field.text = datetime.now().strftime("%Y-%m-%d")
        self.ids.time_field.text = "09:00 AM"
        self.ids.treatment_field.text = "Checkup & Examination"
        self.ids.notes_field.text = ""
