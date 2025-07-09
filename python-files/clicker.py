import pyautogui
import time
import keyboard

print("Press F8 to start. Press ESC to stop.")

keyboard.wait('F8')
print("Started...")

try:
    while True:
        if keyboard.is_pressed('esc'):
            print("Stopped.")
            break

        pyautogui.click()
        print("First click.")
        time.sleep(3.5)

        if keyboard.is_pressed('esc'):
            print("Stopped.")
            break

        pyautogui.click()
        print("Second click.")
        time.sleep(0.5)
except:
    print("Exited.")
