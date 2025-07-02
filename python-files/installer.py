import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import os
import subprocess
import time
import threading
import json
import logging
from PIL import Image, ImageTk
import re
from pathlib import Path
import shutil
import winsound  # For sound on Windows only

try:
    import jsonschema
    jsonschema_available = True
except ImportError:
    jsonschema_available = False

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tooltip import ToolTip
    ttkbootstrap_available = True
except ImportError:
    ttkbootstrap_available = False

# Define fallback ToolTip if ttkbootstrap is not available
if not ttkbootstrap_available:
    def ToolTip(widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        label = tk.Label(tooltip, text=text, bg="#444444", fg="#ffffff", relief="solid", borderwidth=1, font=("Segoe UI", 10))
        label.pack()
        tooltip.withdraw()
        def show(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        def hide(event):
            tooltip.withdraw()
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

# Define JSON schemas
PROGRAMS_SCHEMA = {
    "type": "array",
    "items": {"type": "string"}
}

SOFTWARE_MAP_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9 ]+$": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "install_time": {"type": "number", "minimum": 0}
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}

INSTALL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "auto_install": {
            "type": "object",
            "properties": {
                "XP": {"type": "array", "items": {"type": "string"}},
                "7": {"type": "array", "items": {"type": "string"}},
                "8": {"type": "array", "items": {"type": "string"}},
                "10": {"type": "array", "items": {"type": "string"}},
                "11": {"type": "array", "items": {"type": "string"}}
            },
            "additionalProperties": False
        }
    },
    "required": ["auto_install"],
    "additionalProperties": False
}

SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "theme": {"type": "string", "enum": ["litera", "cyborg", "darkly"]}
    },
    "additionalProperties": False
}

