import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

def mevcut_deger_faktoru(vade_ay, vade_farksiz_ay, faiz_orani):
    faktor = 0
    for t in range(1, vade_ay + 1):
        if t <= vade_farksiz_ay:
            faktor += 1  # Vade farksız aylar için faizsiz
        else:
            faktor += 1 / (1 + faiz_orani) ** (t - vade_farksiz_ay)  # Faizli aylar
    return faktor

def esit_taksit_hesapla(anapara, vade_ay, vade_farksiz_ay, faiz_orani, pesinat):
    if vade_ay <= 0 or anapara <= 0:
        return 0, 0, 0, 0
    # Eşit taksit hesaplama
    md_faktoru = mevcut_deger_faktoru(vade_ay, vade_farksiz_ay, faiz_orani)
    taksit = anapara / md_faktoru if md_faktoru > 0 else anapara / vade_ay
    # Vade farksız ödeme (ilk 3 ay)
    taksit_farksiz = taksit  # Vade farksız taksit, eşit taksit ile aynı
    vade_farksiz_odeme = taksit_farksiz * min(vade_ay, vade_farksiz_ay)
    # Toplam ödeme
    toplam_odeme = taksit * vade_ay + pesinat  # Peşinat ekleniyor
    # Vade farkı
    vade_farki = toplam_odeme - (anapara + pesinat)
    return taksit_farksiz, vade_farksiz_odeme, taksit, toplam_odeme, vade_farki

def odeme_plani_olustur(urun_fiyati, kdv_orani, pesinatlar, vade_ay, vade_farksiz_ay, faiz_orani):
    kdv_tutari = urun_fiyati * kdv_orani
    toplam_fiyat = urun_fiyati + kdv_tutari
    planlar = []

    for pesinat in pesinatlar:
        taksitlendirilen_tutar = toplam_fiyat - pesinat
        taksit_farksiz, vade_farksiz_odeme, taksit, toplam_odeme, vade_farki = esit_taksit_hesapla(
            taksitlendirilen_tutar, vade_ay, vade_farksiz_ay, faiz_orani, pesinat
        )
        planlar.append({
            "Ödeme Planı": f"{vade_ay} Ay ({pesinat:,.2f} TL)",
            "Peşinat": f"{pesinat:,.2f} TL",
            "KDV Tutarı": f"{kdv_tutari:,.2f} TL",
            "Taksitlendirilen Tutar": f"{taksitlendirilen_tutar:,.2f} TL",
            "Vade Farksız Ödeme (İlk 3 Ay)": f"{vade_farksiz_odeme:,.2f} TL",
            "Aylık Taksit": f"{taksit:,.2f} TL",
            "Toplam Ödeme": f"{toplam_odeme:,.2f} TL",
            "Toplam Vade Farkı": f"{vade_farki:,.2f} TL"
        })
    return planlar

