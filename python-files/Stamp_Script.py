import fitz  # PyMuPDF
import os
import datetime
from PIL import Image
from collections import Counter
import numpy as np

# === Paths ===
pdf_folder = r"C:\Users\Arun.Siwakoti\Downloads\Test"
output_folder = r"\\ACS-DC01\General\Stamped"
original_stamp_path = r"\\ACS-DC01\General\Stamp\Stamp.png"
processed_stamp_path = r"\\ACS-DC01\General\Stamp\stamp_transparent_70.png"

# === Ensure output folder exists ===
os.makedirs(output_folder, exist_ok=True)

# === Today's date ===
today_str = datetime.datetime.now().strftime("%d/%m/%Y")

# === Remove white and set opacity to 70% ===
def remove_white_and_set_opacity(input_path, output_path, tolerance=200, opacity=0.7):
    img = Image.open(input_path).convert("RGBA")
    new_data = []
    for pixel in img.getdata():
        r, g, b, a = pixel
        if r > tolerance and g > tolerance and b > tolerance:
            new_data.append((r, g, b, 0))  # Make white transparent
        else:
            new_data.append((r, g, b, int(255 * opacity)))  # 70% opacity
    img.putdata(new_data)
    img.save(output_path)

# === Preprocess the stamp image ===
remove_white_and_set_opacity(original_stamp_path, processed_stamp_path)

# === Color detection ===
def get_dominant_color(page, rect):
    pix = page.get_pixmap(clip=rect, dpi=72, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    data = np.array(img).reshape((-1, 3))
    most_common = Counter(map(tuple, data)).most_common(1)[0][0]
    return most_common

def get_contrasting_color(rgb):
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    if r > 150 and g < 100 and b < 100:
        return (0, 0, 1)  # Blue
    return (0, 0, 0) if luminance > 180 else (1, 1, 1)

# === Find empty space near top ===
def find_empty_space_top(page, box_width=200, box_height=80, margin=20, rows=6, cols=3):
    pw, ph = page.rect.width, page.rect.height
    top_limit = ph * 0.4
    step_y = (top_limit - margin * 2) / rows
    step_x = (pw - margin * 2) / cols

    for r in range(rows):
        for c in range(cols):
            x0 = margin + c * step_x
            y0 = margin + r * step_y
            rect = fitz.Rect(x0, y0, x0 + box_width, y0 + box_height)
            if not page.get_textbox(rect).strip():
                return rect
    return None

# === Main PDF stamping loop ===
for filename in os.listdir(pdf_folder):
    if not filename.lower().endswith(".pdf"):
        continue

    input_path = os.path.join(pdf_folder, filename)
    output_path = os.path.join(output_folder, filename)

    print(f"\n📄 Stamping: {filename}")
    doc = fitz.open(input_path)

    for page_number in range(len(doc)):
        page = doc[page_number]
        print(f"🔄 Processing page {page_number + 1}")
        pw, ph = page.rect.width, page.rect.height

        # === RECEIVED box ===
        received_rect = find_empty_space_top(page)
        if received_rect:
            bg_color = get_dominant_color(page, received_rect)
            text_color = get_contrasting_color(bg_color)

            # Outline
            page.draw_rect(received_rect, color=text_color, width=1.5, stroke_opacity=1.0)

            # Watermark text — transparent
            page.insert_textbox(
                received_rect,
                "RECEIVED",
                fontname="helv",
                fontsize=50,
                color=text_color,
                fill_opacity=0.7,  # 70% visible
                render_mode=0,
                align=1,
                overlay=True
            )

            # Bold RECEIVED label
            page.insert_textbox(
                fitz.Rect(received_rect.x0, received_rect.y0, received_rect.x1, received_rect.y0 + 45),
                "RECEIVED",
                fontname="helv",
                fontsize=24,
                color=text_color,
                fill_opacity=1.0,
                align=1,
                overlay=True,
            )

            # Date text
            page.insert_textbox(
                fitz.Rect(received_rect.x0, received_rect.y0 + 45, received_rect.x1, received_rect.y1),
                today_str,
                fontname="helv",
                fontsize=12,
                color=text_color,
                fill_opacity=1.0,
                align=1,
                overlay=True,
            )
        else:
            print(f"⚠️ No white space found for RECEIVED on page {page_number + 1}")

        # === Insert Stamp image at center ===
        stamp_width, stamp_height = 720, 300
        stamp_rect = fitz.Rect(
            (pw - stamp_width) / 2,
            (ph - stamp_height) / 2,
            (pw + stamp_width) / 2,
            (ph + stamp_height) / 2
        )

        stamp_bg = get_dominant_color(page, stamp_rect)
        if stamp_bg[0] > 150 and stamp_bg[1] < 100 and stamp_bg[2] < 100:
            print(f"🚫 Skipped red-dominant stamp area on page {page_number + 1}")
            continue

        try:
            page.insert_image(
                stamp_rect,
                filename=processed_stamp_path,
                overlay=True,
                keep_proportion=True
            )
            print(f"🖼️ Stamp inserted at 70% opacity on page {page_number + 1}")
        except Exception as e:
            print(f"❌ Failed to insert stamp: {e}")

    # === Save result ===
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError:
            print(f"⚠️ Output file open: {output_path}. Skipping.")
            doc.close()
            continue

    doc.save(output_path)
    doc.close()
    print(f"✅ Saved: {output_path}")

print("\n🎉 All PDFs processed.")
