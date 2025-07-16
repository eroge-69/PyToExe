import os
import sys
import winreg
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import simpledialog, messagebox

APP_NAME = "ReminderApp"
FOLDER_PATH = os.path.join(os.path.expanduser("~"), ".reminder")
NOTE_PATH = os.path.join(FOLDER_PATH, "note.txt")

def ensure_data_folder():
    os.makedirs(FOLDER_PATH, exist_ok=True)

def load_note():
    if os.path.exists(NOTE_PATH):
        with open(NOTE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_note(note):
    with open(NOTE_PATH, "w", encoding="utf-8") as f:
        f.write(note)

def ask_note():
    root = tk.Tk()
    root.withdraw()
    note = simpledialog.askstring("Erinnerung eintragen", "Woran soll ich dich immer erinnern?")
    if note:
        save_note(note)
        messagebox.showinfo("Gespeichert", "Deine Erinnerung wurde gespeichert.")
    else:
        messagebox.showwarning("Abgebrochen", "Keine Erinnerung gespeichert.")

def show_toast(text):
    toaster = ToastNotifier()
    toaster.show_toast("💡 Erinnerung", text, duration=10, icon_path=None, threaded=True)

def add_to_autostart():
    # Registriert sich in Windows-Autostart (HKEY_CURRENT_USER)
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)

def main():
    ensure_data_folder()
    add_to_autostart()
    note = load_note()
    if note:
        show_toast(note)
    else:
        ask_note()

if __name__ == "__main__":
    main()
