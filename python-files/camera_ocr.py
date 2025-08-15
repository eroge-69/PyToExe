#!/usr/bin/env python3
import os
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")  # helpful on some Linux setups

import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import datetime
from pathlib import Path
import numpy as np
import pytesseract

# ---------- Config ----------
DISPLAY_W, DISPLAY_H = 320, 240   # safe small resolution to avoid Xlib issues
CAPTURE_DIR = "captures"
OCR_OUTDIR = "ocr_results"
OCR_LANG = "eng"
MIN_CONF = 50
# Optional: if Tesseract isn't on PATH, set full exe path here:
TESSERACT_CMD = None  # e.g. r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ----------------------------

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# ensure folders exist
Path(CAPTURE_DIR).mkdir(parents=True, exist_ok=True)
Path(OCR_OUTDIR).mkdir(parents=True, exist_ok=True)
CAPTURE_DIR_ABS = str(Path(CAPTURE_DIR).resolve())
OCR_OUTDIR_ABS = str(Path(OCR_OUTDIR).resolve())

# --------- Helpers: preprocess & OCR ----------
def preprocess_for_ocr(img_bgr, target_width=1024):
    """Resize -> gray -> denoise -> CLAHE -> adaptive threshold. Returns thresh & vis (BGR)."""
    h, w = img_bgr.shape[:2]
    if w > target_width:
        scale = target_width / float(w)
        img_bgr = cv2.resize(img_bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    th = cv2.adaptiveThreshold(gray, 255,
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY,
                               blockSize=31, C=11)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return th, vis

def ocr_frame_and_save(bgr_frame, prefix="photo"):
    """
    Run OCR on BGR frame, save text and visualization.
    Returns dict with paths and text summary.
    """
    # timestamp filenames
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_filename = f"{prefix}_{ts}.jpg"
    img_path = str(Path(CAPTURE_DIR) / img_filename)

    # Save original captured image (BGR)
    try:
        ok = cv2.imwrite(img_path, bgr_frame)
        if not ok:
            raise RuntimeError("cv2.imwrite returned False")
    except Exception as e:
        # fallback: convert to PIL and save
        try:
            rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb).save(img_path, "JPEG", quality=90)
        except Exception as e2:
            raise RuntimeError(f"Failed to save captured image: {e} / {e2}")

    # Preprocess and OCR
    th_img, vis_img = preprocess_for_ocr(bgr_frame, target_width=1024)
    pil_for_ocr = Image.fromarray(cv2.cvtColor(th_img, cv2.COLOR_GRAY2RGB))

    # configure tesseract (PSM/OEM)
    custom_oem_psm = r"--oem 3 --psm 3"
    try:
        text = pytesseract.image_to_string(pil_for_ocr, lang=OCR_LANG, config=custom_oem_psm)
    except Exception as e:
        text = ""
        print("Tesseract OCR failed:", e)

    # word-level boxes
    try:
        data = pytesseract.image_to_data(pil_for_ocr, lang=OCR_LANG, config=custom_oem_psm, output_type=pytesseract.Output.DICT)
    except Exception:
        data = None

    words_saved = 0
    if data:
        n = len(data['level'])
        for i in range(n):
            conf_str = data['conf'][i]
            try:
                conf = float(conf_str)
            except:
                conf = -1.0
            txt = data['text'][i].strip()
            if txt and conf >= MIN_CONF:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.rectangle(vis_img, (x, y), (x + w, y + h), (0, 200, 0), 2)
                cv2.putText(vis_img, f"{int(conf)}", (x, max(8, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,200,0), 1, cv2.LINE_AA)
                words_saved += 1

    # save text and visualization
    txt_filename = f"{Path(img_filename).stem}.txt"
    vis_filename = f"{Path(img_filename).stem}_boxes.jpg"
    txt_path = str(Path(OCR_OUTDIR) / txt_filename)
    vis_path = str(Path(OCR_OUTDIR) / vis_filename)

    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        raise RuntimeError(f"Failed saving OCR text: {e}")

    try:
        cv2.imwrite(vis_path, vis_img)
    except Exception as e:
        print("Warning: failed to write vis image:", e)

    return {
        "image": img_path,
        "text_file": txt_path,
        "visualization": vis_path,
        "text": text,
        "words_drawn": words_saved
    }

# ---------- GUI & Camera ----------
root = tk.Tk()
root.title("Camera + OCR")
root.geometry(f"{DISPLAY_W+40}x{DISPLAY_H+160}")
root.resizable(False, False)

# OpenCV capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_H)

if not cap.isOpened():
    messagebox.showerror("Error", "Cannot access camera. Close other camera apps and retry.")
    root.destroy()
    raise SystemExit("Camera not available")

video_label = tk.Label(root, text="Camera not available" if not cap.isOpened() else "")
video_label.pack(padx=10, pady=10)

current_frame = None

def update_frame():
    global current_frame, tk_img
    ret, frame = cap.read()
    if not ret:
        video_label.after(50, update_frame)
        return

    current_frame = frame.copy()
    try:
        # resize display just to be safe (frame may already be DISPLAY_W x DISPLAY_H)
        disp = cv2.resize(frame, (DISPLAY_W, DISPLAY_H))
    except Exception:
        disp = frame

    # BGR -> RGB, convert to PIL then to ImageTk
    rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    try:
        tk_img = ImageTk.PhotoImage(image=pil_img)
        video_label.imgtk = tk_img
        video_label.configure(image=tk_img)
    except Exception as e:
        # If ImageTk fails, skip updating that frame but keep running
        print("Warning: ImageTk update failed:", e)

    # enable capture button once we have a frame
    if capture_btn['state'] == 'disabled':
        capture_btn.config(state='normal')

    video_label.after(30, update_frame)

def capture_photo():
    """Capture current frame, save image, run OCR, and show results."""
    global current_frame
    if current_frame is None:
        messagebox.showwarning("Warning", "No frame available to capture yet.")
        return

    try:
        result = ocr_frame_and_save(current_frame, prefix="photo")
    except Exception as e:
        messagebox.showerror("Error", f"Capture/OCR failed: {e}")
        return

    msg = f"Saved image:\n{result['image']}\n\nOCR text:\n{result['text_file']}\n\nVisualization:\n{result['visualization']}\n\nWords drawn: {result['words_drawn']}"
    # show short preview popup (first few lines)
    preview = (result['text'].strip().splitlines()[:8])
    preview_text = "\n".join(preview) if preview else "[no text detected]"
    messagebox.showinfo("Capture + OCR Complete", f"{msg}\n\nPreview:\n{preview_text}")

def on_closing():
    try:
        cap.release()
    except Exception:
        pass
    root.destroy()

# Controls
btn_frame = tk.Frame(root)
btn_frame.pack(pady=8)
capture_btn = tk.Button(btn_frame, text="Capture + OCR", command=capture_photo, width=16, state="disabled")
capture_btn.pack(side="left", padx=6)
quit_btn = tk.Button(btn_frame, text="Quit", command=on_closing, width=8)
quit_btn.pack(side="left", padx=6)

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start loop
update_frame()
root.mainloop()
