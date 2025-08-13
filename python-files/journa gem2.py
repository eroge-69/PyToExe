import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import datetime
import os
import sys
import json
import base64
import threading
import time
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

# Conditional import for Windows-specific features
try:
    import winreg
except ImportError:
    winreg = None # Set to None on non-Windows systems

# Conditional import for persistent toast notifications
try:
    from win10toast_persist import ToastNotifier
except ImportError:
    ToastNotifier = None


class PasswordDialog(simpledialog.Dialog):
    """A dialog for entering and confirming passwords."""
    def __init__(self, parent, title, prompt1, prompt2=None, prompt3=None):
        self.prompt1 = prompt1
        self.prompt2 = prompt2
        self.prompt3 = prompt3
        self.password = None
        self.new_password = None
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text=self.prompt1).grid(row=0, sticky='w', columnspan=2)
        self.entry1 = ttk.Entry(master, show="*")
        self.entry1.grid(row=1, sticky='ew', columnspan=2, pady=(0, 5))
        
        if self.prompt2:
            ttk.Label(master, text=self.prompt2).grid(row=2, sticky='w', columnspan=2)
            self.entry2 = ttk.Entry(master, show="*")
            self.entry2.grid(row=3, sticky='ew', columnspan=2, pady=(0, 5))
        
        if self.prompt3:
            ttk.Label(master, text=self.prompt3).grid(row=4, sticky='w', columnspan=2)
            self.entry3 = ttk.Entry(master, show="*")
            self.entry3.grid(row=5, sticky='ew', columnspan=2)

        return self.entry1

    def apply(self):
        p1 = self.entry1.get()
        if self.prompt2 and self.prompt3: # Change password case
            p2 = self.entry2.get()
            p3 = self.entry3.get()
            if not p2 or len(p2) < 4:
                messagebox.showwarning("Invalid Password", "New password must be at least 4 characters.", parent=self)
                self.password = None
            elif p2 != p3:
                messagebox.showwarning("Password Mismatch", "The new passwords do not match.", parent=self)
                self.password = None
            else:
                self.password = p1
                self.new_password = p2
        elif self.prompt2: # Create password case
            p2 = self.entry2.get()
            if not p1 or len(p1) < 4:
                messagebox.showwarning("Invalid Password", "Password must be at least 4 characters.", parent=self)
                self.password = None
            elif p1 != p2:
                messagebox.showwarning("Password Mismatch", "The passwords do not match.", parent=self)
                self.password = None
            else:
                self.password = p1
        else: # Unlock case
            self.password = p1

