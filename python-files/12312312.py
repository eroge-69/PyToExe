import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import pyperclip

# Функция для сокращения ссылки
def shorten_url(url):
    try:
        response = requests.get(f"https://clck.ru/--?url={url}")
        if response.status_code == 200:
            return response.text  # Получаем сокращённую ссылку
        else:
            raise Exception("Не удалось сократить ссылку")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return None

# Функция для обработки ссылок из файла
def process_file():
    file_path = filedialog.askopenfilename(title="Выберите файл с ссылками", filetypes=[("Text files", "*.txt")])
    if not file_path:
        return

    try:
        with open(file_path, 'r') as file:
            urls = file.readlines()
        
        shortened_urls = []
        for url in urls:
            url = url.strip()  # Удаляем пробелы и символы новой строки
            if url:
                shortened_url = shorten_url(url)
                if shortened_url:
                    shortened_urls.append(shortened_url)

        # Записываем сокращённые ссылки в output.txt
        with open('output.txt', 'w') as output_file:
            for shortened_url in shortened_urls:
                output_file.write(shortened_url + '\n')

        messagebox.showinfo("Успех", "Сокращённые ссылки записаны в файл output.txt")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Функция для копирования сокращённой ссылки
def copy_to_clipboard():
    shortened_url = entry_shortened.get()  # Получаем сокращённую ссылку из поля
    if shortened_url:
        pyperclip.copy(shortened_url)  # Копируем в буфер обмена
        messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
    else:
        messagebox.showerror("Ошибка", "Нет ссылки для копирования")

# Создание графического интерфейса
root = tk.Tk()
root.title("Сократитель ссылок")

# Поле для ввода ссылки
tk.Label(root, text="Введите ссылку:").pack()
entry_url = tk.Entry(root, width=50)
entry_url.pack()

# Кнопка для сокращения ссылки
btn_shorten = tk.Button(root, text="Сократить", command=lambda: shorten_url(entry_url.get()))
btn_shorten.pack()

# Поле для отображения сокращённой ссылки
tk.Label(root, text="Сокращённая ссылка:").pack()
entry_shortened = tk.Entry(root, width=50)
entry_shortened.pack()

# Кнопка для копирования
btn_copy = tk.Button(root, text="Копировать", command=copy_to_clipboard)
btn_copy.pack()

# Кнопка для обработки файла
btn_process_file = tk.Button(root, text="Обработать файл", command=process_file)
btn_process_file.pack()

# Запуск приложения
root.mainloop()