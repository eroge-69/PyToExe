import pyheif
from PIL import Image
from tkinter import Tk, filedialog
import os


def convert_heic_to_jpeg(heic_path):
    try:
        heif_file = pyheif.read(heic_path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        output_path = os.path.splitext(heic_path)[0] + ".jpeg"
        image.save(output_path, "JPEG", quality=95)
        print(f"✔ Converted: {heic_path} → {output_path}")
    except Exception as e:
        print(f"❌ Failed to convert {heic_path}: {e}")


def main():
    root = Tk()
    root.withdraw()  # не показывать главное окно
    files = filedialog.askopenfilenames(filetypes=[("HEIC files", "*.heic")])

    if not files:
        print("No files selected.")
        return

    for file in files:
        convert_heic_to_jpeg(file)


if __name__ == "__main__":
    main()
