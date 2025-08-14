import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime

# Verileri saklamak i�in bo� tablolar
satislar = pd.DataFrame(columns=["Tarih", "M��teri", "��lem", "Tutar (?)", "A��klama"])
giderler = pd.DataFrame(columns=["Gider T�r�", "Tutar (?)"])

# Pencere olu�tur
pencere = tk.Tk()
pencere.title("D�kkan Otomasyonu")
pencere.geometry("500x400")

# Sat�� Ekleme Fonksiyonu
def satis_ekle():
    tarih = tarih_entry.get()
    musteri = musteri_entry.get()
    islem = islem_entry.get()
    tutar = tutar_entry.get()
    aciklama = aciklama_entry.get()
    
    satislar.loc[len(satislar)] = [tarih, musteri, islem, tutar, aciklama]
    messagebox.showinfo("Ba�ar�l�", "Sat�� kaydedildi!")

# Aray�z Elemanlar�
tk.Label(pencere, text="Tarih:").pack()
tarih_entry = tk.Entry(pencere)
tarih_entry.pack()
tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

tk.Label(pencere, text="M��teri:").pack()
musteri_entry = tk.Entry(pencere)
musteri_entry.pack()

tk.Label(pencere, text="��lem T�r�:").pack()
islem_entry = tk.Entry(pencere)
islem_entry.pack()

tk.Label(pencere, text="Tutar (?):").pack()
tutar_entry = tk.Entry(pencere)
tutar_entry.pack()

tk.Label(pencere, text="A��klama:").pack()
aciklama_entry = tk.Entry(pencere)
aciklama_entry.pack()

tk.Button(pencere, text="Sat�� Ekle", command=satis_ekle).pack()

pencere.mainloop()