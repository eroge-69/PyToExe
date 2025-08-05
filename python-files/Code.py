import sys
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm

# ==============================================
# CONFIGURATION SETTINGS - EDIT THESE AS NEEDED
# ==============================================

# File and folder settings
EXCEL_FILE = "products.xlsx"  # Path to your Excel file
BARCODE_COLUMN = "barcode_column"  # Column name for barcode data
DESCRIPTION_COLUMN = "Description"  # Column name for product description
X_COLUMN = "X"  # Column name for X data
Y_COLUMN = "Y"  # Column name for Y data (status)
IMAGE_NAME_COLUMN = "ID"  # Column name for image filename
OUTPUT_FOLDER = "barcode_images"  # Folder to save generated images
PDF_FILE = "barcodes.pdf"  # Output PDF filename

# Output format settings
OUTPUT_FORMAT = "PNG"  # Choose "PNG" or "JPG"
JPG_QUALITY = 100  # Quality for JPG output (1-100, 95 is high quality)

# Paper settings (A4 in landscape - 297mm × 210mm)
PAPER_ORIENTATION = "landscape"  # "portrait" or "landscape"
PAPER_WIDTH_MM = 297  # A4 landscape width in mm
PAPER_HEIGHT_MM = 210  # A4 landscape height in mm
MARGIN_MM = 30  # Margin on all sides in mm
LABELS_PER_ROW = 1  # Number of labels per row
ROWS_PER_PAGE = 1  # Number of rows per page

# Barcode settings
BARCODE_TYPE = "code128"  # Barcode type (code128, ean13, etc.)
BARCODE_HEIGHT_MM = 10  # Barcode height in mm
DPI = 600  # Print resolution (300 for good quality)
SCALE_FACTOR = 1  # General scaling factor

# Font settings
FONT_NAME = "arialbd"  # Try "arialbd" for bold
FONT_SIZE_PRODUCT = 100  # Base size for product name
FONT_SIZE_CODE = 20  # Base size for barcode text
FONT_SIZE_STATUS = 20  # Base size for status text

# Text positioning (relative to barcode bottom)
TEXT_MARGIN_TOP_MM = -3  # Space between barcode and first text
TEXT_LINE_SPACING_MM = 0  # Space between text lines
LEFT_MARGIN_MM = 5  # Left margin for all text elements
RIGHT_MARGIN_MM = 5  # Right margin for all text elements

# PDF Settings
PDF_PAGE_SIZE = A4  # You can change this to other sizes like LETTER
PDF_ORIENTATION = "landscape"  # "portrait" or "landscape"
PDF_MARGIN_MM = 15  # Margin around each image in the PDF
IMAGE_SCALING = 0.95  # Scale factor for images in PDF (0-1)

# ==============================================
# MAIN SCRIPT
# ==============================================

# Calculate conversions
MM_TO_PIXELS = DPI / 25.4
LABEL_WIDTH_MM = (PAPER_WIDTH_MM - (2 * MARGIN_MM)) / LABELS_PER_ROW
LABEL_HEIGHT_MM = (PAPER_HEIGHT_MM - (2 * MARGIN_MM)) / ROWS_PER_PAGE

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Excel file
df = pd.read_excel(EXCEL_FILE)


# Function to get font with fallback
def get_font(font_name, font_size):
    try:
        return ImageFont.truetype(f"{font_name}.ttf", int(font_size * SCALE_FACTOR))
    except:
        return ImageFont.load_default(size=int(font_size * SCALE_FACTOR))


# Custom writer class for high resolution
class HighResWriter(ImageWriter):
    def __init__(self):
        super().__init__()
        self.dpi = DPI
        self.module_height = (BARCODE_HEIGHT_MM * MM_TO_PIXELS) / self.module_width


# Validate output format
OUTPUT_FORMAT = OUTPUT_FORMAT.upper()
if OUTPUT_FORMAT not in ["PNG", "JPG", "JPEG"]:
    OUTPUT_FORMAT = "PNG"

# Initialize list to store generated image paths
generated_images = []

