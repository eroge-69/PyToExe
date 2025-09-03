import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import time
import json
import threading

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sağlık İzleme Uygulaması")
        self.root.geometry("1000x700")
        
        # Veri depolama dizileri
        self.timestamps = []
        self.heart_rates = []
        self.spo2_values = []
        self.health_scores = []
        self.stress_levels = []
        
        # Seri port bağlantısı
        self.ser = None
        self.connected = False
        self.is_running = True
        
        # Arayüzü oluştur
        self.setup_ui()
        
        # Sağlık parametreleri
        self.normal_hr_min = 60
        self.normal_hr_max = 100
        self.normal_spo2_min = 95
        
        # Veri toplama işlemini başlat
        self.start_data_collection()
        
    def setup_ui(self):
        # Ana çerçeveler
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Bağlantı bilgileri
        ttk.Label(left_frame, text="HC-06 Bağlantı Ayarları", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Label(left_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.port_var = tk.StringVar()
        port_combo = ttk.Combobox(left_frame, textvariable=self.port_var, width=15)
        port_combo.grid(row=1, column=1, pady=2)
        
        # Mevcut portları listele
        ports = [port.device for port in serial.tools.list_ports.comports()]
        port_combo['values'] = ports
        if ports:
            port_combo.current(0)
        
        ttk.Label(left_frame, text="Baud Rate:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.baud_var = tk.StringVar(value="9600")
        baud_combo = ttk.Combobox(left_frame, textvariable=self.baud_var, width=15)
        baud_combo['values'] = ('9600', '19200', '38400', '57600', '115200')
        baud_combo.grid(row=2, column=1, pady=2)
        
        self.connect_btn = ttk.Button(left_frame, text="Bağlan", command=self.toggle_connection)
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Veri görüntüleme
        ttk.Label(left_frame, text="Son Ölçümler", font=('Arial', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=(20, 5))
        
        ttk.Label(left_frame, text="Nabız (BPM):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.hr_label = ttk.Label(left_frame, text="--", foreground="red", font=('Arial', 14, 'bold'))
        self.hr_label.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(left_frame, text="SpO2 (%):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.spo2_label = ttk.Label(left_frame, text="--", foreground="blue", font=('Arial', 14, 'bold'))
        self.spo2_label.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(left_frame, text="Sağlık Skoru:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.health_label = ttk.Label(left_frame, text="--", foreground="green", font=('Arial', 14, 'bold'))
        self.health_label.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(left_frame, text="Stres Seviyesi:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.stress_label = ttk.Label(left_frame, text="--", foreground="purple", font=('Arial', 14, 'bold'))
        self.stress_label.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # Durum göstergesi
        ttk.Label(left_frame, text="Durum:", font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky=tk.W, pady=(20, 2))
        self.status_label = ttk.Label(left_frame, text="Bağlantı bekleniyor", foreground="orange")
        self.status_label.grid(row=9, column=1, sticky=tk.W, pady=(20, 2))
        
        # Grafikler için sağ frame
        self.setup_plots(right_frame)
        
        # Kontrol butonları
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Rapor Oluştur", command=self.generate_report).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Verileri Temizle", command=self.clear_data).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Verileri Kaydet", command=self.save_data_to_file).grid(row=0, column=2, padx=5)
        
    def setup_plots(self, parent):
        # Matplotlib figürü ve grafikleri oluştur
        self.fig = Figure(figsize=(10, 8), dpi=100)
        
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        self.setup_plot_axes()
        
        # Canvas oluştur
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_plot_axes(self):
        # Nabız grafiği
        self.ax1.set_title('Nabız (BPM)')
        self.ax1.set_ylabel('BPM')
        self.ax1.set_ylim(40, 180)
        self.hr_line, = self.ax1.plot([], [], 'r-', label='Nabız')
        self.ax1.legend(loc='upper right')
        self.ax1.grid(True)
        
        # SpO2 grafiği
        self.ax2.set_title('SpO2 (%)')
        self.ax2.set_ylabel('%')
        self.ax2.set_ylim(80, 100)
        self.spo2_line, = self.ax2.plot([], [], 'b-', label='SpO2')
        self.ax2.legend(loc='upper right')
        self.ax2.grid(True)
        
        # Sağlık skoru grafiği
        self.ax3.set_title('Sağlık Skoru')
        self.ax3.set_ylabel('Puan')
        self.ax3.set_ylim(0, 100)
        self.health_line, = self.ax3.plot([], [], 'g-', label='Sağlık Skoru')
        self.ax3.legend(loc='upper right')
        self.ax3.grid(True)
        
        # Stres seviyesi grafiği
        self.ax4.set_title('Stres Seviyesi')
        self.ax4.set_ylabel('Seviye')
        self.ax4.set_ylim(0, 10)
        self.stress_line, = self.ax4.plot([], [], 'm-', label='Stres Seviyesi')
        self.ax4.legend(loc='upper right')
        self.ax4.grid(True)
        
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    def toggle_connection(self):
        if not self.connected:
            self.connect_bluetooth()
        else:
            self.disconnect_bluetooth()
    
    def connect_bluetooth(self):
        port = self.port_var.get()
        baud_rate = int(self.baud_var.get())
        
        if not port:
            messagebox.showerror("Hata", "Lütfen bir port seçin")
            return
        
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            self.connected = True
            self.connect_btn.config(text="Bağlantıyı Kes")
            self.status_label.config(text="Bağlantı kuruldu", foreground="green")
            print(f"Bağlantı başarılı: {port}")
        except Exception as e:
            messagebox.showerror("Bağlantı Hatası", f"Port açılamadı: {str(e)}")
    
    def disconnect_bluetooth(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        self.connect_btn.config(text="Bağlan")
        self.status_label.config(text="Bağlantı kesildi", foreground="red")
    
    def parse_data(self, data):
        try:
            # Farklı veri formatlarını işle
            data = data.decode('utf-8').strip()
            
            # Örnek formatlar: 
            # "HR:75,SPO2:98"
            # "Pulse:80,O2:97"
            # "BPM:72,SpO2:96"
            
            hr = None
            spo2 = None
            
            if 'HR:' in data and 'SPO2:' in data:
                parts = data.split(',')
                for part in parts:
                    if 'HR:' in part:
                        hr = int(part.split(':')[1])
                    elif 'SPO2:' in part:
                        spo2 = int(part.split(':')[1])
            elif 'Pulse:' in data and 'O2:' in data:
                parts = data.split(',')
                for part in parts:
                    if 'Pulse:' in part:
                        hr = int(part.split(':')[1])
                    elif 'O2:' in part:
                        spo2 = int(part.split(':')[1])
            elif 'BPM:' in data and 'SpO2:' in data:
                parts = data.split(',')
                for part in parts:
                    if 'BPM:' in part:
                        hr = int(part.split(':')[1])
                    elif 'SpO2:' in part:
                        spo2 = int(part.split(':')[1])
            
            return hr, spo2
        except Exception as e:
            print(f"Veri ayrıştırma hatası: {e}")
            return None, None
    
    def calculate_health_score(self, hr, spo2):
        if hr is None or spo2 is None:
            return 0, 0
            
        # Nabız puanı (60-100 arası ideal)
        hr_score = 100 - abs(hr - 80) * 0.5  # 80 BPM ideal kabul edildi
        hr_score = max(0, min(100, hr_score))
        
        # SpO2 puanı (%95-100 arası ideal)
        spo2_score = max(0, min(100, (spo2 - 90) * 10))  # %90 altı 0, %100 üstü 100
        
        # Genel sağlık puanı (ağırlıklı ortalama)
        health_score = int(hr_score * 0.4 + spo2_score * 0.6)
        
        # Stres seviyesi (1-10 arası)
        stress_level = 0
        if hr > 100 or spo2 < 95:
            stress_level = min(10, max(1, int((hr - 100) / 5 + (95 - spo2))))
        
        return health_score, stress_level
    
    def update_ui(self):
        if not self.connected or not self.heart_rates:
            return
            
        # Son değerleri göster
        last_hr = self.heart_rates[-1]
        last_spo2 = self.spo2_values[-1]
        last_health = self.health_scores[-1]
        last_stress = self.stress_levels[-1]
        
        self.hr_label.config(text=f"{last_hr}")
        self.spo2_label.config(text=f"{last_spo2}")
        self.health_label.config(text=f"{last_health}")
        self.stress_label.config(text=f"{last_stress}")
        
        # Grafikleri güncelle
        time_window = [t - self.timestamps[0] for t in self.timestamps] if self.timestamps else []
        
        self.hr_line.set_data(time_window, self.heart_rates)
        self.spo2_line.set_data(time_window, self.spo2_values)
        self.health_line.set_data(time_window, self.health_scores)
        self.stress_line.set_data(time_window, self.stress_levels)
        
        # Eksen sınırlarını ayarla
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            if time_window:
                ax.set_xlim(0, max(time_window))
            else:
                ax.set_xlim(0, 10)
        
        self.canvas.draw()
    
    def read_serial_data(self):
        while self.is_running:
            if self.connected and self.ser and self.ser.in_waiting > 0:
                try:
                    data = self.ser.readline()
                    hr, spo2 = self.parse_data(data)
                    
                    if hr is not None and spo2 is not None:
                        current_time = time.time()
                        
                        # Verileri kaydet
                        self.timestamps.append(current_time)
                        self.heart_rates.append(hr)
                        self.spo2_values.append(spo2)
                        
                        # Son 300 veri noktasını tut (5 dakika, 1/sn)
                        if len(self.timestamps) > 300:
                            self.timestamps = self.timestamps[-300:]
                            self.heart_rates = self.heart_rates[-300:]
                            self.spo2_values = self.spo2_values[-300:]
                        
                        # Sağlık skoru ve stres seviyesini hesapla
                        health_score, stress_level = self.calculate_health_score(hr, spo2)
                        self.health_scores.append(health_score)
                        self.stress_levels.append(stress_level)
                        
                        if len(self.health_scores) > 300:
                            self.health_scores = self.health_scores[-300:]
                            self.stress_levels = self.stress_levels[-300:]
                        
                        # UI'yı güncelle
                        self.root.after(0, self.update_ui)
                except Exception as e:
                    print(f"Veri okuma hatası: {e}")
                    self.root.after(0, lambda: self.status_label.config(text=f"Hata: {str(e)}", foreground="red"))
            
            time.sleep(0.1)  # CPU kullanımını azaltmak için
    
    def start_data_collection(self):
        # Seri port verilerini okumak için ayrı bir thread başlat
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
    
    def generate_report(self):
        if not self.health_scores:
            messagebox.showinfo("Bilgi", "Rapor oluşturmak için yeterli veri yok")
            return
            
        avg_hr = np.mean(self.heart_rates)
        avg_spo2 = np.mean(self.spo2_values)
        avg_health = np.mean(self.health_scores)
        avg_stress = np.mean(self.stress_levels)
        
        report = f"""
        SAĞLIK RAPORU
        --------------
        Toplam Ölçüm Sayısı: {len(self.heart_rates)}
        Ölçüm Süresi: {self.timestamps[-1] - self.timestamps[0]:.1f} saniye
        
        Ortalama Nabız: {avg_hr:.1f} BPM
        Ortalama SpO2: {avg_spo2:.1f}%
        Ortalama Sağlık Skoru: {avg_health:.1f}/100
        Ortalama Stres Seviyesi: {avg_stress:.1f}/10
        
        Son Ölçüm:
        - Nabız: {self.heart_rates[-1]} BPM
        - SpO2: {self.spo2_values[-1]}%
        - Sağlık Skoru: {self.health_scores[-1]}/100
        - Stres Seviyesi: {self.stress_levels[-1]}/10
        """
        
        if avg_health > 80:
            report += "\nGenel sağlık durumu: İYİ"
        elif avg_health > 60:
            report += "\nGenel sağlık durumu: ORTA"
        else:
            report += "\nGenel sağlık durumu: DÜŞÜK - Doktora danışmanız önerilir"
        
        # Raporu göster
        report_window = tk.Toplevel(self.root)
        report_window.title("Sağlık Raporu")
        report_window.geometry("500x400")
        
        text_area = tk.Text(report_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, report)
        text_area.config(state=tk.DISABLED)
        
        ttk.Button(report_window, text="Kapat", command=report_window.destroy).pack(pady=10)
    
    def clear_data(self):
        self.timestamps.clear()
        self.heart_rates.clear()
        self.spo2_values.clear()
        self.health_scores.clear()
        self.stress_levels.clear()
        self.update_ui()
        messagebox.showinfo("Bilgi", "Veriler temizlendi")
    
    def save_data_to_file(self):
        if not self.heart_rates:
            messagebox.showinfo("Bilgi", "Kaydedilecek veri yok")
            return
            
        filename = f"health_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w') as f:
                f.write("Timestamp,Nabız(BPM),SpO2(%),Sağlık Skoru,Stres Seviyesi\n")
                for i in range(len(self.heart_rates)):
                    ts = datetime.fromtimestamp(self.timestamps[i]).strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"{ts},{self.heart_rates[i]},{self.spo2_values[i]},{self.health_scores[i]},{self.stress_levels[i]}\n")
            
            messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına kaydedildi")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
    
    def on_closing(self):
        self.is_running = False
        self.disconnect_bluetooth()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()