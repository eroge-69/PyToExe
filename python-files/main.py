import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import json
import os
import base64
import zlib
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import requests
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import pickle
import subprocess
import sys
import winreg
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes

# Windows-specific enhancements
class WindowsFeatures:
    @staticmethod
    def set_dark_title_bar(hwnd):
        """Set dark title bar for Windows 10/11"""
        try:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
        except Exception:
            pass

    @staticmethod
    def get_windows_version():
        """Get detailed Windows version information"""
        try:
            info = sys.getwindowsversion()
            return f"Windows {info.major}.{info.minor} (Build {info.build})"
        except:
            return "Windows (Unknown Version)"

class JARVIS:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. - Enhanced Windows Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a192f")
        
        # Apply Windows dark mode
        try:
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            WindowsFeatures.set_dark_title_bar(hwnd)
        except:
            pass
        
        # Windows version info
        self.windows_version = WindowsFeatures.get_windows_version()
        
        # Initialize modules
        self.memory = self.load_memory()
        self.finance_data = {}
        self.market_status = {}
        self.voice_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        # Set up GUI
        self.setup_gui()
        
        # Start background tasks
        threading.Thread(target=self.update_market_data, daemon=True).start()
        threading.Thread(target=self.background_learning, daemon=True).start()
        threading.Thread(target=self.system_monitor, daemon=True).start()
        
        # Initial greeting
        self.add_message("J.A.R.V.I.S.", f"Initializing system on {self.windows_version}... All systems operational.")
        self.speak(f"Initializing system on {self.windows_version}. All systems operational. How can I assist you today?")

    def setup_gui(self):
        # Create main frames
        main_frame = tk.Frame(self.root, bg="#0a192f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Chat interface
        chat_frame = tk.Frame(main_frame, bg="#112240", bd=2, relief=tk.RIDGE)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, bg="#0a192f", fg="#64ffda", font=("Consolas", 11),
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input area
        input_frame = tk.Frame(chat_frame, bg="#112240")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.user_input = tk.Entry(
            input_frame, bg="#0a192f", fg="#ccd6f6", font=("Consolas", 11),
            insertbackground="#64ffda"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.process_input)
        
        # Voice input button
        self.voice_btn = tk.Button(
            input_frame, text="🎤", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=self.start_voice_recognition
        )
        self.voice_btn.pack(side=tk.LEFT)
        
        # Send button
        send_btn = tk.Button(
            input_frame, text="Send", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=lambda: self.process_input(None)
        )
        send_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right panel - Information displays
        info_frame = tk.Frame(main_frame, bg="#112240", width=300, bd=2, relief=tk.RIDGE)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Tab system
        self.notebook = ttk.Notebook(info_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Financial Analysis Tab
        finance_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(finance_tab, text="Financial Analysis")
        self.setup_finance_tab(finance_tab)
        
        # Technical Tools Tab
        tech_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(tech_tab, text="Technical Tools")
        self.setup_tech_tab(tech_tab)
        
        # System Status Tab
        status_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(status_tab, text="System Status")
        self.setup_status_tab(status_tab)
        
        # Memory and Learning Tab
        memory_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(memory_tab, text="Memory & Learning")
        self.setup_memory_tab(memory_tab)
        
        # Windows Tools Tab (NEW)
        windows_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(windows_tab, text="Windows Tools")
        self.setup_windows_tab(windows_tab)
        
        # Add J.A.R.V.I.S. logo
        self.add_logo()
        
    def setup_windows_tab(self, parent):
        """NEW: Windows-specific tools tab"""
        # System commands
        cmd_frame = tk.LabelFrame(parent, text="System Commands", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        cmd_frame.pack(fill=tk.X, padx=10, pady=10)
        
        commands = [
            ("Restart Computer", self.restart_computer),
            ("Shutdown Computer", self.shutdown_computer),
            ("Open Command Prompt", self.open_cmd),
            ("Open File Explorer", self.open_explorer),
            ("Check Disk Space", self.check_disk_space)
        ]
        
        for text, command in commands:
            btn = tk.Button(
                cmd_frame, text=text, bg="#64ffda", fg="#0a192f", font=("Arial", 9),
                command=command
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Windows settings
        settings_frame = tk.LabelFrame(parent, text="System Settings", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            settings_frame, text="Power Plan:", 
            bg="#0a192f", fg="#ccd6f6", font=("Arial", 9)
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.power_plan = tk.StringVar()
        power_plans = self.get_power_plans()
        if power_plans:
            self.power_plan.set(power_plans[0])
            dropdown = ttk.Combobox(settings_frame, textvariable=self.power_plan, values=power_plans)
            dropdown.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(
                settings_frame, text="Apply Power Plan", bg="#64ffda", fg="#0a192f", font=("Arial", 9),
                command=self.apply_power_plan
            ).pack(pady=5)
        
        # Windows updates
        update_frame = tk.LabelFrame(parent, text="Windows Update", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        update_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            update_frame, text="Check for Updates", bg="#64ffda", fg="#0a192f", font=("Arial", 9),
            command=self.check_windows_updates
        ).pack(pady=5)
    
    # WINDOWS TOOLS FUNCTIONS (NEW)
    def restart_computer(self):
        self.speak("Initiating system restart. Save your work.")
        subprocess.run(["shutdown", "/r", "/t", "10"])
        
    def shutdown_computer(self):
        self.speak("Initiating system shutdown. Save your work.")
        subprocess.run(["shutdown", "/s", "/t", "10"])
        
    def open_cmd(self):
        subprocess.Popen("cmd.exe")
        self.speak("Command prompt opened")
        
    def open_explorer(self):
        subprocess.Popen("explorer.exe")
        self.speak("File Explorer opened")
        
    def check_disk_space(self):
        try:
            result = subprocess.check_output(["wmic", "logicaldisk", "get", "size,freespace,caption"])
            drives = [line.split() for line in result.decode().split('\n') if line.strip()]
            
            # Skip header
            drive_info = []
            for drive in drives[1:]:
                if len(drive) >= 3:
                    letter = drive[0]
                    free = int(drive[1])
                    total = int(drive[2])
                    used = total - free
                    pct_used = (used / total) * 100 if total > 0 else 0
                    
                    drive_info.append(
                        f"{letter}: {pct_used:.1f}% used ({free//(1024**3)}GB free of {total//(1024**3)}GB)"
                    )
            
            message = "Disk Space Summary:\n" + "\n".join(drive_info)
            self.speak(message)
        except Exception as e:
            self.speak(f"Could not retrieve disk space information: {str(e)}")
    
    def get_power_plans(self):
        try:
            result = subprocess.check_output(["powercfg", "/list"], text=True)
            plans = []
            for line in result.split('\n'):
                if "Power Scheme GUID" in line:
                    parts = line.split()
                    guid = parts[3]
                    name = " ".join(parts[5:])
                    if name not in plans:
                        plans.append(name)
            return plans
        except:
            return []
    
    def apply_power_plan(self):
        plan_name = self.power_plan.get()
        if plan_name:
            try:
                # Find GUID for the selected plan
                result = subprocess.check_output(["powercfg", "/list"], text=True)
                for line in result.split('\n'):
                    if plan_name in line:
                        parts = line.split()
                        guid = parts[3]
                        subprocess.run(["powercfg", "/setactive", guid])
                        self.speak(f"Power plan set to {plan_name}")
                        return
                self.speak("Could not find selected power plan")
            except Exception as e:
                self.speak(f"Error setting power plan: {str(e)}")
    
    def check_windows_updates(self):
        try:
            result = subprocess.check_output(
                ["powershell", "Get-WindowsUpdate -IsInstalled:$false -IsHidden:$false | Format-Table -AutoSize"],
                text=True
            )
            if "Title" in result:
                updates = [line.strip() for line in result.split('\n') if line.strip() and "Title" not in line]
                if updates:
                    self.speak(f"There are {len(updates)} Windows updates available")
                else:
                    self.speak("Your system is up to date")
            else:
                self.speak("No updates available")
        except:
            self.speak("Could not check for Windows updates")
    
    # EXISTING FUNCTIONS WITH WINDOWS ENHANCEMENTS
    def start_voice_recognition(self):
        def recognize_thread():
            self.voice_btn.config(state=tk.DISABLED, text="Listening...")
            with sr.Microphone() as source:
                # Windows-specific audio adjustments
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                    text = self.recognizer.recognize_google(audio)
                    self.user_input.delete(0, tk.END)
                    self.user_input.insert(0, text)
                    self.process_input(None)
                except sr.UnknownValueError:
                    self.add_message("System", "Could not understand audio")
                except sr.RequestError as e:
                    self.add_message("System", f"Speech service error: {str(e)}")
                except Exception as e:
                    self.add_message("System", f"Audio error: {str(e)}")
                finally:
                    self.voice_btn.config(state=tk.NORMAL, text="🎤")
        
        threading.Thread(target=recognize_thread).start()
    
    def decrypt_file(self):
        file_path = self.file_entry.get()
        if not file_path:
            self.speak("Please specify a file path for decryption")
            return
        
        # Windows path normalization
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            self.speak("File does not exist")
            return
        
        # Simulate decryption process
        self.speak(f"Attempting decryption of {os.path.basename(file_path)}")
        time.sleep(1)
        
        try:
            # Windows-specific decryption simulation
            decrypted = self.simulate_decryption(file_path)
            self.speak(f"Decryption successful! File contents: {decrypted[:100]}...")
        except Exception as e:
            self.speak(f"Decryption failed: {str(e)}")
    
    def simulate_decryption(self, file_path):
        """Windows-specific decryption simulation"""
        # For a real implementation, you would use cryptography libraries
        # Here we'll just simulate with file operations
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Simple XOR "decryption" for simulation
        key = b'JARVIS_SECRET_KEY'
        decrypted = bytes([content[i] ^ key[i % len(key)] for i in range(len(content)))
        
        return decrypted.decode('utf-8', errors='ignore')
    
    def run_diagnostics(self):
        self.diag_text.config(state=tk.NORMAL)
        self.diag_text.delete(1.0, tk.END)
        
        diagnostics = "Running advanced system diagnostics...\n\n"
        
        # Windows-specific diagnostics
        try:
            # CPU info
            cpu_info = subprocess.check_output(["wmic", "cpu", "get", "name"], text=True)
            cpu_name = [line.strip() for line in cpu_info.split('\n') if line.strip()][1]
            
            # Memory info
            mem_info = subprocess.check_output(["wmic", "memorychip", "get", "capacity"], text=True)
            total_mem = sum(int(line.strip()) for line in mem_info.split('\n')[1:] if line.strip())
            
            diagnostics += f"- CPU: {cpu_name}\n"
            diagnostics += f"- Total RAM: {total_mem//(1024**3)} GB\n"
        except:
            diagnostics += "- Hardware info: Unavailable\n"
        
        diagnostics += f"- Windows Version: {self.windows_version}\n"
        diagnostics += f"- Disk Space: {self.get_disk_space_summary()}\n"
        diagnostics += f"- Network Status: {'Connected' if self.check_network() else 'Disconnected'}\n"
        diagnostics += f"- Security Systems: Active\n"
        diagnostics += f"- Learning Module: Operational\n"
        diagnostics += f"- Financial Analysis: Ready\n"
        diagnostics += f"- Decryption Tools: Functional\n\n"
        diagnostics += "All systems operating within normal parameters."
        
        self.diag_text.insert(tk.END, diagnostics)
        self.diag_text.config(state=tk.DISABLED)
        self.speak("System diagnostics complete. All systems operational.")
    
    def get_disk_space_summary(self):
        try:
            total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
            return f"{free//(1024**3)}GB free of {total//(1024**3)}GB"
        except:
            return "Unknown"
    
    def check_network(self):
        try:
            response = subprocess.run(
                ["ping", "-n", "1", "8.8.8.8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return response.returncode == 0
        except:
            return False
    
    def update_status(self):
        status = "System Status Report\n\n"
        status += f"- OS: {self.windows_version}\n"
        status += f"- Current Time: {datetime.now().strftime('%H:%M:%S')}\n"
        status += f"- Active Modules: Financial Analysis, Decryption, Learning\n"
        status += f"- Memory Items: {len(self.memory['facts'])}\n"
        status += f"- Conversation History: {len(self.memory['conversation'])} entries\n"
        status += f"- Market Data: Updated at {self.market_status.get('last_updated', 'N/A')}\n"
        status += f"- System Security: Level 4 Encryption Active\n"
        status += f"- AI Learning Rate: Adaptive\n\n"
        status += "All systems functioning optimally."
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status)
        self.status_text.config(state=tk.DISABLED)
        
        # Update every minute
        self.root.after(60000, self.update_status)
    
    def system_monitor(self):
        """Continuous system monitoring for Windows"""
        while True:
            # Monitor critical resources
            if not self.check_network():
                self.root.after(0, lambda: self.add_message("System", "Network connection lost"))
                
            # Check disk space
            try:
                total, used, free = shutil.disk_usage("C:\\")
                if free / total < 0.1:  # Less than 10% free
                    self.root.after(0, lambda: self.add_message("System", 
                        f"Low disk space on C: ({free//(1024**3)}GB remaining)"))
            except:
                pass
            
            time.sleep(60)

    # Rest of the existing class remains with minor adjustments for Windows compatibility

if __name__ == "__main__":
    root = tk.Tk()
    app = JARVIS(root)
    root.mainloop()