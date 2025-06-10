from math import sqrt
import tkinter as tk
from tkinter import ttk, messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asenkron Motor ve Elektrikli Isıtıcı Sigorta Hesaplama")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Stil ayarları
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"), background="#e0e0e0")
        
        # Ana çerçeve
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        header = ttk.Label(self.main_frame, text="Asenkron Motor ve Elektrikli Isıtıcı Sigorta Hesaplama", 
                          style="Header.TLabel")
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Marka/Model girişi
        brand_frame = ttk.Frame(self.main_frame)
        brand_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(brand_frame, text="Marka/Model:").pack(side=tk.LEFT, padx=(0, 10))
        self.brand_entry = ttk.Entry(brand_frame, width=40)
        self.brand_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.brand_entry.insert(0, "Giriniz: ...")
        
        # Cihaz tipi seçimi
        device_frame = ttk.LabelFrame(self.main_frame, text="Cihaz Tipi Seçimi")
        device_frame.pack(fill=tk.X, pady=10)
        
        self.device_type = tk.StringVar(value="1")
        devices = [
            ("Monofaze Asenkron Motor", "1"),
            ("Trifaze Asenkron Motor", "2"),
            ("Monofaze Elektrikli Isıtıcı", "3"),
            ("Trifaze Elektrikli Isıtıcı", "4")
        ]
        
        for i, (text, value) in enumerate(devices):
            rb = ttk.Radiobutton(device_frame, text=text, variable=self.device_type, 
                                value=value)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
        
        # Hesaplama tipi seçimi
        calc_frame = ttk.LabelFrame(self.main_frame, text="Hesaplama Türü")
        calc_frame.pack(fill=tk.X, pady=10)
        
        self.calc_type = tk.StringVar(value="1")
        ttk.Radiobutton(calc_frame, text="Güç Hesaplama", variable=self.calc_type, 
                       value="1").pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Radiobutton(calc_frame, text="Akım Hesaplama (Sigorta Seçimi)", 
                       variable=self.calc_type, value="2").pack(side=tk.LEFT, padx=20, pady=5)
        
        # Parametreler girişi
        self.param_frame = ttk.LabelFrame(self.main_frame, text="Parametreler")
        self.param_frame.pack(fill=tk.X, pady=10)
        
        # Parametre etiketleri ve giriş alanları
        self.params = {}
        param_labels = ["Akım (A)", "Güç Faktörü (cosφ)", "Çalışma Gerilimi (V)", "Güç (kW)"]
        
        for i, label in enumerate(param_labels):
            frame = ttk.Frame(self.param_frame)
            frame.grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            ttk.Label(frame, text=label, width=20).pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=15)
            entry.pack(side=tk.LEFT)
            self.params[label] = entry
        
        # Sonuç alanı
        result_frame = ttk.LabelFrame(self.main_frame, text="Hesaplama Sonuçları")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=8, font=("Arial", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.result_text.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Hesapla", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Temizle", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Çıkış", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Altbilgi
        footer = ttk.Label(self.main_frame, 
                          text="Created by Yigit GURLER - +90 543 947 82 96", 
                          font=("Arial", 9))
        footer.pack(side=tk.BOTTOM, pady=10)
        
        # Başlangıçta parametreleri güncelle
        self.update_parameters()
        self.device_type.trace_add("write", lambda *args: self.update_parameters())
        self.calc_type.trace_add("write", lambda *args: self.update_parameters())
    
    def update_parameters(self):
        """Seçilen cihaz ve hesaplama tipine göre parametreleri günceller"""
        device = self.device_type.get()
        calc_type = self.calc_type.get()
        
        # Tüm parametreleri gizle
        for label in self.params:
            self.params[label].master.grid_remove()
        
        # Güç hesaplama için parametreler
        if calc_type == "1":
            if device in ["1", "2"]:  # Motorlar
                self.params["Akım (A)"].master.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Güç Faktörü (cosφ)"].master.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Çalışma Gerilimi (V)"].master.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
            else:  # Isıtıcılar
                self.params["Akım (A)"].master.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Çalışma Gerilimi (V)"].master.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        # Akım hesaplama için parametreler
        else:
            if device in ["1", "2"]:  # Motorlar
                self.params["Güç (kW)"].master.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Güç Faktörü (cosφ)"].master.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Çalışma Gerilimi (V)"].master.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
            else:  # Isıtıcılar
                self.params["Güç (kW)"].master.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
                self.params["Çalışma Gerilimi (V)"].master.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    
    def get_float_value(self, entry, param_name):
        """Giriş alanından float değer alır, hata kontrolü yapar"""
        value = entry.get().strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            messagebox.showerror("Hata", f"Geçersiz {param_name} değeri: {value}")
            return None
    
    def calculate(self):
        """Hesaplama işlemlerini yürütür"""
        # Marka/model bilgisi
        brand_model = self.brand_entry.get().strip()
        if not brand_model:
            messagebox.showwarning("Uyarı", "Lütfen marka/model bilgisini giriniz")
            return
        
        device = self.device_type.get()
        calc_type = self.calc_type.get()
        
        # Sonuç metnini hazırla
        result = f"Marka/Model: {brand_model}\n"
        
        # Güç hesaplama
        if calc_type == "1":
            if device == "1":  # Monofaze motor
                i = self.get_float_value(self.params["Akım (A)"], "akım")
                cosFi = self.get_float_value(self.params["Güç Faktörü (cosφ)"], "güç faktörü")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [i, cosFi, U]:
                    return
                
                P = (U * i * cosFi) / 1000
                result += f"Monofaze Asenkron Motor Güç Hesaplama:\n"
                result += f"Akım: {i} A, Güç Faktörü: {cosFi}, Gerilim: {U} V\n"
                result += f"Hesaplanan Güç: {P:.2f} kW"
            
            elif device == "2":  # Trifaze motor
                i = self.get_float_value(self.params["Akım (A)"], "akım")
                cosFi = self.get_float_value(self.params["Güç Faktörü (cosφ)"], "güç faktörü")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [i, cosFi, U]:
                    return
                
                P = (sqrt(3) * U * i * cosFi) / 1000
                result += f"Trifaze Asenkron Motor Güç Hesaplama:\n"
                result += f"Akım: {i} A, Güç Faktörü: {cosFi}, Gerilim: {U} V\n"
                result += f"Hesaplanan Güç: {P:.2f} kW"
            
            elif device == "3":  # Monofaze ısıtıcı
                i = self.get_float_value(self.params["Akım (A)"], "akım")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [i, U]:
                    return
                
                P = (U * i) / 1000
                result += f"Monofaze Elektrikli Isıtıcı Güç Hesaplama:\n"
                result += f"Akım: {i} A, Gerilim: {U} V\n"
                result += f"Hesaplanan Güç: {P:.2f} kW"
            
            elif device == "4":  # Trifaze ısıtıcı
                i = self.get_float_value(self.params["Akım (A)"], "akım")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [i, U]:
                    return
                
                P = (sqrt(3) * U * i) / 1000
                result += f"Trifaze Elektrikli Isıtıcı Güç Hesaplama:\n"
                result += f"Akım: {i} A, Gerilim: {U} V\n"
                result += f"Hesaplanan Güç: {P:.2f} kW"
        
        # Akım hesaplama
        else:
            if device == "1":  # Monofaze motor
                P = self.get_float_value(self.params["Güç (kW)"], "güç")
                cosFi = self.get_float_value(self.params["Güç Faktörü (cosφ)"], "güç faktörü")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [P, cosFi, U]:
                    return
                
                i = (P * 1000) / (U * cosFi)
                result += f"Monofaze Asenkron Motor Akım Hesaplama:\n"
                result += f"Güç: {P} kW, Güç Faktörü: {cosFi}, Gerilim: {U} V\n"
                result += f"Hesaplanan Akım: {i:.2f} A\n\n"
                result += self.get_fuse_recommendation(i, "monofaze_motor")
            
            elif device == "2":  # Trifaze motor
                P = self.get_float_value(self.params["Güç (kW)"], "güç")
                cosFi = self.get_float_value(self.params["Güç Faktörü (cosφ)"], "güç faktörü")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [P, cosFi, U]:
                    return
                
                i = (P * 1000) / (sqrt(3) * U * cosFi)
                result += f"Trifaze Asenkron Motor Akım Hesaplama:\n"
                result += f"Güç: {P} kW, Güç Faktörü: {cosFi}, Gerilim: {U} V\n"
                result += f"Hesaplanan Akım: {i:.2f} A\n\n"
                result += self.get_fuse_recommendation(i, "trifaze_motor")
            
            elif device == "3":  # Monofaze ısıtıcı
                P = self.get_float_value(self.params["Güç (kW)"], "güç")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [P, U]:
                    return
                
                i = (P * 1000) / U
                result += f"Monofaze Elektrikli Isıtıcı Akım Hesaplama:\n"
                result += f"Güç: {P} kW, Gerilim: {U} V\n"
                result += f"Hesaplanan Akım: {i:.2f} A\n\n"
                result += self.get_fuse_recommendation(i, "monofaze_heater")
            
            elif device == "4":  # Trifaze ısıtıcı
                P = self.get_float_value(self.params["Güç (kW)"], "güç")
                U = self.get_float_value(self.params["Çalışma Gerilimi (V)"], "gerilim")
                
                if None in [P, U]:
                    return
                
                i = (P * 1000) / (sqrt(3) * U)
                result += f"Trifaze Elektrikli Isıtıcı Akım Hesaplama:\n"
                result += f"Güç: {P} kW, Gerilim: {U} V\n"
                result += f"Hesaplanan Akım: {i:.2f} A\n\n"
                result += self.get_fuse_recommendation(i, "trifaze_heater")
        
        # Sonuçları göster
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)
    
    def get_fuse_recommendation(self, current, device_type):
        """Akım değerine göre uygun sigorta önerisini döndürür"""
        fuse_ranges = [
            (1, 3), (2, 4), (4, 6), (7, 10), (10, 13), (13, 16), 
            (17, 20), (22, 25), (29, 32), (37, 40), (47, 50), 
            (54, 63), (72, 80), (92, 100), (114, 125)
        ]
        
        # Cihaz tipine göre sigorta özellikleri
        if device_type == "monofaze_motor":
            fuse_type = "Tek kutup, C tipi"
        elif device_type == "trifaze_motor":
            fuse_type = "3 kutup, C tipi"
        elif device_type == "monofaze_heater":
            fuse_type = "Tek kutup, B tipi"
        elif device_type == "trifaze_heater":
            fuse_type = "3 kutup, B tipi"
        else:
            fuse_type = "Uygun tip"
        
        # Uygun sigortayı bul
        fuse_value = None
        for max_current, fuse in fuse_ranges:
            if current < max_current:
                fuse_value = fuse
                break
        
        if fuse_value is None:
            fuse_value = 125
        
        return f"Önerilen Sigorta: {fuse_type}, {fuse_value}A"
    
    def clear_form(self):
        """Formu temizler"""
        self.brand_entry.delete(0, tk.END)
        
        for entry in self.params.values():
            entry.delete(0, tk.END)
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        self.device_type.set("1")
        self.calc_type.set("1")
        self.update_parameters()

if __name__ == "__main__":
    app = App()
    app.mainloop()