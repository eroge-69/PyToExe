import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import codecs

# Всего полей в PNL (A–Q)
TOTAL_FIELDS = 17

# Конвертация мм → дюймы
def mm_to_in(mm: float) -> float:
    return mm / 25.4

# Поиск DXF-файла (рекурсивно), нормализация пути
def find_dxf(base_dir: str, part_name: str) -> str:
    target = part_name.lower() + ".dxf"
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower() == target:
                return os.path.normpath(os.path.join(root, f))
    return ""

# Логирование в текстовый виджет
def log_message(msg: str, level: str="INFO"):
    symbols = {"INFO": "✓", "WARNING": "⚠", "ERROR": "✖"}
    prefix = symbols.get(level, "")
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"{prefix} {msg}\n")
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

# Основная генерация PNL
def generate_pnl():
    # Очистка лога
    log_text.config(state=tk.NORMAL)
    log_text.delete("1.0", tk.END)
    log_text.config(state=tk.DISABLED)

    table_path = table_var.get().strip()
    dxf_dir    = dxf_var.get().strip()
    save_path  = save_var.get().strip()

    # Валидация путей
    if not os.path.isfile(table_path):
        log_message("Ошибка: таблица не найдена", "ERROR")
        return
    if not os.path.isdir(dxf_dir):
        log_message("Ошибка: папка DXF не найдена", "ERROR")
        return
    if not save_path:
        log_message("Ошибка: путь сохранения не задан", "ERROR")
        return

    # Чтение Excel (пропуск первой строки-заголовка)
    try:
        df = pd.read_excel(
            table_path,
            header=0,
            usecols="A:D",
            names=["name","qty","mat","th_mm"],
            skiprows=1
        )
        df = df[df["name"].notna()]
    except Exception as e:
        log_message(f"Ошибка чтения Excel: {e}", "ERROR")
        return

    total_rows = len(df)
    log_message(f"Строк в Excel (без заголовка): {total_rows}", "INFO")

    lines = []
    # Шапка: [HEADER], PNL_fixed, остальные пустые
    header = ["[HEADER]", "PNL_fixed"] + [""] * (TOTAL_FIELDS - 2)
    lines.append("\t".join(header))
    # Три пустые строки
    blank = "\t".join([""] * TOTAL_FIELDS)
    lines.extend([blank] * 3)

    found = missing = 0
    # Перебор строк деталей
    for idx, row in df.iterrows():
        name_raw = str(row["name"]).strip()
        try:
            qty   = int(row["qty"])
            th_mm = float(row["th_mm"])
        except:
            log_message(f"Пропущена строка {idx+2}: некорректные qty/th", "WARNING")
            continue

        mat = str(row["mat"]).strip().upper()[:40]
        th_in = mm_to_in(th_mm)
        dxf_path = find_dxf(dxf_dir, name_raw)
        if not dxf_path:
            log_message(f"DXF не найден: {name_raw}", "WARNING")
            missing += 1
            continue

        base = os.path.splitext(os.path.basename(dxf_path))[0]
        # Поля A–Q (17 полей)
        detail = [
            dxf_path,            # A: путь
            "0",                 # B: тип файла = 0
            str(qty),            # C: количество
            "0.0",               # D: зарезерв
            "5",                 # E: приоритет
            "0.00",              # F: зарезерв
            "0.00",              # G: зарезерв
            "M",                 # H: единицы (мм)
            "0",                 # I: номер детали
            "0",                 # J: зарезерв
            "CADFILE",           # K: источник
            "0",                 # L: зарезерв
            "   ",               # M: три пробела
            base,                # N: имя файла без расшир.
            "0",                 # O: зарезерв
            mat,                 # P: материал (MS/SS/AL)
            f"{th_in:.4f}"       # Q: толщина в дюймах
        ]
        # Дополняем до TOTAL_FIELDS, если нужно
        if len(detail) < TOTAL_FIELDS:
            detail += [""] * (TOTAL_FIELDS - len(detail))

        lines.append("\t".join(detail))
        found += 1

    log_message(f"Успешно добавлено: {found}", "INFO")
    log_message(f"Пропущено (DXF не найден): {missing}", "WARNING")

    # Запись PNL в UTF-16 LE с BOM и CRLF
    try:
        text = "\r\n".join(lines)
        with open(save_path, "wb") as f:
            f.write(codecs.BOM_UTF16_LE)
            f.write(text.encode("utf-16-le"))
        log_message(f"PNL сохранён (UTF-16 LE + BOM): {save_path}", "INFO")
    except Exception as e:
        log_message(f"Ошибка сохранения: {e}", "ERROR")

# Фоновой запуск генерации, чтобы GUI не зависал
def run_generation():
    generate_button.config(state=tk.DISABLED)
    progress.start()
    try:
        generate_pnl()
    finally:
        progress.stop()
        generate_button.config(state=tk.NORMAL)

# --- GUI setup ---
root = tk.Tk()
root.title("Генератор PNL")

table_var = tk.StringVar()
dxf_var   = tk.StringVar()
save_var  = tk.StringVar()

# Исходные данные
input_frame = ttk.LabelFrame(root, text="Исходные данные", padding=10)
input_frame.pack(fill=tk.X, padx=10, pady=5)

def make_row(parent, label, var, cmd, row):
    ttk.Label(parent, text=label, width=25).grid(row=row, column=0, sticky=tk.W, pady=2)
    ttk.Entry(parent, textvariable=var, width=60).grid(row=row, column=1, padx=5)
    ttk.Button(parent, text="...", command=cmd).grid(row=row, column=2)

make_row(input_frame, "Excel (A–D):", table_var,
         lambda: table_var.set(filedialog.askopenfilename(
             title="Выберите Excel-файл", filetypes=[("Excel","*.xlsx;*.xls")])), 0)
make_row(input_frame, "Папка с DXF:", dxf_var,
         lambda: dxf_var.set(filedialog.askdirectory(
             title="Выберите папку DXF")), 1)
make_row(input_frame, "Сохранить PNL:", save_var,
         lambda: save_var.set(filedialog.asksaveasfilename(
             title="Куда сохранить PNL", defaultextension=".pnl",
             filetypes=[("PNL","*.pnl")])), 2)

# Кнопка и прогрессбар
action_frame = ttk.Frame(root, padding=10)
action_frame.pack(fill=tk.X)
generate_button = ttk.Button(
    action_frame,
    text="Сгенерировать PNL",
    command=lambda: threading.Thread(target=run_generation, daemon=True).start()
)
generate_button.pack(side=tk.LEFT)
progress = ttk.Progressbar(action_frame, mode="indeterminate")
progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# Лог
log_frame = ttk.LabelFrame(root, text="Лог сообщений", padding=10)
log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
log_text = tk.Text(log_frame, state=tk.DISABLED, height=12)
log_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
