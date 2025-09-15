# Aplikasi Perpustakaan Sederhana
# Fitur: Tambah, Tampilkan, Cari, Hapus buku

# List untuk menyimpan data buku
daftar_buku = []

def tambah_buku():
    print("\n=== TAMBAH BUKU ===")
    judul = input("Masukkan judul buku: ")
    penulis = input("Masukkan nama penulis: ")
    tahun = input("Masukkan tahun terbit: ")
    genre = input("Masukkan genre buku: ")
    
    buku = {
        "judul": judul,
        "penulis": penulis,
        "tahun": tahun,
        "genre": genre
    }
    
    daftar_buku.append(buku)
    print(f"Buku '{judul}' berhasil ditambahkan!\n")

def tampilkan_buku():
    print("\n=== DAFTAR BUKU ===")
    if not daftar_buku:
        print("Tidak ada buku dalam koleksi.\n")
        return
    
    for i, buku in enumerate(daftar_buku, 1):
        print(f"{i}. Judul: {buku['judul']}")
        print(f"   Penulis: {buku['penulis']}")
        print(f"   Tahun: {buku['tahun']}")
        print(f"   Genre: {buku['genre']}")
        print()

def cari_buku():
    print("\n=== CARI BUKU ===")
    if not daftar_buku:
        print("Tidak ada buku dalam koleksi.\n")
        return
    
    kata_kunci = input("Masukkan judul atau penulis buku yang dicari: ").lower()
    hasil_pencarian = []
    
    for buku in daftar_buku:
        if (kata_kunci in buku['judul'].lower() or 
            kata_kunci in buku['penulis'].lower()):
            hasil_pencarian.append(buku)
    
    if not hasil_pencarian:
        print("Tidak ditemukan buku dengan kata kunci tersebut.\n")
        return
    
    print(f"\nDitemukan {len(hasil_pencarian)} buku:")
    for i, buku in enumerate(hasil_pencarian, 1):
        print(f"{i}. Judul: {buku['judul']}")
        print(f"   Penulis: {buku['penulis']}")
        print(f"   Tahun: {buku['tahun']}")
        print(f"   Genre: {buku['genre']}")
        print()

def hapus_buku():
    print("\n=== HAPUS BUKU ===")
    if not daftar_buku:
        print("Tidak ada buku dalam koleksi.\n")
        return
    
    tampilkan_buku()
    try:
        nomor = int(input("Masukkan nomor buku yang akan dihapus: "))
        if 1 <= nomor <= len(daftar_buku):
            buku_dihapus = daftar_buku.pop(nomor - 1)
            print(f"Buku '{buku_dihapus['judul']}' berhasil dihapus!\n")
        else:
            print("Nomor tidak valid.\n")
    except ValueError:
        print("Masukkan nomor yang valid.\n")

def main():
    while True:
        print("=== APLIKASI PERPUSTAKAAN SEDERHANA ===")
        print("===      DIBUAT OLEH PAK MUFA ===")
        print("===         PRAKTIK 11 F1 ===")
        print("1. Tambah Buku")
        print("2. Tampilkan Semua Buku")
        print("3. Cari Buku")
        print("4. Hapus Buku")
        print("5. Keluar")
        
        pilihan = input("Masukkan pilihan (1-5): ")
        
        if pilihan == "1":
            tambah_buku()
        elif pilihan == "2":
            tampilkan_buku()
        elif pilihan == "3":
            cari_buku()
        elif pilihan == "4":
            hapus_buku()
        elif pilihan == "5":
            print("Terima kasih telah menggunakan aplikasi perpustakaan!")
            break
        else:
            print("Pilihan tidak valid. Silakan masukkan angka 1-5.\n")

if __name__ == "__main__":
    main()