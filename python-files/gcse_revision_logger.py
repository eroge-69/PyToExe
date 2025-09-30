"""
GCSE Revision Logger - Simple Windows App
-----------------------------------------
✅ Features:
- Manual add: Subject, Date (DD/MM/YY), Duration (minutes), Note
- Live timer with automatic date logging
- View sessions and totals
- Export to CSV
- Auto-database upgrade (safe for old data)

"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import threading
import csv
import os

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

DB_FILENAME = "revision_logs.db"


# -------------------- Database --------------------
class RevisionDB:
    def __init__(self, filename=DB_FILENAME):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self._create_tables()
        self._ensure_date_column()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                subject TEXT NOT NULL,
                start_ts TEXT,
                end_ts TEXT,
                duration_seconds INTEGER NOT NULL,
                note TEXT
            )
            """
        )
        self.conn.commit()

    def _ensure_date_column(self):
        """Add 'date_tag' column if it doesn't exist (automatic upgrade)."""
        c = self.conn.cursor()
        c.execute("PRAGMA table_info(sessions)")
        cols = [row[1] for row in c.fetchall()]
        if "date_tag" not in cols:
            c.execute("ALTER TABLE sessions ADD COLUMN date_tag TEXT")
            self.conn.commit()

    def add_session(self, subject, duration_seconds, date_tag, note="", start_ts="", end_ts=""):
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO sessions (subject, start_ts, end_ts, duration_seconds, note, date_tag)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (subject, start_ts, end_ts, duration_seconds, note, date_tag),
        )
        self.conn.commit()

    def list_sessions(self, limit=500):
        c = self.conn.cursor()
        c.execute(
            """SELECT id, subject, date_tag, duration_seconds, note
               FROM sessions ORDER BY id DESC LIMIT ?""",
            (limit,),
        )
        return c.fetchall()

    def delete_session(self, session_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self.conn.commit()

    def totals_by_subject(self):
        c = self.conn.cursor()
        c.execute(
            "SELECT subject, SUM(duration_seconds) FROM sessions GROUP BY subject"
        )
        return c.fetchall()

    def export_csv(self, path):
        rows = self.list_sessions(limit=1000000)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "subject", "date", "duration_seconds", "note"])
            for r in rows:
                writer.writerow(r)


