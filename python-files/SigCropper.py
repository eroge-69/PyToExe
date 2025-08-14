import cv2
import numpy as np
import os
import glob

def crop_whitespace(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    _, binary = cv2.threshold(norm, 250, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(binary)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        return image[y:y+h, x:x+w]
    else:
        return image

def enhance_and_binarize(image):
    # Expecting BGRA input
    gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)

    # Stronger local contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Normalize to stretch blacks and whites
    norm = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)

    # Lower threshold ? stronger blacks
    _, binary = cv2.threshold(norm, 130, 255, cv2.THRESH_BINARY)

    # Remove small white specks inside black regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return cleaned

def make_transparent(image_bgra, binary):
    # Force RGB to pure black where binary is black
    mask_black = (binary == 0)
    image_bgra[mask_black] = (0, 0, 0, 255)

    # Alpha mask: background transparent
    alpha = cv2.bitwise_not(binary)
    image_bgra[:, :, 3] = alpha
    return image_bgra


def crop_and_pad_to_ratio(image, target_ratio=(4, 1), crop_px=28):
    # Convert to BGRA right away so padding can be transparent
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    h, w = image.shape[:2]
    cropped = image[crop_px:h-crop_px, crop_px:w-crop_px]

    h_new, w_new = cropped.shape[:2]
    target_width = int(h_new * target_ratio[0] / target_ratio[1])

    if target_width <= w_new:
        print(f"Skipping: already wider than {target_ratio[0]}:{target_ratio[1]}")
        return None

    total_padding = target_width - w_new
    pad_left = total_padding // 2
    pad_right = total_padding - pad_left

    padded = cv2.copyMakeBorder(
        cropped,
        0, 0,
        pad_left, pad_right,
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255, 0)  # Transparent padding
    )
    return padded

# ---------------- MAIN PROCESS ----------------
os.remove("annotated_cells.jpg") if os.path.exists("annotated_cells.jpg") else None
jpg_files = glob.glob("*.jpg")
if not jpg_files:
    raise FileNotFoundError("No JPG files found in the current folder.")

image_path = max(jpg_files, key=os.path.getmtime)
img = cv2.imread(image_path)
annotated_img = img.copy()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV, 15, 10
)

horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

grid = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

output_folder = "cropped"
os.makedirs(output_folder, exist_ok=True)
cell_index = 0
padding = 20

for cnt in contours:
    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    if len(approx) == 4 and cv2.contourArea(cnt) > 1000:
        x, y, w, h = cv2.boundingRect(approx)
        if h < 100 or h > 500:
            continue

        x_pad = max(x - padding, 0)
        y_pad = max(y - padding, 0)
        x_end = min(x + w + padding, img.shape[1])
        y_end = min(y + h + padding, img.shape[0])

        cv2.rectangle(annotated_img, (x_pad, y_pad), (x_end, y_end), (0, 255, 0), 2)
        cropped = img[y_pad:y_end, x_pad:x_end]

        result = crop_and_pad_to_ratio(cropped)
        if result is None:
            continue

        binary = enhance_and_binarize(result)
        transparent = make_transparent(result, binary)

        save_path = os.path.join(output_folder, f"cell_{cell_index:03d}.png")
        cv2.imwrite(save_path, transparent)
        cell_index += 1

annotated_output = "annotated_cells.jpg"
cv2.imwrite(annotated_output, annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 10])

print(f"Done! {cell_index} cropped transparent cells saved to '{output_folder}'.")
