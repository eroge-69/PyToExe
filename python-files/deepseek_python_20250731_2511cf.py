import os
import sys
import json
import psutil
import platform
import threading
import winsound
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import win32gui
import win32con
import win32api

# Configuration
CONFIG_FILE = "battery_monitor_config.json"
DEFAULT_CONFIG = {
    "alerts": [
        {"level": 85, "message": "Battery at 85% - Consider unplugging"},
        {"level": 95, "message": "Battery at 95% - Unplug now!"}
    ],
    "check_interval": 60,
    "enable_sound": True,
    "start_minimized": False
}

class BatteryMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Monitor Settings")
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Load or create config
        self.load_config()
        
        # System tray icon
        self.create_system_tray_icon()
        
        # GUI Elements
        self.setup_gui()
        
        # Start monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_battery, daemon=True)
        self.monitor_thread.start()
        
        # Start minimized if configured
        if self.config["start_minimized"]:
            self.minimize_to_tray()
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            else:
                self.config = DEFAULT_CONFIG
                self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
            self.config = DEFAULT_CONFIG
    
    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, S, E, W))
        
        # Alerts list
        ttk.Label(main_frame, text="Battery Level Alerts:").grid(row=0, column=0, sticky=W, pady=(0, 5))
        
        self.alert_tree = ttk.Treeview(main_frame, columns=("level", "message"), show="headings", height=5)
        self.alert_tree.heading("level", text="Level (%)")
        self.alert_tree.heading("message", text="Message")
        self.alert_tree.column("level", width=80)
        self.alert_tree.column("message", width=300)
        self.alert_tree.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(E, W))
        
        # Populate alerts
        for alert in self.config["alerts"]:
            self.alert_tree.insert("", "end", values=(alert["level"], alert["message"]))
        
        # Add/Edit/Remove buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Add", command=self.add_alert).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_alert).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_alert).pack(side=LEFT, padx=5)
        
        # Test button
        ttk.Button(main_frame, text="Test Alert", command=self.test_alert).grid(row=3, column=0, pady=(10, 5), sticky=W)
        
        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=3, sticky=(E, W), pady=(10, 0))
        
        ttk.Label(settings_frame, text="Check Interval (seconds):").grid(row=0, column=0, sticky=W)
        self.interval_var = IntVar(value=self.config["check_interval"])
        ttk.Spinbox(settings_frame, from_=10, to=600, textvariable=self.interval_var, width=5).grid(row=0, column=1, sticky=W, padx=5)
        
        self.sound_var = BooleanVar(value=self.config["enable_sound"])
        ttk.Checkbutton(settings_frame, text="Enable Sound", variable=self.sound_var).grid(row=1, column=0, sticky=W, pady=(5, 0))
        
        self.minimized_var = BooleanVar(value=self.config["start_minimized"])
        ttk.Checkbutton(settings_frame, text="Start Minimized", variable=self.minimized_var).grid(row=1, column=1, sticky=W, pady=(5, 0))
        
        # Save button
        ttk.Button(main_frame, text="Save Settings", command=self.save_settings).grid(row=5, column=0, pady=(10, 0), sticky=W)
        
        # Make resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def add_alert(self):
        add_window = Toplevel(self.root)
        add_window.title("Add Alert")
        
        ttk.Label(add_window, text="Battery Level (%):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        level_var = IntVar()
        ttk.Spinbox(add_window, from_=1, to=100, textvariable=level_var, width=5).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_window, text="Message:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        message_var = StringVar()
        ttk.Entry(add_window, textvariable=message_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        def save():
            if not level_var.get() or not message_var.get():
                messagebox.showerror("Error", "Both fields are required")
                return
            self.alert_tree.insert("", "end", values=(level_var.get(), message_var.get()))
            add_window.destroy()
        
        ttk.Button(add_window, text="Add", command=save).grid(row=2, column=1, pady=5, sticky=E)
    
    def edit_alert(self):
        selected = self.alert_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an alert to edit")
            return
        
        values = self.alert_tree.item(selected, "values")
        
        edit_window = Toplevel(self.root)
        edit_window.title("Edit Alert")
        
        ttk.Label(edit_window, text="Battery Level (%):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        level_var = IntVar(value=values[0])
        ttk.Spinbox(edit_window, from_=1, to=100, textvariable=level_var, width=5).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Message:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        message_var = StringVar(value=values[1])
        ttk.Entry(edit_window, textvariable=message_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        def save():
            if not level_var.get() or not message_var.get():
                messagebox.showerror("Error", "Both fields are required")
                return
            self.alert_tree.item(selected, values=(level_var.get(), message_var.get()))
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Save", command=save).grid(row=2, column=1, pady=5, sticky=E)
    
    def remove_alert(self):
        selected = self.alert_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an alert to remove")
            return
        self.alert_tree.delete(selected)
    
    def test_alert(self):
        self.show_alert("Test Alert", "This is a test notification for the battery monitor")
    
    def save_settings(self):
        # Save alerts
        self.config["alerts"] = []
        for item in self.alert_tree.get_children():
            level, message = self.alert_tree.item(item, "values")
            self.config["alerts"].append({"level": int(level), "message": message})
        
        # Save other settings
        self.config["check_interval"] = self.interval_var.get()
        self.config["enable_sound"] = self.sound_var.get()
        self.config["start_minimized"] = self.minimized_var.get()
        
        self.save_config()
        messagebox.showinfo("Success", "Settings saved successfully")
    
    def monitor_battery(self):
        while self.monitoring:
            if not hasattr(psutil, "sensors_battery"):
                print("No battery detected")
                time.sleep(self.config["check_interval"])
                continue
            
            battery = psutil.sensors_battery()
            if battery is None:
                print("No battery detected")
                time.sleep(self.config["check_interval"])
                continue
            
            percent = battery.percent
            plugged = battery.power_plugged
            
            # Check all alerts
            for alert in self.config["alerts"]:
                if plugged and percent >= alert["level"]:
                    self.show_alert(f"Battery at {percent}%", alert["message"])
                    # Wait a bit after showing alert to prevent rapid-fire popups
                    time.sleep(10)
                    break
            
            time.sleep(self.config["check_interval"])
    
    def show_alert(self, title, message):
        # Create popup window
        popup = Toplevel()
        popup.title(title)
        popup.attributes("-topmost", True)
        popup.grab_set()
        
        # Force window to front (even over fullscreen apps)
        popup.lift()
        popup.attributes('-topmost', True)
        popup.after_idle(popup.attributes, '-topmost', False)
        
        # Make window stay on top of fullscreen applications
        hwnd = int(popup.winfo_id())
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        
        # Window content
        ttk.Label(popup, text=message, font=("Arial", 12, "bold"), foreground="red").pack(padx=20, pady=10)
        ttk.Button(popup, text="Dismiss", command=popup.destroy).pack(pady=(0, 10))
        
        # Play sound if enabled
        if self.config["enable_sound"]:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass
    
    def create_system_tray_icon(self):
        # Create image for system tray
        image = Image.new('RGB', (16, 16), color = 'black')
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), "B", fill="white")
        self.tray_icon = ImageTk.PhotoImage(image)
        
        # System tray menu
        menu = (
            item('Show Settings', self.restore_from_tray),
            item('Exit', self.quit_app)
        )
        
        self.icon = pystray.Icon("battery_monitor", self.tray_icon, "Battery Monitor", menu)
        
        # Start system tray icon in separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def minimize_to_tray(self):
        self.root.withdraw()
    
    def restore_from_tray(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_app(self):
        self.monitoring = False
        self.icon.stop()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("This application is designed for Windows only")
        sys.exit(1)
    
    root = Tk()
    app = BatteryMonitorApp(root)
    root.mainloop()