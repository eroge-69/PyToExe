# Earthion game.bin file unpacker
# v3.3.0 (script v3)
# Please support Ancient and buy the official release:
# https://store.steampowered.com/app/3597580/Earthion/

import lzma
import sys
from struct import pack

with open('game.bin', 'rb') as f:
    b = bytearray(f.read())

print('Decrypting game.bin')

fnv_seed = 0xdeafcafe
fnv_prime = 0x1000193

fnv_hash = fnv_seed
for i in range(len(b)):
    b[i] ^= (fnv_hash >> 9) & 0xff
    fnv_hash = ((fnv_hash ^ b[i]) * fnv_prime) & 0xffffffff

if fnv_hash == 0x2bbe2a9f:  # 2025-07-31 build 19428595
    roms = (
        ('Earthion English.md', 0x43, 0x4bbeb8, 0x780000),
        ('Earthion Japanese.md', 0x4bbefb, 0x4b8836, 0x780000),
        ('Earthion Portuguese.md', 0x974731, 0x4bc5a8, 0x780000),
        ('Earthion Summer 2024 Demo.md', 0xe30cd9, 0x259279, 0x6a0000),
        ('Earthion Fall 2024 Demo.md', 0x1089f52, 0x35e3f6, 0x6a0000),
        ('Earthion Winter 2024 Demo.md', 0x13e8348, 0x40e7e8, 0x740000),
        ('Earthion Early Prototype.md', 0x17f6b30, 0x1894a, 0xa0000),
    )
    confusion = bytes.fromhex('bff058108a26d4775754e507f3e8c999312536c914bb23ca72aef391d93580eda4a3c33babee30b317d6d11ee2478ac9d1b0a623c361aa45424901da8dd439bb939c89bf087976de88669e0fcc7d8995b267fd9ddc2da7c2a959e84f7007cf4680eb4d0a558b4616277c8104494e48e09ecfd00c854a9da4ff7a698f9081b524bb41a32606a6542c878b9968b4969296e0ec78defb5e1881564bf5bc71df72330612b9da175f1ad7a63e1030b30ff8b0198f409ae0a584694b7458d02cdd54a56d41d8c98cb3052a5548e0bd1fb753098767cfc2eebc68f15ef41810423ca0808a1ae108009a14f851add52a0ce04b24243de53325f015f0ac352dd2e77ded3a')
elif fnv_hash == 0x4a3d1a69:  # 2025-08-04 build 19468996
    roms = (
        ('Earthion English (v2.0.1).md', 0x43, 0x4c5f44, 0x780000),
        ('Earthion Japanese (v2.0.1).md', 0x4c5f87, 0x4c15ae, 0x780000),
        ('Earthion Portuguese (v2.0.1).md', 0x987535, 0x4c639d, 0x780000),
        ('Earthion Summer 2024 Demo (v2.0.1).md', 0xe4d8d2, 0x2591ca, 0x6a0000),
        ('Earthion Fall 2024 Demo (v2.0.1).md', 0x10a6a9c, 0x35e304, 0x6a0000),
        ('Earthion Winter 2024 Demo (v2.0.1).md', 0x1404da0, 0x40dc1d, 0x740000),
        ('Earthion Early Prototype (v2.0.1).md', 0x18129bd, 0x188d3, 0xa0000),
    )
    confusion = bytes.fromhex('311664841554eb1a575459352174843ceb0ed90f71bb0cb35a96397a4dd897eda4a3c33babee30b317d6d11ee2478ac9d1b0a623c361aa45424901da8dd439bb939c89bf087976de88669e0fcc7d8995b267fd9ddc2da7c2a959e84f7007cf4680eb4d0a558b4616277c8104494e48e09ecfd00c854a9da4ff7a698f9081b524bb41a32606a6542c878b9968b4969296e0ec78defb5e1881564bf5bc71df72330612b9da175f1ad7a63e1030b30ff8b0198f409ae0a584694b7458d02cdd54a56d41d8c98cb3052a5548e0bd1fb753098767cfc2eebc68f15ef41810423ca0808a1ae108009a14f851add52a0ce04b24243de53325f015f0ac352dd2e77ded3a')
