import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import calendar

# -------------------- ЦЕНЫ --------------------
positions_prices = {
    "BARRY 1300": 1300,
    "BARRY 1400": 1300,
    "BRACE 1000": 580,
    "BRACE 1100": 580,
    "BRACE 1200": 580,
    "BRACE 1300": 580,
    "BRACE 1400": 580,
    "BRACE 1500": 580,
    "BRACE 1600": 620,
    "BRACE 1700": 620,
    "BRACE 1800": 620,
    "CASINO 1300": 800,
    "CASINO 1400": 800,
    "CORONA 1300": 850,
    "CORONA 1400": 850,
    "CROCUS 1300, ткань": 740,
    "CROCUS 1400, ткань": 740,
    "CROCUS 1500, ткань": 740,
    "CROCUS 1600, ткань": 740,
    "CROCUS 1700, ткань": 850,
    "CROCUS 1800, ткань": 850,
    "CROCUS 1300, массив": 740,
    "CROCUS 1100, массив": 740,
    "DAZE 1000": 480,
    "DAZE 1100": 480,
    "DAZE 1200": 480,
    "DAZE 1300": 480,
    "DAZE 1400": 480,
    "DAZE 1500": 480,
    "DAZE 1600": 480,
    "DAZE 1700": 480,
    "DAZE 1800": 480,
    "ELLA 1300": 960,
    "ELLA 1400": 960,
    "INTER 1300": 680,
    "INTER 1400": 740,
    "LUTON (ELLA) 1300": 720,
    "LUTON (ECLA) 1400": 720,
    "COTON (ЛЕДИ) 1300": 720,
    "(CUTON (ЛЕДИ) 1400)": 720,
    "MILANO 1000": 480,
    "MILANO 1100": 480,
    "MILANO 1200": 480,
    "MILANO 1300": 480,
    "MILANO 1400": 480,
    "MILANO 1500": 480,
    "MILANO 1600": 530,
    "MILANO 1700": 530,
    "MILANO 1800": 530,
    "MOOSE 1000": 480,
    "MOOSE 1100": 480,
    "MOOSE 1200": 480,
    "MOOSE 1300": 480,
    "MOOSE 1400": 480,
    "MOOSE 1500": 480,
    "MOOSE 1600": 530,
    "MOOSE 1700": 530,
    "MOOSE 1800": 530,
    "ARNO": 480,
    "CASINO": 480,
    "CROCUS ткань": 460,
    "CROCUS массив": 460,
    "ELLA": 480,
    "INTER": 480,
    "KINZA": 480,
    "LUTON (ЛЕДИ)": 480,
    "MANTRA (мет.оп.)": 350,
    "MANTRA (дер.оп.)": 350,
    "MANTRA (качалка)": 350,
    "MILANO": 380,
    "MOSS 1300": 580,
    "RAZOR (мет.оп.)": 720,
    "RAZOR (дер. оп.)": 720,
    "RAZOR Mini (мeт.оп.)": 530,
    "RAZOR Mini (дер.оп.)": 530,
    "RAZOR Mini LOUNGE (мет.оп.)": 530,
    "RAZOR Mini LOUNGE (дер.оп.)": 530,
    "TIKA": 580,
    "TUTTU": 0,
    "Квин": 720,
    "Квин Н": 720,
    "Леди": 720,
    "Леди Н": 720,
    "Casino Patchwork": 480,
    "LOVER Lounge": 720,
    "Mantra Mini": 350,
    "WOOPY": 720,
    "WOOPY SPIN": 720,
    "NID Кресло h810": 970,
    "NID 2 Кресло h1090": 1580,
    "Кресло Uno": 580,
    "Кресло Gentle": 580,
    "Кресло LUNA": 580,
    "TED": 140,
    "VNOSS 1800": 720,
    "MOSS 2400": 800,
    "OW591 1300": 720,
    "OW591 1400": 720,
    "RAZOR 1300 (дер.оп.)": 800,
    "RAZOR 1400 (дер. оп.)": 800,
    "RAZOR 1300 (Meт.on.)": 800,
    "RAZOR 1400 (meт.on.)": 800,
    "SEN 1000": 480,
    "SEN 1100": 480,
    "SEN 1200": 480,
    "SEN 1300": 480,
    "SEN 1400": 480,
    "SEN 1500": 510,
    "SEN 1600": 580,
    "SEN 1700": 630,
    "SEN 1800": 630,
    "TUTTU 1340": 0,
    "WAVE": 580,
    "Леди 1300": 960,
    "Леди 1400": 960,
    "LORA 1300": 580,
    "LORA 1400": 580,
    "KATANA/KATANA lounge": 720,
    "Noook 1 1140": 1200,
    "Noook 1 1600": 1200,
    "Noook 1 2200": 1200,
    "Noook 2 1140": 960,
    "Noook 2 1600": 1100,
    "Noook 2 2200": 1200,
    "Noook 3 1140": 960,
    "Noook 3 1600": 1100,
    "Noook 3 2200": 1200,
    "Woopy 1400": 960,
    "NID 1 1464x730x810": 1440,
    "NID 2 1464x730x1090": 1780,
    "NID 1 2000x730x810": 1680,
    "NID 2 2000x730x1090": 1920,
    "Dandy": 0,
    "Agava 1000-1100": 430,
    "Agava 1200": 480,
    "Agava 1300": 480,
    "Agava 1400": 530,
    "Agava 1500": 530,
    "Agava 1600": 580,
}

