import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import json
import os
from tkinter.font import Font
from tkinter import PhotoImage

# ======================
# GLOBAL STYLE CONFIGURATION
# ======================
STYLE_CONFIG = {
    # Root window styling
    "root": {
        "bg": "#050505",       # Dark background color
        "fg": "#D41D1D",        # Light text color
        "highlight": "#1a1b1c",  # Accent color
        "font":("Univers",10)
    },
    
    # Tab styling
    "tab": {
        "bg": "#f7f3f3",        # Tab background
        "fg": "#0f0d0d",        # Tab text color
        "selected_bg": "#91c117", # Selected tab background
        "selected_fg": "#fd0707", # Selected tab text
        "font": ("Univers",10)  # Tab font
    },
    
    # Text styling
    "text": {
        "normal": "#f7f8fa",    # Regular text
        "heading": "#f7f8fa",   # Headings
        "error": "#cf6679",     # Error messages
        "status": "#07ba58",    # Status bar
        "highlight": "#f7f8fa",  # Highlighted text
        "font":("Univers",10)
    },
    
    # Button styling
    "button": {
        "bg": "#1ab660",        # Button background
        "fg": "#ffffff",       # Button text
        "active_bg": "#3a56a0", # Active state
        "disabled_bg": "#f10707", # Disabled state
        "font": ("Univers",10) # Button font
    },
    
    # Entry field styling
    "entry": {
        "bg": "#f6eded",       # Background
        "fg": "#2813c5",       # Text color
        "insertbg": "#e69090",  # Cursor color
        "selectbg": "#7e98df", # Selection background
        "selectfg": "#ffffff", # Selection text
        "font": ("Univers",10,"bold"),# Font
        "width":8, 
        "height":8,
    },
    
    # Label styling
    "label": {
        "bg": "#f7f3f3",       # Background
        "fg": "#0b0a0a",       # Text color
        "font": ("Univers",10), # Font
        "border":"#bf7979",
    },
    
    # Frame styling
    "frame": {
        "bg": "#f7f3f3",       # Background
        "highlight": "#060606"  # Border highlight
    },
    
    # Status bar styling
    "statusbar": {
        "bg": "#95a67c",       # Background
        "fg": "#480ea5",       # Text color
        "font": ("Univers",10)  # Font
    },
    
    # Scrollbar styling
    "scrollbar": {
        "bg": "#a39696",       # Background
        "trough": "#f60c61",    # Trough color
        "arrow": "#000000"      # Arrow color
    }
}

