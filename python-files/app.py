# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import xml.etree.ElementTree as ET
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter
import configparser

APP_NAME = "VaynakhTowerFinder"

def load_towers(kml_path):
    """
    Parse a KML file and return a list of towers as dicts:
    [{"name": <str or None>, "lat": float, "lon": float}]
    Only Point features are considered.
    """
    if not os.path.exists(kml_path):
        raise FileNotFoundError(f"Файл не найден: {kml_path}")
    try:
        tree = ET.parse(kml_path)
    except ET.ParseError as e:
        raise ValueError(f"Не удалось прочитать KML (ошибка формата): {e}")
    root = tree.getroot()
    ns = {"kml": "http://www.opengis.net/kml/2.2",
          "gx": "http://www.google.com/kml/ext/2.2"}

    towers = []
    for pm in root.findall(".//kml:Placemark", ns):
        # учитывать только точки (Point), игнорировать линии/полигоны
        point = pm.find(".//kml:Point", ns)
        if point is None:
            continue
        coords_el = point.find(".//kml:coordinates", ns)
        if coords_el is None or not coords_el.text:
            continue
        # KML coordinates are "lon,lat[,alt]"
        first = coords_el.text.strip().split()[0]
        parts = [p for p in first.split(",") if p]
        if len(parts) < 2:
            continue
        lon, lat = float(parts[0]), float(parts[1])
        name_el = pm.find("kml:name", ns)
        name = name_el.text.strip() if (name_el is not None and name_el.text) else None
        towers.append({"name": name, "lat": lat, "lon": lon})
    if not towers:
        raise ValueError("В KML не найдено ни одной точки (Point). Проверьте, что в файле именно метки-точки.")
    return towers

def geocode_address(address, language="ru", timeout=10):
    geolocator = Nominatim(user_agent=APP_NAME, timeout=timeout, scheme='https')
    # вежливая задержка между запросами (на случай повторных)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    location = geocode(address, language=language, addressdetails=False)
    if not location:
        return None
    return (location.latitude, location.longitude)

def find_nearest(user_coords, towers):
    """
    user_coords: (lat, lon)
    towers: list of dicts with lat, lon
    returns (best, best_dist_m) where best is tower dict + 'distance_m'
    """
    if not towers:
        return None, None
    best = None
    best_dist = None
    for t in towers:
        dist_m = geodesic((t["lat"], t["lon"]), user_coords).meters
        if best_dist is None or dist_m < best_dist:
            best_dist = dist_m
            best = t
    if best is None:
        return None, None
    best = dict(best)
    best["distance_m"] = best_dist
    return best, best_dist

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Поиск ближайшей вышки Вайнах Телеком")
        self.geometry("560x260")
        self.resizable(False, False)
        self.iconbitmap(False, '')  # игнорируем иконку, чтобы не падало на Linux/Mac
        self.config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        self.config = configparser.ConfigParser()
        self._load_config()

        # KML path
        tk.Label(self, text="Файл KML с вышками:").place(x=20, y=20)
        self.kml_var = tk.StringVar(value=self.config.get("app", "kml_path", fallback=""))
        tk.Entry(self, textvariable=self.kml_var, width=52).place(x=160, y=18)
        tk.Button(self, text="Выбрать…", command=self.choose_kml).place(x=480, y=15)

        # Address
        tk.Label(self, text="Адрес для проверки:").place(x=20, y=70)
        self.address_var = tk.StringVar()
        tk.Entry(self, textvariable=self.address_var, width=60).place(x=160, y=68)

        # Language
        tk.Label(self, text="Язык геокодера:").place(x=20, y=110)
        self.lang_var = tk.StringVar(value=self.config.get("app", "language", fallback="ru"))
        tk.Entry(self, textvariable=self.lang_var, width=10).place(x=160, y=108)

        # Buttons
        tk.Button(self, text="Рассчитать", command=self.calculate).place(x=160, y=150)
        tk.Button(self, text="О программе", command=self.show_about).place(x=260, y=150)

        # Results
        self.result = tk.StringVar(value="")
        tk.Label(self, textvariable=self.result, justify="left").place(x=20, y=190)

    def _load_config(self):
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding="utf-8")

    def _save_config(self):
        if "app" not in self.config.sections():
            self.config.add_section("app")
        self.config.set("app", "kml_path", self.kml_var.get())
        self.config.set("app", "language", self.lang_var.get())
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    def choose_kml(self):
        path = filedialog.askopenfilename(
            title="Выберите KML файл",
            filetypes=[("KML файлы", "*.kml"), ("Все файлы", "*.*")]
        )
        if path:
            self.kml_var.set(path)
            self._save_config()

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "VaynakhTowerFinder\n"
            "1) Выберите файл KML с метками вышек Вайнах Телеком\n"
            "2) Введите адрес и нажмите «Рассчитать»\n\n"
            "Геокодирование: Nominatim (OpenStreetMap).\n"
            "Результат: расстояние до ближайшей вышки (метры)."
        )

    def calculate(self):
        kml_path = self.kml_var.get().strip()
        if not kml_path:
            messagebox.showerror("Ошибка", "Сначала укажите файл KML с вышками.")
            return
        if not os.path.exists(kml_path):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{kml_path}")
            return
        address = self.address_var.get().strip()
        if not address:
            messagebox.showerror("Ошибка", "Введите адрес.")
            return
        language = (self.lang_var.get() or "ru").strip()

        try:
            towers = load_towers(kml_path)
        except Exception as e:
            messagebox.showerror("Ошибка KML", str(e))
            return

        coords = geocode_address(address, language=language)
        if not coords:
            messagebox.showerror("Адрес не найден", "Не удалось геокодировать адрес. Попробуйте уточнить формулировку.")
            return

        best, dist = find_nearest(coords, towers)
        if not best:
            messagebox.showerror("Ошибка", "Не удалось определить ближайшую вышку.")
            return

        self._save_config()

        name = best.get("name") or "(без названия)"
        self.result.set(
            f"Найдено вышек: {len(towers)}\n"
            f"Ближайшая вышка: {name}\n"
            f"Расстояние: {best['distance_m']:.1f} м\n"
            f"Координаты адреса: {coords[0]:.6f}, {coords[1]:.6f}"
        )

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
