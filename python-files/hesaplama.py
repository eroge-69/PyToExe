def karisim_hesapla(recine_miktari, oranlar):
    toplam_oran = 1 - sum(oranlar) / 100
    if toplam_oran <= 0:
        print("❌ Toplam oran %100'ü aşamaz!")
        return

    toplam_cozelti = recine_miktari / toplam_oran
    print(f"\n🔍 Toplam çözelti miktarı: {toplam_cozelti:.2f} g\n")

    for i, oran in enumerate(oranlar, start=1):
        malzeme_gram = (oran / 100) * toplam_cozelti
        print(f"Malzeme {i}: {malzeme_gram:.2f} g (%{oran})")

    print(f"\nReçine: {recine_miktari:.2f} g")

# Kullanıcıdan veri al
try:
    recine = float(input("Reçine miktarını girin (gram): "))
    malzeme_sayisi = int(input("Kaç malzeme eklenecek?: "))

    oranlar = []
    for i in range(malzeme_sayisi):
        oran = float(input(f"{i+1}. malzemenin yüzde oranı (%): "))
        oranlar.append(oran)

    karisim_hesapla(recine, oranlar)

except ValueError:
    print("❌ Lütfen geçerli sayısal değerler girin.")
