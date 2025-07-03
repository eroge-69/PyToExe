import sys

def to_ascii_bytes(string):
    return [ord(c) for c in string]

def calc_crc16_ibm(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            lsb = crc & 0x0001
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return [crc & 0xFF, (crc >> 8) & 0xFF]

def generate_code(euro_amount):
    base = [
        0x1D, 0x36, 0x30, 0x30, 0x33, 0x32, 0x33, 0x37,
        0x36, 0x37, 0x37, 0x30
    ]

    amount_str = f"{euro_amount:.2f}".replace('.', '').zfill(4)
    base += to_ascii_bytes(amount_str)

    cent = int(round(euro_amount * 100))
    approx = cent // 10
    approx_str = f"{approx:04d}"
    base += to_ascii_bytes(approx_str)

    base += [0x30] * 10

    crc = calc_crc16_ibm(base)
    base += crc

    hex_code = ' '.join(f"{b:02X}" for b in base)
    return hex_code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte Euro-Betrag als Argument angeben, z.B.:")
        print("  generate_crc16_code.exe 100.00")
        sys.exit(1)

    try:
        euro_amount = float(sys.argv[1])
    except ValueError:
        print("Ungültiger Betrag.")
        sys.exit(1)

    code = generate_code(euro_amount)
    print(f"Code für {euro_amount:.2f} Euro:")
    print(code)
