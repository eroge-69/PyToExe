import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import time
from datetime import datetime
from collections import defaultdict, deque
from pocketoptionapi_async import AsyncPocketOptionClient

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ᴏᴛᴇᴄᴀɴᴏɴɪᴍᴀ - Торговый анализатор")
        self.root.geometry("1800x900")
        self.root.configure(bg='#0d1117')

        # Variables
        self.client = None
        self.is_running = False
        self.loop = None
        self.thread = None

        # Price data storage
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.current_prices = {}
        self.price_changes = {}
        self.volume_data = defaultdict(float)
        self.timeframe_data = defaultdict(dict)

        # Assets to monitor
        self.assets = [
            "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc",
            "USDCAD_otc", "USDCHF_otc", "NZDUSD_otc", "EURGBP_otc",
            "EURJPY_otc", "GBPJPY_otc", "XAUUSD_otc", "BTCUSD_otc"
        ]

        # Timeframes for analysis
        self.timeframes = [60, 300, 900]

        # Setup dark theme
        self.setup_dark_theme()

        # Create main layout
        self.create_main_layout()

    def setup_dark_theme(self):
        """Setup dark theme for the application"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure dark colors
        style.configure('TLabel', background='#0d1117', foreground='#ffffff')
        style.configure('TFrame', background='#0d1117')
        style.configure('TEntry', background='#21262d', foreground='#ffffff', fieldbackground='#21262d')
        style.configure('TButton', background='#238636', foreground='#ffffff')
        style.map('TButton', background=[('active', '#2ea043')])
        style.configure('Treeview', background='#21262d', foreground='#ffffff', fieldbackground='#21262d')
        style.configure('Treeview.Heading', background='#30363d', foreground='#ffffff')
        style.configure('TCombobox', background='#21262d', foreground='#ffffff', fieldbackground='#21262d')

    def create_main_layout(self):
        """Create main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top control panel
        self.create_control_panel(main_frame)

        # Create order book window
        windows_frame = ttk.Frame(main_frame)
        windows_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.create_order_book_window(windows_frame)

    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.LabelFrame(parent, text="Управление подключением", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # SSID input
        ssid_frame = ttk.Frame(control_frame)
        ssid_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ssid_frame, text="SSID PocketOption:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.ssid_entry = ttk.Entry(ssid_frame, width=80, font=('Consolas', 10))
        self.ssid_entry.pack(fill=tk.X, pady=(5, 0))

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_button = ttk.Button(button_frame, text="🚀 Запустить анализ", command=self.start_order_book)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(button_frame, text="⏹️ Остановить", command=self.stop_order_book, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        self.ssid_help_button = ttk.Button(button_frame, text="❓ Как получить SSID?", command=self.show_ssid_help)
        self.ssid_help_button.pack(side=tk.LEFT)

        # Status
        status_frame = ttk.Frame(button_frame)
        status_frame.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(status_frame, text="⏸️ Статус: Остановлен", 
                                    foreground="#f85149", font=('Arial', 10, 'bold'))
        self.status_label.pack()

    def create_order_book_window(self, parent):
        """Create order book window"""
        order_book_frame = ttk.LabelFrame(parent, text="Анализ рынка в реальном времени", padding=10)
        order_book_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Актив", "Текущая цена", "Изменение", "Процент", "M1", "M5", "M15", "Сигнал", "Объем", "Время")
        self.order_book_tree = ttk.Treeview(order_book_frame, columns=columns, show="headings", height=20)

        column_widths = {
            "Актив": 120, "Текущая цена": 100, "Изменение": 80, "Процент": 70,
            "M1": 60, "M5": 60, "M15": 60, "Сигнал": 80, "Объем": 80, "Время": 80
        }

        for col in columns:
            self.order_book_tree.heading(col, text=col)
            self.order_book_tree.column(col, width=column_widths.get(col, 80))

        order_book_scrollbar = ttk.Scrollbar(order_book_frame, orient=tk.VERTICAL, command=self.order_book_tree.yview)
        self.order_book_tree.configure(yscrollcommand=order_book_scrollbar.set)

        self.order_book_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        order_book_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_ssid_help(self):
        """Show SSID help window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Инструкция по получению SSID")
        help_window.geometry("800x600")
        help_window.configure(bg='#0d1117')

        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, bg='#21262d', fg='#ffffff', font=('Consolas', 10), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        help_text = """ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ SSID ДЛЯ POCKETOPTION API

1. Откройте PocketOption в браузере и войдите в аккаунт
2. Нажмите F12 для открытия инструментов разработчика
3. Перейдите на вкладку Network (Сеть)
4. В фильтре выберите WS (WebSocket)
5. Перейдите на любую торговую страницу
6. Найдите сообщение начинающееся с: 42["auth"
7. Скопируйте ПОЛНОЕ сообщение целиком

ПРИМЕР ПРАВИЛЬНОГО SSID:
42["auth",{"session":"ваш_session_id","isDemo":1,"uid":12345,"platform":1}]

ВАЖНО:
- Копируйте ВСЁ сообщение целиком, не только session_id
- isDemo:1 = демо счет, isDemo:0 = реальный счет
- Не делитесь SSID с другими людьми
- SSID может истечь, тогда нужно получить новый

РЕШЕНИЕ ПРОБЛЕМ:
- Если не видите WebSocket сообщения, обновите страницу после открытия F12
- Если SSID не работает, проверьте что скопировали полное сообщение
- Попробуйте получить новый SSID если старый не работает"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        close_button = ttk.Button(help_window, text="Закрыть", command=help_window.destroy)
        close_button.pack(pady=10)

    def start_order_book(self):
        """Start the order book monitoring"""
        if not self.ssid_entry.get():
            messagebox.showerror("Ошибка", "Введите SSID")
            return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Статус: Подключение...", foreground="#f9826c")

        self.thread = threading.Thread(target=self.run_order_book_monitor, daemon=True)
        self.thread.start()

    def stop_order_book(self):
        """Stop the order book monitoring"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Статус: Остановлен", foreground="#f85149")

        if self.client:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)

    def run_order_book_monitor(self):
        """Run the order book monitoring in async loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.order_book_main())

    async def order_book_main(self):
        """Main order book monitoring logic"""
        try:
            ssid = self.ssid_entry.get().strip()
            self.client = AsyncPocketOptionClient(ssid, is_demo=True, enable_logging=True)

            connected = await self.client.connect()
            if not connected:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось подключиться к PocketOption"))
                self.root.after(0, lambda: self.status_label.config(text="Статус: Ошибка подключения", foreground="#f85149"))
                return

            self.root.after(0, lambda: self.status_label.config(text="Статус: Активен", foreground="#56d364"))
            await self.start_asset_monitoring()

        except Exception as e:
            error_msg = f"Ошибка мониторинга: {e}"
            self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="Статус: Ошибка", foreground="#f85149"))

    async def start_asset_monitoring(self):
        """Start monitoring all assets"""
        tasks = []
        for asset in self.assets:
            for timeframe in self.timeframes:
                task = asyncio.create_task(self.monitor_asset_timeframe(asset, timeframe))
                tasks.append(task)

        update_task = asyncio.create_task(self.update_gui_loop())
        tasks.append(update_task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def monitor_asset_timeframe(self, asset, timeframe):
        """Monitor prices for a specific asset and timeframe"""
        last_price = None

        while self.is_running:
            try:
                candles = await self.client.get_candles(asset, timeframe, 5)
                if candles and len(candles) > 0:
                    current_candle = candles[-1]
                    current_price = current_candle.close
                    current_time = datetime.now()

                    if last_price is not None:
                        price_change = current_price - last_price
                        percent_change = (price_change / last_price) * 100 if last_price != 0 else 0

                        self.timeframe_data[asset][timeframe] = {
                            'price': current_price,
                            'change': price_change,
                            'percent': percent_change,
                            'volume': current_candle.volume,
                            'time': current_time,
                            'trend': self.calculate_trend(candles)
                        }

                        if timeframe == 60:
                            self.current_prices[asset] = current_price
                            self.price_changes[asset] = {
                                'change': price_change,
                                'percent': percent_change,
                                'time': current_time
                            }
                            self.volume_data[asset] = current_candle.volume

                            self.price_history[asset].append({
                                'time': current_time,
                                'price': current_price,
                                'change': price_change,
                                'percent': percent_change,
                                'volume': current_candle.volume
                            })

                    last_price = current_price

                if timeframe == 60:
                    await asyncio.sleep(2)
                elif timeframe == 300:
                    await asyncio.sleep(10)
                else:
                    await asyncio.sleep(30)

            except Exception as e:
                print(f"Ошибка мониторинга {asset} {timeframe}s: {e}")
                await asyncio.sleep(5)

    def calculate_trend(self, candles):
        """Calculate trend direction based on candles"""
        if len(candles) < 3:
            return "HOLD"

        prices = [c.close for c in candles[-3:]]

        if prices[-1] > prices[-2] > prices[-3]:
            return "CALL"
        elif prices[-1] < prices[-2] < prices[-3]:
            return "PUT"
        else:
            return "HOLD"

    def generate_trading_signal(self, asset):
        """Generate trading signal based on multiple timeframes"""
        if asset not in self.timeframe_data:
            return "WAIT"

        trends = {}
        for tf in self.timeframes:
            if tf in self.timeframe_data[asset]:
                trends[tf] = self.timeframe_data[asset][tf].get('trend', 'HOLD')

        if len(set(trends.values())) == 1:
            trend = list(trends.values())[0]
            if trend in ['CALL', 'PUT']:
                return trend

        if trends.get(300) == trends.get(900) and trends.get(300) in ['CALL', 'PUT']:
            return trends.get(300)

        return "WAIT"

    async def update_gui_loop(self):
        """Update GUI periodically"""
        while self.is_running:
            try:
                self.root.after(0, self.update_order_book_display)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Ошибка обновления GUI: {e}")
                await asyncio.sleep(1)

    def update_order_book_display(self):
        """Update order book display with enhanced data"""
        for item in self.order_book_tree.get_children():
            self.order_book_tree.delete(item)

        for asset in self.assets:
            if asset in self.current_prices:
                price = self.current_prices[asset]
                change_data = self.price_changes.get(asset, {})
                change = change_data.get('change', 0)
                percent = change_data.get('percent', 0)
                time_str = change_data.get('time', datetime.now()).strftime("%H:%M:%S")
                volume = self.volume_data.get(asset, 0)

                m1_trend = "—"
                m5_trend = "—"
                m15_trend = "—"

                if asset in self.timeframe_data:
                    if 60 in self.timeframe_data[asset]:
                        m1_trend = self.timeframe_data[asset][60].get('trend', '—')
                    if 300 in self.timeframe_data[asset]:
                        m5_trend = self.timeframe_data[asset][300].get('trend', '—')
                    if 900 in self.timeframe_data[asset]:
                        m15_trend = self.timeframe_data[asset][900].get('trend', '—')

                signal = self.generate_trading_signal(asset)

                change_str = f"{change:+.5f}" if change != 0 else "0.00000"
                percent_str = f"{percent:+.2f}%" if percent != 0 else "0.00%"
                volume_str = f"{volume:.0f}" if volume > 0 else "0"

                item = self.order_book_tree.insert("", "end", values=(
                    asset, f"{price:.5f}", change_str, percent_str,
                    m1_trend, m5_trend, m15_trend, signal, volume_str, time_str
                ))

                tags = []
                if change > 0:
                    tags.append("positive")
                elif change < 0:
                    tags.append("negative")

                if signal == "CALL":
                    tags.append("call_signal")
                elif signal == "PUT":
                    tags.append("put_signal")

                if tags:
                    self.order_book_tree.item(item, tags=tags)

        self.order_book_tree.tag_configure("positive", foreground="#56d364")
        self.order_book_tree.tag_configure("negative", foreground="#f85149")
        self.order_book_tree.tag_configure("call_signal", background="#1f4529")
        self.order_book_tree.tag_configure("put_signal", background="#4a1e1e")

def main():
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()