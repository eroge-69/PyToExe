import random
from collections import defaultdict

# 🧠 Hafıza: çekilen sayıların frekansı
hafiza = defaultdict(int)
toplam_giris = 0

# 🔸 Sayı girişi fonksiyonu
def sayi_ekle(sayi_listesi):
    global toplam_giris
    for s in sayi_listesi:
        if 1 <= s <= 90:
            hafiza[s] += 1
            toplam_giris += 1
        else:
            print(f"Hatalı sayı: {s} (1–90 arasında olmalı)")

# 🔸 Olasılık hesaplama (Laplace düzeltmeli)
def olasilik_hesapla():
    return {s: (hafiza[s] + 1) / (toplam_giris + 90) for s in range(1, 91)}

# 🔸 Ağırlıklı rastgele tahmin
def tahmin_yap():
    olasiliklar = olasilik_hesapla()
    sayilar, agirliklar = zip(*olasiliklar.items())
    tahmin = random.choices(sayilar, weights=agirliklar, k=6)
    tahmin = sorted(set(tahmin))  # tekrarları engelle
    analiz_et(tahmin)

# 🔸 Tahmin analizi
def analiz_et(sayilar):
    print("\n🎯 Tahmin edilen sayılar:", sayilar)
    cift = sum(1 for s in sayilar if s % 2 == 0)
    tek = len(sayilar) - cift
    print(f"🧮 Çift: {cift}, Tek: {tek}")

    # Sıralı üçlü uyarısı
    for s in sayilar:
        if s+1 in sayilar and s+2 in sayilar:
            print(f"⚠️ Sıralı üçlü tespiti: {s}, {s+1}, {s+2}")

    # Frekans bilgisi
    for s in sayilar:
        print(f"🔢 {s}: {hafiza[s]} kez görülmüş")

# 🔍 Örnek kullanım:
if __name__ == "__main__":
    # 📝 Geçmiş çekiliş verileri giriliyor
    sayi_ekle([7, 14, 23, 45, 66, 77])
    sayi_ekle([3, 14, 23, 42, 66, 90])