class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Journal")
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cipher = None
        self.reminder_active = True

        self.init_database()
        self.setup_ui()
        
        self.notebook.grid_remove() 
        self.root.after(100, self.attempt_unlock)

    def attempt_unlock(self):
        app_data_dir = os.path.join(os.path.expanduser("~"), ".DailyJournalApp")
        self.salt_path = os.path.join(app_data_dir, "journal.salt")

        if not os.path.exists(self.salt_path):
            dialog = PasswordDialog(self.root, "Create Master Password", 
                                    "Create a password for your journal (min 4 chars):", 
                                    "Confirm password:")
            password = dialog.password
            if not password:
                self.root.destroy()
                return
            
            salt = os.urandom(16)
            self.setup_encryption(password, salt)
            with open(self.salt_path, "wb") as f:
                f.write(salt)
            
            ver_hash = hashlib.sha256((password + salt.hex()).encode()).hexdigest()
            self.set_setting('password_verification_hash', ver_hash)
            self.initialize_main_app()
        else:
            with open(self.salt_path, "rb") as f:
                salt = f.read()
            
            while self.cipher is None:
                dialog = PasswordDialog(self.root, "Unlock Journal", "Enter your password:")
                password = dialog.password
                if not password:
                    self.root.destroy()
                    return

                ver_hash = hashlib.sha256((password + salt.hex()).encode()).hexdigest()
                saved_hash = self.get_setting('password_verification_hash')

                if ver_hash == saved_hash:
                    self.setup_encryption(password, salt)
                    self.initialize_main_app()
                else:
                    messagebox.showerror("Incorrect Password", "The password you entered is incorrect. Please try again.", parent=self.root)

    def initialize_main_app(self):
        self.notebook.grid()
        self.load_settings()
        self.load_journal_entry_for_today()
        self.update_calendar()
        self.load_behaviors()
        self.update_analysis()
        self.load_emotions_to_settings()

        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()

    def setup_encryption(self, password, salt):
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self.cipher = Fernet(key)
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to set up encryption: {e}")
            self.root.destroy()

    def encrypt_data(self, data):
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()

    def init_database(self):
        db_dir = os.path.join(os.path.expanduser("~"), ".DailyJournalApp")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "journal.db")
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute('CREATE TABLE IF NOT EXISTS journal_entries (id INTEGER PRIMARY KEY, date TEXT UNIQUE, content BLOB, word_count INTEGER, completed INTEGER DEFAULT 0)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS emotions (id INTEGER PRIMARY KEY, entry_id INTEGER, emotion TEXT, FOREIGN KEY (entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS behaviors (id INTEGER PRIMARY KEY, name TEXT UNIQUE, attribute TEXT)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS behavior_instances (id INTEGER PRIMARY KEY, behavior_id INTEGER, date TEXT, frequency INTEGER, notes BLOB, FOREIGN KEY (behavior_id) REFERENCES behaviors (id) ON DELETE CASCADE)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS emotion_definitions (name TEXT PRIMARY KEY)')
            
            self.cursor.execute("SELECT count(*) FROM emotion_definitions")
            if self.cursor.fetchone()[0] == 0:
                default_emotions = ["Happy", "Sad", "Angry", "Anxious", "Calm", "Excited", "Stressed", "Grateful"]
                self.cursor.executemany("INSERT INTO emotion_definitions (name) VALUES (?)", [(e,) for e in default_emotions])
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.root.destroy()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.primary_color, self.secondary_color, self.accent_color = "#4285F4", "#F8F9FA", "#EA4335"
        self.text_color, self.success_color, self.border_color = "#202124", "#34A853", "#DADCE0"
        self.light_bg_color, self.header_color = "#FFFFFF", "#5F6368"
        self.root.configure(bg=self.secondary_color)
        self.style.configure('TNotebook', background=self.secondary_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=[16, 8], background=self.secondary_color, foreground=self.header_color, borderwidth=0, font=('Segoe UI', 11))
        self.style.map('TNotebook.Tab', background=[('selected', self.secondary_color)], foreground=[('selected', self.primary_color)])
        self.style.configure('TFrame', background=self.secondary_color)
        self.style.configure('Card.TFrame', background=self.light_bg_color, relief='solid', borderwidth=1, bordercolor=self.border_color)
        self.style.configure('TButton', background=self.primary_color, foreground=self.light_bg_color, padding=[12, 8], font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#3367D6')])
        self.style.configure('Success.TButton', background=self.success_color, foreground=self.light_bg_color)
        self.style.map('Success.TButton', background=[('active', '#2B9348')])
        self.style.configure('TLabel', background=self.secondary_color, foreground=self.text_color, font=('Segoe UI', 10))
        self.style.configure('Card.TLabel', background=self.light_bg_color)
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground=self.text_color)
        self.style.configure('Subheader.TLabel', font=('Segoe UI', 12), foreground=self.header_color)
        self.style.configure('TEntry', fieldbackground=self.light_bg_color, borderwidth=1, relief='solid', bordercolor=self.border_color, font=('Segoe UI', 10), padding=5)
        self.style.map('TEntry', bordercolor=[('focus', self.primary_color)])
        self.style.configure('TProgressbar', background=self.primary_color, troughcolor=self.border_color, borderwidth=0, thickness=8)
        self.style.configure('Success.TProgressbar', background=self.success_color)
        self.style.configure('Treeview', rowheight=25, fieldbackground=self.light_bg_color, font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background=self.secondary_color, borderwidth=0)
        self.style.map('Treeview.Heading', background=[('active', self.border_color)])
        self.style.configure('Toolbutton', padding=5, font=('Segoe UI', 9), borderwidth=1)
        self.style.map('Toolbutton', background=[('selected', self.primary_color), ('!selected', self.light_bg_color)], foreground=[('selected', self.light_bg_color), ('!selected', self.text_color)], bordercolor=[('selected', self.primary_color), ('!selected', self.border_color)])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.journal_tab, self.calendar_tab, self.behavior_tab, self.analysis_tab, self.settings_tab = (ttk.Frame(self.notebook, padding=10) for _ in range(5))
        self.notebook.add(self.journal_tab, text="Journal")
        self.notebook.add(self.calendar_tab, text="Calendar")
        self.notebook.add(self.behavior_tab, text="Behaviors")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.settings_tab, text="Settings")

        self.setup_journal_tab()
        self.setup_calendar_tab()
        self.setup_behavior_tab()
        self.setup_analysis_tab()
        self.setup_settings_tab()

    def setup_journal_tab(self):
        self.journal_tab.grid_columnconfigure(0, weight=1)
        self.journal_tab.grid_rowconfigure(1, weight=1)
        ttk.Label(self.journal_tab, text=datetime.date.today().strftime('%A, %B %d, %Y'), style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 20), padx=10)
        entry_card = ttk.Frame(self.journal_tab, style='Card.TFrame', padding=20)
        entry_card.grid(row=1, column=0, sticky="nsew", padx=10)
        entry_card.grid_columnconfigure(0, weight=1)
        entry_card.grid_rowconfigure(1, weight=1)
        self.journal_text = tk.Text(entry_card, wrap=tk.WORD, font=('Segoe UI', 11), bg=self.light_bg_color, fg=self.text_color, padx=15, pady=15, borderwidth=0, relief="flat", undo=True)
        self.journal_text.grid(row=1, column=0, sticky="nsew")
        self.journal_text.bind("<KeyRelease>", self.update_word_count)
        scrollbar = ttk.Scrollbar(entry_card, command=self.journal_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.journal_text.config(yscrollcommand=scrollbar.set)
        count_frame = ttk.Frame(entry_card, style='Card.TFrame')
        count_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        count_frame.grid_columnconfigure(1, weight=1)
        self.word_count_var = tk.StringVar(value="0 / 200 words")
        self.word_count_label = ttk.Label(count_frame, textvariable=self.word_count_var, style='Card.TLabel')
        self.word_count_label.grid(row=0, column=0, sticky="w", padx=10)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(count_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=10)
        self.emotions_card = ttk.LabelFrame(self.journal_tab, text="How are you feeling today?", style='Card.TFrame', padding=20)
        self.emotions_card.grid(row=2, column=0, sticky="ew", padx=10, pady=20)
        self.refresh_emotions_display()
        self.save_button = ttk.Button(self.journal_tab, text="Save Journal Entry", command=self.save_journal_entry, style='Success.TButton')
        self.save_button.grid(row=3, column=0, pady=(0, 10), padx=10, sticky="e")

    def refresh_emotions_display(self):
        for widget in self.emotions_card.winfo_children():
            widget.destroy()
        self.emotion_vars = {}
        emotions = self.get_all_emotions()
        for i, emotion in enumerate(emotions):
            var = tk.IntVar()
            self.emotion_vars[emotion] = var
            cb = ttk.Checkbutton(self.emotions_card, text=emotion, variable=var, style='Toolbutton')
            cb.grid(row=i // 5, column=i % 5, padx=5, pady=5, sticky="ew")

    def setup_calendar_tab(self):
        self.calendar_tab.grid_columnconfigure(0, weight=1)
        self.calendar_tab.grid_columnconfigure(1, weight=1)
        self.calendar_tab.grid_rowconfigure(0, weight=1)
        calendar_card = ttk.Frame(self.calendar_tab, style='Card.TFrame', padding=20)
        calendar_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        calendar_card.grid_columnconfigure(0, weight=1)
        calendar_card.grid_rowconfigure(2, weight=1)
        nav_frame = ttk.Frame(calendar_card, style='Card.TFrame')
        nav_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        nav_frame.grid_columnconfigure(1, weight=1)
        self.current_month, self.current_year = datetime.datetime.now().month, datetime.datetime.now().year
        ttk.Button(nav_frame, text="<", width=3, command=self.prev_month).grid(row=0, column=0)
        self.month_year_label = ttk.Label(nav_frame, text="", style='Header.TLabel', background=self.light_bg_color, anchor='center')
        self.month_year_label.grid(row=0, column=1, sticky="ew")
        ttk.Button(nav_frame, text=">", width=3, command=self.next_month).grid(row=0, column=2)
        ttk.Button(nav_frame, text="Today", command=self.go_to_today).grid(row=0, column=3, padx=(10, 0))
        days_header_frame = ttk.Frame(calendar_card, style='Card.TFrame')
        days_header_frame.grid(row=1, column=0, sticky="ew", pady=5)
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            days_header_frame.grid_columnconfigure(i, weight=1)
            ttk.Label(days_header_frame, text=day, anchor='center', font=('Segoe UI', 10, 'bold'), background=self.light_bg_color).grid(row=0, column=i, sticky="ew")
        self.days_frame = ttk.Frame(calendar_card, style='Card.TFrame')
        self.days_frame.grid(row=2, column=0, sticky="nsew")
        self.day_frames, self.day_labels, self.day_content_labels = [], [], []
        for r in range(6):
            self.days_frame.grid_rowconfigure(r, weight=1)
            for c in range(7):
                self.days_frame.grid_columnconfigure(c, weight=1)
                day_f = ttk.Frame(self.days_frame, relief='solid', borderwidth=1)
                day_f.grid(row=r, column=c, sticky="nsew")
                day_f.grid_rowconfigure(1, weight=1)
                day_f.grid_columnconfigure(0, weight=1)
                day_l = ttk.Label(day_f)
                day_l.grid(row=0, column=0, sticky="ne", padx=5, pady=2)
                content_l = ttk.Label(day_f)
                content_l.grid(row=1, column=0, sticky="s")
                for widget in [day_f, day_l, content_l]:
                    widget.bind("<Button-1>", lambda e, r=r, c=c: self.select_date(r, c))
                self.day_frames.append(day_f)
                self.day_labels.append(day_l)
                self.day_content_labels.append(content_l)
        self.setup_calendar_styles()
        self.entry_display_card = ttk.Frame(self.calendar_tab, style='Card.TFrame', padding=20)
        self.entry_display_card.grid(row=0, column=1, sticky="nsew")
        self.entry_display_card.grid_columnconfigure(0, weight=1)
        self.entry_display_card.grid_rowconfigure(1, weight=1)
        self.selected_date_label = ttk.Label(self.entry_display_card, text="Select a date to view entry", style='Subheader.TLabel', background=self.light_bg_color)
        self.selected_date_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        entry_text_frame = ttk.Frame(self.entry_display_card, style='Card.TFrame')
        entry_text_frame.grid(row=1, column=0, sticky="nsew")
        entry_text_frame.grid_columnconfigure(0, weight=1)
        entry_text_frame.grid_rowconfigure(0, weight=1)
        self.entry_text_display = tk.Text(entry_text_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Segoe UI', 11), bg=self.light_bg_color, borderwidth=0)
        self.entry_text_display.grid(row=0, column=0, sticky="nsew")
        entry_scrollbar = ttk.Scrollbar(entry_text_frame, command=self.entry_text_display.yview)
        entry_scrollbar.grid(row=0, column=1, sticky="ns")
        self.entry_text_display.config(yscrollcommand=entry_scrollbar.set)
        emotions_frame = ttk.Frame(self.entry_display_card, style='Card.TFrame')
        emotions_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(emotions_frame, text="Emotions:", style='Subheader.TLabel', background=self.light_bg_color).pack(side=tk.LEFT)
        self.emotions_display_label = ttk.Label(emotions_frame, text="None", background=self.light_bg_color, wraplength=300)
        self.emotions_display_label.pack(side=tk.LEFT, padx=5)

    def setup_calendar_styles(self):
        for state in ['CalendarDay', 'OtherMonth', 'Today', 'Selected']:
            bg, fg, border, font = self.light_bg_color, self.text_color, self.border_color, ('Segoe UI', 10)
            if state == 'OtherMonth': bg, fg = self.secondary_color, self.header_color
            elif state == 'Today': bg, border, fg, font = '#E8F0FE', self.primary_color, self.primary_color, ('Segoe UI', 10, 'bold')
            elif state == 'Selected': bg, border = '#D2E3FC', self.primary_color
            self.style.configure(f'{state}.TFrame', background=bg, bordercolor=border)
            self.style.configure(f'{state}Number.TLabel', background=bg, foreground=fg, font=font)
            self.style.configure(f'{state}Content.TLabel', background=bg)

    def setup_behavior_tab(self):
        self.behavior_tab.grid_columnconfigure(0, weight=1); self.behavior_tab.grid_columnconfigure(1, weight=2); self.behavior_tab.grid_rowconfigure(0, weight=1)
        left_col = ttk.Frame(self.behavior_tab); left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10)); left_col.grid_rowconfigure(1, weight=1); left_col.grid_columnconfigure(0, weight=1)
        add_card = ttk.LabelFrame(left_col, text="Define Behavior", style='Card.TFrame', padding=15); add_card.grid(row=0, column=0, sticky="ew"); add_card.grid_columnconfigure(1, weight=1)
        ttk.Label(add_card, text="Name:", style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=2); self.new_behavior_name = ttk.Entry(add_card); self.new_behavior_name.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(add_card, text="Attribute:", style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=2); self.attribute_var = tk.StringVar(value="Neutral"); self.attribute_menu = ttk.Combobox(add_card, textvariable=self.attribute_var, values=["Constructive", "Neutral", "Destructive"], state="readonly"); self.attribute_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(add_card, text="Add Behavior", command=self.add_behavior).grid(row=2, column=1, sticky="e", padx=5, pady=10)
        list_card = ttk.LabelFrame(left_col, text="Defined Behaviors", style='Card.TFrame', padding=15); list_card.grid(row=1, column=0, sticky="nsew", pady=(20, 0)); list_card.grid_columnconfigure(0, weight=1); list_card.grid_rowconfigure(0, weight=1)
        cols = ('name', 'attribute'); self.behaviors_tree = ttk.Treeview(list_card, columns=cols, show='headings', selectmode='browse'); self.behaviors_tree.heading('name', text='Behavior Name'); self.behaviors_tree.heading('attribute', text='Attribute'); self.behaviors_tree.column('attribute', width=100, anchor='center'); self.behaviors_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll = ttk.Scrollbar(list_card, orient="vertical", command=self.behaviors_tree.yview); tree_scroll.grid(row=0, column=1, sticky='ns'); self.behaviors_tree.configure(yscrollcommand=tree_scroll.set)
        btn_frame = ttk.Frame(list_card, style='Card.TFrame'); btn_frame.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0)); ttk.Button(btn_frame, text="Delete", command=self.delete_behavior).pack()
        right_col = ttk.Frame(self.behavior_tab); right_col.grid(row=0, column=1, sticky="nsew"); right_col.grid_rowconfigure(1, weight=1); right_col.grid_columnconfigure(0, weight=1)
        track_card = ttk.LabelFrame(right_col, text="Track Behavior", style='Card.TFrame', padding=15); track_card.grid(row=0, column=0, sticky="ew"); track_card.grid_columnconfigure(1, weight=1)
        ttk.Label(track_card, text="Behavior:", style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=2); self.behavior_var = tk.StringVar(); self.behavior_dropdown = ttk.Combobox(track_card, textvariable=self.behavior_var, state="readonly"); self.behavior_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(track_card, text="Date:", style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=2); self.behavior_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d")); self.behavior_date_entry = ttk.Entry(track_card, textvariable=self.behavior_date_var); self.behavior_date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(track_card, text="Frequency:", style='Card.TLabel').grid(row=2, column=0, sticky="w", pady=2); self.frequency_var = tk.IntVar(value=1); ttk.Spinbox(track_card, from_=1, to=100, textvariable=self.frequency_var, width=5).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(track_card, text="Notes:", style='Card.TLabel').grid(row=3, column=0, sticky="nw", pady=2); self.behavior_notes = tk.Text(track_card, height=4, font=('Segoe UI', 10), relief='solid', borderwidth=1); self.behavior_notes.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(track_card, text="Record Behavior", command=self.record_behavior, style='Success.TButton').grid(row=4, column=1, sticky="e", padx=5, pady=10)
        history_card = ttk.LabelFrame(right_col, text="Recent History", style='Card.TFrame', padding=15); history_card.grid(row=1, column=0, sticky="nsew", pady=(20, 0)); history_card.grid_columnconfigure(0, weight=1); history_card.grid_rowconfigure(0, weight=1)
        hist_cols = ('date', 'name', 'frequency'); self.history_tree = ttk.Treeview(history_card, columns=hist_cols, show='headings'); self.history_tree.heading('date', text='Date'); self.history_tree.column('date', width=100); self.history_tree.heading('name', text='Behavior'); self.history_tree.heading('frequency', text='Frequency'); self.history_tree.column('frequency', width=80, anchor='center'); self.history_tree.grid(row=0, column=0, sticky="nsew")
        hist_scroll = ttk.Scrollbar(history_card, orient="vertical", command=self.history_tree.yview); hist_scroll.grid(row=0, column=1, sticky='ns'); self.history_tree.configure(yscrollcommand=hist_scroll.set)

    def setup_analysis_tab(self):
        self.analysis_tab.grid_columnconfigure(0, weight=1); self.analysis_tab.grid_rowconfigure(1, weight=1)
        controls_frame = ttk.Frame(self.analysis_tab, padding=10); controls_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=(0, 10)); self.time_range_var = tk.StringVar(value="Last 30 days"); ranges = ["Last 7 days", "Last 30 days", "Last 90 days", "This year", "All time"]
        ttk.Combobox(controls_frame, textvariable=self.time_range_var, values=ranges, state="readonly").pack(side=tk.LEFT)
        ttk.Button(controls_frame, text="Update Analysis", command=self.update_analysis).pack(side=tk.LEFT, padx=10)
        analysis_notebook = ttk.Notebook(self.analysis_tab); analysis_notebook.grid(row=1, column=0, sticky="nsew", pady=(10,0))
        self.emotion_trends_tab, self.behavior_freq_tab, self.correlations_tab = (ttk.Frame(analysis_notebook, padding=15) for _ in range(3))
        analysis_notebook.add(self.emotion_trends_tab, text="Emotion Trends"); analysis_notebook.add(self.behavior_freq_tab, text="Behavior Frequency"); analysis_notebook.add(self.correlations_tab, text="Correlations")
        self.emotion_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.light_bg_color); self.emotion_canvas = FigureCanvasTkAgg(self.emotion_fig, master=self.emotion_trends_tab); self.emotion_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.behavior_fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.light_bg_color); self.behavior_canvas = FigureCanvasTkAgg(self.behavior_fig, master=self.behavior_freq_tab); self.behavior_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.corr_fig = Figure(figsize=(6, 5), dpi=100, facecolor=self.light_bg_color); self.corr_canvas = FigureCanvasTkAgg(self.corr_fig, master=self.correlations_tab); self.corr_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_settings_tab(self):
        self.settings_tab.grid_columnconfigure(0, weight=1)
        emotion_manage_card = ttk.LabelFrame(self.settings_tab, text="Manage Emotions", style='Card.TFrame', padding=15); emotion_manage_card.grid(row=0, column=0, sticky="ew", pady=10); emotion_manage_card.grid_columnconfigure(0, weight=1)
        self.emotions_listbox = tk.Listbox(emotion_manage_card, font=('Segoe UI', 10), height=6); self.emotions_listbox.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        add_emotion_frame = ttk.Frame(emotion_manage_card, style='Card.TFrame'); add_emotion_frame.grid(row=1, column=0, sticky='ew'); add_emotion_frame.grid_columnconfigure(0, weight=1)
        self.new_emotion_entry = ttk.Entry(add_emotion_frame); self.new_emotion_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        ttk.Button(add_emotion_frame, text="Add", command=self.add_emotion).grid(row=0, column=1)
        ttk.Button(emotion_manage_card, text="Remove Selected Emotion", command=self.remove_emotion).grid(row=2, column=0, sticky='w', pady=(10,0))
        
        reminder_card = ttk.LabelFrame(self.settings_tab, text="Reminders & Startup", style='Card.TFrame', padding=15); reminder_card.grid(row=1, column=0, sticky="ew", pady=10); reminder_card.grid_columnconfigure(1, weight=1)
        ttk.Label(reminder_card, text="Reminder Time (HH:MM):", style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=5)
        time_frame = ttk.Frame(reminder_card, style='Card.TFrame'); time_frame.grid(row=0, column=1, sticky="w", padx=5)
        self.reminder_hour_var = tk.StringVar(value="19"); self.reminder_minute_var = tk.StringVar(value="00")
        ttk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.reminder_hour_var).pack(side=tk.LEFT); ttk.Label(time_frame, text=":", style='Card.TLabel').pack(side=tk.LEFT); ttk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.reminder_minute_var).pack(side=tk.LEFT)
        
        ttk.Label(reminder_card, text="Reminder Message:", style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=5)
        self.reminder_message_var = tk.StringVar()
        ttk.Entry(reminder_card, textvariable=self.reminder_message_var).grid(row=1, column=1, sticky="ew", padx=5)

        self.autostart_var = tk.IntVar(value=0)
        ttk.Checkbutton(reminder_card, text="Start application on Windows startup", variable=self.autostart_var, style='Toolbutton').grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        security_card = ttk.LabelFrame(self.settings_tab, text="Security", style='Card.TFrame', padding=15); security_card.grid(row=2, column=0, sticky="ew", pady=10)
        ttk.Button(security_card, text="Change Password", command=self.change_password).pack(side=tk.LEFT)

        data_card = ttk.LabelFrame(self.settings_tab, text="Data Management", style='Card.TFrame', padding=15); data_card.grid(row=3, column=0, sticky="ew", pady=10)
        ttk.Button(data_card, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=(0, 10)); ttk.Button(data_card, text="Import Data", command=self.import_data).pack(side=tk.LEFT)
        ttk.Button(self.settings_tab, text="Save Settings", command=self.save_settings, style='Success.TButton').grid(row=4, column=0, sticky="e", pady=20)

    def get_all_emotions(self):
        self.cursor.execute("SELECT name FROM emotion_definitions ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def load_emotions_to_settings(self):
        self.emotions_listbox.delete(0, tk.END)
        for emotion in self.get_all_emotions():
            self.emotions_listbox.insert(tk.END, emotion)

    def add_emotion(self):
        new_emotion = self.new_emotion_entry.get().strip()
        if not new_emotion: return
        try:
            self.cursor.execute("INSERT INTO emotion_definitions (name) VALUES (?)", (new_emotion,))
            self.conn.commit()
            self.new_emotion_entry.delete(0, tk.END)
            self.load_emotions_to_settings()
            self.refresh_emotions_display()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate", f"'{new_emotion}' already exists.", parent=self.root)

    def remove_emotion(self):
        selected_indices = self.emotions_listbox.curselection()
        if not selected_indices: return
        emotion_to_remove = self.emotions_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{emotion_to_remove}'?"):
            self.cursor.execute("DELETE FROM emotion_definitions WHERE name = ?", (emotion_to_remove,))
            self.conn.commit()
            self.load_emotions_to_settings()
            self.refresh_emotions_display()

    def load_journal_entry_for_today(self):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT content FROM journal_entries WHERE date = ?", (today_str,))
        result = self.cursor.fetchone()
        if result and result[0]:
            try:
                self.journal_text.insert("1.0", self.decrypt_data(result[0]))
                self.update_word_count()
            except Exception:
                self.journal_text.insert("1.0", "[Could not decrypt entry]")
        self.cursor.execute("SELECT e.emotion FROM emotions e JOIN journal_entries j ON e.entry_id = j.id WHERE j.date = ?", (today_str,))
        emotions_today = {row[0] for row in self.cursor.fetchall()}
        for emotion, var in self.emotion_vars.items():
            if emotion in emotions_today:
                var.set(1)

    def update_word_count(self, event=None):
        word_count = len(self.journal_text.get("1.0", "end-1c").split())
        self.word_count_var.set(f"{word_count} / 200 words")
        progress = min(word_count / 200 * 100, 100)
        self.progress_var.set(progress)
        self.progress_bar.configure(style='Success.TProgressbar' if word_count >= 200 else 'TProgressbar')

    def save_journal_entry(self):
        content, word_count, date = self.journal_text.get("1.0", "end-1c").strip(), len(self.journal_text.get("1.0", "end-1c").split()), datetime.date.today().strftime("%Y-%m-%d")
        if word_count == 0: messagebox.showwarning("Empty Entry", "Cannot save an empty journal entry."); return
        completed, encrypted_content = (1 if word_count >= 200 else 0), self.encrypt_data(content)
        try:
            self.cursor.execute("SELECT id FROM journal_entries WHERE date = ?", (date,)); result = self.cursor.fetchone()
            entry_id = result[0] if result else None
            if entry_id:
                self.cursor.execute("UPDATE journal_entries SET content = ?, word_count = ?, completed = ? WHERE id = ?", (encrypted_content, word_count, completed, entry_id))
                self.cursor.execute("DELETE FROM emotions WHERE entry_id = ?", (entry_id,))
            else:
                self.cursor.execute("INSERT INTO journal_entries (date, content, word_count, completed) VALUES (?, ?, ?, ?)", (date, encrypted_content, word_count, completed)); entry_id = self.cursor.lastrowid
            selected_emotions = [e for e, v in self.emotion_vars.items() if v.get() == 1]
            if selected_emotions: self.cursor.executemany("INSERT INTO emotions (entry_id, emotion) VALUES (?, ?)", [(entry_id, emo) for emo in selected_emotions])
            self.conn.commit(); messagebox.showinfo("Success", "Journal entry saved successfully!"); self.update_calendar()
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to save entry: {e}")

    def update_calendar(self):
        first_day = datetime.date(self.current_year, self.current_month, 1)
        self.month_year_label.config(text=first_day.strftime("%B %Y"))
        start, end = first_day.strftime("%Y-%m-01"), (first_day + datetime.timedelta(days=32)).strftime("%Y-%m-01")
        self.cursor.execute("SELECT date, completed FROM journal_entries WHERE date >= ? AND date < ?", (start, end))
        entries = {row[0][-2:]: row[1] for row in self.cursor.fetchall()}
        start_weekday, num_days = first_day.weekday(), (datetime.date(self.current_year, self.current_month % 12 + 1, 1) if self.current_month < 12 else datetime.date(self.current_year + 1, 1, 1)) - datetime.timedelta(days=1)
        today = datetime.date.today()
        for i, frame in enumerate(self.day_frames):
            day_num = i - start_weekday + 1
            is_today = (self.current_year == today.year and self.current_month == today.month and day_num == today.day)
            is_selected = hasattr(self, 'selected_date') and self.selected_date and (self.current_year == self.selected_date.year and self.current_month == self.selected_date.month and day_num == self.selected_date.day)
            if 1 <= day_num <= num_days.day:
                self.day_labels[i].config(text=str(day_num)); self.day_content_labels[i].config(text="")
                style_prefix = "Selected" if is_selected else "Today" if is_today else "CalendarDay"
                for widget, name in [(frame, 'TFrame'), (self.day_labels[i], 'Number.TLabel'), (self.day_content_labels[i], 'Content.TLabel')]:
                    widget.config(style=f'{style_prefix}.{name}' if name != 'TFrame' else f'{style_prefix}.TFrame')
                if f"{day_num:02d}" in entries: self.day_content_labels[i].config(text="●", foreground=self.success_color if entries[f"{day_num:02d}"] == 1 else self.border_color)
            else:
                self.day_labels[i].config(text=""); self.day_content_labels[i].config(text="")
                for widget, name in [(frame, 'TFrame'), (self.day_labels[i], 'Number.TLabel')]:
                    widget.config(style=f'OtherMonth.{name}' if name != 'TFrame' else 'OtherMonth.TFrame')

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1: self.current_month, self.current_year = 12, self.current_year - 1
        self.update_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month, self.current_year = 1, self.current_year + 1
        self.update_calendar()

    def go_to_today(self):
        self.current_year, self.current_month = datetime.date.today().year, datetime.date.today().month
        self.select_date(0, 0, date_obj=datetime.date.today())

    def select_date(self, row, col, date_obj=None):
        if date_obj: self.selected_date = date_obj
        else:
            day_text = self.day_labels[row * 7 + col].cget("text")
            if not day_text: return
            self.selected_date = datetime.date(self.current_year, self.current_month, int(day_text))
        self.update_calendar()
        self.selected_date_label.config(text=self.selected_date.strftime('%A, %B %d, %Y'))
        self.load_entry_for_display(self.selected_date.strftime("%Y-%m-%d"))

    def load_entry_for_display(self, date_str):
        self.entry_text_display.config(state=tk.NORMAL); self.entry_text_display.delete("1.0", tk.END); self.emotions_display_label.config(text="None")
        self.cursor.execute("SELECT id, content FROM journal_entries WHERE date = ?", (date_str,))
        result = self.cursor.fetchone()
        if result and result[1]:
            entry_id, content = result
            try: self.entry_text_display.insert("1.0", self.decrypt_data(content))
            except Exception: self.entry_text_display.insert("1.0", "[Could not decrypt entry]")
            self.cursor.execute("SELECT emotion FROM emotions WHERE entry_id = ?", (entry_id,)); emotions = [r[0] for r in self.cursor.fetchall()]
            if emotions: self.emotions_display_label.config(text=", ".join(emotions))
        else: self.entry_text_display.insert("1.0", "No entry for this date.")
        self.entry_text_display.config(state=tk.DISABLED)

    def load_behaviors(self):
        for i in self.behaviors_tree.get_children(): self.behaviors_tree.delete(i)
        self.cursor.execute("SELECT name, attribute FROM behaviors ORDER BY name"); behaviors = self.cursor.fetchall()
        behavior_names = [b[0] for b in behaviors]
        for name, attribute in behaviors: self.behaviors_tree.insert('', 'end', values=(name, attribute))
        self.behavior_dropdown['values'] = behavior_names
        if behavior_names: self.behavior_var.set(behavior_names[0])
        self.load_behavior_history()

    def add_behavior(self):
        name, attr = self.new_behavior_name.get().strip(), self.attribute_var.get()
        if not name: messagebox.showwarning("Input Error", "Behavior name cannot be empty."); return
        try: self.cursor.execute("INSERT INTO behaviors (name, attribute) VALUES (?, ?)", (name, attr)); self.conn.commit(); self.new_behavior_name.delete(0, tk.END); self.load_behaviors()
        except sqlite3.IntegrityError: messagebox.showerror("Duplicate Error", f"Behavior '{name}' already exists.")
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to add behavior: {e}")

    def delete_behavior(self):
        item = self.behaviors_tree.focus()
        if not item: messagebox.showwarning("Selection Error", "Please select a behavior to delete."); return
        name = self.behaviors_tree.item(item)['values'][0]
        if messagebox.askyesno("Confirm Deletion", f"Delete '{name}' and all its data?"):
            try: self.cursor.execute("DELETE FROM behaviors WHERE name = ?", (name,)); self.conn.commit(); self.load_behaviors()
            except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to delete behavior: {e}")

    def record_behavior(self):
        name, date, freq, notes = self.behavior_var.get(), self.behavior_date_var.get(), self.frequency_var.get(), self.behavior_notes.get("1.0", "end-1c").strip()
        if not name: messagebox.showwarning("Input Error", "Please select a behavior."); return
        try:
            self.cursor.execute("SELECT id FROM behaviors WHERE name = ?", (name,)); behavior_id = self.cursor.fetchone()[0]
            encrypted_notes = self.encrypt_data(notes) if notes else None
            self.cursor.execute("INSERT INTO behavior_instances (behavior_id, date, frequency, notes) VALUES (?, ?, ?, ?)", (behavior_id, date, freq, encrypted_notes))
            self.conn.commit(); self.behavior_notes.delete("1.0", tk.END); self.load_behavior_history()
        except (sqlite3.Error, TypeError) as e: messagebox.showerror("Database Error", f"Failed to record behavior: {e}")

    def load_behavior_history(self):
        for i in self.history_tree.get_children(): self.history_tree.delete(i)
        self.cursor.execute("SELECT bi.date, b.name, bi.frequency FROM behavior_instances bi JOIN behaviors b ON bi.behavior_id = b.id ORDER BY bi.date DESC LIMIT 50")
        for date, name, frequency in self.cursor.fetchall(): self.history_tree.insert('', 'end', values=(date, name, f"x{frequency}"))

    def update_analysis(self):
        time_range = self.time_range_var.get(); end_date = datetime.date.today()
        days = {'Last 7 days': 7, 'Last 30 days': 30, 'Last 90 days': 90}.get(time_range)
        if days: start_date = end_date - datetime.timedelta(days=days)
        elif time_range == "This year": start_date = datetime.date(end_date.year, 1, 1)
        else: start_date = datetime.date(2000, 1, 1)
        start_str, end_str = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        try:
            emotion_df = pd.read_sql_query("SELECT j.date, e.emotion FROM emotions e JOIN j ON e.entry_id = j.id WHERE j.date BETWEEN ? AND ?", self.conn, params=(start_str, end_str))
            behavior_df = pd.read_sql_query("SELECT bi.date, b.name, bi.frequency FROM behavior_instances bi JOIN b ON bi.behavior_id = b.id WHERE bi.date BETWEEN ? AND ?", self.conn, params=(start_str, end_str))
            self.plot_emotion_trends(emotion_df); self.plot_behavior_frequency(behavior_df); self.plot_correlations(emotion_df, behavior_df)
        except Exception as e: print(f"Analysis Error: {e}")

    def plot_emotion_trends(self, df):
        self.emotion_fig.clear(); ax = self.emotion_fig.add_subplot(111)
        if not df.empty: df['emotion'].value_counts().plot(kind='bar', ax=ax, color=self.primary_color); ax.set_title("Emotion Frequency", color=self.text_color); ax.set_ylabel("Count", color=self.text_color)
        else: ax.text(0.5, 0.5, "No emotion data", ha='center', va='center')
        self.stylize_plot(ax, self.emotion_fig); self.emotion_canvas.draw()

    def plot_behavior_frequency(self, df):
        self.behavior_fig.clear(); ax = self.behavior_fig.add_subplot(111)
        if not df.empty: df.groupby('name')['frequency'].sum().plot(kind='bar', ax=ax, color=self.success_color); ax.set_title("Behavior Frequency", color=self.text_color); ax.set_ylabel("Total Occurrences", color=self.text_color)
        else: ax.text(0.5, 0.5, "No behavior data", ha='center', va='center')
        self.stylize_plot(ax, self.behavior_fig); self.behavior_canvas.draw()

    def plot_correlations(self, emotion_df, behavior_df):
        self.corr_fig.clear(); ax = self.corr_fig.add_subplot(111)
        if emotion_df.empty or behavior_df.empty: ax.text(0.5, 0.5, "Not enough data for correlation", ha='center', va='center')
        else:
            emotion_dummies = pd.get_dummies(emotion_df.set_index('date')['emotion']).groupby('date').sum()
            behavior_pivot = behavior_df.pivot_table(index='date', columns='name', values='frequency', aggfunc='sum').fillna(0)
            merged_df = pd.concat([emotion_dummies, behavior_pivot], axis=1).fillna(0)
            if merged_df.shape[1] > 1 and len(emotion_dummies.columns) > 0 and len(behavior_pivot.columns) > 0:
                corr_matrix = merged_df.corr().loc[emotion_dummies.columns, behavior_pivot.columns]
                im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1); self.corr_fig.colorbar(im, ax=ax)
                ax.set_xticks(np.arange(len(corr_matrix.columns))); ax.set_yticks(np.arange(len(corr_matrix.index)))
                ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right"); ax.set_yticklabels(corr_matrix.index)
                ax.set_title("Emotion-Behavior Correlation", color=self.text_color)
            else: ax.text(0.5, 0.5, "Not enough variety for correlation", ha='center', va='center')
        self.stylize_plot(ax, self.corr_fig, grid=False); self.corr_canvas.draw()

    def stylize_plot(self, ax, fig, grid=True):
        fig.patch.set_facecolor(self.light_bg_color); ax.set_facecolor(self.light_bg_color)
        for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']: ax.spines[spine].set_color(self.border_color)
        ax.tick_params(colors=self.header_color)
        if grid: ax.grid(axis='y', linestyle='--', color=self.border_color, alpha=0.7)
        fig.tight_layout()

    def get_setting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,)); result = self.cursor.fetchone()
        return result[0] if result else None

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)); self.conn.commit()

    def save_settings(self):
        self.set_setting("reminder_hour", self.reminder_hour_var.get())
        self.set_setting("reminder_minute", self.reminder_minute_var.get())
        self.set_setting("autostart", self.autostart_var.get())
        self.set_setting("reminder_message", self.reminder_message_var.get())
        self.setup_autostart(); messagebox.showinfo("Success", "Settings saved.")

    def load_settings(self):
        self.reminder_hour_var.set(self.get_setting("reminder_hour") or "19")
        self.reminder_minute_var.set(self.get_setting("reminder_minute") or "00")
        self.autostart_var.set(int(self.get_setting("autostart") or "0"))
        self.reminder_message_var.set(self.get_setting("reminder_message") or "Time to reflect on your day! Please write at least 200 words.")

    def change_password(self):
        dialog = PasswordDialog(self.root, "Change Password", "Enter your CURRENT password:", "Enter your NEW password:", "Confirm NEW password:")
        old_pass, new_pass = dialog.password, dialog.new_password
        if not old_pass or not new_pass: return
        
        with open(self.salt_path, "rb") as f: salt = f.read()
        ver_hash = hashlib.sha256((old_pass + salt.hex()).encode()).hexdigest()
        saved_hash = self.get_setting('password_verification_hash')
        
        if ver_hash == saved_hash:
            new_salt = os.urandom(16)
            with open(self.salt_path, "wb") as f: f.write(new_salt)
            new_ver_hash = hashlib.sha256((new_pass + new_salt.hex()).encode()).hexdigest()
            self.set_setting('password_verification_hash', new_ver_hash)
            self.setup_encryption(new_pass, new_salt)
            messagebox.showinfo("Success", "Password changed successfully. Your data has been re-encrypted.", parent=self.root)
        else:
            messagebox.showerror("Error", "Your current password was incorrect.", parent=self.root)

    def setup_autostart(self):
        if winreg is None:
            if self.autostart_var.get() == 1: print("Autostart not supported on this OS.")
            return
        key_path, app_name = r"Software\Microsoft\Windows\CurrentVersion\Run", "DailyJournal"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            if self.autostart_var.get() == 1:
                python_exe, script_path = sys.executable, os.path.abspath(__file__)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{python_exe}" "{script_path}"')
            else: winreg.DeleteValue(key, app_name)
            winreg.CloseKey(key)
        except FileNotFoundError: pass
        except Exception as e: messagebox.showwarning("Autostart Error", f"Could not update startup settings: {e}\nTry running as administrator.")

    def export_data(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Encrypted JSON", "*.json")], title="Export Journal Data")
        if not filepath: return
        data_to_export = {}
        tables = ['journal_entries', 'emotions', 'behaviors', 'behavior_instances', 'emotion_definitions', 'settings']
        try:
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
                for col in df.columns:
                    if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, bytes)).any():
                        df[col] = df[col].apply(lambda x: base64.b64encode(x).decode() if isinstance(x, bytes) else x)
                data_to_export[table] = df.to_dict(orient='records')
            json_data = json.dumps(data_to_export, indent=4)
            encrypted_export = self.encrypt_data(json_data)
            with open(filepath, 'wb') as f: f.write(encrypted_export)
            messagebox.showinfo("Export Successful", f"Data successfully exported to {filepath}")
        except Exception as e: messagebox.showerror("Export Error", f"An error occurred during export: {e}")

    def import_data(self):
        if not messagebox.askyesno("Confirm Import", "This will ERASE all current data. Are you sure?"): return
        filepath = filedialog.askopenfilename(filetypes=[("Encrypted JSON", "*.json")], title="Import Journal Data")
        if not filepath: return
        try:
            with open(filepath, 'rb') as f: encrypted_data = f.read()
            decrypted_json = self.decrypt_data(encrypted_data)
            imported_data = json.loads(decrypted_json)
            tables = ['behavior_instances', 'emotions', 'journal_entries', 'behaviors', 'emotion_definitions', 'settings']
            for table in tables: self.cursor.execute(f"DELETE FROM {table}")
            for table_name, records in imported_data.items():
                if records:
                    df = pd.DataFrame(records)
                    for col in df.columns:
                        if df[col].dtype == 'object' and df[col].str.match(r'^[A-Za-z0-9+/=]+$').all():
                            try: df[col] = df[col].apply(lambda x: base64.b64decode(x) if isinstance(x, str) else x)
                            except: pass
                    df.to_sql(table_name, self.conn, if_exists='append', index=False)
            self.conn.commit()
            messagebox.showinfo("Import Successful", "Data imported. The app will now restart.")
            self.on_close(force=True)
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e: messagebox.showerror("Import Error", f"Failed to import data. File may be corrupt or use a different key.\nError: {e}")

    def reminder_loop(self):
        while self.reminder_active:
            time.sleep(15 * 60)
            try:
                reminder_time = datetime.time(int(self.reminder_hour_var.get()), int(self.reminder_minute_var.get()))
                now = datetime.datetime.now()
                if now.time() > reminder_time:
                    self.cursor.execute("SELECT completed FROM journal_entries WHERE date = ?", (now.strftime("%Y-%m-%d"),))
                    result = self.cursor.fetchone()
                    if not result or result[0] == 0: self.root.after(0, self.show_reminder)
            except (ValueError, sqlite3.Error) as e: print(f"Reminder loop error: {e}")

    def show_reminder(self):
        self.root.deiconify(); self.root.lift(); self.root.focus_force()
        self.notebook.select(self.journal_tab)
        
        message = self.reminder_message_var.get()
        title = "Daily Journal Reminder"

        if ToastNotifier:
            try:
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=None, threaded=True) # duration=None makes it persistent
                return
            except Exception as e:
                print(f"Failed to show toast notification: {e}")
        
        # Fallback to messagebox
        messagebox.showinfo(title, message)

    def on_close(self, force=False):
        if not force and self.cipher: # Only check if app is unlocked
            try:
                reminder_time = datetime.time(int(self.reminder_hour_var.get()), int(self.reminder_minute_var.get()))
                if datetime.datetime.now().time() > reminder_time:
                    self.cursor.execute("SELECT completed FROM journal_entries WHERE date = ?", (datetime.date.today().strftime("%Y-%m-%d"),))
                    result = self.cursor.fetchone()
                    if (not result or result[0] == 0) and not messagebox.askyesno("Exit Confirmation", "Journal incomplete. Are you sure you want to exit?"):
                        return
            except (ValueError, sqlite3.Error): pass
        self.reminder_active = False
        if hasattr(self, 'conn'): self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()

