import tkinter as tk
import threading
import time
import psutil  # pip install psutil
import sys
import socket
import platform

# For Windows: import to get active window info
if platform.system() == "Windows":
    import ctypes
    import ctypes.wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    GetForegroundWindow = user32.GetForegroundWindow
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    GetWindowTextW = user32.GetWindowTextW

    def get_active_window_title():
        hwnd = GetForegroundWindow()
        length = GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

else:
    # Fallback for other OSes (Linux/Mac) - returns None, no tracking
    def get_active_window_title():
        return None

# === Your faces dict ===
faces_dict = {
    1: {"face": "(⇀‿‿↼)", "mood": "sleeping - late night, low activity"},
    2: {"face": "(≖‿‿≖)", "mood": "awakening - just woke up"},
    3: {"face": "(◕‿‿◕)", "mood": "awake / normal - casual use"},
    4: {"face": "(⚆⚆)", "mood": "observing (neutral mood) - app switched"},
    5: {"face": "(☉☉)", "mood": "observing (neutral mood) - idle for a bit"},
    6: {"face": "(◕‿◕)", "mood": "observing (happy) - using productive app"},
    7: {"face": "(◕‿―)", "mood": "observing (happy) - long session on productive app"},
    8: {"face": "(°▃▃°)", "mood": "intense - high CPU or stressed"},
    9: {"face": "(⌐■_■)", "mood": "cool - focused, deep work"},
    10: {"face": "(•‿‿•)", "mood": "happy - relaxed and chill"},
    11: {"face": "(^‿‿^)", "mood": "grateful - nice break"},
    12: {"face": "(ᵔ◡◡ᵔ)", "mood": "excited - just started a new app"},
    13: {"face": "(✜‿‿✜)", "mood": "smart - coding or math app active"},
    14: {"face": "(♥‿‿♥)", "mood": "friendly - chatting/social app active"},
    15: {"face": "(☼‿‿☼)", "mood": "motivated - morning energy"},
    16: {"face": "(≖__≖)", "mood": "demotivated - tired, late day"},
    17: {"face": "(-__-)", "mood": "bored - idle for a long time"},
    18: {"face": "(╥☁╥)", "mood": "sad - long break, no activity"},
    19: {"face": "(ب__ب)", "mood": "lonely - no apps used for long"},
    20: {"face": "(☓‿‿☓)", "mood": "broken - error state or crash"},
    21: {"face": "(#__#)", "mood": "debugging - coding session"},
}

# === Globals ===
current_face_num = 1
custom_face = None
scale = 1.0

# Track active app and duration
active_app = None
app_start_time = None

# Define some example "productive" apps and categories (customize as you want)
productive_apps_keywords = ["code", "pycharm", "visual studio", "mathematica", "terminal", "bash", "python", "jupyter", "vscode", "sublime"]
social_apps_keywords = ["discord", "slack", "telegram", "whatsapp", "zoom", "skype", "teams"]
chatting_apps_keywords = social_apps_keywords  # same for now

# === Tkinter main window setup ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.resizable(False, False)
TRANSPARENT_COLOR = 'magenta'
root.config(bg=TRANSPARENT_COLOR)
root.attributes('-transparentcolor', TRANSPARENT_COLOR)

canvas_width = int(175 * scale)
canvas_height = int(75 * scale)
corner_radius = 30

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=TRANSPARENT_COLOR, highlightthickness=0)
canvas.pack()

