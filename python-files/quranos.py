import os

def main():
    print("QuranOS 1.5")
    print("Try the Our 2 week ago app in https://github.com/amr-aisy/Alquran-app")
    print(">_")

    ayat_folder = "ayat"

    if not os.path.exists(ayat_folder):
        print("Folder 'ayat' tidak ditemukan!")
        return

    while True:
        command = input(">_ ").strip()

        if command.lower() in ["exit", "quit"]:
            print("Keluar dari QuranOS...")
            break

        filename = os.path.join(ayat_folder, f"{command}.txt")

        if os.path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"\n--- {command} ---\n")
                print(content if content else "(kosong, silakan isi manual)")
                print("\n-----------------\n")
        else:
            print(f"Surat '{command}' tidak ditemukan. Pastikan ada file {command}.txt di folder 'ayat'.")

if __name__ == "__main__":
    main()
