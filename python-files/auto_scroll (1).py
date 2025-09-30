# auto_scroll.py
# גלילה למעלה ולמטה בלי הפסקה - התחלה F8, עצירה F6, יציאה ESC
# מהירות גבוהה מאוד

import threading
import time
from pynput.mouse import Controller
import keyboard

mouse = Controller()

# הגדרות
SCROLL_AMOUNT = 1      # גודל גלילה. 1 = מעלה, -1 = מטה (נשנה תוך כדי)
INTERVAL = 0.01       # מהירות גבוהה מאוד (כמה שיותר קטן = יותר מהיר)

_running = threading.Event()
_thread = None

def scroll_loop():
    direction = 1
    while _running.is_set():
        mouse.scroll(0, direction)
        direction *= -1  # מחליף בין למעלה ולמטה כל פעם
        time.sleep(INTERVAL)

def start_scrolling():
    global _thread
    if _running.is_set():
        print("Already running")
        return
    _running.set()
    _thread = threading.Thread(target=scroll_loop, daemon=True)
    _thread.start()
    print("Scrolling started (F6 to stop)")

def stop_scrolling():
    if not _running.is_set():
        print("Not running")
        return
    _running.clear()
    print("Scrolling stopped")

def main():
    print("Press F8 to START, F6 to STOP, ESC to exit.")
    keyboard.on_press_key("f8", lambda _: start_scrolling())
    keyboard.on_press_key("f6", lambda _: stop_scrolling())
    keyboard.wait("esc")
    stop_scrolling()
    print("Exiting...")

if __name__ == "__main__":
    main()
