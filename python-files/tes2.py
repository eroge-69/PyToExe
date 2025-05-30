import os
import cv2
import numpy as np
import random
from PIL import Image, ImageFilter
from scipy.signal import convolve2d
from skimage.util import random_noise

# Folder konfigurasi
input_folder = "input_images"
output_root = "outputs"

# Parameter
def jpeg_quality(): return random.randint(30, 95)
def rand(prob): return random.random() < prob

# Fungsi pemrosesan
def save_step(img, img_name, step_name, step_num):
    out_dir = os.path.join(output_root, img_name, f"{step_num:02d}_{step_name}")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "result.jpg")
    cv2.imwrite(out_path, img)
    return img

def usm_sharpen(img):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    sharpened = pil_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    return cv2.cvtColor(np.array(sharpened), cv2.COLOR_RGB2BGR)

def apply_blur(img):
    ksize = 21
    sigma = random.uniform(0.2, 3)
    return cv2.GaussianBlur(img, (ksize, ksize), sigma)

def random_resize(img, prob, resize_range):
    mode = random.choices(['up', 'down', 'keep'], prob)[0]
    scale = random.uniform(*resize_range)
    h, w = img.shape[:2]
    if mode == 'keep':
        return img
    if mode == 'up':
        scale = max(1.0, scale)
    else:
        scale = min(1.0, scale)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return cv2.resize(img, new_size, interpolation=cv2.INTER_LINEAR)

def add_noise(img, gray, var_range):
    if gray:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        noisy = random_noise(gray_img, mode='gaussian', var=(random.uniform(*var_range) / 255) ** 2)
        noisy = (noisy * 255).astype(np.uint8)
        return cv2.cvtColor(noisy, cv2.COLOR_GRAY2BGR)
    else:
        noisy = random_noise(img, mode='gaussian', var=(random.uniform(*var_range) / 255) ** 2)
        return (noisy * 255).astype(np.uint8)

def add_poisson(img, scale_range):
    scale = random.uniform(*scale_range)
    noisy = np.random.poisson(img * scale) / scale
    return np.clip(noisy, 0, 255).astype(np.uint8)

def jpeg_compress(img, out_path, quality=None):
    quality = quality or jpeg_quality()
    Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save(out_path, "JPEG", quality=quality)
    return cv2.imread(out_path)

def apply_sinc(img):
    k = 21
    y, x = np.ogrid[-k//2+1:k//2+1, -k//2+1:k//2+1]
    mask = x**2 + y**2 <= (k//2)**2
    kernel = np.zeros((k, k), dtype=np.float32)
    kernel[mask] = 1
    kernel /= kernel.sum()
    return np.stack([convolve2d(img[..., c], kernel, mode='same', boundary='symm') for c in range(3)], axis=-1).astype(np.uint8)
    
def random_augment(img, hflip=True, rot=False):
    if hflip and random.random() < 0.5:
        img = cv2.flip(img, 1)
    if rot:
        k = random.randint(0, 3)
        img = np.rot90(img, k).copy()
    return img

def random_crop(img, size):
    h, w = img.shape[:2]
    if h < size or w < size:
        raise ValueError(f"Image too small for crop: {h}x{w} < {size}")
    top = random.randint(0, h - size)
    left = random.randint(0, w - size)
    return img[top:top + size, left:left + size]

# ==================== MAIN ====================
img_list = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

for img_file in img_list:
    img_name = os.path.splitext(img_file)[0]
    img = cv2.imread(os.path.join(input_folder, img_file))

    print(f"🖼️ Memproses: {img_file}")

    # Step 1: USM
    img = usm_sharpen(img)
    img = save_step(img, img_name, "usm", 1)
    gt = img.copy()  # Simpan sebagai GT sebelum proses degradasi

    # Step 2: Blur 1
    img = apply_blur(img)
    img = save_step(img, img_name, "blur1", 2)

    # Step 3: Resize 1
    img = random_resize(img, [0.2, 0.7, 0.1], [0.15, 1.5])
    img = save_step(img, img_name, "resize1", 3)

    # Step 4: Noise 1
    if rand(0.5): img = add_noise(img, gray=rand(0.4), var_range=[1, 30])
    if rand(0.5): img = add_poisson(img, [0.05, 3])
    img = save_step(img, img_name, "noise1", 4)

    # Step 5: JPEG 1
    temp_path = os.path.join(output_root, img_name, "05_jpeg1/tmp.jpg")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    img = jpeg_compress(img, temp_path)
    img = save_step(img, img_name, "jpeg1", 5)

    # Step 6: Blur 2
    if rand(0.8):
        img = apply_blur(img)
    img = save_step(img, img_name, "blur2", 6)

    # Step 7: Resize 2
    img = random_resize(img, [0.3, 0.4, 0.3], [0.3, 1.2])
    img = save_step(img, img_name, "resize2", 7)

    # Step 8: Noise 2
    if rand(0.5): img = add_noise(img, gray=rand(0.4), var_range=[1, 25])
    if rand(0.5): img = add_poisson(img, [0.05, 2.5])
    img = save_step(img, img_name, "noise2", 8)

    # Step 9: JPEG 2
    temp_path = os.path.join(output_root, img_name, "09_jpeg2/tmp.jpg")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    img = jpeg_compress(img, temp_path)
    img = save_step(img, img_name, "jpeg2", 9)

    # Step 10: Final Sinc
    if rand(0.8):
        img = apply_sinc(img)
    img = save_step(img, img_name, "final_sinc", 10)
    
    # Step 11: Augment (Flip & Rotate)
    img = random_augment(img, hflip=True, rot=False)
    gt = random_augment(gt, hflip=True, rot=False)  # GT ikut augmentasi juga
    augmented_dir = os.path.join(output_root, img_name, "10_augment")
    os.makedirs(augmented_dir, exist_ok=True)
    cv2.imwrite(os.path.join(augmented_dir, "augmented.png"), img)
    cv2.imwrite(os.path.join(augmented_dir, "gt_augmented.png"), gt)

    # Step 12: Crop
    gt_crop = random_crop(gt, 256)
    lq_crop = random_crop(img, 256)

    # Step 13: Simpan input/output akhir
    final_dir = os.path.join(output_root, img_name, "11_input_target")
    os.makedirs(final_dir, exist_ok=True)
    cv2.imwrite(os.path.join(final_dir, "GT.png"), gt_crop)
    cv2.imwrite(os.path.join(final_dir, "LQ.png"), lq_crop)


    print(f"✅ Selesai: {img_file}")

print("\n🎉 Semua gambar selesai diproses!")
