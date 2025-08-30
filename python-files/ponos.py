import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def choose_file(entry_widget):
    path = filedialog.askopenfilename()
    if path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)

def choose_folder(entry_widget):
    path = filedialog.askdirectory()
    if path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)

def choose_source():
    choose_file(source_entry)  # For simplicity, initially only allow file selection for source

def choose_destination():
    path = filedialog.askdirectory() # Destination should always be a directory
    if path:
        destination_entry.delete(0, tk.END)
        destination_entry.insert(0, path)

def delete_file():
    path = source_entry.get()
    if not os.path.exists(path):
        messagebox.showwarning("Внимание", "Файл не найден!")
        return
    if not os.path.isfile(path):
        messagebox.showwarning("Внимание", "Это не файл!")
        return

    try:
        os.remove(path)
        messagebox.showinfo("Успех", f"Файл удалён:\n{path}")
        source_entry.delete(0, tk.END)
    except PermissionError:
        messagebox.showerror("Ошибка", "Нет прав для удаления.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить:\n{e}")

def delete_folder():
    path = source_entry.get()
    if not os.path.exists(path):
        messagebox.showwarning("Внимание", "Папка не найдена!")
        return
    if not os.path.isdir(path):
        messagebox.showwarning("Внимание", "Это не папка!")
        return

    try:
        shutil.rmtree(path)
        messagebox.showinfo("Успех", f"Папка удалена:\n{path}")
        source_entry.delete(0, tk.END)
    except PermissionError:
        messagebox.showerror("Ошибка", "Нет прав для удаления.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить:\n{e}")

def combined_delete_path():
    path = source_entry.get()
    if not os.path.exists(path):
        messagebox.showwarning("Внимание", "Файл или папка не найдены!")
        return

    if os.path.isfile(path):
        delete_file()
    elif os.path.isdir(path):
        delete_folder()
    else:
        messagebox.showwarning("Внимание", "Указанный путь не является ни файлом, ни папкой!")

def transfer_path():
    source_path = source_entry.get()
    destination_path = destination_entry.get()

    if not os.path.exists(source_path):
        messagebox.showwarning("Внимание", "Исходный файл или папка не найдены!")
        return

    try:
        shutil.move(source_path, destination_path)
        messagebox.showinfo("Успех", f"Перемещено:\n{source_path}\nв\n{destination_path}")
        source_entry.delete(0, tk.END)
        destination_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось переместить:\n{e}")

# окно программы
root = tk.Tk()
root.title("Удаление файлов и папок")
root.geometry("450x400")

# поля ввода пути
source_label = tk.Label(root, text="Исходный путь:")
source_label.pack(pady=2)
source_entry = tk.Entry(root, width=60)
source_entry.pack(pady=2)

destination_label = tk.Label(root, text="Целевой путь:")
destination_label.pack(pady=2)
destination_entry = tk.Entry(root, width=60)
destination_entry.pack(pady=2)

# кнопки
btn_choose_file = tk.Button(root, text="Выбрать файл", command=choose_source, fg="white", bg="gray")
btn_choose_file.pack(pady=5)

btn_choose_folder = tk.Button(root, text="Выбрать папку", command=choose_destination, fg="white", bg="gray")
btn_choose_folder.pack(pady=5)

btn_delete = tk.Button(root, text="Удалить", command=combined_delete_path, fg="white", bg="red")
btn_delete.pack(pady=5)

btn_transfer = tk.Button(root, text="Переместить", command=transfer_path, fg="white", bg="blue")
btn_transfer.pack(pady=5)

root.mainloop()