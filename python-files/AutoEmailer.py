import win32com.client
import re
import subprocess
import time
from datetime import datetime, timedelta
import json
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from collections import deque
import csv
import winsound
import traceback
import uuid

# ==================== CONFIGURATION ====================

DEFAULT_CONFIG = {
    "kde_device_id": "",
    "email_keywords": ["kennedyc notification: assigned lead", "se notifications"],
    "scan_interval": 300,
    "emails_to_scan": 100,
    "catchup_hours": 24,
    "setup_completed": True,
    "auto_send": False,
    "sound_enabled": True,
    "sound_volume": 50,
    "email_response_enabled": False,
    "from_email": "",
    "active_preset": "Default - Water Inquiry",
    "business_hours": {
        "enabled": False,
        "start": "09:00",
        "end": "17:00"
    }
}

DEFAULT_PRESETS = {
    "Default - Water Inquiry": "Hey {firstname} this is Kodi with Culligan, I saw you entered some information in online in regards to your water, could you explain a little more on what issues you're having? Is it staining? or odors etc?",
    "After Hours": "Hi {firstname}, this is Kodi with Culligan. I received your inquiry after business hours. I'll follow up with you first thing tomorrow morning. Thanks!"
}

DEFAULT_EMAIL_TEMPLATES = {
    "Default Reply": {
        "subject": "Re: Your Water Inquiry",
        "body": "Hi {firstname},\n\nThank you for your interest in Culligan water solutions. I'll be reaching out shortly to discuss your water needs.\n\nBest regards,\nKodi\nCulligan of Kendallville"
    }
}

DEFAULT_STATS = {
    "total_texts_sent": 0,
    "total_emails_processed": 0,
    "total_email_responses_sent": 0,
    "daily_stats": {},
    "weekly_stats": {}
}

COLORS = {
    "bg": "#f0f2f5",
    "card": "#ffffff", 
    "primary": "#2c3e50",
    "secondary": "#34495e",
    "accent": "#3498db",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
    "text_light": "#7f8c8d",
    "background": "#f8f9fa"
}

class ModernCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["card"], relief="flat", bd=0, **kwargs)
        shadow = tk.Frame(parent, bg="#e0e0e0", height=2)
        shadow.place(in_=self, x=2, y=2, relwidth=1, relheight=1)
        self.lift()

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color=None, hover_color=None, 
                 width=120, height=35, icon=None, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color or COLORS["primary"]
        self.hover_color = hover_color or COLORS["secondary"]
        self.text = text
        self.icon = icon
        self.create_button()
        self.bind_events()
    
    def create_button(self):
        self.rect = self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(),
                                         fill=self.bg_color, outline="", width=0)
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.text_item = self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2,
                                         text=display_text, fill="white", 
                                         font=("Segoe UI", 9, "bold"))
    
    def bind_events(self):
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.tag_bind(self.rect, "<Button-1>", self.on_click)
        self.tag_bind(self.text_item, "<Button-1>", self.on_click)
    
    def on_click(self, event=None):
        if self.command:
            self.command()
    
    def on_enter(self, event=None):
        self.itemconfig(self.rect, fill=self.hover_color)
    
    def on_leave(self, event=None):
        self.itemconfig(self.rect, fill=self.bg_color)
    
    def update_text(self, new_text):
        self.text = new_text
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.itemconfig(self.text_item, text=display_text)

