import os
import sys
import datetime
import time
import json
import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import ctypes

# Константы
LOCK_FILE = "license_remover.lock"
LICENSE_FILE = "license"
CODE = "7118"

def create_lock_file():
    """Создает файл блокировки с временем удаления"""
    lock_data = {
        "delete_time": (datetime.datetime.now() + datetime.timedelta(hours=24)).timestamp(),
        "created": datetime.datetime.now().timestamp()
    }
    
    with open(LOCK_FILE, "w") as f:
        json.dump(lock_data, f)
    
    messagebox.showinfo("Успех", "Защита активирована! Файл license будет автоматически удален через 48 часов.\n"
                        f"Для отмены введите код {CODE} при появлении диалога.")

def should_delete():
    """Проверяет, нужно ли запускать процесс удаления"""
    if not os.path.exists(LOCK_FILE):
        return False
    
    try:
        with open(LOCK_FILE) as f:
            data = json.load(f)
        
        current_time = time.time()
        delete_time = data["delete_time"]
        
        # Проверяем, наступило ли время удаления
        return current_time >= delete_time
    except:
        return False

def cleanup():
    """Удаляет файл лицензии"""
    if os.path.exists(LICENSE_FILE):
        try:
            os.remove(LICENSE_FILE)
            return True
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False
    return False

def show_confirmation_dialog():
    """Показывает диалоговое окно с запросом кода"""
    root = tk.Tk()
    root.title("Подтверждение удаления")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Делаем окно поверх всех и с фокусом
    root.attributes('-topmost', True)
    root.focus_force()
    root.grab_set()
    
    # Принудительно устанавливаем фокус на окно
    root.after(100, lambda: root.focus_force())
    
    # Создаем элементы интерфейса
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(frame, text="Файл license будет удален!", 
             font=("Arial", 12, "bold"), fg="red").pack(pady=(0, 10))
    
    tk.Label(frame, text=f"Для отмены удаления введите код {CODE}:").pack()
    
    code_entry = tk.Entry(frame, show="*", font=("Arial", 14), width=10)
    code_entry.pack(pady=10)
    code_entry.focus_set()
    
    timer_label = tk.Label(frame, text="Осталось времени: 60 секунд", font=("Arial", 10))
    timer_label.pack()
    
    result = {"value": False}
    
    def check_code():
        """Проверяет введенный код"""
        input_code = code_entry.get()
        if input_code == CODE:
            result["value"] = True
            root.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный код! Повторите попытку.")
            code_entry.delete(0, tk.END)
    
    def perform_cleanup():
        """Выполняет очистку и закрывает окно"""
        if cleanup():
            message = "Файл license успешно удален!"
        else:
            message = "Файл license не найден или уже удален"
        
        result["value"] = False
        root.destroy()
        # Удаляем файл блокировки после выполнения
        try:
            os.remove(LOCK_FILE)
        except:
            pass
        # Завершаем программу после удаления
        sys.exit(0)
    
    # Таймер обратного отсчета
    def countdown(seconds=60):
        while seconds > 0 and root.winfo_exists():
            timer_label.config(text=f"Осталось времени: {seconds} секунд")
            seconds -= 1
            time.sleep(1)
        
        if root.winfo_exists():
            perform_cleanup()
    
    # Запускаем таймер в отдельном потоке
    timer_thread = threading.Thread(target=countdown, daemon=True)
    timer_thread.start()
    
    # Кнопки
    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Отменить удаление", 
              command=check_code, width=15).pack(side=tk.LEFT, padx=5)
    
    tk.Button(btn_frame, text="Удалить сейчас", 
              command=perform_cleanup, width=15).pack(side=tk.LEFT, padx=5)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", perform_cleanup)
    
    # Периодически возвращаем фокус на окно
    def keep_focus():
        if root.winfo_exists():
            root.attributes('-topmost', True)
            root.focus_force()
            root.grab_set()
            root.after(1000, keep_focus)
    
    root.after(1000, keep_focus)
    
    root.mainloop()
    
    # Если удаление отменено
    if result["value"]:
        try:
            os.remove(LOCK_FILE)
            messagebox.showinfo("Отменено", "Удаление файла license отменено!")
            sys.exit(0)
        except:
            sys.exit(0)

def add_to_startup():
    """Добавляет программу в автозагрузку текущего пользователя"""
    try:
        # Получаем путь к папке автозагрузки
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Создаем ярлык
        script_path = os.path.abspath(sys.argv[0])
        shortcut_path = os.path.join(startup_path, "LicenseProtector.lnk")
        
        # Создаем команду для создания ярлыка
        vbs_script = os.path.join(startup_path, "create_shortcut.vbs")
        
        with open(vbs_script, "w") as f:
            f.write(f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            Set oLink = oWS.CreateShortcut("{shortcut_path}")
            oLink.TargetPath = "{script_path}"
            oLink.Save
            """)
        
        # Выполняем скрипт VBS для создания ярлыка
        subprocess.run(['cscript.exe', vbs_script], check=True)
        
        # Удаляем временный скрипт
        time.sleep(1)
        os.remove(vbs_script)
        
        return True
    except Exception as e:
        print(f"Ошибка добавления в автозагрузку: {e}")
        return False

def main():
    # Проверяем, нужно ли показать диалог удаления
    if should_delete():
        show_confirmation_dialog()
        return
    
    # Если файл блокировки не существует, создаем его
    if not os.path.exists(LOCK_FILE):
        create_lock_file()
        
        # Добавляем в автозагрузку
        if add_to_startup():
            print("done")
        else:
            messagebox.showwarning("Предупреждение", 
                                  "Не удалось добавить программу в автозагрузку.\n"
                                  "Диалог удаления не появится автоматически после перезагрузки.")
        
        # Сразу завершаем работу после настройки
        sys.exit(0)

if __name__ == "__main__":
    # Запускаем только если в текущей папке есть файл license
    if os.path.exists(LICENSE_FILE):
        main()
    else:
        messagebox.showwarning(
            "Файл не найден", 
            f"Файл {LICENSE_FILE} не найден в текущей папке.\n"
            "Программа будет закрыта."
        )
        
