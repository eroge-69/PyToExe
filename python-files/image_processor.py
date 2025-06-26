import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import os
from pathlib import Path

class ImageProcessor:
    def __init__(self):
        self.target_size = (720, 720)
    
    def remove_background(self, image_path):
        """Remove background from image using rembg"""
        try:
            with open(image_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Remove background
            output_data = remove(input_data)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(output_data))
            return image
        except Exception as e:
            print(f"Error removing background: {e}")
            # Fallback to original image
            return Image.open(image_path)
    
    def enhance_old_image(self, image):
        """Enhance old/low quality images"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply noise reduction
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Enhance color saturation
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)
            
            # Enhance brightness slightly
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.02)
            
            return image
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return image
    
    def resize_with_padding(self, image, target_size):
        """Resize image to target size while maintaining aspect ratio with padding"""
        # Calculate the ratio and new dimensions
        ratio = min(target_size[0] / image.width, target_size[1] / image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        
        # Resize the image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new image with target size and transparent background
        if image.mode == 'RGBA':
            new_image = Image.new('RGBA', target_size, (0, 0, 0, 0))
        else:
            new_image = Image.new('RGB', target_size, (255, 255, 255))
        
        # Calculate position to center the resized image
        x = (target_size[0] - new_width) // 2
        y = (target_size[1] - new_height) // 2
        
        # Paste the resized image onto the new image
        new_image.paste(resized_image, (x, y))
        
        return new_image
    
    def process_image(self, input_path, output_path=None, remove_bg=True, enhance=True):
        """Main function to process the image"""
        try:
            input_path = Path(input_path)
            
            # Generate output path if not provided
            if output_path is None:
                output_path = input_path.parent / f"{input_path.stem}_processed.png"
            else:
                output_path = Path(output_path)
            
            print(f"Processing: {input_path}")
            
            # Step 1: Remove background (optional)
            if remove_bg:
                print("Removing background...")
                image = self.remove_background(input_path)
            else:
                image = Image.open(input_path)
            
            # Step 2: Enhance image quality (optional)
            if enhance:
                print("Enhancing image quality...")
                image = self.enhance_old_image(image)
            
            # Step 3: Resize to 720x720 with padding
            print("Resizing to 720x720...")
            image = self.resize_with_padding(image, self.target_size)
            
            # Step 4: Convert to PNG and save
            print("Saving as PNG...")
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            image.save(output_path, 'PNG', optimize=True)
            print(f"Processed image saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def batch_process(self, input_folder, output_folder=None):
        """Process multiple images in a folder"""
        input_folder = Path(input_folder)
        
        if output_folder is None:
            output_folder = input_folder / "processed"
        else:
            output_folder = Path(output_folder)
        
        # Create output folder if it doesn't exist
        output_folder.mkdir(exist_ok=True)
        
        # Supported image formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        processed_count = 0
        for image_file in input_folder.iterdir():
            if image_file.suffix.lower() in supported_formats:
                output_path = output_folder / f"{image_file.stem}_processed.png"
                result = self.process_image(image_file, output_path)
                if result:
                    processed_count += 1
        
        print(f"\nBatch processing complete! Processed {processed_count} images.")

# Advanced enhancement using OpenCV (alternative method)
def advanced_enhance_opencv(image_path):
    """Alternative enhancement method using OpenCV for more advanced processing"""
    # Read image
    img = cv2.imread(image_path)
    
    # Noise reduction using Non-local Means Denoising
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    # Sharpening using unsharp mask
    gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
    img = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)
    
    # Histogram equalization for better contrast
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    
    # Convert back to PIL Image
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

# Usage examples
if __name__ == "__main__":
    import io  # Add this import for the remove_background method
    
    # Initialize the processor
    processor = ImageProcessor()
    
    # Example 1: Process a single image with all features
    # processor.process_image("input_image.jpg", "output_image.png")
    
    # Example 2: Process without background removal
    # processor.process_image("input_image.jpg", "output_image.png", remove_bg=False)
    
    # Example 3: Process without enhancement
    # processor.process_image("input_image.jpg", "output_image.png", enhance=False)
    
    # Example 4: Batch process all images in a folder
    # processor.batch_process("input_folder", "output_folder")
    
    # Example 5: Interactive mode
    while True:
        print("\n=== Image Processor ===")
        print("1. Process single image")
        print("2. Batch process folder")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            input_path = input("Enter input image path: ").strip()
            if os.path.exists(input_path):
                remove_bg = input("Remove background? (y/n): ").strip().lower() == 'y'
                enhance = input("Enhance image quality? (y/n): ").strip().lower() == 'y'
                
                result = processor.process_image(input_path, remove_bg=remove_bg, enhance=enhance)
                if result:
                    print(f"Success! Output saved to: {result}")
                else:
                    print("Failed to process image.")
            else:
                print("File not found!")
        
        elif choice == '2':
            input_folder = input("Enter input folder path: ").strip()
            if os.path.exists(input_folder):
                output_folder = input("Enter output folder path (or press Enter for default): ").strip()
                if not output_folder:
                    output_folder = None
                processor.batch_process(input_folder, output_folder)
            else:
                print("Folder not found!")
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
