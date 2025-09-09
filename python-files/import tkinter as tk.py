import tkinter as tk
from tkinter import messagebox
import requests
import hashlib
import socket
import time
import threading
import ctypes
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# Configuration - REPLACE WITH YOUR FIREBASE DETAILS
FIREBASE_URL = "https://cheatygonzales-4b407-default-rtdb.europe-west1.firebasedatabase.app/"
API_KEY = "AIzaSyBp0SygE3cw2RjDCbgY1B9qjf0N68CfuTw"

# Symbol to show after access granted - CHANGE THIS TO WHATEVER YOU WANT
ACCESS_SYMBOL = "✓"

# Direct Input mouse movement setup
SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions for mouse input
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class PasswordManager:
    def __init__(self):
        # ====== REPLACE WITH YOUR 10 PASSWORDS ======
        self.passwords = [
            "1", "2KKuT]d[=,uH5$L", "'1[m^%ivStUPA3H",
            "biT.QJ%F,^zp2zI", "-2(umR6FV+gM8jQ", "oX[GDyGj!}BnL}@",
            "MIq04CZ0I^^;K3S", "_^6XpmZIhzMXF8L", "CNf_&tiOlr7yTfB",
            "KnAkP;K6YFHptNp"
        ]
        # ============================================
        
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_client_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"
    
    def check_password(self, password):
        hashed = self.hash_password(password)
        url = f"{FIREBASE_URL}passwords/{hashed}.json?auth={API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return False
    
    def register_password(self, password):
        hashed = self.hash_password(password)
        ip = self.get_client_ip()
        url = f"{FIREBASE_URL}passwords/{hashed}.json?auth={API_KEY}"
        requests.put(url, json=ip)

