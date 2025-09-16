import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import math
from typing import Literal
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
import urllib.parse
import threading
import atexit
import sys
import os
import numpy as np
from tkcalendar import DateEntry

# Подавление предупреждений Tkinter (опционально)
os.environ['TK_SILENCE_DEPRECATION'] = '1'

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

disable_warnings(InsecureRequestWarning)

OptionSide = Literal["call", "put"]


# ========================
# FX Option Pricer (Garman-Kohlhagen)
# ========================
class FXOption:
    def __init__(self, spot: float, strike: float, T: float,
                 rd: float, rf: float, vol: float, side: OptionSide = "call"):
        self.S = float(spot)
        self.K = float(strike)
        self.T = float(T)
        self.rd = float(rd)
        self.rf = float(rf)
        self.vol = float(vol)
        self.side = side

    def _d1_d2(self) -> tuple[float, float]:
        sigma_sqrt_T = self.vol * math.sqrt(self.T)
        d1 = (
            math.log(self.S / self.K)
            + (self.rd - self.rf + 0.5 * self.vol ** 2) * self.T
        ) / sigma_sqrt_T
        d2 = d1 - sigma_sqrt_T
        return d1, d2

    @staticmethod
    def _N(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))

    def price(self) -> float:
        d1, d2 = self._d1_d2()
        df_d = math.exp(-self.rd * self.T)
        df_f = math.exp(-self.rf * self.T)

        if self.side == "call":
            return self.S * df_f * self._N(d1) - self.K * df_d * self._N(d2)
        else:
            return self.K * df_d * self._N(-d2) - self.S * df_f * self._N(-d1)


