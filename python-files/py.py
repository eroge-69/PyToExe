import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import threading
import datetime
import subprocess

class FileSearchTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Инструмент поиска и удаления файлов")
        self.root.geometry("425x410")
        self.root.resizable(False, False) # Запрет изменения размера

        # --- Элементы управления ---
        # 1. Поле ввода "Имя папки"
        self.label_path = ttk.Label(root, text="Имя папки:")
        self.label_path.place(x=10, y=10)
        self.entry_path = ttk.Entry(root, width=50)
        self.entry_path.place(x=10, y=30)

        # 1.1 Кнопка "Проверить"
        self.button_check = ttk.Button(root, text="Проверить", command=self.check_path)
        self.button_check.place(x=325, y=4)


        # 2. Поле ввода "Имена файлов"
        self.label_files = ttk.Label(root, text="Имена файлов (через ';' без пробела):")
        self.label_files.place(x=10, y=60)
        self.entry_files = ttk.Entry(root, width=50)
        self.entry_files.place(x=10, y=80)

        # 3. Список найденных файлов и кнопки
        self.label_found_files = ttk.Label(root, text="Найденные файлы:")
        self.label_found_files.place(x=10, y=120)
        self.button_clear = ttk.Button(root, text="Очистить", command=self.clear_listbox)
        self.button_clear.place(x=325, y=110)

        self.listbox_files = tk.Listbox(root, width=52, height=10, font=("Arial", 9))  # Уменьшенная высота для соответствия интерфейсу
        self.listbox_files.place(x=10, y=140)
        self.listbox_files.config(exportselection=False)  #  Предотвращение сброса выделения при переключении между виджетами

        self.button_report = ttk.Button(root, text="Отчет", command=self.create_report)
        self.button_report.place(x=240, y=110)


        # 4. Кнопки управления
        self.button_search = ttk.Button(root, text="Поиск", command=self.search_files)
        self.button_search.place(x=10, y=320)
        self.button_open_folder = ttk.Button(root, text="Открыть папку", command=self.open_folder, state=tk.DISABLED)
        self.button_open_folder.place(x=100, y=320)
        self.button_delete = ttk.Button(root, text="Удалить", command=self.delete_file, state=tk.DISABLED)
        self.button_delete.place(x=220, y=320)
        self.button_delete_all = ttk.Button(root, text="Удалить всё", command=self.delete_all_files, state=tk.DISABLED)
        self.button_delete_all.place(x=300, y=320)

        # Label с информацией
        self.form_label = ttk.Label(root, text="Если не указать папку, будет искать в папке где лежит сам файл F-D")
        self.form_label.place(x=15, y=350)


    # --- Функции-обработчики ---
    def check_path(self):
        path = self.entry_path.get()
        if os.path.exists(path):
            messagebox.showinfo("Проверка", "ПК доступен")
        else:
            messagebox.showerror("Проверка", "ПК недоступен")

    def search_files(self):
        self.root.title("Выполняется поиск...")
        self.listbox_files.delete(0, tk.END)
        files = self.entry_files.get().split(";")
        path = self.entry_path.get()

        self.button_search.config(state=tk.DISABLED)
        self.button_open_folder.config(state=tk.DISABLED)
        self.button_delete.config(state=tk.DISABLED)
        self.button_delete_all.config(state=tk.DISABLED)

        def search_thread():
            try:
                for file in files:
                    if path:
                        for root, _, filenames in os.walk(path):
                            for filename in filenames:
                                if filename == file:
                                    full_path = os.path.join(root, filename)
                                    self.listbox_files.insert(tk.END, full_path)
                    else:
                        # Поиск в папке, где лежит скрипт
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        for root, _, filenames in os.walk(script_dir):
                            for filename in filenames:
                                if filename == file:
                                    full_path = os.path.join(root, filename)
                                    self.listbox_files.insert(tk.END, full_path)


                self.root.after(0, self.update_ui_after_search)  # Безопасное обновление UI
                if self.listbox_files.size() > 0:
                    messagebox.showwarning("Информация", "Поиск окончен, что-то найдено")
                else:
                    messagebox.showinfo("Информация", "Поиск окончен, ничего не найдено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка во время поиска: {e}")

        threading.Thread(target=search_thread).start()

    def update_ui_after_search(self):
        self.root.title("Инструмент поиска и удаления файлов")
        self.button_search.config(state=tk.NORMAL)
        if self.listbox_files.size() > 0:
            self.button_open_folder.config(state=tk.NORMAL)
            self.button_delete.config(state=tk.NORMAL)
            self.button_delete_all.config(state=tk.NORMAL)

    def create_report(self):
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        path_text = self.entry_path.get() or os.path.dirname(os.path.abspath(__file__))

        folder_name_short = path_text[:10]
        folder_name_short = ''.join(c for c in folder_name_short if c.isalnum())
        report_file = f".\\Отчет_{folder_name_short}_{date}.txt"

        content = f"Имя папки:\t{path_text}\n"
        content += f"Имена файлов:\t{self.entry_files.get()}\n"
        content += "Найденные файлы:\n"
        for i in range(self.listbox_files.size()):
            content += f"{self.listbox_files.get(i)}\n"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Успех", f"Отчет создан: {report_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании отчета: {e}")

    def open_folder(self):
        selected_item = self.listbox_files.get(self.listbox_files.curselection())
        if selected_item:
          folder_path = os.path.dirname(selected_item)
          try:
              subprocess.Popen(f'explorer "{folder_path}"')
          except Exception as e:
              messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

    def delete_file(self):
        try:
            selected_file = self.listbox_files.get(self.listbox_files.curselection())
            if selected_file:
                os.remove(selected_file)
                self.listbox_files.delete(self.listbox_files.curselection())

                if self.listbox_files.size() == 0:
                    self.button_open_folder.config(state=tk.DISABLED)
                    self.button_delete.config(state=tk.DISABLED)
                    self.button_delete_all.config(state=tk.DISABLED)
        except OSError as e:
             messagebox.showerror("Ошибка удаления", f"Не удалось удалить файл: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def delete_all_files(self):
        try:
           for i in range(self.listbox_files.size() - 1, -1, -1):
             file_path = self.listbox_files.get(i)
             try:
                os.remove(file_path)
             except OSError as e:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить файл: {file_path}. Ошибка: {e}")
             except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка при удалении файла {file_path}: {e}")

           self.listbox_files.delete(0, tk.END)
           self.button_open_folder.config(state=tk.DISABLED)
           self.button_delete.config(state=tk.DISABLED)
           self.button_delete_all.config(state=tk.DISABLED)
           messagebox.showinfo("Информация", "Файлы успешно удалены")

        except Exception as e:
           messagebox.showerror("Ошибка", f"Произошла общая ошибка: {e}")


    def clear_listbox(self):
        self.listbox_files.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    tool = FileSearchTool(root)
    root.mainloop()