import psutil
import subprocess
import random
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
import pydirectinput
import pyautogui
from pynput.keyboard import Controller, Key, Listener
from PIL import Image
import webbrowser  # <-- added for clickable link

keyboard = Controller()
stop_afk = False
paused = True
ui_running = False
log_output = None
status_label = None

try:
    img = Image.open("bo6_lobby_logo.png")
    pixel_color = img.getpixel((16, 13))
    print(pixel_color)
except Exception as e:
    print(f"Image load error: {e}")

def is_in_lobby():
    try:
        location = pyautogui.locateOnScreen('bo6_lobby_logo.png', confidence=0.98)
        if location:
            print(f"Found logo at {location}")
            return True
        else:
            print("Logo not found")
            return False
    except Exception as e:
        print(f"Error during lobby detection: {e}")
        return False

def monitor_game():
    while not stop_afk:
        if is_in_lobby():
            log("Detected lobby screen - skipping input.")
            time.sleep(2.5)
            continue
        if not is_game_running():
            launch_cod_via_steam()
            time.sleep(40)
        time.sleep(15)

def log(msg):
    print(msg)
    if log_output:
        log_output.after(0, lambda: (
            log_output.insert(tk.END, f"{msg}\n"),
            log_output.see(tk.END)
        ))

def update_status(text):
    if status_label:
        status_label.config(text=f"Status: {text}")

def on_press(key):
    global paused
    if key == Key.shift_r:
        paused = not paused
        update_status("Paused" if paused else "Running")
        log("Script paused." if paused else "Script resumed.")

def smooth_move_mouse(target_x, target_y, steps=100, delay=0.010):
    current_x, current_y = pyautogui.position()
    step_x = (target_x - current_x) / steps
    step_y = (target_y - current_y) / steps

    for _ in range(steps):
        if stop_afk or paused:
            break
        current_x += step_x
        current_y += step_y
        pydirectinput.moveTo(int(current_x), int(current_y))
        time.sleep(delay)

def rotate_mouse():
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    radius = min(screen_width, screen_height) // 4

    while not stop_afk:
        if is_in_lobby():
            log("Detected lobby screen - skipping input.")
            time.sleep(11)
            continue
        if paused:
            time.sleep(3)
            continue
        direction = random.choice(['positive', 'negative'])
        target_x = center_x + radius * (1 + 0.5 * random.random()) if direction == 'positive' else center_x - radius * (1 + 0.5 * random.random())
        target_y = center_y
        smooth_move_mouse(target_x, target_y)
        time.sleep(0.01)

def perform_sequence():
    while not stop_afk:
        if is_in_lobby():
            log("Detected lobby screen - skipping input.")
            time.sleep(11)
            continue
        if paused:
            time.sleep(3)
            continue
        actions = [
            ('w', random.uniform(0.5, 1.5)),
            ('d', random.uniform(0.5, 1.5)),
            ('q', random.uniform(0.1, 0.3)),
            ('s', random.uniform(0.5, 1.5)),
            ('a', random.uniform(0.5, 1.5)),
            ('space', random.uniform(0.1, 0.3)),
            ('e', random.uniform(0.1, 0.3)),
            ('ctrl', random.uniform(0.1, 0.3)),
            ('v', random.uniform(0.1, 0.3)),
            ('right', random.uniform(0.5, 1)),
            ('ctrl', random.uniform(0.1, 0.3)),
            ('left', random.uniform(0.3, 0.8)),
            ('r', random.uniform(0.1, 0.3)),
        ]
        for key, duration in actions:
            if stop_afk or paused:
                break
            log(f"Pressing: {key} for {duration:.2f}s")
            if key == 'right':
                pydirectinput.mouseDown(button='right')
                time.sleep(duration)
                pydirectinput.mouseUp(button='right')
            elif key == 'left':
                pydirectinput.mouseDown(button='left')
                time.sleep(duration)
                pydirectinput.mouseUp(button='left')
            else:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
            log(f"Released: {key}")
            time.sleep(random.uniform(0.5, 1.3))

def type_message_in_chat():
    global paused
    messages = [
        "hi", "came here", "unlocky bro", "i have 100.000 cash", "you have uav", "okey", "yes", "yes yes!",
        "what's up?", "anyone here?", "let's go!", "nice game", "good luck", "well played", "gg", "brb",
        "afk for a bit", "back now", "discord.gg/pshop", "teamwork!", "focus up", "let's push", "defend!",
        "attack now", "need help", "on my way", "wait for me", "let's regroup", "nice shot!", "great job",
        "thanks!", "no problem", "sorry!", "my bad", "let's try again", "next round", "we got this",
        "keep it up", "don't give up", "almost there", "victory!", "defeat...", "next time", "good game",
        "well played everyone", "let's do better", "practice makes perfect", "see you next time", "bye!"
    ]
    last_message = None
    while not stop_afk:
        if is_in_lobby():
            log("Detected lobby screen - skipping input.")
            time.sleep(11)
            continue
        if paused:
            time.sleep(3)
            continue
        available_messages = [msg for msg in messages if msg != last_message]
        if not available_messages:
            available_messages = messages
        message = random.choice(available_messages)
        last_message = message
        paused = True
        time.sleep(3)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(2)
        keyboard.type(message)
        time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        log(f"Typed in chat: {message}")
        time.sleep(3)
        paused = False
        time.sleep(random.uniform(30, 60))

