import json
import logging
import threading
import time
import tkinter as tk
from datetime import datetime
from queue import Queue
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any

from pybit import HTTP, WebSocket
from pybit.exceptions import InvalidRequestError, FailedRequestError


class BybitAccount:
    """Класс для управления подключением к аккаунту Bybit"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.http_session: Optional[HTTP] = None
        self.ws_private: Optional[WebSocket] = None
        
    def create_http_session(self, market_type: str) -> bool:
        """Создание HTTP-сессии для REST API"""
        try:
            if market_type == "Spot":
                self.http_session = HTTP(
                    endpoint="https://api-testnet.bybit.com" if self.testnet else "https://api.bybit.com",
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )
            else:  # Futures
                self.http_session = HTTP(
                    endpoint="https://api-testnet.bybit.com" if self.testnet else "https://api.bybit.com",
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    recv_window=5000
                )
            # Проверка подключения
            self.http_session.get_wallet_balance()
            return True
        except Exception as e:
            logging.error(f"Ошибка создания HTTP-сессии: {e}")
            return False
            
    def create_websocket_connection(self, market_type: str, callback: callable) -> bool:
        """Создание WebSocket-соединения для получения данных в реальном времени"""
        try:
            if market_type == "Spot":
                self.ws_private = WebSocket(
                    channel_type="private",
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    spot=True,
                    testnet=self.testnet,
                    callback=callback
                )
            else:  # Futures
                self.ws_private = WebSocket(
                    channel_type="private",
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    testnet=self.testnet,
                    callback=callback
                )
            return True
        except Exception as e:
            logging.error(f"Ошибка создания WebSocket-соединения: {e}")
            return False


class TradeCopierBot:
    """Основной класс торгового бота для копирования сделок"""
    
    def __init__(self, log_queue: Queue):
        self.log_queue = log_queue
        self.master_account = None
        self.slave_account = None
        self.market_type = "Futures"  # По умолчанию фьючерсы
        self.volume_multiplier = 1.0
        self.copy_only_open = True
        self.is_running = False
        self.testnet = True
        
    def log_message(self, message: str, level=logging.INFO):
        """Добавление сообщения в очередь логов"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_queue.put((formatted_message, level))
        logging.log(level, message)
        
    def setup_accounts(self, master_key: str, master_secret: str, 
                      slave_key: str, slave_secret: str) -> bool:
        """Настройка аккаунтов для копирования"""
        try:
            self.master_account = BybitAccount(master_key, master_secret, self.testnet)
            self.slave_account = BybitAccount(slave_key, slave_secret, self.testnet)
            
            # Проверка подключения к аккаунтам
            if not self.master_account.create_http_session(self.market_type):
                self.log_message("Ошибка подключения к ведущему аккаунту", logging.ERROR)
                return False
                
            if not self.slave_account.create_http_session(self.market_type):
                self.log_message("Ошибка подключения к ведомому аккаунту", logging.ERROR)
                return False
                
            self.log_message("Успешное подключение к обоим аккаунтам")
            return True
            
        except Exception as e:
            self.log_message(f"Ошибка настройки аккаунтов: {e}", logging.ERROR)
            return False
            
    def start_copying(self):
        """Запуск процесса копирования сделок"""
        if not self.master_account or not self.slave_account:
            self.log_message("Аккаунты не настроены", logging.ERROR)
            return
            
        try:
            # Создание WebSocket соединения для ведущего аккаунта
            success = self.master_account.create_websocket_connection(
                self.market_type, self.handle_websocket_message
            )
            
            if success:
                self.is_running = True
                self.log_message("Бот запущен и начал отслеживание сделок")
            else:
                self.log_message("Ошибка запуска WebSocket соединения", logging.ERROR)
                
        except Exception as e:
            self.log_message(f"Ошибка запуска копирования: {e}", logging.ERROR)
            
    def stop_copying(self):
        """Остановка процесса копирования сделок"""
        self.is_running = False
        if self.master_account and self.master_account.ws_private:
            self.master_account.ws_private.exit()
        self.log_message("Бот остановлен")
        
    def handle_websocket_message(self, message):
        """Обработка входящих сообщений из WebSocket"""
        if not self.is_running:
            return
            
        try:
            # Обработка разных форматов сообщений
            if 'topic' in message and 'execution' in message['topic']:
                self.process_execution(message['data'])
            elif 'e' in message and message['e'] == 'execution':
                self.process_execution([message])
                
        except Exception as e:
            self.log_message(f"Ошибка обработки WebSocket сообщения: {e}", logging.ERROR)
            
    def process_execution(self, execution_data):
        """Обработка данных о исполнении ордеров"""
        try:
            for execution in execution_data:
                # Проверяем, является ли это интересующей нас сделкой
                if self.is_valid_execution(execution):
                    self.replicate_trade(execution)
                    
        except Exception as e:
            self.log_message(f"Ошибка обработки исполнения: {e}", logging.ERROR)
            
    def is_valid_execution(self, execution: Dict[str, Any]) -> bool:
        """Проверка, является ли исполнение valid для копирования"""
        # Здесь должна быть реализована логика проверки
        # Например, проверка типа ордера, статуса и т.д.
        return True
        
    def replicate_trade(self, execution: Dict[str, Any]):
        """Копирование сделки на ведомый аккаунт"""
        try:
            symbol = execution['symbol']
            side = execution['side']
            order_type = execution['order_type']
            qty = float(execution['exec_qty'])
            price = float(execution['exec_price']) if order_type == 'Limit' else None
            
            # Применяем множитель объема
            adjusted_qty = qty * self.volume_multiplier
            
            # Проверяем баланс перед отправкой ордера
            if self.check_balance(symbol, side, adjusted_qty, price):
                # Отправляем ордер на ведомый аккаунт
                order_params = {
                    'symbol': symbol,
                    'side': side,
                    'order_type': order_type,
                    'qty': adjusted_qty,
                    'time_in_force': 'GoodTillCancel'
                }
                
                if price:
                    order_params['price'] = price
                    
                # Различные методы для spot и futures
                if self.market_type == "Spot":
                    if side == 'Buy':
                        self.slave_account.http_session.place_active_order(**order_params)
                    else:  # Sell
                        self.slave_account.http_session.place_active_order(**order_params)
                else:  # Futures
                    self.slave_account.http_session.place_active_order(**order_params)
                    
                self.log_message(f"Скопирована сделка: {symbol} {side} {adjusted_qty}")
                
        except Exception as e:
            self.log_message(f"Ошибка копирования сделки: {e}", logging.ERROR)
            
    def check_balance(self, symbol: str, side: str, qty: float, price: float = None) -> bool:
        """Проверка достаточности баланса для сделки"""
        try:
            if self.market_type == "Spot":
                # Для spot market проверяем доступность валюты
                coin = symbol.replace('USDT', '') if side == 'Buy' else 'USDT'
                balance = self.slave_account.http_session.get_wallet_balance(coin=coin)
                available_balance = float(balance['result'][coin]['available_balance'])
                
                if side == 'Buy' and price:
                    required = qty * price
                else:
                    required = qty
                    
                if available_balance >= required:
                    return True
                else:
                    self.log_message(f"Недостаточно баланса. Доступно: {available_balance}, Требуется: {required}", logging.WARNING)
                    return False
                    
            else:  # Futures
                # Для фьючерсов проверяем доступную маржу
                balance = self.slave_account.http_session.get_wallet_balance(coin='USDT')
                available_balance = float(balance['result']['USDT']['available_balance'])
                
                # Упрощенная проверка - в реальной реализации нужно учитывать leverage и т.д.
                if price:
                    order_value = qty * price
                else:
                    # Для market orders получаем текущую цену
                    ticker = self.slave_account.http_session.latest_information_for_symbol(symbol=symbol)
                    last_price = float(ticker['result'][0]['last_price'])
                    order_value = qty * last_price
                    
                if available_balance >= order_value * 0.1:  # Предполагаем leverage 10x
                    return True
                else:
                    self.log_message(f"Недостаточно маржи. Доступно: {available_balance}, Требуется: {order_value * 0.1}", logging.WARNING)
                    return False
                    
        except Exception as e:
            self.log_message(f"Ошибка проверки баланса: {e}", logging.ERROR)
            return False


