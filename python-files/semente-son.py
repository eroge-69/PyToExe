import math

# Numara ↔ çelik tipi eşleştirmesi
cementation_steels = {
    1: "16MnCr5",
    2: "20MnCr5",
    3: "18CrNiMo7-6",
    4: "20NiCrMo2-2 (8620)",
    5: "18NiCrMo4 (9310)",
    6: "17NiCr",
    7: "15CrNi6",
    8: "16NiCr4",
    9: "18NiCr5-4",
    10: "17CrNi6-6",
    11: "15NiCr13",
    12: "18CrMo4",
    13: "18NiCrMo14-6",
}

# Her çelik türü için 900–950 °C aralığındaki pratik k katsayıları (mm/√saat)
k_values = {
    "16MnCr5": [(900, 950, 0.30)],
    "20MnCr5": [(900, 950, 0.30)],
    "18CrNiMo7-6": [(900, 950, 0.32)],
    "20NiCrMo2-2 (8620)": [(900, 950, 0.33)],
    "18NiCrMo4 (9310)": [(900, 950, 0.35)],
    "17NiCr": [(900, 950, 0.31)],
    "15CrNi6": [(900, 950, 0.32)],
    "16NiCr4": [(900, 950, 0.30)],
    "18NiCr5-4": [(900, 950, 0.31)],
    "17CrNi6-6": [(900, 950, 0.32)],
    "15NiCr13": [(900, 950, 0.33)],
    "18CrMo4": [(900, 950, 0.29)],
    "18NiCrMo14-6": [(900, 950, 0.34)],
}

def find_k(celik_tipi, sicaklik):
    for alt, ust, k in k_values.get(celik_tipi, []):
        if alt <= sicaklik < ust:
            return k
    return None

def hesapla_sure_lira(celik_tipi, sicaklik_C, derinlik_mm):
    if celik_tipi not in k_values:
        raise ValueError("Geçersiz çelik türü seçildi.")
    k = find_k(celik_tipi, sicaklik_C)
    if k is None:
        raise ValueError(f"{çelik_tipi} için {sicaklik_C} °C aralığında k değeri tanımlı değil.")
    # Süre (saat cinsinden decimal)
    t_saat = (derinlik_mm / k) ** 2
    # Tam saat ve kalan dakikayı hesapla
    tam_saat = int(t_saat)
    kalan_saat = t_saat - tam_saat
    dakika = int(round(kalan_saat * 60))

    # Eğer dakika 60'a eşit ise, bir sonraki saate aktar
    if dakika == 60:
        tam_saat += 1
        dakika = 0

    return k, t_saat, tam_saat, dakika

if __name__ == "__main__":
    print("Numaralı Sementasyon Çelikleri Listesi:")
    for no, isim in cementation_steels.items():
        print(f"{no}. {isim}")

    try:
        secim = int(input("Çelik tipi numarasını girin (1‑13): "))
        celik_tipi = cementation_steels[secim]
    except (KeyError, ValueError):
        print("Geçersiz seçim.")
        exit()

    try:
        sicaklik = float(input("Sıcaklık (°C): "))
        derinlik = float(input("Hedef derinlik (mm): "))
    except ValueError:
        print("Lütfen geçerli sayısal değerler girin.")
        exit()

    try:
        k, sure_decimal, saat, dakika = hesapla_sure_lira(celik_tipi, sicaklik, derinlik)
        print("\n--- Hesaplama Sonucu ---")
        print(f"Çelik Tipi        : {celik_tipi}")
        print(f"Sıcaklık          : {sicaklik:.1f} °C")
        print(f"Derinlik          : {derinlik:.2f} mm")
        print(f"Yaklaşık k değeri : {k:.2f} mm/√saat")
        print(f"Proses Süresi     : {sure_decimal:.2f} saat ({saat} saat {dakika} dakika)")
    except ValueError as e:
        print("Hata:", e)
