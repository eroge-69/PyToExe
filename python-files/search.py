import os
import tkinter as tk
from tkinter import filedialog, messagebox

class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск файлов")
        self.create_widgets()

    def create_widgets(self):
        self.path_label = tk.Label(self.root, text="Папка:")
        self.path_label.pack(pady=5, anchor='w')

        frame = tk.Frame(self.root)
        frame.pack(fill='x', pady=5)

        self.path_entry = tk.Entry(frame)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=5)

        self.browse_button = tk.Button(frame, text="Обзор", command=self.browse_folder)
        self.browse_button.pack(side='right', padx=5)

        self.search_label = tk.Label(self.root, text="Имя файла для поиска:")
        self.search_label.pack(pady=5, anchor='w')

        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack(fill='x', padx=5)

        self.search_button = tk.Button(self.root, text="Искать", command=self.search_files)
        self.search_button.pack(pady=10)

        self.results_box = tk.Listbox(self.root, height=15)
        self.results_box.pack(fill='both', expand=True, padx=5, pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def search_files(self):
        folder = self.path_entry.get()
        term = self.search_entry.get()
        self.results_box.delete(0, tk.END)

        if not folder or not term:
            messagebox.showwarning("Ошибка", "Пожалуйста, укажите папку и имя файла.")
            return

        for root_dir, dirs, files in os.walk(folder):
            for file in files:
                if term.lower() in file.lower():
                    full_path = os.path.join(root_dir, file)
                    self.results_box.insert(tk.END, full_path)

        if self.results_box.size() == 0:
            self.results_box.insert(tk.END, "Файлы не найдены.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(root)
    root.geometry("700x400")
    root.mainloop()