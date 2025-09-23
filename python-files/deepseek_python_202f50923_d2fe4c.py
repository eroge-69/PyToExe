import psutil
import platform
import socket
import requests
import time
from datetime import datetime
import json
import os

class PCMonitor:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_to_telegram(self, message):
        """Отправка сообщения в Telegram"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(self.telegram_url, data=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")
            return False
    
    def get_system_info(self):
        """Сбор основной информации о системе"""
        try:
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            system_info = f"""
<b>💻 СИСТЕМНАЯ ИНФОРМАЦИЯ</b>
├─ Система: {uname.system}
├─ Версия: {uname.release}
├─ Архитектура: {platform.architecture()[0]}
├─ Имя ПК: {uname.node}
├─ Процессор: {uname.processor}
├─ Время загрузки: {boot_time.strftime("%Y-%m-%d %H:%M:%S")}
└─ IP-адрес: {socket.gethostbyname(socket.gethostname())}
"""
            return system_info
        except Exception as e:
            return f"❌ Ошибка сбора системной информации: {str(e)}"
    
    def get_cpu_info(self):
        """Сбор информации о процессоре"""
        try:
            # Замеряем использование CPU за 1 секунду
            psutil.cpu_percent(interval=1)
            cpu_percent = psutil.cpu_percent(percpu=True)
            
            cpu_info = f"""
<b>⚙️ ИНФОРМАЦИЯ О ПРОЦЕССОРЕ</b>
├─ Ядер (физ/лог): {psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}
├─ Общая загрузка: {psutil.cpu_percent()}%
"""
            
            # Добавляем информацию по каждому ядру
            for i, usage in enumerate(cpu_percent):
                cpu_info += f"├─ Ядро {i+1}: {usage}%\n"
            
            # Информация о частоте
            if hasattr(psutil, 'cpu_freq'):
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info += f"└─ Частота: {freq.current:.0f} MHz\n"
            
            return cpu_info
        except Exception as e:
            return f"❌ Ошибка сбора информации о CPU: {str(e)}"
    
    def get_memory_info(self):
        """Сбор информации о памяти"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            memory_info = f"""
<b>💾 ИНФОРМАЦИЯ О ПАМЯТИ</b>
├─ ОЗУ всего: {self.bytes_to_gb(virtual_mem.total):.1f} GB
├─ ОЗУ использовано: {self.bytes_to_gb(virtual_mem.used):.1f} GB
├─ ОЗУ свободно: {self.bytes_to_gb(virtual_mem.available):.1f} GB
├─ Загрузка ОЗУ: {virtual_mem.percent}%
├─ SWAP всего: {self.bytes_to_gb(swap_mem.total):.1f} GB
├─ SWAP использовано: {self.bytes_to_gb(swap_mem.used):.1f} GB
└─ Загрузка SWAP: {swap_mem.percent}%
"""
            return memory_info
        except Exception as e:
            return f"❌ Ошибка сбора информации о памяти: {str(e)}"
    
    def get_disk_info(self):
        """Сбор информации о дисках"""
        try:
            disk_info = "<b>💿 ИНФОРМАЦИЯ О ДИСКАХ</b>\n"
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                    
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info += f"""
├─ Устройство: {partition.device}
├─ Точка монтирования: {partition.mountpoint}
├─ Файловая система: {partition.fstype}
├─ Всего: {self.bytes_to_gb(partition_usage.total):.1f} GB
├─ Использовано: {self.bytes_to_gb(partition_usage.used):.1f} GB
├─ Свободно: {self.bytes_to_gb(partition_usage.free):.1f} GB
├─ Загрузка: {partition_usage.percent}%
└─{'─' * 30}
"""
                except PermissionError:
                    continue
            
            return disk_info
        except Exception as e:
            return f"❌ Ошибка сбора информации о дисках: {str(e)}"
    
    def get_network_info(self):
        """Сбор информации о сети"""
        try:
            net_io = psutil.net_io_counters()
            network_info = f"""