elif fnv_hash == 0x50d53ff6:  # 2025-09-10 build 19874841
    roms = (
        ('Earthion English (v3.3.0).md', 0x43, 0x4706eb, 0x700000),
        ('Earthion Japanese (v3.3.0).md', 0x47072e, 0x46cf5d, 0x700000),
        ('Earthion Portuguese (v3.3.0).md', 0x8dd68b, 0x470849, 0x700000),
        ('Earthion Summer 2024 Demo (v3.3.0).md', 0xd4ded4, 0x2591b0, 0x6a0000),
        ('Earthion Fall 2024 Demo (v3.3.0).md', 0xfa7084, 0x35dd95, 0x6a0000),
        ('Earthion Winter 2024 Demo (v3.3.0).md', 0x1304e19, 0x40db21, 0x740000),
        ('Earthion Early Prototype (v3.3.0).md', 0x171293a, 0x18933, 0xa0000),
    )
    confusion = bytes.fromhex('979692102cf7eb5f6f3db6640ae8e1825f827c26fd76522772966806aaf097eda4a3c33babee30b317d6d11ee2478ac9d1b0a623c361aa45424901da8dd439bb939c89bf087976de88669e0fcc7d8995b267fd9ddc2da7c2a959e84f7007cf4680eb4d0a558b4616277c8104494e48e09ecfd00c854a9da4ff7a698f9081b524bb41a32606a6542c878b9968b4969296e0ec78defb5e1881564bf5bc71df72330612b9da175f1ad7a63e1030b30ff8b0198f409ae0a584694b7458d02cdd54a56d41d8c98cb3052a5548e0bd1fb753098767cfc2eebc68f15ef41810423ca0808a1ae108009a14f851add52a0ce04b24243de53325f015f0ac352dd2e77ded3a')
elif fnv_hash == 0x726347a3:  # 2025-09-10 build 19929821
    roms = (
        ('Earthion English (v3.3.0 19929821).md', 0x43, 0x47027a, 0x700000),
        ('Earthion Japanese (v3.3.0 19929821).md', 0x4702bd, 0x46d0fb, 0x700000),
        ('Earthion Portuguese (v3.3.0 19929821).md', 0x8dd3b8, 0x470519, 0x700000),
        ('Earthion Summer 2024 Demo (v3.3.0 19929821).md', 0xd4d8d1, 0x258ca6, 0x6a0000),
        ('Earthion Fall 2024 Demo (v3.3.0 19929821).md', 0xfa6577, 0x35e116, 0x6a0000),
        ('Earthion Winter 2024 Demo (v3.3.0 19929821).md', 0x130468d, 0x40de9b, 0x740000),
        ('Earthion Early Prototype (v3.3.0 19929821).md', 0x1712528, 0x18922, 0xa0000),
    )
    confusion = bytes.fromhex('56c03bcab80e481afa9a8807388b0fc88e0e4e9aa0a452e1b87f391dd9aa0ceda4a3c33babee30b317d6d11ee2478ac9d1b0a623c361aa45424901da8dd439bb939c89bf087976de88669e0fcc7d8995b267fd9ddc2da7c2a959e84f7007cf4680eb4d0a558b4616277c8104494e48e09ecfd00c854a9da4ff7a698f9081b524bb41a32606a6542c878b9968b4969296e0ec78defb5e1881564bf5bc71df72330612b9da175f1ad7a63e1030b30ff8b0198f409ae0a584694b7458d02cdd54a56d41d8c98cb3052a5548e0bd1fb753098767cfc2eebc68f15ef41810423ca0808a1ae108009a14f851add52a0ce04b24243de53325f015f0ac352dd2e77ded3a')
else:
    print('Unsupported version')
    sys.exit(1)

vectors = None
if fnv_hash in (0x50d53ff6, 0x726347a3):
    vec_enc = bytes.fromhex('0001e60001f10001fa0001f17fb28a0001f10002030001f10001e60001f10001fa0001f17fb28a0001f10002030001f10001e60001f10001fa0001f17fb28a0001f10002030001f10001e60001f10001fa0001f17fb02d0001f10002030001f10001e60001f10001fa0001f17fb1210001f10002030001f10001e60001f10001fa0001f17fb1690001f10002030001f10001f40001ff0002080001ff0002110001ff00021a0001ff')
    vectors = []
    for game in range(7):
        v = bytearray()
        for i in range(8):
            off = game * 24 + i * 3
            v += pack(">I", int.from_bytes(vec_enc[off:off+3]) << 1)
        vectors.append(v)

for game_index, (filename, offset, size, usize) in enumerate(roms):
    print(f'Uncompressing {filename}')
    packed = b[offset:offset + size]
    # Workaround for https://github.com/python/cpython/issues/92018
    packed[5:13] = b'\xff' * 8
    unpacked = lzma.decompress(packed, format=lzma.FORMAT_ALONE)
    assert len(unpacked) == usize

    print(f'Decrypting {filename}')
    decrypted = bytearray(usize)
    for i in range(usize):
        #x = (active_banks[(i >> 19) & 7] << 19) | (i & 0x7ffff)
        x = i
        y = x ^ ((i >> 6) & 0xf80) ^ ((x >> 16) & 0xfffffffe) ^ 0xa56
        z = (((x >> 14) ^ (i >> 7)) & 0xfe) ^ (i & 0xff)
        decrypted[x] = unpacked[y] ^ confusion[z]

    if vectors is not None:
        decrypted[0x60:0x60+len(vectors[game_index])] = vectors[game_index]

    print(f'Writing {filename}')
    with open(filename, 'wb') as f:
        f.write(decrypted)
