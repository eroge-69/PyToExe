import sys
import json
import urllib.request
import urllib.parse
import csv
import math
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os

class ModernStyle:
    """Современные стили для интерфейса"""
    COLORS = {
        'primary': '#2E86AB',
        'secondary': '#A23B72',
        'success': '#F18F01',
        'danger': '#C73E1D',
        'warning': '#FF6B35',
        'info': '#4ECDC4',
        'light': '#F7F7F7',
        'dark': '#2C3E50',
        'white': '#FFFFFF',
        'gray': '#95A5A6'
    }
    
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'subtitle': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 10),
        'button': ('Segoe UI', 11, 'bold')
    }

class BinanceDataFetcher:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    def get_all_symbols(self):
        """Получает все торговые пары с Binance"""
        try:
            url = f"{self.base_url}/exchangeInfo"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                symbols = []
                for symbol_info in data['symbols']:
                    if symbol_info['status'] == 'TRADING' and symbol_info['quoteAsset'] == 'USDT':
                        symbols.append(symbol_info['symbol'])
                return symbols
        except Exception as e:
            print(f"Ошибка при получении символов: {e}")
            return []
    
    def get_klines(self, symbol, interval='1d', limit=100):
        """Получает исторические данные для символа"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            with urllib.request.urlopen(full_url) as response:
                data = json.loads(response.read().decode())
                
                # Преобразуем данные в список словарей
                klines = []
                for kline in data:
                    klines.append({
                        'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[5])
                    })
                return klines
        except Exception as e:
            print(f"Ошибка при получении данных для {symbol}: {e}")
            return None

class TechnicalAnalyzer:
    def __init__(self):
        self.rules = {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'sma_short': 10,
            'sma_long': 50
        }
    
    def calculate_sma(self, prices, period):
        """Рассчитывает Simple Moving Average"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_rsi(self, prices, period=14):
        """Рассчитывает RSI"""
        if len(prices) < period + 1:
            return None
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return None
            
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Рассчитывает Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
            
        sma = self.calculate_sma(prices, period)
        if sma is None:
            return None, None, None
            
        # Рассчитываем стандартное отклонение
        variance = sum((price - sma) ** 2 for price in prices[-period:]) / period
        std = math.sqrt(variance)
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    def analyze_signals(self, klines):
        """Анализирует сигналы на основе технических индикаторов"""
        if len(klines) < 50:
            return None
            
        prices = [kline['close'] for kline in klines]
        volumes = [kline['volume'] for kline in klines]
        
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'strength': 0,
            'recommendation': 'HOLD',
            'buy_price': None,
            'sell_price': None,
            'stop_loss': None,
            'take_profit': None,
            'rules_applied': []
        }
        
        current_price = prices[-1]
        previous_price = prices[-2]
        
        # RSI анализ
        rsi = self.calculate_rsi(prices)
        if rsi is not None:
            if rsi < 30:
                signals['buy_signals'].append(f"RSI перепродан ({rsi:.2f})")
                signals['strength'] += 2
                signals['rules_applied'].append("RSI < 30: Сильный сигнал на покупку")
            elif rsi > 70:
                signals['sell_signals'].append(f"RSI перекуплен ({rsi:.2f})")
                signals['strength'] -= 2
                signals['rules_applied'].append("RSI > 70: Сильный сигнал на продажу")
        
        # Moving Average анализ
        sma_short = self.calculate_sma(prices, 10)
        sma_long = self.calculate_sma(prices, 50)
        
        if sma_short is not None and sma_long is not None:
            if len(prices) >= 51:
                prev_sma_short = self.calculate_sma(prices[:-1], 10)
                prev_sma_long = self.calculate_sma(prices[:-1], 50)
                
                if prev_sma_short is not None and prev_sma_long is not None:
                    if sma_short > sma_long and prev_sma_short <= prev_sma_long:
                        signals['buy_signals'].append("Краткосрочная SMA пересекла долгосрочную снизу вверх")
                        signals['strength'] += 1
                        signals['rules_applied'].append("SMA 10 > SMA 50: Сигнал на покупку")
                    elif sma_short < sma_long and prev_sma_short >= prev_sma_long:
                        signals['sell_signals'].append("Краткосрочная SMA пересекла долгосрочную сверху вниз")
                        signals['strength'] -= 1
                        signals['rules_applied'].append("SMA 10 < SMA 50: Сигнал на продажу")
        
        # Bollinger Bands анализ
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
        if bb_upper is not None and bb_lower is not None:
            if current_price <= bb_lower:
                signals['buy_signals'].append("Цена касается нижней полосы Боллинджера")
                signals['strength'] += 1
                signals['rules_applied'].append("Цена <= нижняя полоса Боллинджера: Сигнал на покупку")
            elif current_price >= bb_upper:
                signals['sell_signals'].append("Цена касается верхней полосы Боллинджера")
                signals['strength'] -= 1
                signals['rules_applied'].append("Цена >= верхняя полоса Боллинджера: Сигнал на продажу")
        
        # Volume анализ
        if len(volumes) >= 20:
            avg_volume = sum(volumes[-20:]) / 20
            current_volume = volumes[-1]
            
            if current_volume > avg_volume * 1.5:
                if current_price > previous_price:
                    signals['buy_signals'].append("Высокий объем при росте цены")
                    signals['strength'] += 1
                    signals['rules_applied'].append("Объем > 1.5x среднего при росте: Сигнал на покупку")
                else:
                    signals['sell_signals'].append("Высокий объем при падении цены")
                    signals['strength'] -= 1
                    signals['rules_applied'].append("Объем > 1.5x среднего при падении: Сигнал на продажу")
        
        # Определение рекомендации
        if signals['strength'] >= 3:
            signals['recommendation'] = 'STRONG_BUY'
            signals['buy_price'] = current_price * 0.98
            signals['stop_loss'] = current_price * 0.95
            signals['take_profit'] = current_price * 1.10
        elif signals['strength'] >= 1:
            signals['recommendation'] = 'BUY'
            signals['buy_price'] = current_price * 0.99
            signals['stop_loss'] = current_price * 0.96
            signals['take_profit'] = current_price * 1.08
        elif signals['strength'] <= -3:
            signals['recommendation'] = 'STRONG_SELL'
            signals['sell_price'] = current_price * 1.02
            signals['stop_loss'] = current_price * 1.05
            signals['take_profit'] = current_price * 0.90
        elif signals['strength'] <= -1:
            signals['recommendation'] = 'SELL'
            signals['sell_price'] = current_price * 1.01
            signals['stop_loss'] = current_price * 1.04
            signals['take_profit'] = current_price * 0.92
        else:
            signals['recommendation'] = 'HOLD'
        
        return signals

class ModernCryptoAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Анализатор Криптовалют Binance - Современная версия")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernStyle.COLORS['light'])
        
        # Устанавливаем иконку
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.fetcher = BinanceDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.results = []
        self.analysis_running = False
        
        self.init_ui()
        
    def init_ui(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок с современным дизайном
        header_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['primary'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚀 Анализатор Криптовалют Binance", 
                              font=ModernStyle.FONTS['title'], 
                              bg=ModernStyle.COLORS['primary'], 
                              fg=ModernStyle.COLORS['white'])
        title_label.pack(expand=True)
        
        # Кнопки управления с современным дизайном
        button_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['light'])
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Стили для кнопок
        button_style = {
            'font': ModernStyle.FONTS['button'],
            'borderwidth': 0,
            'relief': 'flat',
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2'
        }
        
        self.start_button = tk.Button(button_frame, text="▶️ Начать Анализ", 
                                     command=self.start_analysis, 
                                     bg=ModernStyle.COLORS['success'], 
                                     fg=ModernStyle.COLORS['white'],
                                     **button_style)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Остановить", 
                                    command=self.stop_analysis, 
                                    bg=ModernStyle.COLORS['danger'], 
                                    fg=ModernStyle.COLORS['white'],
                                    **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_button.config(state=tk.DISABLED)
        
        # Прогресс бар с современным дизайном
        progress_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['light'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400, style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack()
        
        # Статус
        self.status_label = tk.Label(progress_frame, text="Готов к анализу", 
                                    font=ModernStyle.FONTS['body'],
                                    bg=ModernStyle.COLORS['light'],
                                    fg=ModernStyle.COLORS['dark'])
        self.status_label.pack(pady=(5, 0))
        
        # Создаем notebook для вкладок с современным стилем
        style = ttk.Style()
        style.theme_use('clam')
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка результатов
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📊 Результаты Анализа")
        
        # Таблица результатов с дополнительными колонками
        columns = ("Символ", "Цена", "Изменение 24ч", "Объем", "RSI", 
                  "Рекомендация", "Сила", "Комментарий")
        
        # Создаем Treeview с современным стилем
        tree_frame = tk.Frame(self.results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        column_widths = {
            "Символ": 100,
            "Цена": 120,
            "Изменение 24ч": 120,
            "Объем": 120,
            "RSI": 80,
            "Рекомендация": 120,
            "Сила": 80,
            "Комментарий": 300
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=column_widths.get(col, 120), minwidth=80)
        
        # Скроллбары
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Размещение таблицы
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Двойной клик для перехода к детальному анализу
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Вкладка детального анализа
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="🔍 Детальный Анализ")
        
        # Выбор символа
        symbol_frame = tk.Frame(self.detail_frame, bg=ModernStyle.COLORS['light'])
        symbol_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(symbol_frame, text="Выберите символ:", 
                font=ModernStyle.FONTS['subtitle'],
                bg=ModernStyle.COLORS['light']).pack(side=tk.LEFT)
        
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(symbol_frame, textvariable=self.symbol_var, 
                                        state="readonly", width=20, font=ModernStyle.FONTS['body'])
        self.symbol_combo.pack(side=tk.LEFT, padx=10)
        self.symbol_combo.bind('<<ComboboxSelected>>', self.show_detailed_analysis)
        
        # Текстовое поле для детального анализа
        self.detail_text = scrolledtext.ScrolledText(self.detail_frame, height=30, width=80,
                                                    font=ModernStyle.FONTS['body'],
                                                    bg=ModernStyle.COLORS['white'],
                                                    fg=ModernStyle.COLORS['dark'])
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Вкладка настроек с подробным описанием
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Настройки")
        
        # Создаем скроллируемый фрейм для настроек
        settings_canvas = tk.Canvas(self.settings_frame, bg=ModernStyle.COLORS['light'])
        settings_scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=settings_canvas.yview)
        settings_scrollable_frame = tk.Frame(settings_canvas, bg=ModernStyle.COLORS['light'])
        
        settings_scrollable_frame.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )
        
        settings_canvas.create_window((0, 0), window=settings_scrollable_frame, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        
        # Настройки RSI с подробным описанием
        rsi_frame = tk.LabelFrame(settings_scrollable_frame, text="📈 Настройки RSI (Relative Strength Index)", 
                                 font=ModernStyle.FONTS['subtitle'],
                                 bg=ModernStyle.COLORS['light'],
                                 fg=ModernStyle.COLORS['dark'],
                                 padx=20, pady=20)
        rsi_frame.pack(fill=tk.X, padx=20, pady=10)
        
        rsi_desc = tk.Text(rsi_frame, height=8, wrap=tk.WORD, font=ModernStyle.FONTS['body'],
                          bg=ModernStyle.COLORS['white'], fg=ModernStyle.COLORS['dark'])
        rsi_desc.insert(tk.END, """
RSI (Relative Strength Index) - это осциллятор импульса, который измеряет скорость и изменение ценовых движений.

🔍 КАК РАБОТАЕТ RSI:
• RSI колеблется от 0 до 100
• Значения выше 70 указывают на перекупленность (возможное падение цены)
• Значения ниже 30 указывают на перепроданность (возможный рост цены)
• RSI = 100 - (100 / (1 + RS)), где RS = средний рост / среднее падение

📊 ПРАВИЛА ТОРГОВЛИ:
• RSI < 30: Сильный сигнал на покупку (актив перепродан)
• RSI > 70: Сильный сигнал на продажу (актив перекуплен)
• RSI = 50: Нейтральная зона

⚙️ НАСТРОЙКИ:
""")
        rsi_desc.config(state=tk.DISABLED)
        rsi_desc.pack(fill=tk.X, pady=(0, 10))
        
        # Контролы RSI
        rsi_controls = tk.Frame(rsi_frame, bg=ModernStyle.COLORS['light'])
        rsi_controls.pack(fill=tk.X)
        
        tk.Label(rsi_controls, text="Перепродан (сигнал на покупку):", 
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['light']).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.rsi_oversold_var = tk.IntVar(value=30)
        tk.Spinbox(rsi_controls, from_=10, to=40, textvariable=self.rsi_oversold_var, 
                  width=10, font=ModernStyle.FONTS['body']).grid(row=0, column=1, padx=5)
        
        tk.Label(rsi_controls, text="Перекуплен (сигнал на продажу):", 
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['light']).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.rsi_overbought_var = tk.IntVar(value=70)
        tk.Spinbox(rsi_controls, from_=60, to=90, textvariable=self.rsi_overbought_var, 
                  width=10, font=ModernStyle.FONTS['body']).grid(row=1, column=1, padx=5)
        
        # Настройки Moving Averages с подробным описанием
        ma_frame = tk.LabelFrame(settings_scrollable_frame, text="📊 Moving Averages (Скользящие Средние)", 
                                font=ModernStyle.FONTS['subtitle'],
                                bg=ModernStyle.COLORS['light'],
                                fg=ModernStyle.COLORS['dark'],
                                padx=20, pady=20)
        ma_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ma_desc = tk.Text(ma_frame, height=10, wrap=tk.WORD, font=ModernStyle.FONTS['body'],
                         bg=ModernStyle.COLORS['white'], fg=ModernStyle.COLORS['dark'])
        ma_desc.insert(tk.END, """
Moving Averages (MA) - это технические индикаторы, которые показывают среднюю цену актива за определенный период.

🔍 КАК РАБОТАЮТ MA:
• SMA (Simple Moving Average) = сумма цен за период / количество периодов
• Краткосрочная MA более чувствительна к изменениям цены
• Долгосрочная MA показывает общий тренд
• Пересечение MA дает торговые сигналы

📊 ПРАВИЛА ТОРГОВЛИ:
• Краткосрочная MA > Долгосрочная MA: Восходящий тренд (сигнал на покупку)
• Краткосрочная MA < Долгосрочная MA: Нисходящий тренд (сигнал на продажу)
• Золотой крест: краткосрочная MA пересекает долгосрочную снизу вверх
• Мертвый крест: краткосрочная MA пересекает долгосрочную сверху вниз

⚙️ НАСТРОЙКИ:
""")
        ma_desc.config(state=tk.DISABLED)
        ma_desc.pack(fill=tk.X, pady=(0, 10))
        
        # Контролы MA
        ma_controls = tk.Frame(ma_frame, bg=ModernStyle.COLORS['light'])
        ma_controls.pack(fill=tk.X)
        
        tk.Label(ma_controls, text="Краткосрочная SMA (период):", 
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['light']).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.sma_short_var = tk.IntVar(value=10)
        tk.Spinbox(ma_controls, from_=5, to=20, textvariable=self.sma_short_var, 
                  width=10, font=ModernStyle.FONTS['body']).grid(row=0, column=1, padx=5)
        
        tk.Label(ma_controls, text="Долгосрочная SMA (период):", 
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['light']).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.sma_long_var = tk.IntVar(value=50)
        tk.Spinbox(ma_controls, from_=20, to=200, textvariable=self.sma_long_var, 
                  width=10, font=ModernStyle.FONTS['body']).grid(row=1, column=1, padx=5)
        
        # Описание других индикаторов
        other_frame = tk.LabelFrame(settings_scrollable_frame, text="📈 Другие Технические Индикаторы", 
                                   font=ModernStyle.FONTS['subtitle'],
                                   bg=ModernStyle.COLORS['light'],
                                   fg=ModernStyle.COLORS['dark'],
                                   padx=20, pady=20)
        other_frame.pack(fill=tk.X, padx=20, pady=10)
        
        other_desc = tk.Text(other_frame, height=12, wrap=tk.WORD, font=ModernStyle.FONTS['body'],
                            bg=ModernStyle.COLORS['white'], fg=ModernStyle.COLORS['dark'])
        other_desc.insert(tk.END, """
🔍 BOLLINGER BANDS (Полосы Боллинджера):
• Состоят из трех линий: верхняя, средняя (SMA), нижняя
• Верхняя и нижняя линии = SMA ± (2 × стандартное отклонение)
• Цена касается верхней полосы = перекупленность (сигнал на продажу)
• Цена касается нижней полосы = перепроданность (сигнал на покупку)

📊 VOLUME ANALYSIS (Анализ Объема):
• Высокий объем подтверждает силу движения цены
• Объем > 1.5x среднего при росте = сильный сигнал на покупку
• Объем > 1.5x среднего при падении = сильный сигнал на продажу

💡 ОБЩИЕ ПРАВИЛА ТОРГОВЛИ:
• Всегда используйте стоп-лоссы для управления рисками
• Не инвестируйте больше, чем можете позволить себе потерять
• Диверсифицируйте портфель (не кладите все яйца в одну корзину)
• Следите за объемом торгов - он подтверждает тренды
• Учитывайте рыночные тренды и новости
• Технический анализ - это инструмент, а не гарантия

⚠️ ВАЖНО: Эта программа предназначена только для информационных целей. 
Всегда проводите собственный анализ и управляйте рисками!
""")
        other_desc.config(state=tk.DISABLED)
        other_desc.pack(fill=tk.X)
        
        # Размещаем canvas и scrollbar
        settings_canvas.pack(side="left", fill="both", expand=True)
        settings_scrollbar.pack(side="right", fill="y")
        
    def on_tree_double_click(self, event):
        """Обработчик двойного клика по таблице"""
        item = self.tree.selection()[0]
        symbol = self.tree.item(item, "values")[0]
        self.symbol_var.set(symbol)
        self.notebook.select(1)  # Переключаемся на вкладку детального анализа
        self.show_detailed_analysis()
        
    def start_analysis(self):
        if self.analysis_running:
            return
            
        self.analysis_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text="Получение списка торговых пар...")
        
        # Запускаем анализ в отдельном потоке
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
        
    def stop_analysis(self):
        self.analysis_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Анализ остановлен")
        
    def run_analysis(self):
        try:
            # Получаем все символы
            symbols = self.fetcher.get_all_symbols()
            if not symbols:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось получить список торговых пар"))
                self.root.after(0, self.stop_analysis)
                return
            
            self.root.after(0, lambda: self.status_label.config(text=f"Найдено {len(symbols)} торговых пар"))
            
            results = []
            total_symbols = len(symbols)
            
            for i, symbol in enumerate(symbols):
                if not self.analysis_running:
                    break
                    
                try:
                    # Получаем данные
                    klines = self.fetcher.get_klines(symbol, interval='1d', limit=100)
                    if klines is None or len(klines) < 50:
                        continue
                    
                    # Анализируем сигналы
                    signals = self.analyzer.analyze_signals(klines)
                    if signals is None:
                        continue
                    
                    # Рассчитываем изменение за 24 часа
                    change_24h = 0
                    if len(klines) >= 2:
                        change_24h = ((klines[-1]['close'] - klines[-2]['close']) / klines[-2]['close']) * 100
                    
                    # Формируем комментарий
                    comment = self.generate_comment(signals, klines[-1]['close'])
                    
                    # Добавляем результат
                    result = {
                        'symbol': symbol,
                        'current_price': klines[-1]['close'],
                        'change_24h': change_24h,
                        'volume_24h': klines[-1]['volume'],
                        'rsi': self.analyzer.calculate_rsi([k['close'] for k in klines]),
                        'recommendation': signals['recommendation'],
                        'strength': signals['strength'],
                        'buy_signals': signals['buy_signals'],
                        'sell_signals': signals['sell_signals'],
                        'buy_price': signals['buy_price'],
                        'sell_price': signals['sell_price'],
                        'stop_loss': signals['stop_loss'],
                        'take_profit': signals['take_profit'],
                        'rules_applied': signals['rules_applied'],
                        'comment': comment
                    }
                    
                    results.append(result)
                    
                    # Обновляем прогресс
                    progress = (i + 1) / total_symbols * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    self.root.after(0, lambda s=symbol: self.status_label.config(text=f"Анализ: {s}"))
                    
                    # Небольшая задержка чтобы не перегружать API
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Ошибка при анализе {symbol}: {e}")
                    continue
            
            # Сортируем результаты по силе сигнала
            results.sort(key=lambda x: abs(x['strength']), reverse=True)
            
            self.root.after(0, lambda: self.analysis_complete(results))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка: {e}"))
            self.root.after(0, self.stop_analysis)
    
    def generate_comment(self, signals, current_price):
        """Генерирует комментарий для торговой пары"""
        if signals['recommendation'] == 'STRONG_BUY':
            return f"СРОЧНО ПОКУПАТЬ по ${current_price:.6f}, продавать по ${signals['take_profit']:.6f}"
        elif signals['recommendation'] == 'BUY':
            return f"Покупать по ${signals['buy_price']:.6f}, продавать по ${signals['take_profit']:.6f}"
        elif signals['recommendation'] == 'STRONG_SELL':
            return f"СРОЧНО ПРОДАВАТЬ по ${current_price:.6f}, покупать по ${signals['take_profit']:.6f}"
        elif signals['recommendation'] == 'SELL':
            return f"Продавать по ${signals['sell_price']:.6f}, покупать по ${signals['take_profit']:.6f}"
        else:
            return "Держать позицию, ждать лучших сигналов"
    
    def analysis_complete(self, results):
        self.results = results
        self.display_results()
        self.update_symbol_combo()
        
        self.analysis_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Анализ завершен. Проанализировано {len(results)} торговых пар.")
        
        messagebox.showinfo("Завершено", f"Анализ завершен.\nПроанализировано {len(results)} торговых пар.")
    
    def display_results(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем результаты
        for result in self.results:
            rsi_text = f"{result['rsi']:.2f}" if result['rsi'] is not None else "N/A"
            
            values = (
                result['symbol'],
                f"${result['current_price']:.6f}",
                f"{result['change_24h']:+.2f}%",
                f"{result['volume_24h']:.2f}",
                rsi_text,
                result['recommendation'],
                str(result['strength']),
                result['comment']
            )
            
            item = self.tree.insert('', 'end', values=values)
            
            # Цветовая маркировка
            if result['recommendation'] in ['STRONG_BUY', 'BUY']:
                self.tree.set(item, 'Рекомендация', result['recommendation'])
            elif result['recommendation'] in ['STRONG_SELL', 'SELL']:
                self.tree.set(item, 'Рекомендация', result['recommendation'])
    
    def update_symbol_combo(self):
        symbols = [result['symbol'] for result in self.results]
        self.symbol_combo['values'] = symbols
        if symbols:
            self.symbol_combo.set(symbols[0])
    
    def show_detailed_analysis(self, event=None):
        symbol = self.symbol_var.get()
        if not symbol or not self.results:
            return
        
        # Находим результат для выбранного символа
        result = next((r for r in self.results if r['symbol'] == symbol), None)
        if not result:
            return
        
        # Форматируем RSI правильно
        rsi_text = f"{result['rsi']:.2f}" if result['rsi'] is not None else "N/A"
        rsi_status = ""
        if result['rsi'] is not None:
            if result['rsi'] < 30:
                rsi_status = "(Перепродан)"
            elif result['rsi'] > 70:
                rsi_status = "(Перекуплен)"
            else:
                rsi_status = "(Нейтральный)"
        
        analysis_text = f"""
🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ДЛЯ {symbol}
{'='*60}

📊 ТЕКУЩИЕ ДАННЫЕ:
• Текущая цена: ${result['current_price']:.6f}
• Изменение за 24 часа: {result['change_24h']:+.2f}%
• Объем торгов: {result['volume_24h']:.2f}

📈 ТЕХНИЧЕСКИЕ ИНДИКАТОРЫ:
• RSI: {rsi_text} {rsi_status}

🎯 РЕКОМЕНДАЦИЯ: {result['recommendation']}
💪 Сила сигнала: {result['strength']}

📋 ПРАВИЛА, КОТОРЫМ СЛЕДОВАЛА ПРОГРАММА:
"""
        
        if result['rules_applied']:
            for rule in result['rules_applied']:
                analysis_text += f"• {rule}\n"
        else:
            analysis_text += "• Нет активных правил\n"
            
        analysis_text += f"""
💰 СИГНАЛЫ НА ПОКУПКУ:
"""
        
        if result['buy_signals']:
            for signal in result['buy_signals']:
                analysis_text += f"• {signal}\n"
        else:
            analysis_text += "• Нет сигналов на покупку\n"
            
        analysis_text += f"""
📉 СИГНАЛЫ НА ПРОДАЖУ:
"""
        
        if result['sell_signals']:
            for signal in result['sell_signals']:
                analysis_text += f"• {signal}\n"
        else:
            analysis_text += "• Нет сигналов на продажу\n"
            
        # Форматируем цены правильно
        buy_price_text = f"${result['buy_price']:.6f}" if result['buy_price'] else "Не применимо"
        sell_price_text = f"${result['sell_price']:.6f}" if result['sell_price'] else "Не применимо"
        stop_loss_text = f"${result['stop_loss']:.6f}" if result['stop_loss'] else "Не применимо"
        take_profit_text = f"${result['take_profit']:.6f}" if result['take_profit'] else "Не применимо"
        
        analysis_text += f"""
💵 ЦЕНОВЫЕ УРОВНИ:
• Рекомендуемая цена покупки: {buy_price_text}
• Рекомендуемая цена продажи: {sell_price_text}
• Стоп-лосс: {stop_loss_text}
• Тейк-профит: {take_profit_text}

💬 КОММЕНТАРИЙ: {result['comment']}

⚠️ ВАЖНО: Эта программа предназначена только для информационных целей. 
Всегда проводите собственный анализ и управляйте рисками!
"""
        
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, analysis_text)
    
    def sort_treeview(self, col):
        """Сортировка таблицы по колонке"""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort()
        
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
    
    def run(self):
        self.root.mainloop()

def main():
    app = ModernCryptoAnalyzerGUI()
    app.run()

if __name__ == '__main__':
    main() 