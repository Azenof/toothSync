"""
dashboard.py - Dashboard Screen for ToothSync KivyMD Application
"""

import sys
import os
from datetime import datetime

from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.chip import MDChip

# Parent path import fix
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self, *args):
        """Called when entering the screen to refresh data."""
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refreshes the dashboard cards and list of today's appointments."""
        container = self.ids.appointments_container
        container.clear_widgets()

        today_str = datetime.now().strftime("%Y-%m-%d")
        appts = database.get_today_appointments()

        total_count = len(appts)
        completed_count = sum(1 for a in appts if a[5] == "completed")
        pending_count = total_count - completed_count

        # Update stats labels
        self.ids.date_label.text = f"📅 Today: {today_str}"
        self.ids.total_label.text = str(total_count)
        self.ids.pending_label.text = str(pending_count)
        self.ids.completed_label.text = str(completed_count)

        if not appts:
            empty_card = MDCard(
                orientation="vertical",
                padding=dp(20),
                size_hint_y=None,
                height=dp(80),
                radius=[12, 12, 12, 12],
                elevation=1
            )
            empty_label = MDLabel(
                text="No appointments scheduled for today.",
                halign="center",
                theme_text_color="Hint"
            )
            empty_card.add_widget(empty_label)
            container.add_widget(empty_card)
            return

        for appt in appts:
            # appt tuple structure: (id, name, phone, time, treatment, status)
            appt_id, p_name, p_phone, appt_time, treatment, status = appt

            card = MDCard(
                orientation="horizontal",
                padding=dp(12),
                spacing=dp(12),
                size_hint_y=None,
                height=dp(90),
                radius=[12, 12, 12, 12],
                elevation=2,
                line_color=(0.9, 0.9, 0.9, 1)
            )

            # Left side details
            info_box = MDBoxLayout(orientation="vertical", spacing=dp(4))
            
            header_box = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(24))
            name_label = MDLabel(
                text=p_name,
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Primary",
                size_hint_x=0.7
            )
            status_chip = MDLabel(
                text=status.upper(),
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.1, 0.7, 0.3, 1) if status == "completed" else (0.9, 0.5, 0.1, 1),
                size_hint_x=0.3,
                halign="right"
            )
            header_box.add_widget(name_label)
            header_box.add_widget(status_chip)
            
            detail_label = MDLabel(
                text=f"⏰ {appt_time}  |  🩺 {treatment}  |  📞 {p_phone}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )

            info_box.add_widget(header_box)
            info_box.add_widget(detail_label)

            # Right side action buttons
            btn_box = MDBoxLayout(orientation="horizontal", spacing=dp(4), size_hint_x=None, width=dp(90))
            
            if status == "pending":
                complete_btn = MDIconButton(
                    icon="check-circle-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.1, 0.7, 0.3, 1),
                    on_release=lambda x, aid=appt_id: self.mark_complete(aid)
                )
                btn_box.add_widget(complete_btn)

            delete_btn = MDIconButton(
                icon="delete-outline",
                theme_icon_color="Custom",
                icon_color=(0.9, 0.2, 0.2, 1),
                on_release=lambda x, aid=appt_id, name=p_name: self.confirm_delete(aid, name)
            )
            btn_box.add_widget(delete_btn)

            card.add_widget(info_box)
            card.add_widget(btn_box)

            container.add_widget(card)

    def mark_complete(self, appt_id):
        database.complete_appointment(appt_id)
        self.refresh_dashboard()

    def confirm_delete(self, appt_id, name):
        self.dialog = MDDialog(
            title="Delete Appointment",
            text=f"Are you sure you want to delete appointment for {name}?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x, aid=appt_id: self.do_delete(aid)
                ),
            ],
        )
        self.dialog.open()

    def do_delete(self, appt_id):
        if self.dialog:
            self.dialog.dismiss()
        database.delete_appointment(appt_id)
        self.refresh_dashboard()
