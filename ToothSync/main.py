"""
main.py - Main entry point for ToothSync KivyMD Application
"""

import sys
import os
from unittest.mock import MagicMock

# Fix for KivyMD 1.2.0 compatibility on Python 3.14 environment
if 'kivy.core.window.window_sdl2' not in sys.modules:
    try:
        import kivy.core.window.window_sdl2
    except ModuleNotFoundError:
        sys.modules['kivy.core.window.window_sdl2'] = MagicMock()
        sys.modules['kivy.core.window._window_sdl2'] = MagicMock()

from datetime import datetime

import kivy
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

# Import local screens and database
sys.path.insert(0, os.path.dirname(__file__))
import database
from screens.dashboard import DashboardScreen
from screens.booking import BookingScreen
from screens.patients import PatientsScreen

KV_STRING = """
#:import datetime datetime.datetime

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)

        # Header bar & Date
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(36)
            MDLabel:
                text: "ToothSync Dashboard"
                font_style: "H5"
                bold: True
                theme_text_color: "Primary"
            MDLabel:
                id: date_label
                text: "Today"
                font_style: "Subtitle2"
                theme_text_color: "Secondary"
                halign: "right"

        # Stats Cards Grid
        MDGridLayout:
            cols: 3
            spacing: dp(12)
            size_hint_y: None
            height: dp(76)

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [10, 10, 10, 10]
                elevation: 2
                md_bg_color: 0.9, 0.95, 1, 1
                MDLabel:
                    id: total_label
                    text: "0"
                    font_style: "H4"
                    bold: True
                    halign: "center"
                    theme_text_color: "Primary"
                MDLabel:
                    text: "Total Today"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [10, 10, 10, 10]
                elevation: 2
                md_bg_color: 1, 0.95, 0.9, 1
                MDLabel:
                    id: pending_label
                    text: "0"
                    font_style: "H4"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.9, 0.5, 0.1, 1
                MDLabel:
                    text: "Pending"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [10, 10, 10, 10]
                elevation: 2
                md_bg_color: 0.9, 1, 0.93, 1
                MDLabel:
                    id: completed_label
                    text: "0"
                    font_style: "H4"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.7, 0.3, 1
                MDLabel:
                    text: "Completed"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

        MDLabel:
            text: "Today's Schedule"
            font_style: "Subtitle1"
            bold: True
            size_hint_y: None
            height: dp(28)

        # Scrollable Appointments List
        MDScrollView:
            MDBoxLayout:
                id: appointments_container
                orientation: "vertical"
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height


<BookingScreen>:
    name: "booking"
    MDScrollView:
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(14)
            size_hint_y: None
            height: self.minimum_height

            MDLabel:
                text: "Book New Appointment"
                font_style: "H5"
                bold: True
                theme_text_color: "Primary"
                size_hint_y: None
                height: dp(36)

            MDTextField:
                id: patient_field
                hint_text: "Select Patient (or type name)"
                helper_text: "Tap to pick from registered patients"
                helper_text_mode: "on_focus"
                icon_right: "account-search"
                on_focus: if self.focus: root.open_patient_menu()

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(12)
                size_hint_y: None
                height: dp(60)

                MDTextField:
                    id: date_field
                    hint_text: "Date (YYYY-MM-DD)"
                    text: root.today
                    icon_right: "calendar"

                MDTextField:
                    id: time_field
                    hint_text: "Time Slot"
                    text: "09:00 AM"
                    icon_right: "clock-outline"
                    on_focus: if self.focus: root.time_menu.open()

            MDTextField:
                id: treatment_field
                hint_text: "Treatment Type"
                text: "Checkup"
                icon_right: "tooth-outline"
                on_focus: if self.focus: root.treatment_menu.open()

            MDTextField:
                id: notes_field
                hint_text: "Clinical Notes / Remarks (Optional)"
                multiline: True
                max_height: dp(100)
                icon_right: "note-text-outline"

            MDRaisedButton:
                text: "BOOK APPOINTMENT"
                icon: "calendar-check"
                font_style: "Button"
                size_hint_x: 1
                height: dp(48)
                on_release: root.submit_booking()


<PatientsScreen>:
    name: "patients"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)

        MDLabel:
            text: "Patient Directory"
            font_style: "H5"
            bold: True
            theme_text_color: "Primary"
            size_hint_y: None
            height: dp(32)

        # Search Bar
        MDTextField:
            id: search_field
            hint_text: "Search patients by name or phone..."
            icon_right: "magnify"
            size_hint_y: None
            height: dp(48)
            on_text: root.on_search(self.text)

        # Quick Add Patient Card
        MDCard:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(8)
            size_hint_y: None
            height: dp(190)
            radius: [10, 10, 10, 10]
            elevation: 2

            MDLabel:
                text: "Register New Patient"
                font_style: "Subtitle2"
                bold: True
                theme_text_color: "Primary"
                size_hint_y: None
                height: dp(20)

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(8)
                size_hint_y: None
                height: dp(40)
                MDTextField:
                    id: name_field
                    hint_text: "Full Name *"
                MDTextField:
                    id: phone_field
                    hint_text: "Phone *"

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(8)
                size_hint_y: None
                height: dp(40)
                MDTextField:
                    id: email_field
                    hint_text: "Email"
                MDTextField:
                    id: address_field
                    hint_text: "Address"

            MDRaisedButton:
                text: "ADD PATIENT"
                icon: "account-plus"
                size_hint_x: 1
                on_release: root.register_patient()

        MDLabel:
            text: "Registered Patients"
            font_style: "Subtitle1"
            bold: True
            size_hint_y: None
            height: dp(24)

        # Patient List
        MDScrollView:
            MDBoxLayout:
                id: patients_container
                orientation: "vertical"
                spacing: dp(8)
                size_hint_y: None
                height: self.minimum_height
"""


class ToothSyncApp(MDApp):
    def build(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.title = "ToothSync Dental Management"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        # Initialize SQLite database
        database.create_database()

        # Load KV layout string
        Builder.load_string(KV_STRING)

        # Root Bottom Navigation
        bottom_nav = MDBottomNavigation()

        # Dashboard Tab
        dash_item = MDBottomNavigationItem(
            name="tab_dashboard",
            text="Dashboard",
            icon="view-dashboard"
        )
        self.dashboard_screen = DashboardScreen()
        dash_item.add_widget(self.dashboard_screen)

        # Booking Tab
        book_item = MDBottomNavigationItem(
            name="tab_booking",
            text="Book",
            icon="calendar-plus"
        )
        self.booking_screen = BookingScreen()
        book_item.add_widget(self.booking_screen)

        # Patients Tab
        patient_item = MDBottomNavigationItem(
            name="tab_patients",
            text="Patients",
            icon="account-group"
        )
        self.patients_screen = PatientsScreen()
        patient_item.add_widget(self.patients_screen)

        bottom_nav.add_widget(dash_item)
        bottom_nav.add_widget(book_item)
        bottom_nav.add_widget(patient_item)

        return bottom_nav


if __name__ == "__main__":
    app = ToothSyncApp()
    app.run()
