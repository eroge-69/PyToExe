#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
free_slots_gui.py — GUI tool to detect free time slots from a noisy Excel schedule.

Build EXE (one-file) with PyInstaller (optional):
    pip install pyinstaller pandas openpyxl
    pyinstaller --noconfirm --onefile --windowed free_slots_gui.py
"""

import re
import sys
import traceback
from datetime import datetime
import pandas as pd

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# روزها به ترتیب نمایش
DAYS_CANON = ["شنبه","یکشنبه","دوشنبه","سه شنبه","چهارشنبه","پنج شنبه"]

# --- نرمال‌سازی متن/اعداد ---

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS  = "٠١٢٣٤٥٦٧٨٩"
EN_DIGITS      = "0123456789"
DIGIT_TRANS = str.maketrans({**{p:e for p,e in zip(PERSIAN_DIGITS, EN_DIGITS)},
                             **{a:e for a,e in zip(ARABIC_DIGITS,  EN_DIGITS)}})

def normalize_text(s: str) -> str:
    """پاک‌سازی نویزهای رایج اکسل، نیم‌فاصله‌ها، و نرمال‌سازی اعداد به انگلیسی"""
    if s is None:
        return ""
    s = str(s)
    s = s.replace("_x000D_", " ").replace("\r", " ").replace("\n", " ")
    s = s.replace("‌", " ")  # zero-width non-joiner -> space
    s = re.sub(r"\s+", " ", s).strip()
    s = s.translate(DIGIT_TRANS)
    # یکنواخت کردن داش‌ها ( - – — )
    s = s.replace("–", "-").replace("—", "-")
    # یکنواخت کردن سه‌شنبه/پنج‌شنبه
    s = s.replace("سه‌شنبه", "سه شنبه").replace("پنج‌شنبه", "پنج شنبه").replace("یک شنبه","یکشنبه")
    return s

def canon_day(d: str) -> str:
    return normalize_text(d)

def time_to_dt(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")

# الگوهای پایه
DAYS_PATTERN = r"(شنبه|یکشنبه|یک شنبه|دوشنبه|سه ?شنبه|سه‌شنبه|چهارشنبه|پنج ?شنبه|پنج‌شنبه)"
TIME_PATTERN = r"(\d{2}:\d{2})\s*تا\s*(\d{2}:\d{2})"
ENTRY_REGEX  = re.compile(DAYS_PATTERN + r"\s+" + TIME_PATTERN)

def looks_like_schedule_text(sample: str) -> int:
    """به هر رشته‌ای که شبیه برنامه‌ی زمانی است امتیاز می‌دهد (برای پیدا کردن ستون مناسب)"""
    s = normalize_text(sample)
    score = 0
    if re.search(DAYS_PATTERN, s):
        score += 2
    if "تا" in s:
        score += 3
    if re.search(r"\d{2}:\d{2}", s):
        score += 3
    # چند ورودی در یک خط؟
    if len(ENTRY_REGEX.findall(s)) >= 2:
        score += 2
    return score

def parse_excel(input_path: str, sheet: str|None=None, column: str|None=None) -> tuple[list[str], list[str], str, str]:
    """
    فایل اکسل را می‌خواند و بهترین ستون متنی را برمی‌گرداند.
    خروجی: (lines, all_columns, used_column, used_sheet)
    """
    try:
        # اگر نام شیت داده شده ولی وجود ندارد، خودکار به اولی فالبک می‌کنیم
        xl = pd.ExcelFile(input_path)
        sheets = xl.sheet_names
        sheet_to_use = sheet if (sheet in sheets) else (sheet if sheet else sheets[0])
        if sheet_to_use not in sheets:
            sheet_to_use = sheets[0]
        df = pd.read_excel(input_path, sheet_name=sheet_to_use)
    except Exception as e:
        raise RuntimeError(f"خطا در باز کردن فایل/شیت: {e}")

    cols = list(df.columns)

    # اگر کاربر ستونی مشخص کرده و موجود است، همان را بگیر؛ وگرنه بهترین ستون را حدس بزن
    if column and column in df.columns:
        used_col = column
    else:
        if not cols:
            raise RuntimeError("ستونی در فایل پیدا نشد.")
        # انتخاب بهترین ستون بر اساس شباهت به متن برنامه‌ی زمانی
        best_col, best_score = cols[0], -1
        for c in cols:
            series = df[c].dropna().astype(str)
            # چند نمونه اول را بررسی کن
            samples = list(series.head(30))
            score = sum(looks_like_schedule_text(x) for x in samples)
            if score > best_score:
                best_col, best_score = c, score
        used_col = best_col

    # استخراج خطوط متنی
    lines = df[used_col].dropna().astype(str).map(normalize_text).tolist()
    return lines, cols, used_col, sheet_to_use

def parse_text_lines(lines: list[str]) -> dict:
    """
    خروجی: {class_name: {day: [(start,end), ...]}}
    قواعد:
      - هر خطی که «تا» داشته باشد، رکورد زمانی است.
      - هر خط غیرخالی که «تا» نداشته باشد و همچنین شامل نام روز نباشد، سربرگ کلاس است.
      - نام کلاس می‌تواند با فاصله یا دش به عدد (مثلاً شماره کلاس/اتاق) ختم شود؛ همان‌طور که هست ذخیره می‌شود.
    """
    classes: dict[str, dict[str, list[tuple[str,str]]]] = {}
    current_class = None

    for raw_line in lines:
        line = normalize_text(raw_line)
        if not line or line.lower() == "(blank)" or line == "Row Labels":
            continue

        has_time = "تا" in line and re.search(r"\d{2}:\d{2}", line)
        has_day  = re.search(DAYS_PATTERN, line) is not None

        # سربرگ کلاس: بدون زمان و بدون نام روز (مثلا: "مهندسی دو-107" یا "مهندسی دو 107")
        if not has_time and not has_day:
            # اگر دوست دارید فقط الگوهای نام-عدد را بپذیرید، این شرط را فعال کنید:
            # if not re.search(r".+\s*-?\s*\d+$", line): continue
            current_class = line
            classes.setdefault(current_class, {})
            continue

        # رکورد زمانی
        if current_class is None:
            # اگر قبلش سربرگ نداشته‌ایم، از این نوع خطوط صرف‌نظر می‌کنیم
            continue

        for m in ENTRY_REGEX.finditer(line):
            day_raw = m.group(1)
            s, e = m.group(2), m.group(3)
            day = canon_day(day_raw)
            classes[current_class].setdefault(day, []).append((s, e))

    return classes

def compute_gaps(classes: dict, start_str: str, end_str: str) -> pd.DataFrame:
    day_start = time_to_dt(start_str)
    day_end   = time_to_dt(end_str)

    rows = []
    for cls, by_day in classes.items():
        for day in DAYS_CANON:
            intervals = by_day.get(day, [])
            ivs = sorted([(time_to_dt(s), time_to_dt(e)) for s, e in intervals], key=lambda x: x[0])
            current = day_start
            for s, e in ivs:
                if s > current:
                    rows.append([cls, day, current.strftime("%H:%M"), s.strftime("%H:%M")])
                if e > current:
                    current = e
            if current < day_end:
                rows.append([cls, day, current.strftime("%H:%M"), day_end.strftime("%H:%M")])
    df = pd.DataFrame(rows, columns=["کلاس","روز","شروع خالی","پایان خالی"])
    if df.empty:
        df = pd.DataFrame(columns=["کلاس","روز","شروع خالی","پایان خالی"])
    return df

def add_durations(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        df = df.copy()
        df["طول (دقیقه)"] = []
        return df
    FMT = "%H:%M"
    df = df.copy()
    df["طول (دقیقه)"] = df.apply(
        lambda r: (datetime.strptime(r["پایان خالی"], FMT) - datetime.strptime(r["شروع خالی"], FMT)).seconds // 60,
        axis=1
    )
    return df

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("پیدا کردن سانس‌های خالی کلاس‌ها (07:30–18:30)")
        self.geometry("1000x640")
        self.minsize(800, 560)

        # State
        self.input_path = tk.StringVar()
        self.sheet_name = tk.StringVar(value="")     # خالی: خودش تشخیص می‌دهد
        self.column_name = tk.StringVar(value="")    # خالی: خودش تشخیص می‌دهد
        self.start_time = tk.StringVar(value="07:30")
        self.end_time   = tk.StringVar(value="18:30")
        self.min_gap    = tk.IntVar(value=31)  # >30 min by default
        self.columns_detected: list[str] = []
        self.sheet_used = ""

        self._build_ui()

        self.df_full = pd.DataFrame()
        self.df_filtered = pd.DataFrame()

    def _build_ui(self):
        pad = {"padx":8, "pady":6}

        top = ttk.LabelFrame(self, text="ورودی")
        top.pack(fill="x", **pad)

        ttk.Label(top, text="فایل اکسل:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.input_path, width=70).grid(row=0, column=1, sticky="we")
        ttk.Button(top, text="انتخاب...", command=self.browse_file).grid(row=0, column=2, sticky="w")

        ttk.Label(top, text="Sheet:").grid(row=1, column=0, sticky="w")
        self.sheet_entry = ttk.Entry(top, textvariable=self.sheet_name, width=20)
        self.sheet_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(top, text="ستون متن:").grid(row=1, column=2, sticky="e")
        self.col_combo = ttk.Combobox(top, textvariable=self.column_name, width=30, values=[])
        self.col_combo.grid(row=1, column=3, sticky="w")

        ttk.Label(top, text="شروع روز:").grid(row=2, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.start_time, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(top, text="پایان روز:").grid(row=2, column=2, sticky="e")
        ttk.Entry(top, textvariable=self.end_time, width=10).grid(row=2, column=3, sticky="w")

        ttk.Label(top, text="حداقل طول خلا (دقیقه):").grid(row=2, column=4, sticky="e")
        ttk.Spinbox(top, from_=0, to=600, textvariable=self.min_gap, width=8).grid(row=2, column=5, sticky="w")

        mid = ttk.Frame(self)
        mid.pack(fill="x", **pad)
        ttk.Button(mid, text="تحلیل و نمایش", command=self.run_analysis).pack(side="left", padx=4)
        ttk.Button(mid, text="ذخیره نتایج (Excel)", command=self.save_excel).pack(side="left", padx=4)
        ttk.Button(mid, text="ذخیره نتایج (TXT)", command=self.save_txt).pack(side="left", padx=4)

        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, **pad)

        cols = ("کلاس","روز","شروع خالی","پایان خالی","طول (دقیقه)")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Status bar
        self.status = tk.StringVar(value="آماده")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=8, pady=4)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="انتخاب فایل اکسل",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not path:
            return
        self.input_path.set(path)
        # تلاش برای خواندن شیت و تشخیص ستون‌ها
        try:
            _, cols, used, used_sheet = parse_excel(path, self.sheet_name.get() or None, self.column_name.get() or None)
            self.columns_detected = cols
            self.col_combo["values"] = cols
            if used not in cols and cols:
                used = cols[0]
            self.column_name.set(used)
            self.sheet_used = used_sheet
            hint_cols = ", ".join(cols[:5]) + ("..." if len(cols) > 5 else "")
            self.status.set(f"فایل خوانده شد. شیت: {used_sheet} | ستون‌ها: {hint_cols}")
        except Exception as e:
            messagebox.showerror("خطا", str(e))
            self.status.set("خطا در خواندن فایل.")

    def run_analysis(self):
        try:
            path = self.input_path.get().strip()
            if not path:
                messagebox.showwarning("هشدار", "اول فایل اکسل را انتخاب کنید.")
                return
            # اعتبارسنجی زمان‌ها (پس از نرمال‌سازی ارقام)
            st, et = normalize_text(self.start_time.get().strip()), normalize_text(self.end_time.get().strip())
            time_to_dt(st); time_to_dt(et)
            if time_to_dt(st) >= time_to_dt(et):
                messagebox.showwarning("هشدار", "زمان شروع باید قبل از زمان پایان باشد.")
                return

            lines, cols, used_col, used_sheet = parse_excel(
                path,
                self.sheet_name.get().strip() or None,
                self.column_name.get().strip() or None
            )
            self.sheet_used = used_sheet

            classes = parse_text_lines(lines)
            df_free = compute_gaps(classes, st, et)
            df_free = add_durations(df_free)

            # فیلتر طول حداقل خلا
            min_gap = int(self.min_gap.get())
            df_filtered = df_free[df_free["طول (دقیقه)"] >= min_gap].reset_index(drop=True)

            self.df_full = df_free
            self.df_filtered = df_filtered

            # پر کردن جدول
            for i in self.tree.get_children():
                self.tree.delete(i)
            for _, r in df_filtered.iterrows():
                self.tree.insert("", "end", values=(r["کلاس"], r["روز"], r["شروع خالی"], r["پایان خالی"], r["طول (دقیقه)"]))

            self.status.set(
                f"انجام شد. کل خلاها: {len(df_free)} | بعد از فیلتر ({min_gap} دقیقه): {len(df_filtered)} | "
                f"شیت: {used_sheet} | ستون: {used_col}"
            )
        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("خطا در تحلیل", f"{e}\n\n{tb}")
            self.status.set("خطا در تحلیل.")

    def save_excel(self):
        if self.df_full is None or self.df_full.empty:
            messagebox.showwarning("هشدار", "ابتدا تحلیل را اجرا کنید.")
            return
        out = filedialog.asksaveasfilename(
            title="ذخیره Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not out:
            return
        try:
            self.df_full.to_excel(out, index=False)
            self.status.set(f"فایل Excel ذخیره شد: {out}")
        except Exception as e:
            messagebox.showerror("خطا", f"ذخیره اکسل ناموفق: {e}")

    def save_txt(self):
        if self.df_filtered is None or self.df_filtered.empty:
            messagebox.showwarning("هشدار", "ابتدا تحلیل را اجرا کنید و حداقل یک خلا بعد از فیلتر داشته باشید.")
            return
        out = filedialog.asksaveasfilename(
            title="ذخیره TXT",
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")]
        )
        if not out:
            return
        try:
            with open(out, "w", encoding="utf-8") as f:
                for _, r in self.df_filtered.iterrows():
                    f.write(f"{r['کلاس']} | {r['روز']} | {r['شروع خالی']} تا {r['پایان خالی']} | {r['طول (دقیقه)']} دقیقه\n")
            self.status.set(f"فایل TXT ذخیره شد: {out}")
        except Exception as e:
            messagebox.showerror("خطا", f"ذخیره TXT ناموفق: {e}")

def main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        # Fallback console error (in case GUI fails to start)
        print("خطای غیرمنتظره:", e, file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

if __name__ == "__main__":
    main()
