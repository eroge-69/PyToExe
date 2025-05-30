import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def rename_folders():
    # Запрос начального числа
    start_num = simpledialog.askinteger("Начальное число", "Введите начальное число:", minvalue=1, initialvalue=21)
    if start_num is None:  # Если нажали "Отмена"
        return

    # Выбор папки
    folder_path = filedialog.askdirectory(title="Выберите папку")
    if not folder_path:
        return

    try:
        # Получаем список папок и сортируем их по имени (как числа)
        folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        
        # Сортируем папки как числа (если они состоят из цифр)
        folders.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
        
        # Переименовываем в порядке возрастания
        for i, folder in enumerate(folders, start_num):
            old_path = os.path.join(folder_path, folder)
            new_path = os.path.join(folder_path, str(i))
            os.rename(old_path, new_path)
            
        messagebox.showinfo("Готово!", f"Переименовано {len(folders)} папок (с {start_num}).")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

root = tk.Tk()
root.title("Переименование папок")
tk.Button(root, text="Выбрать папку", command=rename_folders).pack(pady=20)
root.mainloop()