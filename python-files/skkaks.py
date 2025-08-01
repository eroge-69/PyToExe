# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: aaaa.py
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import tkinter as tk
from tkinter import messagebox
import mss
import keyboard
import mouse, time, winsound, cv2, numpy as np, pyttsx3
from threading import Thread, Lock
import webbrowser
import uuid
import hashlib
import os
import pyperclip

LOWER_RED_HSV = [0, 100, 100]
UPPER_RED_HSV = [10, 255, 255]
LOWER_BLUE_HSV = [110, 100, 100]
UPPER_BLUE_HSV = [130, 255, 255]
LOWER_PURPLE_HSV = [140, 100, 100]
UPPER_PURPLE_HSV = [160, 255, 255]
LOWER_GREEN_HSV = [50, 100, 100]
UPPER_GREEN_HSV = [70, 255, 255]
LICENSE_FILE = 'license.key'

def get_machine_id():
    """Generate unique device ID based on hardware"""
    return str(uuid.getnode())

def generate_license_key(machine_id):
    """Generate license key based on device ID"""
    return hashlib.sha256(machine_id.encode()).hexdigest()

def check_license():
    """Check license existence and validity"""
    machine_id = get_machine_id()
    expected_key = generate_license_key(machine_id)
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            stored_key = f.read().strip()
            return stored_key == expected_key

def save_license_key(key):
    """Save license key to file"""
    with open(LICENSE_FILE, 'w') as f:
        f.write(key)

