import requests
import time
import json
from datetime import datetime, timedelta
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from openpyxl import Workbook

CONFIG_FILE = "config.json"
BASE_URL = "https://market.csgo.com/api/v2/operation-history"

last_clicked_item = None
items_cache = []           # кэш строк (для фильтра и сортировки)
sort_state = {}            # {col_index: reverse_bool}
auto_job_id = None         # id запланированной задачи .after


# ===== Работа с конфигом =====
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(api_key: str):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key}, f)
    except Exception as e:
        print(f"Ошибка сохранения API ключа: {e}")


# ===== API =====
def check_api_key(key: str) -> bool:
    """Проверяем API ключ простым запросом."""
    try:
        params = {"key": key, "date": int(time.time()) - 3600, "date_end": int(time.time())}
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
        return data.get("success", False)
    except Exception:
        return False


def get_sold_items(api_key: str, start_ts: int, end_ts: int):
    """История продаж (только УСПЕШНЫЕ сделки)."""
    params = {"key": api_key, "date": start_ts, "date_end": end_ts}
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data}")

    def to_int(x, default=0):
        try:
            return int(x)
        except (TypeError, ValueError):
            return default

    filtered = []
    for op in data.get("data", []):
        if op.get("event") != "sell":
            continue
        settlement = to_int(op.get("settlement"), 0)
        stage = str(op.get("stage"))
        # Успешные продажи: факт передачи предмета/расчёт
        if settlement > 0 or stage == "2":
            filtered.append(op)

    return filtered


# ===== Рендер таблицы из кэша =====
def render_table():
    """Перерисовывает таблицу из items_cache с учётом фильтра."""
    filter_text = entry_filter.get().strip().lower()
    # очистка таблицы
    for row in tree.get_children():
        tree.delete(row)

    total_received = 0.0
    for i, row in enumerate(items_cache):
        # row = (ts_str, name, price_str, received_str)
        if filter_text and filter_text not in row[1].lower():
            continue
        tag = "oddrow" if i % 2 == 0 else "evenrow"
        tree.insert("", "end", values=row, tags=(tag,))
        try:
            total_received += float(row[3])
        except:
            pass

    label_total.config(text=f"Итого: {total_received:.2f} ₽")


# ===== Загрузка данных =====
def load_data():
    """Загрузка и отображение данных в таблице."""
    global items_cache
    api_key = entry_key.get().strip()
    if not check_api_key(api_key):
        Messagebox.show_error("Неверный API ключ", "Ошибка")
        return
    save_config(api_key)  # сохраняем ключ

    try:
        start_date = entry_start.entry.get()
        end_date = entry_end.entry.get()

        start_h = int(spin_start_h.get())
        start_m = int(spin_start_m.get())
        end_h = int(spin_end_h.get())
        end_m = int(spin_end_m.get())

        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=start_h, minute=start_m)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=end_h, minute=end_m)

        start_ts = int(time.mktime(start_dt.timetuple()))
        end_ts = int(time.mktime(end_dt.timetuple()))

        items = get_sold_items(api_key, start_ts, end_ts)

        # заполняем кэш строк
        items_cache = []
        for op in items:
            ts_str = datetime.fromtimestamp(int(op["time"])).strftime("%Y-%m-%d %H:%M:%S")
            name = op.get("market_hash_name", "")
            price = int(op.get("price", 0)) / 100
            received = int(op.get("received", 0)) / 100
            items_cache.append((ts_str, name, f"{price:.2f}", f"{received:.2f}"))

        # перерисовка
        render_table()

    except Exception as e:
        Messagebox.show_error(str(e), "Ошибка")


