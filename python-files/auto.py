import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import shutil
from PIL import Image, ImageTk
import webbrowser

class CarDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учета автомобилей с документами")
        self.root.geometry("900x700")
        
        # База данных и папки для хранения
        self.cars_db = {}
        self.data_file = "cars_database.json"
        self.attachments_dir = "car_attachments"
        
        # Создаем папку для вложений если ее нет
        if not os.path.exists(self.attachments_dir):
            os.makedirs(self.attachments_dir)
        
        # Загрузка данных при запуске
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка добавления автомобиля
        add_frame = ttk.Frame(notebook)
        notebook.add(add_frame, text="Добавить автомобиль")
        self.create_add_tab(add_frame)
        
        # Вкладка поиска и просмотра
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Поиск и просмотр")
        self.create_search_tab(search_frame)
        
        # Вкладка просмотра всех автомобилей
        view_frame = ttk.Frame(notebook)
        notebook.add(view_frame, text="Все автомобили")
        self.create_view_tab(view_frame)
        
    def create_add_tab(self, parent):
        # Поля для ввода данных
        fields = [
            ("Государственный номер:*", "license_entry"),
            ("Марка автомобиля:*", "brand_entry"),
            ("Данные ПТС:", "pts_entry"),
            ("Данные СТС:", "sts_entry"),
            ("Дополнительные заметки:", "notes_entry")
        ]
        
        entries = {}
        for i, (label_text, entry_name) in enumerate(fields):
            label = ttk.Label(parent, text=label_text)
            label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            if entry_name == "notes_entry":
                entry = scrolledtext.ScrolledText(parent, width=40, height=4)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='we')
            else:
                entry = ttk.Entry(parent, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='we')
            
            entries[entry_name] = entry
        
        self.license_entry = entries["license_entry"]
        self.brand_entry = entries["brand_entry"]
        self.pts_entry = entries["pts_entry"]
        self.sts_entry = entries["sts_entry"]
        self.notes_entry = entries["notes_entry"]
        
        # Секция для прикрепления документов
        docs_frame = ttk.LabelFrame(parent, text="Прикрепленные документы")
        docs_frame.grid(row=len(fields), column=0, columnspan=2, sticky='we', padx=5, pady=10)
        
        # Кнопки для добавления документов
        docs_buttons_frame = ttk.Frame(docs_frame)
        docs_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(docs_buttons_frame, text="Добавить фото ПТС", 
                  command=lambda: self.add_document("ПТС")).pack(side='left', padx=2)
        ttk.Button(docs_buttons_frame, text="Добавить фото СТС", 
                  command=lambda: self.add_document("СТС")).pack(side='left', padx=2)
        ttk.Button(docs_buttons_frame, text="Добавить фото авто", 
                  command=lambda: self.add_document("Авто")).pack(side='left', padx=2)
        ttk.Button(docs_buttons_frame, text="Добавить другой документ", 
                  command=lambda: self.add_document("Другой")).pack(side='left', padx=2)
        
        # Список прикрепленных документов
        self.attachments_listbox = tk.Listbox(docs_frame, height=4)
        self.attachments_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Кнопка удаления выбранного документа
        ttk.Button(docs_buttons_frame, text="Удалить выбранный", 
                  command=self.remove_selected_document).pack(side='right', padx=2)
        
        # Хранилище для временных путей документов
        self.temp_attachments = []
        
        # Кнопка добавления автомобиля
        add_btn = ttk.Button(parent, text="Добавить автомобиль", command=self.add_car)
        add_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        # Настройка веса колонок для растягивания
        parent.columnconfigure(1, weight=1)
        
    def create_search_tab(self, parent):
        # Поисковая строка
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск по гос. номеру:").pack(side='left', padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_car())
        
        ttk.Button(search_frame, text="Найти", command=self.search_car).pack(side='left', padx=5)
        
        # Область для отображения результатов
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Основная информация
        info_frame = ttk.LabelFrame(result_frame, text="Информация об автомобиле")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(info_frame, height=8)
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.result_text.config(state=tk.DISABLED)
        
        # Документы
        docs_frame = ttk.LabelFrame(result_frame, text="Прикрепленные документы")
        docs_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Фрейм для миниатюр документов
        self.docs_container = ttk.Frame(docs_frame)
        self.docs_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Полоса прокрутки для документов
        self.docs_canvas = tk.Canvas(self.docs_container)
        scrollbar = ttk.Scrollbar(self.docs_container, orient="vertical", command=self.docs_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.docs_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.docs_canvas.configure(scrollregion=self.docs_canvas.bbox("all"))
        )
        
        self.docs_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.docs_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.docs_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_view_tab(self, parent):
        # Панель управления
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Обновить список", command=self.refresh_list).pack(side='left', padx=5)
        
        self.count_label = ttk.Label(control_frame, text="Всего автомобилей: 0")
        self.count_label.pack(side='right', padx=5)
        
        # Таблица автомобилей
        columns = ("Номер", "Марка", "ПТС", "СТС", "Документы")
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        column_widths = {"Номер": 120, "Марка": 150, "ПТС": 150, "СТС": 150, "Документы": 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5)
        scrollbar.pack(side='right', fill='y', padx=5)
        
        # Двойной клик для просмотра деталей
        self.tree.bind('<Double-1>', self.show_car_details)
        
        self.refresh_list()
        
    def add_document(self, doc_type):
        """Добавление документа через диалог выбора файла"""
        file_types = [
            ('Изображения', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('PDF документы', '*.pdf'),
            ('Все файлы', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(title=f"Выберите файл {doc_type}", filetypes=file_types)
        
        if file_path:
            filename = os.path.basename(file_path)
            display_name = f"{doc_type}: {filename}"
            self.attachments_listbox.insert(tk.END, display_name)
            self.temp_attachments.append((file_path, doc_type, filename))
            
    def remove_selected_document(self):
        """Удаление выбранного документа из списка"""
        selection = self.attachments_listbox.curselection()
        if selection:
            index = selection[0]
            self.attachments_listbox.delete(index)
            if index < len(self.temp_attachments):
                self.temp_attachments.pop(index)
                
    def copy_attachments(self, license_plate):
        """Копирование прикрепленных файлов в папку автомобиля"""
        if not self.temp_attachments:
            return []
        
        car_dir = os.path.join(self.attachments_dir, license_plate)
        if not os.path.exists(car_dir):
            os.makedirs(car_dir)
        
        saved_attachments = []
        
        for original_path, doc_type, filename in self.temp_attachments:
            # Создаем уникальное имя файла
            name, ext = os.path.splitext(filename)
            new_filename = f"{doc_type}_{name}{ext}"
            new_path = os.path.join(car_dir, new_filename)
            
            # Копируем файл
            shutil.copy2(original_path, new_path)
            saved_attachments.append((doc_type, new_filename))
            
        return saved_attachments
        
    def add_car(self):
        """Добавление нового автомобиля в базу"""
        license_plate = self.license_entry.get().strip().upper()
        brand = self.brand_entry.get().strip()
        
        if not license_plate or not brand:
            messagebox.showerror("Ошибка", "Заполните обязательные поля (отмечены *)!")
            return
            
        if license_plate in self.cars_db:
            messagebox.showerror("Ошибка", "Автомобиль с таким номером уже существует!")
            return
            
        # Копируем прикрепленные документы
        attachments = self.copy_attachments(license_plate)
        
        # Сохраняем данные автомобиля
        self.cars_db[license_plate] = {
            'Марка': brand,
            'ПТС': self.pts_entry.get().strip(),
            'СТС': self.sts_entry.get().strip(),
            'Заметки': self.notes_entry.get("1.0", tk.END).strip(),
            'Документы': attachments
        }
        
        # Очистка полей
        self.license_entry.delete(0, tk.END)
        self.brand_entry.delete(0, tk.END)
        self.pts_entry.delete(0, tk.END)
        self.sts_entry.delete(0, tk.END)
        self.notes_entry.delete("1.0", tk.END)
        self.attachments_listbox.delete(0, tk.END)
        self.temp_attachments.clear()
        
        self.save_data()
        self.refresh_list()
        messagebox.showinfo("Успех", f"Автомобиль {license_plate} успешно добавлен!")
        
    def search_car(self):
        """Поиск автомобиля по гос. номеру"""
        license_plate = self.search_entry.get().strip().upper()
        
        if not license_plate:
            messagebox.showerror("Ошибка", "Введите гос. номер для поиска!")
            return
            
        car = self.cars_db.get(license_plate)
        
        # Очистка предыдущих результатов
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        
        # Очистка области документов
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if car:
            # Вывод основной информации
            info_text = f"Гос. номер: {license_plate}\n\n"
            for key, value in car.items():
                if key != 'Документы':
                    info_text += f"{key}: {value}\n\n"
            
            self.result_text.insert(tk.END, info_text)
            
            # Отображение документов
            attachments = car.get('Документы', [])
            if attachments:
                self.show_attachments(license_plate, attachments)
            else:
                no_docs_label = ttk.Label(self.scrollable_frame, text="Нет прикрепленных документов")
                no_docs_label.pack(pady=10)
        else:
            self.result_text.insert(tk.END, f"Автомобиль с номером {license_plate} не найден!")
            
        self.result_text.config(state=tk.DISABLED)
        
    def show_attachments(self, license_plate, attachments):
        """Отображение прикрепленных документов"""
        car_dir = os.path.join(self.attachments_dir, license_plate)
        
        for i, (doc_type, filename) in enumerate(attachments):
            doc_frame = ttk.Frame(self.scrollable_frame, relief='solid', borderwidth=1)
            doc_frame.pack(fill='x', padx=5, pady=5)
            
            # Название документа
            ttk.Label(doc_frame, text=f"{doc_type}: {filename}").pack(anchor='w', padx=5, pady=2)
            
            # Кнопка просмотра
            doc_path = os.path.join(car_dir, filename)
            ttk.Button(doc_frame, text="Открыть документ", 
                      command=lambda path=doc_path: self.open_document(path)).pack(padx=5, pady=2)
            
    def open_document(self, file_path):
        """Открытие документа в стандартном приложении"""
        try:
            if os.path.exists(file_path):
                webbrowser.open(file_path)
            else:
                messagebox.showerror("Ошибка", "Файл не найден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
            
    def refresh_list(self):
        """Обновление списка автомобилей"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for license_plate, car in self.cars_db.items():
            docs_count = len(car.get('Документы', []))
            self.tree.insert('', tk.END, values=(
                license_plate,
                car['Марка'],
                car['ПТС'][:20] + "..." if len(car['ПТС']) > 20 else car['ПТС'],
                car['СТС'][:20] + "..." if len(car['СТС']) > 20 else car['СТС'],
                f"{docs_count} файлов"
            ))
            
        self.count_label.config(text=f"Всего автомобилей: {len(self.cars_db)}")
        
    def show_car_details(self, event):
        """Просмотр деталей автомобиля по двойному клику"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            license_plate = item['values'][0]
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, license_plate)
            self.search_car()
            
            # Переключение на вкладку поиска
            self.root.nametowidget(self.root.winfo_children()[0]).select(1)
        
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.cars_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.cars_db = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

def main():
    root = tk.Tk()
    app = CarDatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()