# Generate individual barcode images
for index, row in df.iterrows():
    barcode_data = str(row[BARCODE_COLUMN])
    description = str(row[DESCRIPTION_COLUMN])
    x_code = str(row[X_COLUMN])
    y_code = str(row[Y_COLUMN])
    image_name = str(row[IMAGE_NAME_COLUMN])  # Get the custom image name

    # Generate barcode
    code = barcode.get_barcode_class(BARCODE_TYPE)
    barcode_img = code(barcode_data, writer=HighResWriter())
    temp_filename = f"{OUTPUT_FOLDER}/temp_{barcode_data}"
    barcode_img.save(temp_filename)

    # Open barcode image
    img = Image.open(f"{temp_filename}.png")
    width, barcode_height = img.size

    # Calculate text positions
    left_margin = int(LEFT_MARGIN_MM * MM_TO_PIXELS)
    right_margin = int(RIGHT_MARGIN_MM * MM_TO_PIXELS)
    available_width = width - left_margin - right_margin
    text_margin_top = int(TEXT_MARGIN_TOP_MM * MM_TO_PIXELS)
    text_line_spacing = int(TEXT_LINE_SPACING_MM * MM_TO_PIXELS)

    # Initialize fonts with dynamic sizing
    font_product = get_font(FONT_NAME, FONT_SIZE_PRODUCT)
    font_code = get_font(FONT_NAME, FONT_SIZE_CODE)
    font_status = get_font(FONT_NAME, FONT_SIZE_STATUS)


    # Function to wrap text and adjust font size if needed
    def prepare_text(text, font, max_width, original_size):
        current_font = font
        while True:
            lines = []
            current_line = []

            for word in text.split():
                test_line = ' '.join(current_line + [word])
                test_width = current_font.getlength(test_line)

                if test_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:  # Only add if not empty
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            # Check if all lines fit
            if len(lines) == 1 or current_font.size <= 10:  # Minimum font size
                return lines, current_font

            # Reduce font size and try again
            new_size = current_font.size - 2
            current_font = get_font(FONT_NAME, new_size)


    # Prepare all text elements
    product_lines, font_product = prepare_text(description, font_product, available_width, FONT_SIZE_PRODUCT)
    code_lines, font_code = prepare_text(barcode_data, font_code, available_width, FONT_SIZE_CODE)
    status_lines, font_status = prepare_text(y_code, font_status, available_width, FONT_SIZE_STATUS)

    # Calculate required text space
    text_space = (text_margin_top +
                  len(product_lines) * (font_product.size + text_line_spacing) +
                  len(code_lines) * (font_code.size + text_line_spacing) +
                  len(status_lines) * (font_status.size + text_line_spacing))

    # Create new image with space for text
    new_height = barcode_height + text_space
    new_img = Image.new("RGB", (width, new_height), "white")
    new_img.paste(img, (0, 0))
    new_img.info['dpi'] = (DPI, DPI)

    # Draw text with consistent left alignment
    draw = ImageDraw.Draw(new_img)
    text_y = barcode_height + text_margin_top

    # Draw product description
    for line in product_lines:
        draw.text((left_margin, text_y), line, font=font_product, fill="black")
        text_y += font_product.size + text_line_spacing

    # Draw barcode data
    for line in code_lines:
        draw.text((left_margin, text_y), line, font=font_code, fill="black")
        text_y += font_code.size + text_line_spacing

    # Draw status
    for line in status_lines:
        draw.text((left_margin, text_y), line, font=font_status, fill="black")
        text_y += font_status.size + text_line_spacing

    # Save final image using the custom image name
    final_filename = f"{OUTPUT_FOLDER}/{image_name}.{OUTPUT_FORMAT.lower()}"
    generated_images.append(final_filename)

    if OUTPUT_FORMAT == "PNG":
        new_img.save(final_filename, dpi=(DPI, DPI), quality=100)
    else:  # JPG
        if new_img.mode in ('RGBA', 'LA'):
            new_img = new_img.convert('RGB')
        new_img.save(final_filename,
                     dpi=(DPI, DPI),
                     quality=JPG_QUALITY,
                     subsampling=0)

    os.remove(f"{temp_filename}.png")
    print(f"Generated: {final_filename}")

print(f"All barcodes generated in {OUTPUT_FORMAT} format with all data included!")

# ==============================================
# PDF GENERATION
# ==============================================

print("\nCreating PDF document...")

# Set up PDF page size and orientation
if PDF_ORIENTATION == "landscape":
    page_size = landscape(PDF_PAGE_SIZE)
else:
    page_size = portrait(PDF_PAGE_SIZE)

# Create PDF canvas
c = canvas.Canvas(PDF_FILE, pagesize=page_size)
page_width, page_height = page_size

# Calculate available space for images with margins
margin = PDF_MARGIN_MM * mm
available_width = page_width - (2 * margin)
available_height = page_height - (2 * margin)

# Process each generated image
for image_path in generated_images:
    try:
        # Open the image to get its dimensions
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Calculate scaling factor to fit within available space
        width_scale = (available_width * IMAGE_SCALING) / img_width
        height_scale = (available_height * IMAGE_SCALING) / img_height
        scale = min(width_scale, height_scale)

        # Calculate scaled dimensions
        scaled_width = img_width * scale
        scaled_height = img_height * scale

        # Calculate position to center the image
        x_pos = (page_width - scaled_width) / 2
        y_pos = (page_height - scaled_height) / 2

        # Draw the image on the PDF
        c.drawImage(ImageReader(image_path),
                    x_pos, y_pos,
                    width=scaled_width,
                    height=scaled_height,
                    preserveAspectRatio=True)

        # Add a new page for the next image
        c.showPage()
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

# Save the PDF
c.save()
print(f"PDF created successfully: {PDF_FILE}")
# Keep the window open after execution
if __name__ == '__main__':
    if sys.platform.startswith('win'):
        import msvcrt
        print("\nPress any key to exit...")
        msvcrt.getch()
    else:
        input("\nPress Enter to exit...")