import tkinter as tk
from tkinter import ttk
import pyautogui
import numpy as np
import cv2
import dxcam
import threading
import time
import keyboard
import ctypes
from PIL import Image, ImageTk

# State Variables
aimbot_running = False
target_color = (255, 0, 0)
tolerance = 60
fps = 60
smoothness = 10
use_color_range = False
use_prediction = False
show_red_dot = False
show_preview = False
use_relative_move = False
scan_area = 1.0
last_position = None
preview_imgtk = None

# Camera setup
camera = dxcam.create(output_color="BGR")
camera.start(target_fps=fps)

# Transparent overlay for FOV
def create_overlay():
    overlay = tk.Toplevel()
    overlay.overrideredirect(True)
    overlay.geometry(f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0")
    overlay.attributes("-topmost", True)
    overlay.attributes("-transparentcolor", "black")
    overlay.configure(bg="black")
    canvas = tk.Canvas(overlay, width=overlay.winfo_screenwidth(), height=overlay.winfo_screenheight(),
                       bg="black", highlightthickness=0)
    canvas.pack()
    return overlay, canvas

overlay, canvas = create_overlay()

def draw_fov_circle():
    canvas.delete("all")
    w = overlay.winfo_screenwidth()
    h = overlay.winfo_screenheight()
    radius = int(min(w, h) * scan_area / 2)
    cx, cy = w // 2, h // 2
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="lime", width=2)

# Color match logic
def is_color_match(pixel, target, tolerance):
    if use_color_range:
        r, g, b = pixel
        if r > 150 and g < 100 and b < 100: return True
        if g > 150 and r < 100 and b < 100: return True
        if b > 150 and r < 100 and g < 100: return True
        return False
    else:
        return all(abs(pixel[i] - target[i]) < tolerance for i in range(3))

# Scan area calculation
def get_center_scan_order(width, height, step=2):
    cx, cy = width // 2, height // 2
    area_w, area_h = int(width * scan_area), int(height * scan_area)
    start_x, start_y = cx - area_w // 2, cy - area_h // 2
    coords = []
    for y in range(start_y, start_y + area_h, step):
        for x in range(start_x, start_x + area_w, step):
            if 0 <= x < width and 0 <= y < height:
                coords.append((x, y))
    return coords

# Predict position
def predict_position(current, last):
    if not last: return current
    dx = current[0] - last[0]
    dy = current[1] - last[1]
    return (current[0] + dx, current[1] + dy)

# Aimbot logic
def aimbot_loop():
    global aimbot_running, last_position, preview_imgtk
    while aimbot_running:
        img = camera.get_latest_frame()
        if img is None:
            continue
        height, width, _ = img.shape
        coords = get_center_scan_order(width, height, step=2)
        found_pos = None
        for (x, y) in coords:
            pixel = img[y, x][:3]
            if is_color_match(pixel, target_color, tolerance):
                found_pos = (x, y)
                break
        if found_pos:
            aim_pos = predict_position(found_pos, last_position) if use_prediction else found_pos
            if use_relative_move:
                screen_w, screen_h = pyautogui.size()
                dx = aim_pos[0] - screen_w // 2
                dy = aim_pos[1] - screen_h // 2
                ctypes.windll.user32.mouse_event(0x0001, int(dx), int(dy), 0, 0)
            else:
                move_duration = smoothness / 1000
                pyautogui.moveTo(*aim_pos, duration=move_duration)
            last_position = found_pos

        if show_preview:
            preview_imgtk = update_preview(img)

        time.sleep(1 / max(fps, 1))

