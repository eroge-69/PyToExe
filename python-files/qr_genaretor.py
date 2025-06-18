import qrcode
from PIL import Image
import json
import sys
import os

def load_config(path="config.json"):
    if not os.path.exists(path):
        raise FileNotFoundError("Config file not found.")
    with open(path, "r") as file:
        return json.load(file)

def generate_qr(data, output_file, config):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((config["width"], config["height"]), Image.ANTIALIAS)
    img.save(output_file)
    print(f"✅ QR code saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python generate_qr.py <data> <output_filename>")
        sys.exit(1)

    data = sys.argv[1]
    output_filename = sys.argv[2]

    config = load_config()
    generate_qr(data, output_filename, config)