import random
import time
import os

# Цвета ANSI для "гинеанстикми" букв (яркие неоновые)
NEON_COLORS = ["\033[95m", "\033[96m", "\033[92m", "\033[93m", "\033[91m"]
RESET = "\033[0m"

banner = """\n"""
for c in "FINDER":
    color = random.choice(NEON_COLORS)
    banner += f"{color}{c}{RESET}"
banner += "\n"

menu = """
1) Поиск виртуалок
2) Поиск СНГ юзеров
3) Выход
"""

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_virtual_numbers():
    print("\nПоиск виртуальных номеров Telegram...")
    for i in range(10):
        num = "+7{}{}{}{}{}{}{}{}{}".format(*[random.randint(0, 9) for _ in range(9)])
        registered = random.choice(["Зарегистрирован", "Не зарегистрирован"])
        print(f"Найден: {num} | {registered}")
        time.sleep(0.3)
    print("\nПоиск завершён.")

def find_sng_users():
    print("\nПоиск СНГ юзеров Telegram...")
    sng_usernames = [
        "@vadim_228", "@olya_kisa", "@maks_kiev", "@sasha_minsk", "@katya_msk", "@pasha_kz",
        "@andrey_kg", "@inna_khv", "@dima_don", "@lena_kharkiv"
    ]
    found = random.sample(sng_usernames, k=random.randint(3, 7))
    for user in found:
        print(f"Найден пользователь: {user}")
        time.sleep(0.3)
    print("\nПоиск завершён.")

def main():
    while True:
        clear()
        print(banner)
        print(menu)
        choice = input("Выберите опцию: ")

        if choice == "1":
            find_virtual_numbers()
        elif choice == "2":
            find_sng_users()
        elif choice == "3":
            print("Выход...")
            break
        else:
            print("Некорректный ввод, попробуйте снова.")

        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()