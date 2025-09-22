import csv
import os

def parse_gtin(karekod: str) -> str:
    """
    Karekodun GTIN (ilk 14 hane) bilgisini döner.
    """
    karekod = karekod.strip().replace(" ", "")
    return karekod[:14]

def main():
    # Dosya isimleri
    csv_file = "ilaclar.csv"
    txt_file = "input.txt"
    output_file = "eksikler.txt"

    if not os.path.exists(csv_file):
        print(f"{csv_file} bulunamadı!")
        return
    if not os.path.exists(txt_file):
        print(f"{txt_file} bulunamadı!")
        return

    # TXT'den karekodları oku
    with open(txt_file, "r", encoding="utf-8") as f:
        txt_karekodlar = [line.strip().replace(" ", "") for line in f if line.strip()]
    txt_gtin_map = {}
    for k in txt_karekodlar:
        gtin = parse_gtin(k)
        txt_gtin_map.setdefault(gtin, set()).add(k)

    # CSV'den karekodları oku
    csv_karekodlar = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if not row:
                continue
            karekod = row[0].strip().replace(" ", "")
            csv_karekodlar.append(karekod)
    csv_gtin_map = {}
    for k in csv_karekodlar:
        gtin = parse_gtin(k)
        csv_gtin_map.setdefault(gtin, set()).add(k)

    # Karşılaştırma
    with open(output_file, "w", encoding="utf-8") as out:
        for gtin, csv_set in csv_gtin_map.items():
            txt_set = txt_gtin_map.get(gtin, set())
            eksikler = csv_set - txt_set
            if eksikler:
                out.write(f"GTIN: {gtin}\n")
                for e in eksikler:
                    out.write(f"  Eksik: {e}\n")
                out.write("\n")

    print(f"Tamamlandı ✅ Eksikler {output_file} dosyasına yazıldı.")

if __name__ == "__main__":
    main()
