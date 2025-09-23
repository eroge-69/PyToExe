import os
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox

# Функция для повреждения файла
def corrupt_file(file_path):
    try:
        with open(file_path, 'r+b') as f:
            file_content = f.read()
            corrupt_content = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=len(file_content)))
            f.seek(0)
            f.write(corrupt_content.encode())
            f.truncate()  # Ensure the file size remains the same
        print(f"Файл {file_path} поврежден.")
    except Exception as e:
        print(f"Ошибка: {e}")

# Функция для обработки выбранной папки
def select_folder():
    folder_path = filedialog.askdirectory()  # Открыть диалоговое окно для выбора папки
    if folder_path:
        folder_label.config(text=f"Выбрана папка: {folder_path}")
        process_button.config(state=tk.NORMAL, command=lambda: process_folder(folder_path))
    else:
        folder_label.config(text="Папка не выбрана")

# Функция для обработки всех файлов в папке
def process_folder(folder_path):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                corrupt_file(file_path)
        messagebox.showinfo("Готово", "Все файлы в папке были повреждены.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Создание главного окна приложения
root = tk.Tk()
root.title("Повреждение файлов")

# Создание виджетов
select_button = tk.Button(root, text="Выбрать папку", command=select_folder)
select_button.pack(pady=10)

folder_label = tk.Label(root, text="Папка не выбрана", width=50)
folder_label.pack(pady=5)

process_button = tk.Button(root, text="Повредить файлы", state=tk.DISABLED)
process_button.pack(pady=20)

# Запуск основного цикла приложения
root.mainloop()
