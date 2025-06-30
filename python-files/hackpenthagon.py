import random
import string
import time
from datetime import timedelta

def generate_random_string(length=10):
    """Генерирует случайную строку из букв и цифр"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_nickname():
    """Генерирует случайный никнейм"""
    prefixes = ['User', 'Player', 'Agent', 'Hacker', 'Shadow', 'Ghost']
    suffixes = ['X', 'Pro', 'Master', 'Elite', str(random.randint(100, 999))]
    return random.choice(prefixes) + random.choice(suffixes) + str(random.randint(1000, 9999))

def countdown(minutes):
    """Функция для отсчёта времени"""
    total_seconds = minutes * 60
    start_time = time.time()
    while time.time() - start_time < total_seconds:
        password = generate_random_string(12)
        nickname = generate_nickname()
        print(f"({password}, {nickname})")
        time.sleep(0.1)  # Ускорить или замедлить вывод

def main():
    print("ARE YOU SURE YOU WANT TO HACK PENTAGON?")
    choice = input("Введите Y (да) или N (нет): ").strip().upper()

    if choice == 'N':
        print("Operation cancelled.")
        time.sleep(1)
        return
    elif choice != 'Y':
        print("Неверный ввод. Выход.")
        time.sleep(1)
        return

    print("\n[INFO] Начало операции...\n")
    print("[SYSTEM] Подключение к серверам Пентагона...")
    time.sleep(2)
    print("[SYSTEM] Брутфорс начат. Поиск уязвимостей...")
    time.sleep(1)

    try:
        countdown(15)  # 15 минут
    except KeyboardInterrupt:
        print("\n\n[ALERT] Операция прервана вручную!")
        return

    print("\n[SUCCESS] ПЕНТАГОН ВЗЛОМАН!")
    print("ДАННЫЕ ПОЛУЧЕНЫ:")
    print("(PELMEN1234865, SERYOGA765915DFTGBN)")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()