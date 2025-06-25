import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os  # Импортируем модуль os


def search_in_file():
    file_path_value = file_path.get()
    search_term = search_entry.get()

    if not file_path_value or not search_term:
        messagebox.showerror("Ошибка", "Пожалуйста, укажите файл и слово для поиска.")
        return

    try:
        results = []
        with open(file_path_value, 'r', encoding='utf-8') as file:
            for line in file:
                if search_term in line:
                    results.append(line.strip())

        if results:
            df = pd.DataFrame(results, columns=["Результаты"])
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                     filetypes=[("Excel files", "*.xlsx"),
                                                                ("All files", "*.*")])
            if save_path:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("Успех", "Результаты успешно сохранены в файл.")

                # Открываем папку, где сохранен файл
                folder_path = os.path.dirname(save_path)  # Получаем путь к папке
                os.startfile(folder_path)  # Открываем папку (работает только на Windows)

        else:
            messagebox.showinfo("Результат", "Совпадений не найдено.")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def browse_file():
    file_path_value = filedialog.askopenfilename(
        filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")])
    file_path.delete(0, tk.END)  # Очистка поля ввода
    file_path.insert(0, file_path_value)  # Вставка выбранного пути в поле ввода


root = tk.Tk()
root.title("Поиск в файлах")

tk.Label(root, text="Выберите файл:").pack(pady=5)
file_path = tk.Entry(root, width=50)
file_path.pack(pady=5)

tk.Button(root, text="Обзор", command=browse_file).pack(pady=5)

tk.Label(root, text="Введите слово для поиска:").pack(pady=5)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

tk.Button(root, text="Поиск", command=search_in_file).pack(pady=5)

root.mainloop()
