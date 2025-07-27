from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from bs4 import BeautifulSoup
import threading
import time
import json
import requests
from requests.auth import HTTPDigestAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import logging
import os
import tempfile
from datetime import datetime
import queue
from typing import Optional, Dict, List, Any, Union
from filelock import FileLock
import subprocess
import traceback
import sys
import uuid
from flask_socketio import emit
import random

def handle_exception(exc_type, exc_value, exc_traceback):
    with open("error.log", "a") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    sys.exit(1)

sys.excepthook = handle_exception
# Настройка логирования

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

class WarrantyChecker:
    def __init__(self):
        self.base_url = "https://shop-repair.bitmain.com/api/warranty/getWarranty"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://service.bitmain.com/support/warranty',
            'Origin': 'https://service.bitmain.com',
            'DNT': '1',
        })
        self.history_file = os.path.join(monitor_server.data_dir, 'warranty_history.json')
        self.history = self.load_history()

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"Error loading warranty history: {e}")
            return []

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving warranty history: {e}")

    def check_serials(self, serials):
        """Проверяет гарантию для списка серийных номеров"""
        results = []
        total = len(serials)
        
        for index, serial in enumerate(serials, 1):
            serial = serial.strip()
            if not serial:
                continue
                
            try:
                time.sleep(8 + random.uniform(0, 5))
                
                params = {'serialNumber': serial}
                response = self.session.get(self.base_url, params=params, timeout=25)
                
                if response.status_code == 429:
                    result = {
                        'serial': serial,
                        'status': 'rate_limit',
                        'message': 'Превышен лимит запросов',
                        'date': None
                    }
                    results.append(result)
                    continue
                
                data = response.json()
                
                if response.status_code == 200 and 'warrantyEndDate' in data:
                    warranty_date = data['warrantyEndDate']
                    try:
                        dt = datetime.strptime(warranty_date, '%Y-%m-%d %H:%M:%S')
                        formatted_date = dt.strftime('%Y-%m-%d')
                        result = {
                            'serial': serial,
                            'status': 'ok',
                            'message': 'Гарантия действительна до',
                            'date': formatted_date
                        }
                    except ValueError:
                        result = {
                            'serial': serial,
                            'status': 'ok',
                            'message': 'Гарантия действительна до',
                            'date': warranty_date
                        }
                else:
                    result = {
                        'serial': serial,
                        'status': 'error',
                        'message': 'Данные о гарантии не найдены',
                        'date': None
                    }
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'serial': serial,
                    'status': 'error',
                    'message': f'Ошибка: {str(e)}',
                    'date': None
                })
            
            # Сохраняем в историю
            self.history.append({
                'serial': serial,
                'result': results[-1],
                'timestamp': datetime.now().isoformat()
            })
            
            # Периодически сохраняем историю
            if index % 5 == 0:
                self.save_history()
        
        self.save_history()
        return results

    def get_history(self, limit=50):
        """Возвращает историю проверок"""
        return sorted(self.history, key=lambda x: x['timestamp'], reverse=True)[:limit]

