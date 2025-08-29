import rawpy
import cv2
import numpy as np
import os
import shutil

# ----------- CONFIG ------------
input_folder = r"E:\DAVID PICKED IT"       
output_folder = r"E:\DAVID PICKED IT\GOOD_IMAGES"

# Blur and exposure thresholds (tuned for RAW)
blur_threshold = 50  # Lower = more forgiving
overexposed_pct = 0.05  # % of pixels near maximum value
underexposed_pct = 0.05 # % of pixels near minimum value
# --------------------------------

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

raw_extensions = ('.cr2', '.nef', '.arw', '.dng', '.rw2', '.orf')

def load_raw_image(file_path):
    with rawpy.imread(file_path) as raw:
        rgb = raw.postprocess()
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

# Relaxed blur detection
def is_blurry(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return lap_var < blur_threshold

# Better exposure detection for RAW
def is_overexposed(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    high_pixels = np.sum(gray >= 250)  # almost white pixels
    return high_pixels / gray.size > overexposed_pct

def is_underexposed(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    low_pixels = np.sum(gray <= 5)  # almost black pixels
    return low_pixels / gray.size > underexposed_pct

# Process all RAW images
for filename in os.listdir(input_folder):
    if filename.lower().endswith(raw_extensions):
        file_path = os.path.join(input_folder, filename)
        try:
            image = load_raw_image(file_path)
        except:
            print(f"Could not load {filename}, skipping (corrupt?).")
            continue

        # Only skip truly bad images
        if is_blurry(image):
            print(f"{filename} is blurry. Skipping.")
            continue
        if is_overexposed(image):
            print(f"{filename} is overexposed. Skipping.")
            continue
        if is_underexposed(image):
            print(f"{filename} is underexposed. Skipping.")
            continue

        # Copy good RAW file
        shutil.copy2(file_path, os.path.join(output_folder, filename))
        print(f"{filename} kept.")

print("Culling complete! Check the GOOD_IMAGES folder.")
