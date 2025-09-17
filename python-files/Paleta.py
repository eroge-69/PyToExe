import struct

# Lista das 16 cores em RGB
colors = [
    (0, 0, 0),
    (16, 16, 16),
    (32, 32, 32),
    (64, 64, 64),
    (80, 80, 80),
    (96, 96, 96),
    (120, 120, 120),
    (144, 144, 144),
    (160, 160, 160),
    (168, 168, 168),
    (176, 176, 176),
    (200, 200, 200),
    (216, 216, 216),
    (232, 232, 232),
    (239, 241, 243),
    (248, 249, 250)
]

# Cabeçalho do LOGPALETTE
version = 0x0300
num_entries = len(colors)

palette_data = struct.pack("<HH", version, num_entries)

# Adicionar as cores (R,G,B,0)
for r, g, b in colors:
    palette_data += struct.pack("BBBB", r, g, b, 0)

# Montar o RIFF
riff_header = b"RIFF"
riff_size = 4 + 4 + 4 + len(palette_data)  # 'PAL ' + 'data' + size + data
riff_data = b"PAL " + b"data" + struct.pack("<I", len(palette_data)) + palette_data

with open("palette.pal", "wb") as f:
    f.write(riff_header)
    f.write(struct.pack("<I", riff_size))
    f.write(riff_data)

print("Arquivo 'palette.pal' gerado com sucesso!")