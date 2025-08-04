import os
import glob
import shutil

# ✅ Source folder (Desktop)
source_folder = os.path.join(os.path.expanduser("~"), "Desktop")

# ✅ Destination folder (Desktop\PDF)
destination_folder = os.path.join(source_folder, "PDF")

# ✅ Create "PDF" folder if not exists
os.makedirs(destination_folder, exist_ok=True)

# ✅ Collect all PDF files from Desktop
pdf_files = glob.glob(os.path.join(source_folder, "*.pdf"))

if pdf_files:
    print(f"✅ Found {len(pdf_files)} PDF files. Moving to {destination_folder}...")
    for file in pdf_files:
        shutil.move(file, destination_folder)  # Use shutil.copy() if you want to copy instead of move
    print("✅ All PDFs moved successfully!")
else:
    print("❌ No PDF files found on Desktop!")
