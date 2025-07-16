import time
import os
import sys

VALID_KEY = "XPLODE-LOADER-KEY-777"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_and_print(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def main():
    clear()
    print("🔐 Введите ключ для доступа:")
    user_key = input(">> ").strip()

    if user_key != VALID_KEY:
        print("❌ Неверный ключ! Программа завершена.")
        time.sleep(2)
        sys.exit()

    while True:
        clear()
        print("✅ Доступ разрешен.\n")
        print("Выберите опцию:")
        print("1. Запустить Чит")
        print("2. Версия игры")
        print("0. Выход")
        choice = input(">> ")

        if choice == "1":
            clear()
            wait_and_print("Загрузка чита...", 0.1)
            time.sleep(2)
            print("\n❌ error: у вас нет dll для Чита, скачайте его в телеграмм канале:")
            print("🔗 https://t.me/xplodecheat")
            input("\nНажмите Enter для возврата в меню...")
        elif choice == "2":
            print("\n🎮 Версия игры: 0.34.0")
            input("\nНажмите Enter для возврата в меню...")
        elif choice == "0":
            print("👋 До свидания!")
            time.sleep(1)
            break
        else:
            print("❗ Неверный выбор. Попробуйте снова.")
            time.sleep(1)

if __name__ == "__main__":
    main()