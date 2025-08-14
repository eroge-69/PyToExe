import re
import cv2
import numpy as np
from pathlib import Path
import sys
import os
from PIL import Image

import torch
# Fix for PyInstaller onefile builds
if getattr(sys, 'frozen', False):
    # Add the temporary extraction directory to DLL search path
    if sys.platform == 'win32':
        os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']
        if hasattr(sys, '_MEIPASS'):
            os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']

import torch.nn.functional as F
from torchvision.transforms.functional import normalize

from transformers import AutoModelForImageSegmentation
model = AutoModelForImageSegmentation.from_pretrained(
    r"C:/Users/mis/Downloads/WPy64-312101/notebooks/RMBG-1.4",  # use forward slashes
    trust_remote_code=True
)
print("Model loaded successfully!")


class SuppressStderr:
    def __enter__(self):
        self.stderr_fileno = sys.stderr.fileno()
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        self.old_stderr = os.dup(self.stderr_fileno)
        os.dup2(self.devnull, self.stderr_fileno)
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.old_stderr, self.stderr_fileno)
        os.close(self.devnull)

with SuppressStderr():
    import mediapipe as mp
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# --- RMBG Model Setup ---
def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2,0,1)
    im_tensor = F.interpolate(torch.unsqueeze(im_tensor,0), size=model_input_size, mode='bilinear')
    image = torch.divide(im_tensor, 255.0)
    image = normalize(image, [0.5,0.5,0.5], [1.0,1.0,1.0])
    return image

def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
    result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result-mi)/(ma-mi)
    im_array = (result*255).permute(1,2,0).cpu().data.numpy().astype(np.uint8)
    im_array = np.squeeze(im_array)
    return im_array

# Load RMBG model
model = AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4", trust_remote_code=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)
model_input_size = [1024, 1024]

# Configuration
input_folder = "input_folder"
output_folder = "output_folder"
preview_size = 700
default_zoom = 2.15
zoom_increment = 0.01
move_increment = 0.005

# Supported input extensions
input_extensions = ('.jpg', '.jpeg', '.png')

# Create output folder
Path(output_folder).mkdir(parents=True, exist_ok=True)

def extract_number(filename):
    """Extract numeric portion from filename"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

def get_resume_index():
    """Determine where to resume processing based on output files"""
    input_files = sorted([f for f in os.listdir(input_folder) 
                         if f.lower().endswith(input_extensions)], 
                        key=extract_number)
    output_files = sorted([f for f in os.listdir(output_folder) 
                          if f.lower().endswith('.jpg')], 
                         key=extract_number)
    
    if not output_files:
        return 0  # Start from beginning if no outputs
    
    # Get highest numbered output file
    last_output = output_files[-1]
    last_num = extract_number(last_output)
    
    # Find position in input files
    for i, f in enumerate(input_files):
        if extract_number(f) > last_num:
            return i
    
    return len(input_files)  # All files processed

def detect_faces(image):
    """Detect faces in image using MediaPipe"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_image)
    
    faces = []
    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            faces.append({
                'x': bbox.xmin,
                'y': bbox.ymin,
                'width': bbox.width,
                'height': bbox.height
            })
    return faces

