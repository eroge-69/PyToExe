import os

# Path file asli
src_file = "ImVehFt.asi"
dst_file = "ImVehFt_fixed.asi"

# Buka file sebagai biner
with open(src_file, "rb") as f:
    data = bytearray(f.read())

# Cari string "Color"
pos = data.find(b"Color")
if pos == -1:
    print("String 'Color' tidak ditemukan.")
else:
    print(f"'Color' ditemukan di offset {hex(pos)}")

    # Patch: NOP (0x90) area sekitar string (±50 byte sebelum & sesudah)
    start = max(0, pos - 50)
    end = min(len(data), pos + 50)
    for i in range(start, end):
        data[i] = 0x90

    # Simpan hasil patch ke file baru
    with open(dst_file, "wb") as f:
        f.write(data)

    print(f"Patched file saved as {dst_file}")
