# Arti Kode Kedipan Lampu MIL pada Honda Vario 110 LED
def main():
    print("================================================")
    print("  INTERPRETER KODE MIL HONDA VARIO 110 LED")
    print("================================================")
    print("Cara penggunaan:")
    print("1. Hidupkan mesin (tanpa starter)")
    print("2. Amati kedipan lampu MIL (warna kuning)")
    print("3. Hitung kombinasi kedipan PANJANG dan PENDEK")
    print("------------------------------------------------")
    print("Format kode: [PANJANG]-[PENDEK]")
    print("Contoh: 2 kedipan panjang + 3 pendek → 2-3")
    print("================================================\n")

    # Database kode MIL
    error_codes = {
        "0-1": "Sensor Posisi Camshaft (CMP) Malfungsi",
        "0-2": "Sensor Posisi Crankshaft (CKP) Malfungsi",
        "0-3": "Sensor Tekanan Udara (MAP) Malfungsi",
        "0-4": "Sensor Posisi Throttle (TP) Malfungsi",
        "0-5": "Sensor Suhu Air (ECT) Malfungsi",
        "0-6": "Sensor Suhu Udara (IAT) Malfungsi",
        "0-7": "Sensor Oksigen (O2) Malfungsi",
        "0-8": "Sensor Kecepatan (VSS) Malfungsi",
        "1-0": "Sistem Pengapian Malfungsi",
        "1-1": "Injector Malfungsi",
        "1-2": "Fuel Pump Malfungsi",
        "1-3": "ECU Malfungsi",
        "1-4": "Karburator Heater Malfungsi",
        "1-5": "Sistem Charging Malfungsi",
        "2-1": "Sistem Immobilizer Malfungsi",
        "2-2": "Bank Angle Sensor Malfungsi",
        "3-1": "Transmisi Otomatis Malfungsi",
        "5-2": "Masalah pada sensor CKP (Crankshaft Position)",
        "8-1": "Sistem Kelistrikan Umum Malfungsi",
        "9-1": "Sistem Diagnosa Internal ECU Error"
    }

    while True:
        try:
            # Input kode dari pengguna
            code = input("Masukkan kode kedipan (format X-Y) atau 'exit' untuk keluar: ").strip()

            if code.lower() == 'exit':
                print("\nProgram dihentikan. Semoga membantu!")
                break

            # Validasi format input
            if '-' not in code:
                raise ValueError("Format salah! Gunakan format X-Y (contoh: 1-2)")

            # Cek kode di database
            if code in error_codes:
                print(f"\n⛔ KODE {code}: {error_codes[code]}")
                print("----------------------------------------------")
                print("Tindakan yang disarankan:")
                print("1. Matikan mesin")
                print("2. Periksa konektor dan kabel terkait")
                print("3. Bersihkan sensor dari kotoran/debu")
                print("4. Kunjungi bengkel resmi Honda untuk diagnosa lebih lanjut\n")
            else:
                print(f"\n❌ Kode {code} tidak dikenal. Silakan cek kembali pola kedipan atau konsultasikan dengan mekanik Honda.\n")

        except ValueError as e:
            print(f"\n⚠️ Error: {e}\n")

if __name__ == "__main__":
    main()