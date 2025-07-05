import pyautogui
import time
import keyboard

# ตำแหน่งคลิก
position1 = (863, 701)
position2 = (588, 600)

print("🔁 Auto clicker started. Press 'Esc' to stop.")

# วนลูปคลิก
while True:
    if keyboard.is_pressed('esc'):
        print("⛔ Stopped by user.")
        break

    # คลิกที่ตำแหน่งที่ 1
    pyautogui.click(position1)
    print(f"✅ Clicked at position1: {position1}")
    time.sleep(5)  # รอ 5 วินาที

    # คลิกที่ตำแหน่งที่ 2
    pyautogui.click(position2)
    print(f"✅ Clicked at position2: {position2}")
    time.sleep(5 * 60 + 5)  # รอ 5 นาที 5 วินาที
