import os
from PIL import Image
import numpy as np

def find_file(suffix):
    for f in os.listdir('.'):
        if f.lower().endswith(('.png', '.tga', '.dds')):
            name = os.path.splitext(f)[0].lower()
            if name.endswith(suffix):
                return f
    return None

def main():
    print("=== EFT → STALKER Bump Converter ===")

    normal_path = find_file('_nrm')
    gloss_path = find_file('_glos')

    if not normal_path or not gloss_path:
        print("❌ Missing required files (_nrm and _glos).")
        input("Press Enter to exit...")
        return

    print(f"✅ Normal found: {normal_path}")
    print(f"✅ Gloss found: {gloss_path}")

    normal = Image.open(normal_path).convert('RGBA')
    gloss = Image.open(gloss_path).convert('RGBA')

    # Convert to numpy arrays
    normal_np = np.array(normal, dtype=np.float32) / 255.0
    gloss_np = np.array(gloss, dtype=np.float32) / 255.0

    # Convert gloss to grayscale
    gloss_gray = np.mean(gloss_np[..., :3], axis=2)

    # Compose bump map according to STALKER format
    bump = np.zeros_like(normal_np)
    bump[..., 0] = gloss_gray            # Red = Gloss
    bump[..., 1] = normal_np[..., 1]     # Green = Normal G
    bump[..., 2] = normal_np[..., 2]     # Blue = Normal B
    bump[..., 3] = normal_np[..., 0]     # Alpha = Normal R

    bump_img = Image.fromarray((bump * 255).astype(np.uint8), mode='RGBA')

    out_name = os.path.splitext(normal_path)[0] + "_bump.png"
    bump_img.save(out_name)
    print(f"✅ Done! Saved: {out_name}")

    input("Press Enter to close...")

if __name__ == "__main__":
    main()
