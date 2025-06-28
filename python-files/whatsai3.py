# Institute_Agent_V14_Definitive_Edition.py
#
# This is the final, complete, and fully functional application.
# It includes the complete implementation for all features, including the robust
# Selenium bot, Template Manager, Excel Import, and all UI improvements.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import time
import os
import sys
import pyodbc
from datetime import datetime
import random
import pyperclip
import shutil
import json

# --- Prerequisite Check ---
try:
    import pandas as pd
except ImportError:
    messagebox.showerror("Dependency Error", "'pandas' library not found. Please install it by running:\n\npip install pandas openpyxl")
    sys.exit()
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Dependency Error", "'tkcalendar' library not found. Please install it by running:\n\npip install tkcalendar")
    sys.exit()
try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Dependency Error", "'Pillow' library not found. Please install it by running:\n\npip install Pillow")
    sys.exit()

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    webdriver_available = True
except ImportError:
    messagebox.showerror("Dependency Error", "'selenium' library not found. Please install it by running:\n\npip install selenium")
    webdriver_available = False
    sys.exit()

# --- CONFIGURATION MANAGER ---
class ConfigManager:
    def __init__(self, config_file='config.json'): self.config_file = config_file; self.config = self.load_config()
    def load_config(self):
        if not os.path.exists(self.config_file): return {}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, IOError): return {}
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f: json.dump(self.config, f, indent=4); return True
        except IOError: return False
    def get(self, key, default=None): return self.config.get(key, default)
    def set(self, key, value): self.config[key] = value

# --- DATABASE MANAGER ---
class DatabaseManager:
    def __init__(self, db_path): self.db_path = db_path
    def get_connection(self):
        if not self.db_path or not os.path.exists(self.db_path): raise FileNotFoundError(f"Database file not found: {self.db_path}")
        return pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + self.db_path + ';')
    def fetch_all(self, query, params=()):
        with self.get_connection() as conn: cursor = conn.cursor(); cursor.execute(query, params); return cursor.fetchall()
    def fetch_one(self, query, params=()):
        with self.get_connection() as conn: cursor = conn.cursor(); cursor.execute(query, params); return cursor.fetchone()
    def execute_query(self, query, params=()):
        with self.get_connection() as conn: cursor = conn.cursor(); cursor.execute(query, params); conn.commit()
    def get_all_students_summary(self): return self.fetch_all("SELECT StudentID, StudentName, PhoneNumber FROM Students ORDER BY StudentName")
    def update_student(self, student_id, data):
        query = "UPDATE Students SET StudentName = ?, PhoneNumber = ?, StudentAddress = ?, StudentEmail = ?, Course = ?, DateOfBirth = ?, PracticalTime = ?, TheoryTime = ?, AcademicYear = ?, PhotoPath = ? WHERE StudentID = ?"
        params = (data["StudentName"], data["PhoneNumber"], data["StudentAddress"], data["StudentEmail"], data["Course"], data["DateOfBirth"], data["PracticalTime"], data["TheoryTime"], data["AcademicYear"], data["PhotoPath"], student_id)
        self.execute_query(query, params)
    def is_student_id_unique(self, student_id): return self.fetch_one("SELECT COUNT(*) FROM Students WHERE StudentID = ?", (student_id,))[0] == 0

# --- TEMPLATE MANAGER ---
class TemplateManager:
    def __init__(self, filepath='templates.json'):
        self.filepath = filepath
        self.templates = self._load()
    def _get_default_templates(self):
        return {
            "Welcome New Inquiry":"Hello! Thank you for your interest...", "Course Details Follow-up":"Dear {StudentName}, following up on your inquiry...",
            "Admission Confirmation":"Congratulations, {StudentName}! Your admission is confirmed.", "New Batch Welcome":"Hello {StudentName}, your new batch for {Course} will commence on {Date}.",
            "Fee Reminder (Gentle)":"Dear {StudentName}, this is a friendly reminder about your fee payment.",
            "Birthday Wish":"Dear {StudentName},\n\nThe institute wishes you a very happy birthday! We hope you have a wonderful day. 🎉🎂"
        }
    def _load(self):
        if not os.path.exists(self.filepath):
            default_templates = self._get_default_templates(); self._save(default_templates); return default_templates
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, IOError): return self._get_default_templates()
    def _save(self, data):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4); return True
        except IOError: return False
    def get_templates(self): return self.templates
    def save_template(self, name, content, old_name=None):
        if old_name and old_name != name: del self.templates[old_name]
        self.templates[name] = content; return self._save(self.templates)
    def delete_template(self, name):
        if name in self.templates: del self.templates[name]; return self._save(self.templates)
        return False

# --- WHATSAPP BOT (ROBUST VERSION) ---
class WhatsAppBot:
    def __init__(self, driver_path, user_data_dir):
        self.driver_path = driver_path; self.user_data_dir = user_data_dir; self.driver = None
    def login(self):
        if not self.driver_path or not os.path.exists(self.driver_path): raise FileNotFoundError(f"WebDriver not found: {self.driver_path}")
        service = Service(executable_path=self.driver_path); options = webdriver.EdgeOptions()
        options.add_argument(f"user-data-dir={self.user_data_dir}"); options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Edge(service=service, options=options); self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window(); WebDriverWait(self.driver, 300).until(EC.presence_of_element_located((By.ID, "side"))); time.sleep(5)
    def send_message(self, number, message, image_path=None):
        if not self.driver: raise ConnectionError("Driver not initialized.")
        try:
            self.driver.get(f"https://web.whatsapp.com/send?phone={number}&text=")
            chat_box_xpath = '//footer//div[@contenteditable="true"][@role="textbox"]'
            main_chat_box = WebDriverWait(self.driver, 40).until(EC.element_to_be_clickable((By.XPATH, chat_box_xpath))); time.sleep(1)
            try:
                self.driver.find_element(By.XPATH, "//*[contains(text(), 'Phone number shared via URL is invalid')]")
                return False, "Invalid or Not on WhatsApp"
            except NoSuchElementException: pass
            if image_path and os.path.exists(image_path):
                try: attach_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Attach"]'))); attach_button.click()
                except TimeoutException: return False, "Timeout: Could not find 'Attach' button."
                try:
                    attach_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')))
                    attach_input.send_keys(os.path.abspath(image_path))
                except TimeoutException: return False, "Timeout: Could not find file input."
                try:
                    caption_box_xpath = '//div[@aria-label="Add a caption…"]//div[@role="textbox"]'
                    caption_box = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, caption_box_xpath)))
                    pyperclip.copy(message); caption_box.click(); ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform(); time.sleep(1)
                    send_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))); send_button.click()
                except TimeoutException: return False, "Timeout: Could not find caption box or send button."
            else:
                pyperclip.copy(message); main_chat_box.click()
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(0.5); ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            try: WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[contains(@aria-label, 'check')]")))
            except TimeoutException: return False, "Message sent, but failed to get delivery confirmation."
            return True, "Success"
        except Exception as e: return False, f"An unexpected error occurred: {e}"
    def quit(self):
        if self.driver: self.driver = None

