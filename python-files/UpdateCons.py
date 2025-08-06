import os
import subprocess
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# Конфигурация
TASK_NAME = "ConsDailyUpdate"
LOG_FILE = "updlogs.txt"
CONS_EXE = "cons.exe"

# Логирование
def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")

# Проверка прав администратора
def is_admin():
    try:
        return os.getuid() == 0  # Для Linux/Mac (в Windows всегда вернет False)
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # Для Windows

# Проверка наличия cons.exe
def check_cons_exe():
    if not os.path.exists(CONS_EXE):
        messagebox.showerror("Ошибка", f"Файл {CONS_EXE} не найден в текущей папке!")
        write_log(f"ОШИБКА: {CONS_EXE} не найден")
        return False
    return True

# Проверка существования задачи
def task_exists():
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", TASK_NAME],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

# Создание/обновление задачи
def create_or_update_task(time):
    try:
        exe_path = os.path.join(os.getcwd(), CONS_EXE)
        subprocess.run([
            "schtasks", "/create", "/tn", TASK_NAME,
            "/tr", f'"{exe_path}" /adm /base* /receive_inet /yes /sendstt /process=1',
            "/sc", "daily", "/st", time,
            "/ru", "System", "/rl", "HIGHEST", "/f"
        ], check=True)
        write_log(f"Задача создана. Время: {time}")
        return True
    except subprocess.CalledProcessError as e:
        write_log(f"ОШИБКА создания задачи: {e}")
        return False

# Удаление задачи
def delete_task():
    try:
        subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], check=True)
        write_log("Задача удалена")
        return True
    except subprocess.CalledProcessError as e:
        write_log(f"ОШИБКА удаления задачи: {e}")
        return False

# Запуск задачи
def run_task():
    try:
        subprocess.run(["schtasks", "/run", "/tn", TASK_NAME], check=True)
        write_log("Задача запущена вручную")
        return True
    except subprocess.CalledProcessError as e:
        write_log(f"ОШИБКА запуска задачи: {e}")
        return False

# GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cons Update Scheduler")
        self.geometry("350x250")
        self.resizable(False, False)
        
        # Проверка прав администратора
        if not is_admin():
            messagebox.showerror("Ошибка", "Запустите программу от имени администратора!")
            write_log("ОШИБКА: Недостаточно прав")
            sys.exit(1)
        
        write_log("Программа запущена")
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопки
        btn_create = tk.Button(self, text="Создать задачу", command=self.on_create)
        btn_create.place(x=75, y=30, width=200, height=30)
        
        btn_delete = tk.Button(self, text="Удалить задачу", command=self.on_delete)
        btn_delete.place(x=75, y=70, width=200, height=30)
        
        btn_run = tk.Button(self, text="Запустить задачу", command=self.on_run)
        btn_run.place(x=75, y=110, width=200, height=30)
    
    def on_create(self):
        if not check_cons_exe():
            return
        
        time = simpledialog.askstring("Ввод времени", "Введите время (HH:mm):")
        if time and self.validate_time(time):
            if create_or_update_task(time):
                messagebox.showinfo("Успех", f"Задача создана на {time}")
        elif time:
            messagebox.showerror("Ошибка", "Неверный формат времени!")
    
    def on_delete(self):
        if task_exists():
            if delete_task():
                messagebox.showinfo("Успех", "Задача удалена")
        else:
            messagebox.showwarning("Ошибка", "Задача не найдена")
    
    def on_run(self):
        if task_exists():
            if run_task():
                messagebox.showinfo("Успех", "Задача запущена")
        else:
            messagebox.showerror("Ошибка", "Сначала создайте задачу!")
    
    @staticmethod
    def validate_time(time):
        try:
            datetime.strptime(time, "%H:%M")
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    app = App()
    app.mainloop()
