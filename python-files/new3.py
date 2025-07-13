
# -*- coding: utf-8 -*-

# Импорты для GUI и многопоточности
import customtkinter
import threading
import queue

# Импорты для основной логики анализа
import os
import platform
import subprocess
import json
from datetime import datetime
import psutil
import wmi

# --- МОДУЛИ АНАЛИЗА (Ваш код без изменений) ---
# Весь код для сбора и анализа данных остается здесь.
# GUI будет вызывать эти функции.

def get_system_info():
    """Собирает основную информацию об операционной системе."""
    try:
        c = wmi.WMI()
        os_info = c.Win32_OperatingSystem()[0]
        return {
            "os_name": os_info.Caption,
            "version": os_info.Version,
            "architecture": os_info.OSArchitecture,
            "system_drive": os_info.SystemDrive
        }
    except Exception as e:
        print(f"Ошибка при сборе информации об ОС: {e}")
        return {}

def get_hardware_info():
    """Собирает информацию об аппаратном обеспечении (CPU, RAM, GPU, диски)."""
    hardware_data = {}
    c = wmi.WMI()

    try:
        cpu_info = c.Win32_Processor()[0]
        hardware_data['cpu'] = {
            "name": cpu_info.Name.strip(),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "current_frequency_mhz": psutil.cpu_freq().current
        }
    except Exception as e:
        hardware_data['cpu'] = f"Не удалось получить информацию: {e}"

    try:
        ram_info = psutil.virtual_memory()
        hardware_data['ram'] = {
            "total_gb": round(ram_info.total / (1024*3), 2),
            "used_gb": round(ram_info.used / (1024*3), 2),
            "free_gb": round(ram_info.free / (1024*3), 2)
        }
    except Exception as e:
        hardware_data['ram'] = f"Не удалось получить информацию: {e}"

    try:
        gpu_info = c.Win32_VideoController()[0]
        hardware_data['gpu'] = {
            "name": gpu_info.Name,
            "video_memory_gb": round(int(gpu_info.AdapterRAM) / (1024*3), 2) if gpu_info.AdapterRAM else "N/A"
        }
    except Exception as e:
        hardware_data['gpu'] = f"Не удалось получить информацию: {e}"
        
    try:
        disks = []
        for disk in c.Win32_DiskDrive():
            disk_type = "SSD" if "ssd" in disk.Model.lower() else "HDD"
            disks.append({
                "model": disk.Model.strip(),
                "size_gb": round(int(disk.Size) / (1024*3), 2),
                "type": disk_type
            })
        hardware_data['physical_disks'] = disks
    except Exception as e:
        hardware_data['physical_disks'] = f"Не удалось получить информацию: {e}"



def get_software_info():
    """Собирает информацию о программах, процессах и службах."""
    software_data = {}
    
    try:
        c = wmi.WMI()
        startup_items = []
        for item in c.Win32_StartupCommand():
            startup_items.append({"name": item.Name, "location": item.Location, "command": item.Command})
        software_data['startup_programs'] = startup_items
    except Exception as e:
        software_data['startup_programs'] = f"Не удалось получить информацию: {e}"

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            p_info = proc.info
            p_info['memory_mb'] = round(p_info['memory_info'].rss / (1024*2), 2)
            processes.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    software_data['running_processes'] = processes

    return software_data

def get_performance_usage():
    """Собирает данные о текущей загрузке ресурсов."""
    usage_data = {}
    usage_data['cpu_percent'] = psutil.cpu_percent(interval=1)
    usage_data['ram_percent'] = psutil.virtual_memory().percent
    disk_usage = []
    for part in psutil.disk_partitions():
        if os.path.exists(part.mountpoint):
            usage = psutil.disk_usage(part.mountpoint)
            disk_usage.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "percent_used": usage.percent
            })
    usage_data['disk_usage'] = disk_usage
    return usage_data

