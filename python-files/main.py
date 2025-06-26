# --- DATA KAMUS TEMATIK ---
kamus_tematik = {
    "Makanan": {
        "Roti": "خبز (Khubz)",
        "Nasi": "أرز (Aruz)",
        "Air": "ماء (Maa')",
        "Susu": "حليب (Haliib)",
        "Daging": "لحم (Lahm)",
        "Ayam": "دجاج (Dajaaj)",
        "Ikan": "سمك (Samak)",
        "Buah": "فاكهة (Faakihah)",
        "Sayur": "خضروات (KhudrawaT)",
        "Kopi": "قهوة (Qahwah)",
        "Teh": "شاي (Shay)",
        "Gula": "سكر (Sukkar)",
        "Garam": "ملح (Milh)",
    },
    "Keluarga": {
        "Ayah": "أب (Ab)",
        "Ibu": "أم (Umm)",
        "Saudara Laki-laki": "أخ (Akh)",
        "Saudari Perempuan": "أخت (Ukht)",
        "Anak Laki-laki": "ابن (Ibn)",
        "Anak Perempuan": "ابنة (Ibnah)",
        "Kakek": "جد (Jadd)",
        "Nenek": "جدة (Jaddah)",
        "Paman (dari ayah)": "عم (Amm)",
        "Bibi (dari ayah)": "عمة (Ammah)",
        "Paman (dari ibu)": "خال (Khaal)",
        "Bibi (dari ibu)": "خالة (Khaalah)",
    },
    "Perjalanan": {
        "Bandara": "مطار (MaTaar)",
        "Pesawat": "طائرة (Taa'irah)",
        "Kereta": "قطار (QiTaar)",
        "Mobil": "سيارة (Sayyaarah)",
        "Bus": "حافلة (Haafilah)",
        "Hotel": "فندق (Funduq)",
        "Paspor": "جواز سفر (Jawaaz Safar)",
        "Tiket": "تذكرة (Tadhkirah)",
        "Kota": "مدينة (Madiinah)",
        "Negara": "بلد (Balad)",
        "Jalan": "شارع (Shaari')",
        "Stasiun": "محطة (MaHaTTah)",
    },
    "Salam dan Frasa Umum": {
        "Halo": "مرحبا (Marhaban)",
        "Terima Kasih": "شكرا (Syukran)",
        "Ya": "نعم (Na'am)",
        "Tidak": "لا (Laa)",
        "Nama saya...": "اسمي... (Ismi...)",
        "Bagaimana kabarmu?": "كيف حالك؟ (Kaifa haluk?)",
        "Baik": "بخير (Bi Khair)",
        "Selamat pagi": "صباح الخير (Sabah al-khair)",
        "Selamat siang/sore": "مساء الخير (Masa' al-khair)",
        "Selamat malam": "ليلة سعيدة (Lailah Sa'idah)",
        "Sampai jumpa": "إلى اللقاء (Ila al-liqa')",
        "Maaf": "آسف (Aasif)",
        "Tolong": "من فضلك (Min fadlik)",
        "Berapa harganya?": "بكم هذا؟ (Bikam hadha?)",
        "Saya tidak mengerti": "لا أفهم (La afham)",
        "Bisakah Anda mengulanginya?": "هل يمكنك تكرار ذلك؟ (Hal yumkinuka takraru dhalik?)",
    },
    "Angka": {
        "Nol": "صفر (Sifr)",
        "Satu": "واحد (Waahid)",
        "Dua": "اثنان (Itsnaan)",
        "Tiga": "ثلاثة (Thalaathah)",
        "Empat": "أربعة (Arba'ah)",
        "Lima": "خمسة (Khamsah)",
        "Enam": "ستة (Sittah)",
        "Tujuh": "سبعة (Sab'ah)",
        "Delapan": "ثمانية (Thamaaniyah)",
        "Sembilan": "تسعة (Tis'ah)",
        "Sepuluh": "عشرة (Asharah)",
    }
}