DATA_FILE = "salary_data.json"

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_day_data(date_str, position, count, data):
    if date_str not in data:
        data[date_str] = {}
    if position in data[date_str]:
        data[date_str][position] += count
    else:
        data[date_str][position] = count

def calc_day_earnings(date_str, data):
    if date_str not in data:
        return 0
    total = 0
    for pos, count in data[date_str].items():
        price = positions_prices.get(pos, 0)
        total += price * count
    return total

class SalaryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учет зарплаты")
        self.geometry("800x600")
        self.data = load_data()
        self.today = datetime.now()
        self.create_widgets()

    def create_widgets(self):
        frm = tk.Frame(self)
        frm.pack(pady=10)

        tk.Label(frm, text="Позиция:").grid(row=0, column=0)
        self.position_var = tk.StringVar()
        self.position_combobox = ttk.Combobox(frm, textvariable=self.position_var, width=40)
        self.position_combobox['values'] = sorted(list(positions_prices.keys()))
        self.position_combobox.grid(row=1, column=0, padx=5)

        tk.Label(frm, text="Количество:").grid(row=0, column=1)
        self.count_entry = tk.Entry(frm, width=10)
        self.count_entry.grid(row=1, column=1, padx=5)

        tk.Button(frm, text="Добавить", command=self.add_position).grid(row=1, column=2, padx=10)

        report_frame = tk.Frame(self)
        report_frame.pack(pady=10)
        tk.Label(report_frame, text="От:").grid(row=0, column=0)
        self.start_entry = tk.Entry(report_frame, width=12)
        self.start_entry.grid(row=0, column=1)
        first_day = self.today.replace(day=1).strftime("%Y-%m-%d")
        self.start_entry.insert(0, first_day)

        tk.Label(report_frame, text="До:").grid(row=0, column=2)
        self.end_entry = tk.Entry(report_frame, width=12)
        self.end_entry.grid(row=0, column=3)
        last_day = self.today.replace(day=calendar.monthrange(self.today.year, self.today.month)[1]).strftime("%Y-%m-%d")
        self.end_entry.insert(0, last_day)

        tk.Button(report_frame, text="Показать отчет", command=self.show_report).grid(row=0, column=4, padx=10)

        self.tree = ttk.Treeview(self, columns=["date", "position", "amount"], show="headings", height=20)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        self.tree.heading("date", text="Дата")
        self.tree.heading("position", text="Позиция (× кол-во)")
        self.tree.heading("amount", text="Сумма (₽)")

        self.tree.column("date", width=150)
        self.tree.column("position", width=400)
        self.tree.column("amount", width=100, anchor="center")

        self.total_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

        # Кнопка удаления
        tk.Button(self, text="Удалить выбранную строку", command=self.delete_selected).pack(pady=5)

    def add_position(self):
        pos = self.position_var.get()
        if pos not in positions_prices:
            messagebox.showerror("Ошибка", "Неверная позиция.")
            return
        try:
            count = int(self.count_entry.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество.")
            return

        today_str = self.today.strftime("%Y-%m-%d")
        add_day_data(today_str, pos, count, self.data)
        save_data(self.data)
        self.count_entry.delete(0, tk.END)
        messagebox.showinfo("Добавлено", f"{pos} × {count} добавлено.")

    def show_report(self):
        self.tree.delete(*self.tree.get_children())
        try:
            start_date = datetime.strptime(self.start_entry.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты.")
            return

        if end_date < start_date:
            messagebox.showerror("Ошибка", "Дата конца раньше начала.")
            return

        week_total = 0
        total_sum = 0
        day_total = 0

        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            d_str = day.strftime("%Y-%m-%d")
            weekday = DAYS[day.weekday()]
            display_date = f"{d_str} ({weekday})"

            if d_str in self.data:
                self.tree.insert("", "end", values=(f"── {display_date} ──", "", ""))
                day_total = 0
                for pos, qty in self.data[d_str].items():
                    price = positions_prices.get(pos, 0)
                    total = qty * price
                    day_total += total
                    week_total += total
                    total_sum += total
                    self.tree.insert("", "end", values=(d_str, f"{pos} × {qty}", f"{total:,}"))
                self.tree.insert("", "end", values=("Итог за день:", "", f"{day_total:,} ₽"), tags=("bold",))

            if day.weekday() == 6:  # Воскресенье
                self.tree.insert("", "end", values=("Итог за неделю:", "", f"{week_total:,} ₽"), tags=("bold",))
                week_total = 0

        if week_total > 0:
            self.tree.insert("", "end", values=("Итог за неделю:", "", f"{week_total:,} ₽"), tags=("bold",))

        self.total_label.config(text=f"Сумма за период: {total_sum:,} ₽")

        if end_date.day in [30, 31] or (end_date + timedelta(days=1)).month != end_date.month:
            month_total = self.get_month_total(end_date.year, end_date.month)
            self.total_label.config(
                text=f"Сумма за период: {total_sum:,} ₽\nИтог за {end_date.strftime('%B %Y')}: {month_total:,} ₽"
            )

        self.tree.tag_configure("bold", font=("Arial", 10, "bold"))

    def get_month_total(self, year, month):
        total = 0
        for date_str, day_data in self.data.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj.year == year and date_obj.month == month:
                    for pos, count in day_data.items():
                        total += positions_prices.get(pos, 0) * count
            except ValueError:
                continue
        return total

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите строку для удаления.")
            return

        for item in selected:
            values = self.tree.item(item, "values")
            if len(values) != 3 or not values[0] or not values[1]:
                continue  # пропустить строки-разделители или итоги

            date_str = values[0].split(" ")[0]  # убрать (день недели)
            pos_qty = values[1]
            if '×' not in pos_qty:
                continue
            pos, qty = pos_qty.rsplit(' × ', 1)
            try:
                qty = int(qty)
            except ValueError:
                continue

            if date_str in self.data and pos in self.data[date_str]:
                self.data[date_str][pos] -= qty
                if self.data[date_str][pos] <= 0:
                    del self.data[date_str][pos]
                if not self.data[date_str]:
                    del self.data[date_str]

        save_data(self.data)
        self.show_report()

if __name__ == "__main__":
    app = SalaryApp()
    app.mainloop()