# ===== Экспорт =====
def export_to_excel():
    """Экспорт ВИДИМЫХ строк таблицы в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Продажи"
    ws.append(["Дата", "Название", "Цена", "Цена с комиссией"])

    for row_id in tree.get_children():
        ws.append(tree.item(row_id, "values"))

    filename = "sales.xlsx"
    wb.save(filename)
    Messagebox.show_info(f"Данные сохранены в {filename}", "Экспорт")


# ===== Сумма по выделенным =====
def calc_selected_sum(event=None):
    """Считает сумму по выделенным строкам (колонка 'Цена с комиссией')."""
    selected = tree.selection()
    total = 0.0
    for item in selected:
        values = tree.item(item, "values")
        if values and len(values) >= 4:
            try:
                total += float(values[3])
            except ValueError:
                pass
    label_selected.config(text=f"Выбрано: {total:.2f} ₽")


# ===== Фильтр =====
def apply_filter(event=None):
    render_table()


# ===== Сортировка =====
def sort_by_column(col_index):
    """Сортировка кэша по колонке с перерисовкой."""
    reverse = sort_state.get(col_index, False)

    def try_num(x):
        try:
            return float(x.replace(",", "."))
        except Exception:
            return x

    items_cache.sort(key=lambda row: try_num(row[col_index]), reverse=reverse)
    sort_state[col_index] = not reverse
    render_table()


# ===== Выделение строк (как Excel) =====
def on_treeview_click(event):
    """Начало выделения."""
    global last_clicked_item
    current_item = tree.identify_row(event.y)
    if not current_item:
        return

    # Ctrl — стандартное поведение (добавляет/снимает выделение)
    if event.state & 0x4:
        return

    # Shift — диапазон от last_clicked_item до текущего
    if event.state & 0x1:
        if last_clicked_item:
            all_items = tree.get_children()
            start_idx = all_items.index(last_clicked_item)
            end_idx = all_items.index(current_item)
            tree.selection_set(all_items[min(start_idx, end_idx):max(start_idx, end_idx) + 1])
    else:
        # обычный ЛКМ — начинаем новое выделение
        tree.selection_set([current_item])
        last_clicked_item = current_item


def on_treeview_drag(event):
    """Протягивание ЛКМ — выделение диапазона."""
    global last_clicked_item
    current_item = tree.identify_row(event.y)
    if not current_item or not last_clicked_item:
        return
    all_items = tree.get_children()
    start_idx = all_items.index(last_clicked_item)
    end_idx = all_items.index(current_item)
    tree.selection_set(all_items[min(start_idx, end_idx):max(start_idx, end_idx) + 1])


# ===== Автообновление =====
def schedule_auto_update():
    """Запускает/останавливает автообновление по галочке."""
    global auto_job_id
    if auto_var.get():
        # включили автообновление
        minutes = 0
        try:
            minutes = int(spin_interval.get())
        except:
            minutes = 1
        minutes = max(1, minutes)
        # Если есть существующая задача — отменяем
        if auto_job_id is not None:
            app.after_cancel(auto_job_id)
            auto_job_id = None

        def tick():
            global auto_job_id
            load_data()
            auto_job_id = app.after(minutes * 60 * 1000, tick)

        auto_job_id = app.after(0, tick)
    else:
        # выключили автообновление
        if auto_job_id is not None:
            app.after_cancel(auto_job_id)
            auto_job_id = None


# ===== GUI =====
app = tb.Window(themename="superhero")
app.title("CS2 Market Продажи")
app.geometry("1180x760")

# --- API ключ ---
frame_key = tb.Frame(app)
frame_key.pack(pady=10, padx=10, fill="x")

tb.Label(frame_key, text="API Key:").pack(side="left", padx=5)
entry_key = tb.Entry(frame_key, width=60, bootstyle="info")
entry_key.pack(side="left", padx=5)

btn_check = tb.Button(frame_key, text="Проверить", bootstyle="secondary-outline", command=lambda: (
    save_config(entry_key.get().strip()),
    Messagebox.show_info("API ключ действителен ✅", "Успех") if check_api_key(entry_key.get().strip())
    else Messagebox.show_error("Неверный API ключ ❌", "Ошибка")
))
btn_check.pack(side="left", padx=5)

# Загружаем сохранённый ключ
cfg = load_config()
if "api_key" in cfg:
    entry_key.insert(0, cfg["api_key"])

# --- Период ---
frame_top = tb.Labelframe(app, text="Выбор периода", bootstyle="primary")
frame_top.pack(pady=10, padx=10, fill="x")

tb.Label(frame_top, text="Начало:").grid(row=0, column=0, padx=5, pady=5)
entry_start = tb.DateEntry(frame_top, bootstyle="info", dateformat="%Y-%m-%d")
entry_start.grid(row=0, column=1, padx=5)

spin_start_h = tb.Spinbox(frame_top, from_=0, to=23, width=3)
spin_start_h.grid(row=0, column=2)
spin_start_m = tb.Spinbox(frame_top, from_=0, to=59, width=3)
spin_start_m.grid(row=0, column=3)

tb.Label(frame_top, text="Конец:").grid(row=0, column=4, padx=5, pady=5)
entry_end = tb.DateEntry(frame_top, bootstyle="info", dateformat="%Y-%m-%d")
entry_end.grid(row=0, column=5, padx=5)
spin_end_h = tb.Spinbox(frame_top, from_=0, to=23, width=3)
spin_end_h.grid(row=0, column=6)
spin_end_m = tb.Spinbox(frame_top, from_=0, to=59, width=3)
spin_end_m.grid(row=0, column=7)

btn_load = tb.Button(frame_top, text="Загрузить", bootstyle="success", command=load_data)
btn_load.grid(row=0, column=8, padx=10)

# Значения по умолчанию: время и даты
today = datetime.today()
week_ago = today - timedelta(days=7)

entry_start.entry.delete(0, "end")
entry_start.entry.insert(0, week_ago.strftime("%Y-%m-%d"))
spin_start_h.delete(0, "end"); spin_start_h.insert(0, "00")
spin_start_m.delete(0, "end"); spin_start_m.insert(0, "00")

entry_end.entry.delete(0, "end")
entry_end.entry.insert(0, today.strftime("%Y-%m-%d"))
spin_end_h.delete(0, "end"); spin_end_h.insert(0, "23")
spin_end_m.delete(0, "end"); spin_end_m.insert(0, "59")

# --- Фильтр ---
frame_filter = tb.Frame(app)
frame_filter.pack(fill="x", padx=10, pady=5)

tb.Label(frame_filter, text="Фильтр по названию:").pack(side="left", padx=5)
entry_filter = tb.Entry(frame_filter, width=40, bootstyle="info")
entry_filter.pack(side="left", padx=5)
entry_filter.bind("<KeyRelease>", apply_filter)

# --- Таблица ---
frame_table = tb.Frame(app)
frame_table.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Дата", "Название", "Цена", "Цена с комиссией")
tree = tb.Treeview(
    frame_table,
    columns=columns,
    show="headings",
    height=22,
    bootstyle="info",
    selectmode="extended"
)

# заголовки + сортировка
for idx, col in enumerate(columns):
    tree.heading(col, text=col, command=lambda i=idx: sort_by_column(i))
    tree.column(col, anchor="center", width=220 if col != "Название" else 400, stretch=True)

tree.tag_configure("oddrow", background="#2c2f33")
tree.tag_configure("evenrow", background="#23272a")

# Скроллбар
scrollbar = tb.Scrollbar(frame_table, orient="vertical", command=tree.yview, bootstyle="round-success")
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

# --- Итоги + Экспорт + Автообновление ---
frame_bottom = tb.Frame(app)
frame_bottom.pack(fill="x", padx=10, pady=8)

btn_export = tb.Button(frame_bottom, text="Экспорт в Excel (XLSX)", bootstyle="info-outline", command=export_to_excel)
btn_export.pack(side="left", padx=5)

# автообновление
auto_var = tb.BooleanVar(value=False)
chk_auto = tb.Checkbutton(frame_bottom, text="Обновлять каждые", variable=auto_var, command=schedule_auto_update, bootstyle="success-round-toggle")
chk_auto.pack(side="left", padx=(15, 5))

spin_interval = tb.Spinbox(frame_bottom, from_=1, to=1440, width=5)
spin_interval.pack(side="left")
spin_interval.delete(0, "end"); spin_interval.insert(0, "5")  # по умолчанию каждые 5 минут
tb.Label(frame_bottom, text="мин.").pack(side="left", padx=(5, 15))

label_selected = tb.Label(
    frame_bottom, text="Выбрано: 0 ₽",
    anchor="e", font=("Arial", 12, "bold"),
    bootstyle="info"
)
label_selected.pack(side="left")

label_total = tb.Label(
    frame_bottom, text="Итого: 0 ₽",
    anchor="e", font=("Arial", 14, "bold"),
    bootstyle="success"
)
label_total.pack(side="right")

# события
tree.bind("<Button-1>", on_treeview_click)
tree.bind("<B1-Motion>", on_treeview_drag)
tree.bind("<<TreeviewSelect>>", calc_selected_sum)

app.mainloop()
