import tkinter as tk
from tkinter import ttk
import threading
import tempfile
import os
import sys
import subprocess
import zipfile
import requests
import io

class GfusionLauncher:
    def __init__(self):
        self.temp_dir = None
        self.repo_url = "https://github.com/Cr0mb/CS2-GFusion-Python/archive/refs/heads/main.zip"
    
    def download_and_extract_gfusion(self):
        """Скачивает и распаковывает Gfusion с GitHub"""
        try:
            # Создаем временную папку
            self.temp_dir = tempfile.mkdtemp()
            
            # Скачиваем архив с GitHub
            print("Скачивание Gfusion...")
            response = requests.get(self.repo_url)
            zip_data = io.BytesIO(response.content)
            
            # Распаковываем архив
            print("Распаковка Gfusion...")
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Путь к распакованной папке
            extracted_dir = os.path.join(self.temp_dir, "CS2-GFusion-Python-main")
            return extracted_dir
            
        except Exception as e:
            print(f"Ошибка при загрузке Gfusion: {e}")
            return None
    
    def start_gfusion(self):
        """Запускает Gfusion через start.pyw"""
        try:
            # Скачиваем и распаковываем
            gfusion_dir = self.download_and_extract_gfusion()
            if not gfusion_dir:
                return False
            
            # Путь к start.pyw
            start_pyw_path = os.path.join(gfusion_dir, "start.pyw")
            
            if not os.path.exists(start_pyw_path):
                print("Файл start.pyw не найден!")
                return False
            
            # Запускаем start.pyw
            print("Запуск Gfusion...")
            if sys.platform == "win32":
                # Для Windows используем startfile чтобы открыть .pyw без консоли
                os.startfile(start_pyw_path)
            else:
                # Для других OS используем subprocess
                subprocess.Popen([sys.executable, start_pyw_path], 
                               cwd=gfusion_dir,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при запуске Gfusion: {e}")
            return False

# Создаем главное окно для Timer Resolution
def create_timer_resolution_gui():
    root = tk.Tk()
    root.title("Set Timer Resolution")
    root.geometry("400x250")
    root.resizable(False, False)

    # Timer Resolution Range
    range_frame = ttk.LabelFrame(root, text="Timer Resolution Range", padding=10)
    range_frame.pack(pady=10, padx=10, fill="x")

    min_label = ttk.Label(range_frame, text="Minimum Resolution  15.625")
    min_label.pack(anchor="w")

    max_label = ttk.Label(range_frame, text="Maximum Resolution  0.500")
    max_label.pack(anchor="w")

    # Current Timer Information
    current_frame = ttk.LabelFrame(root, text="Current Timer Information", padding=10)
    current_frame.pack(pady=10, padx=10, fill="x")

    current_res_label = ttk.Label(current_frame, text="Current Resolution  15.625 milliseconds")
    current_res_label.pack(anchor="w")

    # Кнопки
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=20)

    max_button = ttk.Button(button_frame, text="Maximum", command=lambda: set_resolution("max"))
    max_button.pack(side="left", padx=5)

    default_button = ttk.Button(button_frame, text="Default", command=lambda: set_resolution("default"))
    default_button.pack(side="left", padx=5)

    close_button = ttk.Button(button_frame, text="Close", command=root.quit)
    close_button.pack(side="left", padx=5)

    # Функция для кнопок (заглушка)
    def set_resolution(mode):
        pass

    # Функция для активации читера по F12
    def open_cheat(event):
        # Показываем сообщение о запуске
        status_window = tk.Toplevel(root)
        status_window.title("Cheat Status")
        status_window.geometry("300x120")
        status_window.attributes("-topmost", True)
        
        label = tk.Label(status_window, text="Запуск Gfusion...", font=("Arial", 12))
        label.pack(pady=20)
        
        progress = ttk.Progressbar(status_window, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        # Запускаем Gfusion в отдельном потоке
        def start_cheat():
            try:
                launcher = GfusionLauncher()
                success = launcher.start_gfusion()
                
                if success:
                    status_window.after(0, lambda: label.config(text="Gfusion запущен!"))
                    status_window.after(2000, status_window.destroy)
                else:
                    status_window.after(0, lambda: label.config(text="Ошибка запуска Gfusion"))
                    status_window.after(3000, status_window.destroy)
                    
            except Exception as e:
                status_window.after(0, lambda: label.config(text=f"Ошибка: {str(e)}"))
                status_window.after(3000, status_window.destroy)
        
        cheat_thread = threading.Thread(target=start_cheat)
        cheat_thread.daemon = True
        cheat_thread.start()

    root.bind('<F12>', open_cheat)
    root.focus_set()

    root.mainloop()

if __name__ == "__main__":
    create_timer_resolution_gui()