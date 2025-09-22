import tkinter as tk
import psutil
import time
import threading
import winsound

def get_speed():
    old_value = psutil.net_io_counters()
    old_recv = old_value.bytes_recv
    old_sent = old_value.bytes_sent
    time.sleep(1)  # measure per second
    new_value = psutil.net_io_counters()
    new_recv = new_value.bytes_recv
    new_sent = new_value.bytes_sent

    download_speed = (new_recv - old_recv) / 1024  # KBps
    upload_speed = (new_sent - old_sent) / 1024

    if download_speed > 1024:
        d_speed = f"↓ {download_speed/1024:.1f} Mbps"
    else:
        d_speed = f"↓ {download_speed:.1f} Kbps"

    if upload_speed > 1024:
        u_speed = f"↑ {upload_speed/1024:.1f} Mbps"
    else:
        u_speed = f"↑ {upload_speed:.1f} Kbps"

    return d_speed, u_speed

def update_speed():
    while True:
        d, u = get_speed()
        label.config(text=f"{d}\n{u}")
        root.update_idletasks()

# --- Dragging functionality ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# --- Right-click menu ---
def show_menu(event):
    menu.post(event.x_root, event.y_root)

def quit_app():
    root.destroy()

def toggle_taskbar():
    global in_taskbar
    if in_taskbar:
        root.overrideredirect(True)   # hide from taskbar
        menu.entryconfig(1, label="Keep in Taskbar")
        in_taskbar = False
    else:
        root.overrideredirect(False)  # show in taskbar
        root.update_idletasks()
        menu.entryconfig(1, label="Remove from Taskbar")
        in_taskbar = True

# GUI setup
root = tk.Tk()
root.title("IKA Internet Speed Monitor")

root.configure(bg="green")
root.overrideredirect(True)   # start hidden from taskbar
root.attributes("-topmost", True)

label = tk.Label(root, text="Starting...", fg="white", bg="green", font=("Segoe UI", 12))
label.pack(padx=5, pady=2)

# Enable dragging
label.bind("<Button-1>", start_move)
label.bind("<ButtonRelease-1>", stop_move)
label.bind("<B1-Motion>", do_move)

# Right-click menu
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Exit", command=quit_app)
menu.add_command(label="Keep in Taskbar", command=toggle_taskbar)
label.bind("<Button-3>", show_menu)

# Track state
in_taskbar = False

# Start background thread
threading.Thread(target=update_speed, daemon=True).start()

# --- Beep on startup ---
winsound.Beep(1000, 200)  # frequency=1000Hz, duration=300ms
# winsound.Beep(1200, 200)

root.mainloop()
