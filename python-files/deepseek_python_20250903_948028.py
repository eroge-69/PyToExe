import pyautogui
import keyboard
import time
import threading

# Координаты для кликов с указанием кнопки мыши
points = [
    (1166, 285, 'right'),  # 1 - правая кнопка
    (1076, 280, 'right'),  # 2 - правая кнопка
    (799, 576, 'right'),   # 3 - правая кнопка
    (823, 669, 'left')     # 4 - левая кнопка (как вы requested)
]

# Флаги для управления скриптом
is_active = False
program_running = True

def click_sequence():
    global is_active
    while program_running:
        if is_active:
            print("Запуск последовательности кликов...")
            
            for i, (x, y, button) in enumerate(points, 1):
                if not is_active or not program_running:
                    break
                    
                pyautogui.moveTo(x, y)
                pyautogui.click(button=button)
                print(f"Клик {i} на координатах ({x}, {y}), кнопка: {button}")
                
                # Задержка между кликами с возможностью прерывания
                for _ in range(5):
                    if not is_active or not program_running:
                        break
                    time.sleep(0.1)
            
            if is_active and program_running:
                print("Ожидание 10 секунд до следующего цикла...")
                # Задержка 10 секунд с проверкой флагов каждые 0.1 секунды
                for _ in range(100):
                    if not is_active or not program_running:
                        break
                    time.sleep(0.1)
        else:
            time.sleep(0.1)

def toggle_activation():
    global is_active
    is_active = not is_active
    status = "активирован" if is_active else "деактивирован"
    print(f"Скрипт {status}")

def exit_script():
    global program_running, is_active
    print("Завершение работы скрипта...")
    is_active = False
    program_running = False
    # Даем время потоку завершиться
    time.sleep(0.5)
    print("Нажмите Enter чтобы закрыть окно...")

# Создаем и запускаем поток
thread = threading.Thread(target=click_sequence)
thread.daemon = True
thread.start()

# Регистрируем горячие клавиши
keyboard.add_hotkey('f4', toggle_activation)
keyboard.add_hotkey('esc', exit_script)

print("Скрипт запущен. Нажмите F4 для активации/деактивации. ESC для выхода.")

# Бесконечный цикл чтобы консоль не закрывалась
try:
    while program_running:
        time.sleep(0.1)
except KeyboardInterrupt:
    exit_script()

# Ожидание перед закрытием
if not program_running:
    input()  # Ожидание ввода перед закрытием консоли