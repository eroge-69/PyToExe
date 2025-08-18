import os
import shutil
from pathlib import Path

def crc16_lsb_table(data, poly_ref=0x8408, init=0xFFFF, xorout=0x0000):
    # Таблица для LSB-first
    table = []
    for byte in range(256):
        crc = byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ poly_ref
            else:
                crc >>= 1
        table.append(crc & 0xFFFF)

    crc = init & 0xFFFF
    for b in data:
        crc = (crc >> 8) ^ table[(crc ^ b) & 0xFF]
    crc ^= xorout
    return crc & 0xFFFF

def byteswap16(x: int) -> int:
    return ((x & 0xFF) << 8) | ((x >> 8) & 0xFF)

def process_file(path: Path):
    d = bytearray(path.read_bytes())

    # CRC хранится по адресу 0xC0000 (2 байта)
    stored = int.from_bytes(d[0xC0000:0xC0002], "big")

    # Диапазон для расчёта CRC: 0xC0002 .. 0xFFFFB (включительно)
    start = 0xC0002
    count = (3 << 16) + 0xFFFA  # 0x2FFFA
    end = start + count - 1
    data = d[start:end+1]

    # Вычисляем CRC (LSB-first)
    calc = crc16_lsb_table(data, poly_ref=0x8408, init=0xFFFF, xorout=0x0000)
    new_crc = byteswap16(calc)

    print(f"\nФайл: {path.name}")
    print(f"  CRC (вычислен) = 0x{calc:04X}")
    print(f"  byteswap(calc) = 0x{new_crc:04X}")
    print(f"  CRC в файле    = 0x{stored:04X}")

    if new_crc == stored:
        print("  ✅ CRC совпадает.")
    else:
        print("  ❌ CRC не совпадает.")
        ans = input("  Обновить CRC в файле? (y/n): ").strip().lower()
        if ans == "y":
            # Создаём резервную копию
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            print(f"  📂 Создана резервная копия: {backup.name}")

            # Обновляем CRC в файле
            d[0xC0000:0xC0002] = new_crc.to_bytes(2, "big")
            path.write_bytes(d)
            print("  🔄 CRC обновлён в файле.")

def main():
    folder = Path(os.getcwd())
    bin_files = list(folder.glob("*.BIN"))
    if not bin_files:
        print("В папке нет файлов .BIN")
        return

    for f in bin_files:
        process_file(f)

if __name__ == "__main__":
    main()
