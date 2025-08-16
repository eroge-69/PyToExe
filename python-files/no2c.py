import time
import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
import logging
import requests
from urllib.parse import urljoin
from PIL import Image, ImageFilter
from io import BytesIO
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import numpy
import pytesseract
import re
import websocket
import ssl
import urllib.parse
import os
import json
import asyncio
import aiohttp
import socket
from typing import Dict, Optional
from tabulate import tabulate
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import threading

# Указываем путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === НАСТРОЙКИ ===
BASE_URL = "https://www.mahsaserver.com"
CONFIG_ADD_URL = urljoin(BASE_URL, "/my-configs/add/")
CFG_FILE = "cfgs.txt"
ADS_TEXT = "t.me/allworldcfg"
WAIT_TIME = 15
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1ODQ1MDk5LCJpYXQiOjE3NTUyNDAyOTksImp0aSI6IjBkZThiMjFiMTY2MTRkMWViMjZiN2QwMjQzZWMyNzc2IiwidXNlcl9pZCI6IjAyMjBiYjA4NGQ3ZmI0IiwiaXNfc3VwZXJ1c2VyIjpmYWxzZSwiaXNfc3RhZmYiOmZhbHNlLCJwZXJtaXNzaW9ucyI6W119.qpnQ-pVs8oa0yIC6NSA-2xRKaH_bhjPBPzDqeovubpM"  # Замените на ваш токен, если используется
GETIP_API_URL = "http://ip-api.com/json/"

# === TELEGRAM ===
TELEGRAM_BOT_TOKEN = "7212575469:AAHQlAbeOqN67HbnpiF125SctEoxzXLkKQE"
TELEGRAM_CHAT_ID = "1353700460"

# === ЛОГГИНГ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vpn_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === КЭШ ДЛЯ IP И СТРАН ===
ip_country_cache = {}  # Кэш для хранения пар IP -> страна

# === ОТПРАВКА В TELEGRAM ===
def escape_markdown(text: str) -> str:
    """Экранирует спецсимволы MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def send_telegram_message(message: str) -> bool:
    """Улучшенная функция отправки сообщений в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'MarkdownV2'
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.error(f"Ошибка Telegram API: {response.text}")
            return False
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {str(e)}")
        return False

