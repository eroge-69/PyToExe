import psutil
import time
import tkinter as tk
from tkinter import messagebox
import os

# Список названий процессов для блокировки
process_names = ["ExecutedProgramsList.exe", "ShellBag Analyzer & Cleaner (3..", "Shellbags.exe", 
                "Prefecth.exe", "Recent.exe", "Roaming.exe", "Temp.exe", "LastActivityView.exe", 
                "Everything.exe", "WinPrefetchView.exe", "JumpListsView.exe", "UserAssistView.exe", 
                "Lists USB Devices.exe", "Проводник.exe"]

def block_process():
    running_processes = set()
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_name = proc.info['name']
                if any(name in process_name for name in process_names) and proc.pid not in running_processes:
                    # Сначала завершаем процесс
                    try:
                        proc.terminate()
                        proc.kill()  # Убеждаемся, что процесс завершен
                        proc.wait(timeout=0.5)  # Короткий таймаут для завершения
                    except psutil.TimeoutExpired:
                        try:
                            os.kill(proc.pid, 9)  # Принудительное завершение
                        except (OSError, psutil.NoSuchProcess):
                            pass
                    except psutil.AccessDenied:
                        print(f"Доступ запрещен для процесса {process_name}, требуется запуск с правами администратора.")
                    
                    running_processes.add(proc.pid)
                    
                    # Проверка и повторное завершение, если процесс пытается возобновиться
                    while psutil.pid_exists(proc.pid):
                        try:
                            os.kill(proc.pid, 9)
                        except (psutil.NoSuchProcess, OSError):
                            break
                        time.sleep(0.05)
                    
                    # Создаем и сразу скрываем главное окно
                    root = tk.Tk()
                    root.withdraw()
                    # Устанавливаем окно поверх всех
                    root.attributes('-topmost', 1)
                    # Показываем сообщение об ошибке
                    messagebox.showerror("Ошибка", 
                                        f"Ошибка: x80003x - Запуск процесса {process_name} заблокирован! Приложение недоступно.", 
                                        parent=root)
                    # Закрываем окно
                    root.destroy()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        time.sleep(0.05)  # Минимальная задержка для частой проверки
        # Очистка списка завершенных процессов
        running_processes = {pid for pid in running_processes if psutil.pid_exists(pid)}

if __name__ == "__main__":
    print("Мониторинг и блокировка процессов запущены...")
    block_process()