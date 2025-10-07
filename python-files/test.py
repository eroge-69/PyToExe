import os
import socket
import datetime
import getpass

def get_user_info():
    """Собирает информацию о пользователе, его IP и имени хоста."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "username": username,
        "hostname": hostname,
        "ip_address": ip_address
    }

def create_log_file():
    """Создает лог-файл с именем, соответствующим текущей дате."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_filename = f"user_login_{today}.log"

    # Проверяем, существует ли файл, если нет - создаем
    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as f:
            f.write("Timestamp, Username, Hostname, IP Address\n")

    return log_filename

def log_user_info():
    """Записывает информацию о пользователе в лог-файл."""
    user_info = get_user_info()
    log_filename = create_log_file()

    with open(log_filename, 'a') as f:
        log_entry = f"{user_info['timestamp']}, {user_info['username']}, {user_info['hostname']}, {user_info['ip_address']}\n"
        f.write(log_entry)

if __name__ == "__main__":
    log_user_info()
    print("Информация о пользователе успешно записана в лог.")