class WeathercloudAPI:
    def __init__(self):
        self.base_url = "https://app.weathercloud.net/device/stats"
        self.code = "1910596670"  # Ваш код устройства
        self.csrf_token = "YTl2Qm5sUGNrdmJEWDZHNWpEd051cXRzcHNxTXZ-blT_VZP710tJ3B8EfWXliEzfYkLXgGZ9d_C459gc8-ssWQ=="
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://app.weathercloud.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        })
        
    def get_weather_data(self):
        """Получение данных о погоде с Weathercloud"""
        params = {
            "code": self.code,
            "WEATHERCLOUD_CSRF_TOKEN": self.csrf_token
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return self._format_weather_data(response.json())
        except Exception as e:
            logging.error(f"Ошибка получения данных Weathercloud: {e}")
            return None
            
    def _format_weather_data(self, data):
        """Форматирование данных о погоде"""
        if not data:
            return None
            
        # Основные метрики (первый элемент - timestamp, второй - значение)
        current_values = {
            'temperature': data.get('temp_current', [0, 0])[1],
            'comfort_temperature': data.get('heat_current', [0, 0])[1],
            'humidity': data.get('hum_current', [0, 0])[1],
            'pressure': data.get('bar_current', [0, 0])[1] / 10,  # Переводим в гПа
            'wind_speed': data.get('wspd_current', [0, 0])[1],
            'wind_direction': data.get('wdir_current', [0, 0])[1],
            'dew_point': data.get('dew_current', [0, 0])[1],
            'solar_radiation': data.get('solarrad_current', [0, 0])[1],
            'uvi': data.get('uvi_current', [0, 0])[1],
            'rain_rate': data.get('rainrate_current', [0, 0])[1],
            'rain_today': data.get('rain_day_total', [0, 0])[1],
            'wind_gust': data.get('wspdhi_current', [0, 0])[1],
            'timestamp': data.get('last_update', 0),
            'date': datetime.fromtimestamp(data.get('last_update', 0)).isoformat() if data.get('last_update') else None
        }
        
        return current_values

class MinerMonitorServer:
    def __init__(self):
        self.data_dir = os.environ.get('MINER_MONITOR_DATA_DIR', os.path.abspath('miner_monitor_data'))
        self.file_lock = FileLock(os.path.join(self.data_dir, 'config.lock'))
        self.settings_file = os.path.join(self.data_dir, 'app_settings.json')
        self.ip_ranges_file = os.path.join(self.data_dir, 'ip_ranges.json')
        self.range_names_file = os.path.join(self.data_dir, 'range_names.json')
        self.active_ranges_file = os.path.join(self.data_dir, 'active_ranges.json')
        self.excluded_models_file = os.path.join(self.data_dir, 'excluded_models.json')
        self.range_cache_dir = os.path.join(self.data_dir, 'range_cache')
        self.monitoring_cycles = 0  # Счетчик кругов мониторинга


        self.default_settings = {
            "scan_timeout": 30,
            "max_workers": 50,
            "username": "root",
            "password": "root",
            "alarm_temp": 75,
            "alarm_power": 1300,
            "alarm_hashrate": 180,
            "scan_speed": "medium",
            "alarm_enabled": True,
            "alarm_sound": True,
            "min_voltage": 12.0,
            "max_voltage": 16.0,
            "voltage_step": 0.1
        }
        
        self.settings = self.default_settings.copy()
        self.miners = []
        self.cached_miners = []
        self.ip_ranges = []
        self.range_names = {}
        self.active_ranges = {}
        self.excluded_models = []
        self.monitoring = False
        self.stop_event = threading.Event()
        self.scan_lock = threading.Lock()
        self.update_queue = queue.Queue()
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.settings["username"], self.settings["password"])
        self.last_scan_time = None
        
        self.initialize_files()
        self.load_all_data()
        self.validate_ranges()
        
        self.start_autosave()
        threading.Thread(target=self.process_update_queue, daemon=True).start()

    def start_autosave(self, interval=300):
        """Запускает фоновый поток для автоматического сохранения данных"""
        def autosave_task():
            while True:
                time.sleep(interval)
                with self.file_lock:
                    try:
                        # Сохраняем данные всех диапазонов с отметками времени
                        for ip_range in self.ip_ranges:
                            if self.active_ranges.get(ip_range, False):
                                self.save_range_cache(ip_range)
                        
                        # Сохраняем основные файлы данных
                        self.save_ip_ranges()
                        self.save_range_names()
                        self.save_active_ranges()
                        
                        # Сохраняем время последнего сканирования
                        if self.last_scan_time:
                            with open(os.path.join(self.data_dir, 'last_scan.json'), 'w') as f:
                                json.dump({
                                    'timestamp': time.time(),
                                    'datetime': datetime.now().isoformat()
                                }, f)
                        
                        logging.debug("Автосохранение завершено")
                    except Exception as e:
                        logging.error(f"Ошибка автосохранения: {e}")

        threading.Thread(target=autosave_task, daemon=True).start()

    def clear_all_cache(self):
        """Полностью очищает все кешированные данные"""
        try:
            # Блокируем доступ на время очистки
            with self.file_lock:
                # Очищаем кеш диапазонов
                if os.path.exists(self.range_cache_dir):
                    for filename in os.listdir(self.range_cache_dir):
                        file_path = os.path.join(self.range_cache_dir, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            logging.error(f"Не удалось удалить файл кеша {file_path}: {e}")
                            continue
            
            # Очищаем список майнеров
                self.miners = []
            
            # Сбрасываем счетчик кругов
                self.monitoring_cycles = 0
            
                logging.info("Все кешированные данные успешно очищены")
                return True
            
        except Exception as e:
            logging.error(f"Критическая ошибка при очистке кеша: {e}")
            return False
    def validate_ranges(self):
        """Проверяет и инициализирует данные по диапазонам IP"""
        for ip_range in self.ip_ranges:
            if ip_range not in self.range_names:
                self.range_names[ip_range] = f"Диапазон {len(self.range_names)+1}"
            if ip_range not in self.active_ranges:
                self.active_ranges[ip_range] = True

    def check_file_permissions(self, file_path: str) -> bool:
        """Проверяет права доступа к файлу"""
        try:
            if os.path.exists(file_path):
                return os.access(file_path, os.R_OK | os.W_OK)
            else:
                dir_path = os.path.dirname(file_path)
                return os.access(dir_path, os.W_OK | os.X_OK)
        except Exception as e:
            logging.error(f"Permission check failed for {file_path}: {e}")
            return False

    def initialize_files(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            if os.name == 'nt':
                import win32api, win32con
                win32api.SetFileAttributes(self.data_dir, win32con.FILE_ATTRIBUTE_NORMAL)
            
            if hasattr(os, 'chmod'):
                os.chmod(self.data_dir, 0o777)
            
            os.makedirs(self.range_cache_dir, exist_ok=True)
            if os.name == 'nt':
                win32api.SetFileAttributes(self.range_cache_dir, win32con.FILE_ATTRIBUTE_NORMAL)
            if hasattr(os, 'chmod'):
                os.chmod(self.range_cache_dir, 0o777)
            
        except Exception as e:
            logging.error(f"Cannot initialize data directory: {e}")
            raise

        for file_path, default_data in [
            (self.settings_file, self.default_settings),
            (self.ip_ranges_file, []),
            (self.range_names_file, {}),
            (self.active_ranges_file, {}),
            (self.excluded_models_file, [])
        ]:
            with self.file_lock:
                try:
                    if not os.path.exists(file_path):
                        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as temp_file:
                            json.dump(default_data, temp_file, indent=4, ensure_ascii=False)
                        os.replace(temp_file.name, file_path)
                        os.chmod(file_path, 0o644)
                        logging.info(f"Created default file: {file_path}")
                    elif not self.check_file_permissions(file_path):
                        raise PermissionError(f"No read/write permissions for {file_path}")
                except Exception as e:
                    logging.error(f"Failed to initialize file {file_path}: {e}")
                    self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                        'message': f"Failed to initialize file {file_path}: {msg}",
                        'type': 'error'
                    }))
                    raise

    def load_all_data(self):
        try:
            self.load_settings()
            self.load_ip_ranges()
            self.load_range_names()
            self.load_active_ranges()
            self.load_excluded_models()
    
        # Очищаем текущий список майнеров перед загрузкой кеша
            self.miners = []
        
        # Загружаем кешированные данные
            cached_ranges = self.get_all_cached_ranges()
            for ip_range, cache_data in cached_ranges.items():
                if ip_range in self.ip_ranges and self.active_ranges.get(ip_range, False):
                # Полностью заменяем данные майнеров для этого диапазона
                    range_miners = cache_data.get('miners', [])
                
                # Удаляем старые майнеры этого диапазона
                    start_ip, end_ip = ip_range.split('-')
                    self.miners = [
                        m for m in self.miners 
                        if not (
                            self.ip_to_int(m["IP"]) >= self.ip_to_int(start_ip) and 
                            self.ip_to_int(m["IP"]) <= self.ip_to_int(end_ip)
                        )
                    ]
                
                # Добавляем свежие данные из кеша
                    self.miners.extend(range_miners)
    
            logging.info("All data loaded successfully")
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def save_range_cache(self, ip_range: str):
        try:
            os.makedirs(self.range_cache_dir, exist_ok=True)

            start_ip, end_ip = ip_range.split('-')
            range_miners = [m for m in self.miners 
                        if self.ip_to_int(m["IP"]) >= self.ip_to_int(start_ip) and 
                        self.ip_to_int(m["IP"]) <= self.ip_to_int(end_ip)]

        # Получаем timestamp последнего обновления
            last_updated = max(
                [m.get("last_updated_timestamp", time.time()) 
                for m in range_miners],
                default=time.time()
            )

            cache_file = os.path.join(self.range_cache_dir, f"{ip_range.replace('-', '_')}.json")

            cache_data = {
            'miners': range_miners,
            'stats': self.calculate_range_stats(ip_range),
            'last_scan': time.time(),  # Сохраняем как timestamp
            'last_updated': last_updated,
            'range_name': self.range_names.get(ip_range, ip_range),
            'timestamp': time.time()  # Текущее время сохранения кеша
            }

        # Atomic write
            temp_file = f"{cache_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=4, ensure_ascii=False)

        # Replace existing file
            if os.path.exists(cache_file):
                os.remove(cache_file)
            os.rename(temp_file, cache_file)
            os.chmod(cache_file, 0o644)

        except Exception as e:
            logging.error(f"Failed to save cache for range {ip_range}: {e}")

    def is_data_fresh(self, timestamp, max_age_seconds=3600):
        """Проверяет, насколько свежие данные по timestamp"""
        if not timestamp:
            return False
        return time.time() - float(timestamp) < max_age_seconds        

    def get_all_cached_ranges(self) -> Dict:
        """Возвращает данные всех кешированных диапазонов с проверкой валидности"""
        cached_ranges = {}
        try:
            if os.path.exists(self.range_cache_dir):
                for filename in os.listdir(self.range_cache_dir):
                    if filename.endswith('.json'):
                        try:
                            ip_range = filename.replace('_', '-').replace('.json', '')
                            cache_file = os.path.join(self.range_cache_dir, filename)
                    
                            with open(cache_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                        
                        # Добавляем timestamp если отсутствует (для обратной совместимости)
                            if 'timestamp' not in data:
                                data['timestamp'] = time.time()
                            if 'last_updated' not in data:
                            # Если нет last_updated, используем last_scan или текущее время
                                if 'last_scan' in data:
                                    try:
                                        data['last_updated'] = datetime.strptime(data['last_scan'], "%Y-%m-%d %H:%M:%S").timestamp()
                                    except:
                                        data['last_updated'] = time.time()
                                else:
                                    data['last_updated'] = time.time()
                        
                            cached_ranges[ip_range] = data
                        
                        except json.JSONDecodeError as e:
                            logging.error(f"Invalid JSON in cache file {filename}: {e}")
                        except Exception as e:
                            logging.error(f"Error loading cache file {filename}: {e}")
        except Exception as e:
            logging.error(f"Failed to load cached ranges: {e}")
        return cached_ranges

    def validate_cache_data(self, data: dict) -> bool:
        """Проверяет что загруженные кешированные данные имеют правильную структуру"""
        required_keys = ['miners', 'stats', 'last_scan']
        if not all(key in data for key in required_keys):
            return False
        
        # Дополнительные проверки
        if not isinstance(data.get('miners', []), list):
            return False
        if not isinstance(data.get('stats', {}), dict):
            return False
        
        return True

    def load_range_cache(self, ip_range: str) -> Optional[Dict]:
        try:
            cache_file = os.path.join(self.range_cache_dir, f"{ip_range.replace('-', '_')}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Конвертация старых форматов
                    if 'last_scan' in data and isinstance(data['last_scan'], str):
                        try:
                            data['last_scan'] = datetime.fromisoformat(data['last_scan']).timestamp()
                        except:
                            data['last_scan'] = time.time()
                        
                    if 'last_updated' in data and isinstance(data['last_updated'], str):
                        try:
                            data['last_updated'] = datetime.fromisoformat(data['last_updated']).timestamp()
                        except:
                            data['last_updated'] = time.time()
                        
                    return data
        except Exception as e:
            logging.error(f"Failed to load cache for range {ip_range}: {e}")
        return None

    def save_settings(self):
        try:
            temp_path = f"{self.settings_file}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        
            # Atomic replace
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
            os.rename(temp_path, self.settings_file)
        
            # Set proper permissions
            if os.name == 'nt':
                import win32api, win32con
                win32api.SetFileAttributes(self.settings_file, win32con.FILE_ATTRIBUTE_NORMAL)
            if hasattr(os, 'chmod'):
                os.chmod(self.settings_file, 0o666)
            
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            return False

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                if not self.check_file_permissions(self.settings_file):
                    raise PermissionError(f"No read permissions for {self.settings_file}")
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    for key in ['scan_timeout', 'max_workers', 'alarm_temp', 'alarm_power', 'alarm_hashrate']:
                        if key in loaded_settings:
                            loaded_settings[key] = float(loaded_settings[key])
                    self.settings.update(loaded_settings)
                logging.info(f"Settings loaded from {self.settings_file}: {loaded_settings}")
            else:
                logging.warning(f"Settings file {self.settings_file} not found, creating default")
                self.save_settings()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to load settings: {msg}",
                'type': 'error'
            }))
            self.settings = self.default_settings.copy()
            self.save_settings()

    def save_ip_ranges(self):
        try:
            if not self.check_file_permissions(self.ip_ranges_file):
                raise PermissionError(f"No write permissions for {self.ip_ranges_file}")
        
            temp_path = f"{self.ip_ranges_file}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.ip_ranges, f, indent=4, ensure_ascii=False)
        
            if os.path.exists(self.ip_ranges_file):
                os.remove(self.ip_ranges_file)
            os.rename(temp_path, self.ip_ranges_file)
            logging.info(f"IP ranges saved to {self.ip_ranges_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving IP ranges: {str(e)}", exc_info=True)
            return False

    def load_ip_ranges(self):
        try:
            if os.path.exists(self.ip_ranges_file):
                if not self.check_file_permissions(self.ip_ranges_file):
                    raise PermissionError(f"No read permissions for {self.ip_ranges_file}")
                with open(self.ip_ranges_file, 'r', encoding='utf-8') as f:
                    self.ip_ranges = json.load(f)
                logging.info(f"Loaded {len(self.ip_ranges)} IP ranges: {self.ip_ranges}")
            else:
                logging.warning(f"IP ranges file {self.ip_ranges_file} not found, creating empty")
                self.ip_ranges = []
                self.save_ip_ranges()
        except Exception as e:
            logging.error(f"Error loading IP ranges: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to load IP ranges: {msg}",
                'type': 'error'
            }))
            self.ip_ranges = []
            self.save_ip_ranges()

    def save_range_names(self):
        try:
            temp_path = f"{self.range_names_file}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.range_names, f, indent=4, ensure_ascii=False)
        
            if os.path.exists(self.range_names_file):
                os.remove(self.range_names_file)
            os.rename(temp_path, self.range_names_file)
            logging.info(f"Range names saved to {self.range_names_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving range names: {str(e)}", exc_info=True)
            return False

    def load_range_names(self):
        try:
            if os.path.exists(self.range_names_file):
                if not self.check_file_permissions(self.range_names_file):
                    raise PermissionError(f"No read permissions for {self.range_names_file}")
                with open(self.range_names_file, 'r', encoding='utf-8') as f:
                    self.range_names = json.load(f)
                logging.info(f"Loaded names for {len(self.range_names)} ranges: {self.range_names}")
            else:
                logging.warning(f"Range names file {self.range_names_file} not found, creating empty")
                self.range_names = {}
                self.save_range_names()
        except Exception as e:
            logging.error(f"Error loading range names: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to load range names: {msg}",
                'type': 'error'
            }))
            self.range_names = {}
            self.save_range_names()

    def save_active_ranges(self):
        with self.file_lock:
            try:
                if not self.check_file_permissions(self.data_dir):
                    raise PermissionError(f"No write permissions for {self.data_dir}")
                
                temp_dir = os.path.dirname(self.active_ranges_file)
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    encoding='utf-8',
                    dir=temp_dir,
                    delete=False
                ) as temp_file:
                    json.dump(self.active_ranges, temp_file, indent=4, ensure_ascii=False)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                
                if os.path.exists(self.active_ranges_file):
                    os.remove(self.active_ranges_file)
                
                os.rename(temp_file.name, self.active_ranges_file)
                os.chmod(self.active_ranges_file, 0o644)
                logging.info(f"Active ranges saved to {self.active_ranges_file}: {self.active_ranges}")
                self.update_queue.put(lambda: socketio.emit('notification', {
                    'message': "Active ranges saved successfully",
                    'type': 'success'
                }))
                return True
            except Exception as e:
                logging.error(f"Error saving active ranges to {self.active_ranges_file}: {e}")
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                    'message': f"Failed to save active ranges: {msg}",
                    'type': 'error'
                }))
                if 'temp_file' in locals() and os.path.exists(temp_file.name):
                    try:
                        os.remove(temp_file.name)
                    except:
                        pass
                return False

    def load_active_ranges(self):
        try:
            if os.path.exists(self.active_ranges_file):
                if not self.check_file_permissions(self.active_ranges_file):
                    raise PermissionError(f"No read permissions for {self.active_ranges_file}")
                with open(self.active_ranges_file, 'r', encoding='utf-8') as f:
                    self.active_ranges = json.load(f)
                logging.info(f"Loaded active status for {len(self.active_ranges)} ranges: {self.active_ranges}")
            else:
                logging.warning(f"Active ranges file {self.active_ranges_file} not found, creating empty")
                self.active_ranges = {}
                self.save_active_ranges()
        except Exception as e:
            logging.error(f"Error loading active ranges: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to load active ranges: {msg}",
                'type': 'error'
            }))
            self.active_ranges = {}
            self.save_active_ranges()

    def save_excluded_models(self):
        with self.file_lock:
            try:
                if not self.check_file_permissions(self.data_dir):
                    raise PermissionError(f"No write permissions for {self.data_dir}")
                
                temp_dir = os.path.dirname(self.excluded_models_file)
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    encoding='utf-8',
                    dir=temp_dir,
                    delete=False
                ) as temp_file:
                    json.dump(self.excluded_models, temp_file, indent=4, ensure_ascii=False)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                
                if os.path.exists(self.excluded_models_file):
                    os.remove(self.excluded_models_file)
                
                os.rename(temp_file.name, self.excluded_models_file)
                os.chmod(self.excluded_models_file, 0o644)
                logging.info(f"Excluded models saved to {self.excluded_models_file}: {self.excluded_models}")
                self.update_queue.put(lambda: socketio.emit('notification', {
                    'message': "Excluded models saved successfully",
                    'type': 'success'
                }))
                return True
            except Exception as e:
                logging.error(f"Error saving excluded models to {self.excluded_models_file}: {e}")
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                    'message': f"Failed to save excluded models: {msg}",
                    'type': 'error'
                }))
                if 'temp_file' in locals() and os.path.exists(temp_file.name):
                    try:
                        os.remove(temp_file.name)
                    except:
                        pass
                return False

    def load_excluded_models(self):
        try:
            if os.path.exists(self.excluded_models_file):
                if not self.check_file_permissions(self.excluded_models_file):
                    raise PermissionError(f"No read permissions for {self.excluded_models_file}")
                with open(self.excluded_models_file, 'r', encoding='utf-8') as f:
                    self.excluded_models = json.load(f)
                logging.info(f"Loaded {len(self.excluded_models)} excluded models: {self.excluded_models}")
            else:
                logging.warning(f"Excluded models file {self.excluded_models_file} not found, creating empty")
                self.excluded_models = []
                self.save_excluded_models()
        except Exception as e:
            logging.error(f"Error loading excluded models: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to load excluded models: {msg}",
                'type': 'error'
            }))
            self.excluded_models = []
            self.save_excluded_models()

    def get_miner_summary(self, ip: str) -> Optional[dict]:
        """Получает данные summary.cgi с майнера"""
        try:
            response = self.send_request('GET', f"http://{ip}/cgi-bin/summary.cgi")
            if response and response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Error getting summary from {ip}: {e}")
            return None

    def get_miner_warnings(self, ip: str) -> Optional[dict]:
        """Получает данные warning.cgi с майнера"""
        try:
            response = self.send_request('GET', f"http://{ip}/cgi-bin/warning.cgi")
            if response and response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Error getting warnings from {ip}: {e}")
            return None

    def get_miner_errors(self, ip: str) -> dict:
        """Получает все ошибки майнера из summary.cgi и warning.cgi"""
        errors = {
            "network": None,
            "fans": None,
            "temperature": None,
            "performance": None,
            "other_warnings": []
        }
        
        # Получаем данные summary.cgi
        summary_data = self.get_miner_summary(ip)
        if summary_data and "SUMMARY" in summary_data and summary_data["SUMMARY"]:
            summary = summary_data["SUMMARY"][0]
            
            # Обрабатываем все статусы
            for status in summary.get("status", []):
                if not isinstance(status, dict):
                    continue
                    
                status_type = status.get("type")
                status_msg = status.get("msg", "")
                
                # Ошибка сети
                if status_type == "network" and status.get("status") == "e":
                    errors["network"] = {
                        "code": status.get("code", ""),
                        "message": status_msg or "Network connection issue",
                        "source": "summary.cgi"
                    }
                
                # Ошибка вентиляторов
                elif status_type == "fans" and status.get("status") == "e":
                    errors["fans"] = {
                        "code": status.get("code", ""),
                        "message": status_msg or "Fan malfunction",
                        "source": "summary.cgi"
                    }
                
                # Ошибка температуры
                elif status_type == "temp" and status.get("status") == "e":
                    errors["temperature"] = {
                        "code": status.get("code", ""),
                        "message": status_msg or "Temperature warning",
                        "source": "summary.cgi"
                    }
                
                # Ошибка хешрейта
                elif status_type == "rate" and status.get("status") == "e":
                    errors["performance"] = {
                        "code": status.get("code", ""),
                        "message": status_msg or "Low hashrate",
                        "source": "summary.cgi"
                    }
        
        # Получаем данные warning.cgi
        warning_data = self.get_miner_warnings(ip)
        if warning_data:
            # Основное сообщение об ошибке
            if warning_data.get("error_message"):
                errors["other_warnings"].append({
                    "message": warning_data["error_message"],
                    "source": "warning.cgi"
                })
            
            # Дополнительные предупреждения
            for warning in warning_data.get("WARNING", []):
                if isinstance(warning, dict) and (warning.get("suggestion") or warning.get("code")):
                    errors["other_warnings"].append({
                        "code": warning.get("code", ""),
                        "message": warning.get("suggestion", "Unknown warning"),
                        "suggestion": warning.get("suggestion", ""),
                        "timestamp": warning.get("timestamp", ""),
                        "source": "warning.cgi"
                    })
        
        return errors

    def calculate_power(self, model: str, hashrate: float, system_info_response) -> float:
        """Рассчитывает мощность майнера в зависимости от модели"""
        if model == "Antminer S21+":
            return float(system_info_response.json().get("watt", 0)) if system_info_response else 0.0
        elif model == "Antminer S19k Pro":
            return float(hashrate) * 0.024
        elif model == "Antminer S19 Pro":
            return float(hashrate) * 0.030
        elif model == "Antminer S19i":
            return float(hashrate) * 0.035
        else:
            return float(system_info_response.json().get("power", 0)) if system_info_response and system_info_response.status_code == 200 else 0.0

    def calculate_efficiency(self, hashrate: float, power: float) -> float:
        """Рассчитывает эффективность майнера"""
        if float(hashrate) > 0 and float(power) > 0:
            return round(float(power) / (float(hashrate) / 1000), 1)
        return 0.0

    def scan_miners(self):
        while True:
            try:
                while self.monitoring and not self.stop_event.is_set():
                    start_scan_time = time.time()
                
                # Увеличиваем счетчик кругов
                    self.monitoring_cycles += 1
                    logging.debug(f"Текущий цикл мониторинга: {self.monitoring_cycles}")
                
                # Проверяем необходимость очистки кеша
                    if self.monitoring_cycles >= 10:
                        logging.info("Достигнуто 10 циклов мониторинга - очищаем кеш")
                        if self.clear_all_cache():
                            self.update_queue.put(lambda: socketio.emit('notification', {
                            'message': "Автоматическая очистка кеша выполнена, начинаем новое сканирование",
                            'type': 'info'
                            }))
                        # Сбрасываем счетчик циклов
                            self.monitoring_cycles = 0
                        # Немедленно начинаем новое сканирование
                            continue  # Переходим к следующей итерации цикла while
                        else:
                            self.update_queue.put(lambda: socketio.emit('notification', {
                            'message': "Не удалось выполнить автоматическую очистку кеша",
                            'type': 'warning'
                            }))
                
                # Получаем список активных диапазонов
                    active_ranges = [r for r in self.ip_ranges if self.active_ranges.get(r, False)]
                
                    if not active_ranges:
                        self.update_queue.put(lambda: socketio.emit('notification', {
                        'message': "Нет активных диапазонов для сканирования!",
                        'type': 'warning'
                        }))
                        time.sleep(5)
                        continue

                    logging.info(f"Начато сканирование {len(active_ranges)} активных диапазонов")
                    self.update_queue.put(lambda: socketio.emit('scan_state', {'scanning': True}))

                # Сканируем каждый диапазон по очереди
                    for ip_range in active_ranges:
                        if self.stop_event.is_set():
                            break
                        
                    # Полностью очищаем майнеров только текущего диапазона
                        start_ip, end_ip = ip_range.split('-')
                        self.miners = [
                            m for m in self.miners 
                            if not self.is_miner_in_range(m["IP"], ip_range)
                        ]
                    
                    # Генерируем IP для текущего диапазона
                        ips = self.generate_ip_range(start_ip, end_ip)
                        total_ips = len(ips)
                        scanned_ips = 0
                    
                    # Параллельное сканирование
                        with ThreadPoolExecutor(max_workers=int(self.settings["max_workers"])) as executor:
                            futures = []
                            for ip in ips:
                                if self.stop_event.is_set():
                                    break
                                futures.append(executor.submit(self.scan_miner, ip))
                            
                            for future in as_completed(futures):
                                if self.stop_event.is_set():
                                    break
                                
                                scanned_ips += 1
                                progress = min(1.0, scanned_ips / total_ips) if total_ips > 0 else 0
                            
                            # Обновляем прогресс
                                if time.time() - start_scan_time > 0.3:
                                    self.update_queue.put(lambda p=progress: socketio.emit('scan_progress', {
                                    'progress': p,
                                    'scanned': scanned_ips,
                                    'total': total_ips,
                                    'current_range': ip_range
                                    }))
                                    start_scan_time = time.time()

                    # После сканирования диапазона сохраняем его кеш
                            if not self.stop_event.is_set():
                                self.save_range_cache(ip_range)
                                stats = self.calculate_range_stats(ip_range)
                                self.update_queue.put(lambda r=ip_range, s=stats: 
                                    socketio.emit('range_update', {
                                'range': r,
                                'name': self.range_names.get(r, r),
                                'stats': s,
                                'has_problems': self.check_range_problems(s),
                                'last_scan': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'sortable': True
                                    }))

                # После сканирования всех диапазонов
                        if not self.stop_event.is_set():
                            self.update_queue.put(lambda: socketio.emit('miners_data', {
                        'miners': self.get_miners_data(),
                        'sortable_columns': [
                            'IP', 'Model', 'Name', 'Hashrate', 'Firmware', 
                            'UpTime', 'Freq', 'Chain0', 'Chain1', 'Chain2',
                            'Chain0_SN', 'Chain1_SN', 'Chain2_SN',
                            'Voltage', 'Power', 'Temp', 'TempTarget', 
                            'Efficiency', 'MAC', 'Serinum', 'Tuned'
                            ]
                            }))
                    
                        self.last_scan_time = datetime.now()
                        logging.info(f"Сканирование завершено. Найдено {len(self.miners)} майнеров")

                # Пауза между сканированиями
                    scan_delay = {
                    'low': 180,
                    'medium': 120,
                    'high': 60
                    }.get(self.settings.get('scan_speed', 'medium'), 120)
                
                    time.sleep(scan_delay)

            except Exception as e:
                logging.error(f"Критическая ошибка в цикле сканирования: {str(e)}", exc_info=True)
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Ошибка сканирования: {msg}",
                'type': 'error'
                }))
                time.sleep(30)
        
            finally:
                self.update_queue.put(lambda: socketio.emit('scan_state', {'scanning': False}))
                self.update_queue.put(lambda: socketio.emit('scan_progress', {
                'progress': 1,
                'scanned': total_ips if 'total_ips' in locals() else 0,
                'total': total_ips if 'total_ips' in locals() else 0
                }))
            
                if not self.monitoring:
                    break

    def get_cache_status(self):
        """Возвращает статус кеша и счетчик циклов"""
        return {
        'cycles': self.monitoring_cycles,
        'next_clear': 10 - self.monitoring_cycles if self.monitoring_cycles < 10 else 0,
        'cache_size': len(os.listdir(self.range_cache_dir)) if os.path.exists(self.range_cache_dir) else 0
        }        

    def is_miner_in_range(self, miner_ip: str, ip_range: str) -> bool:
        """Проверяет принадлежит ли майнер указанному диапазону"""
        start_ip, end_ip = ip_range.split('-')
        return (self.ip_to_int(miner_ip) >= self.ip_to_int(start_ip) and 
            (self.ip_to_int(miner_ip) <= self.ip_to_int(end_ip)))   

    def scan_miner(self, ip: str):
        if self.stop_event.is_set():
            return

        try:
        # Получаем основную статистику
            stats_response = self.send_request('GET', f"http://{ip}/cgi-bin/stats.cgi")
            if not stats_response or stats_response.status_code != 200:
                return

            stats_data = stats_response.json()
            model = stats_data.get("INFO", {}).get("type", "0")
            if model in self.excluded_models:
                logging.debug(f"Model {model} excluded for {ip}")
                return

            # Получаем все ошибки
            miner_errors = self.get_miner_errors(ip)
    
            # Получаем дополнительную информацию
            config = self.get_miner_config(ip)
            pools = self.send_request('GET', f"http://{ip}/cgi-bin/pools.cgi")
            system_info = self.send_request('GET', f"http://{ip}/cgi-bin/get_system_info.cgi")

        # Обработка данных цепей и температуры
            chain_freqs = [0, 0, 0]
            chain_sns = ["N/A", "N/A", "N/A"]  # Добавляем список для серийных номеров
        
            if "STATS" in stats_data and len(stats_data["STATS"]) > 0:
                chains = stats_data["STATS"][0].get("chain", [])
                for chain in chains:
                    idx = chain.get("index", 0)
                    if 0 <= idx < 3:
                        chain_freqs[idx] = chain.get("freq_avg", 0)
                        chain_sns[idx] = chain.get("sn", "N/A")  # Получаем серийный номер

            avg_temp = round(self.get_miner_temperature(stats_data, ip))
            hashrate = float(stats_data.get("STATS", [{}])[0].get("rate_5s", 0))
    
        # Расчет мощности в зависимости от модели
            power = 0.0
            if model == "Antminer S21+":
                power = float(stats_data.get("STATS", [{}])[0].get("watt", 0))
            elif model == "Antminer S19k Pro":
                power = float(hashrate) * 0.024
            elif model == "Antminer S19 Pro":
                power = float(hashrate) * 0.030
            elif model == "Antminer S19i":
                power = float(hashrate) * 0.035
            else:
                power = float(system_info.json().get("power", 0)) if system_info and system_info.status_code == 200 else 0.0
    
        # Округляем мощность до целого числа
            power = round(power)
            efficiency = self.calculate_efficiency(hashrate, power)

        # Формируем данные майнера
            miner_data = {
        "IP": ip,
        "Model": model,
        "Name": pools.json()["POOLS"][0].get("user", "N/A") if pools and pools.status_code == 200 else "N/A",
        "Hashrate": hashrate,
        "Firmware": stats_data.get("INFO", {}).get("CompileTime", "Unknown"),
        "UpTime": stats_data.get("STATS", [{}])[0].get("elapsed", 0),
        "Freq": config.get("bitmain-freq-chain", "0") if config else "0",
        "Chain0": chain_freqs[0],
        "Chain1": chain_freqs[1],
        "Chain2": chain_freqs[2],
        "Chain0_SN": chain_sns[0],  # Добавляем серийный номер первой платы
        "Chain1_SN": chain_sns[1],  # Добавляем серийный номер второй платы
        "Chain2_SN": chain_sns[2],  # Добавляем серийный номер третьей платы
        "Voltage": config.get("bitmain-volt-chain", "0") if config else "0",
        "Power": power,
        "Temp": avg_temp,
        "TempTarget": int(config.get("bitmain-temp-target", "0")) if config else 0,
        "Efficiency": efficiency,
        "MAC": system_info.json().get("macaddr", "N/A") if system_info else "N/A",
        "Serinum": system_info.json().get("serinum", "N/A") if system_info else "N/A",
        "Tuned": False,
        "last_updated": datetime.now().isoformat(),  # для совместимости
        "last_updated_timestamp": time.time(),  # для внутренних расчетов
        "errors": miner_errors,
        "has_errors": any(
            miner_errors["network"] or 
            miner_errors["fans"] or 
            miner_errors["temperature"] or 
            miner_errors["performance"] or 
            miner_errors["other_warnings"]
            )
            }

            with self.scan_lock:
                existing_index = next((i for i, m in enumerate(self.miners) if m["IP"] == ip), -1)
                if existing_index >= 0:
                    self.miners[existing_index] = miner_data
                else:
                    self.miners.append(miner_data)
        
                self.update_queue.put(lambda m=miner_data: socketio.emit('new_miner', m))

        except Exception as e:
            logging.error(f"Error scanning {ip}: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
        'message': f"Error scanning miner {ip}: {msg}",
        'type': 'error'
            }))
        finally:
            self.update_queue.put(lambda: socketio.emit('miners_count', {'count': len(self.miners)}))

    def check_specific_errors(self, miner_data: dict) -> dict:
        """Проверяет конкретные ошибки майнера"""
        errors = miner_data.get("errors", {})
        
        return {
            "has_network_error": bool(errors.get("network")),
            "has_fan_error": bool(errors.get("fans")),
            "has_temp_error": bool(errors.get("temperature")),
            "has_perf_error": bool(errors.get("performance")),
            "has_other_errors": len(errors.get("other_warnings", [])) > 0,
            "network_error": errors.get("network"),
            "fan_error": errors.get("fans"),
            "temp_error": errors.get("temperature"),
            "perf_error": errors.get("performance"),
            "other_errors": errors.get("other_warnings", []),
            "last_error_time": max(
                [
                    e.get("timestamp") 
                    for e in [
                        errors.get("network", {}),
                        errors.get("fans", {}),
                        errors.get("temperature", {}),
                        errors.get("performance", {}),
                        *errors.get("other_warnings", [])
                    ] 
                    if e and e.get("timestamp")
                ],
                default=None
            )
        }

    def get_miner_config(self, ip: str) -> Optional[Dict]:
        try:
            response = self.send_request('GET', f"http://{ip}/cgi-bin/get_miner_conf.cgi")
            return response.json() if response and response.status_code == 200 else None
        except Exception as e:
            logging.error(f"Error getting config for {ip}: {e}")
            return None

    def get_miner_temperature(self, stats_data: dict, ip: str) -> float:
        try:
            max_temp = 0.0
        
            if "STATS" not in stats_data or len(stats_data["STATS"]) == 0:
                return max_temp
            
            chains = stats_data["STATS"][0].get("chain", [])
        
            for chain in chains:
                temp_chip = chain.get("temp_chip", [])
                if len(temp_chip) >= 4:
                    chain_max_temp = max(temp_chip[2], temp_chip[3])
                    if chain_max_temp > max_temp:
                        max_temp = chain_max_temp
        
            return max_temp if max_temp > 0 else 0.0
        
        except Exception as e:
            logging.error(f"Error processing temperature data for {ip}: {e}")
            return 0.0

    def send_request(self, method: str, url: str, max_retries=1, **kwargs) -> Optional[requests.Response]:
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method, url,
                    timeout=int(self.settings["scan_timeout"]),
                    headers={
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    **kwargs
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.debug(f"Request error (attempt {attempt+0}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(1 * (attempt + 0))
        return None

    def send_async_request(self, method: str, url: str, **kwargs):
        def fire_and_forget():
            try:
                requests.request(
                    method=method,
                    url=url,
                    timeout=2,
                    auth=HTTPDigestAuth(self.settings["username"], self.settings["password"]),
                    **kwargs
                )
            except Exception as e:
                logging.error(f"Async request error: {e}")

        threading.Thread(target=fire_and_forget, daemon=True).start()

    def generate_ip_range(self, start_ip: str, end_ip: str) -> List[str]:
        try:
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            
            if start > end:
                return []
                
            ip_range = []
            current = start
            while current <= end:
                ip_range.append(str(current))
                current += 1
                
            return ip_range
        except Exception as e:
            logging.error(f"Error generating IP range {start_ip}-{end_ip}: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to generate IP range {start_ip}-{end_ip}: {msg}",
                'type': 'error'
            }))
            return []

    def ip_to_int(self, ip: str) -> int:
        try:
            return int(ipaddress.IPv4Address(ip))
        except Exception as e:
            logging.error(f"Error converting IP {ip} to integer: {e}")
            return 0

    def validate_ip_range(self, start_ip: str, end_ip: str) -> bool:
        try:
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            return start <= end
        except ipaddress.AddressValueError:
            return False

    def validate_single_ip(self, ip: str) -> bool:
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

    def start_monitoring(self):
        if not self.monitoring:
            self.stop_event.clear()
            self.monitoring = True
            self.scan_thread = threading.Thread(target=self.scan_miners, daemon=True)
            self.scan_thread.start()
            logging.info("Monitoring started")
            self.update_queue.put(lambda: socketio.emit('notification', {
                'message': "Monitoring started",
                'type': 'success'
            }))
            socketio.emit('monitoring_state', {'monitoring': True})
            self.update_range_stats()

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            self.stop_event.set()
            logging.info("Monitoring stopped")
            self.update_queue.put(lambda: socketio.emit('notification', {
                'message': "Monitoring stopped",
                'type': 'success'
            }))
            socketio.emit('monitoring_state', {'monitoring': False})
            self.update_range_stats()

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def add_ip_range(self, start_ip: str, end_ip: str) -> bool:
        ip_range = f"{start_ip}-{end_ip}"
        try:
            with self.file_lock:
                self.ip_ranges.append(ip_range)
                self.range_names[ip_range] = f"Диапазон {len(self.ip_ranges)}"
                self.active_ranges[ip_range] = True
            
                if not all([
                    self.save_ip_ranges(),
                    self.save_range_names(),
                    self.save_active_ranges()
                ]):
                    raise IOError("Failed to save one or more files")
            
                logging.info(f"Added range: {ip_range}")
                return True
        except Exception as e:
            logging.error(f"Error adding range: {str(e)}")
            if ip_range in self.ip_ranges:
                self.ip_ranges.remove(ip_range)
            if ip_range in self.range_names:
                del self.range_names[ip_range]
            if ip_range in self.active_ranges:
                del self.active_ranges[ip_range]
            return False

    def remove_ip_range(self, ip_range: str) -> bool:
        try:
            with self.file_lock:
                self.ip_ranges.remove(ip_range)
                if ip_range in self.range_names:
                    del self.range_names[ip_range]
                if ip_range in self.active_ranges:
                    del self.active_ranges[ip_range]
            
                if not all([
                    self.save_ip_ranges(),
                    self.save_range_names(),
                    self.save_active_ranges()
                ]):
                    raise IOError("Failed to save one or more files")
            
                logging.info(f"Removed range: {ip_range}")
                return True
        except Exception as e:
            logging.error(f"Error removing range: {str(e)}")
            return False

    def rename_range(self, ip_range: str, new_name: str) -> bool:
        try:
            with self.file_lock:
                self.range_names[ip_range] = new_name
                if not self.save_range_names():
                    raise IOError("Failed to save range names")
            
                logging.info(f"Renamed {ip_range} to {new_name}")
                return True
        except Exception as e:
            logging.error(f"Error renaming range: {str(e)}")
            return False

    def toggle_range_active(self, ip_range: str, active: bool) -> bool:
        if ip_range in self.ip_ranges:
            try:
                self.active_ranges[ip_range] = active
                self.save_active_ranges()
                logging.info(f"Set range {ip_range} active={active}")
                self.update_queue.put(lambda: socketio.emit('notification', {
                    'message': f"Range {ip_range} set to {'active' if active else 'inactive'}",
                    'type': 'success'
                }))
                return True
            except Exception as e:
                logging.error(f"Failed to toggle range {ip_range}: {e}")
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                    'message': f"Failed to toggle range: {msg}",
                    'type': 'error'
                }))
                return False
        return False

    def select_all_ranges(self):
        try:
            for ip_range in self.ip_ranges:
                self.active_ranges[ip_range] = True
            self.save_active_ranges()
            logging.info("Selected all IP ranges")
            self.update_queue.put(lambda: socketio.emit('notification', {
                'message': "All IP ranges selected",
                'type': 'success'
            }))
        except Exception as e:
            logging.error(f"Failed to select all ranges: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to select all ranges: {msg}",
                'type': 'error'
            }))

    def deselect_all_ranges(self):
        try:
            for ip_range in self.ip_ranges:
                self.active_ranges[ip_range] = False
            self.save_active_ranges()
            logging.info("Deselected all IP ranges")
            self.update_queue.put(lambda: socketio.emit('notification', {
                'message': "All IP ranges deselected",
                'type': 'success'
            }))
        except Exception as e:
            logging.error(f"Failed to deselect all ranges: {e}")
            self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                'message': f"Failed to deselect all ranges: {msg}",
                'type': 'error'
            }))

    def add_excluded_model(self, model: str) -> bool:
        if model and model not in self.excluded_models:
            try:
                self.excluded_models.append(model)
                self.save_excluded_models()
                logging.info(f"Added excluded model: {model}")
                self.update_queue.put(lambda: socketio.emit('notification', {
                    'message': f"Model {model} added to excluded list",
                    'type': 'success'
                }))
                return True
            except Exception as e:
                logging.error(f"Failed to add excluded model {model}: {e}")
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                    'message': f"Failed to add excluded model: {msg}",
                    'type': 'error'
                }))
                self.excluded_models.remove(model)
                return False
        return False

    def remove_excluded_model(self, model: str) -> bool:
        if model in self.excluded_models:
            try:
                self.excluded_models.remove(model)
                self.save_excluded_models()
                logging.info(f"Removed excluded model: {model}")
                self.update_queue.put(lambda: socketio.emit('notification', {
                    'message': f"Model {model} removed from excluded list",
                    'type': 'success'
                }))
                return True
            except Exception as e:
                logging.error(f"Failed to remove excluded model {model}: {e}")
                self.update_queue.put(lambda msg=str(e): socketio.emit('notification', {
                    'message': f"Failed to remove excluded model: {msg}",
                    'type': 'error'
                }))
                return False
        return False

    def update_settings(self, new_settings: dict) -> bool:
        try:
            required_fields = ['scan_timeout', 'max_workers', 'username', 'password']
            for field in required_fields:
                if field not in new_settings:
                    raise ValueError(f"Missing required field: {field}")
        
            # Convert numeric settings
            for key in ['scan_timeout', 'max_workers', 'alarm_temp', 'alarm_power', 'alarm_hashrate']:
                if key in new_settings:
                    new_settings[key] = float(new_settings[key])
        
            self.settings.update(new_settings)
        
            self.session.auth = HTTPDigestAuth(
                self.settings["username"],
                self.settings["password"]
            )
        
            return self.save_settings()
        except Exception as e:
            logging.error(f"Failed to update settings: {e}")
            return False

    def get_miners_data(self) -> List[Dict]:
        miners = self.miners.copy()
        for miner in miners:
            miner['data_fresh'] = self.is_data_fresh(
                datetime.fromisoformat(miner["last_updated"]).timestamp() 
                if "last_updated" in miner else None
            )
        return miners

    def get_ranges_data(self) -> List[Dict]:
        return [{
            'range': ip_range,
            'name': self.range_names.get(ip_range, ip_range),
            'active': self.active_ranges.get(ip_range, True)
        } for ip_range in self.ip_ranges]

    def get_excluded_models(self) -> List[str]:
        return self.excluded_models

    def get_settings(self) -> Dict:
        return self.settings

    def process_update_queue(self):
        while True:
            try:
                task = self.update_queue.get(timeout=1)
                if callable(task):
                    task()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Queue processing error: {e}")

    def calculate_range_stats(self, ip_range: str) -> dict:
        start_ip, end_ip = ip_range.split('-')
    
        miners_in_range = [
            m for m in self.miners 
            if self.ip_to_int(m["IP"]) >= self.ip_to_int(start_ip) and 
            self.ip_to_int(m["IP"]) <= self.ip_to_int(end_ip)
        ]
    
        fresh_miners = [m for m in miners_in_range 
                    if self.is_data_fresh(datetime.fromisoformat(m["last_updated"]).timestamp())]
    
        if not miners_in_range:
            return {
            "avg_hashrate": 0,
            "avg_power": 0,
            "avg_efficiency": 0,
            "avg_temp": 0,
            "online_count": 0,
            "problem_count": 0,
            "network_errors": 0,
            "fan_errors": 0,
            "temp_errors": 0,
            "perf_errors": 0,
            "other_errors": 0,
            "fresh_data_ratio": 0,
            "last_updated": None
            }
    
        problem_count = 0
        network_errors = 0
        fan_errors = 0
        temp_errors = 0
        perf_errors = 0
        other_errors = 0
    
        for miner in miners_in_range:
            errors = self.check_specific_errors(miner)
            if errors["has_network_error"]:
                network_errors += 1
                problem_count += 1
            if errors["has_fan_error"]:
                fan_errors += 1
                problem_count += 1
            if errors["has_temp_error"]:
                temp_errors += 1
                problem_count += 1
            if errors["has_perf_error"]:
                perf_errors += 1
                problem_count += 1
            if errors["has_other_errors"]:
                other_errors += len(errors["other_errors"])
                problem_count += len(errors["other_errors"])
    
        online_count = len(miners_in_range)
        avg_hashrate = sum(float(m["Hashrate"]) for m in miners_in_range) / online_count
        avg_power = sum(float(m["Power"]) for m in miners_in_range) / online_count
        avg_temp = sum(float(m["Temp"]) for m in miners_in_range) / online_count
    
        total_hashrate = sum(float(m["Hashrate"]) for m in miners_in_range)
        total_power = sum(float(m["Power"]) for m in miners_in_range)
        avg_efficiency = total_power / (total_hashrate / 1000) if total_hashrate > 0 else 0
    
        return {
        "avg_hashrate": avg_hashrate,
        "avg_power": avg_power,
        "avg_efficiency": avg_efficiency,
        "avg_temp": avg_temp,
        "online_count": online_count,
        "problem_count": problem_count,
        "network_errors": network_errors,
        "fan_errors": fan_errors,
        "temp_errors": temp_errors,
        "perf_errors": perf_errors,
        "other_errors": other_errors,
        "has_problems": problem_count > 0,
        "fresh_data_ratio": len(fresh_miners) / len(miners_in_range),
        "last_updated": max(
            [m.get("last_updated_timestamp", time.time()) 
            for m in miners_in_range],
            default=time.time()
        ),
        "has_stale_data": len(fresh_miners) < len(miners_in_range)
        }

    def check_range_problems(self, stats):
        return (stats["avg_temp"] > float(self.settings["alarm_temp"]) or
                stats["avg_power"] > float(self.settings["alarm_power"]) or
                stats["avg_hashrate"] < float(self.settings["alarm_hashrate"]))

    def reboot_miners(self, ips: list):
        for ip in ips:
            self.send_async_request(
                'POST',
                f"http://{ip}/cgi-bin/reboot.cgi",
                json={'reboot': True}
            )

    def toggle_blink(self, ips: list, enable: bool):
        for ip in ips:
            self.send_async_request(
                'POST',
                f"http://{ip}/cgi-bin/blink.cgi",
                json={'blink': enable}
            )

    def adjust_voltage(self, ips: list, delta: float):
        for ip in ips:
            try:
                config = self.get_miner_config(ip)
                if not config:
                    continue
                
                current_voltage_str = config.get("volt-chain", "0.0")
                try:
                    current_voltage = float(current_voltage_str)
                except (ValueError, TypeError):
                    logging.error(f"Invalid voltage value for {ip}: {current_voltage_str}")
                    continue
                
                new_voltage = round(current_voltage + delta, 1)

                if new_voltage < float(self.settings["min_voltage"]):
                    continue
                if new_voltage > float(self.settings["max_voltage"]):
                    continue
                
                updated_config = config.copy()
                updated_config["bitmain-volt-chain"] = f"{new_voltage:.1f}"
            
                self.send_async_request(
                'POST',
                f"http://{ip}/cgi-bin/set_miner_conf.cgi",
                json=updated_config
                )
            except Exception as e:
                logging.error(f"Error adjusting voltage for {ip}: {e}")

    def adjust_temp_target(self, ips: list, delta: int):
        for ip in ips:
            try:
                config = self.get_miner_config(ip)
                if not config:
                    continue
                    
                current_temp_target = int(config.get("bitmain-temp-target", "68"))
                new_temp_target = current_temp_target + delta
                
                if new_temp_target < 50 or new_temp_target > 80:
                    continue
                    
                updated_config = config.copy()
                updated_config["bitmain-temp-target"] = str(new_temp_target)
                
                self.send_async_request(
                    'POST',
                    f"http://{ip}/cgi-bin/set_miner_conf.cgi",
                    json=updated_config
                )
            except Exception as e:
                logging.error(f"Error adjusting temp target for {ip}: {e}")

    def update_range_stats(self):
        range_stats = {}
        for ip_range in self.ip_ranges:
            if not self.active_ranges.get(ip_range, False):
                continue
                
            stats = self.calculate_range_stats(ip_range)
            name = self.range_names.get(ip_range, ip_range)
            range_stats[ip_range] = {
                'name': name,
                'stats': stats,
                'has_problems': self.check_range_problems(stats)
            }
        
        self.update_queue.put(lambda: socketio.emit('range_stats', range_stats))

    def update_single_range_stats(self, ip_range: str):
        if not self.active_ranges.get(ip_range, False):
            return
                
        stats = self.calculate_range_stats(ip_range)
        name = self.range_names.get(ip_range, ip_range)
        
        self.update_queue.put(lambda: socketio.emit('range_update', {
            'range': ip_range,
            'name': name,
            'stats': stats,
            'has_problems': self.check_range_problems(stats),
            'last_scan': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }))

