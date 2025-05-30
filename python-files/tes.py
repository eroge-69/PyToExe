import os
import cv2
import numpy as np
import random

# Fungsi-fungsi pemrosesan gambar
def resize_image(image, scale_range=(0.15, 1.5)):
    h, w = image.shape[:2]
    scale = random.uniform(*scale_range)
    new_size = (int(w * scale), int(h * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)

def add_gaussian_noise(image, noise_range=(1, 30)):
    sigma = random.uniform(*noise_range)
    gauss = np.random.normal(0, sigma, image.shape).astype(np.float32)
    noisy = image.astype(np.float32) + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)

def add_poisson_noise(image, scale_range=(0.05, 3)):
    scale = random.uniform(*scale_range)
    noisy = np.random.poisson(image.astype(np.float32) * scale) / scale
    return np.clip(noisy, 0, 255).astype(np.uint8)

def convert_to_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_jpeg_compression(image, quality_range=(30, 95)):
    quality = random.randint(*quality_range)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode('.jpg', image, encode_param)
    return cv2.imdecode(encimg, 1)

# Fungsi utama
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input_images')
    output_base = os.path.join(base_dir, 'output')

    # Daftar fungsi pemrosesan dan nama folder outputnya
    processes = [
        ('01_resize', resize_image),
        ('02_gaussian_noise', add_gaussian_noise),
        ('03_poisson_noise', add_poisson_noise),
        ('04_grayscale', convert_to_grayscale),
        ('05_jpeg_compression', apply_jpeg_compression),
        ('06_resize2', resize_image),
        ('07_gaussian_noise2', add_gaussian_noise),
        ('08_poisson_noise2', add_poisson_noise),
        ('09_grayscale2', convert_to_grayscale),
        ('10_jpeg_compression2', apply_jpeg_compression)
    ]

    # Membuat folder output jika belum ada
    for folder_name, _ in processes:
        os.makedirs(os.path.join(output_base, folder_name), exist_ok=True)

    # Memproses setiap gambar dalam folder input
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Gagal membaca gambar: {filename}")
                continue
            current_image = image
            name, ext = os.path.splitext(filename)
            
            # Proses gambar satu per satu
            for folder_name, func in processes:
                try:
                    # Memproses gambar dengan fungsi saat ini
                    current_image = func(current_image)

                    # Menentukan output filename dan path berdasarkan proses
                    if folder_name == '05_jpeg_compression' or folder_name == '10_jpeg_compression2':
                        output_filename = f"{name}.jpg"  # Simpan sebagai .jpg untuk kompresi JPEG
                    else:
                        output_filename = f"{name}{ext}"  # Simpan dengan ekstensi asli untuk proses lainnya
                    
                    output_path = os.path.join(output_base, folder_name, output_filename)

                    # Menyimpan gambar hasil proses
                    cv2.imwrite(output_path, current_image)
                    print(f"Proses {folder_name} berhasil untuk {filename}")
                except Exception as e:
                    print(f"Kesalahan saat memproses {filename} dengan {folder_name}: {e}")
                    break  # Hentikan pemrosesan lebih lanjut untuk gambar ini

if __name__ == "__main__":
    main()
