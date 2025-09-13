import os
import shutil
import re
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматическая сортировка файлов")
        self.root.geometry("600x300")

        # Переменная для хранения пути к папке
        self.folder_path = ""

        # Создаем элементы интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Автоматическая сортировка файлов",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Кнопка выбора папки
        select_folder_btn = tk.Button(self.root, text="Выбрать папку для сортировки",
                                      command=self.select_folder, bg="lightblue",
                                      font=("Arial", 12), height=1, width=25)
        select_folder_btn.pack(pady=10)

        # Метка для отображения выбранной папки
        self.folder_label = tk.Label(self.root, text="Папка не выбрана",
                                     wraplength=500, justify="center")
        self.folder_label.pack(pady=5)

        # Кнопка сортировки
        self.sort_button = tk.Button(self.root, text="Сортировать", command=self.start_sorting,
                                     bg="green", fg="white", font=("Arial", 14),
                                     height=2, width=20, state="disabled")
        self.sort_button.pack(pady=20)

        # Статус
        self.status_label = tk.Label(self.root, text="Выберите папку для сортировки", fg="blue")
        self.status_label.pack()

    def select_folder(self):
        """Выбор папки для сортировки"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.folder_label.config(text=f"Выбрана папка: {folder_selected}")
            self.sort_button.config(state="normal")
            self.status_label.config(text="Готов к сортировке", fg="blue")

    def start_sorting(self):
        """Запуск процесса сортировки"""
        if not self.folder_path:
            messagebox.showerror("Ошибка", "Сначала выберите папку для сортировки!")
            return

        self.status_label.config(text="Идет сортировка...", fg="orange")
        self.root.update()

        try:
            result = self.auto_organize_files(self.folder_path)
            self.status_label.config(text=result, fg="green")
            messagebox.showinfo("Готово", result)
        except Exception as e:
            self.status_label.config(text="Ошибка!", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def find_existing_folder(self, search_root, folder_name):
        """
        Ищет папку с заданным именем в указанной директории и всех поддиректориях
        """
        for root, dirs, files in os.walk(search_root):
            if folder_name in dirs:
                return os.path.join(root, folder_name)
        return None

    def auto_organize_files(self, source_folder):
        """
        Автоматически сортирует Word-документы по номерам маршрутов
        с поддержкой буквенных обозначений и поиском существующих папок
        """
        # Получаем все Word-документы
        self.status_label.config(text="Поиск Word-документов...")
        self.root.update()

        word_files = []
        for ext in ["*.doc", "*.docx"]:
            word_files.extend(list(Path(source_folder).glob(ext)))
            # Также ищем файлы в подпапках
            word_files.extend(list(Path(source_folder).rglob(ext)))

        # Убираем дубликаты
        word_files = list(set(word_files))

        print(f"Найдено {len(word_files)} Word-документов")

        # Статистика обработки
        processed_count = 0
        error_count = 0
        skipped_count = 0

        # Обрабатываем каждый файл
        for file_path in word_files:
            try:
                # Извлекаем номер маршрута из имени файла
                filename = file_path.stem  # Имя файла без расширения
                print(f"Обрабатываем файл: {filename}")

                # Используем улучшенное регулярное выражение для извлечения номера маршрута
                # Поддерживает буквы и цифры: НС_551_01.09.2025 или НС_с9_01.09.2025
                match = re.search(r'_([a-zA-Zа-яА-Я0-9]+)_', filename)
                if match:
                    route_number = match.group(1)
                    print(f"Найден номер маршрута: {route_number}")

                    # Ищем существующую папку с таким именем
                    target_folder = self.find_existing_folder(source_folder, route_number)

                    # Если папка не найдена, создаем новую в корневой папке
                    if target_folder is None:
                        target_folder = os.path.join(source_folder, route_number)
                        os.makedirs(target_folder, exist_ok=True)
                        print(f"Создана новая папка: {route_number}")
                    else:
                        print(f"Найдена существующая папка: {target_folder}")

                    # Проверяем, не пытаемся ли переместить файл в ту же папку
                    if os.path.dirname(file_path) == target_folder:
                        print(f"Файл уже находится в целевой папке: {file_path.name}")
                        skipped_count += 1
                        continue

                    # Перемещаем файл в целевую папку
                    target_path = os.path.join(target_folder, file_path.name)
                    shutil.move(str(file_path), target_path)

                    print(f"Перемещен: {file_path.name} -> папка {route_number}")
                    processed_count += 1
                else:
                    print(f"Не удалось найти номер маршрута: {filename}")
                    error_count += 1

            except Exception as e:
                print(f"Ошибка при обработке файла {file_path.name}: {str(e)}")
                error_count += 1

        # Формируем сообщение о результатах
        result_message = f"Обработка завершена!\nУспешно обработано: {processed_count} файлов\nПропущено: {skipped_count} файлов\nОшибок: {error_count}"
        return result_message


# Создаем исполняемый файл
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()