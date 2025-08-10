import time
import threading
from pynput import mouse, keyboard

running = False  # Флаг работы спамера

mouse_controller = mouse.Controller()

def click_spammer():
    global running
    while running:
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.01)  # 10 мс

def on_press(key):
    global running
    try:
        if key == keyboard.Key.f6:  # Запуск спама
            if not running:
                running = True
                threading.Thread(target=click_spammer, daemon=True).start()
                print("Спамер запущен")
        elif key == keyboard.Key.f7:  # Остановка спама
            running = False
            print("Спамер остановлен")
    except:
        pass

print("F6 - старт, F7 - стоп (без выхода)")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
