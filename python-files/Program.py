import csv
import os
import sys
import json
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# необязательная современная тема (если установлена)
try:
    import sv_ttk
    HAVE_SVTTK = True
except Exception:
    HAVE_SVTTK = False

APP_TITLE = "Учёт доходов • Pro"
DEFAULT_CSV = "Доходы.csv"

CONFIG_PATH = Path("config.json")
DEFAULT_TAX = 4.0  # % по умолчанию

COLUMNS = (
    "Дата",              # dd.mm.yyyy
    "Сумма, ₽",          # без чаевых
    "Чаевые, ₽",
    "Общая, ₽",
    "Налог 4%, ₽",
    "После налога, ₽",
    "Траты, ₽",
    "Чистыми, ₽",
)

# -------------------- Утилиты --------------------
def is_float(s: str) -> bool:
    try:
        float(str(s).replace(" ", "").replace(",", "."))
        return True
    except Exception:
        return False

def parse_money(s: str) -> float:
    return float(str(s).replace("₽", "").replace(" ", "").replace(",", ".") or 0)

def fmt_money(v: float) -> str:
    s = f"{v:,.2f}".replace(",", " ")
    return s

def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

def lerp(a, b, t):
    return tuple(int(aa + (bb - aa) * t) for aa, bb in zip(a, b))


