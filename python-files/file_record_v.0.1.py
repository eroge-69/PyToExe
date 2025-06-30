import os
import shutil
from tkinter import Tk, filedialog

def select_file(title="Выберите файл"):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title)
    root.destroy()
    return file_path

def select_folder(title="Выберите папку"):
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_path

def distribute_file_to_textures_folders(file_path, root_folder):
    """
    Ищет все папки с именем 'Textures' в указанной директории и её поддиректориях,
    и копирует в каждую из них указанный файл (с заменой, если уже есть).
    """
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if os.path.basename(dirpath) == "Textures":
            dest_file = os.path.join(dirpath, os.path.basename(file_path))
            shutil.copy2(file_path, dest_file)
            print(f"Скопировано в: {dest_file}")

if __name__ == "__main__":
    file_path = select_file("Выберите файл для копирования")
    if not file_path:
        print("Файл не выбран.")
        exit(1)
    root_folder = select_folder("Выберите корневую папку для распределения файла")
    if not root_folder:
        print("Папка не выбрана.")
        exit(1)
    distribute_file_to_textures_folders(file_path, root_folder)
    print("Готово!")