def tablo_kaydet(planlar, dosya_adi):
    headers = ["Ödeme Planı", "Peşinat", "KDV Tutarı", "Taksitlendirilen Tutar", "Vade Farksız Ödeme (İlk 3 Ay)", "Aylık Taksit", "Toplam Ödeme", "Toplam Vade Farkı"]
    with open(dosya_adi, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for plan in planlar:
            writer.writerow(plan)
    messagebox.showinfo("Başarılı", f"Sonuçlar '{dosya_adi}' dosyasına kaydedildi.")

def hesapla_ve_goster():
    try:
        urun_fiyati = float(entry_urun_fiyati.get() or 99000)
        pesinatlar = [float(x.strip()) for x in entry_pesinatlar.get().split(",") if x.strip()] or [20000, 30000]
        vade_ay = int(vade_var.get())
        kdv_orani = 0.20  # Sabit %20
        vade_farksiz_ay = 3  # Sabit 3 ay
        faiz_orani = 0.065  # Sabit %6.5

        # Tabloyu temizle
        for item in tree.get_children():
            tree.delete(item)

        # Ödeme planını oluştur ve tabloya ekle
        planlar = odeme_plani_olustur(urun_fiyati, kdv_orani, pesinatlar, vade_ay, vade_farksiz_ay, faiz_orani)
        for plan in planlar:
            tree.insert("", "end", values=(
                plan["Ödeme Planı"],
                plan["Peşinat"],
                plan["KDV Tutarı"],
                plan["Taksitlendirilen Tutar"],
                plan["Vade Farksız Ödeme (İlk 3 Ay)"],
                plan["Aylık Taksit"],
                plan["Toplam Ödeme"],
                plan["Toplam Vade Farkı"]
            ))
        
        # CSV kaydetme butonunu etkinleştir
        btn_kaydet.config(state="normal")
        global son_planlar
        son_planlar = planlar

    except ValueError as e:
        messagebox.showerror("Hata", f"Geçersiz giriş! Lütfen doğru formatta değerler girin.\nHata: {e}")

def csv_kaydet():
    if son_planlar:
        dosya_adi = f"odeme_plani_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        tablo_kaydet(son_planlar, dosya_adi)
    else:
        messagebox.showwarning("Uyarı", "Önce ödeme planını hesaplayın!")

# Ana pencere
root = tk.Tk()
root.title("Ödeme Planı Hesaplayıcı")
root.geometry("900x600")

# Giriş alanları
frame_giris = ttk.Frame(root, padding="10")
frame_giris.pack(fill="x")

ttk.Label(frame_giris, text="Ürün Fiyatı (TL, KDV hariç):").grid(row=0, column=0, sticky="w", pady=5)
entry_urun_fiyati = ttk.Entry(frame_giris)
entry_urun_fiyati.insert(0, "99000")
entry_urun_fiyati.grid(row=0, column=1, sticky="ew", pady=5)

ttk.Label(frame_giris, text="KDV Oranı: Sabit %20").grid(row=1, column=0, sticky="w", pady=5)

ttk.Label(frame_giris, text="Peşinatlar (virgülle ayırın, örn: 20000,30000):").grid(row=2, column=0, sticky="w", pady=5)
entry_pesinatlar = ttk.Entry(frame_giris)
entry_pesinatlar.insert(0, "20000,30000")
entry_pesinatlar.grid(row=2, column=1, sticky="ew", pady=5)

ttk.Label(frame_giris, text="Vade Farksız Ay: Sabit 3 Ay").grid(row=3, column=0, sticky="w", pady=5)

ttk.Label(frame_giris, text="Aylık Faiz Oranı: Sabit %6.5").grid(row=4, column=0, sticky="w", pady=5)

ttk.Label(frame_giris, text="Vade Seçimi (Ay):").grid(row=5, column=0, sticky="w", pady=5)
vade_var = tk.StringVar(value="6")  # Varsayılan 6 ay
frame_vade = ttk.Frame(frame_giris)
frame_vade.grid(row=5, column=1, sticky="w", pady=5)
for vade in [3, 6, 9, 12]:
    ttk.Radiobutton(frame_vade, text=f"{vade} Ay", value=str(vade), variable=vade_var).pack(side="left", padx=5)

# Butonlar
frame_butonlar = ttk.Frame(root, padding="10")
frame_butonlar.pack(fill="x")
ttk.Button(frame_butonlar, text="Hesapla", command=hesapla_ve_goster).pack(side="left", padx=5)
btn_kaydet = ttk.Button(frame_butonlar, text="CSV'ye Kaydet", command=csv_kaydet, state="disabled")
btn_kaydet.pack(side="left", padx=5)

# Tablo
frame_tablo = ttk.Frame(root, padding="10")
frame_tablo.pack(fill="both", expand=True)
tree = ttk.Treeview(frame_tablo, columns=("Ödeme Planı", "Peşinat", "KDV Tutarı", "Taksitlendirilen Tutar", "Vade Farksız Ödeme (İlk 3 Ay)", "Aylık Taksit", "Toplam Ödeme", "Toplam Vade Farkı"), show="headings")
tree.heading("Ödeme Planı", text="Ödeme Planı")
tree.heading("Peşinat", text="Peşinat")
tree.heading("KDV Tutarı", text="KDV Tutarı")
tree.heading("Taksitlendirilen Tutar", text="Taksitlendirilen Tutar")
tree.heading("Vade Farksız Ödeme (İlk 3 Ay)", text="Vade Farksız Ödeme (İlk 3 Ay)")
tree.heading("Aylık Taksit", text="Aylık Taksit")
tree.heading("Toplam Ödeme", text="Toplam Ödeme")
tree.heading("Toplam Vade Farkı", text="Toplam Vade Farkı")
tree.column("Ödeme Planı", width=150)
tree.column("Peşinat", width=100)
tree.column("KDV Tutarı", width=100)
tree.column("Taksitlendirilen Tutar", width=150)
tree.column("Vade Farksız Ödeme (İlk 3 Ay)", width=150)
tree.column("Aylık Taksit", width=100)
tree.column("Toplam Ödeme", width=100)
tree.column("Toplam Vade Farkı", width=120)
tree.pack(fill="both", expand=True)

# Global değişken
son_planlar = []

# Ana döngü
root.mainloop()