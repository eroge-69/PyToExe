import os
import time
import platform
import subprocess
from configparser import ConfigParser

def ping(host):
    """Функция для выполнения ping"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        if "TTL=" in output or "ttl=" in output:
            # Извлекаем время из ответа
            time_ms = None
            for line in output.split('\n'):
                if 'time=' in line:
                    time_ms = line.split('time=')[1].split(' ')[0]
                    break
            return True, time_ms
    except subprocess.CalledProcessError:
        pass
    return False, None

def read_config():
    """Чтение конфигурационных файлов"""
    devices = []
    with open('1.cfg', 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    devices.append((parts[0], parts[1]))
    
    config = ConfigParser()
    config.read('3.ini')
    interval = int(config.get('DEFAULT', 'time', fallback=5))
    
    return devices, interval

def main():
    """Основная функция"""
    print("Network Ping Monitor (Python)")
    print("=============================")
    
    if not os.path.exists('1.cfg'):
        print("Ошибка: файл 1.cfg не найден!")
        time.sleep(5)
        return
    
    if not os.path.exists('3.ini'):
        print("Ошибка: файл 3.ini не найден!")
        time.sleep(5)
        return
    
    devices, interval = read_config()
    
    # Очистка файла результатов при первом запуске
    if not os.path.exists('2.txt'):
        with open('2.txt', 'w') as f:
            f.write("Ping Monitor Log\n")
            f.write("===============\n")
            f.write(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Polling interval: {interval} seconds\n\n")
    
    try:
        while True:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\nПроверка: {current_time}")
            print("IP адрес".ljust(16) + "Имя узла".ljust(20) + "Статус")
            print("-" * 50)
            
            with open('2.txt', 'a') as log_file:
                log_file.write(f"\nПроверка: {current_time}\n")
                
                for ip, name in devices:
                    status, latency = ping(ip)
                    if status:
                        status_str = f"ONLINE ({latency} ms)" if latency else "ONLINE"
                        print(f"{ip.ljust(16)}{name.ljust(20)}\033[92m{status_str}\033[0m")
                        log_file.write(f"{ip} - {name} - {status_str}\n")
                    else:
                        status_str = "OFFLINE"
                        print(f"{ip.ljust(16)}{name.ljust(20)}\033[91m{status_str}\033[0m")
                        log_file.write(f"{ip} - {name} - {status_str}\n")
                        # Звуковой сигнал для Windows XP
                        print('\a', end='')
            
            print("\nРезультаты сохранены в 2.txt")
            print(f"Следующая проверка через {interval} секунд...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nМониторинг остановлен пользователем")

if __name__ == "__main__":
    main()