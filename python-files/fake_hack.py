import time
import os
import msvcrt  # Для обработки нажатия клавиш в Windows

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def press_any_key():
    print("\n(Для того чтобы продолжить нажмите любую клавишу)")
    msvcrt.getch()  # Ожидание нажатия любой клавиши

def animated_progress_bar(duration_seconds):
    width = 20
    for i in range(width + 1):
        progress = i / width
        bar = '[' + '=' * i + ' ' * (width - i) + ']'
        percent = int(progress * 100)
        print(f"\r{bar} {percent}/100", end='', flush=True)
        time.sleep(duration_seconds / width)
    print()

def main():
    clear_screen()
    print('"Чего нового? (Build 1.04.4)"')
    print(' Новые функции')
    
    press_any_key()
    
    nickname = input("\nВведите ник: ")
    while True:
        try:
            amount = int(input("Введите сумму: "))
            break
        except ValueError:
            print("Пожалуйста, введите число!")
    
    print("\nПроцесс пошел! Ожидайте!")
    animated_progress_bar(60)  # 60 секунд анимация
    
    print("\n(Загрузка идет 1 минуту)")
    time.sleep(5)  # Уменьшил для демонстрации, можно поставить 60
    
    print(f"\nУспешно! Мы вывели вам {amount} игровой валюты на аккаунт {nickname}!")
    press_any_key()

if __name__ == "__main__":
    main()