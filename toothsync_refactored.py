"""
main_refactored.py
Refactored version of main.py applying three design patterns:
  - Singleton  (DatabaseManager)
  - Observer   (AppointmentSubject)
  - Factory    (WidgetFactory)
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from toothsync import (
    STORAGE_FILE,
    TREATMENTS,
    TIMES,
    TREATMENT_COLORS,
    C_BG, C_SIDEBAR, C_ACCENT, C_ACCENT2, C_WHITE,
    C_TEXT, C_SUBTEXT, C_PENDING, C_DONE, C_DANGER, C_BORDER,
    make_record,
    validate_booking,
    filter_records,
    get_unique_patients,
)


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return self._seed()

    def save(self, records):
        with open(STORAGE_FILE, "w") as f:
            json.dump(records, f, indent=4)

    def _seed(self):
        today = datetime.now().strftime("%Y-%m-%d")
        seeds = [
            {
                "id": "seed-1",
                "patientName": "Eleanor Vance",
                "phone": "(555) 234-5678",
                "email": "eleanor.v@example.com",
                "date": today, "time": "09:00 AM",
                "treatment": "Checkup",
                "notes": "High sensitivity in molars.",
                "status": "completed"
            },
            {
                "id": "seed-2",
                "patientName": "Marcus Brody",
                "phone": "(555) 987-6543",
                "email": "marcus.b@museum.org",
                "date": today, "time": "11:00 AM",
                "treatment": "Cleaning",
                "notes": "Regular scale and polish.",
                "status": "pending"
            },
            {
                "id": "seed-3",
                "patientName": "Sarah Connor",
                "phone": "(555) 543-2109",
                "email": "sconnor@cyberdyne.net",
                "date": today, "time": "02:00 PM",
                "treatment": "Root Canal",
                "notes": "Dental anxiety — offer nitrous oxide.",
                "status": "pending"
            },
        ]
        self.save(seeds)
        return seeds


class AppointmentSubject:
    def __init__(self, records):
        self._records = records
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def _notify(self):
        for observer in self._observers:
            observer()

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        self._records = value
        DatabaseManager().save(self._records)
        self._notify()

    def append(self, record):
        self._records.append(record)
        DatabaseManager().save(self._records)
        self._notify()

    def complete(self, rid):
        for r in self._records:
            if r["id"] == rid:
                r["status"] = "completed"
        DatabaseManager().save(self._records)
        self._notify()

    def delete(self, rid):
        self._records = [r for r in self._records if r["id"] != rid]
        DatabaseManager().save(self._records)
        self._notify()


class WidgetFactory:
    @staticmethod
    def button(parent, text, command, bg=C_ACCENT, fg=C_WHITE,
               padx=14, pady=6, font_size=10):
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=C_ACCENT2, activeforeground=C_WHITE,
            relief="flat", cursor="hand2",
            font=("Helvetica", font_size, "bold"),
            padx=padx, pady=pady, bd=0
        )

    @staticmethod
    def label(parent, text, size=10, bold=False, color=C_TEXT, bg=C_WHITE):
        weight = "bold" if bold else "normal"
        return tk.Label(parent, text=text, font=("Helvetica", size, weight),
                        fg=color, bg=bg)

    @staticmethod
    def entry(parent, width=28, textvariable=None):
        return tk.Entry(parent, width=width, relief="solid", bd=1,
                        font=("Helvetica", 10),
                        highlightthickness=1, highlightcolor=C_ACCENT,
                        bg=C_WHITE, fg=C_TEXT,
                        textvariable=textvariable)


def make_button(parent, text, command, bg=C_ACCENT, fg=C_WHITE,
                padx=14, pady=6, font_size=10, radius=6):
    return WidgetFactory.button(parent, text, command,
                                bg=bg, fg=fg, padx=padx, pady=pady,
                                font_size=font_size)


class ToothSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🦷  ToothSync  —  Dentist Scheduler")
        self.geometry("900x640")
        self.minsize(800, 560)
        self.configure(bg=C_BG)
        self.resizable(True, True)

        self._db = DatabaseManager()
        self._subject = AppointmentSubject(self._db.load())
        self._subject.subscribe(self.refresh_schedule)
        self._subject.subscribe(self.refresh_patients)

        self.search_var = tk.StringVar()
        self._build_layout()
        self.search_var.trace_add("write", lambda *_: self.refresh_schedule())
        self.show_tab("schedule")

    def _build_layout(self):
        sidebar = tk.Frame(self, bg=C_SIDEBAR, width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🦷", font=("Helvetica", 36),
                 bg=C_SIDEBAR, fg=C_WHITE).pack(pady=(30, 4))
        tk.Label(sidebar, text="ToothSync", font=("Helvetica", 16, "bold"),
                 bg=C_SIDEBAR, fg=C_WHITE).pack()
        tk.Label(sidebar, text="Dental Scheduler", font=("Helvetica", 9),
                 bg=C_SIDEBAR, fg="#94D8D3").pack(pady=(0, 30))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=16, pady=4)

        self.nav_buttons = {}
        for label_text, tab in [
            ("📅  Schedule",   "schedule"),
            ("➕  New Booking", "booking"),
            ("👥  Patients",    "patients"),
        ]:
            btn = tk.Button(
                sidebar, text=label_text, anchor="w",
                font=("Helvetica", 11), fg=C_WHITE, bg=C_SIDEBAR,
                activebackground=C_ACCENT, activeforeground=C_WHITE,
                relief="flat", cursor="hand2", padx=20, pady=10, bd=0,
                command=lambda t=tab: self.show_tab(t)
            )
            btn.pack(fill="x")
            self.nav_buttons[tab] = btn

        self.content = tk.Frame(self, bg=C_BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.frames = {}
        for tab in ("schedule", "booking", "patients"):
            self.frames[tab] = tk.Frame(self.content, bg=C_BG)

        self._build_schedule_tab()
        self._build_booking_tab()
        self._build_patients_tab()

    def show_tab(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        for t, btn in self.nav_buttons.items():
            btn.configure(bg=C_ACCENT if t == name else C_SIDEBAR)
        if name == "schedule":
            self.refresh_schedule()
        elif name == "patients":
            self.refresh_patients()

    def _build_schedule_tab(self):
        parent = self.frames["schedule"]

        header = tk.Frame(parent, bg=C_BG, pady=12)
        header.pack(fill="x", padx=20)
        tk.Label(header, text="Today's Schedule", font=("Helvetica", 18, "bold"),
                 fg=C_TEXT, bg=C_BG).pack(side="left")

        self.stats_frame = tk.Frame(parent, bg=C_BG)
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        self._stat_labels = {}
        for key, caption, color in [
            ("today",   "Today",     C_ACCENT),
            ("pending", "Pending",   C_PENDING),
            ("done",    "Completed", C_DONE),
            ("total",   "Total",     C_TEXT),
        ]:
            card = tk.Frame(self.stats_frame, bg=C_WHITE, relief="solid", bd=1, padx=12, pady=8)
            card.pack(side="left", padx=(0, 10))
            tk.Label(card, text=caption, font=("Helvetica", 8), fg=C_SUBTEXT, bg=C_WHITE).pack()
            lbl = tk.Label(card, text="0", font=("Helvetica", 20, "bold"), fg=color, bg=C_WHITE)
            lbl.pack()
            self._stat_labels[key] = lbl

        search_row = tk.Frame(parent, bg=C_BG)
        search_row.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(search_row, text="🔍", font=("Helvetica", 12), fg=C_SUBTEXT, bg=C_BG).pack(side="left")
        search_entry = tk.Entry(search_row, textvariable=self.search_var,
                                font=("Helvetica", 10), relief="solid", bd=1,
                                bg=C_WHITE, fg=C_TEXT, width=30)
        search_entry.pack(side="left", padx=6, ipady=4)
        search_entry.insert(0, "Search name or phone…")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.delete(0, "end")
                          if search_entry.get() == "Search name or phone…" else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search name or phone…")
                          if search_entry.get() == "" else None)

        self.schedule_canvas = tk.Canvas(parent, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.schedule_canvas.yview)
        self.schedule_inner = tk.Frame(self.schedule_canvas, bg=C_BG)
        self.schedule_inner.bind("<Configure>",
            lambda e: self.schedule_canvas.configure(
                scrollregion=self.schedule_canvas.bbox("all")))
        self.schedule_canvas.create_window((0, 0), window=self.schedule_inner, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=scrollbar.set)
        self.schedule_canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

    def refresh_schedule(self):
        if not hasattr(self, "schedule_inner"):
            return
        for w in self.schedule_inner.winfo_children():
            w.destroy()

        query = self.search_var.get().lower().strip()
        if query == "search name or phone…":
            query = ""

        today = datetime.now().strftime("%Y-%m-%d")
        records = self._subject.records
        shown = filter_records(records, query=query)

        self._stat_labels["today"].config(text=str(sum(1 for r in records if r["date"] == today)))
        self._stat_labels["pending"].config(text=str(sum(1 for r in records if r["status"] == "pending")))
        self._stat_labels["done"].config(text=str(sum(1 for r in records if r["status"] == "completed")))
        self._stat_labels["total"].config(text=str(len(records)))

        if not shown:
            tk.Label(self.schedule_inner, text="No appointments found.",
                     font=("Helvetica", 12), fg=C_SUBTEXT, bg=C_BG).pack(pady=40)
            return

        for r in shown:
            self._make_appt_card(self.schedule_inner, r)

    def _make_appt_card(self, parent, r):
        color = TREATMENT_COLORS.get(r["treatment"], C_ACCENT)
        status_color = C_DONE if r["status"] == "completed" else C_PENDING

        card = tk.Frame(parent, bg=C_WHITE, relief="solid", bd=1)
        card.pack(fill="x", pady=5, ipady=4)

        tk.Frame(card, bg=color, width=6).pack(side="left", fill="y")

        body = tk.Frame(card, bg=C_WHITE, padx=12, pady=8)
        body.pack(side="left", fill="both", expand=True)

        row1 = tk.Frame(body, bg=C_WHITE)
        row1.pack(fill="x")
        tk.Label(row1, text=r["patientName"], font=("Helvetica", 12, "bold"),
                 fg=C_TEXT, bg=C_WHITE).pack(side="left")
        tk.Label(row1, text=r["status"].upper(), font=("Helvetica", 8, "bold"),
                 fg=status_color, bg=C_WHITE).pack(side="right")

        row2 = tk.Frame(body, bg=C_WHITE)
        row2.pack(fill="x")
        tk.Label(row2, text=f"📅 {r['date']}   🕐 {r['time']}",
                 font=("Helvetica", 9), fg=C_SUBTEXT, bg=C_WHITE).pack(side="left")
        tk.Label(row2, text=r["treatment"], font=("Helvetica", 9, "bold"),
                 fg=color, bg=C_WHITE).pack(side="right")

        row3 = tk.Frame(body, bg=C_WHITE)
        row3.pack(fill="x")
        tk.Label(row3, text=f"📞 {r['phone']}   ✉️ {r['email']}",
                 font=("Helvetica", 9), fg=C_SUBTEXT, bg=C_WHITE).pack(side="left")

        btns = tk.Frame(card, bg=C_WHITE, padx=8)
        btns.pack(side="right", fill="y")
        if r["status"] == "pending":
            make_button(btns, "✓ Done", lambda rid=r["id"]: self._complete(rid),
                        bg=C_DONE, padx=8, pady=4, font_size=9).pack(pady=(6, 2))
        make_button(btns, "🗑 Delete", lambda rid=r["id"]: self._delete(rid),
                    bg=C_DANGER, padx=8, pady=4, font_size=9).pack(pady=(2, 6))

    def _complete(self, rid):
        self._subject.complete(rid)

    def _delete(self, rid):
        rec = next((r for r in self._subject.records if r["id"] == rid), None)
        if rec and messagebox.askyesno(
                "Delete Appointment",
                f"Delete appointment for {rec['patientName']}?"):
            self._subject.delete(rid)

    def _build_booking_tab(self):
        parent = self.frames["booking"]

        canvas = tk.Canvas(parent, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C_BG)
        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        pad = dict(padx=24, pady=4)
        tk.Label(inner, text="Book New Appointment", font=("Helvetica", 18, "bold"),
                 fg=C_TEXT, bg=C_BG).pack(anchor="w", padx=24, pady=(20, 8))

        self._section_title(inner, "PATIENT PROFILE")
        self.f_name      = self._field(inner, "Full Name *")
        self.f_phone     = self._field(inner, "Phone Number *")
        self.f_email     = self._field(inner, "Email Address *")

        self._section_title(inner, "APPOINTMENT DETAILS")
        self.f_date      = self._field(inner, "Date (YYYY-MM-DD) *", placeholder=datetime.now().strftime("%Y-%m-%d"))
        self.f_time_var  = tk.StringVar(value="Select Time *")
        self.f_treat_var = tk.StringVar(value="Select Treatment *")

        row = tk.Frame(inner, bg=C_BG)
        row.pack(fill="x", **pad)
        tk.Label(row, text="Time *", width=18, anchor="w",
                 font=("Helvetica", 10), fg=C_SUBTEXT, bg=C_BG).pack(side="left")
        ttk.Combobox(row, textvariable=self.f_time_var, values=TIMES,
                     state="readonly", width=22).pack(side="left")

        row2 = tk.Frame(inner, bg=C_BG)
        row2.pack(fill="x", **pad)
        tk.Label(row2, text="Treatment *", width=18, anchor="w",
                 font=("Helvetica", 10), fg=C_SUBTEXT, bg=C_BG).pack(side="left")
        ttk.Combobox(row2, textvariable=self.f_treat_var, values=TREATMENTS,
                     state="readonly", width=22).pack(side="left")

        self.f_notes = self._field(inner, "Clinical Notes (optional)", multiline=True)

        make_button(inner, "  ✓  Book Appointment  ", self._submit_booking,
                    padx=20, pady=10, font_size=12).pack(anchor="w", padx=24, pady=(16, 4))

    def _section_title(self, parent, text):
        tk.Label(parent, text=text, font=("Helvetica", 9, "bold"),
                 fg=C_SUBTEXT, bg=C_BG).pack(anchor="w", padx=24, pady=(14, 2))
        tk.Frame(parent, bg=C_BORDER, height=1).pack(fill="x", padx=24, pady=(0, 6))

    def _field(self, parent, label_text, placeholder="", multiline=False):
        row = tk.Frame(parent, bg=C_BG)
        row.pack(fill="x", padx=24, pady=4)
        tk.Label(row, text=label_text, width=22, anchor="w",
                 font=("Helvetica", 10), fg=C_SUBTEXT, bg=C_BG).pack(side="left")
        if multiline:
            w = tk.Text(row, width=30, height=3, relief="solid", bd=1,
                        font=("Helvetica", 10), bg=C_WHITE, fg=C_TEXT)
            w.pack(side="left")
            return w
        var = tk.StringVar(value=placeholder)
        w = tk.Entry(row, textvariable=var, width=32, relief="solid", bd=1,
                     font=("Helvetica", 10), bg=C_WHITE, fg=C_TEXT)
        w.pack(side="left")
        return var

    def _submit_booking(self):
        name  = self.f_name.get().strip()
        phone = self.f_phone.get().strip()
        email = self.f_email.get().strip()
        date  = self.f_date.get().strip()
        time  = self.f_time_var.get()
        treat = self.f_treat_var.get()
        notes = self.f_notes.get("1.0", "end").strip() if isinstance(self.f_notes, tk.Text) else ""

        errors = validate_booking(name, phone, email, date, time, treat)
        if errors:
            messagebox.showwarning("Missing Fields", errors[0])
            return

        rec = make_record(name=name, phone=phone, email=email, date=date,
                          time=time, treatment=treat, notes=notes)
        self._subject.append(rec)

        self.f_name.set("")
        self.f_phone.set("")
        self.f_email.set("")
        self.f_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.f_time_var.set("Select Time *")
        self.f_treat_var.set("Select Treatment *")
        if isinstance(self.f_notes, tk.Text):
            self.f_notes.delete("1.0", "end")

        messagebox.showinfo("Success", f"Appointment for {name} booked successfully!")
        self.show_tab("schedule")

    def _build_patients_tab(self):
        parent = self.frames["patients"]
        tk.Label(parent, text="Patient Directory", font=("Helvetica", 18, "bold"),
                 fg=C_TEXT, bg=C_BG).pack(anchor="w", padx=20, pady=(20, 10))

        cols = ("Name", "Phone", "Email", "Visits")
        self.patient_tree = ttk.Treeview(parent, columns=cols, show="headings",
                                          selectmode="browse")
        for c in cols:
            self.patient_tree.heading(c, text=c)
            self.patient_tree.column(c, width=180 if c != "Visits" else 60, anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        self.patient_tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))

        self.patient_tree.tag_configure("odd",  background=C_WHITE)
        self.patient_tree.tag_configure("even", background="#F8FAFC")

    def refresh_patients(self):
        if not hasattr(self, "patient_tree"):
            return
        for row in self.patient_tree.get_children():
            self.patient_tree.delete(row)
        unique = get_unique_patients(self._subject.records)
        for i, (_, p) in enumerate(sorted(unique.items())):
            tag = "odd" if i % 2 == 0 else "even"
            self.patient_tree.insert("", "end",
                                     values=(p["name"], p["phone"], p["email"], p["count"]),
                                     tags=(tag,))


if __name__ == "__main__":
    app = ToothSyncApp()
    app.mainloop()
