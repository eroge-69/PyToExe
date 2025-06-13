import tkinter as tk
from tkinter import messagebox
import datetime
import calendar
import json
import os

DATA_FILE = "court_schedule.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class CourtScheduler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Судебный Ежедневник")
        self.geometry("800x700")
        self.resizable(False, False)

        self.data = load_data()
        self.today = datetime.date.today()
        self.year = self.today.year
        self.month = self.today.month

        self.selected_date = None
        self.entries = {}

        self.create_widgets()
        self.draw_calendar()

    def create_widgets(self):
        self.calendar_frame = tk.Frame(self)
        self.calendar_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='w')

        # Навигация по месяцам
        tk.Button(self, text="<", command=self.prev_month).grid(row=0, column=0, sticky="w", padx=10)
        tk.Button(self, text=">", command=self.next_month).grid(row=0, column=1, sticky="w")

        # Поля ввода
        fields = ["Номер дела", "Суд", "Дата (ДД.ММ.ГГГГ)", "Время (ЧЧ:ММ)", "Зал заседания", "Комментарий"]
        for i, label in enumerate(fields):
            tk.Label(self, text=label).grid(row=i+1, column=0, sticky="w", padx=10)
            entry = tk.Entry(self, width=40)
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky='w')
            self.entries[label] = entry

        # Кнопки
        tk.Button(self, text="Добавить дело", command=self.add_case).grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky='w')

        self.case_listbox = tk.Listbox(self, width=70, height=10)
        self.case_listbox.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
        self.case_listbox.bind('<<ListboxSelect>>', self.on_select_case)

        tk.Button(self, text="Удалить", command=self.delete_case).grid(row=10, column=0, sticky='w', padx=10)
        tk.Button(self, text="Сохранить изменения", command=self.edit_case).grid(row=10, column=1, sticky='w', padx=10)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        tk.Label(self.calendar_frame, text=f"{calendar.month_name[self.month]} {self.year}", font=('Arial', 14, 'bold')).grid(row=0, column=2, columnspan=3)

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for idx, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=('Arial', 10, 'bold')).grid(row=1, column=idx)

        month_calendar = calendar.monthcalendar(self.year, self.month)
        for row_idx, week in enumerate(month_calendar):
            for col_idx, day in enumerate(week):
                if day == 0:
                    label = tk.Label(self.calendar_frame, text="", width=4, height=2)
                else:
                    date_str = f"{day:02d}.{self.month:02d}.{self.year}"
                    has_case = date_str in self.data
                    color = 'red' if has_case else 'black'
                    label = tk.Label(self.calendar_frame, text=str(day), width=4, height=2, fg=color, cursor="hand2")
                    label.bind("<Button-1>", lambda e, d=date_str: self.select_date(d))
                label.grid(row=row_idx+2, column=col_idx)

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.draw_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.draw_calendar()

    def select_date(self, date_str):
        self.selected_date = date_str
        self.entries["Дата (ДД.ММ.ГГГГ)"].delete(0, tk.END)
        self.entries["Дата (ДД.ММ.ГГГГ)"].insert(0, date_str)
        self.show_cases(date_str)

    def show_cases(self, date_str):
        self.case_listbox.delete(0, tk.END)
        if date_str in self.data:
            for idx, case in enumerate(self.data[date_str]):
                display = f"{idx+1}. [{case['время']}] {case['номер дела']} - {case['суд']} ({case['зал']})"
                self.case_listbox.insert(tk.END, display)

    def on_select_case(self, event):
        selection = event.widget.curselection()
        if not selection or not self.selected_date:
            return

        index = selection[0]
        case = self.data[self.selected_date][index]

        self.entries["Номер дела"].delete(0, tk.END)
        self.entries["Суд"].delete(0, tk.END)
        self.entries["Время (ЧЧ:ММ)"].delete(0, tk.END)
        self.entries["Зал заседания"].delete(0, tk.END)
        self.entries["Комментарий"].delete(0, tk.END)

        self.entries["Номер дела"].insert(0, case["номер дела"])
        self.entries["Суд"].insert(0, case["суд"])
        self.entries["Время (ЧЧ:ММ)"].insert(0, case["время"])
        self.entries["Зал заседания"].insert(0, case["зал"])
        self.entries["Комментарий"].insert(0, case["комментарий"])

    def add_case(self):
        date = self.entries["Дата (ДД.ММ.ГГГГ)"].get()
        case = {
            "номер дела": self.entries["Номер дела"].get(),
            "суд": self.entries["Суд"].get(),
            "время": self.entries["Время (ЧЧ:ММ)"].get(),
            "зал": self.entries["Зал заседания"].get(),
            "комментарий": self.entries["Комментарий"].get()
        }

        if not all([case["номер дела"], case["суд"], date, case["время"], case["зал"]]):
            messagebox.showwarning("Ошибка", "Заполните обязательные поля")
            return

        try:
            datetime.datetime.strptime(date, "%d.%m.%Y")
            datetime.datetime.strptime(case["время"], "%H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты или времени")
            return

        if date not in self.data:
            self.data[date] = []
        self.data[date].append(case)

        save_data(self.data)
        self.draw_calendar()
        self.select_date(date)

        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def delete_case(self):
        selection = self.case_listbox.curselection()
        if not selection or not self.selected_date:
            return
        index = selection[0]
        del self.data[self.selected_date][index]
        if not self.data[self.selected_date]:
            del self.data[self.selected_date]
        save_data(self.data)
        self.draw_calendar()
        self.select_date(self.selected_date)

    def edit_case(self):
        selection = self.case_listbox.curselection()
        if not selection or not self.selected_date:
            return
        index = selection[0]
        case = {
            "номер дела": self.entries["Номер дела"].get(),
            "суд": self.entries["Суд"].get(),
            "время": self.entries["Время (ЧЧ:ММ)"].get(),
            "зал": self.entries["Зал заседания"].get(),
            "комментарий": self.entries["Комментарий"].get()
        }
        try:
            datetime.datetime.strptime(case["время"], "%H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат времени")
            return

        self.data[self.selected_date][index] = case
        save_data(self.data)
        self.select_date(self.selected_date)

if __name__ == "__main__":
    app = CourtScheduler()
    app.mainloop()
