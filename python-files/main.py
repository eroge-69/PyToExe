import os
from datetime import datetime

def create_file_content(kurs_cb, kurs_buy, kurs_sell, n):
    current_date = datetime.now().strftime("%Y%m%d")
    year_day = datetime.now().strftime("%j")
    current_time = input("Soat nechidagi kurs? Masalan: 0930 =>")

    content = f"""FH000001FX_RATES  10 09060 {current_date}{current_time}0000{int(n):02d}{current_date}                                                                                                                                                *
RD00000209060 860840                                0000000{int(kurs_cb):07d}0000000000000{int(kurs_buy):07d}0000000000000{int(kurs_sell):07d}0000000000000{int(kurs_cb):07d}00000000010000001000                 N                                 *
FT000003{int(n):06d}                                                                                                                                                                                       *
"""

    file_name = f"K9060_{int(n):02d}.{year_day}"

    return content, file_name

def save_file(content, file_name):
    with open(file_name, 'w') as file:
        file.write(content)
    print(f"Fayl '{file_name}' saqlandi.")

def main():
    kurs_cb = input("Markaziy bank kursi (7 xonali): ")
    kurs_buy = input("Sotib olish kursi (7 xonali): ")
    kurs_sell = input("Sotish kursi (7 xonali): ")
    n = input("Nechanchi marta (raqam bilan, m.n., 1, 2, ...): ")

    if not kurs_cb.isdigit() or not kurs_buy.isdigit() or not kurs_sell.isdigit() or not n.isdigit():
        print("Noto`g`ri ma'lumot. Iltimos kiritganlaringiz faqat raqam ekanini tekshiring!")
        return

    content, file_name = create_file_content(kurs_cb, kurs_buy, kurs_sell, n)

    save_file(content, file_name)

if __name__ == "__main__":
    main()
