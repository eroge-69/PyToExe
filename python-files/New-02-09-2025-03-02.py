#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust Live Edge Detection (vmbpy + OpenCV)

- Enumerates Allied Vision cameras (vmbpy)
- Converts any incoming frame to a 3-channel OpenCV BGR uint8 image
- Loads affine calibration and overlays edge-to-edge measurements
- Hotkeys: ESC, S, R, I, C, L
"""
import cv2
import numpy as np
import math
from datetime import datetime
from vmbpy import VmbSystem
import os

# ---------- Config ----------
CALIB_XML_PATH = "calibration_data.xml"
MIN_AREA = 500
WINDOW_NAME = "Live Detection"
FRAME_WIDTH = 1280  # Fixed frame width for GUI
FRAME_HEIGHT = 720  # Fixed frame height for GUI

# ROI size settings (independent width and height)
ROI_WIDTH = 1000
ROI_HEIGHT = 600

# Trackbar and buttons dimensions and positions
TRACKBAR_HEIGHT = 55
BUTTONS_HEIGHT = 30
WINDOW_MARGIN = 15
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Colors
COLOR_BG = (40, 40, 40)
COLOR_TEXT = (220, 220, 220)
COLOR_ACCENT = (0, 140, 255)
COLOR_BUTTON_BG = (60, 60, 60)
COLOR_BUTTON_BORDER = (100, 100, 100)
COLOR_BUTTON_TEXT = (200, 200, 200)

# Canvas size (fixed)
CANVAS_WIDTH = FRAME_WIDTH + WINDOW_MARGIN * 2
CANVAS_HEIGHT = FRAME_HEIGHT + TRACKBAR_HEIGHT + BUTTONS_HEIGHT + WINDOW_MARGIN * 4

# ---------- Globals ----------
AFFINE_PARAMS = None
INVERT_BINARY = True
last_output = None

# Calibration mode globals
calibration_mode = False
calib_points_img = []
calib_points_real = []
calib_clicks_img = None

# Mouse offset for image in window (top-left corner of image inside canvas)
mouse_img_offset_x = WINDOW_MARGIN
mouse_img_offset_y = WINDOW_MARGIN

# ---------- Calibration ----------
def load_calibration(xml_path=CALIB_XML_PATH):
    if not os.path.isfile(xml_path):
        print(f"⚠️ Calibration file {xml_path} does not exist.")
        return None

    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        print(f"⚠️ Could not open calibration file: {xml_path}")
        return None
    params = fs.getNode("affine_parameters").mat()
    fs.release()

    if params is None or params.size == 0:
        print("⚠️ 'affine_parameters' not found or empty in calibration XML.")
        return None

    if params.shape != (3, 2):
        if params.size == 6:
            params = params.reshape((3, 2))
        else:
            print(f"⚠️ Unexpected affine_parameters shape {params.shape}, expected (3,2).")
            return None

    print("✅ Calibration loaded from XML.")
    return params

def save_calibration(affine_params, xml_path=CALIB_XML_PATH):
    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_WRITE)
    fs.write("affine_parameters", affine_params)
    fs.release()
    print(f"💾 Calibration saved to {xml_path}")

def pixels_to_microns(points_xy, affine_params):
    points_xy = np.asarray(points_xy, dtype=np.float32)
    ones = np.ones((points_xy.shape[0], 1), dtype=np.float32)
    img_ext = np.hstack([points_xy, ones])
    mic = img_ext @ affine_params.astype(np.float32)
    return mic

# ---------- UI helpers ----------
def nothing(x): pass
def ensure_odd(n): return n if n % 2 == 1 else max(1, n-1)

def setup_window():
    # Create fixed-size window, allow normal window but fix size and trackbars
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, CANVAS_WIDTH, CANVAS_HEIGHT)
    # Create trackbars once here
    cv2.createTrackbar("Thresh Low", WINDOW_NAME, 50, 255, nothing)
    cv2.createTrackbar("Thresh High", WINDOW_NAME, 255, 255, nothing)
    cv2.createTrackbar("Kernel Size", WINDOW_NAME, 5, 31, nothing)

def draw_buttons_and_text(img):
    # Draw a sober, simple UI panel for buttons and instructions below the image and trackbars
    height, width = img.shape[:2]
    panel_top = FRAME_HEIGHT + TRACKBAR_HEIGHT + WINDOW_MARGIN * 2
    panel_bottom = panel_top + BUTTONS_HEIGHT + WINDOW_MARGIN
    cv2.rectangle(img, (0, panel_top), (width, panel_bottom), COLOR_BG, thickness=-1)

    keys_text = "[ESC]=Quit  [S]=Save  [R]=Reset kernel  [I]=Invert  [C]=Reload XML  [L]=Calibrate"
    cv2.putText(img, keys_text, (WINDOW_MARGIN, panel_top + BUTTONS_HEIGHT - 8),
                FONT, 0.55, COLOR_TEXT, 1, cv2.LINE_AA)

def get_trackbar_values():
    # Wrap getTrackbarPos in try-except to avoid errors if trackbars are missing
    try:
        t_low = cv2.getTrackbarPos("Thresh Low", WINDOW_NAME)
        t_high = cv2.getTrackbarPos("Thresh High", WINDOW_NAME)
        ksize = ensure_odd(max(1, cv2.getTrackbarPos("Kernel Size", WINDOW_NAME)))
    except cv2.error:
        # Default values if trackbars not ready
        t_low, t_high, ksize = 50, 255, 5
    return t_low, t_high, ksize

# ---------- Frame normalization ----------
def normalize_frame_to_bgr(img):
    if img is None:
        raise ValueError("Received None image")
    img = np.asarray(img)
    if img.dtype != np.uint8:
        if np.issubdtype(img.dtype, np.floating):
            img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.ndim == 3:
        h, w, ch = img.shape
        if ch == 1:
            squeezed = img.reshape((h, w))
            return cv2.cvtColor(squeezed, cv2.COLOR_GRAY2BGR)
        if ch == 3:
            return img
        if ch == 4:
            try:
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            except Exception:
                return img[:, :, :3]
        if ch > 4:
            return img[:, :, :3]
        raise ValueError(f"Unsupported image shape {img.shape}")
    raise ValueError(f"Unsupported image ndim {img.ndim}")

# ---------- Calibration mouse callback ----------
def calibration_mouse_callback(event, x, y, flags, param):
    global calib_points_img, calib_points_real, calib_clicks_img, calibration_mode
    if not calibration_mode:
        return

    # Convert mouse (x,y) to image coordinates relative to image origin on canvas
    img_x = x - mouse_img_offset_x
    img_y = y - mouse_img_offset_y

    # Check if click inside image area
    if img_x < 0 or img_x >= FRAME_WIDTH or img_y < 0 or img_y >= FRAME_HEIGHT:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(calib_points_img) < 3:
            calib_points_img.append((img_x, img_y))
            calib_points_real.append((float(img_x), float(img_y)))  # 1 px = 1 mm
            cv2.circle(calib_clicks_img, (int(img_x), int(img_y)), 7, (0, 255, 255), -1)
            cv2.putText(calib_clicks_img, f"P{len(calib_points_img)}", (int(img_x) + 10, int(img_y) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            print(f"🖱️ Calibration point {len(calib_points_img)}: Image {int(img_x)},{int(img_y)} Real {int(img_x)},{int(img_y)}")
        if len(calib_points_img) == 3:
            print("✅ 3 calibration points collected. Computing affine transform...")
            compute_and_save_calibration()

def compute_and_save_calibration():
    global AFFINE_PARAMS, calib_points_img, calib_points_real, calibration_mode
    pts_img = np.array(calib_points_img, dtype=np.float32)
    pts_real = np.array(calib_points_real, dtype=np.float32)

    affine = cv2.getAffineTransform(pts_img, pts_real)
    affine_params = np.vstack([affine.T, [0, 0]]).astype(np.float32)
    AFFINE_PARAMS = affine_params
    save_calibration(AFFINE_PARAMS)
    calibration_mode = False
    print("🎉 Calibration complete and saved. Resuming normal operations.")

# ---------- Processing ----------
def process_frame(frame_bgr):
    global last_output, AFFINE_PARAMS, INVERT_BINARY

    h, w = frame_bgr.shape[:2]

    roi_w = min(ROI_WIDTH, w)
    roi_h = min(ROI_HEIGHT, h)
    x_start = (w - roi_w) // 2
    y_start = (h - roi_h) // 2
    x_end = x_start + roi_w
    y_end = y_start + roi_h

    roi = frame_bgr[y_start:y_end, x_start:x_end]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    t_low, t_high, ksize = get_trackbar_values()

    if INVERT_BINARY:
        _, mask = cv2.threshold(gray, t_low, t_high, cv2.THRESH_BINARY_INV)
    else:
        _, mask = cv2.threshold(gray, t_low, t_high, cv2.THRESH_BINARY)

    kernel = np.ones((ksize, ksize), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output = frame_bgr.copy()

    cv2.rectangle(output, (x_start, y_start), (x_end, y_end), (255, 255, 255), 2)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        approx_offset = approx + np.array([x_start, y_start])
        cv2.drawContours(output, [approx_offset], -1, (0, 255, 0), 2)

        pts = approx.reshape(-1, 2)
        if pts.shape[0] < 2:
            continue

        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]

            x1_full, y1_full = x1 + x_start, y1 + y_start
            x2_full, y2_full = x2 + x_start, y2 + y_start

            if AFFINE_PARAMS is not None:
                mic = pixels_to_microns(np.array([[x1_full, y1_full], [x2_full, y2_full]], dtype=np.float32), AFFINE_PARAMS)
                (X1, Y1), (X2, Y2) = mic[0], mic[1]
                length_mm = float(np.hypot(X2 - X1, Y2 - Y1))
                label = f"{length_mm:.3f} mm"
            else:
                length_px = math.hypot(x2 - x1, y2 - y1)
                label = f"{length_px:.1f} px"

            mid_x, mid_y = int((x1_full + x2_full) * 0.5), int((y1_full + y2_full) * 0.5)
            cv2.putText(output, label, (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    border_size = 5
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_bgr = cv2.copyMakeBorder(mask_bgr, border_size, border_size, border_size, border_size,
                                  cv2.BORDER_CONSTANT, value=(0, 0, 0))
    frame_bgr_border = cv2.copyMakeBorder(frame_bgr, border_size, border_size, border_size, border_size,
                                          cv2.BORDER_CONSTANT, value=(0, 0, 0))
    output_border = cv2.copyMakeBorder(output, border_size, border_size, border_size, border_size,
                                       cv2.BORDER_CONSTANT, value=(0, 0, 0))

    try:
        stacked = np.hstack((frame_bgr_border, mask_bgr, output_border))
    except Exception:
        stacked = output_border
    last_output = output.copy()
    return stacked

def save_output_frame():
    global last_output
    if last_output is None:
        print("⚠️ No processed frame to save yet.")
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"measured_{ts}.png"
    cv2.imwrite(fname, last_output)
    print(f"💾 Saved: {fname}")
    return fname

# ---------- Camera selection ----------
def list_cameras(vmb):
    cams = vmb.get_all_cameras()
    info = []
    for i, cam in enumerate(cams):
        try:
            cam_id = cam.get_id()
        except Exception:
            cam_id = f"cam_{i}"
        try:
            cam_name = cam.get_name()
        except Exception:
            cam_name = cam_id
        info.append((i, cam_id, cam_name, cam))
    return info

def choose_camera_auto(vmb):
    cams_info = list_cameras(vmb)
    if not cams_info:
        print("❌ No Allied Vision cameras found.")
        return None
    i, cam_id, cam_name, cam_obj = cams_info[0]
    print(f"👉 Automatically selected camera [{i}] id={cam_id} name={cam_name}")
    return cam_obj

# ---------- Main ----------
def main():
    global AFFINE_PARAMS, INVERT_BINARY, calibration_mode, calib_clicks_img, calib_points_img, calib_points_real

    AFFINE_PARAMS = load_calibration(CALIB_XML_PATH)
    if AFFINE_PARAMS is None:
        print("⚠️ No calibration data found. Press 'L' to start calibration.")

    setup_window()
    cv2.setMouseCallback(WINDOW_NAME, calibration_mouse_callback)

    try:
        with VmbSystem.get_instance() as vmb:
            cam = choose_camera_auto(vmb)
            if cam is None:
                return

            with cam:
                print("🎥 Camera opened. Starting stream... (press ESC to quit)")
                print("   Keys: [ESC]=Quit  [S]=Save  [R]=Reset kernel  [I]=Invert  [C]=Reload XML  [L]=Calibrate")

                try:
                    if hasattr(cam, "set_pixel_format"):
                        for fmt in ("Bgr8", "BGR8", "RGB8", "Mono8"):
                            try:
                                cam.set_pixel_format(fmt)
                                print(f"Requested pixel format: {fmt}")
                                break
                            except Exception:
                                continue
                except Exception:
                    pass

                while True:
                    try:
                        try:
                            frame = cam.get_frame(timeout_ms=2000)
                        except TypeError:
                            frame = cam.get_frame()
                        img = None
                        if hasattr(frame, "as_opencv_image"):
                            try:
                                img = frame.as_opencv_image()
                            except Exception:
                                img = None
                        if img is None and hasattr(frame, "as_numpy"):
                            try:
                                img = np.array(frame.as_numpy(), copy=False)
                            except Exception:
                                img = None
                        if img is None:
                            raise RuntimeError("Cannot convert frame to numpy image; frame repr: " + repr(frame))

                        img_bgr = normalize_frame_to_bgr(img)

                    except Exception as e:
                        print("⚠️ Frame grab / conversion failed:", e)
                        break

                    img_bgr = cv2.resize(img_bgr, (FRAME_WIDTH, FRAME_HEIGHT))

                    # Prepare canvas with fixed size
                    canvas = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
                    canvas[:] = COLOR_BG

                    if calibration_mode:
                        if calib_clicks_img is None:
                            calib_clicks_img = img_bgr.copy()
                        canvas[WINDOW_MARGIN:WINDOW_MARGIN + FRAME_HEIGHT, WINDOW_MARGIN:WINDOW_MARGIN + FRAME_WIDTH] = calib_clicks_img
                    else:
                        stacked_img = process_frame(img_bgr)
                        try:
                            stacked_img = cv2.resize(stacked_img, (FRAME_WIDTH, FRAME_HEIGHT))
                        except Exception:
                            pass
                        canvas[WINDOW_MARGIN:WINDOW_MARGIN + FRAME_HEIGHT, WINDOW_MARGIN:WINDOW_MARGIN + FRAME_WIDTH] = stacked_img

                    # Draw trackbars background rectangle (below image)
                    trackbar_y_start = WINDOW_MARGIN + FRAME_HEIGHT + WINDOW_MARGIN
                    cv2.rectangle(canvas, (0, trackbar_y_start), (CANVAS_WIDTH, trackbar_y_start + TRACKBAR_HEIGHT), COLOR_BG, -1)

                    # Draw buttons/keys instructions panel
                    draw_buttons_and_text(canvas)

                    cv2.imshow(WINDOW_NAME, canvas)

                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC
                        break
                    elif key in (ord('s'), ord('S')):
                        save_output_frame()
                    elif key in (ord('r'), ord('R')):
                        cv2.setTrackbarPos("Kernel Size", WINDOW_NAME, 5)
                        print("🔧 Kernel size reset to 5.")
                    elif key in (ord('i'), ord('I')):
                        INVERT_BINARY = not INVERT_BINARY
                        print(f"🌓 Invert binary = {INVERT_BINARY}")
                    elif key in (ord('c'), ord('C')):
                        AFFINE_PARAMS = load_calibration(CALIB_XML_PATH)
                    elif key in (ord('l'), ord('L')):
                        calibration_mode = True
                        calib_points_img = []
                        calib_points_real = []
                        calib_clicks_img = img_bgr.copy()
                        print("🛠️ Calibration mode started. Click 3 points on the image.")

    except Exception as e:
        print("Vmbpy/Vimba system error (main):", e)

    finally:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        print("👋 Bye.")

if __name__ == "__main__":
    main()