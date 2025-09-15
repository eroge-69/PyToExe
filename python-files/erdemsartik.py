import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta

class ErdemSartikApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ERDEM SARTIK Uygulaması")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")
        
        # Renk şeması
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "background": "#f0f0f0",
            "text": "#2c3e50"
        }
        
        # Basit kullanıcı veritabanı (gerçek uygulamada şifreler hash'lenmelidir)
        self.users = {
            "erdem": "sartik",
            "admin": "admin123",
            "user": "password"
        }
        
        self.create_login_screen()
        
    def create_login_screen(self):
        self.login_frame = tk.Frame(self.root, bg=self.colors["background"])
        self.login_frame.pack(fill="both", expand=True)
        
        # Başlık
        title_label = tk.Label(
            self.login_frame, 
            text="ERDEM SARTIK", 
            font=("Arial", 16, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["background"]
        )
        title_label.pack(pady=20)
        
        # Kullanıcı adı
        tk.Label(
            self.login_frame, 
            text="Kullanıcı Adı:", 
            fg=self.colors["text"],
            bg=self.colors["background"]
        ).pack(pady=5)
        
        self.username_entry = tk.Entry(self.login_frame, width=25)
        self.username_entry.pack(pady=5)
        
        # Şifre
        tk.Label(
            self.login_frame, 
            text="Şifre:", 
            fg=self.colors["text"],
            bg=self.colors["background"]
        ).pack(pady=5)
        
        self.password_entry = tk.Entry(self.login_frame, width=25, show="*")
        self.password_entry.pack(pady=5)
        
        # Giriş butonu
        login_btn = tk.Button(
            self.login_frame, 
            text="Giriş Yap", 
            command=self.check_login,
            bg=self.colors["primary"], 
            fg="white", 
            width=15
        )
        login_btn.pack(pady=20)
        
        # Giriş bilgileri
        info_text = "Demo Kullanıcıları:\n- erdem / sartik\n- admin / admin123\n- user / password"
        info_label = tk.Label(
            self.login_frame, 
            text=info_text,
            fg=self.colors["text"],
            bg=self.colors["background"],
            justify="left"
        )
        info_label.pack(pady=10)
        
    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.users and self.users[username] == password:
            self.login_frame.destroy()
            self.create_main_interface()
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre!")
        
    def create_main_interface(self):
        # Notebook (sekmeler) oluştur
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sekmeleri oluştur
        self.create_time_difference_tab(notebook)
        self.create_ninety_days_tab(notebook)
        self.create_notes_tab(notebook)
        
        # Çıkış butonu
        exit_btn = tk.Button(
            self.root, 
            text="Çıkış", 
            command=self.root.quit,
            bg=self.colors["accent"], 
            fg="white", 
            width=10
        )
        exit_btn.pack(pady=10)
        
    def create_time_difference_tab(self, notebook):
        # Zaman farkı sekmesi
        time_frame = ttk.Frame(notebook, padding=10)
        notebook.add(time_frame, text="Zaman Farkı Hesaplama")
        
        # Başlangıç tarihi
        tk.Label(time_frame, text="Başlangıç Tarihi (GG/AA/YYYY SS:DD):", 
                fg=self.colors["text"]).grid(row=0, column=0, sticky="w", pady=5)
        self.start_entry = tk.Entry(time_frame, width=25)
        self.start_entry.grid(row=0, column=1, pady=5)
        self.start_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        # Bitiş tarihi
        tk.Label(time_frame, text="Bitiş Tarihi (GG/AA/YYYY SS:DD):", 
                fg=self.colors["text"]).grid(row=1, column=0, sticky="w", pady=5)
        self.end_entry = tk.Entry(time_frame, width=25)
        self.end_entry.grid(row=1, column=1, pady=5)
        self.end_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        # Hesapla butonu
        calc_btn = tk.Button(time_frame, text="Hesapla", command=self.calculate_time_difference,
                            bg=self.colors["primary"], fg="white", width=15)
        calc_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Sonuç alanı
        self.result_text = scrolledtext.ScrolledText(time_frame, width=40, height=10, wrap=tk.WORD)
        self.result_text.grid(row=3, column=0, columnspan=2, pady=10)
        
    def create_ninety_days_tab(self, notebook):
        # 90 gün kontrol sekmesi
        days_frame = ttk.Frame(notebook, padding=10)
        notebook.add(days_frame, text="90 Gün Kontrol")
        
        tk.Label(days_frame, text="Kontrol Edilecek Tarih (GG/AA/YYYY):", 
                fg=self.colors["text"]).grid(row=0, column=0, sticky="w", pady=5)
        self.check_date_entry = tk.Entry(days_frame, width=25)
        self.check_date_entry.grid(row=0, column=1, pady=5)
        self.check_date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Kontrol butonu
        check_btn = tk.Button(days_frame, text="Kontrol Et", command=self.check_ninety_days,
                             bg=self.colors["secondary"], fg="white", width=15)
        check_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Sonuç etiketi
        self.check_result = tk.Label(days_frame, text="", fg=self.colors["text"], wraplength=300)
        self.check_result.grid(row=2, column=0, columnspan=2, pady=10)
        
    def create_notes_tab(self, notebook):
        # Notlar sekmesi
        notes_frame = ttk.Frame(notebook, padding=10)
        notebook.add(notes_frame, text="Notlar")
        
        # Not giriş alanı
        self.notes_text = scrolledtext.ScrolledText(notes_frame, width=40, height=15, wrap=tk.WORD)
        self.notes_text.pack(pady=5)
        
        # Buton çerçevesi
        button_frame = tk.Frame(notes_frame)
        button_frame.pack(pady=10)
        
        # Kaydet butonu
        save_btn = tk.Button(button_frame, text="Notu Kaydet", command=self.save_note,
                            bg=self.colors["accent"], fg="white", width=12)
        save_btn.pack(side="left", padx=5)
        
        # Notları yükle butonu
        load_btn = tk.Button(button_frame, text="Notları Yükle", command=self.load_notes,
                            bg=self.colors["primary"], fg="white", width=12)
        load_btn.pack(side="left", padx=5)
        
    def calculate_time_difference(self):
        try:
            start_str = self.start_entry.get()
            end_str = self.end_entry.get()
            
            start_date = datetime.strptime(start_str, "%d/%m/%Y %H:%M")
            end_date = datetime.strptime(end_str, "%d/%m/%Y %H:%M")
            
            difference = end_date - start_date
            
            # Toplam saniye cinsinden fark
            total_seconds = difference.total_seconds()
            
            # Zaman birimlerine ayır
            days = difference.days
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Sonuçları formatla
            result = f"Toplam Fark:\n"
            result += f"{days} gün, {int(hours)} saat, {int(minutes)} dakika, {int(seconds)} saniye\n\n"
            
            result += f"Detaylı Hesaplama:\n"
            result += f"- Toplam dakika: {total_seconds / 60:.2f}\n"
            result += f"- Toplam saat: {total_seconds / 3600:.2f}\n"
            result += f"- Toplam gün: {total_seconds / 86400:.2f}\n"
            
            # Geçen veya kalan süre
            if total_seconds > 0:
                result += f"\nGeçen süre: {days} gün, {int(hours)} saat"
            else:
                result += f"\nKalan süre: {abs(days)} gün, {abs(int(hours))} saat"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tarihleri doğru formatta giriniz (GG/AA/YYYY SS:DD)")
    
    def check_ninety_days(self):
        try:
            check_date_str = self.check_date_entry.get()
            check_date = datetime.strptime(check_date_str, "%d/%m/%Y")
            current_date = datetime.now()
            
            # 90 gün öncesini hesapla
            ninety_days_ago = current_date - timedelta(days=90)
            
            if check_date < ninety_days_ago:
                self.check_result.config(
                    text=f"UYARI: {check_date.strftime('%d/%m/%Y')} tarihi, 90 günden daha eskidir!\n"
                         f"90 gün öncesi: {ninety_days_ago.strftime('%d/%m/%Y')}",
                    fg="red"
                )
            else:
                days_remaining = (check_date + timedelta(days=90) - current_date).days
                self.check_result.config(
                    text=f"{check_date.strftime('%d/%m/%Y')} tarihi 90 günü aşmamıştır.\n"
                         f"90 gün dolmasına {days_remaining} gün kaldı.",
                    fg="green"
                )
                
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tarihi doğru formatta giriniz (GG/AA/YYYY)")
    
    def save_note(self):
        note = self.notes_text.get(1.0, tk.END).strip()
        if note:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            with open("notlar.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}]\n{note}\n\n")
            messagebox.showinfo("Başarılı", "Notunuz kaydedildi!")
            self.notes_text.delete(1.0, tk.END)
        else:
            messagebox.showwarning("Uyarı", "Kaydedilecek not bulunamadı!")
    
    def load_notes(self):
        try:
            with open("notlar.txt", "r", encoding="utf-8") as f:
                notes = f.read()
            
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(tk.END, notes)
        except FileNotFoundError:
            messagebox.showinfo("Bilgi", "Henüz kaydedilmiş not bulunamadı.")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ErdemSartikApp()
    app.run()