class TradeCopierGUI:
    """Класс для графического интерфейса торгового бота"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bybit Trade Copier Bot")
        self.root.geometry("800x600")
        
        self.bot = None
        self.log_queue = Queue()
        self.setup_logging()
        self.create_widgets()
        self.update_logs()
        
    def setup_logging(self):
        """Настройка системы логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trade_copier.log'),
                logging.StreamHandler()
            ]
        )
        
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов столбцов и строк для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Поля для API ключей ведущего аккаунта
        ttk.Label(main_frame, text="Master API Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.master_key = ttk.Entry(main_frame, width=40, show="*")
        self.master_key.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(main_frame, text="Master API Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.master_secret = ttk.Entry(main_frame, width=40, show="*")
        self.master_secret.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Поля для API ключей ведомого аккаунта
        ttk.Label(main_frame, text="Slave API Key:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.slave_key = ttk.Entry(main_frame, width=40, show="*")
        self.slave_key.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(main_frame, text="Slave API Secret:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.slave_secret = ttk.Entry(main_frame, width=40, show="*")
        self.slave_secret.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Выбор режима торговли
        ttk.Label(main_frame, text="Режим торговли:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.trade_mode = ttk.Combobox(main_frame, values=["Spot", "Futures"], state="readonly")
        self.trade_mode.set("Futures")
        self.trade_mode.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Множитель объема
        ttk.Label(main_frame, text="Множитель объема:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.volume_multiplier = ttk.Entry(main_frame, width=10)
        self.volume_multiplier.insert(0, "1.0")
        self.volume_multiplier.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Чекбокс для копирования только открытия позиций
        self.copy_only_open_var = tk.BooleanVar(value=True)
        copy_only_open_cb = ttk.Checkbutton(
            main_frame, 
            text="Копировать только открытие позиций",
            variable=self.copy_only_open_var
        )
        copy_only_open_cb.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Чекбокс для тестового режима
        self.testnet_var = tk.BooleanVar(value=True)
        testnet_cb = ttk.Checkbutton(
            main_frame, 
            text="Тестовый режим (testnet)",
            variable=self.testnet_var
        )
        testnet_cb.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Запуск бота", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Остановка бота", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_btn = ttk.Button(button_frame, text="Тест подключения", command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        # Поле для логов
        ttk.Label(main_frame, text="Логи:").grid(row=9, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=20, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания для основного фрейма
        main_frame.rowconfigure(10, weight=1)
        
    def update_logs(self):
        """Обновление логов в интерфейсе"""
        while not self.log_queue.empty():
            message, level = self.log_queue.get()
            self.log_text.config(state=tk.NORMAL)
            
            # Добавление цветового форматирования в зависимости от уровня
            if level >= logging.ERROR:
                tag = "error"
            elif level >= logging.WARNING:
                tag = "warning"
            else:
                tag = "info"
                
            self.log_text.insert(tk.END, message + "\n", tag)
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
            
        self.root.after(100, self.update_logs)
        
    def start_bot(self):
        """Запуск бота"""
        try:
            # Получение параметров из интерфейса
            master_key = self.master_key.get().strip()
            master_secret = self.master_secret.get().strip()
            slave_key = self.slave_key.get().strip()
            slave_secret = self.slave_secret.get().strip()
            market_type = self.trade_mode.get()
            volume_multiplier = float(self.volume_multiplier.get().strip())
            copy_only_open = self.copy_only_open_var.get()
            testnet = self.testnet_var.get()
            
            # Валидация параметров
            if not all([master_key, master_secret, slave_key, slave_secret]):
                messagebox.showerror("Ошибка", "Заполните все поля API ключей")
                return
                
            # Создание и настройка бота
            self.bot = TradeCopierBot(self.log_queue)
            self.bot.market_type = market_type
            self.bot.volume_multiplier = volume_multiplier
            self.bot.copy_only_open = copy_only_open
            self.bot.testnet = testnet
            
            # Настройка аккаунтов
            if self.bot.setup_accounts(master_key, master_secret, slave_key, slave_secret):
                # Запуск в отдельном потоке
                bot_thread = threading.Thread(target=self.bot.start_copying)
                bot_thread.daemon = True
                bot_thread.start()
                
                # Обновление состояния кнопок
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                
        except ValueError:
            messagebox.showerror("Ошибка", "Множитель объема должен быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запуска бота: {e}")
            
    def stop_bot(self):
        """Остановка бота"""
        if self.bot:
            self.bot.stop_copying()
            
        # Обновление состояния кнопок
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
    def test_connection(self):
        """Тестирование подключения к аккаунтам"""
        try:
            master_key = self.master_key.get().strip()
            master_secret = self.master_secret.get().strip()
            slave_key = self.slave_key.get().strip()
            slave_secret = self.slave_secret.get().strip()
            market_type = self.trade_mode.get()
            testnet = self.testnet_var.get()
            
            if not all([master_key, master_secret, slave_key, slave_secret]):
                messagebox.showerror("Ошибка", "Заполните все поля API ключей")
                return
                
            # Тестирование подключения к ведущему аккаунту
            master_account = BybitAccount(master_key, master_secret, testnet)
            if master_account.create_http_session(market_type):
                messagebox.showinfo("Успех", "Подключение к ведущему аккаунту успешно")
            else:
                messagebox.showerror("Ошибка", "Ошибка подключения к ведущему аккаунту")
                return
                
            # Тестирование подключения к ведомому аккаунту
            slave_account = BybitAccount(slave_key, slave_secret, testnet)
            if slave_account.create_http_session(market_type):
                messagebox.showinfo("Успех", "Подключение к ведомому аккаунту успешно")
            else:
                messagebox.showerror("Ошибка", "Ошибка подключения к ведомому аккаунту")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка тестирования подключения: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TradeCopierGUI(root)
    
    # Настройка тегов для цветного текста в логах
    app.log_text.tag_config("error", foreground="red")
    app.log_text.tag_config("warning", foreground="orange")
    app.log_text.tag_config("info", foreground="green")
    
    root.mainloop()