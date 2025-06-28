import math
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class HeatExchangerCalculator:
    """Isı değiştiricisi hesaplamaları için ana sınıf"""
    
    @staticmethod
    def calculate_lmtd(t_hot_in, t_hot_out, t_cold_in, t_cold_out):
        """Logaritmik Ortalama Sıcaklık Farkı (LMTD) hesaplama"""
        # Sıcak uç ve soğuk uç sıcaklık farklarını hesapla
        dt_hot = t_hot_in - t_cold_out
        dt_cold = t_hot_out - t_cold_in
        
        # Geçersiz değerleri kontrol et
        if dt_hot <= 0 or dt_cold <= 0:
            raise ValueError("Sıcaklık farkları pozitif olmalıdır. Akış düzenini kontrol edin.")
        
        # Eğer sıcaklık farkları eşitse
        if abs(dt_hot - dt_cold) < 1e-6:
            return dt_hot
        
        # LMTD formülü
        try:
            lmtd = (dt_hot - dt_cold) / math.log(dt_hot / dt_cold)
            return abs(lmtd)
        except (ZeroDivisionError, ValueError) as e:
            raise ValueError(f"LMTD hesaplama hatası: {str(e)}")
    
    @staticmethod
    def calculate_heat_transfer_rate(U, A, lmtd):
        """Isı transfer hızı hesaplama: Q = U * A * LMTD"""
        if U <= 0 or A <= 0 or lmtd <= 0:
            raise ValueError("U, A ve LMTD değerleri pozitif olmalıdır.")
        return U * A * lmtd
    
    @staticmethod
    def validate_temperatures(t_hot_in, t_hot_out, t_cold_in, t_cold_out):
        """Sıcaklık değerlerinin mantıklılığını kontrol et"""
        errors = []
        
        if t_hot_in <= t_hot_out:
            errors.append("Sıcak akışkan giriş sıcaklığı çıkış sıcaklığından yüksek olmalıdır.")
        
        if t_cold_out <= t_cold_in:
            errors.append("Soğuk akışkan çıkış sıcaklığı giriş sıcaklığından yüksek olmalıdır.")
        
        if t_hot_out <= t_cold_in:
            errors.append("Sıcak akışkan çıkış sıcaklığı soğuk akışkan giriş sıcaklığından yüksek olmalıdır.")
        
        if t_hot_in <= t_cold_out:
            errors.append("Sıcak akışkan giriş sıcaklığı soğuk akışkan çıkış sıcaklığından yüksek olmalıdır.")
        
        return errors

