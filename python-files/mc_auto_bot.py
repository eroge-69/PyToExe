import keyboard
import pyautogui
import time
import sys
import threading

# Settings
toggle_key = '+'
delay_seconds = 10
click_interval = 0.75  # 15 ticks = 750ms
is_running = False
main_thread = None
click_thread = None
user_active = False
last_input_time = time.time()

# Monitor input (keyboard + mouse move)
def monitor_input():
    global user_active, last_input_time

    def on_key_event(e):
        global user_active, last_input_time
        user_active = True
        last_input_time = time.time()

    keyboard.hook(on_key_event)

    last_mouse_pos = pyautogui.position()
    while True:
        current_pos = pyautogui.position()
        if current_pos != last_mouse_pos:
            user_active = True
            last_input_time = time.time()
        elif time.time() - last_input_time >= 5:
            user_active = False

        last_mouse_pos = current_pos
        time.sleep(0.1)

def main_loop():
    while True:
        if is_running and not user_active:
            keyboard.press_and_release('t')
            time.sleep(0.3)
            keyboard.write('/sell blaze_rod')
            keyboard.press_and_release('enter')
            print("[✓] Sent '/sell blaze_rod'. Countdown:")
            for i in range(delay_seconds, 0, -1):
                if not is_running or user_active:
                    break
                sys.stdout.write(f"\r⏳ Next in: {i:2d} sec ")
                sys.stdout.flush()
                time.sleep(1)
            print()
        else:
            time.sleep(0.1)

def click_loop():
    while True:
        if is_running and not user_active:
            pyautogui.click(button='left')
        time.sleep(click_interval)

def toggle():
    global is_running, main_thread, click_thread
    is_running = not is_running
    if is_running:
        print("\n[+] Started Script")

        if main_thread is None or not main_thread.is_alive():
            main_thread = threading.Thread(target=main_loop, daemon=True)
            main_thread.start()

        if click_thread is None or not click_thread.is_alive():
            click_thread = threading.Thread(target=click_loop, daemon=True)
            click_thread.start()
    else:
        print("\n[⏸️] Stopped Script")

# Start toggle and monitor threads
keyboard.add_hotkey(toggle_key, toggle)
threading.Thread(target=monitor_input, daemon=True).start()

print("📜 Minecraft Auto Bot with Inactivity Detection")
print("- Press '+' to Start/Stop")
print("- Pauses if mouse or keyboard used")
print("- Resumes after 5 seconds of no input")

while True:
    time.sleep(0.1)
