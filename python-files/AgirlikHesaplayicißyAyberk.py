def hesapla():
    try:
        Wi = float(input("Intensity ağırlığını gir (Wi): "))
        Ri = float(input("Intensity tekrar sayısını gir (Ri): "))
        Rv = float(input("Volume tekrar sayısını gir (Rv): "))
        alpha = float(input("Üs katsayısını gir (0.6 - 0.8 arası): "))
        if not (0.6 <= alpha <= 0.8):
            print("Üs katsayısı 0.6 ile 0.8 arasında olmalı.")
            return

        Wv = Wi * ((Ri / Rv) ** alpha)
        print(f"Volume günündeki ağırlık (Wv): {Wv:.2f} kg")
    except ValueError:
        print("Lütfen geçerli bir sayı giriniz.")

    input("\nÇıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    hesapla()