class TriggerBot:
    def __init__(self, grabzone, sleep_time, screen_width=800, screen_height=600, mouse_speed=10, auto_fire=False, fire_delay=0.1):
        self.grabzone = grabzone
        self.sleep_time = sleep_time
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.toggled = False
        self.color_mode = 'red'
        self.engine = pyttsx3.init()
        self.lock = Lock()
        self.mouse_speed = mouse_speed
        self.auto_fire = auto_fire
        self.fire_delay = fire_delay
        self.last_fire_time = 0
        self.trigger_key = '+'

    def toggle(self):
        with self.lock:
            self.toggled = not self.toggled

    def toggle_auto_fire(self):
        with self.lock:
            self.auto_fire = not self.auto_fire

    def switch_color(self):
        color_modes = ['red', 'blue', 'purple', 'green']
        current_index = color_modes.index(self.color_mode)
        self.color_mode = color_modes[(current_index + 1) % len(color_modes)]

    def update_settings(self, grabzone, sleep_time, screen_width, screen_height, mouse_speed, auto_fire, fire_delay, trigger_key):
        with self.lock:
            self.grabzone = grabzone
            self.sleep_time = sleep_time
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.mouse_speed = mouse_speed
            self.auto_fire = auto_fire
            self.fire_delay = fire_delay
            self.trigger_key = trigger_key

    def move_mouse(self, x, y):
        current_x, current_y = mouse.get_position()
        step_x = (x - current_x) / self.mouse_speed
        step_y = (y - current_y) / self.mouse_speed
        for _ in range(self.mouse_speed):
            current_x += step_x
            current_y += step_y
            mouse.move(int(current_x), int(current_y))
            time.sleep(0.001)

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

    def approx(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = None
        if self.color_mode == 'red':
            mask = cv2.inRange(hsv, np.array(LOWER_RED_HSV), np.array(UPPER_RED_HSV))
        return (np.any(mask), mask)

    def scan(self):
        with mss.mss() as sct:
            monitor = {'top': self.screen_height // 2 - self.grabzone, 
                      'left': self.screen_width // 2 - self.grabzone, 
                      'width': self.grabzone * 2, 
                      'height': self.grabzone * 2}
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            found, mask = self.approx(img)
            if found:
                nonzero_points = np.column_stack(np.where(mask > 0))
                if nonzero_points.size > 0:
                    center_x = np.mean(nonzero_points[:, 1])
                    center_y = np.mean(nonzero_points[:, 0])
                    center_x = center_x + (self.screen_width // 2 - self.grabzone)
                    center_y = center_y + (self.screen_height // 2 - self.grabzone)
                    self.move_mouse(center_x, center_y)
                    if self.auto_fire and time.time() - self.last_fire_time >= self.fire_delay:
                        mouse.click(button='left')
                        self.last_fire_time = time.time()
            time.sleep(self.sleep_time * 0.02)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('TriggerBot')
        self.geometry('400x550')
        self.input_received = False
        self.bot_thread = None
        self.status_label = None
        self.bot = None
        self.check_license_and_start()

    def check_license_and_start(self):
        """Check license before running the program"""
        if not check_license():
            self.show_license_dialog()
        return None

    def show_license_dialog(self):
        """Show license key entry window"""
        self.license_window = tk.Toplevel(self)
        self.license_window.title('License Activation')
        self.license_window.geometry('300x280')
        
        tk.Label(self.license_window, text='Enter license key:', font=('Arial', 12)).pack(pady=10)
        machine_id = get_machine_id()
        tk.Label(self.license_window, text=f'Device ID: {machine_id}', font=('Arial', 10), wraplength=280).pack(pady=5)
        tk.Label(self.license_window, text='Copy this ID and send it to support.', font=('Arial', 8)).pack(pady=5)
        tk.Button(self.license_window, text='Copy Device ID', command=lambda: pyperclip.copy(machine_id)).pack(pady=5)
        
        self.license_entry = tk.Entry(self.license_window)
        self.license_entry.pack(pady=10)
        self.license_entry.bind('<Button-3>', self.show_context_menu)
        
        tk.Button(self.license_window, text='Paste License Key', command=self.paste_license_key).pack(pady=5)
        tk.Button(self.license_window, text='Activate', command=self.verify_license).pack(pady=5)
        tk.Button(self.license_window, text='Contact Support', command=self.open_telegram).pack(pady=5)

    def show_context_menu(self, event):
        """Show right-click context menu for pasting"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label='Paste', command=self.paste_license_key)
        context_menu.post(event.x_root, event.y_root)

    def paste_license_key(self):
        """Paste license key from clipboard"""
        try:
            self.license_entry.delete(0, tk.END)
            self.license_entry.insert(0, pyperclip.paste())
        except Exception as e:
            messagebox.showerror('Error', 'Failed to paste license key. Please enter manually.')

    def verify_license(self):
        """Verify entered license key"""
        entered_key = self.license_entry.get().strip()
        expected_key = generate_license_key(get_machine_id())
        if entered_key == expected_key:
            save_license_key(entered_key)
            self.license_window.destroy()
            self.create_widgets()
            messagebox.showinfo('Success', 'License verified successfully!')
        else:
            messagebox.showerror('Error', 'Invalid license key!')
        return None

    def create_widgets(self):
        tk.Label(self, text='Developed by Farshad PM', font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Button(self, text='Contact Telegram Support', command=self.open_telegram).pack(pady=5)
        
        tk.Label(self, text='Activation Key:').pack(pady=5)
        self.entry1 = tk.Entry(self)
        self.entry1.pack()
        self.entry1.insert(0, '+')
        
        tk.Label(self, text='Scan Area (pixels):').pack(pady=5)
        self.entry2 = tk.Entry(self)
        self.entry2.pack()
        self.entry2.insert(0, '12')
        
        tk.Label(self, text='Delay Time (seconds):').pack(pady=5)
        self.entry3 = tk.Entry(self)
        self.entry3.pack()
        self.entry3.insert(0, '0.4')
        
        tk.Label(self, text='Screen Width:').pack(pady=5)
        self.entry4 = tk.Entry(self)
        self.entry4.pack()
        self.entry4.insert(0, '1024')
        
        tk.Label(self, text='Screen Height:').pack(pady=5)
        self.entry5 = tk.Entry(self)
        self.entry5.pack()
        self.entry5.insert(0, '768')
        
        tk.Label(self, text='Mouse Speed:').pack(pady=5)
        self.entry6 = tk.Entry(self)
        self.entry6.pack()
        self.entry6.insert(0, '3')
        
        tk.Label(self, text='Fire Delay (seconds):').pack(pady=5)
        self.entry7 = tk.Entry(self)
        self.entry7.pack()
        self.entry7.insert(0, '0.1')
        
        self.auto_fire_var = tk.BooleanVar()
        tk.Checkbutton(self, text='Auto Fire', variable=self.auto_fire_var).pack(pady=5)
        
        tk.Button(self, text='Start Bot', command=self.start_bot_thread).pack(pady=10)
        tk.Button(self, text='Apply Settings', command=self.apply_settings).pack(pady=5)
        
        self.error_label = tk.Label(self, text='', fg='red')
        self.error_label.pack()
        self.status_label = tk.Label(self, text='', fg='green')
        self.status_label.pack()

    def open_telegram(self):
        webbrowser.open('https://t.me/farshad_pm_org')

    def show_error(self, message, clear=False):
        self.error_label.config(text='' if clear else message)

    def update_status(self, message):
        self.status_label.config(text=message)

    def validate_entries(self):
        try:
            int(self.entry2.get())
            float(self.entry3.get())
            int(self.entry4.get())
            int(self.entry5.get())
            int(self.entry6.get())
            float(self.entry7.get())
            return True
        except ValueError:
            self.show_error('Please enter valid numeric values!')
            return False

    def apply_settings(self):
        if self.validate_entries() and self.bot:
            try:
                trigger_key = self.entry1.get().strip()
                grabzone = int(self.entry2.get())
                sleep_time = float(self.entry3.get())
                screen_width = int(self.entry4.get())
                screen_height = int(self.entry5.get())
                mouse_speed = int(self.entry6.get())
                fire_delay = float(self.entry7.get())
                auto_fire = self.auto_fire_var.get()
                
                if not trigger_key:
                    raise ValueError('Activation key cannot be empty')
                
                self.bot.update_settings(grabzone, sleep_time, screen_width, screen_height, 
                                       mouse_speed, auto_fire, fire_delay, trigger_key)
                self.show_error('Settings applied successfully!', clear=True)
                
            except Exception as e:
                self.show_error(f'Error: {e}')

    def start_bot_thread(self):
        if self.validate_entries() and (self.bot_thread is None or not self.bot_thread.is_alive()):
            self.bot_thread = Thread(target=self.start_bot, daemon=True)
            self.bot_thread.start()
            return None

    def start_bot(self):
        try:
            trigger_key = self.entry1.get().strip()
            grabzone = int(self.entry2.get())
            sleep_time = float(self.entry3.get())
            screen_width = int(self.entry4.get())
            screen_height = int(self.entry5.get())
            mouse_speed = int(self.entry6.get())
            fire_delay = float(self.entry7.get())
            auto_fire = self.auto_fire_var.get()
            
            if not trigger_key:
                raise ValueError('Activation key cannot be empty')
            
            self.bot = TriggerBot(grabzone, sleep_time, screen_width, screen_height,
                                mouse_speed, auto_fire, fire_delay)
            self.bot_thread = Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()
            self.update_status('Bot started successfully!')
            
        except Exception as e:
            self.show_error(f'Error: {e}')

    def run_bot(self):
        while True:
            if self.bot.toggled:
                self.bot.scan()
            time.sleep(0.01)

if __name__ == '__main__':
    app = App()
    app.mainloop()