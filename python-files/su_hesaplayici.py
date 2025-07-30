def su_tuketimi_hesapla():
    """
    Kullanıcının gün içinde içtiği su miktarını hesaplar.
    """
    toplam_su_ml = 0
    print("Su tüketimi hesaplayıcıya hoş geldiniz!")
    print("İçtiğiniz her bardak veya şişe su miktarını (ml olarak) girin.")
    print("Bitirdiğinizde 'bitir' yazıp Enter tuşuna basın.")

    while True:
        giris = input("İçilen su miktarı (ml) veya 'bitir': ")
        if giris.lower() == 'bitir':
            break
        try:
            miktar = float(giris)
            if miktar <= 0:
                print("Lütfen pozitif bir değer girin.")
            else:
                toplam_su_ml += miktar
                print(f"Güncel toplam: {toplam_su_ml / 1000:.2f} litre")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı veya 'bitir' yazın.")

    toplam_su_litre = toplam_su_ml / 1000
    print(f"\nGün boyunca toplam {toplam_su_litre:.2f} litre su içtiniz.")

    # Ortalama önerilen su miktarını kıyaslama (genel bir rehberdir)
    onerilen_su_litre = 2.5 # Ortalama yetişkin için genel öneri

    if toplam_su_litre < onerilen_su_litre:
        fark = onerilen_su_litre - toplam_su_litre
        print(f"Önerilen günlük {onerilen_su_litre:.1f} litre hedefine ulaşmak için {fark:.2f} litre daha suya ihtiyacınız var.")
    elif toplam_su_litre > onerilen_su_litre + 0.5: # Küçük bir marj bırakıyoruz
        print("Harika! Önerilen günlük su alım miktarını aştınız. Hidrasyonunuz iyi görünüyor.")
    else:
        print("Önerilen günlük su alım hedefinize ulaştınız. Tebrikler!")

# Programı çalıştırmak için
su_tuketimi_hesapla()