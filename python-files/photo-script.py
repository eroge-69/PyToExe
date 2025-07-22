import os
import time
from PIL import Image, ImageOps, ImageFilter
from ftplib import FTP

# ===============================
# NASTAVENÍ
INPUT_DIR = "puvodni"
OUTPUT_DIR = "upravene"
UNEDITED_DIR = "neupravene"
QUALITY = 85
FINAL_DPI = (72, 72)

WHITE_THRESHOLD = 240
WHITE_RATIO_THRESHOLD = 0.2

# CROP_PADDING = 0.05  # 5% kolem produktu (pouze pro bílé fotky)

SHARPEN_RADIUS = 1
SHARPEN_PERCENT = 100
SHARPEN_THRESHOLD = 2

MIN_SIZE = 1000
MAX_SIZE = 1500
ABSOLUTE_MIN_SIZE = 500

# ---- FTP nastavení ----
FTP_ENABLED = True            # nastav na False, pokud nechceš nahrávat
FTP_HOST = "jakubrejlek.cz"
FTP_USER = "jakubrejle5"
FTP_PASS = "Pdp3x7CJUY"
FTP_DIR = ""  # cílová složka na FTP
# ===============================

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UNEDITED_DIR, exist_ok=True)

def is_white_background(img: Image.Image) -> bool:
    if img.mode != "RGB":
        img = img.convert("RGB")
    gray = img.convert("L")
    pixels = list(gray.getdata())
    white_pixels = sum(1 for p in pixels if p >= WHITE_THRESHOLD)
    ratio = white_pixels / len(pixels)
    return ratio >= WHITE_RATIO_THRESHOLD

def crop_white_background(img: Image.Image) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    gray = img.convert("L")
    mask = gray.point(lambda x: 255 if x < WHITE_THRESHOLD else 0)
    bbox = mask.getbbox()
    return img.crop(bbox) if bbox else img

# def crop_white_background(img: Image.Image) -> Image.Image:  // crop padding version
#     """Ořízne bílé/téměř bílé pozadí + přidá CROP_PADDING."""
#     if img.mode != "RGB":
#         img = img.convert("RGB")
#     gray = img.convert("L")
#     mask = gray.point(lambda x: 255 if x < WHITE_THRESHOLD else 0)
#     bbox = mask.getbbox()
#     if not bbox:
#         return img
#
#     # Přidání "bezpečné mezery" podle CROP_PADDING
#     padding_x = int((bbox[2] - bbox[0]) * CROP_PADDING)
#     padding_y = int((bbox[3] - bbox[1]) * CROP_PADDING)
#
#     left = max(bbox[0] - padding_x, 0)
#     top = max(bbox[1] - padding_y, 0)
#     right = min(bbox[2] + padding_x, img.width)
#     bottom = min(bbox[3] + padding_y, img.height)
#
#     return img.crop((left, top, right, bottom))

def add_square_with_border(img: Image.Image) -> Image.Image:
    max_side = max(img.width, img.height)
    square = Image.new("RGB", (max_side, max_side), (255, 255, 255))
    square.paste(img, ((max_side - img.width)//2, (max_side - img.height)//2))
    border_size = int(0.05 * max_side)
    return ImageOps.expand(square, border_size, fill="white")

def upscale_and_sharpen(img: Image.Image, target_size: int) -> Image.Image:
    resized = img.resize((target_size, target_size), Image.LANCZOS)
    return resized.filter(
        ImageFilter.UnsharpMask(
            radius=SHARPEN_RADIUS,
            percent=SHARPEN_PERCENT,
            threshold=SHARPEN_THRESHOLD
        )
    )

def resize_only(img: Image.Image) -> Image.Image:
    max_side = max(img.width, img.height)
    if max_side > MAX_SIZE:
        return img.resize((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    elif MIN_SIZE + 250 <= max_side <= MAX_SIZE:
        return upscale_and_sharpen(img, MAX_SIZE)
    elif MIN_SIZE <= max_side < MIN_SIZE + 250:
        return img
    elif ABSOLUTE_MIN_SIZE <= max_side < MIN_SIZE:
        return upscale_and_sharpen(img, MIN_SIZE)
    else:
        return None

def save_as_jpg(img: Image.Image, path: str):
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, format="JPEG", dpi=FINAL_DPI, quality=QUALITY, optimize=True)

def process_image(file_path, output_path, unedited_path):
    img = Image.open(file_path)

    if is_white_background(img):
        img = crop_white_background(img)
        img = add_square_with_border(img)
        max_side = max(img.width, img.height)

        if max_side > MAX_SIZE:
            final_img = img.resize((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
        elif MIN_SIZE + 250 <= max_side <= MAX_SIZE:
            final_img = upscale_and_sharpen(img, MAX_SIZE)
        elif MIN_SIZE <= max_side < MIN_SIZE + 250:
            final_img = img
        elif ABSOLUTE_MIN_SIZE <= max_side < MIN_SIZE:
            final_img = upscale_and_sharpen(img, MIN_SIZE)
        else:
            save_as_jpg(img, unedited_path)
            print(f"⚠ (Bílá) Malý obrázek do neupravené: {os.path.basename(file_path)}")
            return

        save_as_jpg(final_img, output_path)
        print(f"✅ (Bílá) Hotovo: {os.path.basename(file_path)}")

    else:
        final_img = resize_only(img)
        if final_img is None:
            save_as_jpg(img, unedited_path)
            print(f"⚠ (Reálné) Malý obrázek do neupravené: {os.path.basename(file_path)}")
            return

        save_as_jpg(final_img, output_path)
        print(f"✅ (Reálné) Hotovo: {os.path.basename(file_path)}")

def upload_to_ftp():
    if not FTP_ENABLED:
        return

    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)
        print(f"\n🌐 Připojeno k FTP: {FTP_HOST} ({FTP_DIR})")

        for filename in os.listdir(OUTPUT_DIR):
            if filename.lower().endswith(".jpg"):
                local_path = os.path.join(OUTPUT_DIR, filename)
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {filename}", f)
                print(f"⬆ Nahráno na FTP: {filename}")

        ftp.quit()
        print("✅ Všechny upravené fotky byly nahrány na FTP.")
    except Exception as e:
        print(f"❌ Chyba při nahrávání na FTP: {e}")

def main():
    start_time = time.time()

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".bmp"))]
    if not files:
        print("Ve složce 'vstup' nejsou žádné fotky!")
        return

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        base_name = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(OUTPUT_DIR, base_name)
        unedited_path = os.path.join(UNEDITED_DIR, base_name)

        try:
            process_image(input_path, output_path, unedited_path)
        except Exception as e:
            print(f"❌ Chyba u souboru {filename}: {e}")

    upload_to_ftp()

    # Čas zpracování
    elapsed = int(time.time() - start_time)
    h, m = divmod(elapsed, 3600)
    m, s = divmod(m, 60)
    print(f"\n✅ Vše hotovo za {h:02d}:{m:02d}:{s:02d}")

if __name__ == "__main__":
    main()