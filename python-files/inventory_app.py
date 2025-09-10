import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime
import os

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Инвентаризация компьютерной техники")
        self.root.geometry("900x600")
        
        # Центрирование окна
        self.center_window()
        
        # Данные
        self.employees = []
        self.equipment = []
        self.load_data()
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Вкладка оборудования
        self.create_equipment_tab()
        
        # Вкладка сотрудников
        self.create_employees_tab()
        
        # Вкладка отчетов
        self.create_reports_tab()
        
        # Кнопка сохранения
        self.save_button = tk.Button(root, text="Сохранить данные", command=self.save_data)
        self.save_button.pack(pady=5)
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def load_data(self):
        try:
            # Для exe-файла используем путь рядом с исполняемым файлом
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            data_file = os.path.join(application_path, 'inventory_data.json')
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.employees = data.get('employees', [])
                self.equipment = data.get('equipment', [])
        except FileNotFoundError:
            # Начальные данные для демонстрации
            self.employees = [
                {"id": 1, "name": "Иванов Иван Иванович", "department": "IT"},
                {"id": 2, "name": "Петров Петр Петрович", "department": "Бухгалтерия"}
            ]
            self.equipment = [
                {"id": 1, "type": "Компьютер", "model": "Dell Optiplex 7050", "serial": "ABC123", "employee_id": 1},
                {"id": 2, "type": "Монитор", "model": "Dell U2419H", "serial": "DEF456", "employee_id": 1},
                {"id": 3, "type": "Принтер", "model": "HP LaserJet Pro", "serial": "GHI789", "employee_id": 2},
                {"id": 4, "type": "Сканер", "model": "Canon CanoScan", "serial": "JKL012", "employee_id": None}
            ]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            # Начальные данные в случае ошибки
            self.employees = []
            self.equipment = []
    
    def save_data(self):
        try:
            # Для exe-файла используем путь рядом с исполняемым файлом
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            data_file = os.path.join(application_path, 'inventory_data.json')
            
            data = {
                'employees': self.employees,
                'equipment': self.equipment
            }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", "Данные успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def on_closing(self):
        if messagebox.askokcancel("Выход", "Сохранить данные перед выходом?"):
            self.save_data()
        self.root.destroy()
    
    def create_equipment_tab(self):
        # Вкладка для оборудования
        equipment_frame = ttk.Frame(self.notebook)
        self.notebook.add(equipment_frame, text="Оборудование")
        
        # Панель управления
        control_frame = ttk.Frame(equipment_frame)
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="Добавить", command=self.add_equipment).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Редактировать", command=self.edit_equipment).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Удалить", command=self.delete_equipment).pack(side=tk.LEFT, padx=5)
        
        # Таблица оборудования
        columns = ("ID", "Тип", "Модель", "Серийный номер", "Сотрудник")
        self.equipment_tree = ttk.Treeview(equipment_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.equipment_tree.heading(col, text=col)
            self.equipment_tree.column(col, width=150)
        
        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_tree.yview)
        self.equipment_tree.configure(yscrollcommand=scrollbar.set)
        
        self.equipment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обновление таблицы
        self.update_equipment_tree()
    
    def create_employees_tab(self):
        # Вкладка для сотрудников
        employees_frame = ttk.Frame(self.notebook)
        self.notebook.add(employees_frame, text="Сотрудники")
        
        # Панель управления
        control_frame = ttk.Frame(employees_frame)
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="Добавить", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Редактировать", command=self.edit_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Удалить", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        
        # Таблица сотрудников
        columns = ("ID", "ФИО", "Отдел")
        self.employees_tree = ttk.Treeview(employees_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.employees_tree.heading(col, text=col)
            self.employees_tree.column(col, width=200)
        
        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(employees_frame, orient="vertical", command=self.employees_tree.yview)
        self.employees_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обновление таблицы
        self.update_employees_tree()
    
    def create_reports_tab(self):
        # Вкладка для отчетов
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Отчеты")
        
        # Варианты отчетов
        report_types = [
            "Вся техника",
            "Техника по отделам",
            "Техника без привязки",
            "Техника по типам"
        ]
        
        tk.Label(reports_frame, text="Выберите тип отчета:").pack(pady=5)
        
        self.report_var = tk.StringVar()
        self.report_combo = ttk.Combobox(reports_frame, textvariable=self.report_var, values=report_types)
        self.report_combo.pack(pady=5)
        self.report_combo.current(0)
        
        tk.Button(reports_frame, text="Сформировать отчет", command=self.generate_report).pack(pady=5)
        tk.Button(reports_frame, text="Экспорт в CSV", command=self.export_to_csv).pack(pady=5)
        
        # Поле для отображения отчета
        self.report_text = tk.Text(reports_frame, height=20)
        
        # Добавляем scrollbar для текстового поля
        text_scrollbar = ttk.Scrollbar(reports_frame, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=text_scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_equipment_tree(self):
        # Очистка таблицы
        for item in self.equipment_tree.get_children():
            self.equipment_tree.delete(item)
        
        # Заполнение данными
        for item in self.equipment:
            employee_name = "Не назначено"
            if item['employee_id']:
                for emp in self.employees:
                    if emp['id'] == item['employee_id']:
                        employee_name = emp['name']
                        break
            
            self.equipment_tree.insert("", "end", values=(
                item['id'], item['type'], item['model'], item['serial'], employee_name
            ))
    
    def update_employees_tree(self):
        # Очистка таблицы
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Заполнение данными
        for emp in self.employees:
            self.employees_tree.insert("", "end", values=(
                emp['id'], emp['name'], emp['department']
            ))
    
    def add_equipment(self):
        self.equipment_dialog("Добавить оборудование")
    
    def edit_equipment(self):
        selected = self.equipment_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите оборудование для редактирования")
            return
        
        item_id = self.equipment_tree.item(selected[0])['values'][0]
        equipment = None
        for item in self.equipment:
            if item['id'] == item_id:
                equipment = item
                break
        
        if equipment:
            self.equipment_dialog("Редактировать оборудование", equipment)
    
    def delete_equipment(self):
        selected = self.equipment_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите оборудование для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранное оборудование?"):
            item_id = self.equipment_tree.item(selected[0])['values'][0]
            self.equipment = [item for item in self.equipment if item['id'] != item_id]
            self.update_equipment_tree()
    
    def equipment_dialog(self, title, equipment=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        tk.Label(dialog, text="Тип:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Компьютер", "Монитор", "Принтер", "Сканер"])
        type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(dialog, text="Модель:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        model_entry = tk.Entry(dialog, width=30)
        model_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Серийный номер:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        serial_entry = tk.Entry(dialog, width=30)
        serial_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Сотрудник:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        employee_var = tk.StringVar()
        employee_names = ["Не назначено"] + [emp['name'] for emp in self.employees]
        employee_combo = ttk.Combobox(dialog, textvariable=employee_var, values=employee_names)
        employee_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Заполнение данных если редактирование
        if equipment:
            type_var.set(equipment['type'])
            model_entry.insert(0, equipment['model'])
            serial_entry.insert(0, equipment['serial'])
            
            if equipment['employee_id']:
                for emp in self.employees:
                    if emp['id'] == equipment['employee_id']:
                        employee_var.set(emp['name'])
                        break
            else:
                employee_var.set("Не назначено")
        
        # Кнопки
        def save_equipment():
            # Валидация
            if not type_var.get() or not model_entry.get() or not serial_entry.get():
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            # Поиск ID сотрудника
            employee_id = None
            if employee_var.get() != "Не назначено":
                for emp in self.employees:
                    if emp['name'] == employee_var.get():
                        employee_id = emp['id']
                        break
            
            # Сохранение
            if equipment:
                # Обновление существующего оборудования
                equipment['type'] = type_var.get()
                equipment['model'] = model_entry.get()
                equipment['serial'] = serial_entry.get()
                equipment['employee_id'] = employee_id
            else:
                # Добавление нового оборудования
                new_id = max([item['id'] for item in self.equipment], default=0) + 1
                self.equipment.append({
                    'id': new_id,
                    'type': type_var.get(),
                    'model': model_entry.get(),
                    'serial': serial_entry.get(),
                    'employee_id': employee_id
                })
            
            self.update_equipment_tree()
            dialog.destroy()
        
        tk.Button(dialog, text="Сохранить", command=save_equipment).grid(row=4, column=0, padx=5, pady=10)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=4, column=1, padx=5, pady=10)
    
    def add_employee(self):
        self.employee_dialog("Добавить сотрудника")
    
    def edit_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return
        
        item_id = self.employees_tree.item(selected[0])['values'][0]
        employee = None
        for emp in self.employees:
            if emp['id'] == item_id:
                employee = emp
                break
        
        if employee:
            self.employee_dialog("Редактировать сотрудника", employee)
    
    def delete_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return
        
        item_id = self.employees_tree.item(selected[0])['values'][0]
        
        # Проверка, есть ли привязанное оборудование
        has_equipment = any(item['employee_id'] == item_id for item in self.equipment)
        
        if has_equipment:
            messagebox.showerror("Ошибка", "Нельзя удалить сотрудника, у которого есть привязанное оборудование")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранного сотрудника?"):
            self.employees = [emp for emp in self.employees if emp['id'] != item_id]
            self.update_employees_tree()
    
    def employee_dialog(self, title, employee=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        tk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Отдел:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        department_entry = tk.Entry(dialog, width=30)
        department_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Заполнение данных если редактирование
        if employee:
            name_entry.insert(0, employee['name'])
            department_entry.insert(0, employee['department'])
        
        # Кнопки
        def save_employee():
            # Валидация
            if not name_entry.get() or not department_entry.get():
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            # Сохранение
            if employee:
                # Обновление существующего сотрудника
                employee['name'] = name_entry.get()
                employee['department'] = department_entry.get()
            else:
                # Добавление нового сотрудника
                new_id = max([emp['id'] for emp in self.employees], default=0) + 1
                self.employees.append({
                    'id': new_id,
                    'name': name_entry.get(),
                    'department': department_entry.get()
                })
            
            self.update_employees_tree()
            dialog.destroy()
        
        tk.Button(dialog, text="Сохранить", command=save_employee).grid(row=2, column=0, padx=5, pady=10)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=2, column=1, padx=5, pady=10)
    
    def generate_report(self):
        report_type = self.report_var.get()
        report_text = f"Отчет: {report_type}\n"
        report_text += f"Сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if report_type == "Вся техника":
            for item in self.equipment:
                employee_name = "Не назначено"
                if item['employee_id']:
                    for emp in self.employees:
                        if emp['id'] == item['employee_id']:
                            employee_name = emp['name']
                            break
                
                report_text += f"{item['type']} {item['model']} (S/N: {item['serial']}) - {employee_name}\n"
        
        elif report_type == "Техника по отделам":
            departments = {}
            for emp in self.employees:
                departments[emp['department']] = []
            
            for item in self.equipment:
                employee_name = "Не назначено"
                department = "Не назначено"
                
                if item['employee_id']:
                    for emp in self.employees:
                        if emp['id'] == item['employee_id']:
                            employee_name = emp['name']
                            department = emp['department']
                            break
                
                if department not in departments:
                    departments[department] = []
                
                departments[department].append(f"{item['type']} {item['model']} (S/N: {item['serial']}) - {employee_name}")
            
            for department, items in departments.items():
                if items:
                    report_text += f"\n{department}:\n"
                    for item in items:
                        report_text += f"  {item}\n"
        
        elif report_type == "Техника без привязки":
            unassigned = [item for item in self.equipment if not item['employee_id']]
            if unassigned:
                for item in unassigned:
                    report_text += f"{item['type']} {item['model']} (S/N: {item['serial']})\n"
            else:
                report_text += "Вся техника привязана к сотрудникам\n"
        
        elif report_type == "Техника по типам":
            types = {}
            for item in self.equipment:
                if item['type'] not in types:
                    types[item['type']] = []
                
                employee_name = "Не назначено"
                if item['employee_id']:
                    for emp in self.employees:
                        if emp['id'] == item['employee_id']:
                            employee_name = emp['name']
                            break
                
                types[item['type']].append(f"{item['model']} (S/N: {item['serial']}) - {employee_name}")
            
            for eq_type, items in types.items():
                report_text += f"\n{eq_type}:\n"
                for item in items:
                    report_text += f"  {item}\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_text)
    
    def export_to_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Экспорт в CSV"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Тип', 'Модель', 'Серийный номер', 'Сотрудник', 'Отдел'])
                
                for item in self.equipment:
                    employee_name = "Не назначено"
                    department = "Не назначено"
                    
                    if item['employee_id']:
                        for emp in self.employees:
                            if emp['id'] == item['employee_id']:
                                employee_name = emp['name']
                                department = emp['department']
                                break
                    
                    writer.writerow([item['type'], item['model'], item['serial'], employee_name, department])
            
            messagebox.showinfo("Экспорт", "Данные успешно экспортированы в CSV")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
