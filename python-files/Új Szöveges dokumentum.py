from collections import Counter

def main():
    print("🧩 NAND Egyesítő (6 dump alapján)")

    file_names = [
        "nand1.bin",
        "nand2.bin",
        "nand3.bin",
        "nand4.bin",
        "nand5.bin",
        "nand6.bin"
    ]

    nand_data = []
    for name in file_names:
        try:
            with open(name, "rb") as f:
                nand_data.append(f.read())
        except FileNotFoundError:
            print(f"❌ Nem található: {name}")
            nand_data.append(None)

    valid_nands = [data for data in nand_data if data is not None]

    if len(valid_nands) < 2:
        print("⚠️ Legalább 2 érvényes NAND fájl szükséges!")
        return

    lengths = set(len(nand) for nand in valid_nands)
    if len(lengths) != 1:
        print("⚠️ A fájlok nem azonos hosszúságúak – nem lehet összehasonlítani őket.")
        return

    print("🔄 Többségi byte-egyesítés folyamatban...")

    merged_nand = bytearray()
    length = lengths.pop()
    for i in range(length):
        bytes_at_i = [nand[i] for nand in valid_nands]
        most_common_byte, _ = Counter(bytes_at_i).most_common(1)[0]
        merged_nand.append(most_common_byte)

    output_filename = "merged_nand.bin"
    with open(output_filename, "wb") as f:
        f.write(merged_nand)

    print(f"✅ Kész: {output_filename}")

if __name__ == "__main__":
    main()
