import tkinter as tk
from tkinter import ttk, messagebox, font
import datetime
import time
import random
import json
import os
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import base64

class PrefectAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("M.S.C BIBILE ශිශ්‍යනායක පැමිණීම් පද්ධතිය")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Color scheme (Blue and White)
        self.primary_color = "#1a4d8f"  # Dark blue
        self.secondary_color = "#ffffff"  # White
        self.accent_color = "#4a90e2"  # Light blue
        self.text_color = "#333333"  # Dark gray
        self.light_bg = "#f5f9ff"  # Very light blue
        self.dark_mode = False
        
        # Initialize variables
        self.current_user = None
        self.current_date = datetime.date.today()
        self.selected_prefect = None
        self.attendance_data = {}
        self.prefects_data = []
        self.notifications = []
        
        # Initialize data
        self.initialize_data()
        
        # Show loading screen
        self.show_loading_screen()
        
    def initialize_data(self):
        """Initialize sample data for prefects"""
        # Sample prefects data with Sinhala names
        self.prefects_data = [
            {"id": 1, "name": "කවිඳු සේනාරත්න", "grade": "13", "class": "A", "position": "Head Prefect", 
             "contact": "0711234567", "email": "kavindu@example.com", "emergency_contact": "පියා - 0777654321"},
            {"id": 2, "name": "සඳුනි පෙරේරා", "grade": "13", "class": "B", "position": "Deputy Head Prefect", 
             "contact": "0722345678", "email": "sanduni@example.com", "emergency_contact": "මව - 0778765432"},
            {"id": 3, "name": "චමින්ද කුමාර", "grade": "12", "class": "A", "position": "Senior Prefect", 
             "contact": "0733456789", "email": "chamin@example.com", "emergency_contact": "�ාප - 0779876543"},
            {"id": 4, "name": "නිලුමි ජයසිංහ", "grade": "12", "class": "B", "position": "Senior Prefect", 
             "contact": "0744567890", "email": "nilumi@example.com", "emergency_contact": "මව - 0770987654"},
            {"id": 5, "name": "සුරංග බණ්ඩාර", "grade": "12", "class": "C", "position": "Senior Prefect", 
             "contact": "0755678901", "email": "suranga@example.com", "emergency_contact": "පියා - 0771098765"},
            {"id": 6, "name": "මල්කාන්ති සිල්වා", "grade": "11", "class": "A", "position": "Junior Prefect", 
             "contact": "0766789012", "email": "malkanthi@example.com", "emergency_contact": "මව - 0772109876"},
            {"id": 7, "name": "කසුන් ප්‍රනාන්දු", "grade": "11", "class": "B", "position": "Junior Prefect", 
             "contact": "0777890123", "email": "kasun@example.com", "emergency_contact": "පියා - 0773210987"},
            {"id": 8, "name": "තිසරි රණසිංහ", "grade": "11", "class": "C", "position": "Junior Prefect", 
             "contact": "0788901234", "email": "thisari@example.com", "emergency_contact": "මව - 0774321098"},
            {"id": 9, "name": "දිනේෂ් ප්‍රනාන්දු", "grade": "10", "class": "A", "position": "Junior Prefect", 
             "contact": "0799012345", "email": "dinesh@example.com", "emergency_contact": "පියා - 0775432109"},
            {"id": 10, "name": "ශෂිකලා ද සිල්වා", "grade": "10", "class": "B", "position": "Junior Prefect", 
             "contact": "0700123456", "email": "shashikala@example.com", "emergency_contact": "මව - 0776543210"},
            {"id": 11, "name": "නිරෝෂන් විජේසිංහ", "grade": "13", "class": "C", "position": "Senior Prefect", 
             "contact": "0711234567", "email": "niroshan@example.com", "emergency_contact": "පියා - 0777654321"},
            {"id": 12, "name": "දිල්ෂානි ප්‍රනාන්දු", "grade": "12", "class": "A", "position": "Senior Prefect", 
             "contact": "0722345678", "email": "dilshani@example.com", "emergency_contact": "මව - 0778765432"},
            {"id": 13, "name": "කවින්ද්‍යා තෙන්නකෝන්", "grade": "11", "class": "A", "position": "Junior Prefect", 
             "contact": "0733456789", "email": "kavindya@example.com", "emergency_contact": "මව - 0779876543"},
            {"id": 14, "name": "චනුක ද සිල්වා", "grade": "10", "class": "C", "position": "Junior Prefect", 
             "contact": "0744567890", "email": "chanuka@example.com", "emergency_contact": "පියා - 0770987654"},
            {"id": 15, "name": "නිමාලි බණ්ඩාර", "grade": "13", "class": "B", "position": "Senior Prefect", 
             "contact": "0755678901", "email": "nimali@example.com", "emergency_contact": "මව - 0771098765"},
            {"id": 16, "name": "කේෂාන් මුණසිංහ", "grade": "12", "class": "B", "position": "Senior Prefect", 
             "contact": "0766789012", "email": "keshan@example.com", "emergency_contact": "පියා - 0772109876"},
            {"id": 17, "name": "සචිනි රණවීර", "grade": "11", "class": "B", "position": "Junior Prefect", 
             "contact": "0777890123", "email": "sachini@example.com", "emergency_contact": "මව - 0773210987"},
            {"id": 18, "name": "අමිල ප්‍රනාන්දු", "grade": "10", "class": "A", "position": "Junior Prefect", 
             "contact": "0788901234", "email": "amila@example.com", "emergency_contact": "පියා - 0774321098"},
            {"id": 19, "name": "සුගන්ධිකා සෙනෙවිරත්න", "grade": "13", "class": "A", "position": "Senior Prefect", 
             "contact": "0799012345", "email": "sugandhika@example.com", "emergency_contact": "මව - 0775432109"},
            {"id": 20, "name": "ලහිරු පෙරේරා", "grade": "12", "class": "C", "position": "Senior Prefect", 
             "contact": "0700123456", "email": "lahiru@example.com", "emergency_contact": "පියා - 0776543210"}
        ]
        
        # Initialize attendance data
        for prefect in self.prefects_data:
            self.attendance_data[prefect["id"]] = {
                "dates": {},
                "total_days": 0,
                "present_days": 0,
                "absent_days": 0,
                "late_days": 0
            }
        
        # Initialize sample attendance data
        self.initialize_sample_attendance()
        
        # Initialize notifications
        self.notifications = [
            {"id": 1, "message": "දින 3ක් නොපැමිණි ශිශ්‍යනායකයින් ඇත", "time": "10:30 AM", "read": False},
            {"id": 2, "message": "අද සියලුම ශිශ්‍යනායකයින් පැමිණ ඇත", "time": "Yesterday", "read": True},
            {"id": 3, "message": "නව ශිශ්‍යනායක තෝරා ගැනීම සඳහා අයදුම්පත් කැඳවයි", "time": "2 days ago", "read": True}
        ]
        
    def initialize_sample_attendance(self):
        """Initialize sample attendance data for demonstration"""
        today = datetime.date.today()
        
        # Generate random attendance for the past 30 days
        for i in range(30):
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            for prefect in self.prefects_data:
                # Random attendance status
                rand = random.random()
                if rand < 0.8:  # 80% chance of being present
                    status = "Present"
                    time_arrived = f"{random.randint(7, 8):02d}:{random.randint(0, 59):02d}"
                elif rand < 0.9:  # 10% chance of being late
                    status = "Late"
                    time_arrived = f"{random.randint(8, 9):02d}:{random.randint(0, 59):02d}"
                else:  # 10% chance of being absent
                    status = "Absent"
                    time_arrived = None
                
                # Add to attendance data
                self.attendance_data[prefect["id"]]["dates"][date_str] = {
                    "status": status,
                    "time_arrived": time_arrived
                }
                
                # Update counters
                self.attendance_data[prefect["id"]]["total_days"] += 1
                if status == "Present":
                    self.attendance_data[prefect["id"]]["present_days"] += 1
                elif status == "Late":
                    self.attendance_data[prefect["id"]]["late_days"] += 1
                else:  # Absent
                    self.attendance_data[prefect["id"]]["absent_days"] += 1
    
    def show_loading_screen(self):
        """Display loading screen with animation"""
        self.loading_frame = tk.Frame(self.root, bg=self.primary_color)
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center frame
        center_frame = tk.Frame(self.loading_frame, bg=self.primary_color)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # School logo placeholder (using text)
        logo_label = tk.Label(center_frame, text="M.S.C BIBILE", 
                             font=("Arial", 28, "bold"), 
                             bg=self.primary_color, 
                             fg=self.secondary_color)
        logo_label.pack(pady=20)
        
        # Loading text
        loading_label = tk.Label(center_frame, text="ශිශ්‍යනායක පැමිණීම් පද්ධතිය පූරණය වෙමින්...", 
                               font=("Arial", 14), 
                               bg=self.primary_color, 
                               fg=self.secondary_color)
        loading_label.pack(pady=10)
        
        # Progress bar
        progress_bar = ttk.Progressbar(center_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress_bar.pack(pady=20)
        
        # Loading animation
        self.loading_progress = 0
        self.update_loading(progress_bar)
        
    def update_loading(self, progress_bar):
        """Update loading progress bar"""
        self.loading_progress += 5
        progress_bar['value'] = self.loading_progress
        
        if self.loading_progress < 100:
            self.root.after(100, lambda: self.update_loading(progress_bar))
        else:
            self.loading_frame.destroy()
            self.show_login_screen()
    
    def show_login_screen(self):
        """Display login screen"""
        self.login_frame = tk.Frame(self.root, bg=self.primary_color)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center frame
        center_frame = tk.Frame(self.login_frame, bg=self.secondary_color, relief=tk.RAISED, bd=2)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=400)
        
        # School logo
        logo_frame = tk.Frame(center_frame, bg=self.primary_color)
        logo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        logo_label = tk.Label(logo_frame, text="M.S.C BIBILE", 
                             font=("Arial", 20, "bold"), 
                             bg=self.primary_color, 
                             fg=self.secondary_color,
                             pady=10)
        logo_label.pack()
        
        # Login title
        title_label = tk.Label(center_frame, text="ශිශ්‍යනායක පැමිණීම් පද්ධතිය", 
                              font=("Arial", 16, "bold"), 
                              bg=self.secondary_color, 
                              fg=self.primary_color,
                              pady=10)
        title_label.pack()
        
        # Username
        username_frame = tk.Frame(center_frame, bg=self.secondary_color)
        username_frame.pack(fill=tk.X, padx=30, pady=10)
        
        username_label = tk.Label(username_frame, text="පරිශීලක නාමය:", 
                                 font=("Arial", 12), 
                                 bg=self.secondary_color, 
                                 fg=self.text_color,
                                 anchor=tk.W)
        username_label.pack(fill=tk.X)
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.username_entry.pack(fill=tk.X, pady=5)
        self.username_entry.insert(0, "admin")  # Default username for demo
        
        # Password
        password_frame = tk.Frame(center_frame, bg=self.secondary_color)
        password_frame.pack(fill=tk.X, padx=30, pady=10)
        
        password_label = tk.Label(password_frame, text="මුරපදය:", 
                                 font=("Arial", 12), 
                                 bg=self.secondary_color, 
                                 fg=self.text_color,
                                 anchor=tk.W)
        password_label.pack(fill=tk.X)
        
        self.password_entry = tk.Entry(password_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, show="*")
        self.password_entry.pack(fill=tk.X, pady=5)
        self.password_entry.insert(0, "password")  # Default password for demo
        
        # Remember me checkbox
        remember_frame = tk.Frame(center_frame, bg=self.secondary_color)
        remember_frame.pack(fill=tk.X, padx=30, pady=5)
        
        self.remember_var = tk.IntVar()
        remember_check = tk.Checkbutton(remember_frame, text="මම මතක තබාගන්න", 
                                       variable=self.remember_var, 
                                       font=("Arial", 10), 
                                       bg=self.secondary_color, 
                                       fg=self.text_color,
                                       selectcolor=self.secondary_color,
                                       activebackground=self.secondary_color,
                                       activeforeground=self.text_color)
        remember_check.pack(anchor=tk.W)
        
        # Forgot password link
        forgot_pass = tk.Label(center_frame, text="මුරපදය අමතකද?", 
                              font=("Arial", 10, "underline"), 
                              bg=self.secondary_color, 
                              fg=self.accent_color,
                              cursor="hand2")
        forgot_pass.pack(pady=5)
        forgot_pass.bind("<Button-1>", lambda e: self.forgot_password())
        
        # Login button
        login_button = tk.Button(center_frame, text="පිවිසෙන්න", 
                                font=("Arial", 12, "bold"), 
                                bg=self.primary_color, 
                                fg=self.secondary_color,
                                bd=0,
                                padx=20,
                                pady=10,
                                cursor="hand2",
                                command=self.login)
        login_button.pack(pady=20)
        
        # Bind Enter key to login
        self.root.bind("<Return>", lambda e: self.login())
    
    def forgot_password(self):
        """Handle forgot password functionality"""
        messagebox.showinfo("මුරපදය අමතකද?", "කරුණාකර පරිපාලක වෙත සම්බන්ධ වන්න: admin@mscbibile.edu.lk")
    
    def login(self):
        """Handle login functionality"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Simple authentication (in a real app, this would be more secure)
        if username == "admin" and password == "password":
            self.current_user = {"username": username, "role": "admin"}
            self.login_frame.destroy()
            self.show_dashboard()
        else:
            messagebox.showerror("පිවිසීම අසමත් විය", "වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්. කරුණාකර නැවත උත්සාහ කරන්න.")
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.dashboard_frame = tk.Frame(self.root, bg=self.light_bg)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header()
        
        # Main content area
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top row - Stats cards and date/time
        top_row = tk.Frame(main_content, bg=self.light_bg)
        top_row.pack(fill=tk.X, pady=(0, 20))
        
        # Stats cards
        stats_frame = tk.Frame(top_row, bg=self.light_bg)
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Total Prefects card
        total_card = self.create_stats_card(stats_frame, "සම්පූර්ණ ශිශ්‍යනායකයින්", str(len(self.prefects_data)), self.primary_color)
        total_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Present Today card
        present_count = self.get_attendance_count("Present")
        present_card = self.create_stats_card(stats_frame, "අද පැමිණි", str(present_count), "#2ecc71")
        present_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Absent Today card
        absent_count = self.get_attendance_count("Absent")
        absent_card = self.create_stats_card(stats_frame, "අද නොපැමිණි", str(absent_count), "#e74c3c")
        absent_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Late Arrivals card
        late_count = self.get_attendance_count("Late")
        late_card = self.create_stats_card(stats_frame, "ප්‍රමාද වී පැමිණි", str(late_count), "#f39c12")
        late_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Date and time panel
        datetime_frame = tk.Frame(top_row, bg=self.primary_color, relief=tk.RAISED, bd=1)
        datetime_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Date selector
        date_label = tk.Label(datetime_frame, text="දිනය තෝරන්න:", 
                             font=("Arial", 10), 
                             bg=self.primary_color, 
                             fg=self.secondary_color)
        date_label.pack(padx=10, pady=(10, 0))
        
        self.date_selector = DateEntry(datetime_frame, width=12, background=self.primary_color, 
                                      foreground=self.secondary_color, borderwidth=2,
                                      date_pattern='yyyy-mm-dd')
        self.date_selector.pack(padx=10, pady=(0, 10))
        self.date_selector.set_date(self.current_date)
        self.date_selector.bind("<<DateEntrySelected>>", self.on_date_change)
        
        # Real-time clock
        self.clock_label = tk.Label(datetime_frame, text="", 
                                   font=("Arial", 16, "bold"), 
                                   bg=self.primary_color, 
                                   fg=self.secondary_color,
                                   pady=10)
        self.clock_label.pack(padx=10, pady=(0, 10))
        self.update_clock()
        
        # Bottom row - Quick actions
        bottom_row = tk.Frame(main_content, bg=self.light_bg)
        bottom_row.pack(fill=tk.BOTH, expand=True)
        
        # Attendance management section
        attendance_frame = tk.LabelFrame(bottom_row, text="පැමිණීම් කළමනාකරණය", 
                                        font=("Arial", 14, "bold"), 
                                        bg=self.secondary_color, 
                                        fg=self.primary_color,
                                        relief=tk.RAISED, bd=2)
        attendance_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Attendance buttons
        attendance_buttons = tk.Frame(attendance_frame, bg=self.secondary_color)
        attendance_buttons.pack(fill=tk.X, padx=10, pady=10)
        
        mark_all_present_btn = tk.Button(attendance_buttons, text="සියලුම දෙනා පැමිණියා ලෙස සලකුණු කරන්න", 
                                        font=("Arial", 10), 
                                        bg="#2ecc71", 
                                        fg=self.secondary_color,
                                        bd=0,
                                        padx=10,
                                        pady=5,
                                        cursor="hand2",
                                        command=lambda: self.mark_all_attendance("Present"))
        mark_all_present_btn.pack(side=tk.LEFT, padx=5)
        
        mark_all_absent_btn = tk.Button(attendance_buttons, text="සියලුම දෙනා නොපැමිණියා ලෙස සලකුණු කරන්න", 
                                       font=("Arial", 10), 
                                       bg="#e74c3c", 
                                       fg=self.secondary_color,
                                       bd=0,
                                       padx=10,
                                       pady=5,
                                       cursor="hand2",
                                       command=lambda: self.mark_all_attendance("Absent"))
        mark_all_absent_btn.pack(side=tk.LEFT, padx=5)
        
        # Prefects list
        list_frame = tk.Frame(attendance_frame, bg=self.secondary_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search bar
        search_frame = tk.Frame(list_frame, bg=self.secondary_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_label = tk.Label(search_frame, text="සොයන්න:", 
                               font=("Arial", 10), 
                               bg=self.secondary_color, 
                               fg=self.text_color)
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), bd=2, relief=tk.GROOVE)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_prefects)
        
        # Filter dropdown
        filter_label = tk.Label(search_frame, text="පෙරහන:", 
                               font=("Arial", 10), 
                               bg=self.secondary_color, 
                               fg=self.text_color)
        filter_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_var.set("සියලුම")
        filter_options = ["සියලුම", "පැමිණි", "නොපැමිණි", "ප්‍රමාද වී පැමිණි"]
        filter_dropdown = ttk.Combobox(search_frame, textvariable=self.filter_var, values=filter_options, state="readonly", width=15)
        filter_dropdown.pack(side=tk.LEFT)
        filter_dropdown.bind("<<ComboboxSelected>>", self.filter_prefects)
        
        # Prefects list with scrollbar
        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prefects_listbox = tk.Listbox(list_frame, font=("Arial", 10), bd=2, relief=tk.GROOVE, 
                                          yscrollcommand=list_scroll.set, height=10)
        self.prefects_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.prefects_listbox.yview)
        
        self.prefects_listbox.bind("<<ListboxSelect>>", self.on_prefect_select)
        
        # Populate prefects list
        self.populate_prefects_list()
        
        # Attendance buttons for selected prefect
        attendance_btn_frame = tk.Frame(attendance_frame, bg=self.secondary_color)
        attendance_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.present_btn = tk.Button(attendance_btn_frame, text="පැමිණියා", 
                                    font=("Arial", 10, "bold"), 
                                    bg="#2ecc71", 
                                    fg=self.secondary_color,
                                    bd=0,
                                    padx=20,
                                    pady=5,
                                    cursor="hand2",
                                    state=tk.DISABLED,
                                    command=lambda: self.mark_attendance("Present"))
        self.present_btn.pack(side=tk.LEFT, padx=5)
        
        self.absent_btn = tk.Button(attendance_btn_frame, text="නොපැමිණියා", 
                                   font=("Arial", 10, "bold"), 
                                   bg="#e74c3c", 
                                   fg=self.secondary_color,
                                   bd=0,
                                   padx=20,
                                   pady=5,
                                   cursor="hand2",
                                   state=tk.DISABLED,
                                   command=lambda: self.mark_attendance("Absent"))
        self.absent_btn.pack(side=tk.LEFT, padx=5)
        
        self.late_btn = tk.Button(attendance_btn_frame, text="ප්‍රමාද වී පැමිණියා", 
                                 font=("Arial", 10, "bold"), 
                                 bg="#f39c12", 
                                 fg=self.secondary_color,
                                 bd=0,
                                 padx=20,
                                 pady=5,
                                 cursor="hand2",
                                 state=tk.DISABLED,
                                 command=lambda: self.mark_attendance("Late"))
        self.late_btn.pack(side=tk.LEFT, padx=5)
        
        # Reports section
        reports_frame = tk.LabelFrame(bottom_row, text="වාර්තා", 
                                     font=("Arial", 14, "bold"), 
                                     bg=self.secondary_color, 
                                     fg=self.primary_color,
                                     relief=tk.RAISED, bd=2)
        reports_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Report buttons
        report_buttons = tk.Frame(reports_frame, bg=self.secondary_color)
        report_buttons.pack(fill=tk.X, padx=10, pady=10)
        
        daily_report_btn = tk.Button(report_buttons, text="දිනපතා වාර්තාව", 
                                    font=("Arial", 10), 
                                    bg=self.primary_color, 
                                    fg=self.secondary_color,
                                    bd=0,
                                    padx=10,
                                    pady=5,
                                    cursor="hand2",
                                    command=lambda: self.show_report("daily"))
        daily_report_btn.pack(side=tk.LEFT, padx=5)
        
        weekly_report_btn = tk.Button(report_buttons, text="සතිපතා සාරාංශය", 
                                     font=("Arial", 10), 
                                     bg=self.primary_color, 
                                     fg=self.secondary_color,
                                     bd=0,
                                     padx=10,
                                     pady=5,
                                     cursor="hand2",
                                     command=lambda: self.show_report("weekly"))
        weekly_report_btn.pack(side=tk.LEFT, padx=5)
        
        monthly_report_btn = tk.Button(report_buttons, text="මාසික සංඛ්‍යාලේඛන", 
                                     font=("Arial", 10), 
                                     bg=self.primary_color, 
                                     fg=self.secondary_color,
                                     bd=0,
                                     padx=10,
                                     pady=5,
                                     cursor="hand2",
                                     command=lambda: self.show_report("monthly"))
        monthly_report_btn.pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        export_frame = tk.Frame(reports_frame, bg=self.secondary_color)
        export_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        export_pdf_btn = tk.Button(export_frame, text="PDF ලෙස අපනයනය කරන්න", 
                                  font=("Arial", 10), 
                                  bg=self.accent_color, 
                                  fg=self.secondary_color,
                                  bd=0,
                                  padx=10,
                                  pady=5,
                                  cursor="hand2",
                                  command=lambda: self.export_report("pdf"))
        export_pdf_btn.pack(side=tk.LEFT, padx=5)
        
        export_print_btn = tk.Button(export_frame, text="මුද්‍රණය කරන්න", 
                                    font=("Arial", 10), 
                                    bg=self.accent_color, 
                                    fg=self.secondary_color,
                                    bd=0,
                                    padx=10,
                                    pady=5,
                                    cursor="hand2",
                                    command=lambda: self.export_report("print"))
        export_print_btn.pack(side=tk.LEFT, padx=5)
        
        # Attendance chart
        chart_frame = tk.Frame(reports_frame, bg=self.secondary_color)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_attendance_chart(chart_frame)
    
    def create_header(self):
        """Create application header"""
        header = tk.Frame(self.dashboard_frame, bg=self.primary_color, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header, bg=self.primary_color)
        logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        logo_label = tk.Label(logo_frame, text="M.S.C BIBILE", 
                             font=("Arial", 16, "bold"), 
                             bg=self.primary_color, 
                             fg=self.secondary_color)
        logo_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(logo_frame, text="ශිශ්‍යනායක පැමිණීම් පද්ධතිය", 
                                 font=("Arial", 12), 
                                 bg=self.primary_color, 
                                 fg=self.secondary_color)
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Navigation buttons
        nav_frame = tk.Frame(header, bg=self.primary_color)
        nav_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        dashboard_btn = tk.Button(nav_frame, text="මුල් පුවරුව", 
                                 font=("Arial", 10), 
                                 bg=self.accent_color, 
                                 fg=self.secondary_color,
                                 bd=0,
                                 padx=10,
                                 pady=5,
                                 cursor="hand2",
                                 command=self.show_dashboard)
        dashboard_btn.pack(side=tk.LEFT, padx=5)
        
        attendance_btn = tk.Button(nav_frame, text="පැමිණීම්", 
                                  font=("Arial", 10), 
                                  bg=self.accent_color, 
                                  fg=self.secondary_color,
                                  bd=0,
                                  padx=10,
                                  pady=5,
                                  cursor="hand2",
                                  command=self.show_attendance_management)
        attendance_btn.pack(side=tk.LEFT, padx=5)
        
        reports_btn = tk.Button(nav_frame, text="වාර්තා", 
                               font=("Arial", 10), 
                               bg=self.accent_color, 
                               fg=self.secondary_color,
                               bd=0,
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.show_reports)
        reports_btn.pack(side=tk.LEFT, padx=5)
        
        profiles_btn = tk.Button(nav_frame, text="පැතිකඩ", 
                                font=("Arial", 10), 
                                bg=self.accent_color, 
                                fg=self.secondary_color,
                                bd=0,
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.show_profiles)
        profiles_btn.pack(side=tk.LEFT, padx=5)
        
        # Notifications button
        notifications_btn = tk.Button(nav_frame, text="දැනුම්දීම්", 
                                     font=("Arial", 10), 
                                     bg=self.accent_color, 
                                     fg=self.secondary_color,
                                     bd=0,
                                     padx=10,
                                     pady=5,
                                     cursor="hand2",
                                     command=self.show_notifications)
        notifications_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings button
        settings_btn = tk.Button(nav_frame, text="සැකසුම්", 
                                font=("Arial", 10), 
                                bg=self.accent_color, 
                                fg=self.secondary_color,
                                bd=0,
                                padx=10,
                                pady=5,
                                cursor="hand2",
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Logout button
        logout_btn = tk.Button(nav_frame, text="නික්මෙන්න", 
                              font=("Arial", 10), 
                               bg="#e74c3c", 
                               fg=self.secondary_color,
                               bd=0,
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.logout)
        logout_btn.pack(side=tk.LEFT, padx=5)
    
    def create_stats_card(self, parent, title, value, color):
        """Create a stats card widget"""
        card = tk.Frame(parent, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        
        # Card header
        header = tk.Frame(card, bg=color, height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, 
                              font=("Arial", 10, "bold"), 
                              bg=color, 
                              fg=self.secondary_color)
        title_label.pack(pady=5)
        
        # Card value
        value_label = tk.Label(card, text=value, 
                              font=("Arial", 24, "bold"), 
                              bg=self.secondary_color, 
                              fg=color)
        value_label.pack(pady=10)
        
        return card
    
    def update_clock(self):
        """Update real-time clock"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        self.clock_label.config(text=f"{date_str}\n{time_str}")
        self.root.after(1000, self.update_clock)
    
    def on_date_change(self, event):
        """Handle date change event"""
        selected_date = self.date_selector.get_date()
        self.current_date = selected_date
        self.populate_prefects_list()
        self.update_stats_cards()
    
    def get_attendance_count(self, status):
        """Get count of prefects with given attendance status for current date"""
        date_str = self.current_date.strftime("%Y-%m-%d")
        count = 0
        
        for prefect_id in self.attendance_data:
            if date_str in self.attendance_data[prefect_id]["dates"]:
                if self.attendance_data[prefect_id]["dates"][date_str]["status"] == status:
                    count += 1
        
        return count
    
    def update_stats_cards(self):
        """Update stats cards with current date data"""
        # This would be implemented to update the stats cards when date changes
        pass
    
    def populate_prefects_list(self):
        """Populate the prefects list with current data"""
        self.prefects_listbox.delete(0, tk.END)
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        for prefect in self.prefects_data:
            # Get attendance status for current date
            status = "නොදනී"
            status_color = self.text_color
            
            if date_str in self.attendance_data[prefect["id"]]["dates"]:
                status = self.attendance_data[prefect["id"]]["dates"][date_str]["status"]
                if status == "Present":
                    status = "පැමිණියා"
                    status_color = "#2ecc71"
                elif status == "Absent":
                    status = "නොපැමිණියා"
                    status_color = "#e74c3c"
                elif status == "Late":
                    status = "ප්‍රමාද වී පැමිණියා"
                    status_color = "#f39c12"
            
            # Format list item
            list_item = f"{prefect['name']} - {prefect['grade']} {prefect['class']} - {prefect['position']} - {status}"
            
            # Add to listbox
            self.prefects_listbox.insert(tk.END, list_item)
            
            # Set item color based on status
            self.prefects_listbox.itemconfig(tk.END, {'fg': status_color})
    
    def filter_prefects(self, event=None):
        """Filter prefects list based on search and filter criteria"""
        search_term = self.search_entry.get().lower()
        filter_value = self.filter_var.get()
        
        self.prefects_listbox.delete(0, tk.END)
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        for prefect in self.prefects_data:
            # Check if prefect matches search term
            if search_term and search_term not in prefect['name'].lower() and \
               search_term not in prefect['grade'].lower() and \
               search_term not in prefect['position'].lower():
                continue
            
            # Get attendance status for current date
            status = "නොදනී"
            status_color = self.text_color
            
            if date_str in self.attendance_data[prefect["id"]]["dates"]:
                status = self.attendance_data[prefect["id"]]["dates"][date_str]["status"]
                if status == "Present":
                    status = "පැමිණියා"
                    status_color = "#2ecc71"
                elif status == "Absent":
                    status = "නොපැමිණියා"
                    status_color = "#e74c3c"
                elif status == "Late":
                    status = "ප්‍රමාද වී පැමිණියා"
                    status_color = "#f39c12"
            
            # Apply filter
            if filter_value != "සියලුම":
                if filter_value == "පැමිණි" and status != "පැමිණියා":
                    continue
                elif filter_value == "නොපැමිණි" and status != "නොපැමිණියා":
                    continue
                elif filter_value == "ප්‍රමාද වී පැමිණි" and status != "ප්‍රමාද වී පැමිණියා":
                    continue
            
            # Format list item
            list_item = f"{prefect['name']} - {prefect['grade']} {prefect['class']} - {prefect['position']} - {status}"
            
            # Add to listbox
            self.prefects_listbox.insert(tk.END, list_item)
            
            # Set item color based on status
            self.prefects_listbox.itemconfig(tk.END, {'fg': status_color})
    
    def on_prefect_select(self, event):
        """Handle prefect selection from list"""
        selection = self.prefects_listbox.curselection()
        if not selection:
            return
        
        # Get selected prefect
        index = selection[0]
        prefect_name = self.prefects_listbox.get(index).split(" - ")[0]
        
        # Find prefect in data
        for prefect in self.prefects_data:
            if prefect['name'] == prefect_name:
                self.selected_prefect = prefect
                break
        
        # Enable attendance buttons
        self.present_btn.config(state=tk.NORMAL)
        self.absent_btn.config(state=tk.NORMAL)
        self.late_btn.config(state=tk.NORMAL)
    
    def mark_attendance(self, status):
        """Mark attendance for selected prefect"""
        if not self.selected_prefect:
            return
        
        date_str = self.current_date.strftime("%Y-%m-%d")
        time_arrived = None
        
        if status in ["Present", "Late"]:
            now = datetime.datetime.now()
            time_arrived = now.strftime("%H:%M")
        
        # Update attendance data
        self.attendance_data[self.selected_prefect["id"]]["dates"][date_str] = {
            "status": status,
            "time_arrived": time_arrived
        }
        
        # Show success message
        status_text = ""
        if status == "Present":
            status_text = "පැමිණියා"
        elif status == "Absent":
            status_text = "නොපැමිණියා"
        elif status == "Late":
            status_text = "ප්‍රමාද වී පැමිණියා"
        
        messagebox.showinfo("සාර්ථකයි", f"{self.selected_prefect['name']} ගේ පැමිණීම {status_text} ලෙස සටහන් කරන ලදී.")
        
        # Refresh list
        self.populate_prefects_list()
        self.filter_prefects()
    
    def mark_all_attendance(self, status):
        """Mark attendance for all prefects"""
        confirm = messagebox.askyesno("තහවුරු කරන්න", f"සියලුම ශිශ්‍යනායකයින් {status} ලෙස සලකුණු කිරීමට අවශ්‍යද?")
        
        if not confirm:
            return
        
        date_str = self.current_date.strftime("%Y-%m-%d")
        time_arrived = None
        
        if status in ["Present", "Late"]:
            now = datetime.datetime.now()
            time_arrived = now.strftime("%H:%M")
        
        # Update attendance data for all prefects
        for prefect in self.prefects_data:
            self.attendance_data[prefect["id"]]["dates"][date_str] = {
                "status": status,
                "time_arrived": time_arrived
            }
        
        # Show success message
        status_text = ""
        if status == "Present":
            status_text = "පැමිණියා"
        elif status == "Absent":
            status_text = "නොපැමිණියා"
        elif status == "Late":
            status_text = "ප්‍රමාද වී පැමිණියා"
        
        messagebox.showinfo("සාර්ථකයි", f"සියලුම ශිශ්‍යනායකයින්ගේ පැමිණීම {status_text} ලෙස සටහන් කරන ලදී.")
        
        # Refresh list
        self.populate_prefects_list()
        self.filter_prefects()
    
    def create_attendance_chart(self, parent):
        """Create attendance statistics chart"""
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data for the last 7 days
        dates = []
        present_counts = []
        absent_counts = []
        late_counts = []
        
        for i in range(6, -1, -1):
            date = datetime.date.today() - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            dates.append(date.strftime("%m/%d"))
            
            present = 0
            absent = 0
            late = 0
            
            for prefect_id in self.attendance_data:
                if date_str in self.attendance_data[prefect_id]["dates"]:
                    status = self.attendance_data[prefect_id]["dates"][date_str]["status"]
                    if status == "Present":
                        present += 1
                    elif status == "Absent":
                        absent += 1
                    elif status == "Late":
                        late += 1
            
            present_counts.append(present)
            absent_counts.append(absent)
            late_counts.append(late)
        
        # Create stacked bar chart
        ax.bar(dates, present_counts, color='#2ecc71', label='පැමිණි')
        ax.bar(dates, absent_counts, bottom=present_counts, color='#e74c3c', label='නොපැමිණි')
        ax.bar(dates, late_counts, bottom=[i+j for i,j in zip(present_counts, absent_counts)], color='#f39c12', label='ප්‍රමාද වී පැමිණි')
        
        ax.set_title('පසුගිය සතියේ පැමිණීම් සංඛ්‍යාලේඛන', fontdict={'fontsize': 10})
        ax.set_xlabel('දිනය', fontdict={'fontsize': 8})
        ax.set_ylabel('ශිශ්‍යනායකයින් ගණන', fontdict={'fontsize': 8})
        ax.legend(fontsize=8)
        
        # Add chart to frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_attendance_management(self):
        """Show attendance management screen"""
        # Clear current frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self.create_header()
        
        # Main content
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_content, text="පැමිණීම් කළමනාකරණය", 
                        font=("Arial", 18, "bold"), 
                        bg=self.light_bg, 
                        fg=self.primary_color)
        title.pack(pady=(0, 20))
        
        # Date selector
        date_frame = tk.Frame(main_content, bg=self.light_bg)
        date_frame.pack(fill=tk.X, pady=(0, 20))
        
        date_label = tk.Label(date_frame, text="දිනය තෝරන්න:", 
                             font=("Arial", 12), 
                             bg=self.light_bg, 
                             fg=self.text_color)
        date_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.attendance_date_selector = DateEntry(date_frame, width=12, background=self.primary_color, 
                                                foreground=self.secondary_color, borderwidth=2,
                                                date_pattern='yyyy-mm-dd')
        self.attendance_date_selector.pack(side=tk.LEFT, padx=(0, 20))
        self.attendance_date_selector.set_date(self.current_date)
        self.attendance_date_selector.bind("<<DateEntrySelected>>", self.on_attendance_date_change)
        
        # Search and filter
        search_filter_frame = tk.Frame(main_content, bg=self.light_bg)
        search_filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        search_label = tk.Label(search_filter_frame, text="සොයන්න:", 
                               font=("Arial", 12), 
                               bg=self.light_bg, 
                               fg=self.text_color)
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.attendance_search_entry = tk.Entry(search_filter_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, width=30)
        self.attendance_search_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.attendance_search_entry.bind("<KeyRelease>", self.filter_attendance_list)
        
        filter_label = tk.Label(search_filter_frame, text="පෙරහන:", 
                               font=("Arial", 12), 
                               bg=self.light_bg, 
                               fg=self.text_color)
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.attendance_filter_var = tk.StringVar()
        self.attendance_filter_var.set("සියලුම")
        filter_options = ["සියලුම", "පැමිණි", "නොපැමිණි", "ප්‍රමාද වී පැමිණි"]
        filter_dropdown = ttk.Combobox(search_filter_frame, textvariable=self.attendance_filter_var, values=filter_options, state="readonly", width=15)
        filter_dropdown.pack(side=tk.LEFT)
        filter_dropdown.bind("<<ComboboxSelected>>", self.filter_attendance_list)
        
        # Bulk actions
        bulk_frame = tk.Frame(main_content, bg=self.light_bg)
        bulk_frame.pack(fill=tk.X, pady=(0, 20))
        
        mark_all_present_btn = tk.Button(bulk_frame, text="සියලුම දෙනා පැමිණියා ලෙස සලකුණු කරන්න", 
                                        font=("Arial", 12), 
                                        bg="#2ecc71", 
                                        fg=self.secondary_color,
                                        bd=0,
                                        padx=20,
                                        pady=10,
                                        cursor="hand2",
                                        command=lambda: self.mark_all_attendance("Present"))
        mark_all_present_btn.pack(side=tk.LEFT, padx=5)
        
        mark_all_absent_btn = tk.Button(bulk_frame, text="සියලුම දෙනා නොපැමිණියා ලෙස සලකුණු කරන්න", 
                                       font=("Arial", 12), 
                                       bg="#e74c3c", 
                                       fg=self.secondary_color,
                                       bd=0,
                                       padx=20,
                                       pady=10,
                                       cursor="hand2",
                                       command=lambda: self.mark_all_attendance("Absent"))
        mark_all_absent_btn.pack(side=tk.LEFT, padx=5)
        
        # Prefects table
        table_frame = tk.Frame(main_content, bg=self.light_bg)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for prefects
        columns = ("ID", "Name", "Grade", "Class", "Position", "Status", "Time")
        self.attendance_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.attendance_tree.heading("ID", text="ID")
        self.attendance_tree.heading("Name", text="නම")
        self.attendance_tree.heading("Grade", text="ශ්‍රේණිය")
        self.attendance_tree.heading("Class", text="පන්තිය")
        self.attendance_tree.heading("Position", text="තනතුර")
        self.attendance_tree.heading("Status", text="තත්ත්වය")
        self.attendance_tree.heading("Time", text="පැමිණි වේලාව")
        
        # Define columns
        self.attendance_tree.column("ID", width=40, anchor=tk.CENTER)
        self.attendance_tree.column("Name", width=200, anchor=tk.W)
        self.attendance_tree.column("Grade", width=60, anchor=tk.CENTER)
        self.attendance_tree.column("Class", width=60, anchor=tk.CENTER)
        self.attendance_tree.column("Position", width=150, anchor=tk.W)
        self.attendance_tree.column("Status", width=100, anchor=tk.CENTER)
        self.attendance_tree.column("Time", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate table
        self.populate_attendance_table()
        
        # Attendance buttons
        attendance_btn_frame = tk.Frame(main_content, bg=self.light_bg)
        attendance_btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.att_present_btn = tk.Button(attendance_btn_frame, text="පැමිණියා", 
                                        font=("Arial", 12, "bold"), 
                                        bg="#2ecc71", 
                                        fg=self.secondary_color,
                                        bd=0,
                                        padx=20,
                                        pady=10,
                                        cursor="hand2",
                                        state=tk.DISABLED,
                                        command=lambda: self.mark_table_attendance("Present"))
        self.att_present_btn.pack(side=tk.LEFT, padx=5)
        
        self.att_absent_btn = tk.Button(attendance_btn_frame, text="නොපැමිණියා", 
                                       font=("Arial", 12, "bold"), 
                                       bg="#e74c3c", 
                                       fg=self.secondary_color,
                                       bd=0,
                                       padx=20,
                                       pady=10,
                                       cursor="hand2",
                                       state=tk.DISABLED,
                                       command=lambda: self.mark_table_attendance("Absent"))
        self.att_absent_btn.pack(side=tk.LEFT, padx=5)
        
        self.att_late_btn = tk.Button(attendance_btn_frame, text="ප්‍රමාද වී පැමිණියා", 
                                      font=("Arial", 12, "bold"), 
                                      bg="#f39c12", 
                                      fg=self.secondary_color,
                                      bd=0,
                                      padx=20,
                                      pady=10,
                                      cursor="hand2",
                                      state=tk.DISABLED,
                                      command=lambda: self.mark_table_attendance("Late"))
        self.att_late_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.attendance_tree.bind("<<TreeviewSelect>>", self.on_attendance_select)
    
    def on_attendance_date_change(self, event):
        """Handle date change in attendance management screen"""
        selected_date = self.attendance_date_selector.get_date()
        self.current_date = selected_date
        self.populate_attendance_table()
    
    def populate_attendance_table(self):
        """Populate attendance table with current data"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        for prefect in self.prefects_data:
            # Get attendance status for current date
            status = "නොදනී"
            time_arrived = "-"
            
            if date_str in self.attendance_data[prefect["id"]]["dates"]:
                status = self.attendance_data[prefect["id"]]["dates"][date_str]["status"]
                time_arrived = self.attendance_data[prefect["id"]]["dates"][date_str]["time_arrived"] or "-"
                
                if status == "Present":
                    status = "පැමිණියා"
                elif status == "Absent":
                    status = "නොපැමිණියා"
                elif status == "Late":
                    status = "ප්‍රමාද වී පැමිණියා"
            
            # Add to treeview
            self.attendance_tree.insert("", tk.END, values=(
                prefect["id"],
                prefect["name"],
                prefect["grade"],
                prefect["class"],
                prefect["position"],
                status,
                time_arrived
            ))
    
    def filter_attendance_list(self, event=None):
        """Filter attendance table based on search and filter criteria"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        search_term = self.attendance_search_entry.get().lower()
        filter_value = self.attendance_filter_var.get()
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        for prefect in self.prefects_data:
            # Check if prefect matches search term
            if search_term and search_term not in prefect['name'].lower() and \
               search_term not in prefect['grade'].lower() and \
               search_term not in prefect['position'].lower():
                continue
            
            # Get attendance status for current date
            status = "නොදනී"
            time_arrived = "-"
            
            if date_str in self.attendance_data[prefect["id"]]["dates"]:
                status = self.attendance_data[prefect["id"]]["dates"][date_str]["status"]
                time_arrived = self.attendance_data[prefect["id"]]["dates"][date_str]["time_arrived"] or "-"
                
                if status == "Present":
                    status = "පැමිණියා"
                elif status == "Absent":
                    status = "නොපැමිණියා"
                elif status == "Late":
                    status = "ප්‍රමාද වී පැමිණියා"
            
            # Apply filter
            if filter_value != "සියලුම":
                if filter_value == "පැමිණි" and status != "පැමිණියා":
                    continue
                elif filter_value == "නොපැමිණි" and status != "නොපැමිණියා":
                    continue
                elif filter_value == "ප්‍රමාද වී පැමිණි" and status != "ප්‍රමාද වී පැමිණියා":
                    continue
            
            # Add to treeview
            self.attendance_tree.insert("", tk.END, values=(
                prefect["id"],
                prefect["name"],
                prefect["grade"],
                prefect["class"],
                prefect["position"],
                status,
                time_arrived
            ))
    
    def on_attendance_select(self, event):
        """Handle prefect selection from attendance table"""
        selection = self.attendance_tree.selection()
        if not selection:
            return
        
        # Enable attendance buttons
        self.att_present_btn.config(state=tk.NORMAL)
        self.att_absent_btn.config(state=tk.NORMAL)
        self.att_late_btn.config(state=tk.NORMAL)
    
    def mark_table_attendance(self, status):
        """Mark attendance for selected prefect from table"""
        selection = self.attendance_tree.selection()
        if not selection:
            return
        
        # Get selected prefect
        item = self.attendance_tree.item(selection[0])
        prefect_id = int(item['values'][0])
        prefect_name = item['values'][1]
        
        # Find prefect in data
        prefect = None
        for p in self.prefects_data:
            if p['id'] == prefect_id:
                prefect = p
                break
        
        if not prefect:
            return
        
        date_str = self.current_date.strftime("%Y-%m-%d")
        time_arrived = None
        
        if status in ["Present", "Late"]:
            now = datetime.datetime.now()
            time_arrived = now.strftime("%H:%M")
        
        # Update attendance data
        self.attendance_data[prefect["id"]]["dates"][date_str] = {
            "status": status,
            "time_arrived": time_arrived
        }
        
        # Show success message
        status_text = ""
        if status == "Present":
            status_text = "පැමිණියා"
        elif status == "Absent":
            status_text = "නොපැමිණියා"
        elif status == "Late":
            status_text = "ප්‍රමාද වී පැමිණියා"
        
        messagebox.showinfo("සාර්ථකයි", f"{prefect_name} ගේ පැමිණීම {status_text} ලෙස සටහන් කරන ලදී.")
        
        # Refresh table
        self.populate_attendance_table()
        self.filter_attendance_list()
    
    def show_reports(self):
        """Show reports screen"""
        # Clear current frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self.create_header()
        
        # Main content
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_content, text="වාර්තා", 
                        font=("Arial", 18, "bold"), 
                        bg=self.light_bg, 
                        fg=self.primary_color)
        title.pack(pady=(0, 20))
        
        # Report type selection
        report_type_frame = tk.Frame(main_content, bg=self.light_bg)
        report_type_frame.pack(fill=tk.X, pady=(0, 20))
        
        report_type_label = tk.Label(report_type_frame, text="වාර්තා වර්ගය:", 
                                    font=("Arial", 12), 
                                    bg=self.light_bg, 
                                    fg=self.text_color)
        report_type_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.report_type_var = tk.StringVar()
        self.report_type_var.set("daily")
        report_type_options = [("දිනපතා වාර්තාව", "daily"), 
                              ("සතිපතා සාරාංශය", "weekly"), 
                              ("මාසික සංඛ්‍යාලේඛන", "monthly")]
        
        for text, value in report_type_options:
            radio_btn = tk.Radiobutton(report_type_frame, text=text, 
                                      variable=self.report_type_var, 
                                      value=value,
                                      font=("Arial", 12), 
                                      bg=self.light_bg, 
                                      fg=self.text_color,
                                      activebackground=self.light_bg,
                                      activeforeground=self.text_color,
                                      selectcolor=self.light_bg,
                                      command=self.update_report_view)
            radio_btn.pack(side=tk.LEFT, padx=10)
        
        # Date range selection
        date_range_frame = tk.Frame(main_content, bg=self.light_bg)
        date_range_frame.pack(fill=tk.X, pady=(0, 20))
        
        from_label = tk.Label(date_range_frame, text="සිට:", 
                             font=("Arial", 12), 
                             bg=self.light_bg, 
                             fg=self.text_color)
        from_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.report_from_date = DateEntry(date_range_frame, width=12, background=self.primary_color, 
                                         foreground=self.secondary_color, borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.report_from_date.pack(side=tk.LEFT, padx=(0, 20))
        
        to_label = tk.Label(date_range_frame, text="දක්වා:", 
                           font=("Arial", 12), 
                           bg=self.light_bg, 
                           fg=self.text_color)
        to_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.report_to_date = DateEntry(date_range_frame, width=12, background=self.primary_color, 
                                       foreground=self.secondary_color, borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
        self.report_to_date.pack(side=tk.LEFT, padx=(0, 20))
        
        # Set default date range based on report type
        today = datetime.date.today()
        self.report_to_date.set_date(today)
        
        if self.report_type_var.get() == "daily":
            self.report_from_date.set_date(today)
        elif self.report_type_var.get() == "weekly":
            week_ago = today - datetime.timedelta(days=7)
            self.report_from_date.set_date(week_ago)
        elif self.report_type_var.get() == "monthly":
            month_ago = today - datetime.timedelta(days=30)
            self.report_from_date.set_date(month_ago)
        
        # Generate report button
        generate_btn = tk.Button(date_range_frame, text="වාර්තාව උත්පාදනය කරන්න", 
                               font=("Arial", 12, "bold"), 
                               bg=self.primary_color, 
                               fg=self.secondary_color,
                               bd=0,
                               padx=20,
                               pady=5,
                               cursor="hand2",
                               command=self.generate_report)
        generate_btn.pack(side=tk.LEFT, padx=20)
        
        # Export buttons
        export_frame = tk.Frame(date_range_frame, bg=self.light_bg)
        export_frame.pack(side=tk.RIGHT)
        
        export_pdf_btn = tk.Button(export_frame, text="PDF ලෙස අපනයනය කරන්න", 
                                  font=("Arial", 12), 
                                  bg=self.accent_color, 
                                  fg=self.secondary_color,
                                  bd=0,
                                  padx=10,
                                  pady=5,
                                  cursor="hand2",
                                  command=lambda: self.export_report("pdf"))
        export_pdf_btn.pack(side=tk.LEFT, padx=5)
        
        export_print_btn = tk.Button(export_frame, text="මුද්‍රණය කරන්න", 
                                    font=("Arial", 12), 
                                    bg=self.accent_color, 
                                    fg=self.secondary_color,
                                    bd=0,
                                    padx=10,
                                    pady=5,
                                    cursor="hand2",
                                    command=lambda: self.export_report("print"))
        export_print_btn.pack(side=tk.LEFT, padx=5)
        
        # Report display area
        self.report_frame = tk.Frame(main_content, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        self.report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Generate initial report
        self.generate_report()
    
    def update_report_view(self):
        """Update report view based on selected report type"""
        today = datetime.date.today()
        self.report_to_date.set_date(today)
        
        if self.report_type_var.get() == "daily":
            self.report_from_date.set_date(today)
        elif self.report_type_var.get() == "weekly":
            week_ago = today - datetime.timedelta(days=7)
            self.report_from_date.set_date(week_ago)
        elif self.report_type_var.get() == "monthly":
            month_ago = today - datetime.timedelta(days=30)
            self.report_from_date.set_date(month_ago)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate report based on selected criteria"""
        # Clear existing report
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        # Get date range
        from_date = self.report_from_date.get_date()
        to_date = self.report_to_date.get_date()
        
        # Create report title
        report_type = self.report_type_var.get()
        report_title = ""
        
        if report_type == "daily":
            report_title = f"දිනපතා පැමිණීම් වාර්තාව - {from_date.strftime('%Y-%m-%d')}"
        elif report_type == "weekly":
            report_title = f"සතිපතා පැමිණීම් සාරාංශය - {from_date.strftime('%Y-%m-%d')} සිට {to_date.strftime('%Y-%m-%d')} දක්වා"
        elif report_type == "monthly":
            report_title = f"මාසික පැමිණීම් සංඛ්‍යාලේඛන - {from_date.strftime('%Y-%m-%d')} සිට {to_date.strftime('%Y-%m-%d')} දක්වා"
        
        title_label = tk.Label(self.report_frame, text=report_title, 
                              font=("Arial", 16, "bold"), 
                              bg=self.secondary_color, 
                              fg=self.primary_color,
                              pady=10)
        title_label.pack(fill=tk.X)
        
        # Create notebook for different report sections
        notebook = ttk.Notebook(self.report_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary tab
        summary_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(summary_frame, text="සාරාංශය")
        
        # Create summary stats
        summary_stats_frame = tk.Frame(summary_frame, bg=self.secondary_color)
        summary_stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calculate summary statistics
        total_days = 0
        total_present = 0
        total_absent = 0
        total_late = 0
        
        for prefect_id in self.attendance_data:
            for date_str, data in self.attendance_data[prefect_id]["dates"].items():
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if from_date <= date <= to_date:
                    total_days += 1
                    if data["status"] == "Present":
                        total_present += 1
                    elif data["status"] == "Absent":
                        total_absent += 1
                    elif data["status"] == "Late":
                        total_late += 1
        
        # Create summary cards
        total_card = self.create_stats_card(summary_stats_frame, "මුළු දින", str(total_days), self.primary_color)
        total_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        present_card = self.create_stats_card(summary_stats_frame, "පැමිණි", str(total_present), "#2ecc71")
        present_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        absent_card = self.create_stats_card(summary_stats_frame, "නොපැමිණි", str(total_absent), "#e74c3c")
        absent_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        late_card = self.create_stats_card(summary_stats_frame, "ප්‍රමාද වී පැමිණි", str(total_late), "#f39c12")
        late_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create pie chart
        chart_frame = tk.Frame(summary_frame, bg=self.secondary_color)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Data for pie chart
        labels = ['පැමිණි', 'නොපැමිණි', 'ප්‍රමාද වී පැමිණි']
        sizes = [total_present, total_absent, total_late]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        
        # Create pie chart
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        ax.set_title('පැමිණීම් බෙදීම', fontdict={'fontsize': 12})
        
        # Add chart to frame
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Detailed tab
        detailed_frame = tk.Frame(notebook, bg=self.secondary_color)
        notebook.add(detailed_frame, text="විස්තරාත්මක")
        
        # Create treeview for detailed report
        columns = ("ID", "Name", "Grade", "Class", "Position", "Present Days", "Absent Days", "Late Days", "Attendance %")
        detailed_tree = ttk.Treeview(detailed_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        detailed_tree.heading("ID", text="ID")
        detailed_tree.heading("Name", text="නම")
        detailed_tree.heading("Grade", text="ශ්‍රේණිය")
        detailed_tree.heading("Class", text="පන්තිය")
        detailed_tree.heading("Position", text="තනතුර")
        detailed_tree.heading("Present Days", text="පැමිණි දින")
        detailed_tree.heading("Absent Days", text="නොපැමිණි දින")
        detailed_tree.heading("Late Days", text="ප්‍රමාද වූ දින")
        detailed_tree.heading("Attendance %", text="පැමිණීම් %")
        
        # Define columns
        detailed_tree.column("ID", width=40, anchor=tk.CENTER)
        detailed_tree.column("Name", width=150, anchor=tk.W)
        detailed_tree.column("Grade", width=60, anchor=tk.CENTER)
        detailed_tree.column("Class", width=60, anchor=tk.CENTER)
        detailed_tree.column("Position", width=120, anchor=tk.W)
        detailed_tree.column("Present Days", width=80, anchor=tk.CENTER)
        detailed_tree.column("Absent Days", width=80, anchor=tk.CENTER)
        detailed_tree.column("Late Days", width=80, anchor=tk.CENTER)
        detailed_tree.column("Attendance %", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(detailed_frame, orient=tk.VERTICAL, command=detailed_tree.yview)
        detailed_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        detailed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # Populate detailed tree
        for prefect in self.prefects_data:
            prefect_id = prefect["id"]
            
            # Calculate attendance stats for this prefect
            present_days = 0
            absent_days = 0
            late_days = 0
            
            for date_str, data in self.attendance_data[prefect_id]["dates"].items():
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if from_date <= date <= to_date:
                    if data["status"] == "Present":
                        present_days += 1
                    elif data["status"] == "Absent":
                        absent_days += 1
                    elif data["status"] == "Late":
                        late_days += 1
            
            # Calculate attendance percentage
            total_days = present_days + absent_days + late_days
            attendance_percentage = 0
            if total_days > 0:
                attendance_percentage = round((present_days / total_days) * 100, 1)
            
            # Add to treeview
            detailed_tree.insert("", tk.END, values=(
                prefect["id"],
                prefect["name"],
                prefect["grade"],
                prefect["class"],
                prefect["position"],
                present_days,
                absent_days,
                late_days,
                f"{attendance_percentage}%"
            ))
    
    def show_report(self, report_type):
        """Show specific report type"""
        # Navigate to reports screen
        self.show_reports()
        
        # Set report type
        self.report_type_var.set(report_type)
        
        # Update date range
        today = datetime.date.today()
        self.report_to_date.set_date(today)
        
        if report_type == "daily":
            self.report_from_date.set_date(today)
        elif report_type == "weekly":
            week_ago = today - datetime.timedelta(days=7)
            self.report_from_date.set_date(week_ago)
        elif report_type == "monthly":
            month_ago = today - datetime.timedelta(days=30)
            self.report_from_date.set_date(month_ago)
        
        # Generate report
        self.generate_report()
    
    def export_report(self, export_type):
        """Export report to PDF or print"""
        if export_type == "pdf":
            messagebox.showinfo("PDF අපනයනය", "වාර්තාව PDF ලෙස සුරකින ලදී.")
        elif export_type == "print":
            messagebox.showinfo("මුද්‍රණය", "වාර්තාව මුද්‍රණය සඳහා සූදානම් කරන ලදී.")
    
    def show_profiles(self):
        """Show profiles management screen"""
        # Clear current frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self.create_header()
        
        # Main content
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_content, text="ශිශ්‍යනායක පැතිකඩ", 
                        font=("Arial", 18, "bold"), 
                        bg=self.light_bg, 
                        fg=self.primary_color)
        title.pack(pady=(0, 20))
        
        # Profiles list and details frame
        profiles_container = tk.Frame(main_content, bg=self.light_bg)
        profiles_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Profiles list
        profiles_list_frame = tk.Frame(profiles_container, bg=self.secondary_color, relief=tk.RAISED, bd=1, width=400)
        profiles_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        profiles_list_frame.pack_propagate(False)
        
        # Search bar
        search_frame = tk.Frame(profiles_list_frame, bg=self.secondary_color)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        search_label = tk.Label(search_frame, text="සොයන්න:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color)
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.profiles_search_entry = tk.Entry(search_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.profiles_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profiles_search_entry.bind("<KeyRelease>", self.filter_profiles_list)
        
        # Profiles list
        list_scroll = tk.Scrollbar(profiles_list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.profiles_listbox = tk.Listbox(profiles_list_frame, font=("Arial", 10), bd=2, relief=tk.GROOVE, 
                                          yscrollcommand=list_scroll.set, height=15)
        self.profiles_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        list_scroll.config(command=self.profiles_listbox.yview)
        
        self.profiles_listbox.bind("<<ListboxSelect>>", self.on_profile_select)
        
        # Add new profile button
        add_profile_btn = tk.Button(profiles_list_frame, text="නව ශිශ්‍යනායකයෙකු එකතු කරන්න", 
                                   font=("Arial", 12), 
                                   bg=self.primary_color, 
                                   fg=self.secondary_color,
                                   bd=0,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2",
                                   command=self.add_new_profile)
        add_profile_btn.pack(pady=(0, 10))
        
        # Right side - Profile details
        profile_details_frame = tk.Frame(profiles_container, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        profile_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Profile details title
        details_title = tk.Label(profile_details_frame, text="ශිශ්‍යනායක විස්තර", 
                                font=("Arial", 16, "bold"), 
                                bg=self.secondary_color, 
                                fg=self.primary_color,
                                pady=10)
        details_title.pack(fill=tk.X)
        
        # Profile details container
        self.profile_details_container = tk.Frame(profile_details_frame, bg=self.secondary_color)
        self.profile_details_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # No profile selected message
        self.no_profile_label = tk.Label(self.profile_details_container, text="ශිශ්‍යනායකයෙකු තෝරන්න", 
                                        font=("Arial", 14), 
                                        bg=self.secondary_color, 
                                        fg=self.text_color)
        self.no_profile_label.pack(pady=50)
        
        # Populate profiles list
        self.populate_profiles_list()
    
    def populate_profiles_list(self):
        """Populate profiles list with prefect data"""
        self.profiles_listbox.delete(0, tk.END)
        
        for prefect in self.prefects_data:
            # Format list item
            list_item = f"{prefect['name']} - {prefect['grade']} {prefect['class']} - {prefect['position']}"
            
            # Add to listbox
            self.profiles_listbox.insert(tk.END, list_item)
    
    def filter_profiles_list(self, event=None):
        """Filter profiles list based on search term"""
        search_term = self.profiles_search_entry.get().lower()
        
        self.profiles_listbox.delete(0, tk.END)
        
        for prefect in self.prefects_data:
            # Check if prefect matches search term
            if search_term and search_term not in prefect['name'].lower() and \
               search_term not in prefect['grade'].lower() and \
               search_term not in prefect['position'].lower():
                continue
            
            # Format list item
            list_item = f"{prefect['name']} - {prefect['grade']} {prefect['class']} - {prefect['position']}"
            
            # Add to listbox
            self.profiles_listbox.insert(tk.END, list_item)
    
    def on_profile_select(self, event):
        """Handle profile selection from list"""
        selection = self.profiles_listbox.curselection()
        if not selection:
            return
        
        # Get selected prefect
        index = selection[0]
        prefect_name = self.profiles_listbox.get(index).split(" - ")[0]
        
        # Find prefect in data
        for prefect in self.prefects_data:
            if prefect['name'] == prefect_name:
                self.selected_profile = prefect
                break
        
        # Show profile details
        self.show_profile_details()
    
    def show_profile_details(self):
        """Show details of selected profile"""
        # Clear existing details
        for widget in self.profile_details_container.winfo_children():
            widget.destroy()
        
        if not self.selected_profile:
            # No profile selected message
            self.no_profile_label = tk.Label(self.profile_details_container, text="ශිශ්‍යනායකයෙකු තෝරන්න", 
                                            font=("Arial", 14), 
                                            bg=self.secondary_color, 
                                            fg=self.text_color)
            self.no_profile_label.pack(pady=50)
            return
        
        # Profile photo placeholder
        photo_frame = tk.Frame(self.profile_details_container, bg=self.secondary_color)
        photo_frame.pack(fill=tk.X, pady=10)
        
        photo_label = tk.Label(photo_frame, text="ඡායාරූපය", 
                              font=("Arial", 10), 
                              bg=self.secondary_color, 
                              fg=self.text_color)
        photo_label.pack()
        
        # Create a placeholder image
        img = Image.new('RGB', (150, 150), color=self.light_bg)
        d = ImageDraw.Draw(img)
        d.text((75, 75), "ඡායාරූපය", fill=self.text_color)
        
        photo = ImageTk.PhotoImage(img)
        photo_display = tk.Label(photo_frame, image=photo, bg=self.secondary_color)
        photo_display.image = photo  # Keep a reference
        photo_display.pack(pady=5)
        
        # Profile details form
        details_frame = tk.Frame(self.profile_details_container, bg=self.secondary_color)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        name_frame = tk.Frame(details_frame, bg=self.secondary_color)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = tk.Label(name_frame, text="නම:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        name_label.pack(side=tk.LEFT)
        
        self.profile_name_entry = tk.Entry(name_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.profile_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profile_name_entry.insert(0, self.selected_profile["name"])
        
        # Grade
        grade_frame = tk.Frame(details_frame, bg=self.secondary_color)
        grade_frame.pack(fill=tk.X, pady=5)
        
        grade_label = tk.Label(grade_frame, text="ශ්‍රේණිය:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        grade_label.pack(side=tk.LEFT)
        
        self.profile_grade_entry = tk.Entry(grade_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, width=5)
        self.profile_grade_entry.pack(side=tk.LEFT)
        self.profile_grade_entry.insert(0, self.selected_profile["grade"])
        
        # Class
        class_label = tk.Label(grade_frame, text="පන්තිය:", 
                              font=("Arial", 12), 
                              bg=self.secondary_color, 
                              fg=self.text_color,
                              width=10,
                              anchor=tk.W)
        class_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.profile_class_entry = tk.Entry(grade_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, width=5)
        self.profile_class_entry.pack(side=tk.LEFT)
        self.profile_class_entry.insert(0, self.selected_profile["class"])
        
        # Position
        position_frame = tk.Frame(details_frame, bg=self.secondary_color)
        position_frame.pack(fill=tk.X, pady=5)
        
        position_label = tk.Label(position_frame, text="තනතුර:", 
                                font=("Arial", 12), 
                                bg=self.secondary_color, 
                                fg=self.text_color,
                                width=15,
                                anchor=tk.W)
        position_label.pack(side=tk.LEFT)
        
        self.profile_position_var = tk.StringVar()
        position_options = ["Head Prefect", "Deputy Head Prefect", "Senior Prefect", "Junior Prefect"]
        position_dropdown = ttk.Combobox(position_frame, textvariable=self.profile_position_var, 
                                       values=position_options, state="readonly", width=20)
        position_dropdown.pack(side=tk.LEFT)
        position_dropdown.set(self.selected_profile["position"])
        
        # Contact
        contact_frame = tk.Frame(details_frame, bg=self.secondary_color)
        contact_frame.pack(fill=tk.X, pady=5)
        
        contact_label = tk.Label(contact_frame, text="�බාකාර ඇමතුම:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color,
                               width=15,
                               anchor=tk.W)
        contact_label.pack(side=tk.LEFT)
        
        self.profile_contact_entry = tk.Entry(contact_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.profile_contact_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profile_contact_entry.insert(0, self.selected_profile["contact"])
        
        # Email
        email_frame = tk.Frame(details_frame, bg=self.secondary_color)
        email_frame.pack(fill=tk.X, pady=5)
        
        email_label = tk.Label(email_frame, text="විද්‍යුත් තැපෑල:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        email_label.pack(side=tk.LEFT)
        
        self.profile_email_entry = tk.Entry(email_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.profile_email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profile_email_entry.insert(0, self.selected_profile["email"])
        
        # Emergency contact
        emergency_frame = tk.Frame(details_frame, bg=self.secondary_color)
        emergency_frame.pack(fill=tk.X, pady=5)
        
        emergency_label = tk.Label(emergency_frame, text="හදිසි ඇමතුම:", 
                                  font=("Arial", 12), 
                                  bg=self.secondary_color, 
                                  fg=self.text_color,
                                  width=15,
                                  anchor=tk.W)
        emergency_label.pack(side=tk.LEFT)
        
        self.profile_emergency_entry = tk.Entry(emergency_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.profile_emergency_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profile_emergency_entry.insert(0, self.selected_profile["emergency_contact"])
        
        # Attendance statistics
        stats_frame = tk.LabelFrame(details_frame, text="පැමිණීම් සංඛ්‍යාලේඛන", 
                                   font=("Arial", 12, "bold"), 
                                   bg=self.secondary_color, 
                                   fg=self.primary_color)
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_inner = tk.Frame(stats_frame, bg=self.secondary_color)
        stats_inner.pack(fill=tk.X, padx=10, pady=10)
        
        prefect_id = self.selected_profile["id"]
        prefect_stats = self.attendance_data[prefect_id]
        
        total_days = prefect_stats["total_days"]
        present_days = prefect_stats["present_days"]
        absent_days = prefect_stats["absent_days"]
        late_days = prefect_stats["late_days"]
        
        # Calculate attendance percentage
        attendance_percentage = 0
        if total_days > 0:
            attendance_percentage = round((present_days / total_days) * 100, 1)
        
        # Create stats labels
        total_label = tk.Label(stats_inner, text=f"මුළු දින: {total_days}", 
                              font=("Arial", 11), 
                              bg=self.secondary_color, 
                              fg=self.text_color,
                              anchor=tk.W)
        total_label.pack(fill=tk.X, pady=2)
        
        present_label = tk.Label(stats_inner, text=f"පැමිණි දින: {present_days}", 
                                font=("Arial", 11), 
                                bg=self.secondary_color, 
                                fg="#2ecc71",
                                anchor=tk.W)
        present_label.pack(fill=tk.X, pady=2)
        
        absent_label = tk.Label(stats_inner, text=f"නොපැමිණි දින: {absent_days}", 
                               font=("Arial", 11), 
                               bg=self.secondary_color, 
                               fg="#e74c3c",
                               anchor=tk.W)
        absent_label.pack(fill=tk.X, pady=2)
        
        late_label = tk.Label(stats_inner, text=f"ප්‍රමාද වූ දින: {late_days}", 
                             font=("Arial", 11), 
                             bg=self.secondary_color, 
                             fg="#f39c12",
                             anchor=tk.W)
        late_label.pack(fill=tk.X, pady=2)
        
        percentage_label = tk.Label(stats_inner, text=f"පැමිණීම් %: {attendance_percentage}%", 
                                   font=("Arial", 11, "bold"), 
                                   bg=self.secondary_color, 
                                   fg=self.primary_color,
                                   anchor=tk.W)
        percentage_label.pack(fill=tk.X, pady=2)
        
        # Action buttons
        action_frame = tk.Frame(self.profile_details_container, bg=self.secondary_color)
        action_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(action_frame, text="සුරකින්න", 
                            font=("Arial", 12), 
                            bg=self.primary_color, 
                            fg=self.secondary_color,
                            bd=0,
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=self.save_profile)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(action_frame, text="මකන්න", 
                              font=("Arial", 12), 
                              bg="#e74c3c", 
                              fg=self.secondary_color,
                              bd=0,
                              padx=20,
                              pady=5,
                              cursor="hand2",
                              command=self.delete_profile)
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    def save_profile(self):
        """Save profile changes"""
        if not self.selected_profile:
            return
        
        # Get values from form
        name = self.profile_name_entry.get()
        grade = self.profile_grade_entry.get()
        class_name = self.profile_class_entry.get()
        position = self.profile_position_var.get()
        contact = self.profile_contact_entry.get()
        email = self.profile_email_entry.get()
        emergency_contact = self.profile_emergency_entry.get()
        
        # Update prefect data
        self.selected_profile["name"] = name
        self.selected_profile["grade"] = grade
        self.selected_profile["class"] = class_name
        self.selected_profile["position"] = position
        self.selected_profile["contact"] = contact
        self.selected_profile["email"] = email
        self.selected_profile["emergency_contact"] = emergency_contact
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", f"{name} ගේ පැතිකඩ යාවත්කාලීන කරන ලදී.")
        
        # Refresh profiles list
        self.populate_profiles_list()
    
    def delete_profile(self):
        """Delete selected profile"""
        if not self.selected_profile:
            return
        
        confirm = messagebox.askyesno("�ැරෑවින් තහවුරු කරන්න", 
                                      f"{self.selected_profile['name']} මකා දැමීමට අවශ්‍යද?")
        
        if not confirm:
            return
        
        # Remove from prefects data
        self.prefects_data.remove(self.selected_profile)
        
        # Remove from attendance data
        if self.selected_profile["id"] in self.attendance_data:
            del self.attendance_data[self.selected_profile["id"]]
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", f"{self.selected_profile['name']} මකා දමන ලදී.")
        
        # Clear selection
        self.selected_profile = None
        
        # Refresh profiles list
        self.populate_profiles_list()
        
        # Clear profile details
        for widget in self.profile_details_container.winfo_children():
            widget.destroy()
        
        # No profile selected message
        self.no_profile_label = tk.Label(self.profile_details_container, text="ශිශ්‍යනායකයෙකු තෝරන්න", 
                                        font=("Arial", 14), 
                                        bg=self.secondary_color, 
                                        fg=self.text_color)
        self.no_profile_label.pack(pady=50)
    
    def add_new_profile(self):
        """Add a new prefect profile"""
        # Create dialog for new profile
        dialog = tk.Toplevel(self.root)
        dialog.title("නව ශිශ්‍යනායකයෙකු එකතු කරන්න")
        dialog.geometry("500x500")
        dialog.minsize(400, 400)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="නව ශිශ්‍යනායකයෙකු එකතු කරන්න", 
                              font=("Arial", 16, "bold"), 
                              bg=self.secondary_color, 
                              fg=self.primary_color)
        title_label.pack(pady=(0, 20))
        
        # Form fields
        # Name
        name_frame = tk.Frame(main_frame, bg=self.secondary_color)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = tk.Label(name_frame, text="නම:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        name_label.pack(side=tk.LEFT)
        
        new_name_entry = tk.Entry(name_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        new_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Grade
        grade_frame = tk.Frame(main_frame, bg=self.secondary_color)
        grade_frame.pack(fill=tk.X, pady=5)
        
        grade_label = tk.Label(grade_frame, text="ශ්‍රේණිය:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        grade_label.pack(side=tk.LEFT)
        
        new_grade_entry = tk.Entry(grade_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, width=5)
        new_grade_entry.pack(side=tk.LEFT)
        
        # Class
        class_label = tk.Label(grade_frame, text="පන්තිය:", 
                              font=("Arial", 12), 
                              bg=self.secondary_color, 
                              fg=self.text_color,
                              width=10,
                              anchor=tk.W)
        class_label.pack(side=tk.LEFT, padx=(10, 0))
        
        new_class_entry = tk.Entry(grade_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, width=5)
        new_class_entry.pack(side=tk.LEFT)
        
        # Position
        position_frame = tk.Frame(main_frame, bg=self.secondary_color)
        position_frame.pack(fill=tk.X, pady=5)
        
        position_label = tk.Label(position_frame, text="තනතුර:", 
                                font=("Arial", 12), 
                                bg=self.secondary_color, 
                                fg=self.text_color,
                                width=15,
                                anchor=tk.W)
        position_label.pack(side=tk.LEFT)
        
        new_position_var = tk.StringVar()
        position_options = ["Head Prefect", "Deputy Head Prefect", "Senior Prefect", "Junior Prefect"]
        position_dropdown = ttk.Combobox(position_frame, textvariable=new_position_var, 
                                       values=position_options, state="readonly", width=20)
        position_dropdown.pack(side=tk.LEFT)
        
        # Contact
        contact_frame = tk.Frame(main_frame, bg=self.secondary_color)
        contact_frame.pack(fill=tk.X, pady=5)
        
        contact_label = tk.Label(contact_frame, text="භාකාර ඇමතුම:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color,
                               width=15,
                               anchor=tk.W)
        contact_label.pack(side=tk.LEFT)
        
        new_contact_entry = tk.Entry(contact_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        new_contact_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Email
        email_frame = tk.Frame(main_frame, bg=self.secondary_color)
        email_frame.pack(fill=tk.X, pady=5)
        
        email_label = tk.Label(email_frame, text="විද්‍යුත් තැපෑල:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=15,
                             anchor=tk.W)
        email_label.pack(side=tk.LEFT)
        
        new_email_entry = tk.Entry(email_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        new_email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Emergency contact
        emergency_frame = tk.Frame(main_frame, bg=self.secondary_color)
        emergency_frame.pack(fill=tk.X, pady=5)
        
        emergency_label = tk.Label(emergency_frame, text="හදිසි ඇමතුම:", 
                                  font=("Arial", 12), 
                                  bg=self.secondary_color, 
                                  fg=self.text_color,
                                  width=15,
                                  anchor=tk.W)
        emergency_label.pack(side=tk.LEFT)
        
        new_emergency_entry = tk.Entry(emergency_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        new_emergency_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_btn = tk.Button(button_frame, text="සුරකින්න", 
                            font=("Arial", 12), 
                            bg=self.primary_color, 
                            fg=self.secondary_color,
                            bd=0,
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=lambda: self.save_new_profile(
                                dialog, new_name_entry, new_grade_entry, new_class_entry,
                                new_position_var, new_contact_entry, new_email_entry, new_emergency_entry
                            ))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="අවලංගු කරන්න", 
                              font=("Arial", 12), 
                              bg="#e74c3c", 
                              fg=self.secondary_color,
                              bd=0,
                              padx=20,
                              pady=5,
                              cursor="hand2",
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save_new_profile(self, dialog, name_entry, grade_entry, class_entry, 
                       position_var, contact_entry, email_entry, emergency_entry):
        """Save new profile data"""
        # Get values from form
        name = name_entry.get()
        grade = grade_entry.get()
        class_name = class_entry.get()
        position = position_var.get()
        contact = contact_entry.get()
        email = email_entry.get()
        emergency_contact = emergency_entry.get()
        
        # Validate required fields
        if not name or not grade or not class_name or not position:
            messagebox.showerror("දෝෂයකි", "කරුණාකර සියලුම අවශ්‍ය තොරතුරු පුරවන්න.")
            return
        
        # Generate new ID
        new_id = max([p["id"] for p in self.prefects_data]) + 1 if self.prefects_data else 1
        
        # Create new prefect
        new_prefect = {
            "id": new_id,
            "name": name,
            "grade": grade,
            "class": class_name,
            "position": position,
            "contact": contact,
            "email": email,
            "emergency_contact": emergency_contact
        }
        
        # Add to prefects data
        self.prefects_data.append(new_prefect)
        
        # Initialize attendance data
        self.attendance_data[new_id] = {
            "dates": {},
            "total_days": 0,
            "present_days": 0,
            "absent_days": 0,
            "late_days": 0
        }
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", f"{name} නව ශිශ්‍යනායකයෙකු ලෙස එකතු කරන ලදී.")
        
        # Close dialog
        dialog.destroy()
        
        # Refresh profiles list
        self.populate_profiles_list()
    
    def show_notifications(self):
        """Show notifications screen"""
        # Clear current frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self.create_header()
        
        # Main content
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_content, text="දැනුම්දීම්", 
                        font=("Arial", 18, "bold"), 
                        bg=self.light_bg, 
                        fg=self.primary_color)
        title.pack(pady=(0, 20))
        
        # Notifications list
        notifications_frame = tk.Frame(main_content, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        notifications_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notifications header
        header_frame = tk.Frame(notifications_frame, bg=self.primary_color, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text="දැනුම්දීම්", 
                               font=("Arial", 14, "bold"), 
                               bg=self.primary_color, 
                               fg=self.secondary_color,
                               pady=10)
        header_label.pack(side=tk.LEFT, padx=20)
        
        mark_all_read_btn = tk.Button(header_frame, text="සියල්ල කියවූ ලෙස සලකුණු කරන්න", 
                                    font=("Arial", 10), 
                                    bg=self.secondary_color, 
                                    fg=self.primary_color,
                                    bd=0,
                                    padx=10,
                                    pady=5,
                                    cursor="hand2",
                                    command=self.mark_all_notifications_read)
        mark_all_read_btn.pack(side=tk.RIGHT, padx=20)
        
        # Notifications list with scrollbar
        list_scroll = tk.Scrollbar(notifications_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notifications_listbox = tk.Listbox(notifications_frame, font=("Arial", 12), bd=0, relief=tk.FLAT, 
                                              yscrollcommand=list_scroll.set, height=15)
        self.notifications_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.notifications_listbox.yview)
        
        self.notifications_listbox.bind("<<ListboxSelect>>", self.on_notification_select)
        
        # Populate notifications list
        self.populate_notifications_list()
        
        # Notification details
        details_frame = tk.Frame(main_content, bg=self.secondary_color, relief=tk.RAISED, bd=1, height=200)
        details_frame.pack(fill=tk.X, pady=(20, 0))
        details_frame.pack_propagate(False)
        
        details_title = tk.Label(details_frame, text="දැනුම්දීම් විස්තර", 
                                font=("Arial", 14, "bold"), 
                                bg=self.secondary_color, 
                                fg=self.primary_color,
                                pady=10)
        details_title.pack(fill=tk.X)
        
        self.notification_details = tk.Text(details_frame, font=("Arial", 12), bd=0, relief=tk.FLAT, 
                                          height=8, wrap=tk.WORD)
        self.notification_details.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        self.notification_details.config(state=tk.DISABLED)
    
    def populate_notifications_list(self):
        """Populate notifications list"""
        self.notifications_listbox.delete(0, tk.END)
        
        for notification in self.notifications:
            # Format list item
            if notification["read"]:
                list_item = f"{notification['time']} - {notification['message']}"
            else:
                list_item = f"● {notification['time']} - {notification['message']}"
            
            # Add to listbox
            self.notifications_listbox.insert(tk.END, list_item)
            
            # Set item color based on read status
            if notification["read"]:
                self.notifications_listbox.itemconfig(tk.END, {'fg': self.text_color})
            else:
                self.notifications_listbox.itemconfig(tk.END, {'fg': self.primary_color, 'font': ("Arial", 12, "bold")})
    
    def on_notification_select(self, event):
        """Handle notification selection"""
        selection = self.notifications_listbox.curselection()
        if not selection:
            return
        
        # Get selected notification
        index = selection[0]
        notification = self.notifications[index]
        
        # Mark as read
        notification["read"] = True
        
        # Update list
        self.populate_notifications_list()
        
        # Show details
        self.notification_details.config(state=tk.NORMAL)
        self.notification_details.delete(1.0, tk.END)
        self.notification_details.insert(tk.END, f"දැනුම්දීම: {notification['message']}\n\n")
        self.notification_details.insert(tk.END, f"කාලය: {notification['time']}\n\n")
        self.notification_details.insert(tk.END, "මෙය පද්ධතියෙන් නිකුත් කරන ලද ස්වයංක්‍රීය දැනුම්දීමකි.")
        self.notification_details.config(state=tk.DISABLED)
    
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification["read"] = True
        
        # Update list
        self.populate_notifications_list()
        
        # Clear details
        self.notification_details.config(state=tk.NORMAL)
        self.notification_details.delete(1.0, tk.END)
        self.notification_details.config(state=tk.DISABLED)
    
    def show_settings(self):
        """Show settings screen"""
        # Clear current frame
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self.create_header()
        
        # Main content
        main_content = tk.Frame(self.dashboard_frame, bg=self.light_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_content, text="සැකසුම්", 
                        font=("Arial", 18, "bold"), 
                        bg=self.light_bg, 
                        fg=self.primary_color)
        title.pack(pady=(0, 20))
        
        # Settings container
        settings_container = tk.Frame(main_content, bg=self.secondary_color, relief=tk.RAISED, bd=1)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Theme settings
        theme_frame = tk.LabelFrame(settings_container, text="තේමා සැකසුම්", 
                                   font=("Arial", 14, "bold"), 
                                   bg=self.secondary_color, 
                                   fg=self.primary_color)
        theme_frame.pack(fill=tk.X, padx=20, pady=20)
        
        theme_inner = tk.Frame(theme_frame, bg=self.secondary_color)
        theme_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme toggle
        theme_label = tk.Label(theme_inner, text="අඳුරු තේමාව:", 
                             font=("Arial", 12), 
                             bg=self.secondary_color, 
                             fg=self.text_color,
                             width=20,
                             anchor=tk.W)
        theme_label.pack(side=tk.LEFT)
        
        self.theme_var = tk.IntVar(value=0)
        theme_check = tk.Checkbutton(theme_inner, text="සක්‍රීය කරන්න", 
                                    variable=self.theme_var, 
                                    font=("Arial", 12), 
                                    bg=self.secondary_color, 
                                    fg=self.text_color,
                                    selectcolor=self.secondary_color,
                                    activebackground=self.secondary_color,
                                    activeforeground=self.text_color,
                                    command=self.toggle_theme)
        theme_check.pack(side=tk.LEFT)
        
        # User settings
        user_frame = tk.LabelFrame(settings_container, text="පරිශීලක සැකසුම්", 
                                  font=("Arial", 14, "bold"), 
                                  bg=self.secondary_color, 
                                  fg=self.primary_color)
        user_frame.pack(fill=tk.X, padx=20, pady=20)
        
        user_inner = tk.Frame(user_frame, bg=self.secondary_color)
        user_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Change password
        password_label = tk.Label(user_inner, text="මුරපදය වෙනස් කරන්න:", 
                                font=("Arial", 12), 
                                bg=self.secondary_color, 
                                fg=self.text_color,
                                width=20,
                                anchor=tk.W)
        password_label.pack(side=tk.LEFT)
        
        change_password_btn = tk.Button(user_inner, text="මුරපදය වෙනස් කරන්න", 
                                       font=("Arial", 12), 
                                       bg=self.primary_color, 
                                       fg=self.secondary_color,
                                       bd=0,
                                       padx=10,
                                       pady=5,
                                       cursor="hand2",
                                       command=self.change_password)
        change_password_btn.pack(side=tk.LEFT)
        
        # Data management
        data_frame = tk.LabelFrame(settings_container, text="දත්ත කළමනාකරණය", 
                                 font=("Arial", 14, "bold"), 
                                 bg=self.secondary_color, 
                                 fg=self.primary_color)
        data_frame.pack(fill=tk.X, padx=20, pady=20)
        
        data_inner = tk.Frame(data_frame, bg=self.secondary_color)
        data_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Backup data
        backup_label = tk.Label(data_inner, text="දත්ත උපස්ථ කරන්න:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color,
                               width=20,
                               anchor=tk.W)
        backup_label.pack(side=tk.LEFT)
        
        backup_btn = tk.Button(data_inner, text="උපස්ථ කරන්න", 
                               font=("Arial", 12), 
                               bg=self.primary_color, 
                               fg=self.secondary_color,
                               bd=0,
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.backup_data)
        backup_btn.pack(side=tk.LEFT, padx=5)
        
        # Restore data
        restore_btn = tk.Button(data_inner, text="ප්‍රතිසාධනය කරන්න", 
                               font=("Arial", 12), 
                               bg=self.primary_color, 
                               fg=self.secondary_color,
                               bd=0,
                               padx=10,
                               pady=5,
                               cursor="hand2",
                               command=self.restore_data)
        restore_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear data
        clear_btn = tk.Button(data_inner, text="දත්ත මකන්න", 
                             font=("Arial", 12), 
                             bg="#e74c3c", 
                             fg=self.secondary_color,
                             bd=0,
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=self.clear_data)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # About
        about_frame = tk.LabelFrame(settings_container, text="පද්ධතිය පිළිබඳව", 
                                   font=("Arial", 14, "bold"), 
                                   bg=self.secondary_color, 
                                   fg=self.primary_color)
        about_frame.pack(fill=tk.X, padx=20, pady=20)
        
        about_inner = tk.Frame(about_frame, bg=self.secondary_color)
        about_inner.pack(fill=tk.X, padx=10, pady=10)
        
        about_text = tk.Text(about_inner, font=("Arial", 12), bd=0, relief=tk.FLAT, 
                            height=6, wrap=tk.WORD)
        about_text.pack(fill=tk.X)
        about_text.insert(tk.END, "M.S.C BIBILE ශිශ්‍යනායක පැමිණීම් පද්ධතිය\n\n")
        about_text.insert(tk.END, "අනුවාදය: 1.0.0\n")
        about_text.insert(tk.END, "සංවර්ධනය: මා.සි.සී. බිබිලේ විද්‍යාලය\n")
        about_text.insert(tk.END, "කතුහිමි අයිතිය: © 2023 සියලු හිමිකම් ඇවිරිණි.")
        about_text.config(state=tk.DISABLED)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = self.theme_var.get() == 1
        
        if self.dark_mode:
            # Switch to dark theme
            self.primary_color = "#0a192f"  # Dark blue
            self.secondary_color = "#172a45"  # Medium blue
            self.accent_color = "#64ffda"  # Teal
            self.text_color = "#ccd6f6"  # Light gray
            self.light_bg = "#0d1117"  # Very dark blue
        else:
            # Switch to light theme
            self.primary_color = "#1a4d8f"  # Dark blue
            self.secondary_color = "#ffffff"  # White
            self.accent_color = "#4a90e2"  # Light blue
            self.text_color = "#333333"  # Dark gray
            self.light_bg = "#f5f9ff"  # Very light blue
        
        # Refresh current screen
        current_screen = None
        
        # Determine current screen
        if hasattr(self, 'dashboard_frame') and self.dashboard_frame.winfo_exists():
            if hasattr(self, 'report_frame') and self.report_frame.winfo_exists():
                current_screen = "reports"
            elif hasattr(self, 'profile_details_container') and self.profile_details_container.winfo_exists():
                current_screen = "profiles"
            elif hasattr(self, 'notifications_listbox') and self.notifications_listbox.winfo_exists():
                current_screen = "notifications"
            elif hasattr(self, 'theme_var') and self.theme_var.winfo_exists():
                current_screen = "settings"
            elif hasattr(self, 'attendance_tree') and self.attendance_tree.winfo_exists():
                current_screen = "attendance"
            else:
                current_screen = "dashboard"
        
        # Recreate current screen with new theme
        if current_screen == "dashboard":
            self.show_dashboard()
        elif current_screen == "attendance":
            self.show_attendance_management()
        elif current_screen == "reports":
            self.show_reports()
        elif current_screen == "profiles":
            self.show_profiles()
        elif current_screen == "notifications":
            self.show_notifications()
        elif current_screen == "settings":
            self.show_settings()
    
    def change_password(self):
        """Show change password dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("මුරපදය වෙනස් කරන්න")
        dialog.geometry("400x300")
        dialog.minsize(350, 250)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.secondary_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="මුරපදය වෙනස් කරන්න", 
                              font=("Arial", 16, "bold"), 
                              bg=self.secondary_color, 
                              fg=self.primary_color)
        title_label.pack(pady=(0, 20))
        
        # Current password
        current_frame = tk.Frame(main_frame, bg=self.secondary_color)
        current_frame.pack(fill=tk.X, pady=5)
        
        current_label = tk.Label(current_frame, text="වත්මන් මුරපදය:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color,
                               width=15,
                               anchor=tk.W)
        current_label.pack(side=tk.LEFT)
        
        current_entry = tk.Entry(current_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, show="*")
        current_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        current_entry.insert(0, "password")  # Default password for demo
        
        # New password
        new_frame = tk.Frame(main_frame, bg=self.secondary_color)
        new_frame.pack(fill=tk.X, pady=5)
        
        new_label = tk.Label(new_frame, text="නව මුරපදය:", 
                            font=("Arial", 12), 
                            bg=self.secondary_color, 
                            fg=self.text_color,
                            width=15,
                            anchor=tk.W)
        new_label.pack(side=tk.LEFT)
        
        new_entry = tk.Entry(new_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, show="*")
        new_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Confirm password
        confirm_frame = tk.Frame(main_frame, bg=self.secondary_color)
        confirm_frame.pack(fill=tk.X, pady=5)
        
        confirm_label = tk.Label(confirm_frame, text="නව මුරපදය තහවුරු කරන්න:", 
                               font=("Arial", 12), 
                               bg=self.secondary_color, 
                               fg=self.text_color,
                               width=15,
                               anchor=tk.W)
        confirm_label.pack(side=tk.LEFT)
        
        confirm_entry = tk.Entry(confirm_frame, font=("Arial", 12), bd=2, relief=tk.GROOVE, show="*")
        confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.secondary_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_btn = tk.Button(button_frame, text="සුරකින්න", 
                            font=("Arial", 12), 
                            bg=self.primary_color, 
                            fg=self.secondary_color,
                            bd=0,
                            padx=20,
                            pady=5,
                            cursor="hand2",
                            command=lambda: self.save_new_password(
                                dialog, current_entry, new_entry, confirm_entry
                            ))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="අවලංගු කරන්න", 
                              font=("Arial", 12), 
                              bg="#e74c3c", 
                              fg=self.secondary_color,
                              bd=0,
                              padx=20,
                              pady=5,
                              cursor="hand2",
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save_new_password(self, dialog, current_entry, new_entry, confirm_entry):
        """Save new password"""
        current_password = current_entry.get()
        new_password = new_entry.get()
        confirm_password = confirm_entry.get()
        
        # Validate current password
        if current_password != "password":
            messagebox.showerror("දෝෂයකි", "වත්මන් මුරපදය වැරදිය.")
            return
        
        # Validate new password
        if not new_password:
            messagebox.showerror("දෝෂයකි", "කරුණාකර නව මුරපදයක් ඇතුළත් කරන්න.")
            return
        
        # Validate password confirmation
        if new_password != confirm_password:
            messagebox.showerror("දෝෂයකි", "මුරපද ගැලපෙන්නේ නැත.")
            return
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", "මුරපදය සාර්ථකව වෙනස් කරන ලදී.")
        
        # Close dialog
        dialog.destroy()
    
    def backup_data(self):
        """Backup system data"""
        # Create backup data structure
        backup_data = {
            "prefects": self.prefects_data,
            "attendance": self.attendance_data,
            "notifications": self.notifications,
            "backup_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Convert to JSON
        backup_json = json.dumps(backup_data, indent=2)
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", "දත්ත සාර්ථකව උපස්ථ කරන ලදී.")
    
    def restore_data(self):
        """Restore system data from backup"""
        # Show file dialog
        messagebox.showinfo("දත්ත ප්‍රතිසාධනය", "මෙම විශේෂාංගය සංවර්ධනය වෙමින් පවතී.")
    
    def clear_data(self):
        """Clear all system data"""
        confirm = messagebox.askyesno("තහවුරු කරන්න", "ඔබට විශ්වාසද? සියලුම දත්ත මකා දමනු ඇත.")
        
        if not confirm:
            return
        
        # Confirm again
        confirm = messagebox.askyesno("අවසාන තහවුරු කිරීම", "මෙම ක්‍රියාව අහෝසි කළ නොහැකිය. ඔබට විශ්වාසද?")
        
        if not confirm:
            return
        
        # Clear data
        self.prefects_data = []
        self.attendance_data = {}
        self.notifications = []
        
        # Reinitialize with sample data
        self.initialize_data()
        
        # Show success message
        messagebox.showinfo("සාර්ථකයි", "සියලුම දත්ත මකා දමන ලදී. නියැදි දත්ත නැවත උත්පාදනය කරන ලදී.")
        
        # Refresh current screen
        self.show_dashboard()
    
    def logout(self):
        """Logout from the system"""
        confirm = messagebox.askyesno("නික්මෙන්න", "පද්ධතියෙන් නික්මෙන්නද?")
        
        if confirm:
            # Clear current frame
            for widget in self.dashboard_frame.winfo_children():
                widget.destroy()
            
            # Reset user
            self.current_user = None
            
            # Show login screen
            self.show_login_screen()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PrefectAttendanceSystem(root)
    root.mainloop()