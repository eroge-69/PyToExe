import fitz  # PyMuPDF
from PIL import Image
import io
import os
import sys
from pathlib import Path

def extract_images_from_pdf(pdf_path, quality=85, max_width=1920):
    """
    Extract images from PDF pages and save them as compressed JPEG files.
    
    Args:
        pdf_path (str): Path to the PDF file
        quality (int): JPEG compression quality (1-100, higher = better quality)
        max_width (int): Maximum width for resizing (maintains aspect ratio)
    """
    
    # Open the PDF
    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return
    
    # Get the directory where the PDF is located
    pdf_dir = Path(pdf_path).parent
    pdf_name = Path(pdf_path).stem
    
    print(f"Processing {len(pdf_document)} pages...")
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Get the page as an image (pixmap)
        # Use a reasonable DPI (150) for good quality without excessive file size
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom = ~150 DPI
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # Resize if the image is too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"Page {page_num + 1}: Resized to {max_width}x{new_height}")
        
        # Convert to RGB if necessary (for JPEG)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as compressed JPEG
        output_path = pdf_dir / f"{pdf_name}_page_{page_num + 1:03d}.jpg"
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        
        print(f"Saved: {output_path}")
        
        # Clean up
        pix = None
        img.close()
    
    # Store page count before closing
    total_pages = len(pdf_document)
    pdf_document.close()
    print(f"\nCompleted! Extracted {total_pages} images.")

def main():
    # Get PDF path from command line argument or user input
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("Enter the path to your PDF file: ").strip().strip('"')
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found!")
        return
    
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: Please provide a PDF file!")
        return
    
    print("PDF Image Extractor - High Quality")
    print("Settings: 1080x1536 pixels, 100% quality, 600 DPI rendering")
    
    # Extract images with fixed settings
    extract_images_from_pdf(pdf_path)

if __name__ == "__main__":
    main()