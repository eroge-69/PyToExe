import time
import platform
import os

def cal_alarm():
    print("\n⏰ Süre doldu! Alarm çalıyor...")
    if platform.system() == "Windows":
        import winsound
        for _ in range(3):
            winsound.Beep(1000, 1000)
            time.sleep(0.5)
    elif platform.system() == "Darwin":
        os.system('say "Süre doldu"')
    else:
        os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')

def main():
    print("Süre Seçenekleri:")
    options = {
        "1": 120,
        "2": 240,
        "3": 360,
        "4": 480,
        "5": 720
    }
    for k,v in options.items():
        print(f"{k}. {v} dakika")

    secim = input("Lütfen bir seçenek girin (1-5): ")

    if secim not in options:
        print("Geçersiz seçim!")
        return

    dakika = options[secim]
    print(f"{dakika} dakika için sayaç başladı...")
    try:
        for i in range(dakika * 60, 0, -1):
            saat = i // 3600
            dakika_kalan = (i % 3600) // 60
            saniye = i % 60
            print(f"\rKalan süre: {saat:02d}:{dakika_kalan:02d}:{saniye:02d}", end="")
            time.sleep(1)
        print("\nSüre doldu!")
        cal_alarm()
    except KeyboardInterrupt:
        print("\nSayaç durduruldu.")

if __name__ == "__main__":
    main()