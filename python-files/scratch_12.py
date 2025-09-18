import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import keyboard  # global hotkeys (may require admin on Windows)

# ---------------- SETTINGS ----------------
VALUE_1_LIST = ["654","652","659","664","661","656","659","665","671","675","675","675","672","666","662","659","650","649","647","653","657","660","656","663","668","667","663","660","654","648","643","641","645","641","644","648","655","660","665","669","680","680","682","677","673","679","676","682","672","668","660","655","647","643","640","642"]
VALUE_2_LIST = ["620","624","620","619","624","625","628","626","626","622","622","617","614","612","611","614","616","628","633","635","636","633","631","630","617","607","604","607","607","609","615","620","624","625","628","637","640","640","638","631","625","620","615","613","610","607","603","604","604","603","601","601","602","604","607","611"]

# ---------------- STATE ----------------
round_counter = 0
start_time = None
running = False
paused = False
coords_list = []

# ---------------- HELPERS ----------------
def human_delay(base):
    return max(0, base + random.uniform(-0.03, 0.03))

def smart_sleep(seconds):
    global running, paused
    end = time.time() + seconds
    while time.time() < end:
        if not running:
            return
        while paused and running:
            time.sleep(0.05)
        time.sleep(0.02)

def double_click_with_delay(delay):
    pyautogui.click()
    smart_sleep(human_delay(delay))
    pyautogui.click()

def move_mouse(x, y, speed):
    pyautogui.moveTo(x, y, duration=human_delay(speed))

# ---------------- FINAL GENERATOR FUNCTION ----------------
def generate_all_towers_sorted(nearest_per_castle=10, step=39):
    relative_offsets = [(dx * step, dy * step) for dx in range(-15,16) for dy in range(-15,16)]
    all_towers = []

    # Generate towers around each castle
    for x_str, y_str in zip(VALUE_1_LIST, VALUE_2_LIST):
        cx, cy = int(x_str), int(y_str)
        towers = [(cx + dx, cy + dy) for dx, dy in relative_offsets]
        # take nearest_per_castle towers per castle
        towers_sorted = sorted(towers, key=lambda p: math.dist((cx, cy), p))[:nearest_per_castle]
        all_towers.extend(towers_sorted)

    # Remove duplicates
    all_towers = list(set(all_towers))

    # Sort all towers by distance to the nearest castle
    all_towers_sorted = sorted(
        all_towers,
        key=lambda t: min(math.dist((int(cx), int(cy)), t) for cx, cy in zip(map(int, VALUE_1_LIST), map(int, VALUE_2_LIST)))
    )
    return all_towers_sorted

# ---------------- BOT LOGIC ----------------
def scan_towers():
    global coords_list
    try:
        max_rounds = max_attacks_var.get()
        nearest_per_castle = max_rounds // len(VALUE_1_LIST)  # distribute attacks per castle
        nearest_per_castle = max(1, nearest_per_castle)

        coords_list = generate_all_towers_sorted(nearest_per_castle=nearest_per_castle, step=39)

        status_var.set(f"Scan complete: {len(coords_list)} coords ready.")
        messagebox.showinfo("Scan Complete", f"Found {len(coords_list)} coordinates.\nClosest first.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_macro():
    global round_counter, start_time, running, paused, coords_list
    if not coords_list:
        messagebox.showwarning("Scan first", "No towers scanned yet. Click ‘Scan’ before Start.")
        return

    try:
        mouse_speed = mouse_speed_var.get() / 1000.0
        click_delay = click_delay_var.get() / 1000.0
        typing_speed = typing_speed_var.get() / 1000.0

        smart_sleep(human_delay(2.0))
        start_time = time.time()
        running = True
        paused = False
        round_counter = 0
        update_timer()
        status_var.set("Attacking...")

        for (x_val, y_val) in coords_list:
            if not running:
                break
            val1, val2 = str(x_val), str(y_val)

            # X coordinate
            move_mouse(825, 105, mouse_speed)
            double_click_with_delay(click_delay)
            smart_sleep(human_delay(0.25))
            pyautogui.typewrite(val1, interval=human_delay(typing_speed))

            # Y coordinate
            move_mouse(875, 105, mouse_speed)
            double_click_with_delay(click_delay)
            smart_sleep(human_delay(0.25))
            pyautogui.typewrite(val2, interval=human_delay(typing_speed))

            # Click sequence (unchanged)
            move_mouse(930, 115, mouse_speed);  double_click_with_delay(click_delay); smart_sleep(human_delay(0.15))
            move_mouse(930, 115, mouse_speed);  double_click_with_delay(click_delay); smart_sleep(human_delay(0.15))
            move_mouse(1070, 580, mouse_speed); pyautogui.click(); smart_sleep(human_delay(0.10))
            move_mouse(1070, 705, mouse_speed); pyautogui.click(); smart_sleep(human_delay(0.10))
            move_mouse(1400, 730, mouse_speed); double_click_with_delay(click_delay); smart_sleep(human_delay(0.90))
            move_mouse(1334, 962, mouse_speed); pyautogui.click(); smart_sleep(human_delay(1.50))
            move_mouse(1205, 570, mouse_speed); pyautogui.click(); smart_sleep(human_delay(0.80))
            move_mouse(1115, 815, mouse_speed); pyautogui.click(); smart_sleep(human_delay(0.25))
            move_mouse(1250, 815, mouse_speed); pyautogui.click(); smart_sleep(human_delay(0.25))
            move_mouse(950, 785, mouse_speed);  pyautogui.click(); smart_sleep(human_delay(0.40))
            move_mouse(950, 720, mouse_speed);  pyautogui.click(); smart_sleep(human_delay(0.25))


            round_counter += 1
            counter_var.set(f"Rounds: {round_counter}")

        running = False
        total_time = round(time.time() - start_time, 2)
        status_var.set("Done.")
        messagebox.showinfo("Done", f"Macro finished.\nTime taken: {total_time} sec")

    except Exception as e:
        running = False
        status_var.set("Error.")
        messagebox.showerror("Error", str(e))

def start_macro():
    if running:
        return
    threading.Thread(target=run_macro, daemon=True).start()

def stop_macro():
    global running
    running = False
    status_var.set("Stopped.")

def toggle_pause():
    global paused
    if not running:
        return
    paused = not paused
    pause_btn.config(text="▶ Resume" if paused else "⏸ Pause")
    status_var.set("Paused." if paused else "Attacking...")

def update_timer():
    if running and start_time:
        elapsed = int(time.time() - start_time)
        m, s = divmod(elapsed, 60)
        timer_var.set(f"{m:02}:{s:02}")
        root.after(1000, update_timer)

# ---------------- UI ----------------
root = tk.Tk()
root.title("Goodgame Empire Bot")
root.geometry("650x400")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11), padding=8)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
style.configure("Badge.TLabel", relief="groove", padding=4)