class HeatExchangerGUI:
    """Isı değiştiricisi hesaplayıcısı GUI sınıfı"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Isı Değiştiricisi Hesaplayıcısı v2.0")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Hesaplanan değerleri sakla
        self.last_U = None
        self.last_lmtd = None
        self.last_A = None
        self.last_Q = None
        
        self.setup_gui()
        self.set_default_values()
    
    def setup_gui(self):
        """GUI bileşenlerini oluştur"""
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Isı Değiştiricisi Hesaplayıcısı", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Giriş parametreleri bölümü
        input_frame = ttk.LabelFrame(main_frame, text="Giriş Parametreleri", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.create_input_fields(input_frame)
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.calc_button = ttk.Button(button_frame, text="Hesapla", 
                                     command=self.calculate, width=15)
        self.calc_button.grid(row=0, column=0, padx=5)
        
        self.plot_button = ttk.Button(button_frame, text="Grafik Göster", 
                                     command=self.show_plot, width=15)
        self.plot_button.grid(row=0, column=1, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Temizle", 
                                      command=self.clear_results, width=15)
        self.clear_button.grid(row=0, column=2, padx=5)
        
        # Sonuçlar bölümü
        result_frame = ttk.LabelFrame(main_frame, text="Hesaplama Sonuçları", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.result_text = tk.Text(result_frame, height=15, width=80, wrap=tk.WORD,
                                  font=('Courier', 10))
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Grid ağırlıkları
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def create_input_fields(self, parent):
        """Giriş alanlarını oluştur"""
        fields = [
            ("Sıcak Akışkan Giriş Sıcaklığı (°C):", "t_hot_in"),
            ("Sıcak Akışkan Çıkış Sıcaklığı (°C):", "t_hot_out"),
            ("Soğuk Akışkan Giriş Sıcaklığı (°C):", "t_cold_in"),
            ("Soğuk Akışkan Çıkış Sıcaklığı (°C):", "t_cold_out"),
            ("Toplam Isı Transfer Katsayısı U (W/m²·K):", "U"),
            ("Yüzey Alanı A (m²):", "A")
        ]
        
        self.entries = {}
        
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(parent, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=3)
            
            entry = ttk.Entry(parent, width=20, font=('Arial', 10))
            entry.grid(row=i, column=1, padx=(10, 0), pady=3)
            self.entries[var_name] = entry
    
    def set_default_values(self):
        """Varsayılan değerleri ayarla"""
        defaults = {
            "t_hot_in": "120",
            "t_hot_out": "80",
            "t_cold_in": "40",
            "t_cold_out": "70",
            "U": "250",
            "A": "1.0"
        }
        
        for var_name, value in defaults.items():
            self.entries[var_name].insert(0, value)
    
    def get_input_values(self):
        """Giriş değerlerini al ve doğrula"""
        try:
            values = {}
            for var_name, entry in self.entries.items():
                value = entry.get().strip()
                if not value:
                    raise ValueError(f"{var_name} alanı boş bırakılamaz.")
                values[var_name] = float(value)
            return values
        except ValueError as e:
            raise ValueError(f"Geçersiz giriş: {str(e)}")
    
    def calculate(self):
        """Ana hesaplama fonksiyonu"""
        try:
            # Giriş değerlerini al
            values = self.get_input_values()
            
            # Sıcaklık değerlerini doğrula
            temp_errors = HeatExchangerCalculator.validate_temperatures(
                values["t_hot_in"], values["t_hot_out"], 
                values["t_cold_in"], values["t_cold_out"]
            )
            
            if temp_errors:
                error_msg = "Sıcaklık değerleri hatalı:\n" + "\n".join(f"• {error}" for error in temp_errors)
                messagebox.showerror("Giriş Hatası", error_msg)
                return
            
            # LMTD hesapla
            lmtd = HeatExchangerCalculator.calculate_lmtd(
                values["t_hot_in"], values["t_hot_out"],
                values["t_cold_in"], values["t_cold_out"]
            )
            
            # Isı transfer hızını hesapla
            Q = HeatExchangerCalculator.calculate_heat_transfer_rate(
                values["U"], values["A"], lmtd
            )
            
            # Sonuçları sakla
            self.last_U = values["U"]
            self.last_lmtd = lmtd
            self.last_A = values["A"]
            self.last_Q = Q
            
            # Sonuçları göster
            self.display_results(values, lmtd, Q)
            
        except ValueError as e:
            messagebox.showerror("Hesaplama Hatası", str(e))
        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"Bir hata oluştu: {str(e)}")
    
    def display_results(self, values, lmtd, Q):
        """Sonuçları metin alanında göster"""
        result_text = f"""
{'='*60}
                ISI DEĞİŞTİRİCİSİ HESAPLAMA SONUÇLARI
{'='*60}

GİRİŞ PARAMETRELERİ:
{'-'*40}
Sıcak Akışkan Giriş Sıcaklığı    : {values['t_hot_in']:8.1f} °C
Sıcak Akışkan Çıkış Sıcaklığı    : {values['t_hot_out']:8.1f} °C
Soğuk Akışkan Giriş Sıcaklığı    : {values['t_cold_in']:8.1f} °C
Soğuk Akışkan Çıkış Sıcaklığı    : {values['t_cold_out']:8.1f} °C
Toplam Isı Transfer Katsayısı    : {values['U']:8.1f} W/m²·K
Yüzey Alanı                      : {values['A']:8.2f} m²

HESAPLAMA SONUÇLARI:
{'-'*40}
Logaritmik Ortalama Sıcaklık Farkı (LMTD) : {lmtd:8.2f} K
Isı Transfer Hızı (Q)                      : {Q:8.2f} W
Isı Akısı (q)                              : {Q/values['A']:8.2f} W/m²

EK BİLGİLER:
{'-'*40}
Sıcak Uç Sıcaklık Farkı (ΔT₁)    : {values['t_hot_in'] - values['t_cold_out']:8.2f} K
Soğuk Uç Sıcaklık Farkı (ΔT₂)    : {values['t_hot_out'] - values['t_cold_in']:8.2f} K
Ortalama Sıcaklık Farkı          : {(values['t_hot_in'] - values['t_cold_out'] + values['t_hot_out'] - values['t_cold_in'])/2:8.2f} K

FORMÜL: Q = U × A × LMTD = {values['U']} × {values['A']} × {lmtd:.2f} = {Q:.2f} W

