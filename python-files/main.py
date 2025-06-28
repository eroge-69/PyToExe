import tkinter as tk
from tkinter import ttk, messagebox

# Функции
def open_references():
    messagebox.showinfo("Справочники", "Функция открытия справочников активирована")

def add_achievement():
    messagebox.showinfo("Добавление достижения", "Функция добавления достижения активирована")

def about_app():
    messagebox.showinfo("О программе", "АИС система учета и мониторинга достижений\nВерсия 1.0")

# Создание основного окна
root = tk.Tk()
root.title("АИС система учета и мониторинга достижений")
root.geometry("600x400")
root.configure(bg='#d9d9d9')

# Стилизация кнопок
style = ttk.Style()
style.configure('TButton', font=('Arial', 12), padding=10, background='#f0f0f0')

# Приветственная надпись
welcome_label = tk.Label(
    root, 
    text="Добро пожаловать в АИС система учета и мониторинга достижений\nв образовательном учреждении",
    font=('Arial', 14, 'bold'),
    bg='#d9d9d9',
    pady=20,
    justify=tk.CENTER
)
welcome_label.pack(pady=20)

# Рамка для кнопок
button_frame = ttk.Frame(root)
button_frame.pack(pady=20)

# Кнопка "Справочники"
references_btn = ttk.Button(
    button_frame,
    text="Справочники",
    command=open_references
)
references_btn.pack(side=tk.LEFT, padx=20)

# Кнопка "Внести данные о достижении"
add_achievement_btn = ttk.Button(
    button_frame,
    text="Внести данные о достижении",
    command=add_achievement
)
add_achievement_btn.pack(side=tk.LEFT, padx=20)

# Запуск основного цикла
root.mainloop()
