import os
import shutil
from PIL import Image, UnidentifiedImageError
import numpy as np

# === Nastavení cesty ===
source_dir = r"D:\Vytřízeno\Pictures"
target_dir = r"D:\Vytřízeno\Pictures\nefunkční"
image_extensions = ('.jpg', '.jpeg', '.bmp', '.dng', '.gif', '.heic', '.png', '.svg', '.tif', '.tiff', '.webp')
gray_threshold = 0.98  # 98 % pixelů má stejnou barvu = podezřelé

# Vytvoření cílové složky
os.makedirs(target_dir, exist_ok=True)

def is_suspicious_image(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert('L')  # grayscale
            arr = np.array(img)
            if arr.size == 0:
                return True
            counts = np.bincount(arr.flatten(), minlength=256)
            most_common = np.max(counts)
            ratio = most_common / arr.size
            return ratio >= gray_threshold
    except UnidentifiedImageError:
        return True
    except Exception:
        return True

print("Kontrola obrázků...")

moved = 0
checked = 0

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.lower().endswith(image_extensions):
            checked += 1
            full_path = os.path.join(root, file)
            if is_suspicious_image(full_path):
                name_only = os.path.basename(full_path)
                target_path = os.path.join(target_dir, name_only)
                i = 1
                while os.path.exists(target_path):
                    name, ext = os.path.splitext(name_only)
                    target_path = os.path.join(target_dir, f"{name}_{i}{ext}")
                    i += 1
                shutil.move(full_path, target_path)
                print(f"[PŘESUNUTO] {full_path}")
                moved += 1

print(f"\nHotovo. Zkontrolováno: {checked}, přesunuto podezřelých: {moved}")
input("Stiskni Enter pro ukončení...")
