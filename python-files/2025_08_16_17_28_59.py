import pydirectinput
import threading
import time
from pynput import keyboard

# Настройки
speeds = [0.5, 1, 2, 3, 4, 5, 6, 7, 8]  # 9 уровней скорости
current_speed_index = 4  # стартовый уровень
current_speed = 0  # текущая фактическая скорость
acceleration = 0.1  # скорость изменения текущей скорости

moving = False
stop_thread = False

# Функция плавного движения
def move_cursor():
    global current_speed
    while not stop_thread:
        target_speed = speeds[current_speed_index] if moving else 0

        # Плавное изменение текущей скорости к целевой
        if current_speed < target_speed:
            current_speed += acceleration
            if current_speed > target_speed:
                current_speed = target_speed
        elif current_speed > target_speed:
            current_speed -= acceleration
            if current_speed < target_speed:
                current_speed = target_speed

        # Двигаем мышь
        if current_speed != 0:
            pydirectinput.move(0, current_speed)

        time.sleep(0.01)

# Обработчик клавиш
def on_press(key):
    global current_speed_index
    try:
        if key == keyboard.Key.f4 and current_speed_index < len(speeds) - 1:
            current_speed_index += 1
        elif key == keyboard.Key.f3 and current_speed_index > 0:
            current_speed_index -= 1
    except AttributeError:
        pass

# Запуск слушателя клавиш и потока движения
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

threading.Thread(target=move_cursor, daemon=True).start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_thread = True
    keyboard_listener.stop()