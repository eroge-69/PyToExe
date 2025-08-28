import fungsi
import os

while True:
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
    
    fungsi.pilih_menu()
    menu = input("Masukkan pilihan Anda (1-5): ")
    
    if menu == '1':
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        fungsi.pesan_tiket()
        if not fungsi.kembali_menu():
            break
    
    elif menu == '2':
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        fungsi.nomor_antrian()
        if not fungsi.kembali_menu():
            break

    elif menu == '3':
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        fungsi.batalkan_pesanan()
        if not fungsi.kembali_menu():
            break
    elif menu == '4':
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        fungsi.pilih_kursi(fungsi.pengunjung)
        if not fungsi.kembali_menu():   
            break
    elif menu == '5':
        fungsi.keluar()
    else:
        fungsi.pesan_salah()
        if not fungsi.kembali_menu():
            break