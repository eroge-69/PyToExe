import sys
import os
from PIL import Image

# The watermark file must be in the same folder as this exe
WATERMARK_PATH = os.path.join(os.path.dirname(sys.argv[0]), "watermark.png")

def add_watermark(image_path, output_dir):
    base = Image.open(image_path).convert("RGBA")
    watermark = Image.open(WATERMARK_PATH).convert("RGBA")

    # Scale watermark relative to image width
    scale = 0.25
    w = int(base.width * scale)
    h = int(watermark.height * (w / watermark.width))
    watermark = watermark.resize((w, h), Image.LANCZOS)

    # Position: bottom-right with margin
    position = (base.width - w - 20, base.height - h - 20)

    # Overlay
    transparent = Image.new("RGBA", base.size)
    transparent.paste(base, (0, 0))
    transparent.paste(watermark, position, mask=watermark)
    output_path = os.path.join(output_dir, os.path.basename(image_path))
    transparent.convert("RGB").save(output_path, "JPEG", quality=95)

def main():
    files = sys.argv[1:]
    if not files:
        print("No images provided.")
        return
    
    output_dir = os.path.join(os.path.dirname(files[0]), "watermarked")
    os.makedirs(output_dir, exist_ok=True)

    for f in files:
        try:
            add_watermark(f, output_dir)
            print(f"Processed: {f}")
        except Exception as e:
            print(f"Failed: {f} ({e})")

if __name__ == "__main__":
    main()
