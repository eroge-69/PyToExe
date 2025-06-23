import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.ttk as ttk
import getpass
from datetime import datetime, timedelta

def get_days_of_month_for(year, month):
    """Возвращает список всех дат за указанный месяц"""
    first_day = datetime(year, month, 1).date()
    next_month = datetime(year + 1, 1, 1) if month == 12 \
        else datetime(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).date()

    delta = timedelta(days=1)
    current = first_day
    days = []

    while current <= last_day:
        days.append(current.strftime('%Y-%m-%d'))
        current += delta

    return days
PLANNED_STOPS_PERCENT = 15  # %

# === Подключение к БД и создание таблицы ===
def connect_db():
    conn = sqlite3.connect('daily_entries.db')
    cursor = conn.cursor()

    # Таблица данных за день
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            machine_name TEXT,
            shift1_time INTEGER DEFAULT 0,
            shift1_prod REAL DEFAULT 0,
            shift2_time INTEGER DEFAULT 0,
            shift2_prod REAL DEFAULT 0,
            stops INTEGER DEFAULT 0,
            UNIQUE(date, machine_name)
        )
    ''')

    try:
        cursor.execute('SELECT stops FROM daily_work LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE daily_work ADD COLUMN stops INTEGER DEFAULT 0')

    # Целевые значения по месяцам и машинам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_targets (
            month TEXT,
            machine_name TEXT,
            target_oee REAL,
            target_mtbf REAL,
            target_stops REAL,
            machine_speed REAL,
            PRIMARY KEY (month, machine_name)
        )
    ''')

    #current_month = datetime.now().strftime("%Y-%m")
    #cursor.execute('SELECT machine_name FROM monthly_targets WHERE month=?', (current_month,))
    #if cursor.fetchone() is None:
    #    cursor.execute('''
    #        INSERT INTO monthly_targets (
    #            month, machine_name, target_oee, target_mtbf, target_stops, machine_speed
    #        ) VALUES (?, ?, ?, ?, ?, ?)
    #    ''', (current_month, "Линия 1", 90.0, 150.0, 3.0, 2.0))
    #    conn.commit()

    return conn, cursor


# === Получить список дней текущего месяца ===
def get_days_of_month():
    today = datetime.now().date()
    year, month = today.year, today.month

    first_day = datetime(year, month, 1).date()
    next_month = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).date()

    delta = timedelta(days=1)
    current = first_day
    days = []

    while current <= last_day:
        days.append(current.strftime('%Y-%m-%d'))
        current += delta

    return days


# === Проверить, есть ли запись на дату и машину ===
def is_date_saved(cursor, date_str, machine_name):
    cursor.execute('''
        SELECT 1 FROM daily_work WHERE date=? AND machine_name=?
    ''', (date_str, machine_name))
    return cursor.fetchone() is not None


