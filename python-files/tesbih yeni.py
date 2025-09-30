import tkinter as tk
from tkinter import messagebox
import sqlite3
import math

class TesbihHesaplayiciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tesbih Üretim Takip ve Hesaplama Uygulaması")
        self.root.geometry("1200x800")

        # Veritabanı bağlantısı ve tablo oluşturma
        self.conn = sqlite3.connect('tesbih_verileri.db')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS uretim_kayitlari (
                id INTEGER PRIMARY KEY,
                is_adi TEXT,
                cubuk_boyu REAL,
                cubuk_sayisi INTEGER,
                boncuk_boyu REAL,
                boncuk_sayisi_bir_tesbih INTEGER,
                ara_tane_boyu REAL,
                ara_tane_sayisi_bir_tesbih INTEGER,
                pul_boyu REAL,
                pul_sayisi_bir_tesbih INTEGER,
                imame_boyu REAL,
                sikke_boyu REAL,
                dugum_boyu REAL,
                tepelik_boyu REAL,
                civi_boyu REAL,
                isimlik_boyu REAL,
                toplam_tesbih_adeti INTEGER,
                rapor_metni TEXT
            )
        ''')
        self.conn.commit()

        # Ana çerçeveler
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.list_frame = tk.Frame(self.main_frame, width=300, relief=tk.GROOVE, borderwidth=2)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.input_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # İş Listesi
        tk.Label(self.list_frame, text="Geçmiş İşler", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.is_listbox = tk.Listbox(self.list_frame, width=40, font=("Helvetica", 12))
        self.is_listbox.pack(fill=tk.Y, expand=True)
        self.is_listbox.bind('<<ListboxSelect>>', self.is_secildi)

        # Giriş Alanı Tablosu
        self.create_input_grid()

        # Sonuç Alanı
        self.result_label = tk.Label(self.input_frame, text="Sonuç:", font=("Helvetica", 20, "bold"))
        self.result_label.grid(row=20, column=0, columnspan=2, pady=20, sticky="w")

        self.report_label = tk.Label(self.input_frame, text="Çubuk Dağıtım Raporu:", font=("Helvetica", 12, "bold"), justify=tk.LEFT)
        self.report_label.grid(row=22, column=0, columnspan=2, pady=(10, 5), sticky="w")

        self.report_text = tk.Text(self.input_frame, height=15, width=70, font=("Courier", 12))
        self.report_text.grid(row=23, column=0, columnspan=2, sticky="ew")
        
        # Düğmeler
        self.button_frame = tk.Frame(self.input_frame)
        self.button_frame.grid(row=24, column=0, columnspan=2, pady=10)

        self.hesapla_button = tk.Button(self.button_frame, text="Hesapla ve Kaydet", command=self.hesapla_ve_kaydet, font=("Helvetica", 14), bg="#4CAF50", fg="white", relief="flat")
        self.hesapla_button.pack(side=tk.LEFT, padx=10)
        
        self.temizle_button = tk.Button(self.button_frame, text="Alanları Temizle", command=self.alanlari_temizle, font=("Helvetica", 14), bg="#F44336", fg="white", relief="flat")
        self.temizle_button.pack(side=tk.LEFT, padx=10)
        
        self.delete_button = tk.Button(self.button_frame, text="Seçili Kaydı Sil", command=self.kaydi_sil, font=("Helvetica", 14), bg="#FF5722", fg="white", relief="flat")
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        self.listeyi_guncelle()

    def create_input_grid(self):
        self.entries = {}
        input_data = [
            ("İş Adı:", "is_adi"),
            ("Çubuk Boyu (mm):", "cubuk_boyu"),
            ("Toplam Çubuk Sayısı:", "cubuk_sayisi"),
            ("Boncuk Boyu (mm):", "boncuk_boyu"),
            ("1 Tesbih İçin Boncuk Sayısı:", "boncuk_sayisi_bir_tesbih"),
            ("Ara Tane Boyu (mm):", "ara_tane_boyu"),
            ("1 Tesbih İçin Ara Tane Sayısı:", "ara_tane_sayisi_bir_tesbih"),
            ("Pul Boyu (mm):", "pul_boyu"),
            ("1 Tesbih İçin Pul Sayısı:", "pul_sayisi_bir_tesbih"),
            ("İmame Boyu (mm):", "imame_boyu"),
            ("Sikke Boyu (mm):", "sikke_boyu"),
            ("Düğümlük Boyu (mm):", "dugum_boyu"),
            ("Tepelik Boyu (mm):", "tepelik_boyu"),
            ("Çivi Boyu (mm):", "civi_boyu"),
            ("İsimlik Boyu (mm):", "isimlik_boyu")
        ]

        for i, (label_text, entry_key) in enumerate(input_data):
            row_num = i
            label = tk.Label(self.input_frame, text=label_text, font=("Helvetica", 12))
            label.grid(row=row_num, column=0, sticky="w", pady=2, padx=5)
            
            entry = tk.Entry(self.input_frame, font=("Helvetica", 12))
            entry.grid(row=row_num, column=1, sticky="ew", pady=2, padx=5)
            self.entries[entry_key] = entry
        
        self.input_frame.columnconfigure(1, weight=1)

    def hesapla_ve_kaydet(self):
        try:
            is_adi = self.entries["is_adi"].get()
            if not is_adi:
                messagebox.showerror("Hata", "Lütfen bir iş adı girin.")
                return

            data = {}
            for key in self.entries:
                val = self.entries[key].get().replace(',', '.')
                if not val:
                    val = "0"
                if key in ["is_adi"]:
                    data[key] = val
                elif key in ["cubuk_sayisi", "boncuk_sayisi_bir_tesbih", "ara_tane_sayisi_bir_tesbih", "pul_sayisi_bir_tesbih"]:
                    data[key] = int(val)
                else:
                    data[key] = float(val)

            cubuk_boyu = data["cubuk_boyu"]
            toplam_cubuk_sayisi = data["cubuk_sayisi"]
            
            parca_sayilari_bir_tesbih = {
                "boncuk": data["boncuk_sayisi_bir_tesbih"],
                "ara_tane": data["ara_tane_sayisi_bir_tesbih"],
                "pul": data["pul_sayisi_bir_tesbih"],
                "imame": 1, "sikke": 1, "dugum": 1, "tepelik": 1, "civi": 1, "isimlik": 1
            }

            toplam_cubuk_ihtiyaci = 0
            cubuk_ihtiyaclari_parca_basina = {}

            for parca in parca_sayilari_bir_tesbih:
                boy_key = f"{parca}_boyu"
                parca_boyu = data[boy_key]
                adet_bir_tesbih = parca_sayilari_bir_tesbih[parca]
                
                if parca_boyu > 0 and adet_bir_tesbih > 0:
                    adet_bir_cubuk = int(cubuk_boyu // parca_boyu)
                    if adet_bir_cubuk > 0:
                        cubuk_ihtiyaci = adet_bir_tesbih / adet_bir_cubuk
                        cubuk_ihtiyaclari_parca_basina[parca] = cubuk_ihtiyaci
                        toplam_cubuk_ihtiyaci += cubuk_ihtiyaci
                    else:
                        cubuk_ihtiyaclari_parca_basina[parca] = float('inf')
                else:
                    cubuk_ihtiyaclari_parca_basina[parca] = 0

            if toplam_cubuk_ihtiyaci == 0 or toplam_cubuk_sayisi == 0:
                 toplam_tam_tesbih = 0
            else:
                 toplam_tam_tesbih = math.floor(toplam_cubuk_sayisi / toplam_cubuk_ihtiyaci)

            # Raporlama
            rapor_metni = ""
            rapor_metni += f"Tahmini üretim: {toplam_tam_tesbih} adet TAM tesbih.\n\n"
            rapor_metni += "Çubuk Dağılımı:\n"
            
            toplam_kullanilan_cubuk = 0
            
            for parca in cubuk_ihtiyaclari_parca_basina:
                cubuk_ihtiyaci = cubuk_ihtiyaclari_parca_basina[parca]
                parca_boyu = data[f"{parca}_boyu"]
                
                if parca_boyu > 0 and cubuk_ihtiyaci > 0:
                    ayrilmasi_gereken_cubuk_sayisi = math.ceil(toplam_tam_tesbih * cubuk_ihtiyaci)
                    toplam_kullanilan_cubuk += ayrilmasi_gereken_cubuk_sayisi

                    adet_bir_cubuk = int(cubuk_boyu // parca_boyu)
                    toplam_elde_edilen_adet = ayrilmasi_gereken_cubuk_sayisi * adet_bir_cubuk
                    kullanilan_adet = toplam_tam_tesbih * parca_sayilari_bir_tesbih[parca]
                    
                    rapor_metni += f"- {parca.capitalize()}: {ayrilmasi_gereken_cubuk_sayisi} çubuk ({toplam_elde_edilen_adet} üretilecek, {kullanilan_adet} kullanılacak)\n"
                elif parca_boyu == 0:
                    rapor_metni += f"- {parca.capitalize()}: 0 çubuk\n"
            
            kalan_cubuk = toplam_cubuk_sayisi - toplam_kullanilan_cubuk
            rapor_metni += f"\nToplam {toplam_cubuk_sayisi} çubuktan {toplam_kullanilan_cubuk} adeti kullanıldı. {kalan_cubuk} adet çubuk artmıştır."

            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, rapor_metni)
            self.result_label.config(text=f"Sonuç: Toplam {toplam_tam_tesbih} adet TAM tesbih üretilebilir.")

            self.c.execute('''
                INSERT INTO uretim_kayitlari (
                    is_adi, cubuk_boyu, cubuk_sayisi, boncuk_boyu, boncuk_sayisi_bir_tesbih,
                    ara_tane_boyu, ara_tane_sayisi_bir_tesbih, pul_boyu, pul_sayisi_bir_tesbih,
                    imame_boyu, sikke_boyu, dugum_boyu, tepelik_boyu, civi_boyu, isimlik_boyu,
                    toplam_tesbih_adeti, rapor_metni
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                is_adi, data["cubuk_boyu"], data["cubuk_sayisi"], data["boncuk_boyu"],
                data["boncuk_sayisi_bir_tesbih"], data["ara_tane_boyu"], data["ara_tane_sayisi_bir_tesbih"],
                data["pul_boyu"], data["pul_sayisi_bir_tesbih"], data["imame_boyu"],
                data["sikke_boyu"], data["dugum_boyu"], data["tepelik_boyu"],
                data["civi_boyu"], data["isimlik_boyu"], toplam_tam_tesbih, rapor_metni
            ))
            self.conn.commit()
            
            self.listeyi_guncelle()
            messagebox.showinfo("Başarılı", "Hesaplama yapıldı ve kayıt başarıyla eklendi.")

        except ValueError:
            messagebox.showerror("Hata", "Lütfen tüm alanlara geçerli sayısal değerler girin. Boş bırakılan alanlar sıfır olarak kabul edilir. Ondalık sayılar için nokta (.) kullanın.")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def listeyi_guncelle(self):
        self.is_listbox.delete(0, tk.END)
        self.c.execute("SELECT id, is_adi FROM uretim_kayitlari ORDER BY id DESC")
        kayitlar = self.c.fetchall()
        for kayit in kayitlar:
            self.is_listbox.insert(tk.END, f"{kayit[0]} - {kayit[1]}")
    
    def is_secildi(self, event):
        try:
            selected_index = self.is_listbox.curselection()[0]
            secilen_kayit_str = self.is_listbox.get(selected_index)
            is_id = int(secilen_kayit_str.split(' - ')[0])

            self.c.execute("SELECT * FROM uretim_kayitlari WHERE id=?", (is_id,))
            kayit = self.c.fetchone()
            
            if kayit:
                self.alanlari_temizle()
                keys = ["id", "is_adi", "cubuk_boyu", "cubuk_sayisi", "boncuk_boyu", "boncuk_sayisi_bir_tesbih", 
                        "ara_tane_boyu", "ara_tane_sayisi_bir_tesbih", "pul_boyu", "pul_sayisi_bir_tesbih", 
                        "imame_boyu", "sikke_boyu", "dugum_boyu", "tepelik_boyu", "civi_boyu", 
                        "isimlik_boyu", "toplam_tesbih_adeti", "rapor_metni"]
                
                for i, key in enumerate(keys):
                    if key in self.entries:
                        self.entries[key].insert(0, str(kayit[i]))
                
                self.result_label.config(text=f"Sonuç: Toplam {kayit[-2]} adet TAM tesbih üretilebilir.")
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, kayit[-1])

        except IndexError:
            pass

    def alanlari_temizle(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.result_label.config(text="Sonuç:")
        self.report_text.delete(1.0, tk.END)

    def kaydi_sil(self):
        try:
            selected_index = self.is_listbox.curselection()[0]
            secilen_kayit_str = self.is_listbox.get(selected_index)
            is_id = int(secilen_kayit_str.split(' - ')[0])

            cevap = messagebox.askyesno("Silme Onayı", "Bu kaydı silmek istediğinizden emin misiniz?")
            if cevap:
                self.c.execute("DELETE FROM uretim_kayitlari WHERE id=?", (is_id,))
                self.conn.commit()
                self.listeyi_guncelle()
                self.alanlari_temizle()
                messagebox.showinfo("Silindi", "Kayıt başarıyla silindi.")
        except IndexError:
            messagebox.showerror("Hata", "Lütfen listeden bir kayıt seçin.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TesbihHesaplayiciApp(root)
    root.mainloop()
