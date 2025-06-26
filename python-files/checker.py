import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import requests
from concurrent.futures import ThreadPoolExecutor
import re
import time
from queue import Queue
import urllib3
import traceback
import threading
import socket
import json
import sys  # Додаємо для sys.exit()

# Придушити InsecureRequestWarning для самопідписаних сертифікатів або подібних проблем
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ****** ВАЖЛИВО: ЩОБ УНИКНУТИ ПОМИЛОК SOCKS ('Missing dependencies for SOCKS support'),
# ****** ВСТАНОВІТЬ PYSOсKS ЗА ДОПОМОГОЮ ЦІЄЇ КОМАНДИ В ТЕРМІНАЛІ:
# pip install PySocks

class ProxyChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Scanner v4.5")  # Оновлена версія

        # Приховуємо стандартний заголовок вікна Windows та іконку
        self.root.overrideredirect(True)
        self.root.wm_attributes('-toolwindow', True) # Робить вікно "інструментальним", без іконки в панелі завдань

        # Залишаємо мінімальний розмір для кнопки закриття
        self.root.geometry("200x50")
        self.root.configure(bg="#1e272e")

        self.style = ttk.Style()
        self.style.theme_use('default')

        # Створення власного рядка заголовка лише з кнопкою закриття
        self.title_bar = tk.Frame(root, bg="#2d3436", relief="raised", bd=0)
        self.title_bar.pack(expand=True, fill=tk.X)

        self.title_label = tk.Label(self.title_bar, text="Proxy Scanner v4.5 (Фоновий процес)", bg="#2d3436", fg="#00ff7f",
                                    font=("Consolas", 10, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Кнопка закриття вікна
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.on_closing,
                                      bg="#2d3436", fg="#00ff7f",
                                      font=("Consolas", 12, "bold"), bd=0, highlightbackground="#2d3436",
                                      activebackground="#e74c3c", activeforeground="white", width=4)
        self.close_button.pack(side=tk.RIGHT)

        # Прив'язка подій для перетягування (навіть якщо вікно мінімальне)
        self.title_bar.bind("<ButtonPress-1>", self.start_move_window)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move_window)
        self.title_label.bind("<ButtonPress-1>", self.start_move_window)
        self.title_label.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<ButtonRelease-1>", self.stop_move_window)

        self.is_maximized = False # Зберігаємо для сумісності, хоча вікно не максимізуватиметься
        self.original_geometry = ""

        # Видаляємо всі інші елементи GUI
        # self.proxy_input, self.output, self.tree, progress bars, stats labels, other buttons

        # Змінні стану та об'єкти для багатопотоковості
        self.proxies = []
        self.running = False
        self.index = 0
        self.all_proxies = []
        self.good_proxies = []
        self.bad_proxies = []
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.result_queue = Queue()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Визначення власного зовнішнього IP
        self.my_external_ip = self._get_my_external_ip()
        if self.my_external_ip:
            print(f"Ваш зовнішній IP: {self.my_external_ip}\n")
        else:
            print("Не вдалося визначити ваш зовнішній IP. Перевірка анонімності може бути менш точною.\n")

        # Автоматично починаємо сканування при запуску (або додайте логіку для завантаження проксі)
        # Наразі, потрібно буде вручну завантажити проксі або передати їх.
        # Для демонстрації, я додам кілька фіктивних проксі
        self.proxies = ["http://1.2.3.4:8080", "socks5://5.6.7.8:1080", "9.10.11.12:3128"]
        self.start_checking()


    def start_move_window(self, event):
        """Зберігає початкові координати для перетягування вікна."""
        self._x = event.x
        self._y = event.y

    def move_window(self, event):
        """Переміщує вікно під час перетягування."""
        if self.is_maximized:
            self.toggle_maximize()
        x = self.root.winfo_x() + event.x - self._x
        y = self.root.winfo_y() + event.y - self._y
        self.root.geometry(f"+{x}+{y}")

    def stop_move_window(self, event):
        """Очищає початкові координати після завершення перетягування."""
        self._x = None
        self._y = None

    def toggle_maximize(self):
        """Ця функція більше не потрібна, але залишаємо для сумісності."""
        pass # Вікно не буде максимізуватися

    def _get_my_external_ip(self):
        """Отримує ваш реальний зовнішній IP-адрес, роблячи запит без проксі."""
        try:
            response = requests.get("http://httpbin.org/ip", timeout=5)
            response.raise_for_status()
            return response.json().get('origin')
        except requests.exceptions.RequestException as e:
            print(f"Error getting external IP: {e}")
            return None

    def sort_column(self, col, reverse):
        """Ця функція більше не потрібна без Treeview."""
        pass

    def on_closing(self):
        """
        Обробка події закриття вікна.
        Намагається граціозно завершити потоки, потім закриває вікно.
        """
        if self.running:
            self.stop_checking()
            print("Завершення робочих потоків...\n")
            self.root.update_idletasks()

        self.executor.shutdown(wait=True)

        if not self.executor._work_queue.empty():
            print("Деякі потоки не завершились вчасно. Примусове завершення.\n")

        self.root.destroy()

    def load_from_file(self):
        """Ця функція більше не потрібна без GUI для завантаження."""
        print("Завантаження з файлу не підтримується в цьому режимі.")
        pass

    def show_context_menu(self, event):
        """Ця функція більше не потрібна без Treeview."""
        pass

    def copy_selected_proxy(self):
        """Ця функція більше не потрібна без Treeview."""
        pass

    def copy_selected_row(self, ):
        """Ця функція більше не потрібна без Treeview."""
        pass

    def copy_selected_items_ctrl_c(self, event=None):
        """Ця функція більше не потрібна без Treeview."""
        pass

    def _parse_proxy_string(self, proxy_raw):
        """
        Розбирає необроблений рядок проксі на компоненти: user, password, ip, port, type.
        Підтримує формати:
        - ip:port
        - http://ip:port
        - socks5://user:pass@ip:port
        - user:pass@ip:port (якщо не вказано протокол, за замовчуванням HTTP або за портом)
        """
        user, password, ip, port, p_type = None, None, None, None, None

        match = re.match(
            r'^(?:(http|https|socks4|socks5)://)?(?:([^:]+):([^@]+)@)?([\d.]+)(?::(\d+))?$',
            proxy_raw
        )

        if match:
            p_type, user, password, ip, port = match.groups()

            if p_type:
                p_type = p_type
            else:
                if port:
                    if port in ['80', '8080', '3128', '8888']:
                        p_type = "http"
                    elif port in ['443', '8443']:
                        p_type = "https"
                    elif port == '1080':
                        p_type = "socks5"
                    else:
                        p_type = "http"
                else:
                    p_type = "http"

            if not port:
                if p_type == "http":
                    port = '80'
                elif p_type == "https":
                    port = '443'
                elif p_type in ["socks4", "socks5"]:
                    port = '1080'

        else:
            parts = proxy_raw.split(':')
            if len(parts) >= 2:
                ip = parts[0]
                port = parts[1]
                if port in ['80', '8080', '3128', '8888']:
                    p_type = "http"
                elif port in ['443', '8443']:
                    p_type = "https"
                elif port == '1080':
                    p_type = "socks5"
                else:
                    p_type = "http"
            elif len(parts) == 1:
                ip = parts[0]
                port = '80'
                p_type = "http"
            else:
                ip = "N/A"
                port = "N/A"
                p_type = "Unknown"

        try:
            socket.inet_aton(ip)
        except (socket.error, TypeError):
            ip = "N/A"

        try:
            port = str(int(port))
        except (ValueError, TypeError):
            port = "N/A"

        return user, password, ip, port, p_type

    def _get_geolocation_from_multiple_sources(self, ip_address):
        """
        Отримує геолокаційні дані з декількох джерел.
        Спробує ipinfo.io, потім ip-api.com.
        """
        if not ip_address or ip_address == "N/A" or ip_address == "127.0.0.1":
            return "Localhost" if ip_address == "127.0.0.1" else "N/A"

        url_ipinfo = f"https://ipinfo.io/{ip_address}/json"
        try:
            response = requests.get(url_ipinfo, timeout=5)
            data = response.json()
            if response.status_code == 200 and data.get('country'):
                country = data.get('country', 'Невідомо')
                city = data.get('city', 'Невідомо')
                return f"{country}, {city}"
        except requests.exceptions.RequestException:
            pass

        url_ipapi = f"http://ip-api.com/json/{ip_address}"
        try:
            response = requests.get(url_ipapi, timeout=5)
            data = response.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Невідомо')
                city = data.get('city', 'Невідомо')
                return f"{country}, {city}"
        except requests.exceptions.RequestException:
            pass

        return "Невідоме місцезнаходження"

    def check_proxy(self, proxy_raw):
        """
        Виконує повну перевірку проксі: статус, швидкість, тип, анонімність.
        Автоматично перебирає типи, якщо початковий не працює.
        """
        user, password, ip, port, initial_type = self._parse_proxy_string(proxy_raw)

        if ip == "N/A" or port == "N/A":
            self.result_queue.put(
                (ip, port, "Недійсний формат", "N/A", "Невідомо", "Невідомо", "Недійсний формат проксі", proxy_raw))
            return

        geo_info = self._get_geolocation_from_multiple_sources(ip)
        proxy_type = "Невідомо"
        status = "Не вдалося"
        latency_ms = "N/A"
        anonymity = "Невідомо"

        test_urls = {
            "http": "http://httpbin.org/get",
            "https": "https://httpbin.org/get",
            "socks5": "http://httpbin.org/get",
            "socks4": "http://httpbin.org/get"
        }

        final_try_order = []
        if initial_type:
            final_try_order.append(initial_type)
            if initial_type == "socks5":
                if "socks4" not in final_try_order: final_try_order.append("socks4")
            elif initial_type == "socks4":
                if "socks5" not in final_try_order: final_try_order.append("socks5")

        for t in ["http", "https", "socks5", "socks4"]:
            if t not in final_try_order:
                final_try_order.append(t)

        final_try_order = list(dict.fromkeys(final_try_order))

        for p_type in final_try_order:
            if not self.running:
                break

            proxies_dict = {}
            proxy_url = f"{p_type}://"
            if user and password:
                proxy_url += f"{user}:{password}@"
            proxy_url += f"{ip}:{port}"

            proxies_dict = {'http': proxy_url, 'https': proxy_url}

            try:
                start_time = time.perf_counter()
                response = requests.get(test_urls.get(p_type, "http://httpbin.org/get"),
                                        proxies=proxies_dict,
                                        timeout=7,
                                        verify=False)
                end_time = time.perf_counter()
                latency_ms = round((end_time - start_time) * 1000, 2)

                if response.status_code == 200:
                    status = "Працює"
                    proxy_type = p_type.upper()

                    res_json = response.json()
                    client_ip_from_httpbin = res_json.get('origin')
                    request_headers = res_json.get('headers', {})

                    if self.my_external_ip and self.my_external_ip in client_ip_from_httpbin:
                        anonymity = "Прозорий"
                    elif 'X-Forwarded-For' in request_headers or 'Via' in request_headers or 'Proxy-Connection' in request_headers:
                        anonymity = "Анонімний"
                    elif client_ip_from_httpbin and client_ip_from_httpbin == ip:
                        anonymity = "Елітний"
                    else:
                        anonymity = "Невідомий/Інший"

                    break

            except requests.exceptions.Timeout:
                status = "Тайм-аут"
                latency_ms = "N/A"
            except requests.exceptions.SSLError:
                status = "Помилка SSL"
                latency_ms = "N/A"
            except requests.exceptions.ConnectionError as ce:
                error_message = str(ce)
                if "Failed to establish a new connection" in error_message or "Connection refused" in error_message:
                    status = "Відмова з'єднання"
                elif "Name or service not known" in error_message or "nodename nor servname provided, or not known" in error_message:
                    status = "Невідомий хост"
                else:
                    status = "Помилка підключення"
                latency_ms = "N/A"
            except requests.exceptions.ProxyError as pe:
                if "Missing dependencies for SOCKS support" in str(pe):
                    status = "Помилка SOCKS (PySocks відсутній?)"
                elif "SOCKSHTTPSConnection" in str(pe) and "SSL/TLS handshake" in str(pe):
                    status = "SOCKS SSL/TLS помилка"
                else:
                    status = f"Помилка проксі: {type(pe).__name__}"
                latency_ms = "N/A"
            except json.JSONDecodeError:
                status = "Помилка відповіді (JSON)"
                latency_ms = "N/A"
            except requests.exceptions.RequestException as re_exc:
                status = f"HTTP Запит: {type(re_exc).__name__}"
                latency_ms = "N/A"
            except Exception as e:
                status = f"Невідома помилка: {type(e).__name__}"
                latency_ms = "N/A"
                with self.lock:
                    print(f"Несподівана помилка при перевірці {proxy_raw} з {p_type}: {type(e).__name__} - {e}\n")

        self.result_queue.put((ip, port, geo_info, latency_ms, proxy_type, anonymity, status, proxy_raw))

    def get_speed_tag(self, speed_ms):
        """Ця функція більше не використовується для GUI візуалізації, але може бути корисною для логіки."""
        if speed_ms == "N/A":
            return "bad"
        try:
            speed = float(speed_ms)
            if speed <= 200:
                return "very_good"
            elif speed <= 500:
                return "good"
            elif speed <= 1500:
                return "medium"
            elif speed <= 3000:
                return "slow"
            else:
                return "bad"
        except ValueError:
            return "bad"

    def update_gui(self):
        """Оновлює GUI з результатами з черги та прогресом."""
        try:
            if self.running:
                processed_this_cycle = 0
                while not self.result_queue.empty():
                    ip, port, geo_info, latency_ms, proxy_type, anonymity, status, raw_proxy_string = self.result_queue.get()

                    with self.lock:
                        self.all_proxies.append(raw_proxy_string)
                        if status == "Працює":
                            self.good_proxies.append(raw_proxy_string)
                        else:
                            self.bad_proxies.append(raw_proxy_string)

                        # Вивід результатів в консоль
                        print(f"Перевірено: {raw_proxy_string} -> Статус: {status}, Затримка: {latency_ms}мс, Тип: {proxy_type}, Анонімність: {anonymity}\n")

                        processed_this_cycle += 1

                # Оновлення прогресу (тепер це лише для внутрішньої логіки завершення, без відображення GUI)
                if len(self.proxies) > 0:
                    self.index += processed_this_cycle
                    self.index = min(self.index, len(self.proxies))

                    if self.index >= len(self.proxies) and len(self.proxies) > 0:
                        self.stop_checking()

        except Exception as e:
            print(f"Помилка оновлення логіки: {str(e)}\n{traceback.format_exc()}\n")
        finally:
            if self.running:
                self.root.after(50, self.update_gui)

    def start_checking(self):
        """Ініціює процес сканування проксі."""
        if self.running:
            print("Сканування вже запущено!")
            return

        # Якщо проксі не завантажено, можна додати тут логіку для завантаження з файлу або з певного джерела
        if not self.proxies:
            print("Немає проксі для перевірки! Завантажте проксі перед запуском.")
            return

        self.running = True

        # Скидання всіх лічильників та списків
        self.all_proxies = []
        self.good_proxies = []
        self.bad_proxies = []
        self.index = 0

        print(f"Початок сканування {len(self.proxies)} проксі...\n")

        for proxy in self.proxies:
            if not self.running:
                break
            self.executor.submit(self.check_proxy, proxy)

        self.root.after(50, self.update_gui)

    def stop_checking(self):
        """Граціозно зупиняє процес перевірки проксі, дозволяючи поточним завданням завершитися."""
        with self.lock:
            if not self.running:
                print("Сканування не запущено.")
                return
            self.running = False

        print("\nСканування зупинено користувачем або завершено. Завершення результатів...\n")

        self.root.after(100, self.process_remaining_results)

    def process_remaining_results(self):
        """
        Обробляє будь-які елементи, що залишилися в черзі результатів після зупинки сканування.
        Викликається рекурсивно через after, щоб не блокувати GUI.
        """
        processed_count = 0
        max_process_per_call = 20

        while not self.result_queue.empty() and processed_count < max_process_per_call:
            try:
                ip, port, geo_info, latency_ms, proxy_type, anonymity, status, raw_proxy_string = self.result_queue.get(
                    block=False)
                with self.lock:
                    self.all_proxies.append(raw_proxy_string)
                    if status == "Працює":
                        self.good_proxies.append(raw_proxy_string)
                    else:
                        self.bad_proxies.append(raw_proxy_string)

                    print(f"Завершено: {raw_proxy_string} -> Статус: {status}, Затримка: {latency_ms}мс, Тип: {proxy_type}, Анонімність: {anonymity}\n")
                    processed_count += 1
            except Exception as e:
                print(f"Помилка обробки решти результатів: {str(e)}\n")
                break

        if not self.result_queue.empty():
            self.root.after(50, self.process_remaining_results)
        else:
            print(f"Сканування завершено. Загалом працюючих: {len(self.good_proxies)}, Загалом непрацюючих/помилок: {len(self.bad_proxies)}.\n")
            self.save_results() # Автоматичне збереження результатів після завершення

    def save_results(self):
        """Зберігає категоризовані результати проксі (всі, робочі, неробочі) в текстові файли."""
        if not self.all_proxies:
            print("Результатів для збереження ще немає!")
            return

        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # Ви можете вказати фіксований шлях або запитати його при запуску без GUI
            # For this example, we'll save to the current directory
            save_dir = "." # Зберігаємо в поточній директорії

            all_file_path = f"{save_dir}/all_proxies_{timestamp}.txt"
            good_file_path = f"{save_dir}/good_proxies_{timestamp}.txt"
            bad_file_path = f"{save_dir}/bad_proxies_{timestamp}.txt"

            with open(all_file_path, 'w', encoding='utf-8') as f_all:
                f_all.write("\n".join(self.all_proxies))

            with open(good_file_path, 'w', encoding='utf-8') as f_good:
                f_good.write("\n".join(self.good_proxies))

            with open(bad_file_path, 'w', encoding='utf-8') as f_bad:
                f_bad.write("\n".join(self.bad_proxies))

            print(f"Результати збережено до:\n"
                  f"{all_file_path}\n"
                  f"{good_file_path}\n"
                  f"{bad_file_path}\n")
        except Exception as e:
            print(f"Не вдалося зберегти результати: {str(e)}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyChecker(root)
    root.mainloop()