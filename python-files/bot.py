from PIL import Image
import os

# Sabitler
DPI = 300
A4_WIDTH_MM = 297
A4_HEIGHT_MM = 210

# Kağıt boyutunu piksele çevir
def mm_to_px(mm, dpi=DPI):
    return int((mm / 25.4) * dpi)

# A4 boyutunda boş sayfa oluştur
def create_blank_a4():
    width_px = mm_to_px(A4_WIDTH_MM)
    height_px = mm_to_px(A4_HEIGHT_MM)
    return Image.new("RGB", (width_px, height_px), "white")

# Resimleri yerleştir
def layout_images(base_image_path, output_path, rows=5, cols=2, image_width_mm=70, image_height_mm=35):
    base_img = Image.open(base_image_path)

    # Resim boyutunu mm'den px'e çevir
    img_w = mm_to_px(image_width_mm)
    img_h = mm_to_px(image_height_mm)

    # A4 kağıdı oluştur
    canvas = create_blank_a4()
    canvas_w, canvas_h = canvas.size

    # Aralık hesapla
    margin_x = (canvas_w - (cols * img_w)) // (cols + 1)
    margin_y = (canvas_h - (rows * img_h)) // (rows + 1)

    # Resmi yeniden boyutlandır
    img_resized = base_img.resize((img_w, img_h))

    # Resimleri yerleştir
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (img_w + margin_x)
            y = margin_y + row * (img_h + margin_y)
            canvas.paste(img_resized, (x, y))

    canvas.save(output_path, dpi=(DPI, DPI))
    print(f"Saved: {output_path}")

# Ana program
if __name__ == "__main__":
    # Resimlerin fiziksel boyutu (mm cinsinden)
    image_width_mm = 70
    image_height_mm = 35

    layout_images("front_image.jpg", "output_front.jpg", image_width_mm=image_width_mm, image_height_mm=image_height_mm)
    layout_images("back_image.jpg", "output_back.jpg", image_width_mm=image_width_mm, image_height_mm=image_height_mm)
