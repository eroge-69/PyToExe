import time
import os
import sys

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def loading_animation(text, delay=0.05):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def progress_bar(total=30, delay=0.05):
    for i in range(total + 1):
        bar = "█" * i + "-" * (total - i)
        percent = int((i / total) * 100)
        print(f"\r[{bar}] {percent}%", end="", flush=True)
        time.sleep(delay)
    print()

def main():
    clear()
    print("=== СНОСЕР Telegram ===")
    print()

    target = input("Введите User ID / @юзернейм / номер телефона: ")
    clear()
    print(f"[Система] Цель установлена: {target}")
    time.sleep(1)

    steps = [
        "Инициализация модулей...",
        "Подготовка пакета жалоб...",
        "Анализ профиля...",
        "Создание 100 автоматических жалоб...",
        "Подключение к узлам...",
        "Шифрование данных...",
        "Подтверждение отправки жалоб...",
        "Ожидание реакции системы...",
        "Подача дополнительных жалоб...",
        "Финализация процедуры..."
    ]

    for step in steps:
        loading_animation(f"[Задача] {step}", 0.03)
        progress_bar(30, 0.02)
        print()

    print("\n[Система] Процедура завершена.")
    print("✅ Готово! Аккаунта не будет примерно через 7 дней, но может задержаться.")

    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()