class InstallerApp:
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Dreams SoFT Installer")
        self.root.geometry("1200x850")
        self.root.resizable(True, True)
        self.root.minsize(900, 650)
        self.is_closing = False

        # Set up base directory
        self.base_dir = Path(__file__).parent.resolve()
        self.programs_dir = self.base_dir / "programs"  # Fixed directory for program files
        self.programs_dir.mkdir(exist_ok=True)  # Create programs directory if it doesn't exist

        # Set up logging first
        logging.basicConfig(
            filename=str(self.programs_dir / 'installer_log.txt'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger()

        # Variables
        self.selected_version = None
        self.check_vars = {}  # Now a dict of program: (var, box_id)
        self.install_thread = None
        self.cancel_event = threading.Event()
        self.start_button = None
        self.auto_install_button = None
        self.cancel_button = None
        self.status_label = None
        self.progress = None
        self.progress_label = None
        self.elapsed_time_label = None
        self.header_label = None
        self.version_buttons = []
        self.remove_button = None
        self.add_program_button = None
        self.testing_button = None
        self.action_buttons = []
        self.is_installing = False
        self.start_time = None
        self.programs_frame = None
        self.programs_canvas = None
        self.checkbox_count = 1
        self.testing_mode = False
        self.programs = self.load_programs()
        self.software_map = self.load_software_map()
        self.install_config = self.load_install_config()
        self.search_var = tk.StringVar()
        self.resize_timer = None
        self.settings = self.load_settings()
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "litera"))
        self.icons = {}

        # Load icons after logger initialization
        self.load_icons()

        # Initialize ttkbootstrap
        if ttkbootstrap_available:
            self.style = ttk.Style(theme=self.theme_var.get())
            self.root.configure(bg=self.style.lookup("TFrame", "background"))
            self.style.configure("Hover.TButton", background="#d0e8ff")
            self.style.configure("Card.TFrame", background="#f5f5f5", relief="flat")
        else:
            self.style = ttk.Style()
            self.style.configure("TButton", font=("Segoe UI", 11), background="#e0e0e0")
            self.style.configure("TLabel", font=("Segoe UI", 11), background="#f5f5f5")
            self.style.configure("TCheckbutton", font=("Segoe UI", 11), background="#f5f5f5")

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_icons(self):
        """Load icons with a fallback default"""
        icons_dir = self.base_dir / "icons"
        icons_dir.mkdir(exist_ok=True)
        icon_files = {
            "start": "start.png",
            "auto_install": "auto_install.png",
            "cancel": "cancel.png",
            "clear": "clear.png",
            "add_program": "add_program.png",
            "load_config": "load_config.png",
            "testing": "testing.png"
        }
        for key, file_name in icon_files.items():
            try:
                img = Image.open(icons_dir / file_name).resize((24, 24), Image.LANCZOS)
                self.icons[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.log_message(f"Failed to load icon {file_name}: {e}", "WARNING")
                self.icons[key] = tk.PhotoImage(width=24, height=24)

    def load_settings(self):
        """Load settings with manual validation"""
        file_path = self.programs_dir / "settings.json"
        default_settings = {"theme": "litera"}
        try:
            with file_path.open("r", encoding="utf-8") as f:
                settings = json.load(f)
                if jsonschema_available:
                    jsonschema.validate(settings, SETTINGS_SCHEMA)
                else:
                    if not isinstance(settings, dict) or "theme" not in settings or settings["theme"] not in ["litera", "cyborg", "darkly"]:
                        raise ValueError("Invalid settings format")
                return settings
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)
            return default_settings

    def save_settings(self):
        """Save settings"""
        file_path = self.programs_dir / "settings.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def load_programs(self):
        """Load programs list"""
        file_path = self.programs_dir / "programs.json"
        try:
            with file_path.open("r", encoding="utf-8") as f:
                programs = json.load(f)
                if jsonschema_available:
                    jsonschema.validate(programs, PROGRAMS_SCHEMA)
                return programs
        except (FileNotFoundError, json.JSONDecodeError, jsonschema.ValidationError):
            default_programs = []
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(default_programs, f, ensure_ascii=False, indent=4)
            return default_programs

    def save_programs(self):
        """Save programs list"""
        file_path = self.programs_dir / "programs.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(self.programs, f, ensure_ascii=False, indent=4)

    def load_install_config(self):
        """Load installation configuration"""
        default_config = {"auto_install": {"XP": [], "7": [], "8": [], "10": [], "11": []}}
        file_path = self.programs_dir / "install_config.json"
        try:
            with file_path.open("r", encoding="utf-8") as f:
                config = json.load(f)
                if jsonschema_available:
                    jsonschema.validate(config, INSTALL_CONFIG_SCHEMA)
                return config
        except (FileNotFoundError, json.JSONDecodeError, jsonschema.ValidationError):
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return default_config

    def load_software_map(self):
        """Load software map"""
        default_map = {}
        file_path = self.programs_dir / "software_map.json"
        try:
            with file_path.open("r", encoding="utf-8") as f:
                software_map = json.load(f)
                if jsonschema_available:
                    jsonschema.validate(software_map, SOFTWARE_MAP_SCHEMA)
                return software_map
        except (FileNotFoundError, json.JSONDecodeError, jsonschema.ValidationError):
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(default_map, f, ensure_ascii=False, indent=4)
            return default_map

    def save_software_map(self):
        """Save software map"""
        file_path = self.programs_dir / "software_map.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(self.software_map, f, ensure_ascii=False, indent=4)

    def scan_pro_folder(self):
        """Scan the pro folder for .exe files"""
        self.update_ui_safe(lambda: self.status_label.config(text="Scanning pro folder..."))
        programs = []
        pro_dir = self.programs_dir / "pro"  # Changed to programs_dir/pro
        pro_dir.mkdir(exist_ok=True)
        for file in pro_dir.glob("*.exe"):
            program_name = file.stem.replace("_", " ")
            if program_name not in programs:
                programs.append(program_name)
            if program_name not in self.software_map:
                self.software_map[program_name] = {
                    "path": str(file.relative_to(self.programs_dir)),  # Relative to programs_dir
                    "install_time": 2.0
                }
        self.save_software_map()
        self.update_ui_safe(lambda: self.status_label.config(text="Ready"))
        return programs

    def setup_ui(self):
        """Set up the user interface"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar_frame = ttk.Frame(main_container, width=220, padding=10, style="Card.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)

        # Theme selection
        ttk.Label(sidebar_frame, text="🎨 Theme", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
        theme_menu = ttk.Combobox(
            sidebar_frame, textvariable=self.theme_var, values=["litera", "cyborg", "darkly"],
            state="readonly", width=15, font=("Segoe UI", 11)
        )
        theme_menu.pack(anchor="w", padx=5, pady=5)
        theme_menu.bind("<<ComboboxSelected>>", self.change_theme)
        ToolTip(theme_menu, text="Select application theme")
        ttk.Separator(sidebar_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Windows version selection
        ttk.Label(sidebar_frame, text="🖥️ Windows Version", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
        versions = ["XP", "7", "8", "10", "11"]
        self.version_buttons = []
        for version in versions:
            recommended = self.install_config.get("auto_install", {}).get(version, [])
            tooltip_text = f"Select Windows {version}\nRecommended: {', '.join(recommended) if recommended else 'None'}"
            btn = ttk.Button(
                sidebar_frame, text=f"Win {version}", style="primary.TButton",
                command=lambda v=version: self.select_version(v), width=15
            )
            btn.pack(anchor="w", pady=3, padx=5)
            self.version_buttons.append(btn)
            ToolTip(btn, text=tooltip_text)
            if ttkbootstrap_available:
                btn.bind("<Enter>", lambda e, b=btn: b.configure(style="Hover.TButton"))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(style="primary.TButton"))
        ttk.Separator(sidebar_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Actions
        ttk.Label(sidebar_frame, text="⚙️ Actions", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
        self.remove_button = ttk.Button(
            sidebar_frame, text="Clear", image=self.icons.get("clear"), compound=tk.LEFT,
            style="secondary.TButton", command=self.remove_selection, width=15
        )
        self.remove_button.pack(anchor="w", pady=3, padx=5)
        ToolTip(self.remove_button, text="Clear selected version and checkboxes")

        self.add_program_button = ttk.Button(
            sidebar_frame, text="Add Program", image=self.icons.get("add_program"), compound=tk.LEFT,
            style="info.TButton", command=self.add_program_dialog, width=15
        )
        self.add_program_button.pack(anchor="w", pady=3, padx=5)
        ToolTip(self.add_program_button, text="Add a new program")

        load_config_button = ttk.Button(
            sidebar_frame, text="Load Config", image=self.icons.get("load_config"), compound=tk.LEFT,
            style="info.TButton", command=self.load_config_file, width=15
        )
        load_config_button.pack(anchor="w", pady=3, padx=5)
        ToolTip(load_config_button, text="Load a custom config file")
        ttk.Separator(sidebar_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Testing mode
        testing_var = tk.BooleanVar(value=self.testing_mode)
        self.testing_button = ttk.Checkbutton(
            sidebar_frame, text="Testing Mode", image=self.icons.get("testing"), compound=tk.LEFT,
            variable=testing_var, command=lambda: self.toggle_testing(testing_var.get()),
            style="info.TCheckbutton"
        )
        self.testing_button.pack(anchor="w", pady=5, padx=5)
        ToolTip(self.testing_button, text="Simulate installations without running executables")

        # Main content
        main_frame = ttk.Frame(main_container, padding=10)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        self.header_label = ttk.Label(
            header_frame, text="Dreams SoFT Installer", font=("Segoe UI", 28, "bold"),
            foreground="#0288d1", anchor="center"
        )
        self.header_label.pack(pady=10)
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)

        # Search bar
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="🔍 Search", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=("Segoe UI", 11))
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_software())
        search_entry.bind("<Return>", lambda e: self.filter_software())
        search_entry.bind("<Escape>", lambda e: self.clear_search())
        search_entry.focus_set()
        ToolTip(search_entry, text="Search programs (Esc to clear)")
        clear_search_button = ttk.Button(
            search_frame, text="✖", style="danger.TButton", command=self.clear_search, width=3
        )
        clear_search_button.pack(side=tk.LEFT)
        ToolTip(clear_search_button, text="Clear search query")

        # Status panel
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=10, padx=10)
        self.status_label = ttk.Label(
            status_frame, text="Ready", font=("Segoe UI", 12, "bold"),
            foreground="#388e3c", background="#e8f5e9", padding=5
        )
        self.status_label.pack(fill=tk.X)

        # Programs list
        programs_frame = ttk.LabelFrame(main_frame, text="Programs", padding=10)
        programs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.programs_canvas = tk.Canvas(programs_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(programs_frame, orient=tk.VERTICAL, command=self.programs_canvas.yview)
        self.programs_frame = ttk.Frame(self.programs_canvas)

        self.programs_canvas.configure(yscrollcommand=scrollbar.set)
        self.programs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.programs_canvas.create_window((0, 0), window=self.programs_frame, anchor="nw")

        self.populate_programs()

        self.programs_frame.bind("<Configure>", lambda e: self.programs_canvas.configure(scrollregion=self.programs_canvas.bbox("all")))
        self.root.bind("<Configure>", self.schedule_adjust_layout)

        # Post-installation actions
        actions_frame = ttk.LabelFrame(main_frame, text="Post-Installation Action", padding=10)
        actions_frame.pack(fill=tk.X, pady=10, padx=10)
        self.action_var = tk.StringVar(value="1")
        actions = {
            "Choose Select": "1", "Application Exit": "2",
            "System Reboot": "3", "Shutdown": "4"
        }
        self.action_buttons = []
        for text, value in actions.items():
            btn = ttk.Radiobutton(
                actions_frame, text=text, value=value, variable=self.action_var, style="info.TRadiobutton"
            )
            btn.pack(side=tk.LEFT, padx=15)
            self.action_buttons.append(btn)
            btn.bind("<Tab>", lambda e: btn.focus_set())

        # Progress bar
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=10, padx=10)
        self.progress = ttk.Progressbar(
            progress_frame, length=500, mode="determinate", style="success.striped.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, pady=5)
        progress_info_frame = ttk.Frame(progress_frame)
        progress_info_frame.pack(fill=tk.X)
        self.progress_label = ttk.Label(
            progress_info_frame, text="0%", font=("Segoe UI", 11), foreground="#0288d1"
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)
        self.elapsed_time_label = ttk.Label(
            progress_info_frame, text="Elapsed: 0s", font=("Segoe UI", 11), foreground="#0288d1"
        )
        self.elapsed_time_label.pack(side=tk.LEFT, padx=10)

        # Control buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=15)
        self.start_button = ttk.Button(
            buttons_frame, text="Start", image=self.icons.get("start"), compound=tk.LEFT,
            style="success.TButton", command=self.start_installation, state=tk.DISABLED, width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.start_button.bind("<Return>", lambda e: self.start_installation())
        ToolTip(self.start_button, text="Start the installation process")
        self.start_button.bind("<Enter>", lambda e: self.start_button.configure(style="success.Outline.TButton"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.configure(style="success.TButton"))

        self.auto_install_button = ttk.Button(
            buttons_frame, text="Auto Install", image=self.icons.get("auto_install"), compound=tk.LEFT,
            style="success.TButton", command=self.start_auto_installation, state=tk.DISABLED, width=15
        )
        self.auto_install_button.pack(side=tk.LEFT, padx=10)
        self.auto_install_button.bind("<Return>", lambda e: self.start_auto_installation())
        ToolTip(self.auto_install_button, text="Auto install based on config")
        self.auto_install_button.bind("<Enter>", lambda e: self.auto_install_button.configure(style="success.Outline.TButton"))
        self.auto_install_button.bind("<Leave>", lambda e: self.auto_install_button.configure(style="success.TButton"))

        self.cancel_button = ttk.Button(
            buttons_frame, text="Cancel", image=self.icons.get("cancel"), compound=tk.LEFT,
            style="danger.TButton", command=self.cancel_installation, state=tk.DISABLED, width=15
        )
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button.bind("<Return>", lambda e: self.cancel_installation())
        ToolTip(self.cancel_button, text="Cancel the ongoing installation")
        self.cancel_button.bind("<Enter>", lambda e: self.cancel_button.configure(style="danger.Outline.TButton"))
        self.cancel_button.bind("<Leave>", lambda e: self.cancel_button.configure(style="danger.TButton"))

        # Configure styles
        if ttkbootstrap_available:
            self.style.configure("TButton", font=("Segoe UI", 11), padding=8)
            self.style.configure("TCheckbutton", font=("Segoe UI", 11))
            self.style.configure("TLabel", font=("Segoe UI", 11))
            self.style.configure("TRadiobutton", font=("Segoe UI", 11))

    def change_theme(self, event=None):
        """Change the theme and save preferences"""
        theme = self.theme_var.get()
        if ttkbootstrap_available:
            try:
                self.style.theme_use(theme)
                self.root.configure(bg=self.style.lookup("TFrame", "background"))
                self.settings["theme"] = theme
                self.save_settings()
                self.log_message(f"Changed theme to {theme}")
            except Exception as e:
                self.log_message(f"Failed to change theme: {e}", "ERROR")
                self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to change theme: {e}"))

    def update_ui_safe(self, callback):
        """Update UI safely from threads"""
        if not self.is_closing:
            try:
                if self.root and self.root.winfo_exists():
                    if isinstance(callback, list):
                        for cb in callback:
                            self.root.after(0, cb)
                    else:
                        self.root.after(0, callback)
            except Exception as e:
                self.log_message(f"UI update failed: {e}", "ERROR")

    def on_closing(self):
        """Handle window closing"""
        self.is_closing = True
        if self.is_installing:
            if messagebox.askokcancel("Quit", "Installation in progress. Cancel and quit?"):
                self.cancel_installation()
                self.root.after(100, self.root.destroy)
        else:
            self.root.destroy()

    def select_version(self, version):
        """Select Windows version"""
        self.log_message(f"Selected Windows version: {version}")
        self.selected_version = version

        for program, (var, box_id) in self.check_vars.items():
            var.set(False)

        recommended = self.install_config.get("auto_install", {}).get(version, [])
        for program in recommended:
            if program in self.check_vars:
                self.check_vars[program][0].set(True)

        self.populate_programs(query=self.search_var.get().strip())
        self.update_ui_safe(lambda: self.status_label.config(text=f"Selected: Windows {version} ({len(recommended)} programs pre-selected)"))
        self.update_ui_safe(lambda: self.start_button.config(state=tk.NORMAL if recommended else tk.DISABLED))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.NORMAL if recommended else tk.DISABLED))

        for btn in self.version_buttons:
            self.update_ui_safe(lambda b=btn: b.config(style="primary.TButton"))
        btn_index = ["XP", "7", "8", "10", "11"].index(version)
        self.update_ui_safe(lambda: self.version_buttons[btn_index].config(style="success.TButton"))

    def filter_software(self):
        """Filter programs based on search query"""
        query = self.search_var.get().strip()
        self.populate_programs(query=query)

    def clear_search(self):
        """Clear search query"""
        self.search_var.set("")
        self.populate_programs()

    def populate_programs(self, query=""):
        """Populate programs list"""
        for widget in self.programs_frame.winfo_children():
            widget.destroy()
        self.check_vars = {}

        filtered_programs = []
        query = query.lower()
        try:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            filtered_programs = [p for p in self.programs if pattern.search(p.lower())]
        except re.error:
            filtered_programs = [p for p in self.programs if query in p.lower()]

        for item in sorted(filtered_programs):
            var = tk.BooleanVar()
            self.check_vars[item] = (var, f"Box{self.checkbox_count:02d}")
            self.log_message(f"Created checkbox for '{item}' with ID 'Box{self.checkbox_count:02d}'")
            program_frame = ttk.Frame(self.programs_frame)
            program_frame.pack(anchor="w", padx=5, pady=3, fill=tk.X)
            style = "info.TCheckbutton"
            if self.selected_version and item in self.install_config.get("auto_install", {}).get(self.selected_version, []):
                style = "success.TCheckbutton"
            chk = ttk.Checkbutton(
                program_frame, text=item, variable=var, style=style, command=self.on_check
            )
            chk.pack(side=tk.LEFT)
            chk.bind("<Tab>", lambda e: chk.focus_set())
            self.checkbox_count += 1

        self.programs_frame.update_idletasks()
        self.programs_canvas.configure(scrollregion=self.programs_canvas.bbox("all"))

    def schedule_adjust_layout(self, event=None):
        """Schedule layout adjustment"""
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        self.resize_timer = self.root.after(100, self.adjust_layout)

    def adjust_layout(self):
        """Adjust programs list layout"""
        self.programs_frame.update_idletasks()
        self.programs_canvas.configure(scrollregion=self.programs_canvas.bbox("all"))

    def on_check(self):
        """Enable start button if any program is selected"""
        any_checked = any(var.get() for var, _ in self.check_vars.values())
        self.update_ui_safe(lambda: self.start_button.config(state=tk.NORMAL if any_checked else tk.DISABLED))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.NORMAL if any_checked else tk.DISABLED))

    def toggle_testing(self, enabled):
        """Toggle testing mode"""
        self.testing_mode = enabled
        self.log_message(f"Testing mode {'enabled' if enabled else 'disabled'}")

    def load_config_file(self):
        """Load a custom configuration file"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if jsonschema_available:
                        jsonschema.validate(config, INSTALL_CONFIG_SCHEMA)
                    self.install_config = config
                self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.NORMAL))
                self.log_message(f"Loaded config file: {file_path}")
                for btn, version in zip(self.version_buttons, ["XP", "7", "8", "10", "11"]):
                    recommended = self.install_config.get("auto_install", {}).get(version, [])
                    tooltip_text = f"Select Windows {version}\nRecommended: {', '.join(recommended) if recommended else 'None'}"
                    ToolTip(btn, text=tooltip_text)
                self.update_ui_safe(lambda: messagebox.showinfo("Success", f"Loaded {file_path}"))
            except Exception as e:
                self.log_message(f"Failed to load {file_path}: {e}", "ERROR")
                self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to load: {e}"))

    def add_program_dialog(self):
        """Open the add program dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Program")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Add New Program", font=("Segoe UI", 16, "bold")).pack(pady=10)

        program_frame = ttk.Frame(dialog, padding=10)
        program_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(program_frame, text="Name:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        program_name_entry = ttk.Entry(program_frame, font=("Segoe UI", 10))
        program_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_button = ttk.Button(
            program_frame, text="📁 Browse", style="secondary.TButton",
            command=lambda: self.browse_exe(program_name_entry)
        )
        browse_button.pack(side=tk.LEFT, padx=5)

        # Context menu for right-click
        context_menu = tk.Menu(program_frame, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: program_name_entry.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: program_name_entry.event_generate("<<Paste>>"))
        context_menu.add_command(label="Cut", command=lambda: program_name_entry.event_generate("<<Cut>>"))
        program_name_entry.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

        version_frame = ttk.Frame(dialog, padding=10)
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(version_frame, text="Recommended for:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        version_vars = {v: tk.BooleanVar() for v in ["XP", "7", "8", "10", "11"]}
        for version, var in version_vars.items():
            chk = ttk.Checkbutton(
                version_frame, text=f"Win {version}", variable=var, style="info.TCheckbutton"
            )
            chk.pack(side=tk.LEFT, padx=5)

        # Add Program button
        add_button = ttk.Button(
            dialog, text="Add Program", style="success.TButton",
            command=lambda: self.add_program(program_name_entry.get(), version_vars, dialog)
        )
        add_button.pack(pady=15)

        # Bind Enter key to add program
        dialog.bind("<Return>", lambda e: add_button.invoke())

        ttk.Button(dialog, text="Cancel", style="secondary.TButton", command=dialog.destroy).pack(pady=5)

    def browse_exe(self, entry):
        """Browse for .exe files and copy to pro folder"""
        file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if file_path:
            file_path = Path(file_path)
            program_name = file_path.stem.replace(".", "").replace("_", " ")
            pro_dir = self.programs_dir / "pro"  # Changed to programs_dir/pro
            pro_dir.mkdir(exist_ok=True)
            try:
                target_path = pro_dir / file_path.name
                if file_path != target_path:
                    shutil.copy2(file_path, target_path)
                    self.log_message(f"Copied {file_path} to {target_path}")
                relative_path = str(target_path.relative_to(self.programs_dir))  # Relative to programs_dir
                self.software_map[program_name] = {
                    "path": relative_path,
                    "install_time": 2.0
                }
                self.save_software_map()
                entry.delete(0, tk.END)
                entry.insert(0, program_name)
            except Exception as e:
                self.log_message(f"Failed to copy or process {file_path}: {e}", "ERROR")
                self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to process {file_path}: {e}"))

    def add_program(self, program_name, version_vars, dialog):
        """Add a new program"""
        program_name = program_name.strip()
        if not program_name:
            self.update_ui_safe(lambda: messagebox.showerror("Error", "Enter a program name!", parent=dialog))
            self.log_message("Add program failed: no name", "ERROR")
            return

        try:
            if program_name not in self.programs:
                self.programs.append(program_name)
                self.save_programs()
                self.log_message(f"Added program: {program_name}")
            else:
                self.log_message(f"{program_name} already exists", "WARNING")

            for version, var in version_vars.items():
                if var.get():
                    if version not in self.install_config["auto_install"]:
                        self.install_config["auto_install"][version] = []
                    if program_name not in self.install_config["auto_install"][version]:
                        self.install_config["auto_install"][version].append(program_name)
                        self.log_message(f"Added {program_name} to auto-install for {version}")
            with (self.programs_dir / "install_config.json").open("w", encoding="utf-8") as f:
                json.dump(self.install_config, f, ensure_ascii=False, indent=4)

            self.populate_programs()
            self.update_ui_safe(lambda: [
                messagebox.showinfo("Success", f"{program_name} added!", parent=dialog),
                dialog.destroy()
            ])
        except Exception as e:
            error_message = str(e)
            self.log_message(f"Failed to add {program_name}: {error_message}", "ERROR")
            self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to add {program_name}: {error_message}", parent=dialog))

    def remove_selection(self):
        """Clear selections"""
        self.selected_version = None
        for program, (var, _) in self.check_vars.items():
            var.set(False)
        self.update_ui_safe(lambda: self.status_label.config(text="Ready"))
        self.update_ui_safe(lambda: self.start_button.config(state=tk.DISABLED))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.DISABLED))
        for btn in self.version_buttons:
            self.update_ui_safe(lambda b=btn: b.config(style="primary.TButton"))
        self.populate_programs()
        self.log_message("Cleared selections")

    def start_installation(self):
        """Start installation"""
        self.log_message("Start installation initiated")
        if self.is_installing:
            self.log_message("Installation already in progress", "WARNING")
            self.update_ui_safe(lambda: messagebox.showwarning("Warning", "Installation in progress!"))
            return
        selected_programs = []
        total_weight = 0
        for program, (var, _) in self.check_vars.items():
            if var.get():
                selected_programs.append(program)
                total_weight += self.software_map.get(program, {}).get("install_time", 2.0)
        if not selected_programs:
            self.update_ui_safe(lambda: messagebox.showwarning("Warning", "No programs selected!"))
            self.log_message("No programs selected for installation", "WARNING")
            return

        self.is_installing = True
        self.cancel_event.clear()
        self.update_ui_safe(lambda: self.start_button.config(state=tk.DISABLED))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.DISABLED))
        self.update_ui_safe(lambda: self.cancel_button.config(state=tk.NORMAL))
        self.update_ui_safe(lambda: self.status_label.config(text="Installing..."))
        self.start_time = time.time()
        self.install_thread = threading.Thread(target=self.install_programs, args=(selected_programs, total_weight))
        self.install_thread.start()
        self.update_progress()

    def start_auto_installation(self):
        """Start auto installation"""
        self.log_message("Auto installation initiated")
        if self.is_installing:
            self.update_ui_safe(lambda: messagebox.showwarning("Warning", "Installation in progress!"))
            self.log_message(f"Auto installation attempted during active installation", "WARNING")
            return
        if not self.selected_version:
            self.update_ui_safe(lambda: messagebox.showwarning("Error", "Select a Windows version!"))
            self.log_message("No Windows version selected for auto-installation", "ERROR")
            return
        recommended = self.install_config.get("auto_install", {}).get(self.selected_version, [])
        if not recommended:
            self.update_ui_safe(lambda: messagebox.showwarning("Warning", f"No programs configured for {self.selected_version}!"))
            return

        for program, (var, _) in self.check_vars.items():
            var.set(program in recommended)
        self.start_installation()

    def cancel_installation(self):
        """Cancel the ongoing installation"""
        self.log_message("Installation cancellation requested")
        if not self.is_installing:
            return
        self.is_installing = False
        self.cancel_event.set()
        self.install_thread = None
        self.update_ui_safe(lambda: self.status_label.config(text="Cancelled"))
        self.update_ui_safe(lambda: self.cancel_button.config(state=tk.DISABLED))
        self.update_ui_safe(lambda: self.start_button.config(state=tk.NORMAL))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.NORMAL))
        self.update_ui_safe(lambda: self.progress.config(value=0))
        self.update_ui_safe(lambda: self.progress_label.config(text="0%"))
        self.update_ui_safe(lambda: self.elapsed_time_label.config(text="Elapsed: 0s"))
        self.log_message("Installation cancelled")

    def install_programs(self, programs, total_weight):
        """Install selected programs"""
        current_weight = 0
        for program in programs:
            if self.cancel_event.is_set():
                self.log_message(f"{self.selected_version} - Installation cancelled during processing")
                break
            self.update_ui_safe(lambda p=program: self.status_label.config(text=f"Installing {p}..."))
            self.log_message(f"Installing {program}")
            try:
                if self.testing_mode:
                    install_time = self.software_map.get(program, {}).get("install_time", 2.0)
                    time.sleep(install_time)
                    self.log_message(f"Simulated installation of {program}")
                else:
                    exe_path = self.programs_dir / self.software_map.get(program, {}).get("path", f"pro/{program}.exe")
                    if not exe_path.exists():
                        raise FileNotFoundError(f"Executable not found: {exe_path}")
                    subprocess.run([str(exe_path)], check=True)
                    self.log_message(f"Installed {program} successfully")
                current_weight += self.software_map.get(program, {}).get("install_time", 2.0)
                self.update_ui_safe(lambda w=current_weight, t=total_weight: self.progress.config(value=(w / t) * 100))
                self.update_ui_safe(lambda v=int(self.progress['value']): self.progress_label.config(text=f"{v}%"))
            except Exception as e:
                self.log_message(f"Failed to install {program}: {e}", "ERROR")
                self.update_ui_safe(lambda p=program, ex=e: messagebox.showerror("Error", f"Failed to install {p}: {ex}\nContinue installation?", parent=self.root))
                if not messagebox.askyesno("Continue", f"Failed to install {program}. Continue?", parent=self.root):
                    self.cancel_installation()
                    break
        if not self.cancel_event.is_set():
            self.finalize_installation()

    def update_progress(self):
        """Update progress time"""
        if self.is_installing:
            elapsed = time.time() - self.start_time
            self.update_ui_safe(lambda: self.elapsed_time_label.config(text=f"Elapsed: {int(elapsed)}s"))
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after(1000, self.update_progress)
            except Exception as e:
                self.log_message(f"Progress update failed: {e}", "ERROR")

    def finalize_installation(self):
        """Finalize installation"""
        self.is_installing = False
        self.install_thread = None
        self.update_ui_safe(lambda: self.status_label.config(text="Completed"))
        self.update_ui_safe(lambda: self.cancel_button.config(state=tk.DISABLED))
        self.update_ui_safe(lambda: self.start_button.config(state=tk.NORMAL))
        self.update_ui_safe(lambda: self.auto_install_button.config(state=tk.NORMAL))
        try:
            winsound.Beep(1000, 500)
        except Exception as e:
            self.log_message(f"Beep failed: {e}", "ERROR")

        self.log_message("Installation completed")

        action = self.action_var.get()
        self.log_message(f"Selected post-installation action: {action}")

        if action == "2":
            self.log_message("Application Exit")
            self.update_ui_safe(lambda: self.root.destroy())
        elif action == "3":
            self.log_message("Initiating system reboot")
            try:
                subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
            except Exception as e:
                self.log_message(f"Failed to reboot: {e}", "ERROR")
                self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to reboot: {e}"))
        elif action == "4":
            self.log_message("Initiating system shutdown")
            try:
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
            except Exception as e:
                self.log_message(f"Failed to shutdown: {e}", "ERROR")
                self.update_ui_safe(lambda: messagebox.showerror("Error", f"Failed to shutdown: {e}"))

    def log_message(self, message, level="INFO"):
        """Log a message"""
        self.logger.log(getattr(logging, level), f"{self.selected_version or 'No version selected'} - {message}")

if __name__ == "__main__":
    root = tk.Tk() if not ttkbootstrap_available else ttk.Window()
    app = InstallerApp(root)
    root.mainloop()