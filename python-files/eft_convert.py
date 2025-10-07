import os
from PIL import Image
import numpy as np

def find_file(suffix):
    for f in os.listdir('.'):
        if f.lower().endswith('.png') and f.lower().endswith(suffix + '.png'):
            return f
    return None

def main():
    normal_path = find_file('_nrm')
    gloss_path = find_file('_glos')

    if not normal_path or not gloss_path:
        print("❌ Missing _nrm.png or _glos.png in folder.")
        return

    print("✅ Normal:", normal_path)
    print("✅ Gloss:", gloss_path)

    normal = Image.open(normal_path).convert('RGB')
    gloss = Image.open(gloss_path).convert('RGB')

    normal_np = np.array(normal, dtype=np.float32) / 255.0
    gloss_np = np.array(gloss, dtype=np.float32) / 255.0

    normal_blue = normal_np[..., 2]
    gloss_gray = np.mean(gloss_np, axis=2)

    # blend theo hướng dẫn modder
    height = normal_blue * 0.7 + (1.0 - gloss_gray) * 0.3
    height = np.clip(height * 255, 0, 255).astype(np.uint8)

    Image.fromarray(height, mode='L').save('height_result.png')
    print("✅ Created height_result.png")

if __name__ == "__main__":
    main()
