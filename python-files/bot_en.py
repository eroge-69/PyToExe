import pyautogui
import time
import keyboard

button_image = "button.png"   # Screenshot of the button to search for
click_count = 1               # How many times to click each button
click_interval = 0.3          # Delay between clicks (seconds)

print("⏳ Prepare the page within 3 seconds...")
time.sleep(3)

print("🔍 Program started. Left Shift = pause/resume, ESC = exit")

running = True  # Initially running

while True:
    # ESC → exit
    if keyboard.is_pressed("esc"):
        print("🛑 Program terminated by user.")
        break

    # Shift → toggle start/stop
    if keyboard.is_pressed("shift"):
        running = not running
        state = "running" if running else "paused"
        print(f"⏸ Toggle: Clicking is now {state}.")
        time.sleep(0.5)  # wait to avoid key repetition

    if not running:
        time.sleep(0.2)
        continue

    matches = list(pyautogui.locateAllOnScreen(button_image, confidence=0.8))

    if not matches:
        print("❌ Button not found, try scrolling the page...")
        time.sleep(1)
        continue

    for match in matches:
        center = pyautogui.center(match)
        for c in range(click_count):
            pyautogui.click(center)
            print(f"✅ Clicked button at: {center} ({c+1}. click)")
            time.sleep(click_interval)
