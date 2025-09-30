import customtkinter
import tkinter as tk
import webbrowser

# --- Настройка внешнего вида CustomTkinter ---
# Устанавливаем режим: "Dark" (Темный)
customtkinter.set_appearance_mode("Dark") 
# Устанавливаем цветовую схему: "Blue" (Синяя)
customtkinter.set_default_color_theme("blue") 

class App(customtkinter.CTk):
    """Класс основного приложения."""
    def __init__(self):
        super().__init__()

        # --- Основные настройки окна ---
        self.title("Info")  
        # Устанавливаем желаемый размер: стало больше!
        self.window_width = 600
        self.window_height = 450
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)
        
        # --- Центрирование окна ---
        self.center_window()

        # --- Настройка макета (Grid) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Фрейм-контейнер для центрирования элементов
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Настройка строк и колонок для центрирования элементов внутри фрейма
        self.main_frame.grid_rowconfigure((0, 4), weight=1)    
        self.main_frame.grid_columnconfigure((0, 2), weight=1) 
        
        # --- Заголовок ---
        self.label = customtkinter.CTkLabel(
            self.main_frame, 
            text="Спасибо за выбор", 
            font=customtkinter.CTkFont(size=30, weight="bold") # Сделаем текст крупнее
        )
        self.label.grid(row=1, column=1, padx=20, pady=(40, 40))

        # --- Кнопка "Наш форум" ---
        self.forum_button = customtkinter.CTkButton(
            self.main_frame, 
            text="Наш форум", 
            command=self.open_forum,
            width=250, # Сделаем кнопки шире
            height=50, # Сделаем кнопки выше
            corner_radius=12,
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.forum_button.grid(row=2, column=1, padx=20, pady=15)

        # --- Кнопка "Мой телеграм" ---
        self.telegram_button = customtkinter.CTkButton(
            self.main_frame, 
            text="Мой телеграм", 
            command=self.open_telegram,
            width=250,
            height=50,
            corner_radius=12,
            fg_color="#0088CC",  # Фирменный синий Telegram
            hover_color="#006699",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.telegram_button.grid(row=3, column=1, padx=20, pady=15)

    # --- Функция для центрирования окна ---
    def center_window(self):
        """Вычисляет и устанавливает позицию окна по центру экрана."""
        # Получаем высоту и ширину экрана
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Вычисляем позицию X и Y для центрирования
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)

        # Устанавливаем геометрию окна
        self.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')

    # --- Функции-обработчики кнопок ---
    def open_forum(self):
        """Открывает ссылку на форум в браузере."""
        # ! ЗАМЕНИТЕ ЭТУ ССЫЛКУ НА АДРЕС ВАШЕГО ФОРУМА !
        forum_url = "yabforum.com.tr"  
        webbrowser.open(forum_url)
        print(f"Открыта ссылка: {forum_url}")

    def open_telegram(self):
        """Открывает ссылку на Telegram в браузере."""
        # ! ЗАМЕНИТЕ ЭТУ ССЫЛКУ НА ВАШ НИК/КАНАЛ В ТЕЛЕГРАМ !
        telegram_url = "https://t.me/sbyov"  
        webbrowser.open(telegram_url)
        print(f"Открыта ссылка: {telegram_url}")

# --- Запуск приложения ---
if __name__ == "__main__":
    app = App()
    app.mainloop()