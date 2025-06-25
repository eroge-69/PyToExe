import os
import shutil
from PIL import Image, ImageStat, ImageFilter
from tqdm import tqdm

# Dossiers source et destination
SRC_DIR = r"D:\2020"
DST_DIR = r"E:\Photo"

# Extensions photos et vidéos supportées
PHOTO_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.jfif', '.heic', '.webp'}
VIDEO_EXT = {'.mp4', '.mov', '.avi', '.3gp', '.mkv', '.wmv', '.flv'}

def is_image_blurry(image, threshold=100):
    # Détection flou via variance du laplacien (simplifié)
    gray = image.convert('L')
    lap = gray.filter(ImageFilter.FIND_EDGES)
    variance = ImageStat.Stat(lap).var[0]
    return variance < threshold

def is_image_too_dark(image, threshold=40):
    # Détection trop sombre par luminosité moyenne
    stat = ImageStat.Stat(image.convert('L'))
    return stat.mean[0] < threshold

def is_image_too_bright(image, threshold=215):
    # Détection surexposition par luminosité moyenne
    stat = ImageStat.Stat(image.convert('L'))
    return stat.mean[0] > threshold

def is_image_usable(image_path):
    try:
        with Image.open(image_path) as img:
            if is_image_blurry(img):
                return False
            if is_image_too_dark(img):
                return False
            if is_image_too_bright(img):
                return False
            return True
    except Exception:
        # Si problème d'ouverture, on exclut
        return False

def find_existing_files(dst_dir):
    # Retourne un dict {nom_fichier: taille} pour la base propre
    files = {}
    for f in os.listdir(dst_dir):
        path = os.path.join(dst_dir, f)
        if os.path.isfile(path):
            files[f] = os.path.getsize(path)
    return files

def get_incremented_name(dst_dir, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(dst_dir, new_name)):
        new_name = f"{name}_{counter}{ext}"
        counter +=1
    return new_name

def copy_file_with_check(src_path, dst_dir, existing_files):
    filename = os.path.basename(src_path)
    size = os.path.getsize(src_path)

    # Si fichier existant avec même nom et taille, on skip
    if filename in existing_files and existing_files[filename] == size:
        return False  # doublon détecté

    # Sinon, on copie avec incrément si besoin
    target_name = filename
    if filename in existing_files:
        target_name = get_incremented_name(dst_dir, filename)

    dst_path = os.path.join(dst_dir, target_name)
    shutil.copy2(src_path, dst_path)
    existing_files[target_name] = size
    return True

def main():
    existing_files = find_existing_files(DST_DIR)
    all_files = []
    for root, _, files in os.walk(SRC_DIR):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in PHOTO_EXT or ext in VIDEO_EXT:
                all_files.append(os.path.join(root, f))

    print(f"Found {len(all_files)} media files in source.")

    copied_count = 0

    for filepath in tqdm(all_files, desc="Processing files"):
        ext = os.path.splitext(filepath)[1].lower()

        # Pour les images, check qualité
        if ext in PHOTO_EXT:
            if not is_image_usable(filepath):
                continue

        # Pour les vidéos, pas de check qualité, juste nom+taille

        if copy_file_with_check(filepath, DST_DIR, existing_files):
            copied_count += 1

    print(f"Copied {copied_count} new files to {DST_DIR}.")

if __name__ == "__main__":
    main()