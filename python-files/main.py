import os
import sys
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from cefpython3 import cefpython as cef
from openpyxl import load_workbook
from datetime import datetime
from PIL import Image, ImageTk
import folium
import shutil
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMSI_DIR = os.path.join(BASE_DIR, "data", "imsi")
HTML_DIR = os.path.join(BASE_DIR, "html")
MAP_PATH = os.path.join(HTML_DIR, "karakalpakstan_detailed_map.html")
TEMP_MAP_PATH = os.path.join(HTML_DIR, "temp_map.html")
MAP_URL = "file:///" + MAP_PATH.replace("\\", "/")
TEMP_MAP_URL = "file:///" + TEMP_MAP_PATH.replace("\\", "/")
DB_FILE = os.path.join(BASE_DIR, "locations.json")

os.makedirs(IMSI_DIR, exist_ok=True)
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f, indent=2)

class App:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap("logo.ico")
        self.root.title("Анализ преступлений")
        self.root.geometry("1200x700")
        self.left = tk.Frame(self.root, width=250, height=700, bg="#eeeeee")
        self.left.pack(side=tk.LEFT, fill=tk.Y)
        self.right = tk.Frame(self.root)
        self.right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.dynamic_frame = None

        # Загрузка и вставка логотипа
        logo_path = os.path.join(BASE_DIR, "лого.png")  # Убедись, что имя файла совпадает
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((100, 100))  # Можешь изменить размер
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.left, image=self.logo_photo, bg="#eeeeee")
            logo_label.pack(pady=10)


        ttk.Button(self.left, text="Добавить преступление", command=self.add_crime).pack(pady=5)
        ttk.Button(self.left, text="Фильтр по времени", command=self.filter_by_year).pack(pady=5)
        ttk.Button(self.left, text="Фильтр по статье", command=self.filter_by_article).pack(pady=5)
        ttk.Button(self.left, text="Поиск по IMSI", command=self.search_imsi).pack(pady=5)
        ttk.Button(self.left, text="Обновить", command=self.reset_map).pack(pady=5)
        ttk.Button(self.left, text="Все преступления", command=self.show_all_crimes).pack(pady=5)

        self.root.after(100, self.embed_map)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def cef_query_handler(self, request):
        # 🔧 ЕСЛИ request — словарь, берём значение из ключа 'request'
        if isinstance(request, dict) and "request" in request:
            request = request["request"]

        print("📩 cefQuery получен:", request)

        if ":" not in request:
            print("❌ Неверный формат:", request)
            return

        action, id_str = request.split(":", 1)
        self.handle_action(id_str, action)


    def embed_map(self):
        self.root.update_idletasks()
        self.root.update()
        width = self.right.winfo_width()
        height = self.right.winfo_height()
        window_info = cef.WindowInfo()
        rect = [0, 0, width, height]
        window_info.SetAsChild(self.right.winfo_id(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=MAP_URL)
        self.right.update()
        self.right.focus_set()

        bindings = cef.JavascriptBindings()
        bindings.SetFunction("cefQuery", self.cef_query_handler)
        self.browser.SetJavascriptBindings(bindings)


    def clear_dynamic_frame(self):
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
            self.dynamic_frame = None

    def save_locations(self, data):
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def load_locations(self):
        with open(DB_FILE, 'r') as f:
            return json.load(f)

    def show_all_crimes(self):
        self.clear_dynamic_frame()
        data = self.load_locations()
        m = folium.Map(location=[43.07, 58.91], zoom_start=7)

        for loc in data:
            color = "blue" if loc.get("status") == "solved" else "red"
            popup_html = f"""
            <b>Дата/время:</b> {loc['time']}<br>
            <b>Статья:</b> {loc['article']}<br>
            <b>Фабула:</b> {loc['fabula'][:300]}<br><br>
            <a href="javascript:void(0)" onclick="if (confirm('Вы действительно хотите удалить?')) window.cefQuery({{request: 'delete:{loc["id"]}'}})">🗑 Удалить</a><br>
            <a href="javascript:void(0)" onclick="window.cefQuery({{request: '{'unsolved' if loc.get('status') == 'solved' else 'solved'}:{loc['id']}'}})">
                {'🔴 Преступление не раскрыто' if loc.get('status') == 'solved' else '✅ Преступление раскрыто'}
            </a><br>
            <a href="javascript:void(0)" onclick="window.cefQuery({{request: 'edit:{loc['id']}'}})">✏ Изменить</a>
            """



            folium.Marker(
                [loc['lat'], loc['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(m)

        m.save(MAP_PATH)
        self.browser.LoadUrl(MAP_URL)

    def reset_map(self):
        self.clear_dynamic_frame()
        self.browser.LoadUrl(MAP_URL)

    def on_close(self):
        cef.QuitMessageLoop()
        self.root.destroy()

    def add_crime(self):
        self.clear_dynamic_frame()
        self.dynamic_frame = tk.Frame(self.left, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.dynamic_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.65)

        def close():
            self.clear_dynamic_frame()

        tk.Button(self.dynamic_frame, text="X", command=close, fg="red").pack(anchor="ne", padx=5, pady=5)

        labels = ["Дата/время:", "Фабула:", "Статья:", "Широта:", "Долгота:"]
        entries = {}

        for label in labels:
            tk.Label(self.dynamic_frame, text=label).pack(anchor='w', padx=5)
            if label == "Фабула:":
                entry = tk.Text(self.dynamic_frame, height=4, wrap=tk.WORD)
                entry.insert("1.0", "")
                entry.config(state="normal")  # <-- обязательно включаем редактирование

            else:
                entry = tk.Entry(self.dynamic_frame)
            entry.pack(fill=tk.X, padx=5, pady=2)
            entries[label] = entry

        excel_path_var = tk.StringVar()
        def choose_excel():
            path = filedialog.askopenfilename(title="Excel", filetypes=[("Excel", "*.xlsx *.xls")])
            if path:
                excel_path_var.set(path)

        ttk.Button(self.dynamic_frame, text="Выбрать Excel-файл", command=choose_excel).pack(pady=3)

        def submit():
            time_str = entries["Дата/время:"].get().strip()
            fabula = entries["Фабула:"].get("1.0", tk.END).strip()
            article = entries["Статья:"].get().strip()
            try:
                lat = float(entries["Широта:"].get().strip())
                lon = float(entries["Долгота:"].get().strip())
            except:
                messagebox.showerror("Ошибка", "Неверные координаты")
                return
            path = excel_path_var.get()
            if path:
                new_name = f"{uuid.uuid4().hex}_{os.path.basename(path)}"
                shutil.copy2(path, os.path.join(IMSI_DIR, new_name))
            new_entry = {
                "id": uuid.uuid4().hex,
                "time": time_str,
                "fabula": fabula,
                "article": article,
                "lat": lat,
                "lon": lon,
                "status": "active"
            }
            data = self.load_locations()
            data.append(new_entry)
            self.save_locations(data)
            self.show_all_crimes()

        ttk.Button(self.dynamic_frame, text="Сохранить", command=submit).pack(pady=5)
        # 🔧 Добавлено для стабильной работы кнопки
        self.root.focus_force()
        self.dynamic_frame.focus_set()

    def search_imsi(self):
        self.clear_dynamic_frame()
        self.dynamic_frame = tk.Frame(self.left, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.dynamic_frame.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.2)

        def close():
            self.clear_dynamic_frame()

        tk.Button(self.dynamic_frame, text="X", command=close, fg="red").pack(anchor="ne", padx=5, pady=2)

        tk.Label(self.dynamic_frame, text="Введите IMSI:").pack(anchor='w')
        entry_imsi = tk.Entry(self.dynamic_frame)
        entry_imsi.pack(fill=tk.X, padx=5, pady=2)

        def do_search():
            imsi_to_find = entry_imsi.get().strip()
            if not imsi_to_find:
                return

            found_locations = []

            for filename in os.listdir(IMSI_DIR):
                if not filename.endswith((".xlsx", ".xls")):
                    continue
                filepath = os.path.join(IMSI_DIR, filename)
                try:
                    wb = load_workbook(filepath)
                    sheet = wb.active
                    for row in sheet.iter_rows(values_only=True):
                        if not row:
                            continue
                        joined = ",".join([str(cell) for cell in row if cell])
                        row = [c.strip() for c in joined.split(",") if c.strip()]
                        if any(imsi_to_find in cell for cell in row):
                            lat, lon, time_str = None, None, None
                            for cell in row:
                                try:
                                    num = float(cell)
                                    if 20 <= num <= 60:
                                        if not lat:
                                            lat = num
                                        elif not lon:
                                            lon = num
                                except:
                                    if "/" in cell and ":" in cell:
                                        time_str = cell
                            if lat and lon:
                                found_locations.append((lat, lon, time_str or "время неизвестно"))
                except Exception as e:
                    print(f"Ошибка при чтении {filename}: {e}")

            if not found_locations:
                messagebox.showinfo("Результат", "Совпадений не найдено.")
                return

            m = folium.Map(location=[found_locations[0][0], found_locations[0][1]], zoom_start=8)
            locations = self.load_locations()

            for lat, lon, time_str in found_locations:
                matched_fabula = None
                for loc in locations:
                    try:
                        # Сравнение координат
                        if abs(loc["lat"] - lat) < 0.0001 and abs(loc["lon"] - lon) < 0.0001:
                            # Сравнение даты
                            loc_date = loc["time"].split()[0].replace(".", "/")  # '10.02.2025' → '10/02/2025'
                            input_date = time_str.split()[0].replace(".", "/")
                            if loc_date == input_date:
                                matched_fabula = loc["fabula"]
                                break
                    except:
                        continue

                popup_content = f"<b>{time_str}</b>"
                if matched_fabula:
                    popup_content += f"<br><i>{matched_fabula[:150]}</i>"

                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_content, max_width=250),
                    icon=folium.Icon(color="black")
                ).add_to(m)



            m.save(TEMP_MAP_PATH)
            self.browser.LoadUrl(TEMP_MAP_URL)


        ttk.Button(self.dynamic_frame, text="Поиск", command=do_search).pack(pady=5)
        # 🔧 Добавлено для стабильной работы кнопки
        self.root.focus_force()
        self.dynamic_frame.focus_set()

    def handle_action(self, id_str, action):
        data = self.load_locations()
        loc = next((item for item in data if item["id"] == id_str), None)
        if not loc:
            messagebox.showerror("Ошибка", "Локация не найдена.")
            return

        if action == "delete":
            if messagebox.askyesno("Удалить", "Удалить эту локацию?"):
                data = [item for item in data if item["id"] != id_str]
                self.save_locations(data)
                self.show_all_crimes()

        elif action == "solved":
            loc["status"] = "solved"
            self.save_locations(data)
            self.show_all_crimes()

        elif action == "unsolved":
            loc["status"] = "active"
            self.save_locations(data)
            self.show_all_crimes()


        elif action == "edit":
            self.clear_dynamic_frame()
            self.dynamic_frame = tk.Frame(self.left, bg="#ffffff", bd=2, relief=tk.GROOVE)
            self.dynamic_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.65)

            def close(): self.clear_dynamic_frame()
            tk.Button(self.dynamic_frame, text="X", command=close, fg="red").pack(anchor="ne", padx=5, pady=5)

            labels = ["Дата/время:", "Фабула:", "Статья:", "Широта:", "Долгота:"]
            entries = {}

            for label in labels:
                tk.Label(self.dynamic_frame, text=label).pack(anchor='w', padx=5)
                if label == "Фабула:":
                    entry = tk.Text(self.dynamic_frame, height=4, wrap=tk.WORD)
                    entry.insert("1.0", loc["fabula"])
                    entry.config(state="normal")  # 🔓 разрешаем редактирование
                else:
                    entry = tk.Entry(self.dynamic_frame)
                    value = loc["time"] if label == "Дата/время:" else (
                        loc["article"] if label == "Статья:" else (
                            str(loc["lat"]) if label == "Широта:" else str(loc["lon"])
                        )
                    )
                    entry.insert(0, value)
                entry.pack(fill=tk.X, padx=5, pady=2)
                entries[label] = entry

            def update():
                loc["time"] = entries["Дата/время:"].get()
                loc["fabula"] = entries["Фабула:"].get("1.0", tk.END).strip()
                loc["article"] = entries["Статья:"].get()
                loc["lat"] = float(entries["Широта:"].get())
                loc["lon"] = float(entries["Долгота:"].get())
                self.save_locations(data)
                self.show_all_crimes()

            ttk.Button(self.dynamic_frame, text="Обновить", command=update).pack(pady=5)

            # 🔽 Это решение проблемы с невозможностью редактировать
            self.root.focus_force()
            entries["Дата/время:"].focus_set()

    def filter_by_article(self):
        self.clear_dynamic_frame()
        self.dynamic_frame = tk.Frame(self.left, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.dynamic_frame.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.2)

        def close():
            self.clear_dynamic_frame()

        tk.Button(self.dynamic_frame, text="X", command=close, fg="red").pack(anchor="ne", padx=5, pady=2)

        tk.Label(self.dynamic_frame, text="Введите статью:").pack(anchor='w')
        entry_article = tk.Entry(self.dynamic_frame)
        entry_article.pack(fill=tk.X, padx=5, pady=2)

        def do_filter():
            article = entry_article.get().strip()
            if not article:
                return

            data = self.load_locations()
            found = [loc for loc in data if loc["article"] == article]

            if not found:
                messagebox.showinfo("Результат", "Совпадений не найдено.")
                return

            m = folium.Map(location=[found[0]["lat"], found[0]["lon"]], zoom_start=8)
            for loc in found:
                color = "blue" if loc.get("status") == "solved" else "red"
                popup = f"<b>{loc['time']}</b><br>{loc['article']}<br>{loc['fabula'][:100]}"
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    popup=popup,
                    icon=folium.Icon(color=color)
                ).add_to(m)

            m.save(TEMP_MAP_PATH)
            self.browser.LoadUrl(TEMP_MAP_URL)

        ttk.Button(self.dynamic_frame, text="Поиск", command=do_filter).pack(pady=5)
        self.root.focus_force()
        self.dynamic_frame.focus_set()

    def filter_by_year(self):
        self.clear_dynamic_frame()
        self.dynamic_frame = tk.Frame(self.left, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.dynamic_frame.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.2)

        def close():
            self.clear_dynamic_frame()

        tk.Button(self.dynamic_frame, text="X", command=close, fg="red").pack(anchor="ne", padx=5, pady=2)

        tk.Label(self.dynamic_frame, text="Введите год:").pack(anchor='w')
        entry_year = tk.Entry(self.dynamic_frame)
        entry_year.pack(fill=tk.X, padx=5, pady=2)

        def do_filter():
            year = entry_year.get().strip()
            if not year.isdigit():
                messagebox.showerror("Ошибка", "Введите корректный год (например 2025)")
                return

            data = self.load_locations()
            found = [loc for loc in data if year in loc["time"]]

            if not found:
                messagebox.showinfo("Результат", "Совпадений не найдено.")
                return

            m = folium.Map(location=[found[0]["lat"], found[0]["lon"]], zoom_start=8)
            for loc in found:
                color = "blue" if loc.get("status") == "solved" else "red"
                popup = f"<b>{loc['time']}</b><br>{loc['article']}<br>{loc['fabula'][:100]}"
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    popup=popup,
                    icon=folium.Icon(color=color)
                ).add_to(m)

            m.save(TEMP_MAP_PATH)
            self.browser.LoadUrl(TEMP_MAP_URL)

        ttk.Button(self.dynamic_frame, text="Поиск", command=do_filter).pack(pady=5)
        self.root.focus_force()
        self.dynamic_frame.focus_set()


def main():
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    root = tk.Tk()
    app = App(root)

    def loop():
        cef.MessageLoopWork()
        root.after(10, loop)

    loop()
    root.mainloop()
    cef.Shutdown()

if __name__ == "__main__":
    main()
