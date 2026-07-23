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
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog

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
        padding: dp(14)
        spacing: dp(10)

        # Mobile Clinic Header Card
        MDCard:
            orientation: "horizontal"
            padding: dp(12)
            spacing: dp(10)
            size_hint_y: None
            height: dp(68)
            radius: [14, 14, 14, 14]
            elevation: 2
            md_bg_color: 0.1, 0.45, 0.85, 1

            MDIconButton:
                icon: "tooth-outline"
                theme_icon_color: "Custom"
                icon_color: 1, 1, 1, 1
                user_font_size: "26sp"
                pos_hint: {"center_y": 0.5}

            MDBoxLayout:
                orientation: "vertical"
                pos_hint: {"center_y": 0.5}
                MDLabel:
                    text: "👋 Good Morning!"
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 0.9, 0.95, 1, 0.9
                MDLabel:
                    text: "ToothSync Dental Clinic"
                    font_style: "Subtitle1"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                MDLabel:
                    text: "Dr. Alex Vance, D.D.S."
                    font_style: "Overline"
                    theme_text_color: "Custom"
                    text_color: 0.95, 0.98, 1, 0.85

            MDLabel:
                id: date_label
                text: "Today"
                font_style: "Caption"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 0.95
                halign: "right"
                pos_hint: {"center_y": 0.5}

        # Filter Chips Bar (Today, Upcoming, All History)
        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(8)
            size_hint_y: None
            height: dp(34)

            MDRectangleFlatButton:
                text: "TODAY"
                font_style: "Caption"
                line_color: 0.1, 0.45, 0.85, 1
                text_color: 0.1, 0.45, 0.85, 1
                on_release: root.set_filter("today")

            MDRectangleFlatButton:
                text: "UPCOMING"
                font_style: "Caption"
                line_color: 0.4, 0.1, 0.7, 1
                text_color: 0.4, 0.1, 0.7, 1
                on_release: root.set_filter("upcoming")

            MDRectangleFlatButton:
                text: "HISTORY"
                font_style: "Caption"
                line_color: 0.3, 0.3, 0.3, 1
                text_color: 0.3, 0.3, 0.3, 1
                on_release: root.set_filter("all")

        # Mobile 2x2 Statistics Grid
        MDGridLayout:
            cols: 2
            spacing: dp(10)
            size_hint_y: None
            height: dp(130)

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [12, 12, 12, 12]
                elevation: 2
                md_bg_color: 0.9, 0.94, 1, 1
                MDLabel:
                    id: stat_today_label
                    text: "0"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Primary"
                MDLabel:
                    text: "Today's Appointments"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [12, 12, 12, 12]
                elevation: 2
                md_bg_color: 0.95, 0.9, 1, 1
                MDLabel:
                    id: stat_upcoming_label
                    text: "0"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.4, 0.1, 0.7, 1
                MDLabel:
                    text: "Upcoming Appointments"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [12, 12, 12, 12]
                elevation: 2
                md_bg_color: 0.9, 0.98, 0.93, 1
                MDLabel:
                    id: stat_completed_label
                    text: "0"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.65, 0.3, 1
                MDLabel:
                    text: "Completed Patients"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

            MDCard:
                orientation: "vertical"
                padding: dp(8)
                radius: [12, 12, 12, 12]
                elevation: 2
                md_bg_color: 1, 0.92, 0.92, 1
                MDLabel:
                    id: stat_cancelled_label
                    text: "0"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.85, 0.2, 0.2, 1
                MDLabel:
                    text: "Cancelled Appointments"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Secondary"

        MDLabel:
            id: filter_title_label
            text: "Today's Schedule"
            font_style: "Subtitle1"
            bold: True
            size_hint_y: None
            height: dp(24)

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
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            MDLabel:
                text: "Book Appointment"
                font_style: "H5"
                bold: True
                theme_text_color: "Primary"
                size_hint_y: None
                height: dp(32)

            MDCard:
                orientation: "vertical"
                padding: dp(14)
                spacing: dp(12)
                size_hint_y: None
                height: dp(410)
                radius: [14, 14, 14, 14]
                elevation: 2

                MDLabel:
                    text: "Patient Details"
                    font_style: "Subtitle2"
                    bold: True
                    theme_text_color: "Primary"
                    size_hint_y: None
                    height: dp(20)

                MDTextField:
                    id: patient_field
                    hint_text: "Select patient or type full name"
                    helper_text: "Tap to search registered patients"
                    helper_text_mode: "on_focus"
                    icon_right: "account-search"
                    on_focus: if self.focus: root.open_patient_menu()

                MDLabel:
                    text: "Appointment Details"
                    font_style: "Subtitle2"
                    bold: True
                    theme_text_color: "Primary"
                    size_hint_y: None
                    height: dp(20)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(54)

                    MDTextField:
                        id: date_field
                        hint_text: "Date (YYYY-MM-DD)"
                        text: root.today
                        icon_right: "calendar"
                        size_hint_x: 0.72

                    MDRaisedButton:
                        text: "TODAY"
                        size_hint_x: 0.28
                        on_release: root.set_today_date()

                MDTextField:
                    id: time_field
                    hint_text: "Time Slot"
                    text: "09:00 AM"
                    icon_right: "clock-outline"
                    on_focus: if self.focus: root.time_menu.open()

                MDTextField:
                    id: treatment_field
                    hint_text: "Treatment Procedure"
                    text: "Checkup & Examination"
                    icon_right: "tooth-outline"
                    on_focus: if self.focus: root.treatment_menu.open()

                MDTextField:
                    id: notes_field
                    hint_text: "Clinical Notes / Remarks (Optional)"
                    multiline: True
                    max_height: dp(70)
                    icon_right: "note-text-outline"

                MDRaisedButton:
                    text: "CONFIRM BOOKING"
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
        spacing: dp(10)

        MDLabel:
            text: "Patient Directory"
            font_style: "H5"
            bold: True
            theme_text_color: "Primary"
            size_hint_y: None
            height: dp(30)

        # Search Bar
        MDTextField:
            id: search_field
            hint_text: "Search patients by name, phone, or email..."
            icon_right: "magnify"
            size_hint_y: None
            height: dp(46)
            on_text: root.on_search(self.text)

        # Quick Register Patient Card
        MDCard:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(6)
            size_hint_y: None
            height: dp(180)
            radius: [12, 12, 12, 12]
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
                height: dp(38)
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
                height: dp(38)
                MDTextField:
                    id: email_field
                    hint_text: "Email Address"
                MDTextField:
                    id: address_field
                    hint_text: "Residential Address"

            MDRaisedButton:
                text: "REGISTER PATIENT"
                icon: "account-plus"
                size_hint_x: 1
                on_release: root.register_patient()

        MDLabel:
            text: "Registered Patients"
            font_style: "Subtitle1"
            bold: True
            size_hint_y: None
            height: dp(22)

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
        self.title = "ToothSync Dental Clinic"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Cyan"
        self.theme_cls.theme_style = "Light"

        # Initialize SQLite database schema
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

    def backup_database_action(self):
        try:
            backup_path = database.backup_database()
            self.show_dialog("Database Backup", f"Database backup successfully saved to:\n{backup_path}")
        except Exception as e:
            self.show_dialog("Backup Failed", str(e))

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()


if __name__ == "__main__":
    app = ToothSyncApp()
    app.run()