def analyze_data(collected_data):
    """Анализирует собранные данные и возвращает список проблем и рекомендаций."""
    critical_issues = []
    recommendations = []
    system_drive_letter = collected_data['system']['system_drive']
    for disk in collected_data['usage']['disk_usage']:
        if disk['mountpoint'] == system_drive_letter:
            if disk['percent_used'] > 85:
                critical_issues.append(f"Критически мало места на системном диске {system_drive_letter} ({disk['percent_used']}% занято).")
                recommendations.append({"category": "Что очистить", "text": f"Рекомендуется срочно освободить место на диске {system_drive_letter}."})
    
    if isinstance(collected_data['hardware'].get('physical_disks'), list) and collected_data['hardware']['physical_disks']:
        if collected_data['hardware']['physical_disks'][0]['type'] == "HDD":
            recommendations.append({"category": "Что докупить (апгрейд)", "text": "Ваш системный диск - HDD. Замена его на SSD кардинально ускорит систему."})
    
    total_ram_gb = collected_data['hardware'].get('ram', {}).get('total_gb', 0)
    if total_ram_gb < 8:
        recommendations.append({"category": "Что докупить (апгрейд)", "text": f"У вас {total_ram_gb} ГБ ОЗУ. Рекомендуется увеличить до 16 ГБ для комфортной работы."})

    processes = sorted(collected_data['software']['running_processes'], key=lambda p: p.get('cpu_percent', 0), reverse=True)
    top_5_cpu = processes[:5]
    res_text = "Следующие программы потребляют много ресурсов ЦП. Рассмотрите их закрытие или удаление:\n" + \
               "".join([f"  - {p['name']} (CPU: {p.get('cpu_percent', 0)}%)\n" for p in top_5_cpu])
    recommendations.append({"category": "Что удалить", "text": res_text})
    
    startup_count = len(collected_data['software'].get('startup_programs', []))
    if startup_count > 10:
        recommendations.append({"category": "Что отключить", "text": f"В автозагрузке найдено много программ ({startup_count} шт.). Отключите ненужные для ускорения запуска."})

    recommendations.append({"category": "Что исправить", "text": "Регулярно проверяйте обновления драйверов для видеокарты и другого оборудования на сайтах производителей."})
    
    return critical_issues, recommendations

def generate_report_text(collected_data, critical_issues, recommendations):
    """Формирует финальный текстовый отчет."""
    report = []
    report.append("--- Общая сводка по системе ---")


    report.append(f"- ОС: {collected_data['system'].get('os_name', 'N/A')}")
    report.append(f"- Процессор: {collected_data['hardware'].get('cpu', {}).get('name', 'N/A')}")
    report.append(f"- ОЗУ: {collected_data['hardware'].get('ram', {}).get('total_gb', 'N/A')} ГБ")
    report.append(f"- Видеокарта: {collected_data['hardware'].get('gpu', {}).get('name', 'N/A')}")
    report.append("\n" + "-"*30 + "\n")

    if critical_issues:
        report.append("--- КРИТИЧЕСКИЕ ПРОБЛЕМЫ ---")
        for issue in critical_issues:
            report.append(f"- {issue}")
        report.append("\n" + "-"*30 + "\n")
    
    report.append("--- РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ ---")
    grouped_recs = {}
    for rec in recommendations:
        cat = rec['category']
        if cat not in grouped_recs:
            grouped_recs[cat] = []
        grouped_recs[cat].append(rec['text'])
    
    for category, texts in grouped_recs.items():
        report.append(f"\n- {category}:")
        for text in texts:
            indented_text = text.replace('\n', '\n    ')
            report.append(f"  - {indented_text}")

    return "\n".join(report)

