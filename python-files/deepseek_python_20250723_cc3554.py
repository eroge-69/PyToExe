import os
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_time(time_str):
    """Преобразует строку времени в секунды"""
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 3:  # HH:MM:SS
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:  # MM:SS
        return parts[0] * 60 + parts[1]
    else:  # SS
        return parts[0]

def calculate_total_duration():
    """Вычисляет общую длительность"""
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning("Предупреждение", "Список файлов пуст!")
        return
    
    total_seconds = 0
    
    for file_path in files:
        try:
            filename = os.path.basename(file_path)
            time_str = filename.split('_')[-1].split('.')[0]  # предполагаем формат NAME_HH-MM-SS.ext
            seconds = parse_time(time_str.replace('-', ':'))
            total_seconds += seconds
        except (IndexError, ValueError):
            messagebox.showerror("Ошибка", f"Неверный формат времени в файле: {filename}")
            return
    
    # Преобразуем секунды в часы, минуты, секунды
    total_time = timedelta(seconds=total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    result_label.config(text=f"Общая длительность: {hours} ч. {minutes} мин. {seconds} сек.\n"
                            f"Или: {total_time} (HH:MM:SS)")

def add_files():
    """Добавляет файлы в список"""
    files = filedialog.askopenfilenames(title="Выберите видеофайлы")
    if files:
        for file in files:
            file_list.insert(tk.END, file)

def clear_list():
    """Очищает список файлов"""
    file_list.delete(0, tk.END)
    result_label.config(text="Общая длительность: 0 ч. 0 мин. 0 сек.")

# Создаем главное окно
root = tk.Tk()
root.title("Калькулятор длительности видео")
root.geometry("600x400")

# Фрейм для списка файлов
frame = tk.Frame(root)
frame.pack(pady=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

file_list = tk.Listbox(frame, width=70, height=15, yscrollcommand=scrollbar.set)
file_list.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar.config(command=file_list.yview)

# Фрейм для кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Добавить файлы", command=add_files)
add_button.pack(side=tk.LEFT, padx=5)

calculate_button = tk.Button(button_frame, text="Рассчитать", command=calculate_total_duration)
calculate_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(button_frame, text="Очистить", command=clear_list)
clear_button.pack(side=tk.LEFT, padx=5)

# Метка для результата
result_label = tk.Label(root, text="Общая длительность: 0 ч. 0 мин. 0 сек.", font=('Arial', 12))
result_label.pack(pady=10)

# Инструкция
instruction = tk.Label(root, text="Формат имени файла: NAME_HH-MM-SS.ext\nНапример: video_01-23-45.mp4", font=('Arial', 10))
instruction.pack(pady=5)

root.mainloop()