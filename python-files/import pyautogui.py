import pyautogui
import time
import keyboard

# Funkcja do wykrywania i zbierania yangu
def find_and_collect_yang():
    print("Program uruchomiony. Naciśnij 'q' aby zatrzymać.")
    print("Przesuń okno gry na ekran i upewnij się, że yang jest widoczny.")
    while True:
        # Zakładamy, że yang ma kolor żółty (RGB: 255, 255, 0), dostosuj wartości, jeśli potrzebne
        yang_color = (255, 255, 0)  # Żółty kolor (dostosuj RGB do swojego serwera)
        screen = pyautogui.screenshot()
        width, height = screen.size

        for x in range(0, width, 10):  # Przeglądaj ekran co 10 pikseli dla wydajności
            for y in range(0, height, 10):
                pixel_color = screen.getpixel((x, y))
                # Tolerancja 20 dla każdego kanału RGB, aby uwzględnić różnice w kolorze
                if (abs(pixel_color[0] - yang_color[0]) < 20 and 
                    abs(pixel_color[1] - yang_color[1]) < 20 and 
                    abs(pixel_color[2] - yang_color[2]) < 20):
                    print(f"Znaleziono yang na pozycji ({x}, {y})!")
                    pyautogui.moveTo(x, y, duration=0.5)  # Przesuń mysz
                    pyautogui.click()  # Kliknij, aby zebrać yang
                    time.sleep(0.5)  # Poczekaj, aby uniknąć zbyt szybkich ruchów
                    break
            else:
                continue
            break

        # Zatrzymaj program, jeśli naciśniesz 'q'
        if keyboard.is_pressed('q'):
            print("Zatrzymano program.")
            break

        time.sleep(1)  # Odświeżanie co 1 sekundę

# Uruchom program
if __name__ == "__main__":
    print("Naciśnij Enter, aby начать (upewnij się, że gra jest uruchomiona).")
    input()  # Czekaj na Enter, aby upewnić się, że gra jest gotowa
    find_and_collect_yang()