import keyboard
import time
import os

# Переменные
start_key = 'o'       # клавиша для запуска режима
forcestop_key = 'p'   # клавиша для принудительной остановки
flight_mode_duration = 10  # время в секундах

# Имя сетевого интерфейса (замените на название вашего интерфейса)
interface_name = "Ethernet"  # или "Ethernet", или точное название вашего интерфейса

def enable_airplane_mode():
    print("Включение режима 'в самолёте' (отключение сети)...")
    # Отключение интерфейса
    command = f'netsh interface set interface "{interface_name}" disable'
    os.system(command)

def disable_airplane_mode():
    print("Выключение режима 'в самолёте' (включение сети)...")
    # Включение интерфейса
    command = f'netsh interface set interface "{interface_name}" enable'
    os.system(command)

def flight_mode():
    enable_airplane_mode()
    start_time = time.time()
    elapsed = 0
    while elapsed < flight_mode_duration:
        if keyboard.is_pressed(forcestop_key):
            print("Режим прерван принудительно.")
            break
        time.sleep(0.1)
        elapsed = time.time() - start_time
    else:
        print("Время режима истекло.")
    disable_airplane_mode()
    print("Режим завершён.\n")

print(f"Нажмите '{start_key}' для включения режима 'в самолёте' на {flight_mode_duration} секунд.")
print(f"Нажмите '{forcestop_key}' для принудительной остановки.\n")

while True:
    if keyboard.is_pressed(start_key):
        flight_mode()
        # чтобы избежать многократных срабатываний при удержании клавиши
        time.sleep(1)
    time.sleep(0.1)