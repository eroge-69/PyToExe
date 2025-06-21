#!/usr/bin/python
import os
from PIL import Image

SUPPORTED_EXTENSIONS = ('.png', '.bmp')

def load_image_colors(image_path):
    image = Image.open(image_path).convert("RGB")
    return list(image.getdata()), image.size

def round_color(c):
    return tuple(min(round(v / 8) * 8, 248) for v in c)

def build_color_mapping(colors1, colors2):
    if len(colors1) != len(colors2):
        raise ValueError("Images have different number of pixels.")

    color_map = {}
    for i, (c1, c2) in enumerate(zip(colors1, colors2)):
        c1_rounded = round_color(c1)
        c2_rounded = round_color(c2)

        if c1_rounded == c2_rounded:
            continue

        if c1_rounded in color_map and color_map[c1_rounded] != c2_rounded:
            raise ValueError(f"Inconsistent mapping for {c1_rounded} at pixel {i}: {color_map[c1_rounded]} vs {c2_rounded}")

        color_map[c1_rounded] = c2_rounded
    return color_map

def parse_jasc_pal(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    if len(lines) < 4 or lines[0].strip() != "JASC-PAL" or lines[1].strip() != "0100":
        raise ValueError(f"{file_path} is not a valid JASC-PAL file.")

    try:
        count = int(lines[2].strip())  # count on line 3 (index 2)
        colors = []
        for line in lines[3:3 + count]:
            stripped = line.strip()
            parts = stripped.split()
            if len(parts) != 3:
                raise ValueError(f"Palette line does not have exactly 3 components: '{stripped}'")
            colors.append(tuple(map(int, parts)))
    except Exception as e:
        raise ValueError(f"Failed to parse color entries in {file_path}: {e}")

    return lines[:3], colors

def save_jasc_pal(file_path, header, colors):
    with open(file_path, 'w') as f:
        f.writelines(header)
        for color in colors:
            f.write(f"{color[0]} {color[1]} {color[2]}\n")

def update_palettes(color_map, output_dir, palette_files):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for pal_path in palette_files:
        filename = os.path.basename(pal_path)
        print(f"  Processing palette: {filename}")
        try:
            header, colors = parse_jasc_pal(pal_path)

            updated_colors = []
            for c in colors:
                mapped = color_map.get(c, c)
                mapped_rounded = round_color(mapped)

                # Replace non-original-black that became black with (8,8,8)
                if c != (0, 0, 0) and mapped_rounded == (0, 0, 0):
                    mapped_rounded = (8, 8, 8)

                updated_colors.append(mapped_rounded)

            out_path = os.path.join(output_dir, filename)
            save_jasc_pal(out_path, header, updated_colors)
            print(f"    → Saved: {out_path}")
        except Exception as e:
            print(f"    ✖ Error: {e}")

def process_pair(base_path, variant_path, palette_files):
    print(f"\n🔁 Comparing base '{base_path}' to variant '{variant_path}'")

    colors1, size1 = load_image_colors(base_path)
    colors2, size2 = load_image_colors(variant_path)

    if size1 != size2:
        print(f"✖ Skipping '{variant_path}' — image size doesn't match.")
        return

    try:
        color_map = build_color_mapping(colors1, colors2)
    except ValueError as e:
        print(f"✖ Skipping '{variant_path}' — {e}")
        return

    if not color_map:
        print(f"⚠ Skipping '{variant_path}' — no color differences found.")
        return

    output_dir = os.path.splitext(os.path.basename(variant_path))[0]
    print(f"  ✅ Mapping {len(color_map)} color(s) → output: {output_dir}")
    update_palettes(color_map, output_dir, palette_files)

def main(args):
    if len(args) == 1:
        base_image = args[0]
        base_filename = os.path.basename(base_image)

        if not os.path.isfile(base_image):
            print(f"Error: file '{base_image}' not found.")
            return

        all_images = [
            f for f in os.listdir(".")
            if f.lower().endswith(SUPPORTED_EXTENSIONS) and f != base_filename
        ]

        if not all_images:
            print("No matching variant images found in this directory.")
            return

        # All palette files in current directory
        all_palettes = [os.path.join(".", f) for f in os.listdir(".") if f.lower().endswith(".pal")]

        for variant in all_images:
            process_pair(base_image, variant, all_palettes)

    elif len(args) == 3:
        base_image, compare_image, palette_file = args
        if not os.path.isfile(base_image):
            print(f"Error: file '{base_image}' not found.")
            return
        if not os.path.isfile(compare_image):
            print(f"Error: file '{compare_image}' not found.")
            return
        if not os.path.isfile(palette_file):
            print(f"Error: file '{palette_file}' not found.")
            return

        process_pair(base_image, compare_image, [palette_file])

    else:
        print("Usage:")
        print("  python color_mapper.py <base_image.png|bmp>")
        print("  OR")
        print("  python color_mapper.py <base_image.png|bmp> <compare_image.png|bmp> <palette.pal>")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

