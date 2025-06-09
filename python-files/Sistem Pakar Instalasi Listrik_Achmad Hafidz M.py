import os
print("+------------------------------+")
print("|Selamat Datang di Sistem Pakar|")
print("|   Instalasi Listrik Rumah    |")
print("|     by : Achmad Hafidz M     |")
print("+------------------------------+")
pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah?(y/n) = ")

while pilihan == "y" :
    print("Apakah MCB sering trip/turun?")
    diagA1 = input("Jawab y/n = ")
    if diagA1 == "y" :
        print("Apakah banyak alat listrik yang sedang digunakan?")
        diagA2 = input("Jawab y/n = ")
        if diagA2 == "y" :
            print("Kemungkinan beban listrik saat ini melebihi batas")
            print("Kurangi pemakaian alat listrik yang terlalu banyak secara bersamaan")
            pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
        if diagA2 == "n" :
            print("Apakah ada suara percikan bunga api atau bau gosong?")
            diagA3 = input("Jawab y/n = ")
            if diagA3 == "y" :
                print("Periksa sambungan kabel alat listrik yang digunakan")
                print("dan periksa sambungan stop kontak, cek apakah sambungan terminalnya kendor.")
            pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
            if diagA3 == "n" :
                print("Masalah tidak dapat didiagnosa, hubungi teknisi listrik untuk analisis lebih lanjut.")
            pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")

    if diagA1 == "n" :
        print("Apakah lampu sering berkedip?")
        diagB = input("Jawab y/n = ")
        if diagB == "y" :
            print("Periksa sambungan saklar dan fitting lampu. Apabila lampu masih sering berkedip")
            print("ganti lampu dengan lampu yang baru.")
            pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
        if diagB == "n" :
            print("Apakah alat listrik sering hidup-mati?")
            diagC = input("Jawab y/n")
            if diagC == "y" :
                print("Periksa sambungan kabel alat listrik dan terminal pada stop kontak.")
                pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
            if diagC == "n" :
                print("Apakah tagihan listrik lebih tinggi dari biasanya?")
                diagD = input("Jawab y/n = ")
                if diagD == "y" :
                    print("Periksa apakah terdapat alat listrik yang dipakai secara berlebihan")
                    pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
                if diagD == "n" :
                    print("Apakah terdapat sambungan kabel stop kontak yang mengalami panas berlebih?")
                    diagE = input("Jawab y/n = ")
                    if diagE == "y" :
                        print("Matikan alat listrik dan ganti stop kontak yang tersambung dengan stop kontak lain")
                        print("yang memiliki ukuran kabel lebih besar")
                        pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")
                    if diagE == "n" :
                        print("Sepertinya instalasi listrik tidak bermasalah.")
                        print(" Apabila terdapat masalah yang tidak tertera di program ini, silahkan hubungi teknisi listrik")
                        pilihan = input("Apakah anda ingin melakukan diagnosa masalah listrik rumah lagi?(y/n) = ")

while pilihan == "n" :
    print("Diagnosa selesai. Menutup program......")
    exit()