# Инициализация сервера
weather_api = WeathercloudAPI()
weathercloud_api = WeathercloudAPI()

try:
    monitor_server = MinerMonitorServer()
    warranty_checker = WarrantyChecker()  # Добавьте эту строку
except Exception as e:
    logging.error(f"Failed to initialize MinerMonitorServer: {e}")
    raise

# Маршруты Flask
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/api/warranty/check', methods=['POST'])
def api_warranty_check():
    data = request.get_json()
    if not data or 'serials' not in data:
        return jsonify({'success': False, 'message': 'Необходим список серийных номеров'}), 400
    
    serials = data['serials']
    if not isinstance(serials, list):
        return jsonify({'success': False, 'message': 'Серийные номера должны быть в виде массива'}), 400
    
    try:
        results = warranty_checker.check_serials(serials)
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/warranty/history', methods=['GET'])
def api_warranty_history():
    limit = request.args.get('limit', default=50, type=int)
    try:
        history = warranty_checker.get_history(limit)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/cache/full_clear', methods=['POST'])  # Изменили имя на full_clear
def clear_cache_completely():
    try:
        if monitor_server.clear_all_cache():
            return jsonify({
                'success': True,
                'message': 'Кеш полностью очищен',
                'status': monitor_server.get_cache_status()
            })
        return jsonify({
            'success': False,
            'message': 'Не удалось очистить кеш',
            'status': monitor_server.get_cache_status()
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': monitor_server.get_cache_status()
        }), 500

