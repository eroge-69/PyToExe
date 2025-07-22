import os
import sys
import threading
import ctypes
import winreg
from pynput import keyboard
from pygame import mixer
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import customtkinter as ctk

APP_NAME = "SoundHotkeyApp"
sound_enabled = True
volume = 1.0
listener = None
icon = None
window = None
tray_ready = threading.Event()

# --- Гучність ---
def play_sound():
    if sound_enabled:
        try:
            sound = mixer.Sound(sound_path)
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"Помилка: {e}")

# --- Автозапуск ---
def set_autostart(enable: bool):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_ALL_ACCESS)
    if enable:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.executable)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    key.Close()

def check_autostart():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_READ)
    try:
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        return True
    except FileNotFoundError:
        return False

# --- Шлях до звуку ---
mixer.init()
sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.mp3")

# --- Обробка клавіш ---
def on_press(key):
    if sound_enabled:
        threading.Thread(target=play_sound, daemon=True).start()

def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def stop_listener():
    global listener
    if listener:
        listener.stop()
        listener = None

# --- Трей ---
def create_image():
    image = Image.new('RGB', (64, 64), color=(40, 40, 40))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(0, 200, 0))
    return image

def show_window(icon_, item):
    if window:
        window.after(0, window.deiconify)

def exit_program(icon_, item):
    stop_listener()
    icon_.stop()
    if window:
        window.quit()

def setup_tray():
    global icon
    icon = Icon(APP_NAME,
                icon=create_image(),
                title="SoundHotkey",
                menu=Menu(
                    MenuItem("Відкрити", show_window),
                    MenuItem("Вийти", exit_program)
                ))
    tray_ready.set()
    icon.run()

# --- GUI ---
def create_gui():
    global window, sound_enabled, volume

    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.title("Sound Hotkey")
    window.geometry("300x200")

    def on_close():
        window.withdraw()

    def on_volume_change(val):
        global volume
        volume = float(val) / 100

    def on_toggle_sound():
        nonlocal sound_switch
        global sound_enabled
        sound_enabled = sound_switch.get()

    def on_toggle_autostart():
        nonlocal autostart_switch
        set_autostart(autostart_switch.get())

    def minimize_to_tray():
        window.withdraw()

    # --- UI ---
    ctk.CTkLabel(window, text="Гучність").pack(pady=(10, 2))
    vol_slider = ctk.CTkSlider(window, from_=0, to=100, command=on_volume_change)
    vol_slider.set(volume * 100)
    vol_slider.pack()

    sound_switch = ctk.CTkSwitch(window, text="Увімкнено", command=on_toggle_sound)
    sound_switch.select()
    sound_switch.pack(pady=5)

    autostart_switch = ctk.CTkSwitch(window, text="Автозапуск", command=on_toggle_autostart)
    if check_autostart():
        autostart_switch.select()
    autostart_switch.pack(pady=5)

    ctk.CTkButton(window, text="Згорнути в трей", command=minimize_to_tray).pack(pady=(10, 0))

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()

# --- Старт ---
if __name__ == "__main__":
    threading.Thread(target=setup_tray, daemon=True).start()
    tray_ready.wait()
    start_listener()
    create_gui()
