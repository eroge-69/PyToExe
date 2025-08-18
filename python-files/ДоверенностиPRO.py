import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from fpdf import FPDF
import os
import datetime
import winreg

class PowerOfAttorneyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Доверенности PRO")
        self.root.geometry("900x700")
        self.root.iconbitmap(self.get_icon_path())
        
        # Создаем папку для шаблонов в AppData
        self.app_data_path = os.path.join(os.getenv('APPDATA'), 'ДоверенностиPRO')
        os.makedirs(self.app_data_path, exist_ok=True)
        
        # База данных
        self.db_path = os.path.join(self.app_data_path, 'poa_database.db')
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        
        # Переменные
        self.current_id = None
        self.templates = self.load_templates()
        
        # Стили
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#F0F8FF')
        self.style.configure('TButton', background='#4682B4', foreground='white', font=('Arial', 10))
        self.style.configure('Header.TLabel', background='#4682B4', foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure('TLabel', background='#F0F8FF', font=('Arial', 9))
        self.style.map('TButton', background=[('active', '#5A9BD3')])
        
        # Главный фрейм
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Создание виджетов
        self.create_widgets()
        self.load_last_template()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_icon_path(self):
        # Создаем временный файл иконки
        icon_path = os.path.join(os.getenv('TEMP'), 'poa_icon.ico')
        if not os.path.exists(icon_path):
            # Здесь должна быть бинарная data иконки, но для примера просто создаем файл
            open(icon_path, 'wb').close()
        return icon_path

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS templates (
                            id INTEGER PRIMARY KEY,
                            template_name TEXT,
                            issue_date TEXT,
                            valid_until TEXT,
                            organization_name TEXT,
                            organization_inn TEXT,
                            organization_kpp TEXT,
                            organization_address TEXT,
                            bank_name TEXT,
                            bank_account TEXT,
                            bank_bik TEXT,
                            bank_corr TEXT,
                            attorney_name TEXT,
                            passport_data TEXT,
                            receiver_name TEXT,
                            receiver_inn TEXT,
                            basis TEXT,
                            product_name TEXT,
                            unit TEXT,
                            quantity TEXT,
                            director TEXT,
                            accountant TEXT,
                            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def create_widgets(self):
        # Панель истории
        history_frame = ttk.LabelFrame(self.main_frame, text="История доверенностей")
        history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Панель прокрутки
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(
            history_frame, 
            width=30, 
            height=20,
            yscrollcommand=scrollbar.set,
            font=('Arial', 9)
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_listbox.bind('<<ListboxSelect>>', self.load_selected_template)
        
        scrollbar.config(command=self.history_listbox.yview)
        
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.load_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_template).pack(side=tk.LEFT, padx=2)
        
        # Форма ввода
        form_frame = ttk.LabelFrame(self.main_frame, text="Данные доверенности")
        form_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Создаем canvas и скроллбар для формы
        canvas = tk.Canvas(form_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        fields = [
            ("Номер доверенности*:", "number"),
            ("Дата выдачи*:", "issue_date", "Пример: 24 июля 2025 г"),
            ("Действительна до*:", "valid_until", "Пример: 01 сентября 2025 г"),
            ("Организация*:", "organization_name"),
            ("ИНН/КПП*:", "organization_inn_kpp", "Пример: 5040142547 / 770701001"),
            ("Адрес организации*:", "organization_address"),
            ("Банк*:", "bank_name"),
            ("Расчетный счет*:", "bank_account"),
            ("БИК*:", "bank_bik"),
            ("Корр. счет*:", "bank_corr"),
            ("Доверенность выдана*:", "attorney_name", "Пример: Одинцов Максим Олегович"),
            ("Паспортные данные*:", "passport_data", "Пример: 4514 584335 выд. Отделом УФМС..."),
            ("Получить от*:", "receiver_name", "Пример: ИП Вербицкая Елена Александровна"),
            ("ИНН получателя:", "receiver_inn"),
            ("Основание*:", "basis", "Пример: Счет на оплату № 88 от 18 июля 2025 г"),
            ("Товар*:", "product_name", "Пример: Крахмал 25 кг мешок"),
            ("Ед. измерения*:", "unit", "Пример: шт"),
            ("Количество*:", "quantity", "Пример: три (прописью)"),
            ("Руководитель*:", "director", "Пример: С.С. Соловьева"),
            ("Гл. бухгалтер*:", "accountant", "Пример: С.С. Соловьева")
        ]
        
        self.entries = {}
        for i, field in enumerate(fields):
            label = field[0]
            field_key = field[1]
            hint = field[2] if len(field) > 2 else ""
            
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=3)
            
            lbl = ttk.Label(row_frame, text=label, width=25, anchor="e")
            lbl.pack(side=tk.LEFT, padx=(0, 5))
            
            entry = ttk.Entry(row_frame, width=40)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            if hint:
                entry.insert(0, hint)
                entry.config(foreground='grey')
                entry.bind("<FocusIn>", lambda e, entry=entry, hint=hint: self.on_entry_focus_in(e, entry, hint))
                entry.bind("<FocusOut>", lambda e, entry=entry, hint=hint: self.on_entry_focus_out(e, entry, hint))
            
            self.entries[field_key] = entry
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Button(btn_frame, text="Сохранить шаблон", command=self.save_template).pack(side=tk.LEFT, padx=5, ipadx=10)
        ttk.Button(btn_frame, text="Создать PDF", command=self.generate_pdf, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5, ipadx=20)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_form).pack(side=tk.LEFT, padx=5, ipadx=10)
        
        # Создаем стиль для акцентной кнопки
        self.style.configure('Accent.TButton', background='#4CAF50', foreground='white')
        self.style.map('Accent.TButton', background=[('active', '#66BB6A')])
        
        # Загрузка истории
        self.load_history()

    def on_entry_focus_in(self, event, entry, hint):
        if entry.get() == hint:
            entry.delete(0, tk.END)
            entry.config(foreground='black')

    def on_entry_focus_out(self, event, entry, hint):
        if not entry.get():
            entry.insert(0, hint)
            entry.config(foreground='grey')

    def load_templates(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM templates ORDER BY last_used DESC")
        return cursor.fetchall()

    def load_history(self):
        self.templates = self.load_templates()
        self.history_listbox.delete(0, tk.END)
        for template in self.templates:
            self.history_listbox.insert(tk.END, f"{template[1]} ({template[2]})")

    def load_selected_template(self, event):
        selection = self.history_listbox.curselection()
        if not selection:
            return
            
        template = self.templates[selection[0]]
        self.current_id = template[0]
        
        # Обновляем время использования
        cursor = self.conn.cursor()
        cursor.execute("UPDATE templates SET last_used = CURRENT_TIMESTAMP WHERE id = ?", (self.current_id,))
        self.conn.commit()
        
        # Заполняем форму
        fields = [
            'number', 'issue_date', 'valid_until', 'organization_name',
            'organization_inn_kpp', 'organization_address', 'bank_name',
            'bank_account', 'bank_bik', 'bank_corr', 'attorney_name',
            'passport_data', 'receiver_name', 'receiver_inn', 'basis',
            'product_name', 'unit', 'quantity', 'director', 'accountant'
        ]
        
        # Формируем значение для ИНН/КПП
        inn_kpp = f"{template[5] or ''} / {template[6] or ''}".strip()
        if inn_kpp == " / ": inn_kpp = ""
        
        values = [
            template[1],  # number
            template[2],  # issue_date
            template[3],  # valid_until
            template[4],  # organization_name
            inn_kpp,      # organization_inn_kpp
            template[7],  # organization_address
            template[8],  # bank_name
            template[9],  # bank_account
            template[10], # bank_bik
            template[11], # bank_corr
            template[12], # attorney_name
            template[13], # passport_data
            template[14], # receiver_name
            template[15], # receiver_inn
            template[16], # basis
            template[17], # product_name
            template[18], # unit
            template[19], # quantity
            template[20], # director
            template[21]  # accountant
        ]
        
        for field, value in zip(fields, values):
            self.entries[field].delete(0, tk.END)
            if value:
                self.entries[field].insert(0, str(value))
                self.entries[field].config(foreground='black')

    def delete_template(self):
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите шаблон для удаления!")
            return
            
        if not messagebox.askyesno("Подтверждение", "Удалить выбранный шаблон?"):
            return
            
        template_id = self.templates[selection[0]][0]
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        self.conn.commit()
        
        self.load_history()
        if self.current_id == template_id:
            self.clear_form()
        messagebox.showinfo("Удалено", "Шаблон успешно удален!")

    def load_last_template(self):
        if self.templates:
            self.history_listbox.selection_set(0)
            self.load_selected_template(None)

    def save_template(self):
        data = {field: entry.get() for field, entry in self.entries.items()}
        
        # Проверка обязательных полей
        required_fields = ['number', 'issue_date', 'valid_until', 'organization_name',
                          'organization_inn_kpp', 'organization_address', 'bank_name',
                          'bank_account', 'bank_bik', 'bank_corr', 'attorney_name',
                          'passport_data', 'receiver_name', 'basis', 'product_name',
                          'unit', 'quantity', 'director', 'accountant']
        
        missing = [field for field in required_fields if not data[field] or data[field] == self.get_hint(field)]
        if missing:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля (помеченные *)!")
            return
            
        cursor = self.conn.cursor()
        
        # Разделяем ИНН/КПП
        inn_kpp = data['organization_inn_kpp'].split('/')
        inn = inn_kpp[0].strip() if len(inn_kpp) > 0 else ""
        kpp = inn_kpp[1].strip() if len(inn_kpp) > 1 else ""
        
        if self.current_id:
            # Обновление существующего шаблона
            cursor.execute('''UPDATE templates SET
                            template_name = ?, issue_date = ?, valid_until = ?,
                            organization_name = ?, organization_inn = ?, organization_kpp = ?,
                            organization_address = ?, bank_name = ?, bank_account = ?,
                            bank_bik = ?, bank_corr = ?, attorney_name = ?,
                            passport_data = ?, receiver_name = ?, receiver_inn = ?,
                            basis = ?, product_name = ?, unit = ?, quantity = ?,
                            director = ?, accountant = ?, last_used = CURRENT_TIMESTAMP
                            WHERE id = ?''', 
                           (data['number'], data['issue_date'], data['valid_until'],
                            data['organization_name'], inn, kpp,
                            data['organization_address'], data['bank_name'], data['bank_account'],
                            data['bank_bik'], data['bank_corr'], data['attorney_name'],
                            data['passport_data'], data['receiver_name'], data['receiver_inn'],
                            data['basis'], data['product_name'], data['unit'], data['quantity'],
                            data['director'], data['accountant'], self.current_id))
        else:
            # Создание нового шаблона
            cursor.execute('''INSERT INTO templates (
                            template_name, issue_date, valid_until,
                            organization_name, organization_inn, organization_kpp,
                            organization_address, bank_name, bank_account,
                            bank_bik, bank_corr, attorney_name,
                            passport_data, receiver_name, receiver_inn,
                            basis, product_name, unit, quantity,
                            director, accountant)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (data['number'], data['issue_date'], data['valid_until'],
                            data['organization_name'], inn, kpp,
                            data['organization_address'], data['bank_name'], data['bank_account'],
                            data['bank_bik'], data['bank_corr'], data['attorney_name'],
                            data['passport_data'], data['receiver_name'], data['receiver_inn'],
                            data['basis'], data['product_name'], data['unit'], data['quantity'],
                            data['director'], data['accountant']))
            self.current_id = cursor.lastrowid
        
        self.conn.commit()
        self.load_history()
        messagebox.showinfo("Сохранено", "Шаблон успешно сохранен!")

    def get_hint(self, field):
        hints = {
            'issue_date': "Пример: 24 июля 2025 г",
            'valid_until': "Пример: 01 сентября 2025 г",
            'organization_inn_kpp': "Пример: 5040142547 / 770701001",
            'attorney_name': "Пример: Одинцов Максим Олегович",
            'passport_data': "Пример: 4514 584335 выд. Отделом УФМС...",
            'receiver_name': "Пример: ИП Вербицкая Елена Александровна",
            'basis': "Пример: Счет на оплату № 88 от 18 июля 2025 г",
            'product_name': "Пример: Крахмал 25 кг мешок",
            'unit': "Пример: шт",
            'quantity': "Пример: три (прописью)",
            'director': "Пример: С.С. Соловьева",
            'accountant': "Пример: С.С. Соловьева"
        }
        return hints.get(field, "")

    def clear_form(self):
        for field, entry in self.entries.items():
            entry.delete(0, tk.END)
            hint = self.get_hint(field)
            if hint:
                entry.insert(0, hint)
                entry.config(foreground='grey')
        self.current_id = None

    def generate_pdf(self):
        data = {field: entry.get() for field, entry in self.entries.items()}
        
        # Проверка обязательных полей
        required_fields = ['number', 'issue_date', 'valid_until', 'organization_name',
                          'organization_inn_kpp', 'organization_address', 'bank_name',
                          'bank_account', 'bank_bik', 'bank_corr', 'attorney_name',
                          'passport_data', 'receiver_name', 'basis', 'product_name',
                          'unit', 'quantity', 'director', 'accountant']
        
        missing = [field for field in required_fields if not data[field] or data[field] == self.get_hint(field)]
        if missing:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля (помеченные *)!")
            return
            
        # Запрашиваем место сохранения
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Доверенность_{data['number']}.pdf"
        )
        
        if not file_path:
            return
            
        # Создаем PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Добавляем шрифт для кириллицы (используем стандартный шрифт)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 10)
        
        # Шапка документа
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, f"ДОВЕРЕННОСТЬ № {data['number']}", ln=1, align='C')
        pdf.set_font('DejaVu', '', 10)
        
        pdf.cell(50, 8, "Дата выдачи:", ln=0)
        pdf.cell(0, 8, data['issue_date'], ln=1)
        
        pdf.cell(50, 8, "Действительна по:", ln=0)
        pdf.cell(0, 8, data['valid_until'], ln=1)
        
        # Организация
        pdf.ln(5)
        pdf.cell(0, 8, f"{data['organization_name']}, ИНН/КПП {data['organization_inn_kpp']}", ln=1)
        pdf.cell(0, 8, f"Адрес: {data['organization_address']}", ln=1)
        
        # Банковские реквизиты
        pdf.ln(5)
        pdf.cell(0, 8, f"Банк: {data['bank_name']}", ln=1)
        pdf.cell(0, 8, f"Р/с: {data['bank_account']}, БИК: {data['bank_bik']}, К/с: {data['bank_corr']}", ln=1)
        
        # Основной текст
        pdf.ln(10)
        pdf.cell(0, 8, f"Доверенность выдана: {data['attorney_name']}", ln=1)
        pdf.cell(0, 8, f"Паспорт: {data['passport_data']}", ln=1)
        pdf.cell(0, 8, f"На получение от: {data['receiver_name']}{', ИНН ' + data['receiver_inn'] if data['receiver_inn'] else ''}", ln=1)
        pdf.cell(0, 8, f"материальных ценностей по: {data['basis']}", ln=1)
        
        # Таблица товаров
        pdf.ln(10)
        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 8, "Перечень товарно-материальных ценностей, подлежащих получению", ln=1)
        pdf.set_font('DejaVu', '', 10)
        
        col_widths = [15, 80, 30, 50]
        
        # Заголовки таблицы
        headers = ["№", "Материальные ценности", "Ед. измерения", "Количество"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1)
        pdf.ln()
        
        # Данные товара
        pdf.cell(col_widths[0], 8, "1", border=1)
        pdf.cell(col_widths[1], 8, data['product_name'], border=1)
        pdf.cell(col_widths[2], 8, data['unit'], border=1)
        pdf.cell(col_widths[3], 8, data['quantity'], border=1)
        pdf.ln()
        
        # Подписи
        pdf.ln(15)
        pdf.cell(90, 8, "Руководитель ___________________", ln=0)
        pdf.cell(0, 8, data['director'], ln=1)
        
        pdf.cell(90, 8, "Главный бухгалтер ___________________", ln=0)
        pdf.cell(0, 8, data['accountant'], ln=1)
        
        # Сохраняем PDF
        pdf.output(file_path)
        messagebox.showinfo("Готово", f"PDF-документ успешно создан:\n{file_path}")

    def on_close(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerOfAttorneyApp(root)
    root.mainloop()