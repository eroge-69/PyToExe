import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
import urllib.parse
import time
import random
from datetime import datetime
import re
import os

class DepopMessengerBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Depop Messenger Bot PRO v3.0")
        self.root.geometry("1100x850")
        
        # Настройки
        self.running = False
        self.stats = {'sent': 0, 'failed': 0, 'start_time': None}
        self.tokens = []
        self.proxies = []
        self.message = ""
        self.urls = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Right panel
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Proxy settings
        proxy_frame = ttk.LabelFrame(left_panel, text="Настройки прокси", padding="10")
        proxy_frame.pack(fill=tk.X, pady=5)

        ttk.Label(proxy_frame, text="Формат: socks5://ip:port или socks5://user:pass@ip:port").pack(anchor="w")
        self.proxy_entry = ttk.Entry(proxy_frame, width=40)
        self.proxy_entry.pack(fill=tk.X, pady=5)
        
        proxy_btn_frame = ttk.Frame(proxy_frame)
        proxy_btn_frame.pack(fill=tk.X)
        ttk.Button(proxy_btn_frame, text="Проверить", command=self.test_proxy).pack(side=tk.LEFT, expand=True)
        ttk.Button(proxy_btn_frame, text="Загрузить список", command=self.load_proxies).pack(side=tk.LEFT, expand=True)

        # Tokens
        token_frame = ttk.LabelFrame(left_panel, text="Токены Depop", padding="10")
        token_frame.pack(fill=tk.X, pady=5)
        self.token_text = scrolledtext.ScrolledText(token_frame, height=10, width=40)
        self.token_text.pack(fill=tk.BOTH)
        ttk.Button(token_frame, text="Загрузить из файла", command=self.load_tokens).pack(pady=5)

        # Message
        msg_frame = ttk.LabelFrame(left_panel, text="Сообщение", padding="10")
        msg_frame.pack(fill=tk.X, pady=5)
        self.message_text = scrolledtext.ScrolledText(msg_frame, height=10, width=40)
        self.message_text.pack(fill=tk.BOTH)
        ttk.Button(msg_frame, text="Загрузить из файла", command=self.load_message).pack(pady=5)

        # Settings
        settings_frame = ttk.LabelFrame(left_panel, text="Настройки", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="Задержка (сек):").grid(row=0, column=0, sticky="w")
        self.delay_entry = ttk.Entry(settings_frame, width=10)
        self.delay_entry.insert(0, "5-15")
        self.delay_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(settings_frame, text="Попытки:").grid(row=1, column=0, sticky="w")
        self.retry_entry = ttk.Entry(settings_frame, width=5)
        self.retry_entry.insert(0, "3")
        self.retry_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(settings_frame, text="Лимит:").grid(row=2, column=0, sticky="w")
        self.limit_entry = ttk.Entry(settings_frame, width=5)
        self.limit_entry.insert(0, "50")
        self.limit_entry.grid(row=2, column=1, sticky="w")

        # URLs
        url_frame = ttk.LabelFrame(right_panel, text="URL чатов", padding="10")
        url_frame.pack(fill=tk.BOTH, expand=True)
        self.url_text = scrolledtext.ScrolledText(url_frame, height=15, width=60)
        self.url_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(url_frame, text="Загрузить из файла", command=self.load_urls).pack(pady=5)

        # Control buttons
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="СТАРТ", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(btn_frame, text="СТОП", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # Progress
        self.progress = ttk.Progressbar(right_panel, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(fill=tk.X, pady=5)

        # Log
        log_frame = ttk.LabelFrame(right_panel, text="Лог выполнения", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, 
                                                font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message, status="info"):
        """Логирование с цветовой маркировкой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        if status == "error":
            self.log_text.tag_add("error", "end-2l linestart", "end-2l lineend")
            self.log_text.tag_config("error", foreground="red")
        else:
            self.log_text.tag_add("info", "end-2l linestart", "end-2l lineend")
            self.log_text.tag_config("info", foreground="green")
            
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

    def validate_proxy(self, proxy_str):
        """Проверка формата прокси"""
        if not proxy_str:
            return None
            
        patterns = [
            r'^socks5://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$',  # socks5://ip:port
            r'^socks5://[^:@]+:[^:@]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'  # socks5://user:pass@ip:port
        ]
        
        return proxy_str if any(re.match(p, proxy_str) for p in patterns) else None

    def test_proxy(self):
        """Тестирование прокси"""
        proxy_str = self.proxy_entry.get().strip()
        proxy = self.validate_proxy(proxy_str)
        
        if not proxy:
            self.log("Неверный формат прокси. Используйте: socks5://ip:port или socks5://user:pass@ip:port", "error")
            return
            
        try:
            proxies = {'http': proxy, 'https': proxy}
            test_url = "https://api.ipify.org?format=json"
            
            # Временное отключение глобального прокси для теста
            original_socket = socket.socket
            socket.socket = socks.socksocket
            
            socks.set_default_proxy(socks.SOCKS5, 
                                  proxy.split('@')[-1].split(':')[0],  # IP
                                  int(proxy.split(':')[-1]),  # Port
                                  username=proxy.split('://')[1].split(':')[0] if '@' in proxy else None,
                                  password=proxy.split('://')[1].split(':')[1].split('@')[0] if '@' in proxy else None)
            
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                self.log(f"Прокси работает! Ваш IP: {response.json()['ip']}")
                return True
            else:
                self.log(f"Ошибка проверки прокси: {response.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Ошибка проверки прокси: {str(e)}", "error")
            return False
        finally:
            # Восстановление оригинального socket
            socket.socket = original_socket
            socks.set_default_proxy()

    def load_proxies(self):
        """Загрузка списка прокси из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip() and self.validate_proxy(line.strip())]
                
            if self.proxies:
                self.proxy_entry.delete(0, tk.END)
                self.proxy_entry.insert(0, self.proxies[0])
                self.log(f"Загружено {len(self.proxies)} валидных прокси")
            else:
                self.log("Не найдено валидных прокси в файле", "error")

    def load_tokens(self):
        """Загрузка токенов из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.tokens = [line.strip() for line in f if line.strip()]
                self.token_text.delete("1.0", tk.END)
                self.token_text.insert("1.0", "\n".join(self.tokens))
            self.log(f"Загружено {len(self.tokens)} токенов")

    def load_message(self):
        """Загрузка сообщения из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.message = f.read()
                self.message_text.delete("1.0", tk.END)
                self.message_text.insert("1.0", self.message)
            self.log("Сообщение загружено")

    def load_urls(self):
        """Загрузка URL чатов из файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.urls = [line.strip() for line in f if line.strip()]
                self.url_text.delete("1.0", tk.END)
                self.url_text.insert("1.0", "\n".join(self.urls))
            self.log(f"Загружено {len(self.urls)} URL чатов")

    def send_message(self, token, chat_url, message):
        """Отправка сообщения через Depop API"""
        try:
            # Парсинг URL чата
            parsed = urllib.parse.urlparse(chat_url)
            params = urllib.parse.parse_qs(parsed.query)
            user_id = params.get('userId', [None])[0]
            product_id = params.get('productId', [None])[0]
            
            if not user_id or not product_id:
                return False, "Неверный URL чата"
            
            # Формирование запроса
            url = "https://webapi.depop.com/api/v2/chat"
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json",
                "User-Agent": "Depop/2.208.0 (iPhone; iOS 15.4; Scale/3.00)"
            }
            
            payload = {
                "product_id": product_id,
                "recipient_id": user_id,
                "text": message
            }
            
            # Настройка прокси
            proxy = self.proxy_entry.get().strip()
            proxies = None
            if proxy and self.validate_proxy(proxy):
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            # Отправка запроса
            response = requests.post(url, json=payload, headers=headers, 
                                   proxies=proxies, timeout=20)
            
            if response.status_code == 201:
                return True, "Сообщение отправлено"
            else:
                return False, f"Ошибка API: {response.status_code} - {response.text[:200]}"
                
        except requests.exceptions.ProxyError as e:
            return False, f"Ошибка прокси: {str(e)}"
        except Exception as e:
            return False, f"Ошибка сети: {str(e)}"

    def start_bot(self):
        """Запуск бота"""
        if self.running:
            return

        # Получение данных из интерфейса
        self.tokens = self.token_text.get("1.0", tk.END).splitlines()
        self.tokens = [t.strip() for t in self.tokens if t.strip()]
        
        self.message = self.message_text.get("1.0", tk.END).strip()
        self.urls = self.url_text.get("1.0", tk.END).splitlines()
        self.urls = [u.strip() for u in self.urls if u.strip()]

        if not self.tokens or not self.message or not self.urls:
            messagebox.showerror("Ошибка", "Загрузите все необходимые данные!")
            return

        # Проверка прокси
        proxy = self.proxy_entry.get().strip()
        if proxy and not self.validate_proxy(proxy):
            messagebox.showerror("Ошибка", "Неверный формат прокси!")
            return

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.stats = {'sent': 0, 'failed': 0, 'start_time': datetime.now()}

        # Получение настроек
        delay_parts = self.delay_entry.get().split("-")
        min_delay = float(delay_parts[0])
        max_delay = float(delay_parts[1]) if len(delay_parts) > 1 else min_delay
        retries = int(self.retry_entry.get())
        limit = int(self.limit_entry.get())

        # Запуск в отдельном потоке
        threading.Thread(
            target=self.run_bot,
            args=(min_delay, max_delay, retries, limit),
            daemon=True
        ).start()

    def run_bot(self, min_delay, max_delay, retries, limit):
        """Основной цикл работы бота"""
        self.log(f"Начало работы с {len(self.tokens)} токенами и {len(self.urls)} чатами")
        
        for token in self.tokens:
            if not self.running:
                break

            self.log(f"Используется токен: {token[:6]}...{token[-4:]}")
            messages_sent = 0

            for url in self.urls:
                if not self.running or messages_sent >= limit:
                    break

                # Рандомная задержка
                time.sleep(random.uniform(min_delay, max_delay))

                # Попытки отправки
                for attempt in range(retries):
                    if not self.running:
                        break

                    success, result = self.send_message(token, url, self.message)
                    if success:
                        self.stats['sent'] += 1
                        messages_sent += 1
                        self.log(f"Отправлено сообщение {messages_sent}/{limit}")
                        break
                    else:
                        self.stats['failed'] += 1
                        self.log(f"Попытка {attempt+1}/{retries}: {result}", "error")
                        time.sleep(5)

                self.update_stats()

        self.running = False
        self.root.after(0, self.on_bot_finished)

    def stop_bot(self):
        """Остановка бота"""
        self.running = False
        self.log("Остановка работы...")

    def update_stats(self):
        """Обновление статистики"""
        elapsed = datetime.now() - self.stats['start_time']
        speed = self.stats['sent'] / max(elapsed.total_seconds() / 60, 0.1)
        
        status = (
            f"Отправлено: {self.stats['sent']} | "
            f"Ошибок: {self.stats['failed']} | "
            f"Скорость: {speed:.1f} соо/мин"
        )
        self.progress["value"] = (self.stats['sent'] / max(1, self.stats['sent'] + self.stats['failed'])) * 100
        self.root.update()

    def on_bot_finished(self):
        """Завершение работы"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log(f"Работа завершена. Итого: {self.stats['sent']} отправлено, {self.stats['failed']} ошибок")

if __name__ == "__main__":
    import socks
    socket.socket = socks.socksocket  # Глобальная настройка SOCKS
    
    root = tk.Tk()
    app = DepopMessengerBot(root)
    root.mainloop()