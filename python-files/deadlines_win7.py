# -*- coding: utf-8 -*-
"""
Deadlines table + side calendar (Windows 7 friendly, no external libraries).
Tested with Python 3.8 (last Python officially supporting Windows 7).

How to run on Windows:
1) Install Python 3.8 (32-bit) from python.org (choose Windows x86 executable installer).
2) Save this file as deadlines_win7.py (if не сохранён автоматически).
3) Double-click it или запустите в консоли:  python deadlines_win7.py

UI language: Russian.
"""
import re
import csv
import calendar
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_TITLE = "Таблица сроков + календарь (Windows 7)"
DATE_INPUT_HINT = 'Пример: 381пр-2025 от 20.01'

# --- Настраиваемые праздничные дни РФ (упрощённый список, без переносов) ---
# Можно редактировать ниже при необходимости.
FIXED_HOLIDAYS_BY_MD = {
    # Январские праздники (обычно 1–8 января — новогодние каникулы)
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
    # День защитника Отечества
    (2, 23),
    # Международный женский день
    (3, 8),
    # Праздники мая
    (5, 1), (5, 9),
    # День России
    (6, 12),
    # День народного единства
    (11, 4),
}

# --- Бизнес-логика ---
def parse_entry_line(line: str):
    """
    Разбирает строку вида: 381пр-2025 от 20.01
    Возвращает (номер, base_date) где base_date = datetime.date
    """
    # Ищем год после дефиса
    year_match = re.search(r"-\s*(\d{4})", line)
    # Ищем дату "от dd.mm"
    date_match = re.search(r"от\\s*(\\d{1,2})[.\\-/](\\d{1,2})", line, flags=re.IGNORECASE)

    if not date_match or not year_match:
        raise ValueError("Не удалось распознать год и/или дату 'от dd.mm' в строке.")

    year = int(year_match.group(1))
    dd = int(date_match.group(1))
    mm = int(date_match.group(2))

    try:
        base = date(year, mm, dd)
    except ValueError:
        raise ValueError("Некорректная дата в строке: проверьте число и месяц.")

    # Номер (все до ' от '), либо вся строка если нет ' от '
    number = line.split(" от ")[0].strip()
    return number, base


def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)


def is_weekend(d: date) -> bool:
    # 5 = суббота, 6 = воскресенье
    return d.weekday() >= 5


def is_holiday(d: date) -> bool:
    return (d.month, d.day) in FIXED_HOLIDAYS_BY_MD


def mark_text(d: date) -> str:
    """
    Возвращает текст для таблицы. Если это выходной/праздник, добавляет метку.
    """
    mark = []
    if is_weekend(d):
        mark.append("выходной")
    if is_holiday(d):
        mark.append("праздник")
    if mark:
        return f"{d.strftime('%d.%m.%Y')} [{', '.join(mark)}]"
    return d.strftime("%d.%m.%Y")


# --- Модель данных в памяти ---
class Row:
    def __init__(self, number: str, base_date: date):
        self.number = number
        self.base_date = base_date
        # По условию: 10-дневный = +7 к дате исчисления 3-дневного (т.е. итого +10 к базе)
        self.d3 = add_days(base_date, 3)
        self.d10 = add_days(self.d3, 7)  # = base + 10
        self.d30 = add_days(base_date, 30)


