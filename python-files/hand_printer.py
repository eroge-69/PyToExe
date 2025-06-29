import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# Configurations
excel_file = 'hands.xlsx'
hand_images_folder = 'hand_images'
output_image_file = 'output.png'
canvas_size = (1200, 800)  # width, height

# Read Excel Data
df = pd.read_excel(excel_file)

# Create a blank canvas
canvas = Image.new('RGB', canvas_size, 'white')
draw = ImageDraw.Draw(canvas)

# Optional: load a font for labeling
try:
    font = ImageFont.truetype('arial.ttf', 24)
except:
    font = ImageFont.load_default()

# Example data structure:
# | hand_image | x     | y     | label   |
# |------------|-------|-------|---------|
# | hand1.png  | 100   | 200   | Left    |
# | hand2.png  | 400   | 200   | Right   |

for idx, row in df.iterrows():
    image_path = os.path.join(hand_images_folder, str(row['hand_image']))
    if os.path.exists(image_path):
        hand_img = Image.open(image_path).convert('RGBA')
        # Resize if needed
        hand_img = hand_img.resize((200, 200))
        # Paste onto canvas
        canvas.paste(hand_img, (int(row['x']), int(row['y'])), hand_img)
        # Optional: add label
        if 'label' in row and not pd.isna(row['label']):
            draw.text((int(row['x']), int(row['y']) + 210), str(row['label']), fill='black', font=font)
    else:
        print(f"Image not found: {image_path}")

# Save or print the result
canvas.save(output_image_file)
print(f"Image saved as {output_image_file}. You can print it using your system print dialog.")

# To print directly (Windows example, for other OS adjust accordingly)
# Uncomment to enable printing
# import os
# os.startfile(output_image_file, "print")
