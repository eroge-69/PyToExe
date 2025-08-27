import os
import threading
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

#Поддерживаемые расширения Excel
EXCEL_EXTS = {'.xlsm', '.xlsx', '.doc', ',docx', '.pdf'}

class ExcelFinderApp:
    def __init__(self, root):
        self.root = root
        root.title("Поиск и печать ")

        frm = ttk.Frame(root, padding = 10)
        frm.grid(sticky = 'nsew')
        root.columnconfigure(0, weight = 1)
        root.rowconfigure(0, weight = 1)

        #Поле ввода имени
        ttk.Label(frm, text = "Имя файла (без расширения): ").grid(column = 0, row = 0, sticky = 'w')
        self.name_var = tk.StringVar()
        self.entry_name = ttk.Entry(frm, textvariable = self.name_var, width = 40)
        self.entry_name.grid(column = 0, row = 1, sticky = 'we', padx = (0, 10))

        #Кнопка выбора папки
        self.folder_var = tk.StringVar(value = os.path.expanduser('~'))
        btn_choose = ttk.Button(frm, text = 'Выбрать папку...', command = self.choose_folder)
        btn_choose.grid(column = 1, row = 1, sticky = 'e')

        ttk.Label(frm, text = 'Папка для поиска: ').grid(column = 0, row = 2, sticky = 'w', pady = (10, 0))
        self.lbl_folder = ttk.Label(frm, textvariable = self.folder_var)
        self.lbl_folder.grid(column = 0, row = 3, columnspan = 2, sticky = 'w')

        #Кнопка поиска
        btn_search = ttk.Button(frm, text = 'Поиск', command = self.start_search)
        btn_search.grid(column = 0, row = 4, pady = (10, 0), sticky = 'w')

        #Список результатов
        ttk.Label(frm, text = 'Найденные файлы: ').grid(column = 0, row = 5, sticky = 'w', pady = (10, 0))
        self.listbox = tk.Listbox(frm, height = 8, width = 80)
        self.listbox.grid(column = 0, row = 6, columnspan = 2, sticky = 'nsew')
        scrollbar = ttk.Scrollbar (frm, orient = 'vertical', command = self.listbox.yview)
        scrollbar.grid(column = 2, row = 6, sticky = 'ns')

        self.listbox.config(yscrollcommand = scrollbar.set)

        #Кнопки печть/открыть
        btn_open = ttk.Button(frm, text = 'Открыть', command = self.open_selected)
        btn_open.grid(column = 0, row = 7, pady = (10, 0), sticky = 'w')

        btn_print = ttk.Button(frm, text = 'Печать', command = self.print_selected)
        btn_print.grid(column = 1, row = 7, pady = (10, 0), sticky = 'w')

        #Статус
        self.status_var = tk.StringVar(value = '')
        ttk.Label(frm, textvariable = self.status_var, foreground = 'blue').grid(column = 0, row = 8, columnspan = 2,
                                                                                 sticky = 'w', pady = (8, 0))

        #Растягивание списка
        frm.rowconfigure(6, weight = 1)
        frm.columnconfigure(0, weight = 1)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir = self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def start_search(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('Внимание', 'Введите имя файла для поиска.')
            return
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showwarning('Внимание', 'Выберите существующую папку  для поиска.')
            return

        #Запуск в потоке, чтобы UI  не записал
        thread = threading.Thread(target = self.search_files, args = (folder, name), daemon = True)
        thread.start()
        self.status_var.set('Идет поиск...')


    def search_files(self, folder, name):
        found = []
        name_lower = name.lower()
        try:
            for root_dir, dirs, files in os.walk(folder):
                for f in files:
                    fname, ext = os.path.splitext(f)
                    if ext.lower() in EXCEL_EXTS and name_lower in fname.lower():
                        found.append(os.path.join(root_dir, f))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror('Ошибка', 'Ошибка при поиске: {e}'))
            self.root.after(0, lambda: self.status_var.set(''))
            return

        #Обновление UI
        self.root.after(0, lambda: self.update_results(found))

    def update_results(self, found):
        self.listbox.delete(0, tk.END)
        if not found:
            self.status_var.set('Файлы не найдены')
            return
        for p in found:
            self.listbox.insert(tk.END, p)
        self.status_var.set('Файлы найдены')

    def get_selected_path(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Информация', 'Выберите файл в списке')
            return None
        return self.listbox.get(sel[0])

    def open_selected(self):
        path = self.get_selected_path()
        if not path:
            return
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(path, 'open')
            elif system == 'Darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
                self.status_var('Файл открыт')
        except Exception as e:
            messagebox.showerror('Ошибка', 'Не удалось открыть файл: {e')

    def print_selected(self):
        path = self.get_selected_path()
        if not path:
            return
        system = platform.system()
        try:
            os.startfile(path, 'print')
            self.status_var.set('Команда печати отправлена')
        except Exception:
            messagebox.showinfo('Файл открыт для ручной печати')
            self.open_selected()


if __name__ == '__main__':
    root = tk.Tk()
    app = ExcelFinderApp(root)
    root.geometry('800x400')
    root.mainloop()