container = ttk.Frame(root, padding=14)
container.pack(fill="both", expand=True)

# Title & status
ttk.Label(container, text="Goodgame Empire Bot", style="Title.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
timer_var = tk.StringVar(value="00:00")
counter_var = tk.StringVar(value="Rounds: 0")
status_var = tk.StringVar(value="Ready")

ttk.Label(container, text="⏱", width=3).grid(row=0, column=4, sticky="e")
ttk.Label(container, textvariable=timer_var, style="Badge.TLabel", width=8).grid(row=0, column=5, sticky="e")
ttk.Label(container, textvariable=counter_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
ttk.Label(container, textvariable=status_var, foreground="green").grid(row=1, column=2, columnspan=4, sticky="e", pady=(6, 0))

# Slider helper
def add_slider(row, label, var, from_, to_, step, unit_label, width=280, fmt=lambda v: str(int(v))):
    ttk.Label(container, text=label).grid(row=row, column=0, sticky="w", pady=6)
    scale = ttk.Scale(container, from_=from_, to=to_, orient="horizontal", variable=var)
    scale.grid(row=row, column=1, columnspan=3, sticky="ew", padx=8)
    container.grid_columnconfigure(3, minsize=width)
    badge = ttk.Label(container, style="Badge.TLabel", width=10)
    badge.grid(row=row, column=4, sticky="e", padx=4)
    unit = ttk.Label(container, text=unit_label)
    unit.grid(row=row, column=5, sticky="w")
    def on_move(_):
        badge.config(text=fmt(var.get()))
    scale.configure(length=width)
    scale.bind("<B1-Motion>", on_move)
    scale.bind("<ButtonRelease-1>", on_move)
    on_move(None)
    return scale

# Variables (sliders)
max_attacks_var = tk.IntVar(value=50)
grid_radius_var = tk.IntVar(value=15)
mouse_speed_var = tk.IntVar(value=400)   # ms
click_delay_var = tk.IntVar(value=150)   # ms
typing_speed_var = tk.IntVar(value=40)   # ms

# Sliders
add_slider(2, "Max Attacks", max_attacks_var, 1, 3500, 1, "attacks")
add_slider(3, "Mouse Speed", mouse_speed_var, 50, 1500, 10, "ms", fmt=lambda v: f"{int(v)} ms")
add_slider(4, "Click Delay", click_delay_var, 50, 600, 10, "ms", fmt=lambda v: f"{int(v)} ms")
add_slider(5, "Typing Speed", typing_speed_var, 5, 200, 5, "ms", fmt=lambda v: f"{int(v)} ms")

# Buttons
btns = ttk.Frame(container)
btns.grid(row=6, column=0, columnspan=6, pady=14, sticky="ew")
btns.grid_columnconfigure((0,1,2,3), weight=1)

scan_btn  = ttk.Button(btns, text="🔍 Scan", command=scan_towers)
start_btn = ttk.Button(btns, text="▶ Start", command=start_macro)
pause_btn = ttk.Button(btns, text="⏸ Pause", command=toggle_pause)
stop_btn  = ttk.Button(btns, text="⏹ Stop", command=stop_macro)

scan_btn.grid(row=0, column=0, padx=6, sticky="ew")
start_btn.grid(row=0, column=1, padx=6, sticky="ew")
pause_btn.grid(row=0, column=2, padx=6, sticky="ew")
stop_btn.grid(row=0, column=3, padx=6, sticky="ew")

# Footer
ttk.Separator(container).grid(row=7, column=0, columnspan=6, sticky="ew", pady=6)
ttk.Label(container, text="Hotkeys:  Pause/Resume = Ctrl+Alt+P   ·   Stop = Ctrl+Alt+S").grid(row=8, column=0, columnspan=6, sticky="w")

# Global hotkeys
keyboard.add_hotkey('ctrl+alt+p', toggle_pause)
keyboard.add_hotkey('ctrl+alt+s', stop_macro)

root.mainloop()
