"""
dashboard.py - Enhanced Dashboard Screen for ToothSync KivyMD Application
Features prominent time grouping and visual layout for dental clinic schedule.
"""

import sys
import os
from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.current_filter = "today"
        Clock.schedule_once(lambda dt: self.refresh_dashboard(), 0)

    def on_enter(self, *args):
        self.refresh_dashboard()

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refreshes stats and appointment cards according to current_filter."""
        if not hasattr(self, "ids") or "appointments_container" not in self.ids:
            return

        container = self.ids.appointments_container
        container.clear_widgets()

        # Fetch datasets for stats
        today_appts = database.get_today_appointments()
        upcoming_appts = database.get_upcoming_appointments()
        all_appts = database.get_all_appointments()

        # Update stats counter labels
        self.ids.date_label.text = f"📅 {datetime.now().strftime('%A, %b %d, %Y')}"
        self.ids.stat_today_label.text = str(len(today_appts))
        self.ids.stat_upcoming_label.text = str(len(upcoming_appts))
        self.ids.stat_completed_label.text = str(sum(1 for a in all_appts if a[7] == "completed"))
        self.ids.stat_cancelled_label.text = str(sum(1 for a in all_appts if a[7] == "cancelled"))

        # Select dataset based on active filter
        if self.current_filter == "today":
            appts = today_appts
            self.ids.filter_title_label.text = f"Today's Schedule ({len(appts)} Appointments)"
        elif self.current_filter == "upcoming":
            appts = upcoming_appts
            self.ids.filter_title_label.text = f"Upcoming Schedule ({len(appts)} Appointments)"
        else:
            appts = all_appts
            self.ids.filter_title_label.text = f"Full Appointment History ({len(appts)} Total)"

        if not appts:
            empty_card = MDCard(
                orientation="vertical",
                padding=dp(20),
                size_hint_y=None,
                height=dp(85),
                radius=[12, 12, 12, 12],
                elevation=1
            )
            empty_label = MDLabel(
                text=f"No {self.current_filter} appointments found.",
                halign="center",
                theme_text_color="Hint"
            )
            empty_card.add_widget(empty_label)
            container.add_widget(empty_card)
            return

        for appt in appts:
            # Tuple: (id, name, phone, date, time, treatment, notes, status, patient_id)
            appt_id, p_name, p_phone, appt_date, appt_time, treatment, notes, status, p_id = appt

            # Status colors
            if status == "completed":
                status_color = (0.1, 0.7, 0.3, 1)
                time_card_bg = (0.05, 0.5, 0.4, 1)
            elif status == "cancelled":
                status_color = (0.85, 0.2, 0.2, 1)
                time_card_bg = (0.6, 0.2, 0.2, 1)
            else:
                status_color = (0.9, 0.5, 0.1, 1)
                time_card_bg = (0.05, 0.45, 0.55, 1)

            card = MDCard(
                orientation="horizontal",
                padding=dp(8),
                spacing=dp(10),
                size_hint_y=None,
                height=dp(100),
                radius=[12, 12, 12, 12],
                elevation=2,
                line_color=(0.88, 0.88, 0.88, 1)
            )

            # --- 1. PROMINENT TIME BADGE CARD (LEFT) ---
            time_badge = MDCard(
                orientation="vertical",
                padding=dp(6),
                size_hint_x=None,
                width=dp(105),
                radius=[8, 8, 8, 8],
                elevation=0,
                md_bg_color=time_card_bg
            )
            
            time_lbl = MDLabel(
                text=appt_time,
                font_style="Subtitle2",
                bold=True,
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_y=0.6
            )
            date_lbl = MDLabel(
                text=appt_date,
                font_style="Overline",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.9, 0.95, 1, 0.9),
                size_hint_y=0.4
            )
            time_badge.add_widget(time_lbl)
            time_badge.add_widget(date_lbl)

            # --- 2. APPOINTMENT & PATIENT DETAILS (CENTER) ---
            info_box = MDBoxLayout(orientation="vertical", spacing=dp(2), pos_hint={"center_y": 0.5})

            header_box = MDBoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(24))
            name_lbl = MDLabel(
                text=p_name,
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Primary",
                size_hint_x=0.7
            )
            status_lbl = MDLabel(
                text=status.upper(),
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=status_color,
                size_hint_x=0.3,
                halign="right"
            )
            header_box.add_widget(name_lbl)
            header_box.add_widget(status_lbl)

            detail_lbl = MDLabel(
                text=f"🩺 {treatment}   |   📞 {p_phone}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )

            notes_lbl = MDLabel(
                text=f"Notes: {notes if notes else 'None'}",
                font_style="Overline",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(18)
            )

            info_box.add_widget(header_box)
            info_box.add_widget(detail_lbl)
            info_box.add_widget(notes_lbl)

            # --- 3. ACTION BUTTONS (RIGHT) ---
            btn_box = MDBoxLayout(orientation="horizontal", spacing=dp(2), size_hint_x=None, width=dp(110), pos_hint={"center_y": 0.5})

            if status == "pending":
                complete_btn = MDIconButton(
                    icon="check-circle-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.1, 0.7, 0.3, 1),
                    on_release=lambda x, aid=appt_id: self.mark_complete(aid)
                )
                cancel_btn = MDIconButton(
                    icon="close-circle-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.9, 0.5, 0.1, 1),
                    on_release=lambda x, aid=appt_id: self.mark_cancelled(aid)
                )
                btn_box.add_widget(complete_btn)
                btn_box.add_widget(cancel_btn)

            delete_btn = MDIconButton(
                icon="delete-outline",
                theme_icon_color="Custom",
                icon_color=(0.85, 0.2, 0.2, 1),
                on_release=lambda x, aid=appt_id, name=p_name: self.confirm_delete(aid, name)
            )
            btn_box.add_widget(delete_btn)

            card.add_widget(time_badge)
            card.add_widget(info_box)
            card.add_widget(btn_box)

            container.add_widget(card)

    def mark_complete(self, appt_id):
        database.complete_appointment(appt_id)
        self.refresh_dashboard()

    def mark_cancelled(self, appt_id):
        database.cancel_appointment(appt_id)
        self.refresh_dashboard()

    def confirm_delete(self, appt_id, name):
        self.dialog = MDDialog(
            title="Delete Appointment Record",
            text=f"Permanently delete appointment record for {name}?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.85, 0.2, 0.2, 1),
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
