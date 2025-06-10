import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random

class EditableTreeview(ttk.Treeview):
    """Treeview с возможностью редактирования ячеек"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.editable_columns = set()
        self.bind("<Double-1>", self.on_double_click)
        
        # Переменные для редактирования
        self.entry = None
        self.edit_column = None
        self.edit_item = None
    
    def on_double_click(self, event):
        """Обработка двойного клика для редактирования"""
        region = self.identify_region(event.x, event.y)
        if region == "cell":
            column = self.identify_column(event.x)
            item = self.identify_row(event.y)
            
            # Проверяем, можно ли редактировать эту колонку
            if column != '#1' and item:  # Колонка учителя не редактируется
                self.start_edit(item, column)
    
    def start_edit(self, item, column):
        """Начинаем редактирование ячейки"""
        # Получаем координаты ячейки
        column_index = int(column[1:]) - 1
        column_id = self['columns'][column_index]
        
        # Получаем текущее значение
        current_value = self.item(item, 'values')[column_index]
        
        # Создаем поле для ввода
        bbox = self.bbox(item, column)
        if not bbox:
            return
        
        # Удаляем старое поле ввода, если было
        if self.entry:
            self.entry.destroy()
            
        # Создаем новое поле
        self.entry = ttk.Entry(self, width=10)
        self.entry.insert(0, current_value)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # Размещаем поле
        self.entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Назначаем обработчики
        self.entry.bind("<Return>", lambda e: self.finish_edit(item, column_index))
        self.entry.bind("<Escape>", lambda e: self.cancel_edit())
        self.entry.bind("<FocusOut>", lambda e: self.finish_edit(item, column_index))
        
        # Сохраняем данные о редактировании
        self.edit_column = column_index
        self.edit_item = item
    
    def finish_edit(self, item, column_index):
        """Завершаем редактирование и сохраняем значение"""
        if not self.entry:
            return
            
        new_value = self.entry.get()
        current_values = list(self.item(item, 'values'))
        
        # Проверяем введенное значение
        try:
            # Преобразуем в целое число
            int_value = int(new_value)
            if int_value < 0:
                raise ValueError("Отрицательное число")
            current_values[column_index] = int_value
        except ValueError:
            # Если введено не число - сохраняем старое значение
            current_values[column_index] = self.item(item, 'values')[column_index]
        
        # Обновляем значение в таблице
        self.item(item, values=current_values)
        
        # Удаляем поле ввода
        self.entry.destroy()
        self.entry = None
        self.edit_column = None
        self.edit_item = None
    
    def cancel_edit(self):
        """Отменяем редактирование"""
        if self.entry:
            self.entry.destroy()
            self.entry = None
            self.edit_column = None
            self.edit_item = None

class SchoolScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор школьного расписания")
        self.root.geometry("1200x600")
        
        # Инициализация данных
        self.teachers = []
        self.classes = []
        self.lessons_per_week = {}
        self.schedule = {}
        self.days = 5
        self.lessons_per_day = 8
        
        # Создание интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Управляющие кнопки
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Добавить учителей", command=self.add_teachers).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить классы", command=self.add_classes).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Установить уроки", command=self.set_lessons).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сгенерировать расписание", command=self.generate_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать расписание", command=self.show_schedule).pack(side=tk.LEFT, padx=5)
        
        # Область отображения расписания
        self.schedule_frame = ttk.Frame(main_frame)
        self.schedule_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def add_teachers(self):
        teachers_str = simpledialog.askstring("Учителя", "Введите фамилии учителей через запятую:")
        if teachers_str:
            self.teachers = [t.strip() for t in teachers_str.split(",")]
            messagebox.showinfo("Успешно", f"Добавлено учителей: {len(self.teachers)}")
    
    def add_classes(self):
        classes_str = simpledialog.askstring("Классы", "Введите классы через запятую:")
        if classes_str:
            self.classes = [c.strip() for c in classes_str.split(",")]
            messagebox.showinfo("Успешно", f"Добавлено классов: {len(self.classes)}")
    
    def set_lessons(self):
        if not self.teachers or not self.classes:
            messagebox.showerror("Ошибка", "Сначала добавьте учителей и классы")
            return
        
        # Создаем окно для ввода количества уроков
        lesson_window = tk.Toplevel(self.root)
        lesson_window.title("Количество уроков в неделю")
        lesson_window.geometry("800x400")
        
        # Создаем скроллбар
        scroll_frame = ttk.Frame(lesson_window)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем таблицу с возможностью редактирования
        headers = ["Учитель"] + self.classes
        tree = EditableTreeview(scroll_frame, columns=headers, show="headings")
        
        # Настраиваем заголовки
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Добавляем данные
        for teacher in self.teachers:
            values = [teacher]
            for cls in self.classes:
                # Используем сохраненные значения или 0
                count = self.lessons_per_week.get(teacher, {}).get(cls, 0)
                values.append(count)
            tree.insert("", tk.END, values=values)
        
        # Функция для сохранения данных
        def save_lessons():
            self.lessons_per_week = {}
            for item in tree.get_children():
                values = tree.item(item, "values")
                teacher = values[0]
                self.lessons_per_week[teacher] = {}
                for i, cls in enumerate(self.classes):
                    try:
                        count = int(values[i+1])
                        self.lessons_per_week[teacher][cls] = count
                    except ValueError:
                        self.lessons_per_week[teacher][cls] = 0
            
            messagebox.showinfo("Сохранено", "Данные об уроках сохранены")
            lesson_window.destroy()
        
        # Кнопка сохранения
        btn_frame = ttk.Frame(lesson_window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Сохранить", command=save_lessons).pack()
    
    def generate_schedule(self):
        if not self.teachers or not self.classes or not self.lessons_per_week:
            messagebox.showerror("Ошибка", "Сначала добавьте все данные")
            return
        
        # Инициализация расписания
        self.schedule = {}
        for teacher in self.teachers:
            self.schedule[teacher] = {}
            for day in range(self.days):
                for lesson in range(self.lessons_per_day):
                    self.schedule[teacher][(day, lesson)] = None
        
        # Создаем список всех необходимых уроков
        all_lessons = []
        for teacher, classes in self.lessons_per_week.items():
            for cls, count in classes.items():
                for _ in range(count):
                    all_lessons.append((teacher, cls))
        
        # Случайно перемешиваем уроки
        random.shuffle(all_lessons)
        
        # Создаем матрицу занятости классов
        class_busy = {}
        for cls in self.classes:
            class_busy[cls] = [[False for _ in range(self.lessons_per_day)] for _ in range(self.days)]
        
        # Распределяем уроки
        for teacher, cls in all_lessons:
            placed = False
            
            # Создаем список всех возможных слотов и перемешиваем
            slots = [(d, l) for d in range(self.days) for l in range(self.lessons_per_day)]
            random.shuffle(slots)
            
            for day, lesson in slots:
                # Проверяем доступность учителя и класса
                if (self.schedule[teacher][(day, lesson)] is None and 
                    not class_busy[cls][day][lesson]):
                    
                    # Назначаем урок
                    self.schedule[teacher][(day, lesson)] = cls
                    class_busy[cls][day][lesson] = True
                    placed = True
                    break
            
            if not placed:
                messagebox.showwarning("Предупреждение", f"Не удалось разместить урок: {teacher} - {cls}")
        
        messagebox.showinfo("Готово", "Расписание успешно сгенерировано")
    
    def show_schedule(self):
        if not self.schedule:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте расписание")
            return
        
        # Очищаем область отображения
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        # Создаем таблицу
        tree = ttk.Treeview(self.schedule_frame)
        
        # Настраиваем столбцы
        columns = ["Учитель"]
        for day in range(self.days):
            for lesson in range(self.lessons_per_day):
                columns.append(f"День {day+1} Урок {lesson+1}")
        
        tree["columns"] = columns
        tree.column("#0", width=0, stretch=tk.NO)
        tree.heading("#0", text="")
        
        for col in columns:
            tree.column(col, anchor=tk.CENTER, width=100)
            tree.heading(col, text=col)
        
        # Добавляем данные
        for teacher in self.teachers:
            values = [teacher]
            for day in range(self.days):
                for lesson in range(self.lessons_per_day):
                    cls = self.schedule[teacher].get((day, lesson), "")
                    values.append(cls if cls else "-")
            tree.insert("", tk.END, values=values)
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(self.schedule_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolScheduleApp(root)
    root.mainloop()