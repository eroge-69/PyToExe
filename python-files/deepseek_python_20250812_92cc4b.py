import tkinter as tk
import time
from tkinter import font as tkfont

def saati_guncelle():
    # Saat ve dakika bilgilerini al
    su_an = time.localtime()
    saat = su_an.tm_hour
    dakika = su_an.tm_min
    saniye = su_an.tm_sec
    
    # Dijital saat formatı
    dijital_saat = f"{saat:02d}:{dakika:02d}:{saniye:02d}"
    dijital_label.config(text=dijital_saat)
    
    # Türkçe okunuş
    saatler = [
        "on iki", "bir", "iki", "üç", "dört", "beş", "altı", 
        "yedi", "sekiz", "dokuz", "on", "on bir", "on iki"
    ]
    
    dakikalar = [
        "", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
        "on bir", "on iki", "on üç", "on dört", "on beş", "on altı", "on yedi", 
        "on sekiz", "on dokuz", "yirmi", "yirmi bir", "yirmi iki", "yirmi üç", 
        "yirmi dört", "yirmi beş", "yirmi altı", "yirmi yedi", "yirmi sekiz", 
        "yirmi dokuz", "otuz", "otuz bir", "otuz iki", "otuz üç", "otuz dört", 
        "otuz beş", "otuz altı", "otuz yedi", "otuz sekiz", "otuz dokuz", "kırk", 
        "kırk bir", "kırk iki", "kırk üç", "kırk dört", "kırk beş", "kırk altı", 
        "kırk yedi", "kırk sekiz", "kırk dokuz", "elli", "elli bir", "elli iki", 
        "elli üç", "elli dört", "elli beş", "elli altı", "elli yedi", "elli sekiz", 
        "elli dokuz"
    ]
    
    saat_index = saat % 12
    if dakika == 0:
        okunus = f"Saat {saatler[saat_index]}"
    else:
        okunus = f"Saat {saatler[saat_index]} {dakikalar[dakika]}"
    
    okunus_label.config(text=okunus)
    
    # Her saniyede bir güncelle
    pencere.after(1000, saati_guncelle)

# Pencereyi oluştur (masaüstü widget gibi)
pencere = tk.Tk()
pencere.title("Saat Widget")
pencere.attributes('-alpha', 0.85)  # Yarı saydamlık
pencere.attributes('-topmost', True)  # Her zaman üstte
pencere.overrideredirect(True)  # Pencere çerçevesi olmadan

# Özel fontlar
dijital_font = tkfont.Font(family='Consolas', size=24, weight='bold')
okunus_font = tkfont.Font(family='Arial', size=14)

# Dijital saat etiketi
dijital_label = tk.Label(pencere, font=dijital_font, fg='white', bg='black')
dijital_label.pack(padx=10, pady=5)

# Okunuş etiketi
okunus_label = tk.Label(pencere, font=okunus_font, fg='white', bg='black')
okunus_label.pack(padx=10, pady=5)

# Arkaplan rengi
pencere.configure(bg='black')

# Pencereyi sürüklemek için
def bas(event):
    pencere._offsetx = event.x
    pencere._offsety = event.y

def surukle(event):
    x = pencere.winfo_pointerx() - pencere._offsetx
    y = pencere.winfo_pointery() - pencere._offsety
    pencere.geometry(f"+{x}+{y}")

pencere.bind('<Button-1>', bas)
pencere.bind('<B1-Motion>', surukle)

# Saati başlat
saati_guncelle()

# Pencereyi ekranın sağ üst köşesine yerleştir
ekran_genislik = pencere.winfo_screenwidth()
pencere.geometry(f"+{ekran_genislik-300}+20")

pencere.mainloop()