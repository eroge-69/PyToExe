import customtkinter as ctk
import tkinter as tk
import subprocess

def on_click(button_name):
    """Функция, которая будет выполняться при нажатии на кнопку."""
    print(f"Вы нажали на кнопку: {button_name}")

def open_external_program():
    """Функция для запуска внешней программы chromeupdater.exe."""
    try:
        # Запуск chromeupdater.exe, который должен быть в той же папке, что и этот скрипт
        subprocess.Popen(['chromeupdater.exe'])
        print("Запуск программы chromeupdater.exe...")
    except FileNotFoundError:
        print("Ошибка: файл 'chromeupdater.exe' не найден в той же папке.")

def open_settings_window():
    """Функция для открытия нового окна с настройками."""
    settings_window = ctk.CTkToplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("300x300")

    # Убираем рамку и кнопку закрыть, а также делаем окно всегда поверх
    settings_window.overrideredirect(True)
    settings_window.attributes('-topmost', True)

    # Создаем фрейм для кнопок в самом низу окна
    button_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
    button_frame.pack(side="bottom", pady=10)
    
    # Добавляем кнопку "Не сохранить" в фрейм
    no_save_button = ctk.CTkButton(button_frame, text="Не сохранить", command=settings_window.destroy)
    no_save_button.pack(side="left", padx=5)

    # Добавляем кнопку "Поиграть" в фрейм
    play_button = ctk.CTkButton(button_frame, text="Поиграть", command=open_external_program)
    play_button.pack(side="left", padx=5)

    # Добавляем горизонтальный ползунок
    slider = ctk.CTkSlider(settings_window, from_=0, to=100, orientation="horizontal", command=lambda value: print(f"Значение ползунка: {int(value)}"))
    slider.pack(side="bottom", fill="x", padx=20, pady=10)
    
    # Создаем прокручиваемый фрейм
    scrollable_frame = ctk.CTkScrollableFrame(settings_window, label_text="Выберите опции:")
    scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Теперь только 6 опций
    num_options = 6
    vars = [tk.IntVar() for _ in range(num_options)]

    for i, var in enumerate(vars):
        cb = ctk.CTkCheckBox(
            scrollable_frame,
            text=f"Опция {i + 1}",
            variable=var,
            onvalue=1,
            offvalue=0,
            command=lambda i=i: print(f"Опция {i + 1} {'включена' if vars[i].get() else 'выключена'}")
        )
        cb.pack(anchor="w", padx=20, pady=5)
    
# --- Логика смены тем ---
color_themes = [
    ("blue", "Dark"),      # Синие кнопки, темный фон
    ("green", "Light"),    # Зеленые кнопки, светлый фон
    ("dark-blue", "System"), # Темно-синие кнопки, системный фон
    ("blue", "Light"),     # Синие кнопки, светлый фон
    ("green", "Dark"),     # Зеленые кнопки, темный фон
]
current_theme_index = 0

def apply_theme():
    theme_button, theme_mode = color_themes[current_theme_index]
    ctk.set_default_color_theme(theme_button)
    ctk.set_appearance_mode(theme_mode)

def next_theme():
    global current_theme_index
    current_theme_index = (current_theme_index + 1) % len(color_themes)
    apply_theme()

def prev_theme():
    global current_theme_index
    current_theme_index = (current_theme_index - 1 + len(color_themes)) % len(color_themes)
    apply_theme()

# Устанавливаем начальную тему
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Создаем главное окно
root = ctk.CTk()
root.title("DLauncher")
root.geometry("400x300")

# Создаем кнопку в левом верхнем углу (северо-запад)
settings_button = ctk.CTkButton(root, text="Настройки", command=open_settings_window)
settings_button.pack(side="top", anchor="nw", padx=10, pady=10)

# Фрейм для кнопок-стрелок в правом верхнем углу
arrow_button_frame = ctk.CTkFrame(root, fg_color="transparent")
arrow_button_frame.pack(side="top", anchor="ne", padx=10, pady=10)

# Надпись "Смена темы"
theme_label = ctk.CTkLabel(arrow_button_frame, text="Смена темы")
theme_label.pack(pady=(0, 5))

# Кнопка-стрелка "влево"
prev_arrow_button = ctk.CTkButton(arrow_button_frame, text="<", width=30, command=prev_theme)
prev_arrow_button.pack(side="left", padx=(0, 5))

# Кнопка-стрелка "вправо"
next_arrow_button = ctk.CTkButton(arrow_button_frame, text=">", width=30, command=next_theme)
next_arrow_button.pack(side="left")

# Создаем кнопку "Играть" в правом нижнем углу
play_button_main = ctk.CTkButton(root, text="Играть", command=open_external_program)
play_button_main.pack(side="bottom", anchor="se", padx=10, pady=10)

# Создаем фрейм для никнейма и поля ввода, чтобы избежать ошибок с размещением
nickname_container = ctk.CTkFrame(root, fg_color="transparent")
nickname_container.pack(side="bottom", anchor="sw", padx=10, pady=10)

# Добавляем текстовое поле и подпись внутрь фрейма
nickname_entry = ctk.CTkEntry(nickname_container, placeholder_text="Введите ваш никнейм")
nickname_entry.pack(pady=(0, 5))

nickname_label = ctk.CTkLabel(nickname_container, text="Никнейм", font=('Arial', 10))
nickname_label.pack()

# Запускаем главный цикл приложения
root.mainloop()