# --- MAIN APPLICATION ---
class InstituteAgentApp:
    def __init__(self, root_window):
        self.root = root_window; self.root.title("Institute AI Agent - Definitive Edition"); self.root.geometry("1050x900")
        self.config_manager = ConfigManager(); self.db_manager = None; self.whatsapp_bot = None
        self.task_running = threading.Event(); self.agent_thread = None; self.current_profile_id = None
        self.min_delay_var = tk.StringVar(value=self.config_manager.get("min_delay", "8")); self.max_delay_var = tk.StringVar(value=self.config_manager.get("max_delay", "15"))
        self.attachment_path_var = tk.StringVar(); self.template_manager = TemplateManager()
        self.course_list, self.practical_time_list, self.theory_time_list, self.academic_year_list = self.get_course_lists()
        self.setup_ui(); self.root.after(100, self.check_initial_config); self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_course_lists(self):
        c = ["Diploma in Computer Application & Accounting (DCAA)","Diploma in Computer Application, Accounting & AI (DCAA-AI)","MS-Office 2024","MS-Office 365 with AI Features","Advance Excel (Knowledge Level)","Advance Excel with MIS Specialisation","Advance Excel (Professional Level - Corporate Training)","Tally PRIME (Knowledge Level)","Advance Tally PRIME with GST (Skill Level)","Advance GST Accounting in Tally PRIME (Professional Level)","Graphic Designing & Video Editing","Other..."]
        p = ["9:00 AM to 10:00 AM", "10:00 AM to 11:00 AM", "11:00 AM to 12:00 PM","12:00 PM to 1:00 PM", "1:00 PM to 2:00 PM", "2:00 PM to 3:00 PM","3:00 PM to 4:00 PM", "4:00 PM to 5:00 PM", "5:00 PM to 6:00 PM","6:00 PM to 7:00 PM", "7:00 PM to 8:00 PM", "Other..."]
        t = ["9:00 AM", "10:30 AM", "12:00 PM", "1:00 PM", "4:00 PM", "7:00 PM", "Other..."]
        a = ["2024-2025", "2025-2026", "2026-2027", "2027-2028", "Other..."]
        return c, p, t, a

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.LabelFrame(main_frame, text="Connection & Control", padding="10"); control_frame.pack(fill=tk.X, pady=5)
        self.login_button = ttk.Button(control_frame, text="Login to WhatsApp", command=self.start_login_thread); self.login_button.pack(side=tk.LEFT, padx=5)
        self.settings_button = ttk.Button(control_frame, text="Settings", command=self.open_settings_window); self.settings_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button = ttk.Button(control_frame, text="Cancel Task", command=self.cancel_running_task, state=tk.DISABLED); self.cancel_button.pack(side=tk.RIGHT, padx=5)
        self.status_label = ttk.Label(control_frame, text="Status: Not Logged In", font=("Segoe UI", 10, "bold"), foreground="red"); self.status_label.pack(side=tk.RIGHT, padx=10)
        notebook = ttk.Notebook(main_frame); notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        msg_tab, search_tab, form_tab = ttk.Frame(notebook, padding="10"), ttk.Frame(notebook, padding="10"), ttk.Frame(notebook, padding="10")
        notebook.add(msg_tab, text="Send Messages"); notebook.add(search_tab, text="Search & Edit Students"); notebook.add(form_tab, text="Add New Student")
        self.create_messaging_tab(msg_tab); self.create_student_form_tab(form_tab); self.create_search_tab(search_tab)
        log_frame = ttk.Frame(main_frame); log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        log_panel = ttk.LabelFrame(log_frame, text="Live Log", padding=10); log_panel.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.log_area = ScrolledText(log_panel, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 9)); self.log_area.pack(fill=tk.BOTH, expand=True)
        ttk.Button(log_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT, anchor=tk.N, padx=10)
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate'); self.progress_bar.pack(fill=tk.X, pady=(5,0), padx=10); self.progress_bar.pack_forget() 
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=5); self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._toggle_db_features(False)

    def _toggle_db_features(self, enabled=False):
        state = tk.NORMAL if enabled else tk.DISABLED
        if hasattr(self, 'send_filtered_button'):
            self.send_filtered_button.config(state=state if self.whatsapp_bot else tk.DISABLED)
            self.check_birthdays_button.config(state=state)
            self.send_birthday_wishes_button.config(state=state if self.whatsapp_bot else tk.DISABLED)
        if hasattr(self, 'search_button'):
            self.search_button.config(state=state); self.show_all_button.config(state=state)
        if hasattr(self, 'import_button'):
            self.import_button.config(state=state); self.add_student_button.config(state=state)

    def create_messaging_tab(self, parent):
        container = ttk.Frame(parent); container.pack(fill=tk.BOTH, expand=True)
        top_controls_frame = ttk.Frame(container); top_controls_frame.pack(fill=tk.X, pady=(0, 10))
        attachment_frame = ttk.LabelFrame(top_controls_frame, text="Attach Image (Optional)", padding=10)
        attachment_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Entry(attachment_frame, textvariable=self.attachment_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(attachment_frame, text="Browse...", command=self._browse_for_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(attachment_frame, text="Remove", command=lambda: self.attachment_path_var.set("")).pack(side=tk.LEFT)
        timing_frame = ttk.LabelFrame(top_controls_frame, text="Timing", padding=10); timing_frame.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(timing_frame, text="Min(s):").pack(side=tk.LEFT); ttk.Entry(timing_frame, textvariable=self.min_delay_var, width=5).pack(side=tk.LEFT, padx=(0,5))
        ttk.Label(timing_frame, text="Max(s):").pack(side=tk.LEFT); ttk.Entry(timing_frame, textvariable=self.max_delay_var, width=5).pack(side=tk.LEFT)
        compose_frame = ttk.LabelFrame(container, text="Compose Message / Caption", padding=10); compose_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        template_controls_frame = ttk.Frame(compose_frame); template_controls_frame.pack(fill=tk.X, pady=5)
        ttk.Label(template_controls_frame, text="Template:").pack(side=tk.LEFT, padx=(0,5))
        self.template_combo = ttk.Combobox(compose_frame, state='readonly', width=40)
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True); self.template_combo.bind("<<ComboboxSelected>>", self.on_template_select)
        self._load_templates_to_combobox()
        ttk.Button(template_controls_frame, text="Manage Templates...", command=self._open_template_manager).pack(side=tk.LEFT, padx=10)
        self.bulk_message_text = ScrolledText(compose_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10)); self.bulk_message_text.pack(fill=tk.BOTH, expand=True, pady=5); self.bulk_message_text.insert(tk.END, "Dear {StudentName},\n\n")
        filter_frame = ttk.LabelFrame(container, text="Filters & Actions", padding=10); filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Practical Time:").pack(side=tk.LEFT, padx=5); self.practical_time_filter = ttk.Combobox(filter_frame, state='disabled', values=["All"], width=20); self.practical_time_filter.pack(side=tk.LEFT, padx=(0,10)); self.practical_time_filter.set("All")
        ttk.Label(filter_frame, text="Theory Time:").pack(side=tk.LEFT, padx=5); self.theory_time_filter = ttk.Combobox(filter_frame, state='disabled', values=["All"], width=15); self.theory_time_filter.pack(side=tk.LEFT, padx=(0,10)); self.theory_time_filter.set("All")
        ttk.Label(filter_frame, text="Academic Year:").pack(side=tk.LEFT, padx=5); self.academic_year_filter = ttk.Combobox(filter_frame, state='disabled', values=["All"], width=15); self.academic_year_filter.pack(side=tk.LEFT, padx=(0,10)); self.academic_year_filter.set("All")
        self.send_filtered_button = ttk.Button(filter_frame, text="Send to Filtered", command=self.start_filtered_messaging, state=tk.DISABLED); self.send_filtered_button.pack(side=tk.RIGHT, padx=5)
        birthday_frame = ttk.LabelFrame(container, text="Birthday Wishes Section", padding=10); birthday_frame.pack(fill=tk.X, pady=5)
        self.check_birthdays_button = ttk.Button(birthday_frame, text="Check Today's Birthdays", command=self.check_birthdays, state=tk.DISABLED); self.check_birthdays_button.pack(side=tk.LEFT, padx=(0, 10))
        self.send_birthday_wishes_button = ttk.Button(birthday_frame, text="Send Wishes to Selected", command=self.start_birthday_messaging, state=tk.DISABLED); self.send_birthday_wishes_button.pack(side=tk.LEFT)
        self.birthday_listbox = tk.Listbox(birthday_frame, height=3, selectmode=tk.MULTIPLE); self.birthday_listbox.pack(fill=tk.X, pady=5, expand=True)

    def create_student_form_tab(self, parent):
        self.add_student_form_vars = {key: tk.StringVar() for key in ["StudentID", "StudentName", "PhoneNumber", "StudentAddress", "StudentEmail", "PhotoPath", "Course", "DateOfBirth", "PracticalTime", "TheoryTime", "AcademicYear"]}
        form_frame = ttk.Frame(parent); form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        import_frame = ttk.LabelFrame(form_frame, text="Bulk Import", padding=10); import_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(import_frame, text="Import students from an Excel (.xlsx) file.").pack(side=tk.LEFT, padx=5)
        self.import_button = ttk.Button(import_frame, text="Import from Excel", command=self.start_import_from_excel); self.import_button.pack(side=tk.RIGHT, padx=5)
        manual_add_frame = ttk.LabelFrame(form_frame, text="Add a Single Student", padding=10); manual_add_frame.pack(fill=tk.BOTH, expand=True)
        id_row = ttk.Frame(manual_add_frame); id_row.pack(fill=tk.X, pady=4, padx=5)
        ttk.Label(id_row, text="Student ID:", width=25).pack(side=tk.LEFT); ttk.Entry(id_row, textvariable=self.add_student_form_vars["StudentID"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_form_widgets(manual_add_frame, self.add_student_form_vars)
        self.add_student_button = ttk.Button(manual_add_frame, text="Save Student Information", command=self.add_student_to_db); self.add_student_button.pack(pady=15)

    def create_search_tab(self, parent):
        search_controls_frame = ttk.LabelFrame(parent, text="Find Student", padding=10); search_controls_frame.pack(fill=tk.X)
        ttk.Label(search_controls_frame, text="Search By:").pack(side=tk.LEFT, padx=5); self.search_by_var = tk.StringVar(value="Student Name")
        ttk.Combobox(search_controls_frame, textvariable=self.search_by_var, values=["Student Name", "Student ID", "Phone Number"], state='readonly', width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(search_controls_frame, text="Search Term:").pack(side=tk.LEFT, padx=5); self.search_term_var = tk.StringVar()
        search_entry = ttk.Entry(search_controls_frame, textvariable=self.search_term_var, width=40); search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5); search_entry.bind("<Return>", self.run_search_thread) 
        self.search_button = ttk.Button(search_controls_frame, text="Search", command=self.run_search_thread); self.search_button.pack(side=tk.LEFT, padx=5)
        self.show_all_button = ttk.Button(search_controls_frame, text="Show All Students", command=self.run_show_all_thread); self.show_all_button.pack(side=tk.LEFT, padx=5)
        
        results_container = ttk.Frame(parent); results_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_list_frame = ttk.LabelFrame(results_container, text="Student List", padding=10); self.results_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        
        cols = ('id', 'name', 'phone'); self.search_tree = ttk.Treeview(self.results_list_frame, columns=cols, show='headings', height=20)
        self.search_tree.heading('id', text='Student ID'); self.search_tree.column('id', width=80)
        self.search_tree.heading('name', text='Name'); self.search_tree.column('name', width=200)
        self.search_tree.heading('phone', text='Phone Number'); self.search_tree.column('phone', width=120)
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll = ttk.Scrollbar(self.results_list_frame, orient="vertical", command=self.search_tree.yview); tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.configure(yscrollcommand=tree_scroll.set); self.search_tree.bind('<<TreeviewSelect>>', self.on_result_select)

        self.profile_display_frame = ttk.LabelFrame(results_container, text="Student Profile", padding=10); self.profile_display_frame.pack(fill=tk.Y, expand=False, side=tk.LEFT, ipadx=10)
        profile_details_left = ttk.Frame(self.profile_display_frame); profile_details_left.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=5)
        profile_photo_frame = ttk.Frame(self.profile_display_frame, width=160); profile_photo_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y); profile_photo_frame.pack_propagate(False)
        self.photo_label = ttk.Label(profile_photo_frame, anchor=tk.CENTER); self.photo_label.pack(pady=5); self.set_placeholder_image()
        self.profile_display_vars = {}
        fields = ["Student ID", "Full Name", "Phone Number", "Address", "Email", "Course", "Date of Birth", "PracticalTime", "TheoryTime", "Academic Year"]
        for field in fields:
            row_frame = ttk.Frame(profile_details_left); row_frame.pack(fill=tk.X, pady=3); ttk.Label(row_frame, text=f"{field}:", width=15, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            self.profile_display_vars[field] = tk.StringVar(value="-")
            if field == "Phone Number":
                phone_label = ttk.Label(row_frame, textvariable=self.profile_display_vars[field], foreground="cyan", cursor="hand2")
                phone_label.pack(side=tk.LEFT); phone_label.bind("<Button-1>", lambda e, p=self.profile_display_vars["Phone Number"]: self._copy_to_clipboard(p.get()))
            else:
                ttk.Label(row_frame, textvariable=self.profile_display_vars[field], wraplength=400, justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
        self.edit_student_button = ttk.Button(self.profile_display_frame, text="Edit Student Details", command=self.open_edit_window, state=tk.DISABLED); self.edit_student_button.pack(pady=10, side=tk.BOTTOM)
    
    def _clear_log(self):
        self.log_area.config(state=tk.NORMAL); self.log_area.delete('1.0', tk.END); self.log_area.config(state=tk.DISABLED); self.log_message("Log cleared.", "INFO")
    def _copy_to_clipboard(self, text):
        if text and text != "-": pyperclip.copy(text); self.log_message(f"Copied to clipboard: {text}", "INFO")
    def _load_templates_to_combobox(self): self.template_combo['values'] = list(self.template_manager.get_templates().keys())
    def _open_template_manager(self):
        tm_win = tk.Toplevel(self.root); tm_win.title("Template Manager"); tm_win.geometry("800x600"); tm_win.transient(self.root); tm_win.grab_set()
        main_frame = ttk.Frame(tm_win, padding=10); main_frame.pack(fill=tk.BOTH, expand=True)
        list_frame = ttk.LabelFrame(main_frame, text="Templates", padding=10); list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        template_listbox = tk.Listbox(list_frame, height=20); template_listbox.pack(fill=tk.BOTH, expand=True)
        def populate_listbox():
            template_listbox.delete(0, tk.END)
            for name in sorted(self.template_manager.get_templates().keys()): template_listbox.insert(tk.END, name)
        populate_listbox()
        editor_frame = ttk.Frame(main_frame); editor_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        ttk.Label(editor_frame, text="Template Name:").pack(anchor=tk.W); name_var = tk.StringVar(); ttk.Entry(editor_frame, textvariable=name_var).pack(fill=tk.X, pady=(0, 10))
        ttk.Label(editor_frame, text="Template Content:").pack(anchor=tk.W); content_text = ScrolledText(editor_frame, height=10, wrap=tk.WORD); content_text.pack(fill=tk.BOTH, expand=True)
        def clear_editor(): name_var.set(""); content_text.delete('1.0', tk.END); template_listbox.selection_clear(0, tk.END)
        def on_template_select_in_manager(event):
            selection = template_listbox.curselection()
            if not selection: return
            selected_name = template_listbox.get(selection[0]); content = self.template_manager.get_templates().get(selected_name, "")
            name_var.set(selected_name); content_text.delete('1.0', tk.END); content_text.insert('1.0', content)
        template_listbox.bind('<<ListboxSelect>>', on_template_select_in_manager)
        def save_action():
            name = name_var.get().strip(); content = content_text.get('1.0', tk.END).strip()
            if not name or not content: messagebox.showerror("Error", "Name and content cannot be empty.", parent=tm_win); return
            old_name = template_listbox.get(template_listbox.curselection()[0]) if template_listbox.curselection() else None
            if self.template_manager.save_template(name, content, old_name):
                self.log_message(f"Template '{name}' saved.", "SUCCESS"); populate_listbox(); self._load_templates_to_combobox()
            else: messagebox.showerror("Error", "Failed to save template.", parent=tm_win)
        def delete_action():
            selection = template_listbox.curselection()
            if not selection: messagebox.showerror("Error", "Select a template to delete.", parent=tm_win); return
            name_to_delete = template_listbox.get(selection[0])
            if messagebox.askyesno("Confirm Delete", f"Delete '{name_to_delete}'?", parent=tm_win):
                if self.template_manager.delete_template(name_to_delete):
                    self.log_message(f"Template '{name_to_delete}' deleted.", "SUCCESS"); populate_listbox(); self._load_templates_to_combobox(); clear_editor()
                else: messagebox.showerror("Error", "Failed to delete template.", parent=tm_win)
        button_bar = ttk.Frame(editor_frame); button_bar.pack(fill=tk.X, pady=10)
        ttk.Button(button_bar, text="New", command=clear_editor).pack(side=tk.LEFT, padx=5); ttk.Button(button_bar, text="Save", command=save_action).pack(side=tk.LEFT, padx=5); ttk.Button(button_bar, text="Delete Selected", command=delete_action).pack(side=tk.RIGHT, padx=5)
    def _browse_for_attachment(self):
        filepath = filedialog.askopenfilename(title="Select Image to Attach", filetypes=(("Image Files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
        if filepath: self.attachment_path_var.set(filepath); self.log_message(f"Image attached: {os.path.basename(filepath)}", "INFO")
        else: self.attachment_path_var.set("")
    def on_template_select(self, event=None):
        selected_template = self.template_combo.get();
        if "---" in selected_template: return
        message_text = self.template_manager.get_templates().get(selected_template, ""); self.bulk_message_text.delete("1.0", tk.END); self.bulk_message_text.insert("1.0", message_text); self.log_message(f"Template '{selected_template}' loaded.")
    def check_initial_config(self):
        if not self.config_manager.get("db_path"): messagebox.showinfo("Setup", "Please configure paths in Settings."); self.open_settings_window()
        else: self.initialize_managers()
    def initialize_managers(self):
        try:
            self.db_manager = DatabaseManager(self.config_manager.get("db_path")); self.db_manager.get_connection().close()
            self.log_message("DB connected.", "SUCCESS"); self._toggle_db_features(True)
        except Exception as e: self.log_message(f"DB connection failed: {e}", "FATAL"); messagebox.showerror("DB Error", f"Could not connect.\nError: {e}"); self._toggle_db_features(False)
    def _create_form_widgets(self, parent, form_vars):
        fields = {"StudentName": "Full Name:", "PhoneNumber": "WhatsApp Number (with 91):", "StudentAddress": "Address:", "StudentEmail": "Email:", "PhotoPath": "Student Photo:", "Course": "Course:", "DateOfBirth": "Date of Birth (MM/DD/YYYY):", "PracticalTime": "Practical Time:", "TheoryTime": "Theory Time:", "AcademicYear": "Academic Year:"}
        for key, text in fields.items():
            row = ttk.Frame(parent); row.pack(fill=tk.X, pady=4, padx=5); ttk.Label(row, text=text, width=25).pack(side=tk.LEFT)
            if key == "PhotoPath":
                photo_frame = ttk.Frame(row); photo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Entry(photo_frame, textvariable=form_vars[key], state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
                browse_cmd = lambda v=form_vars[key]: self._browse_for_photo(v)
                ttk.Button(photo_frame, text="Browse...", command=browse_cmd).pack(side=tk.LEFT, padx=(5,0))
            elif key == "DateOfBirth":
                DateEntry(row, textvariable=form_vars[key], date_pattern='mm/dd/yyyy', width=48).pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif key in ["Course", "PracticalTime", "TheoryTime", "AcademicYear"]:
                list_map = {"Course": self.course_list, "PracticalTime": self.practical_time_list, "TheoryTime": self.theory_time_list, "AcademicYear": self.academic_year_list}
                widget = ttk.Combobox(row, textvariable=form_vars[key], values=list_map[key])
                widget.bind("<<ComboboxSelected>>", lambda e, w=widget: self.on_dropdown_select(e, w)); widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                ttk.Entry(row, textvariable=form_vars[key]).pack(side=tk.LEFT, fill=tk.X, expand=True)
    def start_import_from_excel(self):
        if not self.db_manager: messagebox.showerror("Database Error", "Cannot import because the database is not connected."); return
        filepath = filedialog.askopenfilename(title="Select Excel File", filetypes=(("Excel Files", "*.xlsx"), ("All files", "*.*")))
        if not filepath: self.log_message("Excel import cancelled.", "INFO"); return
        self.update_ui_for_task(True, "Importing from Excel..."); self.agent_thread = threading.Thread(target=self._run_excel_import_task, args=(filepath,), daemon=True); self.agent_thread.start()
    def _run_excel_import_task(self, filepath):
        self.log_message(f"Starting import from {os.path.basename(filepath)}...", "INFO")
        try: df = pd.read_excel(filepath, dtype=str).fillna('')
        except Exception as e:
            self.log_message(f"Failed to read Excel file: {e}", "FATAL"); messagebox.showerror("File Read Error", f"Could not read the Excel file.\n\nError: {e}"); self.root.after(0, self.update_ui_for_task, False); return
        required_columns = ['StudentID', 'StudentName', 'PhoneNumber']
        for col in required_columns:
            if col not in df.columns:
                self.log_message(f"Missing required column: {col}", "FATAL"); messagebox.showerror("Import Error", f"Excel is missing column: '{col}'."); self.root.after(0, self.update_ui_for_task, False); return
        success_count, skipped_count, total_rows = 0, 0, len(df)
        self.root.after(0, self._update_progress, 0, total_rows, True)
        for index, row in df.iterrows():
            if self.task_running.is_set(): self.log_message("Import cancelled.", "WARN"); break
            self.root.after(0, self._update_progress, index + 1, total_rows)
            student_id, student_name, phone_number = str(row.get('StudentID', '')).strip(), str(row.get('StudentName', '')).strip(), str(row.get('PhoneNumber', '')).strip()
            if not all([student_id, student_name, phone_number]):
                self.log_message(f"Skipping row {index+2}: Missing required data.", "WARN"); skipped_count += 1; continue
            try:
                if not self.db_manager.is_student_id_unique(student_id): self.log_message(f"Skipping row {index+2}: ID '{student_id}' exists.", "WARN"); skipped_count += 1; continue
                params, db_fields = [], ["StudentID", "StudentName", "PhoneNumber", "StudentAddress", "StudentEmail", "Course", "DateOfBirth", "PracticalTime", "TheoryTime", "AcademicYear", "PhotoPath"]
                for field in db_fields:
                    if field in row: params.append(str(row.get(field, '')).strip())
                    elif field == "PhotoPath": params.append(None) 
                    else: params.append('')
                sql = "INSERT INTO Students (StudentID, StudentName, PhoneNumber, StudentAddress, StudentEmail, Course, DateOfBirth, PracticalTime, TheoryTime, AcademicYear, PhotoPath) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                self.db_manager.execute_query(sql, tuple(params)); self.log_message(f"Imported: {student_name} (ID: {student_id})", "SUCCESS"); success_count += 1
            except Exception as e: self.log_message(f"Error on row {index+2} ({student_name}): {e}", "ERROR"); skipped_count += 1
        summary = f"Import Complete!\n\nImported: {success_count}\nSkipped: {skipped_count}"
        self.log_message(summary, "INFO"); messagebox.showinfo("Import Summary", summary); self.root.after(0, self.load_filter_options); self.root.after(0, self._update_progress, 0, 0, False); self.root.after(0, self.update_ui_for_task, False)
    def _browse_for_photo(self, string_var_to_update):
        filepath = filedialog.askopenfilename(title="Select Student Photo", filetypes=(("Image Files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
        if filepath: string_var_to_update.set(filepath); self.log_message(f"Photo selected: {os.path.basename(filepath)}")
    def on_dropdown_select(self, event, combobox_widget):
        if combobox_widget.get() == "Other...": combobox_widget.set(""); combobox_widget.focus(); self.log_message("Custom entry enabled.")
    def on_closing(self):
        self.log_message("Closing..."); self.cancel_running_task()
        if self.agent_thread and self.agent_thread.is_alive(): self.agent_thread.join(timeout=3)
        if self.whatsapp_bot: self.whatsapp_bot.quit()
        self.root.destroy()
    def set_placeholder_image(self):
        try: placeholder = Image.new('RGB', (150, 150), color = 'grey'); self.placeholder_img = ImageTk.PhotoImage(placeholder); self.photo_label.config(image=self.placeholder_img)
        except NameError: self.photo_label.config(text="[ No Photo ]")
    def open_settings_window(self):
        settings_win = tk.Toplevel(self.root); settings_win.title("Settings"); settings_win.geometry("600x250"); settings_win.transient(self.root); settings_win.grab_set()
        frame = ttk.Frame(settings_win, padding=10); frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Application Paths", font=("Segoe UI", 12, "bold")).pack(pady=5)
        db_path_var = tk.StringVar(value=self.config_manager.get("db_path", "")); photo_dir_var = tk.StringVar(value=self.config_manager.get("photo_dir", "")); driver_path_var = tk.StringVar(value=self.config_manager.get("driver_path", ""))
        def create_path_row(parent, label_text, text_var):
            row = ttk.Frame(parent); row.pack(fill=tk.X, pady=5); ttk.Label(row, text=label_text, width=20).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=text_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            return lambda: text_var.set(filedialog.askopenfilename() if "Driver" in label_text or "Database" in label_text else filedialog.askdirectory())
        db_browse = create_path_row(frame, "MS Access Database:", db_path_var); ttk.Button(frame.winfo_children()[-1], text="Browse...", command=db_browse).pack(side=tk.RIGHT)
        photo_browse = create_path_row(frame, "Student Photos Dir:", photo_dir_var); ttk.Button(frame.winfo_children()[-1], text="Browse...", command=photo_browse).pack(side=tk.RIGHT)
        driver_browse = create_path_row(frame, "Edge WebDriver:", driver_path_var); ttk.Button(frame.winfo_children()[-1], text="Browse...", command=driver_browse).pack(side=tk.RIGHT)
        def save_settings():
            self.config_manager.set("db_path", db_path_var.get()); self.config_manager.set("photo_dir", photo_dir_var.get()); self.config_manager.set("driver_path", driver_path_var.get())
            if self.config_manager.save_config(): messagebox.showinfo("Success", "Settings saved.", parent=settings_win); self.initialize_managers(); settings_win.destroy()
            else: messagebox.showerror("Error", "Failed to save.", parent=settings_win)
        ttk.Button(frame, text="Save Settings", command=save_settings).pack(pady=20)
    def start_login_thread(self):
        if not self.config_manager.get("driver_path"): messagebox.showerror("Error", "WebDriver path not set in Settings."); return
        self.update_ui_for_task(True, "Logging In..."); self.status_label.config(text="Status: Logging In...", foreground="orange")
        self.log_message("Initiating login..."); self.agent_thread = threading.Thread(target=self.initialize_and_login_bot, daemon=True); self.agent_thread.start()
    def initialize_and_login_bot(self):
        try:
            driver_path = self.config_manager.get("driver_path"); script_dir = os.path.dirname(os.path.realpath(sys.argv[0])); user_data_dir = os.path.join(script_dir, "whatsapp_session")
            self.whatsapp_bot = WhatsAppBot(driver_path, user_data_dir); self.whatsapp_bot.login(); self.root.after(0, self.update_ui_after_login, True)
        except Exception as e:
            self.log_message(f"Login error: {e}", "FATAL")
            if self.whatsapp_bot: self.whatsapp_bot.quit(); self.whatsapp_bot = None
            self.root.after(0, self.update_ui_after_login, False)
    def update_ui_after_login(self, success):
        self.update_ui_for_task(False)
        if success:
            self.status_label.config(text="Status: Logged In", foreground="green"); self.log_message("Login successful.", "SUCCESS")
            self.send_filtered_button.config(state=tk.NORMAL); self.send_birthday_wishes_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Status: Not Logged In", foreground="red"); self.log_message("Login failed.", "ERROR")
    def load_filter_options(self):
        if not self.db_manager: return
        try:
            self.practical_time_filter['values'] = ["All"] + [r[0] for r in self.db_manager.fetch_all("SELECT DISTINCT PracticalTime FROM Students WHERE PracticalTime IS NOT NULL AND PracticalTime <> '' ORDER BY PracticalTime")]
            self.theory_time_filter['values'] = ["All"] + [r[0] for r in self.db_manager.fetch_all("SELECT DISTINCT TheoryTime FROM Students WHERE TheoryTime IS NOT NULL AND TheoryTime <> '' ORDER BY TheoryTime")]
            self.academic_year_filter['values'] = ["All"] + [r[0] for r in self.db_manager.fetch_all("SELECT DISTINCT AcademicYear FROM Students WHERE AcademicYear IS NOT NULL AND AcademicYear <> '' ORDER BY AcademicYear")]
            self.log_message("Filter options loaded.")
        except Exception as e: self.log_message(f"Filter load error: {e}", "ERROR")
    def run_search_thread(self, event=None):
        if not self.db_manager: messagebox.showerror("Database Error", "Database is not connected."); return
        self.update_ui_for_task(True, "Searching..."); self.agent_thread = threading.Thread(target=self.search_for_student_task, daemon=True); self.agent_thread.start()
    def run_show_all_thread(self):
        if not self.db_manager: messagebox.showerror("Database Error", "Database is not connected."); return
        self.update_ui_for_task(True, "Loading..."); self.agent_thread = threading.Thread(target=self.show_all_students_task, daemon=True); self.agent_thread.start()
    def search_for_student_task(self):
        term = self.search_term_var.get().strip()
        if not term: self.log_message("Search term empty.", "WARN"); self.root.after(0, self.update_ui_for_task, False); return
        field_map = {"Student Name": "StudentName", "Student ID": "StudentID", "Phone Number": "PhoneNumber"}; db_field = field_map[self.search_by_var.get()]
        self.log_message(f"Searching for '{term}'...")
        try:
            if self.search_by_var.get() == "Student Name": query = f"SELECT StudentID, StudentName, PhoneNumber FROM Students WHERE {db_field} LIKE ? ORDER BY StudentName"; params = (f'%{term}%',)
            else: query = f"SELECT StudentID, StudentName, PhoneNumber FROM Students WHERE {db_field} = ? ORDER BY StudentName"; params = (term,)
            self.root.after(0, self.handle_search_results, self.db_manager.fetch_all(query, params))
        except Exception as e: self.log_message(f"Search error: {e}", "ERROR"); self.root.after(0, self.update_ui_for_task, False)
    def show_all_students_task(self):
        self.log_message("Fetching all..."); self.update_ui_for_task(True)
        try: self.root.after(0, self.handle_search_results, self.db_manager.get_all_students_summary())
        except Exception as e: self.log_message(f"Fetch all error: {e}", "ERROR"); self.root.after(0, self.update_ui_for_task, False)
    def handle_search_results(self, results):
        for i in self.search_tree.get_children(): self.search_tree.delete(i)
        self.clear_profile_display()
        if not results: self.log_message("No students found.", "INFO"); messagebox.showinfo("Info", "No students found.")
        else:
            self.log_message(f"Found {len(results)} students."); 
            for res in results: self.search_tree.insert('', tk.END, values=res)
        self.update_ui_for_task(False)
    def on_result_select(self, event=None):
        selection = self.search_tree.focus()
        if not selection: return
        self.fetch_and_display_profile(self.search_tree.item(selection)['values'][0])
    def fetch_and_display_profile(self, student_id):
        self.log_message(f"Fetching profile for ID: {student_id}")
        try:
            query = "SELECT * FROM Students WHERE StudentID = ?"; profile_data = self.db_manager.fetch_one(query, (student_id,))
            if profile_data: self.root.after(0, self.display_student_profile, profile_data)
        except Exception as e: self.log_message(f"Profile fetch error: {e}", "ERROR")
    def display_student_profile(self, data):
        self.clear_profile_display(); student_dict = dict(zip([d[0] for d in data.cursor_description], data))
        self.current_profile_id = student_dict['StudentID']; self.edit_student_button.config(state=tk.NORMAL)
        for key, var in self.profile_display_vars.items():
            db_key = key.replace(' ', '')
            value = student_dict.get(db_key)
            if isinstance(value, datetime): value = value.strftime('%m/%d/%Y')
            var.set(str(value) if value is not None else "-")
        photo_path = student_dict.get('PhotoPath')
        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path); img.thumbnail((150, 150)); self.student_photo = ImageTk.PhotoImage(img); self.photo_label.config(image=self.student_photo)
            except Exception as e: self.log_message(f"Image load error: {e}", "WARN"); self.set_placeholder_image()
        else: self.set_placeholder_image()
    def clear_profile_display(self):
        for var in self.profile_display_vars.values(): var.set("-")
        self.set_placeholder_image(); self.current_profile_id = None; self.edit_student_button.config(state=tk.DISABLED)
    def add_student_to_db(self):
        if not self.db_manager: messagebox.showerror("Database Error", "Database is not connected."); return
        data = {key: var.get().strip() for key, var in self.add_student_form_vars.items()}
        if not data["StudentName"] or not data["PhoneNumber"] or not data["StudentID"]: messagebox.showerror("Error", "ID, Name, and Phone are required."); return
        try:
            if not self.db_manager.is_student_id_unique(data["StudentID"]): messagebox.showerror("Error", f"ID '{data['StudentID']}' already exists."); return
            photo_path = data["PhotoPath"]; final_photo_path = ""
            if photo_path and os.path.exists(photo_path):
                photo_dir = self.config_manager.get("photo_dir")
                if not photo_dir or not os.path.isdir(photo_dir): messagebox.showerror("Error", "Photos directory not configured."); return
                filename = f"{data['StudentID']}_{os.path.basename(photo_path)}"; final_photo_path = os.path.join(photo_dir, filename)
                shutil.copy(photo_path, final_photo_path); self.log_message(f"Photo copied to {final_photo_path}")
            dob = data["DateOfBirth"] if data["DateOfBirth"] else None
            sql = "INSERT INTO Students (StudentID, StudentName, PhoneNumber, StudentAddress, StudentEmail, Course, DateOfBirth, PracticalTime, TheoryTime, AcademicYear, PhotoPath) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (data["StudentID"], data["StudentName"], data["PhoneNumber"], data["StudentAddress"], data["StudentEmail"], data["Course"], dob, data["PracticalTime"], data["TheoryTime"], data["AcademicYear"], final_photo_path)
            self.db_manager.execute_query(sql, params); self.log_message(f"Student '{data['StudentName']}' saved.", "SUCCESS"); messagebox.showinfo("Success", "Student saved."); self.load_filter_options()
            for var in self.add_student_form_vars.values(): var.set("")
        except Exception as e: self.log_message(f"Save error: {e}", "ERROR"); messagebox.showerror("Database Error", f"Save error: {e}")
    def open_edit_window(self):
        if not self.current_profile_id: return
        try:
            query = "SELECT * FROM Students WHERE StudentID = ?"; student_data = self.db_manager.fetch_one(query, (self.current_profile_id,))
            if not student_data: messagebox.showerror("Error", "Could not retrieve student data."); return
            student_dict = dict(zip([d[0] for d in student_data.cursor_description], student_data))
        except Exception as e: messagebox.showerror("Error", f"Fetch error: {e}"); return
        
        edit_win = tk.Toplevel(self.root); edit_win.title(f"Editing: {self.current_profile_id}"); edit_win.geometry("700x600"); edit_win.transient(self.root); edit_win.grab_set()
        form_frame = ttk.Frame(edit_win, padding=10); form_frame.pack(fill=tk.BOTH, expand=True)
        edit_form_vars = {key: tk.StringVar() for key in student_dict.keys()}
        for key, value in student_dict.items():
            if isinstance(value, datetime): value = value.strftime('%m/%d/%Y')
            edit_form_vars[key].set(str(value) if value is not None else "")
        self._create_form_widgets(form_frame, edit_form_vars)
        ttk.Button(form_frame, text="Save Changes", command=lambda: self.save_student_changes(self.current_profile_id, edit_form_vars, edit_win)).pack(pady=15)
    def save_student_changes(self, student_id, form_vars, window):
        data = {key: var.get().strip() for key, var in form_vars.items()}
        if not data["StudentName"] or not data["PhoneNumber"]: messagebox.showerror("Error", "Name and Phone cannot be empty.", parent=window); return
        try:
            photo_path = data["PhotoPath"]; final_photo_path = photo_path
            photo_dir = self.config_manager.get("photo_dir", "")
            if photo_dir and photo_path and not photo_path.startswith(photo_dir):
                filename = f"{student_id}_{os.path.basename(photo_path)}"; final_photo_path = os.path.join(photo_dir, filename)
                shutil.copy(photo_path, final_photo_path); self.log_message(f"Photo updated: {final_photo_path}"); data["PhotoPath"] = final_photo_path
            data["DateOfBirth"] = data["DateOfBirth"] if data["DateOfBirth"] else None
            self.db_manager.update_student(student_id, data); self.log_message(f"Student ID {student_id} updated.", "SUCCESS"); messagebox.showinfo("Success", "Details updated.", parent=window)
            window.destroy(); self.fetch_and_display_profile(student_id); self.load_filter_options()
        except Exception as e:
            self.log_message(f"Update error: {e}", "ERROR"); messagebox.showerror("DB Error", f"Update error: {e}", parent=window)
    def check_birthdays(self):
        if not self.db_manager: messagebox.showerror("Database Error", "Database is not connected."); return
        self.log_message("Checking birthdays..."); self.birthday_listbox.delete(0, tk.END); today = datetime.now()
        try:
            sql = "SELECT StudentID, StudentName, PhoneNumber FROM Students WHERE DateOfBirth IS NOT NULL AND Month(DateOfBirth) = ? AND Day(DateOfBirth) = ?"
            self.birthday_students_list = self.db_manager.fetch_all(sql, (today.month, today.day))
            if not self.birthday_students_list: self.birthday_listbox.insert(tk.END, "No birthdays today.")
            else:
                self.log_message(f"Found {len(self.birthday_students_list)} birthday(s).", "SUCCESS")
                for student in self.birthday_students_list: self.birthday_listbox.insert(tk.END, f"{student[1]} (ID: {student[0]})")
        except Exception as e: self.log_message(f"Birthday check error: {e}", "ERROR")
    def start_filtered_messaging(self):
        if not self.whatsapp_bot: messagebox.showwarning("Not Logged In", "Please log in to WhatsApp first."); return
        message = self.bulk_message_text.get("1.0", tk.END).strip()
        if not message: messagebox.showwarning("Warning", "Message/caption cannot be empty."); return
        image_path = self.attachment_path_var.get()
        if image_path and not os.path.exists(image_path): messagebox.showerror("Error", "Attachment image not found."); return
        query = "SELECT StudentID FROM Students WHERE PhoneNumber IS NOT NULL AND PhoneNumber <> ''"; params = []
        filters = {"PracticalTime": self.practical_time_filter.get(), "TheoryTime": self.theory_time_filter.get(), "AcademicYear": self.academic_year_filter.get()}
        for field, value in filters.items():
            if value != "All": query += f" AND {field} = ?"; params.append(value)
        try:
            student_ids = [row[0] for row in self.db_manager.fetch_all(query, tuple(params))]
            if not student_ids: messagebox.showinfo("Info", "No students match filters."); return
            self.update_ui_for_task(True, "Sending messages..."); self.agent_thread = threading.Thread(target=self.run_messaging_task, args=(message, student_ids, image_path), daemon=True); self.agent_thread.start()
        except Exception as e: self.log_message(f"Filtered fetch error: {e}", "ERROR")
    def start_birthday_messaging(self):
        if not self.whatsapp_bot: messagebox.showwarning("Not Logged In", "Please log in to WhatsApp first."); return
        indices = self.birthday_listbox.curselection()
        if not hasattr(self, 'birthday_students_list') or not indices: messagebox.showwarning("Warning", "Select students."); return
        image_path = self.attachment_path_var.get()
        if image_path and not os.path.exists(image_path): messagebox.showerror("Error", "Attachment image not found."); return
        student_ids = [self.birthday_students_list[i][0] for i in indices]
        template = self.get_all_templates().get("Birthday Wish")
        self.update_ui_for_task(True, "Sending wishes..."); self.agent_thread = threading.Thread(target=self.run_messaging_task, args=(template, student_ids, image_path), daemon=True); self.agent_thread.start()
    def run_messaging_task(self, message_template, student_ids, image_path=None):
        total = len(student_ids); log_msg = f"Starting task for {total} students"
        if image_path: log_msg += " with attachment"
        self.log_message(log_msg, "INFO"); self.task_running.clear(); self.root.after(0, self._update_progress, 0, total, True)
        try:
            min_delay = int(self.min_delay_var.get()); max_delay = int(self.max_delay_var.get())
            if min_delay <= 0 or max_delay <= 0 : raise ValueError("Delay must be positive")
        except ValueError:
            self.log_message("Invalid delay value, using defaults.", "WARN"); min_delay, max_delay = 8, 15
        
        for i, student_id in enumerate(student_ids):
            if self.task_running.is_set(): self.log_message("Task cancelled.", "WARN"); break
            self.root.after(0, self._update_progress, i + 1, total)
            try:
                data = self.db_manager.fetch_one("SELECT * FROM Students WHERE StudentID = ?", (student_id,))
                if not data: self.log_message(f"Skip: No data for ID {student_id}", "WARN"); continue
                s_dict = dict(zip([d[0] for d in data.cursor_description], data)); name = s_dict.get('StudentName',''); phone = s_dict.get('PhoneNumber','')
                if not phone: self.log_message(f"Skip: {name} has no number.", "WARN"); continue
                self.update_statusbar_text(f"Sending to {name} ({i+1}/{total})...")
                final_message = self._prepare_message(message_template, s_dict)
                success, reason = self.whatsapp_bot.send_message(str(phone), final_message, image_path)
                if success: self.log_message(f"({i+1}/{total}) Sent to {name}.", "SUCCESS"); time.sleep(random.randint(min_delay, max_delay) if i < total - 1 else 0)
                else: self.log_message(f"({i+1}/{total}) FAILED for {name}: {reason}", "ERROR"); time.sleep(2)
            except Exception as e: self.log_message(f"Error for ID {student_id}: {e}", "FATAL")
        self.root.after(0, self._update_progress, 0, 0, False); self.root.after(0, self.update_ui_for_task, False)
    def _update_progress(self, current, total, show=True):
        if show: self.progress_bar.pack(fill=tk.X, padx=10, pady=5); self.progress_bar['maximum'] = total; self.progress_bar['value'] = current
        else: self.progress_bar.pack_forget()
    def _prepare_message(self, template, student_dict):
        message = template
        for key, value in student_dict.items():
            placeholder = f"{{{key}}}";
            if isinstance(value, datetime): value = value.strftime('%d-%b-%Y')
            message = message.replace(placeholder, str(value if value is not None else ""))
        return message
    def cancel_running_task(self):
        if self.agent_thread and self.agent_thread.is_alive():
            self.task_running.set(); self.log_message("Cancellation signal sent.", "WARN")
    def update_ui_for_task(self, is_starting, status_text="Ready"):
        state = tk.DISABLED if is_starting else tk.NORMAL
        cancel_state = tk.NORMAL if is_starting else tk.DISABLED
        self.login_button.config(state=state); self.settings_button.config(state=state); self.import_button.config(state=state)
        self.send_filtered_button.config(state=state if self.whatsapp_bot else tk.DISABLED)
        self.check_birthdays_button.config(state=state if self.db_manager else tk.DISABLED)
        self.send_birthday_wishes_button.config(state=state if self.whatsapp_bot else tk.DISABLED)
        self.edit_student_button.config(state=tk.DISABLED) 
        if self.current_profile_id and not is_starting: self.edit_student_button.config(state=tk.NORMAL)
        self.search_button.config(state=state); self.show_all_button.config(state=state)
        self.cancel_button.config(state=cancel_state)
        self.update_statusbar_text(status_text)
        if not is_starting: self.update_statusbar_text("Ready")
    def log_message(self, message, level="INFO"):
        self.root.after(0, self._log_message_thread_safe, message, level)
    def _log_message_thread_safe(self, message, level):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"[{level}] {message}\n")
        self.log_area.see(tk.END); self.log_area.config(state=tk.DISABLED)
    def update_statusbar_text(self, text):
        self.statusbar.config(text=text)
    def get_all_templates(self): return self.template_manager.get_templates()

if __name__ == "__main__":
    if not webdriver_available: sys.exit()
    root = tk.Tk()
    app = InstituteAgentApp(root)
    root.mainloop()