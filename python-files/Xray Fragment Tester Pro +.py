"""
Project: Xray Fragment Tester Pro +
Author: github.com/sasanxxx updated
Version: 3.1.1
Description: Automated fragment optimization with real-time scanning and results display
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import subprocess
import os
import platform
import threading
import time
from typing import Dict, Tuple, List, Optional
from core import generate_config, scan_optimal_fragments

# Constants
BEST_RESULT_FILENAME = "best_result.json"
CONFIG_FILENAME = "params.json"
BASE_CONFIG_FILENAME = "Xray_Config (Fragment).json"
MAIN_SCRIPT = "A.py"
SCAN_LOG_FILE = "scan.log"

DEFAULT_PARAMS = {
    "fragment_length": "5-10, 20-40",
    "fragment_interval": "10-20, 20-30",
    "server_name": "www.google.com, www.microsoft.com",
    "dns_server_url": "https://dns.google/dns-query, https://cloudflare-dns.com/dns-query",
    "websites_to_test": "https://www.google.com, https://www.youtube.com"
}

DEFAULT_BASE_CONFIG = {
    "inbounds": [
        {
            "port": 1080,
            "protocol": "socks",
            "settings": {
                "auth": "noauth",
                "udp": True
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        },
        {
            "protocol": "blackhole",
            "settings": {},
            "tag": "blocked"
        }
    ],
    "routing": {
        "rules": [
            {
                "type": "field",
                "ip": [
                    "geoip:private"
                ],
                "outboundTag": "blocked"
            }
        ]
    }
}

THEME = {
    "bg": "#f5f7fa",
    "fg": "#2d3748",
    "primary": "#4a6fa5",
    "secondary": "#6c757d",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "light": "#e9ecef",
    "dark": "#343a40",
    "font": ("Segoe UI", 10),
    "font_bold": ("Segoe UI", 10, "bold"),
    "font_title": ("Segoe UI", 12, "bold"),
    "font_mono": ("Consolas", 9)
}


class XrayFragmentTester:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Xray Fragment Tester Pro +")
        self.root.geometry("900x700")
        self.root.configure(bg=THEME["bg"])
        self.root.minsize(800, 600)
        
        self.entries: Dict[str, ttk.Entry] = {}
        self.scan_thread: Optional[threading.Thread] = None
        self.test_process: Optional[subprocess.Popen] = None
        self.scan_active = False
        self.test_active = False
        self.best_params = self.load_initial_params()
        self.base_config_path = BASE_CONFIG_FILENAME
        
        # Create default files if missing
        self.ensure_base_config_exists()
        
        # Setup custom styles
        self.setup_styles()
        self.setup_ui()
        self.center_window()

    def ensure_base_config_exists(self):
        """Create default base config if it doesn't exist"""
        if not os.path.exists(BASE_CONFIG_FILENAME):
            try:
                with open(BASE_CONFIG_FILENAME, 'w', encoding='utf-8') as f:
                    json.dump(DEFAULT_BASE_CONFIG, f, indent=2)
                print(f"Created default base config: {BASE_CONFIG_FILENAME}")
            except Exception as e:
                print(f"Error creating base config: {str(e)}")

    def setup_styles(self):
        """Configure widget styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure("TFrame", background=THEME["bg"])
        style.configure("Header.TFrame", background=THEME["primary"])
        
        # Label styles
        style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"], font=THEME["font"])
        style.configure("Header.TLabel", background=THEME["primary"], foreground="white", font=THEME["font_title"])
        style.configure("Status.TLabel", background=THEME["dark"], foreground="white", font=THEME["font_mono"])
        
        # Button styles
        style.configure("TButton", font=THEME["font_bold"], padding=6)
        style.map("TButton", background=[("active", THEME["light"])])
        
        for color_name, color_code in THEME.items():
            if color_name in ["primary", "success", "warning", "danger"]:
                style.configure(
                    f"{color_name}.TButton", 
                    foreground="white" if color_name != "warning" else "black",
                    background=color_code,
                    bordercolor=color_code,
                    focuscolor=color_code
                )
                style.map(
                    f"{color_name}.TButton",
                    background=[("active", self.darken_color(color_code))]
                )
        
        # Entry styles
        style.configure("TEntry", fieldbackground="white", font=THEME["font"])
        
        # Notebook styles
        style.configure("TNotebook", background=THEME["bg"])
        style.configure("TNotebook.Tab", background=THEME["light"], padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", THEME["primary"])], 
                foreground=[("selected", "white")])
        
    def darken_color(self, hex_color: str, factor=0.8) -> str:
        """Darken a hex color by a factor"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def load_initial_params(self) -> Dict:
        """Load initial parameters from best result or defaults"""
        try:
            if os.path.exists(BEST_RESULT_FILENAME):
                with open(BEST_RESULT_FILENAME, 'r', encoding='utf-8') as f:
                    params = json.load(f)
                
                if os.path.exists(CONFIG_FILENAME):
                    with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                        last_params = json.load(f)
                    params["websites_to_test"] = ", ".join(last_params["websites_to_test"])
                return params
        except Exception:
            pass
        return DEFAULT_PARAMS

    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header = ttk.Label(
            header_frame, 
            text="XRAY FRAGMENT TESTER PRO", 
            style="Header.TLabel"
        )
        header.pack(pady=10)
        
        # Tab control
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        
        # Form container
        form_frame = ttk.LabelFrame(config_frame, text="Connection Parameters")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create form fields
        self.create_form_fields(form_frame)
        
        # Results Tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Test Results")
        
        # Log viewer
        log_frame = ttk.LabelFrame(results_frame, text="Scanning & Testing Logs")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            font=THEME["font_mono"],
            bg="#2d3748",
            fg="#e9ecef",
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Button container
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        # Action buttons
        self.create_buttons(button_frame)
        
        # Status bar
        status_frame = ttk.Frame(self.root, height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            style="Status.TLabel",
            anchor=tk.W,
            padding=(10, 0)
        )
        status_bar.pack(fill=tk.X)

    def create_form_fields(self, parent: ttk.Frame):
        """Create the configuration form fields"""
        labels = {
            "fragment_length": "Fragment Length:",
            "fragment_interval": "Fragment Interval:",
            "server_name": "Server Name:",
            "dns_server_url": "DNS Server URL:",
            "websites_to_test": "Websites to Test:"
        }
        
        for i, (key, text) in enumerate(labels.items()):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, padx=10, pady=8)
            
            label = ttk.Label(row_frame, text=text, width=20, anchor=tk.W)
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            entry = ttk.Entry(row_frame, width=60)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Set initial values
            default_value = self.best_params.get(key, DEFAULT_PARAMS.get(key, ""))
            entry.insert(0, default_value)
            self.entries[key] = entry

    def create_buttons(self, parent: ttk.Frame):
        """Create action buttons"""
        buttons = [
            ("Scan Optimal Fragments", self.scan_optimal_fragments, "primary"),
            ("Start Test", self.start_test, "success"),
            ("Generate Config", self.generate_manual_config, "warning"),
            ("Stop Test", self.stop_test, "danger"),
            ("Select Config", self.select_base_config, "secondary")
        ]
        
        for text, command, color in buttons:
            btn = ttk.Button(
                parent,
                text=text,
                command=command,
                style=f"{color}.TButton" if color != "secondary" else "TButton",
                width=20
            )
            btn.pack(side=tk.LEFT, padx=5, expand=True)

    def log_message(self, message: str):
        """Add message to log viewer"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

    def clear_log(self):
        """Clear the log viewer"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def get_params_from_gui(self, single_values: bool = False) -> Dict:
        """Get parameters from GUI with validation"""
        params = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                raise ValueError(f"Field '{key.replace('_', ' ').title()}' cannot be empty.")
            
            if single_values:
                params[key] = value.split(',')[0].strip()
            else:
                params[key] = [s.strip() for s in value.split(',')]
        return params

    def scan_optimal_fragments(self):
        """Scan for optimal fragment parameters"""
        if self.scan_active:
            messagebox.showinfo("Info", "Scan is already in progress")
            return
            
        self.clear_log()
        self.log_message("=== STARTING FRAGMENT OPTIMIZATION SCAN ===")
        self.log_message("Analyzing current internet connection...")
        self.status_var.set("Scanning for optimal fragments...")
        
        # Disable scan button during operation
        self.scan_active = True
        
        # Run scan in background thread
        self.scan_thread = threading.Thread(target=self.run_fragment_scan, daemon=True)
        self.scan_thread.start()

    def run_fragment_scan(self):
        """Run the fragment scan in a background thread"""
        try:
            # Perform actual fragment scanning
            optimal_length, optimal_interval = scan_optimal_fragments()
            
            self.log_message(f"Optimal fragment length found: {optimal_length}")
            self.log_message(f"Optimal fragment interval found: {optimal_interval}")
            
            # Update GUI with results
            self.root.after(0, lambda: self.update_fragment_fields(optimal_length, optimal_interval))
            self.log_message("Scan completed successfully!")
            self.status_var.set("Optimal fragments found and applied")
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
            self.log_message(f"ERROR: {str(e)}")
            self.status_var.set("Scan failed")
        finally:
            self.scan_active = False

    def update_fragment_fields(self, length: str, interval: str):
        """Update fragment fields with optimal values"""
        self.entries["fragment_length"].delete(0, tk.END)
        self.entries["fragment_length"].insert(0, length)
        
        self.entries["fragment_interval"].delete(0, tk.END)
        self.entries["fragment_interval"].insert(0, interval)
        
        self.log_message("Fragment parameters updated with optimal values")

    def start_test(self):
        """Start the fragment test"""
        if self.test_active:
            messagebox.showinfo("Info", "Test is already running")
            return
            
        try:
            # Get parameters with optimized fragments
            params = self.get_params_from_gui()
            
            # Save parameters
            with open(CONFIG_FILENAME, "w", encoding='utf-8') as f:
                json.dump(params, f, indent=2)
            
            # Prepare test environment
            script_path = os.path.join(os.path.dirname(__file__), MAIN_SCRIPT)
            if not os.path.exists(script_path):
                messagebox.showerror("Error", f"Main script file '{MAIN_SCRIPT}' not found.")
                return
            
            self.clear_log()
            self.log_message("=== STARTING FRAGMENT TEST ===")
            self.log_message("Using parameters:")
            for key, value in params.items():
                self.log_message(f"  {key}: {', '.join(value)}")
            
            self.status_var.set("Test running...")
            self.test_active = True
            
            # Run test in background
            test_thread = threading.Thread(target=self.run_fragment_test, args=(script_path,), daemon=True)
            test_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_message(f"ERROR: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")

    def run_fragment_test(self, script_path: str):
        """Run the fragment test in a background thread"""
        try:
            # Platform-specific command execution
            if platform.system() == "Windows":
                self.test_process = subprocess.Popen(
                    f'python "{script_path}"',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.test_process = subprocess.Popen(
                    f'python3 "{script_path}"',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    shell=True
                )
            
            # Stream output to log viewer
            while True:
                output = self.test_process.stdout.readline()
                if output == '' and self.test_process.poll() is not None:
                    break
                if output:
                    self.root.after(0, lambda: self.log_message(output.strip()))
            
            # Process completed
            self.root.after(0, self.test_completed)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Test Error", str(e)))
            self.log_message(f"ERROR: {str(e)}")
            self.status_var.set("Test failed")
        finally:
            self.test_active = False

    def test_completed(self):
        """Handle test completion"""
        self.log_message("\n=== TEST COMPLETED ===")
        self.status_var.set("Test completed")
        self.test_active = False
        
        # Load and show best results
        try:
            if os.path.exists(BEST_RESULT_FILENAME):
                with open(BEST_RESULT_FILENAME, 'r', encoding='utf-8') as f:
                    best_params = json.load(f)
                
                self.log_message("\nBEST RESULTS:")
                self.log_message(f"Fragment Length: {best_params.get('fragment_length', 'N/A')}")
                self.log_message(f"Fragment Interval: {best_params.get('fragment_interval', 'N/A')}")
                self.log_message(f"Speed Improvement: {best_params.get('speed_improvement', 'N/A')}%")
                self.log_message(f"Stability: {best_params.get('stability', 'N/A')}")
                
        except Exception as e:
            self.log_message(f"ERROR loading results: {str(e)}")

    def stop_test(self):
        """Stop the running test"""
        if self.test_active and self.test_process:
            self.test_process.terminate()
            self.log_message("=== TEST STOPPED BY USER ===")
            self.status_var.set("Test stopped")
            self.test_active = False
        else:
            messagebox.showinfo("Info", "No active test to stop")

    def select_base_config(self):
        """Allow user to select base config file"""
        file_path = filedialog.askopenfilename(
            title="Select Base Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=BASE_CONFIG_FILENAME
        )
        if file_path:
            self.base_config_path = file_path
            self.log_message(f"Selected base config: {os.path.basename(file_path)}")
            self.status_var.set(f"Base config: {os.path.basename(file_path)}")

    def generate_config_from_params(self, params: Dict):
        """Generate configuration from parameters"""
        try:
            if not os.path.exists(self.base_config_path):
                choice = messagebox.askyesno(
                    "Config Not Found",
                    f"Base config file not found at:\n{self.base_config_path}\n\n"
                    "Would you like to create a default configuration?",
                    icon=messagebox.WARNING
                )
                if choice:
                    self.ensure_base_config_exists()
                else:
                    return
            
            with open(self.base_config_path, "r", encoding='utf-8') as f:
                base_config = json.load(f)
            
            final_config = generate_config(base_config, params)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Config As...",
                initialfile="optimized_config.json"
            )
            
            if file_path:
                with open(file_path, "w", encoding='utf-8') as f:
                    json.dump(final_config, f, indent=2)
                messagebox.showinfo("Success", f"Optimized configuration saved to:\n{file_path}")
                self.status_var.set(f"Config saved to {os.path.basename(file_path)}")
                self.log_message(f"Generated config saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {str(e)}")
            self.log_message(f"CONFIG ERROR: {str(e)}")

    def generate_manual_config(self):
        """Generate config from manual entries"""
        try:
            params = self.get_params_from_gui(single_values=True)
            self.generate_config_from_params(params)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {str(e)}")
            self.log_message(f"CONFIG ERROR: {str(e)}")

    def on_closing(self):
        """Handle window closing event"""
        if self.scan_active:
            if messagebox.askokcancel("Quit", "Scan is in progress. Are you sure you want to quit?"):
                self.root.destroy()
        elif self.test_active:
            if messagebox.askokcancel("Quit", "Test is running. Are you sure you want to quit?"):
                self.stop_test()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = XrayFragmentTester(root)
    
    # Set closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()