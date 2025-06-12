
import sys
import os

def parse_dat_file(file_path, output_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_chunk = ' '.join(f'{b:02X}' for b in chunk)
            ascii_chunk = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f'{i:08X}  {hex_chunk:<48}  {ascii_chunk}')

        with open(output_path, "w", encoding="utf-8") as out:
            out.write("\n".join(lines))

        print(f"✅ Gotowe! Wynik zapisano do: {output_path}")
    except Exception as e:
        print(f"❌ Błąd: {e}")

def main():
    print("=== GG Archiwum Viewer (.dat) ===")
    if len(sys.argv) < 2:
        print("Użycie: gg_archiwum_viewer.exe <ścieżka_do_pliku.dat>")
        return

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        print("❌ Nie znaleziono pliku:", input_path)
        return

    output_path = os.path.splitext(input_path)[0] + "_output.txt"
    parse_dat_file(input_path, output_path)

if __name__ == "__main__":
    main()
