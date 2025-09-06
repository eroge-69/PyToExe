import rasterio
import numpy as np
from PIL import Image
from matplotlib import cm

def main():
    print("=== GeoTIFF to PNG Converter ===")
    
    # Prompt for input and output
    input_tif = input("Enter the path to the GeoTIFF file: ").strip()
    output_png = input("Enter the desired output PNG file path: ").strip()
    
    # Ask if user wants colored terrain
    use_color = input("Do you want a colored terrain map? (y/n): ").strip().lower() == "y"
    
    try:
        with rasterio.open(input_tif) as src:
            band = src.read(1)
            band = np.where(band == src.nodata, np.nan, band)
            
        # Normalize data
        min_val = np.nanmin(band)
        max_val = np.nanmax(band)
        normalized = ((band - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        normalized = np.nan_to_num(normalized, nan=0)
        
        if use_color:
            colored = cm.terrain(normalized / 255.0)  # RGBA float
            colored_img = (colored[:, :, :3] * 255).astype(np.uint8)  # Drop alpha
            img = Image.fromarray(colored_img)
        else:
            img = Image.fromarray(normalized)
        
        img.save(output_png)
        print(f"Successfully converted '{input_tif}' to '{output_png}'!")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
