import curses
import time
import signal
import sys
import socket
import datetime

class WinLocker:
    def __init__(self, password):
        self.locked = True  # По умолчанию "Винлокер" активирован
        self.password = password

    def unlock(self, input_password):
        if self.locked:
            if input_password == self.password:
                self.locked = False
                return True
            else:
                return False
        else:
            return True

# Перехват сигналов (Ctrl+C, Ctrl+Z и т.д.)
def ignore_signals(signum, frame):
    pass

# Функция для записи IP-адреса в лог-файл
def log_ip(ip):
    with open("ip_log.txt", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {ip}\n")

# Получение IP-адреса пользователя
def get_user_ip():
    try:
        # Получаем имя хоста
        hostname = socket.gethostname()
        # Получаем IP-адрес
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return "Unknown IP"

# Основное меню
def main_menu(stdscr):
    password = "1488"  # Пароль
    winlocker = WinLocker(password)

    # Настройка curses
    curses.curs_set(0)  # Скрываем курсор
    stdscr.nodelay(0)   # Ожидание ввода пользователя
    stdscr.keypad(True) # Включение обработки специальных клавиш
    stdscr.clear()
    stdscr.refresh()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()  # Получаем размеры терминала

        # Отображаем заголовок
        title = "=== Меню Винлокера ==="
        stdscr.addstr(height // 2 - 3, (width - len(title)) // 2, title)

        # Отображаем инструкцию
        instruction = "Введите пароль для разблокировки:"
        stdscr.addstr(height // 2 - 1, (width - len(instruction)) // 2, instruction)

        # Поле для ввода пароля
        curses.echo()
        stdscr.addstr(height // 2 + 1, (width - 20) // 2, " " * 20)
        stdscr.move(height // 2 + 1, (width - 20) // 2)
        password_input = stdscr.getstr(height // 2 + 1, (width - 20) // 2, 20).decode("utf-8")
        curses.noecho()

        # Логируем IP-адрес пользователя
        user_ip = get_user_ip()
        log_ip(user_ip)

        # Проверка пароля
        if winlocker.unlock(password_input):
            stdscr.clear()
            stdscr.addstr(height // 2, (width - 30) // 2, "🔓 Винлокер деактивирован! Система разблокирована.")
            stdscr.refresh()
            time.sleep(2)
            break
        else:
            stdscr.clear()
            stdscr.addstr(height // 2, (width - 30) // 2, "❌ Неверный пароль! Винлокер остается активным.")
            stdscr.refresh()
            time.sleep(2)

# Запуск программы
if __name__ == "__main__":
    # Блокируем сигналы
    signal.signal(signal.SIGINT, ignore_signals)  # Ctrl+C
    signal.signal(signal.SIGTSTP, ignore_signals)  # Ctrl+Z
    signal.signal(signal.SIGTERM, ignore_signals)  # Сигнал завершения

    # Запуск основного меню
    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass

