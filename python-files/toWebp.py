import sys
from PIL import Image
import os

def optimize_image_to_webp_q100(file_path, output_path=None, max_dimension=1080):
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if needed
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            original_width, original_height = img.size

            # Calculate dimensions
            if original_width > original_height:
                if original_width > max_dimension:
                    new_width = max_dimension
                    new_height = int((max_dimension / original_width) * original_height)
                else:
                    new_width, new_height = original_width, original_height
            else:
                if original_height > max_dimension:
                    new_height = max_dimension
                    new_width = int((max_dimension / original_height) * original_width)
                else:
                    new_width, new_height = original_width, original_height

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if not output_path:
                base, _ = os.path.splitext(file_path)
                output_path = base + "_q100.webp"

            # Save with quality=100 (maximum)
            img.save(output_path, "WEBP", quality=100, method=6)

            print(f"✅ Saved high-quality WebP as: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: drag and drop an image file onto this script or run with: python optimize_to_webp_q100.py image.jpg")
        input("Press Enter to exit...")
        sys.exit(1)

    input_file = sys.argv[1]
    optimize_image_to_webp_q100(input_file)