# === Сохранить данные за день ===
def save_day_data(cursor, conn, date_str, machine_name, shift1_time, shift1_prod, shift2_time, shift2_prod, stops):
    cursor.execute('''
        INSERT OR IGNORE INTO daily_work (
            date, machine_name, shift1_time, shift1_prod, shift2_time, shift2_prod, stops
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date_str, machine_name, shift1_time, shift1_prod, shift2_time, shift2_prod, stops))

    cursor.execute('''
        UPDATE daily_work SET
            shift1_time = ?,
            shift1_prod = ?,
            shift2_time = ?,
            shift2_prod = ?,
            stops = ?
        WHERE date = ? AND machine_name = ?
    ''', (shift1_time, shift1_prod, shift2_time, shift2_prod, stops, date_str, machine_name))
    conn.commit()


# === Сохранить цели по месяцу и машине ===
def save_target_values(cursor, conn, month_str, machine_name, oee, mtbf, stops, speed):
    cursor.execute('''
        INSERT OR REPLACE INTO monthly_targets (
            month, machine_name, target_oee, target_mtbf, target_stops, machine_speed
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (month_str, machine_name, oee, mtbf, stops, speed))
    conn.commit()


# === Загрузить цели по месяцу и машине ===
def load_target_values(cursor, month_str, machine_name):
    cursor.execute('''
        SELECT target_oee, target_mtbf, target_stops, machine_speed
        FROM monthly_targets WHERE month=? AND machine_name=?
    ''', (month_str, machine_name))
    row = cursor.fetchone()
    if not row:
        return 70.0, 7.0, 150.0, 2.0
    return round(row[0], 1), round(row[1], 1), round(row[2], 1), round(row[3], 2)


# === Список машин из БД (по текущему месяцу) ===
def load_machine_names(cursor, current_month):
    cursor.execute('''
        SELECT DISTINCT machine_name FROM monthly_targets WHERE month=?
        ORDER BY machine_name
    ''', (current_month,))
    rows = cursor.fetchall()
    return [row[0] for row in rows if row[0]]


# === Расчёт среднего OEE по месяцу и машине ===
def calculate_global_average_for_month(cursor, month_str, machine_name):
    cursor.execute('''
        SELECT shift1_time, shift1_prod, shift2_time, shift2_prod
        FROM daily_work WHERE date LIKE ? AND machine_name=?
    ''', (f"{month_str}%", machine_name))
    rows = cursor.fetchall()

    total_time = 0
    total_prod = 0
    machine_speed = load_machine_speed(cursor, month_str, machine_name)

    for row in rows:
        s1t, s1p, s2t, s2p = row
        total_time += s1t + s2t
        total_prod += s1p + s2p

    max_possible = total_time * machine_speed
    return round((total_prod / max_possible) * 100, 1) if max_possible > 0 else 0.0


# === Среднее число остановок по месяцу и машине ===
def calculate_avg_stops(cursor, month_str, machine_name):
    cursor.execute('''
        SELECT stops FROM daily_work
        WHERE date LIKE ? AND machine_name=? AND shift1_time + shift2_time > 0
    ''', (f"{month_str}%", machine_name))
    rows = cursor.fetchall()
    if not rows:
        return "--"
    total = sum(row[0] for row in rows)
    avg = round(total / len(rows), 1)
    return avg


# === Средний MTBF по месяцу и машине ===
def calculate_avg_mtbf(cursor, month_str, machine_name):
    cursor.execute('SELECT date FROM daily_work WHERE date LIKE ? AND machine_name=?',
                   (f"{month_str}%", machine_name))
    dates = [row[0] for row in cursor.fetchall()]

    total_effective_time = 0
    total_stops = 0
    machine_speed = load_machine_speed(cursor, month_str, machine_name)

    for date_str in dates:
        cursor.execute('''
            SELECT shift1_time, shift1_prod, shift2_time, shift2_prod, stops
            FROM daily_work WHERE date=? AND machine_name=?
        ''', (date_str, machine_name))
        row = cursor.fetchone()
        if not row:
            continue
        s1t, s1p, s2t, s2p, stops = row
        total_time = s1t + s2t
        total_prod = s1p + s2p

        if total_time == 0 or stops == 0:
            continue

        oee = round((total_prod / (total_time * machine_speed)) * 100, 1)
        effective_time = total_time * (oee / 100 + PLANNED_STOPS_PERCENT / 100)
        total_effective_time += effective_time
        total_stops += stops

    if total_stops == 0:
        return "--"
    avg_mtbf = round(total_effective_time / total_stops, 1)
    return avg_mtbf


# === Необходимая выработка для достижения цели ===
def calculate_daily_required(cursor, days, machine_name):
    """
    Рассчитывает необходимую суточную выработку для достижения цели
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    current_month = today_str[:7]

    # Цель OEE и скорость машины
    cursor.execute('''
        SELECT target_oee, machine_speed FROM monthly_targets
        WHERE month=? AND machine_name=?
    ''', (current_month, machine_name))
    row = cursor.fetchone()
    if not row:
        return "--"
    target_oee, machine_speed = round(row[0], 1), round(row[1], 2)

    # Данные за уже заполненные дни
    cursor.execute('''
        SELECT shift1_time, shift2_time, shift1_prod, shift2_prod 
        FROM daily_work WHERE date BETWEEN ? AND ? AND machine_name=?
    ''', (f"{current_month}-01", f"{current_month}-31", machine_name))

    rows = cursor.fetchall()

    total_time_filled = 0
    total_prod_filled = 0

    for row in rows:
        s1t, s2t, s1p, s2p = row
        total_time_filled += s1t + s2t
        total_prod_filled += s1p + s2p

    filled_days = len(rows)
    if filled_days == 0:
        return "--"

    # Общее время месяца — с учётом оставшихся дней × 1440
    year = int(current_month.split("-")[0])
    month = int(current_month.split("-")[1])

    all_days = get_days_of_month_for(year, month)
    remaining_days = max(0, len(all_days) - filled_days)

    planned_time_left = remaining_days * 1440
    full_month_time = total_time_filled + planned_time_left

    # Плановая выработка
    target_total_prod = full_month_time * machine_speed * target_oee / 100
    prod_needed = target_total_prod - total_prod_filled

    if prod_needed <= 0:
        return 0.0  # Уже перевыполняем план

    try:
        daily_required = round((prod_needed / remaining_days)/2, 1)
        return daily_required
    except ZeroDivisionError:
        return "--"


# === Скорость машины из БД ===
def load_machine_speed(cursor, month_str, machine_name):
    cursor.execute('SELECT machine_speed FROM monthly_targets WHERE month=? AND machine_name=?',
                   (month_str, machine_name))
    row = cursor.fetchone()
    return round(row[0], 2) if row and row[0] else 2.0


# === Окно графиков ===
class GraphWindow:
    def __init__(self, root, cursor, machine_name):
        self.root = root
        self.cursor = cursor
        self.machine_name = machine_name

        self.graph_window = tk.Toplevel(root)
        self.graph_window.title("Графики: OEE, MTBF, Остановки")
        self.graph_window.geometry("1050x650")

        # --- Выбор месяца ---
        self.month_selector_label = tk.Label(self.graph_window, text="Выберите месяц:", font=("Segoe UI", 10))
        self.month_selector_label.pack(pady=5)

        self.available_months = self.get_available_months()
        self.selected_month = tk.StringVar()
        self.selected_month.set(datetime.now().strftime("%Y-%m"))

        self.month_combo = ttk.Combobox(
            self.graph_window,
            textvariable=self.selected_month,
            values=self.available_months,
            state="readonly",
            width=15
        )
        self.month_combo.pack(pady=5)
        self.month_combo.bind("<<ComboboxSelected>>", lambda e: self.update_graph())

        if not self.available_months:
            self.month_combo.set(datetime.now().strftime("%Y-%m"))
        elif self.selected_month.get() not in self.available_months:
            self.month_combo.set(self.available_months[0])

        # --- График ---
        self.canvas_area = tk.Frame(self.graph_window)
        self.canvas_area.pack(fill=tk.BOTH, expand=1)

        self.target_oee, self.target_mtbf, self.target_stops, _ = load_target_values(cursor, self.month_combo.get(), machine_name)
        self.load_and_draw(month_str=self.month_combo.get())

    def get_available_months(self):
        self.cursor.execute('SELECT DISTINCT SUBSTR(date, 1, 7) FROM daily_work ORDER BY date')
        rows = self.cursor.fetchall()
        months = [row[0] for row in rows if row[0]]
        return months or [datetime.now().strftime("%Y-%m")]

    def update_graph(self):
        selected_month = self.month_combo.get()
        self.clear_canvas()
        self.target_oee, self.target_mtbf, self.target_stops, _ = load_target_values(self.cursor, selected_month, self.machine_name)
        self.load_and_draw(month_str=selected_month)

    def clear_canvas(self):
        for widget in self.canvas_area.winfo_children():
            widget.destroy()

    def load_and_draw(self, month_str=None):
        if not month_str:
            month_str = datetime.now().strftime("%Y-%m")

        year, month = map(int, month_str.split("-"))
        first_day = datetime(year, month, 1).date()
        next_month = datetime(year + 1, 1, 1) if month == 12 \
            else datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).date()

        self.cursor.execute('''
            SELECT date, shift1_time, shift1_prod, shift2_time, shift2_prod, stops
            FROM daily_work WHERE date BETWEEN ? AND ? AND machine_name=?
        ''', (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d'), self.machine_name))
        rows = self.cursor.fetchall()

        dates = []
        oee_values = []
        mtbf_values = []
        stops_values = []

        machine_speed = load_machine_speed(self.cursor, month_str, self.machine_name)

        for row in rows:
            date_str, s1t, s1p, s2t, s2p, stops = row
            total_time = s1t + s2t
            total_prod = s1p + s2p

            if total_time == 0 and total_prod == 0:
                continue

            max_possible = total_time * machine_speed
            if max_possible > 0:
                oee = round((total_prod / max_possible) * 100, 1)
            else:
                oee = "--"

            if total_time > 0 and stops > 0:
                effective_time = total_time * (oee / 100 + 0.15)
                mtbf = round(effective_time / stops, 1)
            else:
                mtbf = "--"

            short_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m')
            dates.append(short_date)
            oee_values.append(oee if isinstance(oee, float) else None)
            mtbf_values.append(mtbf if isinstance(mtbf, float) else None)
            stops_values.append(stops)

        valid_dates_oee = [dates[i] for i in range(len(dates)) if oee_values[i] is not None]
        valid_oee = [oee_values[i] for i in range(len(oee_values)) if oee_values[i] is not None]

        valid_dates_mtbf = [dates[i] for i in range(len(dates)) if mtbf_values[i] is not None]
        valid_mtbf = [mtbf_values[i] for i in range(len(mtbf_values)) if mtbf_values[i] is not None]

        valid_dates_stops = [dates[i] for i in range(len(dates)) if stops_values[i] > 0]
        valid_stops = [stops_values[i] for i in range(len(stops_values)) if stops_values[i] > 0]

        fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(10, 8), sharex=True)

        # --- OEE ---
        ax1.plot(valid_dates_oee, valid_oee, label="OEE (%)", color="green", marker="o")
        ax1.axhline(y=self.target_oee, color='r', linestyle='--', label=f"Цель: {self.target_oee}%")
        ax1.set_title(f"OEE по дням ({month_str})")
        ax1.set_ylabel("OEE (%)")
        ax1.grid(True)
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)

        # --- MTBF ---
        ax2.plot(valid_dates_mtbf, valid_mtbf, label="MTBF (мин)", color="blue", marker="s")
        ax2.axhline(y=self.target_mtbf, color='g', linestyle='--', label=f"Цель: {self.target_mtbf} мин")
        ax2.set_title(f"MTBF по дням ({month_str})")
        ax2.set_ylabel("MTBF (мин)")
        ax2.grid(True)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)

        # --- Стопы ---
        ax3.bar(valid_dates_stops, valid_stops, label="Остановки", color="orange")
        ax3.axhline(y=self.target_stops, color='b', linestyle='--', label=f"Цель: {self.target_stops}")
        ax3.set_title(f"Количество остановок ({month_str})")
        ax3.set_ylabel("Число остановок")
        ax3.grid(True)
        ax3.legend()
        ax3.tick_params(axis='x', rotation=45)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_area)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        plt.close('all')


# === Окно администратора ===
class AdminWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("OEE — Администратор")
        self.root.geometry("770x600")

        self.conn, self.cursor = connect_db()
        self.days = get_days_of_month()
        self.current_index = 0

        # Месяц по умолчанию
        self.current_month = datetime.now().strftime("%Y-%m")

        # Машина
        self.machine_names = load_machine_names(self.cursor, self.current_month)


       # if not self.machine_names:
        #    self.machine_names = [""]
        self.selected_machine = tk.StringVar()
        self.selected_machine.set(self.machine_names[0] if self.machine_names else "Новая машина...")

        # Цели для выбранной машины
        self.target_oee, self.target_mtbf, self.target_stops, self.machine_speed = \
            load_target_values(self.cursor, self.current_month, self.selected_machine.get())

        # === Стили ===
        self.font_label = ("Segoe UI", 10)
        self.font_value = ("Segoe UI", 10, "bold")
        self.color_bg = "#F5F5F5"
        self.color_fg = "#212121"
        self.root.configure(bg=self.color_bg)

        self.create_widgets()
        self.find_first_unfilled_day()
        self.update_stats()

    def create_widgets(self):
        padding_x = 10
        padding_y = 5

        # --- Выбор машины ---
        self.machine_selector_label = tk.Label(self.root, text="Машина:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.machine_selector_label.place(x=20, y=60)

        self.machine_combo = ttk.Combobox(
            self.root,
            textvariable=self.selected_machine,
            values=self.machine_names + ["Новая машина..."],
            state="readonly",
            width=20
        )
        self.machine_combo.place(x=110, y=60)
        self.machine_combo.bind("<<ComboboxSelected>>", self.on_machine_selected)

        # --- Цели ---
        self.target_oee_label = tk.Label(self.root, text="Цель OEE:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.target_oee_label.place(x=20, y=20)

        self.target_oee_var = tk.StringVar(value=str(self.target_oee))
        self.target_oee_entry = tk.Entry(self.root, width=8, textvariable=self.target_oee_var, font=self.font_label)
        self.target_oee_entry.place(x=140, y=20)

        self.target_mtbf_label = tk.Label(self.root, text="Цель MTBF :", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.target_mtbf_label.place(x=230, y=20)

        self.target_mtbf_var = tk.StringVar(value=str(self.target_mtbf))
        self.target_mtbf_entry = tk.Entry(self.root, width=8, textvariable=self.target_mtbf_var, font=self.font_label)
        self.target_mtbf_entry.place(x=350, y=20)

        self.target_stops_label = tk.Label(self.root, text="Цель стопов:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.target_stops_label.place(x=440, y=20)

        self.target_stops_var = tk.StringVar(value=str(self.target_stops))
        self.target_stops_entry = tk.Entry(self.root, width=8, textvariable=self.target_stops_var, font=self.font_label)
        self.target_stops_entry.place(x=550, y=20)

        self.machine_speed_label = tk.Label(self.root, text="Скорость (Кор/мин):", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.machine_speed_label.place(x=310, y=60)

        self.machine_speed_var = tk.StringVar(value=str(self.machine_speed))
        self.machine_speed_entry = tk.Entry(self.root, width=8, textvariable=self.machine_speed_var, font=self.font_label)
        self.machine_speed_entry.place(x=450, y=60)

        self.target_save_button = tk.Button(self.root, text="Сохранить цели", command=self.save_targets,
                                           bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"))
        self.target_save_button.place(x=640, y=18)

        # --- Дата ---
        self.date_label = tk.Label(self.root, text="Дата:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.date_label.place(x=580, y=60)

        self.date_entry = DateEntry(
            self.root,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 10)
        )
        self.date_entry.place(x=635, y=60)
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.load_day_by_date(self.date_entry.get()))
        # --- Смена 1 заголовок ---
        tk.Label(self.root, text="Дневная смена", font=("Segoe UI", 12, "bold"), fg="#1E88E5", bg=self.color_bg).place(x=140, y=90)

        self.shift1_time_label = tk.Label(self.root, text="Время работы :", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.shift1_time_label.place(x=80, y=120)

        self.s1_time_var = tk.StringVar()
        self.s1_time_var.trace_add("write", lambda *args: self.calculate_oee())
        self.shift1_time_entry = tk.Entry(self.root, width=10, textvariable=self.s1_time_var, font=self.font_label)
        self.shift1_time_entry.place(x=230, y=120)

        self.shift1_prod_label = tk.Label(self.root, text="Выработка:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.shift1_prod_label.place(x=80, y=150)

        self.s1_prod_var = tk.StringVar()
        self.s1_prod_var.trace_add("write", lambda *args: self.calculate_oee())
        self.shift1_prod_entry = tk.Entry(self.root, width=10, textvariable=self.s1_prod_var, font=self.font_label)
        self.shift1_prod_entry.place(x=230, y=150)

        self.shift1_oee_value = tk.Label(self.root, text="--%", fg="blue", font=self.font_value)
        self.shift1_oee_value.place(x=350, y=150)

        # --- Смена 2 заголовок ---
        tk.Label(self.root, text="Ночная смена", font=("Segoe UI", 12, "bold"), fg="#43A047", bg=self.color_bg).place(x=490, y=90)

        self.shift2_time_label = tk.Label(self.root, text="Время работы:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.shift2_time_label.place(x=440, y=120)

        self.s2_time_var = tk.StringVar()
        self.s2_time_var.trace_add("write", lambda *args: self.calculate_oee())
        self.shift2_time_entry = tk.Entry(self.root, width=10, textvariable=self.s2_time_var, font=self.font_label)
        self.shift2_time_entry.place(x=590, y=120)

        self.shift2_prod_label = tk.Label(self.root, text="Выработка:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.shift2_prod_label.place(x=440, y=150)

        self.s2_prod_var = tk.StringVar()
        self.s2_prod_var.trace_add("write", lambda *args: self.calculate_oee())
        self.shift2_prod_entry = tk.Entry(self.root, width=10, textvariable=self.s2_prod_var, font=self.font_label)
        self.shift2_prod_entry.place(x=590, y=150)

        self.shift2_oee_value = tk.Label(self.root, text="--%", fg="blue", font=self.font_value)
        self.shift2_oee_value.place(x=710, y=150)

        # --- Общий OEE за день ---
        self.total_oee_label = tk.Label(self.root, text="Суточный OEE:", font=("Segoe UI", 13, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.total_oee_label.place(x=220, y=290)

        self.total_oee_value = tk.Label(self.root, text="--%", font=("Segoe UI", 13, "bold"), fg="black")
        self.total_oee_value.place(x=450, y=290)

        # --- Средний OEE по месяцу ---
        self.average_oee_label = tk.Label(self.root, text="Средний OEE с начала месяца:", font=("Segoe UI", 13, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.average_oee_label.place(x=55, y=350)

        self.average_oee_value = tk.Label(self.root, text="--%", font=("Segoe UI", 15, "bold"), fg="purple")
        self.average_oee_value.place(x=320, y=345)

        # --- Отклонение от цели ---
        self.average_diff_label = tk.Label(self.root, text=":Отклонение от цели ОЕЕ", font=("Segoe UI", 13, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.average_diff_label.place(x=480, y=350)

        self.average_diff_value = tk.Label(self.root, text="--%", font=("Segoe UI", 15, "bold"), fg="black")
        self.average_diff_value.place(x=420, y=345)

        # --- Количество остановок за день ---
        self.stops_label = tk.Label(self.root, text="Кол-во остановок за сутки:", font=self.font_label, bg=self.color_bg, fg=self.color_fg)
        self.stops_label.place(x=220, y=200)

        self.stops_var = tk.StringVar()
        self.stops_entry = tk.Entry(self.root, width=10, textvariable=self.stops_var, font=self.font_label)
        self.stops_entry.place(x=470, y=200)

        # --- Необходимая выработка в день ---
        self.required_prod_label = tk.Label(self.root, text="Необходимо ежесменно выпускать:", font=("Segoe UI", 14, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.required_prod_label.place(x=110, y=455)

        self.required_prod_value = tk.Label(self.root, text="--", font=("Segoe UI", 18, "bold"), fg="orange")
        self.required_prod_value.place(x=470, y=450)

        # --- Ср. число остановок ---
        self.avg_stops_label = tk.Label(self.root, text="Среднее количество остановок:", font=("Segoe UI", 13, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.avg_stops_label.place(x=55, y=400)

        self.avg_stops_value = tk.Label(self.root, text="--", font=("Segoe UI", 15, "bold"), fg="red")
        self.avg_stops_value.place(x=340, y=395)

        # --- Ср. MTBF ---
        self.avg_mtbf_label = tk.Label(self.root, text=":Средний MTBF", font=("Segoe UI", 13, "bold"), bg=self.color_bg, fg=self.color_fg)
        self.avg_mtbf_label.place(x=510, y=400)

        self.avg_mtbf_value = tk.Label(self.root, text="--", font=("Segoe UI", 15, "bold"), fg="blue")
        self.avg_mtbf_value.place(x=430, y=395)

        # --- Кнопки ---
        self.save_button = tk.Button(self.root, text="Сохранить", command=self.save_and_next,
                                    bg="#43A047", fg="white", font=("Segoe UI", 13, "bold"))
        self.save_button.place(x=330, y=240)

        self.graph_button = tk.Button(self.root, text="Показать графики", command=lambda: GraphWindow(self.root, self.cursor, self.selected_machine.get()),
                                     bg="#5E35B1", fg="white", font=("Segoe UI", 13, "bold"))
        self.graph_button.place(x=300, y=510)
        self.update_stats()

    def on_machine_selected(self, event=None):
        selected = self.selected_machine.get()
        if selected == "Новая машина...":
            new_name = simpledialog.askstring("Новая машина", "Введите название новой машины:")
            if new_name:
                save_target_values(
                    self.cursor, self.conn,
                    self.current_month, new_name,
                    self.target_oee, self.target_mtbf, self.target_stops, self.machine_speed
                )
                self.conn.commit()

                self.machine_names = load_machine_names(self.cursor, self.current_month)
                self.machine_combo['values'] = self.machine_names + ["Новая машина..."]
                self.selected_machine.set(new_name)

        # Перезагружаем цели для активной машины
        current_machine = self.selected_machine.get()
        selected_date = self.date_entry.get()
        self.current_month = selected_date[:7]

        self.target_oee, self.target_mtbf, self.target_stops, self.machine_speed = \
            load_target_values(self.cursor, self.current_month, current_machine)

        self.update_stats()
        self.load_day_by_date(selected_date)

    def find_first_unfilled_day(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        for i, date_str in enumerate(self.days):
            if date_str > today_str:
                break
            if not is_date_saved(self.cursor, date_str, self.selected_machine.get()):
                self.load_day_by_date(date_str)
                self.current_index = i
                return

        messagebox.showinfo("Инфо", "Все дни заполнены или будущие.")
        #self.root.after(1000, self.root.destroy)


    def get_days_of_month_for(year, month):
        first_day = datetime(year, month, 1).date()
        next_month = datetime(year + 1, 1, 1) if month == 12 \
            else datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).date()

        delta = timedelta(days=1)
        current = first_day
        days = []

        while current <= last_day:
            days.append(current.strftime('%Y-%m-%d'))
            current += delta

        return days



    def load_day_by_date(self, date_str):
        """Загружает данные за конкретную дату"""

        selected_month = date_str[:7]
        try:
            year, month = map(int, selected_month.split("-"))
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты.")
            return
        # Получаем дни для нужного месяца
        self.days = get_days_of_month_for(year, month)

        # Обновляем месяц
        self.current_month = selected_month

        # Цели для текущей машины и месяца
        current_machine = self.selected_machine.get()
        self.target_oee, self.target_mtbf, self.target_stops, self.machine_speed = \
            load_target_values(self.cursor, self.current_month, current_machine)

        # Обновляем поля ввода целей
        self.target_oee_var.set(str(self.target_oee))
        self.target_mtbf_var.set(str(self.target_mtbf))
        self.target_stops_var.set(str(self.target_stops))
        self.machine_speed_var.set(str(self.machine_speed))

        # Данные за день
        if is_date_saved(self.cursor, date_str, current_machine):
            self.cursor.execute('''
                SELECT shift1_time, shift1_prod, shift2_time, shift2_prod, stops 
                FROM daily_work WHERE date=? AND machine_name=?
            ''', (date_str, current_machine))
            row = self.cursor.fetchone()
            if row:
                s1t, s1p, s2t, s2p, stops = row
                self.s1_time_var.set(s1t)
                self.s1_prod_var.set(round(s1p, 1))
                self.s2_time_var.set(s2t)
                self.s2_prod_var.set(round(s2p, 1))
                self.stops_var.set(stops)
            else:
                self.s1_time_var.set("720")
                self.s1_prod_var.set("")
                self.s2_time_var.set("720")
                self.s2_prod_var.set("")
                self.stops_var.set("")
        else:
            self.s1_time_var.set("720")
            self.s1_prod_var.set("")
            self.s2_time_var.set("720")
            self.s2_prod_var.set("")
            self.stops_var.set("")

        self.calculate_oee()

    def update_stats(self):
        machine_name = self.selected_machine.get()
        month_str = self.current_month

        avg_oee = calculate_global_average_for_month(self.cursor, month_str, machine_name)
        diff = round(avg_oee - self.target_oee, 1) if isinstance(avg_oee, float) else "--"

        avg_stops = calculate_avg_stops(self.cursor, month_str, machine_name)
        avg_mtbf = calculate_avg_mtbf(self.cursor, month_str, machine_name)
        daily_required = calculate_daily_required(self.cursor, self.days, machine_name)

        # --- Обновление метрик ---
        oee_color = "green" if isinstance(avg_oee, float) and avg_oee >= self.target_oee else "red" if isinstance(avg_oee, float) else "black"
        diff_color = "green" if isinstance(diff, float) and diff >= 0 else "red" if isinstance(diff, float) else "black"
        stops_color = "green" if isinstance(avg_stops, float) and avg_stops <= self.target_stops \
            else "red" if isinstance(avg_stops, float) else "black"
        mtbf_color = "green" if isinstance(avg_mtbf, float) and avg_mtbf >= self.target_mtbf \
            else "red" if isinstance(avg_mtbf, float) else "black"
        req_color = "green" if isinstance(daily_required, float) and daily_required >= 0 \
            else "red" if isinstance(daily_required, float) else "black"

        self.average_oee_value.config(text=f"{avg_oee}%" if isinstance(avg_oee, float) else "--%", fg=oee_color)
        self.average_diff_value.config(text=f"{diff:+}%" if isinstance(diff, float) else "--%", fg=diff_color)
        self.avg_stops_value.config(text=f"{avg_stops}" if isinstance(avg_stops, float) else "--", fg=stops_color)
        self.avg_mtbf_value.config(text=f"{avg_mtbf} мин" if isinstance(avg_mtbf, float) else "--", fg=mtbf_color)
        self.required_prod_value.config(text=f"{daily_required} Кор" if isinstance(daily_required, float) else "--", fg=req_color)

    def calculate_oee(self):
        try:
            s1_time = int(self.s1_time_var.get()) if self.s1_time_var.get() else 0
            s1_prod = float(self.s1_prod_var.get()) if self.s1_prod_var.get() else 0.0
            s2_time = int(self.s2_time_var.get()) if self.s2_time_var.get() else 0
            s2_prod = float(self.s2_prod_var.get()) if self.s2_prod_var.get() else 0.0
        except:
            return

        total_time = s1_time + s2_time
        total_prod = s1_prod + s2_prod

        max_total = total_time * self.machine_speed
        if max_total > 0:
            total_oee = round((total_prod / max_total) * 100, 1)
        else:
            total_oee = "--"

        if s1_time > 0:
            oee_s1 = round((s1_prod / (s1_time * self.machine_speed)) * 100, 1)
            s1_color = "green" if oee_s1 >= self.target_oee else "red"
            self.shift1_oee_value.config(text=f"{oee_s1}%", fg=s1_color)
        else:
            self.shift1_oee_value.config(text="--%", fg="black")

        if s2_time > 0:
            oee_s2 = round((s2_prod / (s2_time * self.machine_speed)) * 100, 1)
            s2_color = "green" if oee_s2 >= self.target_oee else "red"
            self.shift2_oee_value.config(text=f"{oee_s2}%", fg=s2_color)
        else:
            self.shift2_oee_value.config(text="--%", fg="black")

        if isinstance(total_oee, float):
            total_color = "green" if total_oee >= self.target_oee else "red"
            self.total_oee_value.config(text=f"{total_oee}%", fg=total_color)
        else:
            self.total_oee_value.config(text="--%", fg="black")

        self.update_stats()

    def save_and_next(self):
        date_str = self.date_entry.get()
        today_str = datetime.now().strftime('%Y-%m-%d')

        if date_str > today_str:
            messagebox.showerror("Ошибка", f"Нельзя заполнять данные за будущие даты. Сегодня: {today_str}")
            return

        try:
            s1t = int(self.s1_time_var.get()) if self.s1_time_var.get() else 0
            s1p = float(self.s1_prod_var.get()) if self.s1_prod_var.get() else 0.0
            s2t = int(self.s2_time_var.get()) if self.s2_time_var.get() else 0
            s2p = float(self.s2_prod_var.get()) if self.s2_prod_var.get() else 0.0
            stops = int(self.stops_var.get()) if self.stops_var.get() else 0
        except:
            messagebox.showerror("Ошибка", "Введите корректные числа во все поля.")
            return

        if s1t == 0:
            s1p = 0.0
        if s2t == 0:
            s2p = 0.0

        save_day_data(self.cursor, self.conn, date_str, self.selected_machine.get(),
                      s1t, s1p, s2t, s2p, stops)
                      
                      
                      

        try:
            idx = self.days.index(date_str)
        except ValueError:
            messagebox.showerror("Ошибка", f"Выбранная дата {date_str} не принадлежит текущему месяцу.")
            return
        
        
        
        if idx < len(self.days) - 1:
            next_date = self.days[idx + 1]
            self.date_entry.set_date(datetime.strptime(next_date, "%Y-%m-%d").date())
            self.load_day_by_date(next_date)
        else:
            messagebox.showinfo("Инфо", "Вы дошли до конца месяца.")

        self.update_stats()

    def save_targets(self):
        try:
            target_oee = float(self.target_oee_var.get())
            target_mtbf = float(self.target_mtbf_var.get())
            target_stops = float(self.target_stops_var.get())
            machine_speed = float(self.machine_speed_var.get())

            if not (0 <= target_oee <= 100 and target_mtbf >= 0 and target_stops >= 0 and machine_speed > 0):
                raise ValueError

            save_target_values(
                self.cursor, self.conn,
                self.current_month, self.selected_machine.get(),
                target_oee, target_mtbf, target_stops, machine_speed
            )

            self.target_oee, self.target_mtbf, self.target_stops, self.machine_speed = \
                load_target_values(self.cursor, self.current_month, self.selected_machine.get())

            self.update_stats()
            self.target_oee_entry.config(fg="black")
            self.target_mtbf_entry.config(fg="black")
            self.target_stops_entry.config(fg="black")
            self.machine_speed_entry.config(fg="black")

        except:
            self.target_oee_entry.config(fg="red")
            self.target_mtbf_entry.config(fg="red")
            self.target_stops_entry.config(fg="red")
            self.machine_speed_entry.config(fg="red")
            messagebox.showerror("Ошибка", "Введите корректные значения целей.")

# === Окно просмотра ===
class ViewerWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ключевые показатели оборудования")
        self.root.geometry("380x630")
        self.root.resizable(False, False)
        self.auto_update_interval = 3600_000  # 300 000 мс = 5 минут
        self.root.after(self.auto_update_interval, self.auto_update)
        self.conn, self.cursor = connect_db()
        self.days = get_days_of_month()

        self.machine_names = load_machine_names(self.cursor, datetime.now().strftime("%Y-%m"))
        self.selected_machine = tk.StringVar()
        self.selected_machine.set(self.machine_names[0] if self.machine_names else "Нет данных")

        self.current_month = datetime.now().strftime("%Y-%m")
        self.target_oee, self.target_mtbf, self.target_stops, _ = \
            load_target_values(self.cursor, self.current_month, self.selected_machine.get())

        # === Создаём виджеты ===
        self.create_widgets()
        self.update_stats()

    def auto_update(self):
        """Обновляет статистику через заданный интервал"""
        print("🔄 Автоматическое обновление данных...")
        self.update_stats()
        self.root.after(self.auto_update_interval, self.auto_update)  # Запускаем снова


    def create_widgets(self):
        padding_y = 5

        # --- Выбор машины ---
        self.machine_selector_label = tk.Label(self.root, text="Выберите машину:", font=("Segoe UI", 10))
        self.machine_selector_label.pack(pady=padding_y)

        self.machine_combo = ttk.Combobox(
            self.root,
            textvariable=self.selected_machine,
            values=self.machine_names or ["Нет данных"],
            state="readonly"
        )
        self.machine_combo.pack(pady=padding_y)
        self.machine_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stats())

        # --- Цель OEE ---
        self.target_oee_label = tk.Label(self.root, text="Цель OEE:", font=("Segoe UI", 15))
        self.target_oee_label.pack(pady=padding_y)

        self.target_oee_value = tk.Label(self.root, text="--%", font=("Segoe UI", 18, "bold"), fg="black")
        self.target_oee_value.pack()

        # --- Среднее значение OEE ---
        self.avg_oee_label = tk.Label(self.root, text="Средний OEE):", font=("Segoe UI", 15))
        self.avg_oee_label.pack(pady=padding_y)

        self.avg_oee_value = tk.Label(self.root, text="--%", font=("Segoe UI", 18, "bold"), fg="purple")
        self.avg_oee_value.pack()

        # --- Отклонение от цели ---
        self.avg_diff_label = tk.Label(self.root, text="Отклонение от цели:", font=("Segoe UI", 15))
        self.avg_diff_label.pack(pady=padding_y)

        self.avg_diff_value = tk.Label(self.root, text="--%", font=("Segoe UI", 18, "bold"), fg="black")
        self.avg_diff_value.pack()

        # --- Ср. число остановок ---
        self.avg_stops_label = tk.Label(self.root, text="Ср. число остановок:", font=("Segoe UI", 15))
        self.avg_stops_label.pack(pady=padding_y)

        self.avg_stops_value = tk.Label(self.root, text="--", font=("Segoe UI", 18, "bold"), fg="red")
        self.avg_stops_value.pack()

        # --- Ср. MTBF ---
        self.avg_mtbf_label = tk.Label(self.root, text="Ср. MTBF:", font=("Segoe UI", 15))
        self.avg_mtbf_label.pack(pady=padding_y)

        self.avg_mtbf_value = tk.Label(self.root, text="--", font=("Segoe UI", 18, "bold"), fg="blue")
        self.avg_mtbf_value.pack()

        # --- Необходимая выработка ---
        self.required_prod_label = tk.Label(self.root, text="Необходимо выпускать в смену:", font=("Segoe UI", 15))
        self.required_prod_label.pack(pady=padding_y)

        self.required_prod_value = tk.Label(self.root, text="--", font=("Segoe UI", 18, "bold"), fg="orange")
        self.required_prod_value.pack()

        # --- Кнопка обновления ---
        #self.refresh_button = tk.Button(self.root, text="Обновить", command=self.update_stats,
        #                               bg="#42A5F5", fg="white", font=("Segoe UI", 15, "bold"))
        #self.refresh_button.pack(pady=10)

        # --- График ---
        self.graph_button = tk.Button(self.root, text="Показать графики", command=lambda: GraphWindow(self.root, self.cursor, self.selected_machine.get()),
                                     bg="#5E35B1", fg="white", font=("Segoe UI", 15, "bold"))
        self.graph_button.pack(pady=5)

    def update_stats(self, event=None):
        machine_name = self.selected_machine.get()
        month_str = datetime.now().strftime("%Y-%m")

        self.target_oee, self.target_mtbf, self.target_stops, _ = load_target_values(self.cursor, month_str, machine_name)

        avg_oee = calculate_global_average_for_month(self.cursor, month_str, machine_name)
        diff = round(avg_oee - self.target_oee, 1) if isinstance(avg_oee, float) else "--"

        avg_stops = calculate_avg_stops(self.cursor, month_str, machine_name)
        avg_mtbf = calculate_avg_mtbf(self.cursor, month_str, machine_name)
        daily_required = calculate_daily_required(self.cursor, self.days, machine_name)

        # --- Цветовая индикация ---
        oee_color = "green" if isinstance(avg_oee, float) and avg_oee >= self.target_oee \
            else "red" if isinstance(avg_oee, float) else "black"
        diff_color = "green" if isinstance(diff, float) and diff >= 0 \
            else "red" if isinstance(diff, float) else "black"

        stops_color = "green" if isinstance(avg_stops, float) and avg_stops <= self.target_stops \
            else "red" if isinstance(avg_stops, float) else "black"

        mtbf_color = "green" if isinstance(avg_mtbf, float) and avg_mtbf >= self.target_mtbf \
            else "red" if isinstance(avg_mtbf, float) else "black"

        req_color = "green" if isinstance(daily_required, float) and daily_required >= 0 \
            else "red" if isinstance(daily_required, float) else "black"

        # --- Обновляем метрики ---
        self.avg_oee_value.config(text=f"{avg_oee}%" if isinstance(avg_oee, float) else "--%", fg=oee_color)
        self.avg_diff_value.config(text=f"{diff:+}%" if isinstance(diff, float) else "--%", fg=diff_color)
        self.avg_stops_value.config(text=f"{avg_stops}" if isinstance(avg_stops, float) else "--", fg=stops_color)
        self.avg_mtbf_value.config(text=f"{avg_mtbf} мин" if isinstance(avg_mtbf, float) else "--", fg=mtbf_color)
        self.required_prod_value.config(text=f"{daily_required} Кор" if isinstance(daily_required, float) else "--", fg=req_color)
        self.target_oee_value.config(text=f"{self.target_oee}%")


# === Запуск программы ===
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно до выбора режима

    current_user = getpass.getuser().lower()
    allowed_admin_users = ["petvolkoy", "petprikhs"]  # Укажи свои разрешённые имена

    if current_user in allowed_admin_users:
        mode = simpledialog.askstring("Режим работы", "Выберите режим:\n\n"
                                                           "1 - Администратор (редактирование)\n"
                                                           "2 - Просмотр (только чтение)", initialvalue="1")
        if mode == "1":
            root.deiconify()  # Показываем окно
            app = AdminWindow(root)
        elif mode == "2":
            root.deiconify()
            app = ViewerWindow(root)
        else:
            messagebox.showerror("Ошибка", "Неверный режим.")
            root.destroy()
    else:
        messagebox.showinfo("Авторизация", f"Вы вошли как {current_user}\n"
                                          "Режим: только просмотр")
        root.deiconify()
        app = ViewerWindow(root)

    root.mainloop()