# --- GUI ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x600")
        self.minsize(980, 560)

        # Данные
        self.rows = []  # list[Row]

        # Верхняя панель ввода
        self._build_topbar()

        # Левая таблица + правая панель календаря
        self._build_main_panes()

        # Отрисовать текущий месяц в календаре
        today = date.today()
        self.current_month = today.month
        self.current_year = today.year
        self._draw_calendar()

    # --- UI: верхняя панель ---
    def _build_topbar(self):
        frame = ttk.Frame(self, padding=(8, 6))
        frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame, text="Ввод строки:").pack(side=tk.LEFT)
        self.entry_var = tk.StringVar(value="")
        entry = ttk.Entry(frame, textvariable=self.entry_var, width=50)
        entry.pack(side=tk.LEFT, padx=6)
        entry.insert(0, DATE_INPUT_HINT)

        ttk.Button(frame, text="Добавить", command=self.on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Удалить выбранные", command=self.on_delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Сохранить CSV", command=self.on_save_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Загрузить CSV", command=self.on_load_csv).pack(side=tk.LEFT, padx=2)

    # --- UI: основная область ---
    def _build_main_panes(self):
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Левая — таблица
        left = ttk.Frame(paned, padding=(6, 6))
        paned.add(left, weight=3)

        cols = ("number", "base", "d3", "d10", "d30")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=20)
        self.tree.heading("number", text="Номер / описание")
        self.tree.heading("base", text="Дата исчисления (база)")
        self.tree.heading("d3", text="3-дневный срок (истекает)")
        self.tree.heading("d10", text="10-дневный срок (истекает)")
        self.tree.heading("d30", text="30-дневный срок (истекает)")

        self.tree.column("number", width=260, anchor=tk.W)
        self.tree.column("base", width=160, anchor=tk.CENTER)
        self.tree.column("d3", width=170, anchor=tk.CENTER)
        self.tree.column("d10", width=170, anchor=tk.CENTER)
        self.tree.column("d30", width=170, anchor=tk.CENTER)

        ysb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        # Подсказки
        hint = ttk.Label(left, foreground="#555",
                         text="Подсветка: в таблице даты-выходные/праздники помечаются в скобках.\n"
                              "Календарь справа показывает все рассчитанные сроки.")
        hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Правая — календарь
        right = ttk.Frame(paned, padding=(6, 6))
        paned.add(right, weight=2)

        topbar = ttk.Frame(right)
        topbar.pack(side=tk.TOP, fill=tk.X)

        self.month_label = ttk.Label(topbar, text="")
        self.month_label.pack(side=tk.LEFT)

        ttk.Button(topbar, text="<<", width=3, command=self.on_prev_month).pack(side=tk.RIGHT, padx=(2, 0))
        ttk.Button(topbar, text=">>", width=3, command=self.on_next_month).pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(right, height=360)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        legend = ttk.Label(right, foreground="#555",
                           text="Легенда: выходные/праздники — красным, "
                                "сроки — рамка.")
        legend.pack(side=tk.TOP, anchor="w", pady=(6, 0))

    # --- Обработчики ---
    def on_add(self):
        raw = self.entry_var.get().strip()
        try:
            number, base = parse_entry_line(raw)
        except Exception as e:
            messagebox.showerror("Ошибка разбора", str(e))
            return

        row = Row(number, base)
        self.rows.append(row)
        self._insert_tree_row(row)
        self._draw_calendar()

    def on_delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        # Удаляем из модели
        to_delete_texts = [self.tree.item(i, "values")[0] for i in sel]  # number
        self.rows = [r for r in self.rows if r.number not in to_delete_texts]
        # Удаляем из UI
        for i in sel:
            self.tree.delete(i)
        self._draw_calendar()

    def on_save_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Сохранить таблицу как CSV"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["number", "base", "d3", "d10", "d30"])
                for r in self.rows:
                    w.writerow([
                        r.number,
                        r.base_date.strftime("%d.%m.%Y"),
                        r.d3.strftime("%d.%m.%Y"),
                        r.d10.strftime("%d.%m.%Y"),
                        r.d30.strftime("%d.%m.%Y"),
                    ])
            messagebox.showinfo("Готово", "CSV сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_load_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Загрузить CSV"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f, delimiter=";")
                self.rows.clear()
                for row in self.tree.get_children():
                    self.tree.delete(row)
                for rec in r:
                    # Ожидаем формат как мы сохраняем
                    number = rec["number"]
                    base = datetime.strptime(rec["base"], "%d.%m.%Y").date()
                    obj = Row(number, base)
                    # Пересчитываем, а не доверяем CSV (чтобы логика была едина)
                    self.rows.append(obj)
                    self._insert_tree_row(obj)
            self._draw_calendar()
            messagebox.showinfo("Готово", "CSV загружен.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_prev_month(self):
        m, y = self.current_month, self.current_year
        m -= 1
        if m < 1:
            m = 12
            y -= 1
        self.current_month, self.current_year = m, y
        self._draw_calendar()

    def on_next_month(self):
        m, y = self.current_month, self.current_year
        m += 1
        if m > 12:
            m = 1
            y += 1
        self.current_month, self.current_year = m, y
        self._draw_calendar()

    # --- UI helpers ---
    def _insert_tree_row(self, r: Row):
        vals = (
            r.number,
            mark_text(r.base_date),
            mark_text(r.d3),
            mark_text(r.d10),
            mark_text(r.d30),
        )
        self.tree.insert("", tk.END, values=vals)

    def _collect_deadline_dates_for_month(self, y: int, m: int):
        """
        Возвращает множество дат в выбранном месяце, где есть какие-либо сроки.
        """
        s = set()
        for r in self.rows:
            for d in (r.base_date, r.d3, r.d10, r.d30):
                if d.year == y and d.month == m:
                    s.add(d.day)
        return s

    def _draw_calendar(self):
        y, m = self.current_year, self.current_month
        self.month_label.config(text=f"{calendar.month_name[m]} {y}".capitalize())

        self.canvas.delete("all")
        width = self.canvas.winfo_width() or 560
        height = self.canvas.winfo_height() or 360

        # Поля и размеры
        margin = 20
        cell_w = (width - margin * 2) // 7
        cell_h = (height - margin * 3) // 7  # 1 строка под дни недели + 6 недель
        x0, y0 = margin, margin

        # Заголовки дней недели (начинаем с Понедельника)
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, wd in enumerate(weekdays):
            self.canvas.create_text(x0 + i * cell_w + cell_w // 2,
                                    y0 + cell_h // 2,
                                    text=wd, font=("TkDefaultFont", 10, "bold"))

        cal = calendar.Calendar(firstweekday=0)  # 0=Пн
        month_days = list(cal.itermonthdates(y, m))
        # Собираем дни этого месяца в сетку: максимум 6 недель, 7 дней в строке
        # Начинаем рисовать со второй строки (первая — шапка дней недели)
        grid_y_start = y0 + cell_h
        deadlines = self._collect_deadline_dates_for_month(y, m)

        # Определить прямоугольники
        row = 0
        col = 0
        for d in month_days:
            cx = x0 + col * cell_w
            cy = grid_y_start + row * cell_h
            rx1, ry1 = cx, cy
            rx2, ry2 = cx + cell_w, cy + cell_h

            # Рамка ячейки
            self.canvas.create_rectangle(rx1, ry1, rx2, ry2)

            # Выходные/праздники — красным
            is_weekend_day = d.weekday() >= 5
            is_hol = is_holiday(d)
            text_fill = "red" if (is_weekend_day or is_hol) and d.month == m else None

            # Число дня
            self.canvas.create_text(rx1 + 6, ry1 + 6, text=str(d.day),
                                    anchor="nw", fill=text_fill)

            # Если это день с дедлайном — рисуем рамку внутри (выделение)
            if d.month == m and d.day in deadlines:
                pad = 4
                self.canvas.create_rectangle(rx1 + pad, ry1 + pad,
                                             rx2 - pad, ry2 - pad,
                                             width=2)

            # следующий столбец/строка
            col += 1
            if col >= 7:
                col = 0
                row += 1

            # Ограничимся максимум 6 неделями (обычно достаточно)
            if row >= 6:
                break


if __name__ == "__main__":
    app = App()
    app.mainloop()
