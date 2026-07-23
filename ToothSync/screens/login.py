"""
login.py - Login & Authentication Screen for ToothSync Application
"""

import sys
import os

from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def perform_login(self, username, password):
        """Authenticates doctor/admin login."""
        username = username.strip()
        password = password.strip()

        if not username or not password:
            self.show_dialog("Login Error", "Please enter both Doctor ID and Password.")
            return

        # Simple secure local clinic authentication
        if (username.lower() in ["doctor", "admin", "dralex"]) and (password in ["1234", "admin", "toothsync"]):
            # Access running app and switch to main screen
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, "root_manager"):
                app.root_manager.current = "main_screen"
        else:
            self.show_dialog("Authentication Failed", "Invalid Doctor ID or Password.\n(Default: doctor / 1234)")

    def show_dialog(self, title, text):
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()
