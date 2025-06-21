#!/usr/bin/python
import os
import re
from PIL import Image
from pathlib import Path

# Round color channel to nearest multiple of 8, capped at 248
def round8(value):
    return min(248, int(round(value / 8.0) * 8))

# Extract palette directly from BMP color table (not pixel order)
def extract_palette_from_bmp_palette(bmp_path):
    with Image.open(bmp_path) as im:
        im = im.convert("P")
        raw_palette = im.getpalette()[:768]  # up to 256 RGB entries

        seen = set()
        ordered_colors = []
        for i in range(0, len(raw_palette), 3):
            r, g, b = raw_palette[i:i+3]
            r, g, b = round8(r), round8(g), round8(b)
            if (r, g, b) not in seen:
                seen.add((r, g, b))
                ordered_colors.append((r, g, b))
            if len(ordered_colors) == 16:
                break
        return ordered_colors

# Pad palette with its own median color if fewer than 16
def pad_palette(colors):
    if len(colors) >= 16:
        return colors[:16]

    packed = [r << 16 | g << 8 | b for r, g, b in colors]
    packed.sort()
    median_color = packed[len(packed) // 2]
    median_rgb = ((median_color >> 16) & 0xFF, (median_color >> 8) & 0xFF, median_color & 0xFF)

    while len(colors) < 16:
        colors.append(median_rgb)
    return colors

# Capitalize and format output filename
def generate_output_name(stem):
    name_part = re.sub(r'\d+$', '', stem)
    digits = re.search(r'\d+$', stem)
    digits_str = f"{int(digits.group()):02}" if digits else ""
    return f"Colour{name_part.capitalize()}{digits_str}.pal"

# Write a JASC-PAL file
def write_jasc_palette(path, colors):
    with open(path, 'w') as f:
        f.write("JASC-PAL\n0100\n16\n")
        for r, g, b in colors:
            f.write(f"{r} {g} {b}\n")

# Main function to process BMPs in current folder
def process_bmps(input_dir='.', output_dir='./Colour00'):
    os.makedirs(output_dir, exist_ok=True)
    for bmp_path in Path(input_dir).glob("*.bmp"):
        colors = extract_palette_from_bmp_palette(bmp_path)
        padded = pad_palette(colors)
        outname = generate_output_name(bmp_path.stem)
        outpath = Path(output_dir) / outname
        write_jasc_palette(outpath, padded)
        print(f"Created: {outpath}")

# Run
if __name__ == "__main__":
    process_bmps()