# --- КЛАСС ГРАФИЧЕСКОГО ИНТЕРФЕЙСА ---

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title("Современный Системный Анализатор")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Установка темы
        customtkinter.set_appearance_mode("System") # Темы: "System", "Dark", "Light"
        customtkinter.set_default_color_theme("blue") # Темы: "blue", "green", "dark-blue"

        # Создание фрейма для элементов управления
        self.control_frame = customtkinter.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1)

        # Кнопка для запуска анализа
        self.analyze_button = customtkinter.CTkButton(self.control_frame, text="Начать анализ", command=self.start_analysis_thread)
        self.analyze_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Переключатель темы
        self.theme_switch = customtkinter.CTkSwitch(self.control_frame, text="Темная тема", command=self.change_theme)
        self.theme_switch.grid(row=0, column=2, padx=10, pady=10)

        # Прогресс-бар и статусная строка
        self.progress_bar = customtkinter.CTkProgressBar(self.control_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = customtkinter.CTkLabel(self.control_frame, text="Готов к работе. Нажмите 'Начать анализ'.")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # Текстовое поле для вывода отчета
        self.report_textbox = customtkinter.CTkTextbox(self, corner_radius=10, state="disabled", font=("Courier New", 12))
        self.report_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Очередь для обмена данными между потоками
        self.queue = queue.Queue()
        
    def change_theme(self):
        mode = "dark" if self.theme_switch.get() == 1 else "light"
        customtkinter.set_appearance_mode(mode)

    def start_analysis_thread(self):
        # Отключаем кнопку и очищаем поле
        self.analyze_button.configure(state="disabled", text="Анализ...")
        self.progress_bar.set(0)
        self.report_textbox.configure(state="normal")
        self.report_textbox.delete("1.0", "end")
        self.report_textbox.configure(state="disabled")

        # Запускаем анализ в новом потоке, чтобы GUI не зависал
        thread = threading.Thread(target=self.run_full_analysis, daemon=True)
        thread.start()
        
        # Запускаем обработчик очереди для обновления GUI
        self.after(100, self.process_queue)

    def run_full_analysis(self):
        """Эта функция выполняется в отдельном потоке."""
        try:


# Шаг 1: Сбор данных
            self.queue.put(("status", "Шаг 1/4: Сбор базовой информации о системе...", 0.1))
            system_info = get_system_info()
            
            self.queue.put(("status", "Шаг 2/4: Сбор данных об оборудовании...", 0.3))
            hardware_info = get_hardware_info()
            
            self.queue.put(("status", "Шаг 3/4: Сбор данных о ПО и процессах...", 0.6))
            software_info = get_software_info()
            
            self.queue.put(("status", "Шаг 4/4: Сбор данных о производительности...", 0.8))
            usage_info = get_performance_usage()

            collected_data = {
                "system": system_info, "hardware": hardware_info,
                "software": software_info, "usage": usage_info
            }
            
            # Шаг 2: Анализ
            self.queue.put(("status", "Анализ собранных данных...", 0.9))
            critical_issues, recommendations = analyze_data(collected_data)

            # Шаг 3: Генерация отчета
            self.queue.put(("status", "Формирование итогового отчета...", 0.95))
            final_report = generate_report_text(collected_data, critical_issues, recommendations)
            
            # Отправляем готовый отчет в GUI
            self.queue.put(("report", final_report))
            self.queue.put(("status", "Анализ завершен!", 1.0))
        except Exception as e:
            error_message = f"Произошла ошибка во время анализа:\n\n{str(e)}"
            self.queue.put(("report", error_message))
            self.queue.put(("status", "Ошибка!", 1.0))

    def process_queue(self):
        """Обрабатывает сообщения из очереди для обновления GUI."""
        try:
            message = self.queue.get_nowait()
            msg_type, data = message[0], message[1:]

            if msg_type == "status":
                text, progress_value = data[0], data[1]
                self.status_label.configure(text=text)
                self.progress_bar.set(progress_value)
                
            elif msg_type == "report":
                report_text = data[0]
                self.report_textbox.configure(state="normal")
                self.report_textbox.delete("1.0", "end")
                self.report_textbox.insert("1.0", report_text)
                self.report_textbox.configure(state="disabled")
                # Возвращаем кнопку в исходное состояние
                self.analyze_button.configure(state="normal", text="Начать анализ")

        except queue.Empty:
            # Если очередь пуста, продолжаем проверять
            self.after(100, self.process_queue)

# --- Точка входа в программу ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
