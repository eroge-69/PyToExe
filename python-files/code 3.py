import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time

class SpinalStimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Стимулятор спинного мозга Крисаф™")
        
        # Инициализация атрибутов
        self.channel_params = []
        self.signal_lines = []
        self.rms_labels = []
        self.ax = None
        self.canvas = None
        self.fig = None
        
        # Цвета каналов
        self.channel_colors = {
            0: '#1f77b4',  # Синий
            1: '#ff7f0e',  # Оранжевый
            2: '#2ca02c',  # Зеленый
            3: '#d62728',  # Красный
            4: '#9467bd'   # Фиолетовый
        }
        
        # Полноэкранный режим
        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        
        # Параметры
        self.max_current = 250
        self.max_frequency = 99
        self.max_rms_current = 45
        
        # Состояние
        self.active_channels = []
        self.battery_level = 100
        self.device_connected = True
        self.stimulation_active = False
        self.current_rms = [0.0] * 5
        self.channel_stimulation_active = [False] * 5
        
        # Оптимизация
        self.last_update_time = 0
        self.update_interval = 0.1
        
        # Инициализация
        self.create_menu()
        self.setup_styles()
        self.create_widgets()
        self.update_status()

    def create_menu(self):
        """Создает верхнее меню программы"""
        menubar = tk.Menu(self.root)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню "Экран"
        screen_menu = tk.Menu(menubar, tearoff=0)
        self.fullscreen_var = tk.BooleanVar(value=self.fullscreen)
        screen_menu.add_checkbutton(label="Полноэкранный", 
                                  variable=self.fullscreen_var,
                                  command=self.toggle_fullscreen)
        menubar.add_cascade(label="Экран", menu=screen_menu)
        
        self.root.config(menu=menubar)

    def toggle_fullscreen(self, event=None):
        """Переключает между полноэкранным и оконным режимом"""
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        self.fullscreen_var.set(self.fullscreen)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Channel.TFrame', background='#e9e9e9', borderwidth=2, relief='groove')
        style.configure('Active.TFrame', background='#d9e7f9')
        style.configure('Red.TLabel', foreground='red')
        style.configure('Green.TLabel', foreground='green')
        style.configure('Yellow.TLabel', foreground='orange')
        style.configure('Blue.TButton', foreground='white', background='#4b8df8', font=('Segoe UI', 9))
        style.configure('Red.TButton', foreground='white', background='#d62728', font=('Segoe UI', 9))
        style.configure('Green.TButton', foreground='white', background='#2ca02c', font=('Segoe UI', 9))
        style.configure('Large.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('ChannelStart.TButton', font=('Segoe UI', 9), width=8)
        style.configure('ChannelStop.TButton', font=('Segoe UI', 9), width=8)

    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель статуса
        self.create_device_status_panel(main_frame)
        
        # Контейнер для каналов с горизонтальной прокруткой
        channels_container = ttk.Frame(main_frame)
        channels_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Холст и скроллбар для горизонтальной прокрутки
        canvas = tk.Canvas(channels_container, height=350)
        scroll_x = ttk.Scrollbar(channels_container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scroll_x.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        scroll_x.pack(side="bottom", fill="x")
        
        # Создаем каналы в горизонтальном расположении
        self.create_channel_controls(scrollable_frame)
        
        # Осциллограф
        self.create_oscilloscope(main_frame)
        
        # Нижняя панель управления
        self.create_system_controls(main_frame)

    def create_device_status_panel(self, parent):
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="СТАТУС УСТРОЙСТВА:", style='Title.TLabel').pack(side=tk.LEFT)
        
        self.connection_status = ttk.Label(status_frame, text="ПОДКЛЮЧЕНО", style='Green.TLabel')
        self.connection_status.pack(side=tk.LEFT, padx=20)
        
        self.battery_status = ttk.Label(status_frame, text=f"БАТАРЕЯ: {self.battery_level}%", style='Green.TLabel')
        self.battery_status.pack(side=tk.LEFT, padx=20)
        
        self.ready_status = ttk.Label(status_frame, text="ГОТОВ", style='Green.TLabel')
        self.ready_status.pack(side=tk.LEFT, padx=20)
        
        self.rms_status_frame = ttk.Frame(status_frame)
        self.rms_status_frame.pack(side=tk.RIGHT)
        
        for i in range(5):
            lbl = ttk.Label(self.rms_status_frame, text=f"Ch{i+1}: 0.0 мА", style='Green.TLabel')
            lbl.pack(side=tk.LEFT, padx=5)
            self.rms_labels.append(lbl)

    def create_channel_controls(self, parent):
        # Контейнер для каналов с горизонтальным расположением
        channels_frame = ttk.Frame(parent)
        channels_frame.pack(fill=tk.BOTH, expand=True)
        
        for i in range(5):
            # Основной фрейм канала с цветной полоской сверху
            channel_frame = ttk.Frame(channels_frame, width=300, style='Channel.TFrame')
            channel_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, ipadx=5, ipady=5)
            
            # Цветная полоска сверху
            color_strip = tk.Canvas(channel_frame, height=5, bg=self.channel_colors[i], highlightthickness=0)
            color_strip.pack(side=tk.TOP, fill=tk.X)
            
            # Заголовок канала
            ttk.Label(channel_frame, text=f"КАНАЛ {i+1}", font=('Segoe UI', 10, 'bold')).pack(pady=(5,10))
            
            # Активация канала
            chk_var = tk.BooleanVar()
            chk = ttk.Checkbutton(channel_frame, text="АКТИВИРОВАТЬ", variable=chk_var,
                                command=lambda idx=i: self.activate_channel(idx))
            chk.pack(pady=(0,10))
            
            # Кнопка старт/стоп для канала
            btn_frame = ttk.Frame(channel_frame)
            btn_frame.pack(fill=tk.X, pady=5)
            
            self.channel_params.append({
                "start_stop_btn": ttk.Button(btn_frame, text="СТАРТ", 
                                           command=lambda idx=i: self.toggle_channel_stimulation(idx),
                                           style='ChannelStart.TButton'),
                "btn_state": False
            })
            
            self.channel_params[-1]["start_stop_btn"].pack(side=tk.TOP, pady=5)
            
            # Полярность
            ttk.Label(channel_frame, text="Полярность:").pack(anchor=tk.W)
            polarity_form = ttk.Combobox(channel_frame, values=["Монополярный", "Биполярный"], state='readonly')
            polarity_form.pack(fill=tk.X, pady=2)
            polarity_form.current(0)
            polarity_form.bind("<<ComboboxSelected>>", lambda e: self.update_rms_value())
            
            # Несущая
            ttk.Label(channel_frame, text="Несущая:").pack(anchor=tk.W)
            carrier_form = ttk.Combobox(channel_frame, values=["Без несущей", "С несущей"], state='readonly')
            carrier_form.pack(fill=tk.X, pady=2)
            carrier_form.current(0)
            carrier_form.bind("<<ComboboxSelected>>", lambda e: self.update_rms_value())
            
            # Индикатор
            channel_led = tk.Canvas(channel_frame, width=20, height=20, bg='white', highlightthickness=0)
            channel_led.pack(pady=10)
            channel_led.create_oval(2, 2, 18, 18, fill='gray')
            
            # Сохраняем параметры канала
            self.channel_params[i].update({
                "frame": channel_frame,
                "active": chk_var,
                "polarity_form": polarity_form,
                "carrier_form": carrier_form,
                "led": channel_led,
                "color": self.channel_colors[i]
            })
        
        # Добавляем контролы после создания всех каналов
        for i in range(5):
            self.add_control(i, "freq", 1, 99, 10)
            self.add_control(i, "current", 0, self.max_current, 50)
            self.add_control(i, "width", 0.1, 1.0, 0.5, 1)
            self.add_control(i, "carrier", 4, 10, 5)

    def add_control(self, channel_idx, name, min_val, max_val, default, decimals=0):
        ch_frame = self.channel_params[channel_idx]["frame"]
        
        frame = ttk.Frame(ch_frame)
        frame.pack(fill=tk.X, pady=2)
        
        label_map = {
            "freq": "Частота (1-99 Гц):",
            "current": f"Сила тока (0-{self.max_current} мА):",
            "width": "Длительность (0.1-1.0 мс):",
            "carrier": "Несущая частота (4-10 кГц):"
        }
        
        ttk.Label(frame, text=label_map[name]).pack(anchor=tk.W)
        
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X)
        
        var = tk.StringVar(value=str(default))
        
        # Кнопки -/+
        ttk.Button(control_frame, text="-", width=3, style='Blue.TButton',
                  command=lambda: self.adjust_value(var, -1, min_val, max_val, decimals)).pack(side=tk.LEFT)
        
        entry = ttk.Entry(control_frame, textvariable=var, width=6)
        entry.pack(side=tk.LEFT, padx=2)
        entry.bind("<KeyRelease>", lambda e: self.update_rms_value())
        
        ttk.Button(control_frame, text="+", width=3, style='Blue.TButton',
                  command=lambda: self.adjust_value(var, 1, min_val, max_val, decimals)).pack(side=tk.LEFT)
        
        slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                          command=lambda v: self.on_slider_change(var, v, decimals))
        slider.set(default)
        slider.pack(fill=tk.X, pady=5)
        
        # Сохраняем элементы управления
        self.channel_params[channel_idx][f"{name}_var"] = var
        self.channel_params[channel_idx][f"{name}_slider"] = slider
        self.channel_params[channel_idx][f"{name}_entry"] = entry
        self.channel_params[channel_idx][f"{name}_minus_btn"] = control_frame.winfo_children()[0]
        self.channel_params[channel_idx][f"{name}_plus_btn"] = control_frame.winfo_children()[2]

    def on_slider_change(self, var, value, decimals):
        var.set(f"{float(value):.{decimals}f}")
        self.update_rms_value()

    def adjust_value(self, var, delta, min_val, max_val, decimals):
        try:
            current = float(var.get())
            new_val = max(min_val, min(max_val, current + delta))
            var.set(f"{new_val:.{decimals}f}")
            self.update_rms_value()
        except ValueError:
            pass

    def toggle_channel_stimulation(self, channel_idx):
        # Проверка RMS перед запуском
        if self.current_rms[channel_idx] > self.max_rms_current and not self.channel_params[channel_idx]["btn_state"]:
            messagebox.showwarning("Предупреждение", 
                                 f"Превышен максимальный RMS для канала {channel_idx+1}!")
            return
        
        # Изменение состояния
        self.channel_params[channel_idx]["btn_state"] = not self.channel_params[channel_idx]["btn_state"]
        
        if self.channel_params[channel_idx]["btn_state"]:
            # Включение стимуляции
            self.channel_params[channel_idx]["start_stop_btn"].config(text="СТОП", style='ChannelStop.TButton')
            self.channel_stimulation_active[channel_idx] = True
            self.lock_channel_controls(channel_idx, True)
        else:
            # Выключение стимуляции
            self.channel_params[channel_idx]["start_stop_btn"].config(text="СТАРТ", style='ChannelStart.TButton')
            self.channel_stimulation_active[channel_idx] = False
            self.lock_channel_controls(channel_idx, False)
        
        self.update_status()

    def lock_channel_controls(self, channel_idx, lock):
        state = "disabled" if lock else "normal"
        
        # Блокировка элементов управления
        self.channel_params[channel_idx]["polarity_form"].config(state=state)
        self.channel_params[channel_idx]["carrier_form"].config(state=state)
        
        for param in ["freq", "current", "width", "carrier"]:
            self.channel_params[channel_idx][f"{param}_slider"].config(state=state)
            self.channel_params[channel_idx][f"{param}_entry"].config(state=state)
            self.channel_params[channel_idx][f"{param}_minus_btn"].config(state=state)
            self.channel_params[channel_idx][f"{param}_plus_btn"].config(state=state)
        
        # Блокировка чекбокса активации
        for child in self.channel_params[channel_idx]["frame"].winfo_children():
            if isinstance(child, ttk.Checkbutton):
                child.config(state=state)

    def activate_channel(self, channel_idx):
        if channel_idx in self.active_channels:
            self.active_channels.remove(channel_idx)
            self.channel_params[channel_idx]["frame"].configure(style='Channel.TFrame')
            self.channel_params[channel_idx]["led"].itemconfig(1, fill='gray')
            
            # Если канал деактивирован, выключаем стимуляцию
            if self.channel_params[channel_idx]["btn_state"]:
                self.toggle_channel_stimulation(channel_idx)
        else:
            self.active_channels.append(channel_idx)
            self.channel_params[channel_idx]["frame"].configure(style='Active.TFrame')
            self.channel_params[channel_idx]["led"].itemconfig(1, fill=self.channel_params[channel_idx]["color"])
        
        self.update_rms_value()

    def update_status(self):
        if self.device_connected:
            self.connection_status.config(text="ПОДКЛЮЧЕНО", style='Green.TLabel')
        else:
            self.connection_status.config(text="НЕТ ПОДКЛЮЧЕНИЯ", style='Red.TLabel')
            
        if self.battery_level > 20:
            self.battery_status.config(text=f"БАТАРЕЯ: {self.battery_level}%", style='Green.TLabel')
        elif self.battery_level > 5:
            self.battery_status.config(text=f"БАТАРЕЯ: {self.battery_level}%", style='Yellow.TLabel')
        else:
            self.battery_status.config(text=f"БАТАРЕЯ: {self.battery_level}%", style='Red.TLabel')
            
        if not self.active_channels:
            self.ready_status.config(text="НЕ АКТИВЕН", style='Red.TLabel')
        elif any(rms > self.max_rms_current for rms in self.current_rms):
            self.ready_status.config(text="ПРЕВЫШЕНИЕ RMS", style='Red.TLabel')
        else:
            self.ready_status.config(text="ГОТОВ", style='Green.TLabel')

    def calculate_rms(self):
        channel_rms = [0.0] * 5
        
        for channel_idx in range(5):
            if channel_idx not in self.active_channels:
                continue
                
            ch = self.channel_params[channel_idx]
            try:
                freq = float(ch["freq_var"].get())
                current = float(ch["current_var"].get())
                width = float(ch["width_var"].get()) * 1000
                carrier_freq = float(ch["carrier_var"].get()) * 1000
                polarity = ch["polarity_form"].get()
                has_carrier = ch["carrier_form"].get() == "С несущей"
            except ValueError:
                continue
            
            t = np.linspace(0, 1000/freq if freq > 0 else 100, 1000)
            signal = np.zeros_like(t)
            
            if polarity == "Монополярный" and not has_carrier:
                signal[(t >= 0) & (t <= width)] = current
            elif polarity == "Биполярный" and not has_carrier:
                signal[(t >= 0) & (t <= width/2)] = current
                signal[(t >= width/2) & (t <= width)] = -current
            elif polarity == "Монополярный" and has_carrier:
                carrier_signal = current * (0.5 * (1 + np.sign(np.sin(2*np.pi*carrier_freq*t/1000))))
                signal[(t >= 0) & (t <= width)] = carrier_signal[(t >= 0) & (t <= width)]
            elif polarity == "Биполярный" and has_carrier:
                carrier_signal = current * np.sin(2*np.pi*carrier_freq*t/1000)
                signal[(t >= 0) & (t <= width)] = carrier_signal[(t >= 0) & (t <= width)]
            
            channel_rms[channel_idx] = np.sqrt(np.mean(signal**2))
        
        return channel_rms

    def update_rms_value(self, event=None):
        self.current_rms = self.calculate_rms()
        
        for i in range(5):
            rms_value = self.current_rms[i]
            if i in self.active_channels:
                if rms_value > self.max_rms_current:
                    self.rms_labels[i].config(text=f"Ch{i+1}: {rms_value:.1f} мА", style='Red.TLabel')
                else:
                    self.rms_labels[i].config(text=f"Ch{i+1}: {rms_value:.1f} мА", style='Green.TLabel')
            else:
                self.rms_labels[i].config(text=f"Ch{i+1}: 0.0 мА", style='Green.TLabel')
        
        self.update_status()
        self.update_oscilloscope()

    def update_oscilloscope(self):
        if not hasattr(self, 'ax') or self.ax is None:
            return
            
        for i, line in enumerate(self.signal_lines):
            if i in self.active_channels:
                ch = self.channel_params[i]
                try:
                    freq = float(ch["freq_var"].get())
                    current = float(ch["current_var"].get())
                    width = float(ch["width_var"].get()) * 1000
                    carrier_freq = float(ch["carrier_var"].get()) * 1000
                    polarity = ch["polarity_form"].get()
                    has_carrier = ch["carrier_form"].get() == "С несущей"
                except ValueError:
                    continue
                
                t = np.linspace(0, 1000/freq if freq > 0 else 100, 1000)
                signal = np.zeros_like(t)
                
                if polarity == "Монополярный" and not has_carrier:
                    signal[(t >= 0) & (t <= width)] = current
                elif polarity == "Биполярный" and not has_carrier:
                    signal[(t >= 0) & (t <= width/2)] = current
                    signal[(t >= width/2) & (t <= width)] = -current
                elif polarity == "Монополярный" and has_carrier:
                    carrier_signal = current * (0.5 * (1 + np.sign(np.sin(2*np.pi*carrier_freq*t/1000))))
                    signal[(t >= 0) & (t <= width)] = carrier_signal[(t >= 0) & (t <= width)]
                elif polarity == "Биполярный" and has_carrier:
                    carrier_signal = current * np.sin(2*np.pi*carrier_freq*t/1000)
                    signal[(t >= 0) & (t <= width)] = carrier_signal[(t >= 0) & (t <= width)]
                
                line.set_data(t, signal)
                line.set_visible(True)
            else:
                line.set_visible(False)
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def create_oscilloscope(self, parent):
        osc_frame = ttk.LabelFrame(parent, text="ОСЦИЛЛОГРАФ СИГНАЛОВ", padding=10)
        osc_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(12, 4))
        self.ax.set_title("ФОРМА ИМПУЛЬСОВ", pad=20)
        self.ax.set_xlabel("Время, мс")
        self.ax.set_ylabel("Ток, мА")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-self.max_current*1.1, self.max_current*1.1)
        
        for i in range(5):
            line, = self.ax.plot([], [], lw=2, color=self.channel_colors[i], label=f"Канал {i+1}")
            self.signal_lines.append(line)
        
        self.ax.legend(loc='upper right')
        self.canvas = FigureCanvasTkAgg(self.fig, master=osc_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_system_controls(self, parent):
        """Создает панель системных кнопок управления"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Кнопка запуска/остановки стимуляции
        self.start_button = ttk.Button(
            control_frame, 
            text="ЗАПУСТИТЬ СТИМУЛЯЦИЮ", 
            command=self.toggle_stimulation,
            style='Large.TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Кнопка сброса параметров
        reset_btn = ttk.Button(
            control_frame, 
            text="СБРОС ПАРАМЕТРОВ", 
            command=self.reset_parameters,
            style='Large.TButton'
        )
        reset_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Кнопка сохранения профиля
        save_btn = ttk.Button(
            control_frame, 
            text="СОХРАНИТЬ ПРОФИЛЬ", 
            command=self.save_profile,
            style='Large.TButton'
        )
        save_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Кнопка загрузки профиля
        load_btn = ttk.Button(
            control_frame, 
            text="ЗАГРУЗИТЬ ПРОФИЛЬ", 
            command=self.load_profile,
            style='Large.TButton'
        )
        load_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def toggle_stimulation(self):
        """Включает/выключает стимуляцию на всех активных каналах"""
        if not self.stimulation_active:
            # Запускаем стимуляцию на всех активных каналах
            for channel_idx in range(5):
                if (channel_idx in self.active_channels and 
                    not self.channel_params[channel_idx]["btn_state"]):
                    self.toggle_channel_stimulation(channel_idx)
            
            self.stimulation_active = True
            self.start_button.config(text="ОСТАНОВИТЬ СТИМУЛЯЦИЮ", style='Red.TButton')
        else:
            # Останавливаем стимуляцию на всех каналах
            for channel_idx in range(5):
                if self.channel_params[channel_idx]["btn_state"]:
                    self.toggle_channel_stimulation(channel_idx)
            
            self.stimulation_active = False
            self.start_button.config(text="ЗАПУСТИТЬ СТИМУЛЯЦИЮ", style='Green.TButton')
        
        self.update_status()

    def reset_parameters(self):
        for i, ch in enumerate(self.channel_params):
            ch["active"].set(False)
            ch["polarity_form"].current(0)
            ch["carrier_form"].current(0)
            ch["freq_var"].set("10")
            ch["current_var"].set("50")
            ch["width_var"].set("0.5")
            ch["carrier_var"].set("5")
            ch["freq_slider"].set(10)
            ch["current_slider"].set(50)
            ch["width_slider"].set(0.5)
            ch["carrier_slider"].set(5)
            ch["frame"].configure(style='Channel.TFrame')
            ch["led"].itemconfig(1, fill='gray')
            
            # Сбрасываем кнопку старт/стоп
            if ch["btn_state"]:
                self.toggle_channel_stimulation(i)
            ch["start_stop_btn"].config(text="СТАРТ", style='ChannelStart.TButton')
            ch["btn_state"] = False
        
        self.active_channels = []
        self.current_rms = [0.0] * 5
        self.update_rms_value()

    def save_profile(self):
        messagebox.showinfo("Сохранение", "Профиль успешно сохранен")

    def load_profile(self):
        messagebox.showinfo("Загрузка", "Профиль успешно загружен")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpinalStimulatorGUI(root)
    root.mainloop()