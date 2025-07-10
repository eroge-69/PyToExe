import os
import sys
import pydivert
import keyboard
import threading
import time
import winsound
import ctypes
import tkinter as tk
from tkinter import messagebox
from win10toast import ToastNotifier
from PIL import Image, ImageTk
import mouse

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

toaster = ToastNotifier()
keybindings_file = "keybindings.txt"

F_O = "outbound and ip and ip.Protocol == 17 and ip.Length >= 50 and ip.Length <= 200"
F_I = "inbound and ip and ip.Protocol == 17 and ip.Length >= 50 and ip.Length <= 250"
F_FILTER = "udp and outbound and ((udp.PayloadLength > 50 and udp.PayloadLength < 200) or udp.PayloadLength == 38 or udp.PayloadLength == 42 or udp.PayloadLength == 26)"

R_O = R_I = R_F = False
W_O = W_I = W_F = None
T_L = threading.Lock()

toggle_key = 'v'
stop_key = 'z'
filter_key = 'b'
keys_configured = False
stream_mode_enabled = False

beep_lock = threading.Lock()
def play_beep(frequency):
    with beep_lock:
        try:
            winsound.Beep(frequency, 100)
        except RuntimeError:
            pass

def read_keybindings():
    global toggle_key, stop_key, filter_key
    try:
        with open(keybindings_file, 'r') as f:
            lines = f.readlines()
            toggle_key = lines[0].strip() if len(lines) > 0 else 'v'
            stop_key = lines[1].strip() if len(lines) > 1 else 'z'
            filter_key = lines[2].strip() if len(lines) > 2 else 'b'
    except FileNotFoundError:
        toggle_key = 'v'
        stop_key = 'z'
        filter_key = 'b'

def save_keybindings():
    try:
        with open(keybindings_file, 'w') as f:
            f.write(f"{toggle_key}\n{stop_key}\n{filter_key}")
    except Exception as e:
        print(f"Error saving keybindings: {e}")

def F_WD():
    global W_O, W_I, W_F
    try:
        for w in [W_O, W_I, W_F]:
            if w:
                w.close()
        W_O = W_I = W_F = None
    except Exception as e:
        print(f"Error closing WinDivert: {e}")

def T_O():
    global R_O, W_O, B_O
    with T_L:
        if R_O:
            toaster.show_toast("🛰️ Tele Ghost", "OFF", duration=0.2, threaded=True)
            play_beep(400)
            W_O.close()
            R_O = False
            B_O.config(text="🛰️ Tele Ghost (OFF)", fg="red", bg="black")
        else:
            try:
                W_O = pydivert.WinDivert(F_O)
                W_O.open()
                R_O = True
                toaster.show_toast("🟢 Tele Ghost", "ON", duration=0.2, threaded=True)
                play_beep(600)
                B_O.config(text="🟢 Tele Ghost (ON)", fg="lime", bg="black")
            except Exception as e:
                print(f"Error opening Outbound: {e}")

def T_I():
    global R_I, W_I, B_I
    with T_L:
        if R_I:
            toaster.show_toast("🛑 Freeze Incoming", "OFF", duration=0.2, threaded=True)
            play_beep(400)
            W_I.close()
            R_I = False
            B_I.config(text="🛑 Freeze Incoming (OFF)", fg="red", bg="black")
        else:
            try:
                W_I = pydivert.WinDivert(F_I)
                W_I.open()
                R_I = True
                toaster.show_toast(" 🟢 Freeze Incoming", "ON", duration=0.2, threaded=True)
                play_beep(600)
                B_I.config(text="🟢 Freeze Incoming (ON)", fg="lime", bg="black")
            except Exception as e:
                print(f"Error opening Inbound: {e}")

def T_Filter():
    global R_F, W_F, B_F
    with T_L:
        if R_F:
            toaster.show_toast("👻 Ghost Mode", "OFF", duration=0.2, threaded=True)
            play_beep(400)
            W_F.close()
            R_F = False
            B_F.config(text="👻 Ghost Mode (OFF)", fg="red", bg="black")
        else:
            try:
                W_F = pydivert.WinDivert(F_FILTER)
                W_F.open()
                R_F = True
                toaster.show_toast("🟢 Ghost Mode", "ON", duration=0.2, threaded=True)
                play_beep(600)
                B_F.config(text="🟢Ghost Mode (ON)", fg="lime", bg="black")
            except Exception as e:
                print(f"Error opening Filter: {e}")

