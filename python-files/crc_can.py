import sys
import time

POLY = 0x4599


def calc_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 7 
        for _ in range(8):
            msb_set = crc & 0x4000
            crc = ((crc << 1) & 0x7FFF)
            if msb_set:
                crc ^= POLY 
    return crc


def main():
    hex_data = input("Podaj dane w formacie hex (maksymalnie 24 cyfry): ")
    if len(hex_data) > 24:
        print("Błąd: maksymalnie 24 cyfry hex (96 bitów).")
        sys.exit(1)

    try:
        iterations = int(input("Podaj liczbę iteracji (1-1000000000): "))
        if not (1 <= iterations <= 1_000_000_000):
            print("Błąd: iteracje muszą być z zakresu 1..1e9.")
            sys.exit(1)
    except ValueError:
        print("Błąd: podaj poprawną liczbę iteracji.")
        sys.exit(1)

    try:
        data_bytes = int(hex_data, 16).to_bytes((len(hex_data) + 1) // 2, "big")
    except ValueError:
        print("Błąd: nieprawidłowy format danych hex.")
        sys.exit(1)

    t0 = time.perf_counter_ns()
    crc_val = 0
    for _ in range(iterations):
        crc_val = calc_crc(data_bytes)
    elapsed = time.perf_counter_ns() - t0

    print(f"CRC=0x{crc_val:04X}")
    print(f"Łączny czas {elapsed / 1e6:.3f} ms")
    print(f"Średnia {(elapsed / iterations):.0f} ns na iterację")


if __name__ == "__main__":
    main()