def draw_rounded_rect(x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x1+r, y1,
        x2-r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y1+r,
        x2, y2-r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x2-r, y2,
        x1+r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y2-r,
        x1, y1+r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

padding = 3
draw_rounded_rect(padding, padding, canvas_width - padding, canvas_height - padding, corner_radius, fill="white", outline="black")

face_label = tk.Label(canvas, text=faces_dict[current_face_num]["face"], font=("Courier", int(28*scale), "bold"), bg="white", fg="black")
face_label.place(relx=0.5, rely=0.5, anchor="center")

# Move window
def start_move(event):
    root.x_start = event.x
    root.y_start = event.y

def do_move(event):
    x = root.winfo_x() + (event.x - root.x_start)
    y = root.winfo_y() + (event.y - root.y_start)
    root.geometry(f"+{x}+{y}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)
face_label.bind("<ButtonPress-1>", start_move)
face_label.bind("<B1-Motion>", do_move)

# Set face functions
def set_face_by_number(num):
    global current_face_num, custom_face
    if num in faces_dict:
        current_face_num = num
        custom_face = None
        face_label.config(text=faces_dict[num]["face"])
        log(f"Set face to #{num}: {faces_dict[num]['face']}")
    else:
        log(f"Face number {num} does not exist.")

def set_custom_face(face_str):
    global custom_face
    custom_face = face_str
    face_label.config(text=face_str)
    log(f"Set custom face: {face_str}")

def log(msg):
    print(msg)

# === Mood logic ===
def time_based_face():
    hour = time.localtime().tm_hour
    if 6 <= hour < 12:
        set_face_by_number(15)  # motivated morning
    elif 12 <= hour < 18:
        set_face_by_number(10)  # happy afternoon
    elif 18 <= hour < 22:
        set_face_by_number(8)   # intense evening
    else:
        set_face_by_number(1)   # sleepy night

def system_mood():
    cpu_load = psutil.cpu_percent(interval=1)
    if cpu_load > 75:
        set_face_by_number(8)  # intense face if CPU is busy
    elif cpu_load < 10:
        set_face_by_number(3)  # normal/chill face if CPU is free

def app_tracking_mood():
    """
    Checks active app, tracks time spent, sets face accordingly with PURPOSE:
    """
    global active_app, app_start_time

    current_app = get_active_window_title()
    now = time.time()

    if current_app is None or current_app.strip() == "":
        # No active window or unsupported OS
        set_face_by_number(19)  # lonely - no app info
        active_app = None
        app_start_time = None
        return

    current_app_lower = current_app.lower()

    if active_app != current_app_lower:
        # App switched
        active_app = current_app_lower
        app_start_time = now
        log(f"App switched to: {current_app}")

        # New app just started
        if any(keyword in current_app_lower for keyword in productive_apps_keywords):
            set_face_by_number(12)  # excited - new productive app
        elif any(keyword in current_app_lower for keyword in chatting_apps_keywords):
            set_face_by_number(14)  # friendly - chatting app active
        else:
            set_face_by_number(4)  # observing neutral - other app
    else:
        # Same app, track duration
        duration = now - app_start_time

        # Purposeful faces based on app and duration
        if any(keyword in current_app_lower for keyword in productive_apps_keywords):
            if duration < 60*10:  # less than 10 mins
                set_face_by_number(6)  # observing happy - starting productive work
            else:
                set_face_by_number(7)  # observing happy - long productive session
        elif any(keyword in current_app_lower for keyword in chatting_apps_keywords):
            if duration < 60*5:
                set_face_by_number(14)  # friendly - chatting newly
            else:
                set_face_by_number(11)  # grateful - chatting for a while
        else:
            # Other apps or unknown apps
            if duration < 60*3:
                set_face_by_number(4)  # observing neutral
            elif duration < 60*15:
                set_face_by_number(5)  # observing neutral (idle longer)
            else:
                set_face_by_number(17)  # bored - long on unproductive app

def pet_mood_loop():
    while True:
        app_tracking_mood()  # updated with active app time tracking
        system_mood()        # system load mood
        time.sleep(15)

threading.Thread(target=pet_mood_loop, daemon=True).start()

# === Settings window ===
settings_window = None

def open_settings_window():
    global settings_window
    if settings_window and settings_window.winfo_exists():
        settings_window.lift()
        return
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x220")  # Slightly taller to fit new button
    settings_window.resizable(False, False)

    tk.Label(settings_window, text="Scale (0.5 to 3.0):").pack(pady=10)

    scale_var = tk.DoubleVar(value=scale)
    scale_slider = tk.Scale(settings_window, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, variable=scale_var)
    scale_slider.pack(padx=20)

    def apply_settings():
        global scale, canvas_width, canvas_height

        scale = scale_var.get()
        new_w = int(175 * scale)
        new_h = int(75 * scale)

        canvas.config(width=new_w, height=new_h)
        canvas.delete("all")
        draw_rounded_rect(padding, padding, new_w - padding, new_h - padding, corner_radius, fill="white", outline="black")

        face_label.config(font=("Courier", int(28 * scale), "bold"))
        face_label.place(relx=0.5, rely=0.5, anchor="center")

        global canvas_width, canvas_height
        canvas_width, canvas_height = new_w, new_h

        settings_window.destroy()

    def reset_scale():
        scale_var.set(1.0)

    apply_btn = tk.Button(settings_window, text="Apply", command=apply_settings)
    apply_btn.pack(pady=(10, 5))

    reset_btn = tk.Button(settings_window, text="Reset Scale", command=reset_scale, fg="crimson")
    reset_btn.pack(pady=(0, 10))

# === Bind the keyboard shortcut for opening settings ===

def on_key_press(event):
    # Check Ctrl+Shift+S (case insensitive)
    # event.state uses a bitmask: Ctrl = 0x4, Shift = 0x1 (on Windows)
    # To be safe cross-platform, check event.state & 0x4 and event.state & 0x1
    if (event.state & 0x4) and (event.state & 0x1) and event.keysym.lower() == 's':
        open_settings_window()

root.bind_all("<KeyPress>", on_key_press)

# === Socket Server for remote commands ===
HOST = '127.0.0.1'
PORT = 65432

def handle_client(conn):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode('utf-8').strip()
            print(f"Received command: {command}")
            if command == "get_faces":
                faces_str = ",".join([f"{k}:{v['face']}" for k,v in faces_dict.items()])
                conn.sendall(faces_str.encode('utf-8'))
            elif command.startswith("set_face"):
                try:
                    num = int(command.split()[1])
                    set_face_by_number(num)
                    conn.sendall(f"Face set to {num}".encode('utf-8'))
                except Exception as e:
                    conn.sendall(f"Error: {e}".encode('utf-8'))
            elif command.startswith("set_custom_face"):
                face = command[len("set_custom_face "):]
                set_custom_face(face)
                conn.sendall(b"Custom face set")
            elif command.startswith("set_scale"):
                try:
                    new_scale = float(command.split()[1])
                    global scale
                    scale = new_scale
                    new_w = int(150 * scale)
                    new_h = int(75 * scale)
                    canvas.config(width=new_w, height=new_h)
                    canvas.delete("all")
                    draw_rounded_rect(padding, padding, new_w - padding, new_h - padding, corner_radius, fill="white", outline="black")
                    face_label.config(font=("Courier", int(28 * scale), "bold"))
                    face_label.place(relx=0.5, rely=0.5, anchor="center")
                    global canvas_width, canvas_height
                    canvas_width, canvas_height = new_w, new_h
                    conn.sendall(b"Scale updated")
                except Exception as e:
                    conn.sendall(f"Error: {e}".encode('utf-8'))
            else:
                conn.sendall(b"Unknown command")

def server_loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            client_thread = threading.Thread(target=handle_client, args=(conn,), daemon=True)
            client_thread.start()

threading.Thread(target=server_loop, daemon=True).start()
def close_on_ctrl_q(event):
    root.destroy()

root.bind_all("<Button-3>", close_on_ctrl_q)

# Start with a time-based face for initial mood
time_based_face()

# Start Tkinter mainloop
root.mainloop()
