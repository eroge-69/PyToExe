import sys
import ctypes
import tkinter as tk
from tkinter import messagebox

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Admin Required", "This script needs to be run as Administrator to function properly.")
    sys.exit(0)

# ----------------------------

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pynput import keyboard, mouse
from pynput.mouse import Controller, Button
import time

root = tk.Tk()
root.title("Recoil Control")
root.geometry("600x350")

recoil_enabled = False
mouse_controller = Controller()

left_pressed = False
right_pressed = False

right_val = tk.IntVar(value=0)
left_val = tk.IntVar(value=0)
up_val = tk.IntVar(value=0)
down_val = tk.IntVar(value=0)

mode_var = tk.StringVar(value="Left Click Only")

def recoil_loop():
    global left_pressed, right_pressed
    while True:
        if recoil_enabled:
            if mode_var.get() == "Left Click Only" and left_pressed:
                move_mouse()
            elif mode_var.get() == "Left + Right Click" and left_pressed and right_pressed:
                move_mouse()
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01)

def move_mouse():
    x_move = right_val.get() - left_val.get()
    y_move = down_val.get() - up_val.get()
    if x_move != 0 or y_move != 0:
        mouse_controller.move(x_move, y_move)
    time.sleep(0.01)

def on_click(x, y, button, pressed):
    global left_pressed, right_pressed
    if button == Button.left:
        left_pressed = pressed
    elif button == Button.right:
        right_pressed = pressed

def on_press(key):
    global recoil_enabled
    if key == keyboard.Key.f1:
        recoil_enabled = True
        update_status()
    elif key == keyboard.Key.f2:
        recoil_enabled = False
        update_status()

def update_status():
    status_text = "Macro ON" if recoil_enabled else "Macro OFF"
    status_label.config(text=status_text)

def update_slider_labels(*args):
    right_val_label.config(text=str(right_val.get()))
    left_val_label.config(text=str(left_val.get()))
    up_val_label.config(text=str(up_val.get()))
    down_val_label.config(text=str(down_val.get()))
    draw_movement_visual()

def save_config():
    config = {
        "right": right_val.get(),
        "left": left_val.get(),
        "up": up_val.get(),
        "down": down_val.get(),
        "mode": mode_var.get()
    }
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Save configuration"
    )
    if not file_path:
        return
    try:
        with open(file_path, 'w') as f:
            for key, val in config.items():
                f.write(f"{key}={val}\n")
        messagebox.showinfo("Save Config", "Configuration saved successfully!")
    except Exception as e:
        messagebox.showerror("Save Config", f"Failed to save configuration:\n{e}")

def load_config():
    file_path = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Load configuration"
    )
    if not file_path:
        return
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        config = {}
        for line in lines:
            if '=' in line:
                key, val = line.strip().split('=', 1)
                config[key] = val
        if 'right' in config:
            right_val.set(int(config['right']))
        if 'left' in config:
            left_val.set(int(config['left']))
        if 'up' in config:
            up_val.set(int(config['up']))
        if 'down' in config:
            down_val.set(int(config['down']))
        if 'mode' in config and config['mode'] in ["Left Click Only", "Left + Right Click"]:
            mode_var.set(config['mode'])
        update_slider_labels()
        messagebox.showinfo("Load Config", "Configuration loaded successfully!")
    except Exception as e:
        messagebox.showerror("Load Config", f"Failed to load configuration:\n{e}")

def draw_movement_visual():
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    center_x = width // 2
    center_y = height // 2

    x_move = right_val.get() - left_val.get()
    y_move = down_val.get() - up_val.get()

    max_slider = 20
    max_length_x = width // 2 - 20
    max_length_y = height // 2 - 20

    dot_x = center_x + int(x_move / max_slider * max_length_x) if max_slider != 0 else center_x
    dot_y = center_y + int(y_move / max_slider * max_length_y) if max_slider != 0 else center_y

    canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5, fill="black")

    color = "yellow"
    if y_move < 0:
        intensity = min(abs(y_move) / max_slider, 1)
        green = int(255 * intensity)
        color = f"#00{green:02x}00"
    elif y_move > 0:
        intensity = min(abs(y_move) / max_slider, 1)
        red = int(255 * intensity)
        color = f"#{red:02x}0000"

    canvas.create_line(center_x, center_y, center_x, dot_y, fill=color, width=3)
    canvas.create_line(center_x, center_y, dot_x, center_y, fill="gray", width=3)
    canvas.create_oval(dot_x-7, dot_y-7, dot_x+7, dot_y+7, fill=color, outline="black")

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

recoil_thread = threading.Thread(target=recoil_loop, daemon=True)
recoil_thread.start()

status_label = tk.Label(root, text="Macro OFF", font=("Arial", 12), fg="red")
status_label.pack(side='bottom', anchor='e', padx=10, pady=5)

instructions_label = tk.Label(root, text="Press F1 to ON, F2 to OFF", font=("Arial", 10))
instructions_label.pack(side='bottom', pady=2)

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

controls_frame = ttk.Frame(main_frame)
controls_frame.pack(side='left', fill='both', expand=True)

def create_slider_with_label(text, variable):
    container = ttk.Frame(controls_frame)
    container.pack(fill='x', pady=5)

    label = ttk.Label(container, text=text)
    label.pack(side='left')

    slider = ttk.Scale(container, from_=-20, to=20, orient='horizontal', variable=variable)
    slider.pack(side='left', fill='x', expand=True, padx=5)

    value_label = ttk.Label(container, text="0", width=3)
    value_label.pack(side='right')

    return value_label

right_val_label = create_slider_with_label("Move Right", right_val)
left_val_label = create_slider_with_label("Move Left", left_val)
up_val_label = create_slider_with_label("Move Up", up_val)
down_val_label = create_slider_with_label("Move Down", down_val)

right_val.trace_add('write', update_slider_labels)
left_val.trace_add('write', update_slider_labels)
up_val.trace_add('write', update_slider_labels)
down_val.trace_add('write', update_slider_labels)

mode_label = ttk.Label(controls_frame, text="Activation Mode:")
mode_label.pack(anchor='w', pady=(10, 0))

mode_combo = ttk.Combobox(controls_frame, textvariable=mode_var, state="readonly")
mode_combo['values'] = ("Left Click Only", "Left + Right Click")
mode_combo.pack(fill='x', pady=5)

button_frame = ttk.Frame(controls_frame)
button_frame.pack(pady=10)

save_button = ttk.Button(button_frame, text="Save Config", command=save_config)
save_button.pack(side='left', padx=10)

load_button = ttk.Button(button_frame, text="Load Config", command=load_config)
load_button.pack(side='left', padx=10)

canvas = tk.Canvas(main_frame, width=200, height=200, bg="white", relief="sunken", bd=2)
canvas.pack(side='right', padx=10, pady=10, fill='both', expand=False)

update_slider_labels()

root.mainloop()
