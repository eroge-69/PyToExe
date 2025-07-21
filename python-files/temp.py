from PIL import Image
import numpy as np
import os

def combine_maps(metallic_path, smoothness_path, output_path):
    # Load images in grayscale
    metallic_img = Image.open(metallic_path).convert("L")
    smoothness_img = Image.open(smoothness_path).convert("L")

    # Resize metallic to match smoothness if needed
    if metallic_img.size != smoothness_img.size:
        metallic_img = metallic_img.resize(smoothness_img.size, Image.BICUBIC)

    # Convert to numpy arrays
    r = np.array(metallic_img)
    a = np.array(smoothness_img)
    g = np.zeros_like(r)
    b = np.zeros_like(r)

    # Combine channels
    rgba = np.stack([r, g, b, a], axis=-1).astype(np.uint8)
    combined_img = Image.fromarray(rgba, mode="RGBA")

    combined_img.save(output_path)
    print(f"✅ Combined image saved as: {output_path}")

if __name__ == "__main__":
    print("Enter path to metallic image:")
    metallic_path = input(">> ").strip('"')
    print("Enter path to smoothness image:")
    smoothness_path = input(">> ").strip('"')

    output_path = "Combined_Metallic_Smoothness.png"
    combine_maps(metallic_path, smoothness_path, output_path)
