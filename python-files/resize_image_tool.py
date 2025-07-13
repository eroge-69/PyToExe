from PIL import Image
import os

def main():
    print("📁 Şəkil faylını buraya atın və ya adını yazın:")
    path = input("Fayl adı: ").strip()

    if not os.path.isfile(path):
        print("❌ Fayl tapılmadı.")
        return

    try:
        img = Image.open(path)
    except:
        print("❌ Şəkil açıla bilmədi.")
        return

    print("🔢 Faizlə ölçü verin (məsələn 60 üçün: 60 və ya 130 üçün: 130):")
    try:
        percent = float(input("Faiz: ").strip())
        if percent <= 0:
            raise ValueError
    except:
        print("❌ Yanlış dəyər.")
        return

    new_size = (int(img.width * percent / 100), int(img.height * percent / 100))
    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

    base, ext = os.path.splitext(path)
    new_filename = f"{base}_resized_{int(percent)}{ext}"
    resized_img.save(new_filename)

    print(f"✅ Uğurla yadda saxlanıldı: {new_filename}")

if __name__ == "__main__":
    main()
