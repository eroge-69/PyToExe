import os
import psutil
import sys

def close_gta5():
    process_name = "GTA5.exe"  # Имя процесса GTA 5
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                proc.terminate()  # Попытка закрыть процесс
                print(f"Процесс GTA5.exe (PID: {proc.info['pid']}) успешно закрыт.")
                return True
            except psutil.NoSuchProcess:
                print("Процесс GTA5.exe не найден.")
            except psutil.AccessDenied:
                print("Недостаточно прав для закрытия процесса.")
            except Exception as e:
                print(f"Ошибка: {e}")
    
    print("GTA 5 не запущена.")
    return False

if __name__ == "__main__":
    close_gta5()
    input("Нажмите Enter для выхода...")
