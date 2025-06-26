from scraper_skyscanner import get_flight_price
from notifier import send_email, send_popup

def main():
    gidis = input("Gidiş tarihi (yyMMdd): ")
    donus = input("Dönüş tarihi (yyMMdd): ")
    kisi_sayisi = int(input("Kişi sayısı: "))
    fiyat_esigi = int(input("Kişi başı max fiyat (₺): "))
    bildirim_tipi = input("Bildirim tipi (popup/email): ").lower()

    if bildirim_tipi == "email":
        gonderici = input("Gönderici Gmail adresi: ")
        sifre = input("Gmail uygulama şifresi: ")
        alici = input("Alıcı e-posta adresi: ")

    toplam_esik = fiyat_esigi * kisi_sayisi
    fiyat = get_flight_price(gidis, donus, kisi_sayisi)

    if fiyat:
        print(f"Bulunan toplam fiyat: {fiyat}₺")
        if fiyat <= toplam_esik:
            mesaj = f"Uçak bileti kişi başı {fiyat//kisi_sayisi}₺ (Toplam: {fiyat}₺)"
            if bildirim_tipi == "popup":
                send_popup("Uygun Fiyat!", mesaj)
            elif bildirim_tipi == "email":
                send_email(gonderici, sifre, alici, "Uçak Bileti Uyarı", mesaj)
        else:
            print("Fiyat eşik üzerinde.")
    else:
        print("Fiyat bilgisi alınamadı.")

if __name__ == "__main__":
    main()
