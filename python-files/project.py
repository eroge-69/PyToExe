
import pandas as pd
import os

DOSYA_ADI = "urunler.xlsx"

# Açılış mesajı
print("""
***************************************
  ÜRÜN TAKİP OTOMASYONU - v1.0
  Geliştirici: Halilcan Elitok
***************************************
""")

# Excel dosyasını yükle veya boş bir DataFrame oluştur
if os.path.exists(DOSYA_ADI):
    df = pd.read_excel(DOSYA_ADI)
else:
    df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Fiyat", "Stok Miktarı", "Açıklama"])

# 1. Ürünleri listele
def urunleri_listele():
    print("\n📦 Mevcut Ürünler:")
    print(df.to_string(index=False))

# 2. Yeni ürün ekle
def yeni_urun_ekle():
    urun = {
        "Ürün Kodu": input("Ürün Kodu: "),
        "Ürün Adı": input("Ürün Adı: "),
        "Fiyat": float(input("Fiyat: ")),
        "Stok Miktarı": int(input("Stok Miktarı: ")),
        "Açıklama": input("Açıklama: ")
    }
    global df
    df = df.append(urun, ignore_index=True)
    print("✅ Ürün eklendi.")

# 3. Stok güncelle
def stok_guncelle():
    kod = input("Stok güncellenecek ürün kodu: ")
    miktar = int(input("Yeni stok miktarı: "))
    if kod in df["Ürün Kodu"].values:
        df.loc[df["Ürün Kodu"] == kod, "Stok Miktarı"] = miktar
        print("✅ Stok güncellendi.")
    else:
        print("❌ Ürün kodu bulunamadı.")

# 4. Stokta olan ürünleri listele
def stokta_olanlar():
    mevcut = df[df["Stok Miktarı"] > 0]
    print("\n📦 Stokta Olan Ürünler:")
    print(mevcut.to_string(index=False))

# 5. Ürün sil
def urun_sil():
    kod = input("Silinecek ürün kodu: ")
    global df
    if kod in df["Ürün Kodu"].values:
        df = df[df["Ürün Kodu"] != kod]
        print("🗑️ Ürün silindi.")
    else:
        print("❌ Ürün bulunamadı.")

# 6. Excel'e kaydet
def veriyi_kaydet():
    df.to_excel(DOSYA_ADI, index=False)
    print(f"💾 Excel dosyasına kaydedildi: {DOSYA_ADI}")

# Menü
while True:
    print("\n--- ÜRÜN OTOMASYONU ---")
    print("1. Ürünleri Listele")
    print("2. Yeni Ürün Ekle")
    print("3. Stok Güncelle")
    print("4. Stokta Olanları Göster")
    print("5. Ürün Sil")
    print("6. Kaydet ve Çık")
    secim = input("Seçim (1-6): ")

    if secim == "1":
        urunleri_listele()
    elif secim == "2":
        yeni_urun_ekle()
    elif secim == "3":
        stok_guncelle()
    elif secim == "4":
        stokta_olanlar()
    elif secim == "5":
        urun_sil()
    elif secim == "6":
        veriyi_kaydet()
        break
    else:
        print("❌ Geçersiz seçim.")
