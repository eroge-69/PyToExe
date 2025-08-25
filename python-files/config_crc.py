#!/usr/bin/env python3
import struct
import sys
import os
import io

def stm32_crc32(bin_data: bytes) -> int:
    """
    Emulates STM32 hardware CRC peripheral (CRC-32 IEEE 802.3, poly 0x04C11DB7,
    init=0xFFFFFFFF, word-reflected, no final xor).
    """
    crc = 0xFFFFFFFF
    poly = 0x04C11DB7

    # process data as 32-bit words (little endian)
    for i in range(0, len(bin_data), 4):
        word = bin_data[i:i+4].ljust(4, b'\x00')
        val = struct.unpack("<I", word)[0]

        # feed each bit (MSB first)
        for bit in range(32):
            if (crc >> 31) ^ ((val >> (31 - bit)) & 1):
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFFFFFF  # keep 32 bits
    return crc

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} SKANSiesta.bin version_string")
        sys.exit(1)

    fw_file = sys.argv[1]
    version = sys.argv[2]
    signature = sys.argv[3]

    if not os.path.exists(fw_file):
        print("Error: File not found:", fw_file)
        sys.exit(1)

    with open(fw_file, "rb") as f:
        data = f.read()

    crc_val = stm32_crc32(data)
    size = len(data)

    # Save config_crc.txt in the same folder as the .bin file
    bin_dir = os.path.dirname(fw_file)
    cfg_path = os.path.join(bin_dir,"config.txt")
    with open(cfg_path, "w") as cfg:
        cfg.write(f"\n|--- SKANRAY TECHNOLOGY LTD ---|\n\n")
        cfg.write(f"CRC = 0x{crc_val:08X}\n")
        cfg.write(f"SIZE = {size}\n")
        cfg.write(f"VERSION = {version}\n")
        cfg.write(f"VALIDATED BY = {signature}\n")

    print("Generated config.txt location:", cfg_path)
    print(f"  CRC=0x{crc_val:08X}")
    print(f"  SIZE={size}")
    print(f"  VERSION={version}")

if __name__ == "__main__":
    main()