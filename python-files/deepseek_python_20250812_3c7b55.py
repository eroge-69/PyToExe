import tkinter as tk
import time
from datetime import datetime

def saati_okunusa_cevir():
    simdi = datetime.now()
    saat = simdi.hour
    dakika = simdi.minute
    
    saat_sozcukleri = [
        "sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
        "on bir", "on iki", "on üç", "on dört", "on beş", "on altı", "on yedi", "on sekiz", "on dokuz", "yirmi",
        "yirmi bir", "yirmi iki", "yirmi üç"
    ]
    
    dakika_sozcukleri = [
        "sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
        "on bir", "on iki", "on üç", "on dört", "on beş", "on altı", "on yedi", "on sekiz", "on dokuz", "yirmi",
        "yirmi bir", "yirmi iki", "yirmi üç", "yirmi dört", "yirmi beş", "yirmi altı", "yirmi yedi", "yirmi sekiz", "yirmi dokuz", "otuz",
        "otuz bir", "otuz iki", "otuz üç", "otuz dört", "otuz beş", "otuz altı", "otuz yedi", "otuz sekiz", "otuz dokuz", "kırk",
        "kırk bir", "kırk iki", "kırk üç", "kırk dört", "kırk beş", "kırk altı", "kırk yedi", "kırk sekiz", "kırk dokuz", "elli",
        "elli bir", "elli iki", "elli üç", "elli dört", "elli beş", "elli altı", "elli yedi", "elli sekiz", "elli dokuz"
    ]
    
    okunus = f"{saat_sozcukleri[saat]} {dakika_sozcukleri[dakika]}"
    return okunus

def saati_guncelle():
    simdi = time.strftime("%H:%M:%S")
    okunus = saati_okunusa_cevir()
    digital_saat.config(text=simdi)
    okunus_saat.config(text=okunus)
    root.after(1000, saati_guncelle)

# Ana pencereyi oluştur
root = tk.Tk()
root.title("Saat Okunuşu")
root.geometry("300x150")

# Dijital saat etiketi
digital_saat = tk.Label(root, font=('Helvetica', 24), fg='blue')
digital_saat.pack(pady=10)

# Okunuş etiketi
okunus_saat = tk.Label(root, font=('Helvetica', 18), fg='green')
okunus_saat.pack(pady=10)

# Saati güncellemeyi başlat
saati_guncelle()

# Pencereyi çalıştır
root.mainloop()