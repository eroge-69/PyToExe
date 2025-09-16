def main():
    # ==============================================================================
    #                               CHANNEL PROBING
    #                               (TOPOLOGI STAR)
    # ==============================================================================
    """
    Fungsi utama untuk mengeksekusi simulasi channel probing.
    """
    from channel_probing import jalankan_channel_probing
    # Menjalankan simulasi untuk "Skenario 1"
    # Parameter fast_mode=False akan memberikan jeda agar terlihat lebih realistis.
    # Ubah ke fast_mode=True untuk mendapatkan output instan.
    channel_probing_elapsed = jalankan_channel_probing(scenario_name="Skenario 1", fast_mode=True)

    # ==============================================================================
    #                           KORELASI CHANNEL PROBING
    # ==============================================================================
    """
    Fungsi utama untuk menjalankan analisis korelasi channel probing.
    Fungsi analisis yang dipanggil akan menangani pencetakan hasil.
    Fungsi ini hanya fokus pada eksekusi dan penanganan error.
    """
    import sys
    from channel_probing_korelasi import analyze_correlation
    try:
        # --- Konfigurasi ---
        FILE_TO_ANALYZE = r"C:\Kuliah STrLJ Telekomunikasi - PENS\Semester 3\Proyek Akhir-2\Source Code\EK\W 3\Skenario 1.xlsx"
        SHEET_NAME = "Channel Probing"
        # Cukup panggil fungsinya. Tampilan output sudah diurus di dalam fungsi itu sendiri.
        # Kita tidak perlu menyimpan hasilnya ke variabel jika tidak akan digunakan lagi di sini.
        analyze_correlation(FILE_TO_ANALYZE, SHEET_NAME)
    
    except (FileNotFoundError, ValueError, IOError) as e:
        # Penanganan error tetap berada di sini agar pemisahan tugas tetap jelas.
        # Modul analisis bertugas memberi tahu 'ada error', main.py bertugas
        # memutuskan apa yang harus dilakukan saat error terjadi (mis: keluar dari program).
        print(f"\nANALYSIS FAILED!\n{e}", file=sys.stderr)
        sys.exit(1) 
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED!\n{e}", file=sys.stderr)
        sys.exit(1)

    # ==============================================================================
    #                                  PRA PROSES
    #                               (MOVING AVERAGE)
    # ==============================================================================
    """
    Titik masuk utama dan konfigurasi parameter untuk pra-proses data DOSS.
    Ubah parameter di bawah ini sesuai kebutuhan.
    """
    # --- Konfigurasi Parameter ---
    FILE_PATH   = FILE_TO_ANALYZE
    SHEET_IN    = "Channel Probing"
    SHEET_OUT   = "Pra Proses"
    WINDOW      = 3      # <<— Ubah ukuran window di sini sesuai kebutuhan
    QUIET       = False   # Set ke True untuk menonaktifkan log konsol
    # ----------------------------

    # Mengimpor dan menjalankan fungsi utama dari modul preprocess_doss
    from pra_proses import run
    
    pra_proses_elapsed = run(
        file_path=FILE_PATH, 
        sheet_in=SHEET_IN, 
        sheet_out=SHEET_OUT, 
        window=WINDOW, 
        quiet=QUIET
    )

    # ==============================================================================
    #                              KORELASI PRA PROSES
    # ==============================================================================
    """
    Fungsi utama untuk menjalankan analisis korelasi pra proses.
    Fungsi analisis yang dipanggil akan menangani pencetakan hasil.
    Fungsi ini hanya fokus pada eksekusi dan penanganan error.
    """
    from pra_proses_korelasi import analyze_correlation
    try:
        # --- Konfigurasi ---
        FILE_TO_ANALYZE = FILE_TO_ANALYZE
        SHEET_NAME = "Pra Proses"
        # Cukup panggil fungsinya. Tampilan output sudah diurus di dalam fungsi itu sendiri.
        # Kita tidak perlu menyimpan hasilnya ke variabel jika tidak akan digunakan lagi di sini.
        analyze_correlation(FILE_TO_ANALYZE, SHEET_NAME)
    
    except (FileNotFoundError, ValueError, IOError) as e:
        # Penanganan error tetap berada di sini agar pemisahan tugas tetap jelas.
        # Modul analisis bertugas memberi tahu 'ada error', main.py bertugas
        # memutuskan apa yang harus dilakukan saat error terjadi (mis: keluar dari program).
        print(f"\nANALYSIS FAILED!\n{e}", file=sys.stderr)
        sys.exit(1) 
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED!\n{e}", file=sys.stderr)
        sys.exit(1)

    # ==============================================================================
    #                              KUANTISASI MULTILEVEL
    #                             (LLOYD-MAX QUANTIZATION)
    # ==============================================================================    
    """
    Fungsi utama untuk menyetel parameter dan menjalankan proses kuantisasi.
    """
    # Pastikan file kuantisasi.py berada di direktori yang sama
    from kuantisasi_multilevel import run

    # --- KONFIGURASI ---
    # Path ke file Excel sumber
    FILE_PATH = FILE_TO_ANALYZE
    
    # Nama sheet input dan output
    SHEET_IN  = "Pra Proses"
    SHEET_OUT = "Kuantisasi Multilevel"
    
    # Parameter untuk algoritma Lloyd-Max
    EPS       = 1e-6    # Toleransi konvergensi
    MAX_ITERS = 200     # Batas maksimum iterasi
    
    # Opsi logging
    QUIET     = False   # Set ke True untuk menonaktifkan pesan di konsol
    
    # Peta dari level kuantisasi ke representasi 2-bit biner
    # JANGAN UBAH URUTAN MAPPING INI SESUAI SPESIFIKASI
    CODE_MAP = {
        1: "00", 
        2: "01", 
        3: "11", 
        4: "10"
    }
    
    # --- EKSEKUSI ---
    kuantisasi_multilevel_elapsed = run(
        file_path=FILE_PATH,
        sheet_in=SHEET_IN,
        sheet_out=SHEET_OUT,
        code_map=CODE_MAP,
        eps=EPS,
        max_iters=MAX_ITERS,
        quiet=QUIET
    )

    # ==============================================================================
    #                           KEY DISAGREEMENT RATE (KDR)
    # ==============================================================================
    """
    Fungsi utama untuk menyetel parameter dan memanggil logika pemrosesan KDR.
    """
    from key_disagremeent_rate import run

    # --- PENGATURAN PARAMETER ---
    FILE_PATH = FILE_TO_ANALYZE
    SHEET_IN  = "Kuantisasi Multilevel"
    COLUMNS   = ("DOSS 1", "DOSS 2", "DOSS 3")
    DECIMALS  = 2  # Jumlah desimal untuk pembulatan output
    QUIET     = False # Set True untuk menonaktifkan log proses di konsol
    
    # Header ini bisa dihilangkan jika Anda ingin output yang sangat bersih
    # print("="*50)
    # print("MEMULAI PROSES PERHITUNGAN KEY DISAGREEMENT RATE (KDR)")
    # print("="*50)

    try:
        # Memanggil fungsi run dari modul kdr
        run(
            file_path=FILE_PATH,
            sheet_in=SHEET_IN,
            columns=COLUMNS,
            decimals=DECIMALS,
            quiet=QUIET
        )
        
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"\n[PROSES GAGAL] Terjadi kesalahan fatal: {e}", file=sys.stderr)
        print("Mohon periksa kembali path file, nama sheet, nama kolom, dan format data.", file=sys.stderr)
        sys.exit(1) # Keluar dari program dengan status error
    except Exception as e:
        print(f"\n[PROSES GAGAL] Terjadi kesalahan yang tidak terduga: {e}", file=sys.stderr)
        sys.exit(1)

    # ==============================================================================
    #                           KEY GENERATION RATE (KGRik)
    # ==============================================================================
    """
    Titik masuk utama program.
    Menyetel parameter, memanggil logika pemrosesan, dan menghitung KGRik.
    """
    # --- Parameter Konfigurasi ---
    FILE_PATH = FILE_TO_ANALYZE
    SHEET_IN  = "Kuantisasi Multilevel"
    COLUMNS   = ("DOSS 1", "DOSS 2", "DOSS 3")

    # Waktu proses (dalam detik)
    #channel_probing_elapsed     = 110 * 1318 / 1000.0  # Contoh: 144.98
    #pra_proses_elapsed          = 0.0
    #kuantisasi_multilevel_elapsed = 0.4                  # Contoh: 400ms

    # Pilih kolom yang bit-nya akan dijumlahkan untuk perhitungan KGR
    USE_COLUMNS = ("DOSS 1",)

    # --- Logika Program ---
    try:
        from key_generation_rate_ik import run

        # Panggil fungsi inti untuk mendapatkan panjang bit
        result = run(file_path=FILE_PATH, sheet_in=SHEET_IN, columns=COLUMNS, quiet=False)

        # Hitung total bit dari kolom yang dipilih
        total_bits = sum(result["bit_lengths"][col] for col in USE_COLUMNS)

        # Hitung total waktu (Tik)
        Tik = channel_probing_elapsed + pra_proses_elapsed + kuantisasi_multilevel_elapsed

        if Tik <= 0:
            raise ValueError("Total waktu (T_ik) harus lebih besar dari 0 untuk menghitung KGRik.")

        # Hitung KGRik (Key Generation Rate setelah kuantisasi)
        KGRik = total_bits / Tik

        # --- Tampilkan Hasil ---
        print(f"Total bit (ΣK) dari kolom {USE_COLUMNS}: {total_bits} bits")
        print(f"Total waktu (T_ik): {Tik:.2f} s")
        print("-" * 40)
        print(f"KGR_ik (ΣK / T_ik): {KGRik:.2f} bps")
        print("==============================================================================\n")

    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Program dihentikan karena error: {e}")
    except Exception as e:
        print(f"Terjadi error yang tidak terduga: {e}")

    # ==============================================================================
    #                             REKONSILIASI INFORMASI
    #                               (LINEAR BLOCK CODE)
    # ==============================================================================
    """
    Titik masuk utama untuk menjalankan skrip rekonsiliasi.
    Atur parameter di bawah ini.
    """
    from rekonsiliasi_informasi import run, timestamp_msg

    # ===== Parameter yang bisa diubah =====
    FILE_PATH = FILE_TO_ANALYZE
    SHEET_IN  = "Kuantisasi Multilevel"
    SHEET_OUT = "Rekonsiliasi Informasi"
    COLUMNS   = ("DOSS 1", "DOSS 2", "DOSS 3")
    QUIET     = False

    try:
        result, rekonsiliasi_informasi_elapsed = run(file_path=FILE_PATH,
                     sheet_in=SHEET_IN,
                     sheet_out=SHEET_OUT,
                     columns=COLUMNS,
                     quiet=QUIET)

        # MODIFIKASI: Menampilkan statistik baru
        if result:
            stats = result["stats"]
            total_rows = result['rows']
            
            timestamp_msg("--- RINGKASAN REKONSILIASI ---", QUIET)
            timestamp_msg(f"Total Baris (Blok) Diproses: {total_rows}", QUIET)
            
            for doss in ["DOSS 2", "DOSS 3"]:
                doss_stats = stats[doss]
                corrected = doss_stats['corrected']
                unchanged = doss_stats['unchanged']
                uncorrectable = doss_stats['uncorrectable']
                successful_ops = corrected + unchanged
                success_percentage = (successful_ops / total_rows * 100) if total_rows > 0 else 0
                
                timestamp_msg(f"{doss} -> Terkoreksi: {corrected}, Tidak Berubah: {unchanged}, Gagal Koreksi: {uncorrectable}", QUIET)
                timestamp_msg(f"{doss} -> Tingkat Keberhasilan Koreksi: {success_percentage:.2f}% ({successful_ops}/{total_rows})", QUIET)

            # BARU: Ringkasan hasil filter
            rows_kept = result['rows_kept']
            rows_dropped = result['rows_dropped']
            final_percentage = (rows_kept / total_rows * 100) if total_rows > 0 else 0

            timestamp_msg("--- HASIL AKHIR SETELAH FILTER ---", QUIET)
            timestamp_msg(f"Baris yang Disimpan (semua DOSS sinkron): {rows_kept}", QUIET)
            timestamp_msg(f"Baris yang Dihapus (ada gagal koreksi): {rows_dropped}", QUIET)
            timestamp_msg(f"Persentase Data Final yang Sinkron: {final_percentage:.2f}%", QUIET)
            
            timestamp_msg("--- PROSES SELESAI ---", QUIET)
            print("==============================================================================\n")

    except (ValueError, FileNotFoundError) as e:
        timestamp_msg(f"ERROR: {e}", QUIET)
    except Exception as e:
        timestamp_msg(f"AN UNEXPECTED ERROR OCCURRED: {e}", QUIET)

    # ==============================================================================
    #                           KEY GENERATION RATE (KGRr)
    # ==============================================================================
    """
    Fungsi utama untuk menjalankan kalkulasi KGRᵣ.
    """
    # ===== Parameter yang bisa diubah =====
    FILE_PATH = FILE_TO_ANALYZE
    SHEET_IN  = "Rekonsiliasi Informasi"
    COLUMNS   = ("DOSS 1 - final", "DOSS 2 - final", "DOSS 3 - final")

    # Pilih kolom mana yang dihitung ΣS (total bit setelah rekonsiliasi).
    # Contoh 1: Hanya DOSS 1
    USE_COLUMNS = ("DOSS 1 - final",)
    # Contoh 2: Gabungan DOSS 1 dan DOSS 2
    # USE_COLUMNS = ("DOSS 1 - final", "DOSS 2 - final")
    # Contoh 3: Gabungan ketiganya
    # USE_COLUMNS = ("DOSS 1 - final", "DOSS 2 - final", "DOSS 3 - final")

    # Waktu proses (dalam detik) — ganti nilai 0.0 dengan hasil pengukuran Anda.
    #channel_probing_elapsed       = 15.52
    #pra_proses_elapsed            = 5.21
    #kuantisasi_multilevel_elapsed = 8.75
    #rekonsiliasi_informasi_elapsed= 12.33

    try:
        from key_generation_rate_r import run, timestamp_msg
    except ImportError:
        print("Pastikan file 'key_generation_rate_r.py' berada di direktori yang sama.")
        return

    try:
        # Jalankan logika pemrosesan
        result = run(
            file_path=FILE_PATH, 
            sheet_in=SHEET_IN, 
            columns=COLUMNS, 
            quiet=False
        )

        # Hitung total bit (ΣS) dari kolom yang dipilih
        total_bits = sum(result["bit_lengths"][col] for col in USE_COLUMNS if col in result["bit_lengths"])
        
        # Hitung total waktu (Tr)
        Tr = (channel_probing_elapsed + pra_proses_elapsed +
              kuantisasi_multilevel_elapsed + rekonsiliasi_informasi_elapsed)

        if Tr <= 0:
            raise ValueError("Total waktu (T_r) harus lebih besar dari 0 untuk menghitung KGRᵣ.")

        KGR_r = total_bits / Tr  # Hasil dalam bit per second (bps)

        # ===== Output Ringkas =====
        #print("\n" + "="*50)
        #print("HASIL PERHITUNGAN KGR SETELAH REKONSILIASI (KGRᵣ)")
        #print("="*50)
        timestamp_msg(f"Total Bit (ΣS) dari {USE_COLUMNS}: {total_bits} bit")
        timestamp_msg(f"Panjang bit per kolom: {result['bit_lengths']}")
        timestamp_msg(f"Baris valid per kolom: {result['valid_rows']}")
        timestamp_msg(f"Total baris di file: {result['total_rows']}")
        timestamp_msg(f"Total Waktu Proses (T_r): {Tr:.4f} s")
        print("-"*40)
        timestamp_msg(f"KGR_r (ΣS / T_r) = {KGR_r:.2f} bps")
        print("==============================================================================\n")
        #print("="*50)

    except (FileNotFoundError, KeyError, ValueError) as e:
        # Menangkap error yang mungkin terjadi dari modul logika dan menampilkannya
        timestamp_msg(f"PROGRAM GAGAL: {e}")
    except Exception as e:
        timestamp_msg(f"Terjadi error yang tidak terduga: {e}")

    # ==============================================================================
    #                             PRIVACY AMPLIFICATION
    #                               (UNIVERSAL HASH)
    # ==============================================================================
    """
    Titik masuk utama untuk menjalankan proses privacy amplification.
    Semua parameter disetel di sini.
    """
    # ===== Parameter yang bisa diubah =====
    FILE_PATH = FILE_TO_ANALYZE
    SHEET_IN  = "Rekonsiliasi Informasi"
    SHEET_OUT = "Universal Hash"
    COLUMNS   = ("DOSS 1 - final", "DOSS 2 - final", "DOSS 3 - final")
    BLOCK_SIZE = 256
    # Set None untuk acak, atau angka (integer) untuk hasil yang reproducible
    SEED       = 42 
    QUIET      = False # Set True untuk menonaktifkan pesan log di konsol

    # Mengimpor fungsi dari modul logika
    try:
        from universal_hash_256 import run, timestamp_msg
    except ImportError:
        print("[ERROR] File 'universal_hash.py' tidak ditemukan di direktori yang sama.")
        return

    try:
        result, universal_hash_256_elapsed = run(
            file_path=FILE_PATH,
            sheet_in=SHEET_IN,
            sheet_out=SHEET_OUT,
            columns=COLUMNS,
            block_size=BLOCK_SIZE,
            seed=SEED,
            quiet=QUIET
        )
        
        # Cetak ringkasan akhir jika tidak dalam mode quiet
        if not QUIET:
            timestamp_msg(f"Proses Universal Hash selesai.")
            timestamp_msg(f"Hasil ditulis ke sheet: '{SHEET_OUT}' di file '{FILE_PATH}'.")
            timestamp_msg(f"Waktu eksekusi universal hash 256: {universal_hash_256_elapsed:.4f} detik")
            print("-" * 40)
            print("Ringkasan per kolom:")
            for col, info in result["summary"].items():
                print(
                    f"  - {col}: \n"
                    f"    Total bit (a) = {info['a']}\n"
                    f"    Bit diproses (remaining) = {info['remaining']}\n"
                    f"    Bit dibuang (deleted) = {info['deleted']}\n"
                    f"    Jumlah kunci = {info['num_keys']}"
                )
            print("-" * 40)
            print("==============================================================================\n")

    except (KeyError, ValueError) as e:
        # Menangkap error validasi yang sudah didefinisikan
        timestamp_msg(f"ERROR: Terjadi kesalahan. {e}")
    except Exception as e:
        # Menangkap error tak terduga lainnya
        timestamp_msg(f"ERROR: Terjadi kesalahan yang tidak terduga. {e}")

    # ==============================================================================
    #                                   UJI NIST
    # ==============================================================================



    # ==============================================================================
    #                             PRIVACY AMPLIFICATION
    #                                   (SHA-256)
    # ==============================================================================



    # ==============================================================================
    #                          KEY GENERATION RATE (KGRpa)
    # ==============================================================================



    # ==============================================================================
    #                               ENKRIPSI-DEKRIPSI
    #                                   (AES-256)
    # ==============================================================================



if __name__ == "__main__":
    main()