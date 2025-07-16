import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import json
import shutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import defaultdict
from datetime import datetime as dt

# Иконка для скрепки в base64
CLIP_ICON_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
    "AAAANwAAADcBMw9GXQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABhSURB"
    "VDiN7dKxCQAgEATBXRCs7C0sLCw8CwtPwcLGRrDQE0SJ+QcGMjA7tA+2JgJwEeIA3iQv5d4yqR7g"
    "A5a1FfIBw1QkX5Ld8t6cBwC4BwD4AQA/AOAHAPwAgB8A8AMAfgDADwD4AQA/AOAHAPwAgB8A8AMA"
    "fgDADwD4AQA/AOAHAPwAgB8A8AMAfgDADwD4AQA/AOAHAPwAgB8A8AMAfgDADwD4AQA/AOAHAPwA"
    "gB8A8AMAfgDADwD4AQA/AOAHAPwAgB8A8AMAfgDADwD4AQA/AOAHAPwAgB8A8AMAfgDADwD4AQD/"
    "A6L9S2mNUxSfAAAAAElFTkSuQmCC"
)




DARK_BG = "#21242b"
LIGHT_BG = "#21242b"
CARD_BG = "#21242b"
PRIMARY_COLOR = "#278735"  # Цвет кнопок
SECONDARY_COLOR = "#5cf772"  # Цвет полей ввода
ACCENT_COLOR = "#e74c3c"
TEXT_COLOR = "#ffffff"
LIGHT_TEXT = "#ffffff"


class JournalEntry:
    def __init__(self, date, status, name, contact, calculation_type, input_data, result,
                 payer="", payee="", attachments=None, client_id=None, intermediaries=None):
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.status = status
        self.name = name
        self.contact = contact
        self.calculation_type = calculation_type
        self.input_data = input_data
        self.result = result
        self.payer = payer
        self.payee = payee
        self.attachments = attachments or []
        self.client_id = client_id or datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.intermediaries = intermediaries or []

    def to_dict(self):
        return {
            'client_id': self.client_id,
            'date': self.date,
            'status': self.status,
            'name': self.name,
            'contact': self.contact,
            'calculation_type': self.calculation_type,
            'input_data': json.dumps(self.input_data, ensure_ascii=False),
            'result': self.result,
            'payer': self.payer,
            'payee': self.payee,
            'attachments': ';'.join(self.attachments),
            'intermediaries': json.dumps(self.intermediaries, ensure_ascii=False)
        }

    @classmethod
    def from_dict(cls, data):
        intermediaries = data.get('intermediaries', [])
        if isinstance(intermediaries, str):
            try:
                intermediaries = json.loads(intermediaries) if intermediaries else []
            except json.JSONDecodeError:
                intermediaries = []

        return cls(
            client_id=data.get('client_id', datetime.now().strftime("%Y%m%d%H%M%S%f")),
            date=data.get('date', datetime.now().strftime("%Y-%m-%d")),
            status=data.get('status', ''),
            name=data.get('name', ''),
            contact=data.get('contact', ''),
            calculation_type=data.get('calculation_type', ''),
            input_data=json.loads(data.get('input_data', '{}')),
            result=data.get('result', ''),
            payer=data.get('payer', ''),
            payee=data.get('payee', ''),
            attachments=data.get('attachments', '').split(';') if data.get('attachments') else [],
            intermediaries=intermediaries
        )