def start_afk_actions():
    threading.Thread(target=monitor_game, daemon=True).start()
    global stop_afk, paused, ui_running
    if ui_running:
        return
    ui_running = True
    stop_afk = False
    paused = False
    threading.Thread(target=perform_sequence, daemon=True).start()
    threading.Thread(target=rotate_mouse, daemon=True).start()
    threading.Thread(target=type_message_in_chat, daemon=True).start()
    update_status("Running")
    log("AFK actions started. Press Right Shift to pause or resume.")

def stop_afk_actions():
    global stop_afk, ui_running
    stop_afk = True
    ui_running = False
    update_status("Stopped")
    log("AFK actions stopped.")

def toggle_pause():
    global paused
    paused = not paused
    update_status("Paused" if paused else "Running")
    log("Paused script" if paused else "Resumed script")

def is_game_running(process_name="cod.exe"):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

def click_safe_mode_no_blocking(x=1028, y=642, delay=5):
    log(f"Waiting {delay}s before clicking 'No' on Safe Mode prompt...")
    time.sleep(delay)
    log(f"Clicking 'No' on Safe Mode prompt at ({x}, {y})")
    pydirectinput.moveTo(x, y)
    time.sleep(0.2)
    pydirectinput.click()
    time.sleep(0.5)

def launch_cod_via_steam(app_id="1938090"):
    global paused
    try:
        paused = True
        subprocess.Popen(["cmd", "/c", f"start steam://rungameid/{app_id}"])
        log("Game was not running. Relaunching via Steam and handling Safe Mode prompt...")
        click_thread = threading.Thread(target=click_safe_mode_no_blocking, daemon=True)
        click_thread.start()
        click_thread.join()
        paused = False
    except Exception as e:
        log(f"Failed to launch the game: {e}")

def run_ui():
    global log_output, status_label
    root = tk.Tk()
    root.title("Purge's AFK Tool")
    root.geometry("520x450")
    root.configure(bg="#111")

    canvas = tk.Canvas(root, width=520, height=450, highlightthickness=0, bg="#111")
    canvas.place(x=0, y=0)

    circle_colors = ["#00ffff", "#ff0055", "#00ff88"]
    circle_positions = [(100, 100), (300, 150), (200, 300)]

    def draw_background():
        canvas.delete("grid", "line", "circle")

        for x in range(0, 520, 40):
            canvas.create_line(x, 0, x, 450, fill="#222", tags="grid")
        for y in range(0, 450, 40):
            canvas.create_line(0, y, 520, y, fill="#222", tags="grid")

        for i in range(0, 450, 40):
            x_offset = (time.time() * 50) % 40
            canvas.create_line(0, i + x_offset, 520, i + x_offset, fill="#0ff", width=1, tags="line")
        for i in range(0, 520, 40):
            y_offset = (time.time() * 40) % 40
            canvas.create_line(i + y_offset, 0, i + y_offset, 450, fill="#f00", width=1, tags="line")

        tick = (time.time() * 1000) % 1000 / 1000
        radius = 8 + (5 * abs((tick * 2) - 1))
        for i, (cx, cy) in enumerate(circle_positions):
            canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                               outline=circle_colors[i % len(circle_colors)],
                               width=2, tags="circle")

        root.after(50, draw_background)

    draw_background()

    title = tk.Label(root, text="Purge's AFK Tool", fg="red", bg="#111", font=("Segoe UI", 16, "bold"))
    title.place(x=160, y=15)

    status_label = tk.Label(root, text="Status: Idle", fg="white", bg="#111", font=("Segoe UI", 12))
    status_label.place(x=200, y=55)

    tk.Button(root, text="▶️ Start", width=20, command=start_afk_actions, bg="red", fg="white").place(x=150, y=90)
    tk.Button(root, text="⏸ Pause/Resume", width=20, command=toggle_pause, bg="#900", fg="white").place(x=150, y=130)
    tk.Button(root, text="🛑 Stop", width=20, command=stop_afk_actions, bg="black", fg="red").place(x=150, y=170)

    log_output = scrolledtext.ScrolledText(root, height=10, width=60, bg="black", fg="lime", font=("Consolas", 9))
    log_output.place(x=20, y=220)

    def open_discord(event=None):
        webbrowser.open("https://discord.gg/pshop")

    support = tk.Label(root, text="discord.gg/pshop", fg="cyan", bg="#111", font=("Segoe UI", 9, "italic"), cursor="hand2")
    support.place(x=400, y=420)
    support.bind("<Button-1>", open_discord)

    root.mainloop()

listener = Listener(on_press=on_press)
threading.Thread(target=run_ui).start()
listener.start()
