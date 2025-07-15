import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkbs

class FolderCreatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Folder Structure Creator")
        self.config_file = os.path.join(os.path.dirname(__file__), "folder_creator.cfg")
        self.default_geometry = "600x500"

        # Инициализация переменных до загрузки настроек
        self.work_folder = tk.StringVar()
        self.project_name = tk.StringVar()
        self.input_fields = []

        # Загрузка настроек
        self.load_settings()

        # Создание элементов интерфейса
        self.create_widgets()

        # Обработчик закрытия окна
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        style = ttkbs.Style()

        # Выбор рабочей папки
        ttk.Label(self.master, text="Рабочая папка:").pack(pady=5)
        folder_frame = ttk.Frame(self.master)
        folder_frame.pack(fill=tk.X, padx=10)

        ttk.Entry(folder_frame, textvariable=self.work_folder, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            folder_frame,
            text="Выбрать...",
            command=self.select_folder,
            style="primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Имя проекта
        ttk.Label(self.master, text="Имя проекта:").pack(pady=5)
        ttk.Entry(self.master, textvariable=self.project_name).pack(fill=tk.X, padx=10)

        # Динамические поля ввода
        ttk.Label(self.master, text="Подпапки:").pack(pady=5)

        # Контейнер с прокруткой
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка добавления полей
        ttk.Button(
            self.master,
            text="Добавить подпапку",
            command=self.add_input_field,
            style="success.TButton"
        ).pack(pady=5)

        # Кнопка создания структуры
        ttk.Button(
            self.master,
            text="Создать структуру папок",
            command=self.create_structure,
            style="info.TButton"
        ).pack(side=tk.BOTTOM, pady=10)

        # Добавляем сохраненные подпапки
        self.restore_input_fields()

    def restore_input_fields(self):
        # Очищаем существующие поля перед восстановлением
        for entry in self.input_fields:
            entry.master.destroy()
        self.input_fields.clear()

        # Добавляем поля из конфига
        if hasattr(self, 'saved_subfolders'):
            for folder in self.saved_subfolders:
                self.add_input_field()
                self.input_fields[-1].insert(0, folder)

    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Восстанавливаем геометрию окна
                self.master.geometry(config.get('geometry', self.default_geometry))

                # Сохраняем подпапки для последующего восстановления
                self.saved_subfolders = config.get('subfolders', [])

                # Устанавливаем значение рабочей папки
                self.work_folder.set(config.get('work_folder', ''))

        except Exception as e:
            print(f"Ошибка загрузки настроек: {str(e)}")

    def save_settings(self):
        config = {
            'geometry': self.master.geometry(),
            'work_folder': self.work_folder.get(),
            'subfolders': [entry.get() for entry in self.input_fields if entry.get().strip()]
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")

    def on_close(self):
        self.save_settings()
        self.master.destroy()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.work_folder.set(folder)

    def add_input_field(self):
        frame = ttk.Frame(self.scroll_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)

        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        btn_remove = ttk.Button(
            frame,
            text="×",
            command=lambda: self.remove_input_field(frame),
            style="danger.TButton",
            width=2
        )
        btn_remove.pack(side=tk.RIGHT)

        self.input_fields.append(entry)

    def remove_input_field(self, frame):
        for entry in self.input_fields:
            if entry.winfo_parent() == frame.winfo_id():
                self.input_fields.remove(entry)
                break
        frame.destroy()

    def create_structure(self):
        work_dir = self.work_folder.get()
        project = self.project_name.get()

        if not work_dir or not project:
            messagebox.showerror("Ошибка", "Укажите рабочую папку и имя проекта!")
            return

        folders = [entry.get() for entry in self.input_fields if entry.get().strip()]
        if not folders:
            messagebox.showerror("Ошибка", "Добавьте хотя бы одну подпапку!")
            return

        project_path = os.path.join(work_dir, project)

        try:
            os.makedirs(project_path, exist_ok=False)
            for folder in folders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path)

            messagebox.showinfo("Успех", f"Структура папок успешно создана в:\n{project_path}")
        except FileExistsError:
            messagebox.showerror("Ошибка", "Папка проекта уже существует!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании папок:\n{str(e)}")

if __name__ == "__main__":
    root = ttkbs.Window(themename="minty")
    app = FolderCreatorApp(root)
    root.mainloop()
