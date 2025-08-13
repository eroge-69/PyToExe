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

# Ẩn cửa sổ CMD
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

toaster = ToastNotifier()
keybindings_file = "keybindings.txt"

# Filter packet
F_O = "outbound and ip and ip.Protocol == 17 and ip.Length >= 50 and ip.Length <= 200"
F_I = "inbound and ip and ip.Protocol == 17 and ip.Length >= 50 and ip.Length <= 250"
F_FILTER = "udp and outbound and ((udp.PayloadLength > 50 and udp.PayloadLength < 200) or udp.PayloadLength == 38 or udp.PayloadLength == 42 or udp.PayloadLength == 26)"

# Trạng thái và đối tượng filter
R_O = R_I = R_F = False
W_O = W_I = W_F = None
T_L = threading.Lock()

# Phím mặc định
toggle_key = 'v'
stop_key = 'z'
filter_key = 'b'
keys_configured = False
stream_mode_enabled = False

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
    with open(keybindings_file, 'w') as f:
        f.write(f"{toggle_key}\n{stop_key}\n{filter_key}")

def F_WD():
    global W_O, W_I, W_F
    try:
        for w in [W_O, W_I, W_F]:
            if w:
                w.close()
        W_O = W_I = W_F = None
    except Exception as e:
        print(f"Lỗi đóng WinDivert: {e}")

def T_O():
    global R_O, W_O, B_O
    with T_L:
        if R_O:
            
            toaster.show_toast("RAW Blocking", "🟢 OFF (Outbound)", duration=0.2, threaded=True)
            W_O.close()
            R_O = False
            B_O.config(text="🛰️ TELE FAKE GHOST (OFF)", fg="white", bg="red")
        else:
            
            try:
                W_O = pydivert.WinDivert(F_O)
                W_O.open()
                R_O = True
                toaster.show_toast("RAW Blocking", "🔴 ON (Outbound)", duration=0.2, threaded=True)
                B_O.config(text="🛰️ TELE FAKE GHOST (ONL)", fg="white", bg="green")
            except Exception as e:
                print(f"Lỗi mở Outbound: {e}")

def T_I():
    global R_I, W_I, B_I
    with T_L:
        if R_I:
            
            toaster.show_toast("RAW Blocking", "🟢 OFF (Inbound)", duration=0.2, threaded=True)
            W_I.close()
            R_I = False
            B_I.config(text="🛑 FREEZE PLAYER (OFF)", fg="white", bg="red")
        else:
            
            try:
                W_I = pydivert.WinDivert(F_I)
                W_I.open()
                R_I = True
                toaster.show_toast("RAW Blocking", "🔴 ON (Inbound)", duration=0.2, threaded=True)
                B_I.config(text="🛑 FREEZE PLAYER (ONL)", fg="white", bg="green")
            except Exception as e:
                print(f"Lỗi mở Inbound: {e}")

def T_Filter():
    global R_F, W_F, B_F
    with T_L:
        if R_F:
            
            toaster.show_toast("Filter", "🟢 OFF (Drop Nhanh)", duration=0.2, threaded=True)
            W_F.close()
            R_F = False
            B_F.config(text="👻 GHOST MODE (OFF)", fg="white", bg="red")
        else:
            
            try:
                W_F = pydivert.WinDivert(F_FILTER)
                W_F.open()
                R_F = True
                toaster.show_toast("Filter", "🔴 ON (Drop Nhanh)", duration=0.2, threaded=True)
                B_F.config(text="👻 GHOST MODE (ONL)", fg="white", bg="green")
            except Exception as e:
                print(f"Lỗi mở Filter: {e}")

def update_keys():
    global toggle_key, stop_key, filter_key, keys_configured
    if not keys_configured:
        toggle_key = entry_toggle_key.get()
        stop_key = entry_stop_key.get()
        filter_key = entry_filter_key.get()
        keys_configured = True
        messagebox.showinfo("Thông báo", f"Đã cập nhật phím:\nTele: {toggle_key}\nNgưng: {stop_key}\nFilter: {filter_key}")
        entry_toggle_key.config(state="disabled")
        entry_stop_key.config(state="disabled")
        entry_filter_key.config(state="disabled")
        save_keybindings()