# ========================
# NDF Pricing Engine
# ========================
class NDFPricing:
    def __init__(self, proxy: str = None):
        from issmoex import ISSMOEX
        self.iss = ISSMOEX(proxy=proxy)

    def pricing(self, currency: str, start_date: str, end_date: str, step_days: int = 30, use_anchor: bool = True) -> pd.DataFrame:
        futures = self.iss.iss_url(
            url='https://iss.moex.com/iss/statistics/engines/futures/markets/forts/series.html?show_expired=1'
        )
        futures = futures[futures['asset_code'].notna()]
        date_spot = (pd.to_datetime('today').normalize() - pd.DateOffset(5)).strftime('%Y-%m-%d')
        if currency == 'USD':
            flt = futures['name'].str.contains('Si-')
            candles = self.iss.candles(engine='futures', market='forts', isin='USDRUBF', date=date_spot)
            spot = candles['close'].iloc[-1] * 1000
        elif currency == 'EUR':
            flt = futures['name'].str.contains('Eu-')
            candles = self.iss.candles(engine='futures', market='forts', isin='EURRUBF', date=date_spot)
            spot = candles['close'].iloc[-1] * 1000
        elif currency == 'CNY':
            flt = futures['name'].str.contains('CNY-') & (futures['underlying_asset'] == 'CNYRUB_TOM')
            candles = self.iss.candles(engine='currency', market='selt', isin='CNY000000TOD', date=date_spot)
            spot = candles['close'].iloc[-1]
        else:
            raise ValueError(f"Unsupported currency: {currency}")
        futures = futures.loc[flt]
        futures['expiration_date'] = pd.to_datetime(futures['expiration_date'])
        today = pd.to_datetime('today').normalize()
        flt_fut = (futures['expiration_date'] > today) & (futures['expiration_date'] < '2050-01-01')
        futures = futures.loc[flt_fut]
        secid_to_exp = dict(zip(futures['secid'], futures['expiration_date']))
        prices_data = []
        today_str = (pd.to_datetime('today').normalize() - pd.DateOffset(7)).strftime('%Y-%m-%d')
        for secid in futures['secid']:
            try:
                candles = self.iss.candles(engine='futures', market='forts', isin=secid, date=today_str)
                if not candles.empty:
                    prices_data.append({
                        'date': candles['end'].iloc[-1],
                        'price': candles['close'].iloc[-1],
                        'name': secid
                    })
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке {secid}: {e}")
                continue
        prices = pd.DataFrame(prices_data)
        if prices.empty:
            raise ValueError("Не удалось загрузить цены фьючерсов.")
        prices['T'] = prices['name'].map(secid_to_exp)
        prices['T'] = pd.to_datetime(prices['T'])
        prices['SPOT'] = spot
        prices['TOD'] = today
        swpdiff = prices['price'] / prices['SPOT'] - 1
        t_y = (prices['T'] - prices['TOD']).dt.days / 365
        prices['swpdiff'] = swpdiff / t_y
        # --- Добавляем якорную ставку КАК ФЬЮЧЕРС НА ЗАВТРА ---
        if not prices.empty:
            nearest_idx = t_y.idxmin()
            r = prices.loc[nearest_idx, 'swpdiff']
            d = (prices.loc[nearest_idx, 'T'] - today).days
            if d > 0 and not math.isnan(r):
                if currency == 'CNY':
                    # Для CNY: Рассчитываем якорную ставку напрямую из TOD и TODTOM
                    try:
                        # Получаем спот из CNY000000TOD (уже есть в переменной 'spot', но перезапросим для надежности)
                        tod_candles = self.iss.candles(
                            engine='currency',
                            market='selt',
                            isin='CNY000000TOD',
                            date=date_spot
                        )
                        if tod_candles.empty:
                            raise ValueError("Не удалось получить данные по CNY000000TOD.")
                        # Получаем дельту из CNYRUBTODTOM
                        todtom_candles = self.iss.candles(
                            engine='currency',
                            market='selt',
                            isin='CNYRUBTODTOM',
                            date=date_spot
                        )
                        if todtom_candles.empty:
                            raise ValueError("Не удалось получить данные по CNYRUBTODTOM.")
                        # Берем последние цены
                        spot_TOD = tod_candles['close'].iloc[-1]
                        delta_TODTOM = todtom_candles['close'].iloc[-1]
                        # Рассчитываем абсолютный курс на T+1
                        forward_T1 = spot_TOD + delta_TODTOM
                        # Рассчитываем якорную ставку на 1 день
                        r_ON = (forward_T1 / spot_TOD - 1) * 365
                    except Exception as e:
                        print(f"⚠️ Ошибка при расчете якорной ставки для CNY: {e}")
                        # Fallback на старый расчет, если что-то пошло не так
                        r_ON = 365 * ((1 + r * d / 365) ** (1/d) - 1)
                else:
                    # Для USD и EUR: оставляем старый расчет по сложному проценту
                    r_ON = 365 * ((1 + r * d / 365) ** (1/d) - 1)
                anchor_row = {
                    'T': today + pd.Timedelta(days=1),
                    'swpdiff': r_ON,
                    'price': spot * (1 + r_ON * 1/365),
                    'SPOT': spot,
                    'name': 'ANCHOR',
                    'date': (today + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                }
                prices = pd.concat([prices, pd.DataFrame([anchor_row])], ignore_index=True)
        # --- Фильтруем якорную точку, если use_anchor=False ---
        if not use_anchor:
            prices_for_interp = prices[prices['name'] != 'ANCHOR'].copy()
        else:
            prices_for_interp = prices.copy()
        t_y_interp = (prices_for_interp['T'] - today).dt.days / 365
        if len(t_y_interp) == 0:
            raise ValueError("Нет доступных данных для интерполяции после фильтрации.")
        sorted_indices = np.argsort(t_y_interp)
        t_y_sorted = t_y_interp.iloc[sorted_indices].values
        swpdiff_sorted = prices_for_interp['swpdiff'].iloc[sorted_indices].values
        t_first = t_y_sorted[0]
        swp_first = swpdiff_sorted[0]
        if len(t_y_sorted) > 1:
            f_interp = interp1d(t_y_sorted, swpdiff_sorted, kind='linear', bounds_error=False, fill_value=np.nan)
        else:
            f_interp = lambda x: swp_first if (x >= t_first) else np.nan
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        if (end_dt - start_dt).days <= 0:
            raise ValueError("Конечная дата должна быть позже начальной.")
        dates_list = []
        current = start_dt
        while current <= end_dt:
            dates_list.append(current)
            if step_days == -1:  # Специальный флаг для месячного шага
                current += pd.DateOffset(months=1)
            else:
                current += pd.Timedelta(days=step_days)
        if dates_list[-1] != end_dt:
            dates_list.append(end_dt)
        dates = pd.DatetimeIndex(dates_list)
        days_to_maturity = (dates - today).days / 365
        pred_diffs = []
        for t in days_to_maturity:
            if t < t_first and t_first > 0:
                swp_t = (1 + swp_first) ** (t / t_first) - 1
                pred_diffs.append(swp_t)
            else:
                interp_val = f_interp(t)
                if np.isnan(interp_val):
                    interp_val = swpdiff_sorted[-1]
                pred_diffs.append(interp_val)
        pred_diffs = [x.item() if hasattr(x, 'item') else x for x in pred_diffs]
        pricing = pd.DataFrame({
            'date': dates,
            'swpdiff': pred_diffs,
            'SPOT': spot,
            'forward_price': spot * (1 + pred_diffs * days_to_maturity)
        })
        pricing.real_data = prices[['T', 'swpdiff', 'price', 'SPOT']].copy()
        pricing.real_data.rename(columns={'T': 'date'}, inplace=True)
        pricing.real_data['swpdiff_pct'] = (pricing.real_data['swpdiff'] * 100).round(4)
        pricing.real_data['forward_price'] = pricing.real_data['SPOT'] * (
                    1 + pricing.real_data['swpdiff'] * ((pricing.real_data['date'] - today).dt.days / 365))
        return pricing

    def pricing_monthly(self, currency: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Точная копия логики из вашего примера — чистая линейная интерполяция с шагом 1 месяц"""
        futures = self.iss.iss_url(
            url='https://iss.moex.com/iss/statistics/engines/futures/markets/forts/series.html?show_expired=1'
        )
        futures = futures[futures['asset_code'].notna()]

        date_spot = (pd.to_datetime('today').normalize() - pd.DateOffset(5)).strftime('%Y-%m-%d')

        if currency == 'USD':
            flt = futures['name'].str.contains('Si-')
            candles = self.iss.candles(engine='futures', market='forts', isin='USDRUBF', date=date_spot)
            spot = candles['close'].iloc[-1] * 1000
        elif currency == 'EUR':
            flt = futures['name'].str.contains('Eu-')
            candles = self.iss.candles(engine='futures', market='forts', isin='EURRUBF', date=date_spot)
            spot = candles['close'].iloc[-1] * 1000
        elif currency == 'CNY':
            flt = futures['name'].str.contains('CNY-') & (futures['underlying_asset'] == 'CNYRUB_TOM')
            candles = self.iss.candles(engine='currency', market='selt', isin='CNY000000TOD', date=date_spot)
            spot = candles['close'].iloc[-1]
        else:
            raise ValueError(f"Unsupported currency: {currency}")

        futures = futures.loc[flt]
        futures['expiration_date'] = pd.to_datetime(futures['expiration_date'])
        today = pd.to_datetime('today').normalize()
        flt_fut = (futures['expiration_date'] > today) & (futures['expiration_date'] < '2050-01-01')
        futures = futures.loc[flt_fut]

        secid_to_exp = dict(zip(futures['secid'], futures['expiration_date']))

        prices_data = []
        today_str = (pd.to_datetime('today').normalize() - pd.DateOffset(7)).strftime('%Y-%m-%d')
        for secid in futures['secid']:
            try:
                candles = self.iss.candles(engine='futures', market='forts', isin=secid, date=today_str)
                if not candles.empty:
                    prices_data.append({
                        'date': candles['end'].iloc[-1],
                        'price': candles['close'].iloc[-1],
                        'name': secid
                    })
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке {secid}: {e}")
                continue

        prices = pd.DataFrame(prices_data)
        if prices.empty:
            raise ValueError("Не удалось загрузить цены фьючерсов.")

        prices['T'] = prices['name'].map(secid_to_exp)
        prices['T'] = pd.to_datetime(prices['T'])
        prices['SPOT'] = spot
        prices['TOD'] = today

        swpdiff = prices['price'] / prices['SPOT'] - 1
        t_y = (prices['T'] - prices['TOD']).dt.days / 365
        prices['swpdiff'] = swpdiff / t_y

        f_interp = interp1d(t_y, prices['swpdiff'], kind='linear', bounds_error=False, fill_value="extrapolate")

        dates = pd.date_range(start=start_date, end=end_date, freq=pd.DateOffset(months=1))
        days_to_maturity = (dates - today).days / 365

        pred_diffs = [f_interp(t).item() if not math.isnan(f_interp(t)) else 0.0 for t in days_to_maturity]

        pricing = pd.DataFrame({
            'date': dates,
            'swpdiff': pred_diffs,
            'SPOT': spot,
            'forward_price': spot * (1 + pred_diffs * days_to_maturity)
        })

        pricing.real_data = prices[['T', 'swpdiff', 'price', 'SPOT']].copy()
        pricing.real_data.rename(columns={'T': 'date'}, inplace=True)
        pricing.real_data['swpdiff_pct'] = (pricing.real_data['swpdiff'] * 100).round(2)
        pricing.real_data['forward_price'] = pricing.real_data['SPOT'] * (
                    1 + pricing.real_data['swpdiff'] * ((pricing.real_data['date'] - today).dt.days / 365))

        return pricing


# ========================
# Login Dialog (вызывается до создания NDFApp)
# ========================
def get_proxy_from_login():
    login_win = tk.Tk()
    login_win.title("Введите учетные данные прокси")
    login_win.geometry("300x180")
    login_win.resizable(False, False)
    login_win.grab_set()  # modal
    login_win.focus_force()

    tk.Label(login_win, text="Логин:").pack(pady=(20, 5))
    login_entry = tk.Entry(login_win, width=30)
    login_entry.pack()

    tk.Label(login_win, text="Пароль:").pack(pady=(10, 5))
    password_entry = tk.Entry(login_win, width=30, show="*")
    password_entry.pack()

    proxy_url = [None]  # используем список для передачи по ссылке

    def on_submit():
        login = login_entry.get().strip()
        password = password_entry.get().strip()
        if not login or not password:
            messagebox.showwarning("Ошибка", "Логин и пароль не могут быть пустыми!", parent=login_win)
            return
        encoded_password = urllib.parse.quote(password, safe='')
        proxy_url[0] = f"http://{login}:{encoded_password}@slar-prx-ba.mtsbank.ru:2270"
        login_win.destroy()

    def on_cancel():
        login_win.destroy()
        exit(0)  # Завершаем процесс, если отмена

    def on_space(event=None):
        on_submit()

    tk.Button(login_win, text="ОК", command=on_submit, width=10).pack(side="left", padx=(60, 10), pady=20)
    tk.Button(login_win, text="Отмена", command=on_cancel, width=10).pack(side="right", padx=(10, 60), pady=20)
    login_win.bind("<Return>", on_space)

    login_win.mainloop()
    return proxy_url[0]


# ========================
# GUI Application
# ========================
class NDFApp:
    def __init__(self, root, proxy):
        self.root = root
        self.proxy = proxy
        self.root.title("NDF & FX Option Pricer")
        self.root.geometry("1800x900")
        self.root.resizable(True, True)
        # Установка дефолтных дат: начало +1 мес, конец +5 мес
        today = pd.Timestamp.today().normalize()
        default_start = (today + pd.Timedelta(days=30)).strftime('%Y-%m-%d')
        default_end = (today + pd.Timedelta(days=150)).strftime('%Y-%m-%d')
        # Variables — ОБЩИЕ для NDF и опционов
        self.currency_var = tk.StringVar(value="EUR")
        self.start_date_var = tk.StringVar(value=default_start)
        self.end_date_var = tk.StringVar(value=default_end)
        self.step_days_var = tk.StringVar(value="1M")  # <<< ЕДИНСТВЕННОЕ ИЗМЕНЕНИЕ: IntVar → StringVar, 30 → "1M"
        # Option-specific variables — дефолт страйка для EUR
        self.strike_var = tk.DoubleVar(value=110.0)
        self.vol_var = tk.DoubleVar(value=0.10)
        self.rd_var = tk.DoubleVar(value=0.15)
        self.rf_var = tk.DoubleVar(value=0.03)
        self.side_var = tk.StringVar(value="call")
        # Флаг для якорной точки
        self.use_anchor_var = tk.BooleanVar(value=True)
        self.spot = None
        self.ndf_results = None
        self.ndf_monthly_results = None  # для месячной таблицы
        self.option_results = None
        # Создаём Scrollable Frame для основного окна
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # Привязываем колёсико мыши к прокрутке
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.create_widgets()
        # Инициализируем дефолтные значения под выбранную валюту (EUR по умолчанию)
        self.on_currency_change()
        # Автоматически выполнить первый расчёт после логина
        self.calculate_ndf()

    def _on_mousewheel(self, event):
        """Прокрутка колёсиком мыши"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def format_rub(self, value):
        """Форматирует число в рублях: 111156.9146 → 111 156,91"""
        if value is None or isinstance(value, float) and math.isnan(value):
            return "—"
        rounded = round(float(value), 2)
        integer_part = int(rounded)
        decimal_part = int((rounded - integer_part) * 100 + 0.5)
        formatted = f"{integer_part:,}".replace(",", " ")
        if decimal_part > 0:
            formatted += f",{decimal_part:02d}"
        else:
            formatted += ",00"
        return formatted

    def create_widgets(self):
        # --- Spot Label ---
        self.spot_label = ttk.Label(self.scrollable_frame, text="Спот: — | NDF: — | Своп дифф: —", font=("Arial", 12, "bold"))
        self.spot_label.pack(pady=5)

        # --- Graph Area с встроенной панелью NDF в верхней левой ячейке ---
        self.figure = plt.figure(figsize=(18, 7))

        # Верхняя левая ячейка — для элементов управления NDF
        self.ax_ndf_controls = self.figure.add_subplot(2, 2, 1)
        self.ax_ndf_controls.set_title("Параметры NDF", fontsize=10, fontweight='bold')
        self.ax_ndf_controls.axis('off')  # Отключаем оси

        # График курса валюты (ax1) — нижняя левая ячейка
        self.ax1 = self.figure.add_subplot(2, 2, 3)
        # График интерполяции (ax2) — нижняя правая ячейка
        self.ax2 = self.figure.add_subplot(2, 2, 4)
        # График реальных данных (ax3) — верхняя правая ячейка
        self.ax3 = self.figure.add_subplot(2, 2, 2)

        # Создаем холст для всей фигуры
        self.canvas_plot = FigureCanvasTkAgg(self.figure, self.scrollable_frame)
        canvas_widget = self.canvas_plot.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Внедряем красивую панель управления NDF в верхнюю левую ячейку ---
        def embed_ndf_controls():
            # Ждём, пока холст отрисуется
            self.root.after(100, _create_control_panel)

        def _create_control_panel():
            # Получаем размеры subplot'а в пикселях
            bbox = self.ax_ndf_controls.get_position()
            fig_width, fig_height = self.figure.get_size_inches() * self.figure.dpi
            x = bbox.x0 * fig_width
            y = (1 - bbox.y1) * fig_height
            width = bbox.width * fig_width
            height = bbox.height * fig_height

            # Создаём фрейм с тонкой рамкой и светло-серым фоном
            control_frame = tk.Frame(canvas_widget, bg="#f0f0f0", bd=1, relief="solid")
            control_frame.place(x=x, y=y, width=width, height=height)

            # Настройка стиля шрифтов
            label_font = ("Helvetica", 9)
            entry_font = ("Helvetica", 9)

            # --- Первый ряд: Валюта, Шаг, Кнопка ---
            row1_frame = tk.Frame(control_frame, bg="#f0f0f0")
            row1_frame.pack(fill="x", padx=5, pady=2)

            # Валюта
            tk.Label(row1_frame, text="Валюта:", bg="#f0f0f0", font=label_font).pack(side="left", padx=(0, 5))
            currency_combo = ttk.Combobox(row1_frame, textvariable=self.currency_var, values=["USD", "EUR", "CNY"], state="readonly", width=6)
            currency_combo.pack(side="left", padx=(0, 15))
            currency_combo.bind("<<ComboboxSelected>>", self.on_currency_change)

            # Шаг
            tk.Label(row1_frame, text="Шаг:", bg="#f0f0f0", font=label_font).pack(side="left", padx=(0, 5))
            step_combo = ttk.Combobox(row1_frame, textvariable=self.step_days_var, values=["1", "7", "1M"], state="readonly", width=5)  # <<< ЕДИНСТВЕННОЕ ИЗМЕНЕНИЕ: "30" → "1M"
            step_combo.pack(side="left", padx=(0, 15))
            step_combo.set("1M")  # <<< ЕДИНСТВЕННОЕ ИЗМЕНЕНИЕ: "30" → "1M"

            # Кнопка
            calc_button = tk.Button(row1_frame, text="Рассчитать NDF", command=self.calculate_ndf, font=entry_font, bg="lightblue", activebackground="skyblue", relief="flat")
            calc_button.pack(side="left", padx=(0, 5))

            # --- Второй ряд: Начало, Конец ---
            row2_frame = tk.Frame(control_frame, bg="#f0f0f0")
            row2_frame.pack(fill="x", padx=5, pady=2)

            # Начало
            tk.Label(row2_frame, text="Начало:", bg="#f0f0f0", font=label_font).pack(side="left", padx=(0, 5))
            today = pd.Timestamp.today().normalize()
            start_date_direct = today + pd.DateOffset(months=1)
            start_date_entry = DateEntry(
                row2_frame,
                width=10,
                date_pattern='y-mm-dd',
                date=start_date_direct,
                font=entry_font
            )
            start_date_entry.pack(side="left", padx=(0, 15))
            start_date_entry.config(textvariable=self.start_date_var)
            self.start_date_var.set(start_date_direct.strftime('%Y-%m-%d'))

            # Конец
            tk.Label(row2_frame, text="Конец:", bg="#f0f0f0", font=label_font).pack(side="left", padx=(0, 5))
            end_date_direct = today + pd.DateOffset(months=4)
            end_date_entry = DateEntry(
                row2_frame,
                width=10,
                date_pattern='y-mm-dd',
                date=end_date_direct,
                font=entry_font
            )
            end_date_entry.pack(side="left", padx=(0, 15))
            end_date_entry.config(textvariable=self.end_date_var)
            self.end_date_var.set(end_date_direct.strftime('%Y-%m-%d'))

        # Запускаем внедрение
        embed_ndf_controls()

        # --- NDF Results Tables и Real Data Table — на одном уровне ---
        table_frame = ttk.Frame(self.scrollable_frame)
        table_frame.pack(fill="x", padx=10, pady=5)

        # Основная NDF Table (левая) — по step_days
        ndf_frame = ttk.LabelFrame(table_frame, text="Результаты NDF (шаг: пользовательский)", padding=(5, 3))
        ndf_frame.pack(side="left", fill="y", padx=(0, 5))
        ndf_tree_frame = ttk.Frame(ndf_frame)
        ndf_tree_frame.pack(fill="y", expand=True)
        self.ndf_tree = ttk.Treeview(ndf_tree_frame, columns=("date", "swpdiff", "forward_price"), show="headings", height=8)
        self.ndf_tree.heading("date", text="Дата")
        self.ndf_tree.heading("swpdiff", text="Своп дифф (%)")
        self.ndf_tree.heading("forward_price", text="Форвард (RUB)")
        self.ndf_tree.column("date", width=100, anchor="center")
        self.ndf_tree.column("swpdiff", width=100, anchor="e")
        self.ndf_tree.column("forward_price", width=120, anchor="e")
        self.ndf_tree.pack(side="left", fill="y", expand=True)
        ndf_vsb = ttk.Scrollbar(ndf_tree_frame, orient="vertical", command=self.ndf_tree.yview)
        ndf_vsb.pack(side="right", fill="y")
        self.ndf_tree.configure(yscrollcommand=ndf_vsb.set)
        ttk.Button(ndf_frame, text="📋 Копировать расчетные", command=self.copy_ndf_table_to_clipboard).pack(pady=(5, 0))

        # Дополнительная NDF Table (средняя) — жёсткий шаг 1 месяц
        ndf_monthly_frame = ttk.LabelFrame(table_frame, text="Результаты NDF (шаг: 1 месяц)", padding=(5, 3))
        ndf_monthly_frame.pack(side="left", fill="y", padx=(5, 5))
        ndf_monthly_tree_frame = ttk.Frame(ndf_monthly_frame)
        ndf_monthly_tree_frame.pack(fill="y", expand=True)
        self.ndf_monthly_tree = ttk.Treeview(ndf_monthly_tree_frame, columns=("date", "swpdiff", "forward_price"), show="headings", height=8)
        self.ndf_monthly_tree.heading("date", text="Дата")
        self.ndf_monthly_tree.heading("swpdiff", text="Своп дифф (%)")
        self.ndf_monthly_tree.heading("forward_price", text="Форвард (RUB)")
        self.ndf_monthly_tree.column("date", width=100, anchor="center")
        self.ndf_monthly_tree.column("swpdiff", width=100, anchor="e")
        self.ndf_monthly_tree.column("forward_price", width=120, anchor="e")
        self.ndf_monthly_tree.pack(side="left", fill="y", expand=True)
        ndf_monthly_vsb = ttk.Scrollbar(ndf_monthly_tree_frame, orient="vertical", command=self.ndf_monthly_tree.yview)
        ndf_monthly_vsb.pack(side="right", fill="y")
        self.ndf_monthly_tree.configure(yscrollcommand=ndf_monthly_vsb.set)
        ttk.Button(ndf_monthly_frame, text="📋 Копировать по месяцам", command=self.copy_ndf_monthly_table_to_clipboard).pack(pady=(5, 0))

        # Real Data Table (правая)
        real_frame = ttk.LabelFrame(table_frame, text="Реальные квартальные фьючерсы", padding=(5, 3))
        real_frame.pack(side="left", fill="y", padx=(5, 0))
        real_tree_frame = ttk.Frame(real_frame)
        real_tree_frame.pack(fill="y", expand=True)
        self.real_tree = ttk.Treeview(real_tree_frame, columns=("date", "swpdiff_pct", "forward_price"), show="headings", height=8)
        self.real_tree.heading("date", text="Дата")
        self.real_tree.heading("swpdiff_pct", text="Своп дифф (%)")
        self.real_tree.heading("forward_price", text="Форвард (RUB)")
        self.real_tree.column("date", width=100, anchor="center")
        self.real_tree.column("swpdiff_pct", width=100, anchor="e")
        self.real_tree.column("forward_price", width=120, anchor="e")
        self.real_tree.pack(side="left", fill="y", expand=True)
        real_vsb = ttk.Scrollbar(real_tree_frame, orient="vertical", command=self.real_tree.yview)
        real_vsb.pack(side="right", fill="y")
        self.real_tree.configure(yscrollcommand=real_vsb.set)
        ttk.Button(real_frame, text="📋 Копировать фьючи", command=self.copy_real_table_to_clipboard).pack(pady=(5, 0))

        # Привязка Ctrl+C
        self.ndf_tree.bind("<Control-c>", lambda e: self.copy_ndf_table_to_clipboard())
        self.ndf_monthly_tree.bind("<Control-c>", lambda e: self.copy_ndf_monthly_table_to_clipboard())
        self.real_tree.bind("<Control-c>", lambda e: self.copy_real_table_to_clipboard())

        # ========================
        # Option Input Panel и Option Results Table — РАЗМЕЩЕНЫ РЯДОМ
        # ========================
        frame_option_container = ttk.Frame(self.scrollable_frame)
        frame_option_container.pack(fill="x", padx=10, pady=5)

        # Левая часть: Панель ввода параметров опционов
        frame_option_input = ttk.LabelFrame(frame_option_container, text="Параметры опционов", padding=(10, 5))
        frame_option_input.pack(side="left", fill="y", padx=(0, 5))  # Занимает левую часть

        # Строка 1: Ставки и волатильность (привязаны к валюте)
        ttk.Label(frame_option_input, text="Ставка RUB:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_option_input, textvariable=self.rd_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_option_input, text="Ставка FX:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_option_input, textvariable=self.rf_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(frame_option_input, text="Волатильность:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_option_input, textvariable=self.vol_var, width=10).grid(row=0, column=5, padx=5, pady=2)

        # Строка 2: Страйк и тип опциона
        ttk.Label(frame_option_input, text="Страйк:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_option_input, textvariable=self.strike_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame_option_input, text="Тип:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        side_combo = ttk.Combobox(frame_option_input, textvariable=self.side_var, values=["call", "put"], state="readonly", width=8)
        side_combo.grid(row=1, column=3, padx=5, pady=2)
        # Кнопка расчета опционов
        ttk.Button(frame_option_input, text="Рассчитать опцион", command=self.calculate_option).grid(row=1, column=4, padx=10, pady=2, sticky="w")

        # Правая часть: Таблица результатов опционов
        option_frame = ttk.LabelFrame(frame_option_container, text="Результаты опционов", padding=(5, 3))
        option_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))  # Занимает правую часть и растягивается

        option_tree_frame = ttk.Frame(option_frame)
        option_tree_frame.pack(side="left", fill="both", expand=True)

        self.option_tree = ttk.Treeview(option_tree_frame, columns=("date", "tenor", "strike", "side", "price_rub", "price_pct"), show="headings", height=8)
        self.option_tree.heading("date", text="Дата")
        self.option_tree.heading("tenor", text="Срок")
        self.option_tree.heading("strike", text="Стр.")
        self.option_tree.heading("side", text="Тип")
        self.option_tree.heading("price_rub", text="₽")
        self.option_tree.heading("price_pct", text="%")
        self.option_tree.column("date", width=95, anchor="center")
        self.option_tree.column("tenor", width=60, anchor="center")
        self.option_tree.column("strike", width=65, anchor="e")
        self.option_tree.column("side", width=45, anchor="center")
        self.option_tree.column("price_rub", width=80, anchor="e")
        self.option_tree.column("price_pct", width=65, anchor="e")
        self.option_tree.pack(side="left", fill="both", expand=True)

        option_vsb = ttk.Scrollbar(option_frame, orient="vertical", command=self.option_tree.yview)
        option_vsb.pack(side="right", fill="y")
        self.option_tree.configure(yscrollcommand=option_vsb.set)

        # Кнопка копирования теперь ПОД таблицей результатов
        option_tree_frame.pack(side="top", fill="both", expand=True)
        # Затем упаковываем кнопку ПОД ней
        ttk.Button(option_frame, text="📋 Копировать опционы", command=self.copy_option_table_to_clipboard).pack(pady=(5, 0), side="top", fill="x")

        self.option_tree.bind("<Control-c>", lambda e: self.copy_option_table_to_clipboard())

    def on_currency_change(self, event=None):
        """Обновляет дефолтные значения ставок, волатильности и страйка при смене валюты"""
        currency = self.currency_var.get()
        if currency == "USD":
            self.rd_var.set(0.15)
            self.rf_var.set(0.045)
            self.vol_var.set(0.12)
            self.strike_var.set(90.0)
        elif currency == "EUR":
            self.rd_var.set(0.15)
            self.rf_var.set(0.03)
            self.vol_var.set(0.10)
            self.strike_var.set(110.0)
        elif currency == "CNY":
            self.rd_var.set(0.15)
            self.rf_var.set(0.02)
            self.vol_var.set(0.08)
            self.strike_var.set(13.0)

    def calculate_ndf(self):
        """Запускает расчет NDF в отдельном потоке, чтобы не блокировать GUI"""
        def worker():
            try:
                step_value = self.step_days_var.get()  # Получаем выбранное значение как строку

                # Определяем, является ли шаг месячным или дневным
                if step_value == "1M":
                    step_days = -1  # Специальное значение-флаг для месячного шага
                else:
                    step_days = int(step_value)  # Преобразуем в int для дневных шагов
                    if step_days <= 0:
                        raise ValueError("Шаг должен быть больше 0 дней.")

                pricer = NDFPricing(proxy=self.proxy)
                # Основной расчет — с пользовательским шагом
                self.ndf_results = pricer.pricing(
                    currency=self.currency_var.get(),
                    start_date=self.start_date_var.get(),
                    end_date=self.end_date_var.get(),
                    step_days=step_days,
                    use_anchor=self.use_anchor_var.get()
                )
                # Дополнительный расчет — строго с шагом 1 месяц (как в вашем примере)
                self.ndf_monthly_results = pricer.pricing_monthly(
                    currency=self.currency_var.get(),
                    start_date=self.start_date_var.get(),
                    end_date=self.end_date_var.get()
                )
                real_data = getattr(self.ndf_results, 'real_data', pd.DataFrame())
                # Обновление GUI в основном потоке
                self.root.after(0, self._update_gui_after_ndf_calculation, real_data)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при расчете NDF:\n{e}"))

        # Запуск в отдельном потоке
        threading.Thread(target=worker, daemon=True).start()

    def _update_gui_after_ndf_calculation(self, real_data):
        """Обновляет все элементы GUI в основном потоке (после завершения расчета NDF)"""
        # Clear previous tables
        for item in self.ndf_tree.get_children():
            self.ndf_tree.delete(item)
        for item in self.ndf_monthly_tree.get_children():
            self.ndf_monthly_tree.delete(item)
        for item in self.real_tree.get_children():
            self.real_tree.delete(item)

        # Получаем данные
        spot_value = self.ndf_results['SPOT'].iloc[0]
        currency = self.currency_var.get()

        # Форматируем спот в зависимости от валюты
        if currency == 'USD':
            spot_display = f"Спот фьюч USDF: {self.format_rub(spot_value / 1000)}"
        elif currency == 'EUR':
            spot_display = f"Спот фьюч EURF: {self.format_rub(spot_value / 1000)}"
        elif currency == 'CNY':
            spot_display = f"Спот MOEX: {self.format_rub(spot_value)}"
        else:
            spot_display = f"Спот: {self.format_rub(spot_value)}"

        # Форматируем последний NDF форвард
        forward_last = self.ndf_results['forward_price'].iloc[-1]
        if currency in ['USD', 'EUR']:
            forward_last /= 1000
        forward_formatted = self.format_rub(forward_last)

        # Получаем своп-дифф для последней даты (в %)
        last_swpdiff_pct = (self.ndf_results['swpdiff'].iloc[-1] * 100).round(2)
        swpdiff_sign = "+" if last_swpdiff_pct >= 0 else ""
        swpdiff_display = f"{swpdiff_sign}{last_swpdiff_pct}%"

        # Обновляем лейбл
        self.spot_label.config(text=f"{spot_display} | NDF (на {self.end_date_var.get()}): {forward_formatted} | Своп дифф: {swpdiff_display}")
        self.spot = spot_value / 1000 if currency in ['USD', 'EUR'] else spot_value

        # Очистка графиков
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Подготовка данных
        normalized_prices = self.ndf_results['forward_price'].copy()
        normalized_swpdiff = self.ndf_results['swpdiff'].copy()
        if currency in ['USD', 'EUR']:
            normalized_prices /= 1000

        dates = self.ndf_results['date']

        # График 1: Курс (форвард)
        def format_y_price(val, pos):
            return self.format_rub(val).replace(",00", "")

        self.ax1.yaxis.set_major_formatter(FuncFormatter(format_y_price))
        self.ax1.plot(dates, normalized_prices, marker='o', linestyle='-', linewidth=2, markersize=5, color='tab:blue')
        self.ax1.set_title(f"Форвард {currency}/RUB", fontsize=10, fontweight='bold')
        self.ax1.set_xlabel("Дата")
        self.ax1.set_ylabel("Курс (RUB)")
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        self.ax1.tick_params(axis='x', rotation=30)

        # График 2: Интерполированный своп-дифф
        def format_y_swpdiff(val, pos):
            return f"{val:.2f}%"

        self.ax2.yaxis.set_major_formatter(FuncFormatter(format_y_swpdiff))
        self.ax2.plot(dates, (normalized_swpdiff * 100).round(2), marker='s', linestyle='-', linewidth=2, markersize=5, color='tab:orange')
        self.ax2.set_title("Своп дифф (интерполяция)", fontsize=10, fontweight='bold')
        self.ax2.set_xlabel("Дата")
        self.ax2.set_ylabel("Своп дифф (%)")
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        self.ax2.tick_params(axis='x', rotation=30)

        # График 3: Реальные данные — включая якорную ставку как обычный фьючерс
        if not real_data.empty:
            real_data_sorted = real_data.sort_values('date').reset_index(drop=True)
            real_dates = pd.to_datetime(real_data_sorted['date'])
            real_swpdiff_pct = real_data_sorted['swpdiff_pct']

            valid_mask = real_dates.notna() & real_swpdiff_pct.notna()
            real_dates = real_dates[valid_mask]
            real_swpdiff_pct = real_swpdiff_pct[valid_mask]

            self.ax3.plot(real_dates, real_swpdiff_pct, marker='D', linestyle='-', linewidth=2, markersize=6, color='gray')

            # УДАЛИЛИ ЛЕГЕНДУ "ФЬЮЧЕРСЫ" — по вашему требованию
            # Никакого self.ax3.legend()!

        self.ax3.yaxis.set_major_formatter(FuncFormatter(format_y_swpdiff))
        self.ax3.set_title("Реальные своп-дифф (исходные фьючерсы)", fontsize=10, fontweight='bold')
        self.ax3.set_xlabel("Дата")
        self.ax3.set_ylabel("Своп дифф (%)")
        self.ax3.grid(True, linestyle='--', alpha=0.5)
        self.ax3.tick_params(axis='x', rotation=30)

        self.figure.tight_layout()
        self.canvas_plot.draw()

        # Заполнение основной таблицы NDF
        for _, row in self.ndf_results.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            swpdiff_display = f"{(row['swpdiff'] * 100):.2f}%"
            forward_display = self.format_rub(row['forward_price'] / 1000 if currency in ['USD', 'EUR'] else row['forward_price'])
            self.ndf_tree.insert("", "end", values=(date_str, swpdiff_display, forward_display))

        # Заполнение таблицы NDF с месячным шагом
        for _, row in self.ndf_monthly_results.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            swpdiff_display = f"{(row['swpdiff'] * 100):.2f}%"
            forward_display = self.format_rub(row['forward_price'] / 1000 if currency in ['USD', 'EUR'] else row['forward_price'])
            self.ndf_monthly_tree.insert("", "end", values=(date_str, swpdiff_display, forward_display))

        # Заполнение таблицы реальных данных
        for _, row in real_data.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            swpdiff_display = f"{row['swpdiff_pct']:.4f}%"
            forward_display = self.format_rub(row['forward_price'] / 1000 if currency in ['USD', 'EUR'] else row['forward_price'])
            self.real_tree.insert("", "end", values=(date_str, swpdiff_display, forward_display))

    def calculate_option(self):
        if self.spot is None:
            messagebox.showwarning("Внимание", "Сначала рассчитайте NDF, чтобы получить спот!")
            return
        try:
            start_dt = pd.to_datetime(self.start_date_var.get())
            end_dt = pd.to_datetime(self.end_date_var.get())
            step_value = self.step_days_var.get()

            # Определяем, является ли шаг месячным или дневным
            if step_value == "1M":
                # Для месячного шага, генерируем список дат с помощью pd.date_range
                dates_list = pd.date_range(start=start_dt, end=end_dt, freq=pd.DateOffset(months=1)).tolist()
                if dates_list[-1] != end_dt:
                    dates_list.append(end_dt)
            else:
                step_days = int(step_value)
                if (end_dt - start_dt).days <= 0:
                    raise ValueError("Конечная дата должна быть позже начальной.")
                dates_list = []
                current = start_dt
                while current <= end_dt:
                    dates_list.append(current)
                    current += pd.Timedelta(days=step_days)
                if dates_list[-1] != end_dt:
                    dates_list.append(end_dt)

            dates = pd.DatetimeIndex(dates_list)
            today = pd.Timestamp.today().normalize()
            tenors = (dates - today).days / 365
            for item in self.option_tree.get_children():
                self.option_tree.delete(item)
            for date, T in zip(dates, tenors):
                if T <= 0:
                    continue
                opt = FXOption(
                    spot=self.spot,
                    strike=self.strike_var.get(),
                    T=T,
                    rd=self.rd_var.get(),
                    rf=self.rf_var.get(),
                    vol=self.vol_var.get(),
                    side=self.side_var.get()
                )
                price_rub = opt.price()
                price_pct = price_rub / self.spot * 100
                date_str = date.strftime('%Y-%m-%d')
                tenor_str = f"{T:.4f}"
                strike_str = f"{self.strike_var.get():.3f}"
                side_str = self.side_var.get()
                price_rub_str = self.format_rub(price_rub)
                price_pct_str = f"{price_pct:.4f}%"
                self.option_tree.insert("", "end", values=(
                    date_str,
                    tenor_str,
                    strike_str,
                    side_str,
                    price_rub_str,
                    price_pct_str
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете опционов:\n{e}")

    def copy_ndf_table_to_clipboard(self):
        if not self.ndf_tree.get_children():
            return

        headers = ["Дата", "Своп дифф (%)", "Форвард (RUB)"]
        rows = [ "\t".join(headers) ]
        for item in self.ndf_tree.get_children():
            values = self.ndf_tree.item(item)['values']
            date_str = str(values[0])
            swpdiff_clean = str(values[1]).replace("%", "").strip()
            try:
                swpdiff_float = float(swpdiff_clean) / 100
            except:
                swpdiff_float = 0.0
            swpdiff_str = f"{swpdiff_float:.6f}"
            forward_str = str(values[2]).replace(" ", "").replace(",", ".")
            rows.append("\t".join([date_str, swpdiff_str, forward_str]))

        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(rows))
        self.root.update()

    def copy_ndf_monthly_table_to_clipboard(self):
        if not self.ndf_monthly_tree.get_children():
            return

        headers = ["Дата", "Своп дифф (%)", "Форвард (RUB)"]
        rows = [ "\t".join(headers) ]
        for item in self.ndf_monthly_tree.get_children():
            values = self.ndf_monthly_tree.item(item)['values']
            date_str = str(values[0])
            swpdiff_clean = str(values[1]).replace("%", "").strip()
            try:
                swpdiff_float = float(swpdiff_clean) / 100
            except:
                swpdiff_float = 0.0
            swpdiff_str = f"{swpdiff_float:.6f}"
            forward_str = str(values[2]).replace(" ", "").replace(",", ".")
            rows.append("\t".join([date_str, swpdiff_str, forward_str]))

        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(rows))
        self.root.update()

    def copy_real_table_to_clipboard(self):
        if not self.real_tree.get_children():
            return

        headers = ["Дата", "Своп дифф (%)", "Форвард (RUB)"]
        rows = [ "\t".join(headers) ]
        for item in self.real_tree.get_children():
            values = self.real_tree.item(item)['values']
            date_str = str(values[0])
            swpdiff_clean = str(values[1]).replace("%", "").strip()
            try:
                swpdiff_float = float(swpdiff_clean) / 100
            except:
                swpdiff_float = 0.0
            swpdiff_str = f"{swpdiff_float:.6f}"
            forward_str = str(values[2]).replace(" ", "").replace(",", ".")
            rows.append("\t".join([date_str, swpdiff_str, forward_str]))

        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(rows))
        self.root.update()

    def copy_option_table_to_clipboard(self):
        if not self.option_tree.get_children():
            return

        headers = ["Дата", "Срок (лет)", "Страйк", "Тип", "Цена (RUB)", "Цена (%)"]
        rows = [ "\t".join(headers) ]
        for item in self.option_tree.get_children():
            values = self.option_tree.item(item)['values']
            date_str = str(values[0])
            tenor_str = str(values[1])
            strike_str = str(values[2])
            side_str = str(values[3])
            rub_str = str(values[4]).replace(" ", "").replace(",", ".")
            pct_str = str(values[5]).replace("%", "").strip()
            rows.append("\t".join([date_str, tenor_str, strike_str, side_str, rub_str, pct_str]))

        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(rows))
        self.root.update()

    def on_closing(self):
        try:
            if hasattr(self, 'canvas_plot'):
                self.canvas_plot.get_tk_widget().destroy()
                del self.canvas_plot
            if hasattr(self, 'figure'):
                plt.close(self.figure)
                del self.figure
            plt.close('all')
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"⚠️ Ошибка при закрытии: {e}")
            self.root.quit()
            self.root.destroy()

    def cleanup(self):
        plt.close('all')


# ========================
# Запуск приложения
# ========================
if __name__ == "__main__":
    proxy = get_proxy_from_login()
    if not proxy:
        print("❌ Приложение закрыто пользователем.")
        exit(0)

    root = tk.Tk()
    app = NDFApp(root, proxy)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    atexit.register(app.cleanup)
    root.mainloop()