import tkinter as tk
import json
import os
import threading
from pathlib import Path

# Для звука (опционально)
try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False  # если не Windows или нет winsound

# Путь к файлу сохранения
SAVE_FILE = Path.home() / ".knitting_counter.json"

class KnittingCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("🧶 Счётчик рядов для вязания")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Установка фиолетовой темы
        self.root.configure(bg="#E6E6FA")  # lavender background

        # Загрузка счётчика
        self.count = self.load_count()

        # Заголовок
        self.label_title = tk.Label(
            root,
            text="🧶 Счётчик рядов",
            font=("Comic Sans MS", 20, "bold"),
            bg="#E6E6FA",
            fg="#6A0DAD"  # тёмно-фиолетовый
        )
        self.label_title.pack(pady=20)

        # Счётчик
        self.label_count = tk.Label(
            root,
            text=str(self.count),
            font=("Arial", 48, "bold"),
            bg="#E6E6FA",
            fg="#800080"  # purple
        )
        self.label_count.pack(pady=20)

        # Кнопка сброса
        self.reset_button = tk.Button(
            root,
            text="🔄 Сбросить",
            font=("Arial", 14, "bold"),
            bg="#9370DB",  # medium purple
            fg="white",
            activebackground="#8A2BE2",  # blue violet
            activeforeground="white",
            relief="raised",
            padx=20,
            pady=10,
            command=self.reset
        )
        self.reset_button.pack(pady=20)

        # Привязка пробела
        self.root.bind('<space>', self.increment)
        self.root.focus_set()

    def increment(self, event=None):
        self.count += 1
        self.update_display()
        self.save_count()  # сразу сохраняем!
        if SOUND_ENABLED:
            threading.Thread(target=lambda: winsound.Beep(800, 100), daemon=True).start()

    def reset(self):
        self.count = 0
        self.update_display()
        self.save_count()

    def update_display(self):
        self.label_count.config(text=str(self.count))

    def save_count(self):
        """Сохраняет счётчик в файл в домашней директории пользователя"""
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump({"count": self.count}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_count(self):
        """Загружает счётчик из файла, если есть"""
        try:
            if SAVE_FILE.exists():
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("count", 0)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        return 0

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = KnittingCounter(root)
    root.mainloop()