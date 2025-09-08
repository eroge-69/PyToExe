import os
from PIL import Image
from tkinter import filedialog, Tk

# Hide the main Tk window
Tk().withdraw()

# Select the main folder
folder = filedialog.askdirectory(title="Select Main Folder (any file type to jpg)")

if not folder:
    print("No folder selected. Exiting...")
    exit()

# Walk through all subfolders
for root, dirs, files in os.walk(folder):
    for file in files:
        if file.lower().endswith(('.webp', '.avif')):
            filepath = os.path.join(root, file)
            try:
                img = Image.open(filepath).convert("RGB")
                new_name = os.path.splitext(file)[0] + "_copy.jpg"
                save_path = os.path.join(root, new_name)
                img.save(save_path, "JPEG")
                print(f"Converted: {filepath} → {save_path}")
            except Exception as e:
                print(f"Error converting {filepath}: {e}")

print("\n✅ Conversion Done!")
input("Press Enter to exit...")
