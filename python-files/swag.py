import os
import sys
import subprocess
from pathlib import Path
from tkinter import *
import webbrowser

class UniversalApp:
    def __init__(self):
        # Определяем пути относительно расположения скрипта
        self.script_dir = Path(__file__).parent.absolute()
        self.image_path = self.script_dir / "2.png"
        self.open_image_script = self.script_dir / "open_image.py"  # Добавляем путь к скрипту
        self.youtube_url = "https://youtu.be/z-iG3QTw41Q?si=rQM-6pdIOLtWAUsW"
        
        # Создаем GUI
        self.root = Tk()
        self.root.title("Универсальное меню")
        self.root.geometry("500x300")
        self.root.configure(bg="#f0f0f0")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настраивает интерфейс пользователя"""
        title = Label(self.root, text="Меню выбора", font=("Arial", 16), bg="#f0f0f0")
        title.pack(pady=10)
        
        button_style = {
            'font': ('Arial', 12),
            'width': 30,
            'height': 2,
            'bd': 2,
            'relief': 'ridge'
        }
        
        Button(self.root, text="1. лав бу пес", 
              command=self.open_image, bg="#00ff00", **button_style).pack(pady=5)
        
        Button(self.root, text="2. люблю сабак", 
              command=self.run_open_image_script, bg="#ff0000", **button_style).pack(pady=5)  # Изменено на запуск скрипта
        
        Button(self.root, text="3. не хуйня", 
              command=self.close_app, bg="#ffffff", **button_style).pack(pady=5)
        
        # Информация о путях
        path_info = Label(self.root, 
                        text=f"Расположение скрипта: {self.script_dir}",
                        font=("Arial", 8), bg="#f0f0f0")
        path_info.pack(pady=10)
    
    def open_image(self):
        """Открывает изображение из папки со скриптом"""
        try:
            if self.image_path.exists():
                if sys.platform == "win32":
                    os.startfile(str(self.image_path))
                elif sys.platform == "darwin":
                    subprocess.Popen(['open', str(self.image_path)])
                else:
                    subprocess.Popen(['xdg-open', str(self.image_path)])
                print(f"Изображение открыто: {self.image_path}")
            else:
                print(f"Файл изображения не найден: {self.image_path}")
        except Exception as e:
            print(f"Ошибка при открытии изображения: {e}")
    
    def run_open_image_script(self):
        """Запускает скрипт open_image.py"""
        try:
            if self.open_image_script.exists():
                if sys.platform == "win32":
                    subprocess.Popen(['python', str(self.open_image_script)], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen(['python3', str(self.open_image_script)])
                print(f"Скрипт запущен: {self.open_image_script}")
            else:
                print(f"Файл скрипта не найден: {self.open_image_script}")
        except Exception as e:
            print(f"Ошибка при запуске скрипта: {e}")
    
    def close_app(self):
        """Закрывает приложение"""
        self.root.destroy()
    
    def run(self):
        """Запускает главный цикл"""
        self.root.mainloop()

if __name__ == "__main__":
    app = UniversalApp()
    app.run()