@app.route('/api/cached_ranges', methods=['GET'])
def get_cached_ranges():
    return jsonify(monitor_server.get_all_cached_ranges())

@app.route('/api/miners', methods=['GET'])
def get_miners():
    miners = monitor_server.get_miners_data()
    return jsonify({
        'miners': miners,
        'fresh_count': sum(1 for m in miners if m.get('data_fresh', False)),
        'total_count': len(miners),
        'timestamp': time.time()  # Время генерации ответа
    })

@app.route('/api/ranges', methods=['GET'])
def get_ranges():
    ranges = monitor_server.get_ranges_data()
    stats = {r['range']: monitor_server.calculate_range_stats(r['range']) for r in ranges}
    return jsonify({
        'ranges': ranges,
        'stats': stats,
        'timestamp': time.time()
    })

@app.route('/api/excluded_models', methods=['GET'])
def get_excluded_models():
    return jsonify(monitor_server.get_excluded_models())

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(monitor_server.get_settings())

@app.route('/api/miner/<ip>/errors', methods=['GET'])
def get_miner_errors(ip):
    miner = next((m for m in monitor_server.miners if m["IP"] == ip), None)
    if not miner:
        return jsonify({"error": "Miner not found"}), 404
    
    errors = monitor_server.check_specific_errors(miner)
    return jsonify(errors)

