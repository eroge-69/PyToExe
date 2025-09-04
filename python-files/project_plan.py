import sys
import psutil
import subprocess
import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
import wmi

# Функции для получения данных
def get_cpu_usage():
    return f"{psutil.cpu_percent(interval=1)}%"

def get_ram_usage():
    ram = psutil.virtual_memory()
    return f"{ram.percent}% ({ram.used//1024//1024}MB used of {ram.total//1024//1024}MB)"

def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    uptime = now - boot_time
    return str(uptime).split('.')[0]  # без микросекунд

def get_event_errors():
    # Получаем последние 5 критических и ошибок
    cmd = ['wevtutil', 'qe', 'System', '/q:*[System[(Level=1 or Level=2)]]', '/c:5', '/f:text']
    try:
        result = subprocess.check_output(cmd, text=True)
        return result
    except Exception as e:
        return f"Ошибка получения событий: {e}"

def check_windows_backup():
    try:
        result = subprocess.check_output('wbadmin get versions', shell=True, text=True)
        return "Архивация включена" if "No" not in result else "Архивация не настроена"
    except Exception as e:
        return f"Ошибка: {e}"

def check_system_restore():
    try:
        c = wmi.WMI()
        for sr in c.Win32_SystemRestore():
            if sr.Description:
                return "Защита системы включена"
        return "Защита системы отключена"
    except Exception as e:
        return f"Ошибка: {e}"

def check_windows_defender():
    try:
        cmd = ['powershell', '-Command', 'Get-MpComputerStatus | Select-Object AMServiceEnabled, AntispywareEnabled, AntivirusEnabled, RealTimeProtectionEnabled']
        result = subprocess.check_output(cmd, text=True)
        return result
    except Exception as e:
        return f"Ошибка: {e}"

# GUI
class OneClickTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("One-Click Health Check")
        self.setGeometry(300, 300, 700, 500)
        layout = QVBoxLayout()

        self.btn = QPushButton("Проверить систему")
        self.btn.clicked.connect(self.run_check)
        layout.addWidget(self.btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def run_check(self):
        self.output.clear()
        self.output.append(f"CPU Usage: {get_cpu_usage()}")
        self.output.append(f"RAM Usage: {get_ram_usage()}")
        self.output.append(f"Uptime: {get_uptime()}")
        self.output.append("\nПоследние системные ошибки:\n")
        self.output.append(get_event_errors())
        self.output.append("\nАрхивация и восстановление:")
        self.output.append(check_windows_backup())
        self.output.append("\nЗащита системы:")
        self.output.append(check_system_restore())
        self.output.append("\nWindows Defender:")
        self.output.append(check_windows_defender())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OneClickTool()
    window.show()
    sys.exit(app.exec())
