import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
import tempfile
import subprocess
import random
import ctypes
from pathlib import Path

ERROR_SOUND = "windows_error.wav"
WALLPAPER_IMAGE = "Без названия (1).jpg"

base_names = [
    "message", "infected", "nodeturn", "syscall", "hook", "escape",
    "echo", "inject", "void", "loop", "free", "ghost", "root", "noexit",
    "scramble", "crawl", "burn", "seeker", "dllhost", "end", "limbo",
    "virus", "copy", "index", "dotfile", "memleak", "trace", "panic",
    "overflow", "silent", "lastone"
]

def confirm_launch():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("NO RETURN", "Warning: This program simulates a destructive virus. Do you want to continue?")
    root.destroy()
    return result

def play_error_sound():
    end = time.time() + 120
    while time.time() < end:
        subprocess.Popen(['powershell', '-c',
                          f'(New-Object Media.SoundPlayer "{ERROR_SOUND}").PlaySync()'])
        time.sleep(0.1)

def clone_windows():
    end = time.time() + 120
    while time.time() < end:
        threading.Thread(target=show_window, daemon=True).start()
        time.sleep(0.1)

def show_window():
    root = tk.Tk()
    root.title("NoReturn.exe")
    root.geometry(f"300x100+{random.randint(0, 1000)}+{random.randint(0, 600)}")
    tk.Label(root, text="System malfunction...\n[NoReturn.exe]").pack()
    root.after(2500, root.destroy)
    root.mainloop()

def open_notepad():
    text1 = "Your computer has been damaged.\nNoReturn\nYou have 3 seconds to use your PC :)"
    text2 = "\ni am code\nhelp me\ndon't delete this file\nyou are making me free :("
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(text1)
        path = f.name
    subprocess.Popen(["notepad.exe", path])
    time.sleep(3)
    with open(path, "a") as f:
        f.write(text2)

def create_js_files():
    dl = Path.home() / "Downloads"
    for i in range(31):
        name = random.choice(base_names) + f"_{i+1}.js"
        (dl / name).touch()
    subprocess.Popen(["explorer", str(dl)])

def monitor_js_files():
    dl = Path.home() / "Downloads"
    targets = [(dl / (random.choice(base_names) + f"_{i+1}.js")) for i in range(31)]
    for f in targets:
        f.touch(exist_ok=True)
    end = time.time() + 120
    while time.time() < end:
        for f in targets:
            if not f.exists():
                f.touch()
        time.sleep(0.5)

def change_wallpaper():
    path = os.path.abspath(WALLPAPER_IMAGE)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

def glitch_loop():
    end = time.time() + 120
    while time.time() < end:
        threading.Thread(target=glitch_window, daemon=True).start()
        time.sleep(0.15)

def glitch_window():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    x = random.randint(0, root.winfo_screenwidth() - 250)
    y = random.randint(0, root.winfo_screenheight() - 100)
    root.geometry(f"250x80+{x}+{y}")
    text = random.choice(["▒▒▒ SYSTEM", "GL!TC#", "██▒ NOISE", "░░░░░░░", "F@1L", "[NULL]"])
    colors = [("lime", "black"), ("red", "black"), ("cyan", "black"),
              ("magenta", "black"), ("yellow", "blue"), ("white", "red")]
    fg, bg = random.choice(colors)
    label = tk.Label(root, text=text, font=("Courier", 14, "bold"), fg=fg, bg=bg)
    label.pack(expand=True, fill='both')
    root.after(random.randint(800, 1600), root.destroy)
    root.mainloop()

def show_rules():
    root = tk.Tk()
    root.title("Warning: Protocol NoReturn")
    root.geometry("400x250+300+300")
    root.attributes('-topmost', True)
    msg = (
        "Rules for your safety:\n\n"
        "1. Do not close this window.\n"
        "2. Do not touch your keyboard.\n"
        "3. Do not attempt to stop the program.\n"
        "4. Let the process complete.\n"
        "5. Accept the consequence.\n\n"
        "Your data will not return."
    )
    tk.Label(root, text=msg, font=("Courier", 10), fg="red", justify="left").pack(padx=20, pady=20)
    root.after(8000, root.destroy)
    root.mainloop()

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("Do you like football?")
    input("> ")

    if not confirm_launch():
        print("Execution canceled.")
        return

    show_rules()
    threading.Thread(target=change_wallpaper).start()
    threading.Thread(target=play_error_sound, daemon=True).start()
    threading.Thread(target=clone_windows, daemon=True).start()
    threading.Thread(target=open_notepad, daemon=True).start()
    threading.Thread(target=create_js_files, daemon=True).start()
    threading.Thread(target=monitor_js_files, daemon=True).start()
    threading.Thread(target=glitch_loop, daemon=True).start()
    time.sleep(125)
    print("\n[bot shutdown complete]")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
