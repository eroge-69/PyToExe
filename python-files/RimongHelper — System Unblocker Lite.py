import tkinter as tk
from tkinter import messagebox
import os
import ctypes
import subprocess
import winreg
import shutil
import psutil

# === Функции системного помощника ===
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

def disable_antivirus_fake():
    messagebox.showinfo("Антивирус", "Отключение Антивируса Не роботает.")
    log("Отключение АнтиВируса No Work.")

def enable_task_manager():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Policies\System")

    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    messagebox.showinfo("Успешно", "Диспетчер задач разблокирован.")
    log("Диспетчер задач разблокирован.")

def enable_regedit():
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
    winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    log("Редактор реестра разблокирован.")

def enable_cmd():
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Policies\Microsoft\Windows\System")
    winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    log("Командная строка разблокирована.")

def enable_powershell():
    subprocess.run("powershell -Command \"Set-ExecutionPolicy Unrestricted -Scope CurrentUser -Force\"",
                   shell=True)
    log("PowerShell разблокирован.")

def restart_explorer():
    os.system("taskkill /f /im explorer.exe")
    os.system("start explorer.exe")
    log("Проводник перезапущен.")

def open_tool(tool):
    try:
        os.system(f"start {tool}")
        log(f"{tool} открыт.")
    except:
        log(f"Не удалось открыть {tool}.")

def clear_temp():
    try:
        temp_paths = [os.environ["TEMP"], os.environ["TMP"]]
        for path in temp_paths:
            for file in os.listdir(path):
                try:
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    continue
        log("Временные файлы удалены.")
    except Exception as e:
        log(f"Ошибка при очистке: {e}")

# === Обновление данных системного монитора ===
def update_monitor():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    cpu_label.config(text=f"Загрузка CPU: {cpu}%")
    ram_label.config(text=f"RAM: {ram.percent}% ({round(ram.used / (1024**3), 1)}ГБ из {round(ram.total / (1024**3), 1)}ГБ)")
    disk_label.config(text=f"Диск: {disk.percent}% ({round(disk.used / (1024**3), 1)}ГБ из {round(disk.total / (1024**3), 1)}ГБ)")

    monitor_frame.after(1000, update_monitor)

# === Интерфейс ===
app = tk.Tk()
app.title("RimongHelper — System Unblocker Lite")
app.geometry("600x750")
app.configure(bg="white")

BUTTON_STYLE = {"bg": "#0078D7", "fg": "white", "font": ("Arial", 14), "width": 40, "height": 2}

tk.Label(app, text="🛠️ RimongHelper", font=("Arial", 24, "bold"), fg="black", bg="white").pack(pady=10)

tk.Button(app, text="🔴 Отключить антивирус (не work)", command=disable_antivirus_fake, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="✅ Включить Диспетчер задач", command=enable_task_manager, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="🟢 Разблокировать Редактор реестра", command=enable_regedit, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="🟢 Разблокировать CMD", command=enable_cmd, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="🔵 Разблокировать PowerShell", command=enable_powershell, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="🔁 Перезапустить Проводник", command=restart_explorer, **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="📂 Открыть regedit", command=lambda: open_tool("regedit"), **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="📂 Открыть msconfig", command=lambda: open_tool("msconfig"), **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="📂 Открыть services.msc", command=lambda: open_tool("services.msc"), **BUTTON_STYLE).pack(pady=3)
tk.Button(app, text="🧹 Очистить временные файлы", command=clear_temp, **BUTTON_STYLE).pack(pady=3)

# === Монитор ===
tk.Label(app, text="📊 Системный монитор", font=("Arial", 18, "bold"), bg="white", fg="black").pack(pady=10)
monitor_frame = tk.Frame(app, bg="white")
monitor_frame.pack(pady=5)

cpu_label = tk.Label(monitor_frame, text="Загрузка CPU: --%", font=("Arial", 14), bg="white", fg="black")
cpu_label.pack(pady=2)

ram_label = tk.Label(monitor_frame, text="RAM: --%", font=("Arial", 14), bg="white", fg="black")
ram_label.pack(pady=2)

disk_label = tk.Label(monitor_frame, text="Диск: --%", font=("Arial", 14), bg="white", fg="black")
disk_label.pack(pady=2)

update_monitor()  # Запускаем обновление монитора

# === Журнал ===
tk.Label(app, text="📝 Журнал действий", font=("Arial", 12), bg="white", fg="black").pack(pady=(10, 5))
log_box = tk.Text(app, height=8, bg="#f0f0f0", fg="black", font=("Consolas", 10))
log_box.pack(fill=tk.BOTH, padx=20, pady=(0, 20))

# Предупреждение о правах администратора
if not is_admin():
    messagebox.showwarning("Требуются права администратора", "Для полной работы запусти программу от имени администратора.")

app.mainloop()
