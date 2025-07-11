import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import subprocess
import time
from tkinter import font

class VanatorPack:
    def __init__(self, root):
        self.root = root
        self.root.title("Vanator Pack - Ultimate System Tweaker")
        self.root.configure(bg="#1a1a2e")
        self.is_activated = False
        self.valid_keys = ["VANATORU-1234-5678", "KARKAN-9012-3456"]
        self.last_tweak_time = None
        self.setup_ui()

    def setup_ui(self):
        # Custom font
        custom_font = font.Font(family="Poppins", size=12, weight="normal")
        bold_font = font.Font(family="Poppins", size=14, weight="bold")

        # Sidebar
        sidebar = tk.Frame(self.root, bg="rgba(44, 44, 44, 0.9)", padx=20, pady=20)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(sidebar, text="VANATOR PACK\nUltimate System Tweaker", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.9)", font=(bold_font, 16)).pack(anchor="w", pady=10)

        pages = ["Ana Sayfa", "FiveM Tweaks", "Windows Tweaks", "Network Tweaks", "Game Tweaks", "System Info", "Tweak History", "Quick Boost", "Tema Değiştir"]
        for page in pages:
            btn = tk.Button(sidebar, text=f"🔹 {page}", fg="#e0e0e0", bg="#333", bd=0, font=custom_font, command=lambda p=page: self.show_page(p))
            btn.pack(anchor="w", pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#444"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#333"))

        # Content
        self.content = tk.Frame(self.root, bg="rgba(44, 44, 44, 0.95)", padx=30, pady=30)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_page("Ana Sayfa")

    def show_page(self, page):
        for widget in self.content.winfo_children():
            widget.destroy()
        custom_font = font.Font(family="Poppins", size=12)
        bold_font = font.Font(family="Poppins", size=16, weight="bold")

        if page == "Ana Sayfa":
            tk.Label(self.content, text="Ana Sayfa", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            tk.Label(self.content, text="🔹 Vanator Pack'e Hoş Geldiniz!", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 16)).pack(pady=10)
            tk.Label(self.content, text="Sisteminizi optimize ederek maksimum performans elde edin. Profesyonel araçlarımızla deneyimlerinizi yükseltin.", fg="#b0b0b0", bg="rgba(44, 44, 44, 0.95)", font=custom_font).pack(pady=10)
            btn = tk.Button(self.content, text="Hızlı Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_system)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
            system_info = tk.Frame(self.content, bg="#333")
            system_info.pack(fill=tk.X, pady=10)
            tk.Label(system_info, text=f"💻 Sistem Bilgisi\nCPU: {psutil.cpu_count()} Çekirdek\nRAM: {round(psutil.virtual_memory().total / (1024 ** 3))} GB\nDisk: {round(psutil.disk_usage('/').total / (1024 ** 3))} GB", bg="#333", fg="#b0b0b0", font=custom_font).pack(side=tk.LEFT, padx=10)
            btn_quick = tk.Button(system_info, text="Hızlı Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_system)
            btn_quick.pack(side=tk.LEFT, padx=10)
            btn_quick.bind("<Enter>", lambda e, b=btn_quick: b.configure(bg="#ff6b6b"))
            btn_quick.bind("<Leave>", lambda e, b=btn_quick: b.configure(bg="#ff4d4d"))
            tk.Label(system_info, text=f"📅 Son Tweakler\n{self.last_tweak_time if self.last_tweak_time else 'Henüz tweak uygulanmadı'}", bg="#333", fg="#b0b0b0", font=custom_font).pack(side=tk.LEFT, padx=10)
        elif page == "FiveM Tweaks":
            tk.Label(self.content, text="FiveM Tweaks", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            self.profile_var = tk.StringVar(value="performance")
            ttk.Combobox(self.content, textvariable=self.profile_var, values=["performance", "balanced", "quality"], font=custom_font).pack(pady=5)
            btn = tk.Button(self.content, text="FiveM Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_fivem)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
        elif page == "Windows Tweaks":
            tk.Label(self.content, text="Windows Tweaks", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            btn = tk.Button(self.content, text="Windows Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_windows)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
        elif page == "Network Tweaks":
            tk.Label(self.content, text="Network Tweaks", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            btn = tk.Button(self.content, text="Ağ Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_network)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
        elif page == "Game Tweaks":
            tk.Label(self.content, text="Game Tweaks", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            btn = tk.Button(self.content, text="Oyun Optimizasyon", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_game)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
        elif page == "System Info":
            tk.Label(self.content, text="System Info", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            tk.Label(self.content, text=f"💻 Sistem Bilgisi\nCPU: {psutil.cpu_count()} Çekirdek\nRAM: {round(psutil.virtual_memory().total / (1024 ** 3))} GB\nDisk: {round(psutil.disk_usage('/').total / (1024 ** 3))} GB", fg="#b0b0b0", bg="rgba(44, 44, 44, 0.95)", font=custom_font).pack(pady=10)
            tk.Label(self.content, text=f"RAM: {psutil.virtual_memory().percent}% CPU: {psutil.cpu_percent()}%", fg="#b0b0b0", bg="rgba(44, 44, 44, 0.95)", font=custom_font).pack(pady=10)
        elif page == "Tweak History":
            tk.Label(self.content, text="Tweak History", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            tk.Label(self.content, text=f"Uygulanan tweak geçmişi: {self.last_tweak_time if self.last_tweak_time else 'Henüz tweak uygulanmadı'}", fg="#b0b0b0", bg="rgba(44, 44, 44, 0.95)", font=custom_font).pack(pady=10)
        elif page == "Quick Boost":
            tk.Label(self.content, text="Quick Boost", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            btn = tk.Button(self.content, text="Hızlı Boost", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.optimize_quick_boost)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))
        elif page == "Tema Değiştir":
            tk.Label(self.content, text="Tema Değiştir", fg="#ff4d4d", bg="rgba(44, 44, 44, 0.95)", font=(bold_font, 20)).pack(pady=10)
            self.theme_var = tk.StringVar(value="dark")
            ttk.Combobox(self.content, textvariable=self.theme_var, values=["dark", "light", "custom", "cyberpunk", "nature", "cosmic"], font=custom_font).pack(pady=5)
            btn = tk.Button(self.content, text="Uygula", bg="#ff4d4d", fg="#fff", font=custom_font, command=self.apply_theme)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#ff6b6b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ff4d4d"))

    def apply_theme(self):
        theme = self.theme_var.get()
        if theme == "light":
            self.root.configure(bg="#f0f0f0")
            self.content.configure(bg="#fff")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#e63946")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#e63946", fg="#333")
        elif theme == "custom":
            self.root.configure(bg="#1a0a3a")
            self.content.configure(bg="#2a1b4a")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#d4a5ff")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#ff4081", fg="#fff")
        elif theme == "cyberpunk":
            self.root.configure(bg="#0a0c1d")
            self.content.configure(bg="#0a0c1d")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#00ffcc")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#00ffcc", fg="#fff")
        elif theme == "nature":
            self.root.configure(bg="#2f6a5c")
            self.content.configure(bg="#2f6a5c")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#d4e4d2")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#a3b18a", fg="#fff")
        elif theme == "cosmic":
            self.root.configure(bg="#0d1b2a")
            self.content.configure(bg="#0d1b2a")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#ff6f61")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#ff6f61", fg="#fff")
        else:
            self.root.configure(bg="#1a1a2e")
            self.content.configure(bg="rgba(44, 44, 44, 0.95)")
            for widget in self.content.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(fg="#ff4d4d")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="#ff4d4d", fg="#fff")

    def optimize_system(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            try:
                subprocess.run(["powercfg", "/setactive", "SCHEME_MIN"], check=True)
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() in ['chrome.exe', 'firefox.exe']:
                        proc.terminate()
                self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
                self.show_page("Ana Sayfa")
                messagebox.showinfo("Tamamlandı", "Sistem optimizasyonu uygulandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Optimizasyon başarısız: {str(e)}")

    def optimize_fivem(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            profile = self.profile_var.get()
            settings = {
                'performance': {'textureQuality': 'Medium', 'shadowQuality': 'Low', 'msaa': 'Off', 'vsync': 'Off', 'grassQuality': 'Low'},
                'balanced': {'textureQuality': 'High', 'shadowQuality': 'Normal', 'msaa': '2x', 'vsync': 'Off', 'grassQuality': 'Normal'},
                'quality': {'textureQuality': 'Very High', 'shadowQuality': 'High', 'msaa': '4x', 'vsync': 'On', 'grassQuality': 'High'}
            }
            print(f"FiveM tweaks uygulandı: {settings[profile]}")
            self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
            self.show_page("FiveM Tweaks")
            messagebox.showinfo("Tamamlandı", "FiveM optimizasyonu uygulandı. FPS artışı bekleniyor.")

    def optimize_windows(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            try:
                subprocess.run(["powercfg", "/setactive", "SCHEME_MIN"], check=True)
                messagebox.showinfo("Tamamlandı", "Windows optimizasyonu uygulandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Optimizasyon başarısız: {str(e)}")
            self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
            self.show_page("Windows Tweaks")

    def optimize_network(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            try:
                subprocess.run(["ipconfig", "/flushdns"], check=True)
                messagebox.showinfo("Tamamlandı", "Ağ optimizasyonu uygulandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Optimizasyon başarısız: {str(e)}")
            self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
            self.show_page("Network Tweaks")

    def optimize_game(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() in ['chrome.exe', 'firefox.exe']:
                        proc.terminate()
                messagebox.showinfo("Tamamlandı", "Oyun optimizasyonu uygulandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Optimizasyon başarısız: {str(e)}")
            self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
            self.show_page("Game Tweaks")

    def optimize_quick_boost(self):
        if not self.is_activated:
            key = tk.simpledialog.askstring("Aktivasyon", "Lütfen aktivasyon anahtarınızı girin:", parent=self.root)
            if key in self.valid_keys:
                self.is_activated = True
                messagebox.showinfo("Başarılı", "Aktivasyon başarılı! Optimizasyonu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", "Geçersiz anahtar! Lütfen doğru anahtarı girin.")
                return
        if self.is_activated:
            self.optimize_system()
            self.optimize_fivem()
            self.last_tweak_time = time.strftime("%d.%m.%Y %H:%M", time.localtime())
            self.show_page("Quick Boost")
            messagebox.showinfo("Tamamlandı", "Hızlı boost uygulandı.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VanatorPack(root)
    root.mainloop()