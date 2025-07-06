import cv2
import numpy as np
import os

# Input and output paths
input_path = 'mysample.mp4'
output_dir = 'enhanced_folder'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'mysample_enhanced.mp4')

# Open input video
cap = cv2.VideoCapture(input_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Initialize stabilization
prev_gray = None
transforms = []

# Helper: Apply white balance
def white_balance(img):
    result = cv2.xphoto.createSimpleWB()
    return result.balanceWhite(img)

# Helper: Enhance color using CLAHE
def enhance_color(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Stabilization: estimate transform
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if prev_gray is not None:
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30)
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None)
        idx = np.where(status == 1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]
        m = cv2.estimateAffinePartial2D(prev_pts, curr_pts)[0]
        if m is not None:
            frame = cv2.warpAffine(frame, m, (width, height))
    prev_gray = gray

    # White balance
    try:
        frame = white_balance(frame)
    except:
        pass  # fallback if white balance fails

    # Denoise
    frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

    # Color enhancement
    frame = enhance_color(frame)

    # Write frame
    out.write(frame)

# Cleanup
cap.release()
out.release()
print(f"✅ Enhanced video saved to: {output_path}")