# ==================== Приложение ====================
class IncomeApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)

        self.master.title(APP_TITLE)
        self.master.minsize(1050, 760)

        # состояние
        self.csv_path = Path.cwd() / DEFAULT_CSV
        self.autosave = tk.BooleanVar(value=True)
        self.darkmode = tk.BooleanVar(value=True if HAVE_SVTTK else False)
        self.last_row = None

        # конфиг (налог)
        self.tax_percent = tk.DoubleVar(value=self._load_tax())

        # итоги
        self.sum_after_tax_var = tk.StringVar(value="0.00")
        self.sum_net_var = tk.StringVar(value="0.00")
        self.banner_total_var = tk.StringVar(value="0.00")

        # undo
        self._undo_stack = None   # (date, row_dict)
        self._undo_toast = None

        # баннер-цвета (нейтральные, без синего)
        self.banner_bg_light = "#F3F4F6"   # светло-серый
        self.banner_bg_dark  = "#1f2937"   # тёмно-серый
        self.banner_fg_light = "#111827"
        self.banner_fg_dark  = "#E5E7EB"
        self.flash_light     = "#FFF4CE"   # мягкая вспышка
        self.flash_dark      = "#3d2e12"

        self._build_ui()
        self._load_table()
        self._apply_theme(initial=True)

        # хоткеи
        self.master.bind("<Return>", lambda e: self.calculate())
        self.master.bind("<Delete>", lambda e: self.delete_selected())
        self.master.bind("<Control-s>", lambda e: self.save_now())
        self.master.bind("<Control-S>", lambda e: self.save_now())
        self.master.bind("<Control-z>", lambda e: self.undo_delete())
        self.master.bind("<Control-Z>", lambda e: self.undo_delete())

        # обработчик закрытия (сохраняем конфиг)
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

    # -------------------- UI --------------------
    def _build_ui(self):
        default_font = ("Segoe UI", 10)
        title_font   = ("Segoe UI Semibold", 18)
        banner_font  = ("Segoe UI Semibold", 22)

        self.master.option_add("*Font", default_font)

        # ===== Топ-бар =====
        topbar = ttk.Frame(self)
        topbar.pack(fill="x", pady=(0, 10))

        title = ttk.Label(topbar, text="Учёт доходов", font=title_font)
        title.pack(side="left")

        # Баннер «Всего чистыми»
        banner = tk.Frame(topbar, bd=0, highlightthickness=0)
        banner.pack(side="right")
        self.banner_frame = tk.Frame(banner, bd=0)
        self.banner_frame.pack()
        self.banner_caption = tk.Label(self.banner_frame, text="Всего чистыми", font=("Segoe UI", 10))
        self.banner_value = tk.Label(self.banner_frame, textvariable=self.banner_total_var, font=banner_font)
        self.banner_caption.grid(row=0, column=0, sticky="e")
        self.banner_value.grid(row=1, column=0, sticky="e")

        # ===== Файл/настройки =====
        header = ttk.LabelFrame(self, text="Файл отчёта")
        header.pack(fill="x", pady=(0, 10))

        self.path_var = tk.StringVar(value=str(self.csv_path))
        ttk.Entry(header, textvariable=self.path_var, state="readonly").grid(row=0, column=0, sticky="we", padx=6, pady=8)
        header.grid_columnconfigure(0, weight=1)

        ttk.Button(header, text="Выбрать файл…", command=self.choose_file).grid(row=0, column=1, padx=4, pady=8)
        ttk.Button(header, text="Открыть файл", command=self.open_file).grid(row=0, column=2, padx=4, pady=8)

        ttk.Checkbutton(header, text="Автосохранение", variable=self.autosave).grid(row=1, column=0, sticky="w", padx=6, pady=(0, 8))
        ttk.Button(header, text="Сохранить сейчас", command=self.save_now).grid(row=1, column=2, padx=4, pady=(0, 8))
        ttk.Checkbutton(header, text="Тёмная тема", variable=self.darkmode, command=self._apply_theme).grid(row=1, column=1, sticky="e", padx=4, pady=(0, 8))

        # ===== Фильтр периода =====
        filters = ttk.LabelFrame(self, text="Фильтр")
        filters.pack(fill="x", pady=(0, 10))

        ttk.Label(filters, text="Месяц:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.cb_month = ttk.Combobox(filters, values=[f"{i:02d}" for i in range(1, 13)], width=6, state="readonly")
        self.cb_month.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(filters, text="Год:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.cb_year = ttk.Combobox(filters, values=[str(y) for y in range(2020, 2036)], width=8, state="readonly")
        self.cb_year.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        ttk.Button(filters, text="Показать период", command=self.apply_period_filter).grid(row=0, column=4, padx=6, pady=6)
        ttk.Button(filters, text="Сброс", command=self.reset_filter).grid(row=0, column=5, padx=6, pady=6)

        for i in range(6):
            filters.grid_columnconfigure(i, weight=1)

        # ===== Ввод =====
        inputs = ttk.LabelFrame(self, text="Ввод данных")
        inputs.pack(fill="x", pady=(0, 10))

        ttk.Label(inputs, text="Дата (дд.мм.гггг):").grid(row=0, column=0, sticky="w", padx=6, pady=8)
        self.e_date = ttk.Entry(inputs, width=16)
        self.e_date.grid(row=0, column=1, padx=6, pady=8, sticky="w")

        ttk.Label(inputs, text="Сумма за сегодня (₽):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.e_sum = ttk.Entry(inputs, width=16)
        self.e_sum.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(inputs, text="Чаевые (₽):").grid(row=1, column=2, sticky="w", padx=6, pady=6)
        self.e_tip = ttk.Entry(inputs, width=16)
        self.e_tip.grid(row=1, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(inputs, text="Налог, %:").grid(row=1, column=4, sticky="w", padx=6, pady=6)
        self.e_tax = ttk.Spinbox(inputs, from_=0, to=30, increment=0.5, width=8, textvariable=self.tax_percent)
        self.e_tax.grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ttk.Button(inputs, text="Рассчитать (Enter)", command=self.calculate).grid(row=2, column=0, columnspan=6, sticky="we", padx=6, pady=(4, 8))
        for col_i in range(6):
            inputs.grid_columnconfigure(col_i, weight=1)

        # ===== Результаты =====
        self.result_lbl = ttk.Label(self, anchor="w")
        self.result_lbl.pack(fill="x", pady=(0, 6))

        # ===== Траты =====
        exp = ttk.LabelFrame(self, text="Траты")
        exp.pack(fill="x", pady=(0, 10))

        ttk.Label(exp, text="Сумма трат (₽):").grid(row=0, column=0, sticky="w", padx=6, pady=8)
        self.e_exp = ttk.Entry(exp, width=16)
        self.e_exp.grid(row=0, column=1, padx=6, pady=8, sticky="w")
        ttk.Button(exp, text="Учесть траты", command=self.apply_expenses).grid(row=0, column=2, padx=6, pady=8)

        self.exp_lbl = ttk.Label(self, anchor="w")
        self.exp_lbl.pack(fill="x", pady=(0, 6))

        # ===== Таблица =====
        table_box = ttk.LabelFrame(self, text="Отчёт")
        table_box.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_box, columns=COLUMNS, show="headings", height=16)
        for col in COLUMNS:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c, False))
            width = 130
            if col == "Дата":
                width = 120
            self.tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        # ===== Кнопки под таблицей =====
        table_actions = ttk.Frame(self)
        table_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(table_actions, text="Удалить выбранную дату", command=self.delete_selected).pack(side="left", padx=6)

        # ===== Сводка =====
        summary = ttk.Frame(self)
        summary.pack(fill="x", pady=(8, 0))
        ttk.Label(summary, text="Σ После налога, ₽:").grid(row=0, column=0, sticky="w", padx=6)
        ttk.Label(summary, textvariable=self.sum_after_tax_var).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(summary, text="Σ Чистыми, ₽:").grid(row=0, column=2, sticky="w", padx=14)
        ttk.Label(summary, textvariable=self.sum_net_var).grid(row=0, column=3, sticky="w", padx=6)

        # ===== Статус =====
        self.status = tk.StringVar(value="Готово")
        ttk.Label(self, textvariable=self.status, anchor="w", foreground="#6a6a6a").pack(fill="x", pady=(6, 0))

    # -------------------- Тема --------------------
    def _apply_theme(self, initial=False):
        if HAVE_SVTTK:
            sv_ttk.set_theme("dark" if self.darkmode.get() else "light")
            dark = self.darkmode.get()
        else:
            style = ttk.Style()
            try:
                style.theme_use("clam")
            except Exception:
                pass
            dark = False

        # Баннер (нейтральные цвета)
        bg = self.banner_bg_dark if dark else self.banner_bg_light
        fg = self.banner_fg_dark if dark else self.banner_fg_light
        for w in (self.banner_frame,):
            w.configure(bg=bg)
        for w in (self.banner_caption, self.banner_value):
            w.configure(bg=bg, fg=fg)

        if not initial:
            self.update_idletasks()

    # -------------------- Анимация баннера --------------------
    def _flash_banner(self, duration_ms=500, steps=12):
        dark = self.darkmode.get() if HAVE_SVTTK else False
        base_bg = self.banner_bg_dark if dark else self.banner_bg_light
        flash_bg = self.flash_dark if dark else self.flash_light
        base_rgb = hex_to_rgb(base_bg)
        flash_rgb = hex_to_rgb(flash_bg)

        seq = list(range(steps)) + list(range(steps, -1, -1))
        def step_anim(i=0):
            if i >= len(seq):
                # вернули базовый
                for w in (self.banner_frame,):
                    w.configure(bg=base_bg)
                for w in (self.banner_caption, self.banner_value):
                    w.configure(bg=base_bg)
                return
            t = seq[i] / steps
            cur_hex = rgb_to_hex(lerp(base_rgb, flash_rgb, t))
            self.banner_frame.configure(bg=cur_hex)
            self.banner_caption.configure(bg=cur_hex)
            self.banner_value.configure(bg=cur_hex)
            self.after(max(1, duration_ms // len(seq)), lambda: step_anim(i + 1))
        step_anim(0)

    # -------------------- Конфиг --------------------
    def _load_tax(self) -> float:
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                return float(data.get("tax", DEFAULT_TAX))
            except Exception:
                return DEFAULT_TAX
        return DEFAULT_TAX

    def _save_tax(self):
        try:
            CONFIG_PATH.write_text(json.dumps({"tax": float(self.tax_percent.get())}, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _on_close(self):
        self._save_tax()
        self.master.destroy()

    # -------------------- Логика расчёта --------------------
    def calculate(self):
        dt = self.e_date.get().strip()
        s = self.e_sum.get().strip()
        t = self.e_tip.get().strip() or "0"
        tax_rate = float(self.tax_percent.get()) / 100.0

        # дата
        try:
            datetime.strptime(dt, "%d.%m.%Y")
        except Exception:
            messagebox.showerror("Ошибка", "Введите дату в формате дд.мм.гггг")
            return

        if not is_float(s) or not is_float(t):
            messagebox.showerror("Ошибка", "Сумма и Чаевые должны быть числами.")
            return

        summa = round(float(s.replace(",", ".")), 2)
        tips = round(float(t.replace(",", ".")), 2)
        total = round(summa + tips, 2)
        tax = round(total * tax_rate, 2)
        after_tax = round(total - tax, 2)

        existing = self._find_by_date(dt)
        expenses = parse_money(existing.get("Траты, ₽", 0)) if existing else 0.0
        net = round(after_tax - expenses, 2)

        self.last_row = {
            "Дата": dt,
            "Сумма, ₽": f"{summa:.2f}",
            "Чаевые, ₽": f"{tips:.2f}",
            "Общая, ₽": f"{total:.2f}",
            "Налог 4%, ₽": f"{tax:.2f}",
            "После налога, ₽": f"{after_tax:.2f}",
            "Траты, ₽": f"{expenses:.2f}",
            "Чистыми, ₽": f"{net:.2f}",
        }

        self.result_lbl.config(
            text=(
                f"Дата: {dt}  |  Доход: {summa:.2f} ₽  + Чаевые: {tips:.2f} ₽  → Общая: {total:.2f} ₽  "
                f"→ Налог {self.tax_percent.get():.1f}%: {tax:.2f} ₽  → После налога: {after_tax:.2f} ₽"
            )
        )
        self.exp_lbl.config(text=f"Траты: {expenses:.2f} ₽  → Чистыми: {net:.2f} ₽")

        if self.autosave.get():
            self._upsert_row(self.last_row)
            self.status.set(f"Автосохранено → {self.csv_path.name}")

    def apply_expenses(self):
        if not self.last_row:
            messagebox.showwarning("Внимание", "Сначала рассчитайте доход.")
            return

        e = self.e_exp.get().strip()
        if not is_float(e):
            messagebox.showerror("Ошибка", "Введите число в поле «Траты».")
            return

        expenses = round(float(e.replace(",", ".")), 2)
        after_tax = parse_money(self.last_row["После налога, ₽"])
        net = round(after_tax - expenses, 2)

        self.last_row["Траты, ₽"] = f"{expenses:.2f}"
        self.last_row["Чистыми, ₽"] = f"{net:.2f}"

        self.exp_lbl.config(text=f"Траты: {expenses:.2f} ₽  → Чистыми: {net:.2f} ₽")

        if self.autosave.get():
            self._upsert_row(self.last_row)
            self.status.set(f"Автосохранено → {self.csv_path.name}")

    # -------------------- Удаление / Undo --------------------
    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Удаление", "Выберите строку в таблице, которую нужно удалить.")
            return
        item_id = sel[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return
        dt = values[0]  # первая колонка — Дата

        if messagebox.askyesno("Подтверждение", f"Удалить запись за дату {dt}?"):
            rows = self._read_csv()
            deleted_row = None
            new_rows = []
            for r in rows:
                if r.get("Дата") == dt and deleted_row is None:
                    deleted_row = r
                    continue
                new_rows.append(r)

            self._write_csv(new_rows)
            self._reload_tree_from(new_rows)
            self.status.set(f"Удалено: {dt}")

            if self.last_row and self.last_row.get("Дата") == dt:
                self.last_row = None

            # сохранить для undo
            self._undo_stack = (dt, deleted_row)
            self._show_undo_toast(dt)

    def _show_undo_toast(self, dt):
        # компактная плашка снизу
        self._safe_close_toast()
        toast = tk.Toplevel(self)
        self._undo_toast = toast
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg="#222222")
        msg = tk.Label(toast, text=f"Удалено {dt}. Отменить?", fg="white", bg="#222222", padx=12, pady=6)
        msg.pack(side="left")
        btn = tk.Button(toast, text="Undo", command=self.undo_delete, bg="#444444", fg="white", relief="flat", padx=10)
        btn.pack(side="left", padx=6)

        self.update_idletasks()
        x = self.master.winfo_rootx() + self.master.winfo_width() - 260
        y = self.master.winfo_rooty() + self.master.winfo_height() - 80
        toast.geometry(f"250x40+{x}+{y}")

        toast.after(8000, self._safe_close_toast)

    def _safe_close_toast(self):
        try:
            if self._undo_toast is not None:
                self._undo_toast.destroy()
        except Exception:
            pass
        self._undo_toast = None

    def undo_delete(self):
        if not self._undo_stack:
            return
        dt, row = self._undo_stack
        rows = self._read_csv()

        # если уже есть запись за дату — заменим
        replaced = False
        for i, r in enumerate(rows):
            if r.get("Дата") == dt:
                rows[i] = row
                replaced = True
                break
        if not replaced and row:
            rows.append(row)

        self._write_csv(rows)
        self._reload_tree_from(rows)
        self.status.set(f"Восстановлено: {dt}")
        self._undo_stack = None
        self._safe_close_toast()

    # -------------------- Фильтры --------------------
    def apply_period_filter(self):
        rows = self._read_csv()
        m = (self.cb_month.get() or "").strip()
        y = (self.cb_year.get() or "").strip()
        if not m and not y:
            self._reload_tree_from(rows)
            self.status.set("Фильтр: нет")
            return
        out = []
        for r in rows:
            dt = r.get("Дата", "")
            parts = dt.split(".")
            if len(parts) == 3:
                dd, mm, yy = parts
                if (not m or mm == m) and (not y or yy == y):
                    out.append(r)
        self._reload_tree_from(out)
        self.status.set(f"Фильтр: месяц={m or '*'}, год={y or '*'}")

    def reset_filter(self):
        self.cb_month.set("")
        self.cb_year.set("")
        self._load_table()
        self.status.set("Фильтр сброшен")

    # -------------------- Файл --------------------
    def choose_file(self):
        fname = filedialog.asksaveasfilename(
            title="Выберите CSV-файл",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
            initialfile=self.csv_path.name,
            initialdir=str(self.csv_path.parent),
        )
        if not fname:
            return
        self.csv_path = Path(fname)
        self.path_var.set(str(self.csv_path))
        self.status.set(f"Файл выбран: {self.csv_path.name}")
        self._load_table()

    def open_file(self):
        if not self.csv_path.exists():
            messagebox.showwarning("Файл не найден", f"Файл «{self.csv_path.name}» пока не создан.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.csv_path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{self.csv_path}"')
            else:
                os.system(f'xdg-open "{self.csv_path}"')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_now(self):
        if not self.last_row:
            messagebox.showwarning("Внимание", "Нет данных для сохранения. Сначала «Рассчитать».")
            return
        self._upsert_row(self.last_row)
        self.status.set(f"Сохранено → {self.csv_path.name}")

    # -------------------- CSV & Таблица --------------------
    def _load_table(self):
        self.tree.delete(*self.tree.get_children())
        rows = self._read_csv()
        for r in rows:
            self.tree.insert("", "end", values=[r.get(col, "") for col in COLUMNS])
        self._update_summary(rows)

    def _read_csv(self):
        rows = []
        if not self.csv_path.exists():
            return rows
        try:
            with self.csv_path.open("r", encoding="utf-8", newline="") as f:
                rd = csv.reader(f, delimiter=";")
                header = None
                for i, line in enumerate(rd):
                    if not line:
                        continue
                    if i == 0 and set(line) >= set(COLUMNS):
                        header = line
                        continue
                    if header and len(line) == len(header):
                        d = dict(zip(header, line))
                    else:
                        d = dict(zip(COLUMNS, line[:len(COLUMNS)]))
                    rows.append(d)
        except Exception as e:
            messagebox.showerror("Ошибка чтения CSV", str(e))
        return rows

    def _write_csv(self, rows):
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.csv_path.open("w", encoding="utf-8", newline="") as f:
                wr = csv.writer(f, delimiter=";")
                wr.writerow(COLUMNS)
                for r in rows:
                    wr.writerow([r.get(col, "") for col in COLUMNS])
        except Exception as e:
            messagebox.showerror("Ошибка записи CSV", str(e))

    def _upsert_row(self, row_dict):
        rows = self._read_csv()
        replaced = False
        for i, r in enumerate(rows):
            if r.get("Дата") == row_dict["Дата"]:
                rows[i] = row_dict
                replaced = True
                break
        if not replaced:
            rows.append(row_dict)

        self._write_csv(rows)
        self._reload_tree_from(rows)

    def _reload_tree_from(self, rows):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=[r.get(col, "") for col in COLUMNS])
        self._update_summary(rows)

    def _find_by_date(self, date_str):
        for r in self._read_csv():
            if r.get("Дата") == date_str:
                return r
        return None

    def _update_summary(self, rows):
        def fsum(key) -> float:
            return sum(parse_money(r.get(key, 0)) for r in rows)

        total_after_tax = fsum("После налога, ₽")
        total_net = fsum("Чистыми, ₽")

        self.sum_after_tax_var.set(fmt_money(total_after_tax))
        self.sum_net_var.set(fmt_money(total_net))
        self.banner_total_var.set(fmt_money(total_net))

        # мягко подсветим баннер при каждом обновлении
        self._flash_banner()

    # -------------------- Сортировка --------------------
    def _sort_by(self, col, desc):
        data = [(self.tree.item(iid, "values"), iid) for iid in self.tree.get_children("")]
        col_idx = COLUMNS.index(col)

        def keyfn(v):
            s = str(v[0][col_idx])
            try:
                return parse_money(s)
            except Exception:
                if col == "Дата" and len(s.split(".")) == 3:
                    dd, mm, yy = s.split(".")
                    return yy + mm + dd
                return s

        data.sort(key=keyfn, reverse=desc)
        for idx, (_, iid) in enumerate(data):
            self.tree.move(iid, "", idx)
        self.tree.heading(col, command=lambda c=col: self._sort_by(c, not desc))


# ==================== Точка входа ====================
def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    if HAVE_SVTTK:
        sv_ttk.set_theme("dark")
    app = IncomeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
