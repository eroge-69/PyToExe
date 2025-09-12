import os

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 30)
        print("     SnonLauncher")
        print("=" * 30)
        print("1. Запустить функцию 1")
        print("2. Запустить функцию 2")
        print("3. Показать информацию о системе")
        print("4. Выход")
        print("=" * 30)

        choice = input("Выберите пункт: ")

        if choice == '1':
            input("Функция 1 выполнена. Нажмите Enter для возврата в меню...")
        elif choice == '2':
            input("Функция 2 выполнена. Нажмите Enter для возврата в меню...")
        elif choice == '3':
            print(f"Имя ОС: {os.name}")
            input("Нажмите Enter для возврата в меню...")
        elif choice == '4':
            print("Завершение работы...")
            break
        else:
            input("Неверный ввод. Нажмите Enter для выбора снова...")

if __name__ == "__main__":
    main()