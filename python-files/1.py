Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... import platform
... import time
... 
... def ping(host):
...     """
...     Пингует указанный хост и возвращает True, если пинг успешен, иначе False.
...     """
...     param = '-n 1' if platform.system().lower()=='windows' else '-c 1'
...     command = 'ping ' + param + ' ' + host
...     return os.system(command) == 0
... 
... def shutdown_computer(computer_name):
...     """
...     Выполняет команду shutdown на указанном компьютере.
...     """
...     command = f'shutdown /s /f /m \\\\{computer_name}'
...     os.system(command)
... 
... if __name__ == "__main__":
...     ip_address = "172.16.47.59"
...     computer_name = "77058-W40400059"
... 
...     while True:
...         if ping(ip_address):
...             print(f"Пинг до {ip_address} успешен.")
...         else:
...             print(f"Пинг до {ip_address} не успешен. Выполняется shutdown на {computer_name}.")
...             shutdown_computer(computer_name)
...             break # Завершаем скрипт после выполнения shutdown
... 
