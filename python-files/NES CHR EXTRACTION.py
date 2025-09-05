import os

def extract_chr_rom():
    print("NES CHR Extractor - Built by Numaticjoe 2025")
    input_path = input("Enter path to .nes ROM: ").strip()
    if not os.path.isfile(input_path):
        print("Error: Input file does not exist.\n")
        return

    default_output = os.path.splitext(input_path)[0] + ".chr"
    print("ENSURE FILE NAME ENDS IN .chr or .bin")
    output_path = input(f"Enter output path for CHR ROM (default: {default_output}): ").strip()
    if not output_path:
        output_path = default_output

    with open(input_path, "rb") as f:
        header = f.read(16)
        if len(header) < 16 or header[:4] != b"NES\x1a":
            print("Error: Not a valid iNES file.\n")
            return

        prg_size = header[4] * 16384  # 16 KB units
        chr_size = header[5] * 8192   # 8 KB units

        if chr_size == 0:
            print("This ROM uses CHR RAM (no CHR ROM present).\n")
            return

        f.seek(16 + prg_size)
        chr_data = f.read(chr_size)

    with open(output_path, "wb") as out:
        out.write(chr_data)

    print(f"CHR ROM ({chr_size} bytes) extracted to: {output_path}\n")

def main():
    while True:
        extract_chr_rom()
        choice = input("Press [1] to Exit or [2] to extract another ROM: ").strip()
        if choice == "1":
            print("Goodbye!")
            break
        elif choice != "2":
            print("Invalid choice, exiting.")
            break

if __name__ == "__main__":
    main()
