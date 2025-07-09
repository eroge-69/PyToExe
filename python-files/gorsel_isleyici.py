
from PIL import Image
import os

input_folder = r"E:\Eltos\Fabrika Ürün Görseli\1 - Testere Grubu"
output_folder = r"E:\Eltos\3000 x 3000 Beyaz  Arka Planlı Web Görseli"
os.makedirs(output_folder, exist_ok=True)

canvas_size = (3000, 3000)
padding = 200
max_img_size = (canvas_size[0] - 2 * padding, canvas_size[1] - 2 * padding)
background_color = (255, 255, 255)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        img_path = os.path.join(input_folder, filename)
        try:
            img = Image.open(img_path).convert('RGBA')
            img.thumbnail(max_img_size, Image.LANCZOS)

            canvas = Image.new('RGBA', canvas_size, background_color + (255,))
            x = (canvas_size[0] - img.width) // 2
            y = (canvas_size[1] - img.height) // 2
            canvas.paste(img, (x, y), img if img.mode == 'RGBA' else None)
            rgb_canvas = canvas.convert('RGB')

            save_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.jpg')
            rgb_canvas.save(save_path, quality=95)
            print(f"{filename} işlendi.")
        except Exception as e:
            print(f"Hata: {filename} → {e}")

print("✅ Tüm görseller başarıyla işlendi.")
input("Çıkmak için Enter'a basın.")
