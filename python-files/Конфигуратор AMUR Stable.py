import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime


class PCConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Конфигуратор AMUR")
        self.root.geometry("1600x900")

        # Настройка цветовой схемы
        self.colors = {
            "header": "#2E86AB",
            "subheader": "#A23B72",
            "accent": "#F18F01",
            "success": "#3E885B",
            "warning": "#C73E1D",
            "background": "#F5F5F5",
            "text": "#333333"
        }

        self.amur_markup = tk.DoubleVar(value=15.0)
        self.merl_markup = tk.DoubleVar(value=15.0)
        self.selected_components = {}
        self.total_price = 0
        self.final_price = 0

        self.components = self.load_components_data()
        self.create_widgets()
        self.update_summary()

    def load_components_data(self):
        return {
            "Материнская плата": [
                {"name": "AMD AMUR A520", "price": 100, "specs": "AM4, DDR4"},
                {"name": "INTEL AMUR H610", "price": 140, "specs": "LGA 1700, DDR4"},
                {"name": "INTEL AMUR B760", "price": 160, "specs": "LGA 1700, DDR5"},
            ],
            "Процессор": [
                {"name": "AMD Ryzen 5 5500GT", "price": 135, "specs": "6 ядер/12 потоков, 3.6-4.4 ГГц"},
                {"name": "AMD Ryzen 5 5600GT", "price": 137, "specs": "6 ядер/12 потоков, 3.6-4.6 ГГц"},
                {"name": "AMD Ryzen 7 5700G", "price": 145, "specs": "8 ядер/16 потоков, 3.8-4.6 ГГц"},
                {"name": "Intel i3 12100", "price": 110, "specs": "4 ядра/8 потоков, 3.3-4.3 ГГц"},
                {"name": "Intel i3 13100", "price": 120, "specs": "4 ядра/8 потоков, 3.4-4.5 ГГц"},
                {"name": "Intel i3 14100", "price": 130, "specs": "4 ядра/8 потоков, 3.5-4.7 ГГц"},
                {"name": "Intel i5 12400", "price": 145, "specs": "6 ядер/12 потоков, 2.5-4.4 ГГц"},
                {"name": "Intel i5 13400", "price": 155, "specs": "10 ядер/16 потоков, 2.5-4.6 ГГц"},
                {"name": "Intel i5 14400", "price": 165, "specs": "10 ядер/16 потоков, 2.5-4.7 ГГц"},
                {"name": "Intel i5 12500", "price": 145, "specs": "6 ядер/12 потоков, 3.0-4.6 ГГц"},
                {"name": "Intel i5 13500", "price": 155, "specs": "14 ядер/20 потоков, 2.5-4.8 ГГц"},
                {"name": "Intel i5 14500", "price": 165, "specs": "14 ядер/20 потоков, 2.6-5.0 ГГц"},
                {"name": "Intel i3 12100F", "price": 107, "specs": "4 ядра/8 потоков, 3.3-4.3 ГГц"},
                {"name": "Intel i3 13100F", "price": 112, "specs": "4 ядра/8 потоков, 3.4-4.5 ГГц"},
                {"name": "Intel i3 14100F", "price": 115, "specs": "4 ядра/8 потоков, 3.5-4.7 ГГц"},
                {"name": "Intel i5 12400F", "price": 165, "specs": "6 ядер/12 потоков, 2.5-4.4 ГГц"},
                {"name": "Intel i5 13400F", "price": 110, "specs": "10 ядер/16 потоков, 2.5-4.6 ГГц"},
                {"name": "Intel i5 14400F", "price": 110, "specs": "10 ядер/16 потоков, 2.5-4.7 ГГц"},
                {"name": "Intel i7 12700", "price": 280, "specs": "12 ядер/20 потоков, 2.1-4.9 ГГц"},
                {"name": "Intel i7 13700", "price": 320, "specs": "16 ядер/24 потока, 2.1-5.2 ГГц"},
                {"name": "Intel i7 14700", "price": 380, "specs": "20 ядер/28 потоков, 2.1-5.4 ГГц"},
                {"name": "Intel i7 12700F", "price": 250, "specs": "12 ядер/20 потоков, 2.1-4.9 ГГц"},
                {"name": "Intel i7 13700F", "price": 290, "specs": "16 ядер/24 потока, 2.1-5.2 ГГц"},
                {"name": "Intel i7 14700F", "price": 350, "specs": "20 ядер/28 потоков, 2.1-5.4 ГГц"}
            ],
            "Процессорный кулер": [
                {"name": "Cooler 95W", "price": 10, "specs": "Air Cooler"},
                {"name": "Cooler 130W", "price": 15, "specs": "Air Cooler"},
                {"name": "Cooler 180W", "price": 20, "specs": "Air CoolerB"},
                {"name": "Cooler 220W", "price": 30, "specs": "Air Cooler"},
                {"name": "Cooler 250W", "price": 40, "specs": "Air Cooler"},
                {"name": "Water Cooler 280W+", "price": 120, "specs": "Water Cooler"},
            ],
            "Видеокарта": [
                {"name": "GT1030", "price": 80, "specs": "2GB GDDR4"},
                {"name": "RTX3050", "price": 250, "specs": "8GB GDDR6"},
                {"name": "RTX4060", "price": 290, "specs": "8GB GDDR6"},
                {"name": "RTX4060TI", "price": 470, "specs": "8GB GDDR6"},
                {"name": "RTX5050", "price": 300, "specs": "8GB GDDR6"},
                {"name": "RTX5060", "price": 350, "specs": "8GB GDDR6"}
            ],
            "Оперативная память (обязательный реестровый компонент)": [
                {"name": "8GB 2666Mhz DDR4 TMY UDIMM", "price": 50, "specs": "1x8GB Kit"},
                {"name": "8GB 3200Mhz DDR4 TMY UDIMM", "price": 68, "specs": "1x8GB Kit"},
                {"name": "16GB 3200Mhz DDR4 TMY UDIMM", "price": 110, "specs": "1x16GB Kit"},
                {"name": "8GB 2666Mhz DDR4 TMY SO-DIMM", "price": 55, "specs": "1x8GB Kit"},
                {"name": "8GB 3200Mhz DDR4 TMY SO-DIMM", "price": 73, "specs": "1x8GB Kit"},
                {"name": "16GB 3200Mhz DDR4 TMY SO-DIMM", "price": 115, "specs": "1x16GB Kit"},
                {"name": "8GB DDR5 TMY UDIMM", "price": 70, "specs": "1x8GB Kit"},
                {"name": "16GB DDR5 TMY UDIMM", "price": 120, "specs": "1x16GB Kit"},
                {"name": "32GB DDR5 TMY UDIMM", "price": 180, "specs": "1x32GB Kit"},
            ],
            "Накопитель SSD (Обязательный реестровый компонент)": [
                {"name": "ТМИ 256GB SATA 2.5", "price": 80, "specs": "SSD SATA-III 2.5"},
                {"name": "ТМИ 512GB SATA 2.5", "price": 120, "specs": "SSD SATA-III 2.5"},
                {"name": "ТМИ 1TB SATA 2.5", "price": 250, "specs": "SSD SATA-III 2.5"},
                {"name": "ТМИ 256GB SATA M.2", "price": 90, "specs": "SSD SATA-III M.2"},
                {"name": "ТМИ 512GB SATA M.2", "price": 130, "specs": "SSD SATA-III M.2"},
                {"name": "ТМИ 1TB SATA M.2", "price": 260, "specs": "SSD SATA-III M.2"},
            ],
            "Накопитель HDD": [
                {"name": "HDD500GB", "price": 65, "specs": "HDD 2.5"},
                {"name": "HDD1TB", "price": 60, "specs": "HDD 3.5"},
                {"name": "HDD2TB", "price": 120, "specs": "HDD 3.5"},
                {"name": "HDD1TB 2.5", "price": 125, "specs": "HDD 2.5"},
                {"name": "HDD2TB 2.5", "price": 125, "specs": "HDD 2.5"},
            ],
            "Блок питания": [
                {"name": "<Встроен в корпус>", "price": 0, "specs": "Если встроен в корпус"},
                {"name": "Accord 400W", "price": 20, "specs": "PSU 400W"},
                {"name": "Accord 450W", "price": 25, "specs": "PSU 450W"},
                {"name": "Accord 500W", "price": 28, "specs": "PSU 500W"},
                {"name": "Accord 550W", "price": 35, "specs": "PSU 550W"},
                {"name": "Accord 600W", "price": 40, "specs": "PSU 600W"},
                {"name": "Deepcool 400W", "price": 20, "specs": "PSU 400W"},
                {"name": "Deepcool 450W", "price": 25, "specs": "PSU 450W"},
                {"name": "Deepcool 500W", "price": 28, "specs": "PSU 500W"},
                {"name": "Deepcool 550W", "price": 35, "specs": "PSU 550W"},
                {"name": "Deepcool 600W", "price": 40, "specs": "PSU 600W"},
                {"name": "be quiet! Straight 750 Power 11", "price": 200, "specs": "750W 80+ Platinum"},
                {"name": "Deepcool PQ850M", "price": 250, "specs": "750W 80+ Gold"}
            ],
            "Корпус": [
                {"name": "2017 AMUR WITH 400W PSU ATX", "price": 50, "specs": "Mid-Tower, Office/Work Class"},
                {"name": "Accord B301", "price": 30, "specs": "Mid-Tower, Office/Work Class"},
                {"name": "Deepcool Matrexx 55", "price": 60, "specs": "Midi-Tower Gaming Case"},
                {"name": "MiniPC AMUR", "price": 45, "specs": "Slim-Case"},
                {"name": "AIO 23.8 Full HD", "price": 350, "specs": "AIO"},
                {"name": "AIO 27 Full HD", "price": 60, "specs": "AIO"},
            ],
            "Охлаждение корпуса": [
                {"name": "Cooler 80x80", "price": 3, "specs": "Case Cooler"},
                {"name": "Cooler 90x90", "price": 4, "specs": "Case Cooler"},
                {"name": "Cooler 120x120", "price": 5, "specs": "Case Cooler"},
            ],
            "Дополнительные компоненты": [
                {"name": "M.2 WIFI/BT модуль", "price": 3, "specs": "AX101"},
                {"name": "Блокировка кнопки питания ЭВМ", "price": 15, "specs": "Option"},
                {"name": "Контроллер x1 (3.0 PCIE M)", "price": 25, "specs": "Controller"},
            ],
            "Монитор": [
                {"name": "Монитор RDW 23.8d Full HD", "price": 90, "specs": "M-RF"},
                {"name": "Монитор RDW 23.8d QHD", "price": 150, "specs": "M-RF"},
                {"name": "Монитор Сова 23.8d Full HD", "price": 90, "specs": "M-RF"},
                {"name": "Монитор Сова 27d Full HD", "price": 150, "specs": "M-RF"},
                {"name": "Монитор Digma 23.8d 24P201F Full HD", "price": 90, "specs": "M-NON-RF"},
                {"name": "Монитор Sunwind 23.8d SM-24FI221 Full HD", "price": 95, "specs": "M-NON-RF"},
                {"name": "Монитор Digma 27d DM-MONB2702 QHD", "price": 150, "specs": "M-NON-RF"},
                {"name": "Монитор Sunwind 27d SUN-M27BA108 QHD", "price": 220, "specs": "M-NON-RF"},
            ],
            "Операционная система": [
                {"name": "RED-OS", "price": 90, "specs": "OS-RF"},
                {"name": "AstraLinux Орёл", "price": 120, "specs": "OS-RF"},
                {"name": "AstraLinux Воронеж", "price": 240, "specs": "OS-RF"},
                {"name": "AstraLinux Смоленск", "price": 360, "specs": "OS-RF"},
            ],
            "Гарантия": [
                {"name": "1 год", "price": 15, "specs": "STD"},
                {"name": "3 года", "price": 30, "specs": "STD"},
                {"name": "5 лет", "price": 50, "specs": "STD"},
            ]
        }

    def get_pc_naming(self):
        """Генерация названия ПК согласно требованиям"""
        if not self.selected_components:
            return "Не выбраны компоненты"

        # Определяем тип корпуса
        case_type = ""
        case_name = ""
        if "Корпус" in self.selected_components:
            case = self.selected_components["Корпус"]['component']['name']
            if "Midi-Tower" in case or "Mid-Tower" in case:
                case_type = "Нарвал"
            elif "Slim-Case" in case or "MiniPC" in case:
                case_type = "Финвал"
            elif "AIO" in case:
                case_type = "Тигр"

        # Получаем компоненты для названия
        cpu = self.selected_components.get("Процессор", {}).get('component', {}).get('name', 'noCPU')
        ram = self.selected_components.get("Оперативная память (обязательный реестровый компонент)", {}).get(
            'component', {}).get('name', 'noRAM')
        ssd = self.selected_components.get("Накопитель SSD (Обязательный реестровый компонент)", {}).get('component',
                                                                                                         {}).get('name',
                                                                                                                 'noSSD')
        hdd = self.selected_components.get("Накопитель HDD", {}).get('component', {}).get('name', '')
        gpu = self.selected_components.get("Видеокарта", {}).get('component', {}).get('name', 'noGPU')
        os_name = self.selected_components.get("Операционная система", {}).get('component', {}).get('name', 'noOS')
        monitor = self.selected_components.get("Монитор", {}).get('component', {}).get('name', '')

        # Упрощаем названия компонентов
        cpu_short = cpu.split()[0] + " " + cpu.split()[1] if len(cpu.split()) > 1 else cpu
        ram_short = ram.split()[0] if ram != 'noRAM' else 'noRAM'
        ssd_short = ssd.split()[1] if ssd != 'noSSD' and len(ssd.split()) > 1 else ssd
        hdd_short = hdd if hdd else ''
        gpu_short = gpu if gpu != 'noGPU' else 'VEGA7' if 'Ryzen' in cpu and 'G' in cpu else 'noGPU'

        # Формируем название с учетом HDD/SSD
        storage_info = ssd_short
        if hdd_short:
            storage_info = f"{ssd_short}+{hdd_short}" if ssd_short != 'noSSD' else hdd_short

        naming = f"PC Amur {case_type} {cpu_short}/{ram_short}/{storage_info}/{gpu_short}/{os_name.split()[0] if os_name != 'noOS' else 'noOS'}/BLACK"

        if monitor:
            naming += " - Монитор в комплекте"

        return naming

    def update_kp(self):
        """Обновление коммерческого предложения с красивым оформлением"""
        self.kp_text.config(state=tk.NORMAL)
        self.kp_text.delete(1.0, tk.END)

        # Название системы
        pc_name = self.get_pc_naming()
        self.kp_text.insert(tk.END, f"{pc_name}\n", "header")
        self.kp_text.insert(tk.END, "═" * 60 + "\n\n")

        # Таблица компонентов
        self.kp_text.insert(tk.END, "КОМПЛЕКТУЮЩИЕ:\n", "subheader")
        self.kp_text.insert(tk.END, "─" * 60 + "\n")

        total_items = 0
        for cat, data in self.selected_components.items():
            if cat not in ["Гарантия"]:  # Гарантию выводим отдельно
                comp = data['component']
                qty = data['quantity']
                total = comp['price'] * qty
                total_items += 1

                # Форматируем строку в виде таблицы
                comp_name = f"{comp['name']}"
                if qty > 1:
                    comp_name += f" (x{qty})"

                # Выравниваем цены
                price_str = f"{total}$".rjust(10)
                self.kp_text.insert(tk.END, f"├─ {comp_name.ljust(50)} {price_str}\n")

        # Итоговая стоимость
        self.kp_text.insert(tk.END, "─" * 60 + "\n")
        self.kp_text.insert(tk.END, f"├─ ИТОГО: {self.final_price:.2f}$".rjust(60) + "\n")

        # Гарантия (посередине снизу)
        warranty = self.selected_components.get("Гарантия", {}).get('component', {}).get('name', 'Не выбрана')
        warranty_price = self.selected_components.get("Гарантия", {}).get('component', {}).get('price', 0)
        warranty_qty = self.selected_components.get("Гарантия", {}).get('quantity', 1)
        warranty_total = warranty_price * warranty_qty

        self.kp_text.insert(tk.END, "─" * 60 + "\n")
        self.kp_text.insert(tk.END, f"ГАРАНТИЯ: {warranty} ({warranty_total}$)\n".center(60), "warranty")
        self.kp_text.insert(tk.END, "─" * 60 + "\n\n")

        # Контактная информация
        self.kp_text.insert(tk.END, "Контактная информация:\n", "subheader")
        self.kp_text.insert(tk.END, f"📞 Телефон: +7 (XXX) XXX-XX-XX\n")
        self.kp_text.insert(tk.END, f"📧 Email: info@amur.ru\n")
        self.kp_text.insert(tk.END, f"📅 Дата составления: {datetime.now().strftime('%d.%m.%Y')}\n")

        # Настройка стилей
        self.kp_text.tag_configure("header", font=("Arial", 16, "bold"), foreground=self.colors["header"],
                                   justify="center")
        self.kp_text.tag_configure("subheader", font=("Arial", 12, "bold"), foreground=self.colors["subheader"])
        self.kp_text.tag_configure("total", font=("Arial", 11, "bold"), foreground=self.colors["warning"])
        self.kp_text.tag_configure("warranty", font=("Arial", 11, "bold"), foreground=self.colors["success"],
                                   justify="center")

        self.kp_text.config(state=tk.DISABLED)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Header с красивым шрифтом
        ttk.Label(main_frame, text="Конфигуратор AMUR TEAM",
                  font=("Arial", 18, "bold"), foreground=self.colors["header"]).grid(row=0, column=0, columnspan=3,
                                                                                     pady=10)

        # Left - Components
        left_frame = ttk.LabelFrame(main_frame, text="Выбор компонентов", padding=10)
        left_frame.grid(row=1, column=0, sticky='nsew', padx=5)

        # Center - Summary (уменьшено на 20% в ширину)
        center_frame = ttk.LabelFrame(main_frame, text="Сводка", padding=10)
        center_frame.grid(row=1, column=1, sticky='nsew', padx=5)

        # Right - Markup & KP
        right_frame = ttk.LabelFrame(main_frame, text="Наценки и КП", padding=10)
        right_frame.grid(row=1, column=2, sticky='nsew', padx=5)

        # Настройка весов для адаптивного изменения размеров
        main_frame.columnconfigure(0, weight=4)
        main_frame.columnconfigure(1, weight=1)  # Уменьшенный вес для сводки
        main_frame.columnconfigure(2, weight=3)
        main_frame.rowconfigure(1, weight=1)

        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        self.create_left_widgets(left_frame)
        self.create_center_widgets(center_frame)
        self.create_right_widgets(right_frame)

    def create_left_widgets(self, frame):
        # Создаем фрейм с прокруткой для компонентов
        container = ttk.Frame(frame)
        container.pack(fill='both', expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.component_vars = {}
        self.quantity_vars = {}
        self.remove_buttons = {}

        for i, category in enumerate(self.components.keys()):
            row_frame = ttk.Frame(scroll_frame)
            row_frame.grid(row=i, column=0, sticky='ew', pady=2)
            row_frame.columnconfigure(1, weight=1)

            ttk.Label(row_frame, text=category, width=25,
                      font=("Arial", 9, "bold"), foreground=self.colors["text"]).grid(row=0, column=0, sticky='w',
                                                                                      padx=5)

            comp_var = tk.StringVar()
            comp_values = ["<Не выбрано>"] + [f"{comp['name']} ({comp['price']}$)" for comp in
                                              self.components[category]]
            comp_cb = ttk.Combobox(row_frame, textvariable=comp_var, width=30, state="readonly")
            comp_cb['values'] = comp_values
            comp_cb.grid(row=0, column=1, padx=5, sticky='ew')
            comp_cb.bind('<<ComboboxSelected>>', lambda e, c=category: self.on_component_select(c))

            quantity_var = tk.IntVar(value=1)
            if category in ["Оперативная память (обязательный реестровый компонент)",
                            "Накопитель SSD (Обязательный реестровый компонент)", "Накопитель HDD",
                            "Охлаждение корпуса", "Дополнительные компоненты", "Монитор"]:
                ttk.Label(row_frame, text="Кол-во:").grid(row=0, column=2, padx=5)
                spin = ttk.Spinbox(row_frame, from_=1, to=10, width=5, textvariable=quantity_var,
                                   command=lambda c=category: self.on_quantity_change(c))
                spin.grid(row=0, column=3, padx=5)

            # Кнопка информации
            info_btn = ttk.Button(row_frame, text="ℹ️", width=3,
                                  command=lambda c=category: self.show_info(c))
            info_btn.grid(row=0, column=4, padx=5)

            # Кнопка удаления компонента
            remove_btn = ttk.Button(row_frame, text="❌", width=3,
                                    command=lambda c=category: self.remove_component(c))
            remove_btn.grid(row=0, column=5, padx=5)
            self.remove_buttons[category] = remove_btn

            self.component_vars[category] = comp_var
            self.quantity_vars[category] = quantity_var

    def create_center_widgets(self, frame):
        # Уменьшаем ширину сводки на 20%
        self.summary_text = scrolledtext.ScrolledText(frame, height=20, width=35, state=tk.DISABLED, wrap=tk.WORD)
        self.summary_text.pack(fill='both', expand=True, pady=5)

        self.total_label = ttk.Label(frame, text="Общая стоимость: 0$",
                                     font=("Arial", 12, "bold"), foreground=self.colors["warning"])
        self.total_label.pack(pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Сохранить", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Загрузить", command=self.load_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Сбросить", command=self.reset_config).pack(side='left', padx=5)

    def create_right_widgets(self, frame):
        # Markup
        markup_frame = ttk.Frame(frame)
        markup_frame.pack(fill='x', pady=5)

        ttk.Label(markup_frame, text="AMUR:", font=("Arial", 10, "bold"),
                  foreground=self.colors["header"]).grid(row=0, column=0, sticky='w')
        ttk.Spinbox(markup_frame, from_=0, to=100, width=8, textvariable=self.amur_markup,
                    command=self.update_markup).grid(row=0, column=1, padx=5)
        ttk.Label(markup_frame, text="%").grid(row=0, column=2, sticky='w')

        ttk.Label(markup_frame, text="MERL:", font=("Arial", 10, "bold"),
                  foreground=self.colors["subheader"]).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Spinbox(markup_frame, from_=0, to=100, width=8, textvariable=self.merl_markup,
                    command=self.update_markup).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(markup_frame, text="%").grid(row=1, column=2, sticky='w', pady=5)

        self.total_markup = ttk.Label(markup_frame, text="Общая наценка: 30.0%",
                                      font=("Arial", 10, "bold"), foreground=self.colors["success"])
        self.total_markup.grid(row=2, column=0, columnspan=3, pady=5)

        self.final_price_label = ttk.Label(markup_frame, text="Итоговая цена: 0$",
                                           font=("Arial", 11, "bold"), foreground=self.colors["warning"])
        self.final_price_label.grid(row=3, column=0, columnspan=3, pady=5)

        # Красивая текстовая сводка вместо таблицы
        summary_frame = ttk.LabelFrame(frame, text="Сводка заказа")
        summary_frame.pack(fill='both', expand=True, pady=5)

        self.text_summary = scrolledtext.ScrolledText(summary_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)
        self.text_summary.pack(fill='both', expand=True, padx=5, pady=5)

        # KP
        kp_frame = ttk.LabelFrame(frame, text="Коммерческое предложение")
        kp_frame.pack(fill='both', expand=True, pady=5)

        self.kp_text = scrolledtext.ScrolledText(kp_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.kp_text.pack(fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Копировать КП", command=self.copy_kp).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Выход", command=self.root.quit).pack(side='left', padx=5)

        # Создаем стиль для кнопок
        style = ttk.Style()
        style.configure("Accent.TButton", background=self.colors["accent"], foreground="white")

    def remove_component(self, category):
        """Удаление выбранного компонента"""
        if category in self.selected_components:
            del self.selected_components[category]
            self.component_vars[category].set('<Не выбрано>')
            self.update_summary()

    def on_component_select(self, category):
        selected = self.component_vars[category].get()
        if selected and selected != '<Не выбрано>':
            comp_name = selected.split(' (')[0]
            for comp in self.components[category]:
                if comp['name'] == comp_name:
                    quantity = self.quantity_vars[category].get() if category in self.quantity_vars else 1
                    self.selected_components[category] = {'component': comp, 'quantity': quantity}
                    break
            self.update_summary()
        elif selected == '<Не выбрано>' and category in self.selected_components:
            self.remove_component(category)

    def on_quantity_change(self, category):
        if category in self.selected_components:
            quantity = self.quantity_vars[category].get()
            self.selected_components[category]['quantity'] = quantity
            self.update_summary()

    def show_info(self, category):
        selected = self.component_vars[category].get()
        if selected and selected != '<Не выбрано>':
            comp_name = selected.split(' (')[0]
            for comp in self.components[category]:
                if comp['name'] == comp_name:
                    messagebox.showinfo(f"Информация - {category}",
                                        f"{comp['name']}\nЦена: {comp['price']}$\nХарактеристики: {comp['specs']}")
                    break

    def update_summary(self):
        self.total_price = sum(data['component']['price'] * data['quantity']
                               for data in self.selected_components.values())

        # Обновляем текстовую сводку
        self.text_summary.config(state=tk.NORMAL)
        self.text_summary.delete(1.0, tk.END)

        if self.selected_components:
            self.text_summary.insert(tk.END, "ВЫБРАННЫЕ КОМПОНЕНТЫ:\n\n", "header")

            for cat, data in self.selected_components.items():
                comp= data['component']
                qty = data['quantity']
                total = comp['price'] * qty

                self.text_summary.insert(tk.END, f"• {cat}:\n", "category")
                self.text_summary.insert(tk.END, f"   {comp['name']}")
                if qty > 1:
                    self.text_summary.insert(tk.END, f" × {qty}")
                self.text_summary.insert(tk.END, f" - {total}$\n")
                self.text_summary.insert(tk.END, f"   Характеристики: {comp['specs']}\n\n")

            self.text_summary.insert(tk.END, f"\nОБЩАЯ СТОИМОСТЬ: {self.total_price}$", "total")
        else:
            self.text_summary.insert(tk.END, "Компоненты не выбраны")

        # Настройка стилей
        self.text_summary.tag_configure("header", font=("Arial", 12, "bold"), foreground=self.colors["header"])
        self.text_summary.tag_configure("category", font=("Arial", 10, "bold"), foreground=self.colors["text"])
        self.text_summary.tag_configure("total", font=("Arial", 11, "bold"), foreground=self.colors["warning"])
        self.text_summary.config(state=tk.DISABLED)

        self.total_label.config(text=f"Общая стоимость: {self.total_price}$")
        self.update_markup()
        self.update_kp()

    def update_markup(self):
        amur = self.amur_markup.get()
        merl = self.merl_markup.get()
        total_markup = amur + merl

        self.final_price = self.total_price * (1 + total_markup / 100)

        self.total_markup.config(text=f"Общая наценка: {total_markup:.1f}%")
        self.final_price_label.config(text=f"Итоговая цена: {self.final_price:.2f}$")

    def save_config(self):
        config = {
            'selected_components': {},
            'amur_markup': self.amur_markup.get(),
            'merl_markup': self.merl_markup.get()
        }

        # Сохраняем только необходимые данные компонентов
        for category, data in self.selected_components.items():
            config['selected_components'][category] = {
                'name': data['component']['name'],
                'price': data['component']['price'],
                'specs': data['component']['specs'],
                'quantity': data['quantity']
            }

        filename = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", f"Конфигурация сохранена в файл: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_config(self):
        from tkinter import filedialog

        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Восстанавливаем компоненты
                self.selected_components = {}
                for category, comp_data in config.get('selected_components', {}).items():
                    if category in self.components:
                        # Ищем соответствующий компонент в оригинальном списке
                        for original_comp in self.components[category]:
                            if original_comp['name'] == comp_data['name']:
                                self.selected_components[category] = {
                                    'component': original_comp,
                                    'quantity': comp_data.get('quantity', 1)
                                }
                                # Обновляем интерфейс
                                self.component_vars[category].set(f"{comp_data['name']} ({comp_data['price']}$)")
                                if category in self.quantity_vars:
                                    self.quantity_vars[category].set(comp_data.get('quantity', 1))
                                break

                # Восстанавливаем наценки
                self.amur_markup.set(config.get('amur_markup', 15.0))
                self.merl_markup.set(config.get('merl_markup', 15.0))

                self.update_summary()
                messagebox.showinfo("Загрузка", "Конфигурация успешно загружена!")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию: {str(e)}")

    def reset_config(self):
        if messagebox.askyesno("Сброс", "Вы уверены, что хотите сбросить конфигурацию?"):
            self.selected_components = {}
            for var in self.component_vars.values():
                var.set('<Не выбрано>')
            for var in self.quantity_vars.values():
                var.set(1)
            self.amur_markup.set(15.0)
            self.merl_markup.set(15.0)
            self.update_summary()

    def copy_kp(self):
        self.kp_text.config(state=tk.NORMAL)
        text = self.kp_text.get(1.0, tk.END)
        self.kp_text.config(state=tk.DISABLED)

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Копирование", "Коммерческое предложение скопировано в буфер обмена!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PCConfigurator(root)
    root.mainloop()
