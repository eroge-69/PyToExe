"""
Главное окно приложения для мониторинга устройств через Modbus.
Реализует GUI интерфейс с выбором COM порта и отображением данных.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import threading
import time
from modbus_client import ModbusClient, DeviceData


class DeviceMonitorApp:
    """Главный класс приложения для мониторинга устройств"""
    
    def __init__(self, root):
        """
        Инициализация главного окна приложения
        
        Args:
            root: Корневое окно Tkinter
        """
        self.root = root
        self.root.title("Мониторинг устройств Modbus")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Объекты для работы с Modbus
        self.modbus_client: ModbusClient = None
        self.monitoring_thread: threading.Thread = None
        self.is_monitoring = False
        
        # Данные устройств
        self.current_data: DeviceData = None
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Обновляем список портов
        self.refresh_ports()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Система мониторинга устройств", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Секция подключения
        connection_frame = ttk.LabelFrame(main_frame, text="Подключение", padding="10")
        connection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        # Выбор COM порта
        ttk.Label(connection_frame, text="COM порт:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var, 
                                      state="readonly", width=15)
        self.port_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Кнопка обновления портов
        refresh_btn = ttk.Button(connection_frame, text="Обновить", 
                                command=self.refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Кнопка подключения/отключения
        self.connect_btn = ttk.Button(connection_frame, text="Подключиться", 
                                     command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=3)
        
        # Статус подключения
        self.status_label = ttk.Label(connection_frame, text="Не подключен", 
                                     foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        # Секция данных измерений
        data_frame = ttk.LabelFrame(main_frame, text="Данные измерений", padding="10")
        data_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(data_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Вкладка напряжений и токов
        self.create_voltage_current_tab()
        
        # Вкладка мощностей
        self.create_power_tab()
        
        # Вкладка состояний устройств
        self.create_device_states_tab()
        
        # Настройка весов для растягивания
        main_frame.rowconfigure(2, weight=1)
        data_frame.rowconfigure(0, weight=1)
    
    def create_voltage_current_tab(self):
        """Создание вкладки с напряжениями и токами"""
        voltage_frame = ttk.Frame(self.notebook)
        self.notebook.add(voltage_frame, text="Напряжения и токи")
        
        # Напряжения
        voltage_group = ttk.LabelFrame(voltage_frame, text="Напряжения (В)", padding="10")
        voltage_group.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Напряжение фазы A
        ttk.Label(voltage_group, text="U_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.voltage_a_var = tk.StringVar(value="0")
        ttk.Label(voltage_group, textvariable=self.voltage_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        # Напряжение фазы B
        ttk.Label(voltage_group, text="U_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.voltage_b_var = tk.StringVar(value="0")
        ttk.Label(voltage_group, textvariable=self.voltage_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        # Напряжение фазы C
        ttk.Label(voltage_group, text="U_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.voltage_c_var = tk.StringVar(value="0")
        ttk.Label(voltage_group, textvariable=self.voltage_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
        
        # Токи
        current_group = ttk.LabelFrame(voltage_frame, text="Токи (А)", padding="10")
        current_group.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Ток фазы A
        ttk.Label(current_group, text="I_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.current_a_var = tk.StringVar(value="0.0")
        ttk.Label(current_group, textvariable=self.current_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        # Ток фазы B
        ttk.Label(current_group, text="I_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.current_b_var = tk.StringVar(value="0.0")
        ttk.Label(current_group, textvariable=self.current_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        # Ток фазы C
        ttk.Label(current_group, text="I_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.current_c_var = tk.StringVar(value="0.0")
        ttk.Label(current_group, textvariable=self.current_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
        
        # Коэффициенты мощности
        cos_phi_group = ttk.LabelFrame(voltage_frame, text="Коэффициенты мощности", padding="10")
        cos_phi_group.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # cosφ фазы A
        ttk.Label(cos_phi_group, text="cosφ_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.cos_phi_a_var = tk.StringVar(value="0.00")
        ttk.Label(cos_phi_group, textvariable=self.cos_phi_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        # cosφ фазы B
        ttk.Label(cos_phi_group, text="cosφ_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.cos_phi_b_var = tk.StringVar(value="0.00")
        ttk.Label(cos_phi_group, textvariable=self.cos_phi_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        # cosφ фазы C
        ttk.Label(cos_phi_group, text="cosφ_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.cos_phi_c_var = tk.StringVar(value="0.00")
        ttk.Label(cos_phi_group, textvariable=self.cos_phi_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
    
    def create_power_tab(self):
        """Создание вкладки с мощностями"""
        power_frame = ttk.Frame(self.notebook)
        self.notebook.add(power_frame, text="Мощности")
        
        # Активные мощности
        active_power_group = ttk.LabelFrame(power_frame, text="Активные мощности (Вт)", padding="10")
        active_power_group.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(active_power_group, text="P_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.power_p_a_var = tk.StringVar(value="0")
        ttk.Label(active_power_group, textvariable=self.power_p_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(active_power_group, text="P_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.power_p_b_var = tk.StringVar(value="0")
        ttk.Label(active_power_group, textvariable=self.power_p_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(active_power_group, text="P_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.power_p_c_var = tk.StringVar(value="0")
        ttk.Label(active_power_group, textvariable=self.power_p_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
        
        # Реактивные мощности
        reactive_power_group = ttk.LabelFrame(power_frame, text="Реактивные мощности (ВАР)", padding="10")
        reactive_power_group.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(reactive_power_group, text="Q_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.power_q_a_var = tk.StringVar(value="0")
        ttk.Label(reactive_power_group, textvariable=self.power_q_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(reactive_power_group, text="Q_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.power_q_b_var = tk.StringVar(value="0")
        ttk.Label(reactive_power_group, textvariable=self.power_q_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(reactive_power_group, text="Q_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.power_q_c_var = tk.StringVar(value="0")
        ttk.Label(reactive_power_group, textvariable=self.power_q_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
        
        # Полные мощности
        apparent_power_group = ttk.LabelFrame(power_frame, text="Полные мощности (ВА)", padding="10")
        apparent_power_group.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(apparent_power_group, text="S_A:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.power_s_a_var = tk.StringVar(value="0")
        ttk.Label(apparent_power_group, textvariable=self.power_s_a_var, 
                 font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(apparent_power_group, text="S_B:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.power_s_b_var = tk.StringVar(value="0")
        ttk.Label(apparent_power_group, textvariable=self.power_s_b_var, 
                 font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(apparent_power_group, text="S_C:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.power_s_c_var = tk.StringVar(value="0")
        ttk.Label(apparent_power_group, textvariable=self.power_s_c_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.W)
        
        # Суммарные мощности
        total_power_group = ttk.LabelFrame(power_frame, text="Суммарные мощности", padding="10")
        total_power_group.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(total_power_group, text="P_total (Вт):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.total_power_p_var = tk.StringVar(value="0")
        ttk.Label(total_power_group, textvariable=self.total_power_p_var, 
                 font=("Arial", 14, "bold"), foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=(0, 30))
        
        ttk.Label(total_power_group, text="Q_total (ВАР):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.total_power_q_var = tk.StringVar(value="0")
        ttk.Label(total_power_group, textvariable=self.total_power_q_var, 
                 font=("Arial", 14, "bold"), foreground="blue").grid(row=0, column=3, sticky=tk.W, padx=(0, 30))
        
        ttk.Label(total_power_group, text="S_total (ВА):").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.total_power_s_var = tk.StringVar(value="0")
        ttk.Label(total_power_group, textvariable=self.total_power_s_var, 
                 font=("Arial", 14, "bold"), foreground="blue").grid(row=0, column=5, sticky=tk.W)
    
    def create_device_states_tab(self):
        """Создание вкладки с состояниями устройств"""
        states_frame = ttk.Frame(self.notebook)
        self.notebook.add(states_frame, text="Состояния устройств")
        
        # Заголовок
        ttk.Label(states_frame, text="Состояние 8 устройств", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Создаем фрейм для состояний устройств
        devices_frame = ttk.Frame(states_frame)
        devices_frame.grid(row=1, column=0, columnspan=2, padx=20)
        
        # Создаем переменные и лейблы для состояний устройств
        self.device_vars = []
        self.device_labels = []
        
        for i in range(8):
            device_num = i + 1
            
            # Переменная для состояния
            var = tk.StringVar(value="ВЫКЛ")
            self.device_vars.append(var)
            
            # Лейбл с номером устройства
            device_label = ttk.Label(devices_frame, text=f"Устройство {device_num}:", 
                                   font=("Arial", 12))
            device_label.grid(row=i, column=0, sticky=tk.W, padx=(0, 20), pady=5)
            
            # Лейбл с состоянием
            state_label = ttk.Label(devices_frame, textvariable=var, 
                                  font=("Arial", 12, "bold"), foreground="red")
            state_label.grid(row=i, column=1, sticky=tk.W)
            self.device_labels.append(state_label)
    
    def refresh_ports(self):
        """Обновление списка доступных COM портов"""
        try:
            ports = serial.tools.list_ports.comports()
            port_list = [port.device for port in ports]
            self.port_combo['values'] = port_list
            if port_list:
                self.port_combo.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список портов: {e}")
    
    def toggle_connection(self):
        """Переключение состояния подключения"""
        if not self.is_monitoring:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """Подключение к устройству"""
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Ошибка", "Выберите COM порт")
            return
        
        try:
            self.modbus_client = ModbusClient(port)
            if self.modbus_client.connect():
                self.is_monitoring = True
                self.connect_btn.config(text="Отключиться")
                self.status_label.config(text=f"Подключен к {port}", foreground="green")
                
                # Запускаем мониторинг в отдельном потоке
                self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
                self.monitoring_thread.start()
            else:
                messagebox.showerror("Ошибка", "Не удалось подключиться к устройству")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")
    
    def disconnect(self):
        """Отключение от устройства"""
        self.is_monitoring = False
        if self.modbus_client:
            self.modbus_client.disconnect()
            self.modbus_client = None
        
        self.connect_btn.config(text="Подключиться")
        self.status_label.config(text="Не подключен", foreground="red")
        
        # Очищаем данные
        self.clear_data()
    
    def monitoring_loop(self):
        """Основной цикл мониторинга данных"""
        while self.is_monitoring and self.modbus_client:
            try:
                # Читаем данные с устройств
                data = self.modbus_client.read_all_data()
                if data:
                    self.current_data = data
                    # Обновляем интерфейс в главном потоке
                    self.root.after(0, self.update_display, data)
                else:
                    print("Не удалось получить данные с устройств")
                
                # Ждем 1 секунду до следующего чтения
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(1.0)
    
    def update_display(self, data: DeviceData):
        """Обновление отображения данных в интерфейсе"""
        try:
            # Обновляем напряжения
            self.voltage_a_var.set(f"{data.voltage_a:.0f}")
            self.voltage_b_var.set(f"{data.voltage_b:.0f}")
            self.voltage_c_var.set(f"{data.voltage_c:.0f}")
            
            # Обновляем токи
            self.current_a_var.set(f"{data.current_a:.1f}")
            self.current_b_var.set(f"{data.current_b:.1f}")
            self.current_c_var.set(f"{data.current_c:.1f}")
            
            # Обновляем коэффициенты мощности
            self.cos_phi_a_var.set(f"{data.cos_phi_a:.2f}")
            self.cos_phi_b_var.set(f"{data.cos_phi_b:.2f}")
            self.cos_phi_c_var.set(f"{data.cos_phi_c:.2f}")
            
            # Обновляем активные мощности
            self.power_p_a_var.set(f"{data.power_p_a:.0f}")
            self.power_p_b_var.set(f"{data.power_p_b:.0f}")
            self.power_p_c_var.set(f"{data.power_p_c:.0f}")
            
            # Обновляем реактивные мощности
            self.power_q_a_var.set(f"{data.power_q_a:.0f}")
            self.power_q_b_var.set(f"{data.power_q_b:.0f}")
            self.power_q_c_var.set(f"{data.power_q_c:.0f}")
            
            # Обновляем полные мощности
            self.power_s_a_var.set(f"{data.power_s_a:.0f}")
            self.power_s_b_var.set(f"{data.power_s_b:.0f}")
            self.power_s_c_var.set(f"{data.power_s_c:.0f}")
            
            # Обновляем суммарные мощности
            self.total_power_p_var.set(f"{data.total_power_p:.0f}")
            self.total_power_q_var.set(f"{data.total_power_q:.0f}")
            self.total_power_s_var.set(f"{data.total_power_s:.0f}")
            
            # Обновляем состояния устройств
            for i, state in enumerate(data.device_states):
                if state:
                    self.device_vars[i].set("ВКЛ")
                    self.device_labels[i].config(foreground="green")
                else:
                    self.device_vars[i].set("ВЫКЛ")
                    self.device_labels[i].config(foreground="red")
                    
        except Exception as e:
            print(f"Ошибка при обновлении интерфейса: {e}")
    
    def clear_data(self):
        """Очистка отображаемых данных"""
        # Очищаем все переменные
        self.voltage_a_var.set("0")
        self.voltage_b_var.set("0")
        self.voltage_c_var.set("0")
        self.current_a_var.set("0.0")
        self.current_b_var.set("0.0")
        self.current_c_var.set("0.0")
        self.cos_phi_a_var.set("0.00")
        self.cos_phi_b_var.set("0.00")
        self.cos_phi_c_var.set("0.00")
        self.power_p_a_var.set("0")
        self.power_p_b_var.set("0")
        self.power_p_c_var.set("0")
        self.power_q_a_var.set("0")
        self.power_q_b_var.set("0")
        self.power_q_c_var.set("0")
        self.power_s_a_var.set("0")
        self.power_s_b_var.set("0")
        self.power_s_c_var.set("0")
        self.total_power_p_var.set("0")
        self.total_power_q_var.set("0")
        self.total_power_s_var.set("0")
        
        # Очищаем состояния устройств
        for i in range(8):
            self.device_vars[i].set("ВЫКЛ")
            self.device_labels[i].config(foreground="red")
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if self.is_monitoring:
            self.disconnect()
        self.root.destroy()


def main():
    """Главная функция приложения"""
    root = tk.Tk()
    app = DeviceMonitorApp(root)
    
    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Запуск приложения
    root.mainloop()


if __name__ == "__main__":
    main()
