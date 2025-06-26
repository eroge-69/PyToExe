
from PIL import Image
import sys
import os

def replace_transparency_with_white(input_path, output_path):
    # Open the image
    img = Image.open(input_path).convert("RGBA")
    
    # Create a white background image
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    
    # Composite the image with white background
    result = Image.alpha_composite(white_bg, img)
    
    # Convert to RGB and save
    result.convert("RGB").save(output_path, "PNG")
    print(f"Saved image with white background to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: replace_alpha.exe input.png output.png")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        replace_transparency_with_white(input_file, output_file)
