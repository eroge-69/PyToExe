def vki_hesapla():
    boy = float(input("Boyunuzu metre cinsinden girin (örn: 1.75): "))
    if boy > 3 or boy < 0.1:
        return vki_hesapla()
    # Kullanıcıdan kilo bilgisi al
    # Kilo bilgisi kilogram cinsinden alınacak
    kilo = float(input("Kilonuzu kilogram cinsinden girin (örn: 70): "))
    if kilo < 20 or kilo > 300:
        return vki_hesapla()
    # Vücut Kitle İndeksi (VKİ) hesaplama
    # VKİ
    vki = kilo / (boy ** 2)

    print("Vücut Kitle İndeksiniz (VKİ):", round(vki, 2))

    # Opsiyonel: VKİ'ye göre sınıflandırma
    if vki < 18.5:
        print("Zayıf")
    elif 18.5 <= vki < 25:
        print("Normal kilolu")
    elif 25 <= vki < 30:
        print("Fazla kilolu")
    else:
        print("Obez")


vki_hesapla()
# Bu kod, kullanıcı tarafından  