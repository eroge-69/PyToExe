
from PIL import Image, ImageDraw, ImageFont
import os

def create_number_image(number):
    width, height = 100, 900
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()

    text = str(number)
    text_width, text_height = draw.textsize(text, font=font)
    position = ((width - text_width) // 2, (height - text_height) // 2)

    draw.text(position, text, fill="black", font=font)
    filename = f"{number}.png"
    img.save(filename)
    print(f"תמונה נוצרה בהצלחה: {filename}")

if __name__ == "__main__":
    num = input("הזן מספר: ")
    if num.isdigit():
        create_number_image(num)
    else:
        print("יש להזין מספר חוקי.")
