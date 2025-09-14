import os
from tkinter import Tk
from tkinter import filedialog
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL

# --- CONFIG ---
template_path = "template.docx"  # Existing file with header C:\الثالث من صفر صفر صفر
output_path = "output.docx"
img_width = Inches(5)            # Adjust width
img_height = Inches(5)           # Optional: fix height
# ----------------

# --- Step 1: Open Tkinter file dialog ---
root = Tk()
root.withdraw()  # Hide the main Tk window

print("📂 Select the images to add (hold Ctrl to select multiple):")
image_paths = filedialog.askopenfilenames(
    title="Select Images",
    filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
)

if not image_paths:
    print("No images selected. Exiting...")
    exit()

image_paths = list(image_paths)  # Convert tuple to list
image_paths.sort()               # Optional: sort alphabetically

# --- Step 2: Load template ---
doc = Document(template_path)

# --- Step 3: Add 2 images per page, centered ---
for i in range(1, len(image_paths), 2):
    # Create a 1-row, 2-column table
    table = doc.add_table(rows=1, cols=2)
    table.autofit = True

    # First image
    cell1 = table.rows[0].cells[0]
    cell1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p1 = cell1.paragraphs[0]
    p1.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    if i < len(image_paths):
        run1 = p1.add_run()
        run1.add_picture(image_paths[i], width=img_width, height=img_height)

    # Second image
    cell2 = table.rows[0].cells[1]
    cell2.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p2 = cell2.paragraphs[0]
    p2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    if i + 1 < len(image_paths):
        run2 = p2.add_run()
        run2.add_picture(image_paths[i + 1], width=img_width, height=img_height)

    # Page break after each pair (except last)
    if i + 2 < len(image_paths):
        doc.add_page_break()

# --- Step 4: Save result ---
doc.save(output_path)
print(f"✅ Done! Saved to {output_path}")