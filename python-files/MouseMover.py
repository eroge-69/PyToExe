import pyautogui
import time

# Calcola il movimento in pixel (1 cm ≈ 37.8 pixel)
move_distance = 37.8  # 1 cm in pixel

while True:
    # Ottieni la posizione attuale del mouse
    current_x, current_y = pyautogui.position()
    
    # Muovi il mouse di 1 cm
    pyautogui.moveTo(current_x + move_distance, current_y)
    
    # Aspetta 5 secondi
    time.sleep(5)
    
    # Ripristina la posizione originale
    pyautogui.moveTo(current_x, current_y)
    
    # Aspetta 5 secondi
    time.sleep(5)

}
