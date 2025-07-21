from PIL import Image
import os

def combine_png_channels(image1_path, image2_path, output_path):
    """
    Combines two PNG images such that:
    - The Red (R) channel of the output gets data from the first image.
    - The Alpha (A) channel of the output gets data from the second image.
    The output image will have the same dimensions as the input images.

    Args:
        image1_path (str): Path to the first PNG image (for Red channel).
        image2_path (str): Path to the second PNG image (for Alpha channel).
        output_path (str): Path to save the combined PNG image.
    """
    try:
        img1 = Image.open(image1_path).convert("L")  # Convert to grayscale for single channel
        img2 = Image.open(image2_path).convert("L")  # Convert to grayscale for single channel
    except FileNotFoundError:
        print(f"Error: One or both input files not found. Check paths:\n{image1_path}\n{image2_path}")
        return
    except Exception as e:
        print(f"Error opening images: {e}")
        return

    if img1.size != img2.size:
        print("Error: Input images must have the same dimensions.")
        return

    width, height = img1.size

    # Create a new RGBA image (Red, Green, Blue, Alpha)
    output_img = Image.new("RGBA", (width, height))

    # Get pixel data as lists
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    output_pixels = []
    for i in range(width * height):
        # The first image (img1) provides the Red channel
        red_value = pixels1[i]
        # The second image (img2) provides the Alpha channel
        alpha_value = pixels2[i]
        
        # Keep Green and Blue channels as 0 (or any desired value, e.g., 255 for white base)
        # We'll make them 0 for a cleaner "red-alpha" effect
        output_pixels.append((red_value, 0, 0, alpha_value))

    output_img.putdata(output_pixels)
    
    try:
        output_img.save(output_path)
        print(f"Successfully combined images and saved to: {output_path}")
    except Exception as e:
        print(f"Error saving output image: {e}")

# --- How to use the script ---
if __name__ == "__main__":
    # Replace with your actual image paths
    input_image1 = "image1.png"  # Path to your first PNG (for Red)
    input_image2 = "image2.png"  # Path to your second PNG (for Alpha)
    output_combined_image = "combined_output.png"

    # Create dummy images for testing if they don't exist
    if not os.path.exists(input_image1):
        print(f"Creating dummy {input_image1}...")
        dummy_img1 = Image.new('L', (100, 100), color=128) # Grey image
        dummy_img1.save(input_image1)

    if not os.path.exists(input_image2):
        print(f"Creating dummy {input_image2}...")
        dummy_img2 = Image.new('L', (100, 100), color=200) # Lighter grey image
        dummy_img2.save(input_image2)

    combine_png_channels(input_image1, input_image2, output_combined_image)