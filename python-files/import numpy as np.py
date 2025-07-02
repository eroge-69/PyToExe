import numpy as np
from PIL import Image
import os
import argparse

def find_unique_pixels(images):
    """
    Finds pixels unique to each image compared to the rest at the same location.
    
    Args:
        images: List of numpy arrays (all same shape [H, W, C]).
        
    Returns:
        List of 2D boolean masks (one per image), where True indicates a unique pixel.
        
    Raises:
        ValueError: If images have different shapes or the list is empty.
    """
    if not images:
        return []
    
    base_shape = images[0].shape
    for i, img in enumerate(images):
        if img.shape != base_shape:
            raise ValueError(f"Image {i} has shape {img.shape}, expected {base_shape}.")
    
    n = len(images)
    H, W, C = base_shape
    
    if n == 1:
        return [np.ones((H, W), dtype=bool)]
    
    masks = []
    for i in range(n):
        other_imgs = [images[j] for j in range(n) if j != i]
        other_stack = np.stack(other_imgs, axis=0)
        
        current = images[i][np.newaxis, ...]
        matches = (other_stack == current)
        full_matches = np.all(matches, axis=-1)
        any_match = np.any(full_matches, axis=0)
        
        masks.append(~any_match)
    
    return masks

def load_images(image_paths):
    """Load images from paths and convert to numpy arrays in RGB format"""
    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(np.array(img))
    return images

def create_highlighted_image(original, mask):
    """Create RGBA image with unique pixels highlighted and others transparent"""
    rgba = np.zeros((original.shape[0], original.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = original
    rgba[:, :, 3] = np.where(mask, 255, 0)  # Alpha channel: 255 for unique, 0 for others
    return Image.fromarray(rgba)

def main():
    parser = argparse.ArgumentParser(
        description='Find pixels unique to each screenshot compared to others.',
        epilog='Example: python unique_pixels.py screenshot1.png screenshot2.png screenshot3.png'
    )
    parser.add_argument('image_files', nargs='+', help='Paths to screenshot files')
    args = parser.parse_args()

    try:
        # Load and validate images
        images = load_images(args.image_files)
        print(f"Loaded {len(images)} images with dimensions {images[0].shape[1]}x{images[0].shape[0]}")
        
        # Find unique pixels
        masks = find_unique_pixels(images)
        print("Unique pixel identification complete")
        
        # Generate output images
        os.makedirs('unique_pixel_outputs', exist_ok=True)
        print("Saving results to 'unique_pixel_outputs' directory:")
        
        for i, (img_path, mask) in enumerate(zip(args.image_files, masks)):
            original_img = Image.open(img_path).convert('RGBA')
            unique_count = np.sum(mask)
            
            # Create highlighted version
            base_name = os.path.basename(img_path)
            output_name = f"unique_{base_name}"
            output_path = os.path.join('unique_pixel_outputs', output_name)
            
            highlighted = create_highlighted_image(images[i], mask)
            highlighted.save(output_path, 'PNG')
            
            print(f"  {base_name}: {unique_count} unique pixels -> saved as {output_name}")

    except Exception as e:
        print(f"Error: {e}")
        print("Ensure all images have the same dimensions and are valid image files")

if __name__ == "__main__":
    main()