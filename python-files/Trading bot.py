import threading
import time
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.animation import Animation
import ccxt
import math
import json

# Konfigurasi file untuk menyimpan API keys
CONFIG_FILE = 'trading_bot_config.json'

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.8, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(40)
        self.font_size = dp(12)  # Ukuran font default
        self.bind(width=self.adjust_font_size)
        
    def adjust_font_size(self, instance, width):
        # Menyesuaikan ukuran font berdasarkan lebar button
        if width > 0:
            # Hitung ukuran font berdasarkan lebar button dan panjang teks
            text_length = len(self.text)
            if text_length > 0:
                # Formula sederhana untuk menyesuaikan font size
                calculated_size = max(dp(10), min(dp(14), width / (text_length * 0.8)))
                self.font_size = calculated_size
    
    def on_press(self):
        # Efek animasi saat button ditekan
        anim = Animation(background_color=(0.1, 0.4, 0.6, 1), duration=0.1) + \
               Animation(background_color=(0.2, 0.6, 0.8, 1), duration=0.1)
        anim.start(self)
        return super().on_press()

class TradingBotGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Status trading
        self.is_trading = False
        self.buy_orders = []
        self.sell_orders = []
        self.exchange = None
        self.current_price = 0
        self.trade_history = []
        self.market_info = None
        self.fdusd_pairs = []  # Daftar pair FDUSD
        
        # Parameter default
        self.params = {
            'trade_amount': 15,
            'buy_discount': 0.15,
            'sell_profit': 0.3,
            'max_buy_orders': 1,
            'wait_time_minutes': 30,
            'min_trade_amount': 10,
            'base_coin': 'BNB',
            'quote_coin': 'FDUSD'
        }
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        # Header dengan background color
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        header = Label(
            text='BINANCE SPOT TRADING BOT', 
            size_hint_y=0.07, 
            font_size=dp(20), 
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(header)
        
        # Tab panel
        self.tab_panel = TabbedPanel(
            do_default_tab=False, 
            size_hint_y=0.7,
            tab_width=dp(120)
        )
        
        # Tab 1: API Configuration
        api_tab = TabbedPanelItem(text='API Settings')
        api_content = GridLayout(cols=1, spacing=dp(10), padding=dp(10), size_hint_y=None)
        api_content.bind(minimum_height=api_content.setter('height'))
        
        api_content.add_widget(Label(
            text='Konfigurasi API Binance', 
            size_hint_y=None, 
            height=dp(30), 
            bold=True,
            color=(0, 0, 0, 1)
        ))
        
        # API Key Input
        api_key_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        api_key_layout.add_widget(Label(text='API Key:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.api_key_input = TextInput(text='', password=False, multiline=False, size_hint_x=0.7)
        api_key_layout.add_widget(self.api_key_input)
        api_content.add_widget(api_key_layout)
        
        # Secret Key Input
        secret_key_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        secret_key_layout.add_widget(Label(text='Secret Key:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.secret_key_input = TextInput(text='', password=True, multiline=False, size_hint_x=0.7)
        secret_key_layout.add_widget(self.secret_key_input)
        api_content.add_widget(secret_key_layout)
        
        # Test API Connection Button
        test_api_button = CustomButton(text='Test Koneksi API')
        test_api_button.bind(on_press=self.test_api_connection)
        api_content.add_widget(test_api_button)
        
        # Load Markets Button
        load_markets_button = CustomButton(text='Load Market FDUSD')
        load_markets_button.bind(on_press=self.load_fdusd_markets)
        api_content.add_widget(load_markets_button)
        
        # Save API Keys Button
        save_api_button = CustomButton(text='Simpan API Keys')
        save_api_button.bind(on_press=self.save_api_keys)
        api_content.add_widget(save_api_button)
        
        api_tab.add_widget(api_content)
        self.tab_panel.add_widget(api_tab)
        
        # Tab 2: Trading Parameters
        trading_tab = TabbedPanelItem(text='Trading Settings')
        trading_content = GridLayout(cols=1, spacing=dp(10), padding=dp(10), size_hint_y=None)
        trading_content.bind(minimum_height=trading_content.setter('height'))
        
        trading_content.add_widget(Label(
            text='Parameter Trading', 
            size_hint_y=None, 
            height=dp(30), 
            bold=True,
            color=(0, 0, 0, 1)
        ))
        
        # Coin Pair Selection
        pair_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        pair_layout.add_widget(Label(text='Pilih Pair Coin:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        
        self.pair_spinner = Spinner(
            text='Pilih Pair',
            values=['Klik Load Market FDUSD dulu'],
            size_hint_x=0.7,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        self.pair_spinner.bind(text=self.on_pair_selected)
        pair_layout.add_widget(self.pair_spinner)
        trading_content.add_widget(pair_layout)
        
        # Manual Pair Input (sebagai fallback)
        manual_pair_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        manual_pair_layout.add_widget(Label(text='Manual Input Pair:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        manual_input_layout = BoxLayout(orientation='horizontal', size_hint_x=0.7)
        self.base_coin_input = TextInput(text=self.params['base_coin'], multiline=False, size_hint_x=0.4, hint_text='Base coin')
        self.quote_coin_input = TextInput(text=self.params['quote_coin'], multiline=False, size_hint_x=0.4, hint_text='Quote coin')
        manual_input_layout.add_widget(self.base_coin_input)
        manual_input_layout.add_widget(Label(text='/', size_hint_x=0.2, color=(0, 0, 0, 1)))
        manual_input_layout.add_widget(self.quote_coin_input)
        manual_pair_layout.add_widget(manual_input_layout)
        trading_content.add_widget(manual_pair_layout)
        
        # Trade amount
        trade_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        trade_layout.add_widget(Label(text='Jumlah Trade:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.trade_amount_input = TextInput(text=str(self.params['trade_amount']), multiline=False, size_hint_x=0.7)
        trade_layout.add_widget(self.trade_amount_input)
        trading_content.add_widget(trade_layout)
        
        # Buy discount
        buy_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        buy_layout.add_widget(Label(text='Diskon Beli (%):', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.buy_discount_input = TextInput(text=str(self.params['buy_discount']), multiline=False, size_hint_x=0.7)
        buy_layout.add_widget(self.buy_discount_input)
        trading_content.add_widget(buy_layout)
        
        # Sell profit
        sell_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        sell_layout.add_widget(Label(text='Profit Jual (%):', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.sell_profit_input = TextInput(text=str(self.params['sell_profit']), multiline=False, size_hint_x=0.7)
        sell_layout.add_widget(self.sell_profit_input)
        trading_content.add_widget(sell_layout)
        
        # Max buy orders
        max_buy_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        max_buy_layout.add_widget(Label(text='Max Order Beli:', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.max_buy_input = TextInput(text=str(self.params['max_buy_orders']), multiline=False, size_hint_x=0.7)
        max_buy_layout.add_widget(self.max_buy_input)
        trading_content.add_widget(max_buy_layout)
        
        # Wait time
        wait_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        wait_layout.add_widget(Label(text='Waktu Tunggu (menit):', size_hint_x=0.3, color=(0, 0, 0, 1)))
        self.wait_time_input = TextInput(text=str(self.params['wait_time_minutes']), multiline=False, size_hint_x=0.7)
        wait_layout.add_widget(self.wait_time_input)
        trading_content.add_widget(wait_layout)
        
        trading_tab.add_widget(trading_content)
        self.tab_panel.add_widget(trading_tab)
        
        # Tab 3: Real-time Trading
        realtime_tab = TabbedPanelItem(text='Real-time')
        realtime_content = GridLayout(cols=1, spacing=dp(10), padding=dp(10))
        
        # Current Price
        price_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        price_layout.add_widget(Label(text='Harga Saat Ini:', size_hint_x=0.4, color=(0, 0, 0, 1)))
        self.price_label = Label(text='0.00', size_hint_x=0.6, color=(0, 0.5, 0, 1), bold=True)
        price_layout.add_widget(self.price_label)
        realtime_content.add_widget(price_layout)
        
        # Market Info
        market_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        market_layout.add_widget(Label(text='Info Market:', size_hint_x=0.4, color=(0, 0, 0, 1)))
        self.market_info_label = Label(text='Belum di-load', size_hint_x=0.6, color=(0.5, 0, 0.5, 1))
        market_layout.add_widget(self.market_info_label)
        realtime_content.add_widget(market_layout)
        
        # Active Orders
        realtime_content.add_widget(Label(
            text='Order Aktif:', 
            size_hint_y=None, 
            height=dp(30), 
            bold=True,
            color=(0, 0, 0, 1)
        ))
        
        self.orders_label = Label(
            text='Tidak ada order aktif', 
            size_hint_y=None, 
            height=dp(100),
            color=(0, 0, 0, 1)
        )
        realtime_content.add_widget(self.orders_label)
        
        # Trade History
        realtime_content.add_widget(Label(
            text='Riwayat Trading:', 
            size_hint_y=None, 
            height=dp(30), 
            bold=True,
            color=(0, 0, 0, 1)
        ))
        
        self.history_scroll = ScrollView(size_hint_y=0.4)
        self.history_label = Label(
            text='Belum ada transaksi', 
            size_hint_y=None,
            color=(0, 0, 0, 1)
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        self.history_scroll.add_widget(self.history_label)
        realtime_content.add_widget(self.history_scroll)
        
        realtime_tab.add_widget(realtime_content)
        self.tab_panel.add_widget(realtime_tab)
        
        self.add_widget(self.tab_panel)
        
        # Status area
        status_area = GridLayout(cols=2, rows=2, size_hint_y=0.15, spacing=dp(5))
        
        # Balance display
        self.balance_label = Label(
            text='Saldo: Loading...', 
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        status_area.add_widget(self.balance_label)
        
        # Status display
        self.status_label = Label(
            text='Status: Tidak aktif', 
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        status_area.add_widget(self.status_label)
        
        # Pair info
        self.pair_label = Label(
            text='Pair: -/-', 
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        status_area.add_widget(self.pair_label)
        
        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.start_button = CustomButton(text='Mulai Trading')
        self.start_button.bind(on_press=self.start_trading)
        self.start_button.disabled = True
        button_layout.add_widget(self.start_button)
        
        self.stop_button = CustomButton(text='Hentikan Trading')
        self.stop_button.bind(on_press=self.stop_trading)
        self.stop_button.disabled = True
        button_layout.add_widget(self.stop_button)
        
        self.update_button = CustomButton(text='Perbarui Data')
        self.update_button.bind(on_press=self.update_data)
        self.update_button.disabled = True
        button_layout.add_widget(self.update_button)
        
        # Tombol: Tutup Semua Order
        self.cancel_all_button = CustomButton(text='Tutup Semua Order')
        self.cancel_all_button.bind(on_press=self.cancel_all_orders)
        self.cancel_all_button.disabled = True
        button_layout.add_widget(self.cancel_all_button)
        
        status_area.add_widget(button_layout)
        self.add_widget(status_area)
        
        # Schedule periodic updates
        Clock.schedule_interval(self.update_display, 2)
        
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        
    def load_fdusd_markets(self, instance):
        """Load semua market FDUSD dari Binance"""
        if not self.initialize_exchange():
            return
            
        try:
            self.status_label.text = "Status: Sedang memuat market FDUSD..."
            
            # Load semua markets
            markets = self.exchange.load_markets()
            
            # Filter hanya market dengan FDUSD sebagai quote currency
            fdusd_pairs = []
            for symbol, market in markets.items():
                if market['quote'] == 'FDUSD' and market['active']:
                    # Format: BTC/FDUSD
                    pair_display = f"{market['base']}/{market['quote']}"
                    fdusd_pairs.append((pair_display, symbol))
            
            # Sort secara alphabet
            fdusd_pairs.sort(key=lambda x: x[0])
            
            # Simpan daftar pair
            self.fdusd_pairs = fdusd_pairs
            
            # Update spinner values
            spinner_values = [pair[0] for pair in fdusd_pairs]
            if not spinner_values:
                spinner_values = ['Tidak ada market FDUSD ditemukan']
            
            self.pair_spinner.values = spinner_values
            self.pair_spinner.text = 'Pilih Pair FDUSD'
            
            self.status_label.text = f"Status: Ditemukan {len(fdusd_pairs)} market FDUSD"
            self.show_ok_popup(f"Berhasil memuat {len(fdusd_pairs)} market FDUSD")
            
        except Exception as e:
            self.show_error(f"Error memuat market FDUSD: {str(e)}")
    
    def on_pair_selected(self, spinner, text):
        """Handle ketika pair dipilih dari spinner"""
        if text != 'Pilih Pair FDUSD' and text != 'Klik Load Market FDUSD dulu':
            # Split pair menjadi base dan quote coin
            parts = text.split('/')
            if len(parts) == 2:
                self.base_coin_input.text = parts[0]
                self.quote_coin_input.text = parts[1]
                self.update_parameters()
                self.status_label.text = f"Status: Pair dipilih - {text}"
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                if 'api_key' in config:
                    self.api_key_input.text = config['api_key']
                if 'secret_key' in config:
                    self.secret_key_input.text = config['secret_key']
                if 'params' in config:
                    self.params.update(config['params'])
                    self.trade_amount_input.text = str(self.params['trade_amount'])
                    self.buy_discount_input.text = str(self.params['buy_discount'])
                    self.sell_profit_input.text = str(self.params['sell_profit'])
                    self.max_buy_input.text = str(self.params['max_buy_orders'])
                    self.wait_time_input.text = str(self.params['wait_time_minutes'])
                    self.base_coin_input.text = self.params['base_coin']
                    self.quote_coin_input.text = self.params['quote_coin']
                    
                self.pair_label.text = f'Pair: {self.params["base_coin"]}/{self.params["quote_coin"]}'
                    
        except Exception as e:
            self.show_error(f"Error loading config: {str(e)}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'api_key': self.api_key_input.text,
                'secret_key': self.secret_key_input.text,
                'params': {
                    'trade_amount': float(self.trade_amount_input.text),
                    'buy_discount': float(self.buy_discount_input.text),
                    'sell_profit': float(self.sell_profit_input.text),
                    'max_buy_orders': int(self.max_buy_input.text),
                    'wait_time_minutes': int(self.wait_time_input.text),
                    'min_trade_amount': 10,
                    'base_coin': self.base_coin_input.text.upper(),
                    'quote_coin': self.quote_coin_input.text.upper()
                }
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            self.show_error(f"Error saving config: {str(e)}")
    
    def initialize_exchange(self):
        """Initialize exchange with API keys"""
        try:
            api_key = self.api_key_input.text.strip()
            secret_key = self.secret_key_input.text.strip()
            
            if not api_key or not secret_key:
                raise ValueError("API Key dan Secret Key harus diisi")
                
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            return True
        except Exception as e:
            self.show_error(f"Error initializing exchange: {str(e)}")
            return False
    
    def get_symbol(self):
        """Get formatted symbol"""
        return f"{self.params['base_coin']}/{self.params['quote_coin']}"
    
    def load_market_info(self):
        """Load market information for the symbol"""
        try:
            symbol = self.get_symbol()
            self.market_info = self.exchange.market(symbol)
            
            min_amount = self.market_info['limits']['amount']['min']
            min_cost = self.market_info['limits']['cost']['min']
            price_precision = self.market_info['precision']['price']
            amount_precision = self.market_info['precision']['amount']
            
            info_text = f"Min: {min_amount} {self.params['base_coin']}, Cost: {min_cost} {self.params['quote_coin']}"
            self.market_info_label.text = info_text
            
        except Exception as e:
            self.market_info_label.text = "Error loading market info"
    
    def test_api_connection(self, instance):
        """Test API connection"""
        if self.initialize_exchange():
            try:
                # Test connection by fetching balance
                balance = self.exchange.fetch_balance()
                self.status_label.text = "Status: Koneksi API berhasil!"
                self.start_button.disabled = False
                self.update_button.disabled = False
                self.cancel_all_button.disabled = False
                self.load_market_info()
                self.update_data()
                self.show_ok_popup("Koneksi API berhasil!")
            except Exception as e:
                error_msg = str(e)
                if "API-key format invalid" in error_msg:
                    self.show_error("Format API Key tidak valid")
                elif "Invalid API-key" in error_msg:
                    self.show_error("API Key tidak valid")
                elif "Signature" in error_msg:
                    self.show_error("Secret Key tidak valid")
                else:
                    self.show_error(f"Koneksi API gagal: {error_msg}")
                self.start_button.disabled = True
                self.update_button.disabled = True
                self.cancel_all_button.disabled = True
    
    def save_api_keys(self, instance):
        """Save API keys to config file"""
        self.save_config()
        self.show_ok_popup("API Keys berhasil disimpan!")
    
    def update_data(self, instance=None):
        """Update all data"""
        if self.exchange:
            self.update_balance()
            self.update_price()
            self.update_orders()
    
    def update_display(self, dt):
        if self.is_trading and self.exchange:
            self.update_price()
            self.update_orders()
            self.trading_logic()
            
    def update_price(self):
        if not self.exchange:
            return
            
        try:
            symbol = self.get_symbol()
            ticker = self.exchange.fetch_ticker(symbol)
            self.current_price = ticker['last']
            self.price_label.text = f'{self.current_price:.4f}'
        except Exception as e:
            self.show_error(f"Error mengambil harga: {str(e)}")
    
    def update_balance(self):
        if not self.exchange:
            return
            
        try:
            balance = self.exchange.fetch_balance()
            quote_balance = balance.get(self.params['quote_coin'], {}).get('free', 0)
            base_balance = balance.get(self.params['base_coin'], {}).get('free', 0)
            
            self.balance_label.text = f'{self.params["quote_coin"]}: {float(quote_balance):.2f} | {self.params["base_coin"]}: {float(base_balance):.6f}'
        except Exception as e:
            self.show_error(f"Error mengambil saldo: {str(e)}")
    
    def update_orders(self):
        if not self.exchange:
            return
            
        try:
            symbol = self.get_symbol()
            open_orders = self.exchange.fetch_open_orders(symbol)
            
            # Filter buy and sell orders
            self.buy_orders = [o for o in open_orders if o['side'] == 'buy']
            self.sell_orders = [o for o in open_orders if o['side'] == 'sell']
            
            # Update orders display
            orders_text = f"BUY Orders: {len(self.buy_orders)}\n"
            for order in self.buy_orders:
                orders_text += f"BUY: {float(order['amount']):.4f} @ {float(order['price']):.4f} ({order['status']})\n"
            
            orders_text += f"\nSELL Orders: {len(self.sell_orders)}\n"
            for order in self.sell_orders:
                orders_text += f"SELL: {float(order['amount']):.4f} @ {float(order['price']):.4f} ({order['status']})\n"
                    
            self.orders_label.text = orders_text if orders_text else "Tidak ada order aktif"
            
        except Exception as e:
            self.show_error(f"Error mengambil order: {str(e)}")
    
    def add_trade_history(self, message):
        """Add trade to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.trade_history.append(f"[{timestamp}] {message}")
        
        # Keep only last 10 history entries
        if len(self.trade_history) > 10:
            self.trade_history = self.trade_history[-10:]
        
        self.history_label.text = "\n".join(self.trade_history)
        self.history_label.texture_update()
    
    def trading_logic(self):
        if not self.exchange:
            return
            
        try:
            # Update parameters from UI
            self.update_parameters()
            
            # Cancel old buy orders
            self.cancel_old_orders()
            
            # PERBAIKAN: Jangan buat order buy jika masih ada sell order aktif
            if len(self.sell_orders) > 0:
                self.add_trade_history("Masih ada order SELL aktif, skip order BUY")
                return
            
            # Create buy orders if we have less than max and no pending sell orders
            if len(self.buy_orders) < self.params['max_buy_orders']:
                self.place_buy_order()
            
            # Create sell orders for filled buy orders
            self.place_sell_orders()
            
        except Exception as e:
            self.show_error(f"Error trading logic: {str(e)}")
    
    def update_parameters(self):
        try:
            self.params['trade_amount'] = float(self.trade_amount_input.text)
            self.params['buy_discount'] = float(self.buy_discount_input.text)
            self.params['sell_profit'] = float(self.sell_profit_input.text)
            self.params['max_buy_orders'] = int(self.max_buy_input.text)
            self.params['wait_time_minutes'] = int(self.wait_time_input.text)
            self.params['base_coin'] = self.base_coin_input.text.upper()
            self.params['quote_coin'] = self.quote_coin_input.text.upper()
            
            self.pair_label.text = f'Pair: {self.params["base_coin"]}/{self.params["quote_coin"]}'
        except ValueError:
            self.show_error("Parameter tidak valid. Pastikan semua nilai angka.")
    
    def cancel_old_orders(self):
        try:
            now = datetime.now()
            symbol = self.get_symbol()
            
            for order in self.buy_orders:
                order_time = self.exchange.parse8601(order['datetime'])
                order_age = now - datetime.fromtimestamp(order_time / 1000)
                
                if order_age > timedelta(minutes=self.params['wait_time_minutes']):
                    result = self.exchange.cancel_order(order['id'], symbol)
                    self.add_trade_history(f"Order BUY dibatalkan: {order['id']}")
                    self.show_ok_popup(f"Order BUY dibatalkan: {order['id']}")
                    self.update_orders()
                    
        except Exception as e:
            self.show_error(f"Error membatalkan order: {str(e)}")
    
    def cancel_all_orders(self, instance):
        """Cancel semua order yang aktif"""
        if not self.exchange:
            return
            
        try:
            symbol = self.get_symbol()
            open_orders = self.exchange.fetch_open_orders(symbol)
            
            if not open_orders:
                self.show_ok_popup("Tidak ada order aktif untuk dibatalkan")
                return
            
            cancelled_count = 0
            for order in open_orders:
                try:
                    self.exchange.cancel_order(order['id'], symbol)
                    cancelled_count += 1
                    self.add_trade_history(f"Order {order['side']} dibatalkan: {order['id']}")
                except Exception as e:
                    self.add_trade_history(f"Gagal membatalkan order {order['id']}: {str(e)}")
            
            self.update_orders()
            self.show_ok_popup(f"Berhasil membatalkan {cancelled_count} order")
            
        except Exception as e:
            self.show_error(f"Error membatalkan semua order: {str(e)}")
    
    def place_buy_order(self):
        try:
            symbol = self.get_symbol()
            
            # Load market info untuk precision
            market = self.exchange.market(symbol)
            min_amount = market['limits']['amount']['min']
            min_cost = market['limits']['cost']['min']
            
            # Calculate buy price with discount
            buy_price = self.current_price * (1 - self.params['buy_discount'] / 100)
            
            # Calculate amount based on trade amount
            amount = self.params['trade_amount'] / buy_price
            
            # Apply precision
            buy_price = float(self.exchange.price_to_precision(symbol, buy_price))
            amount = float(self.exchange.amount_to_precision(symbol, amount))
            
            # Check minimum amount
            if amount < min_amount:
                self.add_trade_history(f"Amount terlalu kecil. Min: {min_amount}")
                return
                
            # Check minimum cost
            if amount * buy_price < min_cost:
                self.add_trade_history(f"Cost terlalu kecil. Min: {min_cost}")
                return
            
            # Check balance
            balance = self.exchange.fetch_balance()
            quote_balance = balance.get(self.params['quote_coin'], {}).get('free', 0)
            
            if amount * buy_price > quote_balance:
                self.add_trade_history(f"Balance {self.params['quote_coin']} tidak cukup")
                return
                
            # Place buy order
            order = self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='buy',
                amount=amount,
                price=buy_price,
                params={'timeInForce': 'GTC'}
            )
            
            message = f"BUY Order: {amount:.4f} {self.params['base_coin']} @ {buy_price:.4f}"
            self.add_trade_history(message)
            self.show_ok_popup(message)
            self.update_orders()
            
        except Exception as e:
            error_msg = str(e)
            if "Account has insufficient balance" in error_msg:
                self.add_trade_history("Balance tidak cukup untuk order BUY")
            elif "Filter failure: MIN_NOTIONAL" in error_msg:
                self.add_trade_history("Jumlah order terlalu kecil")
            else:
                self.show_error(f"Error membuat order beli: {error_msg}")
    
    def place_sell_orders(self):
        try:
            symbol = self.get_symbol()
            
            # Check if we have any base coin to sell
            balance = self.exchange.fetch_balance()
            base_balance = balance.get(self.params['base_coin'], {}).get('free', 0)
            
            if base_balance <= 0:
                return
                
            # Load market info untuk precision
            market = self.exchange.market(symbol)
            min_amount = market['limits']['amount']['min']
            
            if base_balance < min_amount:
                self.add_trade_history(f"Balance {self.params['base_coin']} terlalu kecil. Min: {min_amount}")
                return
            
            # Calculate sell price with profit
            sell_price = self.current_price * (1 + self.params['sell_profit'] / 100)
            sell_price = float(self.exchange.price_to_precision(symbol, sell_price))
            
            # Place sell order (Good Till Canceled)
            order = self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='sell',
                amount=base_balance,
                price=sell_price,
                params={'timeInForce': 'GTC'}
            )
            
            message = f"SELL Order: {base_balance:.4f} {self.params['base_coin']} @ {sell_price:.4f}"
            self.add_trade_history(message)
            self.show_ok_popup(message)
            self.update_orders()
                
        except Exception as e:
            error_msg = str(e)
            if "Account has insufficient balance" in error_msg:
                self.add_trade_history("Balance tidak cukup untuk order SELL")
            elif "Filter failure: MIN_NOTIONAL" in error_msg:
                self.add_trade_history("Jumlah order terlalu kecil")
            else:
                self.show_error(f"Error membuat order jual: {error_msg}")
    
    def start_trading(self, instance):
        if not self.initialize_exchange():
            return
            
        try:
            # Validate API connection
            self.exchange.fetch_balance()
            
            self.is_trading = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_label.text = "Status: Trading aktif"
            
            # Save config
            self.save_config()
            
            # Start trading thread
            self.trading_thread = threading.Thread(target=self.trading_loop)
            self.trading_thread.daemon = True
            self.trading_thread.start()
            
            self.show_ok_popup("Trading dimulai!")
            
        except Exception as e:
            self.show_error(f"Error memulai trading: {str(e)}")
    
    def stop_trading(self, instance):
        """Hentikan trading dan cancel semua order buy"""
        try:
            self.is_trading = False
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.status_label.text = "Status: Trading dihentikan"
            
            # Cancel semua order buy yang aktif
            if self.exchange:
                symbol = self.get_symbol()
                open_orders = self.exchange.fetch_open_orders(symbol)
                
                buy_orders = [o for o in open_orders if o['side'] == 'buy']
                
                if buy_orders:
                    cancelled_count = 0
                    for order in buy_orders:
                        try:
                            self.exchange.cancel_order(order['id'], symbol)
                            cancelled_count += 1
                            self.add_trade_history(f"Order BUY dibatalkan: {order['id']}")
                        except Exception as e:
                            self.add_trade_history(f"Gagal membatalkan order {order['id']}: {str(e)}")
                    
                    self.update_orders()
                    self.show_ok_popup(f"Trading dihentikan. {cancelled_count} order BUY dibatalkan.")
                else:
                    self.show_ok_popup("Trading dihentikan. Tidak ada order BUY aktif.")
            else:
                self.show_ok_popup("Trading dihentikan.")
                
        except Exception as e:
            self.show_error(f"Error menghentikan trading: {str(e)}")
    
    def trading_loop(self):
        while self.is_trading:
            try:
                self.trading_logic()
                time.sleep(10)  # Wait 10 seconds between iterations
            except Exception as e:
                self.show_error(f"Error dalam trading loop: {str(e)}")
                time.sleep(30)  # Wait longer on error
    
    def show_error(self, message):
        # Show error in status label
        self.status_label.text = f"Status: Error - {message}"
        
        # Also show popup for important errors
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=message))
        ok_button = CustomButton(text='OK')
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        ok_button.bind(on_press=popup.dismiss)
        content.add_widget(ok_button)
        popup.open()
    
    def show_ok_popup(self, message):
        """Show success popup with OK button"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=message))
        ok_button = CustomButton(text='OK')
        
        popup = Popup(title='Sukses', content=content, size_hint=(0.8, 0.4))
        ok_button.bind(on_press=popup.dismiss)
        content.add_widget(ok_button)
        popup.open()

class TradingBotApp(App):
    def build(self):
        Window.size = (900, 1000)
        return TradingBotGUI()

if __name__ == '__main__':
    TradingBotApp().run()