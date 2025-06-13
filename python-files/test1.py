import tkinter as tk
from tkinter import ttk

def sadece_sayi_girisi(k):
    return k.isdigit() or k == ""

def hesapla():
    global kullanici_sayisi
    kullanici_sayisi = girdi.get()  # Kullanıcı girişini kaydet
    if kullanici_sayisi == "":
        # Boşsa işlem yapma veya uyarı verebilirsin
        return
    progressbar['value'] = 0
    hesaplanıyor_label.pack(pady=10)
    progressbar.pack(pady=5)
    ilerlet(0)

def ilerlet(deger):
    if deger <= 100:
        progressbar['value'] = deger
        pencere.update_idletasks()
        pencere.after(40, ilerlet, deger+1)
    else:
        # Dolum tamamlandığında arayüzü temizle
        for widget in pencere.winfo_children():
            widget.destroy()

        # "düşündüğünüz sayı" etiketi
        tahmin_label = tk.Label(
            pencere,
            text="düşündüğünüz sayı",
            bg="gray",
            fg="white",
            font=("Arial", 16, "bold"),
            padx=20,
            pady=10
        )
        tahmin_label.pack(pady=(100,10))

        # Kullanıcının ilk girdiği sayıyı gösteren yeni etiket
        sayi_label = tk.Label(
            pencere,
            text=kullanici_sayisi,
            bg="gray",
            fg="white",
            font=("Arial", 20, "bold"),
            padx=20,
            pady=10
        )
        sayi_label.pack()

# Pencereyi oluştur
pencere = tk.Tk()
pencere.title("tahmin v2.4.3.6.3.3.34.5")
pencere.geometry("300x300")

yazi_fontu = ("Arial", 14, "bold")

etiket = tk.Label(
    pencere,
    text="bir sayı düşünün",
    bg="gray",
    fg="white",
    font=yazi_fontu
)
etiket.pack(pady=40)

vcmd = pencere.register(sadece_sayi_girisi)
girdi = tk.Entry(
    pencere,
    validate="key",
    validatecommand=(vcmd, "%P"),
    font=("Arial", 12)
)
girdi.pack(pady=10)

buton = tk.Button(
    pencere,
    text="hesapla",
    bg="gray",
    fg="white",
    font=("Arial", 12, "bold"),
    command=hesapla
)
buton.pack(pady=10)

hesaplanıyor_label = tk.Label(
    pencere,
    text="hesaplanıyor",
    bg="gray",
    fg="white",
    font=("Arial", 12, "bold")
)

style = ttk.Style()
style.theme_use('clam')
style.configure("gray.Horizontal.TProgressbar", troughcolor='gray', background='white')

progressbar = ttk.Progressbar(
    pencere,
    style="gray.Horizontal.TProgressbar",
    orient="horizontal",
    length=250,
    mode="determinate",
    maximum=100
)

pencere.mainloop()