# === КЛАСС VLESSClient ===
class VLESSClient:
    def __init__(self, vless_url: str):
        """Инициализация клиента VLESS с разбором URL."""
        self.vless_url = vless_url
        self.config = self._parse_vless_url()
        self.ws = None
        self.server_ip = None
        self.local_ip = self._get_local_ip()
        self.server_country = None

    def _get_local_ip(self) -> str:
        """Получение локального IP-адреса клиента."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.error(f"Ошибка получения локального IP: {e}")
            return "unknown"

    def _resolve_server_ip(self) -> str:
        """Разрешение доменного имени сервера в IP-адрес."""
        try:
            addr_info = socket.getaddrinfo(self.config['address'], self.config['port'], proto=socket.IPPROTO_TCP)
            self.server_ip = addr_info[0][4][0]
            return self.server_ip
        except Exception as e:
            logger.error(f"Ошибка разрешения IP для {self.config['address']}: {e}")
            return "unknown"

    async def _get_country_by_ip(self) -> str:
        """Получение страны по IP-адресу через ip-api.com с кэшированием и обработкой 429."""
        if not self.server_ip or self.server_ip == "unknown":
            return "unknown"

        # Проверяем кэш
        if self.server_ip in ip_country_cache:
            logger.info(f"Страна для IP {self.server_ip} взята из кэша: {ip_country_cache[self.server_ip]}")
            self.server_country = ip_country_cache[self.server_ip]
            return self.server_country

        # Задержка для соблюдения лимита 45 запросов в минуту (1.5 секунды между запросами)
        await asyncio.sleep(1.5)

        max_retries = 3
        retry_delay = 1  # Начальная задержка в секундах

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{GETIP_API_URL}/{self.server_ip}") as response:
                        if response.status == 200:
                            data = await response.json()
                            self.server_country = data.get('country', 'unknown')
                            ip_country_cache[self.server_ip] = self.server_country  # Сохраняем в кэш
                            logger.info(f"Получена страна для IP {self.server_ip}: {self.server_country}")
                            return self.server_country
                        elif response.status == 429:
                            logger.warning(f"Ошибка 429: Слишком много запросов, попытка {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                retry_delay *= 2  # Экспоненциальный backoff
                            continue
                        else:
                            logger.error(f"Ошибка getip-API: статус {response.status}")
                            return "unknown"
            except Exception as e:
                logger.error(f"Ошибка получения страны для IP {self.server_ip}: {e}")
                return "unknown"
        
        logger.error(f"Не удалось получить страну для IP {self.server_ip} после {max_retries} попыток")
        return "unknown"

    def _parse_vless_url(self) -> Dict:
        """Парсинг VLESS URL для извлечения параметров."""
        try:
            parsed = urllib.parse.urlparse(self.vless_url)
            query_params = urllib.parse.parse_qs(parsed.query)

            config = {
                'uuid': parsed.username,
                'address': parsed.hostname,
                'port': parsed.port or 443,
                'network': query_params.get('type', ['ws'])[0].lower(),
                'path': query_params.get('path', ['/'])[0],
                'encryption': query_params.get('encryption', ['none'])[0],
                'security': query_params.get('security', ['none'])[0].lower(),
            }
            return config
        except Exception as e:
            logger.error(f"Ошибка парсинга VLESS URL: {e}")
            return {
                'uuid': 'unknown',
                'address': 'unknown',
                'port': 443,
                'network': 'unknown',
                'path': '/',
                'encryption': 'none',
                'security': 'none'
            }

    def _build_ws_url(self) -> str:
        """Создание URL для WebSocket."""
        protocol = 'wss' if self.config['security'] in ['tls', 'xtls'] else 'ws'
        address = self.server_ip if self.server_ip else self.config['address']
        return f"{protocol}://{address}:{self.config['port']}{self.config['path']}"

    def _display_config(self):
        """Отображение конфигурации и информации в таблице."""
        table_data = [
            ["UUID", self.config['uuid']],
            ["Server Address", self.config['address']],
            ["Server IP", self.server_ip or "unknown"],
            ["Server Country", self.server_country or "unknown"],
            ["Port", self.config['port']],
            ["Network Type", self.config['network']],
            ["Path", self.config['path']],
            ["Encryption", self.config['encryption']],
            ["Security", self.config['security']],
            ["Local IP", self.local_ip]
        ]
        table = tabulate(table_data, headers=["Parameter", "Value"], tablefmt="grid")
        logger.info(f"\nVLESS Configuration:\n{table}")
        
# Добавляем новый класс для обработки VMESS
class VMESSClient:
    def __init__(self, vmess_url: str):
        """Инициализация клиента VMESS с разбором URL."""
        self.vmess_url = vmess_url
        self.config = self._parse_vmess_url()
        self.server_ip = None
        self.local_ip = self._get_local_ip()
        self.server_country = None

    def _get_local_ip(self) -> str:
        """Получение локального IP-адреса клиента."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.error(f"Ошибка получения локального IP: {e}")
            return "unknown"

    def _resolve_server_ip(self) -> str:
        """Разрешение доменного имени сервера в IP-адрес."""
        try:
            addr_info = socket.getaddrinfo(self.config['address'], self.config['port'], proto=socket.IPPROTO_TCP)
            self.server_ip = addr_info[0][4][0]
            return self.server_ip
        except Exception as e:
            logger.error(f"Ошибка разрешения IP для {self.config['address']}: {e}")
            return "unknown"

    async def _get_country_by_ip(self) -> str:
        """Аналогично методу в VLESSClient"""
        if not self.server_ip or self.server_ip == "unknown":
            return "unknown"

        if self.server_ip in ip_country_cache:
            logger.info(f"Страна для IP {self.server_ip} взята из кэша: {ip_country_cache[self.server_ip]}")
            self.server_country = ip_country_cache[self.server_ip]
            return self.server_country

        await asyncio.sleep(1.5)  # Задержка для API лимита

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{GETIP_API_URL}/{self.server_ip}") as response:
                        if response.status == 200:
                            data = await response.json()
                            self.server_country = data.get('country', 'unknown')
                            ip_country_cache[self.server_ip] = self.server_country
                            logger.info(f"Получена страна для IP {self.server_ip}: {self.server_country}")
                            return self.server_country
                        # ... остальная часть как в VLESSClient ...
            except Exception as e:
                logger.error(f"Ошибка получения страны для IP {self.server_ip}: {e}")
                return "unknown"
        
        return "unknown"

    def _parse_vmess_url(self) -> Dict:
        """Парсинг VMESS URL (vmess://base64)."""
        try:
            # Удаляем префикс vmess://
            base64_str = self.vmess_url.replace('vmess://', '')
            
            # Добавляем padding если нужно
            padding = len(base64_str) % 4
            if padding:
                base64_str += '=' * (4 - padding)
            
            # Декодируем Base64
            decoded_bytes = base64.b64decode(base64_str)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Парсим JSON
            config = json.loads(decoded_str)
            
            return {
                'id': config.get('id'),
                'address': config.get('add'),
                'port': int(config.get('port', 443)),
                'network': config.get('net', 'tcp'),
                'type': config.get('type', 'none'),
                'host': config.get('host', ''),
                'path': config.get('path', '/'),
                'tls': config.get('tls', 'none')
            }
        except Exception as e:
            logger.error(f"Ошибка парсинга VMESS URL: {e}")
            return {
                'id': 'unknown',
                'address': 'unknown',
                'port': 443,
                'network': 'unknown',
                'type': 'none',
                'host': '',
                'path': '/',
                'tls': 'none'
            }

    def _display_config(self):
        """Отображение конфигурации VMESS."""
        table_data = [
            ["UUID", self.config['id']],
            ["Server Address", self.config['address']],
            ["Server IP", self.server_ip or "unknown"],
            ["Server Country", self.server_country or "unknown"],
            ["Port", self.config['port']],
            ["Network Type", self.config['network']],
            ["Path", self.config['path']],
            ["TLS", self.config['tls']],
            ["Local IP", self.local_ip]
        ]
        table = tabulate(table_data, headers=["Parameter", "Value"], tablefmt="grid")
        logger.info(f"\nVMESS Configuration:\n{table}")

    def connect_sync_websocket(self) -> bool:
        """Синхронное подключение через WebSocket."""
        if self.config['network'] != 'ws':
            logger.error("Синхронное подключение поддерживается только для WebSocket")
            return False

        headers = {
            "Sec-WebSocket-Protocol": f"vless {self.config['uuid']}"
        }
        ssl_context = None
        if self.config['security'] in ['tls', 'xtls']:
            ssl_context = {"cert_reqs": ssl.CERT_NONE}

        try:
            self.ws = websocket.WebSocket(sslopt=ssl_context)
            self.ws.connect(self._build_ws_url(), header=headers)
            logger.info(f"Успешное подключение по WebSocket к {self.config['address']} (IP: {self.server_ip}, Страна: {self.server_country})")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения WebSocket: {e}")
            return False

    async def connect_async_websocket(self):
        """Асинхронное подключение через WebSocket."""
        if self.config['network'] != 'ws':
            logger.error("Асинхронное подключение поддерживается только для WebSocket")
            return

        ssl_context = ssl.SSLContext() if self.config['security'] in ['tls', 'xtls'] else None
        headers = {"Sec-WebSocket-Protocol": f"vless {self.config['uuid']}"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.ws_connect(self._build_ws_url(), ssl=ssl_context, headers=headers) as ws:
                    logger.info(f"Успешное асинхронное подключение по WebSocket к {self.config['address']} (IP: {self.server_ip}, Страна: {self.server_country})")
                    await ws.send_json({"message": "test"})
                    async for msg in ws:
                        logger.info(f"Получено: {msg.data}")
                        break
            except Exception as e:
                logger.error(f"Ошибка асинхронного подключения WebSocket: {e}")

    def connect_tcp(self):
        """Подключение через TCP (заглушка)."""
        logger.warning(f"TCP-подключение не реализовано. Сервер IP: {self.server_ip}, Страна: {self.server_country}, Локальный IP: {self.local_ip}")

    def connect_grpc(self):
        """Подключение через gRPC (заглушка)."""
        logger.warning(f"gRPC-подключение не реализовано. Сервер IP: {self.server_ip}, Страна: {self.server_country}, Локальный IP: {self.local_ip}")

    async def connect(self):
        """Основной метод для подключения."""
        # Разрешаем IP и определяем страну
        self._resolve_server_ip()
        self.server_country = await self._get_country_by_ip()
        self._display_config()

        if self.config['network'] == 'ws':
            return self.connect_sync_websocket()
        elif self.config['network'] == 'tcp':
            return self.connect_tcp()
        elif self.config['network'] == 'grpc':
            return self.connect_grpc()
        else:
            logger.error(f"Неподдерживаемый тип транспорта: {self.config['network']}")
            return False

    def close(self):
        """Закрытие соединения."""
        if self.ws:
            self.ws.close()
            logger.info("Соединение закрыто")

class VPNAutomation:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.86'})
        # Список конфигураций для обработки капчи
        self.captcha_configs = [
            {'th1': 140, 'th2': 140, 'sig': 1},
            {'th1': 120, 'th2': 120, 'sig': 1.5},
            {'th1': 160, 'th2': 160, 'sig': 0.8},
            {'th1': 130, 'th2': 150, 'sig': 1.2},
            {'th1': 150, 'th2': 130, 'sig': 1.0}
        ]
        self.current_config_index = 0
        self.country_count = Counter()
        self.add_times = []
        self.success_count = 0
        self.fail_count = 0
        self.gui_root = None

    def init_driver(self):
        try:
            edge_options = EdgeOptions()
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_argument('--start-maximized')

            # Указываем путь к msedgedriver.exe через Service
            self.driver = webdriver.Edge(
                service=Service(r"msedgedriver.exe"),
                options=edge_options
            )
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации драйвера: {e}")
            return False

    def solve_captcha(self, current_url):
        try:
            # Находим изображение капчи
            captcha_img = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@class, 'mr-4')]")))
            captcha_url = captcha_img.get_attribute('src') or ""

            # Корректируем URL капчи
            if captcha_url.startswith('//'):
                captcha_url = 'https:' + captcha_url
            elif captcha_url.startswith('/'):
                captcha_url = urljoin(BASE_URL, captcha_url)
            elif not captcha_url.startswith('http'):
                captcha_url = urljoin(current_url, captcha_url)

            logger.info(f"Загружаем капчу по URL: {captcha_url}")

            # Загружаем изображение капчи
            response = self.session.get(captcha_url, timeout=10)
            image_data = BytesIO(response.content)
            original = Image.open(image_data)

            # Перебираем все конфигурации капчи
            initial_config_index = self.current_config_index
            tried_configs = []
            while len(tried_configs) < len(self.captcha_configs):
                config = self.captcha_configs[self.current_config_index]
                th1 = config['th1']
                th2 = config['th2']
                sig = config['sig']
                logger.info(f"Попытка распознавания капчи с конфигурацией: th1={th1}, th2={th2}, sig={sig}")

                # Обработка изображения
                black_and_white = original.convert("L")
                first_threshold = black_and_white.point(lambda p: p > th1 and 255)
                blur = numpy.array(first_threshold)
                blurred = gaussian_filter(blur, sigma=sig)
                blurred = Image.fromarray(blurred)
                final = blurred.point(lambda p: p > th2 and 255)
                final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
                final = final.filter(ImageFilter.SHARPEN)

                # Разделение изображения на 4 части
                width, height = final.size
                char_width = width // 4
                captcha_code = ""

                for i in range(4):
                    box = (i * char_width, 0, (i + 1) * char_width, height)
                    letter_img = final.crop(box)

                    # Распознавание символа
                    letter = pytesseract.image_to_string(
                        letter_img, config='--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    letter = re.sub(r'[^A-Z]', '', letter)  # Только большие буквы

                    if not letter:
                        letter = '?'  # Если не распозналось, временно ставим ?
                    captcha_code += letter
                    logger.info(f"Буква {i+1}: {letter}")

                # Проверяем, что код состоит из 4 больших букв
                if re.match(r'^[A-Z]{4}$', captcha_code):
                    logger.info(f"Распознанный код капчи: {captcha_code}")
                    # Устанавливаем следующую конфигурацию для следующей попытки
                    self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
                    return captcha_code.strip()
                else:
                    logger.warning(f"Некорректный код капчи: {captcha_code}, пробуем следующую конфигурацию")
                    tried_configs.append(self.current_config_index)
                    self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
                    # Если вернулись к начальной конфигурации, прерываем цикл
                    if self.current_config_index == initial_config_index:
                        break

            # Если не удалось получить корректный код
            logger.error("Не удалось распознать капчу с корректным кодом (4 большие буквы) после перебора всех конфигураций")
            self.driver.save_screenshot("captcha_error.png")
            self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
            return None

        except Exception as e:
            logger.error(f"Ошибка в solve_captcha: {e}")
            self.driver.save_screenshot("captcha_error.png")
            self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
            return None

    def check_error_messages(self):
        timeout = 15
        start = time.time()
        while time.time() - start < timeout:
            try:
                elems = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'bg-red-500')]")
                for el in elems:
                    text = el.text.strip()
                    if "Config did not pass the XRay Test" in text:
                        logger.warning("Конфиг не прошел XRay Test")
                        return "xray"
                    if "You cannot submit same config with different alias" in text:
                        logger.warning("Конфиг с таким alias уже существует")
                        return "alias"
                    if "The entered captcha was not correct! - try again" in text:
                        logger.warning("Капча неверная (логин)")
                        return "captcha_invalid"
                    if "Captcha is not valid" in text:
                        logger.warning("Капча неверная (добавление конфига)")
                        return "captcha_invalid"
                    if "Request failed with status code 500" in text:
                        logger.warning("Ошибка 500, попробуем через время...")
                        time.sleep(5)
                        return "error500"

                if self.driver.current_url == "https://www.mahsaserver.com/my-configs/":
                    logger.info("URL сменился на my-configs, вход успешен")
                    return "success"

                time.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка при проверке сообщений: {e}")
                time.sleep(1)
        logger.warning("Таймаут ожидания сообщения об ошибке, продолжаем проверку")
        return None

    def login(self, access_token):
        try:
            logger.info("Начало процесса входа с использованием access_token из LocalStorage")
            self.driver.get(BASE_URL)
            time.sleep(2)  # Ждем загрузки страницы

            # Устанавливаем access_token в LocalStorage, если предоставлен
            if access_token:
                self.driver.execute_script(f"window.localStorage.setItem('access_token', '{access_token}');")
                logger.info("access_token установлен в LocalStorage")

            # Обновляем страницу, чтобы сайт применил токен
            self.driver.refresh()
            time.sleep(5)  # Ждем применения токена

            # Проверяем, вошли ли мы, перейдя на защищенную страницу
            self.driver.get(urljoin(BASE_URL, "/my-configs/"))
            time.sleep(5)

            if 'login' in self.driver.current_url.lower():
                logger.error("access_token не сработал, вход невозможен")
                return False
            else:
                logger.info("Успешный вход в систему с использованием access_token")
                return True

        except Exception as e:
            logger.error(f"Критическая ошибка в процессе входа: {e}")
            self.driver.save_screenshot("login_critical_error.png")
            return False

    def add_configs(self, ads_text):
        try:
            logger.info("Чтение файла конфигов")
            with open(CFG_FILE, 'r', encoding='utf-8') as file:
                raw_configs = [line.strip() for line in file if line.strip()]

            if not raw_configs:
                raise ValueError("Файл конфигов пуст или не найден")

            logger.info(f"Найдено {len(raw_configs)} конфигов для добавления")

            self.driver.get(urljoin(BASE_URL, "/my-configs/"))
            time.sleep(3)

            # Удаление существующих конфигураций
            try:
                while True:
                    delete_buttons = self.driver.find_elements(By.XPATH,
                        "//button[contains(text(),'Delete') or contains(text(),'Удалить')]")
                    if not delete_buttons:
                        break
                    delete_buttons[0].click()
                    confirm_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Confirm') or contains(text(),'Подтвердить')]")))
                    confirm_btn.click()
                    time.sleep(3)
                    logger.info("Удален один конфиг")
            except Exception as e:
                logger.warning(f"Ошибка при удалении конфигов: {e}")

            self.success_count = 0
            self.fail_count = 0
            configs = []  # Список для хранения всех конфигураций с обновлёнными комментариями
            self.country_count = Counter()
            self.add_times = []

            for i, line in enumerate(raw_configs, 1):
                # Удаляем существующий комментарий, если есть
                if '#' in line:
                    line = line.split('#')[0].strip()

                # Проверяем конфигурацию через VLESSClient перед добавлением
                server_country = "unknown"
                try:
                    logger.info(f"Обработка конфигурации {i}/{len(raw_configs)}: {line}...")
                    client = VLESSClient(line)
                    # Разрешаем IP и получаем страну
                    client._resolve_server_ip()
                    server_country = asyncio.run(client._get_country_by_ip())
                    # Извлекаем тип конфигурации из начала URL
                    config_type = line.split('://')[0] if '://' in line else 'unknown'
                    server_ip = client.server_ip or 'unknown'
                    network_type = client.config['network'] or 'unknown'
                    # Формируем новую строку комментария без эмодзи
                    comment = f"({network_type}) {server_ip}: {server_country}"
                    config = f"{line}#{comment}"
                except Exception as e:
                    logger.error(f"Ошибка обработки конфигурации {line}...: {e}")
                    # Если не удалось разобрать конфигурацию, используем значения по умолчанию
                    comment = "(unknown) unknown: unknown"
                    config = f"{line}#{comment}"

                # Сохраняем конфигурацию с комментарием в список
                configs.append(config)

                # Добавляем конфигурацию на сайт
                captcha_attempts = 0
                max_attempts = 15
                self.current_config_index = 0  # Сбрасываем индекс конфигурации для нового конфига

                while captcha_attempts < max_attempts:
                    try:
                        logger.info(f"Добавление конфига {i}/{len(raw_configs)} (попытка капчи {captcha_attempts + 1}/{max_attempts}): {config}...")
                        self.driver.get(CONFIG_ADD_URL)
                        current_url = self.driver.current_url

                        # Извлекаем чистую конфигурацию без комментария для ввода
                        url_field = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.ID, "url")))
                        url_field.clear()
                        url_field.send_keys(config)  # Вводим только чистую конфигурацию без комментария

                        ads_field = self.driver.find_element(By.ID, "ads")
                        ads_field.clear()
                        ads_field.send_keys(ads_text)

                        captcha_code = self.solve_captcha(current_url)
                        if not captcha_code:
                            logger.warning("Пропуск конфига из-за ошибки капчи")
                            captcha_attempts += 1
                            self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
                            time.sleep(2)
                            continue

                        # Проверяем, что код капчи состоит из 4 больших букв
                        if not re.match(r'^[A-Z]{4}$', captcha_code):
                            logger.warning(f"Получен некорректный код капчи: {captcha_code}, попытка {captcha_attempts + 1}/{max_attempts}")
                            captcha_attempts += 1
                            self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
                            time.sleep(2)
                            continue

                        captcha_field = self.driver.find_element(By.ID, "captcha")
                        captcha_field.clear()
                        captcha_field.send_keys(captcha_code)

                        submit_btn = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                       "//button[contains(@class, 'bg-blue-600') and contains(., 'Submit')]")))
                        submit_btn.click()

                        result = self.check_error_messages()

                        if result == "captcha_invalid":
                            logger.warning(f"Капча неверная, попытка {captcha_attempts + 1}")
                            captcha_attempts += 1
                            self.current_config_index = (self.current_config_index + 1) % len(self.captcha_configs)
                            time.sleep(2)
                            continue

                        elif result in ("xray", "alias"):
                            logger.warning(f"Ошибка при добавлении конфига ({result}), продолжаем")
                            self.fail_count += 1
                            break
                            
                        elif result == "error500":
                            logger.warning(f"Сервера MahsaNG на данный момент не работают, попробуйте позже")
                            ew = tk.Tk()
                            ew.title = "ERROR"
                            ew.geometry('350x200')
                            btn = Button(ew, text = "Exit" ,fg = "red", command=self.gui_root.quit)

                        elif result == "success":
                            logger.info("Конфиг успешно добавлен")
                            self.success_count += 1
                            self.country_count[server_country] += 1
                            self.add_times.append(time.time())
                            
                            # Форматируем сообщение для Telegram
                            meta_text = escape_markdown(
                                f"#{config_type}, {server_ip} | "
                                f"#{network_type} | "
                                f"#{server_country.replace(' ', '_')}"
                            )
                            config_text = escape_markdown(config)
                            
                            message = f"{meta_text}\n`{config_text}`"
                            
                            if not send_telegram_message(message):
                                logger.warning("Не удалось отправить сообщение в Telegram")
                            break

                        else:
                            logger.warning("Неопознанный результат, помечаем как success: {server_ip}.")
                            self.success_count += 1
                            self.country_count[server_country] += 1
                            self.add_times.append(time.time())
                            
                            # Форматируем сообщение для Telegram
                            meta_text = escape_markdown(
                                f"#{config_type}, {server_ip} | "
                                f"#{network_type} | "
                                f"#{server_country.replace(' ', '_')}"
                            )
                            config_text = escape_markdown(config)
                            
                            message = f"{meta_text}\n`{config_text}`"
                            
                            if not send_telegram_message(message):
                                logger.warning("Не удалось отправить сообщение в Telegram")
                            break

                    except Exception as e:
                        logger.error(f"Ошибка при добавлении конфига: {e}")
                        self.fail_count += 1
                        break

                    time.sleep(WAIT_TIME)

                if captcha_attempts >= max_attempts:
                    logger.warning(f"Достигнуто максимальное количество попыток ({max_attempts}) для конфига {i}, продолжаем")
                    self.fail_count += 1
                    continue

                time.sleep(WAIT_TIME)

            # Перезаписываем файл со всеми конфигурациями (успешными и неуспешными)
            with open(CFG_FILE, 'w', encoding='utf-8') as f:
                for c in configs:
                    f.write(c + "\n")
            logger.info(f"Файл {CFG_FILE} перезаписан со всеми конфигурациями ({len(configs)} строк)")

            logger.info(f"Добавлено успешно: {self.success_count}, ошибок: {self.fail_count}")

        except Exception as e:
            logger.error(f"Ошибка в add_configs: {e}")
            # Перезаписываем файл даже в случае ошибки, чтобы сохранить все обработанные конфигурации
            with open(CFG_FILE, 'w', encoding='utf-8') as f:
                for c in configs:
                    f.write(c + "\n")
            logger.info(f"Файл {CFG_FILE} перезаписан со всеми конфигурациями ({len(configs)} строк) несмотря на ошибку")

    def show_stats(self):
        stats_window = tk.Toplevel(self.gui_root)
        stats_window.title("Статистика")

        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill='both', expand=True)

        # Вкладка Configs vs Time
        time_frame = ttk.Frame(notebook)
        notebook.add(time_frame, text='Configs vs Time')

        if self.add_times:
            fig_time, ax_time = plt.subplots()
            cumulative = list(range(1, len(self.add_times) + 1))
            ax_time.plot(self.add_times, cumulative)
            ax_time.set_xlabel('Time')
            ax_time.set_ylabel('Cumulative Configs')
            ax_time.set_title('Configs Added Over Time')

            canvas_time = FigureCanvasTkAgg(fig_time, master=time_frame)
            canvas_time.draw()
            canvas_time.get_tk_widget().pack(fill='both', expand=True)
        else:
            tk.Label(time_frame, text="Нет данных для графика Configs vs Time").pack()

        # Вкладка Configs vs Country (Pie Chart)
        country_frame = ttk.Frame(notebook)
        notebook.add(country_frame, text='Configs vs Country')

        if self.country_count:
            fig_country, ax_country = plt.subplots()
            ax_country.pie(self.country_count.values(), labels=self.country_count.keys(), autopct='%1.1f%%')
            ax_country.set_title('Configs Distribution by Country')

            canvas_country = FigureCanvasTkAgg(fig_country, master=country_frame)
            canvas_country.draw()
            canvas_country.get_tk_widget().pack(fill='both', expand=True)
        else:
            tk.Label(country_frame, text="Нет данных для графика Configs vs Country").pack()

    def run_automation(self, ads_text, access_token):
        if not self.init_driver():
            messagebox.showerror("Ошибка", "Не удалось инициализировать драйвер")
            return

        if not self.login(access_token):
            messagebox.showerror("Ошибка", "Не удалось войти в систему")
            self.driver.quit()
            return

        self.add_configs(ads_text)
        self.driver.quit()
        messagebox.showinfo("Завершено", "Автоматизация завершена")
        self.show_stats()

    def create_gui(self):
        self.gui_root = tk.Tk()
        self.gui_root.title("MahsaNG publish tool v08.25")
        
        # Центрируем окно
        w = self.gui_root.winfo_screenwidth()
        h = self.gui_root.winfo_screenheight()
        w = w // 2 - 228  # Центрируем по ширине
        h = h // 2 - 100  # Центрируем по высоте
        self.gui_root.geometry(f'456x200+{w}+{h}')
        
        # Создаем меню
        menubar = tk.Menu(self.gui_root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.gui_root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Фильтрация конфигураций по слову", command=lambda: os.system("python parse.py"))
        self.gui_root.config(menu=menubar)
        help_menu.add_command(label="Скачиватель из ссылок (из файла webs.txt)", command=lambda: os.system("python multidownloader.py"))
        self.gui_root.config(menu=menubar)
        help_menu.add_command(label="О программе", command=lambda: messagebox.showinfo("О программе", "MahsaNG publish tool v08.25\nАвтоматизация добавления VPN конфигураций\nBy AWCFG"))
        menubar.add_cascade(label="Справка", menu=help_menu)

        

        
        # Создаем фрейм для содержимого
        main_frame = tk.Frame(self.gui_root, padx=10, pady=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Поля ввода
        tk.Label(main_frame, text="Your Telegram User ID:").grid(row=0, column=0, sticky="w", pady=2)
        tg_userid = tk.Entry(main_frame, width=40)
        tg_userid.insert(0, TELEGRAM_CHAT_ID)
        tg_userid.grid(row=0, column=1, sticky="ew")
        
        tk.Label(main_frame, text="Telegram API Bot token:").grid(row=1, column=0, sticky="w", pady=2)
        tg_token = tk.Entry(main_frame, width=40)
        tg_token.insert(0, TELEGRAM_BOT_TOKEN)
        tg_token.grid(row=1, column=1, sticky="ew")
        
        tk.Label(main_frame, text="ADS Text:").grid(row=2, column=0, sticky="w", pady=2)
        ads_entry = tk.Entry(main_frame, width=40)
        ads_entry.insert(0, ADS_TEXT)
        ads_entry.grid(row=2, column=1, sticky="ew")
        
        tk.Label(main_frame, text="Access Token:").grid(row=3, column=0, sticky="w", pady=2)
        token_entry = tk.Entry(main_frame, width=40)
        token_entry.insert(0, ACCESS_TOKEN)
        token_entry.grid(row=3, column=1, sticky="ew")
        
        tk.Label(main_frame, text="Configs file path:").grid(row=4, column=0, sticky="w", pady=2)
        cfgfile = tk.Entry(main_frame, width=40)
        cfgfile.insert(0, CFG_FILE)
        cfgfile.grid(row=4, column=1, sticky="ew")
        
        # Кнопка запуска
        start_button = tk.Button(main_frame, text="Запустить", 
                               command=lambda: threading.Thread(target=self.run_automation, 
                                                              args=(ads_entry.get(), token_entry.get())).start())
        start_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Настройка веса строк и столбцов
        main_frame.columnconfigure(1, weight=1)
        self.gui_root.columnconfigure(0, weight=1)
        self.gui_root.rowconfigure(0, weight=1)
        
        self.gui_root.mainloop()

if __name__ == "__main__":
    bot = VPNAutomation()
    bot.create_gui()