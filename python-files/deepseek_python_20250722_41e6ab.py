from PIL import Image
import math
import os
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo

def closest_power_of_2(n):
    """Find the closest power of 2 to the given number"""
    if n <= 0:
        return 1
    exp = math.floor(math.log2(n))
    lower = 2 ** exp
    upper = 2 ** (exp + 1)
    return lower if (n - lower) <= (upper - n) else upper

def process_image(input_path, output_path):
    """Process single image"""
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        
        target_size = closest_power_of_2(max(width, height))
        new_img = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
        new_img.paste(img, ((target_size - width) // 2, (target_size - height) // 2))
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        new_img.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def select_and_process_images():
    # Hide the root Tkinter window
    root = Tk()
    root.withdraw()
    
    # Open file dialog to select multiple images
    file_paths = filedialog.askopenfilenames(
        title="Select image files",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp")]
    )
    
    if not file_paths:
        print("No files selected")
        return
    
    # Ask for output directory
    output_dir = filedialog.askdirectory(title="Select output directory")
    if not output_dir:
        print("No output directory selected")
        return
    
    # Process each selected file
    success_count = 0
    for input_path in file_paths:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_square{ext}")
        
        if process_image(input_path, output_path):
            success_count += 1
            print(f"Processed: {input_path} -> {output_path}")
    
    # Show completion message
    showinfo("Processing Complete", 
             f"Successfully processed {success_count}/{len(file_paths)} files\n"
             f"Saved to: {output_dir}")

if __name__ == "__main__":
    select_and_process_images()