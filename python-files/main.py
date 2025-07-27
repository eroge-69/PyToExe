# Deklarasi variabel
harga_barang1 = 50000  # Harga barang pertama dalam Rupiah
harga_barang2 = 30000  # Harga barang kedua dalam Rupiah
diskon_persen = 10     # Persentase diskon (misal: 10 untuk 10%)
# Hitung total harga sebelum diskon
total_harga_sebelum_diskon = harga_barang1 + harga_barang2
# Hitung jumlah diskon dalam Rupiah
jumlah_diskon_rupiah = (diskon_persen / 100) * total_harga_sebelum_diskon
# Hitung total harga setelah diskon
total_harga_setelah_diskon = total_harga_sebelum_diskon - jumlah_diskon_rupiah
# Cetak semua hasil perhitungan
print(f"Harga barang 1: Rp {harga_barang1:,}")
print(f"Harga barang 2: Rp {harga_barang2:,}")
print(f"Diskon: {diskon_persen}%")
print("-" * 30)
print(f"Total harga sebelum diskon: Rp {total_harga_sebelum_diskon:,}")
print(f"Jumlah diskon: Rp {jumlah_diskon_rupiah:,}")
print(f"Total harga setelah diskon: Rp {total_harga_setelah_diskon:,}")