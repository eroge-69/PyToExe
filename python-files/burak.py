import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
# pysnmp yerine puresnmp import ediyoruz
from puresnmp import get
 # PySnmpError, puresnmp'nin kendi hata sınıfıdır
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# SNMP sorgu fonksiyonunu puresnmp'ye göre güncelliyoruz
def snmp_get(ip, community, oid):
    try:
        # puresnmp.get fonksiyonu doğrudan IP, community ve OID alır
        # getCmd'deki gibi karmaşık argümanlar yerine basittir.
        # SNMP version 2c (community tabanlı) varsayılan olarak kullanılır.
        value = get(ip, community, oid)
        # Gelen değer genellikle byte string veya int/str olabilir.
        # Biz burada counter değerleri beklediğimiz için int'e çeviriyoruz.
        return int(value)
 
    except Exception as e:
        # print(f"Genel SNMP Hatası: {e}") # Diğer beklenmedik hatalar için
        return None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SNMP Trafik İzleyici")
        self.root.geometry("960x600")
        self.root.configure(bg="#f3f4f6")

        self.stop_event = threading.Event()
        self.monitoring = False

        style = ttk.Style()
        style.configure("TLabel", background="#f3f4f6", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))

        form_frame = ttk.Frame(root)
        form_frame.pack(pady=10)

        self._add_form_row(form_frame, "Switch IP:", "192.168.1.1", 0)
        self._add_form_row(form_frame, "Community:", "public", 1)
        self._add_form_row(form_frame, "Port Index:", "25", 2)
        self._add_form_row(form_frame, "Interval (s):", "1", 3)

        self.start_button = ttk.Button(form_frame, text="Başlat", command=self.start_monitoring)
        self.start_button.grid(row=0, column=4, rowspan=4, padx=10, ipadx=10, ipady=5, sticky="ns")

        self.fig, self.ax = plt.subplots(figsize=(9, 4))
        self.fig.patch.set_facecolor('#ffffff')
        self.ax.set_facecolor('#f9fafb')

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        self.x_data = []
        self.in_data = []
        self.out_data = []

    def _add_form_row(self, parent, label_text, default_val, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=4, sticky="e")
        entry = ttk.Entry(parent, width=18)
        entry.insert(0, default_val)
        entry.grid(row=row, column=1, padx=5, pady=4)
        if "IP" in label_text:
            self.ip_entry = entry
        elif "Community" in label_text:
            self.community_entry = entry
        elif "Port" in label_text:
            self.port_entry = entry
        elif "Interval" in label_text:
            self.interval_entry = entry

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.stop_event.clear()
            # Start and Stop button'u eklemek istersen burada start_button'ı disabled yapıp
            # bir stop_button'ı enabled yapabilirsin.
            threading.Thread(target=self.monitor_thread, daemon=True).start()

    def monitor_thread(self):
        ip = self.ip_entry.get()
        community = self.community_entry.get()
        try:
            port = int(self.port_entry.get())
            interval = float(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Port veya interval sayısal olmalı!")
            self.monitoring = False # Hata durumunda izlemeyi durdur
            return

        # OID'ler pysnmp ve puresnmp için aynı kalır
        in_oid = f'1.3.6.1.2.1.2.2.1.10.{port}'  # ifInOctets
        out_oid = f'1.3.6.1.2.1.2.2.1.16.{port}' # ifOutOctets

        prev_in = snmp_get(ip, community, in_oid)
        prev_out = snmp_get(ip, community, out_oid)
        last_time = time.time()

        if None in (prev_in, prev_out):
            messagebox.showerror("SNMP Hatası", "İlk SNMP sorgusu başarısız oldu. Cihaz kapalı olabilir veya SNMP ayarları yanlış.")
            self.monitoring = False
            return

        while self.monitoring and not self.stop_event.is_set():
            time.sleep(interval)
            curr_time = time.time()
            curr_in = snmp_get(ip, community, in_oid)
            curr_out = snmp_get(ip, community, out_oid)

            if None in (curr_in, curr_out):
                print("SNMP hatası: veri alınamadı. Sonraki döngüde tekrar denenecek.")
                # Hata mesajı gösterme, sadece konsola yazma, sürekli pop-up açmasını engellemek için
                continue

            dt = curr_time - last_time
            # Counter overflow'ları yönetmek için daha sağlam bir kod eklenebilir.
            # SNMP sayaçları 32 bit veya 64 bit olabilir ve belirli bir değere ulaştıklarında sıfırlanır.
            # Şu anki kod, sadece pozitif farkları doğru işler, resetlemeyi hesaba katmaz.
            # Ancak basit trafik izleme için genellikle yeterlidir.
            in_diff = curr_in - prev_in if curr_in >= prev_in else curr_in # Basit overflow yönetimi (sadece sıfırlama)
            out_diff = curr_out - prev_out if curr_out >= prev_out else curr_out # Basit overflow yönetimi

            # BPS (Bits per second) hesaplaması: (Byte farkı * 8 bit/Byte) / Zaman farkı (saniye)
            # Mbps'ye çevirmek için 1_000_000'e böleriz
            in_mbps = (in_diff * 8) / (dt * 1_000_000)
            out_mbps = (out_diff * 8) / (dt * 1_000_000)


            self.x_data.append(time.strftime("%H:%M:%S"))
            self.in_data.append(in_mbps)
            self.out_data.append(out_mbps)

            # Sadece son 60 veriyi tut
            if len(self.x_data) > 60:
                self.x_data.pop(0)
                self.in_data.pop(0)
                self.out_data.pop(0)

            prev_in, prev_out = curr_in, curr_out
            last_time = curr_time

            # Tkinter ana döngüsünde grafik güncelleme
            self.root.after(0, self.update_graph)

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.x_data, self.in_data, label="Giriş (Mbps)", color="#3B82F6", linewidth=2)
        self.ax.plot(self.x_data, self.out_data, label="Çıkış (Mbps)", color="#EF4444", linewidth=2)
        self.ax.set_title("Port Trafik İzleme (Son 60 sn)", fontsize=12, pad=10)
        self.ax.set_xlabel("Zaman")
        self.ax.set_ylabel("Mbps")
        self.ax.set_ylim(bottom=0)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.3)

        self.canvas.draw_idle()


# === UYGULAMA BAŞLAT ===
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    def on_closing():
        print("Kapatılıyor...")
        app.monitoring = False
        app.stop_event.set()
        # Thread'in tamamen durması için kısa bir süre bekle
        # Daemon thread olduğu için Python çıkışında otomatik kapanır, ama emin olmak için bu bir güvenlik önlemidir.
        time.sleep(0.3)
        root.destroy()
        sys.exit(0) # Programdan tamamen çık

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()