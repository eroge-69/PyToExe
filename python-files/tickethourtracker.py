import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Canvas
from datetime import datetime, date, timedelta
import calendar
import csv
import os
import shutil
import time  # For timer functionality

# Database Manager Class
class DatabaseManager:
    def __init__(self, db_name='ticket_tracker.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE NOT NULL,
                client_text TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_date DATE NOT NULL,
                ticket_id INTEGER NOT NULL,
                hours REAL NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')

        # Migration: Add new columns if they don't exist
        self.cursor.execute("PRAGMA table_info(bookings)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if 'start_time' not in columns:
            self.cursor.execute("ALTER TABLE bookings ADD COLUMN start_time TEXT")
        if 'end_time' not in columns:
            self.cursor.execute("ALTER TABLE bookings ADD COLUMN end_time TEXT")
        if 'tags' not in columns:
            self.cursor.execute("ALTER TABLE bookings ADD COLUMN tags TEXT")
        self.conn.commit()

    def add_ticket(self, ticket_number, client_text):
        try:
            self.cursor.execute('INSERT INTO tickets (ticket_number, client_text) VALUES (?, ?)', (ticket_number, client_text))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_tickets(self):
        self.cursor.execute('SELECT id, ticket_number, client_text FROM tickets ORDER BY ticket_number')
        return self.cursor.fetchall()

    def update_ticket(self, ticket_id, ticket_number, client_text):
        try:
            self.cursor.execute('UPDATE tickets SET ticket_number = ?, client_text = ? WHERE id = ?', (ticket_number, client_text, ticket_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_ticket(self, ticket_id):
        self.cursor.execute('DELETE FROM bookings WHERE ticket_id = ?', (ticket_id,))
        self.cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        self.conn.commit()

    def add_booking(self, booking_date, ticket_id, hours, description, start_time=None, end_time=None, tags=None):
        self.cursor.execute('''
            INSERT INTO bookings (booking_date, ticket_id, hours, description, start_time, end_time, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (booking_date, ticket_id, hours, description, start_time, end_time, tags))
        self.conn.commit()

    def get_bookings_by_date(self, booking_date):
        self.cursor.execute('''
            SELECT b.id, t.ticket_number, b.hours, b.description, b.tags, b.start_time, b.end_time
            FROM bookings b JOIN tickets t ON b.ticket_id = t.id
            WHERE b.booking_date = ?
        ''', (booking_date,))
        return self.cursor.fetchall()

    def get_all_bookings(self):
        self.cursor.execute('''
            SELECT b.booking_date, t.ticket_number, b.hours, b.description, b.id, b.tags, b.start_time, b.end_time
            FROM bookings b JOIN tickets t ON b.ticket_id = t.id
            ORDER BY b.booking_date DESC
        ''')
        return self.cursor.fetchall()

    def update_booking(self, booking_id, hours, description, tags=None):
        self.cursor.execute('UPDATE bookings SET hours = ?, description = ?, tags = ? WHERE id = ?', (hours, description, tags, booking_id))
        self.conn.commit()

    def delete_booking(self, booking_id):
        self.cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        self.conn.commit()

    def get_total_hours_by_date(self, booking_date):
        self.cursor.execute('SELECT SUM(hours) FROM bookings WHERE booking_date = ?', (booking_date,))
        return self.cursor.fetchone()[0] or 0.0

    def get_weekly_totals(self, start_date):
        totals = {}
        for i in range(7):
            day = start_date + timedelta(days=i)
            totals[day] = self.get_total_hours_by_date(day)
        return totals

    def get_bookings_by_ticket(self, ticket_id):
        self.cursor.execute('''
            SELECT b.booking_date, b.hours, b.description, b.tags, b.start_time, b.end_time
            FROM bookings b WHERE b.ticket_id = ? ORDER BY b.booking_date DESC
        ''', (ticket_id,))
        return self.cursor.fetchall()

    def get_unique_tags(self):
        self.cursor.execute('SELECT DISTINCT tags FROM bookings WHERE tags IS NOT NULL')
        tags = set()
        for row in self.cursor.fetchall():
            if row[0]:
                tags.update(tag.strip() for tag in row[0].split(','))
        return sorted(tags)

    def get_monthly_totals(self, year, month):
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        self.cursor.execute('''
            SELECT t.ticket_number, SUM(b.hours)
            FROM bookings b JOIN tickets t ON b.ticket_id = t.id
            WHERE b.booking_date BETWEEN ? AND ?
            GROUP BY t.ticket_number
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_annual_totals(self, year):
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        self.cursor.execute('''
            SELECT t.ticket_number, SUM(b.hours)
            FROM bookings b JOIN tickets t ON b.ticket_id = t.id
            WHERE b.booking_date BETWEEN ? AND ?
            GROUP BY t.ticket_number
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_total_hours_this_week(self):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        return sum(self.get_total_hours_by_date(start + timedelta(days=i)) for i in range(7))

    def get_total_hours_this_month(self):
        today = date.today()
        start = date(today.year, today.month, 1)
        end = (start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        self.cursor.execute('SELECT SUM(hours) FROM bookings WHERE booking_date BETWEEN ? AND ?', (start, end))
        return self.cursor.fetchone()[0] or 0.0

    def close(self):
        if self.conn:
            self.conn.close()

# Custom Date Picker Widget
class DatePicker(ttk.Frame):
    def __init__(self, parent, default_date=None):
        super().__init__(parent)
        if default_date is None:
            default_date = datetime.now()

        self.year_var = tk.StringVar(value=str(default_date.year))
        self.month_var = tk.StringVar(value=str(default_date.month))
        self.day_var = tk.StringVar(value=str(default_date.day))

        years = list(range(2000, 2031))
        months = list(range(1, 13))
        days = list(range(1, 32))

        ttk.Label(self, text="Year:").grid(row=0, column=0, padx=5)
        self.year_combo = ttk.Combobox(self, values=years, textvariable=self.year_var, width=5)
        self.year_combo.grid(row=0, column=1)
        self.year_combo.bind("<<ComboboxSelected>>", self.update_days)
        Tooltip(self.year_combo, "Select year")

        ttk.Label(self, text="Month:").grid(row=0, column=2, padx=5)
        self.month_combo = ttk.Combobox(self, values=months, textvariable=self.month_var, width=5)
        self.month_combo.grid(row=0, column=3)
        self.month_combo.bind("<<ComboboxSelected>>", self.update_days)
        Tooltip(self.month_combo, "Select month")

        ttk.Label(self, text="Day:").grid(row=0, column=4, padx=5)
        self.day_combo = ttk.Combobox(self, values=days, textvariable=self.day_var, width=5)
        self.day_combo.grid(row=0, column=5)
        Tooltip(self.day_combo, "Select day")

        self.update_days()

    def update_days(self, event=None):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            _, days_in_month = calendar.monthrange(year, month)
            days = list(range(1, days_in_month + 1))
            self.day_combo['values'] = days
            if int(self.day_var.get()) > days_in_month:
                self.day_var.set(str(days_in_month))
        except ValueError:
            pass

    def get_date(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            return date(year, month, day)
        except ValueError:
            raise ValueError("Invalid date")

# StatusBar Class
class StatusBar(ttk.Label):
    def __init__(self, parent):
        super().__init__(parent, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def set_text(self, text, color='black'):
        self.config(text=text, foreground=color)

# Tooltip Class
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, background="yellow", relief=tk.SOLID, borderwidth=1)
        label.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
        self.tip = None

# TimerWidget Class
class TimerWidget(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.elapsed_label = ttk.Label(self, text="Elapsed: 00:00:00")
        self.elapsed_label.pack(pady=5)
        self.timer_btn = ttk.Button(self, text="Start Timer", command=self.toggle)
        self.timer_btn.pack(pady=5)
        self.app.style.configure("Running.TButton", background="green", foreground="white")
        self.app.style.configure("Stopped.TButton", background="red", foreground="white")
        self.timer_btn.config(style="Stopped.TButton")
        Tooltip(self.timer_btn, "Start/stop real-time tracking for accurate hours")

    def toggle(self):
        if not self.app.timer_running:
            self.app.start_time = time.time()
            self.app.timer_running = True
            self.timer_btn.config(text="Stop Timer", style="Running.TButton")
            self.app.status_bar.set_text("Timer running...", 'green')
            self.update_elapsed()
        else:
            end_time = time.time()
            hours = (end_time - self.app.start_time) / 3600
            self.app.hours_entry.delete(0, tk.END)
            self.app.hours_entry.insert(0, f"{hours:.2f}")
            self.app.timer_running = False
            self.timer_btn.config(text="Start Timer", style="Stopped.TButton")
            self.app.status_bar.set_text("Timer stopped", 'red')
            start_dt = datetime.fromtimestamp(self.app.start_time).isoformat()
            end_dt = datetime.fromtimestamp(end_time).isoformat()
            self.app.temp_start_time = start_dt
            self.app.temp_end_time = end_dt

    def update_elapsed(self):
        if self.app.timer_running:
            elapsed = time.time() - self.app.start_time
            hours = int(elapsed // 3600)
            mins = int((elapsed % 3600) // 60)
            secs = int(elapsed % 60)
            self.elapsed_label.config(text=f"Elapsed: {hours:02d}:{mins:02d}:{secs:02d}")
            self.elapsed_label.after(1000, self.update_elapsed)

# GUI Application Class
class TicketHourTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Hour Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.minsize(600, 400)
        self.db = DatabaseManager()

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Error.TEntry", fieldbackground="pink")
        self.style.configure("Normal.TEntry", fieldbackground="white")
        self.style.configure("Overtime.Treeview", background="orange")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dashboard Tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.setup_dashboard_tab()

        # Add Ticket Tab
        self.add_ticket_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_ticket_tab, text="Add Ticket")
        self.setup_add_ticket_tab()

        # Book Hours Tab
        self.book_hours_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.book_hours_tab, text="Book Hours")
        self.setup_book_hours_tab()

        # View Bookings Tab
        self.view_bookings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.view_bookings_tab, text="View Bookings")
        self.setup_view_bookings_tab()

        # Tickets List Tab
        self.tickets_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tickets_list_tab, text="Tickets List")
        self.setup_tickets_list_tab()

        # Reports Tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        self.setup_reports_tab()

        # Tools Tab
        self.tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_tab, text="Tools")
        self.setup_tools_tab()

        # Status Bar
        self.status_bar = StatusBar(self.root)

        # Timer variables
        self.timer_running = False
        self.start_time = None

        # Initial refresh
        self.refresh_tickets()
        self.load_tickets()
        self.update_dashboard()

        # Bind tab change to update dashboard if selected
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = self.notebook.select()
        if selected_tab == self.notebook.tabs()[0]:
            self.update_dashboard()

    def setup_dashboard_tab(self):
        frame = ttk.LabelFrame(self.dashboard_tab, text="Overview", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        # Weekly total
        ttk.Label(frame, text="This Week's Total Hours:").grid(row=0, column=0, pady=10, sticky=tk.W)
        self.week_total_label = ttk.Label(frame, text="0.0")
        self.week_total_label.grid(row=0, column=1, pady=10)

        # Monthly total
        ttk.Label(frame, text="This Month's Total Hours:").grid(row=1, column=0, pady=10, sticky=tk.W)
        self.month_total_label = ttk.Label(frame, text="0.0")
        self.month_total_label.grid(row=1, column=1, pady=10)

        # Weekly progress bar (assuming 40 hour week)
        ttk.Label(frame, text="Weekly Progress (out of 40 hours):").grid(row=2, column=0, pady=10, sticky=tk.W)
        self.week_progress = Canvas(frame, height=20, width=200, bg="lightgray")
        self.week_progress.grid(row=2, column=1, pady=10)

        # Quick links
        quick_frame = ttk.Frame(frame)
        quick_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(quick_frame, text="Add Ticket", command=lambda: self.notebook.select(self.add_ticket_tab)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Book Hours", command=lambda: self.notebook.select(self.book_hours_tab)).pack(side=tk.LEFT, padx=5)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(4, weight=1)

    def update_dashboard(self):
        week_total = self.db.get_total_hours_this_week()
        month_total = self.db.get_total_hours_this_month()
        self.week_total_label.config(text=f"{week_total:.2f}")
        self.month_total_label.config(text=f"{month_total:.2f}")

        # Progress bar
        progress_width = min(200 * (week_total / 40), 200)
        self.week_progress.delete("all")
        fill_color = "green" if week_total <= 40 else "orange"
        self.week_progress.create_rectangle(0, 0, progress_width, 20, fill=fill_color)

    def setup_add_ticket_tab(self):
        frame = ttk.LabelFrame(self.add_ticket_tab, text="Add New Ticket", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        ttk.Label(frame, text="Ticket Number (e.g., 123/49):").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.ticket_entry = ttk.Entry(frame, style="Normal.TEntry")
        self.ticket_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)
        Tooltip(self.ticket_entry, "Unique ticket identifier")

        ttk.Label(frame, text="Client Text (e.g., Client 1):").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.client_entry = ttk.Entry(frame)
        self.client_entry.grid(row=1, column=1, pady=5, sticky=tk.EW)
        Tooltip(self.client_entry, "Client or project name")

        ttk.Button(frame, text="Save Ticket", command=self.save_ticket).grid(row=2, column=0, columnspan=2, pady=10)

        frame.grid_columnconfigure(1, weight=1)

        # Live validation for duplicate ticket
        self.ticket_entry.bind("<KeyRelease>", self.validate_ticket_number)
        self.ticket_entry.focus_set()  # Auto-focus

    def validate_ticket_number(self, event=None):
        ticket_number = self.ticket_entry.get().strip()
        if ticket_number:
            self.cursor = self.db.cursor
            self.cursor.execute('SELECT COUNT(*) FROM tickets WHERE ticket_number = ?', (ticket_number,))
            if self.cursor.fetchone()[0] > 0:
                self.ticket_entry.config(style="Error.TEntry")
                self.status_bar.set_text("Ticket number already exists", 'red')
            else:
                self.ticket_entry.config(style="Normal.TEntry")
                self.status_bar.set_text("Ready")

    def save_ticket(self):
        ticket_number = self.ticket_entry.get().strip()
        client_text = self.client_entry.get().strip()
        if not ticket_number or not client_text:
            self.status_bar.set_text("Both fields are required", 'red')
            return
        if self.db.add_ticket(ticket_number, client_text):
            self.status_bar.set_text("Ticket added successfully", 'green')
            self.ticket_entry.delete(0, tk.END)
            self.client_entry.delete(0, tk.END)
            self.refresh_tickets()
        else:
            self.status_bar.set_text("Ticket number already exists", 'red')

    def setup_book_hours_tab(self):
        frame = ttk.LabelFrame(self.book_hours_tab, text="Book Hours on Ticket", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        # Date and Ticket group
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="Select Date:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.book_date_picker = DatePicker(input_frame)
        self.book_date_picker.grid(row=0, column=1, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="Select Ticket:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.ticket_combo = ttk.Combobox(input_frame)
        self.ticket_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        Tooltip(self.ticket_combo, "Choose a ticket to book hours on")

        # Hours, Desc, Tags
        ttk.Label(input_frame, text="Hours:").grid(row=2, column=0, pady=5, sticky=tk.W)
        self.hours_entry = ttk.Entry(input_frame)
        self.hours_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        Tooltip(self.hours_entry, "Enter hours worked (e.g., 4.5)")

        ttk.Label(input_frame, text="Description:").grid(row=3, column=0, pady=5, sticky=tk.W)
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=3, column=1, pady=5, sticky=tk.W)
        Tooltip(self.desc_entry, "Brief description of work")

        ttk.Label(input_frame, text="Tags (comma-separated):").grid(row=4, column=0, pady=5, sticky=tk.W)
        self.tags_entry = ttk.Entry(input_frame)
        self.tags_entry.grid(row=4, column=1, pady=5, sticky=tk.W)
        Tooltip(self.tags_entry, "Tags like development,meeting")

        self.tags_combo = ttk.Combobox(input_frame, values=self.db.get_unique_tags())
        self.tags_combo.grid(row=4, column=2, pady=5)
        self.tags_combo.bind("<<ComboboxSelected>>", self.add_selected_tag)
        Tooltip(self.tags_combo, "Select from existing tags to add")

        # Buttons and Timer
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save Booking", command=self.save_booking).pack(side=tk.LEFT, padx=5)
        self.timer_widget = TimerWidget(button_frame, self)
        self.timer_widget.pack(side=tk.LEFT, padx=5)

        frame.grid_columnconfigure(0, weight=1)

    def add_selected_tag(self, event):
        selected = self.tags_combo.get()
        current = self.tags_entry.get().strip()
        if current:
            self.tags_entry.insert(tk.END, f", {selected}")
        else:
            self.tags_entry.insert(0, selected)

    def refresh_tickets(self):
        tickets = self.db.get_all_tickets()
        if hasattr(self, 'ticket_combo'):
            self.ticket_combo['values'] = [f"{t[1]} - {t[2]}" for t in tickets]
        if hasattr(self, 'tickets_tree') and hasattr(self, 'ticket_search_entry'):
            self.load_tickets()
        self.tags_combo['values'] = self.db.get_unique_tags()  # Refresh tags if open

    def save_booking(self):
        try:
            booking_date = self.book_date_picker.get_date()
        except ValueError:
            self.status_bar.set_text("Invalid date", 'red')
            return

        selected_ticket = self.ticket_combo.get()
        tickets = self.db.get_all_tickets()
        if not selected_ticket or not any(selected_ticket == f"{t[1]} - {t[2]}" for t in tickets):
            self.status_bar.set_text("Select a valid ticket", 'red')
            return
        ticket_id = next(t[0] for t in tickets if f"{t[1]} - {t[2]}" == selected_ticket)

        hours_str = self.hours_entry.get().strip()
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValueError
        except ValueError:
            self.status_bar.set_text("Hours must be a positive number", 'red')
            return

        description = self.desc_entry.get().strip()
        if not description:
            self.status_bar.set_text("Description is required", 'red')
            return

        tags = self.tags_entry.get().strip()

        current_total = self.db.get_total_hours_by_date(booking_date)
        if current_total + hours > 8:
            if not messagebox.askyesno("Warning", f"Adding {hours} hours would exceed 8 hours for {booking_date} (current: {current_total}). Proceed?"):
                return

        start_time = getattr(self, 'temp_start_time', None)
        end_time = getattr(self, 'temp_end_time', None)
        self.db.add_booking(booking_date, ticket_id, hours, description, start_time, end_time, tags)
        self.status_bar.set_text("Booking added successfully", 'green')
        self.hours_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.refresh_tickets()
        if hasattr(self, 'temp_start_time'):
            del self.temp_start_time
            del self.temp_end_time
        self.update_dashboard()

    def setup_view_bookings_tab(self):
        frame = ttk.LabelFrame(self.view_bookings_tab, text="View Bookings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search Description or Tags:").pack(side=tk.LEFT, padx=5)
        self.booking_search_entry = ttk.Entry(search_frame)
        self.booking_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        Tooltip(self.booking_search_entry, "Search in description or tags")

        ttk.Button(search_frame, text="Search", command=self.load_bookings_by_date).pack(side=tk.LEFT, padx=5)

        date_frame = ttk.Frame(frame)
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Select Date:").pack(side=tk.LEFT, padx=5)
        self.view_date_picker = DatePicker(date_frame)
        self.view_date_picker.pack(side=tk.LEFT, padx=5)

        self.bookings_tree = ttk.Treeview(frame, columns=("ID", "Ticket", "Hours", "Description", "Tags", "Start", "End"), show="headings")
        self.bookings_tree.heading("ID", text="ID")
        self.bookings_tree.heading("Ticket", text="Ticket")
        self.bookings_tree.heading("Hours", text="Hours")
        self.bookings_tree.heading("Description", text="Description")
        self.bookings_tree.heading("Tags", text="Tags")
        self.bookings_tree.heading("Start", text="Start Time")
        self.bookings_tree.heading("End", text="End Time")
        self.bookings_tree.column("ID", width=0, stretch=tk.NO)
        self.bookings_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.total_label = ttk.Label(frame, text="Total Hours: 0.0")
        self.total_label.pack(pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Load By Date", command=self.load_bookings_by_date).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Load bookings for selected date")

        ttk.Button(button_frame, text="Show All", command=self.show_all_bookings).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Show all bookings")

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected_booking).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Edit the selected booking")

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected_booking).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Delete the selected booking")

        # Auto-size columns on load
        self.bookings_tree.bind("<Configure>", lambda e: [self.bookings_tree.column(col, width=tk.AUTO) for col in self.bookings_tree["columns"]])

    def load_bookings_by_date(self):
        try:
            booking_date = self.view_date_picker.get_date()
        except ValueError:
            self.status_bar.set_text("Invalid date", 'red')
            return

        search_term = self.booking_search_entry.get().strip().lower()

        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        bookings = self.db.get_bookings_by_date(booking_date)
        for booking in bookings:
            booking_id, ticket, hours, desc, tags, start, end = booking
            if (search_term in desc.lower() or (tags and search_term in tags.lower())) or not search_term:
                iid = self.bookings_tree.insert("", "end", values=(booking_id, ticket, hours, desc, tags or '', start or '', end or ''))
                if hours > 8:
                    self.bookings_tree.item(iid, tags=('overtime',))

        total_hours = self.db.get_total_hours_by_date(booking_date)
        self.total_label.config(text=f"Total Hours: {total_hours:.2f}")
        self.bookings_tree.tag_configure('overtime', background='orange')

    def show_all_bookings(self):
        search_term = self.booking_search_entry.get().strip().lower()

        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        all_bookings = self.db.get_all_bookings()
        current_date = None
        total_hours = 0.0
        grand_total = 0.0
        for booking in all_bookings:
            date_str, ticket, hours, desc, booking_id, tags, start, end = booking
            if (search_term in desc.lower() or (tags and search_term in tags.lower())) or not search_term:
                if date_str != current_date:
                    if current_date:
                        self.bookings_tree.insert("", "end", values=("", "", f"Subtotal: {total_hours:.2f}", "", "", "", ""))
                    self.bookings_tree.insert("", "end", values=("", f"Date: {date_str}", "", "", "", "", ""))
                    current_date = date_str
                    total_hours = 0.0
                iid = self.bookings_tree.insert("", "end", values=(booking_id, ticket, hours, desc, tags or '', start or '', end or ''))
                if hours > 8:
                    self.bookings_tree.item(iid, tags=('overtime',))
                total_hours += hours
                grand_total += hours
        if current_date:
            self.bookings_tree.insert("", "end", values=("", "", f"Subtotal: {total_hours:.2f}", "", "", "", ""))
        self.bookings_tree.insert("", "end", values=("", "", f"Grand Total: {grand_total:.2f}", "", "", "", ""))

        self.bookings_tree.tag_configure('overtime', background='orange')

    def edit_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            self.status_bar.set_text("Select a booking to edit", 'red')
            return
        item = self.bookings_tree.item(selected[0])
        values = item['values']
        if len(values) < 7 or "Date:" in values[1] or "Subtotal:" in values[2]:
            self.status_bar.set_text("Select a valid booking entry", 'red')
            return
        booking_id, _, hours, desc, tags, _, _ = values

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Booking")
        edit_window.geometry("300x250")

        ttk.Label(edit_window, text="Hours:").pack(pady=5)
        hours_entry = ttk.Entry(edit_window)
        hours_entry.insert(0, str(hours))
        hours_entry.pack()

        ttk.Label(edit_window, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(edit_window)
        desc_entry.insert(0, desc)
        desc_entry.pack()

        ttk.Label(edit_window, text="Tags (comma-separated):").pack(pady=5)
        tags_entry = ttk.Entry(edit_window)
        tags_entry.insert(0, tags)
        tags_entry.pack()

        def save_edit():
            try:
                new_hours = float(hours_entry.get().strip())
                if new_hours <= 0:
                    raise ValueError
            except ValueError:
                self.status_bar.set_text("Hours must be a positive number", 'red')
                return
            new_desc = desc_entry.get().strip()
            if not new_desc:
                self.status_bar.set_text("Description is required", 'red')
                return
            new_tags = tags_entry.get().strip()
            self.db.update_booking(booking_id, new_hours, new_desc, new_tags)
            self.status_bar.set_text("Booking updated", 'green')
            edit_window.destroy()
            self.load_bookings_by_date()
            self.update_dashboard()

        ttk.Button(edit_window, text="Save", command=save_edit).pack(pady=10)

    def delete_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            self.status_bar.set_text("Select a booking to delete", 'red')
            return
        item = self.bookings_tree.item(selected[0])
        values = item['values']
        if len(values) < 7 or "Date:" in values[1] or "Subtotal:" in values[2]:
            self.status_bar.set_text("Select a valid booking entry", 'red')
            return
        booking_id = values[0]
        if messagebox.askyesno("Confirm", "Delete this booking?"):
            self.db.delete_booking(booking_id)
            self.status_bar.set_text("Booking deleted", 'green')
            self.load_bookings_by_date()
            self.update_dashboard()

    def setup_tickets_list_tab(self):
        frame = ttk.LabelFrame(self.tickets_list_tab, text="Tickets List", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search Ticket/Client:").pack(side=tk.LEFT, padx=5)
        self.ticket_search_entry = ttk.Entry(search_frame)
        self.ticket_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        Tooltip(self.ticket_search_entry, "Search by ticket number or client")

        ttk.Button(search_frame, text="Search", command=self.load_tickets).pack(side=tk.LEFT, padx=5)

        self.tickets_tree = ttk.Treeview(frame, columns=("ID", "Ticket Number", "Client Text", "Total Hours"), show="headings")
        self.tickets_tree.heading("ID", text="ID")
        self.tickets_tree.heading("Ticket Number", text="Ticket Number")
        self.tickets_tree.heading("Client Text", text="Client Text")
        self.tickets_tree.heading("Total Hours", text="Total Hours")
        self.tickets_tree.column("ID", width=0, stretch=tk.NO)
        self.tickets_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected_ticket).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Edit the selected ticket")

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected_ticket).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Delete the selected ticket and bookings")

        ttk.Button(button_frame, text="View Bookings for Selected", command=self.view_bookings_for_ticket).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "View bookings for the selected ticket")

        # Auto-size
        self.tickets_tree.bind("<Configure>", lambda e: [self.tickets_tree.column(col, width=tk.AUTO) for col in self.tickets_tree["columns"]])

    def load_tickets(self):
        if not hasattr(self, 'ticket_search_entry'):
            return
        search_term = self.ticket_search_entry.get().strip().lower()

        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)

        tickets = self.db.get_all_tickets()
        for ticket in tickets:
            ticket_id, number, client = ticket
            total_hours = sum(h[1] for h in self.db.get_bookings_by_ticket(ticket_id))
            if search_term in number.lower() or search_term in client.lower() or not search_term:
                self.tickets_tree.insert("", "end", values=(ticket_id, number, client, f"{total_hours:.2f}"))

    def setup_reports_tab(self):
        frame = ttk.LabelFrame(self.reports_tab, text="Reports", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        select_frame = ttk.Frame(frame)
        select_frame.pack(fill=tk.X)

        ttk.Label(select_frame, text="Select Period:").pack(side=tk.LEFT, padx=5)
        self.report_type = ttk.Combobox(select_frame, values=["Weekly", "Monthly", "Annual"])
        self.report_type.set("Weekly")
        self.report_type.pack(side=tk.LEFT, padx=5)
        Tooltip(self.report_type, "Choose report type")

        self.report_date_picker = DatePicker(select_frame)
        self.report_date_picker.pack(side=tk.LEFT, padx=5)

        self.reports_tree = ttk.Treeview(frame, columns=("Period/Ticket", "Total Hours"), show="headings")
        self.reports_tree.heading("Period/Ticket", text="Period/Ticket")
        self.reports_tree.heading("Total Hours", text="Total Hours")
        self.reports_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Load Report", command=self.load_report).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Load the selected report")

        ttk.Button(button_frame, text="Generate Summary", command=self.generate_summary).pack(side=tk.LEFT, padx=5)
        Tooltip(button_frame.winfo_children()[-1], "Generate text summary for printing")

        # Auto-size
        self.reports_tree.bind("<Configure>", lambda e: [self.reports_tree.column(col, width=tk.AUTO) for col in self.reports_tree["columns"]])

    def load_report(self):
        try:
            start_date = self.report_date_picker.get_date()
        except ValueError:
            self.status_bar.set_text("Invalid date", 'red')
            return

        report_type = self.report_type.get()

        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)

        if report_type == "Weekly":
            totals = self.db.get_weekly_totals(start_date)
            grand_total = 0.0
            for day, hours in totals.items():
                self.reports_tree.insert("", "end", values=(day, f"{hours:.2f}"))
                grand_total += hours
            self.reports_tree.insert("", "end", values=("Weekly Total", f"{grand_total:.2f}"))
        elif report_type == "Monthly":
            year = start_date.year
            month = start_date.month
            monthly_totals = self.db.get_monthly_totals(year, month)
            grand_total = 0.0
            for ticket, hours in monthly_totals:
                self.reports_tree.insert("", "end", values=(ticket, f"{hours:.2f}"))
                grand_total += hours
            self.reports_tree.insert("", "end", values=("Monthly Total", f"{grand_total:.2f}"))
        elif report_type == "Annual":
            year = start_date.year
            annual_totals = self.db.get_annual_totals(year)
            grand_total = 0.0
            for ticket, hours in annual_totals:
                self.reports_tree.insert("", "end", values=(ticket, f"{hours:.2f}"))
                grand_total += hours
            self.reports_tree.insert("", "end", values=("Annual Total", f"{grand_total:.2f}"))

        self.status_bar.set_text("Report loaded", 'green')

    def generate_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Report Summary")
        summary_window.geometry("400x300")

        text = tk.Text(summary_window)
        text.pack(fill=tk.BOTH, expand=True)

        for child in self.reports_tree.get_children():
            values = self.reports_tree.item(child)['values']
            text.insert(tk.END, f"{values[0]}: {values[1]}\n")

        ttk.Button(summary_window, text="Copy to Clipboard", command=lambda: self.root.clipboard_append(text.get("1.0", tk.END))).pack(pady=10)
        self.status_bar.set_text("Summary generated", 'green')

    def setup_tools_tab(self):
        frame = ttk.LabelFrame(self.tools_tab, text="Tools", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        ttk.Button(frame, text="Export Bookings to CSV", command=self.export_to_csv).grid(row=0, column=0, pady=10, padx=10, sticky=tk.EW)
        Tooltip(frame.winfo_children()[-1], "Export all bookings to CSV file")

        ttk.Button(frame, text="Import Tickets from CSV", command=self.import_tickets_from_csv).grid(row=1, column=0, pady=10, padx=10, sticky=tk.EW)
        Tooltip(frame.winfo_children()[-1], "Import tickets from CSV (format: Ticket Number,Client Text)")

        ttk.Button(frame, text="Backup Database", command=self.backup_database).grid(row=2, column=0, pady=10, padx=10, sticky=tk.EW)
        Tooltip(frame.winfo_children()[-1], "Backup the database file")

        frame.grid_columnconfigure(0, weight=1)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        all_bookings = self.db.get_all_bookings()
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Ticket", "Hours", "Description", "Tags", "Start Time", "End Time"])
            writer.writerows([b[:4] + [b[5] or '', b[6] or '', b[7] or ''] for b in all_bookings])
        self.status_bar.set_text("Exported to CSV", 'green')

    def import_tickets_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            added = 0
            duplicates = 0
            for row in reader:
                if len(row) >= 2:
                    ticket_number, client_text = row[0].strip(), row[1].strip()
                    if self.db.add_ticket(ticket_number, client_text):
                        added += 1
                    else:
                        duplicates += 1
        messagebox.showinfo("Import Result", f"Added {added} tickets. Skipped {duplicates} duplicates.")
        self.refresh_tickets()
        self.status_bar.set_text("Tickets imported", 'green')

    def backup_database(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("DB files", "*.db")])
        if not file_path:
            return
        shutil.copy(self.db.db_name, file_path)
        self.status_bar.set_text("Database backed up", 'green')

    def on_closing(self):
        self.db.close()
        self.root.destroy()

    # Placeholder for missing methods (edit_selected_ticket, delete_selected_ticket, view_bookings_for_ticket)
    # Implement these based on your requirements.
    def edit_selected_ticket(self):
        selected = self.tickets_tree.selection()
        if not selected:
            self.status_bar.set_text("Select a ticket to edit", 'red')
            return
        item = self.tickets_tree.item(selected[0])
        values = item['values']
        ticket_id, number, client, _ = values

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Ticket")
        edit_window.geometry("300x200")

        ttk.Label(edit_window, text="Ticket Number:").pack(pady=5)
        number_entry = ttk.Entry(edit_window, style="Normal.TEntry")
        number_entry.insert(0, number)
        number_entry.pack()

        ttk.Label(edit_window, text="Client Text:").pack(pady=5)
        client_entry = ttk.Entry(edit_window)
        client_entry.insert(0, client)
        client_entry.pack()

        def save_edit():
            new_number = number_entry.get().strip()
            new_client = client_entry.get().strip()
            if not new_number or not new_client:
                self.status_bar.set_text("Both fields are required", 'red')
                return
            if self.db.update_ticket(ticket_id, new_number, new_client):
                self.status_bar.set_text("Ticket updated", 'green')
                edit_window.destroy()
                self.load_tickets()
                self.refresh_tickets()
            else:
                self.status_bar.set_text("Ticket number already exists", 'red')

        ttk.Button(edit_window, text="Save", command=save_edit).pack(pady=10)

        # Live validation for duplicate ticket in edit
        def validate_edit(event=None):
            new_number = number_entry.get().strip()
            if new_number and new_number != number:
                self.cursor = self.db.cursor
                self.cursor.execute('SELECT COUNT(*) FROM tickets WHERE ticket_number = ?', (new_number,))
                if self.cursor.fetchone()[0] > 0:
                    number_entry.config(style="Error.TEntry")
                    self.status_bar.set_text("Ticket number already exists", 'red')
                else:
                    number_entry.config(style="Normal.TEntry")
                    self.status_bar.set_text("Ready")

        number_entry.bind("<KeyRelease>", validate_edit)

    def delete_selected_ticket(self):
        selected = self.tickets_tree.selection()
        if not selected:
            self.status_bar.set_text("Select a ticket to delete", 'red')
            return
        ticket_id = self.tickets_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this ticket and all its bookings?"):
            self.db.delete_ticket(ticket_id)
            self.status_bar.set_text("Ticket deleted", 'green')
            self.load_tickets()
            self.refresh_tickets()
            self.update_dashboard()

    def view_bookings_for_ticket(self):
        selected = self.tickets_tree.selection()
        if not selected:
            self.status_bar.set_text("Select a ticket to view bookings", 'red')
            return
        ticket_id = self.tickets_tree.item(selected[0])['values'][0]

        view_window = tk.Toplevel(self.root)
        view_window.title("Bookings for Ticket")
        view_window.geometry("600x400")

        tree = ttk.Treeview(view_window, columns=("Date", "Hours", "Description", "Tags", "Start", "End"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Hours", text="Hours")
        tree.heading("Description", text="Description")
        tree.heading("Tags", text="Tags")
        tree.heading("Start", text="Start Time")
        tree.heading("End", text="End Time")
        tree.pack(fill=tk.BOTH, expand=True, pady=10)

        bookings = self.db.get_bookings_by_ticket(ticket_id)
        total_hours = 0.0
        for booking in bookings:
            date_str, hours, desc, tags, start, end = booking
            tree.insert("", "end", values=(date_str, hours, desc, tags or '', start or '', end or ''))
            total_hours += hours

        total_label = ttk.Label(view_window, text=f"Total Hours: {total_hours:.2f}")
        total_label.pack(pady=5)

        tree.bind("<Configure>", lambda e: [tree.column(col, width=tk.AUTO) for col in tree["columns"]])

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketHourTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()