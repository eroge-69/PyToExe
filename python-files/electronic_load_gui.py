import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from datetime import datetime
import math

class ElectronicLoadController(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Arayüz ayarları
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Elektronik Yük Kontrolörü v4.0")
        self.geometry("1400x900")
        self.ser = None
        self.is_connected = False
        self.is_pc_mode = False
        self.data_log = []
        self.current_mode = "ELEKTRONİK YÜK"  # Varsayılan mod

        # Başlangıç ekranını göster
        self.show_startup_screen()

    def show_startup_screen(self):
        """Açılış animasyonu ve bağlantı kontrolü"""
        self.startup_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.startup_frame.pack(fill="both", expand=True)

        # Logo ve başlık
        self.logo_label = ctk.CTkLabel(
            self.startup_frame,
            text="⚡",
            font=ctk.CTkFont(size=80, weight="bold"),
            text_color="#00ff88"
        )
        self.logo_label.pack(pady=(150, 20))

        self.title_label = ctk.CTkLabel(
            self.startup_frame,
            text="ELEKTRONİK YÜK",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(pady=(0, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.startup_frame,
            text="Profesyonel Test ve Ölçüm Sistemi",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        self.subtitle_label.pack()

        # İlerleme çubuğu
        self.progress_bar = ctk.CTkProgressBar(
            self.startup_frame,
            width=400,
            height=4,
            progress_color="#00ff88"
        )
        self.progress_bar.pack(pady=40)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.startup_frame,
            text="Sistem başlatılıyor...",
            font=ctk.CTkFont(size=14),
            text_color="#cccccc"
        )
        self.status_label.pack()

        # Manuel bağlantı butonu
        self.manual_connect_btn = ctk.CTkButton(
            self.startup_frame,
            text="🔧 Manuel Bağlantı",
            command=self.show_manual_connection,
            fg_color="transparent",
            border_width=2,
            border_color="#00ff88",
            text_color="#00ff88",
            width=200
        )
        self.manual_connect_btn.pack(pady=20)

        # Animasyonu başlat
        self.animate_startup()

    def animate_startup(self):
        """Açılış animasyonu"""
        def update_progress():
            for i in range(101):
                time.sleep(0.03)
                self.progress_bar.set(i/100)

                if i < 30:
                    self.status_label.configure(text="Donanım kontrol ediliyor...")
                elif i < 60:
                    self.status_label.configure(text="Arayüz yükleniyor...")
                elif i < 80:
                    self.status_label.configure(text="Arduino bağlantısı kontrol ediliyor...")
                else:
                    self.status_label.configure(text="Başlatılıyor...")

            # Arduino bağlantı kontrolü
            self.auto_connect_arduino()

        threading.Thread(target=update_progress, daemon=True).start()

    def auto_connect_arduino(self):
        """Otomatik Arduino bağlantısı"""
        self.status_label.configure(text="Arduino aranıyor...", text_color="#ffff00")

        def connect_thread():
            try:
                ports = [port.device for port in serial.tools.list_ports.comports()]
                if not ports:
                    self.status_label.configure(
                        text="Hiçbir COM portu bulunamadı!",
                        text_color="#ff4444"
                    )
                    time.sleep(2)
                    self.show_manual_connection()
                    return

                for port in ports:
                    self.status_label.configure(text=f"{port} kontrol ediliyor...", text_color="#ffff00")

                    try:
                        # Porta bağlan
                        ser = serial.Serial(port, 115200, timeout=2)
                        time.sleep(2)

                        # Buffer'ı temizle
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()

                        # PC moduna geçmesini iste
                        ser.write(b"ENTER_PC_MODE\n")
                        time.sleep(1)

                        # Cevap oku
                        response = ""
                        start_time = time.time()
                        while time.time() - start_time < 3:
                            if ser.in_waiting:
                                line = ser.readline().decode().strip()
                                response += line + "\n"
                                print(f"📡 {port}: {line}")

                                if "PC_MODE_ACTIVE" in line or "DEEPSEEK_ELECTRONIC_LOAD_READY" in line:
                                    # Başarılı bağlantı!
                                    self.ser = ser
                                    self.is_connected = True
                                    self.is_pc_mode = True

                                    self.status_label.configure(
                                        text=f"✅ Arduino bağlandı: {port}",
                                        text_color="#00ff88"
                                    )
                                    time.sleep(1)

                                    # Ana menüye geç
                                    self.show_main_menu()
                                    return

                        # Başarısız olursa portu kapat
                        ser.close()
                        time.sleep(0.5)

                    except Exception as e:
                        print(f"❌ {port} hatası: {e}")
                        continue

                # Hiçbir port bağlanamazsa
                self.status_label.configure(
                    text="Arduino bulunamadı! Manuel bağlantı deneyin.",
                    text_color="#ff4444"
                )
                time.sleep(2)
                self.show_manual_connection()

            except Exception as e:
                print(f"❌ Bağlantı hatası: {e}")
                self.status_label.configure(
                    text=f"Hata: {str(e)}",
                    text_color="#ff4444"
                )
                time.sleep(2)
                self.show_manual_connection()

        threading.Thread(target=connect_thread, daemon=True).start()

    def show_main_menu(self):
        """Ana menü arayüzü"""
        if hasattr(self, 'startup_frame'):
            self.startup_frame.destroy()
        if hasattr(self, 'manual_frame'):
            self.manual_frame.destroy()

        self.main_menu_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main_menu_frame.pack(fill="both", expand=True)

        # Başlık
        ctk.CTkLabel(
            self.main_menu_frame,
            text="⚡ ANA MENÜ",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(100, 50))

        # Mod seçim butonları
        button_frame = ctk.CTkFrame(self.main_menu_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        # 1. Elektronik Yük butonu
        electronic_load_btn = ctk.CTkButton(
            button_frame,
            text="1. ELEKTRONİK YÜK",
            command=lambda: self.start_pc_mode("ELEKTRONİK_YUK"),
            fg_color="#00aa55",
            hover_color="#008844",
            height=60,
            width=300,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        electronic_load_btn.pack(pady=15)

        # 2. Batarya Testi butonu
        battery_test_btn = ctk.CTkButton(
            button_frame,
            text="2. BATARYA TESTİ",
            command=lambda: self.start_pc_mode("BATARYA_TESTI"),
            fg_color="#ffaa00",
            hover_color="#cc8800",
            height=60,
            width=300,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        battery_test_btn.pack(pady=15)

        # Bağlantı durumu
        status_frame = ctk.CTkFrame(self.main_menu_frame, fg_color="transparent")
        status_frame.pack(pady=30)

        ctk.CTkLabel(
            status_frame,
            text="● BAĞLI" if self.is_connected else "● BAĞLI DEĞİL",
            text_color="#00ff88" if self.is_connected else "#ff4444",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)

        ctk.CTkButton(
            status_frame,
            text="🔄 Yeniden Bağlan",
            command=self.restart_application,
            width=200
        ).pack(pady=10)

    def start_pc_mode(self, mode):
        """Seçilen modda PC moduna geç"""
        self.current_mode = mode
        mode_text = "ELEKTRONİK YÜK" if mode == "ELEKTRONİK_YUK" else "BATARYA TESTİ"

        # Arduino'ya mod bilgisini gönder
        if self.is_connected and self.ser:
            try:
                command = f"SET_MODE:{mode}\n"
                self.ser.write(command.encode())
                print(f"📤 Mod ayarı: {mode_text}")
            except Exception as e:
                print(f"❌ Mod gönderme hatası: {e}")

        self.show_pc_mode_interface(mode_text)

    def show_manual_connection(self):
        """Manuel bağlantı arayüzü"""
        self.startup_frame.destroy()

        self.manual_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.manual_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.manual_frame,
            text="🔧 MANUEL BAĞLANTI",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(100, 20))

        ctk.CTkLabel(
            self.manual_frame,
            text="Arduino bağlantısı kurulamadı. Lütfen manuel olarak bağlayın:",
            font=ctk.CTkFont(size=16),
            text_color="#cccccc"
        ).pack(pady=10)

        # Port seçimi
        port_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        port_frame.pack(pady=20)

        ctk.CTkLabel(port_frame, text="COM Port:", font=ctk.CTkFont(size=14)).pack(pady=5)

        self.port_combo = ctk.CTkComboBox(
            port_frame,
            values=self.get_available_ports(),
            width=200
        )
        self.port_combo.pack(pady=5)

        # Refresh butonu
        refresh_btn = ctk.CTkButton(
            port_frame,
            text="🔄 Portları Yenile",
            command=self.refresh_ports,
            width=200
        )
        refresh_btn.pack(pady=5)

        # Bağlan butonu
        connect_btn = ctk.CTkButton(
            self.manual_frame,
            text="🔗 BAĞLAN",
            command=self.manual_connect,
            fg_color="#00aa55",
            hover_color="#008844",
            height=40,
            width=200
        )
        connect_btn.pack(pady=20)

        # Ana menü butonu
        main_menu_btn = ctk.CTkButton(
            self.manual_frame,
            text="🏠 ANA MENÜ",
            command=self.show_main_menu,
            fg_color="transparent",
            border_width=2,
            border_color="#888888",
            text_color="#888888",
            height=40,
            width=200
        )
        main_menu_btn.pack(pady=10)

    def get_available_ports(self):
        """Mevcut portları listele"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["Port bulunamadı"]

    def refresh_ports(self):
        """Port listesini yenile"""
        ports = self.get_available_ports()
        self.port_combo.configure(values=ports)
        if ports and ports[0] != "Port bulunamadı":
            self.port_combo.set(ports[0])

    def manual_connect(self):
        """Manuel bağlantı deneme"""
        port = self.port_combo.get()
        if port == "Port bulunamadı":
            return

        self.status_label = ctk.CTkLabel(
            self.manual_frame,
            text=f"{port} bağlanıyor...",
            font=ctk.CTkFont(size=14),
            text_color="#ffff00"
        )
        self.status_label.pack(pady=10)

        def connect_thread():
            try:
                # Porta bağlan
                ser = serial.Serial(port, 115200, timeout=2)
                time.sleep(2)

                # Buffer'ı temizle
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # PC moduna geçmesini iste
                ser.write(b"ENTER_PC_MODE\n")
                time.sleep(1)

                # Cevap oku
                response = ""
                start_time = time.time()
                while time.time() - start_time < 3:
                    if ser.in_waiting:
                        line = ser.readline().decode().strip()
                        response += line + "\n"
                        print(f"📡 {port}: {line}")

                        if "PC_MODE_ACTIVE" in line or "DEEPSEEK_ELECTRONIC_LOAD_READY" in line:
                            # Başarılı bağlantı!
                            self.ser = ser
                            self.is_connected = True
                            self.is_pc_mode = True

                            self.status_label.configure(
                                text=f"✅ Arduino bağlandı: {port}",
                                text_color="#00ff88"
                            )
                            time.sleep(1)

                            # Ana menüye geç
                            self.show_main_menu()
                            return

                # Başarısız
                ser.close()
                self.status_label.configure(
                    text="❌ Bağlantı başarısız! Port ve baud rate kontrol edin.",
                    text_color="#ff4444"
                )

            except Exception as e:
                self.status_label.configure(
                    text=f"❌ Hata: {str(e)}",
                    text_color="#ff4444"
                )

        threading.Thread(target=connect_thread, daemon=True).start()

    def show_pc_mode_interface(self, mode_text):
        """PC Modu arayüzü"""
        if hasattr(self, 'main_menu_frame'):
            self.main_menu_frame.destroy()
        if hasattr(self, 'manual_frame'):
            self.manual_frame.destroy()

        self.create_pc_mode_widgets(mode_text)

    def create_pc_mode_widgets(self, mode_text):
        """PC Modu için arayüz oluştur"""
        # Ana frame
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Başlık çubuğu
        header_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a", height=80)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text=f"⚡ {mode_text} - PC MODU",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00ff88"
        ).pack(side="left", padx=20, pady=20)

        connection_status = ctk.CTkLabel(
            header_frame,
            text="● BAĞLI" if self.is_connected else "● BAĞLI DEĞİL",
            text_color="#00ff88" if self.is_connected else "#ff4444",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        connection_status.pack(side="right", padx=20, pady=20)

        # İçerik alanı
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Sol panel - Kontroller
        left_panel = ctk.CTkFrame(content_frame, width=350, fg_color="#2a2a2a")
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        # Sağ panel - Grafik ve veri
        right_panel = ctk.CTkFrame(content_frame, fg_color="#1a1a1a")
        right_panel.pack(side="right", fill="both", expand=True)

        # KONTROL PANELİ
        control_section = ctk.CTkFrame(left_panel, fg_color="#2a2a2a")
        control_section.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            control_section,
            text="KONTROL PANELİ",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))

        if mode_text == "ELEKTRONİK YÜK":
            # Elektronik Yük kontrolleri
            ctk.CTkLabel(control_section, text="Akım Ayarı (A):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(5, 0))
            self.current_value = ctk.CTkLabel(control_section, text="1.0 A", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00ff88")
            self.current_value.pack(pady=(0, 10))

            self.current_slider = ctk.CTkSlider(
                control_section,
                from_=0.1,
                to=5.0,
                number_of_steps=49,
                command=self.on_current_change
            )
            self.current_slider.set(1.0)
            self.current_slider.pack(fill="x", pady=(0, 20))

        else:  # Batarya Testi
            # Batarya testi kontrolleri
            ctk.CTkLabel(control_section, text="Bitirme Voltajı (V):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(5, 0))
            self.cutoff_voltage_value = ctk.CTkLabel(control_section, text="9.0 V", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffaa00")
            self.cutoff_voltage_value.pack(pady=(0, 10))

            self.cutoff_voltage_slider = ctk.CTkSlider(
                control_section,
                from_=2.0,
                to=16.0,
                number_of_steps=140,
                command=self.on_cutoff_voltage_change
            )
            self.cutoff_voltage_slider.set(9.0)
            self.cutoff_voltage_slider.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(control_section, text="Deşarj Akımı (A):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(5, 0))
            self.discharge_current_value = ctk.CTkLabel(control_section, text="1.0 A", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ff4444")
            self.discharge_current_value.pack(pady=(0, 10))

            self.discharge_current_slider = ctk.CTkSlider(
                control_section,
                from_=0.1,
                to=5.0,
                number_of_steps=49,
                command=self.on_discharge_current_change
            )
            self.discharge_current_slider.set(1.0)
            self.discharge_current_slider.pack(fill="x", pady=(0, 20))

        # Butonlar
        button_frame = ctk.CTkFrame(control_section, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶ TESTİ BAŞLAT",
            command=self.start_test,
            fg_color="#00aa55",
            hover_color="#008844",
            height=40
        )
        self.start_btn.pack(fill="x", pady=5)

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹ DURDUR",
            command=self.stop_test,
            fg_color="#aa3333",
            hover_color="#882222",
            height=40,
            state="disabled"
        )
        self.stop_btn.pack(fill="x", pady=5)

        # Bağlantı kontrolü
        conn_frame = ctk.CTkFrame(control_section, fg_color="transparent")
        conn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            conn_frame,
            text="🏠 Ana Menü",
            command=self.restart_application,
            height=35
        ).pack(fill="x", pady=5)

        # GERÇEK ZAMANLI VERİ
        data_section = ctk.CTkFrame(left_panel, fg_color="#2a2a2a")
        data_section.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            data_section,
            text="CANLI VERİLER",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))

        # Veri göstergeleri
        self.voltage_display = self.create_data_display(data_section, "Gerilim", "--.-- V", "#ffaa00")
        self.current_display = self.create_data_display(data_section, "Akım", "--.-- A", "#00ff88")
        self.power_display = self.create_data_display(data_section, "Güç", "--.-- W", "#ff4444")
        self.capacity_display = self.create_data_display(data_section, "Kapasite", "--- mAh", "#8888ff")
        self.time_display = self.create_data_display(data_section, "Süre", "00:00", "#ff88ff")

        # GRAFİK ALANI
        graph_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a1a")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Matplotlib figure - 3 GRAFİK
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 10), facecolor='#1a1a1a')

        # Gerilim grafiği (0-20V)
        self.ax1.set_facecolor('#1a1a1a')
        self.voltage_line, = self.ax1.plot([], [], '#ffaa00', linewidth=2, label='Gerilim (V)')
        self.ax1.set_ylabel('Gerilim (V)', color='white')
        self.ax1.set_ylim(0, 20)
        self.ax1.tick_params(colors='white')
        self.ax1.legend(facecolor='#2a2a2a', edgecolor='#444444', labelcolor='white', loc='upper right')
        self.ax1.grid(True, alpha=0.2)

        # Akım grafiği (0-5A)
        self.ax2.set_facecolor('#1a1a1a')
        self.current_line, = self.ax2.plot([], [], '#00ff88', linewidth=2, label='Akım (A)')
        self.ax2.set_ylabel('Akım (A)', color='white')
        self.ax2.set_ylim(0, 5)
        self.ax2.tick_params(colors='white')
        self.ax2.legend(facecolor='#2a2a2a', edgecolor='#444444', labelcolor='white', loc='upper right')
        self.ax2.grid(True, alpha=0.2)

        # Güç grafiği (0-100W)
        self.ax3.set_facecolor('#1a1a1a')
        self.power_line, = self.ax3.plot([], [], '#ff4444', linewidth=2, label='Güç (W)')
        self.ax3.set_ylabel('Güç (W)', color='white')
        self.ax3.set_xlabel('Zaman (s)', color='white')
        self.ax3.set_ylim(0, 100)
        self.ax3.tick_params(colors='white')
        self.ax3.legend(facecolor='#2a2a2a', edgecolor='#444444', labelcolor='white', loc='upper right')
        self.ax3.grid(True, alpha=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Değişkenler
        self.test_start_time = 0
        self.is_test_running = False

        # Serial okuma thread'ini başlat
        self.start_serial_reading()

        # Grafik animasyonu
        self.animation = animation.FuncAnimation(self.fig, self.update_graph, interval=1000, cache_frame_data=False)

    def create_data_display(self, parent, title, value, color):
        """Veri göstergesi oluştur"""
        frame = ctk.CTkFrame(parent, fg_color="#333333")
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="#cccccc").pack(anchor="w", padx=10, pady=(5, 0))
        value_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
        value_label.pack(pady=(0, 5))

        return value_label

    def on_current_change(self, value):
        """Akım değeri değiştiğinde"""
        current = round(value, 2)
        self.current_value.configure(text=f"{current} A")

        if self.is_connected and self.ser:
            try:
                command = f"SET_CURRENT:{current}\n"
                self.ser.write(command.encode())
                print(f"📤 Akım ayarı: {current}A")
            except Exception as e:
                print(f"❌ Gönderme hatası: {e}")

    def on_cutoff_voltage_change(self, value):
        """Bitirme voltajı değiştiğinde"""
        voltage = round(value, 1)
        self.cutoff_voltage_value.configure(text=f"{voltage} V")

        if self.is_connected and self.ser:
            try:
                command = f"SET_CUTOFF_VOLTAGE:{voltage}\n"
                self.ser.write(command.encode())
                print(f"📤 Bitirme voltajı: {voltage}V")
            except Exception as e:
                print(f"❌ Gönderme hatası: {e}")

    def on_discharge_current_change(self, value):
        """Deşarj akımı değiştiğinde"""
        current = round(value, 2)
        self.discharge_current_value.configure(text=f"{current} A")

        if self.is_connected and self.ser:
            try:
                command = f"SET_DISCHARGE_CURRENT:{current}\n"
                self.ser.write(command.encode())
                print(f"📤 Deşarj akımı: {current}A")
            except Exception as e:
                print(f"❌ Gönderme hatası: {e}")

    def start_test(self):
        """Testi başlat"""
        if self.is_connected and self.ser:
            try:
                self.ser.write(b"START_TEST\n")
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                self.is_test_running = True
                self.test_start_time = time.time()
                print("📤 Test başlatıldı")
            except Exception as e:
                print(f"❌ Test başlatma hatası: {e}")

    def stop_test(self):
        """Testi durdur"""
        if self.is_connected and self.ser:
            try:
                self.ser.write(b"STOP_TEST\n")
                self.start_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                self.is_test_running = False
                print("📤 Test durduruldu")
            except Exception as e:
                print(f"❌ Test durdurma hatası: {e}")

    def start_serial_reading(self):
        """Serial veri okuma thread'ini başlat"""
        def read_serial():
            while self.is_connected and self.ser and self.ser.is_open:
                try:
                    if self.ser.in_waiting:
                        line = self.ser.readline().decode().strip()
                        print(f"📥 Gelen veri: {line}")
                        self.process_serial_data(line)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Okuma hatası: {e}")
                    break

        threading.Thread(target=read_serial, daemon=True).start()

    def process_serial_data(self, data):
        """Arduino'dan gelen veriyi işle"""
        try:
            if data.startswith("DATA:"):
                parts = data.split(":")
                if len(parts) >= 5:
                    voltage = float(parts[1])
                    current = float(parts[2])
                    power = float(parts[3])
                    capacity = float(parts[4])

                    # UI güncelle
                    self.voltage_display.configure(text=f"{voltage:.2f} V")
                    self.current_display.configure(text=f"{current:.2f} A")
                    self.power_display.configure(text=f"{power:.2f} W")
                    self.capacity_display.configure(text=f"{capacity:.0f} mAh")

                    # Süre güncelle
                    if self.is_test_running:
                        elapsed = int(time.time() - self.test_start_time)
                        minutes = elapsed // 60
                        seconds = elapsed % 60
                        self.time_display.configure(text=f"{minutes:02d}:{seconds:02d}")

                    # Veri kaydı
                    timestamp = time.time()
                    self.data_log.append({
                        'timestamp': timestamp,
                        'voltage': voltage,
                        'current': current,
                        'power': power,
                        'capacity': capacity
                    })

                    # 100 kayıttan sonra eski verileri temizle
                    if len(self.data_log) > 100:
                        self.data_log.pop(0)

        except ValueError as e:
            print(f"❌ Veri işleme hatası: {e}")

    def update_graph(self, frame):
        """Grafikleri güncelle"""
        if len(self.data_log) > 1:
            times = [entry['timestamp'] - self.data_log[0]['timestamp'] for entry in self.data_log]
            voltages = [entry['voltage'] for entry in self.data_log]
            currents = [entry['current'] for entry in self.data_log]
            powers = [entry['power'] for entry in self.data_log]

            # Son 50 veriyi göster
            self.voltage_line.set_data(times[-50:], voltages[-50:])
            self.current_line.set_data(times[-50:], currents[-50:])
            self.power_line.set_data(times[-50:], powers[-50:])

            # Eksenleri ayarla
            for ax in [self.ax1, self.ax2, self.ax3]:
                ax.relim()
                ax.autoscale_view()
                # Y ekseni limitlerini koru
                if ax == self.ax1:
                    ax.set_ylim(0, 20)
                elif ax == self.ax2:
                    ax.set_ylim(0, 5)
                elif ax == self.ax3:
                    ax.set_ylim(0, 100)

            self.canvas.draw()

    def restart_application(self):
        """Uygulamayı yeniden başlat"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()
        app = ElectronicLoadController()
        app.mainloop()

if __name__ == "__main__":
    app = ElectronicLoadController()
    app.mainloop()
