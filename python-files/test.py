import subprocess
import sys

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"'{package}' saknas, installerar...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"'{package}' har installerats.")

required_packages = ['pyttsx3', 'win10toast']

for pkg in required_packages:
    install_and_import(pkg)

# Nu kan vi importera de installerade paketen utan problem
import ctypes
import winsound
import random
import time
import os
import threading
from tkinter import messagebox, Tk
import tkinter as tk
import pyttsx3

try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except ImportError:
    toaster = None
    print("win10toast missing – system notifications will not show")

# --- Text-to-Speech ---
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS Error] {e}")

# --- Cursor Control ---
def hide_cursor():
    ctypes.windll.user32.ShowCursor(False)

def show_cursor():
    ctypes.windll.user32.ShowCursor(True)

# --- Sounds & Notifications ---
def play_alert_sound():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

def play_usb_insert_sound():
    winsound.PlaySound("SystemDeviceConnect", winsound.SND_ALIAS)

def show_toast_notification(title, msg):
    if toaster:
        toaster.show_toast(title, msg, duration=5, threaded=True)
    else:
        print(f"[Notification] {title}: {msg}")

# --- Popup Windows ---
def show_infected_message():
    root = Tk()
    root.withdraw()
    messagebox.showerror("WARNING", "Your system has been infected!")
    root.destroy()

def show_logout_warning():
    root = Tk()
    root.withdraw()
    messagebox.showwarning("System Notice", "You are about to be logged out! Click OK to continue.")
    root.destroy()

# --- System Behavior ---
def set_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

def hide_desktop_icons(hide=True):
    progman = ctypes.windll.user32.FindWindowW("Progman", None)
    if progman:
        style = ctypes.windll.user32.GetWindowLongW(progman, -16)
        if hide:
            style &= ~0x10000000
        else:
            style |= 0x10000000
        ctypes.windll.user32.SetWindowLongW(progman, -16, style)
        ctypes.windll.user32.ShowWindow(progman, 0 if hide else 5)

def hide_taskbar(hide=True):
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        ctypes.windll.user32.ShowWindow(taskbar, 0 if hide else 5)

# --- Black Screen + Sound + BSOD ---
def play_continuous_beep(stop_event):
    while not stop_event.is_set():
        winsound.Beep(1000, 300)
        time.sleep(0.7)

def black_screen_with_sound_and_bsod():
    stop_event = threading.Event()
    beep_thread = threading.Thread(target=play_continuous_beep, args=(stop_event,))
    beep_thread.start()

    hide_cursor()

    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')

    # Efter 20 sekunder byter vi till BSOD
    def show_bsod():
        # Rensa fönstret
        for widget in root.winfo_children():
            widget.destroy()
        root.configure(bg='#010080')  # BSOD blå färg ungefär

        bsod_text = (
            "A problem has been detected and your computer has been shut down to prevent damage.\n\n"
            "Funny BSOD joke: Why don't programmers like nature? It has too many bugs.\n\n"
            "If this is the first time you've seen this stop error screen,\n"
            "restart your computer. If this screen appears again, follow these steps:\n\n"
            "*** STOP: 0x000000DEADBEEF (0x00000000, 0x00000000, 0x00000000, 0x00000000)"
        )

        label = tk.Label(root, text=bsod_text, fg='white', bg='#010080', font=("Consolas", 18), justify="left")
        label.pack(expand=True, padx=50, pady=50)

    root.after(20000, show_bsod)

    def on_close():
        stop_event.set()
        root.destroy()
        show_cursor()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    beep_thread.join()
    show_cursor()

# --- Main Program ---
def main():
    play_usb_insert_sound()
    show_toast_notification("New Device Connected", "Device 'VirusXYZ' has been inserted.")

    speak("USB device connected. Initializing infection.")
    time.sleep(2)

    play_alert_sound()
    speak("Warning. Your system has been infected.")
    show_infected_message()

    speak("You are about to be logged out. Do not try to stop this.")
    show_logout_warning()

    wallpaper_folder = r"C:\Windows\Web\Wallpaper"
    wallpapers = []
    for root_dir, dirs, files in os.walk(wallpaper_folder):
        for file in files:
            if file.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png')):
                wallpapers.append(os.path.join(root_dir, file))
    if wallpapers:
        selected = random.choice(wallpapers)
        set_wallpaper(selected)

    hide_desktop_icons(True)
    hide_taskbar(True)

    speak("You have lost control. There is no escape.")
    black_screen_with_sound_and_bsod()

    hide_desktop_icons(False)
    hide_taskbar(False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        hide_desktop_icons(False)
        hide_taskbar(False)
        show_cursor()
        print("Program interrupted. Desktop restored.")
        sys.exit()
