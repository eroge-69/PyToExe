import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import os
import csv
from zipfile import ZipFile

class MedicalExaminationManager:
    def __init__(self):
        self.employees_file = "список сотрудников.csv"
        self.signers_file = "подписанты.csv"
        self.settings_file = "настройки.csv"
        self.archive_password = self.load_password()
        self.db_file = "medical_examinations.db"
        
        self.init_files()
        self.init_database()
        
    def load_password(self):
        """Загрузка пароля из файла настроек"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        return row.get('Пароль', 'medical123')
        except:
            pass
        return 'medical123'
    
    def save_password(self, password):
        """Сохранение пароля в файл настроек"""
        try:
            with open(self.settings_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Пароль'])
                writer.writerow([password])
            self.archive_password = password
            return True
        except Exception as e:
            print(f"Ошибка сохранения пароля: {e}")
            return False
        
    def init_files(self):
        """Инициализация CSV файлов если они не существуют"""
        if not os.path.exists(self.employees_file):
            with open(self.employees_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ФИО', 'Год_рождения'])
        
        if not os.path.exists(self.signers_file):
            with open(self.signers_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ФИО', 'Должность'])
                writer.writerow(['М.Б. Шалимов', 'заместитель главного врача по ОВ'])
        
    def init_database(self):
        """Инициализация SQLite базы данных"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT UNIQUE,
                birth_year INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                position TEXT,
                UNIQUE(full_name, position)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS examinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                employee_id INTEGER,
                result TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Загружаем данные из CSV если база пустая
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            self.load_employees_from_csv()
        
        cursor.execute("SELECT COUNT(*) FROM signers")
        if cursor.fetchone()[0] == 0:
            self.load_signers_from_csv()
        
        conn.commit()
        conn.close()
    
    def load_employees_from_csv(self):
        """Загрузка сотрудников из CSV файла в базу данных"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                for row in reader:
                    if row['ФИО'] and row['Год_рождения']:
                        cursor.execute(
                            "INSERT OR IGNORE INTO employees (full_name, birth_year) VALUES (?, ?)",
                            (row['ФИО'], int(row['Год_рождения']))
                        )
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")
        return False
    
    def load_signers_from_csv(self):
        """Загрузка подписантов из CSV файла в базу данных"""
        try:
            with open(self.signers_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                for row in reader:
                    if row['ФИО'] and row['Должность']:
                        cursor.execute(
                            "INSERT OR IGNORE INTO signers (full_name, position) VALUES (?, ?)",
                            (row['ФИО'], row['Должность'])
                        )
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Ошибка загрузки подписантов: {e}")
        return False
    
    def get_all_employees(self):
        """Получение всех сотрудников"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, birth_year FROM employees ORDER BY full_name")
        employees = cursor.fetchall()
        conn.close()
        return employees
    
    def get_all_signers(self):
        """Получение всех подписантов"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, position FROM signers ORDER BY full_name")
        signers = cursor.fetchall()
        conn.close()
        return signers
    
    def check_employee_duplicate(self, name, birth_year):
        """Проверка дубля сотрудника по ФИО и году рождения"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM employees WHERE full_name = ? AND birth_year = ?",
            (name, int(birth_year))
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def add_employee(self, name, birth_year):
        """Добавление нового сотрудника с проверкой дублей"""
        # Проверяем дубли
        if self.check_employee_duplicate(name, birth_year):
            return False, "Сотрудник с таким ФИО и годом рождения уже существует"
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO employees (full_name, birth_year) VALUES (?, ?)",
                (name, int(birth_year))
            )
            conn.commit()
            conn.close()
            
            # Добавляем в CSV файл
            with open(self.employees_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([name, birth_year])
            
            return True, "Сотрудник успешно добавлен"
        except Exception as e:
            return False, f"Ошибка: {e}"
    
    def add_signer(self, name, position):
        """Добавление нового подписанта"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO signers (full_name, position) VALUES (?, ?)",
                (name, position)
            )
            conn.commit()
            conn.close()
            
            # Добавляем в CSV файл
            with open(self.signers_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([name, position])
            
            return True, "Подписант успешно добавлен"
        except Exception as e:
            return False, f"Ошибка: {e}"

    def delete_signer(self, signer_id):
        """Удаление подписанта"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Получаем данные подписанта для удаления из CSV
            cursor.execute("SELECT full_name, position FROM signers WHERE id = ?", (signer_id,))
            signer = cursor.fetchone()
            
            # Удаляем из базы данных
            cursor.execute("DELETE FROM signers WHERE id = ?", (signer_id,))
            conn.commit()
            conn.close()
            
            if signer:
                # Перезаписываем CSV файл без удаленного подписанта
                signers = self.get_all_signers()
                with open(self.signers_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ФИО', 'Должность'])
                    for signer_id, name, position in signers:
                        writer.writerow([name, position])
            
            return True, "Подписант успешно удален"
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"
    
    def add_examination(self, employee_id, date, result="Прошел предсменный медицинский осмотр, к исполнению трудовых обязанностей допущен."):
        """Добавление записи о медосмотре"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO examinations (date, employee_id, result) VALUES (?, ?, ?)",
                (date, employee_id, result)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении осмотра: {e}")
            return False
    
    def create_daily_report(self, date, selected_employees, signer_id, report_format="html"):
        """Создание отчета за день в выбранном формате"""
        if date is None:
            date = datetime.now().strftime("%d.%m.%Y")
            db_date = datetime.now().strftime("%Y-%m-%d")
        else:
            db_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        
        if not selected_employees:
            return False, "Не выбраны сотрудники для отчета"
        
        # Получаем данные подписанта
        signer = self.get_signer_by_id(signer_id)
        if not signer:
            return False, "Не выбран подписант"
        
        try:
            return self._create_html_report(date, db_date, selected_employees, signer)
        except Exception as e:
            return False, f"Ошибка при создании отчета: {e}"
    
    def get_signer_by_id(self, signer_id):
        """Получение подписанта по ID"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, position FROM signers WHERE id = ?", (signer_id,))
        signer = cursor.fetchone()
        conn.close()
        return signer
    
    def _create_html_report(self, date, db_date, selected_employees, signer):
        """Создание отчета в формате HTML с полной шапкой"""
        report_filename = f"Медосмотры_{date.replace('.', '_')}.html"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Медосмотры</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 14px; margin: 5px 0; font-weight: normal; }
        .header .title { font-weight: bold; font-size: 16px; margin: 20px 0; }
        .header .date { font-weight: bold; font-size: 14px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #000; padding: 8px; text-align: left; font-size: 12px; }
        th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
        .signature { margin-top: 50px; text-align: right; }
        .signature-line { border-top: 1px solid #000; width: 200px; margin-left: auto; margin-top: 40px; }
        .page-break { page-break-after: always; }
    </style>
</head>
<body>
''')
            # Шапка учреждения
            f.write('''    <div class="header">
        <h1>Санкт-Петербургское государственное автономное учреждение здравоохранения "Городская поликлиника №81"</h1>
        <h1>196068, г.Санкт-Петербург, ул. Казанская, д. 54 лит. А</h1>
        <h1>тел.: +7 812 31-777-13                       E-mail: p81@zdrav.spb.ru</h1>
        <div class="title">Сведения о прохождении</div>
        <div class="title">предсменных (предрейсовых) медицинских осмотров</div>
        <div class="date">за ''' + date + ''' г.</div>
    </div>
''')
            
            f.write('    <table>\n')
            f.write('        <tr>\n')
            f.write('            <th width="5%">№ п/п</th>\n')
            f.write('            <th width="15%">Дата</th>\n')
            f.write('            <th width="30%">Ф.И.О. водителя</th>\n')
            f.write('            <th width="15%">Год рождения</th>\n')
            f.write('            <th width="35%">Заключение</th>\n')
            f.write('        </tr>\n')
            
            for i, (emp_id, name, birth_year) in enumerate(selected_employees, 1):
                f.write('        <tr>\n')
                f.write(f'            <td align="center">{i}</td>\n')
                f.write(f'            <td>{db_date}</td>\n')
                f.write(f'            <td>{name}</td>\n')
                f.write(f'            <td>{birth_year}</td>\n')
                f.write(f'            <td>Прошел предсменный (предрейсовый) медицинский осмотр, к исполнению трудовых обязанностей допущен.</td>\n')
                f.write('        </tr>\n')
                self.add_examination(emp_id, db_date)
            
            f.write('    </table>\n')
            
            # Подпись
            f.write('    <div class="signature">\n')
            f.write(f'        <div>{signer[1]}</div>\n')
            f.write('        <div class="signature-line"></div>\n')
            f.write(f'        <div>{signer[0]}</div>\n')
            f.write('    </div>\n')
            
            f.write(f'    <div style="margin-top: 30px; text-align: center;">Всего сотрудников: {len(selected_employees)}</div>\n')
            f.write('</body>\n</html>')
        
        return True, f"HTML отчет создан: {report_filename}\nВсего сотрудников в отчете: {len(selected_employees)}"
    
    def archive_files(self, date=None):
        """Архивирование файлов - только HTML отчет"""
        if date is None:
            date = datetime.now().strftime("%d.%m.%Y")
        
        zip_filename = f"Архив_медосмотров_{date.replace('.', '_')}.zip"
        
        try:
            with ZipFile(zip_filename, 'w') as zipf:
                # Добавляем только HTML отчет
                report_file = f"Медосмотры_{date.replace('.', '_')}.html"
                if os.path.exists(report_file):
                    zipf.write(report_file)
            
            return True, f"Архив создан: {zip_filename}\nПароль: {self.archive_password}"
            
        except Exception as e:
            return False, f"Ошибка при создании архива: {e}"
    
    def get_statistics(self, start_date, end_date):
        """Получение статистики за период"""
        try:
            start_db = datetime.strptime(start_date, "%d.%m.%Y").strftime("%Y-%m-%d")
            end_db = datetime.strptime(end_date, "%d.%m.%Y").strftime("%Y-%m-%d")
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(DISTINCT employee_id) 
                FROM examinations 
                WHERE date BETWEEN ? AND ?
            ''', (start_db, end_db))
            unique_employees = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) 
                FROM examinations 
                WHERE date BETWEEN ? AND ?
            ''', (start_db, end_db))
            total_examinations = cursor.fetchone()[0]
            
            conn.close()
            
            return f"Статистика за период с {start_date} по {end_date}:\n" \
                   f"Всего осмотров: {total_examinations}\n" \
                   f"Уникальных сотрудников: {unique_employees}"
                   
        except Exception as e:
            return f"Ошибка при получении статистики: {e}"

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("СПБ ГАУЗ 'Городская поликлиника №81' - Учет предсменных медицинских осмотров")
        self.root.geometry("900x700")
        
        self.manager = MedicalExaminationManager()
        self.selected_employees = []
        
        self.create_widgets()
        self.load_employees_list()
        self.load_signers_list()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок с названием учреждения
        title_label = ttk.Label(main_frame, 
                               text="СПБ ГАУЗ 'Городская поликлиника №81'\nУчет предсменных медицинских осмотров", 
                               font=("Arial", 14, "bold"),
                               justify='center')
        title_label.pack(pady=(0, 20))
        
        # Раздел добавления сотрудников
        add_frame = ttk.LabelFrame(main_frame, text="Добавление нового сотрудника", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        name_frame = ttk.Frame(add_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="ФИО:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(name_frame, text="Год рождения:").pack(side=tk.LEFT, padx=(0, 5))
        self.birth_entry = ttk.Entry(name_frame, width=10)
        self.birth_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(name_frame, text="Добавить сотрудника", 
                  command=self.add_employee).pack(side=tk.LEFT)
        
        # Раздел управления подписантами
        signer_frame = ttk.LabelFrame(main_frame, text="Управление подписантами", padding="10")
        signer_frame.pack(fill=tk.X, pady=(0, 10))
        
        signer_inner_frame = ttk.Frame(signer_frame)
        signer_inner_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(signer_inner_frame, text="ФИО:").pack(side=tk.LEFT, padx=(0, 5))
        self.signer_name_entry = ttk.Entry(signer_inner_frame, width=30)
        self.signer_name_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(signer_inner_frame, text="Должность:").pack(side=tk.LEFT, padx=(0, 5))
        self.signer_position_entry = ttk.Entry(signer_inner_frame, width=30)
        self.signer_position_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(signer_inner_frame, text="Добавить подписанта", 
                  command=self.add_signer).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(signer_inner_frame, text="Удалить выбранного", 
                  command=self.delete_signer).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(signer_inner_frame, text="Изменить пароль архива", 
                  command=self.change_password).pack(side=tk.LEFT)
        
        # Раздел выбора сотрудников для отчета
        selection_frame = ttk.LabelFrame(main_frame, text="Выбор сотрудников для отчета", padding="10")
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="Все сотрудники:").grid(row=0, column=0, sticky=tk.W)
        self.employees_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=8)
        self.employees_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        ttk.Button(button_frame, text="→ Добавить", 
                  command=self.add_to_selection).pack(pady=5)
        ttk.Button(button_frame, text="← Удалить", 
                  command=self.remove_from_selection).pack(pady=5)
        ttk.Button(button_frame, text="Выбрать всех", 
                  command=self.select_all).pack(pady=5)
        ttk.Button(button_frame, text="Очистить", 
                  command=self.clear_selection).pack(pady=5)
        
        ttk.Label(list_frame, text="Выбранные для отчета:").grid(row=0, column=2, sticky=tk.W)
        self.selected_listbox = tk.Listbox(list_frame, height=8)
        self.selected_listbox.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(2, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Раздел создания отчета
        report_frame = ttk.LabelFrame(main_frame, text="Создание отчета", padding="10")
        report_frame.pack(fill=tk.X, pady=(0, 10))
        
        report_top_frame = ttk.Frame(report_frame)
        report_top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(report_top_frame, text="Дата отчета:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = ttk.Entry(report_top_frame, width=12)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(report_top_frame, text="Подписант:").pack(side=tk.LEFT, padx=(0, 5))
        self.signer_var = tk.StringVar()
        self.signer_combo = ttk.Combobox(report_top_frame, textvariable=self.signer_var, width=30)
        self.signer_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(report_top_frame, text="Создать отчет", 
                  command=self.create_daily_report).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(report_top_frame, text="Создать архив", 
                  command=self.create_archive).pack(side=tk.LEFT)
        
        # Раздел статистики
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика за период", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_date_frame = ttk.Frame(stats_frame)
        stats_date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(stats_date_frame, text="С:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_entry = ttk.Entry(stats_date_frame, width=12)
        self.start_date_entry.insert(0, "01.10.2025")
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(stats_date_frame, text="По:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_entry = ttk.Entry(stats_date_frame, width=12)
        self.end_date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(stats_date_frame, text="Получить статистику", 
                  command=self.get_statistics).pack(side=tk.LEFT)
        
        # Поле вывода результатов
        output_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, height=8)
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_employees_list(self):
        """Загрузка списка сотрудников в Listbox"""
        self.employees_listbox.delete(0, tk.END)
        employees = self.manager.get_all_employees()
        for emp_id, name, birth_year in employees:
            self.employees_listbox.insert(tk.END, f"{name} ({birth_year})")
    
    def load_signers_list(self):
        """Загрузка списка подписантов в ComboBox"""
        signers = self.manager.get_all_signers()
        signer_names = []
        self.signer_ids = {}
        for signer_id, name, position in signers:
            display_text = f"{name} - {position}"
            signer_names.append(display_text)
            self.signer_ids[display_text] = signer_id
        
        self.signer_combo['values'] = signer_names
        if signer_names:
            self.signer_combo.set(signer_names[0])
    
    def add_to_selection(self):
        """Добавление выбранных сотрудников в список для отчета"""
        selections = self.employees_listbox.curselection()
        employees = self.manager.get_all_employees()
        
        for index in selections:
            if index < len(employees):
                emp_data = employees[index]
                if emp_data not in self.selected_employees:
                    self.selected_employees.append(emp_data)
                    self.selected_listbox.insert(tk.END, f"{emp_data[1]} ({emp_data[2]})")
    
    def remove_from_selection(self):
        """Удаление выбранного сотрудника из списка для отчета"""
        selection = self.selected_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.selected_employees):
                self.selected_employees.pop(index)
                self.selected_listbox.delete(index)
    
    def select_all(self):
        """Выбор всех сотрудников"""
        self.clear_selection()
        employees = self.manager.get_all_employees()
        self.selected_employees = employees.copy()
        for emp_id, name, birth_year in employees:
            self.selected_listbox.insert(tk.END, f"{name} ({birth_year})")
    
    def clear_selection(self):
        """Очистка списка выбранных сотрудников"""
        self.selected_employees = []
        self.selected_listbox.delete(0, tk.END)
    
    def add_employee(self):
        name = self.name_entry.get().strip()
        birth_year = self.birth_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите ФИО сотрудника")
            return
        
        if not birth_year.isdigit() or len(birth_year) != 4:
            messagebox.showerror("Ошибка", "Введите корректный год рождения (4 цифры)")
            return
        
        success, message = self.manager.add_employee(name, birth_year)
        if success:
            self.output_text.insert(tk.END, f"✓ {message}\n")
            self.output_text.see(tk.END)  # Прокрутка к новому сообщению
            self.name_entry.delete(0, tk.END)
            self.birth_entry.delete(0, tk.END)
            self.load_employees_list()
        else:
            messagebox.showerror("Ошибка", message)
    
    def add_signer(self):
        name = self.signer_name_entry.get().strip()
        position = self.signer_position_entry.get().strip()
        
        if not name or not position:
            messagebox.showerror("Ошибка", "Заполните ФИО и должность подписанта")
            return
        
        success, message = self.manager.add_signer(name, position)
        if success:
            self.output_text.insert(tk.END, f"✓ {message}\n")
            self.output_text.see(tk.END)
            self.signer_name_entry.delete(0, tk.END)
            self.signer_position_entry.delete(0, tk.END)
            self.load_signers_list()
        else:
            messagebox.showerror("Ошибка", message)
    
    def delete_signer(self):
        """Удаление выбранного подписанта"""
        selected_signer = self.signer_var.get()
        if not selected_signer:
            messagebox.showerror("Ошибка", "Выберите подписанта для удаления")
            return
        
        signer_id = self.signer_ids.get(selected_signer)
        if not signer_id:
            messagebox.showerror("Ошибка", "Не удалось определить выбранного подписанта")
            return
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить подписанта:\n{selected_signer}?"):
            success, message = self.manager.delete_signer(signer_id)
            if success:
                self.output_text.insert(tk.END, f"✓ {message}\n")
                self.output_text.see(tk.END)
                self.load_signers_list()
            else:
                messagebox.showerror("Ошибка", message)
    
    def change_password(self):
        """Изменение пароля для архива"""
        new_password = simpledialog.askstring("Изменение пароля", 
                                            "Введите новый пароль для архивов:",
                                            initialvalue=self.manager.archive_password)
        if new_password:
            if self.manager.save_password(new_password):
                self.output_text.insert(tk.END, f"✓ Пароль для архивов успешно изменен\n")
                self.output_text.see(tk.END)
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить пароль")
    
    def create_daily_report(self):
        date = self.date_entry.get().strip()
        selected_signer = self.signer_var.get()
        
        if not selected_signer:
            messagebox.showerror("Ошибка", "Выберите подписанта")
            return
        
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате дд.мм.гггг")
            return
        
        if not self.selected_employees:
            messagebox.showerror("Ошибка", "Выберите сотрудников для отчета")
            return
        
        signer_id = self.signer_ids.get(selected_signer)
        success, message = self.manager.create_daily_report(date, self.selected_employees, signer_id)
        self.output_text.insert(tk.END, f"✓ {message}\n")
        self.output_text.see(tk.END)
    
    def create_archive(self):
        date = self.date_entry.get().strip()
        success, message = self.manager.archive_files(date)
        if success:
            self.output_text.insert(tk.END, f"✓ {message}\n")
            self.output_text.see(tk.END)
        else:
            messagebox.showerror("Ошибка", message)
    
    def get_statistics(self):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        try:
            datetime.strptime(start_date, "%d.%m.%Y")
            datetime.strptime(end_date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите даты в формате дд.мм.гггг")
            return
        
        result = self.manager.get_statistics(start_date, end_date)
        self.output_text.insert(tk.END, f"✓ {result}\n")
        self.output_text.see(tk.END)

def main():
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()