import sys

PASSWORD = "DMR crut"

def main():
    print("Программа заблокирована. Для выхода введите пароль.")
    
    while True:
        user_input = input("Пароль: ")
        if user_input == PASSWORD:
            print("Выход разрешён.")
            sys.exit(0)
        else:
            print("Неверный пароль! Попробуйте снова.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nЗакрытие через Ctrl+C запрещено! Введите пароль.")
        main()