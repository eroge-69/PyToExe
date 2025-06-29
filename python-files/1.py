import tkinter as tk
import subprocess
import os
from datetime import datetime

# ===================== НАСТРОЙКИ =====================
# Проверьте эти пути!
PATHS = {
    1: {'shortcut': r"C:\Script\1 ZAL.lnk", 'script': r"C:\Scripts\run_macro1zal.ps1"},
    2: {'shortcut': r"C:\Script\2 ZAL.lnk", 'script': r"C:\Scripts\run_macro.ps1"},
    3: {'shortcut': r"C:\Script\3 ZAL.lnk", 'script': r"C:\Scripts\run_macro3zal.ps1"}
}

VNC_PATH = r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe"  # Проверьте путь!
VNC_SERVER = "192.168.1.100"  # Замените на ваш IP

LOG_FILE = r"C:\Scripts\zal_log.txt"

# ===================== ФУНКЦИИ =====================
def run_script(zal_number):
    btn = buttons[zal_number]
    original_text = btn['text']
    original_color = btn['bg']
    
    try:
        data = PATHS.get(zal_number)
        if not data:
            update_button(btn, "Ошибка номера", "red")
            return

        # Проверка существования файлов
        missing_files = [name for name, path in {
            'Ярлык': data['shortcut'],
            'Скрипт': data['script']
        }.items() if not os.path.exists(path)]
        
        if missing_files:
            update_button(btn, f"Нет: {', '.join(missing_files)}", "red")
            return

        # Запуск PowerShell
        subprocess.Popen([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-WindowStyle", "Hidden",
            "-File", data['script']
        ], shell=True)
        
        update_button(btn, f"Зал {zal_number} выкл...", "#4CAF50")
        log_action(f"Запущен зал {zal_number}")

    except Exception as e:
        update_button(btn, f"Ошибка: {type(e).__name__}", "red")
        log_action(f"Ошибка в зале {zal_number}: {str(e)}")
    finally:
        btn.after(3000, lambda: reset_button(btn, original_text, original_color))

def run_vnc():
    btn = buttons[4]
    original_text = btn['text']
    original_color = btn['bg']
    
    try:
        if not os.path.exists(VNC_PATH):
            update_button(btn, "VNC не найден!", "red")
            return
            
        subprocess.Popen([VNC_PATH, VNC_SERVER])
        update_button(btn, "Подключение VNC...", "#9C27B0")
        log_action(f"Запущен VNC: {VNC_SERVER}")

    except Exception as e:
        update_button(btn, f"Ошибка VNC", "red")
        log_action(f"Ошибка VNC: {str(e)}")
    finally:
        btn.after(3000, lambda: reset_button(btn, original_text, original_color))

def update_button(btn, text, color):
    btn.config(text=text, bg=color)

def reset_button(btn, text, color):
    btn.config(text=text, bg=color)

def log_action(message):
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {message}\n")
    except Exception as e:
        print(f"Ошибка лога: {str(e)}")

# ===================== ЗАПУСК ПРОГРАММЫ =====================
if __name__ == "__main__":
    try:
        # Создаем главное окно
        window = tk.Tk()
        window.title("Управление залами")
        window.geometry("600x400")
        window.configure(bg="#f0f0f0")

        # Стиль кнопок
        button_style = {
            'font': ('Arial', 12),
            'width': 20,
            'height': 2,
            'borderwidth': 3
        }

        # Создаем и размещаем кнопки
        buttons = {
            1: tk.Button(window, text="ЗАЛ 1", command=lambda: run_script(1), bg="#4CAF50", fg="white", **button_style),
            2: tk.Button(window, text="ЗАЛ 2", command=lambda: run_script(2), bg="#2196F3", fg="white", **button_style),
            3: tk.Button(window, text="ЗАЛ 3", command=lambda: run_script(3), bg="#FF9800", fg="white", **button_style),
            4: tk.Button(window, text="ЗАЛ 4", command=run_vnc, bg="#9C27B0", fg="white", **button_style)
        }

        for i, btn in enumerate(buttons.values(), start=1):
            btn.pack(pady=10)

        # Запускаем главный цикл
        window.mainloop()

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        input("Нажмите Enter для выхода...")