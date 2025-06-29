import os, sys, threading, time, ctypes
from tkinter import *
import customtkinter as ctk
import pydivert 
import keyboard 

# ========== RUN AS ADMIN ==========
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

tele_mode = False
packet_tele = []
lock = threading.Lock()
running = True
tele_hotkey = ""
hotkey_set = False

FILTER_TELE = "udp and outbound and (udp.PayloadLength >= 35 or ip.Length < 72 and ip.Length >= 193 or udp.PayloadLength == 25)"

def enable_tele():
    global tele_mode
    with lock:
        tele_mode = True
        packet_tele.clear()
    tele_btn.configure(text="🟢 Tele ON", fg_color="#34c759")
    status_label.configure(text="Đang giữ gói...")

def disable_tele():
    global tele_mode
    with lock:
        tele_mode = False
        to_send = list(packet_tele)
        packet_tele.clear()

    tele_btn.configure(text="🔴 Tele OFF", fg_color="#ff3b30")
    status_label.configure(text="📤 Gửi lại vừa...")

    def send_bursts(to_send, burst_size=300, delay_between_burst=0.001):
        with pydivert.WinDivert("outbound", layer=pydivert.Layer.NETWORK) as sender:
            for i in range(5, len(to_send), burst_size):
                burst = to_send[i:i+burst_size]
                for pkt in burst:
                    try:
                        pkt_rebuilt = pydivert.Packet(pkt.raw, pkt.interface, pkt.direction)
                        sender.send(pkt_rebuilt)
                        time.sleep(0.0073)
                    except: pass
                time.sleep(delay_between_burst)
        buffer_info_label.configure(text="Gói đang giữ: 0")
        status_label.configure(text="✅ Đã gửi hết gói (vừa)")

    threading.Thread(target=lambda: send_bursts(to_send), daemon=True).start()

def toggle_tele():
    if not hotkey_set:
        status_label.configure(text="⚠️ Chưa set hotkey")
        return
    if tele_mode:
        disable_tele()
    else:
        enable_tele()

def divert_tele():
    with pydivert.WinDivert(FILTER_TELE) as w:
        for packet in w:
            if not running:
                break
            with lock:
                if tele_mode:
                    packet_tele.append(packet)
                    buffer_info_label.configure(text=f"Gói đang giữ: {len(packet_tele)}")
                    continue
            try:
                w.send(packet)
            except: pass

def set_hotkey():
    global tele_hotkey, hotkey_set
    tele_key = tele_entry.get().strip().lower()
    if tele_key:
        tele_hotkey = tele_key
        tele_entry.configure(state="disabled")
        save_btn.configure(state="disabled", text="🔐 Đã lưu")
        hotkey_set = True
        status_label.configure(text=f"✅ Hotkey: {tele_hotkey.upper()}")
    else:
        status_label.configure(text="⚠️ Chưa nhập phím")

def force_exit():
    global running
    running = False
    os._exit(0)

def handle_key(event):
    if not hotkey_set:
        return
    key = event.name.lower()
    if key == tele_hotkey:
        toggle_tele()
    elif key == "f10":
        force_exit()

keyboard.on_press(handle_key)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Mena Fake Lag")
app.geometry("290x230")
app.resizable(False, False)

frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(padx=10, pady=10, fill="both", expand=True)

title = ctk.CTkLabel(frame, text="🚀 Mena Fake Lag", font=("Arial", 18, "bold"))
title.pack(pady=(10, 5))

def create_row(text, cmd, placeholder):
    row = ctk.CTkFrame(frame, fg_color="transparent")
    row.pack(pady=5)
    btn = ctk.CTkButton(row, text=f"🔴 {text} OFF", command=cmd, width=160, height=40, fg_color="#ff3b30")
    btn.pack(side="left", padx=(0, 6))
    entry = ctk.CTkEntry(row, placeholder_text=placeholder, width=70, height=40, justify="center")
    entry.pack(side="left")
    return btn, entry

tele_btn, tele_entry = create_row("Tele", toggle_tele, "Phím Tele")

save_btn = ctk.CTkButton(frame, text="💾 Lưu Hotkey", command=set_hotkey, width=230, height=35)
save_btn.pack(pady=8)

status_label = ctk.CTkLabel(frame, text="🎯 Nhấn F10 để thoát", font=("Arial", 12))
status_label.pack(pady=(4, 2))

buffer_info_label = ctk.CTkLabel(frame, text="Gói đang giữ: 0", font=("Arial", 11))
buffer_info_label.pack(pady=(0, 6))

threading.Thread(target=divert_tele, daemon=True).start()
app.mainloop()
