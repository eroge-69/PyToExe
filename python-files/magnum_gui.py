import tkinter as tk
from tkinter import messagebox
import random
import string

def rastgele_sifre_uret(uzunluk=8):
    karakterler = string.ascii_uppercase + string.digits
    return ''.join(random.choices(karakterler, k=uzunluk))

def sifre_uret():
    try:
        adet = int(giris_adet.get())
        sifreler = [rastgele_sifre_uret() for _ in range(adet)]
        cikti.delete('1.0', tk.END)
        for sifre in sifreler:
            cikti.insert(tk.END, sifre + "\n")
    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")

pencere = tk.Tk()
pencere.title("Magnum Şifre Üretici (GUI)")

etiket = tk.Label(pencere, text="Kaç adet şifre üretmek istiyorsun?")
etiket.pack(pady=10)

giris_adet = tk.Entry(pencere)
giris_adet.pack()

buton = tk.Button(pencere, text="Şifreleri Üret", command=sifre_uret)
buton.pack(pady=10)

cikti = tk.Text(pencere, height=15, width=40)
cikti.pack()

pencere.mainloop()
