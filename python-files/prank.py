import tkinter as tk
import time
import random

DURATION_LOGS_MS = 30_000   # 30 sn log akışı
BLACKOUT_MS      = 5_000    # 5 sn siyah ekran
END_HOLD_MS      = 2_000    # JOKE yazısından sonra bekleme

FAKE_LOGS = [
    "Veriler aktarılıyor...",
    "Sistem dosyaları taranıyor...",
    "IP adresleri eşleştiriliyor...",
    "Güvenlik duvarı konfigürasyonu okunuyor...",
    "Anahtar değişimi başlatıldı...",
    "Paketler şifreleniyor...",
    "Checksum doğrulanıyor...",
    "Portlar dinleniyor...",
    "Kernel modülleri analiz ediliyor...",
    "Bellek snapshot'ı oluşturuluyor...",
    "GPU hızlandırma etkin...",
    "Veri tüneli kuruldu...",
    "Proxy katmanı devrede...",
    "Kimlik doğrulama atlandı...",
    "Parmak izi cache’i güncelleniyor...",
]

SPINNER = ["|", "/", "-", "\\"]

class PrankApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Console")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.config(cursor="none")  # İmleç gizle

        # Klavye: tüm tuşları yut, sadece Esc çalışsın
        self.root.bind_all("<Key>", self.block_keys, add="+")
        self.root.bind_all("<Escape>", lambda e: self.safe_close(), add="+")

        # Fare: olayları yut (görsel olarak da imleç gizli)
        for seq in ("<Button>", "<Button-1>", "<Button-2>", "<Button-3>",
                    "<B1-Motion>", "<B2-Motion>", "<B3-Motion>",
                    "<Motion>", "<MouseWheel>"):
            self.root.bind_all(seq, self.block_mouse, add="+")

        # Başlık
        self.header = tk.Label(
            self.root, text=":: Secure Data Link ::",
            fg="#00ff96", bg="black", font=("Consolas", 20, "bold")
        )
        self.header.pack(anchor="nw", padx=16, pady=(12, 0))

        # “Terminal” alanı
        self.text = tk.Text(
            self.root, bg="black", fg="#00ff00",
            insertbackground="#00ff00",
            font=("Consolas", 14), bd=0, highlightthickness=0
        )
        self.text.pack(expand=True, fill="both", padx=16, pady=8)
        self.text.configure(state="disabled")

        # Alt durum satırı
        self.status = tk.Label(
            self.root, text="", fg="#00ff96", bg="black",
            font=("Consolas", 14)
        )
        self.status.pack(anchor="sw", padx=16, pady=(0, 12))

        # Sahte “sabit imleç” göstergesi (ekranda küçük bir nokta)
        self.fake_cursor = tk.Label(
            self.root, text="•", fg="#00ff96", bg="black",
            font=("Consolas", 18)
        )
        self.fake_cursor.place(relx=0.5, rely=0.5, anchor="center")  # ekranda ortada dursun

        self.log_timer = None
        self.spin_idx = 0
        self.progress = 0

        # Başlangıç mesajları
        self.print_line("Bağlantı başlatılıyor...")
        self.print_line("Yetkilendirme anahtarları yükleniyor...")
        self.print_line("Protokol: TLS-Accelerated QUIC/2")
        self.print_line("")
        self.schedule_next_log()

        # Süre dolunca blackout
        self.root.after(DURATION_LOGS_MS, self.start_blackout)

    # Tüm tuşları yut
    def block_keys(self, event):
        # Escape ayrı bağlandığı için burası çalışsa da kapanmayı engellemiyor
        return "break"

    # Tüm fare olaylarını yut
    def block_mouse(self, event):
        # Sahte imleci merkezde tut (gerçek sistem imleci görünmüyor)
        self.fake_cursor.place(relx=0.5, rely=0.5, anchor="center")
        return "break"

    def print_line(self, s):
        self.text.configure(state="normal")
        self.text.insert("end", s + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def schedule_next_log(self):
        # Spinner + ilerleme yüzdesi
        self.spin_idx = (self.spin_idx + 1) % len(SPINNER)
        self.progress = min(99, self.progress + random.randint(1, 3))
        self.status.config(text=f"[{SPINNER[self.spin_idx]}] Aktarım sürüyor... {self.progress}%")

        # Sahte log
        line = random.choice(FAKE_LOGS)
        self.print_line(f"{time.strftime('%H:%M:%S')}  {line}")

        # Hex dump benzeri satır
        if random.random() < 0.45:
            dump = " ".join(f"{random.randint(0,255):02X}" for _ in range(random.randint(8, 24)))
            self.print_line("   " + dump)

        # 60–140 ms arası değişken hız
        delay = random.randint(60, 140)
        self.log_timer = self.root.after(delay, self.schedule_next_log)

    def start_blackout(self):
        if self.log_timer:
            self.root.after_cancel(self.log_timer)
            self.log_timer = None

        # Tam siyah ekran
        for w in (self.header, self.text, self.status, self.fake_cursor):
            try:
                w.pack_forget()
            except:
                try:
                    w.place_forget()
                except:
                    pass
        self.root.configure(bg="black")

        # 5 sn sonra JOKE
        self.root.after(BLACKOUT_MS, self.show_joke)

    def show_joke(self):
        screen = tk.Frame(self.root, bg="black")
        screen.pack(expand=True, fill="both")

        lbl = tk.Label(screen, text="JOKE", fg="#ff4444", bg="black", font=("Consolas", 96, "bold"))
        lbl.pack(expand=True)

        sub = tk.Label(screen, text="Her şey yolunda 😅  (Esc ile çıkabilirsiniz)",
                       fg="#bbbbbb", bg="black", font=("Consolas", 18))
        sub.pack(pady=24)

        self.status.config(text="Aktarım tamamlandı: 100%")
        self.root.after(END_HOLD_MS, self.safe_close)

    def safe_close(self):
        try:
            if self.log_timer:
                self.root.after_cancel(self.log_timer)
        except:
            pass
        self.root.destroy()

def main():
    PrankApp().root.mainloop()

if __name__ == "__main__":
    main()
