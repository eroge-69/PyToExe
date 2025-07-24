import random
import time
from tkinter import Tk, Frame, Label, Entry, Button, Radiobutton, StringVar
from enum import Enum
from datetime import datetime
import threading


class DataFetcherApp(Tk):
    """Класс приложения для сбора данных"""
    
    class Mode(Enum):
        """Режимы скорости получения данных"""
        FAST = 1
        MEDIUM = 2
        SLOW = 3

    def __init__(self):
        super().__init__()
        
        # Настройка главного окна
        self.title("Data Fetcher Tool v2.0")
        self.geometry("500x300")
        self.configure(bg="#282c34")  # Тёмная тема
        
        # Цветовая палитра
        BG_COLOR = "#282c34"
        FG_COLOR = "#ff6b6b"   # Яркий красный акцент
        BTN_BG = "#3f3f46"
        BTN_FG = "#ffffff"
        ACTIVE_BG = "#4a5568"
        STATUS_SUCCESS = "#ff6b6b"
        
        # Оформление форм и подписей
        title_font = ('Arial Bold', 14)
        label_font = ('Consolas', 12)
        entry_font = ('Consolas', 12)
        
        # Поле ввода URL
        Label(self, text="Enter URL:", bg=BG_COLOR, fg=FG_COLOR, font=title_font).pack(padx=10, pady=10)
        self.url_entry = Entry(self, width=50, font=entry_font, relief='solid', bd=1, insertbackground=FG_COLOR)
        self.url_entry.pack(padx=10, pady=10)
        
        # Переключатели режимов
        radio_frame = Frame(self, bg=BG_COLOR)
        self.mode_var = StringVar(value=self.Mode.FAST.name)
        
        for mode in self.Mode:
            Radiobutton(radio_frame, text=mode.name.capitalize(), variable=self.mode_var, value=mode.name,
                        indicatoron=True, selectcolor=ACTIVE_BG, bg=BG_COLOR, fg=FG_COLOR, highlightthickness=0,
                        activebackground=BTN_BG, activeforeground=BTN_FG).pack(side="left", padx=(10, 0))
            
        radio_frame.pack(padx=10, pady=10)
        
        # Эффектная кнопка с объёмом
        self.button_style = {"bg": BTN_BG, "fg": BTN_FG, "activebackground": ACTIVE_BG, "relief": "raised"}
        Button(self, text="Fetch Data", command=self.start_fetching_thread, **self.button_style).pack(padx=10, pady=10)
        
        # Панель статуса (для отображения хода выполнения)
        self.status_label = Label(self, text="", fg=STATUS_SUCCESS, bg=BG_COLOR, font=label_font)
        self.status_label.pack(padx=10, pady=10)
        
    def start_fetching_thread(self):
        """Обработка начинается в отдельном потоке, чтобы интерфейс остался активным."""
        thread = threading.Thread(target=self.start_fetching)
        thread.daemon = True
        thread.start()

    def animate_progress(self):
        """Показываем простой процент выполнения, чтобы продемонстрировать активность программы."""
        progress = 0
        while getattr(self, "_fetching", False):
            progress += 10
            if progress > 100:
                break
            self.status_label.config(text=f"Fetching data... {progress}% complete.")
            self.update_idletasks()
            time.sleep(0.1)

    def simulate_delay(self):
        """Имитация задержки согласно выбранному режиму скорости."""
        delays = {
            self.Mode.FAST: 1,
            self.Mode.MEDIUM: 2,
            self.Mode.SLOW: 3
        }
        current_mode = self.Mode[self.mode_var.get()]
        delay_range = delays[current_mode]
        time.sleep(random.uniform(delay_range, delay_range + 1))

    def start_fetching(self):
        """Начинаем сбор данных с показом анимации прогресса."""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        # Начинаем анимацию загрузки
        self._fetching = True
        loading_thread = threading.Thread(target=self.animate_progress)
        loading_thread.daemon = True
        loading_thread.start()
        
        # Пауза для симуляции реального процесса
        self.simulate_delay()
        
        # Завершение анимации
        self._fetching = False
        loading_thread.join(timeout=0.5)
        
        # Получили данные и сохранили их в файл
        result = self.fetch_data()
        self.show_result(result)

    def fetch_data(self):
        """Генератор тестовых данных (логин-пароль)."""
        credentials = [
            ("User1", "pass123"),
            ("Admin", "admin123"),
            ("Guest", "guest"),
            ("Test", "test123"),
            ("UserX", "secret")
        ]
        return random.choice(credentials)

    def show_result(self, result):
        """Отобразим собранные данные и сохраним их в файл."""
        user, pwd = result
        self.save_to_history(user, pwd)
        self.status_label.config(text=f"\n\nData fetched successfully!\nUsername: {user}\nPassword: {pwd}\nSaved to file.",
                                 fg=STATUS_SUCCESS)

    def save_to_history(self, username, password):
        """Сохраним полученный результат в файл журнала."""
        with open("fetch_log.txt", "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp}: Username={username}, Password={password}\n")


# Запустим программу
if __name__ == "__main__":
    app = DataFetcherApp()
    app.mainloop()