class RecoilControl:
    def __init__(self):
        self.current_profile = None  # No default profile selected
        self.require_toggle = True
        self.delay_rate = 7  # ms
        self.ingame_sens = 6.4  # Default sensitivity
        
        self.accum_x = 0.0  # Sub-pixel accumulation
        self.accum_y = 0.0
        self.shooting = False
        self.running = False
        self.caps_lock_on = False
        
        # More precise recoil patterns
        self.profiles = {
            "ASH": {"down_force": 119.4, "left_force": 7.0, "right_force": 0.0},
            "DOC": {"down_force": 89.2, "left_force": 5.0, "right_force": 0.0},
            "BUCK": {"down_force": 109.0, "left_force": 2.5, "right_force": 0.0},
            "SMG11": {"down_force": 118.5, "left_force": 0.0, "right_force": 0.4},
            "TWITCH": {"down_force": 175.0, "left_force": 4.4, "right_force": 0.0},
            "SMG12": {"down_force": 145.6, "left_force": 0.0, "right_force": 17.0}
        }
        
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.mouse_listener = None
        self.keyboard_listener = None
    
    def move_mouse(self, dx, dy):
        """Move mouse using direct input (works in games)"""
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(dx, dy, 0, 0x0001, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    def get_calibrated_value(self, base_value):
        return base_value * (1.0 / self.ingame_sens)
    
    def apply_recoil(self):
        while self.shooting and self.running:
            if self.current_profile and (not self.require_toggle or (self.require_toggle and self.caps_lock_on)):
                profile = self.profiles[self.current_profile]
                down_calibrated = self.get_calibrated_value(profile["down_force"])
                left_calibrated = self.get_calibrated_value(profile["left_force"])
                right_calibrated = self.get_calibrated_value(profile["right_force"])
                
                # Calculate forces with sub-pixel precision
                horizontal = right_calibrated - left_calibrated
                vertical = down_calibrated
                
                # Add to accumulators
                self.accum_x += horizontal
                self.accum_y += vertical
                
                # Get integer parts to move
                move_x = int(self.accum_x)
                move_y = int(self.accum_y)
                
                # Keep fractional parts for next iteration
                self.accum_x -= move_x
                self.accum_y -= move_y
                
                if move_x != 0 or move_y != 0:
                    self.move_mouse(move_x, move_y)
            
            time.sleep(self.delay_rate / 1000)
    
    def on_click(self, x, y, button, pressed):
        if button == Button.left:
            if pressed:
                if not self.shooting:
                    self.shooting = True
                    self.accum_x = 0.0
                    self.accum_y = 0.0
                    recoil_thread = threading.Thread(target=self.apply_recoil, daemon=True)
                    recoil_thread.start()
            else:
                self.shooting = False
    
    def on_press(self, key):
        try:
            if key == Key.caps_lock:
                self.caps_lock_on = not self.caps_lock_on
        except AttributeError:
            pass
    
    def start(self):
        if not self.running:
            self.running = True
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.mouse_listener.start()
            self.keyboard_listener.start()
    
    def stop(self):
        if self.running:
            self.running = False
            self.shooting = False
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
    
    def set_profile(self, profile_name):
        if profile_name in self.profiles:
            self.current_profile = profile_name
    
    def set_sensitivity(self, sensitivity):
        try:
            self.ingame_sens = float(sensitivity)
        except ValueError:
            pass

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHEATYGONZALES1.0")
        self.geometry("500x450")  # Increased height for sensitivity field
        self.configure(bg='#222222')
        self.password_manager = PasswordManager()
        self.recoil_control = RecoilControl()
        
        # Theme colors
        self.bg_color = '#222222'
        self.fg_color = '#ffffff'
        self.entry_bg = '#333333'
        self.button_bg = '#444444'
        self.active_bg = '#555555'
        
        self.create_login_screen()
    
    def create_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        tk.Label(self, text="CHEATYGONZALES", 
                font=('Arial', 14), bg=self.bg_color, fg=self.fg_color).pack(pady=20)
        
        tk.Label(self, text="Enter Password:", 
                bg=self.bg_color, fg=self.fg_color).pack()
        
        self.pwd_entry = tk.Entry(self, show="*", width=25, 
                                bg=self.entry_bg, fg=self.fg_color)
        self.pwd_entry.pack(pady=10)
        
        tk.Button(self, text="LOGIN", command=self.attempt_login,
                bg=self.button_bg, fg='white', width=15).pack(pady=20)
    
    def attempt_login(self):
        password = self.pwd_entry.get()
        
        if not password:
            messagebox.showwarning("Error", "Enter a password")
            return
            
        if password not in self.password_manager.passwords:
            messagebox.showwarning("Error", "Invalid password")
            return
            
        status = self.password_manager.check_password(password)
        current_ip = self.password_manager.get_client_ip()
        
        if status is None:
            self.password_manager.register_password(password)
            self.show_authenticated_screen()
        elif status == current_ip:
            self.show_authenticated_screen()
        else:
            messagebox.showerror("Access Denied", 
                               "Password already in use by another device")
    
    def show_authenticated_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header - will change after 5 seconds
        self.access_label = tk.Label(self, text="ACCESS GRANTED", 
                                   font=('Arial', 16), bg=self.bg_color, fg='green')
        self.access_label.pack(pady=10)
        
        # Schedule the text change after 5 seconds (5000ms)
        self.after(5000, lambda: self.access_label.config(text=ACCESS_SYMBOL, fg='green'))
        
        # Sensitivity input field
        sens_frame = tk.Frame(self, bg=self.bg_color)
        sens_frame.pack(pady=10)
        
        tk.Label(sens_frame, text="In-Game Sensitivity:", 
                bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        
        self.sens_entry = tk.Entry(sens_frame, width=6, 
                                 bg=self.entry_bg, fg=self.fg_color)
        self.sens_entry.insert(0, str(self.recoil_control.ingame_sens))
        self.sens_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(sens_frame, text="Update", 
                 command=self.update_sensitivity,
                 bg=self.button_bg, fg='white').pack(side=tk.LEFT)
        
        # Profile selection frame
        profile_frame = tk.Frame(self, bg=self.bg_color)
        profile_frame.pack(pady=10)
        
        # Create profile buttons
        self.profile_buttons = {}
        self.selected_profile = tk.StringVar(value="")  # Empty string for no selection
        
        profiles = ["ASH", "DOC", "BUCK", "SMG11", "TWITCH", "SMG12"]
        
        for i, profile in enumerate(profiles):
            btn = tk.Radiobutton(
                profile_frame,
                text=profile,
                variable=self.selected_profile,
                value=profile,
                command=lambda p=profile: self.on_profile_change(p),
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.active_bg,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                indicatoron=1
            )
            btn.grid(row=i//3, column=i%3, padx=10, pady=5, sticky='w')
            self.profile_buttons[profile] = btn
        
        # Status frame
        status_frame = tk.Frame(self, bg=self.bg_color)
        status_frame.pack(pady=10)
        
        # Toggle checkbox
        self.toggle_var = tk.BooleanVar(value=self.recoil_control.require_toggle)
        tk.Checkbutton(
            status_frame,
            text="Require Toggle (Caps Lock)",
            variable=self.toggle_var,
            command=self.on_toggle_change,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            selectcolor=self.active_bg
        ).pack(side=tk.LEFT, padx=5)
        
        # Always on top checkbox
        self.topmost_var = tk.BooleanVar()
        tk.Checkbutton(
            status_frame,
            text="Always on Top",
            variable=self.topmost_var,
            command=lambda: self.attributes('-topmost', self.topmost_var.get()),
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            selectcolor=self.active_bg
        ).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        tk.Label(self, 
                text="Recoil control activates automatically when shooting (Mouse1)\nCaps Lock toggles when 'Require Toggle' is enabled",
                bg=self.bg_color, fg='yellow').pack(pady=10)
        
        # Start recoil control
        self.recoil_control.start()
    
    def update_sensitivity(self):
        """Update the in-game sensitivity from the entry field"""
        sens_value = self.sens_entry.get()
        try:
            self.recoil_control.set_sensitivity(float(sens_value))
            messagebox.showinfo("Success", f"Sensitivity updated to {sens_value}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def on_profile_change(self, profile):
        self.recoil_control.set_profile(profile)
    
    def on_toggle_change(self):
        self.recoil_control.require_toggle = self.toggle_var.get()
    
    def on_closing(self):
        self.recoil_control.stop()
        self.destroy()

if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()