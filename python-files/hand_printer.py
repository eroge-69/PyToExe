import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def resource_path(relative_path):
    # For PyInstaller to find data files
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurations
excel_file = resource_path('hands.xlsx')
hand_images_folder = resource_path('hand_images')
output_image_file = resource_path('output.png')
canvas_size = (1200, 800)  # width, height

# Read Excel Data
df = pd.read_excel(excel_file)

# Create a blank canvas
canvas = Image.new('RGB', canvas_size, 'white')
draw = ImageDraw.Draw(canvas)

# Optional: load a font for labeling
try:
    font = ImageFont.truetype(resource_path('arial.ttf'), 24)
except:
    font = ImageFont.load_default()

for idx, row in df.iterrows():
    image_path = os.path.join(hand_images_folder, str(row['hand_image']))
    if os.path.exists(image_path):
        hand_img = Image.open(image_path).convert('RGBA')
        hand_img = hand_img.resize((200, 200))
        canvas.paste(hand_img, (int(row['x']), int(row['y'])), hand_img)
        if 'label' in row and not pd.isna(row['label']):
            draw.text((int(row['x']), int(row['y']) + 210), str(row['label']), fill='black', font=font)
    else:
        print(f"Image not found: {image_path}")

canvas.save(output_image_file)
print(f"Image saved as {output_image_file}. You can print it using your system print dialog.")
