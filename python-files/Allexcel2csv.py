import sys
import os
import pandas as pd

def convert_to_csv(file_path):
    try:
        base = os.path.splitext(file_path)[0]
        csv_file = base + ".csv"
        df = pd.read_excel(file_path, dtype=str)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"✅ Çevirme başarılı: {csv_file}")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Dosyayı bu programın üzerine sürükle-bırak 👇")
        input("Kapatmak için Enter'a bas...")
    else:
        for file in sys.argv[1:]:
            convert_to_csv(file)
        input("Tamamlandı. Çıkmak için Enter'a bas...")