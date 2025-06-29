import socket
import sys
import threading
import os
import subprocess
import time
import shlex

# Установка зависимостей: pip install paramiko
import paramiko

# --- Конфигурация Сервера ---
HOST = '127.0.0.1'  # Всегда используем локальный хост для туннеля
PORT = 2222         # Локальный порт для SSH
LOG_FILE = 'ssh_server.log' # Файл для логирования
HOST_KEY_FILE = 'test_rsa.key'

# --- Конфигурация Pinggy ---
# ВАЖНО: Вставьте сюда ваш Authtoken с сайта pinggy.io
# Получить его можно бесплатно после регистрации на https://pinggy.io/
PINGGY_AUTHTOKEN = "PASTE_YOUR_PINGGY_AUTHTOKEN_HERE"

# --- Учетные данные для входа (для демонстрации) ---
SSH_USER = 'user'
SSH_PASSWORD = 'password123'

# --- Проверка наличия Authtoken ---
if 'PASTE_YOUR_PINGGY_AUTHTOKEN_HERE' in PINGGY_AUTHTOKEN:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!! ВНИМАНИЕ: Пожалуйста, вставьте ваш Pinggy Authtoken     !!!")
    print("!!! в переменную PINGGY_AUTHTOKEN в строке 20.            !!!")
    print("!!! Получите токен на https://pinggy.io/                   !!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    sys.exit(1)


# --- Генерация ключа хоста (если не существует) ---
try:
    host_key = paramiko.RSAKey(filename=HOST_KEY_FILE)
except IOError:
    print(f'*** Ключ хоста ({HOST_KEY_FILE}) не найден, генерирую новый...')
    try:
        host_key = paramiko.RSAKey.generate(2048)
        host_key.write_private_key_file(HOST_KEY_FILE)
        print('*** Ключ сгенерирован.')
    except Exception as e:
        print(f'*** Ошибка при генерации ключа: {e}')
        sys.exit(1)

# --- Логирование ---
paramiko.util.log_to_file(LOG_FILE)


# --- Реализация интерфейса сервера Paramiko (без изменений) ---
class SSHServerHandler(paramiko.ServerInterface):
    def __init__(self, client_address):
        self.client_address = client_address
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        print(f"Попытка входа от {username} с адреса {self.client_address[0]}...")
        if (username == SSH_USER) and (password == SSH_PASSWORD):
            print("Аутентификация успешна!")
            return paramiko.AUTH_SUCCESSFUL
        print("Аутентификация не удалась.")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_exec_request(self, channel, command):
        command_str = command.decode('utf-8', 'ignore')
        print(f"Клиент ({self.client_address[0]}) выполняет команду: '{command_str}'")
        try:
            p = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout:
                channel.send(stdout)
            if stderr:
                channel.send_stderr(stderr)
            exit_code = p.wait()
            channel.send_exit_status(exit_code)
            print(f"Команда завершена с кодом {exit_code}")
        except Exception as e:
            error_msg = f"Ошибка выполнения команды: {e}\n".encode('utf-8')
            channel.send_stderr(error_msg)
            channel.send_exit_status(1)
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

# --- Функция для запуска туннеля Pinggy ---
def start_pinggy_tunnel():
    """Запускает pinggy в отдельном потоке и выводит публичный URL."""
    def run_pinggy():
        global pinggy_process
        print("\n*** Запускаю туннель Pinggy...")
        command = f'pinggy tcp -p {PORT} --token {PINGGY_AUTHTOKEN}'
        
        # Используем shlex.split для корректной обработки команды в разных ОС
        pinggy_process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')

        for line in iter(pinggy_process.stdout.readline, ''):
            print(f"[Pinggy]: {line.strip()}")
            if "Tunnel established at" in line:
                # Извлекаем URL из строки
                try:
                    url = line.split("at:")[1].strip()
                    print("\n" + "="*50)
                    print(" " * 10 + "🎉 ТУННЕЛЬ УСПЕШНО СОЗДАН! 🎉")
                    print(f"Для подключения к вашему SSH-серверу извне, используйте:")
                    print(f"ssh {SSH_USER}@{url.replace('tcp://', '')}")
                    print(f"Пароль: {SSH_PASSWORD}")
                    print("="*50 + "\n")
                except IndexError:
                    pass # На случай, если формат вывода изменится

    # Запускаем pinggy в фоновом потоке, чтобы не блокировать основной сервер
    pinggy_thread = threading.Thread(target=run_pinggy, daemon=True)
    pinggy_thread.start()


# --- Основной код запуска сервера ---
def run_server():
    global pinggy_process
    pinggy_process = None
    
    # Запускаем туннель
    start_pinggy_tunnel()
    time.sleep(5) # Даем Pinggy время на запуск и вывод URL

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(100)
        print(f'*** Локальный SSH-сервер запущен на {HOST}:{PORT}...')
        print(f"*** Используйте логин '{SSH_USER}' и пароль '{SSH_PASSWORD}' для входа.")
        print('*** Для остановки сервера нажмите Ctrl+C')
    except Exception as e:
        print(f'*** Ошибка бинда сокета: {e}')
        if pinggy_process:
            pinggy_process.terminate()
        sys.exit(1)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f'\n*** Получено входящее соединение от {client_address[0]}:{client_address[1]}')
            
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(host_key)
            
            server_handler = SSHServerHandler(client_address)
            transport.start_server(server=server_handler)

            channel = transport.accept(20)
            if channel is None:
                print('*** Клиент не запросил канал. Закрываю соединение.')
                transport.close()
                continue
            
            print('*** Аутентифицированный канал открыт.')
            server_handler.event.wait(10)

            if channel.active:
                channel.close()
            transport.close()
            print(f'*** Соединение с {client_address[0]} закрыто.')

    except KeyboardInterrupt:
        print('\n*** Получен сигнал остановки. Завершаю работу...')
    finally:
        if pinggy_process:
            print("*** Останавливаю туннель Pinggy...")
            pinggy_process.terminate()
            pinggy_process.wait()
        server_socket.close()
        print('*** Сервер остановлен.')


if __name__ == '__main__':
    run_server()
