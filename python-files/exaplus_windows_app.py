import os
import json
from datetime import datetime

# Veri klasörlerini oluştur
os.makedirs("data", exist_ok=True)
os.makedirs("form", exist_ok=True)

# Basit veritabanı dosyası
DATA_FILE = "data/stoklar.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def yukle():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def kaydet(veri):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

def stok_ekle(ad, miktar, fiyat):
    if not ad or not miktar or not fiyat:
        print("[UYARI] Tüm alanlar doldurulmalı.")
        return

    try:
        miktar = int(miktar)
        fiyat = float(fiyat)
    except:
        print("[HATA] Miktar tam sayı, fiyat sayı olmalı.")
        return

    stoklar = yukle()
    stoklar.append({
        "ad": ad,
        "miktar": miktar,
        "fiyat": fiyat,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    kaydet(stoklar)
    print(f"[BAŞARILI] '{ad}' eklendi.")

def listele():
    stoklar = yukle()
    if not stoklar:
        print("\n[BOŞ] Henüz stok eklenmemiş.")
        return
    print("\nStok Listesi:")
    print("=" * 60)
    for i, s in enumerate(stoklar, start=1):
        print(f"{i}. {s['ad']} | {s['miktar']} adet | {s['fiyat']} TL | {s['tarih']}")
    print("=" * 60)

# Test senaryosu (input olmadan çalışacak şekilde)
if __name__ == "__main__":
    print("[TEST] Otomatik test başlatıldı")
    stok_ekle("Kalem", "10", "2.5")
    stok_ekle("Defter", "5", "12")
    listele()