class AutoEmailer:
    def __init__(self, root):
        self.root = root
        self.root.title("Culligan Auto-Texter Pro - CRM System")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.data_file = "culligan_crm_data.json"
        self.data = {
            "config": {},
            "presets": {},
            "stats": {},
            "customers": [],
            "processed_emails": [],
            "pending_texts": [],
            "email_templates": {}
        }
        self.load_all_data()
        self.config = self.data["config"]
        self.presets = self.data["presets"] 
        self.stats = self.data["stats"]
        self.processed_emails = set(self.data["processed_emails"])
        self.pending_texts = deque(self.data["pending_texts"])
        self.email_templates = self.data["email_templates"]
        self.monitoring = False
        self.monitor_thread = None
        self.lead_history = []
        self.last_check_time = datetime.now() - timedelta(hours=24)
        self.session_texts_sent = 0
        self.session_emails_processed = 0
        self.session_email_responses = 0
        self.outlook = None
        self.outlook_inbox = None
        self.setup_theme()
        self.create_modern_ui()
        self.update_ui_loop()
        self.schedule_auto_save()
    
    def load_all_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                    for key in self.data:
                        if key in loaded_data:
                            self.data[key] = loaded_data[key]
                        else:
                            if key == "config":
                                self.data[key] = DEFAULT_CONFIG.copy()
                            elif key == "presets":
                                self.data[key] = DEFAULT_PRESETS.copy()
                            elif key == "stats":
                                self.data[key] = DEFAULT_STATS.copy()
                            elif key == "email_templates":
                                self.data[key] = DEFAULT_EMAIL_TEMPLATES.copy()
                print(f"Loaded data from {self.data_file}")
            else:
                self.data["config"] = DEFAULT_CONFIG.copy()
                self.data["presets"] = DEFAULT_PRESETS.copy()
                self.data["stats"] = DEFAULT_STATS.copy()
                self.data["email_templates"] = DEFAULT_EMAIL_TEMPLATES.copy()
                self.save_all_data()
                print(f"Created new data file: {self.data_file}")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data["config"] = DEFAULT_CONFIG.copy()
            self.data["presets"] = DEFAULT_PRESETS.copy() 
            self.data["stats"] = DEFAULT_STATS.copy()
            self.data["email_templates"] = DEFAULT_EMAIL_TEMPLATES.copy()
    
    def save_all_data(self):
        try:
            self.data["config"] = self.config
            self.data["presets"] = self.presets
            self.data["stats"] = self.stats
            self.data["processed_emails"] = list(self.processed_emails)
            self.data["pending_texts"] = list(self.pending_texts)
            self.data["email_templates"] = self.email_templates
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            print(f"Data saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def schedule_auto_save(self):
        self.save_all_data()
        self.root.after(300000, self.schedule_auto_save)
    
    def setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS["bg"])
        style.configure('TLabel', background=COLORS["bg"], foreground=COLORS["dark"])
        style.configure('TButton', font=("Segoe UI", 9))
        style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"), 
                       background=COLORS["card"], foreground=COLORS["primary"])
    
    def create_modern_ui(self):
        main_container = tk.Frame(self.root, bg=COLORS["bg"])
        main_container.pack(fill=tk.BOTH, expand=True)
        self.create_sidebar(main_container)
        content_area = tk.Frame(main_container, bg=COLORS["bg"])
        content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_top_bar(content_area)
        self.create_workflow_tabs(content_area)
    
    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS["primary"], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        logo_frame = tk.Frame(sidebar, bg=COLORS["primary"])
        logo_frame.pack(fill=tk.X, pady=30, padx=20)
        tk.Label(logo_frame, text="💧", font=("Segoe UI", 40), 
                bg=COLORS["primary"], fg="white").pack()
        tk.Label(logo_frame, text="Culligan", font=("Segoe UI", 20, "bold"), 
                bg=COLORS["primary"], fg="white").pack()
        tk.Label(logo_frame, text="CRM Pro", font=("Segoe UI", 11), 
                bg=COLORS["primary"], fg=COLORS["light"]).pack()
        nav_frame = tk.Frame(sidebar, bg=COLORS["primary"])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)
        self.nav_buttons = {}
        nav_items = [
            ("🏠", "Dashboard", 0),
            ("▶️", "Monitor", 1),
            ("📝", "Pending", 2),
            ("💰", "Pending Sold", 3),
            ("✅", "Sold & Installed", 4),
            ("📋", "Customer List", 5),
            ("🗑️", "Trashed", 6),
            ("📜", "History", 7),
            ("📊", "Statistics", 8),
            ("⚙️", "Settings", 9)
        ]
        for icon, text, idx in nav_items:
            btn = self.create_nav_button(nav_frame, icon, text, idx)
            btn.pack(fill=tk.X, pady=5)
            self.nav_buttons[idx] = btn
        status_frame = tk.Frame(sidebar, bg=COLORS["primary"])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=20)
        self.sidebar_status_canvas = tk.Canvas(status_frame, width=20, height=20, 
                                               highlightthickness=0, bg=COLORS["primary"])
        self.sidebar_status_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.sidebar_status_canvas.create_oval(2, 2, 18, 18, fill=COLORS["danger"], outline="")
        self.sidebar_status_label = tk.Label(status_frame, text="Offline", 
                                             font=("Segoe UI", 10, "bold"),
                                             bg=COLORS["primary"], fg="white")
        self.sidebar_status_label.pack(side=tk.LEFT)
    
    def create_nav_button(self, parent, icon, text, idx):
        btn_frame = tk.Frame(parent, bg=COLORS["primary"])
        def on_click():
            self.switch_tab(idx)
        btn = tk.Label(btn_frame, text=f"{icon}  {text}", font=("Segoe UI", 12),
                      bg=COLORS["primary"], fg="white", anchor="w", padx=20, pady=12,
                      cursor="hand2")
        btn.pack(fill=tk.BOTH)
        btn.bind("<Enter>", lambda e: btn.configure(bg=COLORS["secondary"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=COLORS["primary"] if idx != getattr(self, 'current_tab', 0) else COLORS["secondary"]))
        btn.bind("<Button-1>", lambda e: on_click())
        return btn_frame
    
    def create_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg=COLORS["card"], height=60)
        top_bar.pack(fill=tk.X, padx=20, pady=(20, 0))
        top_bar.pack_propagate(False)
        title_frame = tk.Frame(top_bar, bg=COLORS["card"])
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        self.page_title = tk.Label(title_frame, text="Dashboard", 
                                  font=("Segoe UI", 18, "bold"),
                                  bg=COLORS["card"], fg=COLORS["primary"])
        self.page_title.pack(anchor=tk.W, pady=15)
        stats_frame = tk.Frame(top_bar, bg=COLORS["card"])
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        tk.Label(stats_frame, text="Session:", font=("Segoe UI", 10),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, pady=20, padx=(0, 10))
        self.session_stats_label = tk.Label(stats_frame, 
                                           text="0 leads • 0 texts • 0 emails",
                                           font=("Segoe UI", 10, "bold"),
                                           bg=COLORS["card"], fg=COLORS["primary"])
        self.session_stats_label.pack(side=tk.LEFT, pady=20)
    
    def create_workflow_tabs(self, parent):
        self.tab_container = tk.Frame(parent, bg=COLORS["bg"])
        self.tab_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.tabs = {}
        for i in range(10):
            frame = tk.Frame(self.tab_container, bg=COLORS["bg"])
            self.tabs[i] = frame
        self.build_dashboard_tab()
        self.build_monitor_tab()
        self.build_pending_tab()
        self.build_pending_sold_tab()
        self.build_sold_installed_tab()
        self.build_customer_list_tab()
        self.build_trashed_tab()
        self.build_customers_tab()
        self.build_statistics_tab()
        self.build_settings_tab()
        self.current_tab = 0
        self.switch_tab(0)
    
    def switch_tab(self, idx):
        for frame in self.tabs.values():
            frame.pack_forget()
        self.tabs[idx].pack(fill=tk.BOTH, expand=True)
        for i, btn_frame in self.nav_buttons.items():
            btn = btn_frame.winfo_children()[0]
            if i == idx:
                btn.configure(bg=COLORS["secondary"])
            else:
                btn.configure(bg=COLORS["primary"])
        titles = ["Dashboard", "Monitor", "Pending", "Pending Sold", "Sold & Installed", 
                 "Customer List", "Trashed", "History", "Statistics", "Settings"]
        if idx < len(titles):
            self.page_title.config(text=titles[idx])
        self.current_tab = idx
        if idx == 2:
            self.refresh_pending_queue()
        elif idx == 3:
            self.refresh_pending_sold_tab()
        elif idx == 4:
            self.refresh_sold_installed_tab()
        elif idx == 5:
            self.refresh_customer_list()
        elif idx == 6:
            self.refresh_trashed_tab()
    
    def build_dashboard_tab(self):
        tab = self.tabs[0]
        welcome_card = ModernCard(tab)
        welcome_card.pack(fill=tk.X, pady=(0, 20))
        welcome_inner = tk.Frame(welcome_card, bg=COLORS["card"])
        welcome_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(welcome_inner, text="🏠 Welcome to Culligan CRM", 
                font=("Segoe UI", 20, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W)
        tk.Label(welcome_inner, text="Automated lead management and customer relationship system", 
                font=("Segoe UI", 12),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack(anchor=tk.W, pady=(5, 0))
        actions_frame = tk.Frame(welcome_inner, bg=COLORS["card"])
        actions_frame.pack(fill=tk.X, pady=(20, 0))
        self.dashboard_toggle_btn = ModernButton(actions_frame, "Start Scanning", self.toggle_monitoring,
                    bg_color=COLORS["success"], hover_color=COLORS["accent"],
                    width=200, height=50, icon="▶️")
        self.dashboard_toggle_btn.pack(side=tk.LEFT, padx=(0, 15))
        ModernButton(actions_frame, "Manual Scan", self.run_manual_scan,
                    bg_color=COLORS["warning"], hover_color="#E67E22",
                    width=180, height=50, icon="🔍").pack(side=tk.LEFT, padx=(0, 15))
        ModernButton(actions_frame, "View Pending", lambda: self.switch_tab(2),
                    bg_color=COLORS["info"], hover_color=COLORS["secondary"],
                    width=180, height=50, icon="📝").pack(side=tk.LEFT)
        self.create_dashboard_stats(tab)
    
    def create_dashboard_stats(self, parent):
        stats_container = tk.Frame(parent, bg=COLORS["bg"])
        stats_container.pack(fill=tk.BOTH, expand=True)
        stats_row = tk.Frame(stats_container, bg=COLORS["bg"])
        stats_row.pack(fill=tk.X, pady=(0, 20))
        self.stat_cards = {}
        for i, (key, title, color) in enumerate([
            ("emails_processed", "Emails Processed", COLORS["primary"]),
            ("texts_sent", "Texts Sent", COLORS["success"]),
            ("email_responses", "Email Replies", COLORS["info"]),
            ("pending_count", "Pending Approval", COLORS["warning"])
        ]):
            card = self.create_stat_card(stats_row, title, "0", color)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15 if i < 3 else 0))
            self.stat_cards[key] = card.winfo_children()[0].winfo_children()[0]
        crm_card = ModernCard(stats_container)
        crm_card.pack(fill=tk.BOTH, expand=True)
        crm_inner = tk.Frame(crm_card, bg=COLORS["card"])
        crm_inner.pack(fill=tk.BOTH, padx=30, pady=25)
        tk.Label(crm_inner, text="📊 CRM Overview", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        crm_grid = tk.Frame(crm_inner, bg=COLORS["card"])
        crm_grid.pack(fill=tk.X)
        self.crm_stats = {}
        crm_items = [
            ("total_customers", "Total Customers", COLORS["primary"]),
            ("pending_sold", "Pending Sold", COLORS["warning"]),
            ("sold_installed", "Sold & Installed", COLORS["success"]),
            ("active_today", "Active Today", COLORS["info"])
        ]
        for i, (key, label, color) in enumerate(crm_items):
            row = i // 2
            col = i % 2
            item_frame = tk.Frame(crm_grid, bg=COLORS["card"])
            item_frame.grid(row=row, column=col, sticky="ew", padx=(0, 20 if col == 0 else 0), pady=10)
            tk.Label(item_frame, text="0", font=("Segoe UI", 24, "bold"),
                    bg=COLORS["card"], fg=color).pack(side=tk.LEFT)
            tk.Label(item_frame, text=label, font=("Segoe UI", 11),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(15, 0))
            self.crm_stats[key] = item_frame.winfo_children()[0]
        crm_grid.grid_columnconfigure(0, weight=1)
        crm_grid.grid_columnconfigure(1, weight=1)
    
    def create_stat_card(self, parent, title, value, color):
        card = ModernCard(parent)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.BOTH, padx=20, pady=20)
        value_label = tk.Label(inner, text=value, font=("Segoe UI", 28, "bold"),
                              bg=COLORS["card"], fg=color)
        value_label.pack()
        tk.Label(inner, text=title, font=("Segoe UI", 11),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack()
        return card
    
    def build_monitor_tab(self):
        tab = self.tabs[1]
        control_card = ModernCard(tab)
        control_card.pack(fill=tk.X, pady=(0, 20))
        control_inner = tk.Frame(control_card, bg=COLORS["card"])
        control_inner.pack(fill=tk.X, padx=30, pady=25)
        ttk.Label(control_inner, text="Periodic Email Scanner",
                style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 20))
        status_row = tk.Frame(control_inner, bg=COLORS["card"])
        status_row.pack(fill=tk.X, pady=(0, 20))
        tk.Label(status_row, text="Status:", font=("Segoe UI", 12, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 15))
        self.monitor_status_canvas = tk.Canvas(status_row, width=24, height=24,
                                               highlightthickness=0, bg=COLORS["card"])
        self.monitor_status_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.monitor_status_canvas.create_oval(2, 2, 22, 22, fill=COLORS["danger"], outline="")
        self.monitor_status_text = tk.Label(status_row, text="Stopped", 
                                           font=("Segoe UI", 14, "bold"),
                                           bg=COLORS["card"], fg=COLORS["danger"])
        self.monitor_status_text.pack(side=tk.LEFT)
        mode_row = tk.Frame(control_inner, bg=COLORS["card"])
        mode_row.pack(fill=tk.X, pady=15)
        tk.Label(mode_row, text="Mode:", font=("Segoe UI", 11, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 20))
        self.auto_send_var = tk.BooleanVar(value=self.config.get("auto_send", False))
        ttk.Radiobutton(mode_row, text="🤖 Auto-Send (Automatic)", 
                       variable=self.auto_send_var, value=True,
                       command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_row, text="👤 Manual Approval (Review First)", 
                       variable=self.auto_send_var, value=False,
                       command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        btn_row = tk.Frame(control_inner, bg=COLORS["card"])
        btn_row.pack(pady=20)
        self.monitor_toggle_btn = ModernButton(btn_row, "Start Scanning", 
                                               self.toggle_monitoring,
                                               bg_color=COLORS["success"],
                                               hover_color=COLORS["accent"],
                                               width=250, height=55, icon="▶️")
        self.monitor_toggle_btn.pack(side=tk.LEFT, padx=10)
        ModernButton(btn_row, "Manual Scan", self.run_manual_scan,
                    bg_color=COLORS["warning"], hover_color="#E67E22",
                    width=200, height=55, icon="🔍").pack(side=tk.LEFT, padx=10)
        info_card = ModernCard(tab)
        info_card.pack(fill=tk.BOTH, expand=True)
        info_inner = tk.Frame(info_card, bg=COLORS["card"])
        info_inner.pack(fill=tk.BOTH, padx=30, pady=25)
        tk.Label(info_inner, text="📋 How It Works", font=("Segoe UI", 14, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        info_text = """
1. 🔄 Periodic Scanning: Every 5 minutes, the system checks your Outlook inbox for new leads
2. 🎯 Keyword Matching: Emails matching your configured keywords are identified as leads  
3. 📊 Data Extraction: Customer name, phone, and email are automatically extracted
4. 💬 CRM Integration: All customer interactions are logged in the built-in CRM
5. 📱 SMS/Email: Based on your mode, texts are sent automatically or added for approval
6. 🚨 Follow-up Tracking: Customers who don't reply are tracked for follow-up reminders
        """
        tk.Label(info_inner, text=info_text.strip(), font=("Segoe UI", 11),
                bg=COLORS["card"], fg=COLORS["dark"], justify=tk.LEFT).pack(anchor=tk.W)
    
    def build_pending_tab(self):
        tab = self.tabs[2]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.BOTH, padx=30, pady=20)
        ttk.Label(header_inner, text="Pending Approvals",
                style="Heading.TLabel").pack(side=tk.LEFT)
        self.pending_count_label = tk.Label(header_inner, text="0 pending",
                                           font=("Segoe UI", 12),
                                           bg=COLORS["card"], fg=COLORS["text_light"])
        self.pending_count_label.pack(side=tk.RIGHT)
        pending_card = ModernCard(tab)
        pending_card.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(pending_card, bg=COLORS["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(pending_card, orient="vertical", command=canvas.yview)
        self.pending_scrollable_frame = tk.Frame(canvas, bg=COLORS["card"])
        self.pending_scrollable_frame.bind("<Configure>", 
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.pending_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_pending_queue()
    
    def build_pending_sold_tab(self):
        tab = self.tabs[3]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="💰 Pending Sold - Awaiting Installation", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        content_frame = tk.Frame(tab, bg=COLORS["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(content_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.pending_sold_scrollable_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self.pending_sold_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.pending_sold_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_pending_sold_tab()
    
    def build_sold_installed_tab(self):
        tab = self.tabs[4]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="✅ Sold & Installed", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        filter_frame = tk.Frame(header_inner, bg=COLORS["card"])
        filter_frame.pack(side=tk.RIGHT)
        tk.Label(filter_frame, text="Filter by Install Week:", 
                font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 10))
        self.install_week_var = tk.StringVar(value="All")
        week_dropdown = ttk.Combobox(filter_frame, textvariable=self.install_week_var,
                                     state="readonly", width=20)
        week_dropdown.pack(side=tk.LEFT)
        week_dropdown.bind('<<ComboboxSelected>>', lambda e: self.refresh_sold_installed_tab())
        self.install_week_dropdown = week_dropdown
        commission_frame = tk.Frame(header_inner, bg=COLORS["card"])
        commission_frame.pack(side=tk.RIGHT, padx=(0, 30))
        tk.Label(commission_frame, text="Week Commission:", 
                font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 10))
        self.week_commission_label = tk.Label(commission_frame, text="$0.00", 
                                             font=("Segoe UI", 14, "bold"),
                                             bg=COLORS["card"], fg=COLORS["success"])
        self.week_commission_label.pack(side=tk.LEFT)
        content_frame = tk.Frame(tab, bg=COLORS["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(content_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.sold_installed_scrollable_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self.sold_installed_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.sold_installed_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_sold_installed_tab()
    
    def build_customer_list_tab(self):
        tab = self.tabs[5]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="📋 All Customers", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        search_frame = tk.Frame(header_inner, bg=COLORS["card"])
        search_frame.pack(side=tk.RIGHT)
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 14),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.customer_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.customer_search_var,
                               font=("Segoe UI", 11), width=30, relief="flat",
                               bg=COLORS["light"])
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.filter_customer_list())
        content_frame = tk.Frame(tab, bg=COLORS["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(content_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.customer_list_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self.customer_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.customer_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_customer_list()
    
    def build_trashed_tab(self):
        tab = self.tabs[6]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="🗑️ Hidden Customers", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        content_frame = tk.Frame(tab, bg=COLORS["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(content_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.trashed_scrollable_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self.trashed_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.trashed_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_trashed_tab()
    
    def build_customers_tab(self):
        tab = self.tabs[7]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="📜 Customer Interaction History", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        tk.Label(tab, text="📊 Coming Soon\n\nDetailed interaction analytics and history will be available here.", 
                font=("Segoe UI", 14), bg=COLORS["bg"], fg=COLORS["text_light"]).pack(expand=True)
    
    def build_statistics_tab(self):
        tab = self.tabs[8]
        header = ModernCard(tab)
        header.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header, bg=COLORS["card"])
        header_inner.pack(fill=tk.X, padx=30, pady=20)
        tk.Label(header_inner, text="📊 Statistics & Analytics", 
                font=("Segoe UI", 18, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        stats_container = tk.Frame(tab, bg=COLORS["bg"])
        stats_container.pack(fill=tk.BOTH, expand=True)
        row1 = tk.Frame(stats_container, bg=COLORS["bg"])
        row1.pack(fill=tk.X, pady=(0, 20))
        self.create_stat_box(row1, "Total Texts Sent", 
                            str(self.stats.get("total_texts_sent", 0)),
                            COLORS["success"]).pack(side=tk.LEFT, fill=tk.BOTH, 
                                                   expand=True, padx=(0, 10))
        self.create_stat_box(row1, "Emails Processed", 
                            str(self.stats.get("total_emails_processed", 0)),
                            COLORS["primary"]).pack(side=tk.LEFT, fill=tk.BOTH, 
                                                   expand=True, padx=(0, 10))
        self.create_stat_box(row1, "Email Replies", 
                            str(self.stats.get("total_email_responses_sent", 0)),
                            COLORS["warning"]).pack(side=tk.LEFT, fill=tk.BOTH, 
                                                   expand=True, padx=(10, 0))
    
    def create_stat_box(self, parent, title, value, color):
        card = ModernCard(parent)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.BOTH, padx=25, pady=25)
        tk.Label(inner, text=value, font=("Segoe UI", 32, "bold"),
                bg=COLORS["card"], fg=color).pack()
        tk.Label(inner, text=title, font=("Segoe UI", 12),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack()
        return card
    
    def build_settings_tab(self):
        tab = self.tabs[9]
        canvas = tk.Canvas(tab, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        settings_frame = tk.Frame(canvas, bg=COLORS["bg"])
        settings_frame.bind("<Configure>", 
                           lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        kde_card = ModernCard(settings_frame)
        kde_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        kde_inner = tk.Frame(kde_card, bg=COLORS["card"])
        kde_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(kde_inner, text="📱 KDE Connect Setup", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        tk.Label(kde_inner, text="Device ID for SMS sending:", font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(anchor=tk.W, pady=(0, 5))
        self.kde_id_var = tk.StringVar(value=self.config.get("kde_device_id", ""))
        tk.Entry(kde_inner, textvariable=self.kde_id_var, font=("Segoe UI", 11),
                width=50, relief="flat", bg=COLORS["light"]).pack(anchor=tk.W, pady=(0, 10))
        help_frame = tk.Frame(kde_inner, bg=COLORS["light"], relief="solid", bd=1)
        help_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(help_frame, text="💡 To find your KDE Connect device ID, run this command in terminal:",
                font=("Segoe UI", 9, "italic"), bg=COLORS["light"], fg=COLORS["dark"]).pack(anchor=tk.W, padx=10, pady=(8, 2))
        tk.Label(help_frame, text="kdeconnect-cli --list-devices",
                font=("Courier", 9, "bold"), bg=COLORS["light"], fg=COLORS["primary"]).pack(anchor=tk.W, padx=10, pady=(0, 8))
        keywords_card = ModernCard(settings_frame)
        keywords_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        keywords_inner = tk.Frame(keywords_card, bg=COLORS["card"])
        keywords_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(keywords_inner, text="🔍 Email Keywords", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        tk.Label(keywords_inner, text="Keywords to identify customer emails (one per line):", 
                font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(anchor=tk.W, pady=(0, 5))
        self.keywords_text = tk.Text(keywords_inner, height=4, width=60, 
                                    font=("Segoe UI", 10), relief="flat", bg=COLORS["light"])
        self.keywords_text.pack(anchor=tk.W, pady=(0, 15))
        keywords = self.config.get("email_keywords", [])
        self.keywords_text.insert(tk.END, "\n".join(keywords))
        adv_card = ModernCard(settings_frame)
        adv_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        adv_inner = tk.Frame(adv_card, bg=COLORS["card"])
        adv_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(adv_inner, text="⚙️ Advanced Settings", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        interval_frame = tk.Frame(adv_inner, bg=COLORS["card"])
        interval_frame.pack(fill=tk.X, pady=5)
        tk.Label(interval_frame, text="Scan Interval:", font=("Segoe UI", 10),
                bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=str(self.config.get("scan_interval", 300)))
        tk.Entry(interval_frame, textvariable=self.interval_var, width=10, relief="flat",
                bg=COLORS["light"]).pack(side=tk.LEFT, padx=5)
        tk.Label(interval_frame, text="seconds (300 = 5 minutes)", font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        templates_card = ModernCard(settings_frame)
        templates_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        templates_inner = tk.Frame(templates_card, bg=COLORS["card"])
        templates_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(templates_inner, text="💬 SMS Templates Manager", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        template_frame = tk.Frame(templates_inner, bg=COLORS["card"])
        template_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(template_frame, text="Active Template:", font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(side=tk.LEFT, padx=(0, 10))
        self.active_preset_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(template_frame, textvariable=self.active_preset_var,
                                        values=list(self.presets.keys()),
                                        state="readonly", width=30)
        self.template_dropdown.pack(side=tk.LEFT)
        current_preset = self.config.get("active_preset")
        if current_preset in self.presets:
            self.active_preset_var.set(current_preset)
        elif self.presets:
            self.active_preset_var.set(list(self.presets.keys())[0])
        template_btn_frame = tk.Frame(templates_inner, bg=COLORS["card"])
        template_btn_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Button(template_btn_frame, text="➕ New Template", 
                 command=self.add_sms_template,
                 bg=COLORS["success"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(template_btn_frame, text="✏️ Edit Template", 
                 command=self.edit_sms_template,
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(template_btn_frame, text="🗑️ Delete Template", 
                 command=self.delete_sms_template,
                 bg=COLORS["danger"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT)
        email_templates_card = ModernCard(settings_frame)
        email_templates_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        email_templates_inner = tk.Frame(email_templates_card, bg=COLORS["card"])
        email_templates_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(email_templates_inner, text="📧 Email Templates Manager", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        email_template_btn_frame = tk.Frame(email_templates_inner, bg=COLORS["card"])
        email_template_btn_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Button(email_template_btn_frame, text="➕ New Email Template", 
                 command=self.add_email_template,
                 bg=COLORS["success"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(email_template_btn_frame, text="✏️ Edit Email Template", 
                 command=self.edit_email_template,
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(email_template_btn_frame, text="📋 View All Templates", 
                 command=self.view_email_templates,
                 bg=COLORS["info"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold"), padx=15).pack(side=tk.LEFT)
        manual_entry_card = ModernCard(settings_frame)
        manual_entry_card.pack(fill=tk.X, pady=(0, 20), padx=20)
        manual_entry_inner = tk.Frame(manual_entry_card, bg=COLORS["card"])
        manual_entry_inner.pack(fill=tk.X, padx=30, pady=25)
        tk.Label(manual_entry_inner, text="👤 Manual Customer Entry", 
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 15))
        tk.Label(manual_entry_inner, text="Manually add a customer to the pending queue:", 
                font=("Segoe UI", 10),
                bg=COLORS["card"]).pack(anchor=tk.W, pady=(0, 10))
        tk.Button(manual_entry_inner, text="➕ Add Customer Manually", 
                 command=self.open_manual_customer_entry,
                 bg=COLORS["primary"], fg="white", relief="flat",
                 font=("Segoe UI", 10, "bold"), padx=30, pady=10).pack(anchor=tk.W)
        save_frame = tk.Frame(settings_frame, bg=COLORS["bg"])
        save_frame.pack(fill=tk.X, pady=20, padx=20)
        ModernButton(save_frame, "💾 Save All Settings", self.save_all_settings,
                    bg_color=COLORS["success"], hover_color="#27ae60",
                    width=200, height=50).pack()
    
    def add_sms_template(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add SMS Template")
        dialog.geometry("600x400")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text="Create New SMS Template", 
                font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        tk.Label(dialog, text="Template Name:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=("Segoe UI", 10), width=60).pack(padx=20, pady=5)
        tk.Label(dialog, text="Message (use {firstname}, {lastname}, {fullname}):", 
                font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        message_text = tk.Text(dialog, height=8, width=60, font=("Segoe UI", 10))
        message_text.pack(padx=20, pady=5)
        def save_template():
            name = name_var.get().strip()
            message = message_text.get("1.0", tk.END).strip()
            if not name or not message:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            self.presets[name] = message
            self.template_dropdown['values'] = list(self.presets.keys())
            self.save_all_data()
            messagebox.showinfo("Success", f"Template '{name}' created!")
            dialog.destroy()
        tk.Button(dialog, text="Save Template", command=save_template,
                 bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def edit_sms_template(self):
        template_name = self.active_preset_var.get()
        if not template_name or template_name not in self.presets:
            messagebox.showerror("Error", "Please select a template to edit")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit SMS Template: {template_name}")
        dialog.geometry("600x400")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text=f"Editing: {template_name}", 
                font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        tk.Label(dialog, text="Message:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
        message_text = tk.Text(dialog, height=10, width=60, font=("Segoe UI", 10))
        message_text.pack(padx=20, pady=5)
        message_text.insert(tk.END, self.presets[template_name])
        def save_changes():
            message = message_text.get("1.0", tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Message cannot be empty")
                return
            self.presets[template_name] = message
            self.save_all_data()
            messagebox.showinfo("Success", f"Template '{template_name}' updated!")
            dialog.destroy()
        tk.Button(dialog, text="Save Changes", command=save_changes,
                 bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def delete_sms_template(self):
        template_name = self.active_preset_var.get()
        if not template_name or template_name not in self.presets:
            messagebox.showerror("Error", "Please select a template to delete")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete template '{template_name}'?"):
            del self.presets[template_name]
            self.template_dropdown['values'] = list(self.presets.keys())
            if self.presets:
                self.active_preset_var.set(list(self.presets.keys())[0])
            self.save_all_data()
            messagebox.showinfo("Deleted", f"Template '{template_name}' deleted")
    
    def add_email_template(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Email Template")
        dialog.geometry("700x500")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text="Create New Email Template", 
                font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        tk.Label(dialog, text="Template Name:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=("Segoe UI", 10), width=70).pack(padx=20, pady=5)
        tk.Label(dialog, text="Subject:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        subject_var = tk.StringVar()
        tk.Entry(dialog, textvariable=subject_var, font=("Segoe UI", 10), width=70).pack(padx=20, pady=5)
        tk.Label(dialog, text="Body (use {firstname}, {lastname}, {fullname}):", 
                font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        body_text = tk.Text(dialog, height=10, width=70, font=("Segoe UI", 10))
        body_text.pack(padx=20, pady=5)
        def save_template():
            name = name_var.get().strip()
            subject = subject_var.get().strip()
            body = body_text.get("1.0", tk.END).strip()
            if not name or not subject or not body:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            self.email_templates[name] = {"subject": subject, "body": body}
            self.save_all_data()
            messagebox.showinfo("Success", f"Email template '{name}' created!")
            dialog.destroy()
        tk.Button(dialog, text="Save Template", command=save_template,
                 bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def edit_email_template(self):
        if not self.email_templates:
            messagebox.showerror("Error", "No email templates available")
            return
        selection_dialog = tk.Toplevel(self.root)
        selection_dialog.title("Select Email Template")
        selection_dialog.geometry("400x300")
        selection_dialog.configure(bg=COLORS["bg"])
        tk.Label(selection_dialog, text="Select template to edit:", 
                font=("Segoe UI", 12, "bold"), bg=COLORS["bg"]).pack(pady=15)
        template_var = tk.StringVar()
        for template_name in self.email_templates.keys():
            tk.Radiobutton(selection_dialog, text=template_name, variable=template_var,
                          value=template_name, bg=COLORS["bg"], font=("Segoe UI", 10)).pack(anchor=tk.W, padx=40)
        if self.email_templates:
            template_var.set(list(self.email_templates.keys())[0])
        def open_editor():
            selected = template_var.get()
            if not selected:
                return
            selection_dialog.destroy()
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit Email Template: {selected}")
            dialog.geometry("700x500")
            dialog.configure(bg=COLORS["bg"])
            tk.Label(dialog, text=f"Editing: {selected}", 
                    font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
            template = self.email_templates[selected]
            tk.Label(dialog, text="Subject:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
            subject_var = tk.StringVar(value=template.get("subject", ""))
            tk.Entry(dialog, textvariable=subject_var, font=("Segoe UI", 10), width=70).pack(padx=20, pady=5)
            tk.Label(dialog, text="Body:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
            body_text = tk.Text(dialog, height=12, width=70, font=("Segoe UI", 10))
            body_text.pack(padx=20, pady=5)
            body_text.insert(tk.END, template.get("body", ""))
            def save_changes():
                self.email_templates[selected]["subject"] = subject_var.get().strip()
                self.email_templates[selected]["body"] = body_text.get("1.0", tk.END).strip()
                self.save_all_data()
                messagebox.showinfo("Success", f"Email template '{selected}' updated!")
                dialog.destroy()
            tk.Button(dialog, text="Save Changes", command=save_changes,
                     bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20, pady=10).pack(pady=20)
        tk.Button(selection_dialog, text="Edit Selected", command=open_editor,
                 bg=COLORS["primary"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def view_email_templates(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Email Templates")
        dialog.geometry("800x600")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text="All Email Templates", 
                font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        canvas = tk.Canvas(dialog, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg"])
        scrollable_frame.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        for name, template in self.email_templates.items():
            card = tk.Frame(scrollable_frame, bg=COLORS["card"], relief="solid", bd=1)
            card.pack(fill=tk.X, pady=5, padx=10)
            tk.Label(card, text=name, font=("Segoe UI", 12, "bold"),
                    bg=COLORS["card"]).pack(anchor=tk.W, padx=15, pady=(10, 5))
            tk.Label(card, text=f"Subject: {template.get('subject', '')}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(anchor=tk.W, padx=15)
            body_preview = template.get('body', '')[:100] + "..." if len(template.get('body', '')) > 100 else template.get('body', '')
            tk.Label(card, text=f"Body: {body_preview}", 
                    font=("Segoe UI", 9, "italic"),
                    bg=COLORS["card"], fg=COLORS["text_light"], wraplength=700).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def open_manual_customer_entry(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Customer Entry")
        dialog.geometry("600x500")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text="Add Customer Manually", 
                font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        tk.Label(dialog, text="Full Name:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=("Segoe UI", 10), width=50).pack(padx=20, pady=5)
        tk.Label(dialog, text="Phone Number:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        phone_var = tk.StringVar()
        tk.Entry(dialog, textvariable=phone_var, font=("Segoe UI", 10), width=50).pack(padx=20, pady=5)
        tk.Label(dialog, text="Email Address:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        email_var = tk.StringVar()
        tk.Entry(dialog, textvariable=email_var, font=("Segoe UI", 10), width=50).pack(padx=20, pady=5)
        tk.Label(dialog, text="Custom Message (optional):", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
        message_text = tk.Text(dialog, height=6, width=50, font=("Segoe UI", 10))
        message_text.pack(padx=20, pady=5)
        def add_customer():
            name = name_var.get().strip()
            phone = phone_var.get().strip()
            email = email_var.get().strip()
            custom_message = message_text.get("1.0", tk.END).strip()
            if not name:
                messagebox.showerror("Error", "Please enter customer name")
                return
            if not phone and not email:
                messagebox.showerror("Error", "Please enter at least phone or email")
                return
            firstname, lastname = self.parse_customer_name(name)
            if custom_message:
                message = custom_message
            else:
                template_name = self.get_appropriate_template()
                message_template = self.presets.get(template_name, "")
                message = self.format_message(message_template, firstname, lastname)
            customer_data = {
                'email_id': f"manual_{uuid.uuid4()}",
                'full_name': name,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
                'email': email,
                'message': message,
                'priority': 'normal'
            }
            self.pending_texts.append(customer_data)
            self.save_all_data()
            messagebox.showinfo("Success", f"Customer '{name}' added to pending queue!")
            dialog.destroy()
            self.switch_tab(2)
        tk.Button(dialog, text="Add to Pending Queue", command=add_customer,
                 bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=30, pady=12).pack(pady=20)
    
    def check_customer_exists(self, phone, email):
        for customer in self.data["customers"]:
            if (phone and customer.get('phone') == phone) or \
               (email and customer.get('email') == email):
                return True
        return False
    
    def add_customer_interaction(self, customer_data, message, interaction_type, status, is_outbound=True):
        try:
            customer_phone = customer_data.get('phone', '')
            customer_email = customer_data.get('email', '')
            customer = None
            for c in self.data["customers"]:
                if (customer_phone and c.get('phone') == customer_phone) or \
                   (customer_email and c.get('email') == customer_email):
                    customer = c
                    break
            if not customer:
                customer = {
                    "id": str(uuid.uuid4()),
                    "name": customer_data.get('full_name', 'Unknown'),
                    "phone": customer_phone,
                    "email": customer_email,
                    "created_date": datetime.now().isoformat(),
                    "last_contact": datetime.now().isoformat(),
                    "last_inbound": None,
                    "last_outbound": None,
                    "status": "active",
                    "interactions": [],
                    "notes": [],
                    "sales_info": {
                        "equipment_wanted": "",
                        "purchased_equipment": "",
                        "pre_tax_amount": 0.0,
                        "commission": 0.0,
                        "install_date": "",
                        "install_week": ""
                    }
                }
                self.data["customers"].append(customer)
            interaction = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": interaction_type,
                "message": message,
                "status": status,
                "is_outbound": is_outbound
            }
            customer["interactions"].append(interaction)
            customer["last_contact"] = datetime.now().isoformat()
            if is_outbound:
                customer["last_outbound"] = datetime.now().isoformat()
            else:
                customer["last_inbound"] = datetime.now().isoformat()
                customer["status"] = "replied"
            self.save_all_data()
            return customer
        except Exception as e:
            print(f"Error adding customer interaction: {e}")
            return None
    
    def add_customer_note(self, customer, note_text):
        try:
            note = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "text": note_text
            }
            if "notes" not in customer:
                customer["notes"] = []
            customer["notes"].append(note)
            self.save_all_data()
            return True
        except Exception as e:
            print(f"Error adding note: {e}")
            return False
    
    def get_time_ago(self, timestamp):
        try:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            now = datetime.now()
            diff = now - timestamp
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        except:
            return "Unknown"
    
    def refresh_pending_sold_tab(self):
        try:
            for widget in self.pending_sold_scrollable_frame.winfo_children():
                widget.destroy()
            pending_sold_customers = [c for c in self.data["customers"] if c.get("status") == "pending_sold"]
            if not pending_sold_customers:
                no_customers = tk.Frame(self.pending_sold_scrollable_frame, bg=COLORS["bg"])
                no_customers.pack(fill=tk.BOTH, expand=True, pady=50)
                tk.Label(no_customers, text="💰", font=("Segoe UI", 48),
                        bg=COLORS["bg"]).pack()
                tk.Label(no_customers, text="No pending sales", 
                        font=("Segoe UI", 16, "bold"),
                        bg=COLORS["bg"], fg=COLORS["text_light"]).pack()
                tk.Label(no_customers, text="Mark customers as 'Pending Sold' to track installations", 
                        font=("Segoe UI", 12),
                        bg=COLORS["bg"], fg=COLORS["text_light"]).pack()
                return
            pending_sold_customers.sort(key=lambda x: x.get('sales_info', {}).get('install_date', ''))
            for customer in pending_sold_customers:
                self.create_pending_sold_customer_card(customer)
        except Exception as e:
            print(f"Error refreshing pending sold tab: {e}")
            traceback.print_exc()
    
    def refresh_sold_installed_tab(self):
        try:
            for widget in self.sold_installed_scrollable_frame.winfo_children():
                widget.destroy()
            sold_customers = [c for c in self.data["customers"] if c.get("status") == "sold_installed"]
            install_weeks = set()
            for customer in sold_customers:
                week = customer.get('sales_info', {}).get('install_week', '')
                if week:
                    install_weeks.add(week)
            weeks_list = ["All"] + sorted(list(install_weeks), reverse=True)
            self.install_week_dropdown['values'] = weeks_list
            selected_week = self.install_week_var.get()
            if selected_week != "All":
                sold_customers = [c for c in sold_customers 
                                 if c.get('sales_info', {}).get('install_week', '') == selected_week]
            total_commission = sum(c.get('sales_info', {}).get('commission', 0.0) for c in sold_customers)
            self.week_commission_label.config(text=f"${total_commission:,.2f}")
            if not sold_customers:
                no_customers = tk.Frame(self.sold_installed_scrollable_frame, bg=COLORS["bg"])
                no_customers.pack(fill=tk.BOTH, expand=True, pady=50)
                tk.Label(no_customers, text="✅", font=("Segoe UI", 48),
                        bg=COLORS["bg"]).pack()
                tk.Label(no_customers, text="No completed installations", 
                        font=("Segoe UI", 16, "bold"),
                        bg=COLORS["bg"], fg=COLORS["text_light"]).pack()
                return
            sold_customers.sort(key=lambda x: x.get('sales_info', {}).get('install_date', ''), reverse=True)
            for customer in sold_customers:
                self.create_sold_installed_customer_card(customer)
        except Exception as e:
            print(f"Error refreshing sold & installed tab: {e}")
            traceback.print_exc()
    
    def refresh_customer_list(self):
        try:
            self.filter_customer_list()
        except Exception as e:
            print(f"Error refreshing customer list: {e}")
    
    def filter_customer_list(self):
        search_term = self.customer_search_var.get().lower() if hasattr(self, 'customer_search_var') else ""
        for widget in self.customer_list_frame.winfo_children():
            widget.destroy()
        filtered_customers = []
        for customer in self.data["customers"]:
            status = customer.get("status", "active")
            if status in ["trashed", "pending_sold", "sold_installed"]:
                continue
            name = customer.get('name', '').lower()
            phone = customer.get('phone', '').lower()
            email = customer.get('email', '').lower()
            if (not search_term or 
                search_term in name or 
                search_term in phone or 
                search_term in email):
                filtered_customers.append(customer)
        filtered_customers.sort(key=lambda x: x.get('last_contact', ''), reverse=True)
        for customer in filtered_customers:
            self.create_customer_list_card(customer)
    
    def refresh_trashed_tab(self):
        try:
            for widget in self.trashed_scrollable_frame.winfo_children():
                widget.destroy()
            trashed_customers = [c for c in self.data["customers"] if c.get("status") == "trashed"]
            if not trashed_customers:
                no_customers = tk.Frame(self.trashed_scrollable_frame, bg=COLORS["bg"])
                no_customers.pack(fill=tk.BOTH, expand=True, pady=50)
                tk.Label(no_customers, text="🗂️", font=("Segoe UI", 48),
                        bg=COLORS["bg"]).pack()
                tk.Label(no_customers, text="No hidden customers", 
                        font=("Segoe UI", 16, "bold"),
                        bg=COLORS["bg"], fg=COLORS["text_light"]).pack()
                return
            for customer in trashed_customers:
                self.create_trashed_customer_card(customer)
        except Exception as e:
            print(f"Error refreshing trashed tab: {e}")
    
    def create_pending_sold_customer_card(self, customer):
        card = ModernCard(self.pending_sold_scrollable_frame)
        card.pack(fill=tk.X, pady=5)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=20, pady=15)
        info_row = tk.Frame(inner, bg=COLORS["card"])
        info_row.pack(fill=tk.X, pady=(0, 10))
        tk.Label(info_row, text=customer.get('name', 'Unknown'), 
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        install_date = customer.get('sales_info', {}).get('install_date', '')
        if install_date:
            tk.Label(info_row, text=f"📅 Install: {install_date}", 
                    font=("Segoe UI", 11),
                    bg=COLORS["card"], fg=COLORS["warning"]).pack(side=tk.LEFT, padx=(15, 0))
        contact_row = tk.Frame(inner, bg=COLORS["card"])
        contact_row.pack(fill=tk.X, pady=(0, 10))
        if customer.get('phone'):
            tk.Label(contact_row, text=f"📞 {customer['phone']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)
        sales_info = customer.get('sales_info', {})
        equipment = sales_info.get('equipment_wanted', 'N/A')
        amount = sales_info.get('pre_tax_amount', 0.0)
        commission = sales_info.get('commission', 0.0)
        sales_row = tk.Frame(inner, bg=COLORS["card"])
        sales_row.pack(fill=tk.X, pady=(0, 15))
        tk.Label(sales_row, text=f"🔧 Equipment: {equipment}", 
                font=("Segoe UI", 10),
                bg=COLORS["card"], fg=COLORS["dark"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(sales_row, text=f"💵 Amount: ${amount:,.2f}", 
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["card"], fg=COLORS["success"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(sales_row, text=f"💰 Commission: ${commission:,.2f}", 
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["card"], fg=COLORS["info"]).pack(side=tk.LEFT)
        btn_row = tk.Frame(inner, bg=COLORS["card"])
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="✅ Mark as Installed", 
                 command=lambda c=customer: self.mark_as_installed(c),
                 bg=COLORS["success"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="📝 Add Note", 
                 command=lambda c=customer: self.quick_add_note(c),
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="👀 View Details", 
                 command=lambda c=customer: self.show_customer_details_popup(c),
                 bg=COLORS["secondary"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="↩️ Move to Customer List", 
                 command=lambda c=customer: self.move_to_customer_list(c),
                 bg=COLORS["info"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    def create_sold_installed_customer_card(self, customer):
        card = ModernCard(self.sold_installed_scrollable_frame)
        card.pack(fill=tk.X, pady=5)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=20, pady=15)
        info_row = tk.Frame(inner, bg=COLORS["card"])
        info_row.pack(fill=tk.X, pady=(0, 10))
        tk.Label(info_row, text=customer.get('name', 'Unknown'), 
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        sales_info = customer.get('sales_info', {})
        install_date = sales_info.get('install_date', '')
        install_week = sales_info.get('install_week', '')
        if install_date:
            tk.Label(info_row, text=f"📅 Installed: {install_date}", 
                    font=("Segoe UI", 11),
                    bg=COLORS["card"], fg=COLORS["success"]).pack(side=tk.LEFT, padx=(15, 0))
        if install_week:
            tk.Label(info_row, text=f"📊 Week: {install_week}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(10, 0))
        contact_row = tk.Frame(inner, bg=COLORS["card"])
        contact_row.pack(fill=tk.X, pady=(0, 10))
        if customer.get('phone'):
            tk.Label(contact_row, text=f"📞 {customer['phone']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)
        purchased_equipment = sales_info.get('purchased_equipment', 'N/A')
        amount = sales_info.get('pre_tax_amount', 0.0)
        commission = sales_info.get('commission', 0.0)
        sales_row = tk.Frame(inner, bg=COLORS["card"])
        sales_row.pack(fill=tk.X, pady=(0, 15))
        tk.Label(sales_row, text=f"🔧 Equipment: {purchased_equipment}", 
                font=("Segoe UI", 10),
                bg=COLORS["card"], fg=COLORS["dark"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(sales_row, text=f"💵 Sale: ${amount:,.2f}", 
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["card"], fg=COLORS["success"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(sales_row, text=f"💰 Commission: ${commission:,.2f}", 
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["card"], fg=COLORS["info"]).pack(side=tk.LEFT)
        btn_row = tk.Frame(inner, bg=COLORS["card"])
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="❌ Installation Canceled", 
                 command=lambda c=customer: self.cancel_installation(c),
                 bg="#E67E22", fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="📝 Add Note", 
                 command=lambda c=customer: self.quick_add_note(c),
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="👀 View Details", 
                 command=lambda c=customer: self.show_customer_details_popup(c),
                 bg=COLORS["secondary"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
    
    def create_customer_list_card(self, customer):
        card = ModernCard(self.customer_list_frame)
        card.pack(fill=tk.X, pady=3)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=20, pady=12)
        info_row = tk.Frame(inner, bg=COLORS["card"])
        info_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(info_row, text=customer.get('name', 'Unknown'), 
                font=("Segoe UI", 13, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        status = customer.get('status', 'active')
        status_colors = {"active": COLORS["text_light"], "replied": COLORS["success"]}
        status_text = {"active": "Active", "replied": "Replied"}
        tk.Label(info_row, text=status_text.get(status, status), 
                font=("Segoe UI", 10),
                bg=COLORS["card"], fg=status_colors.get(status, COLORS["text_light"])).pack(side=tk.LEFT, padx=(15, 0))
        if customer.get('last_contact'):
            last_contact = datetime.fromisoformat(customer['last_contact'])
            time_ago = self.get_time_ago(last_contact)
            tk.Label(info_row, text=f"Last contact: {time_ago}", 
                    font=("Segoe UI", 9),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.RIGHT)
        contact_row = tk.Frame(inner, bg=COLORS["card"])
        contact_row.pack(fill=tk.X, pady=(0, 10))
        if customer.get('phone'):
            tk.Label(contact_row, text=f"📞 {customer['phone']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)
        if customer.get('email'):
            tk.Label(contact_row, text=f"📧 {customer['email']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(15, 0))
        interaction_count = len(customer.get('interactions', []))
        tk.Label(contact_row, text=f"💬 {interaction_count} interactions", 
                font=("Segoe UI", 9),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.RIGHT)
        btn_row = tk.Frame(inner, bg=COLORS["card"])
        btn_row.pack(fill=tk.X)
        if customer.get('phone'):
            tk.Button(btn_row, text="📱 SMS", 
                     command=lambda c=customer: self.quick_sms_customer(c),
                     bg=COLORS["success"], fg="white", relief="flat",
                     font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 5))
        if customer.get('email'):
            tk.Button(btn_row, text="📧 Email", 
                     command=lambda c=customer: self.quick_email_customer(c),
                     bg=COLORS["info"], fg="white", relief="flat",
                     font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_row, text="💰 Mark Sold", 
                 command=lambda c=customer: self.mark_as_pending_sold(c),
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_row, text="📝 Note", 
                 command=lambda c=customer: self.quick_add_note(c),
                 bg=COLORS["secondary"], fg="white", relief="flat",
                 font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_row, text="👀 Details", 
                 command=lambda c=customer: self.show_customer_details_popup(c),
                 bg=COLORS["primary"], fg="white", relief="flat",
                 font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(btn_row, text="🗑️ Hide", 
                 command=lambda c=customer: self.trash_customer(c),
                 bg=COLORS["danger"], fg="white", relief="flat",
                 font=("Segoe UI", 8, "bold"), padx=15).pack(side=tk.RIGHT)
    
    def create_trashed_customer_card(self, customer):
        card = ModernCard(self.trashed_scrollable_frame)
        card.pack(fill=tk.X, pady=5)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=20, pady=15)
        info_row = tk.Frame(inner, bg=COLORS["card"])
        info_row.pack(fill=tk.X, pady=(0, 10))
        tk.Label(info_row, text=customer.get('name', 'Unknown'), 
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        tk.Label(info_row, text="Hidden", 
                font=("Segoe UI", 11),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(15, 0))
        contact_row = tk.Frame(inner, bg=COLORS["card"])
        contact_row.pack(fill=tk.X, pady=(0, 15))
        if customer.get('phone'):
            tk.Label(contact_row, text=f"📞 {customer['phone']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)
        if customer.get('email'):
            tk.Label(contact_row, text=f"📧 {customer['email']}", 
                    font=("Segoe UI", 10),
                    bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(15, 0))
        btn_row = tk.Frame(inner, bg=COLORS["card"])
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="↩️ Restore", 
                 command=lambda c=customer: self.restore_customer(c),
                 bg=COLORS["success"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="👀 View Details", 
                 command=lambda c=customer: self.show_customer_details_popup(c),
                 bg=COLORS["secondary"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_row, text="🗑️ Delete Forever", 
                 command=lambda c=customer: self.delete_customer_forever(c),
                 bg=COLORS["danger"], fg="white", relief="flat",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    def show_customer_details_popup(self, customer):
        try:
            popup = tk.Toplevel(self.root)
            popup.title(f"Customer Details - {customer.get('name', 'Unknown')}")
            popup.geometry("900x700")
            popup.configure(bg=COLORS["bg"])
            popup.attributes('-topmost', True)
            def toggle_pin():
                current_state = popup.attributes('-topmost')
                popup.attributes('-topmost', not current_state)
                pin_btn.config(text="📌 Pinned" if not current_state else "📍 Pin")
            header = tk.Frame(popup, bg=COLORS["primary"])
            header.pack(fill=tk.X)
            header_left = tk.Frame(header, bg=COLORS["primary"])
            header_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=15)
            tk.Label(header_left, text=customer.get('name', 'Unknown'), 
                    font=("Segoe UI", 18, "bold"), bg=COLORS["primary"], fg="white").pack(anchor=tk.W)
            status = customer.get('status', 'active')
            status_text = {
                "active": "Active",
                "replied": "Replied",
                "pending_sold": "Pending Sold",
                "sold_installed": "Sold & Installed",
                "trashed": "Hidden"
            }
            tk.Label(header_left, text=status_text.get(status, status), 
                    font=("Segoe UI", 11), bg=COLORS["primary"], fg=COLORS["light"]).pack(anchor=tk.W)
            header_right = tk.Frame(header, bg=COLORS["primary"])
            header_right.pack(side=tk.RIGHT, padx=20)
            pin_btn = tk.Button(header_right, text="📌 Pinned", command=toggle_pin,
                               bg=COLORS["secondary"], fg="white", relief="flat",
                               font=("Segoe UI", 9, "bold"), padx=15, pady=8)
            pin_btn.pack()
            canvas = tk.Canvas(popup, bg=COLORS["bg"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            content_frame = tk.Frame(canvas, bg=COLORS["bg"])
            content_frame.bind("<Configure>", 
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)
            contact_card = ModernCard(content_frame)
            contact_card.pack(fill=tk.X, pady=(0, 15))
            contact_inner = tk.Frame(contact_card, bg=COLORS["card"])
            contact_inner.pack(fill=tk.X, padx=25, pady=20)
            tk.Label(contact_inner, text="📞 Contact Information", 
                    font=("Segoe UI", 14, "bold"), bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 10))
            if customer.get('phone'):
                info_row = tk.Frame(contact_inner, bg=COLORS["card"])
                info_row.pack(fill=tk.X, pady=5)
                tk.Label(info_row, text="Phone:", font=("Segoe UI", 11, "bold"),
                        bg=COLORS["card"], width=15, anchor="w").pack(side=tk.LEFT)
                tk.Label(info_row, text=customer['phone'], font=("Segoe UI", 11),
                        bg=COLORS["card"]).pack(side=tk.LEFT)
            if customer.get('email'):
                info_row = tk.Frame(contact_inner, bg=COLORS["card"])
                info_row.pack(fill=tk.X, pady=5)
                tk.Label(info_row, text="Email:", font=("Segoe UI", 11, "bold"),
                        bg=COLORS["card"], width=15, anchor="w").pack(side=tk.LEFT)
                tk.Label(info_row, text=customer['email'], font=("Segoe UI", 11),
                        bg=COLORS["card"]).pack(side=tk.LEFT)
            if customer.get('created_date'):
                info_row = tk.Frame(contact_inner, bg=COLORS["card"])
                info_row.pack(fill=tk.X, pady=5)
                tk.Label(info_row, text="Created:", font=("Segoe UI", 11, "bold"),
                        bg=COLORS["card"], width=15, anchor="w").pack(side=tk.LEFT)
                created = datetime.fromisoformat(customer['created_date']).strftime("%Y-%m-%d %I:%M %p")
                tk.Label(info_row, text=created, font=("Segoe UI", 11),
                        bg=COLORS["card"]).pack(side=tk.LEFT)
            if customer.get('last_contact'):
                info_row = tk.Frame(contact_inner, bg=COLORS["card"])
                info_row.pack(fill=tk.X, pady=5)
                tk.Label(info_row, text="Last Contact:", font=("Segoe UI", 11, "bold"),
                        bg=COLORS["card"], width=15, anchor="w").pack(side=tk.LEFT)
                time_ago = self.get_time_ago(customer['last_contact'])
                tk.Label(info_row, text=time_ago, font=("Segoe UI", 11),
                        bg=COLORS["card"]).pack(side=tk.LEFT)
            if status in ["pending_sold", "sold_installed"]:
                sales_card = ModernCard(content_frame)
                sales_card.pack(fill=tk.X, pady=(0, 15))
                sales_inner = tk.Frame(sales_card, bg=COLORS["card"])
                sales_inner.pack(fill=tk.X, padx=25, pady=20)
                tk.Label(sales_inner, text="💰 Sales Information", 
                        font=("Segoe UI", 14, "bold"), bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 10))
                sales_info = customer.get('sales_info', {})
                if sales_info.get('equipment_wanted'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Equipment Wanted:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=sales_info['equipment_wanted'], font=("Segoe UI", 11),
                            bg=COLORS["card"], wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT)
                if sales_info.get('purchased_equipment'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Purchased Equipment:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=sales_info['purchased_equipment'], font=("Segoe UI", 11),
                            bg=COLORS["card"], wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT)
                if sales_info.get('pre_tax_amount'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Sale Amount:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=f"${sales_info['pre_tax_amount']:,.2f}", font=("Segoe UI", 11),
                            bg=COLORS["card"], fg=COLORS["success"]).pack(side=tk.LEFT)
                if sales_info.get('commission'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Commission:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=f"${sales_info['commission']:,.2f}", font=("Segoe UI", 11),
                            bg=COLORS["card"], fg=COLORS["info"]).pack(side=tk.LEFT)
                if sales_info.get('install_date'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Install Date:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=sales_info['install_date'], font=("Segoe UI", 11),
                            bg=COLORS["card"]).pack(side=tk.LEFT)
                if sales_info.get('install_week'):
                    info_row = tk.Frame(sales_inner, bg=COLORS["card"])
                    info_row.pack(fill=tk.X, pady=5)
                    tk.Label(info_row, text="Install Week:", font=("Segoe UI", 11, "bold"),
                            bg=COLORS["card"], width=20, anchor="w").pack(side=tk.LEFT)
                    tk.Label(info_row, text=sales_info['install_week'], font=("Segoe UI", 11),
                            bg=COLORS["card"]).pack(side=tk.LEFT)
            notes = customer.get('notes', [])
            if notes:
                notes_card = ModernCard(content_frame)
                notes_card.pack(fill=tk.X, pady=(0, 15))
                notes_inner = tk.Frame(notes_card, bg=COLORS["card"])
                notes_inner.pack(fill=tk.X, padx=25, pady=20)
                tk.Label(notes_inner, text="📝 Notes", 
                        font=("Segoe UI", 14, "bold"), bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 10))
                for note in reversed(notes):
                    note_frame = tk.Frame(notes_inner, bg=COLORS["light"], relief="solid", bd=1)
                    note_frame.pack(fill=tk.X, pady=5)
                    note_content = tk.Frame(note_frame, bg=COLORS["light"])
                    note_content.pack(fill=tk.X, padx=10, pady=8)
                    timestamp = note.get('timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%Y-%m-%d %I:%M %p")
                        except:
                            time_str = timestamp
                    else:
                        time_str = "Unknown time"
                    tk.Label(note_content, text=time_str, 
                            font=("Segoe UI", 9), bg=COLORS["light"], fg=COLORS["dark"]).pack(anchor=tk.W)
                    tk.Label(note_content, text=note.get('text', ''), 
                            font=("Segoe UI", 10), bg=COLORS["light"], fg=COLORS["dark"],
                            anchor="w", justify="left", wraplength=800).pack(anchor=tk.W, pady=(2, 0))
            interactions = customer.get('interactions', [])
            if interactions:
                interactions_card = ModernCard(content_frame)
                interactions_card.pack(fill=tk.X, pady=(0, 15))
                interactions_inner = tk.Frame(interactions_card, bg=COLORS["card"])
                interactions_inner.pack(fill=tk.X, padx=25, pady=20)
                tk.Label(interactions_inner, text=f"💬 Interactions ({len(interactions)})", 
                        font=("Segoe UI", 14, "bold"), bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W, pady=(0, 10))
                for interaction in reversed(interactions[-10:]):
                    self.create_interaction_card_simple(interactions_inner, interaction)
            action_frame = tk.Frame(content_frame, bg=COLORS["bg"])
            action_frame.pack(fill=tk.X, pady=15)
            tk.Button(action_frame, text="📝 Add Note", 
                     command=lambda: [self.quick_add_note(customer), popup.destroy()],
                     bg=COLORS["warning"], fg="white", relief="flat",
                     font=("Segoe UI", 10, "bold"), padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
            tk.Button(action_frame, text="Close", command=popup.destroy,
                     bg=COLORS["secondary"], fg="white", relief="flat",
                     font=("Segoe UI", 10, "bold"), padx=20, pady=10).pack(side=tk.RIGHT)
        except Exception as e:
            print(f"Error showing customer details popup: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to show customer details: {str(e)}")
    
    def create_interaction_card_simple(self, parent, interaction):
        card = tk.Frame(parent, bg=COLORS["light"], relief="solid", bd=1)
        card.pack(fill=tk.X, pady=3)
        inner = tk.Frame(card, bg=COLORS["light"])
        inner.pack(fill=tk.X, padx=10, pady=8)
        header_row = tk.Frame(inner, bg=COLORS["light"])
        header_row.pack(fill=tk.X, pady=(0, 5))
        direction = "→" if interaction.get('is_outbound') else "←"
        direction_color = COLORS["primary"] if interaction.get('is_outbound') else COLORS["success"]
        tk.Label(header_row, text=f"{direction} {interaction.get('type', 'Message')}", 
                font=("Segoe UI", 10, "bold"), bg=COLORS["light"], fg=direction_color).pack(side=tk.LEFT)
        status = interaction.get('status', 'Unknown')
        status_color = COLORS["success"] if status == "Sent" else COLORS["danger"] if status == "Failed" else COLORS["warning"]
        tk.Label(header_row, text=status, 
                font=("Segoe UI", 9), bg=COLORS["light"], fg=status_color).pack(side=tk.LEFT, padx=(10, 0))
        timestamp = interaction.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %I:%M %p")
            except:
                time_str = timestamp
        else:
            time_str = "Unknown time"
        tk.Label(header_row, text=time_str, 
                font=("Segoe UI", 8), bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT)
        message = interaction.get('message', '')
        if message:
            message_preview = message[:100] + "..." if len(message) > 100 else message
            tk.Label(inner, text=message_preview, 
                    font=("Segoe UI", 9), bg=COLORS["light"], 
                    anchor="w", justify="left", wraplength=800).pack(fill=tk.X)
    
    def cancel_installation(self, customer):
        try:
            if messagebox.askyesno("Cancel Installation", 
                                 f"Cancel installation for {customer.get('name')}?\n\n"
                                 f"This will move them back to Pending Sold status."):
                customer['status'] = 'pending_sold'
                if 'sales_info' in customer:
                    customer['sales_info']['install_date'] = ""
                    customer['sales_info']['install_week'] = ""
                    if customer['sales_info'].get('purchased_equipment'):
                        customer['sales_info']['equipment_wanted'] = customer['sales_info']['purchased_equipment']
                        customer['sales_info']['purchased_equipment'] = ""
                self.add_customer_note(customer, "Installation canceled - moved back to Pending Sold")
                self.save_all_data()
                self.log(f"Installation canceled for {customer.get('name')}")
                messagebox.showinfo("Installation Canceled", 
                                  f"{customer.get('name')} moved back to Pending Sold")
                if getattr(self, 'current_tab', 0) == 4:
                    self.refresh_sold_installed_tab()
        except Exception as e:
            print(f"Error canceling installation: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to cancel installation: {str(e)}")
    
    def mark_as_pending_sold(self, customer):
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Mark as Pending Sold - {customer.get('name')}")
            dialog.geometry("500x300")
            dialog.configure(bg=COLORS["bg"])
            tk.Label(dialog, text=f"What equipment does {customer.get('name')} want?", 
                    font=("Segoe UI", 12, "bold"), bg=COLORS["bg"]).pack(pady=15)
            equipment_text = tk.Text(dialog, height=8, width=50, font=("Segoe UI", 10))
            equipment_text.pack(padx=20, pady=10)
            def save_pending_sold():
                equipment = equipment_text.get("1.0", tk.END).strip()
                if not equipment:
                    messagebox.showerror("Error", "Please enter equipment information")
                    return
                if 'sales_info' not in customer:
                    customer['sales_info'] = {
                        "equipment_wanted": "",
                        "purchased_equipment": "",
                        "pre_tax_amount": 0.0,
                        "commission": 0.0,
                        "install_date": "",
                        "install_week": ""
                    }
                customer['sales_info']['equipment_wanted'] = equipment
                customer['status'] = 'pending_sold'
                self.add_customer_note(customer, f"Equipment Wanted: {equipment}")
                self.save_all_data()
                self.log(f"Customer {customer.get('name')} marked as pending sold")
                messagebox.showinfo("Success", f"{customer.get('name')} marked as Pending Sold!")
                dialog.destroy()
                current_tab = getattr(self, 'current_tab', 0)
                if current_tab == 5:
                    self.refresh_customer_list()
            tk.Button(dialog, text="Save & Mark as Pending Sold", command=save_pending_sold,
                     bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20, pady=10).pack(pady=20)
        except Exception as e:
            print(f"Error marking as pending sold: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to mark as pending sold: {str(e)}")
    
    def mark_as_installed(self, customer):
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Mark as Sold & Installed - {customer.get('name')}")
            dialog.geometry("600x500")
            dialog.configure(bg=COLORS["bg"])
            tk.Label(dialog, text=f"Sale Details for {customer.get('name')}", 
                    font=("Segoe UI", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
            tk.Label(dialog, text="Purchased Equipment:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
            equipment_text = tk.Text(dialog, height=4, width=60, font=("Segoe UI", 10))
            equipment_text.pack(padx=20, pady=5)
            equipment_wanted = customer.get('sales_info', {}).get('equipment_wanted', '')
            if equipment_wanted:
                equipment_text.insert(tk.END, equipment_wanted)
            tk.Label(dialog, text="Pre-Tax, Pre-Install Fee Amount ($):", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
            amount_var = tk.StringVar()
            amount_entry = tk.Entry(dialog, textvariable=amount_var, font=("Segoe UI", 11), width=20)
            amount_entry.pack(anchor=tk.W, padx=20, pady=5)
            tk.Label(dialog, text="Installation Date (YYYY-MM-DD):", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
            date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
            date_entry = tk.Entry(dialog, textvariable=date_var, font=("Segoe UI", 11), width=20)
            date_entry.pack(anchor=tk.W, padx=20, pady=5)
            commission_preview = tk.Label(dialog, text="Commission (18%): $0.00", 
                                         font=("Segoe UI", 12, "bold"), bg=COLORS["bg"], fg=COLORS["success"])
            commission_preview.pack(pady=15)
            def update_commission(*args):
                try:
                    amount = float(amount_var.get() or 0)
                    commission = amount * 0.18
                    commission_preview.config(text=f"Commission (18%): ${commission:,.2f}")
                except:
                    commission_preview.config(text="Commission (18%): $0.00")
            amount_var.trace('w', update_commission)
            def save_installed():
                equipment = equipment_text.get("1.0", tk.END).strip()
                amount_str = amount_var.get().strip()
                install_date = date_var.get().strip()
                if not equipment or not amount_str or not install_date:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return
                try:
                    amount = float(amount_str)
                except:
                    messagebox.showerror("Error", "Invalid amount format")
                    return
                try:
                    date_obj = datetime.strptime(install_date, "%Y-%m-%d")
                    install_week = date_obj.strftime("%Y-W%U")
                except:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                    return
                commission = amount * 0.18
                if 'sales_info' not in customer:
                    customer['sales_info'] = {}
                customer['sales_info']['purchased_equipment'] = equipment
                customer['sales_info']['pre_tax_amount'] = amount
                customer['sales_info']['commission'] = commission
                customer['sales_info']['install_date'] = install_date
                customer['sales_info']['install_week'] = install_week
                customer['status'] = 'sold_installed'
                self.add_customer_note(customer, 
                    f"SOLD & INSTALLED\n"
                    f"Equipment: {equipment}\n"
                    f"Amount: ${amount:,.2f}\n"
                    f"Commission: ${commission:,.2f}\n"
                    f"Install Date: {install_date}")
                self.save_all_data()
                self.log(f"Customer {customer.get('name')} marked as sold & installed")
                messagebox.showinfo("Success", 
                    f"{customer.get('name')} marked as Sold & Installed!\n\n"
                    f"Commission: ${commission:,.2f}")
                dialog.destroy()
                if getattr(self, 'current_tab', 0) == 3:
                    self.refresh_pending_sold_tab()
            tk.Button(dialog, text="Save & Mark as Installed", command=save_installed,
                     bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=30, pady=12).pack(pady=20)
        except Exception as e:
            print(f"Error marking as installed: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to mark as installed: {str(e)}")
    
    def move_to_customer_list(self, customer):
        try:
            if messagebox.askyesno("Move to Customer List", 
                                 f"Move {customer.get('name')} back to Customer List?"):
                customer['status'] = 'active'
                self.save_all_data()
                self.log(f"Customer {customer.get('name')} moved back to customer list")
                messagebox.showinfo("Moved", f"{customer.get('name')} moved to Customer List")
                if getattr(self, 'current_tab', 0) == 3:
                    self.refresh_pending_sold_tab()
        except Exception as e:
            print(f"Error moving to customer list: {e}")
            messagebox.showerror("Error", f"Failed to move customer: {str(e)}")
    
    def quick_add_note(self, customer):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Note - {customer.get('name')}")
        dialog.geometry("500x300")
        dialog.configure(bg=COLORS["bg"])
        tk.Label(dialog, text=f"Add Note for {customer.get('name')}", 
                font=("Segoe UI", 12, "bold"), bg=COLORS["bg"]).pack(pady=15)
        note_text = tk.Text(dialog, height=8, width=50, font=("Segoe UI", 10))
        note_text.pack(padx=20, pady=10)
        def save_note():
            note = note_text.get("1.0", tk.END).strip()
            if not note:
                messagebox.showerror("Error", "Please enter a note")
                return
            if self.add_customer_note(customer, note):
                messagebox.showinfo("Success", "Note added successfully!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add note")
        tk.Button(dialog, text="Save Note", command=save_note,
                 bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=10).pack(pady=20)
    
    def trash_customer(self, customer):
        try:
            customer["status"] = "trashed"
            self.save_all_data()
            self.log(f"Customer {customer.get('name')} moved to trash")
            current_tab = getattr(self, 'current_tab', 0)
            if current_tab == 5:
                self.refresh_customer_list()
            messagebox.showinfo("Hidden", f"{customer.get('name')} has been hidden")
        except Exception as e:
            print(f"Error trashing customer: {e}")
            messagebox.showerror("Error", f"Failed to hide customer: {str(e)}")
    
    def restore_customer(self, customer):
        try:
            customer["status"] = "active"
            self.save_all_data()
            self.log(f"Customer {customer.get('name')} restored from trash")
            self.refresh_trashed_tab()
            messagebox.showinfo("Restored", f"{customer.get('name')} has been restored")
        except Exception as e:
            print(f"Error restoring customer: {e}")
            messagebox.showerror("Error", f"Failed to restore customer: {str(e)}")
    
    def delete_customer_forever(self, customer):
        try:
            if messagebox.askyesno("Delete Forever", 
                                 f"Permanently delete {customer.get('name')}?\n\nThis cannot be undone!"):
                self.data["customers"].remove(customer)
                self.save_all_data()
                self.log(f"Customer {customer.get('name')} deleted permanently")
                self.refresh_trashed_tab()
        except Exception as e:
            print(f"Error deleting customer: {e}")
    
    def quick_sms_customer(self, customer):
        self.send_followup_sms(customer)
    
    def quick_email_customer(self, customer):
        self.send_followup_email(customer)
    
    def send_followup_sms(self, customer):
        try:
            if not customer.get('phone'):
                messagebox.showerror("No Phone", "Customer has no phone number")
                return
            template_name = self.get_appropriate_template()
            message_template = self.presets.get(template_name, "")
            if not message_template:
                messagebox.showerror("No Template", f"No template found: {template_name}")
                return
            name_parts = customer.get('name', '').split(' ', 1)
            firstname = name_parts[0] if name_parts else "there"
            lastname = name_parts[1] if len(name_parts) > 1 else ""
            message = self.format_message(message_template, firstname, lastname)
            if self.send_sms_kde(customer['phone'], message):
                self.log(f"✅ Follow-up SMS sent to {customer.get('name')}")
                self.add_customer_interaction(customer, message, "SMS", "Sent", True)
                self.update_stats(texts_sent=1)
            else:
                self.log(f"❌ Failed to send follow-up SMS to {customer.get('name')}")
                self.add_customer_interaction(customer, message, "SMS", "Failed", True)
        except Exception as e:
            print(f"Error sending follow-up SMS: {e}")
            messagebox.showerror("Error", f"Failed to send SMS: {str(e)}")
    
    def send_followup_email(self, customer):
        try:
            if not customer.get('email'):
                messagebox.showerror("No Email", "Customer has no email address")
                return
            email_dialog = tk.Toplevel(self.root)
            email_dialog.title("Send Follow-up Email")
            email_dialog.geometry("600x400")
            email_dialog.configure(bg=COLORS["bg"])
            tk.Label(email_dialog, text=f"Send email to: {customer.get('name')} ({customer.get('email')})",
                    font=("Segoe UI", 12, "bold"), bg=COLORS["bg"]).pack(pady=10)
            tk.Label(email_dialog, text="Subject:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20)
            subject_var = tk.StringVar(value="Follow-up from Culligan")
            tk.Entry(email_dialog, textvariable=subject_var, font=("Segoe UI", 10), width=70).pack(padx=20, pady=5)
            tk.Label(email_dialog, text="Message:", font=("Segoe UI", 10), bg=COLORS["bg"]).pack(anchor=tk.W, padx=20, pady=(10, 0))
            message_text = tk.Text(email_dialog, height=10, width=70, font=("Segoe UI", 10))
            message_text.pack(padx=20, pady=5)
            name_parts = customer.get('name', '').split(' ', 1)
            firstname = name_parts[0] if name_parts else "there"
            default_message = f"Hi {firstname},\n\nI wanted to follow up on your water inquiry. How are things going?\n\nBest regards,\nKodi\nCulligan"
            message_text.insert(tk.END, default_message)
            def send_email():
                subject = subject_var.get()
                message = message_text.get("1.0", tk.END).strip()
                if self.send_email_reply(customer['email'], firstname, "", subject, message):
                    self.log(f"✅ Follow-up email sent to {customer.get('name')}")
                    self.add_customer_interaction(customer, message, "Email", "Sent", True)
                    self.update_stats(email_responses=1)
                    email_dialog.destroy()
                else:
                    messagebox.showerror("Failed", "Failed to send email")
            btn_frame = tk.Frame(email_dialog, bg=COLORS["bg"])
            btn_frame.pack(pady=20)
            tk.Button(btn_frame, text="Send Email", command=send_email,
                     bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20, pady=10).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Cancel", command=email_dialog.destroy,
                     bg=COLORS["danger"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20, pady=10).pack(side=tk.LEFT)
        except Exception as e:
            print(f"Error sending follow-up email: {e}")
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
    
    def view_customer_history(self, customer):
        try:
            history_window = tk.Toplevel(self.root)
            history_window.title(f"Customer History - {customer.get('name')}")
            history_window.geometry("800x600")
            history_window.configure(bg=COLORS["bg"])
            header = tk.Frame(history_window, bg=COLORS["primary"])
            header.pack(fill=tk.X)
            tk.Label(header, text=customer.get('name', 'Unknown'), 
                    font=("Segoe UI", 16, "bold"), bg=COLORS["primary"], fg="white").pack(pady=15)
            contact_info = []
            if customer.get('phone'):
                contact_info.append(f"📞 {customer['phone']}")
            if customer.get('email'):
                contact_info.append(f"📧 {customer['email']}")
            tk.Label(header, text=" | ".join(contact_info), 
                    font=("Segoe UI", 11), bg=COLORS["primary"], fg=COLORS["light"]).pack(pady=(0, 15))
            canvas = tk.Canvas(history_window, bg=COLORS["bg"])
            scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=COLORS["bg"])
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)
            interactions = customer.get('interactions', [])
            notes = customer.get('notes', [])
            if notes:
                notes_header = tk.Label(scrollable_frame, text="📝 Notes", 
                                       font=("Segoe UI", 14, "bold"),
                                       bg=COLORS["bg"], fg=COLORS["primary"])
                notes_header.pack(anchor=tk.W, pady=(10, 5))
                for note in reversed(notes):
                    note_card = tk.Frame(scrollable_frame, bg=COLORS["warning"], relief="solid", bd=1)
                    note_card.pack(fill=tk.X, pady=3)
                    note_inner = tk.Frame(note_card, bg=COLORS["warning"])
                    note_inner.pack(fill=tk.X, padx=10, pady=8)
                    timestamp = note.get('timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%Y-%m-%d %I:%M %p")
                        except:
                            time_str = timestamp
                    else:
                        time_str = "Unknown time"
                    tk.Label(note_inner, text=f"📝 {time_str}", 
                            font=("Segoe UI", 9), bg=COLORS["warning"], fg=COLORS["dark"]).pack(anchor=tk.W)
                    tk.Label(note_inner, text=note.get('text', ''), 
                            font=("Segoe UI", 10), bg=COLORS["warning"], fg=COLORS["dark"],
                            anchor="w", justify="left", wraplength=700).pack(anchor=tk.W)
            if interactions:
                interactions_header = tk.Label(scrollable_frame, text="💬 Interactions", 
                                              font=("Segoe UI", 14, "bold"),
                                              bg=COLORS["bg"], fg=COLORS["primary"])
                interactions_header.pack(anchor=tk.W, pady=(20, 5))
                for interaction in reversed(interactions):
                    self.create_interaction_card(scrollable_frame, interaction)
            if not interactions and not notes:
                tk.Label(scrollable_frame, text="No interactions or notes yet", 
                        font=("Segoe UI", 12), bg=COLORS["bg"], fg=COLORS["text_light"]).pack(pady=50)
        except Exception as e:
            print(f"Error showing customer history: {e}")
            messagebox.showerror("Error", f"Failed to show history: {str(e)}")
    
    def create_interaction_card(self, parent, interaction):
        card = tk.Frame(parent, bg=COLORS["card"], relief="solid", bd=1)
        card.pack(fill=tk.X, pady=5)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=15, pady=10)
        header_row = tk.Frame(inner, bg=COLORS["card"])
        header_row.pack(fill=tk.X, pady=(0, 8))
        direction = "→" if interaction.get('is_outbound') else "←" 
        direction_color = COLORS["primary"] if interaction.get('is_outbound') else COLORS["success"]
        tk.Label(header_row, text=f"{direction} {interaction.get('type', 'Message')}", 
                font=("Segoe UI", 11, "bold"), bg=COLORS["card"], fg=direction_color).pack(side=tk.LEFT)
        status = interaction.get('status', 'Unknown')
        status_color = COLORS["success"] if status == "Sent" else COLORS["danger"] if status == "Failed" else COLORS["warning"]
        tk.Label(header_row, text=status, 
                font=("Segoe UI", 10), bg=COLORS["card"], fg=status_color).pack(side=tk.LEFT, padx=(10, 0))
        timestamp = interaction.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %I:%M %p")
            except:
                time_str = timestamp
        else:
            time_str = "Unknown time"
        tk.Label(header_row, text=time_str, 
                font=("Segoe UI", 9), bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.RIGHT)
        message = interaction.get('message', '')
        if message:
            message_label = tk.Label(inner, text=message, 
                                   font=("Segoe UI", 10), bg=COLORS["card"], 
                                   anchor="w", justify="left", wraplength=700)
            message_label.pack(fill=tk.X)
    
    def refresh_pending_queue(self):
        try:
            for widget in self.pending_scrollable_frame.winfo_children():
                widget.destroy()
            self.pending_count_label.config(text=f"{len(self.pending_texts)} pending")
            if not self.pending_texts:
                no_pending = tk.Frame(self.pending_scrollable_frame, bg=COLORS["card"])
                no_pending.pack(fill=tk.BOTH, expand=True, pady=100)
                tk.Label(no_pending, text="📭", font=("Segoe UI", 48),
                        bg=COLORS["card"]).pack()
                tk.Label(no_pending, text="No pending approvals", 
                        font=("Segoe UI", 16, "bold"),
                        bg=COLORS["card"], fg=COLORS["text_light"]).pack()
                tk.Label(no_pending, text="New leads will appear here for manual approval", 
                        font=("Segoe UI", 12),
                        bg=COLORS["card"], fg=COLORS["text_light"]).pack()
                return
            for lead_data in list(self.pending_texts):
                self.create_pending_approval_card(lead_data)
        except Exception as e:
            print(f"Error refreshing pending queue: {e}")
    
    def create_pending_approval_card(self, lead_data):
        card = ModernCard(self.pending_scrollable_frame)
        card.pack(fill=tk.X, pady=10)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill=tk.X, padx=20, pady=15)
        header = tk.Frame(inner, bg=COLORS["card"])
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text=lead_data['full_name'], 
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["card"]).pack(side=tk.LEFT)
        tk.Label(header, text=lead_data['phone'], 
                font=("Segoe UI", 11),
                bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=15)
        message_frame = tk.Frame(inner, bg=COLORS["light"], relief="solid", bd=1)
        message_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(message_frame, text=lead_data.get('message', ''), 
                font=("Segoe UI", 11), bg=COLORS["light"], fg=COLORS["dark"],
                anchor="w", justify="left", wraplength=800).pack(padx=15, pady=12, fill=tk.X)
        button_frame = tk.Frame(inner, bg=COLORS["card"])
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="✅ Approve & Send", 
                 command=lambda: self.approve_pending_text(lead_data, card),
                 bg=COLORS["success"], fg="white", relief="flat",
                 font=("Segoe UI", 11, "bold"), padx=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="✏️ Edit Message", 
                 command=lambda: self.edit_pending_message(lead_data, card),
                 bg=COLORS["warning"], fg="white", relief="flat",
                 font=("Segoe UI", 11, "bold"), padx=20).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="❌ Reject", 
                 command=lambda: self.reject_pending_text(lead_data, card),
                 bg=COLORS["danger"], fg="white", relief="flat",
                 font=("Segoe UI", 11, "bold"), padx=20).pack(side=tk.RIGHT)
    
    def approve_pending_text(self, lead_data, card):
        try:
            if self.send_sms_kde(lead_data['phone'], lead_data['message']):
                self.log(f"✅ Text sent to {lead_data['full_name']}")
                self.add_customer_interaction(lead_data, lead_data['message'], "SMS", "Sent", True)
                self.update_stats(texts_sent=1)
                self.processed_emails.add(lead_data['email_id'])
                self.save_all_data()
            else:
                self.log(f"❌ Failed to send text to {lead_data['full_name']}")
                self.add_customer_interaction(lead_data, lead_data['message'], "SMS", "Failed", True)
            self.pending_texts.remove(lead_data)
            self.refresh_pending_queue()
        except Exception as e:
            print(f"Error approving text: {e}")
    
    def edit_pending_message(self, lead_data, card):
        try:
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title("Edit Message")
            edit_dialog.geometry("500x300")
            edit_dialog.configure(bg=COLORS["bg"])
            tk.Label(edit_dialog, text=f"Edit message for {lead_data['full_name']}:",
                    font=("Segoe UI", 12, "bold"), bg=COLORS["bg"]).pack(pady=10)
            message_text = tk.Text(edit_dialog, height=8, width=60, font=("Segoe UI", 10))
            message_text.pack(padx=20, pady=10)
            message_text.insert(tk.END, lead_data.get('message', ''))
            def save_and_send():
                new_message = message_text.get("1.0", tk.END).strip()
                lead_data['message'] = new_message
                edit_dialog.destroy()
                self.approve_pending_text(lead_data, card)
            def save_only():
                new_message = message_text.get("1.0", tk.END).strip()
                lead_data['message'] = new_message
                edit_dialog.destroy()
                self.refresh_pending_queue()
            btn_frame = tk.Frame(edit_dialog, bg=COLORS["bg"])
            btn_frame.pack(pady=20)
            tk.Button(btn_frame, text="Save & Send", command=save_and_send,
                     bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Save Only", command=save_only,
                     bg=COLORS["warning"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Cancel", command=edit_dialog.destroy,
                     bg=COLORS["danger"], fg="white", font=("Segoe UI", 10, "bold"),
                     padx=20).pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error editing message: {e}")
    
    def reject_pending_text(self, lead_data, card):
        try:
            if messagebox.askyesno("Reject", f"Reject text for {lead_data['full_name']}?"):
                self.log(f"❌ Text rejected for {lead_data['full_name']}")
                self.add_customer_interaction(lead_data, lead_data['message'], "SMS", "Rejected", True)
                self.processed_emails.add(lead_data['email_id'])
                self.pending_texts.remove(lead_data)
                self.save_all_data()
                self.refresh_pending_queue()
        except Exception as e:
            print(f"Error rejecting text: {e}")
    
    def get_appropriate_template(self, priority="normal"):
        try:
            business_hours = self.config.get("business_hours", {})
            if business_hours.get("enabled", False):
                now = datetime.now().time()
                try:
                    start = datetime.strptime(business_hours.get("start", "09:00"), "%H:%M").time()
                    end = datetime.strptime(business_hours.get("end", "17:00"), "%H:%M").time()
                    if not (start <= now <= end):
                        if "After Hours" in self.presets:
                            self.log(f"Using after hours template")
                            return "After Hours"
                except:
                    pass
            active_preset = self.config.get("active_preset")
            self.log(f"Using active preset: '{active_preset}'")
            self.log(f"Available presets: {list(self.presets.keys())}")
            return active_preset
        except Exception as e:
            print(f"Error getting template: {e}")
            return self.config.get("active_preset")
    
    def parse_customer_name(self, full_name):
        try:
            if not full_name:
                return "Customer", ""
            parts = full_name.strip().split()
            if len(parts) == 0:
                return "Customer", ""
            elif len(parts) == 1:
                return parts[0], ""
            else:
                return parts[0], " ".join(parts[1:])
        except:
            return "Customer", ""
    
    def extract_customer_name(self, text):
        try:
            if not text:
                return None
            if "Name:" in text:
                self.log(f"Found 'Name:' in text, searching for customer name...")
            patterns = [
                r'\*\*Name:\*\*\s*\n?\s*([A-Za-z][A-Za-z\s\.\-\']+?)(?:\s*\n|\s*\*\*|\s*$)',
                r'Name:\s*\n?\s*([A-Za-z][A-Za-z\s\.\-\']+?)(?:\s*\n|\s*\*\*|\s*$)',
                r'Name:\s*\t\s*([A-Za-z][A-Za-z\s\.\-\']+?)\s*\t',
                r'Name:\s*\t\s*([A-Za-z][A-Za-z\s\.\-\']+?)(?:\s*\t|\s*\r|\s*\n)',
                r'Name:\s*([^\t\r\n]+)'
            ]
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    name = match.group(1).strip()
                    name = ' '.join(name.split())
                    self.log(f"Name pattern {i+1} matched: '{name}'")
                    if name and len(name) > 1 and not name.isdigit():
                        self.log(f"Valid name found: '{name}'")
                        return name
                    else:
                        self.log(f"Invalid name rejected: '{name}'")
            self.log("No name pattern matched")
            return None
        except Exception as e:
            print(f"Error extracting name: {e}")
            return None
    
    def extract_phone_number(self, text):
        try:
            if not text:
                return None
            if "Phone:" in text:
                self.log(f"Found 'Phone:' in text, searching for number...")
            patterns = [
                r'\*\*Phone:\*\*\s*\(?(\d{3})\)?\s*[-\.\s]?(\d{3})[-\.\s]?(\d{4})',
                r'Phone:\s*\(?(\d{3})\)?\s*[-\.\s]?(\d{3})[-\.\s]?(\d{4})',
                r'Phone:\s*\n?\s*\(?(\d{3})\)?\s*[-\.\s]?(\d{3})[-\.\s]?(\d{4})',
                r'Phone:.*?\(?(\d{3})\)?\s*[-\.\s]?(\d{3})[-\.\s]?(\d{4})',
                r'Phone:\s*\t?\s*(\d{10,11})'
            ]
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    self.log(f"Phone pattern {i+1} matched: {match.group(0)}")
                    if len(match.groups()) >= 3:
                        phone = match.group(1) + match.group(2) + match.group(3)
                    else:
                        phone = match.group(1)
                    phone = re.sub(r'\D', '', phone)
                    self.log(f"Cleaned phone number: '{phone}' (length: {len(phone)})")
                    if len(phone) == 11 and phone.startswith('1'):
                        result = phone[1:]
                        self.log(f"Removed leading 1, returning: {result}")
                        return result
                    elif len(phone) == 10:
                        self.log(f"10-digit phone, returning: {phone}")
                        return phone
                    else:
                        self.log(f"Invalid phone length: {len(phone)}")
            self.log("No phone number pattern matched")
            return None
        except Exception as e:
            print(f"Error extracting phone: {e}")
            return None
    
    def extract_email_address(self, text):
        try:
            if not text:
                return None
            patterns = [
                r'Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'Email:\s*([^\s\t\r\n]+@[^\s\t\r\n]+)',
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    email = match.group(1).strip()
                    if '@' in email and '.' in email.split('@')[1]:
                        return email
            return None
        except Exception as e:
            print(f"Error extracting email: {e}")
            return None
    
    def format_message(self, template, firstname, lastname):
        try:
            message = template.replace("{firstname}", firstname)
            message = message.replace("{lastname}", lastname)
            message = message.replace("{fullname}", f"{firstname} {lastname}".strip())
            return message
        except Exception as e:
            print(f"Error formatting message: {e}")
            return template
    
    def toggle_monitoring(self):
        if not self.monitoring:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        if not self.config.get("kde_device_id"):
            messagebox.showerror("Setup Required", 
                               "Please configure KDE Connect Device ID in Settings tab")
            self.switch_tab(9)
            return
        if not self.config.get("active_preset"):
            messagebox.showerror("Template Required",
                               "Please select an active SMS template in Settings tab")
            self.switch_tab(9)
            return
        try:
            self.get_outlook_connection()
        except Exception as e:
            messagebox.showerror("Outlook Error", 
                               f"Cannot connect to Outlook.\nMake sure Outlook is running.\n\nError: {str(e)}")
            return
        self.monitoring = True
        self.monitor_status_canvas.delete("all")
        self.monitor_status_canvas.create_oval(2, 2, 22, 22, fill=COLORS["success"], outline="")
        self.monitor_status_text.config(text="Scanning", fg=COLORS["success"])
        self.sidebar_status_canvas.delete("all")
        self.sidebar_status_canvas.create_oval(2, 2, 18, 18, fill=COLORS["success"], outline="")
        self.sidebar_status_label.config(text="Online")
        if hasattr(self, 'monitor_toggle_btn'):
            self.monitor_toggle_btn.update_text("Stop Scanning")
            self.monitor_toggle_btn.icon = "⏸️"
            self.monitor_toggle_btn.bg_color = COLORS["danger"]
            self.monitor_toggle_btn.hover_color = "#C0392B"
            self.monitor_toggle_btn.itemconfig(self.monitor_toggle_btn.rect, fill=COLORS["danger"])
            self.monitor_toggle_btn.itemconfig(self.monitor_toggle_btn.text_item, text="⏸️ Stop Scanning")
        if hasattr(self, 'dashboard_toggle_btn'):
            self.dashboard_toggle_btn.update_text("Stop Scanning")
            self.dashboard_toggle_btn.icon = "⏸️"
            self.dashboard_toggle_btn.bg_color = COLORS["danger"]
            self.dashboard_toggle_btn.hover_color = "#C0392B"
            self.dashboard_toggle_btn.itemconfig(self.dashboard_toggle_btn.rect, fill=COLORS["danger"])
            self.dashboard_toggle_btn.itemconfig(self.dashboard_toggle_btn.text_item, text="⏸️ Stop Scanning")
        scan_interval = self.config.get("scan_interval", 300)
        self.log("="*60)
        self.log("✅ Periodic scanning started")
        self.log(f"Mode: {'Auto-Send' if self.config.get('auto_send') else 'Manual Approval'}")
        self.log(f"Template: {self.config.get('active_preset')}")
        self.log(f"Scan interval: {scan_interval} seconds ({scan_interval/60:.1f} minutes)")
        self.log("="*60)
        self.schedule_next_scan()
    
    def stop_scanning(self):
        self.monitoring = False
        self.monitor_status_canvas.delete("all")
        self.monitor_status_canvas.create_oval(2, 2, 22, 22, fill=COLORS["danger"], outline="")
        self.monitor_status_text.config(text="Stopped", fg=COLORS["danger"])
        self.sidebar_status_canvas.delete("all")
        self.sidebar_status_canvas.create_oval(2, 2, 18, 18, fill=COLORS["danger"], outline="")
        self.sidebar_status_label.config(text="Offline")
        if hasattr(self, 'monitor_toggle_btn'):
            self.monitor_toggle_btn.update_text("Start Scanning")
            self.monitor_toggle_btn.icon = "▶️"
            self.monitor_toggle_btn.bg_color = COLORS["success"]
            self.monitor_toggle_btn.hover_color = COLORS["accent"]
            self.monitor_toggle_btn.itemconfig(self.monitor_toggle_btn.rect, fill=COLORS["success"])
            self.monitor_toggle_btn.itemconfig(self.monitor_toggle_btn.text_item, text="▶️ Start Scanning")
        if hasattr(self, 'dashboard_toggle_btn'):
            self.dashboard_toggle_btn.update_text("Start Scanning")
            self.dashboard_toggle_btn.icon = "▶️"
            self.dashboard_toggle_btn.bg_color = COLORS["success"]
            self.dashboard_toggle_btn.hover_color = COLORS["accent"]
            self.dashboard_toggle_btn.itemconfig(self.dashboard_toggle_btn.rect, fill=COLORS["success"])
            self.dashboard_toggle_btn.itemconfig(self.dashboard_toggle_btn.text_item, text="▶️ Start Scanning")
        self.log("⏹️ Periodic scanning stopped")
        self.log(f"Session: {self.session_emails_processed} leads, {self.session_texts_sent} texts")
    
    def schedule_next_scan(self):
        if self.monitoring:
            scan_interval = self.config.get("scan_interval", 300) * 1000
            self.root.after(scan_interval, self.perform_scan)
    
    def perform_scan(self):
        if not self.monitoring:
            return
        try:
            self.log("🔄 Performing scheduled scan...")
            self.run_periodic_scan()
            self.schedule_next_scan()
        except Exception as e:
            self.log(f"❌ Error in scheduled scan: {e}")
            self.schedule_next_scan()
    
    def run_manual_scan(self):
        self.log("🔍 Starting manual scan...")
        self.run_periodic_scan()
    
    def run_periodic_scan(self):
        def scan_thread():
            try:
                inbox = self.get_outlook_connection()
                messages = inbox.Items
                messages.Sort("[ReceivedTime]", True)
                catchup_hours = self.config.get('catchup_hours', 24)
                cutoff_time = datetime.now() - timedelta(hours=catchup_hours)
                count = 0
                found = 0
                processed_for_pending = 0
                keywords = self.config.get("email_keywords", [])
                auto_send = self.config.get("auto_send", False)
                for message in messages:
                    try:
                        received_time = message.ReceivedTime
                        if hasattr(received_time, 'timestamp'):
                            received_dt = datetime.fromtimestamp(received_time.timestamp())
                        else:
                            received_dt = received_time
                        if received_dt < cutoff_time:
                            break
                        count += 1
                        email_id = message.EntryID
                        if email_id in self.processed_emails:
                            continue
                        subject_lower = message.Subject.lower()
                        is_customer_email = any(keyword.lower() in subject_lower for keyword in keywords)
                        if is_customer_email:
                            found += 1
                            full_name = self.extract_customer_name(message.Body)
                            phone = self.extract_phone_number(message.Body)
                            email_addr = self.extract_email_address(message.Body)
                            if not full_name:
                                self.log(f"❌ Skipping: No customer name found")
                            elif not phone and not email_addr:
                                self.log(f"❌ Skipping: No contact info found for {full_name}")
                            else:
                                if self.check_customer_exists(phone, email_addr):
                                    self.log(f"⚠️ Skipping: Customer {full_name} already exists in database")
                                    self.processed_emails.add(email_id)
                                    continue
                                self.log(f"[NEW LEAD] {full_name} - Phone: {phone or 'None'}, Email: {email_addr or 'None'}")
                                firstname, lastname = self.parse_customer_name(full_name)
                                customer_data = {
                                    'email_id': email_id,
                                    'full_name': full_name,
                                    'firstname': firstname,
                                    'lastname': lastname,
                                    'phone': phone or '',
                                    'email': email_addr or '',
                                    'priority': 'normal'
                                }
                                self.play_notification_sound()
                                if phone:
                                    template_name = self.get_appropriate_template()
                                    message_template = self.presets.get(template_name, "")
                                    if not message_template:
                                        self.log(f"❌ Skipping: No message template found for '{template_name}'")
                                    else:
                                        sms_message = self.format_message(message_template, firstname, lastname)
                                        customer_data['message'] = sms_message
                                        if auto_send:
                                            self.log("Auto-send mode: attempting to send SMS")
                                            if self.send_sms_kde(phone, sms_message):
                                                self.log(f"✅ Text sent automatically!")
                                                self.add_customer_interaction(customer_data, sms_message, "SMS", "Sent", True)
                                                self.update_stats(texts_sent=1, emails_processed=1)
                                            else:
                                                self.log(f"❌ Failed to send text")
                                                self.add_customer_interaction(customer_data, sms_message, "SMS", "Failed", True)
                                        else:
                                            self.log(f"Manual mode: adding to pending queue")
                                            try:
                                                already_pending = False
                                                for pending_item in self.pending_texts:
                                                    if (phone and pending_item.get('phone') == phone) or \
                                                       (email_addr and pending_item.get('email') == email_addr):
                                                        already_pending = True
                                                        self.log(f"⚠️ Skipping: {full_name} already in pending queue")
                                                        break
                                                if not already_pending:
                                                    self.pending_texts.append(customer_data)
                                                    self.update_stats(emails_processed=1)
                                                    processed_for_pending += 1
                                                    self.log(f"✅ Successfully added {full_name} to pending queue")
                                                    self.add_customer_interaction(customer_data, f"[PENDING] {sms_message}", "SMS", "Pending", True)
                                                self.processed_emails.add(email_id)
                                            except Exception as pending_error:
                                                self.log(f"❌ Error adding to pending: {pending_error}")
                                elif email_addr:
                                    self.log(f"Email-only customer: {full_name} ({email_addr})")
                                    self.add_customer_interaction(customer_data, "New email lead", "Email", "Received", False)
                                    self.update_stats(emails_processed=1)
                                    self.processed_emails.add(email_id)
                            if email_id not in self.processed_emails:
                                self.processed_emails.add(email_id)
                    except Exception as msg_error:
                        self.log(f"Error processing message: {msg_error}")
                        continue
                self.save_all_data()
                if found > 0:
                    self.log(f"✅ Scan complete: {count} checked, {found} found, {processed_for_pending} added to pending")
                    if getattr(self, 'current_tab', 0) == 2:
                        self.root.after(500, self.refresh_pending_queue)
                else:
                    self.log(f"Scan complete: {count} checked, no new leads")
            except Exception as e:
                self.log(f"❌ Scan error: {e}")
                traceback.print_exc()
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def get_outlook_connection(self):
        try:
            if self.outlook is not None:
                try:
                    _ = self.outlook.Version
                except:
                    self.outlook = None
                    self.outlook_inbox = None
            if self.outlook is None:
                self.log("Connecting to Outlook...")
                self.outlook = win32com.client.Dispatch("Outlook.Application")
                self.log(f"Outlook version: {self.outlook.Version}")
            if self.outlook_inbox is None:
                namespace = self.outlook.GetNamespace("MAPI")
                if namespace.Stores.Count == 0:
                    raise Exception("Outlook is not logged in to any account")
                self.outlook_inbox = namespace.GetDefaultFolder(6)
                folder_name = self.outlook_inbox.Name
                item_count = self.outlook_inbox.Items.Count
                self.log(f"Connected to folder: {folder_name} ({item_count} items)")
            return self.outlook_inbox
        except Exception as e:
            error_msg = str(e)
            self.log(f"Outlook connection failed: {error_msg}")
            self.outlook = None
            self.outlook_inbox = None
            if "outlook" in error_msg.lower() or "application" in error_msg.lower():
                raise Exception("Outlook is not running or not installed. Please start Outlook first.")
            elif "mapi" in error_msg.lower() or "namespace" in error_msg.lower():
                raise Exception("Outlook MAPI error. Try restarting Outlook.")
            elif "logged in" in error_msg.lower():
                raise Exception("Outlook is not logged in. Please log in to your email account.")
            elif "items" in error_msg.lower():
                raise Exception("Cannot access Outlook inbox. Check Outlook permissions or try restarting Outlook.")
            else:
                raise Exception(f"Outlook connection error: {error_msg}")
    
    def send_sms_kde(self, phone, message):
        try:
            device_id = self.config.get("kde_device_id")
            if not device_id:
                print("No KDE Connect device ID configured")
                return False
            cmd = [
                "kdeconnect-cli",
                "--device", device_id,
                "--send-sms", message,
                "--destination", phone
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True
            else:
                print(f"KDE Connect error: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("SMS send timeout")
            return False
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_email_reply(self, email, firstname, lastname, subject=None, body=None):
        try:
            if not subject:
                subject = self.email_templates.get("Default Reply", {}).get("subject", "Re: Your Water Inquiry")
            if not body:
                body_template = self.email_templates.get("Default Reply", {}).get("body", "")
                if body_template:
                    body = self.format_message(body_template, firstname, lastname)
                else:
                    body = f"Hi {firstname},\n\nThank you for your inquiry. I'll be in touch soon.\n\nBest regards,\nKodi\nCulligan"
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = email
            mail.Subject = subject
            mail.Body = body
            from_email = self.config.get("from_email")
            if from_email:
                mail.SentOnBehalfOfName = from_email
            mail.Send()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def play_notification_sound(self):
        try:
            if self.config.get("sound_enabled", True):
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def update_ui_loop(self):
        try:
            session_text = f"{self.session_emails_processed} leads • {self.session_texts_sent} texts • {self.session_email_responses} emails"
            if hasattr(self, 'session_stats_label'):
                self.session_stats_label.config(text=session_text)
            pending_count = len(self.pending_texts)
            if hasattr(self, 'pending_count_label'):
                self.pending_count_label.config(text=f"{pending_count} pending")
            self.refresh_dashboard_stats()
        except Exception as e:
            pass
        self.root.after(5000, self.update_ui_loop)
    
    def refresh_dashboard_stats(self):
        try:
            if hasattr(self, 'stat_cards'):
                self.stat_cards["emails_processed"].config(text=str(self.stats.get("total_emails_processed", 0)))
                self.stat_cards["texts_sent"].config(text=str(self.stats.get("total_texts_sent", 0)))
                self.stat_cards["email_responses"].config(text=str(self.stats.get("total_email_responses_sent", 0)))
                self.stat_cards["pending_count"].config(text=str(len(self.pending_texts)))
            if hasattr(self, 'crm_stats'):
                total_customers = len([c for c in self.data["customers"] if c.get("status") != "trashed"])
                pending_sold_count = len([c for c in self.data["customers"] if c.get("status") == "pending_sold"])
                sold_installed_count = len([c for c in self.data["customers"] if c.get("status") == "sold_installed"])
                self.crm_stats["total_customers"].config(text=str(total_customers))
                self.crm_stats["pending_sold"].config(text=str(pending_sold_count))
                self.crm_stats["sold_installed"].config(text=str(sold_installed_count))
                self.crm_stats["active_today"].config(text="0")
        except:
            pass
    
    def update_stats(self, texts_sent=0, emails_processed=0, email_responses=0):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in self.stats["daily_stats"]:
                self.stats["daily_stats"][today] = {"texts": 0, "emails": 0, "email_responses": 0}
            self.stats["daily_stats"][today]["texts"] += texts_sent
            self.stats["daily_stats"][today]["emails"] += emails_processed
            self.stats["daily_stats"][today]["email_responses"] += email_responses
            self.stats["total_texts_sent"] += texts_sent
            self.stats["total_emails_processed"] += emails_processed
            self.stats["total_email_responses_sent"] += email_responses
            self.session_texts_sent += texts_sent
            self.session_emails_processed += emails_processed
            self.session_email_responses += email_responses
            self.save_all_data()
            self.refresh_dashboard_stats()
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def on_mode_change(self):
        self.config["auto_send"] = self.auto_send_var.get()
        self.save_all_data()
        mode = "Auto-Send" if self.config["auto_send"] else "Manual Approval"
        self.log(f"Mode changed to: {mode}")
    
    def save_all_settings(self):
        try:
            self.config["kde_device_id"] = self.kde_id_var.get().strip()
            keywords = self.keywords_text.get("1.0", tk.END).strip()
            self.config["email_keywords"] = [k.strip() for k in keywords.split("\n") if k.strip()]
            try:
                interval = int(self.interval_var.get())
                self.config["scan_interval"] = max(60, interval)
            except:
                pass
            if hasattr(self, 'active_preset_var'):
                self.config["active_preset"] = self.active_preset_var.get()
            self.save_all_data()
            messagebox.showinfo("Settings Saved", "All settings have been saved successfully!")
        except Exception as e:
            print(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = AutoEmailer(root)
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        traceback.print_exc()
        try:
            import tkinter.messagebox as mb
            mb.showerror("Application Error", 
                        f"Failed to start Culligan CRM:\n\n{str(e)}\n\nCheck console for details.")
        except:
            pass

if __name__ == "__main__":
    main()