# --- FUNGSI-FUNGSI APLIKASI ---

def tampilkan_menu_utama():
    print("\n--- Kamus Tematik Bahasa Arab ---")
    print("1. Jelajahi Tema Kosakata")
    print("2. Cari Kata")
    print("3. Kuis Kosakata (Acak dari Semua Tema)")
    print("4. Keluar")
    print("---------------------------------")

def tampilkan_daftar_tema():
    print("\n--- Pilih Tema ---")
    tema_list = list(kamus_tematik.keys())
    for i, tema in enumerate(tema_list):
        print(f"{i+1}. {tema}")
    print("------------------")
    return tema_list

def jelajahi_tema():
    while True:
        tema_list = tampilkan_daftar_tema()
        pilihan_tema = input("Masukkan nomor tema yang ingin dijelajahi (atau 'b' untuk kembali): ").strip().lower()

        if pilihan_tema == 'b':
            break
        
        try:
            index_tema = int(pilihan_tema) - 1
            if 0 <= index_tema < len(tema_list):
                tema_terpilih = tema_list[index_tema]
                print(f"\n--- Kosakata Tema: {tema_terpilih} ---")
                kosakata_tema = kamus_tematik[tema_terpilih]
                if kosakata_tema:
                    for indonesia, arab in kosakata_tema.items():
                        print(f"- {indonesia}: {arab}")
                else:
                    print("Tidak ada kosakata untuk tema ini.")
                input("\nTekan Enter untuk kembali ke daftar tema...")
            else:
                print("Nomor tema tidak valid.")
        except ValueError:
            print("Input tidak valid. Masukkan nomor atau 'b'.")

def cari_kata():
    print("\n--- Cari Kata ---")
    kata_cari = input("Masukkan kata dalam bahasa Indonesia atau Arab (transliterasi): ").strip().lower()
    ditemukan = False
    
    print("\nHasil Pencarian:")
    for tema, kosakata_tema in kamus_tematik.items():
        for indo, arab in kosakata_tema.items():
            if kata_cari in indo.lower() or kata_cari in arab.lower():
                print(f"- Tema: {tema}, {indo}: {arab}")
                ditemukan = True
    
    if not ditemukan:
        print("Kata tidak ditemukan dalam kamus.")
    
    input("\nTekan Enter untuk kembali ke menu...")

def kuis_kosakata_global():
    print("\n--- Kuis Kosakata Acak (Semua Tema) ---")
    
    # Kumpulkan semua kosakata dari semua tema
    semua_kosakata = {}
    for tema, kosakata_tema in kamus_tematik.items():
        semua_kosakata.update(kosakata_tema)

    if not semua_kosakata:
        print("Kamus kosong. Tidak bisa memulai kuis.")
        return

    kata_acak_indonesia = random.choice(list(semua_kosakata.keys()))
    jawaban_benar_arab = semua_kosakata[kata_acak_indonesia]

    print(f"Apa arti dari kata ini dalam bahasa Arab: '{kata_acak_indonesia}'?")
    user_answer = input("Jawaban Anda (tulis transliterasinya atau Arabnya jika bisa): ").strip()

    # Perbandingan sederhana (bisa diperbaiki untuk mencocokkan lebih baik)
    if user_answer.lower() in jawaban_benar_arab.lower():
        print("BENAR! Selamat.")
    else:
        print(f"SALAH. Jawaban yang benar adalah: {jawaban_benar_arab}")

    input("\nTekan Enter untuk melanjutkan kuis atau kembali ke menu...")

def main():
    while True:
        tampilkan_menu_utama()
        pilihan = input("Masukkan pilihan Anda: ")

        if pilihan == '1':
            jelajahi_tema()
        elif pilihan == '2':
            cari_kata()
        elif pilihan == '3':
            kuis_kosakata_global()
        elif pilihan == '4':
            print("Terima kasih telah menggunakan Kamus Tematik Bahasa Arab. Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# --- MENJALANKAN APLIKASI ---
if __name__ == "__main__":
    main()
