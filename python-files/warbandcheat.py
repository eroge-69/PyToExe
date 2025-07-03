import keyboard
import time
import threading

is_running = False  # toggle durumu
stop_event = threading.Event()

def ctrl_x_loop():
    while not stop_event.is_set():
        keyboard.press('ctrl')
        keyboard.press('x')
        time.sleep(0.0005)
        keyboard.release('x')
        keyboard.release('ctrl')
        time.sleep(0.01)

def toggle():
    global is_running, stop_event
    if not is_running:
        print("Başladı")
        stop_event.clear()
        threading.Thread(target=ctrl_x_loop, daemon=True).start()
    else:
        print("Durduruldu")
        stop_event.set()
    is_running = not is_running

keyboard.add_hotkey('f2', toggle)

print("F2 ile başlat/durdur. Çıkmak için ESC'ye bas.")
keyboard.wait('esc')

