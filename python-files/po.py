import os
import time
import subprocess
import psutil
import sys

def main():
    # �������� PID �������� ��������
    current_pid = os.getpid()
    
    # ������� ������������ ������� (���� �� cmd.exe)
    parent_pid = None
    try:
        current_process = psutil.Process(current_pid)
        parent_process = current_process.parent()
        if parent_process and "cmd.exe" in parent_process.name().lower():
            parent_pid = parent_process.pid
    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
        pass
    
    # ��������� ��� �������� cmd.exe, ����� �������������
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.name().lower() == "cmd.exe" and proc.pid != parent_pid:
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    time.sleep(3)  # ����� 3 �������
    
    # ��������� .bat ����
    bat_path = r"C:\Users\user\Desktop\radio\start_radio.bat"
    if os.path.exists(bat_path):
        subprocess.Popen(bat_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    sys.exit(0)  # ���������� ����������

if __name__ == "__main__":
    main()