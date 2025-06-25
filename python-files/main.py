import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import random
from datetime import datetime

import psycopg2
from psycopg2 import Error # Импортируем Error для обработки ошибок

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import lib1
from TemperatureSensor import TemperatureSensor
from PostgreSQLManager import PostgreSQLManager
# --- 1. Emulated Temperature Sensor ---


# --- 2. PostgreSQL Database Manager ---


# --- 4. Plotter ---
class Plotter:
    def __init__(self, master_frame):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2Tk(self.canvas, master_frame) 
        self.toolbar.update()
        self.canvas_widget.pack(side="top", fill="both", expand=True)

    def plot_data(self, x_values, y_values, title="", xlabel="Время", ylabel="Значение (°C)"):
        self.ax.clear()
        self.ax.plot(x_values, y_values)
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)
        self.canvas.draw()

    def save_plot(self, filename, file_format="pdf"):
        """
        Saves the current plot to a file.
        file_format: 'pdf', 'png', 'jpg', 'svg', etc.
        """
        try:
            self.fig.savefig(f"{filename}.{file_format}", bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Error saving plot: {e}")
            return False

# --- 5. Main Application ---
class TemperatureMonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг температуры с датчиков")
        self.root.geometry("1200x800")

        # --- Database configuration (CHANGE THESE TO YOUR POSTGRESQL CREDENTIALS) ---
        self.db_manager = PostgreSQLManager(
            dbname="sensors",
            user="postgres",     # <--- ВАЖНО: Измените это
            password="postgres"  # <--- ВАЖНО: Измените это
        )
        # --------------------------------------------------------------------------

        self.data_processor = lib1.DataProcessor()
        self.sensors = {} # Инициализируем self.sensors как пустой словарь здесь

        # Сначала инициализируем датчики, чтобы self.sensors был заполнен
        self._initialize_sensors() 
        
        # Теперь, когда self.sensors заполнен, можно создавать виджеты
        self._create_widgets() 

        self.reading_active = False 

    def _initialize_sensors(self):
        # Эмуляция нескольких датчиков для демонстрации
        self.sensors["USB"] = TemperatureSensor("USB", port="USB0", data_format="float", address="0x01")
        self.sensors["Ethernet"] = TemperatureSensor("Ethernet", port="192.168.1.100", data_format="json", address="0x02")
        self.sensors["Wi-Fi"] = TemperatureSensor("Wi-Fi", port="ssid_sensor_net", data_format="xml", address="0x03")
        self.sensors["RS-485"] = TemperatureSensor("RS-485", port="COM1", data_format="binary", address="0x04")
        self.sensors["RS-232"] = TemperatureSensor("RS-232", port="COM2", data_format="text", address="0x05")
        self.sensors["I2C"] = TemperatureSensor("I2C", port="0x48", data_format="byte", address="0x06")
        self.sensors["1-Wire"] = TemperatureSensor("1-Wire", port="DS18B20", data_format="decimal", address="0x07")
        self.sensors["COM"] = TemperatureSensor("COM", port="COM3", data_format="text", address="0x08")

    def _create_widgets(self):
        # Контрольная рамка (левая сторона)
        control_frame = ttk.LabelFrame(self.root, text="Настройки и управление")
        control_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Выбор типа интерфейса
        ttk.Label(control_frame, text="Тип интерфейса:").pack(pady=5)
        self.interface_type_var = tk.StringVar()
        
        # Значения для выпадающего списка берутся из ключей словаря self.sensors
        # self.sensors теперь гарантированно заполнен благодаря измененному порядку в __init__
        self.interface_type_combobox = ttk.Combobox(control_frame,
                                                    textvariable=self.interface_type_var,
                                                    values=list(self.sensors.keys()),
                                                    state="readonly") # Запрещаем ручной ввод
        self.interface_type_combobox.pack(pady=5)
        
        # Устанавливаем первое значение из списка в качестве выбранного по умолчанию
        if self.sensors:
            self.interface_type_combobox.set(list(self.sensors.keys())[0])
        self.interface_type_combobox.bind("<<ComboboxSelected>>", self._on_interface_select)

        # Отображение информации о датчике (только для чтения)
        ttk.Label(control_frame, text="Порт:").pack(pady=2)
        self.port_label = ttk.Label(control_frame, text="")
        self.port_label.pack(pady=2)

        ttk.Label(control_frame, text="Формат данных:").pack(pady=2)
        self.format_label = ttk.Label(control_frame, text="")
        self.format_label.pack(pady=2)

        ttk.Label(control_frame, text="Адрес:").pack(pady=2)
        self.address_label = ttk.Label(control_frame, text="")
        self.address_label.pack(pady=2)
        
        self._on_interface_select() # Обновить информацию при запуске

        # Выбор метода обработки
        ttk.Label(control_frame, text="Метод обработки:").pack(pady=10)
        self.processing_method_var = tk.StringVar()
        ttk.Radiobutton(control_frame, text="Без обработки", variable=self.processing_method_var, value="Без обработки").pack(anchor="w")
        ttk.Radiobutton(control_frame, text="Сглаживание", variable=self.processing_method_var, value="smooth").pack(anchor="w")
        ttk.Radiobutton(control_frame, text="Аппроксимация", variable=self.processing_method_var, value="approximate").pack(anchor="w")
        ttk.Radiobutton(control_frame, text="Дифференцирование", variable=self.processing_method_var, value="differentiate").pack(anchor="w")
        ttk.Radiobutton(control_frame, text="Интегрирование", variable=self.processing_method_var, value="integrate").pack(anchor="w")
        self.processing_method_var.set("Без обработки") # По умолчанию выбираем "Без обработки"

        # Кнопки управления
        self.start_button = ttk.Button(control_frame, text="Начать считывание", command=self._start_reading)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(control_frame, text="Остановить считывание", command=self._stop_reading, state="disabled")
        self.stop_button.pack(pady=5)
        
        self.process_button = ttk.Button(control_frame, text="Обработать и Построить график", command=self._process_and_plot)
        self.process_button.pack(pady=10)

        self.save_button = ttk.Button(control_frame, text="Сохранить график", command=self._save_plot)
        self.save_button.pack(pady=10)
        
        # Кадр участка (правая сторона)
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.plotter = Plotter(plot_frame)

    def _on_interface_select(self, event=None):
        selected_interface = self.interface_type_var.get()
        if selected_interface in self.sensors:
            sensor = self.sensors[selected_interface]
            self.port_label.config(text=sensor.port if sensor.port else "Н/Д")
            self.format_label.config(text=sensor.data_format if sensor.data_format else "Н/Д")
            self.address_label.config(text=sensor.address if sensor.address else "Н/Д")
        else:
            self.port_label.config(text="Н/Д")
            self.format_label.config(text="Н/Д")
            self.address_label.config(text="Н/Д")

    def _start_reading(self):
        # Убедимся, что соединение с базой данных активно перед началом считывания
        if self.db_manager.conn is None or self.db_manager.conn.closed:
            messagebox.showerror("Ошибка подключения к БД", "Не удалось подключиться к базе данных. Проверьте настройки и запустите программу заново.")
            return

        if not self.reading_active:
            self.reading_active = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            # Начинаем считывание в отдельном потоке, чтобы не блокировать графический интерфейс
            self.reading_thread = threading.Thread(target=self._read_sensor_data)
            self.reading_thread.daemon = True # Поток завершится при закрытии приложения
            self.reading_thread.start()
            messagebox.showinfo("Начало считывания", "Считывание данных с датчиков запущено.")

    def _stop_reading(self):
        if self.reading_active:
            self.reading_active = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            messagebox.showinfo("Остановка считывания", "Считывание данных с датчиков остановлено.")

    def _read_sensor_data(self):
        while self.reading_active:
            for interface_type, sensor in self.sensors.items():
                data = sensor.read_data()
                self.db_manager.insert_reading(data)
                
            time.sleep(1) # Считывать данные каждую секунду (для эмуляции)

    def _process_and_plot(self):
        selected_interface = self.interface_type_var.get()
        selected_method = self.processing_method_var.get()

        db_data = self.db_manager.get_data_by_interface(selected_interface)
        if not db_data:
            messagebox.showwarning("Нет данных", f"Нет данных для обработки для интерфейса: {selected_interface}. Начните считывание.")
            return
        
        # Извлечение временных меток и температур
        timestamps = [row[0] for row in db_data]
        temperatures = np.array([row[1] for row in db_data])

        # Преобразование временных меток в числовые значения для построения графиков
        # Используем индексы для оси X для упрощения, так как временные метки могут быть сложными для оси X Matplotlib.
        x_values = np.arange(len(timestamps))
        #datetime_objects = timestamps
       # datetime_objects = [datetime.strptime(ts,"%Y-%m-%d %H:%M:%S") for ts in timestamps]  # Подставьте свой формат, если необходимо

# Преобразование объектов datetime в числовые значения, понятные Matplotlib
       # x_values = mdates.date2num(datetime_obje)
        
        title = f"Температура с датчика {selected_interface}"
        
        try:
            processed_temperatures = temperatures.copy() # Начинаем с копии исходных данных
            x_plot_values = x_values.copy()

            if selected_method == "Без обработки": # Новый вариант для "Без обработки"
                title += " (Без обработки)"
                # Обработка не требуется, используем исходные данные
                pass 
            elif selected_method == "smooth":
                if len(processed_temperatures) < 5:
                    messagebox.showwarning("Ошибка обработки", "Недостаточно данных для сглаживания. Необходимо минимум 5 точек.")
                    self.plotter.plot_data(x_values, temperatures, title="Исходные данные (Недостаточно для сглаживания)", xlabel="Индекс", ylabel="Температура (°C)")
                    return
                processed_temperatures = self.data_processor.smooth(processed_temperatures)
                title += " (Сглаживание)"
            elif selected_method == "approximate":
                if len(processed_temperatures) < 2:
                    messagebox.showwarning("Ошибка обработки", "Недостаточно данных для аппроксимации. Необходимо минимум 2 точки.")
                    self.plotter.plot_data(x_values, temperatures, title="Исходные данные (Недостаточно для аппроксимации)", xlabel="Индекс", ylabel="Температура (°C)")
                    return
                f_approx = self.data_processor.approximate(x_values, processed_temperatures, kind='cubic')
                x_plot_values = np.linspace(min(x_values), max(x_values), 500)
                processed_temperatures = f_approx(x_plot_values)
                title += " (Аппроксимация)"
            elif selected_method == "differentiate":
                processed_temperatures = self.data_processor.differentiate(processed_temperatures)
                x_plot_values = x_values[:-1]
                title += " (Дифференцирование)"
            elif selected_method == "integrate":
                processed_temperatures = self.data_processor.integrate(processed_temperatures)
                x_plot_values = x_values
                title += " (Интегрирование)"
            else:
                messagebox.showerror("Ошибка", "Неизвестный метод обработки.")
                return
            
            self.plotter.plot_data(x_plot_values, processed_temperatures, title=title, xlabel="Индекс данных", ylabel="Значение")
            messagebox.showinfo("График построен", f"График для датчика с интерфейсом {selected_interface} построен с методом {selected_method}.")

        except ValueError as ve:
            messagebox.showwarning("Ошибка обработки", f"Ошибка: {ve}")
            self.plotter.plot_data(x_values, temperatures, title="Исходные данные (Ошибка обработки)", xlabel="Индекс", ylabel="Температура (°C)")
        except Exception as e:
            messagebox.showerror("Ошибка обработки", f"Произошла ошибка при обработке данных: {e}")
            self.plotter.plot_data(x_values, temperatures, title="Исходные данные (Ошибка обработки)", xlabel="Индекс", ylabel="Температура (°C)")


    def _save_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf"),
                                                           ("PNG files", "*.png"),
                                                           ("JPEG files", "*.jpg")])
        if file_path:
            file_format = file_path.split(".")[-1].lower()
            if file_format in ["pdf", "png", "jpg"]:
                if self.plotter.save_plot(file_path.rsplit('.', 1)[0], file_format):
                    messagebox.showinfo("Сохранение графика", f"График успешно сохранен в {file_path}")
                else:
                    messagebox.showerror("Ошибка сохранения", "Не удалось сохранить график.")
            elif file_format == "docx":
                messagebox.showwarning("Сохранение в Word", "Сохранение в .docx не реализовано в данной версии. Сохраните в PDF/PNG и вставьте вручную.")
            else:
                messagebox.showwarning("Неподдерживаемый формат", "Выбранный формат файла не поддерживается для сохранения графика.")


    def on_closing(self):
        self.reading_active = False # Останавливаем поток считывания
        if self.db_manager:
            self.db_manager.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureMonitoringApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
