"""
patients.py - Patient Directory and Detailed Profile Screen for ToothSync
"""

import sys
import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


class PatientsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_dialog = None
        Clock.schedule_once(lambda dt: self.refresh_patient_list(), 0)

    def on_enter(self, *args):
        self.refresh_patient_list()

    def refresh_patient_list(self, query=None):
        if not hasattr(self, "ids") or "patients_container" not in self.ids:
            return

        container = self.ids.patients_container
        container.clear_widgets()

        if query:
            patients = database.search_patients(query)
        else:
            patients = database.get_patients()

        if not patients:
            empty_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                size_hint_y=None,
                height=dp(70),
                radius=[12, 12, 12, 12],
                elevation=1
            )
            empty_card.add_widget(MDLabel(text="No registered patients found.", halign="center", theme_text_color="Hint"))
            container.add_widget(empty_card)
            return

        for p in patients:
            # Tuple: (id, name, phone, email, address, created_at)
            p_id, p_name, p_phone, p_email, p_address, p_created = p

            card = MDCard(
                orientation="vertical",
                padding=dp(12),
                spacing=dp(4),
                size_hint_y=None,
                height=dp(115),
                radius=[12, 12, 12, 12],
                elevation=2,
                line_color=(0.88, 0.88, 0.88, 1)
            )

            title_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
            avatar = MDIconButton(
                icon="account",
                theme_icon_color="Custom",
                icon_color=(0.1, 0.45, 0.85, 1),
                user_font_size="20sp",
                size_hint_x=None,
                width=dp(24),
                pos_hint={"center_y": 0.5}
            )
            name_lbl = MDLabel(text=p_name, font_style="Subtitle1", bold=True, size_hint_x=0.7, pos_hint={"center_y": 0.5})
            id_lbl = MDLabel(text=f"ID: #{p_id}", font_style="Caption", theme_text_color="Hint", size_hint_x=0.3, halign="right", pos_hint={"center_y": 0.5})
            title_box.add_widget(avatar)
            title_box.add_widget(name_lbl)
            title_box.add_widget(id_lbl)

            contact_lbl = MDLabel(
                text=f"📞 {p_phone or 'N/A'}   |   ✉️ {p_email or 'N/A'}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )

            addr_lbl = MDLabel(
                text=f"📍 {p_address or 'No address registered'}  |  Registered: {p_created or 'N/A'}",
                font_style="Overline",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(18)
            )

            # Action buttons row
            btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(30))
            
            history_btn = MDRectangleFlatButton(
                text="HISTORY",
                font_style="Caption",
                size_hint_x=0.35,
                on_release=lambda x, pid=p_id, pname=p_name: self.show_patient_history(pid, pname)
            )
            
            book_btn = MDRaisedButton(
                text="BOOK APPT",
                font_style="Caption",
                size_hint_x=0.45,
                on_release=lambda x, pid=p_id, pname=p_name, pphone=p_phone: self.quick_book_patient(pid, pname, pphone)
            )

            edit_btn = MDIconButton(
                icon="account-edit-outline",
                theme_icon_color="Custom",
                icon_color=(0.1, 0.5, 0.9, 1),
                user_font_size="18sp",
                size_hint_x=0.2,
                on_release=lambda x, prow=p: self.open_edit_dialog(prow)
            )

            btn_row.add_widget(history_btn)
            btn_row.add_widget(book_btn)
            btn_row.add_widget(edit_btn)

            card.add_widget(title_box)
            card.add_widget(contact_lbl)
            card.add_widget(addr_lbl)
            card.add_widget(btn_row)

            container.add_widget(card)

    def on_search(self, query):
        self.refresh_patient_list(query.strip())

    def quick_book_patient(self, patient_id, patient_name, phone):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, "booking_screen"):
            app.booking_screen.selected_patient_id = patient_id
            app.booking_screen.ids.patient_field.text = f"{patient_name} (#{patient_id})"
            if hasattr(app, "bottom_nav"):
                app.bottom_nav.switch_tab("tab_booking")

    def register_patient(self):
        name = self.ids.name_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        email = self.ids.email_field.text.strip()
        address = self.ids.address_field.text.strip()

        if not name:
            self.show_dialog("Error", "Patient Full Name is required.")
            return

        if not phone:
            self.show_dialog("Error", "Patient Phone Number is required.")
            return

        pid = database.add_patient(name, phone, email, address)
        self.show_dialog("Success", f"Patient '{name}' registered successfully (ID: #{pid})!", success=True)

    def show_patient_history(self, patient_id, patient_name):
        history = database.get_patient_appointments(patient_id)
        if not history:
            text = f"No appointment history found for {patient_name}."
        else:
            text = f"Appointment History for {patient_name}:\n\n"
            for h in history:
                text += f"• {h[3]} at {h[4]} - {h[5]} [{h[7].upper()}]\n"
                if h[6]:
                    text += f"  Notes: {h[6]}\n"

        self.dialog = MDDialog(
            title=f"Patient Record (#{patient_id})",
            text=text,
            buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def open_edit_dialog(self, patient_row):
        # patient_row: (id, name, phone, email, address, created_at)
        p_id, p_name, p_phone, p_email, p_address, _ = patient_row

        box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(200))
        name_in = MDTextField(text=p_name, hint_text="Full Name")
        phone_in = MDTextField(text=p_phone, hint_text="Phone Number")
        email_in = MDTextField(text=p_email or "", hint_text="Email Address")
        addr_in = MDTextField(text=p_address or "", hint_text="Address")

        box.add_widget(name_in)
        box.add_widget(phone_in)
        box.add_widget(email_in)
        box.add_widget(addr_in)

        def save_edits(x):
            database.update_patient(
                p_id,
                name_in.text.strip(),
                phone_in.text.strip(),
                email_in.text.strip(),
                addr_in.text.strip()
            )
            self.edit_dialog.dismiss()
            self.refresh_patient_list()

        self.edit_dialog = MDDialog(
            title=f"Edit Patient Record #{p_id}",
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.edit_dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=save_edits)
            ]
        )
        self.edit_dialog.open()

    def show_dialog(self, title, text, success=False):
        def on_close(x):
            self.dialog.dismiss()
            if success:
                self.clear_form()
                self.refresh_patient_list()

        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=on_close)]
        )
        self.dialog.open()

    def clear_form(self):
        self.ids.name_field.text = ""
        self.ids.phone_field.text = ""
        self.ids.email_field.text = ""
        self.ids.address_field.text = ""
