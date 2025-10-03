import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime

CSV_FILE = 'stok_kaydi.csv'

# CSV yoksa oluştur
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Ürün Adı", "Kategori", "Geliş Fiyatı", "Satış Fiyatı", "Stok Adedi", "Geliş Tarihi"
    ])
    df.to_csv(CSV_FILE, index=False)

# Ürün ekleme fonksiyonu
def urun_ekle():
    urun_adi = entry_urun_adi.get()
    kategori = entry_kategori.get()
    gelis_fiyati = entry_gelis_fiyati.get()
    satis_fiyati = entry_satis_fiyati.get()
    stok_adedi = entry_stok_adedi.get()
    gelis_tarihi = entry_gelis_tarihi.get()

    if not (urun_adi and kategori and gelis_fiyati and satis_fiyati and stok_adedi and gelis_tarihi):
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
        return

    try:
        yeni_kayit = pd.DataFrame([{
            "Ürün Adı": urun_adi,
            "Kategori": kategori,
            "Geliş Fiyatı": float(gelis_fiyati),
            "Satış Fiyatı": float(satis_fiyati),
            "Stok Adedi": int(stok_adedi),
            "Geliş Tarihi": gelis_tarihi
        }])
        yeni_kayit.to_csv(CSV_FILE, mode='a', header=False, index=False)
        messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi.")
        listele()
        temizle()
    except Exception as e:
        messagebox.showerror("Hata", f"Veri eklenemedi: {e}")

# Listele
def listele():
    for widget in frame_liste.winfo_children():
        widget.destroy()

    df = pd.read_csv(CSV_FILE)
    for i, col in enumerate(df.columns):
        tk.Label(frame_liste, text=col, bg="lightgray", width=15).grid(row=0, column=i)

    for row_index, row in df.iterrows():
        for col_index, value in enumerate(row):
            tk.Label(frame_liste, text=value, width=15).grid(row=row_index+1, column=col_index)

# Temizle
def temizle():
    entry_urun_adi.delete(0, tk.END)
    entry_kategori.delete(0, tk.END)
    entry_gelis_fiyati.delete(0, tk.END)
    entry_satis_fiyati.delete(0, tk.END)
    entry_stok_adedi.delete(0, tk.END)
    entry_gelis_tarihi.delete(0, tk.END)
    entry_gelis_tarihi.insert(0, datetime.today().strftime('%Y-%m-%d'))

# Arayüz
root = tk.Tk()
root.title("Takı Dükkanı - Stok Takip Programı")

# Form Alanları
tk.Label(root, text="Ürün Adı").grid(row=0, column=0)
entry_urun_adi = tk.Entry(root)
entry_urun_adi.grid(row=0, column=1)

tk.Label(root, text="Kategori").grid(row=1, column=0)
entry_kategori = tk.Entry(root)
entry_kategori.grid(row=1, column=1)

tk.Label(root, text="Geliş Fiyatı").grid(row=2, column=0)
entry_gelis_fiyati = tk.Entry(root)
entry_gelis_fiyati.grid(row=2, column=1)

tk.Label(root, text="Satış Fiyatı").grid(row=3, column=0)
entry_satis_fiyati = tk.Entry(root)
entry_satis_fiyati.grid(row=3, column=1)

tk.Label(root, text="Stok Adedi").grid(row=4, column=0)
entry_stok_adedi = tk.Entry(root)
entry_stok_adedi.grid(row=4, column=1)

tk.Label(root, text="Geliş Tarihi").grid(row=5, column=0)
entry_gelis_tarihi = tk.Entry(root)
entry_gelis_tarihi.grid(row=5, column=1)
entry_gelis_tarihi.insert(0, datetime.today().strftime('%Y-%m-%d'))

# Buton
tk.Button(root, text="Ürünü Ekle", command=urun_ekle, bg="lightblue").grid(row=6, column=0, columnspan=2, pady=10)

# Listeleme alanı
frame_liste = tk.Frame(root)
frame_liste.grid(row=7, column=0, columnspan=2)
listele()

root.mainloop()