def get_crop_coordinates(face, image_size, zoom, x_off, y_off):
    """Calculate crop coordinates with edge detection"""
    img_h, img_w = image_size
    
    x = int(face['x'] * img_w)
    y = int(face['y'] * img_h)
    w = int(face['width'] * img_w)
    h = int(face['height'] * img_h)
    
    center_x = x + w // 2
    center_y = y + h // 2
    
    crop_size = int(min(img_w, img_h, max(w, h) * zoom))
    
    x_off_px = int(x_off * crop_size)
    y_off_px = int(y_off * crop_size)
    
    # Calculate initial crop coordinates
    x1 = center_x - crop_size // 2 + x_off_px
    y1 = center_y - crop_size // 2 + y_off_px
    
    # Adjust if we hit the edges
    if x1 < 0:
        x_off_px = -(center_x - crop_size // 2)
        x1 = 0
    elif x1 + crop_size > img_w:
        x_off_px = img_w - (center_x + crop_size // 2)
        x1 = img_w - crop_size
    
    if y1 < 0:
        y_off_px = -(center_y - crop_size // 2)
        y1 = 0
    elif y1 + crop_size > img_h:
        y_off_px = img_h - (center_y + crop_size // 2)
        y1 = img_h - crop_size
    
    x2 = x1 + crop_size
    y2 = y1 + crop_size
    
    # Calculate actual offsets used
    actual_x_off = x_off_px / crop_size
    actual_y_off = y_off_px / crop_size
    
    return int(x1), int(y1), int(x2), int(y2), actual_x_off, actual_y_off

def add_grid(image, grid_size=3):
    """Add 3x3 grid overlay to image"""
    h, w = image.shape[:2]
    color = (0, 255, 0)  # Green grid lines
    thickness = 1
    
    # Vertical lines
    for i in range(1, grid_size):
        x = int(w * i / grid_size)
        cv2.line(image, (x, 0), (x, h), color, thickness)
    
    # Horizontal lines
    for i in range(1, grid_size):
        y = int(h * i / grid_size)
        cv2.line(image, (0, y), (w, y), color, thickness)
    
    return image
    
def add_border_to_preview(preview, border_size=100, border_color=(30, 30, 30)):
    preview_with_border = cv2.copyMakeBorder(
        preview,
        top=border_size,
        bottom=border_size,
        left=border_size,
        right=border_size,
        borderType=cv2.BORDER_CONSTANT,
        value=border_color
    )
    return preview_with_border

def add_progress_text(image, text):
    """Add progress text to the preview"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color = (255, 255, 255)
    text_bg_color = (0, 0, 0)
    
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x = (image.shape[1] - text_size[0]) // 2
    text_y = (image.shape[0] + text_size[1]) // 2
    
    # Add background rectangle
    cv2.rectangle(image, 
                 (text_x - 5, text_y - text_size[1] - 5),
                 (text_x + text_size[0] + 5, text_y + 5),
                 text_bg_color, -1)
    
    # Add text
    cv2.putText(image, text, (text_x, text_y), 
               font, font_scale, text_color, font_thickness)
    
    return image

def show_preview(image, crop_coords, progress_text=None):
    """Show preview with grid and optional progress text"""
    x1, y1, x2, y2, x_off, y_off = crop_coords
    cropped = image[y1:y2, x1:x2]
    
    if cropped.size > 0:
        preview = cv2.resize(cropped, (preview_size, preview_size))
        preview_with_grid = add_grid(preview.copy())
        
        if progress_text:
            preview_with_grid = add_progress_text(preview_with_grid, progress_text)
            
        preview_with_grid_border = add_border_to_preview(preview_with_grid)
        cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
        cv2.imshow("Preview", preview_with_grid_border)
        cv2.waitKey(1)  # Force update the display
    return cropped, x_off, y_off

def remove_background(cropped_image):
    """Remove background using RMBG model"""
    # Convert to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    
    # Preprocess
    orig_im = np.array(pil_image)
    orig_im_size = orig_im.shape[0:2]
    image = preprocess_image(orig_im, model_input_size).to(device)
    
    # Inference
    with torch.no_grad():
        result = model(image)
    
    # Postprocess mask
    result_image = postprocess_image(result[0][0], orig_im_size)
    
    # Optional: sharpen mask edges with morphology
    kernel = np.ones((3,3), np.uint8)
    mask_refined = cv2.erode(result_image, kernel, iterations=1)
    mask_refined = cv2.dilate(mask_refined, kernel, iterations=1)
    
    # Compose on white background
    pil_mask_im = Image.fromarray(mask_refined).convert("L")
    orig_image = pil_image.convert("RGB")  # ensure no alpha
    bg = Image.new("RGB", orig_image.size, (255,255,255))
    bg.paste(orig_image, mask=pil_mask_im)
    
    return cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)

def process_image(image_path, zoom_level, x_offset, y_offset):
    """Process a single image"""
    current_face_idx = 0
    
    # Load image with alpha channel if it's a PNG
    if image_path.lower().endswith('.png'):
        image = cv2.imread(os.path.join(input_folder, image_path), cv2.IMREAD_UNCHANGED)
        if image is not None:
            # If image has alpha channel, composite with white background
            if image.shape[2] == 4:
                # Create white background
                white_bg = np.ones((image.shape[0], image.shape[1], 3), dtype=np.uint8) * 255
                # Normalize alpha channel to range [0, 1]
                alpha = image[:,:,3] / 255.0
                # Composite RGB channels with white background using alpha
                white_bg = white_bg * (1 - alpha[:, :, None]) + image[:, :, :3] * alpha[:, :, None]
                image = white_bg.astype(np.uint8)
    else:
        image = cv2.imread(os.path.join(input_folder, image_path))

    if image is None:
        print(f"Failed to load image: {image_path}")
        return False, zoom_level, x_offset, y_offset, False
    
    faces = detect_faces(image)
    if not faces:
        print(f"No faces detected in {image_path}")
        # Create marker file
        open(os.path.join(output_folder, f"{Path(image_path).stem}_nofaces.txt"), 'w').close()
        return False, zoom_level, x_offset, y_offset, False
    
    print(f"Found {len(faces)} faces in {image_path}")
    
    while current_face_idx < len(faces):
        face = faces[current_face_idx]
        crop_coords = get_crop_coordinates(face, image.shape[:2], zoom_level, x_offset, y_offset)
        cropped, new_x_offset, new_y_offset = show_preview(image, crop_coords)
        
        # Update offsets
        x_offset, y_offset = new_x_offset, new_y_offset
        
        print(f"Face {current_face_idx + 1}/{len(faces)} - Zoom: {zoom_level:.2f} - "
              f"Offset: ({x_offset:.2f}, {y_offset:.2f}) - "
              f"Press: [Space/S] Save, [N] Next, [P] Previous, [J/L] Move H, [I/K] Move V, [+/-] Zoom")
        
        key = cv2.waitKey(0)
        if key == -1:
            continue
            
        key = key & 0xFF
        
        if key in (43, 120):  # Zoom in
            zoom_level = max(1.0, zoom_level - zoom_increment)
        elif key in (45, 121):  # Zoom out
            zoom_level += zoom_increment
        elif key == 108:  # Move left
            x_offset -= move_increment
        elif key == 106:  # Move right
            x_offset += move_increment
        elif key == 107:  # Move up
            y_offset -= move_increment
        elif key == 105:  # Move down
            y_offset += move_increment
        elif key in (32, 115):  # Save
            if cropped.size > 0:
                # Show "Processing..." message
                _, _, _ = show_preview(image, crop_coords, "Removing background...")
                
                # Remove background
                final_image = remove_background(cropped)
                
                # Show the final image briefly
                preview_final = cv2.resize(final_image, (preview_size, preview_size))
                preview_final_with_border = add_border_to_preview(preview_final)
                cv2.imshow("Preview", preview_final_with_border)
                cv2.waitKey(1000)  # Show for 500ms
                
                # Save the final image
                output_path = os.path.join(output_folder, f"{Path(image_path).stem}_face.jpg")
                cv2.imwrite(output_path, final_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                print(f"Saved to {output_path}")
                
            current_face_idx += 1
            zoom_level = default_zoom
            x_offset = 0.0
            y_offset = 0.0
        elif key == 110:  # Next
            current_face_idx += 1
            zoom_level = default_zoom
            x_offset = 0.0
            y_offset = 0.0
        elif key == 112:  # Previous ('p' key)
            return True, zoom_level, x_offset, y_offset, True  # Signal to go back
        elif key in (27, 113):  # Quit
            cv2.destroyAllWindows()
            return True, zoom_level, x_offset, y_offset, False  # Signal to quit
    
    return False, zoom_level, x_offset, y_offset, False  # No need to go back or quit

def main():
    image_files = sorted([f for f in os.listdir(input_folder)
                          if f.lower().endswith(input_extensions)],
                         key=extract_number)
    if not image_files:
        print(f"No JPG/PNG files found in input folder. Supported extensions: {input_extensions}")
        return
    
    # Determine resume position
    current_image_idx = get_resume_index()
    if current_image_idx >= len(image_files):
        print("All files already processed.")
        return
    
    print(f"Resuming from file {current_image_idx + 1}/{len(image_files)}: {image_files[current_image_idx]}")
    
    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Preview", preview_size, preview_size)
    
    # Initialize state variables
    zoom_level = default_zoom
    x_offset = 0.0
    y_offset = 0.0
    
    while current_image_idx < len(image_files):
        image_file = image_files[current_image_idx]
        
        print(f"\nProcessing {image_file} ({current_image_idx + 1}/{len(image_files)})")
        
        should_exit, zoom_level, x_offset, y_offset, go_back = process_image(
            image_file, zoom_level, x_offset, y_offset
        )
        
        if should_exit:
            if go_back:
                # Go to previous image if possible
                if current_image_idx > 0:
                    current_image_idx -= 1
                    # Reset zoom and offsets when going back
                    zoom_level = default_zoom
                    x_offset = 0.0
                    y_offset = 0.0
                    continue
                else:
                    print("Already at first image")
            else:
                break  # Quit processing
        
        if not go_back:
            current_image_idx += 1
    
    cv2.destroyAllWindows()
    face_detection.close()
    print("Processing complete.")

if __name__ == "__main__":
    main()