# ======================
# BLAST FURNACE CLASS
# ======================
class BlastFurnace:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
        # Initialize application components
        self.setup_main_window()
        self.configure_styles()
        self.initialize_data_structures()
        self.create_widgets()
        self.load_data()
        self.setup_window_management()

    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title(f"*BLAST FURNACE *-* ROURKELA STEEL PLANT*")
        self.root.state("zoom")
        self.root.iconbitmap("bipin.ico")
        
        # Apply root window styling
        self.root.configure(
            bg=STYLE_CONFIG["root"]["bg"],
            highlightthickness=0
        )

    def configure_styles(self):
        """Configure all widget styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Most customizable theme
        
        # Base style for all widgets
        self.style.configure('.', 
            background=STYLE_CONFIG["root"]["bg"],
            foreground=STYLE_CONFIG["text"]["normal"],
            font=STYLE_CONFIG["tab"]["font"],
            borderwidth=0
        )
        
        # Notebook (Tab) styling
        self.style.configure('TNotebook',
            background=STYLE_CONFIG["tab"]["bg"],
            borderwidth=0
        )
        self.style.configure('TNotebook.Tab',
            background=STYLE_CONFIG["tab"]["bg"],
            foreground=STYLE_CONFIG["tab"]["fg"],
            padding=[10, 5],
            font=STYLE_CONFIG["tab"]["font"]
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', STYLE_CONFIG["tab"]["selected_bg"])],
            foreground=[('selected', STYLE_CONFIG["tab"]["selected_fg"])]
        )
        
        # Button styling
        self.style.configure('TButton',
            background=STYLE_CONFIG["button"]["bg"],
            foreground=STYLE_CONFIG["button"]["fg"],
            font=STYLE_CONFIG["button"]["font"],
            borderwidth=1,
            relief="raised"
        )
        self.style.map('TButton',
            background=[
                ('active', STYLE_CONFIG["button"]["active_bg"]),
                ('pressed', STYLE_CONFIG["button"]["active_bg"]),
                ('disabled', STYLE_CONFIG["button"]["disabled_bg"])
            ]
        )
        
        # Entry field styling
        self.style.configure('TEntry',
            fieldbackground=STYLE_CONFIG["entry"]["bg"],
            foreground=STYLE_CONFIG["entry"]["fg"],
            insertcolor=STYLE_CONFIG["entry"]["insertbg"],
            selectbackground=STYLE_CONFIG["entry"]["selectbg"],
            selectforeground=STYLE_CONFIG["entry"]["selectfg"],
            font=STYLE_CONFIG["entry"]["font"],
            borderwidth=1,
            relief="sunken"
        )
        
        # Label styling
        self.style.configure('TLabel',
            background=STYLE_CONFIG["label"]["bg"],
            foreground=STYLE_CONFIG["label"]["fg"],
            font=STYLE_CONFIG["label"]["font"]
        )
        
        # Frame styling
        self.style.configure('TFrame',
            background=STYLE_CONFIG["frame"]["bg"],
            relief="flat"
        )
        
        # LabelFrame styling
        self.style.configure('TLabelframe',
            background=STYLE_CONFIG["frame"]["bg"],
            foreground=STYLE_CONFIG["text"]["heading"],
            bordercolor=STYLE_CONFIG["frame"]["highlight"],
            relief="groove"
        )
        self.style.configure('TLabelframe.Label',
            background=STYLE_CONFIG["frame"]["bg"],
            foreground=STYLE_CONFIG["text"]["heading"]
        )
        
        # Checkbutton styling
        self.style.configure('TCheckbutton',
            background=STYLE_CONFIG["frame"]["bg"],
            foreground=STYLE_CONFIG["text"]["normal"],
            indicatorcolor=STYLE_CONFIG["frame"]["bg"],
            indicatordiameter=15
        )
        self.style.map('TCheckbutton',
            background=[('active', STYLE_CONFIG["frame"]["bg"])]
        )
        
        # Scrollbar styling
        self.style.configure('Vertical.TScrollbar',
            background=STYLE_CONFIG["scrollbar"]["bg"],
            troughcolor=STYLE_CONFIG["scrollbar"]["trough"],
            arrowcolor=STYLE_CONFIG["scrollbar"]["arrow"],
            bordercolor=STYLE_CONFIG["frame"]["bg"]
        )
        
        # Custom tab styles dictionary
        self.tab_styles = {
            "Material Properties": {
                "bg": "#f7f3f3", 
                "fg": "#ffffff", 
                "font": STYLE_CONFIG["tab"]["font"],
                "header_font": ("Univers",10, 'bold'), 
                "button_bg": STYLE_CONFIG["button"]["bg"], 
                "button_fg": STYLE_CONFIG["button"]["fg"],
                "frame_bg": "#3a4e7a"
            },
            "Input Quantities": {
                "bg": "#f7f3f3", 
                "fg": "#ffffff", 
                "font": STYLE_CONFIG["tab"]["font"],
                "header_font": ("Univers",10, 'bold'), 
                "button_bg": STYLE_CONFIG["button"]["bg"], 
                "button_fg": STYLE_CONFIG["button"]["fg"],
                "frame_bg": "#3a4e7a"
            },
            "Results": {
                "bg": "#f7f3f3", 
                "fg": "#ffffff", 
                "font": STYLE_CONFIG["tab"]["font"],
                "header_font": ("Univers",10, 'bold'), 
                "button_bg": STYLE_CONFIG["button"]["bg"], 
                "button_fg": STYLE_CONFIG["button"]["fg"],
                "frame_bg": "#3a4e7a"
            },
            "Settings": {
                "bg": "#f7f3f3", 
                "fg": "#ffffff", 
                "font": STYLE_CONFIG["tab"]["font"],
                "header_font": ("Univers",10, 'bold'), 
                "button_bg": STYLE_CONFIG["button"]["bg"], 
                "button_fg": STYLE_CONFIG["button"]["fg"],
                "frame_bg": "#3a4e7a"
            }
        }
    def initialize_data_structures(self):
        self.data_file = f"furnace_data_{self.username}.json"
        self.materials = {}
        self.inputs = {}
        self.results = {}
        self.calculation_steps = []
        self.auto_save = True
        
        self.default_materials = {
            "COKE": {"C (%)": "86", "Moisture (%)": "4.5", "FE (%)": "0.0", 
                     "SiO2 (%)": "5.5", "CAO (%)": "0.0", "MGO (%)": "0.0", 
                     "AL203 (%)": "3.3", "Density": "0.55"},
            "SINTER": {"C (%)": "0", "Moisture (%)": "0.6", "FE (%)": "53.9", 
                      "SiO2 (%)": "6.9", "CAO (%)": "10.5", "MGO (%)": "2.3", 
                      "AL203 (%)": "3.7", "Density": "1.80"},
            "ORE": {"C (%)": "0", "Moisture (%)": "4.5", "FE (%)": "62.5", 
                   "SiO2 (%)": "2.5", "CAO (%)": "0.0", "MGO (%)": "0.0", 
                   "AL203 (%)": "3.6", "Density": "2.20"},
            "PELLETS": {"C (%)": "0", "Moisture (%)": "2.8", "FE (%)": "63.5", 
                       "SiO2 (%)": "4.0", "CAO (%)": "0.5", "MGO (%)": "0.3", 
                       "AL203 (%)": "1.4", "Density": "2.00"},
            "SCRAP": {"C (%)": "0", "Moisture (%)": "0.5", "FE (%)": "65.0", 
                     "SiO2 (%)": "0.0", "CAO (%)": "0.0", "MGO (%)": "0.0", 
                     "AL203 (%)": "0.0", "Density": "1.20"},
            "PCI": {"C (%)": "88", "Moisture (%)": "0.0", "FE (%)": "0.0", 
                   "SiO2 (%)": "4.4", "CAO (%)": "0.0", "MGO (%)": "0.0", 
                   "AL203 (%)": "2.6", "Density": "0.55"},
            "NCOKE": {"C (%)": "89", "Moisture (%)": "5.7", "FE (%)": "0.0", 
                     "SiO2 (%)": "0.0", "CAO (%)": "0.0", "MGO (%)": "0.0", 
                     "AL203 (%)": "0.0", "Density": "0.55"}
        }
        
        self.default_inputs = {
            "COKE": {"Weight": "8100"},
            "SINTER": {"Weight": "21100"},
            "ORE": {"Weight": "3200"},
            "PELLETS": {"Weight": "3500"},
            "SCRAP": {"Weight": "600"},
            "PCI": {"Weight": "0"},
            "NCOKE": {"Weight": "0"}
        }
        
        # Define hm_prod_var here
        self.hm_prod_var = tk.StringVar(value="")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_title_bar(main_frame)
        self.create_notebook(main_frame)
        self.create_status_bar(main_frame)

    def create_title_bar(self, parent):
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.BOTH, pady=(0, 10))
        ttk.Label(title_frame, text=f"BLAST FURNACE ({self.username})", 
                 font=("Univers",10, 'bold')).pack(side=tk.LEFT)

    def create_notebook(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_materials_tab()
        self.create_inputs_tab()
        self.create_results_tab()
        self.create_settings_tab()

    def create_status_bar(self, parent):
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5,0))
        self.status_var.set("Ready - Enter data to begin calculations")

    def create_materials_tab(self):
        tab_name = "Material Properties"
        style = self.tab_styles[tab_name]
        tab = self.create_scrollable_tab(tab_name, style)
        
        headers = [
            ("Material", "Material name"),
            ("C (%)", "Carbon content"),
            ("Moisture (%)", "Moisture percentage"),
            ("FE (%)", "Iron content"),
            ("SiO2 (%)", "Silicon dioxide"),
            ("CAO (%)", "Calcium oxide"),
            ("MGO (%)", "Magnesium oxide"),
            ("AL203 (%)", "Aluminum oxide"),
            ("Density", "Bulk density (ton/m³)")
        ]
        
        self.create_headers(tab['frame'], headers, style)
        self.create_material_entries(tab['frame'], headers, style)
        self.create_load_defaults_button(tab['frame'], "Load Default Materials", 
                                       self.load_default_materials, style)

    def create_inputs_tab(self):
        tab_name = "Input Quantities"
        style = self.tab_styles[tab_name]
        tab = self.create_scrollable_tab(tab_name, style)

        
        headers = [
            ("Material", "Material name"),
            ("Weight (kg)", "Input weight"),
            ("Moisture Adj.", "Moisture adjustment"),
            ("Dry Weight", "Dry weight"),
            ("Fe Input", "Iron input"),
            ("C Input", "Carbon input"),
            ("SiO2 Input", "SiO2 input"),
            ("CaO Input", "CaO input"),
            ("MgO Input", "MgO input"),
            ("Al2O3 Input", "Al2O3 input")
        ]
        
        self.create_headers(tab['frame'], headers, style)
        self.create_input_entries(tab['frame'], headers, style)
        self.create_load_defaults_button(tab['frame'], "Load Default Inputs", 
                                       self.load_default_inputs, style)

    def create_results_tab(self):
        tab_name = "Results"
        style = self.tab_styles[tab_name]
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=tab_name)
        
        canvas = tk.Canvas(tab, borderwidth=0, highlightthickness=0, bg=style['bg'])
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Results.TFrame')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=style['bg'])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Production parameters
        param_frame = ttk.LabelFrame(scrollable_frame, text="Production Parameters", 
                                   style='Results.TLabelframe', padding=10)
        param_frame.pack(fill=tk.BOTH, pady=5)
        
        
        # Create two columns for results
        columns_frame = ttk.Frame(scrollable_frame, style='Results.TFrame')
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column frame
        left_column = ttk.Frame(columns_frame, style='Results.TFrame')
        left_column.pack(side="left", fill=tk.BOTH, expand=True, padx=5)
        
        # Right column frame
        right_column = ttk.Frame(columns_frame, style='Results.TFrame')
        right_column.pack(side="right", fill=tk.BOTH, expand=True, padx=5)
        
        # Results sections - organized into two columns
        left_sections = [
            ("Consumption Rates", [
                ("Hot Metal", "kg/CH", "Hot Metal production"),
                ("Coke Rate", "kg/THM", "Coke consumption per ton of hot metal"),
                ("Slag Rate", "kg/THM", "Slag produced per ton of hot metal"),
                ("PCI Rate", "kg/THM", "PCI consumption per ton of hot metal"),
                ("Fe/C Ratio", "", "Iron to carbon ratio"),
                ("Slag Basicity", "", "(CaO+MgO)/SiO2 ratio"),
                ("Alumina Ratio", "", "Al2O3/(CaO+MgO) ratio"),
                ("Sinter %", "%", "Percentage of sinter in burden"),
                ("Ore %", "%", "Percentage of ore in burden"),
                ("Pellets %", "%", "Percentage of pellets in burden"),
                ("Scrap %", "%", "Percentage of scrap in burden")
            ])
        ]
        
        right_sections = [
            ("Input Totals", [
                ("Total Weight", "kg", "Total input weight"),
                ("Total Dry Weight", "kg", "Total dry weight"),
                ("Total Fe Input", "kg", "Total iron input"),
                ("Total C Input", "kg", "Total carbon input"),
                ("Total SiO2", "kg", "Total SiO2 input"),
                ("Total CaO", "kg", "Total CaO input"),
                ("Total MgO", "kg", "Total MgO input"),
                ("Total Al2O3", "kg", "Total Al2O3 input")
            ])
        ]
        
        self.result_vars = {}
        
        # Create left column sections
        for section_title, metrics in left_sections:
            section_frame = ttk.LabelFrame(left_column, text=section_title, 
                                         style='Results.TLabelframe', padding=5)
            section_frame.pack(fill=tk.BOTH, pady=5)
            
            for i, (name, unit, tooltip) in enumerate(metrics):
                ttk.Label(section_frame, text=name, style='Results.TLabel').grid(
                    row=i, column=0, sticky="e", padx=5, pady=2)
                
                var = tk.StringVar()
                ttk.Entry(section_frame, textvariable=var, state='readonly', width=15,
                         style='Results.TEntry').grid(
                    row=i, column=1, sticky="w", padx=5, pady=2)
                
                self.result_vars[name] = var
        
        # Create right column sections
        for section_title, metrics in right_sections:
            section_frame = ttk.LabelFrame(right_column, text=section_title, 
                                         style='Results.TLabelframe', padding=5)
            section_frame.pack(fill=tk.BOTH, pady=5)
            
            for i, (name, unit, tooltip) in enumerate(metrics):
                ttk.Label(section_frame, text=name, style='Results.TLabel').grid(
                    row=i, column=0, sticky="e", padx=5, pady=2)
                
                var = tk.StringVar()
                ttk.Entry(section_frame, textvariable=var, state='readonly', width=15,
                         style='Results.TEntry').grid(
                    row=i, column=1, sticky="w", padx=5, pady=2)
                
                self.result_vars[name] = var
    
        # Buttons
        btn_frame = ttk.Frame(scrollable_frame, style='Results.TFrame')
        btn_frame.pack(fill=tk.BOTH, pady=10)
        
        ttk.Button(btn_frame, text="Calculate", command=self.calculate_results,
                  style='Results.TButton').pack()
        ttk.Button(btn_frame, text="Export Results", command=self.export_results,
                  style='Results.TButton').pack(pady=5)

    def create_settings_tab(self):
        tab_name = "Settings"
        style = self.tab_styles[tab_name]
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text=tab_name)
        
        settings_frame = ttk.LabelFrame(tab, text="Data Management", 
                                      style='Settings.TLabelframe', padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auto-save toggle
        self.auto_save_var = tk.BooleanVar(value=self.auto_save)
        ttk.Checkbutton(settings_frame, text="Enable Auto-Save", 
                       variable=self.auto_save_var,
                       command=self.toggle_auto_save,
                       style='Settings.TCheckbutton').pack(anchor="w", pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(settings_frame, style='Settings.TFrame')
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Save All Data Now", 
                  command=self.save_all_data,
                  style='Settings.TButton').pack(side="left", padx=5, fill=tk.X, expand=True)
        
        ttk.Button(btn_frame, text="Reset All Data", 
                  command=self.reset_all_data,
                  style='Settings.TButton').pack(side="left", padx=5, fill=tk.X, expand=True)
        
        # Data file info
        file_frame = ttk.Frame(settings_frame, style='Settings.TFrame')
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Data file location:", style='Settings.TLabel').pack(side="left")
        ttk.Label(file_frame, text=self.data_file, 
                 font=('Univers', 8, 'italic'),
                 style='Settings.TLabel').pack(side="left", padx=5)

    def create_scrollable_tab(self, tab_name, style):
        """Helper method to create a scrollable tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=tab_name)
        
        canvas = tk.Canvas(tab, borderwidth=0, highlightthickness=0, bg=style['bg'])
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=style['bg'])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return {'tab': tab, 'frame': scrollable_frame}

    def create_headers(self, frame, headers, style):
        """Create column headers for a tab"""
        for col, (label, tooltip) in enumerate(headers):
            header = ttk.Label(frame, text=label, 
                             font=style['header_font'],
                             style=f'{style["bg"]}.TLabel')
            header.grid(row=0, column=col, sticky="ew", padx=2)
            self.create_tooltip(header, tooltip)

    def create_material_entries(self, frame, headers, style):
        """Create material entry fields"""
        materials = ["COKE", "SINTER", "ORE", "PELLETS", "SCRAP", "PCI", "NCOKE"]
        self.material_vars = {mat: {} for mat in materials}
        
        for row, mat in enumerate(materials, start=1):
            ttk.Label(frame, text=mat, style=f'{style["bg"]}.TLabel').grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            
            for col in range(1, len(headers)):
                var = tk.StringVar()
                var.trace_add("write", lambda *args, m=mat: self.save_material(m))
                
                entry = ttk.Entry(frame, textvariable=var, width=12,
                                 style=f'{style["bg"]}.TEntry')
                entry.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
                self.material_vars[mat][headers[col][0]] = var

    def create_input_entries(self, frame, headers, style):
        """Create input entry fields"""
        materials = ["COKE", "SINTER", "ORE", "PELLETS", "SCRAP", "PCI", "NCOKE"]
        self.input_vars = {mat: {} for mat in materials}
        self.calc_vars = {mat: {} for mat in materials}
        
        for row, mat in enumerate(materials, start=1):
            ttk.Label(frame, text=mat, style=f'{style["bg"]}.TLabel').grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Weight input
            var = tk.StringVar()
            var.trace_add("write", lambda *args, m=mat: self.calculate_inputs(m))
            entry = ttk.Entry(frame, textvariable=var, width=12,
                            style=f'{style["bg"]}.TEntry')
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            self.input_vars[mat]["Weight"] = var
            
            # Calculated fields (converted to readonly entries)
            for col, calc_field in enumerate(["Moisture Adj.", "Dry Weight", "Fe Input", 
                                             "C Input", "SiO2 Input", "CaO Input", 
                                             "MgO Input", "Al2O3 Input"], start=2):
                var = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=var, state='readonly', width=12,
                                style=f'{style["bg"]}.TEntry')
                entry.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
                self.calc_vars[mat][calc_field] = var

    def create_load_defaults_button(self, frame, text, command, style):
        """Create a load defaults button"""
        btn_frame = ttk.Frame(frame, style=f'{style["bg"]}.TFrame')
        btn_frame.grid(row=len(self.material_vars)+1, column=0, 
                      columnspan=len(self.material_vars)+1, pady=10)
        
        ttk.Button(btn_frame, text=text, 
                  command=command,
                  style=f'{style["bg"]}.TButton').pack(pady=5)

    def create_tooltip(self, widget, text):
        """Create a simple tooltip that shows in the status bar"""
        def enter(event):
            self.status_var.set(text)
        def leave(event):
            self.status_var.set("Ready")
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def setup_window_management(self):
        self.root.minsize(1000, 700)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_auto_save(self):
        self.auto_save = self.auto_save_var.get()
        self.status_var.set(f"Auto-save {'enabled' if self.auto_save else 'disabled'}")

    def load_default_materials(self):
        for mat, values in self.default_materials.items():
            for key, value in values.items():
                self.material_vars[mat][key].set(value)
        self.status_var.set("Default material values loaded")

    def load_default_inputs(self):
        for mat, values in self.default_inputs.items():
            for key, value in values.items():
                self.input_vars[mat][key].set(value)
        self.status_var.set("Default input values loaded")
        self.calculate_all_inputs()

    def calculate_all_inputs(self):
        for material in self.input_vars.keys():
            self.calculate_inputs(material)

    def calculate_inputs(self, material):
        try:
            weight = float(self.input_vars[material]["Weight"].get() or 0)
            
            # Get material properties
            props = {
                'C': float(self.material_vars[material]["C (%)"].get() or 0) / 100,
                'moisture': float(self.material_vars[material]["Moisture (%)"].get() or 0) / 100,
                'fe': float(self.material_vars[material]["FE (%)"].get() or 0) / 100,
                'sio2': float(self.material_vars[material]["SiO2 (%)"].get() or 0) / 100,
                'cao': float(self.material_vars[material]["CAO (%)"].get() or 0) / 100,
                'mgo': float(self.material_vars[material]["MGO (%)"].get() or 0) / 100,
                'al2o3': float(self.material_vars[material]["AL203 (%)"].get() or 0) / 100
            }
            
            # Calculate derived values
            moisture_adj = 1 - props['moisture']
            dry_weight = weight * moisture_adj
            fe_input = dry_weight * props['fe']
            c_input = dry_weight * props['C']
            sio2_input = dry_weight * props['sio2']
            cao_input = dry_weight * props['cao']
            mgo_input = dry_weight * props['mgo']
            al2o3_input = dry_weight * props['al2o3']
            
            # Update calculated fields
            self.calc_vars[material]["Moisture Adj."].set(f"{moisture_adj:.2f}")
            self.calc_vars[material]["Dry Weight"].set(f"{dry_weight:.1f}")
            self.calc_vars[material]["Fe Input"].set(f"{fe_input:.1f}")
            self.calc_vars[material]["C Input"].set(f"{c_input:.1f}")
            self.calc_vars[material]["SiO2 Input"].set(f"{sio2_input:.1f}")
            self.calc_vars[material]["CaO Input"].set(f"{cao_input:.1f}")
            self.calc_vars[material]["MgO Input"].set(f"{mgo_input:.1f}")
            self.calc_vars[material]["Al2O3 Input"].set(f"{al2o3_input:.1f}")
            
            self.calculate_results()
            
        except ValueError:
            pass

    def calculate_results(self):
        try:
            # Calculate totals
            totals = {
                'weight': sum(float(self.input_vars[mat]["Weight"].get() or 0) for mat in self.input_vars),
                'dry_weight': sum(float(self.calc_vars[mat]["Dry Weight"].get() or 0) for mat in self.calc_vars),
                'fe': sum(float(self.calc_vars[mat]["Fe Input"].get() or 0) for mat in self.calc_vars),
                'c': sum(float(self.calc_vars[mat]["C Input"].get() or 0) for mat in self.calc_vars),
                'sio2': sum(float(self.calc_vars[mat]["SiO2 Input"].get() or 0) for mat in self.calc_vars),
                'cao': sum(float(self.calc_vars[mat]["CaO Input"].get() or 0) for mat in self.calc_vars),
                'mgo': sum(float(self.calc_vars[mat]["MgO Input"].get() or 0) for mat in self.calc_vars),
                'al2o3': sum(float(self.calc_vars[mat]["Al2O3 Input"].get() or 0) for mat in self.calc_vars)
            }
            
            # Update total fields
            self.result_vars["Total Weight"].set(f"{totals['weight']:.1f}")
            self.result_vars["Total Dry Weight"].set(f"{totals['dry_weight']:.1f}")
            self.result_vars["Total Fe Input"].set(f"{totals['fe']:.1f}")
            self.result_vars["Total C Input"].set(f"{totals['c']:.1f}")
            self.result_vars["Total SiO2"].set(f"{totals['sio2']:.1f}")
            self.result_vars["Total CaO"].set(f"{totals['cao']:.1f}")
            self.result_vars["Total MgO"].set(f"{totals['mgo']:.1f}")
            self.result_vars["Total Al2O3"].set(f"{totals['al2o3']:.1f}")
            
            # Calculate hot metal production
            try:
                hm_production = float(self.hm_prod_var.get() or 0)
                if hm_production <= 0:
                    hm_production = totals['fe'] / 0.945  # Default calculation if not specified
                    self.hm_prod_var.set(f"{hm_production:.1f}")
            except ValueError:
                hm_production = totals['fe'] / 0.945
                self.hm_prod_var.set(f"{hm_production:.1f}")
            
            # Calculate and display results
            if hm_production > 0:
                # Consumption rates
                self.result_vars["Hot Metal"].set(f"{totals['fe'] / 0.945:.1f}")
                self.result_vars["Coke Rate"].set(f"{(totals['c'] * 1000) / hm_production:.1f}")
                self.result_vars["Slag Rate"].set(f"{(totals['sio2'] + totals['al2o3'] + totals['cao'] + totals['mgo']) * 1000 / hm_production:.1f}")
                self.result_vars["PCI Rate"].set(f"{(totals['PCI']['Weight'] * 1000) / hm_production:.1f}")
                # Ratios
                self.result_vars["Fe/C Ratio"].set(f"{totals['fe'] / totals['c']:.2f}" if totals['c'] > 0 else "0")
                self.result_vars["Slag Basicity"].set(f"{(totals['cao'] + totals['mgo']) / totals['sio2']:.2f}" if totals['sio2'] > 0 else "0")
                
                # Composition percentages
                if totals['weight'] > 0:
                    self.result_vars["Sinter %"].set(f"{(float(self.input_vars['SINTER']['Weight'].get() or 0) / totals['weight']) * 100:.1f}")
                    self.result_vars["Ore %"].set(f"{(float(self.input_vars['ORE']['Weight'].get() or 0) / totals['weight']) * 100:.1f}")
                    self.result_vars["Pellets %"].set(f"{(float(self.input_vars['PELLETS']['Weight'].get() or 0) / totals['weight']) * 100:.1f}")
                    self.result_vars["Scrap %"].set(f"{(float(self.input_vars['SCRAP']['Weight'].get() or 0) / totals['weight']) * 100:.1f}")
                else:
                    self.result_vars["Sinter %"].set("0")
                    self.result_vars["Ore %"].set("0")
                    self.result_vars["Pellets %"].set("0")
                    self.result_vars["Scrap %"].set("0")
                
                self.status_var.set("Calculation successful")
            else:
                self.status_var.set("Error: Hot metal production must be > 0")
                
        except Exception as e:
            self.status_var.set(f"Error in calculations: {str(e)}")

    def save_material(self, material):
        try:
            self.materials[material] = {
                "C": float(self.material_vars[material]["C (%)"].get() or 0),
                "Moisture": float(self.material_vars[material]["Moisture (%)"].get() or 0),
                "FE": float(self.material_vars[material]["FE (%)"].get() or 0),
                "SiO2": float(self.material_vars[material]["SiO2 (%)"].get() or 0),
                "CAO": float(self.material_vars[material]["CAO (%)"].get() or 0),
                "MGO": float(self.material_vars[material]["MGO (%)"].get() or 0),
                "AL203": float(self.material_vars[material]["AL203 (%)"].get() or 0),
                "Density": float(self.material_vars[material]["Density"].get() or 0)
            }
            
            if self.auto_save:
                self.save_all_data()
            
        except ValueError:
            pass

    def save_all_data(self):
        data = {
            "materials": self.materials,
            "inputs": {
                mat: {"Weight": float(self.input_vars[mat]["Weight"].get() or 0)} 
                for mat in self.input_vars
            },
            "settings": {
                "auto_save": self.auto_save,
                "hot_metal_production": float(self.hm_prod_var.get() or 0)
            }
        }
        
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=4)
            self.status_var.set("All data saved successfully")
        except Exception as e:
            self.status_var.set(f"Error saving data: {str(e)}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            self.status_var.set("No data file found - using defaults")
            return
        
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
            
            # Load materials
            for mat, values in data.get("materials", {}).items():
                if mat in self.material_vars:
                    for key, value in values.items():
                        if f"{key} (%)" in self.material_vars[mat]:
                            self.material_vars[mat][f"{key} (%)"].set(str(value))
                        elif key in self.material_vars[mat]:
                            self.material_vars[mat][key].set(str(value))
            
            # Load inputs
            for mat, values in data.get("inputs", {}).items():
                if mat in self.input_vars:
                    self.input_vars[mat]["Weight"].set(str(values.get("Weight", "")))
            
            # Load settings
            settings = data.get("settings", {})
            self.auto_save = settings.get("auto_save", True)
            self.auto_save_var.set(self.auto_save)
            
            # Load hot metal production
            hm_prod = settings.get("hot_metal_production", 16680)
            self.hm_prod_var.set(str(hm_prod))
            
            self.calculate_all_inputs()
            self.status_var.set("Data loaded successfully")
            
        except Exception as e:
            self.status_var.set(f"Error loading data: {str(e)}")

    def export_results(self):
        try:
            results = {
                "hot_metal_production": float(self.hm_prod_var.get() or 0),
                "consumption_rates": {
                    "coke_rate": self.result_vars["Coke Rate"].get(),
                    "slag_rate": self.result_vars["Slag Rate"].get(),
                    "pci_rate": self.result_vars["PCI Rate"].get()
                },
                "chemical_ratios": {
                    "fe_c_ratio": self.result_vars["Fe/C Ratio"].get(),
                    "slag_basicity": self.result_vars["Slag Basicity"].get()
                },
                "burden_composition": {
                    "sinter_percentage": self.result_vars["Sinter %"].get(),
                    "ore_percentage": self.result_vars["Ore %"].get(),
                    "pellets_percentage": self.result_vars["Pellets %"].get(),
                    "scrap_percentage": self.result_vars["Scrap %"].get()
                },
                "input_totals": {
                    "total_weight": self.result_vars["Total Weight"].get(),
                    "total_dry_weight": self.result_vars["Total Dry Weight"].get(),
                    "total_fe_input": self.result_vars["Total Fe Input"].get(),
                    "total_c_input": self.result_vars["Total C Input"].get(),
                    "total_sio2": self.result_vars["Total SiO2"].get(),
                    "total_cao": self.result_vars["Total CaO"].get(),
                    "total_mgo": self.result_vars["Total MgO"].get(),
                    "total_al2o3": self.result_vars["Total Al2O3"].get()
                }
            }
            
            with open("blast_furnace_results.json", "w") as f:
                json.dump(results, f, indent=4)
            self.status_var.set("Results exported to blast_furnace_results.json")
        except Exception as e:
            self.status_var.set(f"Error exporting results: {str(e)}")

    def reset_all_data(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data?"):
            # Clear all entries
            for mat in self.material_vars.values():
                for var in mat.values():
                    var.set("")
            
            for mat in self.input_vars.values():
                var = mat["Weight"]
                var.set("")
            
            # Reset results
            for var in self.result_vars.values():
                if isinstance(var, tk.StringVar):
                    var.set("")
            
            # Reset hot metal production to default
            self.hm_prod_var.set("16680")
            
            # Clear data structures
            self.materials = {}
            self.inputs = {}
            
            self.status_var.set("All data has been reset")

    def on_close(self):
        if self.auto_save:
            self.save_all_data()
        self.root.destroy()

# ======================
# LOGIN SYSTEM CLASS
# ======================
class LoginSystem:
    def __init__(self, root):
        self.root = root
        self.setup_login_window()
        self.load_users()
        self.create_frames()
        self.show_login_frame()

    def setup_login_window(self):
        """Configure the login window appearance"""
        self.root.title("***LOGIN DASHBOARD***")
        self.root.state("zoom")
        self.root.iconbitmap("bipin.ico")
        self.current_user = None
        
        # Apply root window styling
        self.root.configure(
            bg=STYLE_CONFIG["root"]["bg"],
            highlightthickness=0
        )
        
        # Custom fonts
        self.title_font = Font(
            family="Verdana", 
            size=20, 
            weight="bold"
        )
        self.label_font = Font(
            family="Verdana", 
            size=12,
            weight="bold"
        )
        self.button_font = Font(
            family="Verdana", 
            size=10, 
            weight="bold"
        )
        
        # Color scheme using global config
        self.colors = {
            "primary": STYLE_CONFIG["button"]["bg"],
            "primary_light": "#3a56a0",
            "secondary": "#03DAC6",
            "background": STYLE_CONFIG["root"]["bg"],
            "surface": "#3e3e3e",
            "error": STYLE_CONFIG["text"]["error"],
            "text_primary": STYLE_CONFIG["text"]["normal"],
            "text_secondary": "#121212"
        }
        self.root.configure(bg=self.colors["background"])

    def load_users(self):
        self.db_file = "users.json"
        if not os.path.exists(self.db_file):
            self.users = {}
        else:
            with open(self.db_file, 'r') as f:
                self.users = json.load(f)

    def save_users(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_frames(self):
        self.create_login_frame()
        self.create_register_frame()
        self.create_reset_password_frame()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg=self.colors["background"])
        
        # Header
        tk.Label(self.login_frame, text="Welcome Back!", 
                font=self.title_font, bg=self.colors["background"], 
                fg=self.colors["primary_light"]).pack(pady=(40, 20))
        
        # Login form container
        form_frame = tk.Frame(self.login_frame, bg=self.colors["surface"], 
                            padx=30, pady=30, bd=0, relief=tk.RAISED)
        form_frame.pack(pady=20)
        
        # Username field
        tk.Label(form_frame, text="Username", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, font=self.label_font, width=30)
        self.username_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Password field
        tk.Label(form_frame, text="Password", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, show="•", font=self.label_font, width=30)
        self.password_entry.grid(row=3, column=0, pady=(0, 20))
        
        # Login button
        login_btn = tk.Button(form_frame, text="Login", command=self.login, 
                            font=self.button_font, bg=self.colors["primary"], 
                            fg=self.colors["text_primary"], bd=0, padx=20, pady=10,
                            activebackground=self.colors["primary_light"])
        login_btn.grid(row=4, column=0, pady=(10, 0))
        
        # Links frame
        links_frame = tk.Frame(self.login_frame, bg=self.colors["background"])
        links_frame.pack(pady=(20, 40))
        
        # Register link
        register_link = tk.Label(links_frame, text="Don't have an account? Register here", 
                               font=("Arial", 10, "underline"), bg=self.colors["background"], 
                               fg=self.colors["secondary"], cursor="hand2")
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.show_register_frame())
        
        # Reset password link
        reset_link = tk.Label(links_frame, text="Forgot password? Reset here", 
                            font=("Arial", 10, "underline"), bg=self.colors["background"], 
                            fg=self.colors["secondary"], cursor="hand2")
        reset_link.pack(pady=(10, 0))
        reset_link.bind("<Button-1>", lambda e: self.show_reset_password_frame())

    def login(self):
        """Handle login process"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password", parent=self.root)
            return
            
        if username in self.users and self.users[username]["password"] == self._hash_password(password):
            self.current_user = username
            self.root.destroy()  # Close the login window
            # Open the blast furnace app in a new window
            root = tk.Tk()
            app = BlastFurnace(root, username)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password", parent=self.root)

    def create_register_frame(self):
        """Create registration interface"""
        self.register_frame = tk.Frame(self.root, bg=self.colors["background"])
        
        # Header
        tk.Label(self.register_frame, text="Create Account", 
                font=self.title_font, bg=self.colors["background"], 
                fg=self.colors["primary_light"]).pack(pady=(40, 20))
        
        # Registration form container
        form_frame = tk.Frame(self.register_frame, bg=self.colors["surface"], 
                            padx=30, pady=30, bd=0, relief=tk.RAISED)
        form_frame.pack(pady=20)
        
        # Username field
        tk.Label(form_frame, text="Username", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.new_username_entry = ttk.Entry(form_frame, font=self.label_font, width=30)
        self.new_username_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Email field
        tk.Label(form_frame, text="Email", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, font=self.label_font, width=30)
        self.email_entry.grid(row=3, column=0, pady=(0, 15))
        
        # Password field
        tk.Label(form_frame, text="Password", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.new_password_entry = ttk.Entry(form_frame, show="•", font=self.label_font, width=30)
        self.new_password_entry.grid(row=5, column=0, pady=(0, 20))
        
        # Confirm Password field
        tk.Label(form_frame, text="Confirm Password", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.confirm_password_entry = ttk.Entry(form_frame, show="•", font=self.label_font, width=30)
        self.confirm_password_entry.grid(row=7, column=0, pady=(0, 20))
        
        # Register button
        register_btn = tk.Button(form_frame, text="Register", command=self.register, 
                                font=self.button_font, bg=self.colors["primary"], 
                                fg=self.colors["text_primary"], bd=0, padx=20, pady=10,
                                activebackground=self.colors["primary_light"])
        register_btn.grid(row=8, column=0, pady=(10, 0))
        
        # Back to login link
        login_link = tk.Label(self.register_frame, text="Back to Login", 
                            font=("Arial", 10, "underline"), bg=self.colors["background"], 
                            fg=self.colors["secondary"], cursor="hand2")
        login_link.pack(pady=(20, 40))
        login_link.bind("<Button-1>", lambda e: self.show_login_frame())

    def create_reset_password_frame(self):
        """Create password reset interface"""
        self.reset_frame = tk.Frame(self.root, bg=self.colors["background"])
        
        # Header
        tk.Label(self.reset_frame, text="Reset Password", 
                font=self.title_font, bg=self.colors["background"], 
                fg=self.colors["primary_light"]).pack(pady=(40, 20))
        
        # Reset form container
        form_frame = tk.Frame(self.reset_frame, bg=self.colors["surface"], 
                            padx=30, pady=30, bd=0, relief=tk.RAISED)
        form_frame.pack(pady=20)
        
        # Username field
        tk.Label(form_frame, text="Username", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.reset_username_entry = ttk.Entry(form_frame, font=self.label_font, width=30)
        self.reset_username_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Email field (for verification)
        tk.Label(form_frame, text="Email", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.reset_email_entry = ttk.Entry(form_frame, font=self.label_font, width=30)
        self.reset_email_entry.grid(row=3, column=0, pady=(0, 15))
        
        # New Password field
        tk.Label(form_frame, text="New Password", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.new_password_reset_entry = ttk.Entry(form_frame, show="•", font=self.label_font, width=30)
        self.new_password_reset_entry.grid(row=5, column=0, pady=(0, 20))
        
        # Confirm New Password field
        tk.Label(form_frame, text="Confirm New Password", font=self.label_font, 
                bg=self.colors["surface"], fg=self.colors["text_primary"]).grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.confirm_new_password_entry = ttk.Entry(form_frame, show="•", font=self.label_font, width=30)
        self.confirm_new_password_entry.grid(row=7, column=0, pady=(0, 20))
        
        # Reset button
        reset_btn = tk.Button(form_frame, text="Reset Password", command=self.reset_password, 
                            font=self.button_font, bg=self.colors["primary"], 
                            fg=self.colors["text_primary"], bd=0, padx=20, pady=10,
                            activebackground=self.colors["primary_light"])
        reset_btn.grid(row=8, column=0, pady=(10, 0))
        
        # Back to login link
        login_link = tk.Label(self.reset_frame, text="Back to Login", 
                            font=("Arial", 10, "underline"), bg=self.colors["background"], 
                            fg=self.colors["secondary"], cursor="hand2")
        login_link.pack(pady=(20, 40))
        login_link.bind("<Button-1>", lambda e: self.show_login_frame())

    def reset_password(self):
        """Handle password reset process"""
        username = self.reset_username_entry.get().strip()
        email = self.reset_email_entry.get().strip()
        new_password = self.new_password_reset_entry.get()
        confirm_password = self.confirm_new_password_entry.get()
        
        # Validation
        if not all([username, email, new_password, confirm_password]):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
            
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match", parent=self.root)
            return
            
        if len(new_password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters", parent=self.root)
            return
            
        if username not in self.users:
            messagebox.showerror("Error", "Username not found", parent=self.root)
            return
            
        if self.users[username]["email"].lower() != email.lower():
            messagebox.showerror("Error", "Email doesn't match our records", parent=self.root)
            return
            
        # Update password
        self.users[username]["password"] = self._hash_password(new_password)
        self.save_users()
        messagebox.showinfo("Success", "Password reset successfully!", parent=self.root)
        self.show_login_frame()

    def register(self):
        """Handle user registration"""
        username = self.new_username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match", parent=self.root)
            return
            
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters", parent=self.root)
            return
            
        if username in self.users:
            messagebox.showerror("Error", "Username already exists", parent=self.root)
            return
            
        # Save new user
        self.users[username] = {
            "email": email,
            "password": self._hash_password(password)
        }
        self.save_users()
        messagebox.showinfo("Success", "Registration successful!", parent=self.root)
        self.show_login_frame()

    def show_login_frame(self):
        """Show login screen"""
        self.register_frame.pack_forget()
        self.reset_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_register_frame(self):
        """Show registration screen"""
        self.login_frame.pack_forget()
        self.reset_frame.pack_forget()
        self.register_frame.pack(fill=tk.BOTH, expand=True)
        self.new_username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)

    def show_reset_password_frame(self):
        """Show password reset screen"""
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.reset_frame.pack(fill=tk.BOTH, expand=True)
        self.reset_username_entry.delete(0, tk.END)
        self.reset_email_entry.delete(0, tk.END)
        self.new_password_reset_entry.delete(0, tk.END)
        self.confirm_new_password_entry.delete(0, tk.END)

# ======================
# MAIN APPLICATION ENTRY
# ======================
if __name__ == "__main__":
    root = tk.Tk()
    
    # Apply root window styling
    root.configure(
        bg=STYLE_CONFIG["root"]["bg"],
        highlightthickness=0
    )
    
    # Create and run login system
    app = LoginSystem(root)
    root.mainloop()