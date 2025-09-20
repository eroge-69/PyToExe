import customtkinter as ctk
from datetime import datetime

# Yaş hesaplama fonksiyonu
def yaş_hesapla():
    try:
        doğum_tarihi = datetime.strptime(doğum_tarihi_giriş.get(), "%Y-%m-%d")
        şimdiki_tarih = datetime.strptime(şimdiki_tarih_giriş.get(), "%Y-%m-%d")
        
        yaş = şimdiki_tarih - doğum_tarihi
        
        # Başarılı hesaplama durumunda metin ve rengini güncelle
        sonuç_etiketi.configure(
            text=f"Yaşınız: {yaş.days // 365} yıl, {yaş.days % 365} gün", 
            text_color="green" # Başarılı sonuç için yeşil renk
        )
    except ValueError:
        # Hata durumunda metin ve rengini güncelle
        sonuç_etiketi.configure(
            text="Lütfen geçerli bir tarih giriniz (YYYY-MM-DD)", 
            text_color="red" # Hata mesajı için kırmızı renk
        )

# Uygulama penceresini oluştur
uygulama = ctk.CTk()
uygulama.resizable(False,False)
uygulama.title("Yaş Hesaplayıcı")
uygulama.geometry("400x200")

# Giriş kutusu etiketleri ve yerleşimi
dogum_etiketi = ctk.CTkLabel(uygulama, text="Doğum tarihinizi giriniz (YYYY-MM-DD):")
dogum_etiketi.grid(column=0, row=0, padx=10, pady=10, sticky="w")

doğum_tarihi_giriş = ctk.CTkEntry(uygulama, corner_radius=10)
doğum_tarihi_giriş.grid(column=1, row=0, padx=10, pady=10)

simdiki_etiketi = ctk.CTkLabel(uygulama, text="Hesaplama tarihi giriniz (YYYY-MM-DD):")
simdiki_etiketi