# -------------------- Utils --------------------
def seconds_to_hms(seconds):
    td = timedelta(seconds=int(seconds))
    h, remainder = divmod(td.total_seconds(), 3600)
    m, s = divmod(remainder, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


def minutes_to_seconds(minutes_str):
    try:
        return int(float(minutes_str) * 60)
    except ValueError:
        return None


# -------------------- GUI --------------------
class RevisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GCSE Revision Logger")
        self.db = RevisionDB()

        # Timer state
        self.timer_running = False
        self.timer_subject = ""
        self.timer_start = None
        self.timer_thread = None
        self.timer_stop_event = threading.Event()

        self._build_ui()
        self.refresh_sessions()
        self.refresh_totals()

    def _build_ui(self):
        pad = 8
        frm = ttk.Frame(self.root, padding=pad)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ---------- Timer ----------
        timer_frame = ttk.LabelFrame(frm, text="Live Timer", padding=pad)
        timer_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(timer_frame, text="Subject:").grid(row=0, column=0)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(timer_frame, textvariable=self.subject_var)
        self.subject_combo["values"] = self._recent_subjects()
        self.subject_combo.grid(row=0, column=1, sticky="ew")
        timer_frame.columnconfigure(1, weight=1)

        self.timer_label = ttk.Label(
            timer_frame, text="00:00:00", font=("TkDefaultFont", 14)
        )
        self.timer_label.grid(row=0, column=2, padx=10)

        self.start_btn = ttk.Button(timer_frame, text="Start", command=self.start_timer)
        self.start_btn.grid(row=0, column=3, padx=4)
        self.stop_btn = ttk.Button(
            timer_frame, text="Stop", command=self.stop_timer, state="disabled"
        )
        self.stop_btn.grid(row=0, column=4, padx=4)

        # ---------- Manual ----------
        manual_frame = ttk.LabelFrame(frm, text="Add Session Manually", padding=pad)
        manual_frame.grid(row=1, column=0, sticky="ew", pady=(pad, 0))

        ttk.Label(manual_frame, text="Subject:").grid(row=0, column=0)
        self.manual_subject = tk.Entry(manual_frame)
        self.manual_subject.grid(row=0, column=1, sticky="ew")

        ttk.Label(manual_frame, text="Date (DD/MM/YY):").grid(row=0, column=2)
        self.manual_date = tk.Entry(manual_frame)
        self.manual_date.insert(0, datetime.now().strftime("%d/%m/%y"))
        self.manual_date.grid(row=0, column=3)

        ttk.Label(manual_frame, text="Duration (minutes):").grid(row=0, column=4)
        self.manual_duration = tk.Entry(manual_frame)
        self.manual_duration.grid(row=0, column=5)

        ttk.Label(manual_frame, text="Note:").grid(row=1, column=0)
        self.manual_note = tk.Entry(manual_frame)
        self.manual_note.grid(row=1, column=1, columnspan=4, sticky="ew")

        ttk.Button(manual_frame, text="Add Session", command=self.add_manual_session).grid(
            row=1, column=5
        )

        # ---------- Sessions ----------
        sessions_frame = ttk.LabelFrame(frm, text="Sessions", padding=pad)
        sessions_frame.grid(row=2, column=0, sticky="nsew", pady=(pad, 0))
        sessions_frame.columnconfigure(0, weight=1)
        sessions_frame.rowconfigure(0, weight=1)

        cols = ("id", "subject", "date", "duration", "note")
        self.sessions_tree = ttk.Treeview(
            sessions_frame, columns=cols, show="headings", selectmode="browse"
        )
        for c in cols:
            self.sessions_tree.heading(c, text=c.title())
        self.sessions_tree.column("id", width=40, anchor="center")
        self.sessions_tree.column("duration", width=100, anchor="center")
        self.sessions_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            sessions_frame, orient="vertical", command=self.sessions_tree.yview
        )
        self.sessions_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(sessions_frame)
        btn_frame.grid(row=1, column=0, sticky="ew")
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).grid(
            row=0, column=0, padx=4
        )
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).grid(
            row=0, column=1, padx=4
        )
        if MATPLOTLIB_AVAILABLE:
            ttk.Button(btn_frame, text="Show Chart", command=self.show_chart).grid(
                row=0, column=2, padx=4
            )

        # ---------- Totals ----------
        totals_frame = ttk.LabelFrame(frm, text="Totals by Subject", padding=pad)
        totals_frame.grid(row=0, column=1, rowspan=3, sticky="ns", padx=(10, 0))
        totals_frame.columnconfigure(0, weight=1)

        self.totals_tree = ttk.Treeview(
            totals_frame, columns=("subject", "total"), show="headings"
        )
        self.totals_tree.heading("subject", text="Subject")
        self.totals_tree.heading("total", text="Total (HH:MM:SS)")
        self.totals_tree.grid(row=0, column=0, sticky="nsew")

        totals_scroll = ttk.Scrollbar(
            totals_frame, orient="vertical", command=self.totals_tree.yview
        )
        self.totals_tree.configure(yscroll=totals_scroll.set)
        totals_scroll.grid(row=0, column=1, sticky="ns")

    # ---------- Timer ----------
    def start_timer(self):
        subject = self.subject_var.get().strip()
        if not subject:
            messagebox.showwarning("Missing", "Enter a subject first.")
            return
        if self.timer_running:
            return
        self.timer_subject = subject
        self.timer_start = datetime.now()
        self.timer_running = True
        self.timer_stop_event.clear()
        self.start_btn["state"] = "disabled"
        self.stop_btn["state"] = "normal"
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

    def _timer_loop(self):
        while not self.timer_stop_event.is_set():
            elapsed = datetime.now() - self.timer_start
            self.timer_label.config(text=seconds_to_hms(elapsed.total_seconds()))
            self.timer_stop_event.wait(0.5)

    def stop_timer(self):
        if not self.timer_running:
            return
        self.timer_stop_event.set()
        end_time = datetime.now()
        duration = int((end_time - self.timer_start).total_seconds())
        date_tag = datetime.now().strftime("%d/%m/%y")
        self.db.add_session(self.timer_subject, duration, date_tag)
        messagebox.showinfo(
            "Session Saved",
            f"{self.timer_subject}: {seconds_to_hms(duration)} ({date_tag})",
        )
        self.timer_running = False
        self.timer_label.config(text="00:00:00")
        self.start_btn["state"] = "normal"
        self.stop_btn["state"] = "disabled"
        self.refresh_sessions()
        self.refresh_totals()

    # ---------- Manual ----------
    def add_manual_session(self):
        subject = self.manual_subject.get().strip()
        date_text = self.manual_date.get().strip()
        duration_text = self.manual_duration.get().strip()
        note = self.manual_note.get().strip()

        if not subject or not date_text or not duration_text:
            messagebox.showwarning("Missing", "Please fill all required fields.")
            return

        try:
            datetime.strptime(date_text, "%d/%m/%y")
        except ValueError:
            messagebox.showerror("Format Error", "Date must be in DD/MM/YY format.")
            return

        duration_seconds = minutes_to_seconds(duration_text)
        if duration_seconds is None:
            messagebox.showerror("Invalid", "Duration must be a number.")
            return

        self.db.add_session(subject, duration_seconds, date_text, note=note)
        messagebox.showinfo("Saved", f"Session added: {subject} ({date_text})")

        self.manual_subject.delete(0, "end")
        self.manual_duration.delete(0, "end")
        self.manual_note.delete(0, "end")
        self.manual_date.delete(0, "end")
        self.manual_date.insert(0, datetime.now().strftime("%d/%m/%y"))
        self.refresh_sessions()
        self.refresh_totals()

    # ---------- Sessions ----------
    def refresh_sessions(self):
        for r in self.sessions_tree.get_children():
            self.sessions_tree.delete(r)
        for r in self.db.list_sessions():
            id_, subj, date_tag, dur, note = r
            self.sessions_tree.insert(
                "", "end", values=(id_, subj, date_tag, seconds_to_hms(dur), note)
            )

    def delete_selected(self):
        sel = self.sessions_tree.selection()
        if not sel:
            return
        vals = self.sessions_tree.item(sel[0])["values"]
        if messagebox.askyesno("Delete", f"Delete session {vals[0]}?"):
            self.db.delete_session(vals[0])
            self.refresh_sessions()
            self.refresh_totals()

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return
        self.db.export_csv(path)
        messagebox.showinfo("Exported", f"Exported to {path}")

    # ---------- Totals ----------
    def refresh_totals(self):
        for r in self.totals_tree.get_children():
            self.totals_tree.delete(r)
        for subj, total in self.db.totals_by_subject():
            self.totals_tree.insert("", "end", values=(subj, seconds_to_hms(total)))
        self.subject_combo["values"] = self._recent_subjects()

    def _recent_subjects(self):
        rows = self.db.totals_by_subject()
        subs = [r[0] for r in rows]
        return subs or ["Maths", "English", "Biology", "Chemistry", "Physics", "PE", "Latin", "History", "German"]

    # ---------- Chart ----------
    def show_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Missing", "Install matplotlib to use charts.")
            return
        rows = self.db.totals_by_subject()
        if not rows:
            messagebox.showinfo("No Data", "No sessions to display.")
            return
        subjects = [r[0] for r in rows]
        hours = [r[1] / 3600 for r in rows]
        plt.bar(subjects, hours)
        plt.ylabel("Hours")
        plt.title("Total Revision Time")
        plt.tight_layout()
        plt.show()


# -------------------- Run --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("950x650")
    app = RevisionApp(root)
    root.mainloop()
