import subprocess
import threading
import queue
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import re
import datetime

# --- 1. AdbManager Класс ---
class AdbManager:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.output_queue = queue.Queue() # Очередь для асинхронного вывода

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def execute_adb_command(self, command_args, timeout=60):
        """
        Выполняет ADB команду и возвращает её вывод.
        Возвращает (stdout, stderr, returncode)
        """
        full_command = ["adb"] + command_args
        self._log(f"Выполнение: {' '.join(full_command)}")
        try:
            # Используем startupinfo для скрытия окна консоли на Windows
            startupinfo = None
            if os.name == 'nt': # Если ОС Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=False, # Не вызывать исключение при ненулевом коде возврата
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                startupinfo=startupinfo # Скрываем окно консоли
            )
            return process.stdout, process.stderr, process.returncode
        except FileNotFoundError:
            self._log("ОШИБКА: Команда 'adb' не найдена. Убедитесь, что Android SDK Platform-Tools установлен и 'adb.exe' находится в PATH.")
            return "", "adb_not_found", -1
        except subprocess.TimeoutExpired:
            self._log(f"ОШИБКА: Команда истекла по таймауту ({timeout} сек): {' '.join(full_command)}")
            return "", "timeout", -2
        except Exception as e:
            self._log(f"НЕИЗВЕСТНАЯ ОШИБКА при выполнении ADB команды: {e}")
            return "", str(e), -3

    def get_devices(self):
        """Возвращает список подключенных устройств."""
        stdout, stderr, retcode = self.execute_adb_command(["devices"])
        if retcode != 0:
            return []
        devices = []
        for line in stdout.splitlines():
            if "\tdevice" in line and not line.startswith("*"):
                device_id = line.split("\t")[0].strip()
                devices.append(device_id)
        return devices

    def check_adb_available(self):
        """Проверяет, доступен ли ADB."""
        stdout, stderr, retcode = self.execute_adb_command(["version"], timeout=5)
        return retcode == 0 and "Android Debug Bridge version" in stdout

    def get_logcat(self, limit_lines=500):
        """Получает последние строки логов."""
        stdout, stderr, retcode = self.execute_adb_command(["logcat", "-d", "-t", str(limit_lines)], timeout=30)
        if retcode == 0:
            return stdout
        return ""
    
    def get_system_property(self, prop_name):
        """Получает значение системного свойства."""
        stdout, stderr, retcode = self.execute_adb_command(["shell", "getprop", prop_name])
        if retcode == 0:
            return stdout.strip()
        return "Неизвестно"

    def get_dumpsys_output(self, service_name):
        """Получает вывод dumpsys для указанной службы."""
        stdout, stderr, retcode = self.execute_adb_command(["shell", "dumpsys", service_name])
        if retcode == 0:
            return stdout
        return ""

    def get_shell_output(self, command):
        """Выполняет команду в ADB shell."""
        stdout, stderr, retcode = self.execute_adb_command(["shell"] + command.split())
        if retcode == 0:
            return stdout
        return ""

