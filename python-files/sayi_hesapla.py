import tkinter as tk
from tkinter import messagebox

def hesapla():
    try:
        ana_sayi = float(entry_ana_sayi.get())
        ikinci_sayi = float(entry_ikinci_sayi.get())

        sonuc1 = ana_sayi + (ikinci_sayi * 2)
        sonuc2 = ana_sayi - (ikinci_sayi * 2)
        sonuc3 = ana_sayi + (ikinci_sayi * 3)
        sonuc4 = ana_sayi - (ikinci_sayi * 3)

        label_sonuc1.config(text=f"Ana + (2 x sayı) = {sonuc1}")
        label_sonuc2.config(text=f"Ana - (2 x sayı) = {sonuc2}")
        label_sonuc3.config(text=f"Ana + (3 x sayı) = {sonuc3}")
        label_sonuc4.config(text=f"Ana - (3 x sayı) = {sonuc4}")

    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli sayılar girin.")

# Pencere oluştur
pencere = tk.Tk()
pencere.title("Sayı İşlem Hesaplayıcı")
pencere.geometry("300x250")

# Giriş kutuları
tk.Label(pencere, text="Ana Sayı:").pack()
entry_ana_sayi = tk.Entry(pencere)
entry_ana_sayi.pack()

tk.Label(pencere, text="İkinci Sayı:").pack()
entry_ikinci_sayi = tk.Entry(pencere)
entry_ikinci_sayi.pack()

# Hesapla butonu
tk.Button(pencere, text="Hesapla", command=hesapla).pack(pady=10)

# Sonuçlar
label_sonuc1 = tk.Label(pencere, text="")
label_sonuc1.pack()
label_sonuc2 = tk.Label(pencere, text="")
label_sonuc2.pack()
label_sonuc3 = tk.Label(pencere, text="")
label_sonuc3.pack()
label_sonuc4 = tk.Label(pencere, text="")
label_sonuc4.pack()

# Pencereyi çalıştır
pencere.mainloop()
