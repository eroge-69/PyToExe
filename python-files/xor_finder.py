
import os

def is_probable_mp3(data):
    return data.startswith(b"ID3") or data[:2] in [b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2"]

def apply_xor(data, key_bytes):
    return bytes([b ^ key_bytes[i % 4] for i, b in enumerate(data)])

def try_keys(input_file):
    with open(input_file, "rb") as f:
        raw = f.read()

    os.makedirs("output", exist_ok=True)
    found = 0

    for a in range(0x00, 0xFF + 1):
        for b in range(0x00, 0xFF + 1):
            for c in range(0x00, 0xFF + 1):
                for d in range(0x00, 0xFF + 1):
                    key = bytes([a, b, c, d])
                    decoded = apply_xor(raw, key)
                    if is_probable_mp3(decoded):
                        name = os.path.basename(input_file)
                        output_file = f"output/{name}_decrypted_{a:02X}{b:02X}{c:02X}{d:02X}.mp3"
                        with open(output_file, "wb") as out:
                            out.write(decoded)
                        print(f"[✓] Clave encontrada: {a:02X} {b:02X} {c:02X} {d:02X} → {output_file}")
                        found += 1
                        if found >= 1:
                            return
    if found == 0:
        print("No se encontró ninguna clave que produzca un .mp3 válido.")

if __name__ == "__main__":
    print("=== Buscador de clave XOR para archivos .SMP ===")
    path = input("Introduce la ruta del archivo .smp: ").strip()
    if not os.path.isfile(path):
        print("Archivo no encontrado.")
    else:
        try_keys(path)