# --- 2. ParserUtils Класс ---
class ParserUtils:
    @staticmethod
    def parse_battery_info(raw_data):
        """Парсит вывод 'dumpsys battery'."""
        info = {}
        level_match = re.search(r'level:\s*(\d+)', raw_data)
        if level_match: info['Уровень заряда'] = f"{level_match.group(1)}%"

        status_match = re.search(r'status:\s*(\d+)\s*\((.+?)\)', raw_data)
        if status_match:
            status_map = {
                "1": "Неизвестно", "2": "Заряжается", "3": "Разряжается",
                "4": "Не заряжается (полный)", "5": "Полностью заряжен"
            }
            info['Статус'] = status_map.get(status_match.group(1), status_match.group(2))
        else:
            status_match = re.search(r'status:\s*(\d+)', raw_data)
            if status_match:
                status_map = {
                    "1": "Неизвестно", "2": "Заряжается", "3": "Разряжается",
                    "4": "Не заряжается (полный)", "5": "Полностью заряжен"
                }
                info['Статус'] = status_map.get(status_match.group(1), "Неизвестно")

        health_match = re.search(r'health:\s*(\d+)\s*\((.+?)\)', raw_data)
        if health_match:
            health_map = {
                "1": "Неизвестно", "2": "Хорошо", "3": "Перегрев",
                "4": "Мертвая", "5": "Перенапряжение", "6": "Неисправность", "7": "Холодно"
            }
            info['Здоровье'] = health_map.get(health_match.group(1), health_match.group(2))
        else:
            health_match = re.search(r'health:\s*(\d+)', raw_data)
            if health_match:
                health_map = {
                    "1": "Неизвестно", "2": "Хорошо", "3": "Перегрев",
                    "4": "Мертвая", "5": "Перенапряжение", "6": "Неисправность", "7": "Холодно"
                }
                info['Здоровье'] = health_map.get(health_match.group(1), "Неизвестно")

        temp_match = re.search(r'temperature:\s*(\d+)', raw_data)
        if temp_match: info['Температура'] = f"{int(temp_match.group(1)) / 10}°C"

        voltage_match = re.search(r'voltage:\s*(\d+)', raw_data)
        if voltage_match: info['Напряжение'] = f"{int(voltage_match.group(1)) / 1000}V"

        return info

    @staticmethod
    def parse_memory_info(raw_data):
        """Парсит вывод 'dumpsys meminfo'."""
        info = {}
        total_ram_match = re.search(r'Total RAM:\s*([\d.]+)([KMGT]?B)', raw_data)
        if total_ram_match:
            info['Общая RAM'] = f"{total_ram_match.group(1)}{total_ram_match.group(2)}"
        
        free_ram_match = re.search(r'Free RAM:\s*([\d.]+)([KMGT]?B)', raw_data)
        if free_ram_match:
            info['Свободная RAM'] = f"{free_ram_match.group(1)}{free_ram_match.group(2)}"
        
        used_ram_match = re.search(r'Used RAM:\s*([\d.]+)([KMGT]?B)', raw_data)
        if used_ram_match:
            info['Использованная RAM'] = f"{used_ram_match.group(1)}{used_ram_match.group(2)}"

        return info

    @staticmethod
    def parse_storage_info(raw_data):
        """Парсит вывод 'df -h'."""
        info = []
        lines = raw_data.strip().splitlines()
        if len(lines) > 1:
            header_line = lines[0]
            # Улучшенный парсинг заголовка для точного разделения
            headers = ['Filesystem', 'Size', 'Used', 'Avail', 'Use%', 'Mounted on']
            
            for line in lines[1:]:
                # Используем split() без аргументов для обработки множественных пробелов
                parts = line.split()
                if len(parts) >= 6: # Filesystem, Size, Used, Avail, Use%, Mounted on
                    mount_info = {
                        'Файловая система': parts[0],
                        'Размер': parts[1],
                        'Использовано': parts[2],
                        'Доступно': parts[3],
                        'Занято (%)': parts[4],
                        'Точка монтирования': parts[5]
                    }
                    info.append(mount_info)
        return info
    
    @staticmethod
    def parse_wifi_info(raw_data):
        """Парсит вывод 'dumpsys wifi' или 'cmd wifi status'."""
        info = {}
        status_match = re.search(r'Wi-Fi is (\w+)', raw_data)
        if status_match:
            info['Статус Wi-Fi'] = "Включен" if status_match.group(1) == "enabled" else "Выключен"
        else: # Альтернативный парсинг для других версий Android или dumpsys
            status_match = re.search(r'mClientMode:ENABLED', raw_data)
            if status_match:
                 info['Статус Wi-Fi'] = "Включен"
            else:
                 info['Статус Wi-Fi'] = "Выключен"


        ssid_match = re.search(r'SSID:\s*"(.*?)"', raw_data)
        if ssid_match:
            info['Подключен к'] = ssid_match.group(1)
        
        ip_match = re.search(r'ip_address\s*=\s*((\d{1,3}\.){3}\d{1,3})', raw_data)
        if ip_match:
            info['IP адрес'] = ip_match.group(1)
            
        return info

    @staticmethod
    def parse_bluetooth_info(raw_data):
        """Парсит вывод 'settings get global bluetooth_on' или 'dumpsys bluetooth_manager'."""
        info = {}
        if raw_data.strip() == '1':
            info['Статус Bluetooth'] = "Включен"
        elif raw_data.strip() == '0':
            info['Статус Bluetooth'] = "Выключен"
        else: # Альтернативный парсинг для dumpsys bluetooth_manager
            state_match = re.search(r'mState: (\d+)', raw_data)
            if state_match:
                state_code = state_match.group(1)
                bt_states = {
                    "10": "Выключен", "11": "Выключается", "12": "Включен",
                    "13": "Включается", "14": "Неизвестно" # Добавьте другие по необходимости
                }
                info['Статус Bluetooth'] = bt_states.get(state_code, "Неизвестно")
            
        return info

    @staticmethod
    def parse_cpu_info(raw_data):
        """Парсит вывод 'dumpsys cpuinfo' или 'top'."""
        info = {}
        total_cpu_match = re.search(r'CPU usage from \d+%', raw_data)
        if total_cpu_match:
            info['Общая загрузка CPU'] = total_cpu_match.group(0)
        else:
            total_cpu_match = re.search(r'total:\s*([\d.]+)%', raw_data)
            if total_cpu_match:
                info['Общая загрузка CPU'] = f"{total_cpu_match.group(1)}%"

        # Пример парсинга процессов, здесь можно расширить
        processes = []
        for line in raw_data.splitlines():
            if re.match(r'^\s*\d+%', line) and ' / ' in line: # Строка с процентом CPU и названием процесса
                parts = line.strip().split()
                if len(parts) > 5:
                    cpu_percent = parts[0]
                    pid = parts[1]
                    name = parts[-1]
                    processes.append(f"PID: {pid}, CPU: {cpu_percent}, Имя: {name}")
        info['Топ процессов'] = processes
        return info

    @staticmethod
    def parse_sensor_info(raw_data):
        """Парсит вывод 'dumpsys activity service sensors'."""
        info = {}
        sensor_lines = re.findall(r'(\S+):.*\((.+?)\)', raw_data) # Имя датчика и его тип/показания
        if not sensor_lines: # Если не нашли в таком формате, ищем список датчиков
            sensor_lines = re.findall(r'(\d+)\)\s*(.+?) \(type:\s*(\d+)\)', raw_data)
            if sensor_lines:
                info['Доступные датчики'] = [f"{s_name} (Тип: {s_type})" for _, s_name, s_type in sensor_lines]
        else: # Если нашли конкретные показания или типы
            info['Обнаруженные датчики'] = [f"{name}: {value}" for name, value in sensor_lines]

        if not info:
            info['Статус датчиков'] = "Не удалось получить подробную информацию."
        
        return info
    
    @staticmethod
    def parse_display_info(raw_data):
        """Парсит вывод 'dumpsys display'."""
        info = {}
        resolution_match = re.search(r'mOverrideDisplayInfo=\[.+\s*(\d+x\d+),', raw_data)
        if resolution_match:
            info['Разрешение экрана'] = resolution_match.group(1)
        
        density_match = re.search(r'density\s*(\d+)', raw_data)
        if density_match:
            info['Плотность пикселей (dpi)'] = density_match.group(1)
        
        refresh_rate_match = re.search(r'refreshRate\s*=\s*([\d.]+f)', raw_data)
        if refresh_rate_match:
            info['Частота обновления'] = f"{float(refresh_rate_match.group(1))} Гц"

        return info

