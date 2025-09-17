import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from xml.dom import minidom
import base64


class ProtocolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор протоколов испытаний")
        self.root.geometry("1920x1080")
        
        self.protocols = []
        self.current_protocol = {}
        self.fact_values = []  # Список для хранения множественных значений FactValue
        self.pdf_file_path = None  # Путь к выбранному PDF файлу
        self.pdf_base64 = None  # Base64 содержимое PDF
        
        # Загрузка баз данных
        self.load_databases()
        
        # Создаем главный фрейм с прокруткой
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Холст и скроллбар
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Привязываем прокрутку колесиком мыши
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill='y')
        
        # Настройка интерфейса
        self.setup_interface()
        
        # Кнопки внизу
        self.setup_bottom_buttons()
        
        # Привязка горячих клавиш
        self.setup_hotkeys()
        self.disable_default_bindings()  # Отключаем стандартные привязки
        
    def disable_default_bindings(self):
        # Отключаем стандартные привязки для Text и Entry
        self.root.unbind_class('Text', '<Control-c>')
        self.root.unbind_class('Text', '<Control-v>')
        self.root.unbind_class('Text', '<Control-x>')
        self.root.unbind_class('Entry', '<Control-c>')
        self.root.unbind_class('Entry', '<Control-v>')
        self.root.unbind_class('Entry', '<Control-x>')
        
    def setup_hotkeys(self):
        # Привязка горячих клавиш для копирования и вставки
        self.root.bind('<Control-c>', self.copy_text_event)
        self.root.bind('<Control-v>', self.paste_text_event)
        self.root.bind('<Control-x>', self.cut_text_event)
        
    def copy_text_event(self, event):
        # Получаем виджет, который имеет фокус
        widget = self.root.focus_get()
        
        # Проверяем тип виджета и выполняем копирование
        if isinstance(widget, (tk.Entry, tk.Text, tk.Listbox, scrolledtext.ScrolledText)):
            try:
                if widget.selection_present():
                    selected_text = widget.selection_get()
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
            except:
                pass
        return "break"
    
    def paste_text_event(self, event):
        # Получаем виджет, который имеет фокус
        widget = self.root.focus_get()
        
        # Проверяем тип виджета и выполняем вставку
        if isinstance(widget, (tk.Entry, tk.Text, scrolledtext.ScrolledText)):
            try:
                clipboard_text = self.root.clipboard_get()
                widget.insert(tk.INSERT)
                return "break"  # Явно прерываем дальнейшую обработку
            except:
                pass
        return None
    
    def cut_text_event(self, event):
        # Получаем виджет, который имеет фокус
        widget = self.root.focus_get()
        
        # Проверяем тип виджета и выполняем вырезание
        if isinstance(widget, (tk.Entry, tk.Text, scrolledtext.ScrolledText)):
            try:
                if widget.selection_present():
                    selected_text = widget.selection_get()
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except:
                pass
        return "break"
        
    def on_mousewheel(self, event):
        """Обработка прокрутки колесиком мыши"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def load_databases(self):
        # Загрузка базы оборудования
        self.equipment_db = []
        if os.path.exists("equipment.json"):
            try:
                with open("equipment.json", "r", encoding="utf-8") as f:
                    self.equipment_db = json.load(f)
            except:
                self.equipment_db = []
        
        # Загрузка базы испытателей
        self.testers_db = []
        if os.path.exists("testers.json"):
            try:
                with open("testers.json", "r", encoding="utf-8") as f:
                    self.testers_db = json.load(f)
            except:
                self.testers_db = []
        
        # Создаем файлы по умолчанию, если их нет
      #  if not self.equipment_db:
        #    self.equipment_db = [
          #      {"id": "1452367", "name": "П3-41 1053"},
           #     {"id": "1557988", "name": "ADA Co70 000352"},
            #    {"id": "1454222", "name": "ИВА 11150"},
             #   {"id": "2775160", "name": "Vega E303682"}
           # ]
           # self.save_equipment_db()
            
     #   if not self.testers_db:
         #   self.testers_db = [
           #     {"id": "297749", "name": "Иванов И.И.", "post": "Испытатель", "role_id": "1"},
          #      {"id": "297764", "name": "Петров П.П.", "post": "Заместитель руководителя", "role_id": "2"}
         #   ]
         #   self.save_testers_db()
    
    def save_equipment_db(self):
        with open("equipment.json", "w", encoding="utf-8") as f:
            json.dump(self.equipment_db, f, ensure_ascii=False, indent=2)
    
    def save_testers_db(self):
        with open("testers.json", "w", encoding="utf-8") as f:
            json.dump(self.testers_db, f, ensure_ascii=False, indent=2)
    
    def get_role_id_by_post(self, post):
        """Определяет role_id на основе должности"""
        post_lower = post.lower()
        
        # Определяем роль на основе ключевых слов в должности
        if any(keyword in post_lower for keyword in ["Испытатель"]):
            return "1"  # Испытатель
        elif any(keyword in post_lower for keyword in ["Руководитель", "Заместитель руководителя"]):
            return "2"  # Утверждение протокола
        else:
            return "1"  # По умолчанию Испытатель
    
    def setup_interface(self):
        row = 0
        
        # Основная информация
        ttk.Label(self.scrollable_frame, text="Основная информация", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Номер протокола:").grid(row=row, column=0, sticky='w', pady=5)
        self.doc_id = ttk.Entry(self.scrollable_frame, width=40)
        self.doc_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.doc_id)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Дата протокола:").grid(row=row, column=0, sticky='w', pady=5)
        self.doc_creation_date = ttk.Entry(self.scrollable_frame, width=40)
        self.doc_creation_date.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.doc_creation_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        # Добавляем контекстное меню
        self.add_context_menu(self.doc_creation_date)
        row += 1
        
        
        # Скрытые поля (будут в XML, но не показываются в интерфейсе)
        self.doc_start_date = "0001-01-01"
        self.doc_validity_date = "0001-01-01"
        self.data_status_id = "20"
        self.protocol_status_id = "6"
        self.territory_feature = True  # Значение по умолчанию
        self.id_code_oksm = "643"      # Значение по умолчанию
        self.id_addr_type = "3"        # Значение по умолчанию
        self.is_lab = False            # Значение по умолчанию
        self.is_another_doc = False    # Значение по умолчанию
        self.is_rf = True              # Значение по умолчанию
        
        ttk.Label(self.scrollable_frame, text="Адрес проведения:").grid(row=row, column=0, sticky='w', pady=5)
        self.address_text = ttk.Entry(self.scrollable_frame, width=40)
        self.address_text.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.address_text)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Дата заявки:").grid(row=row, column=0, sticky='w', pady=5)
        self.application_date = ttk.Entry(self.scrollable_frame, width=40)
        self.application_date.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.application_date)
        row += 1
        
        # PDF файл
        ttk.Label(self.scrollable_frame, text="PDF файл протокола:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky='w', pady=10)
        row += 1
        
        # Фрейм для выбора PDF
        pdf_frame = ttk.Frame(self.scrollable_frame)
        pdf_frame.grid(row=row, column=0, columnspan=2, sticky='we', pady=5)
        row += 1
        
        self.pdf_label = ttk.Label(pdf_frame, text="Файл не выбран", foreground="red")
        self.pdf_label.pack(side='left', padx=5)
        
        ttk.Button(pdf_frame, text="Выбрать PDF файл", command=self.select_pdf_file).pack(side='left', padx=5)
        ttk.Button(pdf_frame, text="Очистить", command=self.clear_pdf_file).pack(side='left', padx=5)
        
        # Информация о заказчике
        ttk.Label(self.scrollable_frame, text="Информация о заказчике", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Тип заказчика:").grid(row=row, column=0, sticky='w', pady=5)
        self.customer_kind_id = ttk.Entry(self.scrollable_frame, width=40)
        self.customer_kind_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.customer_kind_id.insert(0, "1")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ИНН:").grid(row=row, column=0, sticky='w', pady=5)
        self.inn_id = ttk.Entry(self.scrollable_frame, width=40)
        self.inn_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.inn_id)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ОГРН:").grid(row=row, column=0, sticky='w', pady=5)
        self.ogrn_id = ttk.Entry(self.scrollable_frame, width=40)
        self.ogrn_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.ogrn_id)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Телефон:").grid(row=row, column=0, sticky='w', pady=5)
        self.phone_number = ttk.Entry(self.scrollable_frame, width=40)
        self.phone_number.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        # Добавляем контекстное меню
        self.add_context_menu(self.phone_number)
        row += 1
        
        # Оборудование
        ttk.Label(self.scrollable_frame, text="Оборудование", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Фрейм для оборудования
        equipment_frame = ttk.Frame(self.scrollable_frame)
        equipment_frame.grid(row=row, column=0, columnspan=2, sticky='we', pady=5)
        row += 1
        
        ttk.Label(equipment_frame, text="Доступное оборудование:").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(equipment_frame, text="Выбранное оборудование:").grid(row=0, column=1, sticky='w', padx=5)
        
        # Список доступного оборудования
        self.available_equipment = tk.Listbox(equipment_frame, selectmode=tk.MULTIPLE, height=5)
        self.available_equipment.grid(row=1, column=0, padx=5, sticky='nswe')
        
        # Список выбранного оборудования
        self.selected_equipment = tk.Listbox(equipment_frame, height=5)
        self.selected_equipment.grid(row=1, column=1, padx=5, sticky='nswe')
        
        # Кнопки для оборудования
        btn_frame = ttk.Frame(equipment_frame)
        btn_frame.grid(row=1, column=2, padx=5, sticky='ns')
        
        ttk.Button(btn_frame, text="Добавить →", command=self.add_equipment).pack(pady=2)
        ttk.Button(btn_frame, text="← Удалить", command=self.remove_equipment).pack(pady=2)
        ttk.Button(btn_frame, text="Добавить новое", command=self.add_new_equipment).pack(pady=2)
        
        # Заполняем список оборудования
        self.update_equipment_list()
        
        # Испытатели
        ttk.Label(self.scrollable_frame, text="Испытатели", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Фрейм для испытателей
        testers_frame = ttk.Frame(self.scrollable_frame)
        testers_frame.grid(row=row, column=0, columnspan=2, sticky='we', pady=5)
        row += 1
        
        # Испытатель 1
        ttk.Label(testers_frame, text="Испытатель 1:").grid(row=0, column=0, sticky='w', padx=5)
        
        self.tester1_var = tk.StringVar()
        self.tester1_combo = ttk.Combobox(testers_frame, textvariable=self.tester1_var, state="readonly", width=30)
        self.tester1_combo.grid(row=1, column=0, padx=5, pady=5, sticky='we')
        self.tester1_combo.bind('<<ComboboxSelected>>', lambda e: self.update_tester1_details())
        
        ttk.Label(testers_frame, text="Должность:").grid(row=2, column=0, sticky='w', padx=5)
        self.tester1_post = ttk.Entry(testers_frame, width=30)
        self.tester1_post.grid(row=3, column=0, padx=5, pady=5, sticky='we')
        
        ttk.Label(testers_frame, text="Роль ID:").grid(row=4, column=0, sticky='w', padx=5)
        self.tester1_role = ttk.Entry(testers_frame, width=30)
        self.tester1_role.grid(row=5, column=0, padx=5, pady=5, sticky='we')
        
        # Испытатель 2
        ttk.Label(testers_frame, text="Испытатель 2:").grid(row=0, column=1, sticky='w', padx=5)
        
        self.tester2_var = tk.StringVar()
        self.tester2_combo = ttk.Combobox(testers_frame, textvariable=self.tester2_var, state="readonly", width=30)
        self.tester2_combo.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.tester2_combo.bind('<<ComboboxSelected>>', lambda e: self.update_tester2_details())
        
        ttk.Label(testers_frame, text="Должность:").grid(row=2, column=1, sticky='w', padx=5)
        self.tester2_post = ttk.Entry(testers_frame, width=30)
        self.tester2_post.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(testers_frame, text="Роль ID:").grid(row=4, column=1, sticky='w', padx=5)
        self.tester2_role = ttk.Entry(testers_frame, width=30)
        self.tester2_role.grid(row=5, column=1, padx=5, pady=5, sticky='we')
        
        # Кнопка добавления нового испытателя
        ttk.Button(testers_frame, text="Добавить нового испытателя", command=self.add_new_tester).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Заполняем список испытателей
        self.update_testers_list()
        
        # Информация об объекте испытаний
        ttk.Label(self.scrollable_frame, text="Объект испытаний", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Тип объекта ID:").grid(row=row, column=0, sticky='w', pady=5)
        self.type_object_id = ttk.Entry(self.scrollable_frame, width=40)
        self.type_object_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.type_object_id.insert(0, "8")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ID нормативного документа:").grid(row=row, column=0, sticky='w', pady=5)
        self.method_doc_id = ttk.Entry(self.scrollable_frame, width=40)
        self.method_doc_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.method_doc_id.insert(0, "4505258")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Наименование объекта:").grid(row=row, column=0, sticky='w', pady=5)
        self.full_name_object = ttk.Entry(self.scrollable_frame, width=40)
        self.full_name_object.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.full_name_object.insert(0, "Электромагнитное поле СВЧ-диапазона, создаваемое излучающими техническими средствами базовой станции")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ID показателя:").grid(row=row, column=0, sticky='w', pady=5)
        self.indicator_id = ttk.Entry(self.scrollable_frame, width=40)
        self.indicator_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.indicator_id.insert(0, "125893")
        row += 1
        
        # Фактические значения (множественные)
        ttk.Label(self.scrollable_frame, text="Фактические значения (столбцом):", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Текстовое поле для ввода множественных значений
        ttk.Label(self.scrollable_frame, text="Введите значения FactValue (каждое значение с новой строки):").grid(row=row, column=0, sticky='w', pady=5)
        row += 1
        
        self.fact_values_text = scrolledtext.ScrolledText(self.scrollable_frame, width=50, height=6)
        self.fact_values_text.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky='we')
        
        # Добавляем контекстное меню для вставки
        self.context_menu = tk.Menu(self.fact_values_text, tearoff=0)
        self.context_menu.add_command(label="Вставить", command=self.paste_to_text_widget)
        self.fact_values_text.bind("<Button-3>", self.show_context_menu)  # Правая кнопка мыши
        
        row += 1
        
        # Кнопка для обработки введенных значений
        ttk.Button(self.scrollable_frame, text="Добавить значения", command=self.process_fact_values).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Список добавленных значений с нумерацией и прокруткой
        ttk.Label(self.scrollable_frame, text="Добавленные значения FactValue:").grid(row=row, column=0, sticky='w', pady=5)
        row += 1
        
        # Фрейм для списка значений с прокруткой
        list_frame = ttk.Frame(self.scrollable_frame)
        list_frame.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky='we')
        row += 1
        
        # Ползунок прокрутки для списка значений
        list_scrollbar = ttk.Scrollbar(list_frame)
        list_scrollbar.pack(side='right', fill='y')
        
        # Список добавленных значений с нумерацией
        self.fact_values_listbox = tk.Listbox(list_frame, height=4, yscrollcommand=list_scrollbar.set)
        self.fact_values_listbox.pack(side='left', fill='both', expand=True)
        
        list_scrollbar.config(command=self.fact_values_listbox.yview)
        
        # Кнопка удаления выбранного значения
        ttk.Button(self.scrollable_frame, text="Удалить выбранное значение", command=self.remove_fact_value).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ID единицы измерения:").grid(row=row, column=0, sticky='w', pady=5)
        self.measurement_id = ttk.Entry(self.scrollable_frame, width=40)
        self.measurement_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.measurement_id.insert(0, "680")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="Методика:").grid(row=row, column=0, sticky='w', pady=5)
        self.unique_method = ttk.Entry(self.scrollable_frame, width=40)
        self.unique_method.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.unique_method.insert(0, "МУК 4.3.3830-22 «Определение уровней электромагнитного поля, создаваемого излучающими техническими средствами телевидения, ЧМ радиовещания и базовых станций сухопутной подвижной радиосвязи»")
        row += 1
        
        ttk.Label(self.scrollable_frame, text="ID методики:").grid(row=row, column=0, sticky='w', pady=5)
        self.doc_name_methodik_id = ttk.Entry(self.scrollable_frame, width=40)
        self.doc_name_methodik_id.grid(row=row, column=1, pady=5, padx=5, sticky='we')
        self.doc_name_methodik_id.insert(0, "497")
        row += 1
        
        # Настройка веса колонок для растягивания
        self.scrollable_frame.columnconfigure(1, weight=1)
    
    def select_pdf_file(self):
        """Выбор PDF файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Читаем файл и конвертируем в Base64
                with open(file_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                    self.pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                
                self.pdf_file_path = file_path
                file_name = os.path.basename(file_path)
                self.pdf_label.config(text=file_name, foreground="green")
                messagebox.showinfo("Успех", f"PDF файл '{file_name}' успешно загружен")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
                self.clear_pdf_file()
    
    def clear_pdf_file(self):
        """Очистка выбранного PDF файла"""
        self.pdf_file_path = None
        self.pdf_base64 = None
        self.pdf_label.config(text="Файл не выбран", foreground="red")
    
    def add_context_menu(self, widget):
        """Добавляет контекстное меню к виджету"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Копировать", command=lambda: self.copy_text(widget))
        menu.add_command(label="Вставить", command=lambda: self.paste_text(widget))
        menu.add_command(label="Вырезать", command=lambda: self.cut_text(widget))
        
        widget.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
    
    def copy_text(self, widget):
        """Копирует текст из виджета"""
        try:
            if widget.selection_present():
                selected_text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except:
            pass
    
    def paste_text(self, widget):
        """Вставляет текст в виджет"""
        try:
            clipboard_text = self.root.clipboard_get()
            widget.insert(tk.INSERT, clipboard_text)
        except:
            pass
    
    def cut_text(self, widget):
        """Вырезает текст из виджета"""
        try:
            if widget.selection_present():
                selected_text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
        
    def show_context_menu(self, event):
        """Показывает контекстное меню для текстового поле"""
        self.context_menu.post(event.x_root, event.y_root)
    
    def paste_to_text_widget(self):
        """Вставляет текст из буфера обмена в текстовое поле"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.fact_values_text.insert(tk.INSERT, clipboard_text)
        except:
            messagebox.showerror("Ошибка", "Не удалось вставить текст из буфера обмена")
        
    def setup_bottom_buttons(self):
        # Фрейм для кнопок внизу
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Добавить протокол", command=self.add_protocol).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Сохранить в XML", command=self.save_to_xml).pack(side='right', padx=5)
        
        # Список протоколов
        ttk.Label(self.root, text="Добавленные протоколы:").pack(anchor='w', padx=10)
        
        self.protocols_listbox = tk.Listbox(self.root, height=8)
        self.protocols_listbox.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(self.root, text="Удалить выбранный протокол", command=self.delete_protocol).pack(pady=5)
    
    def process_fact_values(self):
        """Обрабатывает введенные значения FactValue"""
        text = self.fact_values_text.get("1.0", tk.END).strip()
        if text:
            values = [line.strip() for line in text.split('\n') if line.strip()]
            added_count = 0
            
            for value in values:
                if value:  # Добавляем все значения, даже повторяющиеся
                    self.fact_values.append(value)
                    # Добавляем с нумерацией
                    self.fact_values_listbox.insert(tk.END, f"{len(self.fact_values)}. {value}")
                    added_count += 1
            
            # Очищаем текстовое поле после добавления
            self.fact_values_text.delete("1.0", tk.END)
            
            if added_count > 0:
                messagebox.showinfo("Успех", f"Добавлено {added_count} значений")
            else:
                messagebox.showinfo("Информация", "Не было добавлено ни одного значения")
        else:
            messagebox.showwarning("Предупреждение", "Введите значения для добавления")
    
    def remove_fact_value(self):
        """Удаляет выбранное значение из списка"""
        selected = self.fact_values_listbox.curselection()
        if selected:
            index = selected[0]
            # Удаляем из списка значений
            self.fact_values.pop(index)
            # Удаляем из Listbox
            self.fact_values_listbox.delete(index)
            
            # Перестраиваем нумерацию
            self.fact_values_listbox.delete(0, tk.END)
            for i, value in enumerate(self.fact_values, 1):
                self.fact_values_listbox.insert(tk.END, f"{i}. {value}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите значение для удаления")
    
    def update_equipment_list(self):
        self.available_equipment.delete(0, tk.END)
        for equipment in self.equipment_db:
            self.available_equipment.insert(tk.END, f"{equipment['id']} - {equipment['name']}")

    def update_testers_list(self):
    # Разделяем испытателей по ролям
        testers = [f"{t['id']} - {t['name']} ({t['post']})" for t in self.testers_db if t['role_id'] == "1"]
        approvers = [f"{t['id']} - {t['name']} ({t['post']})" for t in self.testers_db if t['role_id'] == "2"]
    
    # Обновляем комбобоксы
        self.tester1_combo['values'] = testers
        self.tester2_combo['values'] = approvers
    
    # Устанавливаем первые значения по умолчанию
        if testers:
            self.tester1_combo.current(0)
            self.update_tester1_details()
        if approvers:
            self.tester2_combo.current(0)
            self.update_tester2_details()

    def update_tester1_details(self):
        selection = self.tester1_combo.get()
        if selection:
            tester_id = selection.split(' - ')[0]
            for tester in self.testers_db:
                if tester['id'] == tester_id and tester['role_id'] == "1":
                    self.tester1_post.delete(0, tk.END)
                    self.tester1_post.insert(0, tester['post'])
                    self.tester1_role.delete(0, tk.END)
                    self.tester1_role.insert(0, tester['role_id'])
                    break

    def update_tester2_details(self):
        selection = self.tester2_combo.get()
        if selection:
            tester_id = selection.split(' - ')[0]
            for tester in self.testers_db:
                if tester['id'] == tester_id and tester['role_id'] == "2":
                    self.tester2_post.delete(0, tk.END)
                    self.tester2_post.insert(0, tester['post'])
                    self.tester2_role.delete(0, tk.END)
                    self.tester2_role.insert(0, tester['role_id'])
                    break


    
    def add_equipment(self):
        selected = self.available_equipment.curselection()
        for index in selected:
            equipment = self.available_equipment.get(index)
            # Проверяем, не добавлено ли уже это оборудование
            if equipment not in self.selected_equipment.get(0, tk.END):
                self.selected_equipment.insert(tk.END, equipment)
    
    def remove_equipment(self):
        selected = self.selected_equipment.curselection()
        for index in selected[::-1]:  # Удаляем с конца, чтобы индексы не сдвигались
            self.selected_equipment.delete(index)
    
    def add_new_equipment(self):
        def save_new_equipment():
            new_id = id_entry.get()
            new_name = name_entry.get()
            
            if new_id and new_name:
                self.equipment_db.append({"id": new_id, "name": new_name})
                self.save_equipment_db()
                self.update_equipment_list()
                new_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        
        new_window = tk.Toplevel(self.root)
        new_window.title("Добавить новое оборудование")
        new_window.geometry("300x150")
        
        ttk.Label(new_window, text="ID оборудования:").pack(pady=5)
        id_entry = ttk.Entry(new_window, width=30)
        id_entry.pack(pady=5)
        
        ttk.Label(new_window, text="Название оборудования:").pack(pady=5)
        name_entry = ttk.Entry(new_window, width=30)
        name_entry.pack(pady=5)
        
        ttk.Button(new_window, text="Сохранить", command=save_new_equipment).pack(pady=10)
    
    def add_new_tester(self):
        def save_new_tester():
            new_id = id_entry.get()
            new_name = name_entry.get()
            new_post = post_entry.get()
            role_id = role_var.get()  # Получаем выбранную роль
        
            if new_id and new_name and new_post:
                self.testers_db.append({
                    "id": new_id, 
                    "name": new_name, 
                    "post": new_post, 
                    "role_id": role_id
                })
                self.save_testers_db()
                self.update_testers_list()
                new_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
    
        new_window = tk.Toplevel(self.root)
        new_window.title("Добавить нового испытателя")
        new_window.geometry("300x250")
    
        ttk.Label(new_window, text="ID испытателя:").pack(pady=5)
        id_entry = ttk.Entry(new_window, width=30)
        id_entry.pack(pady=5)
    
        ttk.Label(new_window, text="ФИО испытателя:").pack(pady=5)
        name_entry = ttk.Entry(new_window, width=30)
        name_entry.pack(pady=5)
    
        ttk.Label(new_window, text="Должность:").pack(pady=5)
        post_entry = ttk.Entry(new_window, width=30)
        post_entry.pack(pady=5)
    
        ttk.Label(new_window, text="Роль:").pack(pady=5)
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(new_window, textvariable=role_var, values=["1 - Испытатель", "2 - Утверждающий"], state="readonly")
        role_combo.pack(pady=5)
        role_combo.current(0)
    
        ttk.Button(new_window, text="Сохранить", command=save_new_tester).pack(pady=10)


    
    def add_protocol(self):
        try:
            # Проверка на уникальность номера протокола
            doc_id = self.doc_id.get()
            for protocol in self.protocols:
                if protocol['doc_id'] == doc_id:
                    messagebox.showerror("Ошибка", "Протокол с таким номером уже существует")
                    return
            
            # Получаем выбранное оборудование
            selected_equipment = [eq.split(' - ')[0] for eq in self.selected_equipment.get(0, tk.END)]
            
            # Получаем данные испытателей
            tester1_id = self.tester1_combo.get().split(' - ')[0] if self.tester1_combo.get() else ""
            tester2_id = self.tester2_combo.get().split(' - ')[0] if self.tester2_combo.get() else ""
            
            # Создаем список ResearchObjectInfo
            research_objects = []
            for fact_value in self.fact_values:
                research_objects.append({
                    'indicator_id': self.indicator_id.get(),
                    'fact_value': fact_value,
                    'measurement_id': self.measurement_id.get(),
                    'unique_method': self.unique_method.get(),
                    'doc_name_methodik_id': self.doc_name_methodik_id.get()
                })
            
            protocol = {
                'doc_id': doc_id,
                'doc_creation_date': self.doc_creation_date.get(),
                'doc_start_date': self.doc_start_date,
                'doc_validity_date': self.doc_validity_date,
                'data_status_id': self.data_status_id,
                'protocol_status_id': self.protocol_status_id,
                'territory_feature': self.territory_feature,
                'address_text': self.address_text.get(),
                'id_code_oksm': self.id_code_oksm,
                'id_addr_type': self.id_addr_type,
                'application_date': self.application_date.get(),
                'customer_kind_id': self.customer_kind_id.get(),
                'inn_id': self.inn_id.get(),
                'ogrn_id': self.ogrn_id.get(),
                'phone_number': self.phone_number.get(),
                'is_rf': self.is_rf,
                'equipment_ids': selected_equipment,
                'approved_users': [
                    {
                        'id': tester1_id,
                        'post': self.tester1_post.get(),
                        'role': self.tester1_role.get()
                    },
                    {
                        'id': tester2_id,
                        'post': self.tester2_post.get(),
                        'role': self.tester2_role.get()
                    }
                ],
                'type_object_id': self.type_object_id.get(),
                'method_doc_id': self.method_doc_id.get(),
                'full_name_object': self.full_name_object.get(),
                'research_objects': research_objects,
                'is_lab': self.is_lab,
                'is_another_doc': self.is_another_doc,
                'pdf_file_name': os.path.basename(self.pdf_file_path) if self.pdf_file_path else "",
                'pdf_base64': self.pdf_base64 if self.pdf_base64 else ""
            }
            
            # Проверка обязательных полей
            if not protocol['doc_id']:
                messagebox.showerror("Ошибка", "Номер протокола обязателен для заполнения")
                return
            
            if not research_objects:
                messagebox.showerror("Ошибка", "Добавьте хотя бы одно значение FactValue")
                return
                
            self.protocols.append(protocol)
            
            # Добавляем информацию о PDF в отображение
            pdf_info = " (с PDF)" if self.pdf_file_path else " (без PDF)"
            self.protocols_listbox.insert(tk.END, f"{protocol['doc_id']} - {protocol['full_name_object']} ({len(research_objects)} значений){pdf_info}")
            messagebox.showinfo("Успех", f"Протокол добавлен в список с {len(research_objects)} значениями")
            
            # Очищаем окно "Добавленные значения FactValue"
            self.fact_values = []
            self.fact_values_listbox.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении протокола: {str(e)}")
    
    def clear_form(self):
        # Очистка всех полей
        self.doc_id.delete(0, tk.END)
        self.doc_creation_date.delete(0, tk.END)
        self.doc_creation_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.address_text.delete(0, tk.END)
        self.application_date.delete(0, tk.END)
        self.customer_kind_id.delete(0, tk.END)
        self.customer_kind_id.insert(0, "1")
        self.inn_id.delete(0, tk.END)
        self.ogrn_id.delete(0, tk.END)
        self.phone_number.delete(0, tk.END)
        
        # Очищаем выбранное оборудование
        self.selected_equipment.delete(0, tk.END)
        
        # Сбрасываем испытателей
        self.update_testers_list()
        
        self.type_object_id.delete(0, tk.END)
        self.type_object_id.insert(0, "8")
        self.method_doc_id.delete(0, tk.END)
        self.method_doc_id.insert(0, "4505258")
        self.full_name_object.delete(0, tk.END)
        self.full_name_object.insert(0, "Электромагнитное поле СВЧ-диапазона, создаваемое излучающими техническими средствами базовой станции")
        self.indicator_id.delete(0, tk.END)
        self.indicator_id.insert(0, "125893")
        
        # Очищаем фактические значения
        self.fact_values_text.delete("1.0", tk.END)
        self.fact_values_listbox.delete(0, tk.END)
        self.fact_values = []
        
        self.measurement_id.delete(0, tk.END)
        self.measurement_id.insert(0, "680")
        self.unique_method.delete(0, tk.END)
        self.unique_method.insert(0, "МУК 4.3.3830-22 «Определение уровней электромагнитного поля, создаваемого излучающими техническими средствами телевидения, ЧМ радиовещания и базовых станций сухопутной подвижной радиосвязи»")
        self.doc_name_methodik_id.delete(0, tk.END)
        self.doc_name_methodik_id.insert(0, "497")
        
        # Очищаем PDF файл
        self.clear_pdf_file()
    
    def delete_protocol(self):
        selected = self.protocols_listbox.curselection()
        if selected:
            index = selected[0]
            self.protocols_listbox.delete(index)
            self.protocols.pop(index)
            messagebox.showinfo("Успех", "Протокол удален")
        else:
            messagebox.showwarning("Предупреждение", "Выберите протокол для удаления")
    
    def save_to_xml(self):
        if not self.protocols:
            messagebox.showwarning("Предупреждение", "Нет протоколов для сохранения")
            return
            
        try:
            # Создаем корневой элемент
            root = ET.Element("root")
            
            for protocol in self.protocols:
                # Создаем элемент протокола
                protocol_elem = ET.SubElement(root, "protocol")
                
                # Основная информация
                ET.SubElement(protocol_elem, "DocId").text = protocol['doc_id']
                ET.SubElement(protocol_elem, "DocCreationDate").text = protocol['doc_creation_date']
                ET.SubElement(protocol_elem, "DocStartDate").text = protocol['doc_start_date']
                ET.SubElement(protocol_elem, "DocValidityDate").text = protocol['doc_validity_date']
                ET.SubElement(protocol_elem, "DataStatusId").text = protocol['data_status_id']
                ET.SubElement(protocol_elem, "ProtocolStatusId").text = protocol['protocol_status_id']
                
                # Добавляем блок ProtocolScan после ProtocolStatusId и перед TerritoryFeature
                if protocol['pdf_base64']:
                    protocol_scan = ET.SubElement(protocol_elem, "ProtocolScan")
                    ET.SubElement(protocol_scan, "Extension").text = "pdf"
                    ET.SubElement(protocol_scan, "FileName").text = protocol['pdf_file_name']
                    ET.SubElement(protocol_scan, "Content").text = protocol['pdf_base64']
                
                ET.SubElement(protocol_elem, "TerritoryFeature").text = str(protocol['territory_feature']).lower()
                
                # Адрес
                address = ET.SubElement(protocol_elem, "Address")
                address_details = ET.SubElement(address, "AddressDetails")
                ET.SubElement(address_details, "idCodeOksm").text = protocol['id_code_oksm']
                ET.SubElement(address_details, "IdAddrType").text = protocol['id_addr_type']
                ET.SubElement(address_details, "UniqueAddress").text = "true" if protocol['address_text'] else "false"
                if protocol['address_text']:
                    ET.SubElement(address_details, "UniqueAddressText").text = protocol['address_text']
                
                # Дата заявки
                ET.SubElement(protocol_elem, "ApplicationDate").text = protocol['application_date']
                
                # Заказчик
                customer = ET.SubElement(protocol_elem, "Customer")
                ET.SubElement(customer, "CustomerKindId").text = protocol['customer_kind_id']
                ET.SubElement(customer, "InnId").text = protocol['inn_id']
                ET.SubElement(customer, "OgrnId").text = protocol['ogrn_id']
                
                # Телефон
                phones = ET.SubElement(customer, "Phones")
                phone_details = ET.SubElement(phones, "PhoneDetails")
                ET.SubElement(phone_details, "Number").text = protocol['phone_number']
                ET.SubElement(phone_details, "IsRf").text = str(protocol['is_rf']).lower()
                
                # Оборудование
                equipment = ET.SubElement(protocol_elem, "Equipment")
                for eq_id in protocol['equipment_ids']:
                    equipment_details = ET.SubElement(equipment, "EquipmentDetails")
                    ET.SubElement(equipment_details, "EquipmentId").text = eq_id
                
                # Исполнители
                approved_user = ET.SubElement(protocol_elem, "ApprovedUser")
                for user in protocol['approved_users']:
                    if user['id']:  # Добавляем только если указан ID
                        approved_user_details = ET.SubElement(approved_user, "ApprovedUserDetails")
                        ET.SubElement(approved_user_details, "idFullName").text = user['id']
                        ET.SubElement(approved_user_details, "PostName").text = user['post']
                        ET.SubElement(approved_user_details, "idRoleName").text = user['role']
                
                # Информация об объекте
                object_info = ET.SubElement(protocol_elem, "ObjectInfo")
                ET.SubElement(object_info, "TypeObjectId").text = protocol['type_object_id']
                ET.SubElement(object_info, "MethodDocId").text = protocol['method_doc_id']
                ET.SubElement(object_info, "FullNameObject").text = protocol['full_name_object']
                
                # Исследования - создаем несколько ResearchObjectInfo
                research_object = ET.SubElement(object_info, "ResearchObject")
                for research_obj in protocol['research_objects']:
                    research_object_info = ET.SubElement(research_object, "ResearchObjectInfo")
                    ET.SubElement(research_object_info, "IndicatorId").text = research_obj['indicator_id']
                    ET.SubElement(research_object_info, "FactValue").text = research_obj['fact_value']
                    ET.SubElement(research_object_info, "MeasurementId").text = research_obj['measurement_id']
                    ET.SubElement(research_object_info, "UniqueMethod").text = research_obj['unique_method']
                    ET.SubElement(research_object_info, "DocNameMethodikId").text = research_obj['doc_name_methodik_id']
                
                ET.SubElement(object_info, "IsLab").text = str(protocol['is_lab']).lower()
                ET.SubElement(object_info, "IsAnotherDoc").text = str(protocol['is_another_doc']).lower()
            
            # Форматируем XML
            rough_string = ET.tostring(root, encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
            
            # Сохраняем в файл
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(pretty_xml)
                messagebox.showinfo("Успех", f"Файл сохранен: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении XML: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProtocolApp(root)
    root.mainloop()