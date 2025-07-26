import os
import random
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

class HitsoundRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hitsound Renamer for osu!")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Основные переменные
        self.folder_path_var = tk.StringVar()
        self.max_size_var = tk.StringVar(value="190")  # По умолчанию 190 КБ
        self.log_text = tk.StringVar()

        # Создаем основные фреймы
        self.create_frames()
        self.create_widgets()

        # Словарь соответствий типов звуков
        self.sound_mapping = {
            "normal-hitnormal": ["kick", "bass"],
            "normal-hitwhistle": ["snare", "snap"],
            "normal-hitclap": ["clap", "hit"],
            "normal-hitfinish": ["cymbal", "finish"]
        }

        # Список категорий
        self.categories = ["normal", "soft", "drum"]

    def create_frames(self):
        """Создаем основные фреймы для группировки элементов."""
        self.header_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        self.header_frame.pack(fill="x")

        self.input_frame = tk.Frame(self.root, pady=10, bg="#ffffff")
        self.input_frame.pack(fill="x", padx=20)

        self.progress_frame = tk.Frame(self.root, pady=10, bg="#ffffff")
        self.progress_frame.pack(fill="x", padx=20)

        self.log_frame = tk.Frame(self.root, pady=10, bg="#ffffff")
        self.log_frame.pack(fill="both", expand=True, padx=20)

        self.footer_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        self.footer_frame.pack(fill="x", side="bottom")

    def create_widgets(self):
        """Создаем виджеты интерфейса."""
        # Заголовок
        title_label = tk.Label(self.header_frame, text="Hitsound Renamer for osu!", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack()

        # Выбор папки
        folder_label = tk.Label(self.input_frame, text="1. Выберите целевую папку:", font=("Arial", 10), bg="#ffffff")
        folder_label.grid(row=0, column=0, sticky="w", pady=5)

        folder_entry = tk.Entry(self.input_frame, textvariable=self.folder_path_var, width=50, state="readonly", relief="flat", bg="#f9f9f9")
        folder_entry.grid(row=0, column=1, pady=5)

        browse_button = tk.Button(self.input_frame, text="Обзор...", command=self.browse_folder, bg="#4CAF50", fg="white", relief="flat")
        browse_button.grid(row=0, column=2, padx=10, pady=5)

        # Максимальный размер файла
        max_size_label = tk.Label(self.input_frame, text="2. Максимальный размер файла (КБ):", font=("Arial", 10), bg="#ffffff")
        max_size_label.grid(row=1, column=0, sticky="w", pady=5)

        max_size_entry = tk.Entry(self.input_frame, textvariable=self.max_size_var, width=10, relief="flat", bg="#f9f9f9")
        max_size_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Кнопка запуска
        rename_button = tk.Button(self.input_frame, text="Создать полный набор звуков", command=self.create_full_soundset, bg="#008CBA", fg="white", relief="flat", width=30)
        rename_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=660, mode="determinate")
        self.progress_bar.pack()

        # Логирование
        log_label = tk.Label(self.log_frame, text="Лог выполнения:", font=("Arial", 10), bg="#ffffff")
        log_label.pack(anchor="w", pady=5)

        self.log_box = tk.Text(self.log_frame, height=10, width=80, wrap="word", bg="#f9f9f9", relief="flat", state="disabled")
        self.log_box.pack(fill="both", expand=True)

        # Кнопка открытия папки вывода
        open_output_button = tk.Button(self.footer_frame, text="Открыть папку вывода", command=self.open_output_folder, bg="#FF9800", fg="white", relief="flat")
        open_output_button.pack(side="left", padx=10)

        # Футер с ссылкой
        footer_label = tk.Label(self.footer_frame, text="By xsa4", font=("Arial", 8, "underline"), bg="#f0f0f0", fg="blue", cursor="hand2")
        footer_label.pack(side="right", padx=10)
        footer_label.bind("<Button-1>", lambda e: webbrowser.open("https://osu.ppy.sh/users/9835274"))

    def browse_folder(self):
        """Выбор целевой папки."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)

    def get_max_size_bytes(self):
        """Получаем максимальный размер файла в байтах."""
        try:
            max_size_kb = int(self.max_size_var.get())
            return max_size_kb * 1024  # Переводим в байты
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректный максимальный размер файла в КБ.")
            return None

    def log_message(self, message):
        """Добавляем сообщение в лог."""
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def open_output_folder(self):
        """Открываем папку вывода."""
        target_folder = self.folder_path_var.get()
        if not target_folder:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите целевую папку.")
            return

        output_folder = os.path.join(target_folder, "full_soundset")
        if not os.path.exists(output_folder):
            messagebox.showinfo("Информация", "Папка вывода еще не создана.")
            return

        os.startfile(output_folder)

    def create_full_soundset(self):
        """Основная функция создания полного набора звуков."""
        target_folder = self.folder_path_var.get()
        if not target_folder:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите целевую папку.")
            return

        max_size_bytes = self.get_max_size_bytes()
        if max_size_bytes is None:
            return

        # Очищаем лог
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        # Получаем список подпапок
        subfolders = [f for f in os.listdir(target_folder) if os.path.isdir(os.path.join(target_folder, f))]
        if not subfolders:
            messagebox.showinfo("Информация", "В целевой папке нет подпапок.")
            return

        # Создаем выходную папку
        output_folder = os.path.join(target_folder, "full_soundset")
        os.makedirs(output_folder, exist_ok=True)

        success_count = 0
        failed_count = 0

        # Шаг 1: Находим файлы для категории "normal"
        normal_files = {}
        total_tasks = len(self.sound_mapping)
        current_task = 0

        for osu_name, keywords in self.sound_mapping.items():
            matching_files = []
            for subfolder in subfolders:
                subfolder_path = os.path.join(target_folder, subfolder)
                files = [f for f in os.listdir(subfolder_path) if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
                for file in files:
                    file_path = os.path.join(subfolder_path, file)
                    file_size = os.path.getsize(file_path)

                    # Проверяем размер файла
                    if file_size > max_size_bytes:
                        self.log_message(f"Файл {file} слишком большой ({file_size / 1024:.2f} КБ). Пропускаем.")
                        continue

                    base_name, _ = os.path.splitext(file)
                    if any(keyword.lower() in base_name.lower() for keyword in keywords):
                        matching_files.append(file_path)

            if not matching_files:
                self.log_message(f"Файлы для {osu_name} не найдены.")
                failed_count += 1
                continue

            # Выбираем случайный файл
            random_file = random.choice(matching_files)
            normal_files[osu_name] = random_file

            # Обновляем прогресс-бар
            current_task += 1
            self.progress_bar["value"] = (current_task / total_tasks) * 100
            self.root.update_idletasks()

        # Шаг 2: Копируем и переименовываем файлы для всех категорий
        total_tasks = len(normal_files) * len(self.categories)
        current_task = 0

        for category in self.categories:
            category_folder = os.path.join(output_folder, category)
            os.makedirs(category_folder, exist_ok=True)

            for osu_name, normal_file in normal_files.items():
                try:
                    # Формируем новое имя файла
                    base_name, ext = os.path.splitext(os.path.basename(normal_file))
                    new_name = f"{category}-{osu_name.split('-')[-1]}{ext}"
                    output_file = os.path.join(category_folder, new_name)

                    # Копируем файл
                    shutil.copy(normal_file, output_file)
                    success_count += 1
                    self.log_message(f"Создан файл: {output_file}")
                except Exception as e:
                    self.log_message(f"Ошибка при обработке файла {normal_file}: {e}")
                    failed_count += 1

                # Обновляем прогресс-бар
                current_task += 1
                self.progress_bar["value"] = (current_task / total_tasks) * 100
                self.root.update_idletasks()

        result_message = f"Обработано: {success_count}\nНе удалось обработать: {failed_count}"
        messagebox.showinfo("Готово", result_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = HitsoundRenamerApp(root)
    root.mainloop()