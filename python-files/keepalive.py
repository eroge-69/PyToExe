
import pyautogui
import time

print("🟢 Mouse mover activo. Presioná Ctrl+C para detener.")

while True:
    current_x, current_y = pyautogui.position()
    pyautogui.moveTo(current_x + 5, current_y)
    pyautogui.moveTo(current_x, current_y)
    pyautogui.click()
    time.sleep(30)
