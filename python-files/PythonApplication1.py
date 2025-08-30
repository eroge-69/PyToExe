
import pyautogui
import keyboard
import time
from datetime import datetime, timedelta

# Setări
interval_sec = 10
durata_totala = 2 * 60 * 60  # 2 ore în secunde
distanta_miscare = 50  # pixeli stânga/dreapta

# Timp de start și end
start_time = datetime.now()
end_time = start_time + timedelta(seconds=durata_totala)

# Poziția inițială
x_initial, y_initial = pyautogui.position()
direction = 1  # 1 = dreapta, -1 = stânga

print("Scriptul a inceput. Apasă ESC pentru a opri manual.")

while datetime.now() < end_time:
    if keyboard.is_pressed('esc'):
        print("Script oprit manual.")
        break

    # Calculează noua poziție
    x_new = x_initial + direction * distanta_miscare
    pyautogui.moveTo(x_new, y_initial, duration=0.5)
    #pyautogui.click()
    
    # Schimbă direcția pentru următoarea mișcare
    direction *= -1

    time.sleep(interval_sec)

print("Scriptul s-a incheiat.")