class JournalManager:
    JOURNAL_FILE = 'journal.csv'

    @classmethod
    def save_entry(cls, entry):
        file_exists = os.path.isfile(cls.JOURNAL_FILE)
        fieldnames = ['client_id', 'date', 'status', 'name', 'contact',
                      'calculation_type', 'input_data', 'result',
                      'payer', 'payee', 'attachments', 'intermediaries']

        try:
            with open(cls.JOURNAL_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(entry.to_dict())
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")
            return False

    @classmethod
    def update_entry(cls, entry):
        if not os.path.exists(cls.JOURNAL_FILE):
            return

        entries = []
        fieldnames = ['client_id', 'date', 'status', 'name', 'contact', 'calculation_type',
                      'input_data', 'result', 'payer', 'payee', 'attachments', 'intermediaries']

        with open(cls.JOURNAL_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_fieldnames = reader.fieldnames or []
            for field in fieldnames:
                if field not in existing_fieldnames:
                    existing_fieldnames.append(field)

            for row in reader:
                if row['client_id'] == entry.client_id:
                    updated_entry = entry.to_dict()
                    for field in existing_fieldnames:
                        if field not in updated_entry:
                            updated_entry[field] = row.get(field, '')
                    entries.append(updated_entry)
                else:
                    entries.append(row)

        with open(cls.JOURNAL_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=existing_fieldnames)
            writer.writeheader()
            writer.writerows(entries)

    @classmethod
    def load_entries(cls):
        if not os.path.exists(cls.JOURNAL_FILE):
            return []

        entries = []
        try:
            with open(cls.JOURNAL_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return []

                for row in reader:
                    try:
                        intermediaries = []
                        if 'intermediaries' in row and row['intermediaries']:
                            try:
                                intermediaries = json.loads(row['intermediaries'])
                            except json.JSONDecodeError:
                                intermediaries = []

                        entry = JournalEntry(
                            date=row.get('date', datetime.now().strftime("%Y-%m-%d")),
                            status=row.get('status', ''),
                            name=row.get('name', ''),
                            contact=row.get('contact', ''),
                            calculation_type=row.get('calculation_type', ''),
                            input_data=json.loads(row.get('input_data', '{}')),
                            result=row.get('result', ''),
                            payer=row.get('payer', ''),
                            payee=row.get('payee', ''),
                            attachments=row.get('attachments', '').split(';') if row.get('attachments') else [],
                            intermediaries=intermediaries,
                            client_id=row.get('client_id', datetime.now().strftime("%Y%m%d%H%M%S%f"))
                        )
                        entries.append(entry)
                    except Exception as e:
                        print(f"Ошибка при загрузке записи: {str(e)}")
                        continue
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить журнал: {str(e)}")

        return entries

    @classmethod
    def delete_entry(cls, client_id):
        if not os.path.exists(cls.JOURNAL_FILE):
            return

        entries = []
        with open(cls.JOURNAL_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['client_id'] != client_id:
                    entries.append(row)

        with open(cls.JOURNAL_FILE, 'w', newline='', encoding='utf-8') as f:
            if entries:
                writer = csv.DictWriter(f, fieldnames=entries[0].keys())
                writer.writeheader()
                writer.writerows(entries)


class Dashboard:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ttk.Frame(parent)
        self.setup_ui()

    def calculate_metrics(self, entries):
        """Рассчитывает метрики на основе записей журнала"""
        total_clients = len(entries)

        status_counts = defaultdict(int)
        income_rub = 0.0
        income_usdt = 0.0
        monthly_income_rub = defaultdict(float)
        monthly_income_usdt = defaultdict(float)

        for entry in entries:
            status_counts[entry.status] += 1

            # Парсим доход из результата
            if entry.result:
                try:
                    if "Наш доход RUB" in entry.result:
                        rub_line = [line for line in entry.result.split('\n') if "Наш доход RUB" in line][0]
                        rub_value = float(rub_line.split(":")[1].strip().split()[0].replace(',', ''))
                        income_rub += rub_value

                        # Добавляем в месячный доход
                        try:
                            month = dt.strptime(entry.date, "%Y-%m-%d").strftime("%Y-%m")
                            monthly_income_rub[month] += rub_value
                        except:
                            pass

                    if "Наш доход USDT" in entry.result:
                        usdt_line = [line for line in entry.result.split('\n') if "Наш доход USDT" in line][0]
                        usdt_value = float(usdt_line.split(":")[1].strip().split()[0].replace(',', ''))
                        income_usdt += usdt_value

                        # Добавляем в месячный доход
                        try:
                            month = dt.strptime(entry.date, "%Y-%m-%d").strftime("%Y-%m")
                            monthly_income_usdt[month] += usdt_value
                        except:
                            pass
                except Exception as e:
                    print(f"Ошибка парсинга дохода: {str(e)}")

        active_deals = status_counts.get('Активный', 0)
        completed_deals = status_counts.get('Завершен', 0)
        canceled_deals = status_counts.get('Отменен', 0)

        # Сортируем месяцы
        sorted_months = sorted(monthly_income_rub.keys())

        return {
            'total_clients': total_clients,
            'active_deals': active_deals,
            'completed_deals': completed_deals,
            'income_rub': income_rub,
            'income_usdt': income_usdt,
            'status_counts': [active_deals, completed_deals, canceled_deals],
            'monthly_income_rub': [monthly_income_rub.get(m, 0) for m in sorted_months],
            'monthly_income_usdt': [monthly_income_usdt.get(m, 0) for m in sorted_months],
            'months': [dt.strptime(m, "%Y-%m").strftime("%b") for m in sorted_months]
        }

    def setup_ui(self):
        self.frame.configure(style='Dashboard.TFrame')

        # Загружаем записи и рассчитываем метрики
        entries = JournalManager.load_entries()
        metrics = self.calculate_metrics(entries)

        # Основной контейнер с центрированием
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_container, bg=DARK_BG)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=DARK_BG)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Центральный контейнер для центрирования контента
        center_container = ttk.Frame(scrollable_frame)
        center_container.pack(expand=True, fill=tk.BOTH)

        # Заголовок
        header_frame = ttk.Frame(center_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=20, anchor='center')
        ttk.Label(header_frame, text="Статистика",
                  style='Header.TLabel', font=('Arial', 24, 'bold')).pack(pady=10)

        # Карточки KPI
        kpi_frame = ttk.Frame(center_container)
        kpi_frame.pack(fill=tk.X, padx=20, pady=10, anchor='center')

        kpi_data = [
            {"title": "Всего клиентов", "value": str(metrics['total_clients']), "change": "", "icon": "👥"},
            {"title": "Активных сделок", "value": str(metrics['active_deals']), "change": "", "icon": "📈"},
            {"title": "Завершенных", "value": str(metrics['completed_deals']), "change": "", "icon": "✅"},
            {"title": "Доход RUB", "value": f"{metrics['income_rub']:,.2f}₽", "change": "", "icon": "💰"},
            {"title": "Доход USDT", "value": f"{metrics['income_usdt']:,.2f}$", "change": "", "icon": "💵"}
        ]

        for i, data in enumerate(kpi_data):
            card = self.create_kpi_card(kpi_frame, data)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)

        # Графики
        charts_frame = ttk.Frame(center_container)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20, anchor='center')

        # Левая колонка - круговая диаграмма
        left_frame = ttk.Frame(charts_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        chart_card = ttk.Frame(left_frame, style='Card.TFrame')
        chart_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(chart_card, text="Распределение по статусам",
                  style='CardTitle.TLabel').pack(pady=10, padx=10, anchor="w")

        fig = plt.Figure(figsize=(5, 4), dpi=80, facecolor=CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        statuses = ['Активные', 'Завершенные', 'Отмененные']
        values = metrics['status_counts']
        colors = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR]

        ax.pie(values, labels=statuses, autopct='%1.1f%%',
               colors=colors, startangle=90, textprops={'color': TEXT_COLOR})
        ax.axis('equal')

        chart = FigureCanvasTkAgg(fig, chart_card)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Правая колонка - столбчатая диаграмма
        right_frame = ttk.Frame(charts_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        chart_card = ttk.Frame(right_frame, style='Card.TFrame')
        chart_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(chart_card, text="Активность по месяцам",
                  style='CardTitle.TLabel').pack(pady=10, padx=10, anchor="w")

        fig = plt.Figure(figsize=(5, 4), dpi=80, facecolor=CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        months = metrics['months']
        income_rub = metrics['monthly_income_rub']
        income_usdt = metrics['monthly_income_usdt']

        bar_width = 0.35
        x = np.arange(len(months))
        bars1 = ax.bar(x - bar_width / 2, income_rub, bar_width, label='RUB', color=PRIMARY_COLOR)
        bars2 = ax.bar(x + bar_width / 2, income_usdt, bar_width, label='USDT', color=SECONDARY_COLOR)

        ax.set_ylabel('Доход', color=TEXT_COLOR)
        ax.set_xticks(x)
        ax.set_xticklabels(months, color=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        ax.legend()

        # Цвета осей и заголовков
        for spine in ax.spines.values():
            spine.set_edgecolor(TEXT_COLOR)

        chart = FigureCanvasTkAgg(fig, chart_card)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Таблица с данными
        table_frame = ttk.Frame(center_container)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20, anchor='center')

        table_card = ttk.Frame(table_frame, style='Card.TFrame')
        table_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(table_card, text="Последние операции",
                  style='CardTitle.TLabel').pack(pady=10, padx=10, anchor="w")

        columns = ("date", "client", "type", "amount", "status")
        tree = ttk.Treeview(table_card, columns=columns, show="headings", style="Treeview")

        tree.heading("date", text="Дата")
        tree.heading("client", text="Клиент")
        tree.heading("type", text="Тип операции")
        tree.heading("amount", text="Сумма")
        tree.heading("status", text="Статус")

        tree.column("date", width=100)
        tree.column("client", width=150)
        tree.column("type", width=150)
        tree.column("amount", width=100)
        tree.column("status", width=100)

        # Заполняем таблицу реальными данными
        recent_entries = entries[-5:] if len(entries) > 5 else entries
        for entry in recent_entries:
            # Пытаемся извлечь сумму из результата
            amount = "N/A"
            if entry.result and "Наш доход RUB" in entry.result:
                try:
                    rub_line = [line for line in entry.result.split('\n') if "Наш доход RUB" in line][0]
                    amount = rub_line.split(":")[1].strip().split()[0] + "₽"
                except:
                    pass

            tree.insert("", "end", values=(
                entry.date,
                entry.name,
                entry.calculation_type,
                amount,
                entry.status
            ), iid=entry.client_id)  # Сохраняем client_id в iid

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Привязываем двойной клик для открытия записи
        tree.bind("<Double-1>", lambda event: self.open_journal_entry(tree))

        self.tree = tree

    def open_journal_entry(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            client_id = selected_item[0]
            self.app.open_journal_entry_by_id(client_id)

    def create_kpi_card(self, parent, data):
        card = ttk.Frame(parent, style='Card.TFrame')

        # Верхняя часть с иконкой
        top_frame = ttk.Frame(card)
        top_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(top_frame, text=data["icon"], font=('Arial', 24),
                  foreground=TEXT_COLOR).pack(side=tk.LEFT)

        # Текст справа
        text_frame = ttk.Frame(top_frame)
        text_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(text_frame, text=data["title"],
                  style='CardTitle.TLabel').pack(anchor="e")
        ttk.Label(text_frame, text=data["change"],
                  style='CardSubtitle.TLabel').pack(anchor="e")

        # Основное значение
        ttk.Label(card, text=data["value"],
                  style='KPIValue.TLabel').pack(pady=10)

        # Прогресс бар
        progress = ttk.Progressbar(card, orient="horizontal",
                                   length=100, mode="determinate",
                                   style="Custom.Horizontal.TProgressbar")
        progress.pack(fill=tk.X, padx=15, pady=10)
        progress['value'] = 65  # Пример значения

        return card


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Клиентская система")
        self.root.state('zoomed')
        self.current_client = None
        self.saved_client_data = None

        # Установка фона главного окна
        self.root.configure(bg=DARK_BG)

        # Настройка стилей
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('alt')  # Используем тему, которая поддерживает кастомные стили

        # Общие стили
        style.configure('.', background=DARK_BG, foreground=TEXT_COLOR, font=('Arial', 12))
        style.configure('Header.TFrame', background=DARK_BG)
        style.configure('Header.TLabel', background=DARK_BG, foreground=TEXT_COLOR,
                        font=('Arial', 16, 'bold'))

        # Стили для карточек
        style.configure('Card.TFrame', background=CARD_BG, borderwidth=1,
                        relief="solid", padding=10, bordercolor="#3c4049")
        style.configure('CardTitle.TLabel', background=CARD_BG,
                        foreground=TEXT_COLOR, font=('Arial', 12, 'bold'))
        style.configure('CardSubtitle.TLabel', background=CARD_BG,
                        foreground=SECONDARY_COLOR, font=('Arial', 10))
        style.configure('KPIValue.TLabel', background=CARD_BG,
                        foreground=TEXT_COLOR, font=('Arial', 24, 'bold'))

        # Стили для боковой панели
        style.configure('Sidebar.TFrame', background=DARK_BG)
        style.configure('Sidebar.TLabel', background=DARK_BG, foreground=TEXT_COLOR)

        # Стиль для кнопок - зеленый (#278735)
        style.configure('TButton', background=PRIMARY_COLOR,
                        foreground=TEXT_COLOR, font=('Arial', 12))
        style.map('TButton',
                  background=[('active', '#1f6b2a')],
                  foreground=[('active', 'white')])

        # Стиль для активной кнопки в боковой панели
        style.configure('Active.TButton', background='#1f6b2a',
                        foreground=TEXT_COLOR, font=('Arial', 12))

        # Стили для Treeview (таблицы)
        style.configure("Treeview", background=CARD_BG, foreground=TEXT_COLOR,
                        fieldbackground=CARD_BG, borderwidth=0)
        style.configure("Treeview.Heading", background=PRIMARY_COLOR,
                        foreground=TEXT_COLOR, borderwidth=0, font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', PRIMARY_COLOR)],
                  foreground=[('selected', TEXT_COLOR)])

        # Стиль для полей ввода - светло-зеленый фон (#5cf772)
        style.configure('TEntry', fieldbackground=SECONDARY_COLOR, foreground='black')
        style.configure('TCombobox', fieldbackground=SECONDARY_COLOR, foreground='black')

        # Стиль для текстового поля
        style.configure('TText', background=CARD_BG, foreground=TEXT_COLOR)

        # Стиль для прогресс-бара
        style.configure("Custom.Horizontal.TProgressbar", background=PRIMARY_COLOR,
                        troughcolor=DARK_BG, thickness=10)

    def setup_ui(self):
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Боковая панель
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Логотип
        logo_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        logo_frame.pack(pady=20)
        ttk.Label(logo_frame, text="💼", font=('Arial', 24),
                  style='Sidebar.TLabel').pack()
        ttk.Label(logo_frame, text="Клиентская система",
                  style='Sidebar.TLabel', font=('Arial', 12)).pack(pady=5)

        # Кнопки навигации
        nav_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        nav_frame.pack(pady=20)

        self.main_btn = ttk.Button(nav_frame, text="Главная",
                                   command=self.show_main_form,
                                   style='Active.TButton')
        self.main_btn.pack(pady=5, fill=tk.X)

        self.stats_btn = ttk.Button(nav_frame, text="Статистика",
                                    command=self.show_dashboard,
                                    style='TButton')
        self.stats_btn.pack(pady=5, fill=tk.X)

        self.journal_btn = ttk.Button(nav_frame, text="Журнал",
                                      command=self.show_journal,
                                      style='TButton')
        self.journal_btn.pack(pady=5, fill=tk.X)

        # Выход
        exit_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        exit_frame.pack(side=tk.BOTTOM, pady=20)
        ttk.Button(exit_frame, text="Выход", command=self.root.destroy,
                   style='TButton').pack(pady=5, fill=tk.X)

        # Контейнер для контента
        self.content_container = ttk.Frame(main_container)
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Показываем главную форму по умолчанию
        self.show_main_form()

    def show_main_form(self):
        # Обновление стилей кнопок навигации
        self.main_btn.configure(style='Active.TButton')
        self.stats_btn.configure(style='TButton')
        self.journal_btn.configure(style='TButton')

        # Очистка контейнера контента
        self.clear_frame()

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_frame = main_frame

        # Заголовок
        ttk.Label(main_frame, text="Добавление нового клиента",
                  style='Header.TLabel', font=('Arial', 16, 'bold')).pack(pady=20)

        # Форма ввода
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)

        # Поле статуса
        ttk.Label(form_frame, text="Статус клиента:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.status_var = tk.StringVar()
        status_combobox = ttk.Combobox(form_frame, textvariable=self.status_var,
                                       values=('Активный', 'Завершен', 'Отменен'),
                                       font=('Arial', 12), width=25)
        status_combobox.grid(row=0, column=1, pady=5, padx=5)

        # Поле имени
        ttk.Label(form_frame, text="Имя клиента:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame, font=('Arial', 12), width=27)
        self.name_entry.grid(row=1, column=1, pady=5, padx=5)

        # Поле контактов
        ttk.Label(form_frame, text="Email/Телефон:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.contact_entry = ttk.Entry(form_frame, font=('Arial', 12), width=27)
        self.contact_entry.grid(row=2, column=1, pady=5, padx=5)

        # Кнопка сохранения
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Создать клиента", command=self.save_client).pack()

        # Статусная метка
        self.status_label = ttk.Label(main_frame, text="", foreground='green')
        self.status_label.pack(pady=10)

    def show_dashboard(self):
        # Обновляем стили кнопок
        self.main_btn.configure(style='TButton')
        self.stats_btn.configure(style='Active.TButton')
        self.journal_btn.configure(style='TButton')

        # Очищаем контейнер контента
        self.clear_frame()

        # Создаем дашборд
        self.dashboard = Dashboard(self.content_container, self)
        self.dashboard.frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = self.dashboard.frame

    def show_journal(self, client_id_to_open=None):
        # Обновляем стили кнопок
        self.main_btn.configure(style='TButton')
        self.stats_btn.configure(style='TButton')
        self.journal_btn.configure(style='Active.TButton')

        # Очищаем контейнер контента
        self.clear_frame()

        # Создаем новый фрейм для журнала
        journal_frame = ttk.Frame(self.content_container)
        journal_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_frame = journal_frame  # Сохраняем ссылку на текущий фрейм

        header = ttk.Label(journal_frame, text="Журнал клиентов", style='Header.TLabel')
        header.pack(pady=20)

        # Загружаем записи
        entries = JournalManager.load_entries()
        self.entries = entries

        # Создаем таблицу
        columns = ("files", "date", "status", "name", "contact", "payer", "payee")
        tree = ttk.Treeview(journal_frame, columns=columns, show="headings", selectmode="browse")

        # Настраиваем заголовки
        tree.heading("files", text="Файлы")
        tree.heading("date", text="Дата")
        tree.heading("status", text="Статус")
        tree.heading("name", text="Имя")
        tree.heading("contact", text="Контакты")
        tree.heading("payer", text="Кто платит")
        tree.heading("payee", text="Кому платим")

        # Настраиваем столбцы
        tree.column("files", width=80, anchor="center")
        tree.column("date", width=100, anchor="center")
        tree.column("status", width=100, anchor="center")
        tree.column("name", width=150, anchor="w")
        tree.column("contact", width=150, anchor="w")
        tree.column("payer", width=150, anchor="w")
        tree.column("payee", width=150, anchor="w")

        # Заполняем таблицу данными
        for entry in entries:
            has_files = "Есть файлы" if entry.attachments else "Нет файлов"
            tree.insert("", "end", values=(
                has_files,
                entry.date,
                entry.status,
                entry.name,
                entry.contact,
                entry.payer,
                entry.payee
            ), iid=entry.client_id)

        # Упаковываем таблицу
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Добавляем кнопки управления
        btn_frame = ttk.Frame(journal_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Изменить статус",
                   command=lambda: self.change_status(tree, entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Добавить файлы",
                   command=lambda: self.add_attachments(tree, entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Скачать файлы",
                   command=lambda: self.download_attachments(tree, entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить запись",
                   command=lambda: self.delete_entry(tree, entries)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Назад", command=self.show_main_form).pack(side=tk.LEFT, padx=5)

        # Привязываем двойной клик для открытия записи
        tree.bind("<Double-1>", lambda event: self.open_journal_entry(tree, entries))

        # Разрешаем редактирование столбцов "Кто платит" и "Кому платим"
        tree.bind("<ButtonRelease-1>", lambda event: self.on_click(event, tree, entries))

        # Сохраняем ссылку на дерево
        self.tree = tree

        # Открываем запись, если указан client_id_to_open
        if client_id_to_open:
            if client_id_to_open in tree.get_children():
                tree.selection_set(client_id_to_open)
                tree.focus(client_id_to_open)
                # Прокручиваем к выбранному элементу
                tree.see(client_id_to_open)


    def open_journal_entry_by_id(self, client_id):
        self.show_journal(client_id_to_open=client_id)

    def download_attachments(self, tree, entries):
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для скачивания файлов")
            return

        client_id = selected[0]
        entry = next((e for e in entries if e.client_id == client_id), None)
        if not entry:
            return

        if not entry.attachments:
            messagebox.showinfo("Информация", "В этой записи нет прикрепленных файлов")
            return

        # Создаем окно выбора файлов
        download_window = tk.Toplevel(self.root)
        download_window.title("Скачать файлы")
        download_window.geometry("400x400")
        download_window.resizable(False, False)

        # Основной фрейм для содержимого
        main_frame = ttk.Frame(download_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для списка файлов с прокруткой
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas и Scrollbar
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Чекбоксы для файлов
        check_vars = []
        for file_path in entry.attachments:
            if not file_path:
                continue
            var = tk.BooleanVar(value=True)
            check_vars.append((file_path, var))
            cb = ttk.Checkbutton(scrollable_frame, text=os.path.basename(file_path), variable=var)
            cb.pack(anchor='w', padx=5, pady=2)

        # Функции для работы с файлами
        def download_selected():
            selected_files = [fp for fp, var in check_vars if var.get() and fp]
            if not selected_files:
                messagebox.showinfo("Информация", "Выберите хотя бы один файл")
                return

            folder = filedialog.askdirectory()
            if not folder:
                return

            success = 0
            for src in selected_files:
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(folder, os.path.basename(src))
                if os.path.exists(dst):
                    if not messagebox.askyesno("Подтверждение", f"Перезаписать {os.path.basename(src)}?"):
                        continue
                try:
                    shutil.copy2(src, dst)
                    success += 1
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка копирования {src}: {str(e)}")

            if success > 0:
                messagebox.showinfo("Успех", f"Скачано {success} файлов")
            download_window.destroy()

        def download_all():
            for _, var in check_vars:
                var.set(True)
            download_selected()

        def open_folder():
            if entry.attachments:
                folder = os.path.dirname(entry.attachments[0])
                if os.path.exists(folder):
                    os.startfile(folder)
                else:
                    messagebox.showinfo("Информация", "Папка недоступна")

        # Фрейм для кнопок
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        # Центрируем кнопки
        center_frame = ttk.Frame(btn_frame)
        center_frame.pack()

        ttk.Button(center_frame, text="Скачать все", command=download_all, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_frame, text="Скачать выбранные", command=download_selected, width=15).pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Button(center_frame, text="Открыть папку", command=open_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_frame, text="Отмена", command=download_window.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def on_click(self, event, tree, entries):
        """Обработка кликов для редактирования ячеек"""
        region = tree.identify("region", event.x, event.y)
        column = tree.identify_column(event.x)
        row_id = tree.focus()

        if not row_id:
            return

        # Разрешаем редактирование только для столбцов "Кто платит" и "Кому платим"
        if region == "cell" and column in ["#6", "#7"]:
            # Получаем текущие значения
            values = tree.item(row_id, "values")
            col_index = int(column[1:]) - 1  # Преобразуем "#6" в 5

            # Создаем поле для редактирования
            entry_edit = ttk.Entry(tree)
            entry_edit.insert(0, values[col_index])
            entry_edit.select_range(0, tk.END)
            entry_edit.focus()

            # Размещаем поле для редактирования
            x, y, width, height = tree.bbox(row_id, column)
            entry_edit.place(x=x, y=y, width=width, height=height)

            # Обработка завершения редактирования
            def save_edit(event):
                # Обновляем значение в таблице
                new_values = list(values)
                new_values[col_index] = entry_edit.get()
                tree.item(row_id, values=new_values)

                # Обновляем запись в данных
                client_id = row_id
                for entry in entries:
                    if entry.client_id == client_id:
                        if column == "#6":
                            entry.payer = entry_edit.get()
                        elif column == "#7":
                            entry.payee = entry_edit.get()
                        JournalManager.update_entry(entry)
                        break

                entry_edit.destroy()

            entry_edit.bind("<Return>", save_edit)
            entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

    def change_status(self, tree, entries):
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для изменения статуса")
            return

        client_id = selected[0]  # Сохраняем ID выбранной записи
        entry = next((e for e in entries if e.client_id == client_id), None)
        if not entry:
            return

        # Создаем диалоговое окно
        status_dialog = tk.Toplevel(self.root)
        status_dialog.title("Изменение статуса")
        status_dialog.resizable(False, False)
        status_dialog.transient(self.root)
        status_dialog.grab_set()

        ttk.Label(status_dialog, text="Выберите новый статус:").pack(pady=10)

        status_var = tk.StringVar(value=entry.status)
        status_combobox = ttk.Combobox(status_dialog, textvariable=status_var,
                                       values=('Активный', 'Завершен', 'Отменен'),
                                       state="readonly", width=20)
        status_combobox.pack(pady=5)
        status_combobox.current(['Активный', 'Завершен', 'Отменен'].index(entry.status))

        def save_status():
            new_status = status_var.get()
            if new_status:
                entry.status = new_status
                try:
                    JournalManager.update_entry(entry)

                    # Обновляем таблицу
                    tree.item(client_id, values=(
                        "Есть файлы" if entry.attachments else "Нет файлов",
                        entry.date,
                        entry.status,
                        entry.name,
                        entry.contact,
                        entry.payer,
                        entry.payee
                    ))
                    status_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обновить статус: {str(e)}")

        btn_frame = ttk.Frame(status_dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=status_dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_attachments(self, tree, entries):
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для добавления файлов")
            return

        client_id = selected[0]
        entry = next((e for e in entries if e.client_id == client_id), None)
        if not entry:
            return

        files = filedialog.askopenfilenames(title="Выберите файлы для прикрепления")
        if files:
            entry.attachments.extend(files)
            JournalManager.update_entry(entry)

            # Обновляем таблицу
            tree.item(selected[0], values=(
                "Есть файлы" if entry.attachments else "Нет файлов",
                entry.date,
                entry.status,
                entry.name,
                entry.contact,
                entry.payer,
                entry.payee
            ))

    def delete_entry(self, tree, entries):
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            client_id = selected[0]
            JournalManager.delete_entry(client_id)
            tree.delete(selected[0])

    def open_journal_entry(self, tree, entries):
        selected = tree.selection()
        if not selected:
            return

        client_id = selected[0]
        entry = next((e for e in entries if e.client_id == client_id), None)
        if not entry:
            return

        # Определяем, доступно ли редактирование
        read_only = entry.status in ["Завершен", "Отменен"]

        # Очищаем контейнер контента
        self.clear_frame()

        # В зависимости от типа расчета открываем соответствующую форму
        if entry.calculation_type == "Анализ":
            self.show_analysis_form(entry, read_only)
        elif entry.calculation_type == "Смешанный RUB/Валюта":
            self.show_mixed_currency_form(entry, read_only)
        elif entry.calculation_type == "Б/нал руб- $$-usdt-кэш руб":
            self.show_cash_usdt_form(entry, read_only)
        elif entry.calculation_type == "Б/нал руб-кэш руб":
            self.show_cash_rub_form(entry, read_only)

    def recalculate(self, entry, input_fields, result_text):
        # Обновляем входные данные
        for key, widget in input_fields.items():
            entry.input_data[key] = widget.get()

        # Обновляем payer/payee
        entry.payer = input_fields['payer'].get()
        entry.payee = input_fields['payee'].get()

        # Выполняем пересчет в зависимости от типа расчета
        result_text.delete(1.0, tk.END)

        try:
            if entry.calculation_type == "Б/нал руб- $$-usdt-кэш руб":
                # Извлекаем данные из полей
                calc_option = int(entry.input_data.get('calc_option', 2))
                commission_pct = float(entry.input_data.get('commission_pct', '0').replace(',', '.')) / 100
                amount = float(entry.input_data.get('amount', '0').replace(',', '.'))
                cb_rate = float(entry.input_data.get('cb_rate', '0').replace(',', '.'))
                buy_percent = float(entry.input_data.get('buy_percent', '0').replace(',', '.'))
                our_percent = float(entry.input_data.get('our_percent', '0').replace(',', '.'))
                rapira_rate = float(entry.input_data.get('rapira_rate', '0').replace(',', '.'))

                # Логика расчета
                if calc_option == 1:  # "Сколько вернуть клиенту"
                    client_receives = amount
                    client_gives = client_receives / (1 - commission_pct)
                    required_usdt_amount = client_gives
                else:  # "Сколько клиент должен дать"
                    required_usdt_amount = amount

                buy_rate = cb_rate + (cb_rate * buy_percent / 100)
                total_percent = our_percent + buy_percent
                sell_rate = cb_rate + (cb_rate * total_percent / 100)

                usdt_to_give = required_usdt_amount / buy_rate
                usdt_to_client = required_usdt_amount / sell_rate
                our_profit_usdt = usdt_to_give - usdt_to_client
                our_profit_rub = our_profit_usdt * rapira_rate

                # Формируем результат
                result = f"════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n"
                if calc_option == 1:
                    result += f"Клиент хочет получить: {client_receives:.2f} RUB\n"
                    result += f"Клиент должен отдать: {required_usdt_amount:.2f} RUB\n"
                    result += f"Комиссия: {commission_pct * 100:.2f}%\n\n"

                result += f"Наш доход RUB: {our_profit_rub:.2f}\n"
                result += f"Наш доход USDT/$: {our_profit_usdt:.6f}\n"
                result += f"Кол-во USDT/$ отданных клиенту: {usdt_to_client:.6f}\n"
                result += f"Кол-во RUB отданных клиенту: {usdt_to_client * rapira_rate:.2f}\n\n"
                result += "════════════════════════════════════\n"
                result += f"Курс покупки: {buy_rate:.4f}\n"
                result += f"Курс продажи: {sell_rate:.4f}\n"
                result += f"Курс Рапира: {rapira_rate:.2f}\n"

                result_text.insert(tk.END, result)
                entry.result = result

            elif entry.calculation_type == "Б/нал руб-кэш руб":
                # Извлекаем данные из полей
                option = int(entry.input_data.get('option', 1))
                amount = float(entry.input_data.get('amount', '0').replace(',', '.'))
                commission = float(entry.input_data.get('commission', '0').replace(',', '.')) / 100

                # Логика расчета
                result = ""
                if option == 1:  # Сколько вернуть клиенту
                    client_return = amount
                    client_give = client_return / (1 - commission)

                    result += "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n"
                    result += f"Клиент должен отдать: {client_give:.2f} RUB\n"
                    result += f"Комиссия ({commission * 100:.2f}%): {(client_give - client_return):.2f} RUB\n"

                    # Пропускаем логику посредников для краткости

                else:  # Сколько клиент должен дать
                    client_amount = amount
                    client_receives = client_amount - client_amount * commission

                    result += "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n"
                    result += f"Клиент получит: {client_receives:.2f} RUB\n"
                    result += f"Комиссия ({commission * 100:.2f}%): {(client_amount * commission):.2f} RUB\n"

                    # Пропускаем логику посредников для краткости

                result_text.insert(tk.END, result)
                entry.result = result

            elif entry.calculation_type == "Смешанный RUB/Валюта":
                # Извлекаем данные из полей
                start_capital = float(entry.input_data.get('start_capital', '0').replace(',', '.'))
                capital_percentages = int(entry.input_data.get('capital_percentages', '50'))
                cb_today = float(entry.input_data.get('cb_today', '0').replace(',', '.'))
                extra_charg = float(entry.input_data.get('extra_charg', '0').replace(',', '.'))
                my_percent = float(entry.input_data.get('my_percent', '0').replace(',', '.'))
                rapira = float(entry.input_data.get('rapira', '0').replace(',', '.'))
                bank_commission = float(entry.input_data.get('bank_commission', '0').replace(',', '.'))

                # Расчет сумм в RUB
                capital_ru = start_capital * capital_percentages / 100
                capital_ru_two = start_capital - capital_ru

                # Расчет комиссий
                extra_charge = extra_charg / 100
                my_percentages = (my_percent + extra_charge) / 100
                bank_commission_pct = bank_commission / 100

                # Расчет USDT для клиента
                total_usdt_klient = capital_ru_two / (cb_today * (1 + my_percentages))

                # Расчет RUB для клиента
                capital_client_ru = capital_ru * (1 - bank_commission_pct)

                # Расчет курсов
                markup_rate = cb_today * (1 + extra_charge)
                total_rate = cb_today * (1 + (extra_charg + my_percent) / 100)

                # Расчет доходов
                total_usdt = capital_ru_two / markup_rate
                our_usdt = total_usdt - total_usdt_klient
                our_rub = our_usdt * rapira

                # Формируем результат
                result = "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n"
                result += f"Клиент получит:\n"
                result += f"• RUB: {capital_client_ru:.2f}\n"
                result += f"• USDT: {total_usdt_klient:.6f}\n\n"
                result += "Ваш доход:\n"
                result += f"• RUB: {our_rub:.2f}\n"
                result += f"• USDT: {our_usdt:.6f}\n\n"
                result += "════════════════════════════════════\n"
                result += f"Исходная сумма: {start_capital:.2f} RUB\n"
                result += f"Распределение: {capital_percentages}% RUB, {100 - capital_percentages}% USDT\n"
                result += f"Курс ЦБ: {cb_today:.4f}\n"
                result += f"Курс с наценкой: {markup_rate:.4f}\n"
                result += f"Курс с вашим процентом: {total_rate:.4f}\n"
                result += f"Курс Рапира: {rapira:.2f}\n"

                result_text.insert(tk.END, result)
                entry.result = result

            elif entry.calculation_type == "Анализ":
                # Извлекаем данные из полей
                amount = float(entry.input_data.get('amount', '0').replace(',', '.'))
                commission = float(entry.input_data.get('commission', '0').replace(',', '.')) / 100
                cb_rate = float(entry.input_data.get('cb_rate', '0').replace(',', '.'))
                buy_percent = float(entry.input_data.get('buy_percent', '0').replace(',', '.'))
                our_percent = float(entry.input_data.get('our_percent', '0').replace(',', '.'))
                rapira_rate = float(entry.input_data.get('rapira_rate', '0').replace(',', '.'))

                # Логика расчета
                buy_rate = cb_rate + (cb_rate * buy_percent / 100)
                total_percent = our_percent + buy_percent
                sell_rate = cb_rate + (cb_rate * total_percent / 100)

                # Выбор варианта расчета
                option = int(entry.input_data.get('option', 1))
                if option == 1:  # Сколько вернуть клиенту
                    client_receives = amount
                    client_gives = client_receives / (1 - commission)
                    required_usdt_amount = client_gives
                else:  # Сколько клиент должен дать
                    required_usdt_amount = amount

                usdt_to_give = required_usdt_amount / buy_rate
                usdt_to_client = required_usdt_amount / sell_rate
                our_profit_usdt = usdt_to_give - usdt_to_client
                our_profit_rub = our_profit_usdt * rapira_rate

                # Формируем результат
                result = f"════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n"
                if option == 1:
                    result += f"Клиент хочет получить: {client_receives:.2f} RUB\n"
                    result += f"Клиент должен отдать: {required_usdt_amount:.2f} RUB\n"
                    result += f"Комиссия: {commission * 100:.2f}%\n\n"

                result += f"Наш доход RUB: {our_profit_rub:.2f}\n"
                result += f"Наш доход USDT/$: {our_profit_usdt:.6f}\n"
                result += f"Кол-во USDT/$ отданных клиенту: {usdt_to_client:.6f}\n"
                result += f"Кол-во RUB отданных клиенту: {usdt_to_client * rapira_rate:.2f}\n\n"
                result += "════════════════════════════════════\n"
                result += f"Курс покупки: {buy_rate:.4f}\n"
                result += f"Курс продажи: {sell_rate:.4f}\n"
                result += f"Курс Рапира: {rapira_rate:.2f}\n"

                result_text.insert(tk.END, result)
                entry.result = result

        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Ошибка при пересчете: {str(e)}")

    def save_journal_changes(self, entry, input_fields, result_text, window):
        # Обновляем входные данные
        for key, widget in input_fields.items():
            entry.input_data[key] = widget.get()

        # Обновляем результат
        entry.result = result_text.get(1.0, tk.END)

        # Сохраняем изменения
        JournalManager.update_entry(entry)
        messagebox.showinfo("Сохранено", "Изменения успешно сохранены")
        window.destroy()

    def cancel_journal_edit(self, entry, original_data, original_result, window):
        # Восстанавливаем исходные данные
        entry.input_data = original_data.copy()
        entry.result = original_result
        window.destroy()

    def save_to_journal(self, calculation_type, input_data, result):
        """Сохраняет запись в журнал"""
        if not hasattr(self, 'saved_client_data'):
            messagebox.showerror("Ошибка", "Сначала создайте клиента")
            return

        # Создаем новую запись
        entry = JournalEntry(
            date=datetime.now().strftime("%Y-%m-%d"),
            status=self.saved_client_data['status'],
            name=self.saved_client_data['name'],
            contact=self.saved_client_data['contact'],
            calculation_type=calculation_type,
            input_data=input_data,
            result=result,
            payer="",  # Добавляем обязательные поля
            payee=""
        )

        # Сохраняем запись
        JournalManager.save_entry(entry)

        # Показываем сообщение об успехе
        messagebox.showinfo("Успех", "Запись успешно сохранена в журнал")
        self.show_journal()  # Переходим сразу в журнал

    def show_action_buttons(self):
        # Обновление стилей кнопок навигации
        self.main_btn.configure(style='Active.TButton')
        self.stats_btn.configure(style='TButton')
        self.journal_btn.configure(style='TButton')

        # Очистка контейнера контента
        self.clear_frame()

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.current_frame = main_frame

        # Заголовок
        ttk.Label(main_frame, text="Выберите действие",
                  style='Header.TLabel', font=('Arial', 16, 'bold')).pack(pady=20)

        # Контейнер для кнопок
        btn_container = ttk.Frame(main_frame)
        btn_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)

        # Список действий
        actions = [
            ("Анализ", self.show_analysis_form),
            ("Смешанный RUB/Валюта", self.show_mixed_currency_form),
            ("Б/нал руб- $$-usdt-кэш руб", self.show_cash_usdt_form),
            ("Б/нал руб-кэш руб", self.show_cash_rub_form)
        ]

        # Создание кнопок действий
        for i, (text, command) in enumerate(actions):
            btn = ttk.Button(
                btn_container,
                text=text,
                command=command,
                style='TButton',
                width=30,
                padding=10
            )
            btn.pack(pady=15, ipady=10)

        # Кнопка возврата
        ttk.Button(
            btn_container,
            text="Назад",
            command=self.show_main_form,
            width=15
        ).pack(pady=20)

    def setup_scrollable_frame(self, parent):
        """Создает скроллируемую область в указанном родительском контейнере"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame, container

    def show_analysis_form(self, entry=None, read_only=False):
        self.clear_frame()
        is_edit_mode = entry is not None

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = main_frame

        # Создание скроллируемой области
        scrollable_frame, container = self.setup_scrollable_frame(main_frame)

        # Центральный контейнер
        center_container = ttk.Frame(scrollable_frame)
        center_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        header = ttk.Label(center_container, text="Анализ", style='Header.TLabel')
        header.pack(pady=10)

        # Радиокнопки выбора
        option_frame = ttk.Frame(center_container)
        option_frame.pack(fill=tk.X, pady=5)

        self.analysis_option = tk.IntVar(value=1)
        rb_frame = ttk.Frame(option_frame)
        rb_frame.pack()

        rb1 = ttk.Radiobutton(rb_frame, text="Сколько вернуть клиенту",
                              variable=self.analysis_option, value=1,
                              state='normal' if not read_only else 'disabled')
        rb2 = ttk.Radiobutton(rb_frame, text="Сколько клиент должен дать",
                              variable=self.analysis_option, value=2,
                              state='normal' if not read_only else 'disabled')
        rb1.pack(side=tk.LEFT, padx=10)
        rb2.pack(side=tk.LEFT, padx=10)

        # Поля ввода суммы и комиссии
        input_frame = ttk.Frame(center_container)
        input_frame.pack(fill=tk.X, pady=5)

        input_grid = ttk.Frame(input_frame)
        input_grid.pack()

        ttk.Label(input_grid, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.analysis_amount_entry = ttk.Entry(input_grid, font=('Arial', 12), width=20,
                                               state='normal' if not read_only else 'disabled')
        self.analysis_amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_grid, text="Комиссия (%):").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.analysis_commission_entry = ttk.Entry(input_grid, font=('Arial', 12), width=10,
                                                   state='normal' if not read_only else 'disabled')
        self.analysis_commission_entry.grid(row=0, column=3, padx=5, pady=5)

        # Две колонки (USDT слева, Рубли справа)
        columns_frame = ttk.Frame(center_container)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Левая колонка - USDT
        left_frame = ttk.LabelFrame(columns_frame, text="USDT Расчет")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        crypto_form = ttk.Frame(left_frame)
        crypto_form.pack(fill=tk.X, padx=10, pady=10)

        fields = ["Курс ЦБ:", "Проценты к покупке (1.5):", "Ваш процент (0.2):", "Курс Рапира:"]
        self.crypto_entries = []

        for i, field in enumerate(fields):
            row_frame = ttk.Frame(crypto_form)
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=field, width=25, anchor='e').pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(row_frame, font=('Arial', 12), width=15,
                              state='normal' if not read_only else 'disabled')
            entry.pack(side=tk.LEFT, padx=5)
            self.crypto_entries.append(entry)

        self.calc_crypto_btn = ttk.Button(left_frame, text="Рассчитать USDT",
                                          command=self.calculate_analysis_crypto,
                                          state='normal' if not read_only else 'disabled')
        self.calc_crypto_btn.pack(pady=5)

        self.crypto_result_text = tk.Text(left_frame, height=10, font=('Arial', 10), wrap=tk.WORD)
        self.crypto_result_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Правая колонка - Рубли
        right_frame = ttk.LabelFrame(columns_frame, text="Рублевый Расчет")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.intermediaries_frame_analysis = ttk.Frame(right_frame)
        self.intermediaries_frame_analysis.pack(fill=tk.X, padx=10, pady=5)

        intermediaries = self.load_intermediaries()
        intermediary_names = [name for name, _ in intermediaries]

        select_frame = ttk.Frame(self.intermediaries_frame_analysis)
        select_frame.pack(fill=tk.X, pady=2)

        ttk.Label(select_frame, text="Выберите посредника:").pack(side=tk.LEFT, padx=5)
        self.intermediary_var_analysis = tk.StringVar()
        self.intermediary_combobox_analysis = ttk.Combobox(select_frame,
                                                           textvariable=self.intermediary_var_analysis,
                                                           values=intermediary_names,
                                                           state="readonly", width=20)
        self.intermediary_combobox_analysis.pack(side=tk.LEFT, padx=5)

        self.add_intermediary_btn = ttk.Button(select_frame, text="Добавить",
                                               command=self.add_selected_intermediary_analysis,
                                               state='normal' if not read_only else 'disabled')
        self.add_intermediary_btn.pack(side=tk.LEFT, padx=5)

        self.new_intermediary_btn = ttk.Button(self.intermediaries_frame_analysis,
                                               text="Создать нового посредника",
                                               command=self.add_intermediary_analysis,
                                               state='normal' if not read_only else 'disabled')
        self.new_intermediary_btn.pack(pady=5)

        self.current_intermediaries_frame_analysis = ttk.LabelFrame(right_frame, text="Текущие посредники")
        self.current_intermediaries_frame_analysis.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        self.intermediaries_list_analysis = []
        self.update_intermediaries_display_analysis()

        self.calc_rub_btn = ttk.Button(right_frame, text="Рассчитать Рубли",
                                       command=self.calculate_analysis_rub,
                                       state='normal' if not read_only else 'disabled')
        self.calc_rub_btn.pack(pady=5)

        self.rub_result_text = tk.Text(right_frame, height=10, font=('Arial', 10), wrap=tk.WORD)
        self.rub_result_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Если редактируем существующую запись
        if is_edit_mode:
            self.analysis_option.set(entry.input_data.get('option', 1))
            self.analysis_amount_entry.insert(0, entry.input_data.get('amount', ''))
            self.analysis_commission_entry.insert(0, entry.input_data.get('commission', ''))
            self.crypto_entries[0].insert(0, entry.input_data.get('cb_rate', ''))
            self.crypto_entries[1].insert(0, entry.input_data.get('buy_percent', ''))
            self.crypto_entries[2].insert(0, entry.input_data.get('our_percent', ''))
            self.crypto_entries[3].insert(0, entry.input_data.get('rapira_rate', ''))

            if hasattr(entry, 'intermediaries') and entry.intermediaries:
                self.intermediaries_list_analysis = entry.intermediaries
            else:
                self.intermediaries_list_analysis = entry.input_data.get('intermediaries', [])

            self.update_intermediaries_display_analysis()
            self.crypto_result_text.insert(tk.END, entry.result)
            self.rub_result_text.insert(tk.END, entry.result)

        # Кнопки управления
        btn_frame = ttk.Frame(center_container)
        btn_frame.pack(pady=10)

        if is_edit_mode:
            if not read_only:
                ttk.Button(btn_frame, text="Сохранить изменения",
                           command=lambda: self.save_analysis(entry)).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="Назад в журнал", command=self.show_journal).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Button(btn_frame, text="Сохранить в журнал", command=self.save_analysis).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="Назад", command=self.show_action_buttons).pack(side=tk.LEFT, padx=10)
    def save_analysis(self, entry=None):
        input_data = {
            'option': self.analysis_option.get(),
            'amount': self.analysis_amount_entry.get(),
            'commission': self.analysis_commission_entry.get(),
            'cb_rate': self.crypto_entries[0].get(),
            'buy_percent': self.crypto_entries[1].get(),
            'our_percent': self.crypto_entries[2].get(),
            'rapira_rate': self.crypto_entries[3].get(),
            'intermediaries': self.intermediaries_list_analysis
        }
        result = self.crypto_result_text.get(1.0, tk.END)

        if entry is None:  # Новая запись
            if not hasattr(self, 'saved_client_data'):
                messagebox.showerror("Ошибка", "Сначала создайте клиента")
                return
            self.save_to_journal("Анализ", input_data, result)
            self.show_main_form()
        else:  # Редактирование существующей
            entry.input_data = input_data
            entry.result = result
            entry.intermediaries = self.intermediaries_list_analysis  # Сохраняем посредников
            JournalManager.update_entry(entry)
            self.show_journal()

    def calculate_analysis_crypto(self):
        # Получаем данные из полей
        try:
            amount = float(self.analysis_amount_entry.get().replace(',', '.'))
            commission = float(self.analysis_commission_entry.get().replace(',', '.')) / 100
            cb_rate = float(self.crypto_entries[0].get().replace(',', '.'))
            buy_percent = float(self.crypto_entries[1].get().replace(',', '.'))
            our_percent = float(self.crypto_entries[2].get().replace(',', '.'))
            rapira_rate = float(self.crypto_entries[3].get().replace(',', '.'))
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")
            return

        # Расчет курсов
        buy_rate = cb_rate + (cb_rate * buy_percent / 100)
        total_percent = our_percent + buy_percent
        sell_rate = cb_rate + (cb_rate * total_percent / 100)

        # Выбор варианта расчета
        option = self.analysis_option.get()
        if option == 1:  # Сколько вернуть клиенту
            client_receives = amount
            client_gives = client_receives / (1 - commission)
            required_usdt_amount = client_gives
        else:  # Сколько клиент должен дать
            required_usdt_amount = amount

        # Расчет сумм
        usdt_to_give = required_usdt_amount / buy_rate
        usdt_to_client = required_usdt_amount / sell_rate
        our_profit_usdt = usdt_to_give - usdt_to_client
        our_profit_rub = our_profit_usdt * rapira_rate

        # Вывод результатов
        self.crypto_result_text.delete(1.0, tk.END)
        self.crypto_result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")

        if option == 1:
            self.crypto_result_text.insert(tk.END, f"Клиент хочет получить: {client_receives:.2f} RUB\n")
            self.crypto_result_text.insert(tk.END, f"Клиент должен отдать: {required_usdt_amount:.2f} RUB\n")
            self.crypto_result_text.insert(tk.END, f"Комиссия: {commission * 100:.2f}%\n\n")

        self.crypto_result_text.insert(tk.END, f"Наш доход RUB: {our_profit_rub:.2f}\n")
        self.crypto_result_text.insert(tk.END, f"Наш доход USDT/$: {our_profit_usdt:.6f}\n")
        self.crypto_result_text.insert(tk.END, f"Кол-во USDT/$ отданных клиенту: {usdt_to_client:.6f}\n")
        self.crypto_result_text.insert(tk.END, f"Кол-во RUB отданных клиенту: {usdt_to_client * rapira_rate:.2f}\n\n")

        self.crypto_result_text.insert(tk.END, "════════════════════════════════════\n")
        self.crypto_result_text.insert(tk.END, f"Курс покупки: {buy_rate:.4f}\n")
        self.crypto_result_text.insert(tk.END, f"Курс продажи: {sell_rate:.4f}\n")
        self.crypto_result_text.insert(tk.END, f"Курс Рапира: {rapira_rate:.2f}\n")

    def calculate_analysis_rub(self):
        # Получаем данные из полей
        try:
            amount = float(self.analysis_amount_entry.get().replace(',', '.'))
            commission = float(self.analysis_commission_entry.get().replace(',', '.')) / 100
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")
            return

        # Выбор варианта расчета
        option = self.analysis_option.get()
        self.rub_result_text.delete(1.0, tk.END)

        if option == 1:  # Сколько вернуть клиенту
            client_return = amount
            client_give = client_return / (1 - commission)

            self.rub_result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")
            self.rub_result_text.insert(tk.END, f"Клиент должен отдать: {client_give:.2f} RUB\n")
            self.rub_result_text.insert(tk.END,
                                        f"Комиссия ({commission * 100:.2f}%): {(client_give - client_return):.2f} RUB\n")

            if self.intermediaries_list_analysis:
                self.rub_result_text.insert(tk.END, "\n════════ КОМИССИИ ПОСРЕДНИКОВ ════════\n\n")

                commission_general = 0.0
                intermediate_values = {}
                current_base = client_give

                for i, (name, comm) in enumerate(self.intermediaries_list_analysis, 1):
                    comm_pct = comm / 100
                    commission_value = current_base * comm_pct
                    commission_general += commission_value
                    intermediate_values[i] = commission_value
                    current_base -= commission_value

                    self.rub_result_text.insert(tk.END, f"Комиссия {name}: {comm:.2f}% = {commission_value:.2f} RUB\n")

                self.rub_result_text.insert(tk.END, f"\nОбщая комиссия посредников: {commission_general:.2f} RUB\n")

                intermediate_value = client_give - commission_general
                my_profit = intermediate_value - client_return

                if my_profit < 0:
                    messagebox.showwarning("Внимание", "Отрицательный доход! Проверьте комиссии")
                    self.rub_result_text.insert(tk.END, "\n════════ ВНИМАНИЕ: ОТРИЦАТЕЛЬНЫЙ ДОХОД! ════════\n\n")

                self.rub_result_text.insert(tk.END, "\n════════ ИТОГИ ════════\n\n")
                self.rub_result_text.insert(tk.END, f"Наш доход: {my_profit:.2f} RUB\n")
                self.rub_result_text.insert(tk.END, f"Клиент получит: {client_return:.2f} RUB\n")
                self.rub_result_text.insert(tk.END, f"Клиент должен отдать: {client_give:.2f} RUB\n")

        else:  # Сколько клиент должен дать
            client_amount = amount
            client_receives = client_amount - client_amount * commission

            self.rub_result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")
            self.rub_result_text.insert(tk.END, f"Клиент получит: {client_receives:.2f} RUB\n")
            self.rub_result_text.insert(tk.END,
                                        f"Комиссия ({commission * 100:.2f}%): {(client_amount * commission):.2f} RUB\n")

            if self.intermediaries_list_analysis:
                self.rub_result_text.insert(tk.END, "\n════════ КОМИССИИ ПОСРЕДНИКОВ ════════\n\n")

                all_fees = 0.0
                agent_data = {}
                current_base = client_amount

                for i, (name, comm) in enumerate(self.intermediaries_list_analysis, 1):
                    comm_pct = comm / 100
                    fee = current_base * comm_pct
                    all_fees += fee
                    agent_data[i] = fee
                    current_base -= fee

                    self.rub_result_text.insert(tk.END, f"Комиссия {name}: {comm:.2f}% = {fee:.2f} RUB\n")

                self.rub_result_text.insert(tk.END, f"\nОбщая комиссия посредников: {all_fees:.2f} RUB\n")

                net_amount = client_amount - all_fees
                profit = net_amount - client_receives

                if profit < 0:
                    messagebox.showwarning("Внимание", "Отрицательный доход! Проверьте комиссии")
                    self.rub_result_text.insert(tk.END, "\n════════ ВНИМАНИЕ: ОТРИЦАТЕЛЬНЫЙ ДОХОД! ════════\n\n")

                self.rub_result_text.insert(tk.END, "\n════════ ИТОГИ ════════\n\n")
                self.rub_result_text.insert(tk.END, f"Наш доход: {profit:.2f} RUB\n")
                self.rub_result_text.insert(tk.END, f"Клиент получит: {client_receives:.2f} RUB\n")
                self.rub_result_text.insert(tk.END, f"Клиент должен отдать: {client_amount:.2f} RUB\n")

    def add_selected_intermediary_analysis(self):
        selected_name = self.intermediary_var_analysis.get()
        if not selected_name:
            return

        intermediaries = self.load_intermediaries()
        for name, commission in intermediaries:
            if name == selected_name:
                self.intermediaries_list_analysis.append((name, commission))
                self.update_intermediaries_display_analysis()
                break

    def add_intermediary_analysis(self):
        top = tk.Toplevel(self.root)
        top.title("Добавить посредника")
        top.geometry("400x400")
        top.resizable(False, False)

        content_frame = ttk.Frame(top)
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(content_frame, text="Имя посредника:").pack(pady=5)
        name_entry = ttk.Entry(content_frame, font=('Arial', 12))
        name_entry.pack(pady=5, fill=tk.X)

        ttk.Label(content_frame, text="Комиссия (%):").pack(pady=5)
        commission_entry = ttk.Entry(content_frame, font=('Arial', 12))
        commission_entry.pack(pady=5, fill=tk.X)

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=20)

        def save_intermediary():
            name = name_entry.get()
            commission = commission_entry.get()

            if not name or not commission:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            try:
                commission_val = float(commission.replace(',', '.'))
                self.save_intermediary_to_csv(name, commission_val)
                self.intermediaries_list_analysis.append((name, commission_val))
                self.update_intermediaries_display_analysis()
                intermediaries = self.load_intermediaries()
                intermediary_names = [n for n, _ in intermediaries]
                self.intermediary_combobox_analysis['values'] = intermediary_names
                top.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное значение комиссии")

        ttk.Button(btn_frame, text="Сохранить", command=save_intermediary, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=top.destroy, width=15).pack(side=tk.LEFT, padx=10)

    def update_intermediaries_display_analysis(self):
        for widget in self.current_intermediaries_frame_analysis.winfo_children():
            widget.destroy()

        if not self.intermediaries_list_analysis:
            ttk.Label(self.current_intermediaries_frame_analysis, text="Нет посредников",
                      font=('Arial', 10), foreground='gray').pack(pady=10)
            return

        for i, (name, commission) in enumerate(self.intermediaries_list_analysis):
            frame = ttk.Frame(self.current_intermediaries_frame_analysis)
            frame.pack(fill=tk.X, pady=5, padx=20)

            ttk.Label(frame, text=f"{name}: {commission}%", font=('Arial', 11)).pack(side=tk.LEFT, padx=10)
            ttk.Button(frame, text="Удалить", command=lambda idx=i: self.remove_intermediary_analysis(idx)).pack(
                side=tk.RIGHT)

    def remove_intermediary_analysis(self, index):
        self.intermediaries_list_analysis.pop(index)
        self.update_intermediaries_display_analysis()

    def show_cash_usdt_form(self, entry=None, read_only=False):
        self.clear_frame()
        is_edit_mode = entry is not None

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = main_frame

        # Создание скроллируемой области
        scrollable_frame, container = self.setup_scrollable_frame(main_frame)

        # Центральный контейнер
        center_container = ttk.Frame(scrollable_frame)
        center_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        header = ttk.Label(center_container, text="Б/нал руб - $$ - usdt - кэш руб", style='Header.TLabel')
        header.pack(pady=10)

        # Радиокнопки выбора
        option_frame = ttk.Frame(center_container)
        option_frame.pack(fill=tk.X, pady=5)

        self.cash_usdt_calc_option = tk.IntVar(value=2)
        rb_frame = ttk.Frame(option_frame)
        rb_frame.pack()

        rb1 = ttk.Radiobutton(rb_frame, text="Сколько вернуть клиенту",
                              variable=self.cash_usdt_calc_option, value=1,
                              state='normal' if not read_only else 'disabled')
        rb2 = ttk.Radiobutton(rb_frame, text="Сколько клиент должен дать",
                              variable=self.cash_usdt_calc_option, value=2,
                              state='normal' if not read_only else 'disabled')
        rb1.pack(side=tk.LEFT, padx=10)
        rb2.pack(side=tk.LEFT, padx=10)

        # Поле для комиссии
        self.commission_frame = ttk.Frame(center_container)
        self.commission_frame.pack(fill=tk.X, pady=5)

        self.commission_label = ttk.Label(self.commission_frame, text="Комиссия (%):")
        self.commission_label.pack(side=tk.LEFT, padx=5)
        self.commission_entry = ttk.Entry(self.commission_frame, font=('Arial', 12), width=15,
                                          state='normal' if not read_only else 'disabled')
        self.commission_entry.pack(side=tk.LEFT, padx=5)

        # Основные поля ввода
        input_frame = ttk.Frame(center_container)
        input_frame.pack(fill=tk.X, pady=5)

        form_grid = ttk.Frame(input_frame)
        form_grid.pack()

        labels = ["Сумма:", "Курс ЦБ:", "Проценты к покупке (1.5):", "Ваш процент (0.2):", "Курс Рапира:"]
        entries = []
        for i, text in enumerate(labels):
            row = ttk.Frame(form_grid)
            row.pack(fill=tk.X, pady=2)

            # Для первой метки сохраняем отдельную ссылку
            if i == 0:
                self.amount_label = ttk.Label(row, text=text, width=25, anchor='e')
                self.amount_label.pack(side=tk.LEFT, padx=5)
            else:
                ttk.Label(row, text=text, width=25, anchor='e').pack(side=tk.LEFT, padx=5)

            entry = ttk.Entry(row, font=('Arial', 12), width=15,
                              state='normal' if not read_only else 'disabled')
            entry.pack(side=tk.LEFT, padx=5)
            entries.append(entry)

        self.amount_entry, self.cb_rate_entry, self.buy_percent_entry, self.our_percent_entry, self.rapira_rate_entry = entries

        # Блок дополнительных комиссий
        comm_block = ttk.LabelFrame(center_container, text="Доп. комиссии")
        comm_block.pack(fill=tk.X, pady=10)

        # Радиокнопки Да/Нет
        comm_radio_frame = ttk.Frame(comm_block)
        comm_radio_frame.pack(pady=5)

        self.commission_var = tk.IntVar(value=2)
        rb_no = ttk.Radiobutton(comm_radio_frame, text="Нет", variable=self.commission_var, value=2,
                                command=self.toggle_commission, state='normal' if not read_only else 'disabled')
        rb_yes = ttk.Radiobutton(comm_radio_frame, text="Да", variable=self.commission_var, value=1,
                                 command=self.toggle_commission, state='normal' if not read_only else 'disabled')
        rb_no.pack(side=tk.LEFT, padx=20)
        rb_yes.pack(side=tk.LEFT, padx=20)

        # Тип комиссии
        comm_type_frame = ttk.Frame(comm_block)
        comm_type_frame.pack(pady=5)

        self.commission_type_var = tk.IntVar()
        self.commission_types = [
            "В рублях",
            "В USDT/$",
            "В процентах (от RUB)",
            "В процентах (от USDT/$)"
        ]

        for i, text in enumerate(self.commission_types):
            rb = ttk.Radiobutton(comm_type_frame, text=text, variable=self.commission_type_var,
                                 value=i + 1, state='disabled')
            rb.pack(anchor='w', padx=10, pady=2)

        # Поле ввода суммы комиссии
        comm_entry_frame = ttk.Frame(comm_block)
        comm_entry_frame.pack(pady=5)

        ttk.Label(comm_entry_frame, text="Сумма комиссии:", width=25, anchor='e').pack(side=tk.LEFT, padx=5)
        self.extra_commission_entry = ttk.Entry(comm_entry_frame, font=('Arial', 12), width=15, state='disabled')
        self.extra_commission_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка расчета
        btn_frame_calc = ttk.Frame(center_container)
        btn_frame_calc.pack(pady=10)
        self.calc_btn = ttk.Button(btn_frame_calc, text="Рассчитать", command=self.calculate_cash_usdt,
                                   state='normal' if not read_only else 'disabled')
        self.calc_btn.pack()

        # Результат
        result_frame = ttk.Frame(center_container)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.result_text = tk.Text(result_frame, height=12, font=('Arial', 11), wrap=tk.WORD, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Если редактируем существующую запись
        if is_edit_mode:
            self.cash_usdt_calc_option.set(entry.input_data.get('calc_option', 2))
            if 'commission_pct' in entry.input_data:
                self.commission_entry.insert(0, entry.input_data['commission_pct'])

            keys = ['amount', 'cb_rate', 'buy_percent', 'our_percent', 'rapira_rate']
            entries_list = [self.amount_entry, self.cb_rate_entry, self.buy_percent_entry,
                            self.our_percent_entry, self.rapira_rate_entry]

            for key, entry_widget in zip(keys, entries_list):
                if key in entry.input_data:
                    entry_widget.insert(0, entry.input_data[key])

            self.result_text.insert(tk.END, entry.result)

        # Управление видимостью полей комиссии
        self.toggle_cash_usdt_calc_option()

        # Кнопки управления внизу
        btn_footer_frame = ttk.Frame(main_frame)
        btn_footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        footer_inner = ttk.Frame(btn_footer_frame)
        footer_inner.pack()

        if is_edit_mode:
            if not read_only:
                ttk.Button(footer_inner, text="Сохранить изменения",
                           command=lambda: self.save_cash_usdt(entry)).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_inner, text="Назад в журнал", command=self.show_journal).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Button(footer_inner, text="Сохранить в журнал", command=self.save_cash_usdt).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_inner, text="Назад", command=self.show_action_buttons).pack(side=tk.LEFT, padx=10)
    def toggle_cash_usdt_calc_option(self):
        if not hasattr(self, 'amount_label'):  # Защита от отсутствия элемента
            return


        if self.cash_usdt_calc_option.get() == 1:  # "Сколько вернуть клиенту"
            # Показываем поле для комиссии
            self.commission_frame.pack(pady=5)
            self.commission_label.pack(side=tk.LEFT, padx=5)
            self.commission_entry.pack(side=tk.LEFT, padx=5)

            # Меняем текст метки суммы
            self.amount_label.config(text="Сумма, которую клиент хочет получить:")
        else:  # "Сколько клиент должен дать"
            # Скрываем поле для комиссии
            self.commission_frame.pack_forget()

            # Возвращаем исходный текст метки суммы
            self.amount_label.config(text="Сумма:")

    def save_cash_usdt(self, entry=None):
        input_data = {
            'calc_option': self.cash_usdt_calc_option.get(),
            'amount': self.amount_entry.get(),
            'cb_rate': self.cb_rate_entry.get(),
            'buy_percent': self.buy_percent_entry.get(),
            'our_percent': self.our_percent_entry.get(),
            'rapira_rate': self.rapira_rate_entry.get()
        }
        if self.cash_usdt_calc_option.get() == 1:
            input_data['commission_pct'] = self.commission_entry.get()
        result = self.result_text.get(1.0, tk.END)

        if entry is None:  # Новая запись
            if not hasattr(self, 'saved_client_data'):
                messagebox.showerror("Ошибка", "Сначала создайте клиента")
                return
            self.save_to_journal("Б/нал руб- $$-usdt-кэш руб", input_data, result)
            self.show_main_form()
        else:  # Редактирование существующей
            entry.input_data = input_data
            entry.result = result
            JournalManager.update_entry(entry)
            self.show_journal()

    def calculate_cash_usdt(self):
        try:
            # Получаем тип расчета
            calc_option = self.cash_usdt_calc_option.get()

            if calc_option == 1:  # "Сколько вернуть клиенту"
                # Получаем комиссию
                commission_pct = float(self.commission_entry.get().replace(',', '.')) / 100
                client_receives = float(self.amount_entry.get().replace(',', '.'))

                # Рассчитываем сумму, которую клиент должен дать
                client_gives = client_receives / (1 - commission_pct)

                # Используем эту сумму для дальнейших расчетов
                required_usdt_amount = client_gives
            else:  # "Сколько клиент должен дать"
                required_usdt_amount = float(self.amount_entry.get().replace(',', '.'))

            central_bank_rate = float(self.cb_rate_entry.get().replace(',', '.'))
            buy_percent = float(self.buy_percent_entry.get().replace(',', '.'))
            our_percent = float(self.our_percent_entry.get().replace(',', '.'))
            rapira_rate = float(self.rapira_rate_entry.get().replace(',', '.'))

            # Расчет курсов
            buy_rate = central_bank_rate + (central_bank_rate * buy_percent / 100)
            total_percent = our_percent + buy_percent
            sell_rate = central_bank_rate + (central_bank_rate * total_percent / 100)

            # Расчет сумм
            usdt_to_give = required_usdt_amount / buy_rate
            usdt_to_client = required_usdt_amount / sell_rate
            our_profit_usdt = usdt_to_give - usdt_to_client
            our_profit_rub = our_profit_usdt * rapira_rate

            # Инициализация переменных для доп. комиссий
            final_profit_rub = our_profit_rub
            final_profit_usdt = our_profit_usdt

            # Дополнительные комиссии
            if self.commission_var.get() == 1:
                extra_value = float(self.extra_commission_entry.get().replace(',', '.'))
                commission_type = self.commission_type_var.get()

                if commission_type == 1:  # В рублях
                    rub_fee = extra_value
                    final_profit_rub = our_profit_rub - rub_fee
                    usdt_equivalent = rub_fee / rapira_rate
                    final_profit_usdt = our_profit_usdt - usdt_equivalent
                elif commission_type == 2:  # В USDT
                    usdt_fee = extra_value
                    final_profit_usdt = our_profit_usdt - usdt_fee
                    rub_equivalent = usdt_fee * rapira_rate
                    final_profit_rub = our_profit_rub - rub_equivalent
                elif commission_type == 3:  # % от RUB
                    rub_percent = extra_value / 100
                    final_profit_rub = our_profit_rub * (1 - rub_percent)
                    final_profit_usdt = final_profit_rub / rapira_rate
                elif commission_type == 4:  # % от USDT
                    usdt_percent = extra_value / 100
                    final_profit_usdt = our_profit_usdt * (1 - usdt_percent)
                    final_profit_rub = final_profit_usdt * rapira_rate

            # Вывод результатов
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")

            if calc_option == 1:
                self.result_text.insert(tk.END, f"Клиент хочет получить: {client_receives:.2f} RUB\n")
                self.result_text.insert(tk.END, f"Клиент должен отдать: {required_usdt_amount:.2f} RUB\n")
                self.result_text.insert(tk.END, f"Комиссия: {commission_pct * 100:.2f}%\n\n")

            self.result_text.insert(tk.END, f"Наш доход RUB: {final_profit_rub:.2f}\n")
            self.result_text.insert(tk.END, f"Наш доход USDT/$: {final_profit_usdt:.6f}\n")
            self.result_text.insert(tk.END, f"Кол-во USDT/$ отданных клиенту: {usdt_to_client:.6f}\n")
            self.result_text.insert(tk.END, f"Кол-во RUB отданных клиенту: {usdt_to_client * rapira_rate:.2f}\n\n")

            self.result_text.insert(tk.END, "════════════════════════════════════\n")
            self.result_text.insert(tk.END, f"Курс покупки: {buy_rate:.4f}\n")
            self.result_text.insert(tk.END, f"Курс продажи: {sell_rate:.4f}\n")
            self.result_text.insert(tk.END, f"Курс Рапира: {rapira_rate:.2f}\n")

            if self.commission_var.get() == 1:
                self.result_text.insert(tk.END, "\nПосле доп. комиссии:\n")
                self.result_text.insert(tk.END, f"• RUB: {final_profit_rub:.2f}\n")
                self.result_text.insert(tk.END, f"• USDT: {final_profit_usdt:.6f}\n")

        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")

    def toggle_commission(self):
        state = 'normal' if self.commission_var.get() == 1 else 'disabled'

        # Enable/disable commission type radio buttons
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame):  # Find our form_frame
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Radiobutton) and child['text'] in self.commission_types:
                        child.config(state=state)

        self.extra_commission_entry.config(state=state)
        if state == 'disabled':
            self.commission_type_var.set(0)

    def show_mixed_currency_form(self, entry=None, read_only=False):
        self.clear_frame()
        is_edit_mode = entry is not None

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = main_frame

        # Создание скроллируемой области
        scrollable_frame, container = self.setup_scrollable_frame(main_frame)

        # Центральный контейнер
        center_container = ttk.Frame(scrollable_frame)
        center_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        header = ttk.Label(center_container, text="Смешанный RUB/Валюта", style='Header.TLabel')
        header.pack(pady=10)

        # Основные поля ввода
        input_frame = ttk.LabelFrame(center_container, text="Параметры расчета")
        input_frame.pack(fill=tk.X, pady=5, padx=10)

        # Список полей
        labels = [
            "Введите сумму вклада:",
            "Процент в рублях (50):",
            "Курс ЦБ (80.075):",
            "Наценка (1.5):",
            "Ваш процент (0.2):",
            "Курс рапиры:",
            "Банковская комиссия (%):"
        ]

        self.mixed_entries = []
        for i, label_text in enumerate(labels):
            row_frame = ttk.Frame(input_frame)
            row_frame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(row_frame, text=label_text, width=25, anchor='e').pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(row_frame, font=('Arial', 12), width=20,
                              state='normal' if not read_only else 'disabled')
            entry.pack(side=tk.LEFT, padx=5)
            self.mixed_entries.append(entry)

        # Блок дополнительных комиссий
        comm_frame = ttk.LabelFrame(center_container, text="Дополнительные комиссии")
        comm_frame.pack(fill=tk.X, pady=10, padx=10)

        # Радиокнопки Да/Нет
        comm_radio_frame = ttk.Frame(comm_frame)
        comm_radio_frame.pack(pady=5, padx=10)

        self.mixed_commission_var = tk.IntVar(value=2)
        rb_no = ttk.Radiobutton(comm_radio_frame, text="Нет", variable=self.mixed_commission_var, value=2,
                                command=self.toggle_mixed_commission, state='normal' if not read_only else 'disabled')
        rb_yes = ttk.Radiobutton(comm_radio_frame, text="Да", variable=self.mixed_commission_var, value=1,
                                 command=self.toggle_mixed_commission, state='normal' if not read_only else 'disabled')
        rb_no.pack(side=tk.LEFT, padx=20)
        rb_yes.pack(side=tk.LEFT, padx=20)

        # Типы комиссий
        type_frame = ttk.Frame(comm_frame)
        type_frame.pack(pady=5, padx=10)

        self.mixed_commission_type_var = tk.IntVar()
        self.mixed_commission_types = [
            "В рублях",
            "В USDT/$",
            "В процентах (от RUB)",
            "В процентах (от USDT/$)"
        ]

        # Центрирование типов комиссий
        type_center = ttk.Frame(type_frame)
        type_center.pack()

        for i, text in enumerate(self.mixed_commission_types):
            rb = ttk.Radiobutton(type_center, text=text, variable=self.mixed_commission_type_var,
                                 value=i + 1, state='disabled')
            rb.pack(anchor='w', pady=2)

        # Поле для суммы комиссии
        comm_entry_frame = ttk.Frame(comm_frame)
        comm_entry_frame.pack(pady=10, padx=10)

        ttk.Label(comm_entry_frame, text="Сумма комиссии:", width=25, anchor='e').pack(side=tk.LEFT, padx=5)
        self.mixed_extra_commission_entry = ttk.Entry(comm_entry_frame, font=('Arial', 12), width=20, state='disabled')
        self.mixed_extra_commission_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка расчета
        btn_frame_calc = ttk.Frame(center_container)
        btn_frame_calc.pack(pady=15)
        self.calc_btn = ttk.Button(btn_frame_calc, text="Рассчитать",
                                   command=self.calculate_mixed_currency,
                                   state='normal' if not read_only else 'disabled')
        self.calc_btn.pack()

        # Поле результатов
        result_frame = ttk.LabelFrame(center_container, text="Результаты расчета")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        self.result_text = tk.Text(result_frame, height=10, font=('Arial', 11),
                                   wrap=tk.WORD, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Заполнение данных из записи журнала
        if is_edit_mode:
            for i, key in enumerate(['start_capital', 'capital_percentages', 'cb_today',
                                     'extra_charg', 'my_percent', 'rapira', 'bank_commission']):
                if key in entry.input_data:
                    self.mixed_entries[i].insert(0, entry.input_data[key])
            self.result_text.insert(tk.END, entry.result)

        # Кнопки управления
        btn_footer_frame = ttk.Frame(main_frame)
        btn_footer_frame.pack(fill=tk.X, pady=10)

        footer_center = ttk.Frame(btn_footer_frame)
        footer_center.pack()

        if is_edit_mode:
            if not read_only:
                ttk.Button(footer_center, text="Сохранить изменения",
                           command=lambda: self.save_mixed_currency(entry),
                           width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_center, text="Назад в журнал",
                       command=self.show_journal,
                       width=20).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Button(footer_center, text="Сохранить в журнал",
                       command=self.save_mixed_currency,
                       width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_center, text="Назад",
                       command=self.show_action_buttons,
                       width=20).pack(side=tk.LEFT, padx=10)

    def save_mixed_currency(self, entry=None):
        input_data = {
            'start_capital': self.mixed_entries[0].get(),
            'capital_percentages': self.mixed_entries[1].get(),
            'cb_today': self.mixed_entries[2].get(),
            'extra_charg': self.mixed_entries[3].get(),
            'my_percent': self.mixed_entries[4].get(),
            'rapira': self.mixed_entries[5].get(),
            'bank_commission': self.mixed_entries[6].get()
        }
        result = self.result_text.get(1.0, tk.END)

        if entry is None:  # Новая запись
            if not hasattr(self, 'saved_client_data'):
                messagebox.showerror("Ошибка", "Сначала создайте клиента")
                return
            self.save_to_journal("Смешанный RUB/Валюта", input_data, result)
            self.show_main_form()
        else:  # Редактирование существующей
            entry.input_data = input_data
            entry.result = result
            JournalManager.update_entry(entry)
            self.show_journal()

    def toggle_mixed_commission(self):
        state = 'normal' if self.mixed_commission_var.get() == 1 else 'disabled'

        # Изменяем состояние radiobuttons для типов комиссий
        for i, text in enumerate(self.mixed_commission_types):
            for child in self.main_frame.winfo_children():
                if isinstance(child, ttk.Frame):  # Ищем наш form_frame
                    for widget in child.winfo_children():
                        if isinstance(widget, ttk.Radiobutton) and widget['text'] == text:
                            widget.config(state=state)

        self.mixed_extra_commission_entry.config(state=state)
        if state == 'disabled':
            self.mixed_commission_type_var.set(0)

    def calculate_mixed_currency(self):
        try:
            # Получаем значения из полей
            start_capital = float(self.mixed_entries[0].get().replace(',', '.'))
            capital_percentages = int(self.mixed_entries[1].get())
            cb_today = float(self.mixed_entries[2].get().replace(',', '.'))
            extra_charg = float(self.mixed_entries[3].get().replace(',', '.'))
            my_percent = float(self.mixed_entries[4].get().replace(',', '.'))
            rapira = float(self.mixed_entries[5].get().replace(',', '.'))
            bank_commission = float(self.mixed_entries[6].get().replace(',', '.'))

            # Вычисляем суммы в RUB
            capital_ru = start_capital * capital_percentages / 100
            capital_ru_two = start_capital - capital_ru

            # Расчет комиссий
            extra_charge = extra_charg / 100
            my_percentages = (my_percent + extra_charge) / 100
            bank_commission_pct = bank_commission / 100

            # Расчет USDT для клиента
            total_usdt_klient = capital_ru_two / (cb_today * (1 + my_percentages))

            # Расчет RUB для клиента
            capital_client_ru = capital_ru * (1 - bank_commission_pct)

            # Расчет курсов
            markup_rate = cb_today * (1 + extra_charge)
            total_rate = cb_today * (1 + (extra_charg + my_percent) / 100)

            # Расчет доходов
            total_usdt = capital_ru_two / markup_rate
            our_usdt = total_usdt - total_usdt_klient
            our_rub = our_usdt * rapira

            # Инициализация переменных для доп. комиссий
            final_our_rub = our_rub
            final_our_usdt = our_usdt

            # Дополнительные комиссии
            if self.mixed_commission_var.get() == 1:
                extra_value = float(self.mixed_extra_commission_entry.get().replace(',', '.'))
                commission_type = self.mixed_commission_type_var.get()

                if commission_type == 1:  # В рублях
                    final_our_rub = our_rub - extra_value
                    final_our_usdt = final_our_rub / rapira
                elif commission_type == 2:  # В USDT
                    final_our_usdt = our_usdt - extra_value
                    final_our_rub = final_our_usdt * rapira
                elif commission_type == 3:  # % от RUB
                    final_our_rub = our_rub * (1 - extra_value / 100)
                    final_our_usdt = final_our_rub / rapira
                elif commission_type == 4:  # % от USDT
                    final_our_usdt = our_usdt * (1 - extra_value / 100)
                    final_our_rub = final_our_usdt * rapira

            # Вывод результатов
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")
            self.result_text.insert(tk.END, f"Клиент получит:\n")
            self.result_text.insert(tk.END, f"• RUB: {capital_client_ru:.2f}\n")
            self.result_text.insert(tk.END, f"• USDT: {total_usdt_klient:.6f}\n\n")

            self.result_text.insert(tk.END, "Ваш доход:\n")
            self.result_text.insert(tk.END, f"• RUB: {final_our_rub:.2f}\n")
            self.result_text.insert(tk.END, f"• USDT: {final_our_usdt:.6f}\n\n")

            self.result_text.insert(tk.END, "════════════════════════════════════\n")
            self.result_text.insert(tk.END, f"Исходная сумма: {start_capital:.2f} RUB\n")
            self.result_text.insert(tk.END,
                                    f"Распределение: {capital_percentages}% RUB, {100 - capital_percentages}% USDT\n")
            self.result_text.insert(tk.END, f"Курс ЦБ: {cb_today:.4f}\n")
            self.result_text.insert(tk.END, f"Курс с наценкой: {markup_rate:.4f}\n")
            self.result_text.insert(tk.END, f"Курс с вашим процентом: {total_rate:.4f}\n")
            self.result_text.insert(tk.END, f"Курс Рапира: {rapira:.2f}\n")

            if self.mixed_commission_var.get() == 1:
                self.result_text.insert(tk.END, "\nПосле доп. комиссии:\n")
                self.result_text.insert(tk.END, f"• RUB: {final_our_rub:.2f}\n")
                self.result_text.insert(tk.END, f"• USDT: {final_our_usdt:.6f}\n")

        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")

    def save_intermediary_to_csv(self, name, commission):
        file_exists = os.path.isfile('intermediaries.csv')
        with open('intermediaries.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Имя", "Комиссия"])
            writer.writerow([name, commission])

    def load_intermediaries(self):
        intermediaries = []
        try:
            with open('intermediaries.csv', 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        intermediaries.append((row[0], float(row[1])))
        except FileNotFoundError:
            pass
        return intermediaries

    def show_cash_rub_form(self, entry=None, read_only=False):
        self.clear_frame()
        is_edit_mode = entry is not None

        # Создание основного фрейма
        main_frame = ttk.Frame(self.content_container)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = main_frame

        # Создание скроллируемой области
        scrollable_frame, container = self.setup_scrollable_frame(main_frame)

        # Центральный контейнер
        center_container = ttk.Frame(scrollable_frame)
        center_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        header = ttk.Label(center_container, text="Б/нал руб-кэш руб", style='Header.TLabel')
        header.pack(pady=10)

        # Выбор варианта расчета
        option_frame = ttk.LabelFrame(center_container, text="Вариант расчета")
        option_frame.pack(fill=tk.X, pady=5, padx=10)

        self.calc_option = tk.IntVar(value=1)
        rb_frame = ttk.Frame(option_frame)
        rb_frame.pack(padx=10, pady=5)

        rb1 = ttk.Radiobutton(rb_frame, text="Сколько вернуть клиенту",
                              variable=self.calc_option, value=1,
                              state='normal' if not read_only else 'disabled')
        rb2 = ttk.Radiobutton(rb_frame, text="Сколько клиент должен дать",
                              variable=self.calc_option, value=2,
                              state='normal' if not read_only else 'disabled')
        rb1.pack(side=tk.LEFT, padx=10)
        rb2.pack(side=tk.LEFT, padx=10)

        # Основные поля ввода
        input_frame = ttk.LabelFrame(center_container, text="Основные параметры")
        input_frame.pack(fill=tk.X, pady=5, padx=10)

        grid_frame = ttk.Frame(input_frame)
        grid_frame.pack(padx=10, pady=5)

        # Сумма
        ttk.Label(grid_frame, text="Сумма:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.amount_entry = ttk.Entry(grid_frame, font=('Arial', 12), width=20,
                                      state='normal' if not read_only else 'disabled')
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Комиссия
        ttk.Label(grid_frame, text="Комиссия (%):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.commission_entry = ttk.Entry(grid_frame, font=('Arial', 12), width=20,
                                          state='normal' if not read_only else 'disabled')
        self.commission_entry.grid(row=1, column=1, padx=5, pady=5)

        # Поля для посредников
        intermediaries_frame = ttk.LabelFrame(center_container, text="Посредники")
        intermediaries_frame.pack(fill=tk.X, pady=10, padx=10)

        # Выбор посредника
        select_frame = ttk.Frame(intermediaries_frame)
        select_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(select_frame, text="Выберите посредника:").pack(side=tk.LEFT, padx=5)
        self.intermediary_var = tk.StringVar()

        intermediaries = self.load_intermediaries()
        intermediary_names = [name for name, _ in intermediaries]
        self.intermediary_combobox = ttk.Combobox(select_frame, textvariable=self.intermediary_var,
                                                  values=intermediary_names, state="readonly", width=25)
        self.intermediary_combobox.pack(side=tk.LEFT, padx=5)

        ttk.Button(select_frame, text="Добавить", command=self.add_selected_intermediary,
                   state='normal' if not read_only else 'disabled').pack(side=tk.LEFT, padx=5)

        # Кнопка создания нового посредника
        ttk.Button(intermediaries_frame, text="Создать нового посредника",
                   command=self.add_intermediary,
                   state='normal' if not read_only else 'disabled').pack(pady=5)

        # Текущие посредники
        current_frame = ttk.LabelFrame(intermediaries_frame, text="Текущие посредники")
        current_frame.pack(fill=tk.X, padx=10, pady=5)

        self.current_intermediaries_frame = ttk.Frame(current_frame)
        self.current_intermediaries_frame.pack(padx=10, pady=5)

        self.intermediaries_list = []
        self.update_intermediaries_display()

        # Кнопка расчета
        btn_frame_calc = ttk.Frame(center_container)
        btn_frame_calc.pack(pady=15)
        self.calc_btn = ttk.Button(btn_frame_calc, text="Рассчитать",
                                   command=self.calculate_cash_rub,
                                   style='TButton',
                                   state='normal' if not read_only else 'disabled')
        self.calc_btn.pack()

        # Поле результатов
        result_frame = ttk.LabelFrame(center_container, text="Результаты расчета")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        self.result_text = tk.Text(result_frame, height=10, font=('Arial', 11),
                                   wrap=tk.WORD, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Заполнение данных из записи журнала
        if is_edit_mode:
            self.calc_option.set(entry.input_data.get('option', 1))
            self.amount_entry.insert(0, entry.input_data.get('amount', ''))
            self.commission_entry.insert(0, entry.input_data.get('commission', ''))
            if hasattr(entry, 'intermediaries') and entry.intermediaries:
                self.intermediaries_list = entry.intermediaries
            else:
                self.intermediaries_list = entry.input_data.get('intermediaries', [])
            self.update_intermediaries_display()
            self.result_text.insert(tk.END, entry.result)

        # Кнопки управления
        btn_footer_frame = ttk.Frame(main_frame)
        btn_footer_frame.pack(fill=tk.X, pady=10)

        footer_center = ttk.Frame(btn_footer_frame)
        footer_center.pack()

        if is_edit_mode:
            if not read_only:
                ttk.Button(footer_center, text="Сохранить изменения",
                           command=lambda: self.save_cash_rub(entry),
                           width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_center, text="Назад в журнал",
                       command=self.show_journal,
                       width=20).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Button(footer_center, text="Сохранить в журнал",
                       command=self.save_cash_rub,
                       width=20).pack(side=tk.LEFT, padx=10)
            ttk.Button(footer_center, text="Назад",
                       command=self.show_action_buttons,
                       width=20).pack(side=tk.LEFT, padx=10)

    def save_cash_rub(self, entry=None):
        input_data = {
            'option': self.calc_option.get(),
            'amount': self.amount_entry.get(),
            'commission': self.commission_entry.get(),
            'intermediaries': self.intermediaries_list
        }
        result = self.result_text.get(1.0, tk.END)

        if entry is None:  # Новая запись
            if not hasattr(self, 'saved_client_data'):
                messagebox.showerror("Ошибка", "Сначала создайте клиента")
                return
            self.save_to_journal("Б/нал руб-кэш руб", input_data, result)
            self.show_main_form()
        else:  # Редактирование существующей
            entry.input_data = input_data
            entry.result = result
            entry.intermediaries = self.intermediaries_list  # Сохраняем посредников
            JournalManager.update_entry(entry)
            self.show_journal()

    def add_selected_intermediary(self):
        selected_name = self.intermediary_var.get()
        if not selected_name:
            return

        intermediaries = self.load_intermediaries()
        for name, commission in intermediaries:
            if name == selected_name:
                self.intermediaries_list.append((name, commission))
                self.update_intermediaries_display()
                break

    def add_intermediary(self):
        # Создаем окно для добавления посредника
        top = tk.Toplevel(self.root)
        top.title("Добавить посредника")
        top.geometry("400x400")
        top.resizable(False, False)

        content_frame = ttk.Frame(top)
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(content_frame, text="Имя посредника:").pack(pady=5)
        name_entry = ttk.Entry(content_frame, font=('Arial', 12))
        name_entry.pack(pady=5, fill=tk.X)

        ttk.Label(content_frame, text="Комиссия (%):").pack(pady=5)
        commission_entry = ttk.Entry(content_frame, font=('Arial', 12))
        commission_entry.pack(pady=5, fill=tk.X)

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=20)

        def save_intermediary():
            name = name_entry.get()
            commission = commission_entry.get()

            if not name or not commission:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            try:
                commission_val = float(commission.replace(',', '.'))
                # Save to CSV
                self.save_intermediary_to_csv(name, commission_val)
                # Add to current list
                self.intermediaries_list.append((name, commission_val))
                self.update_intermediaries_display()
                # Update combobox
                intermediaries = self.load_intermediaries()
                intermediary_names = [n for n, _ in intermediaries]
                self.intermediary_combobox['values'] = intermediary_names
                top.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное значение комиссии")

        ttk.Button(btn_frame, text="Сохранить", command=save_intermediary, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=top.destroy, width=15).pack(side=tk.LEFT, padx=10)

    def update_intermediaries_display(self):
        # Clear current display
        for widget in self.current_intermediaries_frame.winfo_children():
            widget.destroy()

        if not self.intermediaries_list:
            ttk.Label(self.current_intermediaries_frame, text="Нет посредников",
                      font=('Arial', 10), foreground='gray').pack(pady=10)
            return

        # Display current intermediaries in the center
        for i, (name, commission) in enumerate(self.intermediaries_list):
            frame = ttk.Frame(self.current_intermediaries_frame)
            frame.pack(fill=tk.X, pady=5, padx=20)

            ttk.Label(frame, text=f"{name}: {commission}%",
                      font=('Arial', 11)).pack(side=tk.LEFT, padx=10)

            ttk.Button(frame, text="Удалить",
                       command=lambda idx=i: self.remove_intermediary(idx)).pack(side=tk.RIGHT)

    def remove_intermediary(self, index):
        self.intermediaries_list.pop(index)
        self.update_intermediaries_display()

    def calculate_cash_rub(self):
        try:
            self.result_text.delete(1.0, tk.END)

            option = self.calc_option.get()
            amount = float(self.amount_entry.get().replace(',', '.'))
            commission = float(self.commission_entry.get().replace(',', '.')) / 100

            if option == 1:
                # Расчет сколько клиент должен дать
                client_return = amount
                client_give = client_return / (1 - commission)

                self.result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")
                self.result_text.insert(tk.END, f"Клиент должен отдать: {client_give:.2f} RUB\n")
                self.result_text.insert(tk.END,
                                        f"Комиссия ({commission * 100:.2f}%): {(client_give - client_return):.2f} RUB\n")

                if self.intermediaries_list:
                    self.result_text.insert(tk.END, "\n════════ КОМИССИИ ПОСРЕДНИКОВ ════════\n\n")

                    commission_general = 0.0
                    intermediate_values = {}
                    current_base = client_give  # База для расчета первой комиссии

                    # Последовательный расчет комиссий
                    for i, (name, comm) in enumerate(self.intermediaries_list, 1):
                        comm_pct = comm / 100
                        commission_value = current_base * comm_pct
                        commission_general += commission_value
                        intermediate_values[i] = commission_value
                        current_base -= commission_value  # Уменьшаем базу для следующего посредника

                        self.result_text.insert(tk.END, f"Комиссия {name}: {comm:.2f}% = {commission_value:.2f} RUB\n")

                    self.result_text.insert(tk.END, f"\nОбщая комиссия посредников: {commission_general:.2f} RUB\n")

                    intermediate_value = client_give - commission_general
                    my_profit = intermediate_value - client_return

                    if my_profit < 0:
                        messagebox.showwarning("Внимание", "Отрицательный доход! Проверьте комиссии")
                        self.result_text.insert(tk.END, "\n════════ ВНИМАНИЕ: ОТРИЦАТЕЛЬНЫЙ ДОХОД! ════════\n\n")

                    self.result_text.insert(tk.END, "\n════════ ИТОГИ ════════\n\n")
                    self.result_text.insert(tk.END, f"Наш доход: {my_profit:.2f} RUB\n")
                    self.result_text.insert(tk.END, f"Клиент получит: {client_return:.2f} RUB\n")
                    self.result_text.insert(tk.END, f"Клиент должен отдать: {client_give:.2f} RUB\n")

            else:
                # Расчет сколько вернуть клиенту
                client_amount = amount
                client_receives = client_amount - client_amount * commission

                self.result_text.insert(tk.END, "════════ РЕЗУЛЬТАТЫ РАСЧЕТА ════════\n\n")
                self.result_text.insert(tk.END, f"Клиент получит: {client_receives:.2f} RUB\n")
                self.result_text.insert(tk.END,
                                        f"Комиссия ({commission * 100:.2f}%): {(client_amount * commission):.2f} RUB\n")

                if self.intermediaries_list:
                    self.result_text.insert(tk.END, "\n════════ КОМИССИИ ПОСРЕДНИКОВ ════════\n\n")

                    all_fees = 0.0
                    agent_data = {}
                    current_base = client_amount  # База для расчета первой комиссии

                    # Последовательный расчет комиссий
                    for i, (name, comm) in enumerate(self.intermediaries_list, 1):
                        comm_pct = comm / 100
                        fee = current_base * comm_pct
                        all_fees += fee
                        agent_data[i] = fee
                        current_base -= fee  # Уменьшаем базу для следующего посредника

                        self.result_text.insert(tk.END, f"Комиссия {name}: {comm:.2f}% = {fee:.2f} RUB\n")

                    self.result_text.insert(tk.END, f"\nОбщая комиссия посредников: {all_fees:.2f} RUB\n")

                    net_amount = client_amount - all_fees
                    profit = net_amount - client_receives

                    if profit < 0:
                        messagebox.showwarning("Внимание", "Отрицательный доход! Проверьте комиссии")
                        self.result_text.insert(tk.END, "\n════════ ВНИМАНИЕ: ОТРИЦАТЕЛЬНЫЙ ДОХОД! ════════\n\n")

                    self.result_text.insert(tk.END, "\n════════ ИТОГИ ════════\n\n")
                    self.result_text.insert(tk.END, f"Наш доход: {profit:.2f} RUB\n")
                    self.result_text.insert(tk.END, f"Клиент получит: {client_receives:.2f} RUB\n")
                    self.result_text.insert(tk.END, f"Клиент должен отдать: {client_amount:.2f} RUB\n")

        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")

    def save_client(self):
        if not all([self.status_var.get(), self.name_entry.get(), self.contact_entry.get()]):
            self.status_label.config(text="Заполните все поля!", foreground='red')
            return

        try:
            # Сохраняем данные клиента для использования в журнале
            self.saved_client_data = {
                'status': self.status_var.get(),
                'name': self.name_entry.get(),
                'contact': self.contact_entry.get()
            }

            with open('clients.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(["Дата", "Статус", "Имя", "Контакты"])
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    self.saved_client_data['status'],
                    self.saved_client_data['name'],
                    self.saved_client_data['contact']
                ])

            self.name_entry.delete(0, tk.END)
            self.contact_entry.delete(0, tk.END)
            self.status_label.config(text="Клиент успешно сохранен!", foreground='green')
            self.show_action_buttons()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить клиента: {str(e)}")

    def clear_frame(self):
        """Безопасная очистка контента"""
        try:
            for widget in self.content_container.winfo_children():
                widget.destroy()
        except tk.TclError:
            # Игнорируем ошибки, связанные с уничтоженными виджетами
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()