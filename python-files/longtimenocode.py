# mbr_zero_image.py
# Overwrite the first 512 bytes of a raw disk image with zeros.
# WARNING: For image files only. This script refuses to operate on device paths.
import os
import sys

def is_regular_file(path):
    return os.path.isfile(path) and not os.path.islink(path)

def zero_mbr(image_path, confirm=False):
    if not is_regular_file(image_path):
        raise SystemExit(f"Refusing to operate on non-file path: {image_path}")
    if not confirm:
        print("Danger: this will overwrite the first 512 bytes of the image.")
        print("Rerun with the second argument 'YES' to confirm.")
        sys.exit(1)
    with open(image_path, 'r+b') as f:
        f.seek(0)
        f.write(b'\x00' * 512)
        f.flush()
        os.fsync(f.fileno())
    print("First 512 bytes overwritten with zeros.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mbr_zero_image.py <image-file> YES")
        sys.exit(1)
    img = sys.argv[1]
    confirm = (len(sys.argv) > 2 and sys.argv[2] == 'YES')
    zero_mbr(img, confirm)
