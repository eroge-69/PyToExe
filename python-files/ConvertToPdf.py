from PIL import Image  # install by > python3 -m pip install --upgrade Pillow  # ref. https://pillow.readthedocs.io/en/latest/installation.html#basic-installation
from pillow_heif import register_heif_opener

import os

register_heif_opener()

# my_files = [f for f in listdir("/home/piotr/documents")]

images = []

for file in os.listdir():
    if not (file == 'ConvertToPdf.py' or file == 'FinalPdf.pdf' or file=='ConvertToPdf.exe'):
        images.append(Image.open(file))

pdf_path = "FinalPdf.pdf"
    
images[0].save(
    pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
)