from pdf2image import convert_from_path
from PIL import Image
import os

# Konfigurasi
input_pdf = "contoh.pdf"
output_folder = "barcode_output"
os.makedirs(output_folder, exist_ok=True)

# Konversi PDF ke gambar
pages = convert_from_path(input_pdf, dpi=300)

# Parameter berdasarkan pengukuran pixel Anda
FIRST_BARCODE_X = 25       # Posisi X barcode pertama
FIRST_BARCODE_Y = 0         # Posisi Y barcode pertama (akan disesuaikan)
BARCODE_WIDTH = 275         # Lebar barcode
BARCODE_HEIGHT = 250        # Tinggi barcode
HORIZONTAL_SPACING = 120     # Jarak horizontal antar barcode
VERTICAL_SPACING = 0       # Jarak vertikal antar barcode
COLUMNS = 5                 # Jumlah kolom
ROWS = 2                    # Jumlah baris per halaman

output_index = 1

for page in pages:
    img_width, img_height = page.size
    
    # Hitung margin atas berdasarkan rasio resolusi
    scale_factor = img_width / 1920
    first_barcode_y = int(FIRST_BARCODE_Y * scale_factor)
    
    for row in range(ROWS):
        for col in range(COLUMNS):
            # Hitung posisi barcode (perbaikan di sini - menambahkan tanda kurung penutup)
            x = int((FIRST_BARCODE_X + col * (BARCODE_WIDTH + HORIZONTAL_SPACING)) * scale_factor)
            y = int((first_barcode_y + row * (BARCODE_HEIGHT + VERTICAL_SPACING)) * scale_factor)
            
            # Hitung area crop
            left = x
            upper = y
            right = left + int(BARCODE_WIDTH * scale_factor)
            lower = upper + int(BARCODE_HEIGHT * scale_factor)
            
            # Pastikan tidak melebihi batas halaman
            if right > img_width or lower > img_height:
                continue
            
            # Crop dan simpan
            crop_box = (left, upper, right, lower)
            cropped = page.crop(crop_box)
            
            output_path = os.path.join(output_folder, f"barcode_{output_index:03}.png")
            cropped.save(output_path)
            print(f"Disimpan: {output_path} (Position: {x},{y})")
            output_index += 1

print(f"\nSelesai! Total {output_index-1} barcode diproses.")