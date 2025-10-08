#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photoshop Scale Calculator (GUI)
Автор: ChatGPT
Опис: Вводиш поточний розмір шару у %, програма одразу показує:
- що ВВОДИТИ у поле Scale (W/H) у Photoshop,
- множник (у скільки разів),
- приріст у %.
"""

import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Photoshop Scale Calculator"
DEFAULT_PRECISION = 2  # дефолтне округлення для відсотків
MULTIPLIER_PRECISION = 4

def parse_percent(text: str) -> float:
    """
    Приймає рядок з числом (дозволяє кому або крапку),
    повертає float або піднімає ValueError.
    """
    text = text.strip().replace(',', '.')
    if not text:
        raise ValueError("Порожній ввід")
    return float(text)

def calc_values(current_percent: float):
    """
    Розрахунок ключових значень.
    - scale_value: що вводити у поле у Photoshop (у %)
    - multiplier: у скільки разів
    - increase: приріст у %
    """
    if current_percent <= 0:
        raise ValueError("Відсоток має бути > 0")
    multiplier = 100.0 / current_percent
    scale_value = 100.0 * multiplier            # або 10000 / current_percent
    increase = (multiplier - 1.0) * 100.0
    return scale_value, multiplier, increase

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("520x300")
        self.minsize(500, 280)

        # Стиль
        self.style = ttk.Style(self)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")

        # Змінні
        self.var_input = tk.StringVar(value="12,79")
        self.var_scale = tk.StringVar(value="—")
        self.var_multiplier = tk.StringVar(value="—")
        self.var_increase = tk.StringVar(value="—")

        self.precision_percent = tk.IntVar(value=DEFAULT_PRECISION)
        self.precision_multiplier = tk.IntVar(value=MULTIPLIER_PRECISION)

        # Побудова UI
        self._build_ui()

        # Первинний розрахунок
        self.update_results()

    def _build_ui(self):
        pad = 10

        frm_top = ttk.Frame(self, padding=pad)
        frm_top.pack(fill="x")

        lbl_in = ttk.Label(frm_top, text="Поточний розмір шару, %:")
        lbl_in.pack(side="left")

        ent_in = ttk.Entry(frm_top, textvariable=self.var_input, width=15, font=("Segoe UI", 12))
        ent_in.pack(side="left", padx=(8, 8))
        ent_in.bind("<KeyRelease>", lambda e: self.update_results())
        ent_in.bind("<Return>", lambda e: self.update_results())

        btn_calc = ttk.Button(frm_top, text="Розрахувати", command=self.update_results)
        btn_calc.pack(side="left", padx=(0, 8))

        # Параметри округлення
        frm_round = ttk.Frame(self, padding=(pad, 0, pad, pad))
        frm_round.pack(fill="x")

        ttk.Label(frm_round, text="Округлення відсотків:").pack(side="left")
        spn_pct = ttk.Spinbox(frm_round, from_=0, to=4, width=3, textvariable=self.precision_percent, command=self.update_results)
        spn_pct.pack(side="left", padx=(4, 16))

        ttk.Label(frm_round, text="Округлення множника:").pack(side="left")
        spn_mul = ttk.Spinbox(frm_round, from_=0, to=6, width=3, textvariable=self.precision_multiplier, command=self.update_results)
        spn_mul.pack(side="left", padx=(4, 16))

        # Результати
        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=pad, pady=(0, pad))

        frm_results = ttk.Frame(self, padding=pad)
        frm_results.pack(fill="x", expand=True)

        # 1. Що вводити
        row1 = ttk.Frame(frm_results)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="Вводити в поле (W/H):", font=("Segoe UI", 10, "bold")).pack(side="left")
        lbl_scale = ttk.Label(row1, textvariable=self.var_scale, font=("Segoe UI", 11))
        lbl_scale.pack(side="left", padx=(8, 8))
        ttk.Button(row1, text="Скопіювати", command=lambda: self._copy(self.var_scale)).pack(side="left")

        # 2. Множник
        row2 = ttk.Frame(frm_results)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Множник (рази):", font=("Segoe UI", 10, "bold")).pack(side="left")
        lbl_mul = ttk.Label(row2, textvariable=self.var_multiplier, font=("Segoe UI", 11))
        lbl_mul.pack(side="left", padx=(8, 8))
        ttk.Button(row2, text="Скопіювати", command=lambda: self._copy(self.var_multiplier)).pack(side="left")

        # 3. Приріст
        row3 = ttk.Frame(frm_results)
        row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="Приріст:", font=("Segoe UI", 10, "bold")).pack(side="left")
        lbl_inc = ttk.Label(row3, textvariable=self.var_increase, font=("Segoe UI", 11))
        lbl_inc.pack(side="left", padx=(8, 8))
        ttk.Button(row3, text="Скопіювати", command=lambda: self._copy(self.var_increase)).pack(side="left")

        # Низ
        sep2 = ttk.Separator(self, orient="horizontal")
        sep2.pack(fill="x", padx=pad, pady=(pad, 4))

        frm_bottom = ttk.Frame(self, padding=pad)
        frm_bottom.pack(fill="x")
        ttk.Label(
            frm_bottom,
            text="Мнемоніка: що вводити = 10000 / поточний_%.  Приклад: 12,79% → 781,86%.",
            foreground="#555"
        ).pack(side="left")

    def _copy(self, var: tk.StringVar):
        text = var.get()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # потрібно для деяких ОС
        messagebox.showinfo(APP_TITLE, f"Скопійовано: {text}")

    def update_results(self):
        try:
            current = parse_percent(self.var_input.get())
            scale, mul, inc = calc_values(current)

            p_pct = int(self.precision_percent.get())
            p_mul = int(self.precision_multiplier.get())

            # Форматування
            scale_str = f"{scale:.{p_pct}f} %"
            mul_str = f"×{mul:.{p_mul}f}"
            inc_str = f"+{inc:.{p_pct}f} %"

            self.var_scale.set(scale_str)
            self.var_multiplier.set(mul_str)
            self.var_increase.set(inc_str)

        except Exception:
            # Якщо помилка вводу — показуємо тире
            self.var_scale.set("—")
            self.var_multiplier.set("—")
            self.var_increase.set("—")

if __name__ == "__main__":
    app = App()
    app.mainloop()
