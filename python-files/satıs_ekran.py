import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
import json
import datetime

from Tools.scripts.pindent import delete_file

# --- Veritabanı Dosyaları ---
URUN_DOSYASI = "uru.json"
SATIS_DOSYASI = "sati.json"


# --- Dosyadan Veri Yükleme/Kaydetme Fonksiyonları ---

def rst():
    delete_file(URUN_DOSYASI)
    delete_file(SATIS_DOSYASI)




def veri_yukle(dosya_adi):
    """Belirtilen JSON dosyasından veriyi yükler."""
    try:
        with open(dosya_adi, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Dosya yoksa uygun boş yapıyı döndür
        return {} if dosya_adi == URUN_DOSYASI else []
    except json.JSONDecodeError:
        messagebox.showerror("Hata", f"'{dosya_adi}' dosyası bozuk veya boş. Boş olarak başlatılıyor.")
        # Bozuk veya boş dosyadan sonra da boş yapıyı döndür
        return {} if dosya_adi == URUN_DOSYASI else []
    except Exception as e:
        messagebox.showerror("Hata", f"Veri yüklenirken beklenmeyen hata oluştu ({dosya_adi}): {e}")
        return {} if dosya_adi == URUN_DOSYASI else []


def veri_kaydet(veri, dosya_adi):
    """Veriyi belirtilen JSON dosyasına kaydeder."""
    try:
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Hata", f"Veri kaydedilirken hata oluştu ({dosya_adi}): {e}")


# Uygulama başlangıcında verileri yükle
urunler = veri_yukle(URUN_DOSYASI)
satis_gecmisi = veri_yukle(SATIS_DOSYASI)


# --- SATIŞ YAP EKRANI ---
def satis_yap_ekrani():
    """Satış işlemini gerçekleştiren ayrı bir pencere açar."""
    satis_pencere = Toplevel()
    satis_pencere.title("Satış İşlemi")
    satis_pencere.geometry("1000x700")  # Pencere boyutunu biraz artırdık
    satis_pencere.grab_set()  # Ana pencereyi bloke et

    # Global değişkenler yerine, bu fonksiyonun içindeki sepeti kullanacağız
    sepet = {}  # {barkod: {"ad": "", "fiyat": "", "adet": "", "alis_fiyati": ""}}
    toplam_tutar_var = tk.DoubleVar(value=0.0)  # Toplam tutarı dinamik güncellemek için

    # --- Üst Kontrol Çubuğu (Barkod Girişi ve İsim Arama) ---
    ust_frame = tk.Frame(satis_pencere, bd=2, relief=tk.GROOVE)
    ust_frame.pack(pady=10, padx=10, fill=tk.X)

    # Barkod Kısmı
    tk.Label(ust_frame, text="Barkodu Okutun/Giriniz:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10,
                                                                                         pady=5, sticky=tk.W)
    barkod_giris = tk.Entry(ust_frame, font=("Arial", 16), width=25, bd=2, relief=tk.SUNKEN)
    barkod_giris.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
    barkod_giris.focus_set()  # Odak buraya verilsin ki barkod okuyucu direkt buraya yazsın

    # İsim Arama Kısmı
    tk.Label(ust_frame, text="Ürün Adı ile Arayın:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=(30, 5),
                                                                                      pady=5, sticky=tk.W)
    isim_arama_entry = tk.Entry(ust_frame, font=("Arial", 16), width=25, bd=2, relief=tk.SUNKEN)
    isim_arama_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

    # Arama Sonuçları Ağacı
    arama_sonuc_frame = tk.Frame(ust_frame, bd=1, relief=tk.SUNKEN)
    arama_sonuc_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky=tk.NSEW)
    ust_frame.grid_rowconfigure(1, weight=1)  # Arama sonuçları için dikeyde genişleme

    arama_sonuc_tree = ttk.Treeview(arama_sonuc_frame, columns=("Barkod", "Ürün Adı", "Fiyat", "Stok"), show="headings",
                                    selectmode="browse")
    arama_sonuc_tree.heading("Barkod", text="Barkod")
    arama_sonuc_tree.heading("Ürün Adı", text="Ürün Adı")
    arama_sonuc_tree.heading("Fiyat", text="Fiyat")
    arama_sonuc_tree.heading("Stok", text="Stok")

    arama_sonuc_tree.column("Barkod", width=120, anchor=tk.W)
    arama_sonuc_tree.column("Ürün Adı", width=250, anchor=tk.W)
    arama_sonuc_tree.column("Fiyat", width=80, anchor=tk.E)
    arama_sonuc_tree.column("Stok", width=60, anchor=tk.CENTER)

    arama_scrollbar = ttk.Scrollbar(arama_sonuc_frame, orient="vertical", command=arama_sonuc_tree.yview)
    arama_sonuc_tree.configure(yscrollcommand=arama_scrollbar.set)
    arama_scrollbar.pack(side="right", fill="y")
    arama_sonuc_tree.pack(fill=tk.BOTH, expand=True)

    def urun_ara(event=None):
        arama_kelimesi = isim_arama_entry.get().strip().lower()

        # Önceki sonuçları temizle
        for item_id in arama_sonuc_tree.get_children():
            arama_sonuc_tree.delete(item_id)

        if not arama_kelimesi:
            return

        bulunan_urunler = []
        for barkod, bilgi in urunler.items():
            # Sadece ürün adı ve barkod içinde arama yapıyoruz
            if arama_kelimesi in bilgi["ad"].lower() or arama_kelimesi in barkod.lower():
                bulunan_urunler.append((barkod, bilgi["ad"], bilgi["fiyat"], bilgi["stok"]))

        if not bulunan_urunler:
            arama_sonuc_tree.insert("", tk.END, values=("", "Ürün bulunamadı.", "", ""))
            return

        for barkod, ad, fiyat, stok in bulunan_urunler:
            arama_sonuc_tree.insert("", tk.END, values=(barkod, ad, f"{fiyat:.2f} TL", stok),
                                    iid=barkod)  # barkodu iid olarak kullan

    isim_arama_entry.bind("<KeyRelease>", urun_ara)  # Her tuş basımında ara

    def arama_secileni_sepete_ekle(event=None):
        secili_item_id = arama_sonuc_tree.focus()
        if not secili_item_id:
            messagebox.showwarning("Uyarı", "Lütfen önce arama sonuçlarından bir ürün seçin.")
            return

        barkod_eklenecek = secili_item_id
        ekle_urunu_sepete(barkod_eklenecek)
        isim_arama_entry.delete(0, tk.END)  # Arama kutusunu temizle
        urun_ara()  # Arama sonuçlarını temizle

    arama_sonuc_tree.bind("<Double-1>", arama_secileni_sepete_ekle)  # Çift tıklayınca sepete ekle
    arama_sonuc_tree.bind("<Return>", arama_secileni_sepete_ekle)  # Enter'a basınca sepete ekle

    def ekle_urunu_sepete(barkod):
        if barkod not in urunler:
            messagebox.showerror("Hata", f"'{barkod}' barkodlu ürün bulunamadı.")
            return

        urun_bilgi = urunler[barkod]
        if urun_bilgi["stok"] <= 0:
            messagebox.showwarning("Stok Uyarısı", f"{urun_bilgi['ad']} ürünü stokta yok!")
            return

        if "alis_fiyati" not in urun_bilgi:
            messagebox.showwarning("Eksik Bilgi",
                                   f"'{urun_bilgi['ad']}' ürünü için alış fiyatı tanımlanmamış. Kar doğru hesaplanamayabilir!")

        if barkod in sepet:
            sepet[barkod]["adet"] += 1
        else:
            sepet[barkod] = {
                "ad": urun_bilgi["ad"],
                "fiyat": urun_bilgi["fiyat"],
                "alis_fiyati": urun_bilgi.get("alis_fiyati", 0.0),
                "adet": 1
            }

        urunler[barkod]["stok"] -= 1
        sepeti_guncelle()
        barkod_giris.focus_set()  # Tekrar barkod girişine odaklan (devamlı okutma için)

    def barkod_okundu(event=None):
        barkod = barkod_giris.get().strip()
        barkod_giris.delete(0, tk.END)
        if not barkod:
            return
        ekle_urunu_sepete(barkod)

    barkod_giris.bind("<Return>", barkod_okundu)

    # --- Sepet Görünümü ---
    sepet_frame = tk.Frame(satis_pencere, bd=2, relief=tk.SUNKEN)
    sepet_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    columns = ("Ürün Adı", "Adet", "Birim Fiyat", "Toplam")
    sepet_tree = ttk.Treeview(sepet_frame, columns=columns, show="headings", selectmode="browse")
    sepet_tree.heading("Ürün Adı", text="Ürün Adı")
    sepet_tree.heading("Adet", text="Adet")
    sepet_tree.heading("Birim Fiyat", text="Birim Fiyat")
    sepet_tree.heading("Toplam", text="Toplam")

    sepet_tree.column("Ürün Adı", width=300, anchor=tk.W)
    sepet_tree.column("Adet", width=80, anchor=tk.CENTER)
    sepet_tree.column("Birim Fiyat", width=120, anchor=tk.E)
    sepet_tree.column("Toplam", width=120, anchor=tk.E)

    # Scrollbar ekle
    scrollbar = ttk.Scrollbar(sepet_frame, orient="vertical", command=sepet_tree.yview)
    sepet_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    sepet_tree.pack(fill=tk.BOTH, expand=True)

    def sepeti_guncelle():
        """Sepet görünümünü ve toplam tutarı günceller."""
        for item_id in sepet_tree.get_children():
            sepet_tree.delete(item_id)

        anlik_toplam = 0.0
        for barkod, item in sepet.items():
            urun_toplam = item["fiyat"] * item["adet"]
            sepet_tree.insert("", tk.END,
                              values=(item["ad"], item["adet"], f"{item['fiyat']:.2f} TL", f"{urun_toplam:.2f} TL"),
                              iid=barkod)
            anlik_toplam += urun_toplam
        toplam_tutar_var.set(anlik_toplam)

    # --- Sepet Kontrolleri (Adet Artır/Azalt, Çıkar) ---
    sepet_kontrol_frame = tk.Frame(satis_pencere)
    sepet_kontrol_frame.pack(pady=5, padx=10, fill=tk.X)

    def secili_adeti_degistir(miktar):
        secili_item_id = sepet_tree.focus()
        if not secili_item_id:
            messagebox.showwarning("Uyarı", "Lütfen önce sepetten bir ürün seçin.")
            return

        barkod = secili_item_id
        if barkod in sepet:
            eski_adet = sepet[barkod]["adet"]
            yeni_adet = eski_adet + miktar

            if yeni_adet <= 0:
                onay = messagebox.askyesno("Onay", f"{sepet[barkod]['ad']} ürününü sepetten kaldırmak istiyor musunuz?")
                if onay:
                    del sepet[barkod]
                    urunler[barkod]["stok"] += eski_adet  # Stokları geri yükle
                else:
                    return
            else:
                if miktar > 0 and urunler[barkod]["stok"] < miktar:
                    messagebox.showwarning("Stok Uyarısı",
                                           f"{sepet[barkod]['ad']} ürünü için yeterli stok yok! Mevcut: {urunler[barkod]['stok']}")
                    return

                sepet[barkod]["adet"] = yeni_adet
                urunler[barkod]["stok"] -= miktar

            sepeti_guncelle()
        barkod_giris.focus_set()

    btn_adet_azalt = tk.Button(sepet_kontrol_frame, text="- Adet", command=lambda: secili_adeti_degistir(-1),
                               font=("Arial", 12), width=10, bg="#FF6347", fg="white")
    btn_adet_azalt.pack(side=tk.LEFT, padx=5)

    btn_adet_arttir = tk.Button(sepet_kontrol_frame, text="+ Adet", command=lambda: secili_adeti_degistir(1),
                                font=("Arial", 12), width=10, bg="#32CD32", fg="white")
    btn_adet_arttir.pack(side=tk.LEFT, padx=5)

    btn_cikar = tk.Button(sepet_kontrol_frame, text="Seçileni Çıkar", command=lambda: secili_adeti_degistir(
        -sepet[sepet_tree.focus()]["adet"] if sepet_tree.focus() in sepet else 0), font=("Arial", 12), width=15,
                          bg="#FFD700", fg="black")
    btn_cikar.pack(side=tk.LEFT, padx=15)

    # --- Toplam Tutar ve Ödeme Butonları ---
    alt_frame = tk.Frame(satis_pencere, bd=2, relief=tk.GROOVE)
    alt_frame.pack(pady=10, padx=10, fill=tk.X)

    tk.Label(alt_frame, text="Toplam Tutar:", font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Label(alt_frame, textvariable=toplam_tutar_var, font=("Arial", 20, "bold"), fg="blue").pack(side=tk.LEFT, padx=5)

    # --- Ödeme Tipi Seçim Penceresi ---
    def odeme_tipi_sec(sepet_veri, toplam_tutar, main_satis_pencere):
        odeme_pencere = Toplevel()
        odeme_pencere.title("Ödeme Tipi Seçiniz")
        odeme_pencere.geometry("350x250")
        odeme_pencere.grab_set()

        # Pencereyi satış ekranının ortasına hizala
        odeme_pencere.update_idletasks()
        satis_x = main_satis_pencere.winfo_x()
        satis_y = main_satis_pencere.winfo_y()
        satis_width = main_satis_pencere.winfo_width()
        satis_height = main_satis_pencere.winfo_height()

        odeme_width = odeme_pencere.winfo_width()
        odeme_height = odeme_pencere.winfo_height()

        x_offset = satis_x + (satis_width // 2) - (odeme_width // 2)
        y_offset = satis_y + (satis_height // 2) - (odeme_height // 2)
        odeme_pencere.geometry(f'+{x_offset}+{y_offset}')

        tk.Label(odeme_pencere, text="Toplam Tutar:", font=("Arial", 16)).pack(pady=10)
        tk.Label(odeme_pencere, text=f"{toplam_tutar:.2f} TL", font=("Arial", 24, "bold"), fg="darkgreen").pack(pady=5)

        def satisi_kaydet(odeme_tipi):
            toplam_kar = 0.0
            for barkod, item in sepet_veri.items():
                urun_kar = (item["fiyat"] - item.get("alis_fiyati", 0.0)) * item["adet"]
                toplam_kar += urun_kar

            satis_kaydi = {
                "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sepet": sepet_veri,
                "toplam_tutar": toplam_tutar,
                "odeme_tipi": odeme_tipi,
                "toplam_kar": toplam_kar
            }
            satis_gecmisi.append(satis_kaydi)
            veri_kaydet(urunler, URUN_DOSYASI)
            veri_kaydet(satis_gecmisi, SATIS_DOSYASI)
            messagebox.showinfo("Başarılı", f"Satış '{odeme_tipi}' ile tamamlandı ve kaydedildi!")
            odeme_pencere.destroy()
            main_satis_pencere.destroy()

        btn_nakit = tk.Button(odeme_pencere, text="Nakit Ödeme", command=lambda: satisi_kaydet("Nakit"),
                              font=("Arial", 16, "bold"), bg="#28A745", fg="white", width=20, height=2)
        btn_nakit.pack(pady=10)

        btn_kredi_karti = tk.Button(odeme_pencere, text="Kredi Kartı ile Ödeme",
                                    command=lambda: satisi_kaydet("Kredi Kartı"),
                                    font=("Arial", 16, "bold"), bg="#007BFF", fg="white", width=20, height=2)
        btn_kredi_karti.pack(pady=10)

        odeme_pencere.wait_window()

    def satisi_tamamla_butonu_tiklandi():
        if not sepet:
            messagebox.showwarning("Uyarı", "Sepet boş. Satış tamamlanamaz.")
            return

        odeme_tipi_sec(sepet, toplam_tutar_var.get(), satis_pencere)

    btn_tamamla = tk.Button(alt_frame, text="ÖDEME AL / SATIŞI TAMAMLA", command=satisi_tamamla_butonu_tiklandi,
                            font=("Arial", 16, "bold"), bg="#28A745", fg="white", width=30, height=2)
    btn_tamamla.pack(side=tk.RIGHT, padx=10)

    def satisi_iptal_et():
        onay = messagebox.askyesno("Satış İptali",
                                   "Satışı iptal etmek istediğinize emin misiniz? Sepet temizlenecek ve stoklar geri yüklenecektir.")
        if onay:
            # Sepetteki ürünlerin stoklarını geri yükle
            for barkod, item in sepet.items():
                if barkod in urunler:  # Ürünün hala var olduğundan emin ol
                    urunler[barkod]["stok"] += item["adet"]

            # Sepeti ve girişleri sıfırla
            sepet.clear()
            sepeti_guncelle()
            barkod_giris.delete(0, tk.END)
            isim_arama_entry.delete(0, tk.END)
            urun_ara()  # Arama sonuçlarını da temizle
            barkod_giris.focus_set()
            messagebox.showinfo("İptal Edildi", "Satış iptal edildi ve sistem sıfırlandı.")

    btn_iptal = tk.Button(alt_frame, text="İPTAL", command=satisi_iptal_et, font=("Arial", 16), bg="#DC3545",
                          fg="white", width=15, height=2)
    btn_iptal.pack(side=tk.RIGHT, padx=10)

    # --- SIFIRLAMA DÜĞMESİ (Sağ Üst Köşeye Konumlandırma) ---
    def tum_degerleri_sifirla():
        onay = messagebox.askyesno("Sıfırlama Onayı",
                                   "Tüm sepeti ve girişleri sıfırlamak istediğinize emin misiniz? Sepetteki ürünlerin stokları geri yüklenecektir.")
        if onay:
            # Sepetteki ürünlerin stoklarını geri yükle
            for barkod, item in sepet.items():
                if barkod in urunler:  # Ürünün hala var olduğundan emin ol
                    urunler[barkod]["stok"] += item["adet"]

            # Sepeti ve girişleri sıfırla
            sepet.clear()
            sepeti_guncelle()
            barkod_giris.delete(0, tk.END)
            isim_arama_entry.delete(0, tk.END)
            urun_ara()  # Arama sonuçlarını da temizle
            barkod_giris.focus_set()  # Odaklanmayı barkod girişine geri getir
            messagebox.showinfo("Sıfırlandı", "Satış ekranındaki tüm değerler sıfırlandı. Stoklar güncellendi.")

    # ust_frame'in grid yapısına eklemek için
    # sağdaki son sütunu genişletebiliriz
    ust_frame.grid_columnconfigure(5, weight=1)  # Yeni bir sütun ekleyip genişlemesini sağla

    btn_sifirla = tk.Button(ust_frame, text="X", command=tum_degerleri_sifirla,
                            font=("Arial", 10, "bold"), bg="red", fg="white",
                            width=3, height=1, relief=tk.RAISED, bd=2)
    # Düğmeyi en sağ üst köşeye yerleştir
    btn_sifirla.grid(row=0, column=5, padx=5, pady=5, sticky=tk.NE)


# --- ÜRÜN EKLE / GÜNCELLE EKRANI ---
def urun_ekle_ekrani():
    """Ürün ekleme/güncelleme işlemini gerçekleştiren ayrı bir pencere açar."""
    urun_pencere = Toplevel()
    urun_pencere.title("Ürün Ekle/Güncelle")
    urun_pencere.geometry("450x500")
    urun_pencere.grab_set()

    input_frame = tk.Frame(urun_pencere, bd=2, relief=tk.GROOVE, padx=20, pady=20)
    input_frame.pack(pady=20)

    tk.Label(input_frame, text="Barkod:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
    barkod_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
    barkod_entry.grid(row=0, column=1, pady=5, padx=5)
    barkod_entry.focus_set()

    tk.Label(input_frame, text="Ürün Adı:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
    ad_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
    ad_entry.grid(row=1, column=1, pady=5, padx=5)

    tk.Label(input_frame, text="Alış Fiyatı (TL):", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=5,
                                                                             padx=5)
    alis_fiyati_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
    alis_fiyati_entry.grid(row=2, column=1, pady=5, padx=5)

    tk.Label(input_frame, text="Satış Fiyatı (TL):", font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, pady=5,
                                                                              padx=5)
    satis_fiyati_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
    satis_fiyati_entry.grid(row=3, column=1, pady=5, padx=5)

    tk.Label(input_frame, text="Stok Miktarı:", font=("Arial", 12)).grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
    stok_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
    stok_entry.grid(row=4, column=1, pady=5, padx=5)

    def kaydet_urun():
        barkod = barkod_entry.get().strip()
        ad = ad_entry.get().strip()
        alis_fiyati_str = alis_fiyati_entry.get().strip()
        satis_fiyati_str = satis_fiyati_entry.get().strip()
        stok_str = stok_entry.get().strip()

        if not barkod or not ad or not alis_fiyati_str or not satis_fiyati_str or not stok_str:
            messagebox.showerror("Hata", "Tüm alanları doldurmak zorunludur.")
            return

        try:
            alis_fiyati = float(alis_fiyati_str)
            satis_fiyati = float(satis_fiyati_str)
            stok = int(stok_str)
            if alis_fiyati < 0 or satis_fiyati <= 0 or stok < 0:
                messagebox.showerror("Hata", "Fiyatlar pozitif, stok sıfır veya pozitif olmalıdır.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Fiyat ve Stok miktarı geçerli sayılar olmalıdır.")
            return

        if barkod in urunler:
            onay = messagebox.askyesno("Onay",
                                       f"'{ad}' ürünü ({barkod}) zaten var. Bilgileri güncellenecek. Devam etmek istiyor musunuz?")
            if not onay:
                return
            urunler[barkod]["ad"] = ad
            urunler[barkod]["alis_fiyati"] = alis_fiyati
            urunler[barkod]["fiyat"] = satis_fiyati
            urunler[barkod]["stok"] = stok
            messagebox.showinfo("Başarılı", f"'{ad}' ürünü güncellendi.")
        else:
            urunler[barkod] = {"ad": ad, "alis_fiyati": alis_fiyati, "fiyat": satis_fiyati, "stok": stok}
            messagebox.showinfo("Başarılı", f"'{ad}' ürünü başarıyla eklendi.")

        veri_kaydet(urunler, URUN_DOSYASI)
        urun_pencere.destroy()

    def barkod_guncelle(event=None):
        barkod = barkod_entry.get().strip()
        if barkod in urunler:
            urun_bilgi = urunler[barkod]
            ad_entry.delete(0, tk.END)
            ad_entry.insert(0, urun_bilgi["ad"])
            alis_fiyati_entry.delete(0, tk.END)
            alis_fiyati_entry.insert(0, str(urun_bilgi.get("alis_fiyati", "")))
            satis_fiyati_entry.delete(0, tk.END)
            satis_fiyati_entry.insert(0, str(urun_bilgi["fiyat"]))
            stok_entry.delete(0, tk.END)
            stok_entry.insert(0, str(urun_bilgi["stok"]))
            messagebox.showinfo("Bilgi", "Mevcut ürün bilgileri yüklendi.")
        elif barkod:
            ad_entry.delete(0, tk.END)
            alis_fiyati_entry.delete(0, tk.END)
            satis_fiyati_entry.delete(0, tk.END)
            stok_entry.delete(0, tk.END)
            pass

    kaydet_btn = tk.Button(urun_pencere, text="Kaydet", command=kaydet_urun, font=("Arial", 14, "bold"), bg="#4CAF50",
                           fg="white", width=15, height=2)
    kaydet_btn.pack(pady=20)
    barkod_entry.bind("<Return>", barkod_guncelle)


# --- STOK GÖRÜNTÜLE EKRANI ---
def stok_goruntule_ekrani():
    """Stok durumunu gösteren ayrı bir pencere açar."""
    stok_pencere = Toplevel()
    stok_pencere.title("Mevcut Stok Durumu")
    stok_pencere.geometry("850x600")
    stok_pencere.grab_set()

    stok_frame = tk.Frame(stok_pencere, bd=2, relief=tk.SUNKEN)
    stok_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    columns = ("Barkod", "Ürün Adı", "Alış Fiyatı", "Satış Fiyatı", "Stok")
    stok_tree = ttk.Treeview(stok_frame, columns=columns, show="headings", selectmode="browse")
    stok_tree.heading("Barkod", text="Barkod")
    stok_tree.heading("Ürün Adı", text="Ürün Adı")
    stok_tree.heading("Alış Fiyatı", text="Alış Fiyatı")
    stok_tree.heading("Satış Fiyatı", text="Satış Fiyatı")
    stok_tree.heading("Stok", text="Stok")

    stok_tree.column("Barkod", width=150, anchor=tk.W)
    stok_tree.column("Ürün Adı", width=250, anchor=tk.W)
    stok_tree.column("Alış Fiyatı", width=100, anchor=tk.E)
    stok_tree.column("Satış Fiyatı", width=100, anchor=tk.E)
    stok_tree.column("Stok", width=80, anchor=tk.CENTER)

    scrollbar = ttk.Scrollbar(stok_frame, orient="vertical", command=stok_tree.yview)
    stok_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    stok_tree.pack(fill=tk.BOTH, expand=True)

    if not urunler:
        stok_tree.insert("", tk.END, values=("", "Stokta hiç ürün bulunmamaktadır.", "", "", ""))
    else:
        for barkod, bilgi in urunler.items():
            alis_fiyati_str = f"{bilgi.get('alis_fiyati', 0.0):.2f} TL"
            stok_tree.insert("", tk.END,
                             values=(barkod, bilgi["ad"], alis_fiyati_str, f"{bilgi['fiyat']:.2f} TL", bilgi["stok"]))


# --- SATIŞ GEÇMİŞİ EKRANI ---
def satis_gecmisi_ekrani():
    """Satış geçmişini gösteren ayrı bir pencere açar."""
    gecmis_pencere = Toplevel()
    gecmis_pencere.title("Satış Geçmişi")
    gecmis_pencere.geometry("1000x700")
    gecmis_pencere.grab_set()

    gecmis_frame = tk.Frame(gecmis_pencere, bd=2, relief=tk.SUNKEN)
    gecmis_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    columns = ("Tarih", "Ödeme Tipi", "Ürün Adı", "Adet", "Birim Fiyat", "Toplam", "Kar", "Satış Toplamı")
    gecmis_tree = ttk.Treeview(gecmis_frame, columns=columns, show="headings", selectmode="browse")
    gecmis_tree.heading("Tarih", text="Tarih")
    gecmis_tree.heading("Ödeme Tipi", text="Ödeme Tipi")
    gecmis_tree.heading("Ürün Adı", text="Ürün Adı")
    gecmis_tree.heading("Adet", text="Adet")
    gecmis_tree.heading("Birim Fiyat", text="Birim Fiyat")
    gecmis_tree.heading("Toplam", text="Toplam")
    gecmis_tree.heading("Kar", text="Kar")
    gecmis_tree.heading("Satış Toplamı", text="Satış Toplamı")

    gecmis_tree.column("Tarih", width=140, anchor=tk.W)
    gecmis_tree.column("Ödeme Tipi", width=90, anchor=tk.CENTER)
    gecmis_tree.column("Ürün Adı", width=180, anchor=tk.W)
    gecmis_tree.column("Adet", width=60, anchor=tk.CENTER)
    gecmis_tree.column("Birim Fiyat", width=90, anchor=tk.E)
    gecmis_tree.column("Toplam", width=90, anchor=tk.E)
    gecmis_tree.column("Kar", width=90, anchor=tk.E)
    gecmis_tree.column("Satış Toplamı", width=100, anchor=tk.E)

    scrollbar = ttk.Scrollbar(gecmis_frame, orient="vertical", command=gecmis_tree.yview)
    gecmis_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    gecmis_tree.pack(fill=tk.BOTH, expand=True)

    if not satis_gecmisi:
        gecmis_tree.insert("", tk.END, values=("", "", "Henüz kaydedilmiş satış bulunmamaktadır.", "", "", "", "", ""))
    else:
        for satis in satis_gecmisi:
            tarih = satis["tarih"]
            odeme_tipi = satis.get("odeme_tipi", "Bilinmiyor")
            satis_toplami = f"{satis['toplam_tutar']:.2f} TL"
            satis_toplam_kar = f"{satis.get('toplam_kar', 0.0):.2f} TL"

            for i, (barkod, item) in enumerate(satis['sepet'].items()):
                urun_kar = (item["fiyat"] - item.get("alis_fiyati", 0.0)) * item["adet"]
                urun_toplam = item["fiyat"] * item["adet"]

                if i == 0:
                    gecmis_tree.insert("", tk.END, values=(tarih, odeme_tipi, item["ad"], item["adet"],
                                                           f"{item['fiyat']:.2f} TL", f"{urun_toplam:.2f} TL",
                                                           f"{urun_kar:.2f} TL", satis_toplami), tags=("satis_ana",))
                else:
                    gecmis_tree.insert("", tk.END, values=("", "", item["ad"], item["adet"],
                                                           f"{item['fiyat']:.2f} TL", f"{urun_toplam:.2f} TL",
                                                           f"{urun_kar:.2f} TL", ""), tags=("satis_detay",))
            gecmis_tree.insert("", tk.END, values=("", "", "", "", "", "", "", ""))  # Satışlar arasına boş satır


# --- GÜNLÜK KASA DURUMU EKRANI ---
def gunluk_kasa_durumu_ekrani():
    kasa_pencere = Toplevel()
    kasa_pencere.title("Günlük Kasa Durumu")
    kasa_pencere.geometry("400x250")
    kasa_pencere.grab_set()

    kasa_pencere.update_idletasks()
    width = kasa_pencere.winfo_width()
    height = kasa_pencere.winfo_height()
    x = (kasa_pencere.winfo_screenwidth() // 2) - (width // 2)
    y = (kasa_pencere.winfo_screenheight() // 2) - (height // 2)
    kasa_pencere.geometry(f'+{x}+{y}')

    bugun = datetime.datetime.now().strftime("%Y-%m-%d")
    gunluk_toplam_ciro = 0.0  # Tüm satışları toplamak için tek bir değişken
    gunluk_toplam_kar = 0.0

    for satis in satis_gecmisi:
        satis_tarihi = satis["tarih"].split(" ")[0]
        if satis_tarihi == bugun:
            gunluk_toplam_ciro += satis["toplam_tutar"]
            gunluk_toplam_kar += satis.get("toplam_kar", 0.0)

    tk.Label(kasa_pencere, text=f"Bugün: {bugun}", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(kasa_pencere, text=f"Kasada Olan Para (Günlük Ciro):", font=("Arial", 14)).pack(pady=5)
    tk.Label(kasa_pencere, text=f"{gunluk_toplam_ciro:.2f} TL", font=("Arial", 20, "bold"), fg="green").pack(pady=10)
    tk.Label(kasa_pencere, text=f"Günlük Toplam Kar: {gunluk_toplam_kar:.2f} TL", font=("Arial", 14, "italic")).pack(
        pady=5)


# --- TOPLAM KAR EKRANI ---
def toplam_kar_ekrani():
    kar_pencere = Toplevel()
    kar_pencere.title("Toplam Kar")
    kar_pencere.geometry("400x200")
    kar_pencere.grab_set()

    kar_pencere.update_idletasks()
    width = kar_pencere.winfo_width()
    height = kar_pencere.winfo_height()
    x = (kar_pencere.winfo_screenwidth() // 2) - (width // 2)
    y = (kar_pencere.winfo_screenheight() // 2) - (height // 2)
    kar_pencere.geometry(f'+{x}+{y}')

    toplam_kar_tum_zamanlar = 0.0
    for satis in satis_gecmisi:
        toplam_kar_tum_zamanlar += satis.get("toplam_kar", 0.0)

    tk.Label(kar_pencere, text="Tüm Zamanların Toplam Karı:", font=("Arial", 16, "bold")).pack(pady=20)
    tk.Label(kar_pencere, text=f"{toplam_kar_tum_zamanlar:.2f} TL", font=("Arial", 24, "bold"), fg="purple").pack(
        pady=10)


# --- ANA PENCERE OLUŞTURMA ---
def ana_ekrani_olustur():
    pencere = tk.Tk()
    pencere.title("Azad Satıs")
    pencere.geometry("850x950")

    pencere.update_idletasks()
    width = pencere.winfo_width()
    height = pencere.winfo_height()
    x = (pencere.winfo_screenwidth() // 2) - (width // 2)
    y = (pencere.winfo_screenheight() // 2) - (height // 2)
    pencere.geometry(f'{width}x{height}+{x}+{y}')

    button_style = {"font": ("Arial", 14, "bold"), "fg": "white", "width": 25, "height": 2, "relief": tk.RAISED,
                    "bd": 3}
    button_styl = {"font": ("Arial", 14, "bold"), "fg": "white", "width": 5, "height": 0, "relief": tk.RAISED,
                    "bd": 3}

    btn_kasa_durumu = tk.Button(pencere, text="Günlük Kasa Durumu", command=gunluk_kasa_durumu_ekrani, bg="#8B4513",
                                **button_style)
    btn_kasa_durumu.pack(pady=10)


    btn_satis = tk.Button(pencere, text="Satış Yap", command=satis_yap_ekrani, bg="#4CAF50", **button_style)
    btn_satis.pack(pady=10)

    btn_urun_ekle = tk.Button(pencere, text="Ürün Ekle / Güncelle", command=urun_ekle_ekrani, bg="#2196F3",
                              **button_style)
    btn_urun_ekle.pack(pady=10)

    btn_stok_goruntule = tk.Button(pencere, text="Stok Görüntüle", command=stok_goruntule_ekrani, bg="#FFC107",
                                    **button_style)
    btn_stok_goruntule.pack(pady=10)

    btn_satis_gecmisi = tk.Button(pencere, text="Satış Geçmişi", command=satis_gecmisi_ekrani, bg="#9C27B0",
                                  **button_style)
    btn_satis_gecmisi.pack(pady=10)

    btn_toplam_kar = tk.Button(pencere, text="Toplam Kar", command=toplam_kar_ekrani, bg="#6A0DAD", **button_style)
    btn_toplam_kar.pack(pady=10)

    btn_cikis = tk.Button(pencere, text="Çıkış", command=pencere.quit, bg="#F44336", **button_style)
    btn_cikis.pack(pady=20)


    btn_rst.pack(pady=85)



    pencere.mainloop()


# --- Programı Başlat ---
if __name__ == "__main__":
    ana_ekrani_olustur()