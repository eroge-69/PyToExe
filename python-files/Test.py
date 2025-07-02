import tkinter as tk
from tkinter import messagebox
from win10toast import ToastNotifier

def show_notification():
    user_input = entry.get()
    if user_input.strip() == "":
        messagebox.showwarning("Предупреждение", "Пожалуйста, введите текст для уведомления!")
    else:
        # Создаем объект для уведомлений
        toaster = ToastNotifier()
        # Показываем уведомление
        toaster.show_toast(
            "Уведомление",  # Заголовок
            user_input,    # Текст уведомления
            duration=5,     # Длительность отображения (в секундах)
            threaded=True   # Потоковое уведомление (не блокирует программу)
        )
        # Очищаем поле ввода
        entry.delete(0, tk.END)

# Создаем главное окно
root = tk.Tk()
root.title("Уведомления в Windows 10")
root.geometry("400x200")

# Надпись
label = tk.Label(root, text="Введите текст для уведомления:", font=("Arial", 12))
label.pack(pady=10)

# Поле ввода
entry = tk.Entry(root, width=40, font=("Arial", 12))
entry.pack(pady=10)

# Кнопка для создания уведомления
button = tk.Button(root, text="Показать уведомление", command=show_notification, font=("Arial", 12))
button.pack(pady=20)

# Запускаем главный цикл
root.mainloop()