# Update preview
def update_preview(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil = img_pil.resize((480, 270))
    imgtk = ImageTk.PhotoImage(image=img_pil)
    preview_label.config(image=imgtk)
    preview_label.image = imgtk
    return imgtk

# Toggle aimbot
def toggle_aimbot():
    global aimbot_running
    if not aimbot_running:
        aimbot_running = True
        status_label.config(text="Aimbot: ON", fg="green")
        threading.Thread(target=aimbot_loop, daemon=True).start()
    else:
        aimbot_running = False
        status_label.config(text="Aimbot: OFF", fg="red")
        preview_label.config(image='')

# Pick color
def pick_color():
    global target_color
    root.withdraw()
    time.sleep(1)
    x, y = pyautogui.position()
    screenshot = pyautogui.screenshot()
    picked = screenshot.getpixel((x, y))
    target_color = (picked[2], picked[1], picked[0])
    color_label.config(text=f"🎯 Target Color: {picked}")
    root.deiconify()

# Sliders
def update_fps(val):
    global fps
    fps = int(val)
    fps_value_label.config(text=f"{fps}")
    camera.stop()
    camera.start(target_fps=fps)

def update_smoothness(val):
    global smoothness
    smoothness = int(val)
    smooth_value_label.config(text=f"{smoothness}")

def update_tolerance(val):
    global tolerance
    tolerance = int(val)
    tol_value_label.config(text=f"{tolerance}")

def update_scan(val):
    global scan_area
    scan_area = float(val)/100
    scan_value_label.config(text=f"{val}%")
    draw_fov_circle()

# Toggle variables
def toggle_var(name):
    globals()[name] = not globals()[name]
    if name == 'use_color_range':
        range_label.config(text=f"Color Range: {'ON' if use_color_range else 'OFF'}")
    elif name == 'use_prediction':
        predict_label.config(text=f"AI Predict: {'ON' if use_prediction else 'OFF'}")
    elif name == 'show_red_dot':
        dot_label.config(text=f"Red Dot: {'ON' if show_red_dot else 'OFF'}")
    elif name == 'use_relative_move':
        relative_label.config(text=f"Relative Move: {'ON' if use_relative_move else 'OFF'}")

def listen_hotkeys():
    keyboard.add_hotkey('f2', pick_color)
    keyboard.add_hotkey('0', toggle_aimbot)
    keyboard.wait()

# GUI
root = tk.Tk()
root.title("🎯 Color Aimbot (DXCAM)")
root.geometry("600x850")
root.configure(bg="#1e1e1e")

font_style = ("Consolas", 10)
label_config = {"font": font_style, "bg": "#1e1e1e", "fg": "white"}

tk.Label(root, text="🎯 Color Aimbot (DXCAM)", font=("Consolas", 14, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)
color_label = tk.Label(root, text="🎯 Target Color: (255, 0, 0)", **label_config)
color_label.pack(pady=5)

ttk.Button(root, text="Pick Color (F2)", command=pick_color).pack(pady=5)
ttk.Button(root, text="Toggle Aimbot (0)", command=toggle_aimbot).pack(pady=5)

status_label = tk.Label(root, text="Aimbot: OFF", **label_config)
status_label.config(fg="red")
status_label.pack(pady=10)

def make_slider(label, from_, to, command, initial):
    tk.Label(root, text=label, **label_config).pack()
    scale = tk.Scale(root, from_=from_, to=to, orient="horizontal", command=command,
                     bg="#2e2e2e", fg="white", troughcolor="#444")
    scale.set(initial)
    scale.pack()
    val_label = tk.Label(root, text=f"{initial}", **label_config)
    val_label.pack(pady=2)
    return val_label

fps_value_label = make_slider("Scan Speed (FPS)", 10, 120, update_fps, fps)
smooth_value_label = make_slider("Smoothness", 0, 20, update_smoothness, smoothness)
tol_value_label = make_slider("Color Tolerance", 0, 100, update_tolerance, tolerance)
scan_value_label = make_slider("Scan Area %", 10, 100, update_scan, int(scan_area * 100))

toggle_frame = tk.Frame(root, bg="#1e1e1e")
toggle_frame.pack(pady=10)

def make_toggle(row, text, var_name):
    ttk.Checkbutton(toggle_frame, text=text, command=lambda: toggle_var(var_name)).grid(row=row, column=0, sticky="w")
    label = tk.Label(toggle_frame, text=f"{text}: OFF", **label_config)
    label.grid(row=row, column=1)
    return label

range_label = make_toggle(0, "Use RGB Color Range", "use_color_range")
predict_label = make_toggle(1, "AI Movement Predict", "use_prediction")
dot_label = make_toggle(2, "Show Red Dot", "show_red_dot")
relative_label = make_toggle(3, "Use Relative Mouse Move", "use_relative_move")

ttk.Checkbutton(root, text="Show Preview", command=lambda: toggle_var('show_preview')).pack(pady=5)
preview_label = tk.Label(root, bg="#1e1e1e")
preview_label.pack(pady=10)

tk.Label(root, text="Creator: SH4DY410", font=("Consolas", 9), fg="gray", bg="#1e1e1e").pack(side="bottom", anchor="se", padx=10, pady=5)

threading.Thread(target=listen_hotkeys, daemon=True).start()
draw_fov_circle()
root.mainloop()

