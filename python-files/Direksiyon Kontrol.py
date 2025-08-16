from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key, Listener as KeyboardListener
import threading
import time

mouse = MouseController()
keyboard = KeyboardController()

# Ba�lang��ta devre d���
active = False
prev_x = mouse.position[0]

# Aktif/pasif ge�i� tu�u
TOGGLE_KEY = Key.f8

def toggle_listener():
    global active
    def on_press(key):
        global active
        if key == TOGGLE_KEY:
            active = not active
            print(f"Durum: {'AKT�F' if active else 'PAS�F'}")

    with KeyboardListener(on_press=on_press) as listener:
        listener.join()

def main_loop():
    global prev_x
    while True:
        if active:
            current_x = mouse.position[0]
            if current_x > prev_x:
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                print("� Sa� y�n tu�una bas�ld�")
            elif current_x < prev_x:
                keyboard.press(Key.left)
                keyboard.release(Key.left)
                print("� Sol y�n tu�una bas�ld�")
            prev_x = current_x
        time.sleep(0.05)  # Daha h�zl� tepki i�in gecikmeyi d���k tuttum

def start_program():
    # Komut istemcisi penceresinin a��k oldu�u d�ng�
    print("Program �al���yor... F8'e basarak a�/kapa yapabilirsin.")
    threading.Thread(target=toggle_listener, daemon=True).start()
    main_loop()

if __name__ == "__main__":
    start_program()
