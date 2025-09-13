import sys
from PIL import Image

# ---------- ENCODER ----------
def image_to_upl(image_path, upl_path):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = list(img.getdata())

    lines = []
    i = 0
    while i < len(pixels):
        count = 1
        while i + count < len(pixels) and pixels[i] == pixels[i+count]:
            count += 1
        r, g, b = pixels[i]
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        if count > 1:
            lines.append(f"{hex_color}*{count}")
        else:
            lines.append(hex_color)
        i += count

    with open(upl_path, "w") as f:
        f.write(f"{width}x{height}\n")
        f.write(",".join(lines))

    print(f"[+] Saved UPL file: {upl_path}")

# ---------- DECODER ----------
def upl_to_image(upl_path, out_path):
    with open(upl_path, "r") as f:
        lines = f.read().splitlines()
    size = lines[0]
    width, height = map(int, size.split("x"))
    codes = lines[1].split(",")

    pixels = []
    for code in codes:
        if "*" in code:
            color, count = code.split("*")
            count = int(count)
        else:
            color, count = code, 1
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        pixels.extend([(r, g, b)] * count)

    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    img.save(out_path)
    print(f"[+] Reconstructed image saved: {out_path}")

# ---------- MAIN ----------
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  To convert image → UPL: upl_tool encode input.png output.upl")
        print("  To convert UPL → image: upl_tool decode input.upl output.png")
        sys.exit(1)

    mode, infile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]

    if mode == "encode":
        image_to_upl(infile, outfile)
    elif mode == "decode":
        upl_to_image(infile, outfile)
    else:
        print("Unknown mode! Use encode or decode.")