<b>🌐 СЕТЕВАЯ ИНФОРМАЦИЯ</b>
├─ Отправлено: {self.bytes_to_mb(net_io.bytes_sent):.1f} MB
├─ Получено: {self.bytes_to_mb(net_io.bytes_recv):.1f} MB
├─ Пакетов отправлено: {net_io.packets_sent}
└─ Пакетов получено: {net_io.packets_recv}
"""
            return network_info
        except Exception as e:
            return f"❌ Ошибка сбора сетевой информации: {str(e)}"
    
    def get_running_processes(self, top_n=10):
        """Получение списка процессов с наибольшим использованием памяти"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Сортируем по использованию памяти и берем топ-N
            processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            
            processes_info = "<b>📊 ТОП-10 ПРОЦЕССОВ ПО ПАМЯТИ</b>\n"
            for i, proc in enumerate(processes[:top_n]):
                if proc['memory_percent']:
                    processes_info += f"├─ {proc['name']}: {proc['memory_percent']:.1f}%\n"
            
            return processes_info
        except Exception as e:
            return f"❌ Ошибка сбора информации о процессах: {str(e)}"
    
    def bytes_to_gb(self, bytes):
        """Конвертация байтов в гигабайты"""
        return bytes / (1024 ** 3)
    
    def bytes_to_mb(self, bytes):
        """Конвертация байтов в мегабайты"""
        return bytes / (1024 ** 2)
    
    def collect_all_info(self):
        """Сбор всей информации"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report = f"<b>📈 ОТЧЕТ О СОСТОЯНИИ ПК</b>\n<code>Время: {timestamp}</code>\n"
            
            report += self.get_system_info()
            report += self.get_cpu_info()
            report += self.get_memory_info()
            report += self.get_disk_info()
            report += self.get_network_info()
            report += self.get_running_processes()
            
            return report
        except Exception as e:
            return f"❌ Ошибка сбора информации: {str(e)}"
    
    def send_alert(self, threshold_cpu=80, threshold_memory=85, threshold_disk=90):
        """Отправка предупреждения при высоких нагрузках"""
        try:
            alerts = []
            
            # Проверка CPU
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > threshold_cpu:
                alerts.append(f"🚨 ВЫСОКАЯ ЗАГРУЗКА CPU: {cpu_usage}%")
            
            # Проверка памяти
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > threshold_memory:
                alerts.append(f"🚨 ВЫСОКАЯ ЗАГРУЗКА ПАМЯТИ: {memory_usage}%")
            
            # Проверка дисков
            for partition in psutil.disk_partitions():
                try:
                    if 'cdrom' in partition.opts:
                        continue
                    usage = psutil.disk_usage(partition.mountpoint)
                    if usage.percent > threshold_disk:
                        alerts.append(f"🚨 МАЛО МЕСТА НА ДИСКЕ {partition.device}: {usage.percent}%")
                except PermissionError:
                    continue
            
            if alerts:
                alert_message = "<b>⚠️ ПРЕДУПРЕЖДЕНИЕ</b>\n" + "\n".join(alerts)
                self.send_to_telegram(alert_message)
                return True
            return False
        except Exception as e:
            print(f"Ошибка проверки предупреждений: {e}")
            return False

def main():
    # Настройки бота (замените на свои)
    BOT_TOKEN = "8443681477:AAF_ApI2CmaJnYO2nx3YKftFSlYU1tBUO-E"
    CHAT_ID = "8308780076"
    
    # Создаем экземпляр монитора
    monitor = PCMonitor(BOT_TOKEN, CHAT_ID)
    
    print("🚀 Мониторинг ПК запущен...")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        while True:
            # Отправляем полный отчет
            report = monitor.collect_all_info()
            if monitor.send_to_telegram(report):
                print(f"✅ Отчет отправлен в {datetime.now().strftime('%H:%M:%S')}")
            else:
                print("❌ Ошибка отправки отчета")
            
            # Проверяем предупреждения
            monitor.send_alert()
            
            # Ждем 5 минут перед следующей отправкой
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n⏹️ Мониторинг остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