@app.route('/api/miners/errors', methods=['GET'])
def get_all_errors():
    miners_with_errors = []
    for miner in monitor_server.miners:
        if miner.get("has_errors", False):
            errors = monitor_server.check_specific_errors(miner)
            miners_with_errors.append({
                "IP": miner["IP"],
                "Model": miner["Model"],
                "errors": errors
            })
    
    return jsonify({"miners_with_errors": miners_with_errors})

@app.route('/api/journal/load', methods=['GET'])
def load_journal():
    try:
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        if os.path.exists(journal_file):
            with open(journal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify({
                    'success': True,
                    'entries': data.get('entries', []),
                    'timestamp': data.get('timestamp')
                })
        return jsonify({'success': True, 'entries': []})
    except Exception as e:
        logging.error(f"Error loading journal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/journal/save', methods=['POST'])
def save_journal():
    try:
        data = request.get_json()
        if not data or 'entries' not in data:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
            
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        journal_data = {
            'entries': data['entries'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Atomic write
        temp_file = f"{journal_file}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(journal_data, f, indent=4, ensure_ascii=False)
        
        # Replace existing file
        if os.path.exists(journal_file):
            os.remove(journal_file)
        os.rename(temp_file, journal_file)
        
        return jsonify({
            'success': True,
            'timestamp': journal_data['timestamp']
        })
    except Exception as e:
        logging.error(f"Error saving journal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/weather', methods=['GET'])
def api_weather():
    """Endpoint для получения данных о погоде (сначала Weathercloud, потом Gismeteo)"""
    try:
        # Пробуем получить данные от Weathercloud
        weather_data = weathercloud_api.get_weather_data()
        source = 'weathercloud'
        
        # Если не получилось, пробуем Gismeteo
        if not weather_data:
            weather_data = weather_api.get_current_weather(coordinates="56.026443,92.895187")
            source = 'gismeteo'
        
        if weather_data:
            return jsonify({
                'temperature': weather_data.get('temperature'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'wind_speed': weather_data.get('wind_speed'),
                'wind_direction': weather_data.get('wind_direction'),
                'dew_point': weather_data.get('dew_point', None),
                'solar_radiation': weather_data.get('solar_radiation', None),
                'rain': weather_data.get('rain_today', None),
                'last_updated': weather_data.get('date'),
                'source': source,
                'status': 'success'
            })
        return jsonify({
            'error': 'Не удалось получить данные о погоде',
            'status': 'error'
        }), 500
    except Exception as e:
        logging.error(f"Ошибка в API погоды: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Внутренняя ошибка сервера: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/cache/status', methods=['GET'])
def get_cache_status():
    return jsonify(monitor_server.get_cache_status())  

@app.route('/api/ranges/add', methods=['POST'])
def add_range():
    data = request.get_json()
    logging.info(f"Add range request: {data}")
    
    if not data or 'start_ip' not in data or 'end_ip' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.add_ip_range(data['start_ip'], data['end_ip']):
        return jsonify({
            'success': True,
            'ranges': monitor_server.get_ranges_data()
        })
    return jsonify({'success': False, 'message': 'Failed to add range'}), 400

@app.route('/api/ranges/remove', methods=['POST'])
def remove_range():
    data = request.get_json()
    logging.info(f"Remove range request: {data}")
    
    if not data or 'range' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.remove_ip_range(data['range']):
        return jsonify({
            'success': True,
            'ranges': monitor_server.get_ranges_data()
        })
    return jsonify({'success': False, 'message': 'Range not found'}), 404

@app.route('/api/ranges/rename', methods=['POST'])
def rename_range():
    data = request.get_json()
    logging.info(f"Rename range request: {data}")
    
    if not data or 'range' not in data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.rename_range(data['range'], data['name']):
        return jsonify({
            'success': True,
            'ranges': monitor_server.get_ranges_data()
        })
    return jsonify({'success': False, 'message': 'Range not found'}), 404

@app.route('/api/ranges/toggle', methods=['POST'])
def toggle_range():
    data = request.get_json()
    logging.info(f"Toggle range request: {data}")
    
    if not data or 'range' not in data or 'active' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.toggle_range_active(data['range'], data['active']):
        return jsonify({
            'success': True,
            'ranges': monitor_server.get_ranges_data()
        })
    return jsonify({'success': False, 'message': 'Range not found'}), 404

@app.route('/api/reload_cache', methods=['POST'])
def reload_cache():
    try:
        monitor_server.load_all_data()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/infantry', methods=['GET'])
def get_infantry():
    miners_with_errors = []
    for miner in monitor_server.miners:
        if miner.get("has_errors", False):
            errors = monitor_server.check_specific_errors(miner)
            miners_with_errors.append({
                "IP": miner["IP"],
                "Model": miner["Model"],
                "Name": miner["Name"],
                "Hashrate": miner["Hashrate"],
                "Temp": miner["Temp"],
                "errors": errors,
                "last_error_time": errors.get("last_error_time")
            })
    
    # Сортировка по времени последней ошибки (новые сверху)
    miners_with_errors.sort(
        key=lambda x: x["last_error_time"] or "",
        reverse=True
    )
    
    return jsonify({
        "miners_with_errors": miners_with_errors,
        "network_errors": sum(1 for m in miners_with_errors if m["errors"]["has_network_error"]),
        "fan_errors": sum(1 for m in miners_with_errors if m["errors"]["has_fan_error"]),
        "temp_errors": sum(1 for m in miners_with_errors if m["errors"]["has_temp_error"]),
        "perf_errors": sum(1 for m in miners_with_errors if m["errors"]["has_perf_error"]),
        "other_errors": sum(1 for m in miners_with_errors if m["errors"]["has_other_errors"])
    })

@app.route('/api/ranges/select_all', methods=['POST'])
def select_all_ranges():
    monitor_server.select_all_ranges()
    return jsonify({
        'success': True,
        'ranges': monitor_server.get_ranges_data()
    })

@app.route('/api/ranges/deselect_all', methods=['POST'])
def deselect_all_ranges():
    monitor_server.deselect_all_ranges()
    return jsonify({
        'success': True,
        'ranges': monitor_server.get_ranges_data()
    })

@app.route('/api/excluded_models/add', methods=['POST'])
def add_excluded_model():
    data = request.get_json()
    logging.info(f"Add excluded model request: {data}")
    
    if not data or 'model' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.add_excluded_model(data['model']):
        return jsonify({
            'success': True,
            'excluded_models': monitor_server.get_excluded_models()
        })
    return jsonify({'success': False, 'message': 'Failed to add model'}), 400

@app.route('/api/excluded_models/remove', methods=['POST'])
def remove_excluded_model():
    data = request.get_json()
    logging.info(f"Remove excluded model request: {data}")
    
    if not data or 'model' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.remove_excluded_model(data['model']):
        return jsonify({
            'success': True,
            'excluded_models': monitor_server.get_excluded_models()
        })
    return jsonify({'success': False, 'message': 'Model not found'}), 404

@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    data = request.get_json()
    logging.info(f"Update settings request: {data}")
    
    if not data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if monitor_server.update_settings(data):
        return jsonify({
            'success': True,
            'settings': monitor_server.get_settings()
        })
    return jsonify({'success': False, 'message': 'Invalid settings'}), 400

@app.route('/api/control/monitoring', methods=['POST'])
def control_monitoring():
    data = request.get_json()
    logging.info(f"Control monitoring request: {data}")
    
    if not data or 'action' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    if data['action'] == 'start':
        monitor_server.start_monitoring()
    elif data['action'] == 'stop':
        monitor_server.stop_monitoring()
    elif data['action'] == 'toggle':
        monitor_server.toggle_monitoring()
    else:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    return jsonify({
        'success': True,
        'monitoring': monitor_server.monitoring
    })

@app.route('/monitoring')
def monitoring_page():
    return render_template('monitoring.html')  # Обратите внимание на render_template

@app.route('/api/control/reboot', methods=['POST'])
def control_reboot():
    data = request.get_json()
    logging.info(f"Reboot request: {data}")
    
    if not data or 'ips' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    monitor_server.reboot_miners(data['ips'])
    return jsonify({
        'success': True,
        'message': f"Reboot command sent to {len(data['ips'])} devices"
    })

@app.route('/api/control/blink', methods=['POST'])
def control_blink():
    data = request.get_json()
    logging.info(f"Blink control request: {data}")
    
    if not data or 'ips' not in data or 'enable' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    monitor_server.toggle_blink(data['ips'], data['enable'])
    return jsonify({
        'success': True,
        'message': f"Blink {'enabled' if data['enable'] else 'disabled'} for {len(data['ips'])} devices"
    })

@app.route('/api/control/voltage', methods=['POST'])
def control_voltage():
    data = request.get_json()
    logging.info(f"Voltage control request: {data}")
    
    if not data or 'ips' not in data or 'delta' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    monitor_server.adjust_voltage(data['ips'], float(data['delta']))
    return jsonify({
        'success': True,
        'message': f"Voltage adjustment sent to {len(data['ips'])} devices"
    })

@app.route('/warranty')
def warranty_page():
    return render_template('warranty.html')

@app.route('/api/control/temp_target', methods=['POST'])
def control_temp_target():
    data = request.get_json()
    logging.info(f"Temp target control request: {data}")
    
    if not data or 'ips' not in data or 'delta' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    monitor_server.adjust_temp_target(data['ips'], int(data['delta']))
    return jsonify({
        'success': True,
        'message': f"Temperature target adjustment sent to {len(data['ips'])} devices"
    })

# Обработчики событий Socket.IO
@socketio.on('get_infantry')
def handle_get_infantry():
    miners_with_errors = []
    for miner in monitor_server.miners:
        if miner.get("has_errors", False):
            errors = monitor_server.check_specific_errors(miner)
            miners_with_errors.append({
                "IP": miner["IP"],
                "Model": miner["Model"],
                "Name": miner["Name"],
                "Hashrate": miner["Hashrate"],
                "Temp": miner["Temp"],
                "errors": errors,
                "last_error_time": errors.get("last_error_time")
            })
    
    # Сортировка по времени последней ошибки (новые сверху)
    miners_with_errors.sort(
        key=lambda x: x["last_error_time"] or "",
        reverse=True
    )
    
    return {
        "miners_with_errors": miners_with_errors,
        "network_errors": sum(1 for m in miners_with_errors if m["errors"]["has_network_error"]),
        "fan_errors": sum(1 for m in miners_with_errors if m["errors"]["has_fan_error"]),
        "temp_errors": sum(1 for m in miners_with_errors if m["errors"]["has_temp_error"]),
        "perf_errors": sum(1 for m in miners_with_errors if m["errors"]["has_perf_error"]),
        "other_errors": sum(1 for m in miners_with_errors if m["errors"]["has_other_errors"])
    }

@socketio.on('get_miner_errors')
def handle_get_miner_errors(data):
    ip = data.get('ip')
    if not ip:
        return {"error": "IP address required"}
    
    miner = next((m for m in monitor_server.miners if m["IP"] == ip), None)
    if not miner:
        return {"error": "Miner not found"}
    
    return monitor_server.check_specific_errors(miner)

@socketio.on('get_cached_ranges')
def handle_get_cached_ranges(data=None):
    try:
        cached_ranges = monitor_server.get_all_cached_ranges()
        return cached_ranges
    except Exception as e:
        logging.error(f"Error getting cached ranges: {e}")
        return {}
    
# Добавьте эти обработчики Socket.IO в ваш файл server.py

@socketio.on('journal:load')
def handle_journal_load():
    try:
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        if os.path.exists(journal_file):
            with open(journal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                emit('journal:data', {
                    'entries': data.get('entries', []),
                    'timestamp': data.get('timestamp')
                })
        else:
            emit('journal:data', {'entries': [], 'timestamp': None})
    except Exception as e:
        logging.error(f"Error loading journal: {e}")
        emit('journal:error', {'message': str(e)})

@socketio.on('journal:add')
def handle_journal_add(entry):
    try:
        # Add ID if missing
        if 'id' not in entry:
            entry['id'] = str(uuid.uuid4())
            
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        data = {'entries': [], 'timestamp': datetime.now().isoformat()}
        
        if os.path.exists(journal_file):
            with open(journal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # Add new entry
        data['entries'].append(entry)
        data['timestamp'] = datetime.now().isoformat()
        
        # Save to file
        with open(journal_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Broadcast to all clients
        emit('journal:added', entry, broadcast=True)
    except Exception as e:
        logging.error(f"Error adding journal entry: {e}")
        emit('journal:error', {'message': str(e)})

@socketio.on('warranty:check')
def handle_warranty_check(data):
    if not data or 'serials' not in data:
        emit('warranty:error', {'message': 'Необходим список серийных номеров'})
        return
    
    serials = data['serials']
    if not isinstance(serials, list):
        emit('warranty:error', {'message': 'Серийные номера должны быть в виде массива'})
        return
    
    try:
        emit('warranty:progress', {'total': len(serials), 'checked': 0})
        
        results = []
        for i, serial in enumerate(serials, 1):
            result = warranty_checker.check_serials([serial])[0]
            results.append(result)
            emit('warranty:progress', {
                'total': len(serials),
                'checked': i,
                'current': result
            })
            time.sleep(1)  # Минимальная задержка между запросами
        
        emit('warranty:results', {
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('warranty:error', {'message': str(e)})

@socketio.on('warranty:get_history')
def handle_warranty_history(data):
    limit = data.get('limit', 50)
    try:
        history = warranty_checker.get_history(limit)
        emit('warranty:history', {
            'history': history,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('warranty:error', {'message': str(e)})

@socketio.on('journal:delete')
def handle_journal_delete(entry_id):
    try:
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        if os.path.exists(journal_file):
            with open(journal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Remove entry
            data['entries'] = [e for e in data['entries'] if e.get('id') != entry_id]
            data['timestamp'] = datetime.now().isoformat()
            
            # Save to file
            with open(journal_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Broadcast to all clients
            emit('journal:deleted', entry_id, broadcast=True)
    except Exception as e:
        logging.error(f"Error deleting journal entry: {e}")
        emit('journal:error', {'message': str(e)})

@socketio.on('journal:clear')
def handle_journal_clear():
    try:
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        data = {'entries': [], 'timestamp': datetime.now().isoformat()}
        
        # Save to file
        with open(journal_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Broadcast to all clients
        emit('journal:cleared', broadcast=True)
    except Exception as e:
        logging.error(f"Error clearing journal: {e}")
        emit('journal:error', {'message': str(e)})

@socketio.on('journal:save')
def handle_journal_save():
    try:
        journal_file = os.path.join(monitor_server.data_dir, 'duty_journal.json')
        if os.path.exists(journal_file):
            timestamp = datetime.now().isoformat()
            
            with open(journal_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data['timestamp'] = timestamp
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
            
            socketio.emit('journal:saved', timestamp)
    except Exception as e:
        logging.error(f"Error saving journal: {e}")
        socketio.emit('journal:error', {'message': str(e)})

@socketio.on('add_range')
def handle_add_range(data):
    try:
        if monitor_server.add_ip_range(data['start_ip'], data['end_ip']):
            socketio.emit('ranges_updated', {
                'ranges': monitor_server.get_ranges_data(),
                'success': True
            })
        else:
            socketio.emit('ranges_updated', {'success': False})
    except Exception as e:
        logging.error(f"Error in handle_add_range: {str(e)}")
        socketio.emit('notification', {
            'message': f"Ошибка добавления диапазона: {str(e)}",
            'type': 'error'
        })

@socketio.on('clear_cache')
def handle_clear_cache(data=None):  # Добавляем параметр data
    """Обработчик очистки кеша"""
    try:
        if monitor_server.clear_all_cache():
            socketio.emit('notification', {
                'message': 'Кеш успешно очищен',
                'type': 'success'
            })
            # Обновляем данные на клиенте
            socketio.emit('initial_data', {
                'miners': [],
                'fresh_count': 0,
                'total_count': 0,
                'ranges': monitor_server.get_ranges_data(),
                'excluded_models': monitor_server.get_excluded_models(),
                'settings': monitor_server.get_settings(),
                'monitoring': monitor_server.monitoring,
                'cached_ranges': {}
            })
        else:
            socketio.emit('notification', {
                'message': 'Ошибка при очистке кеша',
                'type': 'error'
            })
    except Exception as e:
        logging.error(f"Ошибка в handle_clear_cache: {str(e)}")
        socketio.emit('notification', {
            'message': f"Ошибка при очистке кеша: {str(e)}",
            'type': 'error'
        })

@socketio.on('remove_range')
def handle_remove_range(data):
    try:
        if monitor_server.remove_ip_range(data['range']):
            socketio.emit('ranges_updated', {
                'ranges': monitor_server.get_ranges_data(),
                'success': True
            })
        else:
            socketio.emit('ranges_updated', {'success': False})
    except Exception as e:
        logging.error(f"Error in handle_remove_range: {str(e)}")
        socketio.emit('notification', {
            'message': f"Ошибка удаления диапазона: {str(e)}",
            'type': 'error'
        })

@socketio.on('get_weather')
def handle_get_weather():
    try:
        weather_data = weathercloud_api.get_weather_data()
        source = 'weathercloud'
        
        if not weather_data:
            weather_data = weather_api.get_current_weather(coordinates="56.026443,92.895187")
            source = 'gismeteo'
        
        if weather_data:
            return {
                'temperature': weather_data.get('temperature'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'wind_speed': weather_data.get('wind_speed'),
                'source': source,
                'timestamp': weather_data.get('timestamp')
            }
        return {'error': 'Weather data not available'}
    except Exception as e:
        logging.error(f"Weather socket error: {e}")
        return {'error': str(e)}  

@socketio.on('rename_range')
def handle_rename_range(data):
    try:
        if monitor_server.rename_range(data['range'], data['name']):
            socketio.emit('ranges_updated', {
                'ranges': monitor_server.get_ranges_data(),
                'success': True
            })
        else:
            socketio.emit('ranges_updated', {'success': False})
    except Exception as e:
        logging.error(f"Error in handle_rename_range: {str(e)}")
        socketio.emit('notification', {
            'message': f"Ошибка переименования: {str(e)}",
            'type': 'error'
        })

@socketio.on('toggle_range')
def handle_toggle_range(data):
    ip_range = data.get('range')
    active = data.get('active')
    if monitor_server.toggle_range_active(ip_range, active):
        socketio.emit('ranges_updated', {'ranges': monitor_server.get_ranges_data()})

@socketio.on('toggle_monitoring')
def handle_toggle_monitoring(data=None):
    """Обработчик включения/выключения мониторинга майнеров"""
    try:
        # Initialize data as empty dict if None
        if data is None:
            data = {}
            
        enable = data.get('enable', None)
        
        if enable is None:
            # Если параметр не передан, просто переключаем состояние
            enable = not monitor_server.monitoring
            
        if enable:
            monitor_server.start_monitoring()
        else:
            monitor_server.stop_monitoring()
            
        # Отправляем подтверждение клиенту
        socketio.emit('monitoring_state', {
            'monitoring': monitor_server.monitoring,
            'message': f"Мониторинг {'активирован' if monitor_server.monitoring else 'деактивирован'}"
        })
        
        logging.info(f"Monitoring {'started' if monitor_server.monitoring else 'stopped'}")
        
    except Exception as e:
        logging.error(f"Ошибка при переключении мониторинга: {str(e)}")
        socketio.emit('notification', {
            'message': f"Ошибка: {str(e)}",
            'type': 'error'
        })
        
@socketio.on('select_all_ranges')
def handle_select_all_ranges():
    monitor_server.select_all_ranges()
    socketio.emit('ranges_updated', {'ranges': monitor_server.get_ranges_data()})

@socketio.on('deselect_all_ranges')
def handle_deselect_all_ranges():
    monitor_server.deselect_all_ranges()
    socketio.emit('ranges_updated', {'ranges': monitor_server.get_ranges_data()})

@socketio.on('add_excluded_model')
def handle_add_excluded_model(data):
    model = data.get('model')
    if monitor_server.add_excluded_model(model):
        socketio.emit('excluded_models_updated', {'excluded_models': monitor_server.get_excluded_models()})

@socketio.on('remove_excluded_model')
def handle_remove_excluded_model(data):
    model = data.get('model')
    if monitor_server.remove_excluded_model(model):
        socketio.emit('excluded_models_updated', {'excluded_models': monitor_server.get_excluded_models()})

@socketio.on('update_settings')
def handle_update_settings(data):
    if monitor_server.update_settings(data):
        socketio.emit('settings_updated', {'settings': monitor_server.get_settings()})
        logging.info("Settings updated successfully")
    else:
        logging.error("Failed to update settings")

@socketio.on('adjust_voltage')
def handle_adjust_voltage(data):
    ips = data.get('ips')
    delta = data.get('delta')
    monitor_server.adjust_voltage(ips, delta)

@socketio.on('adjust_temp_target')
def handle_adjust_temp_target(data):
    ips = data.get('ips')
    delta = data.get('delta')
    monitor_server.adjust_temp_target(ips, delta)

@socketio.on('toggle_blink')
def handle_toggle_blink(data):
    ips = data.get('ips')
    enable = data.get('enable')
    monitor_server.toggle_blink(ips, enable)

@socketio.on('reboot_miners')
def handle_reboot_miners(data):
    ips = data.get('ips')
    monitor_server.reboot_miners(ips)

@socketio.on('reboot_miner')
def handle_reboot_miner(data):
    ip = data.get('ip')
    if not ip:
        return {'success': False, 'message': 'IP address required'}
    
    try:
        monitor_server.reboot_miners([ip])  # Используем существующий метод, но передаем список из одного IP
        return {'success': True, 'message': f'Reboot command sent to {ip}'}
    except Exception as e:
        logging.error(f"Error rebooting miner {ip}: {e}")
        return {'success': False, 'message': str(e)}    

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    miners = monitor_server.get_miners_data()
    fresh_count = sum(1 for m in miners if m.get('data_fresh', False))
    cached_ranges = monitor_server.get_all_cached_ranges()
    socketio.emit('initial_data', {
        'miners': miners,
        'fresh_count': fresh_count,
        'total_count': len(miners),
        'miners': monitor_server.get_miners_data(),
        'ranges': monitor_server.get_ranges_data(),
        'excluded_models': monitor_server.get_excluded_models(),
        'settings': monitor_server.get_settings(),
        'monitoring': monitor_server.monitoring,
        'cached_ranges': cached_ranges  # Добавляем кешированные данные
    })

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

if __name__ == '__main__':
    
    logging.info(f"Запуск сервера... Директория данных: {os.path.abspath('miner_monitor_data')}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)