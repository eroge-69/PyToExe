from datetime import datetime

def kiymet_takdiri_uygulamasi():
    """
    KIYMET TAKDİRİ uygulaması: Hayvanın yaşını ve kasaplık/damızlık durumunu kontrol eder.
    """
    print("--- KIYMET TAKDİRİ Uygulamasına Hoş Geldiniz ---")
    
    while True:
        try:
            # Kullanıcıdan doğum tarihini istiyoruz.
            dogum_tarihi_str = input("Hayvanın doğum tarihini 'GG.AA.YYYY' formatında girin (Örn: 15.05.2020) veya çıkmak için 'cikis' yazın: ")
            
            if dogum_tarihi_str.lower() == 'cikis':
                print("Uygulamadan çıkılıyor...")
                break

            # Cinsiyet bilgisini alıyoruz.
            cinsiyet = input("Hayvanın cinsiyetini girin (E/e için erkek, D/d için dişi): ").lower()
            if cinsiyet not in ('e', 'd'):
                print("Geçersiz cinsiyet girişi. Lütfen 'e' veya 'd' girin.")
                continue

            # Hedef tarihi istiyoruz.
            hedef_tarih_str = input("Kıymet Takdiri Yapılacak tarihi 'GG.AA.YYYY' formatında girin (Örn: 05.08.2025): ")
            
            # Girilen tarih stringlerini datetime objelerine dönüştürüyoruz.
            dogum_tarihi = datetime.strptime(dogum_tarihi_str, "%d.%m.%Y")
            hedef_tarihi = datetime.strptime(hedef_tarih_str, "%d.%m.%Y")

            # Hedef tarihin doğum tarihinden sonra olup olmadığını kontrol ediyoruz.
            if hedef_tarihi < dogum_tarihi:
                print("Hedef tarih, doğum tarihinden önce olamaz. Lütfen geçerli bir tarih girin.")
                continue

            # Yaş hesaplaması yapıyoruz.
            gecen_sure = hedef_tarihi - dogum_tarihi
            toplam_gun = gecen_sure.days
            aylik_yas = toplam_gun / 30.44

            # Kasaplık veya damızlık durumunu kontrol ediyoruz.
            durum = ""
            if cinsiyet == 'd':
                if aylik_yas > 96:
                    durum = "BU HAYVAN KASAPLIKTIR(MANDALAR HARİÇ)"
                else:
                    durum = "DAMIZLIK DEĞERİ VARDIR"
            elif cinsiyet == 'e':
                if aylik_yas > 24:
                    durum = "BU HAYVAN KASAPLIKTIR"
                else:
                    durum = "DAMIZLIK DEĞERİ VARDIR"

            # Sonuçları ekrana yazdırıyoruz.
            print(f"\nHayvan, {hedef_tarih_str} yapılacak kıymet takdiri çalışması tarihinde yaklaşık {aylik_yas:.2f} aylıktır.")
            print(f"Cinsiyeti: {'Dişi' if cinsiyet == 'd' else 'Erkek'}")
            print(f"Yaş durumuna Göre: {durum}")
            
        except ValueError:
            print("Hatalı format veya geçersiz tarih girdiniz. Lütfen 'GG.AA.YYYY' formatını kullanın.")
        
        print("-" * 50)  # Ayırıcı çizgi

# Uygulamayı başlatıyoruz.
kiymet_takdiri_uygulamasi()