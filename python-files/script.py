import random
import time
import threading
import keyboard

running = True  # Флаг работы скрипта

# Список
keys = ['w', 'a', 's', 'd']

def random_key_press_sequence():
    sequence = random.sample(keys, len(keys))  # случайный порядок
    for key in sequence:
        if not running:
            break
        delay = round(random.uniform(0.3, 1.2), 2)
        print(f"Нажатие: {key.upper()} | Задержка: {delay} секунд")
        keyboard.press(key)
        time.sleep(0.1)
        keyboard.release(key)
        time.sleep(delay)

def auto_loop():
    global running
    print("Скрипт запущен. Ожидание 15 минут перед первым действием.")
    while running:
        for _ in range(900):  # 15 минут = 900 секунд
            if not running:
                break
            time.sleep(1)
        if running:
            print("\n--- Выполнение случайной последовательности ---")
            random_key_press_sequence()
            print("--- Завершено. Ожидание следующего цикла ---")

def stop_listener():
    global running
    keyboard.wait('backspace')
    running = False
    print("\n[!] Скрипт остановлен пользователем.")

# Отслежка клавииши остановки/запуска
listener_thread = threading.Thread(target=stop_listener, daemon=True)
listener_thread.start()

# Запуск всего цикла
auto_loop()
