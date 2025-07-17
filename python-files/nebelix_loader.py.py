
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import datetime
import hashlib
import subprocess
from pathlib import Path
import random
import string

class NebelixLoader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEBELIX CHEATS")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#0d1117')
        
        # Remove standard window decorations
        self.root.overrideredirect(True)
        
        # Center the window
        self.center_window()
        
        # File paths
        self.config_file = "config.json"
        
        # Default configuration
        self.default_config = {
            "applications": [],
            "master_key": self.generate_master_key(),
            "license": {
                "valid": False,
                "expiry": None
            },
            "settings": {
                "autostart": False,
                "tray": True,
                "autoupdate": True,
                "injection": {
                    "method": "manual",
                    "delay": 3000
                }
            }
        }
        
        # For window movement
        self.drag_data = {"x": 0, "y": 0}
        
        # Selected application
        self.selected_app_id = None
        self.editing_app_id = None
        
        self.load_config()
        self.setup_ui()
    
    def center_window(self):
        """Centers the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def generate_master_key(self):
        """Generates a master key for license validation"""
        return hashlib.sha256("NebelixSecretKey2024".encode()).hexdigest()
    
    def load_config(self):
        """Loads configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        """Saves configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ui(self):
        """Creates the modern user interface"""
        # Main frame with modern design
        main_frame = tk.Frame(self.root, bg='#161b22', bd=1, relief='solid')
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Title area with modern header
        title_frame = tk.Frame(main_frame, bg='#21262d', height=60)
        title_frame.pack(fill='x', pady=(0, 0))
        title_frame.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(title_frame, bg='#21262d')
        logo_frame.pack(side='left', padx=15, pady=15)
        
        # Create a simple shield logo
        logo_canvas = tk.Canvas(logo_frame, width=24, height=24, bg='#21262d', 
                               highlightthickness=0)
        logo_canvas.create_polygon(12, 2, 22, 7, 22, 16, 12, 22, 2, 16, 2, 7, 
                                  fill='#58a6ff', outline='#58a6ff')
        logo_canvas.create_oval(9, 8, 15, 14, fill='#21262d', outline='#21262d')
        logo_canvas.create_rectangle(11, 12, 13, 18, fill='#21262d', outline='#21262d')
        logo_canvas.pack(side='left', padx=(0, 10))
        
        title_label = tk.Label(logo_frame, text="NEBELIX CHEATS", font=('Segoe UI', 12, 'bold'), 
                              bg='#21262d', fg='white')
        title_label.pack(side='left')
        
        # Window controls with modern design
        controls_frame = tk.Frame(title_frame, bg='#21262d')
        controls_frame.pack(side='right', padx=15, pady=15)
        
        # Minimize Button
        self.minimize_btn = tk.Button(controls_frame, text="━", command=self.root.iconify,
                                     bg='#30363d', fg='#7d8590', font=('Segoe UI', 10, 'bold'),
                                     relief='flat', width=4, height=1, bd=0,
                                     activebackground='#484f58', activeforeground='#ffffff',
                                     cursor='hand2')
        self.minimize_btn.pack(side='left', padx=(0, 8))
        
        # Close Button
        self.close_btn = tk.Button(controls_frame, text="✕", command=self.root.destroy,
                                  bg='#30363d', fg='#7d8590', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', width=4, height=1, bd=0,
                                  activebackground='#da3633', activeforeground='#ffffff',
                                  cursor='hand2')
        self.close_btn.pack(side='left')
        
        # Drag functionality
        title_frame.bind("<Button-1>", self.start_drag)
        title_frame.bind("<B1-Motion>", self.do_drag)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#161b22')
        content_frame.pack(fill='both', expand=True)
        
        # Split into sidebar and main area
        self.sidebar_frame = tk.Frame(content_frame, bg='#0d1117', width=200)
        self.sidebar_frame.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)
        
        # Main area with tabs
        main_area = tk.Frame(content_frame, bg='#161b22')
        main_area.pack(side='left', fill='both', expand=True)
        
        # Create sidebar content
        self.create_sidebar()
        
        # Create tabs
        self.create_tabs(main_area)
    
    def create_sidebar(self):
        """Creates the sidebar with license info and app list"""
        # License status
        license_frame = tk.Frame(self.sidebar_frame, bg='#0d1117', padx=10, pady=10)
        license_frame.pack(fill='x')
        
        # License status display
        self.license_status_frame = tk.Frame(license_frame, bg='#da3633', bd=0, padx=10, pady=8)
        self.license_status_frame.pack(fill='x')
        
        self.license_status_label = tk.Label(self.license_status_frame, text="License: Invalid",
                                           font=('Segoe UI', 9), bg='#da3633', fg='white')
        self.license_status_label.pack()
        
        self.license_expiry_label = tk.Label(license_frame, text="No active license",
                                           font=('Segoe UI', 8), bg='#0d1117', fg='#8b949e')
        self.license_expiry_label.pack(pady=(5, 0))
        
        # Applications section
        apps_label_frame = tk.Frame(self.sidebar_frame, bg='#0d1117', padx=10, pady=(20, 5))
        apps_label_frame.pack(fill='x')
        
        apps_label = tk.Label(apps_label_frame, text="APPLICATIONS", font=('Segoe UI', 8, 'bold'),
                             bg='#0d1117', fg='#8b949e')
        apps_label.pack(anchor='w')
        
        # App list container with scrollbar
        app_list_container = tk.Frame(self.sidebar_frame, bg='#0d1117', padx=10)
        app_list_container.pack(fill='both', expand=True)
        
        # Canvas for scrolling
        self.app_canvas = tk.Canvas(app_list_container, bg='#0d1117', bd=0, 
                                   highlightthickness=0, height=350)
        self.app_canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        app_scrollbar = ttk.Scrollbar(app_list_container, orient='vertical', 
                                     command=self.app_canvas.yview)
        app_scrollbar.pack(side='right', fill='y')
        
        # Configure canvas
        self.app_canvas.configure(yscrollcommand=app_scrollbar.set)
        self.app_canvas.bind('<Configure>', 
                            lambda e: self.app_canvas.configure(scrollregion=self.app_canvas.bbox('all')))
        
        # Frame inside canvas for app list
        self.app_list_frame = tk.Frame(self.app_canvas, bg='#0d1117')
        self.app_canvas.create_window((0, 0), window=self.app_list_frame, anchor='nw', width=180)
        
        # Add application button
        add_app_frame = tk.Frame(self.sidebar_frame, bg='#0d1117', padx=10, pady=10)
        add_app_frame.pack(fill='x', side='bottom')
        
        self.add_app_btn = tk.Button(add_app_frame, text="Add Application", bg='#30363d', fg='white',
                                    font=('Segoe UI', 9), relief='flat', padx=10, pady=5,
                                    activebackground='#484f58', activeforeground='white',
                                    command=lambda: self.open_app_modal(False))
        self.add_app_btn.pack(fill='x')
        
        # Populate app list
        self.render_app_list()
    
    def create_tabs(self, parent):
        """Creates the tab system for the main area"""
        # Tab buttons frame
        tab_frame = tk.Frame(parent, bg='#21262d', height=40)
        tab_frame.pack(fill='x')
        
        # Tab buttons
        self.tabs = {}
        tab_names = ["Dashboard", "Settings", "License"]
        
        for i, name in enumerate(tab_names):
            tab = tk.Frame(tab_frame, bg='#21262d' if i > 0 else '#1c2128', padx=15, pady=10, cursor='hand2')
            tab.pack(side='left')
            
            if i == 0:  # First tab is active by default
                tab_indicator = tk.Frame(tab, bg='#58a6ff', height=2)
                tab_indicator.place(relx=0, rely=0.9, relwidth=1)
            
            tab_label = tk.Label(tab, text=name, font=('Segoe UI', 9), 
                                bg=tab.cget('bg'), fg='white')
            tab_label.pack()
            
            # Store reference and bind click event
            self.tabs[name.lower()] = {"frame": tab, "indicator": tab_indicator if i == 0 else None}
            tab.bind("<Button-1>", lambda e, n=name.lower(): self.switch_tab(n))
            tab_label.bind("<Button-1>", lambda e, n=name.lower(): self.switch_tab(n))
        
        # Content frame for tab contents
        self.tab_content = tk.Frame(parent, bg='#161b22', padx=20, pady=20)
        self.tab_content.pack(fill='both', expand=True)
        
        # Create content for each tab
        self.create_dashboard_tab()
        self.create_settings_tab()
        self.create_license_tab()
        
        # Show dashboard by default
        self.current_tab = "dashboard"
        self.tab_contents["dashboard"].pack(fill='both', expand=True)
    
    def create_dashboard_tab(self):
        """Creates the dashboard tab content"""
        if not hasattr(self, 'tab_contents'):
            self.tab_contents = {}
        
        # Dashboard container
        dashboard = tk.Frame(self.tab_content, bg='#161b22')
        self.tab_contents["dashboard"] = dashboard
        
        # Welcome message
        welcome_frame = tk.Frame(dashboard, bg='#161b22', pady=10)
        welcome_frame.pack(fill='x')
        
        welcome_label = tk.Label(welcome_frame, text="Welcome to Nebelix Cheats", 
                                font=('Segoe UI', 14, 'bold'), bg='#161b22', fg='white')
        welcome_label.pack(anchor='w')
        
        welcome_desc = tk.Label(welcome_frame, text="Select an application from the sidebar to get started.", 
                               font=('Segoe UI', 9), bg='#161b22', fg='#8b949e')
        welcome_desc.pack(anchor='w', pady=(5, 0))
        
        # No app selected message
        self.no_app_frame = tk.Frame(dashboard, bg='#0d1117', padx=20, pady=30, bd=1, 
                                    relief='solid')
        self.no_app_frame.pack(fill='both', expand=True, pady=10)
        
        # Simple app icon
        icon_canvas = tk.Canvas(self.no_app_frame, width=48, height=48, bg='#0d1117', 
                               highlightthickness=0)
        icon_canvas.create_rectangle(10, 10, 38, 38, outline='#8b949e', width=2)
        icon_canvas.create_line(10, 10, 24, 24, 38, 10, fill='#8b949e', width=2)
        icon_canvas.create_line(24, 24, 24, 38, fill='#8b949e', width=2)
        icon_canvas.pack(pady=10)
        
        no_app_label = tk.Label(self.no_app_frame, text="No Application Selected", 
                               font=('Segoe UI', 12, 'bold'), bg='#0d1117', fg='white')
        no_app_label.pack()
        
        no_app_desc = tk.Label(self.no_app_frame, 
                              text="Choose an application from the sidebar or add a new one.", 
                              font=('Segoe UI', 9), bg='#0d1117', fg='#8b949e')
        no_app_desc.pack(pady=(5, 15))
        
        add_app_btn_alt = tk.Button(self.no_app_frame, text="Add Application", bg='#30363d', 
                                   fg='white', font=('Segoe UI', 9), relief='flat', 
                                   padx=15, pady=5, activebackground='#484f58', 
                                   activeforeground='white',
                                   command=lambda: self.open_app_modal(False))
        add_app_btn_alt.pack()
        
        # App details frame (hidden by default)
        self.app_details_frame = tk.Frame(dashboard, bg='#161b22')
        
        # App info section
        app_info_frame = tk.Frame(self.app_details_frame, bg='#0d1117', padx=20, pady=15, bd=1, 
                                 relief='solid')
        app_info_frame.pack(fill='x', pady=(10, 5))
        
        app_info_top = tk.Frame(app_info_frame, bg='#0d1117')
        app_info_top.pack(fill='x', pady=(0, 15))
        
        app_info_left = tk.Frame(app_info_top, bg='#0d1117')
        app_info_left.pack(side='left')
        
        self.app_name_label = tk.Label(app_info_left, text="Application Name", 
                                      font=('Segoe UI', 12, 'bold'), bg='#0d1117', fg='white')
        self.app_name_label.pack(anchor='w')
        
        self.app_path_label = tk.Label(app_info_left, text="Path: C:\\path\\to\\app.exe", 
                                      font=('Segoe UI', 8), bg='#0d1117', fg='#8b949e')
        self.app_path_label.pack(anchor='w')
        
        app_info_right = tk.Frame(app_info_top, bg='#0d1117')
        app_info_right.pack(side='right')
        
        edit_app_btn = tk.Button(app_info_right, text="Edit", bg='#30363d', fg='white',
                                font=('Segoe UI', 8), relief='flat', padx=10, pady=2,
                                activebackground='#484f58', activeforeground='white',
                                command=lambda: self.open_app_modal(True))
        edit_app_btn.pack(side='left', padx=(0, 5))
        
        remove_app_btn = tk.Button(app_info_right, text="Remove", bg='#da3633', fg='white',
                                  font=('Segoe UI', 8), relief='flat', padx=10, pady=2,
                                  activebackground='#f85149', activeforeground='white',
                                  command=self.remove_app)
        remove_app_btn.pack(side='left')
        
        app_info_bottom = tk.Frame(app_info_frame, bg='#0d1117')
        app_info_bottom.pack(fill='x')
        
        status_frame = tk.Frame(app_info_bottom, bg='#0d1117')
        status_frame.pack(side='left')
        
        status_label = tk.Label(status_frame, text="Status:", font=('Segoe UI', 9), 
                               bg='#0d1117', fg='white')
        status_label.pack(side='left')
        
        self.app_status_label = tk.Label(status_frame, text="Ready", font=('Segoe UI', 9), 
                                        bg='#0d1117', fg='#2ea043')
        self.app_status_label.pack(side='left', padx=(5, 0))
        
        launch_frame = tk.Frame(app_info_bottom, bg='#0d1117')
        launch_frame.pack(side='right')
        
        # Loading indicator (hidden by default)
        self.loader_canvas = tk.Canvas(launch_frame, width=20, height=20, bg='#0d1117', 
                                      highlightthickness=0)
        self.loader_canvas.pack(side='left', padx=(0, 10))
        self.create_loader_animation()
        
        launch_btn = tk.Button(launch_frame, text="Launch", bg='#238636', fg='white',
                              font=('Segoe UI', 9), relief='flat', padx=15, pady=5,
                              activebackground='#2ea043', activeforeground='white',
                              command=self.launch_app)
        launch_btn.pack(side='left')
        
        # Cheat options section
        cheat_frame = tk.Frame(self.app_details_frame, bg='#0d1117', padx=20, pady=15, bd=1, 
                              relief='solid')
        cheat_frame.pack(fill='x', pady=(5, 0), expand=True)
        
        cheat_title = tk.Label(cheat_frame, text="Cheat Options", font=('Segoe UI', 12, 'bold'), 
                              bg='#0d1117', fg='white')
        cheat_title.pack(anchor='w', pady=(0, 15))
        
        # Cheat toggles
        cheat_options = ["Aimbot", "ESP", "Wallhack", "Radar"]
        self.cheat_vars = {}
        
        for option in cheat_options:
            option_frame = tk.Frame(cheat_frame, bg='#0d1117', pady=5)
            option_frame.pack(fill='x')
            
            option_label = tk.Label(option_frame, text=option, font=('Segoe UI', 9), 
                                   bg='#0d1117', fg='white')
            option_label.pack(side='left')
            
            # Create toggle variable
            self.cheat_vars[option] = tk.BooleanVar(value=False)
            
            # Custom toggle switch
            toggle_frame = tk.Frame(option_frame, bg='#0d1117')
            toggle_frame.pack(side='right')
            
            toggle_bg = tk.Frame(toggle_frame, width=40, height=20, bg='#21262d', bd=0)
            toggle_bg.pack()
            
            # Make the toggle clickable
            toggle_bg.bind("<Button-1>", lambda e, opt=option: self.toggle_cheat(opt))
            
            # Toggle indicator
            self.cheat_vars[option].indicator = tk.Frame(toggle_bg, width=16, height=16, bg='white', bd=0)
            self.cheat_vars[option].indicator.place(x=2, y=2)
    
    def create_settings_tab(self):
        """Creates the settings tab content"""
        if not hasattr(self, 'tab_contents'):
            self.tab_contents = {}
        
        # Settings container
        settings = tk.Frame(self.tab_content, bg='#161b22')
        self.tab_contents["settings"] = settings
        
        # Title
        settings_title = tk.Label(settings, text="Settings", font=('Segoe UI', 14, 'bold'), 
                                 bg='#161b22', fg='white')
        settings_title.pack(anchor='w', pady=(0, 15))
        
        # General settings section
        general_frame = tk.Frame(settings, bg='#0d1117', padx=20, pady=15, bd=1, relief='solid')
        general_frame.pack(fill='x', pady=(0, 10))
        
        general_title = tk.Label(general_frame, text="General Settings", font=('Segoe UI', 12, 'bold'), 
                                bg='#0d1117', fg='white')
        general_title.pack(anchor='w', pady=(0, 15))
        
        # General settings toggles
        general_options = [
            {"name": "Auto-start with Windows", "var": "autostart"},
            {"name": "Minimize to tray", "var": "tray", "default": True},
            {"name": "Auto-update", "var": "autoupdate", "default": True}
        ]
        
        self.settings_vars = {}
        
        for option in general_options:
            option_frame = tk.Frame(general_frame, bg='#0d1117', pady=8)
            option_frame.pack(fill='x')
            
            option_label = tk.Label(option_frame, text=option["name"], font=('Segoe UI', 9), 
                                   bg='#0d1117', fg='white')
            option_label.pack(side='left')
            
            # Create toggle variable
            default = option.get("default", False)
            self.settings_vars[option["var"]] = tk.BooleanVar(value=default)
            
            # Custom toggle switch
            toggle_frame = tk.Frame(option_frame, bg='#0d1117')
            toggle_frame.pack(side='right')
            
            toggle_bg = tk.Frame(toggle_frame, width=40, height=20, bg='#21262d', bd=0)
            toggle_bg.pack()
            
            # Make the toggle clickable
            toggle_bg.bind("<Button-1>", lambda e, var=option["var"]: self.toggle_setting(var))
            
            # Toggle indicator
            self.settings_vars[option["var"]].indicator = tk.Frame(toggle_bg, width=16, height=16, 
                                                                 bg='white', bd=0)
            
            # Position based on default value
            x_pos = 22 if default else 2
            self.settings_vars[option["var"]].indicator.place(x=x_pos, y=2)
            
            # Update toggle background color based on state
            if default:
                toggle_bg.configure(bg='#238636')
        
        # Advanced settings section
        advanced_frame = tk.Frame(settings, bg='#0d1117', padx=20, pady=15, bd=1, relief='solid')
        advanced_frame.pack(fill='x', expand=True)
        
        advanced_title = tk.Label(advanced_frame, text="Advanced Settings", 
                                 font=('Segoe UI', 12, 'bold'), bg='#0d1117', fg='white')
        advanced_title.pack(anchor='w', pady=(0, 15))
        
        # Injection method
        method_frame = tk.Frame(advanced_frame, bg='#0d1117', pady=8)
        method_frame.pack(fill='x')
        
        method_label = tk.Label(method_frame, text="Injection Method", font=('Segoe UI', 9), 
                               bg='#0d1117', fg='white')
        method_label.pack(anchor='w', pady=(0, 5))
        
        self.injection_method = tk.StringVar(value="manual")
        
        # Custom styled combobox
        method_combo_frame = tk.Frame(method_frame, bg='#0d1117', bd=1, relief='solid')
        method_combo_frame.pack(fill='x')
        
        method_combo = ttk.Combobox(method_combo_frame, textvariable=self.injection_method,
                                   values=["Manual Map", "LoadLibrary", "Remote Thread"],
                                   state="readonly", font=('Segoe UI', 9))
        method_combo.pack(fill='x', padx=1, pady=1)
        
        # Injection delay
        delay_frame = tk.Frame(advanced_frame, bg='#0d1117', pady=8)
        delay_frame.pack(fill='x')
        
        delay_label = tk.Label(delay_frame, text="Injection Delay (ms)", font=('Segoe UI', 9), 
                              bg='#0d1117', fg='white')
        delay_label.pack(anchor='w', pady=(0, 5))
        
        self.injection_delay = tk.StringVar(value="3000")
        
        delay_entry = tk.Entry(delay_frame, textvariable=self.injection_delay, font=('Segoe UI', 9),
                              bg='#0d1117', fg='white', insertbackground='white',
                              relief='solid', bd=1)
        delay_entry.pack(fill='x')
        
        # Save button
        save_frame = tk.Frame(advanced_frame, bg='#0d1117', pady=(15, 0))
        save_frame.pack(fill='x')
        
        save_btn = tk.Button(save_frame, text="Save Settings", bg='#238636', fg='white',
                            font=('Segoe UI', 9), relief='flat', padx=15, pady=5,
                            activebackground='#2ea043', activeforeground='white',
                            command=self.save_settings)
        save_btn.pack(side='left')
    
    def create_license_tab(self):
        """Creates the license tab content"""
        if not hasattr(self, 'tab_contents'):
            self.tab_contents = {}
        
        # License container
        license_tab = tk.Frame(self.tab_content, bg='#161b22')
        self.tab_contents["license"] = license_tab
        
        # Title
        license_title = tk.Label(license_tab, text="License Management", 
                                font=('Segoe UI', 14, 'bold'), bg='#161b22', fg='white')
        license_title.pack(anchor='w', pady=(0, 15))
        
        # License information section
        info_frame = tk.Frame(license_tab, bg='#0d1117', padx=20, pady=15, bd=1, relief='solid')
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_title = tk.Label(info_frame, text="License Information", font=('Segoe UI', 12, 'bold'), 
                             bg='#0d1117', fg='white')
        info_title.pack(anchor='w', pady=(0, 15))
        
        # Status
        status_label_frame = tk.Frame(info_frame, bg='#0d1117', pady=5)
        status_label_frame.pack(fill='x')
        
        status_label = tk.Label(status_label_frame, text="Status", font=('Segoe UI', 9), 
                               bg='#0d1117', fg='white')
        status_label.pack(anchor='w', pady=(0, 5))
        
        self.license_status_detail = tk.Frame(info_frame, bg='#da3633', padx=0, pady=10)
        self.license_status_detail.pack(fill='x')
        
        self.license_status_text = tk.Label(self.license_status_detail, text="Invalid License", 
                                          font=('Segoe UI', 9), bg='#da3633', fg='white')
        self.license_status_text.pack()
        
        # Expiration
        expiry_label_frame = tk.Frame(info_frame, bg='#0d1117', pady=5)
        expiry_label_frame.pack(fill='x', pady=(10, 0))
        
        expiry_label = tk.Label(expiry_label_frame, text="Expiration", font=('Segoe UI', 9), 
                               bg='#0d1117', fg='white')
        expiry_label.pack(anchor='w', pady=(0, 5))
        
        self.license_expiry_detail = tk.Frame(info_frame, bg='#21262d', padx=0, pady=10)
        self.license_expiry_detail.pack(fill='x')
        
        self.license_expiry_text = tk.Label(self.license_expiry_detail, text="No active license", 
                                          font=('Segoe UI', 9), bg='#21262d', fg='white')
        self.license_expiry_text.pack()
        
        # License activation section
        activate_frame = tk.Frame(license_tab, bg='#0d1117', padx=20, pady=15, bd=1, relief='solid')
        activate_frame.pack(fill='x', expand=True)
        
        activate_title = tk.Label(activate_frame, text="Activate License", 
                                 font=('Segoe UI', 12, 'bold'), bg='#0d1117', fg='white')
        activate_title.pack(anchor='w', pady=(0, 15))
        
        # License key input
        key_label_frame = tk.Frame(activate_frame, bg='#0d1117', pady=5)
        key_label_frame.pack(fill='x')
        
        key_label = tk.Label(key_label_frame, text="License Key", font=('Segoe UI', 9), 
                            bg='#0d1117', fg='white')
        key_label.pack(anchor='w', pady=(0, 5))
        
        self.license_key = tk.StringVar()
        
        key_entry = tk.Entry(activate_frame, textvariable=self.license_key, font=('Segoe UI', 9),
                            bg='#0d1117', fg='white', insertbackground='white',
                            relief='solid', bd=1)
        key_entry.pack(fill='x')
        key_entry.insert(0, "XXXX-XXXX-XXXX-XXXX")
        key_entry.bind("<FocusIn>", lambda e: key_entry.selection_range(0, 'end'))
        
        # Activate button
        activate_btn_frame = tk.Frame(activate_frame, bg='#0d1117', pady=(15, 0))
        activate_btn_frame.pack(fill='x')
        
        activate_btn = tk.Button(activate_btn_frame, text="Activate License", bg='#238636', fg='white',
                                font=('Segoe UI', 9), relief='flat', padx=15, pady=5,
                                activebackground='#2ea043', activeforeground='white',
                                command=self.activate_license)
        activate_btn.pack(side='left')
    
    def create_app_modal(self):
        """Creates the modal for adding/editing applications"""
        if hasattr(self, 'app_modal'):
            return
        
        # Modal window
        self.app_modal = tk.Toplevel(self.root)
        self.app_modal.title("Add Application")
        self.app_modal.geometry("400x300")
        self.app_modal.configure(bg='#161b22')
        self.app_modal.resizable(False, False)
        self.app_modal.transient(self.root)
        self.app_modal.withdraw()
        
        # Remove standard window decorations
        self.app_modal.overrideredirect(True)
        
        # Modal header
        header_frame = tk.Frame(self.app_modal, bg='#21262d', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        self.modal_title = tk.Label(header_frame, text="Add Application", font=('Segoe UI', 12, 'bold'),
                                   bg='#21262d', fg='white')
        self.modal_title.pack(side='left', padx=15, pady=15)
        
        close_modal_btn = tk.Button(header_frame, text="✕", command=self.close_app_modal,
                                   bg='#21262d', fg='#8b949e', font=('Segoe UI', 10, 'bold'),
                                   relief='flat', width=3, height=1, bd=0,
                                   activebackground='#da3633', activeforeground='#ffffff')
        close_modal_btn.pack(side='right', padx=15, pady=15)
        
        # Modal content
        content_frame = tk.Frame(self.app_modal, bg='#161b22', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # App name
        name_label = tk.Label(content_frame, text="Application Name", font=('Segoe UI', 9),
                             bg='#161b22', fg='white')
        name_label.pack(anchor='w', pady=(0, 5))
        
        self.app_name_input = tk.Entry(content_frame, font=('Segoe UI', 9), bg='#0d1117', fg='white',
                                      insertbackground='white', relief='solid', bd=1)
        self.app_name_input.pack(fill='x', pady=(0, 10))
        
        # App path
        path_label = tk.Label(content_frame, text="Application Path", font=('Segoe UI', 9),
                             bg='#161b22', fg='white')
        path_label.pack(anchor='w', pady=(0, 5))
        
        path_frame = tk.Frame(content_frame, bg='#161b22')
        path_frame.pack(fill='x', pady=(0, 10))
        
        self.app_path_input = tk.Entry(path_frame, font=('Segoe UI', 9), bg='#0d1117', fg='white',
                                      insertbackground='white', relief='solid', bd=1)
        self.app_path_input.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(path_frame, text="Browse", bg='#30363d', fg='white',
                              font=('Segoe UI', 9), relief='flat', padx=10, pady=0,
                              activebackground='#484f58', activeforeground='white',
                              command=self.browse_file)
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Process name
        process_label = tk.Label(content_frame, text="Process Name", font=('Segoe UI', 9),
                                bg='#161b22', fg='white')
        process_label.pack(anchor='w', pady=(0, 5))
        
        self.app_process_input = tk.Entry(content_frame, font=('Segoe UI', 9), bg='#0d1117', fg='white',
                                         insertbackground='white', relief='solid', bd=1)
        self.app_process_input.pack(fill='x')
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#161b22', pady=15)
        button_frame.pack(fill='x', side='bottom')
        
        cancel_btn = tk.Button(button_frame, text="Cancel", bg='#30363d', fg='white',
                              font=('Segoe UI', 9), relief='flat', padx=15, pady=5,
                              activebackground='#484f58', activeforeground='white',
                              command=self.close_app_modal)
        cancel_btn.pack(side='right')
        
        self.save_app_btn = tk.Button(button_frame, text="Save", bg='#238636', fg='white',
                                     font=('Segoe UI', 9), relief='flat', padx=15, pady=5,
                                     activebackground='#2ea043', activeforeground='white',
                                     command=self.save_app)
        self.save_app_btn.pack(side='right', padx=(0, 10))
    
    def start_drag(self, event):
        """Start window dragging"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def do_drag(self, event):
        """Handle window dragging"""
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        if self.current_tab == tab_name:
            return
        
        # Remove indicator from current tab
        if self.tabs[self.current_tab].get("indicator"):
            self.tabs[self.current_tab]["indicator"].destroy()
            self.tabs[self.current_tab]["indicator"] = None
        
        # Update tab styles
        self.tabs[self.current_tab]["frame"].configure(bg='#21262d')
        self.tabs[self.current_tab]["frame"].winfo_children()[0].configure(bg='#21262d')
        
        self.tabs[tab_name]["frame"].configure(bg='#1c2128')
        self.tabs[tab_name]["frame"].winfo_children()[0].configure(bg='#1c2128')
        
        # Add indicator to new tab
        self.tabs[tab_name]["indicator"] = tk.Frame(self.tabs[tab_name]["frame"], bg='#58a6ff', height=2)
        self.tabs[tab_name]["indicator"].place(relx=0, rely=0.9, relwidth=1)
        
        # Hide current tab content and show new one
        self.tab_contents[self.current_tab].pack_forget()
        self.tab_contents[tab_name].pack(fill='both', expand=True)
        
        self.current_tab = tab_name
    
    def render_app_list(self):
        """Renders the application list in the sidebar"""
        # Clear existing items
        for widget in self.app_list_frame.winfo_children():
            widget.destroy()
        
        if not self.config.get("applications"):
            empty_label = tk.Label(self.app_list_frame, text="No applications added",
                                  font=('Segoe UI', 9), bg='#0d1117', fg='#8b949e')
            empty_label.pack(pady=10)
            return
        
        # Add each application
        for app in self.config["applications"]:
            app_frame = tk.Frame(self.app_list_frame, bg='#161b22' if self.selected_app_id != app["id"] else '#1c2128',
                                bd=1, relief='solid', padx=10, pady=8, cursor='hand2')
            app_frame.pack(fill='x', pady=2)
            
            # Highlight selected app
            if self.selected_app_id == app["id"]:
                app_frame.configure(highlightbackground='#58a6ff', highlightthickness=1)
            else:
                app_frame.configure(highlightthickness=0)
            
            app_name = tk.Label(app_frame, text=app["name"], font=('Segoe UI', 9, 'bold'),
                               bg=app_frame.cget('bg'), fg='white')
            app_name.pack(anchor='w')
            
            app_process = tk.Label(app_frame, text=app["process"], font=('Segoe UI', 8),
                                  bg=app_frame.cget('bg'), fg='#8b949e')
            app_process.pack(anchor='w')
            
            # Bind click event
            app_frame.bind("<Button-1>", lambda e, id=app["id"]: self.select_app(id))
            app_name.bind("<Button-1>", lambda e, id=app["id"]: self.select_app(id))
            app_process.bind("<Button-1>", lambda e, id=app["id"]: self.select_app(id))
        
        # Update canvas scroll region
        self.app_list_frame.update_idletasks()
        self.app_canvas.configure(scrollregion=self.app_canvas.bbox('all'))
    
    def select_app(self, app_id):
        """Selects an application from the list"""
        self.selected_app_id = app_id
        self.render_app_list()
        
        # Show app details
        app = next((a for a in self.config["applications"] if a["id"] == app_id), None)
        if app:
            self.no_app_frame.pack_forget()
            self.app_details_frame.pack(fill='both', expand=True)
            
            self.app_name_label.configure(text=app["name"])
            self.app_path_label.configure(text=f"Path: {app['path']}")
        else:
            self.app_details_frame.pack_forget()
            self.no_app_frame.pack(fill='both', expand=True)
    
    def open_app_modal(self, is_edit=False):
        """Opens the modal for adding/editing applications"""
        self.create_app_modal()
        
        if is_edit and self.selected_app_id:
            app = next((a for a in self.config["applications"] if a["id"] == self.selected_app_id), None)
            if app:
                self.editing_app_id = app["id"]
                self.modal_title.configure(text="Edit Application")
                self.app_name_input.delete(0, tk.END)
                self.app_name_input.insert(0, app["name"])
                self.app_path_input.delete(0, tk.END)
                self.app_path_input.insert(0, app["path"])
                self.app_process_input.delete(0, tk.END)
                self.app_process_input.insert(0, app["process"])
        else:
            self.editing_app_id = None
            self.modal_title.configure(text="Add Application")
            self.app_name_input.delete(0, tk.END)
            self.app_path_input.delete(0, tk.END)
            self.app_process_input.delete(0, tk.END)
        
        # Center modal on parent window
        self.center_modal()
        self.app_modal.deiconify()
        self.app_modal.grab_set()
    
    def center_modal(self):
        """Centers the modal on the parent window"""
        self.app_modal.update_idletasks()
        
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        
        modal_width = self.app_modal.winfo_width()
        modal_height = self.app_modal.winfo_height()
        
        x = parent_x + (parent_width // 2) - (modal_width // 2)
        y = parent_y + (parent_height // 2) - (modal_height // 2)
        
        self.app_modal.geometry(f"+{x}+{y}")
    
    def close_app_modal(self):
        """Closes the application modal"""
        self.app_modal.grab_release()
        self.app_modal.withdraw()
    
    def browse_file(self):
        """Opens file browser to select application"""
        file_path = filedialog.askopenfilename(
            title="Select Application",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.app_path_input.delete(0, tk.END)
            self.app_path_input.insert(0, file_path)
            
            # Auto-fill process name if empty
            if not self.app_process_input.get():
                process_name = os.path.basename(file_path)
                self.app_process_input.delete(0, tk.END)
                self.app_process_input.insert(0, process_name)
    
    def save_app(self):
        """Saves the application data"""
        name = self.app_name_input.get().strip()
        path = self.app_path_input.get().strip()
        process = self.app_process_input.get().strip()
        
        if not name or not path or not process:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if self.editing_app_id:
            # Edit existing app
            for app in self.config["applications"]:
                if app["id"] == self.editing_app_id:
                    app["name"] = name
                    app["path"] = path
                    app["process"] = process
                    break
        else:
            # Add new app
            new_id = 1
            if self.config["applications"]:
                new_id = max(app["id"] for app in self.config["applications"]) + 1
            
            self.config["applications"].append({
                "id": new_id,
                "name": name,
                "path": path,
                "process": process
            })
            
            self.selected_app_id = new_id
        
        self.save_config()
        self.render_app_list()
        self.select_app(self.selected_app_id)
        self.close_app_modal()
    
    def remove_app(self):
        """Removes the selected application"""
        if not self.selected_app_id:
            return
        
        app = next((a for a in self.config["applications"] if a["id"] == self.selected_app_id), None)
        if not app:
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove {app['name']}?"):
            self.config["applications"] = [a for a in self.config["applications"] if a["id"] != self.selected_app_id]
            self.save_config()
            
            if self.config["applications"]:
                self.selected_app_id = self.config["applications"][0]["id"]
            else:
                self.selected_app_id = None
            
            self.render_app_list()
            
            if self.selected_app_id:
                self.select_app(self.selected_app_id)
            else:
                self.app_details_frame.pack_forget()
                self.no_app_frame.pack(fill='both', expand=True)
    
    def launch_app(self):
        """Launches the selected application with cheats"""
        if not self.selected_app_id:
            return
        
        app = next((a for a in self.config["applications"] if a["id"] == self.selected_app_id), None)
        if not app:
            return
        
        # Check license
        if not self.config.get("license", {}).get("valid", False):
            messagebox.showerror("Error", "Invalid license. Please activate your license to use this feature.")
            return
        
        # Show loading animation
        self.app_status_label.configure(text="Launching...", fg='#f0883e')
        self.start_loader_animation()
        
        # Simulate launching
        self.root.after(2000, lambda: self.finish_launch(app))
    
    def finish_launch(self, app):
        """Completes the launch process"""
        self.stop_loader_animation()
        self.app_status_label.configure(text="Running", fg='#2ea043')
        
        messagebox.showinfo("Success", f"Launching {app['name']}...\nInjecting cheats into {app['process']}")
    
    def create_loader_animation(self):
        """Creates the loader animation"""
        self.loader_angle = 0
        self.loader_running = False
        
        # Draw initial loader (hidden)
        self.loader_canvas.create_oval(2, 2, 18, 18, outline='#30363d', width=2, tags="loader_bg")
        self.loader_canvas.create_arc(2, 2, 18, 18, start=0, extent=60, 
                                     outline='#58a6ff', width=2, style=tk.ARC, tags="loader")
    
    def start_loader_animation(self):
        """Starts the loader animation"""
        self.loader_running = True
        self.animate_loader()
    
    def animate_loader(self):
        """Animates the loader"""
        if not self.loader_running:
            return
        
        self.loader_angle = (self.loader_angle + 10) % 360
        self.loader_canvas.itemconfig("loader", start=self.loader_angle)
        self.root.after(50, self.animate_loader)
    
    def stop_loader_animation(self):
        """Stops the loader animation"""
        self.loader_running = False
    
    def toggle_cheat(self, option):
        """Toggles a cheat option"""
        current_value = self.cheat_vars[option].get()
        new_value = not current_value
        self.cheat_vars[option].set(new_value)
        
        # Update toggle appearance
        indicator = self.cheat_vars[option].indicator
        parent = indicator.master
        
        if new_value:
            parent.configure(bg='#238636')
            indicator.place(x=22, y=2)
        else:
            parent.configure(bg='#21262d')
            indicator.place(x=2, y=2)
    
    def toggle_setting(self, setting):
        """Toggles a setting option"""
        current_value = self.settings_vars[setting].get()
        new_value = not current_value
        self.settings_vars[setting].set(new_value)
        
        # Update toggle appearance
        indicator = self.settings_vars[setting].indicator
        parent = indicator.master
        
        if new_value:
            parent.configure(bg='#238636')
            indicator.place(x=22, y=2)
        else:
            parent.configure(bg='#21262d')
            indicator.place(x=2, y=2)
    
    def save_settings(self):
        """Saves the settings"""
        self.config["settings"] = {
            "autostart": self.settings_vars["autostart"].get(),
            "tray": self.settings_vars["tray"].get(),
            "autoupdate": self.settings_vars["autoupdate"].get(),
            "injection": {
                "method": self.injection_method.get().lower().replace(" ", ""),
                "delay": int(self.injection_delay.get())
            }
        }
        
        self.save_config()
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def activate_license(self):
        """Activates the license"""
        key = self.license_key.get().strip()
        
        if not key:
            messagebox.showerror("Error", "Please enter a license key")
            return
        
        # Simulate license validation
        if len(key) >= 16:
            # Set license as valid for 30 days
            expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
            
            self.config["license"] = {
                "valid": True,
                "expiry": expiry_date.isoformat()
            }
            
            self.save_config()
            self.update_license_ui()
            
            messagebox.showinfo("Success", "License activated successfully!")
            self.license_key.set("")
        else:
            messagebox.showerror("Error", "Invalid license key. Please check and try again.")
    
    def update_license_ui(self):
        """Updates the license UI elements"""
        if self.config.get("license", {}).get("valid", False):
            expiry_date = datetime.datetime.fromisoformat(self.config["license"]["expiry"])
            formatted_date = expiry_date.strftime("%Y-%m-%d")
            
            self.license_status_label.configure(text="License: Valid")
            self.license_expiry_label.configure(text=f"Expires: {formatted_date}")
            self.license_status_text.configure(text="Valid License")
            self.license_expiry_text.configure(text=f"Expires on {formatted_date}")
            
            self.license_status_frame.configure(bg='#238636')
            self.license_status_label.configure(bg='#238636')
            self.license_status_detail.configure(bg='#238636')
            self.license_status_text.configure(bg='#238636')
        else:
            self.license_status_label.configure(text="License: Invalid")
            self.license_expiry_label.configure(text="No active license")
            self.license_status_text.configure(text="Invalid License")
            self.license_expiry_text.configure(text="No active license")
            
            self.license_status_frame.configure(bg='#da3633')
            self.license_status_label.configure(bg='#da3633')
            self.license_status_detail.configure(bg='#da3633')
            self.license_status_text.configure(bg='#da3633')
    
    def run(self):
        """Runs the application"""
        # Load settings into UI
        if "settings" in self.config:
            settings = self.config["settings"]
            if "autostart" in settings:
                self.toggle_setting("autostart") if settings["autostart"] != self.settings_vars["autostart"].get() else None
            if "tray" in settings:
                self.toggle_setting("tray") if settings["tray"] != self.settings_vars["tray"].get() else None
            if "autoupdate" in settings:
                self.toggle_setting("autoupdate") if settings["autoupdate"] != self.settings_vars["autoupdate"].get() else None
            if "injection" in settings:
                self.injection_method.set(settings["injection"]["method"])
                self.injection_delay.set(str(settings["injection"]["delay"]))
        
        # Update license UI
        self.update_license_ui()
        
        # Select first app if available
        if self.config["applications"]:
            self.select_app(self.config["applications"][0]["id"])
        
        self.root.mainloop()

if __name__ == "__main__":
    app = NebelixLoader()
    app.run()
