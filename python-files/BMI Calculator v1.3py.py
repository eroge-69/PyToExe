from datetime import datetime, timedelta, timezone
import math

#Language Selection
print("Sila Pilih Bahasa\nPlease Choose Language")
print("1 - Bahasa Melayu\n2 - English")

langsel = True
while langsel:
    lang = input("Input: ")
    match lang:
        case "1":
            #Display On BM
            print("#################################################")
            print("   BBBBBBBBB     MMMMM   MMMMM   IIIIIII")
            print("   BBB     BBB   MMMMMM MMMMMM     III")
            print("   BBB     BBB   MMM MMMMM MMM     III")
            print("   BBBBBBBB      MMM  MMM  MMM     III   v1.3py")
            print("   BBB     BBB   MMM       MMM     III")
            print("   BBB     BBB   MMM       MMM     III")
            print("   BBBBBBBBB     MMM       MMM   IIIIIII")
            print("#################################################")
            print("Selamat Datang Ke BMI Calculator v1.3py")
            print("Direka oleh Fuad Muhammad Najmudin Bin Ali Puad")
            print("Direka Pada 18/8/2025")
            print("Dikemaskini Pada 20/8/2025")
            tz_utc_plus_8 = timezone(timedelta(hours=8), 'UTC+8')
            now_utc = datetime.now(timezone.utc)
            now_utc_plus_8 = now_utc.astimezone(tz_utc_plus_8)
            print(f"Diakses Oleh Pengguna Pada", (now_utc_plus_8.strftime("%x")),(now_utc_plus_8.strftime("%X")))

            #User Input
            run = True
            while run:
                print("-----------------------------------------------------------------------")
                w = input("Berapakah Berat Badan Anda Dalam Kilogram, kg:")
                h = input("Berapakah Tinggi Badan Anda Dalam Sentimeter, cm:")

                #BMI Calculation
                h2 = float(h) / 100
                H = pow(float(h2), float(h2))
                BMI = float(w) / float(H)

                #Result
                print("BMI Anda Adalah:", BMI)

                #Kategori BMI
                if BMI < 16.0:
                    print("Anda Adalah KURUS BERLEBIHAN\n")
                elif BMI >= 16.0 and BMI < 17.0:
                    print("Anda Adalah KURUS SEDERHANA\n")
                elif BMI >= 17.0 and BMI < 18.5:
                    print("Anda Adalah KURUS SEDIKIT\n")
                elif BMI >= 18.5 and BMI < 25.0:
                    print("Anda Adalah BIASA\n")
                elif BMI >= 25.0 and BMI < 30.0:
                    print("Anda Adalah BERAT BERLEBIHAN\n")
                elif BMI >= 30.0 and BMI < 35.0:
                    print("Anda Adalah OBESE KELAS I\n")
                elif BMI >= 35.0 and BMI < 40:
                    print("Anda Adalah OBESE KELAS II\n")
                else:
                    print("Anda Adalah OBESE KELAS III\n")
    
                print("Adakah Anda Mahu Melakukan Pengiraan BMI Yang Lain?\nY - Ya, Teruskan Dengan Pengiraan Seterusnya\nN - Tidak, Tamatkan Program Ini")
                YesNo = True
                while YesNo:
                    choice = input("Pilihan Anda:")
                    if choice in ["y", "Y"]:
                        run = True
                        break
                    elif choice in ["n", "N"]:
                        print("Terima Kasih Kerana Menggunakan Sistem Ini :)")
                        run = False
                        langsel = False
                        break
                    else:
                        print("Pilihan Ini Tiada, Sila Masukkan y, Y, n or N")
                        YesNo = True
        case "2":
            #Display On BI
            print("#################################################")
            print("   BBBBBBBBB     MMMMM   MMMMM   IIIIIII")
            print("   BBB     BBB   MMMMMM MMMMMM     III")
            print("   BBB     BBB   MMM MMMMM MMM     III")
            print("   BBBBBBBB      MMM  MMM  MMM     III   v1.3py")
            print("   BBB     BBB   MMM       MMM     III")
            print("   BBB     BBB   MMM       MMM     III")
            print("   BBBBBBBBB     MMM       MMM   IIIIIII")
            print("#################################################")
            print("Welcome To BMI Calculator v1.3py")
            print("Designed By Fuad Muhammad Najmudin Bin Ali Puad")
            print("Designed At 18/8/2025")
            print("Updated At 20/8/2025")
            tz_utc_plus_8 = timezone(timedelta(hours=8), 'UTC+8')
            now_utc = datetime.now(timezone.utc)
            now_utc_plus_8 = now_utc.astimezone(tz_utc_plus_8)
            print(f"Accessed By User At", (now_utc_plus_8.strftime("%x")),(now_utc_plus_8.strftime("%X")))

            #User Input
            run = True
            while run:
                print("-----------------------------------------------------------------------")
                w = input("What Is You Weight In Kilogram, kg:")
                h = input("What Is Your Height In Centimeter, cm:")

                #BMI Calculation
                h2 = float(h) / 100
                H = pow(float(h2), float(h2))
                BMI = float(w) / float(H)

                #Result
                print("Your BMI Is:", BMI)

                #Kategori BMI
                if BMI < 16.0:
                    print("You Are In SEVERE THINNESS\n")
                elif BMI >= 16.0 and BMI < 17.0:
                    print("You Are In MODERATE THINNESS\n")
                elif BMI >= 17.0 and BMI < 18.5:
                    print("You Are In MILD THINNESS\n")
                elif BMI >= 18.5 and BMI < 25.0:
                    print("You Are In NORMAL\n")
                elif BMI >= 25.0 and BMI < 30.0:
                    print("You Are In OVERWEIGHT\n")
                elif BMI >= 30.0 and BMI < 35.0:
                    print("You Are In OBESE CLASS I\n")
                elif BMI >= 35.0 and BMI < 40:
                    print("You Are In OBESE CLASS II\n")
                else:
                    print("You Are In OBESE CLASS III\n")
    
                print("Do You Want To Make Next BMI Calculation?\nY - Yes, Continue For Next Calculation\nN - No, Terminate This Program")
                YesNo = True
                while YesNo:
                    choice = input("Your Choice:")
                    if choice in ["y", "Y"]:
                        run = True
                        break
                    elif choice in ["n", "N"]:
                        print("Thank You For Using This System :)")
                        run = False
                        langsel = False
                        break
                    else:
                        print("Invalid Choice, Please Enter y, Y, n or N")
                        YesNo = True
        case _:
            print("Pilihan itu Tiada\nThat Selection Unavailable")
            langsel = True