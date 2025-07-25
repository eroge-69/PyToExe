import os
from pillow_heif import register_heif_opener
from PIL import Image

# Register HEIC support
register_heif_opener()

# === Set your folder path here ===
folder_path = r"d:\R8982\Mes documents\TOUT LES DOC\+Missions d'audit 2025\Gestion des vacations\Audit\CAPTURES"

# Create output folder (optional)
output_folder = os.path.join(folder_path, "converted_jpg")
os.makedirs(output_folder, exist_ok=True)

# Loop through HEIC files and convert them
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".heic"):
        heic_path = os.path.join(folder_path, filename)
        jpg_filename = os.path.splitext(filename)[0] + ".jpg"
        jpg_path = os.path.join(output_folder, jpg_filename)

        try:
            with Image.open(heic_path) as img:
                img.save(jpg_path, format="JPEG", quality=95)
            print(f"✅ Converted: {filename} → {jpg_filename}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")
