# app.py
# Python 3.10+
# GUI-калькулятор аудитодней (tkinter)

import tkinter as tk
from tkinter import ttk, messagebox

# ---- Базовые таблицы (пример ISO 9001 QMS) ----
# Ключ верхняя граница численности, Значение аудитодни для сертификации (Stage 1+2)
QMS_TABLE = {
    5 1.5,
    10 2,
    15 2.5,
    25 3,
    45 4,
    65 5,
    85 6,
    125 7,
    175 8,
    275 9,
    425 10,
    625 11,
    875 12,
    1175 13,
    1550 14,
    2025 15,
    2675 16,
    3450 17,
    4350 18,
    5450 19,
    6800 20,
    8500 21,
    10700 22
}
# Если численность больше последней границы – продолжаем прогрессию (≈+1 день на следующий диапазон)

def base_days_qms(headcount int) - float
    for limit, days in QMS_TABLE.items()
        if headcount = limit
            return days
    # extrapolation 10700
    extra = (headcount - 10700)  2000 + 1
    return QMS_TABLE[10700] + extra

# ---- Универсальный расчёт ----
def calc_days(standard str, headcount int, complexity str, audit_type str,
              multisite bool, integration bool, factors dict) - float
    # 1. База
    if standard in (ISO 9001, ГОСТ РВ 0015-002)
        days = base_days_qms(headcount)
    else
        # упрощённо берём QMS как основу
        days = base_days_qms(headcount)

    # 2. Сложность  риск
    if complexity == низкая
        days = 0.9
    elif complexity == высокая
        days = 1.2

    # 3. Мультисайт
    if multisite
        days = 1.2  # упрощённо +20%

    # 4. Интеграция
    if integration
        days = 0.85  # упрощённо экономия 15%

    # 5. Факторы
    if factors.get(аутсорсинг)
        days = 1.1
    if factors.get(автоматизация)
        days = 0.9
    if factors.get(разработки)
        days += 0.5
    if factors.get(сменность)
        days += 0.5

    # 6. Тип аудита
    if audit_type == Сертификация
        pass
    elif audit_type == ИК1 or audit_type == ИК2
        days = 0.33
        if days  1
            days = 1
    elif audit_type == Ресертификация
        days = 0.67

    return round(days, 1)

# ---- GUI ----
class AuditApp(tk.Tk)
    def __init__(self)
        super().__init__()
        self.title(Калькулятор аудитодней)
        self.geometry(500x400)

        # Виджеты
        ttk.Label(self, text=Стандарт).pack()
        self.standard = ttk.Combobox(self, values=[ISO 9001, ISO 14001, ISO 45001, ISO 50001, ГОСТ РВ 0015-002])
        self.standard.current(0)
        self.standard.pack()

        ttk.Label(self, text=Численность персонала).pack()
        self.headcount = tk.Entry(self)
        self.headcount.insert(0, 100)
        self.headcount.pack()

        ttk.Label(self, text=Сложностьриск).pack()
        self.complexity = ttk.Combobox(self, values=[низкая, средняя, высокая])
        self.complexity.current(1)
        self.complexity.pack()

        ttk.Label(self, text=Тип аудита).pack()
        self.audit_type = ttk.Combobox(self, values=[Сертификация, ИК1, ИК2, Ресертификация])
        self.audit_type.current(0)
        self.audit_type.pack()

        self.multisite = tk.BooleanVar()
        tk.Checkbutton(self, text=Мультисайт, variable=self.multisite).pack()
        self.integration = tk.BooleanVar()
        tk.Checkbutton(self, text=Интегрированная система, variable=self.integration).pack()

        self.factors = {
            аутсорсинг tk.BooleanVar(),
            автоматизация tk.BooleanVar(),
            разработки tk.BooleanVar(),
            сменность tk.BooleanVar()
        }
        for f in self.factors
            tk.Checkbutton(self, text=f.capitalize(), variable=self.factors[f]).pack()

        ttk.Button(self, text=Рассчитать, command=self.calculate).pack(pady=10)
        self.result = tk.Label(self, text=Результат -)
        self.result.pack()

    def calculate(self)
        try
            hc = int(self.headcount.get())
            days = calc_days(
                self.standard.get(),
                hc,
                self.complexity.get(),
                self.audit_type.get(),
                self.multisite.get(),
                self.integration.get(),
                {k v.get() for k, v in self.factors.items()}
            )
            self.result.config(text=fРезультат {days} аудитодней)
        except Exception as e
            messagebox.showerror(Ошибка, str(e))

if __name__ == __main__
    app = AuditApp()
    app.mainloop()
