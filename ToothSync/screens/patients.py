"""
patients.py - Patient Management Screen for ToothSync KivyMD Application
"""

import sys
import os

from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


class PatientsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self, *args):
        self.refresh_patient_list()

    def refresh_patient_list(self, query=None):
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
            empty_card.add_widget(MDLabel(text="No patients found.", halign="center", theme_text_color="Hint"))
            container.add_widget(empty_card)
            return

        for p in patients:
            # patient tuple: (id, name, phone, email, address, created_at)
            p_id, p_name, p_phone, p_email, p_address, p_created = p

            card = MDCard(
                orientation="vertical",
                padding=dp(12),
                spacing=dp(4),
                size_hint_y=None,
                height=dp(95),
                radius=[10, 10, 10, 10],
                elevation=2,
                line_color=(0.9, 0.9, 0.9, 1)
            )

            title_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
            name_lbl = MDLabel(text=f"{p_name}", font_style="Subtitle1", bold=True, size_hint_x=0.8)
            id_lbl = MDLabel(text=f"ID: #{p_id}", font_style="Caption", theme_text_color="Hint", size_hint_x=0.2, halign="right")
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
                text=f"📍 {p_address or 'No address registered'}",
                font_style="Overline",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(18)
            )

            card.add_widget(title_box)
            card.add_widget(contact_lbl)
            card.add_widget(addr_lbl)

            container.add_widget(card)

    def on_search(self, query):
        self.refresh_patient_list(query.strip())

    def register_patient(self):
        name = self.ids.name_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        email = self.ids.email_field.text.strip()
        address = self.ids.address_field.text.strip()

        if not name:
            self.show_dialog("Error", "Patient Name is required.")
            return

        if not phone:
            self.show_dialog("Error", "Patient Phone Number is required.")
            return

        pid = database.add_patient(name, phone, email, address)
        self.show_dialog("Success", f"Patient '{name}' registered successfully (ID: #{pid})!", success=True)

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
