import csv
from datetime import datetime, timedelta

# CSV dosyası
REZERVASYON_DOSYA = "rezervasyonlar.csv"
ODALAR = ['Oda 101', 'Oda 102', 'Oda 103', 'Oda 104', 'Oda 105']

# Dosya kontrol ve başlık ekleme
def dosya_kontrol():
    try:
        with open(REZERVASYON_DOSYA, 'r', newline='') as f:
            pass
    except FileNotFoundError:
        with open(REZERVASYON_DOSYA, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Misafir Adı", "Giriş Tarihi", "Çıkış Tarihi", "Oda", "Kişi Sayısı", "Ödeme Durumu", "Tutar (₺)"])

# Rezervasyon ekleme
def rezervasyon_ekle():
    misafir = input("Misafir Adı Soyadı: ")
    giris = input("Giriş Tarihi (YYYY-MM-DD): ")
    cikis = input("Çıkış Tarihi (YYYY-MM-DD): ")
    print("Mevcut odalar:", ODALAR)
    oda = input("Oda Numarası: ")
    kisi = input("Kişi Sayısı: ")
    odeme = input("Ödeme Durumu (Ödendi / Beklemede): ")
    tutar = input("Tutar (₺): ")

    with open(REZERVASYON_DOSYA, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([misafir, giris, cikis, oda, kisi, odeme, tutar])
    print("Rezervasyon başarıyla eklendi!\n")

# Doluluk durumu görüntüleme
def doluluk_goruntule():
    tarih = input("Doluluk için tarih girin (YYYY-MM-DD): ")
    tarih_dt = datetime.strptime(tarih, "%Y-%m-%d")
    dolu_odalar = []
    with open(REZERVASYON_DOSYA, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            giris = datetime.strptime(row["Giriş Tarihi"], "%Y-%m-%d")
            cikis = datetime.strptime(row["Çıkış Tarihi"], "%Y-%m-%d")
            if giris <= tarih_dt < cikis:
                dolu_odalar.append(row["Oda"])
    print(f"{tarih} tarihinde dolu odalar: {dolu_odalar}\n")

# Gelir raporu
def gelir_raporu():
    toplam = 0
    with open(REZERVASYON_DOSYA, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            toplam += float(row["Tutar (₺)"])
    print(f"Toplam gelir: ₺{toplam}\n")

# Menü
def menu():
    dosya_kontrol()
    while True:
        print("1- Rezervasyon Ekle")
        print("2- Doluluk Durumu Görüntüle")
        print("3- Gelir Raporu")
        print("4- Çıkış")
        secim = input("Seçiminiz: ")
        if secim == '1':
            rezervasyon_ekle()
        elif secim == '2':
            doluluk_goruntule()
        elif secim == '3':
            gelir_raporu()
        elif secim == '4':
            break
        else:
            print("Geçersiz seçenek!")

if __name__ == "__main__":
    menu()
