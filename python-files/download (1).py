import socket
import os

def change_dns(new_dns_server):
    """
    Меняем DNS сервер в настройках системы (только для Windows)
    """
    current_ip = socket.gethostbyname(socket.gethostname())
    cmd = f"netsh interface ip set dns \"Ethernet\" static {new_dns_server}"
    result = os.system(cmd)
    if result == 0:
        print(f"ДНС сервер сменён на {new_dns_server}.")
    else:
        print("Ошибка изменения DNS сервера.")

def main():
    