# --- 3. DiagnosticModes Класс ---
class DiagnosticModes:
    def __init__(self, adb_manager, log_callback, result_callback):
        self.adb = adb_manager
        self.log = log_callback
        self.result_callback = result_callback
        self.report_data = []

    def _add_to_report(self, section, data):
        self.report_data.append(f"\n--- {section} ---")
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.report_data.append(f"{key}:")
                    for item in value:
                        self.report_data.append(f"  - {item}")
                else:
                    self.report_data.append(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        self.report_data.append(f"  {k}: {v}")
                else:
                    self.report_data.append(f"  - {item}")
        else:
            self.report_data.append(str(data))

    def _run_test(self, test_name, func):
        self.log(f"\nЗапуск теста: {test_name}...")
        self.result_callback(f"** {test_name} **")
        result = func()
        if result:
            self.result_callback("  " + "\n  ".join([f"{k}: {v}" if not isinstance(v, list) else f"{k}:\n    " + "\n    ".join(v) for k, v in result.items()]) if isinstance(result, dict) else str(result))
            self._add_to_report(test_name, result)
        else:
            self.result_callback("  Нет данных или произошла ошибка.")
            self._add_to_report(test_name, "Нет данных или произошла ошибка.")
        return result
    
    def _run_complex_test(self, test_name, func):
        self.log(f"\nЗапуск теста: {test_name}...")
        self.result_callback(f"** {test_name} **")
        results = func()
        for section, data in results.items():
            self.result_callback(f"  --- {section} ---")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        self.result_callback(f"    {key}:")
                        for item in value:
                            self.result_callback(f"      - {item}")
                    else:
                        self.result_callback(f"    {key}: {value}")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        self.result_callback("    " + "\n    ".join([f"{k}: {v}" for k, v in item.items()]))
                    else:
                        self.result_callback(f"    - {item}")
            else:
                self.result_callback(f"    {data}")
            self._add_to_report(f"{test_name} - {section}", data)
        if not results:
            self.result_callback("  Нет данных или произошла ошибка.")
            self._add_to_report(test_name, "Нет данных или произошла ошибка.")
        return results


    def _get_device_info(self):
        info = {}
        info['Модель'] = self.adb.get_system_property("ro.product.model")
        info['Производитель'] = self.adb.get_system_property("ro.product.manufacturer")
        info['Версия Android'] = self.adb.get_system_property("ro.build.version.release")
        info['Уровень API'] = self.adb.get_system_property("ro.build.version.sdk")
        info['Серийный номер'] = self.adb.get_system_property("ro.serialno")
        info['Время сборки'] = self.adb.get_system_property("ro.build.date")
        return info

    def _get_battery_info(self):
        raw_data = self.adb.get_dumpsys_output("battery")
        return ParserUtils.parse_battery_info(raw_data)

    def _get_memory_info(self):
        raw_data = self.adb.get_dumpsys_output("meminfo")
        return ParserUtils.parse_memory_info(raw_data)
    
    def _get_storage_info(self):
        raw_data = self.adb.get_shell_output("df -h")
        return ParserUtils.parse_storage_info(raw_data)

    def _get_network_info(self):
        results = {}
        wifi_raw = self.adb.get_dumpsys_output("wifi")
        results['Wi-Fi'] = ParserUtils.parse_wifi_info(wifi_raw)
        
        bt_raw = self.adb.get_dumpsys_output("bluetooth_manager")
        if not bt_raw: # Попытка через settings, если dumpsys bluetooth_manager пуст
             bt_raw = self.adb.get_shell_output("settings get global bluetooth_on")
        results['Bluetooth'] = ParserUtils.parse_bluetooth_info(bt_raw)

        ip_info_raw = self.adb.get_shell_output("ip -f inet addr show")
        results['IP-адреса'] = self.parse_ip_addresses(ip_info_raw)
        
        return results

    def parse_ip_addresses(self, raw_data):
        ips = []
        # Находим блоки, относящиеся к интерфейсам
        interfaces = re.findall(r'(\d+:\s*\S+:\s*<.+?>\s*.*\s*inet\s*[\d.]+\S*)', raw_data, re.DOTALL)
        for interface_block in interfaces:
            interface_name_match = re.search(r'^\d+:\s*(\S+):', interface_block)
            ip_match = re.search(r'inet\s*((\d{1,3}\.){3}\d{1,3}/\d+)', interface_block)
            
            if interface_name_match and ip_match:
                interface_name = interface_name_match.group(1)
                ip_address = ip_match.group(1)
                ips.append(f"{interface_name}: {ip_address}")
        return ips

    def _get_cpu_info(self):
        raw_data = self.adb.get_dumpsys_output("cpuinfo")
        if not raw_data:
            raw_data = self.adb.get_shell_output("top -n 1 -m 5") # Получить топ 5 процессов, если cpuinfo нет
        return ParserUtils.parse_cpu_info(raw_data)

    def _get_sensor_info(self):
        raw_data = self.adb.get_dumpsys_output("activity service sensors")
        return ParserUtils.parse_sensor_info(raw_data)
    
    def _get_display_info(self):
        raw_data = self.adb.get_dumpsys_output("display")
        return ParserUtils.parse_display_info(raw_data)

    def _analyze_logcat(self):
        log_data = self.adb.get_logcat(limit_lines=1000)
        critical_errors = []
        warnings = []
        for line in log_data.splitlines():
            if " E/" in line or " F/" in line: # Ошибки и фатальные ошибки
                critical_errors.append(line)
            elif " W/" in line: # Предупреждения
                warnings.append(line)
        
        info = {
            "Количество записей": len(log_data.splitlines()),
            "Критические ошибки (E/F)": critical_errors if critical_errors else ["Нет критических ошибок."],
            "Предупреждения (W)": warnings if warnings else ["Нет предупреждений."]
        }
        return info

    # --- Режимы диагностики ---

    def quick_scan(self):
        self.report_data = [] # Очищаем данные для нового отчета
        self.log("\n--- Запуск Быстрой Диагностики ---")
        self.result_callback("\n### Быстрая Диагностика ###")

        self._run_test("Информация об устройстве", self._get_device_info)
        self._run_test("Информация о батарее", self._get_battery_info)
        self._run_test("Использование памяти", self._get_memory_info)
        self._run_complex_test("Сетевая информация", self._get_network_info)

        self.log("\n--- Быстрая Диагностика Завершена ---")
        self.result_callback("\n--- Быстрая Диагностика Завершена ---")

    def deep_scan(self):
        self.report_data = [] # Очищаем данные для нового отчета
        self.log("\n--- Запуск Глубокой Диагностики ---")
        self.result_callback("\n### Глубокая Диагностика ###")

        self._run_test("Информация об устройстве", self._get_device_info)
        self._run_test("Информация о батарее", self._get_battery_info)
        self._run_test("Использование памяти", self._get_memory_info)
        self._run_test("Информация о хранилище", self._get_storage_info)
        self._run_complex_test("Сетевая информация", self._get_network_info)
        self._run_test("Информация о CPU и процессах", self._get_cpu_info)
        self._run_test("Информация о датчиках", self._get_sensor_info)
        self._run_test("Информация о дисплее", self._get_display_info)
        self._run_test("Анализ Logcat", self._analyze_logcat)

        self.log("\n--- Глубокая Диагностика Завершена ---")
        self.result_callback("\n--- Глубокая Диагностика Завершена ---")

    def hardware_assisted_test(self):
        self.report_data = [] # Очищаем данные для нового отчета
        self.log("\n--- Запуск Аппаратной Диагностики (с участием пользователя) ---")
        self.result_callback("\n### Аппаратная Диагностика (следуйте инструкциям на экране телефона) ###")

        self._add_to_report("Аппаратная Диагностика", "Требуется взаимодействие с пользователем.")

        # Экран
        self.result_callback("\n--- Тест Экрана ---")
        self.log("Инструкция: Программа покажет полноэкранные цвета на вашем телефоне. Проверьте экран на битые пиксели, засветы и равномерность цветопередачи.")
        self.log("Нажмите ОК после проверки каждого цвета.")
        self.result_callback("  1. **Тест на битые пиксели/цвета:** Программа покажет полноэкранные цвета.")
        self.result_callback("     - Перейдите в режим разработчика на телефоне (если еще не включен).")
        self.result_callback("     - Найдите 'Показать указатели касания' (Show taps) и 'Показать обновления поверхности' (Show surface updates) для визуальной проверки.")

        # Мы не можем напрямую управлять отображением цветов через ADB для всех устройств, но можем дать инструкцию
        # Для продвинутых тестов могли бы использовать:
        # self.adb.execute_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "https://example.com/test_screen.html"])
        # Либо запустить тестовое приложение, если оно установлено.

        user_input_screen = messagebox.askyesno(
            "Тест Экрана",
            "Запустите тест экрана на вашем телефоне (например, с помощью стороннего приложения 'Screen Test' или системных настроек).\n"
            "Последовательно проверьте экран на битые пиксели и засветы (особенно на черном фоне).\n"
            "Экран в порядке?"
        )
        screen_result = "Пройден" if user_input_screen else "Не пройден"
        self.result_callback(f"  Результат теста экрана: {screen_result}")
        self._add_to_report("Тест Экрана", {"Результат": screen_result})

        # Камера
        self.result_callback("\n--- Тест Камеры ---")
        self.log("Инструкция: Откройте приложение 'Камера' на телефоне. Проверьте основную и фронтальную камеры.")
        self.log("Убедитесь, что камера фокусируется, работает вспышка (если есть) и качество изображения приемлемое.")
        self.result_callback("  2. **Тест Камеры:** Откройте приложение 'Камера'.")
        self.result_callback("     - Сделайте фото на основную камеру со вспышкой и без.")
        self.result_callback("     - Переключитесь на фронтальную камеру и сделайте фото.")
        
        user_input_camera = messagebox.askyesno(
            "Тест Камеры",
            "Откройте приложение 'Камера' на телефоне. Проверьте основную и фронтальную камеры, вспышку.\n"
            "Камеры работают нормально?"
        )
        camera_result = "Пройден" if user_input_camera else "Не пройден"
        self.result_callback(f"  Результат теста камеры: {camera_result}")
        self._add_to_report("Тест Камеры", {"Результат": camera_result})

        # Динамики и Микрофон
        self.result_callback("\n--- Тест Динамиков и Микрофона ---")
        self.log("Инструкция: Воспроизведите музыку/видео для проверки динамиков. Запишите короткое голосовое сообщение для проверки микрофона.")
        self.result_callback("  3. **Тест Динамиков:** Воспроизведите любой звук (музыку, видео).")
        self.result_callback("  4. **Тест Микрофона:** Запишите короткое голосовое сообщение через Диктофон или мессенджер.")

        user_input_audio = messagebox.askyesno(
            "Тест Аудио",
            "Проверьте динамики (воспроизведите звук) и микрофон (запишите голос).\n"
            "Аудио работает нормально?"
        )
        audio_result = "Пройден" if user_input_audio else "Не пройден"
        self.result_callback(f"  Результат теста аудио: {audio_result}")
        self._add_to_report("Тест Аудио", {"Результат": audio_result})

        # Кнопки
        self.result_callback("\n--- Тест Кнопок ---")
        self.log("Инструкция: Нажимайте кнопки громкости, питания и (если есть) кнопку Домой. Проверьте их реакцию.")
        self.result_callback("  5. **Тест Кнопок:** Нажимайте кнопки громкости (+/-), питания, и Home/Назад/Недавние приложения.")
        
        user_input_buttons = messagebox.askyesno(
            "Тест Кнопок",
            "Нажимайте все физические кнопки телефона (громкость, питание, домой/навигация).\n"
            "Все кнопки работают и реагируют?"
        )
        buttons_result = "Пройден" if user_input_buttons else "Не пройден"
        self.result_callback(f"  Результат теста кнопок: {buttons_result}")
        self._add_to_report("Тест Кнопок", {"Результат": buttons_result})

        self.log("\n--- Аппаратная Диагностика Завершена ---")
        self.result_callback("\n--- Аппаратная Диагностика Завершена ---")

    def save_report(self):
        if not self.report_data:
            messagebox.showinfo("Сохранить Отчет", "Нет данных для сохранения. Сначала запустите диагностику.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Сохранить отчет как",
            initialfile=f"Отчет_диагностики_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"--- Отчет о Диагностике Телефона ---\n")
                    f.write(f"Дата и время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"-------------------------------------\n\n")
                    f.write("\n".join(self.report_data))
                messagebox.showinfo("Сохранить Отчет", f"Отчет успешно сохранен в: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить отчет: {e}")

# --- 4. PhoneDiagnosticApp Класс (GUI) ---
class PhoneDiagnosticApp:
    def __init__(self, master):
        self.master = master
        master.title("Диагностика Телефона (ADB Python)")
        master.geometry("1000x700") # Устанавливаем размер окна по умолчанию

        self.adb_manager = AdbManager(self._log_to_console)
        self.diagnostic_modes = DiagnosticModes(self.adb_manager, self._log_to_console, self._display_result)

        self._create_widgets()
        self.master.after(100, self.check_adb_status) # Проверяем ADB после инициализации GUI

    def _create_widgets(self):
        # Фрейм для кнопок режимов
        self.mode_frame = tk.LabelFrame(self.master, text="Режимы Диагностики", padx=10, pady=10)
        self.mode_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Button(self.mode_frame, text="Быстрая Диагностика", command=lambda: self._run_diagnostic_mode(self.diagnostic_modes.quick_scan)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.mode_frame, text="Глубокая Диагностика", command=lambda: self._run_diagnostic_mode(self.diagnostic_modes.deep_scan)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.mode_frame, text="Аппаратный Тест (с участием пользователя)", command=lambda: self._run_diagnostic_mode(self.diagnostic_modes.hardware_assisted_test)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.mode_frame, text="Сохранить Отчет", command=self.diagnostic_modes.save_report).pack(side=tk.RIGHT, padx=5, pady=5)

        # Фрейм для вывода результатов
        self.result_frame = tk.LabelFrame(self.master, text="Результаты Диагностики", padx=10, pady=10)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        self.result_text.pack(expand=True, fill=tk.BOTH)

        # Фрейм для консоли
        self.console_frame = tk.LabelFrame(self.master, text="Консоль (ADB логи)", padx=10, pady=10)
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=10, pady=5) # Не расширять по вертикали

        self.console_text = scrolledtext.ScrolledText(self.console_frame, wrap=tk.WORD, width=80, height=8, font=("Consolas", 9), bg="#2c2c2c", fg="#00ff00", insertbackground="#00ff00")
        self.console_text.pack(expand=True, fill=tk.BOTH)
        self.console_text.config(state=tk.DISABLED) # Сделать консоль только для чтения

    def _log_to_console(self, message):
        """Выводит сообщение в консоль (лог ADB)"""
        self.console_text.config(state=tk.NORMAL) # Временно включаем запись
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END) # Прокрутка до конца
        self.console_text.config(state=tk.DISABLED) # Выключаем запись

    def _display_result(self, message):
        """Выводит сообщение в область результатов диагностики"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END) # Прокрутка до конца

    def _run_diagnostic_mode(self, mode_func):
        """Запускает выбранный режим диагностики в отдельном потоке."""
        self.result_text.delete(1.0, tk.END) # Очищаем результаты
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END) # Очищаем консоль
        self.console_text.config(state=tk.DISABLED)
        
        self._log_to_console(f"Запуск режима: {mode_func.__name__}...")
        self._display_result(f"*** Запуск режима: {mode_func.__name__} ***\n")
        
        # Запускаем диагностику в отдельном потоке, чтобы GUI не зависал
        threading.Thread(target=mode_func, daemon=True).start()

    def check_adb_status(self):
        """Проверяет статус ADB при запуске и каждые 5 секунд."""
        is_available = self.adb_manager.check_adb_available()
        devices = self.adb_manager.get_devices()
        
        if not is_available:
            self._log_to_console("Статус ADB: НЕ НАЙДЕН. Убедитесь, что 'adb.exe' в PATH.")
            messagebox.showerror("Ошибка ADB", "ADB не найден. Пожалуйста, убедитесь, что Android SDK Platform-Tools установлен и 'adb.exe' находится в PATH.")
            self.master.title("Диагностика Телефона (ADB не найден)")
            # Отключаем кнопки диагностики
            for child in self.mode_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state=tk.DISABLED)
        elif not devices:
            self._log_to_console("Статус ADB: ОК, но устройство НЕ ПОДКЛЮЧЕНО или Отладка по USB не включена.")
            self.master.title("Диагностика Телефона (Устройство не подключено)")
            # Отключаем кнопки диагностики, кроме кнопки сохранения отчета
            for child in self.mode_frame.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") != "Сохранить Отчет":
                    child.config(state=tk.DISABLED)
        else:
            self._log_to_console(f"Статус ADB: ОК. Подключено устройств: {len(devices)} ({', '.join(devices)})")
            self.master.title(f"Диагностика Телефона (Подключено: {devices[0]})" if devices else "Диагностика Телефона")
            # Включаем кнопки диагностики
            for child in self.mode_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state=tk.NORMAL)

        # Повторяем проверку каждые 5 секунд
        self.master.after(5000, self.check_adb_status)


# --- 5. Main Блок ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneDiagnosticApp(root)
    root.mainloop()