{'='*60}
"""
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
    
    def show_plot(self):
        """Q vs A grafiğini göster"""
        if self.last_U is None:
            messagebox.showwarning("Veri Yok", "Önce hesaplama yapınız!")
            return
        
        try:
            self.generate_plot()
        except Exception as e:
            messagebox.showerror("Grafik Hatası", f"Grafik oluşturulurken hata: {str(e)}")
    
    def generate_plot(self):
        """Q vs A grafiğini oluştur"""
        # Alan değerleri (0.1'den 20 m²'ye kadar)
        areas = [i * 0.1 for i in range(1, 201)]  # 0.1, 0.2, ..., 20.0
        heat_rates = [self.last_U * area * self.last_lmtd for area in areas]
        
        plt.figure(figsize=(12, 8))
        
        # Ana grafik
        plt.plot(areas, heat_rates, 'b-', linewidth=2, label='Q = U × A × LMTD')
        
        # Mevcut nokta
        plt.plot(self.last_A, self.last_Q, 'ro', markersize=10, 
                label=f'Hesaplanan Nokta (A={self.last_A:.2f} m², Q={self.last_Q:.0f} W)')
        
        # Dikey ve yatay çizgiler
        plt.axvline(x=self.last_A, color='r', linestyle='--', alpha=0.7)
        plt.axhline(y=self.last_Q, color='r', linestyle='--', alpha=0.7)
        
        plt.title('Isı Transfer Hızı - Yüzey Alanı İlişkisi', fontsize=16, fontweight='bold')
        plt.xlabel('Yüzey Alanı A (m²)', fontsize=12)
        plt.ylabel('Isı Transfer Hızı Q (W)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        
        # Grafik formatını iyileştir
        plt.tight_layout()
        
        # Türkçe karakterler için font ayarı
        plt.rcParams['font.family'] = ['DejaVu Sans']
        
        plt.show()
    
    def clear_results(self):
        """Sonuçları temizle"""
        self.result_text.delete(1.0, tk.END)
        self.last_U = None
        self.last_lmtd = None
        self.last_A = None
        self.last_Q = None

def run_test():
    """Test hesaplaması çalıştır"""
    print("\n" + "="*60)
    print("                    TEST HESAPLAMASI")
    print("="*60)
    
    # Test verileri
    test_data = {
        "t_hot_in": 120,
        "t_hot_out": 80,
        "t_cold_in": 40,
        "t_cold_out": 70,
        "U": 250,
        "A": 1.0
    }
    
    try:
        # Sıcaklıkları doğrula
        temp_errors = HeatExchangerCalculator.validate_temperatures(
            test_data["t_hot_in"], test_data["t_hot_out"],
            test_data["t_cold_in"], test_data["t_cold_out"]
        )
        
        if temp_errors:
            print("HATA: Sıcaklık değerleri geçersiz!")
            for error in temp_errors:
                print(f"  • {error}")
            return
        
        # LMTD hesapla
        lmtd = HeatExchangerCalculator.calculate_lmtd(
            test_data["t_hot_in"], test_data["t_hot_out"],
            test_data["t_cold_in"], test_data["t_cold_out"]
        )
        
        # Isı transfer hızını hesapla
        Q = HeatExchangerCalculator.calculate_heat_transfer_rate(
            test_data["U"], test_data["A"], lmtd
        )
        
        # Sonuçları yazdır
        print(f"\nGiriş Parametreleri:")
        print(f"  T_hot_in  = {test_data['t_hot_in']} °C")
        print(f"  T_hot_out = {test_data['t_hot_out']} °C")
        print(f"  T_cold_in = {test_data['t_cold_in']} °C")
        print(f"  T_cold_out= {test_data['t_cold_out']} °C")
        print(f"  U         = {test_data['U']} W/m²·K")
        print(f"  A         = {test_data['A']} m²")
        
        print(f"\nSonuçlar:")
        print(f"  LMTD      = {lmtd:.2f} K")
        print(f"  Q         = {Q:.2f} W")
        print(f"  q         = {Q/test_data['A']:.2f} W/m²")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"HATA: {e}")

def main():
    """Ana fonksiyon"""
    print("Isı Değiştiricisi Hesaplayıcısı v2.0")
    print("="*40)
    print("1. Test hesaplaması çalıştır")
    print("2. GUI uygulamasını aç")
    print("3. Çıkış")
    
    while True:
        try:
            choice = input("\nSeçiminizi yapın (1-3): ").strip()
            
            if choice == "1":
                run_test()
                break
            elif choice == "2":
                print("GUI açılıyor...")
                root = tk.Tk()
                app = HeatExchangerGUI(root)
                root.mainloop()
                break
            elif choice == "3":
                print("Program sonlandırıldı.")
                sys.exit(0)
            else:
                print("Geçersiz seçim! Lütfen 1, 2 veya 3 girin.")
                
        except KeyboardInterrupt:
            print("\n\nProgram kullanıcı tarafından sonlandırıldı.")
            sys.exit(0)
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()