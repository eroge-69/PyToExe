
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta

KULLANICI_ADI = "gulleci1903"
SIFRE = "YS3GP4BR8B4000085"

class ServisUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Servis Uygulaması")
        self.root.geometry("700x500")
        self.giris_ekrani()

    def giris_ekrani(self):
        self.temizle()
        tk.Label(self.root, text="Kullanıcı Adı:").pack(pady=5)
        self.kullanici_giris = tk.Entry(self.root)
        self.kullanici_giris.pack()

        tk.Label(self.root, text="Şifre:").pack(pady=5)
        self.sifre_giris = tk.Entry(self.root, show="*")
        self.sifre_giris.pack()

        tk.Button(self.root, text="Giriş Yap", command=self.dogrula).pack(pady=20)

    def dogrula(self):
        if (self.kullanici_giris.get() == KULLANICI_ADI and
            self.sifre_giris.get() == SIFRE):
            self.ana_menü()
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış.")

    def ana_menü(self):
        self.temizle()
        tk.Label(self.root, text="Servis Uygulaması", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Servis İşlemleri", command=self.servis_menusu, width=30).pack(pady=5)
        tk.Button(self.root, text="Garanti İşlemleri", command=self.garanti_menusu, width=30).pack(pady=5)
        tk.Button(self.root, text="Çıkış", command=self.root.quit, width=30).pack(pady=5)

    def servis_menusu(self):
        self.temizle()
        tk.Label(self.root, text="Servis İşlemleri", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Yeni Servis İşlemi Ekle", command=self.yeni_servis).pack(pady=5)
        tk.Button(self.root, text="Geriye Dönük İşlem Ekle", command=self.geriye_donuk).pack(pady=5)
        tk.Button(self.root, text="Serbest İşlem", command=self.serbest_islem).pack(pady=5)
        tk.Button(self.root, text="← Geri", command=self.ana_menü).pack(pady=20)

    def garanti_menusu(self):
        self.temizle()
        tk.Label(self.root, text="Garanti İşlemleri", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Garanti Ekle", command=self.garanti_ekle).pack(pady=5)
        tk.Button(self.root, text="Garanti Sorgula", command=self.garanti_sorgula).pack(pady=5)
        tk.Button(self.root, text="← Geri", command=self.ana_menü).pack(pady=20)

    def yeni_servis(self):
        self.temizle()
        tk.Label(self.root, text="Yeni Servis İşlemi", font=("Arial", 12)).pack(pady=10)
        self.servis_girdi_ekrani(tarih_otomatik=True)

    def geriye_donuk(self):
        self.temizle()
        tk.Label(self.root, text="Geriye Dönük Servis İşlemi", font=("Arial", 12)).pack(pady=10)
        self.servis_girdi_ekrani(tarih_otomatik=False)

    def servis_girdi_ekrani(self, tarih_otomatik=True):
        self.girdi_frame = tk.Frame(self.root)
        self.girdi_frame.pack()

        self.entries = {}
        for field in ["Ürün Tipi", "Marka", "Model", "Yapılan İşlem", "Seri Numarası"]:
            tk.Label(self.girdi_frame, text=field).pack()
            entry = tk.Entry(self.girdi_frame, width=50)
            entry.pack()
            self.entries[field] = entry

        if tarih_otomatik:
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tk.Label(self.girdi_frame, text="Tarih").pack()
            self.entries["Tarih"] = tk.Entry(self.girdi_frame, width=50)
            self.entries["Tarih"].insert(0, tarih_str)
            self.entries["Tarih"].config(state="disabled")
            self.entries["Tarih"].pack()
        else:
            tk.Label(self.girdi_frame, text="Tarih (GG-AA-YYYY)").pack()
            self.entries["Tarih"] = tk.Entry(self.girdi_frame, width=50)
            self.entries["Tarih"].pack()

        tk.Label(self.girdi_frame, text="Açıklama (max 3500 karakter)").pack()
        self.aciklama = tk.Text(self.girdi_frame, width=60, height=10)
        self.aciklama.pack()

        tk.Button(self.girdi_frame, text="Kaydet", command=self.kaydet_servis).pack(pady=10)
        tk.Button(self.girdi_frame, text="← Geri", command=self.servis_menusu).pack()

    def kaydet_servis(self):
        uzunluk = len(self.aciklama.get("1.0", "end-1c"))
        if uzunluk > 3500:
            messagebox.showwarning("Uyarı", "Açıklama 3500 karakteri geçemez!")
        else:
            messagebox.showinfo("Başarılı", "Servis kaydı başarıyla oluşturuldu.")

    def serbest_islem(self):
        self.temizle()
        tk.Label(self.root, text="Serbest İşlem", font=("Arial", 12)).pack(pady=10)
        self.serbest_yazi = tk.Text(self.root, width=80, height=20)
        self.serbest_yazi.pack()
        tk.Button(self.root, text="Kaydet", command=self.kaydet_serbest).pack(pady=10)
        tk.Button(self.root, text="← Geri", command=self.servis_menusu).pack()

    def kaydet_serbest(self):
        uzunluk = len(self.serbest_yazi.get("1.0", "end-1c"))
        if uzunluk > 3500:
            messagebox.showwarning("Uyarı", "Yazı 3500 karakteri geçemez!")
        else:
            messagebox.showinfo("Başarılı", "Serbest işlem kaydedildi.")

    def garanti_ekle(self):
        self.temizle()
        self.garanti_frame = tk.Frame(self.root)
        self.garanti_frame.pack()
        tk.Label(self.root, text="Garanti Ekle", font=("Arial", 12)).pack(pady=10)

        self.garanti_alanlar = {}
        for alan in ["Marka", "Model Kodu", "Seri No", "Başlangıç Tarihi (GG-AA-YYYY)", "Garanti Süresi (Ay)"]:
            tk.Label(self.garanti_frame, text=alan).pack()
            entry = tk.Entry(self.garanti_frame, width=50)
            entry.pack()
            self.garanti_alanlar[alan] = entry

        tk.Button(self.root, text="Kaydet", command=self.kaydet_garanti).pack(pady=10)
        tk.Button(self.root, text="← Geri", command=self.garanti_menusu).pack()

        self.garanti_veritabani = {}

    def kaydet_garanti(self):
        try:
            baslangic = datetime.strptime(self.garanti_alanlar["Başlangıç Tarihi (GG-AA-YYYY)"].get(), "%d-%m-%Y")
            sure = int(self.garanti_alanlar["Garanti Süresi (Ay)"].get())
            bitis = baslangic + timedelta(days=30*sure)
            key = (self.garanti_alanlar["Marka"].get(), self.garanti_alanlar["Model Kodu"].get(), self.garanti_alanlar["Seri No"].get())
            self.garanti_veritabani[key] = bitis.strftime("%d-%m-%Y")
            messagebox.showinfo("Başarılı", f"Garanti Bitiş Tarihi: {self.garanti_veritabani[key]}")
        except:
            messagebox.showerror("Hata", "Verileri kontrol edin.")

    def garanti_sorgula(self):
        self.temizle()
        self.sorgu_frame = tk.Frame(self.root)
        self.sorgu_frame.pack()
        tk.Label(self.root, text="Garanti Sorgula", font=("Arial", 12)).pack(pady=10)

        self.sorgu_entries = {}
        for field in ["Marka", "Model Kodu", "Seri No"]:
            tk.Label(self.sorgu_frame, text=field).pack()
            entry = tk.Entry(self.sorgu_frame, width=50)
            entry.pack()
            self.sorgu_entries[field] = entry

        tk.Button(self.root, text="Sorgula", command=self.sorgula_garanti).pack(pady=10)
        tk.Button(self.root, text="← Geri", command=self.garanti_menusu).pack()

    def sorgula_garanti(self):
        key = (self.sorgu_entries["Marka"].get(), self.sorgu_entries["Model Kodu"].get(), self.sorgu_entries["Seri No"].get())
        tarih = self.garanti_veritabani.get(key)
        if tarih:
            messagebox.showinfo("Garanti Bilgisi", f"Garanti Bitiş Tarihi: {tarih}")
        else:
            messagebox.showinfo("Sonuç", "KAYITLI ÜRÜN BULUNAMAMAKTADIR.")

    def temizle(self):
        for widget in self.root.winfo_children():
            widget.destroy()

root = tk.Tk()
app = ServisUygulamasi(root)
root.mainloop()
