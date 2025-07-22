import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class CTRMConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Конфигуратор оборудования CTR-M")
        self.root.geometry("1000x700")
        
        # Загрузка базы данных
        self.db_file = "ctrm_db.json"
        self.load_database()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Текущая конфигурация
        self.current_config = {
            "processor": None,
            "baskets": [],
            "io_modules": [],
            "comm_modules": [],
            "special_modules": []
        }
        
        # Инициализация шагов конфигурации
        self.config_steps = [
            {"name": "Выбор процессорного модуля", "method": self.select_processor},
            {"name": "Конфигурация корзин", "method": self.configure_baskets},
            {"name": "Выбор модулей ввода/вывода", "method": self.select_io_modules},
            {"name": "Выбор специальных модулей", "method": self.select_special_modules},
            {"name": "Просмотр конфигурации", "method": self.review_configuration}
        ]
        
        self.current_step = 0
        self.update_step_display()

    def load_database(self):
        """Загрузка базы данных из файла"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.database = json.load(f)
            except:
                # Если файл поврежден, загружаем стандартную базу
                self.load_default_database()
        else:
            self.load_default_database()
    
    def load_default_database(self):
        """Загрузка стандартной базы данных"""
        self.database = {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "processors": [
                {"id": "CTR-MATM", "name": "CTR-MATM", "voltage": "~230V", "ports": ["Ethernet", "CAN"], "description": "Процессорный модуль с поддержкой распределённого ввода/вывода"},
                {"id": "CTR-MDTM", "name": "CTR-MDTM", "voltage": "=24V", "ports": ["Ethernet", "CAN"], "description": "Процессорный модуль с поддержкой распределённого ввода/вывода"},
                {"id": "CTR-MATRC", "name": "CTR-MATRC", "voltage": "~230V", "ports": ["Ethernet", "CAN", "RS-485"], "description": "Процессорный модуль с поддержкой распределённого ввода/вывода и полевых шин"}
            ],
            "baskets": [
                {"id": "CTR-MBASE-8", "name": "Основная корзина 8 слотов", "type": "main", "slots": 8},
                {"id": "CTR-MBASE-10", "name": "Основная корзина 10 слотов", "type": "main", "slots": 10},
                {"id": "CTR-MEXP-6", "name": "Корзина расширения 6 слотов", "type": "expansion", "slots": 6}
            ],
            "io_modules": [
                {"id": "CTR-M1-10HDI", "name": "10HDI 230V AC", "type": "input", "channels": 10, "voltage": "~230V"},
                {"id": "CTR-M2-10DI", "name": "10DI 24V DC", "type": "input", "channels": 10, "voltage": "=24V"},
                {"id": "CTR-M3-8AI", "name": "8AI 0-20mA DC", "type": "input", "channels": 8, "signal": "0-20mA"},
                {"id": "CTR-M8-4RO", "name": "4RO 5A AC/DC", "type": "output", "channels": 4, "current": "5A"}
            ],
            "special_modules": [
                {"id": "CTR-MEM-H", "name": "Счетчик электроэнергии 5A", "type": "energy", "current": "5A"},
                {"id": "CTR-MF", "name": "Модуль-регулятор", "type": "controller", "channels": 4}
            ]
        }
        self.save_database()
    
    def save_database(self):
        """Сохранение базы данных в файл"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, ensure_ascii=False, indent=4)
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Панель шагов конфигурации
        self.steps_frame = ttk.LabelFrame(self.root, text="Шаги конфигурации")
        self.steps_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.steps_labels = []
        for i in range(5):
            lbl = ttk.Label(self.steps_frame, text=f"{i+1}. ", style='Step.TLabel')
            lbl.grid(row=0, column=i, padx=10, pady=5)
            self.steps_labels.append(lbl)
        
        # Основная область конфигурации
        self.config_frame = ttk.LabelFrame(self.root, text="Конфигурация")
        self.config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель управления
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.prev_btn = ttk.Button(self.control_frame, text="Назад", command=self.prev_step)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(self.control_frame, text="Далее", command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(self.control_frame, text="Экспорт конфигурации", command=self.export_config)
        self.export_btn.pack(side=tk.RIGHT, padx=5)
        
        self.update_db_btn = ttk.Button(self.control_frame, text="Обновить БД", command=self.update_database)
        self.update_db_btn.pack(side=tk.RIGHT, padx=5)
        
        # Стили
        style = ttk.Style()
        style.configure('Step.TLabel', font=('Arial', 10, 'bold'))
        style.configure('ActiveStep.TLabel', font=('Arial', 10, 'bold'), foreground='blue')
        style.configure('CompletedStep.TLabel', font=('Arial', 10, 'bold'), foreground='green')
    
    def update_step_display(self):
        """Обновление отображения шагов конфигурации"""
        for i, step in enumerate(self.config_steps):
            if i == self.current_step:
                self.steps_labels[i].configure(text=f"{i+1}. {step['name']}", style='ActiveStep.TLabel')
            elif i < self.current_step:
                self.steps_labels[i].configure(text=f"{i+1}. {step['name']}", style='CompletedStep.TLabel')
            else:
                self.steps_labels[i].configure(text=f"{i+1}. {step['name']}", style='Step.TLabel')
        
        # Очистка области конфигурации
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        
        # Вызов метода текущего шага
        self.config_steps[self.current_step]["method"]()
        
        # Обновление состояния кнопок
        self.prev_btn.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_step < len(self.config_steps)-1 else tk.DISABLED)
    
    def next_step(self):
        """Переход к следующему шагу"""
        if self.current_step < len(self.config_steps) - 1:
            self.current_step += 1
            self.update_step_display()
    
    def prev_step(self):
        """Переход к предыдущему шагу"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()
    
    def select_processor(self):
        """Шаг 1: Выбор процессорного модуля"""
        lbl = ttk.Label(self.config_frame, text="Выберите процессорный модуль:", font=('Arial', 10, 'bold'))
        lbl.pack(pady=10)
        
        self.processor_var = tk.StringVar()
        self.processor_var.set(self.current_config["processor"] if self.current_config["processor"] else "")
        
        for proc in self.database["processors"]:
            rb = ttk.Radiobutton(
                self.config_frame, 
                text=f"{proc['name']} ({proc['voltage']}) - {', '.join(proc['ports'])}",
                variable=self.processor_var,
                value=proc['id']
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Кнопка для сохранения выбора
        save_btn = ttk.Button(self.config_frame, text="Сохранить выбор", command=self.save_processor)
        save_btn.pack(pady=10)
    
    def save_processor(self):
        """Сохранение выбранного процессора"""
        if not self.processor_var.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите процессорный модуль")
            return
        
        self.current_config["processor"] = self.processor_var.get()
        messagebox.showinfo("Сохранено", "Процессорный модуль успешно выбран")
        self.next_step()
    
    def configure_baskets(self):
        """Шаг 2: Конфигурация корзин"""
        lbl = ttk.Label(self.config_frame, text="Конфигурация корзин:", font=('Arial', 10, 'bold'))
        lbl.pack(pady=10)
        
        # Основная корзина
        main_frame = ttk.LabelFrame(self.config_frame, text="Основная корзина")
        main_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.main_basket_var = tk.StringVar()
        self.main_basket_var.set(self.current_config["baskets"][0]["id"] if self.current_config["baskets"] else "")
        
        for basket in [b for b in self.database["baskets"] if b["type"] == "main"]:
            rb = ttk.Radiobutton(
                main_frame, 
                text=f"{basket['name']} ({basket['slots']} слотов)",
                variable=self.main_basket_var,
                value=basket['id']
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Корзины расширения
        exp_frame = ttk.LabelFrame(self.config_frame, text="Корзины расширения")
        exp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.exp_basket_vars = []
        self.exp_basket_checks = []
        
        for i, basket in enumerate([b for b in self.database["baskets"] if b["type"] == "expansion"]):
            var = tk.IntVar()
            self.exp_basket_vars.append(var)
            
            cb = ttk.Checkbutton(
                exp_frame, 
                text=f"{basket['name']} ({basket['slots']} слотов)",
                variable=var
            )
            cb.pack(anchor=tk.W, padx=20, pady=2)
            self.exp_basket_checks.append(cb)
        
        # Кнопка для сохранения выбора
        save_btn = ttk.Button(self.config_frame, text="Сохранить конфигурацию", command=self.save_baskets)
        save_btn.pack(pady=10)
    
    def save_baskets(self):
        """Сохранение конфигурации корзин"""
        if not self.main_basket_var.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите основную корзину")
            return
        
        # Сохраняем основную корзину
        main_basket = next(b for b in self.database["baskets"] if b["id"] == self.main_basket_var.get())
        self.current_config["baskets"] = [{
            "id": main_basket["id"],
            "name": main_basket["name"],
            "type": "main",
            "slots": main_basket["slots"]
        }]
        
        # Сохраняем корзины расширения
        for i, var in enumerate(self.exp_basket_vars):
            if var.get():
                basket = [b for b in self.database["baskets"] if b["type"] == "expansion"][i]
                self.current_config["baskets"].append({
                    "id": basket["id"],
                    "name": basket["name"],
                    "type": "expansion",
                    "slots": basket["slots"]
                })
        
        messagebox.showinfo("Сохранено", "Конфигурация корзин успешно сохранена")
        self.next_step()
    
    def select_io_modules(self):
        """Шаг 3: Выбор модулей ввода/вывода"""
        lbl = ttk.Label(self.config_frame, text="Выберите модули ввода/вывода:", font=('Arial', 10, 'bold'))
        lbl.pack(pady=10)
        
        # Определяем доступные слоты
        total_slots = sum(b["slots"] for b in self.current_config["baskets"])
        used_slots = 0  # Пока не учитываем специальные модули
        
        # Создаем Treeview для выбора модулей
        columns = ("id", "name", "type", "channels", "details")
        self.io_tree = ttk.Treeview(self.config_frame, columns=columns, show="headings", height=10)
        
        self.io_tree.heading("id", text="Артикул")
        self.io_tree.heading("name", text="Название")
        self.io_tree.heading("type", text="Тип")
        self.io_tree.heading("channels", text="Каналы")
        self.io_tree.heading("details", text="Характеристики")
        
        self.io_tree.column("id", width=100)
        self.io_tree.column("name", width=150)
        self.io_tree.column("type", width=80)
        self.io_tree.column("channels", width=60)
        self.io_tree.column("details", width=200)
        
        # Заполняем данными
        for module in self.database["io_modules"]:
            details = ""
            if "voltage" in module:
                details = f"Напряжение: {module['voltage']}"
            elif "signal" in module:
                details = f"Сигнал: {module['signal']}"
            elif "current" in module:
                details = f"Ток: {module['current']}"
            
            self.io_tree.insert("", tk.END, values=(
                module["id"],
                module["name"],
                module["type"],
                module.get("channels", "-"),
                details
            ))
        
        self.io_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки для выбора
        btn_frame = ttk.Frame(self.config_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        add_btn = ttk.Button(btn_frame, text="Добавить модуль", command=self.add_io_module)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(btn_frame, text="Удалить модуль", command=self.remove_io_module)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Список выбранных модулей
        selected_lbl = ttk.Label(self.config_frame, text="Выбранные модули:", font=('Arial', 10, 'bold'))
        selected_lbl.pack(pady=5)
        
        self.selected_io_tree = ttk.Treeview(self.config_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            self.selected_io_tree.heading(col, text=self.io_tree.heading(col)["text"])
            self.selected_io_tree.column(col, width=self.io_tree.column(col)["width"])
        
        self.selected_io_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопка для сохранения выбора
        save_btn = ttk.Button(self.config_frame, text="Сохранить выбор", command=self.save_io_modules)
        save_btn.pack(pady=10)
    
    def add_io_module(self):
        """Добавление модуля ввода/вывода в список выбранных"""
        selected = self.io_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите модуль из списка")
            return
        
        item = self.io_tree.item(selected[0])
        values = item["values"]
        
        # Проверяем, не добавлен ли уже этот модуль
        for child in self.selected_io_tree.get_children():
            if self.selected_io_tree.item(child)["values"][0] == values[0]:
                messagebox.showerror("Ошибка", "Этот модуль уже добавлен")
                return
        
        self.selected_io_tree.insert("", tk.END, values=values)
    
    def remove_io_module(self):
        """Удаление модуля ввода/вывода из списка выбранных"""
        selected = self.selected_io_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите модуль для удаления")
            return
        
        for item in selected:
            self.selected_io_tree.delete(item)
    
    def save_io_modules(self):
        """Сохранение выбранных модулей ввода/вывода"""
        selected_modules = []
        for child in self.selected_io_tree.get_children():
            values = self.selected_io_tree.item(child)["values"]
            module = {
                "id": values[0],
                "name": values[1],
                "type": values[2],
                "channels": values[3],
                "details": values[4]
            }
            selected_modules.append(module)
        
        self.current_config["io_modules"] = selected_modules
        messagebox.showinfo("Сохранено", "Модули ввода/вывода успешно сохранены")
        self.next_step()
    
    def select_special_modules(self):
        """Шаг 4: Выбор специальных модулей"""
        lbl = ttk.Label(self.config_frame, text="Выберите специальные модули:", font=('Arial', 10, 'bold'))
        lbl.pack(pady=10)
        
        # Создаем Treeview для выбора модулей
        columns = ("id", "name", "type", "details")
        self.special_tree = ttk.Treeview(self.config_frame, columns=columns, show="headings", height=5)
        
        self.special_tree.heading("id", text="Артикул")
        self.special_tree.heading("name", text="Название")
        self.special_tree.heading("type", text="Тип")
        self.special_tree.heading("details", text="Характеристики")
        
        self.special_tree.column("id", width=100)
        self.special_tree.column("name", width=150)
        self.special_tree.column("type", width=80)
        self.special_tree.column("details", width=200)
        
        # Заполняем данными
        for module in self.database["special_modules"]:
            details = ""
            if "current" in module:
                details = f"Ток: {module['current']}"
            elif "channels" in module:
                details = f"Каналы: {module['channels']}"
            
            self.special_tree.insert("", tk.END, values=(
                module["id"],
                module["name"],
                module["type"],
                details
            ))
        
        self.special_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки для выбора
        btn_frame = ttk.Frame(self.config_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        add_btn = ttk.Button(btn_frame, text="Добавить модуль", command=self.add_special_module)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(btn_frame, text="Удалить модуль", command=self.remove_special_module)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Список выбранных модулей
        selected_lbl = ttk.Label(self.config_frame, text="Выбранные модули:", font=('Arial', 10, 'bold'))
        selected_lbl.pack(pady=5)
        
        self.selected_special_tree = ttk.Treeview(self.config_frame, columns=columns, show="headings", height=3)
        
        for col in columns:
            self.selected_special_tree.heading(col, text=self.special_tree.heading(col)["text"])
            self.selected_special_tree.column(col, width=self.special_tree.column(col)["width"])
        
        self.selected_special_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопка для сохранения выбора
        save_btn = ttk.Button(self.config_frame, text="Сохранить выбор", command=self.save_special_modules)
        save_btn.pack(pady=10)
    
    def add_special_module(self):
        """Добавление специального модуля в список выбранных"""
        selected = self.special_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите модуль из списка")
            return
        
        item = self.special_tree.item(selected[0])
        values = item["values"]
        
        # Проверяем, не добавлен ли уже этот модуль
        for child in self.selected_special_tree.get_children():
            if self.selected_special_tree.item(child)["values"][0] == values[0]:
                messagebox.showerror("Ошибка", "Этот модуль уже добавлен")
                return
        
        self.selected_special_tree.insert("", tk.END, values=values)
    
    def remove_special_module(self):
        """Удаление специального модуля из списка выбранных"""
        selected = self.selected_special_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите модуль для удаления")
            return
        
        for item in selected:
            self.selected_special_tree.delete(item)
    
    def save_special_modules(self):
        """Сохранение выбранных специальных модулей"""
        selected_modules = []
        for child in self.selected_special_tree.get_children():
            values = self.selected_special_tree.item(child)["values"]
            module = {
                "id": values[0],
                "name": values[1],
                "type": values[2],
                "details": values[3]
            }
            selected_modules.append(module)
        
        self.current_config["special_modules"] = selected_modules
        messagebox.showinfo("Сохранено", "Специальные модули успешно сохранены")
        self.next_step()
    
    def review_configuration(self):
        """Шаг 5: Просмотр конфигурации"""
        lbl = ttk.Label(self.config_frame, text="Итоговая конфигурация:", font=('Arial', 12, 'bold'))
        lbl.pack(pady=10)
        
        # Отображение выбранного процессора
        proc_frame = ttk.LabelFrame(self.config_frame, text="Процессорный модуль")
        proc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.current_config["processor"]:
            proc = next(p for p in self.database["processors"] if p["id"] == self.current_config["processor"])
            ttk.Label(proc_frame, text=f"{proc['name']} ({proc['voltage']})").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(proc_frame, text=f"Порты: {', '.join(proc['ports'])}").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(proc_frame, text=proc["description"]).pack(anchor=tk.W, padx=10, pady=2)
        else:
            ttk.Label(proc_frame, text="Не выбран").pack(anchor=tk.W, padx=10, pady=2)
        
        # Отображение корзин
        basket_frame = ttk.LabelFrame(self.config_frame, text="Корзины")
        basket_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.current_config["baskets"]:
            for basket in self.current_config["baskets"]:
                ttk.Label(basket_frame, text=f"{basket['name']} ({basket['slots']} слотов, {'основная' if basket['type'] == 'main' else 'расширение'})").pack(anchor=tk.W, padx=10, pady=2)
        else:
            ttk.Label(basket_frame, text="Не выбраны").pack(anchor=tk.W, padx=10, pady=2)
        
        # Отображение модулей ввода/вывода
        io_frame = ttk.LabelFrame(self.config_frame, text="Модули ввода/вывода")
        io_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.current_config["io_modules"]:
            for module in self.current_config["io_modules"]:
                ttk.Label(io_frame, text=f"{module['name']} ({module['type']}, {module['channels']} каналов)").pack(anchor=tk.W, padx=10, pady=2)
        else:
            ttk.Label(io_frame, text="Не выбраны").pack(anchor=tk.W, padx=10, pady=2)
        
        # Отображение специальных модулей
        special_frame = ttk.LabelFrame(self.config_frame, text="Специальные модули")
        special_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.current_config["special_modules"]:
            for module in self.current_config["special_modules"]:
                ttk.Label(special_frame, text=f"{module['name']} ({module['type']})").pack(anchor=tk.W, padx=10, pady=2)
        else:
            ttk.Label(special_frame, text="Не выбраны").pack(anchor=tk.W, padx=10, pady=2)
    
    def export_config(self):
        """Экспорт конфигурации в файл"""
        if not self.current_config["processor"]:
            messagebox.showerror("Ошибка", "Конфигурация не завершена")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить конфигурацию"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_config, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", f"Конфигурация сохранена в файл:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def update_database(self):
        """Обновление базы данных из файла"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите файл базы данных"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_db = json.load(f)
                
                # Проверяем обязательные поля
                required_sections = ["processors", "baskets", "io_modules"]
                for section in required_sections:
                    if section not in new_db:
                        raise ValueError(f"Отсутствует обязательный раздел: {section}")
                
                self.database = new_db
                self.save_database()
                messagebox.showinfo("Успех", "База данных успешно обновлена")
                
                # Перезагружаем текущий шаг для отображения новых данных
                self.update_step_display()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить базу данных:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CTRMConfigurator(root)
    root.mainloop()