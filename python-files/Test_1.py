import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import subprocess
from datetime import datetime, time
import winreg
import threading

class StartupScheduler:
    def __init__(self):
        self.config_file = "scheduler_config.json"
        self.app_name = "StartupScheduler"
        self.config = self.load_config()
        
        # Check if running from startup
        self.is_startup_run = self.check_startup_execution()
        
        if self.is_startup_run:
            self.check_and_run_program()
            return
        
        self.create_gui()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "start_time": "09:00",
            "end_time": "17:00",
            "selected_program": "",
            "enabled": False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
        except Exception as e:
            print(f"Error loading config: {e}")
            # If there's an error, try to backup the corrupted file
            if os.path.exists(self.config_file):
                try:
                    backup_name = f"{self.config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.rename(self.config_file, backup_name)
                    print(f"Corrupted config backed up to: {backup_name}")
                except:
                    pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def check_startup_execution(self):
        """Check if the program is running from startup"""
        # Simple check - if no display available, likely running from startup
        try:
            # If we can create a test window, we're in interactive mode
            test_root = tk.Tk()
            test_root.withdraw()
            test_root.destroy()
            return len(sys.argv) > 1 and sys.argv[1] == "--startup"
        except:
            return True
    
    def check_and_run_program(self):
        """Check if current time is within range and run program if needed"""
        if not self.config.get("enabled", False) or not self.config.get("selected_program"):
            return
        
        current_time = datetime.now().time()
        start_time = datetime.strptime(self.config["start_time"], "%H:%M").time()
        end_time = datetime.strptime(self.config["end_time"], "%H:%M").time()
        
        # Handle overnight time ranges
        if start_time <= end_time:
            in_range = start_time <= current_time <= end_time
        else:
            in_range = current_time >= start_time or current_time <= end_time
        
        if in_range:
            try:
                subprocess.Popen(self.config["selected_program"], shell=True)
                print(f"Started program: {self.config['selected_program']}")
            except Exception as e:
                print(f"Failed to start program: {e}")
    
    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Scheduler")
        self.root.geometry("400x500")
        self.root.configure(bg='white')
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure minimal styles
        style.configure('Title.TLabel', font=('Arial', 16), background='white', foreground='black')
        style.configure('Soft.TFrame', background='white')
        style.configure('Black.TButton', background='black', foreground='white', font=('Arial', 10))
        style.configure('Gray.TButton', background='#f0f0f0', foreground='black', font=('Arial', 10))
        
        self.create_widgets()
        self.load_current_values()
        
        # Bind window close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Soft.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Scheduler", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Time settings frame
        time_frame = ttk.LabelFrame(main_frame, text="Time Settings", padding="10")
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Start time
        start_frame = ttk.Frame(time_frame)
        start_frame.pack(fill=tk.X, pady=5)
        ttk.Label(start_frame, text="Start Time:").pack(side=tk.LEFT)
        self.start_time_var = tk.StringVar()
        start_entry = ttk.Entry(start_frame, textvariable=self.start_time_var, width=10)
        start_entry.pack(side=tk.RIGHT)
        ttk.Label(start_frame, text="(HH:MM)").pack(side=tk.RIGHT, padx=(0, 10))
        
        # End time
        end_frame = ttk.Frame(time_frame)
        end_frame.pack(fill=tk.X, pady=5)
        ttk.Label(end_frame, text="End Time:").pack(side=tk.LEFT)
        self.end_time_var = tk.StringVar()
        end_entry = ttk.Entry(end_frame, textvariable=self.end_time_var, width=10)
        end_entry.pack(side=tk.RIGHT)
        ttk.Label(end_frame, text="(HH:MM)").pack(side=tk.RIGHT, padx=(0, 10))
        
        # Program selection frame
        program_frame = ttk.LabelFrame(main_frame, text="Program Settings", padding="10")
        program_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Selected program display
        self.program_var = tk.StringVar()
        program_label = ttk.Label(program_frame, textvariable=self.program_var, 
                                 wraplength=350, background='white', relief='solid', padding="8")
        program_label.pack(fill=tk.X, pady=(0, 10))
        
        # Browse button
        browse_btn = tk.Button(program_frame, text="Browse", 
                              command=self.browse_program,
                              bg='black', fg='white', font=('Arial', 10),
                              relief='flat', padx=15, pady=5)
        browse_btn.pack(pady=5)
        
        # Enable/Disable checkbox
        self.enabled_var = tk.BooleanVar()
        enabled_check = ttk.Checkbutton(program_frame, text="Enable scheduled execution", 
                                       variable=self.enabled_var)
        enabled_check.pack(pady=10)
        
        # Startup settings frame
        startup_frame = ttk.LabelFrame(main_frame, text="Windows Startup", padding="10")
        startup_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Startup status
        self.startup_status_var = tk.StringVar()
        status_label = ttk.Label(startup_frame, textvariable=self.startup_status_var)
        status_label.pack(pady=5)
        
        startup_btn_frame = ttk.Frame(startup_frame)
        startup_btn_frame.pack(fill=tk.X)
        
        add_startup_btn = tk.Button(startup_btn_frame, text="Add to Startup", 
                                   command=self.add_to_startup,
                                   bg='#f0f0f0', fg='black', font=('Arial', 10),
                                   relief='flat', padx=10, pady=5)
        add_startup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_startup_btn = tk.Button(startup_btn_frame, text="Remove from Startup", 
                                      command=self.remove_from_startup,
                                      bg='#f0f0f0', fg='black', font=('Arial', 10),
                                      relief='flat', padx=10, pady=5)
        remove_startup_btn.pack(side=tk.LEFT)
        
        # Save button
        save_btn = tk.Button(main_frame, text="Save Settings", 
                            command=self.save_settings,
                            bg='black', fg='white', font=('Arial', 12),
                            relief='flat', padx=20, pady=10)
        save_btn.pack(pady=15)
        
        # Update startup status
        self.update_startup_status()
    
    def load_current_values(self):
        """Load current configuration values into GUI"""
        self.start_time_var.set(self.config["start_time"])
        self.end_time_var.set(self.config["end_time"])
        self.enabled_var.set(self.config.get("enabled", False))
        
        program_text = self.config.get("selected_program", "")
        if program_text:
            # Show full path for better clarity
            self.program_var.set(f"Selected: {program_text}")
        else:
            self.program_var.set("No program selected")
    
    def browse_program(self):
        """Open file dialog to select a program"""
        file_path = filedialog.askopenfilename(
            title="Select Program to Run",
            filetypes=[
                ("Executable files", "*.exe"),
                ("Batch files", "*.bat"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.config["selected_program"] = file_path
            self.program_var.set(f"Selected: {os.path.basename(file_path)}")
    
    def validate_time_format(self, time_str):
        """Validate time format HH:MM"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def save_settings(self):
        """Save all settings"""
        # Validate time formats
        start_time = self.start_time_var.get()
        end_time = self.end_time_var.get()
        
        if not self.validate_time_format(start_time):
            messagebox.showerror("Invalid Time", "Start time must be in HH:MM format")
            return
        
        if not self.validate_time_format(end_time):
            messagebox.showerror("Invalid Time", "End time must be in HH:MM format")
            return
        
        # Update configuration
        self.config["start_time"] = start_time
        self.config["end_time"] = end_time
        self.config["enabled"] = self.enabled_var.get()
        
        # Keep the selected program path if it exists
        if not self.config.get("selected_program") and self.program_var.get() != "No program selected":
            # Extract program path from display text
            program_text = self.program_var.get()
            if program_text.startswith("Selected: "):
                self.config["selected_program"] = program_text[10:]  # Remove "Selected: " prefix
        
        # Save to file
        self.save_config()
        messagebox.showinfo("Success", "Settings saved successfully!")
        
        # Update the display to show the saved values
        self.load_current_values()
    
    def get_executable_path(self):
        """Get the path to the current executable or script"""
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            return f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    
    def add_to_startup(self):
        """Add program to Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            executable_path = self.get_executable_path()
            startup_command = f"{executable_path} --startup"
            
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            
            messagebox.showinfo("Success", "Program added to Windows startup!")
            self.update_startup_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to startup: {e}")
    
    def remove_from_startup(self):
        """Remove program from Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            
            messagebox.showinfo("Success", "Program removed from Windows startup!")
            self.update_startup_status()
        except FileNotFoundError:
            messagebox.showinfo("Info", "Program was not in startup registry")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove from startup: {e}")
    
    def is_in_startup(self):
        """Check if program is in Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            
            try:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def update_startup_status(self):
        """Update the startup status display"""
        if self.is_in_startup():
            self.startup_status_var.set("✓ Program is in Windows startup")
        else:
            self.startup_status_var.set("✗ Program is NOT in Windows startup")
    
    def on_closing(self):
        """Handle window closing - save settings automatically"""
        try:
            # Save current settings before closing
            self.save_settings()
        except Exception as e:
            print(f"Error saving settings on close: {e}")
        
        self.root.destroy()

if __name__ == "__main__":
    app = StartupScheduler()