def update_keys():
    global toggle_key, stop_key, filter_key, keys_configured
    toggle_key = entry_toggle_key.get()
    stop_key = entry_stop_key.get()
    filter_key = entry_filter_key.get()
    keys_configured = True
    entry_toggle_key.config(state="disabled")
    entry_stop_key.config(state="disabled")
    entry_filter_key.config(state="disabled")
    messagebox.showinfo("Notification", f"Keys updated:\nTele: {toggle_key}\nStop: {stop_key}\nFilter: {filter_key}")
    save_keybindings()

def create_ui():
    global B_O, B_I, B_F, entry_toggle_key, entry_stop_key, entry_filter_key

    R = tk.Tk()
    R.title("Mani272!!")
    R.geometry("300x420")
    R.configure(bg="#242323")
    R.resizable(False, False)

    try:
        bg_img = Image.open("background_new.png")
        bg_img = bg_img.resize((300, 420))
        bg = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(R, image=bg)
        bg_label.image = bg
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Background image error: {e}")

    header = tk.Label(R, text="Mani272!!", font=("Consolas", 16, "bold"), bg="#242323", fg="white")
    header.pack(pady=8)

    B_I = tk.Button(R, text="🛑 Freeze Incoming (OFF)", command=lambda: threading.Thread(target=T_I, daemon=True).start(), font=("Arial", 11), bg="black", fg="red", height=2)
    B_I.pack(fill=tk.X, padx=40, pady=4)

    B_O = tk.Button(R, text="🛰️ Tele Ghost (OFF)", command=lambda: threading.Thread(target=T_O, daemon=True).start(), font=("Arial", 11), bg="black", fg="red", height=2)
    B_O.pack(fill=tk.X, padx=40, pady=4)

    B_F = tk.Button(R, text="👻 Ghost Mode (OFF)", command=lambda: threading.Thread(target=T_Filter, daemon=True).start(), font=("Arial", 11), bg="black", fg="red", height=2)
    B_F.pack(fill=tk.X, padx=40, pady=4)

    frame_keys = tk.Frame(R, bg="#2e2e2e")
    frame_keys.pack(pady=4)

    entry_toggle_key = tk.Entry(frame_keys, width=5)
    entry_toggle_key.insert(0, toggle_key)
    entry_toggle_key.pack(side=tk.LEFT, padx=3)
    entry_stop_key = tk.Entry(frame_keys, width=5)
    entry_stop_key.insert(0, stop_key)
    entry_stop_key.pack(side=tk.LEFT, padx=3)
    entry_filter_key = tk.Entry(frame_keys, width=5)
    entry_filter_key.insert(0, filter_key)
    entry_filter_key.pack(side=tk.LEFT, padx=3)

    tk.Button(R, text="💾 Save Keys", command=update_keys, font=("Arial", 9), bg="black", fg="white").pack(pady=4)

    tk.Label(R, text="Update Mani Ghost Hack  -  OB49", bg="#2e2e2e", fg="white", font=("Arial", 9, "italic")).pack(pady=2) 
    tk.Label(R, text="[+] 100 % Safe & Secure", bg="#2e2e2e", fg="white", font=("Arial", 9, "italic")).pack(pady=2)
    tk.Label(R, text="Join our Discord Server - https://discord.gg/mani272", bg="#ff5959", fg="white", font=("Arial", 9, "bold")).pack(pady=2)
    tk.Label(R, text="</> Developer: Mani272!!", fg="white", bg="#2e2e2e", font=("Consolas", 10, "bold")).pack(side=tk.BOTTOM, pady=0)

    def handle_global_key(e):
        if e.event_type == "down":
            if e.name == toggle_key:
                threading.Thread(target=T_O, daemon=True).start()
            elif e.name == stop_key:
                threading.Thread(target=T_I, daemon=True).start()
            elif e.name == filter_key:
                threading.Thread(target=T_Filter, daemon=True).start()
            elif e.name == 'f10':
                F_WD()
                os._exit(0)

    keyboard.hook(handle_global_key)
    R.mainloop()

read_keybindings()
create_ui()
