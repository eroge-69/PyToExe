import tkinter as tk
from tkinter import Toplevel, Label, Button

def on_button_click():
    text = entry.get()  # Получаем текст из поля ввода
    
    # Создаем свое большое окно вместо messagebox
    age_window = Toplevel(window)
    age_window.title("Твой возраст")
    age_window.geometry("600x300")  # Большой размер окна
    age_window.configure(bg='white')
    
    # Центрируем окно относительно главного
    age_window.transient(window)
    age_window.grab_set()
    
    # Создаем метку с большим текстом
    label = Label(
        age_window, 
        text=f"Тебе: {text} лет", 
        font=("Arial", 24),
        bg='white',
        fg='darkblue'
    )
    label.pack(pady=50)
    
    # Кнопка закрытия окна
    close_button = Button(
        age_window, 
        text="Закрыть", 
        command=age_window.destroy,
        font=("Arial", 16),
        width=15,
        height=2
    )
    close_button.pack(pady=20)
    
    entry.delete(0, tk.END)  # Очищаем поле после получения

# Создаем главное окно
window = tk.Tk()
window.title("Сколько тебе лет?")
window.geometry("800x400")

# Создаем поле ввода
entry = tk.Entry(window, width=50, font=("Arial", 20))
entry.pack(pady=20)

# НЕИЗМЕНЯЕМЫЙ ТЕКСТ - метка
static_text = tk.Label(
    window, 
    text="Введите ваш возраст:",  # Текст который нельзя изменить
    font=("Arial", 16),           # Шрифт
    fg="darkblue",                # Цвет текста
    bg="lightgray"               # Цвет фона
)
static_text.pack(pady=20)
static_text = tk.Label(
    window, 
    text="BY Antontop8742 (не гудбист):",  # Текст который нельзя изменить
    font=("Arial", 16),           # Шрифт
    fg="darkblue",                # Цвет текста
    bg="lightgray"               # Цвет фона
)
static_text.pack(pady=20)

# Создаем кнопку
button = tk.Button(
    window, 
    text="Получить ответ", 
    command=on_button_click,
    font=("Arial", 16),
    width=20,
    height=2
)
button.pack(pady=20)

# Запускаем программу
window.mainloop()