def create_ui():
    global B_O, B_I, B_F, entry_toggle_key, entry_stop_key, entry_filter_key, R

    R = tk.Tk()
    R.title("Unk Cheats | ")
    R.geometry("300x340")
    R.resizable(False, False)

    try:
        background_image = Image.open("background.gif")
        background_image = background_image.resize((300, 340), Image.ANTIALIAS)
        bg = ImageTk.PhotoImage(background_image)
        bg_label = tk.Label(R, image=bg)
        bg_label.image = bg
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Lỗi ảnh nền: {e}")

    tk.Label(R, text="🔥 </>Dev : Unknown 🔥", font=("Segoe UI", 11, "bold"), bg="pink").pack(pady=6)

    B_I = tk.Button(R, text="🛑 FREEZE PLAYER", command=lambda: threading.Thread(target=T_I, daemon=True).start(),
                    fg="white", bg="black", font=("Segoe UI", 9, "bold"), height=2)
    B_I.pack(fill=tk.X, padx=30, pady=4)

    B_O = tk.Button(R, text="☯TELE FAKE GHOST", command=lambda: threading.Thread(target=T_O, daemon=True).start(),
                    fg="white", bg="black", font=("Segoe UI", 9, "bold"), height=2)
    B_O.pack(fill=tk.X, padx=30, pady=4)

    B_F = tk.Button(R, text="👻 GHOST MODE", command=lambda: threading.Thread(target=T_Filter, daemon=True).start(),
                    fg="white", bg="black", font=("Segoe UI", 9, "bold"), height=2)
    B_F.pack(fill=tk.X, padx=30, pady=4)

    frame_keys = tk.Frame(R)
    frame_keys.pack(pady=8)

    entry_toggle_key = tk.Entry(frame_keys, width=8)
    entry_toggle_key.insert(0, toggle_key)
    entry_toggle_key.pack(side=tk.LEFT, padx=3)
    entry_stop_key = tk.Entry(frame_keys, width=8)
    entry_stop_key.insert(0, stop_key)
    entry_stop_key.pack(side=tk.LEFT, padx=3)
    entry_filter_key = tk.Entry(frame_keys, width=8)
    entry_filter_key.insert(0, filter_key)
    entry_filter_key.pack(side=tk.LEFT, padx=3)

    tk.Button(R, text="💾 BIND KEYS", command=update_keys, width=20).pack(pady=5)

    R.protocol("WM_DELETE_WINDOW", lambda: (F_WD(), os._exit(0)))

    def toggle_stream_mode():
        hwnd = ctypes.windll.user32.GetParent(R.winfo_id())
        global stream_mode_enabled
        stream_mode_enabled = not stream_mode_enabled
        if stream_mode_enabled:
            R.overrideredirect(True)
            R.wm_attributes("-topmost", True)
            ctypes.windll.user32.ShowWindow(hwnd, 1)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00000080)
        else:
            R.overrideredirect(False)
            R.wm_attributes("-topmost", False)
            ctypes.windll.user32.ShowWindow(hwnd, 1)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00000000)

    def start_move(event):
        R.x = event.x
        R.y = event.y

    def do_move(event):
        deltax = event.x - R.x
        deltay = event.y - R.y
        R.geometry(f"+{R.winfo_x() + deltax}+{R.winfo_y() + deltay}")

    R.bind("<Button-1>", start_move)
    R.bind("<B1-Motion>", do_move)

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
            elif keyboard.is_pressed('ctrl') and e.name == 'k':
                toggle_stream_mode()

    keyboard.hook(handle_global_key)
    R.mainloop()

# Run
read_keybindings()
create_ui()