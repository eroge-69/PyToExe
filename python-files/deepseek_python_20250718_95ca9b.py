import os
import time
import subprocess
import keyboard
from threading import Thread

class CameraBlocker:
    def __init__(self):
        self.running = False
        self.check_interval = 1  # seconds
        self.camera_blocked = False
        self.active = False
        
    def is_camera_active(self):
        """Проверяет, активна ли камера (для Windows)"""
        try:
            result = subprocess.run(
                ['powershell', '-command', 'Get-CimInstance -Query "SELECT * FROM Win32_PnPEntity WHERE (PNPClass = \'Image\' OR PNPClass = \'Camera\')" | Where-Object { $_.Status -eq \'OK\' }'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Win32_PnPEntity" in result.stdout
        except:
            return False
    
    def disable_camera(self):
        """Отключает камеру (для Windows)"""
        try:
            subprocess.run(
                ['powershell', '-command', 'Get-CimInstance -Query "SELECT * FROM Win32_PnPEntity WHERE (PNPClass = \'Image\' OR PNPClass = \'Camera\')" | ForEach-Object { Disable-PnpDevice -InstanceId $_.DeviceID -Confirm:$false }'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.camera_blocked = True
            print("Камера была отключена")
        except Exception as e:
            print(f"Ошибка при отключении камеры: {e}")
    
    def enable_camera(self):
        """Включает камеру (для Windows)"""
        try:
            subprocess.run(
                ['powershell', '-command', 'Get-CimInstance -Query "SELECT * FROM Win32_PnPEntity WHERE (PNPClass = \'Image\' OR PNPClass = \'Camera\')" | ForEach-Object { Enable-PnpDevice -InstanceId $_.DeviceID -Confirm:$false }'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.camera_blocked = False
            print("Камера была включена")
        except Exception as e:
            print(f"Ошибка при включении камеры: {e}")
    
    def monitor(self):
        """Мониторит состояние камеры"""
        while self.running:
            if self.active and self.is_camera_active():
                print("Обнаружена активная камера - отключаем...")
                self.disable_camera()
            time.sleep(self.check_interval)
    
    def start(self):
        """Запускает мониторинг камеры"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.monitor)
            self.thread.daemon = True
            self.thread.start()
            print("Ожидание активации Streamer Mode (нажмите F2)...")
    
    def stop(self):
        """Останавливает мониторинг и включает камеру обратно"""
        if self.running:
            self.running = False
            if self.camera_blocked:
                self.enable_camera()
            self.thread.join()
            print("Streamer Mode деактивирован.")

def main():
    blocker = CameraBlocker()
    blocker.start()
    
    try:
        while True:
            if keyboard.is_pressed('F2'):
                if not blocker.active:
                    blocker.active = True
                    print("Streamer Mode АКТИВИРОВАН")
                else:
                    blocker.active = False
                    print("Streamer Mode ДЕАКТИВИРОВАН")
                time.sleep(0.5)  # Задержка для предотвращения многократного срабатывания
            time.sleep(0.1)
    except KeyboardInterrupt:
        blocker.stop()
        print("Программа завершена.")

if __name__ == "__main__":
    # Проверка прав администратора для Windows
    if os.name == 'nt':
        try:
            test_file = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except PermissionError:
            print("Ошибка: Этот скрипт требует прав администратора для работы на Windows.")
            print("Пожалуйста, запустите скрипт от имени администратора.")
            input("Нажмите Enter для выхода...")
            exit()
    
    # Проверка наличия модуля keyboard
    try:
        import keyboard
    except ImportError:
        print("Требуется модуль keyboard. Установите его командой: pip install keyboard")
        input("Нажмите Enter для выхода...")
        exit()
    
    print("=== Streamer Mode Camera Blocker ===")
    print("Нажмите F2 для активации/деактивации режима")
    print("Нажмите Ctrl+C для выхода")
    main()