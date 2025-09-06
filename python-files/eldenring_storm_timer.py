import cv2
import pytesseract
import keyboard
import time
import threading
import tkinter as tk
import sys
import os

# --- SETTINGS ---
REGION = (100, 100, 400, 100)  # (x, y, w, h) - adjust to where the storm timer text is
CHECK_INTERVAL = 1.0  # seconds between OCR checks
STORM_DURATIONS = {"Day1": 300, "Day2": 420}  # seconds each storm lasts (customize)
ALERT_THRESHOLD = 30  # warn this many seconds before storm closes

# --- GLOBAL STATE ---
current_day = None
storm_end_time = None
running = True

# --- RESTART WITHOUT CONSOLE (WINDOWS ONLY) ---
if sys.platform == "win32" and sys.stdout is sys.__stdout__:
    # Relaunch script with pythonw.exe to hide console
    pythonw = os.path.join(sys.exec_prefix, 'pythonw.exe')
    os.spawnv(os.P_NOWAIT, pythonw, ['pythonw.exe'] + sys.argv)
    sys.exit()

# --- GUI ---
root = tk.Tk()
root.title("Nightreign Storm Timer")
root.geometry("300x150")
root.configure(bg="#1e1e1e")
root.wm_attributes("-transparentcolor", "#1e1e1e")  # make background transparent
root.attributes("-alpha", 0.85)  # translucent effect

status_label = tk.Label(root, text="No storm active", font=("Comic Sans MS", 14), fg="white", bg="#1e1e1e")
status_label.pack(pady=10)

countdown_label = tk.Label(root, text="--:--", font=("Comic Sans MS", 24, "bold"), fg="#00ff00", bg="#1e1e1e")
countdown_label.pack(pady=10)

# --- OCR FUNCTION ---
def get_storm_text():
    x, y, w, h = REGION
    screenshot = cv2.VideoCapture(0)  # replace with game capture method or screen grab
    ret, frame = screenshot.read()
    screenshot.release()
    if not ret:
        return None

    roi = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text.strip()

# --- TIMER THREAD ---
def storm_timer():
    global storm_end_time, current_day, running
    while running:
        if storm_end_time:
            remaining = storm_end_time - time.time()
            if remaining <= 0:
                storm_end_time = None
                current_day = None
                update_gui("Storm closed!", "00:00", "#ff0000")
            else:
                mins, secs = divmod(int(remaining), 60)
                time_str = f"{mins:02d}:{secs:02d}"
                color = "#ffcc00" if remaining <= ALERT_THRESHOLD else "#00ff00"
                update_gui(f"{current_day} active", time_str, color)
        else:
            update_gui("No storm active", "--:--", "#888888")
        time.sleep(1)

# --- UPDATE GUI ---
def update_gui(status, countdown, color):
    def _update():
        status_label.config(text=status)
        countdown_label.config(text=countdown, fg=color)
    root.after(0, _update)

# --- KEYBINDS ---
def keybinds():
    global current_day, storm_end_time, running

    while running:
        if keyboard.is_pressed("f1"):  # Start Day 1 storm
            current_day = "Day1"
            storm_end_time = time.time() + STORM_DURATIONS["Day1"]
            time.sleep(0.5)

        if keyboard.is_pressed("f2"):  # Start Day 2 storm
            current_day = "Day2"
            storm_end_time = time.time() + STORM_DURATIONS["Day2"]
            time.sleep(0.5)

        if keyboard.is_pressed("f3"):  # Reset
            storm_end_time = None
            current_day = None
            time.sleep(0.5)

        if keyboard.is_pressed("esc"):  # Exit
            running = False
            break

# --- MAIN ---
if __name__ == "__main__":
    threading.Thread(target=storm_timer, daemon=True).start()
    threading.Thread(target=keybinds, daemon=True).start()
    root.mainloop()
