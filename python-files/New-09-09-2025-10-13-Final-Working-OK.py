#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust Live Edge Detection (vmbpy + OpenCV)

- Enumerates Allied Vision cameras (vmbpy)
- Converts any incoming frame to a 3-channel OpenCV BGR uint8 image
- Loads affine calibration and overlays edge-to-edge measurements
- Measurements displayed in mm with adjustable correction factor
- Hotkeys: ESC, S, R, I, C, L, +, -
"""

import cv2
import numpy as np
import math
from datetime import datetime
from vmbpy import VmbSystem
import os
import re
import tkinter as tk
from tkinter import ttk

# ---------- Config ----------
CALIB_XML_PATH = "camera_calibration.xml"
SETTINGS_XML_PATH = "program_settings.xml"
MIN_AREA = 500
WINDOW_NAME = "Live Detection"
FRAME_WIDTH = 1936  # Fixed frame width for GUI
FRAME_HEIGHT = 1216  # Fixed frame height for GUI

# ROI size settings (independent width and height)
ROI_WIDTH = 608
ROI_HEIGHT = 970

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
COLOR_CALIB_INSTRUCTION = (0, 255, 0)
COLOR_CALIB_POINT = (0, 255, 255)
COLOR_CALIB_CONFIRM = (0, 200, 255)
COLOR_TEXTBOX_BG = (30, 30, 30)
COLOR_TEXTBOX_BORDER = (100, 100, 100)
COLOR_TEXTBOX_TEXT = (255, 255, 255)
COLOR_ERROR = (0, 0, 255)
COLOR_MM_CORRECTION = (255, 255, 0)  # Yellow for correction factor display
COLOR_CHECKBOX = (0, 255, 0)  # Green for checkbox
COLOR_TAB_ACTIVE = (60, 60, 100)
COLOR_TAB_INACTIVE = (40, 40, 60)
COLOR_VIEW_SELECTOR = (0, 200, 255)  # Orange for view selector

# Canvas size (fixed)
CANVAS_WIDTH = FRAME_WIDTH + WINDOW_MARGIN * 2
CANVAS_HEIGHT = FRAME_HEIGHT + TRACKBAR_HEIGHT + BUTTONS_HEIGHT + WINDOW_MARGIN * 4 + 40  # Added space for tabs

# ---------- Globals ----------
AFFINE_PARAMS = None
INVERT_BINARY = True
last_output = None
MM_CORRECTION_FACTOR = 1.0  # Default correction factor (no correction)
SHOW_IN_MM = True  # Default to show measurements in mm

# Tab system globals
current_tab = 0  # 0: Live View, 1: Settings, 2: Calibration
TAB_NAMES = ["Live View", "Settings", "Calibration"]

# View selection globals
current_view = 3  # 0: Original, 1: Mask, 2: Processed, 3: All views
VIEW_NAMES = ["Original", "Mask", "Processed", "All Views"]

# Calibration mode globals
calibration_mode = False
calib_points_img = []
calib_points_real = []
calib_clicks_img = None
calib_zoom_factor = 1.0
calib_zoom_center = (FRAME_WIDTH // 2, FRAME_HEIGHT // 2)
calib_step = 0  # 0: collecting points, 1: entering grid info, 2: confirmation
grid_width = 0
grid_height = 0
grid_spacing = 0
max_calib_points = 12  # Maximum number of calibration points

# Save mode globals
save_mode = False
text_input_active = False
current_textbox = 0
textbox_values = ["", "", ""]  # [numerical1, numerical2, alphabetical]
error_message = ""
error_message_time = 0

# Settings globals
settings_values = {
    "threshold_low": 100,
    "threshold_high": 255,
    "kernel_size": 8,
    "min_area": 500,
    "roi_width": 608,
    "roi_height": 970,
    "mm_correction": 1.0,
    "show_in_mm": True,
    "current_view": 0  # Store the current view selection
}

# Mouse offset for image in window (top-left corner of image inside canvas)
mouse_img_offset_x = WINDOW_MARGIN
mouse_img_offset_y = WINDOW_MARGIN + 40  # Added space for tabs

# ---------- Settings Management ----------
def load_settings(xml_path=SETTINGS_XML_PATH):
    global settings_values, MM_CORRECTION_FACTOR, current_view
    
    if not os.path.isfile(xml_path):
        print(f"⚠️ Settings file {xml_path} does not exist. Using default values.")
        return False

    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        print(f"⚠️ Could not open settings file: {xml_path}")
        return False
    
    # Load settings values
    settings_values["threshold_low"] = int(fs.getNode("threshold_low").real() or settings_values["threshold_low"])
    settings_values["threshold_high"] = int(fs.getNode("threshold_high").real() or settings_values["threshold_high"])
    settings_values["kernel_size"] = int(fs.getNode("kernel_size").real() or settings_values["kernel_size"])
    settings_values["min_area"] = int(fs.getNode("min_area").real() or settings_values["min_area"])
    settings_values["roi_width"] = int(fs.getNode("roi_width").real() or settings_values["roi_width"])
    settings_values["roi_height"] = int(fs.getNode("roi_height").real() or settings_values["roi_height"])
    settings_values["mm_correction"] = float(fs.getNode("mm_correction").real() or settings_values["mm_correction"])
    settings_values["show_in_mm"] = bool(int(fs.getNode("show_in_mm").real() or settings_values["show_in_mm"]))
    settings_values["current_view"] = int(fs.getNode("current_view").real() or settings_values["current_view"])
    
    # Update global variables
    MM_CORRECTION_FACTOR = settings_values["mm_correction"]
    current_view = settings_values["current_view"]
    SHOW_IN_MM = settings_values["show_in_mm"]
    
    fs.release()
    print(f"✅ Settings loaded from {xml_path}")
    return True

def save_settings(xml_path=SETTINGS_XML_PATH):
    global settings_values
    
    # Update settings with current values
    settings_values["threshold_low"] = cv2.getTrackbarPos("Thresh Low", WINDOW_NAME)
    settings_values["threshold_high"] = cv2.getTrackbarPos("Thresh High", WINDOW_NAME)
    settings_values["kernel_size"] = cv2.getTrackbarPos("Kernel Size", WINDOW_NAME)
    settings_values["mm_correction"] = MM_CORRECTION_FACTOR
    settings_values["show_in_mm"] = SHOW_IN_MM
    settings_values["current_view"] = current_view
    
    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_WRITE)
    fs.write("threshold_low", settings_values["threshold_low"])
    fs.write("threshold_high", settings_values["threshold_high"])
    fs.write("kernel_size", settings_values["kernel_size"])
    fs.write("min_area", settings_values["min_area"])
    fs.write("roi_width", settings_values["roi_width"])
    fs.write("roi_height", settings_values["roi_height"])
    fs.write("mm_correction", settings_values["mm_correction"])
    fs.write("show_in_mm", int(settings_values["show_in_mm"]))
    fs.write("current_view", settings_values["current_view"])
    fs.release()
    print(f"💾 Settings saved to {xml_path}")

# ---------- Window Management ----------
def setup_window():
    # Create fixed-size window, allow normal window but fix size and trackbars
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, CANVAS_WIDTH, CANVAS_HEIGHT)
    
    # Maximize the window
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Hide minimize and close buttons using Tkinter
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
    except:
        pass
    
    # Create trackbars once here with saved values
    cv2.createTrackbar("Thresh Low", WINDOW_NAME, settings_values["threshold_low"], 255, nothing)
    cv2.createTrackbar("Thresh High", WINDOW_NAME, settings_values["threshold_high"], 255, nothing)
    cv2.createTrackbar("Kernel Size", WINDOW_NAME, settings_values["kernel_size"], 31, nothing)

# ---------- Calibration ----------
def load_calibration(xml_path=CALIB_XML_PATH):
    global AFFINE_PARAMS
    
    if not os.path.isfile(xml_path):
        print(f"⚠️ Calibration file {xml_path} does not exist.")
        return None

    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        print(f"⚠️ Could not open calibration file: {xml_path}")
        return None
    
    # Try to load the mm_per_px value
    mm_per_px = fs.getNode("mm_per_px").real()
    
    if mm_per_px is not None:
        # Create a simple affine matrix that converts pixels to mm
        AFFINE_PARAMS = np.array([
            [mm_per_px, 0, 0],
            [0, mm_per_px, 0],
            [0, 0, 1]
        ], dtype=np.float32)
        print(f"✅ Calibration loaded from XML. mm_per_px: {mm_per_px}")
        return AFFINE_PARAMS
    
    # If mm_per_px not found, try to load the new format
    affine_matrix = fs.getNode("affine_matrix").mat()
    
    # If new format not found, try old format
    if affine_matrix is None:
        params = fs.getNode("affine_parameters").mat()
        if params is None or params.size == 0:
            print("⚠️ No calibration data found in XML.")
            fs.release()
            return None
        
        # Handle old format (3, 2) matrix
        if params.shape == (3, 2):
            # Convert old format to new format (3, 3)
            affine_matrix = np.eye(3, dtype=np.float32)
            affine_matrix[0:2, :] = params
            print("✅ Converted old calibration format to new format.")
        else:
            print(f"⚠️ Unexpected calibration data shape {params.shape}.")
            fs.release()
            return None
    
    fs.release()
    
    if affine_matrix is None or affine_matrix.size == 0:
        print("⚠️ Calibration matrix not found or empty in calibration XML.")
        return None

    if affine_matrix.shape != (3, 3):
        print(f"⚠️ Unexpected affine_matrix shape {affine_matrix.shape}, expected (3,3).")
        return None

    AFFINE_PARAMS = affine_matrix
    print("✅ Calibration loaded from XML.")
    return AFFINE_PARAMS

def save_calibration(affine_matrix, xml_path=CALIB_XML_PATH):
    fs = cv2.FileStorage(xml_path, cv2.FILE_STORAGE_WRITE)
    fs.write("affine_matrix", affine_matrix)
    fs.release()
    print(f"💾 Calibration saved to {xml_path}")

def pixels_to_microns(points_xy, affine_matrix):
    points_xy = np.asarray(points_xy, dtype=np.float32)
    if points_xy.ndim == 1:
        points_xy = points_xy.reshape(1, -1)
    
    # Convert to homogeneous coordinates
    ones = np.ones((points_xy.shape[0], 1), dtype=np.float32)
    points_homogeneous = np.hstack([points_xy, ones])
    
    # Apply affine transformation
    mic = points_homogeneous @ affine_matrix[:2, :].T
    
    return mic

# ---------- UI helpers ----------
def nothing(x): pass
def ensure_odd(n): return n if n % 2 == 1 else max(1, n-1)

def draw_tabs(canvas):
    """Draw the tab navigation at the top of the window"""
    tab_width = CANVAS_WIDTH // len(TAB_NAMES)
    
    for i, name in enumerate(TAB_NAMES):
        x_start = i * tab_width
        x_end = (i + 1) * tab_width
        
        # Draw tab background
        color = COLOR_TAB_ACTIVE if i == current_tab else COLOR_TAB_INACTIVE
        cv2.rectangle(canvas, (x_start, 0), (x_end, 40), color, -1)
        cv2.rectangle(canvas, (x_start, 0), (x_end, 40), COLOR_TEXT, 1)
        
        # Draw tab text
        text_size = cv2.getTextSize(name, FONT, 0.7, 2)[0]
        text_x = x_start + (tab_width - text_size[0]) // 2
        text_y = 25
        cv2.putText(canvas, name, (text_x, text_y), FONT, 0.7, COLOR_TEXT, 2)

def draw_view_selector(canvas):
    """Draw the view selector below the tabs"""
    view_width = CANVAS_WIDTH // len(VIEW_NAMES)
    view_y = 45  # Below tabs
    
    for i, name in enumerate(VIEW_NAMES):
        x_start = i * view_width
        x_end = (i + 1) * view_width
        
        # Draw view background
        color = COLOR_VIEW_SELECTOR if i == current_view else COLOR_TAB_INACTIVE
        cv2.rectangle(canvas, (x_start, view_y), (x_end, view_y + 30), color, -1)
        cv2.rectangle(canvas, (x_start, view_y), (x_end, view_y + 30), COLOR_TEXT, 1)
        
        # Draw view text
        text_size = cv2.getTextSize(name, FONT, 0.5, 1)[0]
        text_x = x_start + (view_width - text_size[0]) // 2
        text_y_pos = view_y + 20
        cv2.putText(canvas, name, (text_x, text_y_pos), FONT, 0.5, COLOR_TEXT, 1)

def draw_buttons_and_text(img):
    # Draw a sober, simple UI panel for buttons and instructions below the image and trackbars
    height, width = img.shape[:2]
    panel_top = FRAME_HEIGHT + TRACKBAR_HEIGHT + WINDOW_MARGIN * 2 + 40 + 30  # Added space for tabs and view selector
    panel_bottom = panel_top + BUTTONS_HEIGHT + WINDOW_MARGIN
    cv2.rectangle(img, (0, panel_top), (width, panel_bottom), COLOR_BG, thickness=-1)

    keys_text = "[ESC]=Quit  [S]=Save  [R]=Reset kernel  [I]=Invert  [C]=Reload XML  [L]=Calibrate  [+/-]=Adjust mm  [M]=Toggle mm/px  [TAB]=Switch tabs  [V]=Switch views"
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

def draw_settings_tab(canvas):
    """Draw the settings tab content"""
    # Draw settings background
    settings_bg_top = 40 + 30  # Below tabs and view selector
    settings_bg_bottom = CANVAS_HEIGHT
    cv2.rectangle(canvas, (0, settings_bg_top), (CANVAS_WIDTH, settings_bg_bottom), COLOR_BG, -1)
    
    # Draw settings title
    cv2.putText(canvas, "Settings", (WINDOW_MARGIN, settings_bg_top + 40), 
                FONT, 1.2, COLOR_TEXT, 2)
    
    # Draw settings options
    y_pos = settings_bg_top + 100
    settings_list = [
        f"Threshold Low: {settings_values['threshold_low']}",
        f"Threshold High: {settings_values['threshold_high']}",
        f"Kernel Size: {settings_values['kernel_size']}",
        f"Min Area: {settings_values['min_area']}",
        f"ROI Width: {settings_values['roi_width']}",
        f"ROI Height: {settings_values['roi_height']}",
        f"MM Correction: {settings_values['mm_correction']:.3f}",
        f"Show in MM: {'Yes' if settings_values['show_in_mm'] else 'No'}",
        f"Current View: {VIEW_NAMES[settings_values['current_view']]}"
    ]
    
    for i, setting in enumerate(settings_list):
        cv2.putText(canvas, setting, (WINDOW_MARGIN, y_pos + i * 40), 
                    FONT, 0.8, COLOR_TEXT, 1)
    
    # Draw instructions
    instructions = "Press 'A' to apply settings or 'ESC' to go back"
    cv2.putText(canvas, instructions, (WINDOW_MARGIN, settings_bg_top + 400), 
                FONT, 0.7, COLOR_TEXT, 1)

def draw_calibration_tab(canvas):
    """Draw the calibration tab content"""
    # Draw calibration background
    calib_bg_top = 40 + 30  # Below tabs and view selector
    calib_bg_bottom = CANVAS_HEIGHT
    cv2.rectangle(canvas, (0, calib_bg_top), (CANVAS_WIDTH, calib_bg_bottom), COLOR_BG, -1)
    
    # Draw calibration title
    cv2.putText(canvas, "Calibration", (WINDOW_MARGIN, calib_bg_top + 40), 
                FONT, 1.2, COLOR_TEXT, 2)
    
    # Draw calibration status
    if AFFINE_PARAMS is not None:
        status_text = "✅ Calibration loaded successfully"
        status_color = COLOR_CALIB_INSTRUCTION
    else:
        status_text = "⚠️ No calibration data found"
        status_color = COLOR_ERROR
    
    cv2.putText(canvas, status_text, (WINDOW_MARGIN, calib_bg_top + 100), 
                FONT, 0.8, status_color, 1)
    
    # Draw calibration instructions
    instructions = [
        "Press 'L' to start calibration mode",
        "Click on grid points in the image",
        "Use mouse wheel to zoom in/out",
        "Press 'L' again when done or 'X' to cancel"
    ]
    
    for i, instruction in enumerate(instructions):
        cv2.putText(canvas, instruction, (WINDOW_MARGIN, calib_bg_top + 160 + i * 40), 
                    FONT, 0.7, COLOR_TEXT, 1)
    
    # Draw calibration details if available
    if AFFINE_PARAMS is not None:
        details = [
            f"MM per Pixel: {AFFINE_PARAMS[0, 0]:.6f}",
            f"Correction Factor: {MM_CORRECTION_FACTOR:.3f}"
        ]
        
        for i, detail in enumerate(details):
            cv2.putText(canvas, detail, (WINDOW_MARGIN, calib_bg_top + 320 + i * 40), 
                        FONT, 0.7, COLOR_MM_CORRECTION, 1)

# ---------- Text input handling ----------
def handle_keypress(key):
    global text_input_active, current_textbox, textbox_values, error_message, error_message_time
    
    if not text_input_active:
        return False
    
    # ESC to cancel text input
    if key == 27:
        text_input_active = False
        save_mode = False
        error_message = "Save cancelled"
        error_message_time = cv2.getTickCount()
        return True
    
    # Tab to move to next textbox
    if key == 9:  # Tab key
        current_textbox = (current_textbox + 1) % 3
        return True
    
    # Enter to confirm or move to next textbox
    if key == 13:  # Enter key
        if current_textbox < 2:
            current_textbox += 1
        else:
            # Try to save if all textboxes are filled
            if validate_textboxes():
                save_with_textbox_data()
                text_input_active = False
                save_mode = False
            else:
                error_message = "Please fill all fields correctly"
                error_message_time = cv2.getTickCount()
        return True
    
    # Backspace to delete character
    if key == 8:  # Backspace
        if len(textbox_values[current_textbox]) > 0:
            textbox_values[current_textbox] = textbox_values[current_textbox][:-1]
        return True
    
    # Regular character input
    if 32 <= key <= 126:
        char = chr(key)
        
        # Validate input based on textbox type
        if current_textbox in [0, 1]:  # Numerical textboxes
            if char.isdigit() and len(textbox_values[current_textbox]) < 4:
                textbox_values[current_textbox] += char
        else:  # Alphabetical textbox
            if char.isalpha() and len(textbox_values[current_textbox]) < 2:
                textbox_values[current_textbox] += char.upper()
        
        return True
    
    return False

def validate_textboxes():
    # Check if all textboxes have at least one character
    if len(textbox_values[0]) < 1:
        return False
    if len(textbox_values[1]) < 1:
        return False
    if len(textbox_values[2]) < 1:
        return False
    return True

def draw_textboxes(canvas):
    global error_message, error_message_time
    
    # Draw background for textboxes
    textbox_y = FRAME_HEIGHT + TRACKBAR_HEIGHT + WINDOW_MARGIN * 2 + 40 + 30 + 40  # Added space for tabs and view selector
    cv2.rectangle(canvas, (WINDOW_MARGIN, textbox_y), 
                 (CANVAS_WIDTH - WINDOW_MARGIN, textbox_y + 80), 
                 COLOR_BG, -1)
    
    # Draw textbox labels
    labels = ["Lot Number", "Serial Number", "Tag"]
    
    # Calculate positions for horizontal layout
    box_width = 150
    box_spacing = 20
    total_width = 3 * box_width + 2 * box_spacing
    start_x = (CANVAS_WIDTH - total_width) // 2
    
    for i in range(3):
        label_y = textbox_y + 20
        box_y = textbox_y + 30
        
        # Draw label
        cv2.putText(canvas, labels[i], (start_x + i*(box_width + box_spacing), label_y),
                    FONT, 0.5, COLOR_TEXT, 1, cv2.LINE_AA)
        
        # Draw textbox
        box_color = COLOR_ACCENT if current_textbox == i else COLOR_TEXTBOX_BORDER
        cv2.rectangle(canvas, (start_x + i*(box_width + box_spacing), box_y),
                     (start_x + i*(box_width + box_spacing) + box_width, box_y + 30),
                     box_color, 2)
        cv2.rectangle(canvas, (start_x + i*(box_width + box_spacing), box_y),
                     (start_x + i*(box_width + box_spacing) + box_width, box_y + 30),
                     COLOR_TEXTBOX_BG, -1)
        
        # Draw text
        cv2.putText(canvas, textbox_values[i], (start_x + i*(box_width + box_spacing) + 10, box_y + 20),
                    FONT, 0.6, COLOR_TEXTBOX_TEXT, 1, cv2.LINE_AA)
    
    # Draw instructions
    instructions = "Press TAB to move between fields, ENTER to confirm, ESC to cancel"
    cv2.putText(canvas, instructions, (WINDOW_MARGIN + 10, textbox_y + 70),
                FONT, 0.5, COLOR_TEXT, 1, cv2.LINE_AA)
    
    # Draw error message if any (with timeout)
    if error_message and (cv2.getTickCount() - error_message_time) / cv2.getTickFrequency() < 3:
        cv2.putText(canvas, error_message, (WINDOW_MARGIN + 10, textbox_y + 90),
                    FONT, 0.5, COLOR_ERROR, 1, cv2.LINE_AA)

# ---------- Frame normalization ----------
def normalize_frame_to_bgr(img):
    if img is None:
        raise ValueError("Received None image")
    img = np.asarray(img)
    if img.dtype != np.uint8:
        if np.issubdtype(img.dtype, np.floating):
            img = np.clip(img * 255.0, 0, 255).ast(np.uint8)
        else:
            img = np.clip(img, 0, 255).ast(np.uint8)
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

# ---------- Zoom functionality ----------
def apply_zoom(img, zoom_factor, center):
    if zoom_factor == 1.0:
        return img
    
    h, w = img.shape[:2]
    
    # Calculate the region to zoom
    new_w = int(w / zoom_factor)
    new_h = int(h / zoom_factor)
    
    x1 = max(0, center[0] - new_w // 2)
    y1 = max(0, center[1] - new_h // 2)
    x2 = min(w, x1 + new_w)
    y2 = min(h, y1 + new_h)
    
    # If we're at the edge, adjust the other side
    if x2 == w:
        x1 = w - new_w
    if y2 == h:
        y1 = h - new_h
    
    # Crop and resize
    zoomed = img[y1:y2, x1:x2]
    zoomed = cv2.resize(zoomed, (w, h))
    
    return zoomed

# ---------- Calibration mouse callback ----------
def calibration_mouse_callback(event, x, y, flags, param):
    global calib_points_img, calib_points_real, calib_clicks_img
    global calibration_mode, calib_zoom_factor, calib_zoom_center, calib_step

    if not calibration_mode or calib_step != 0:
        return

    # Convert mouse (x,y) to image coordinates relative to image origin on canvas
    img_x = x - mouse_img_offset_x
    img_y = y - mouse_img_offset_y

    # Check if click inside image area
    if img_x < 0 or img_x >= FRAME_WIDTH or img_y < 0 or img_y >= FRAME_HEIGHT:
        return

    # Handle zoom with mouse wheel
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:  # Scroll up - zoom in
            calib_zoom_factor = min(8.0, calib_zoom_factor * 1.2)
        else:  # Scroll down - zoom out
            calib_zoom_factor = max(1.0, calib_zoom_factor / 1.2)
        calib_zoom_center = (img_x, img_y)
        print(f"🔍 Zoom: {calib_zoom_factor:.1f}x")
        return

    # Handle point selection with left click
    if event == cv2.EVENT_LBUTTONDOWN and calib_step == 0:
        # Apply inverse zoom transformation to get original coordinates
        if calib_zoom_factor > 1.0:
            h, w = calib_clicks_img.shape[:2]
            new_w = int(w / calib_zoom_factor)
            new_h = int(h / calib_zoom_factor)
            
            x1 = max(0, calib_zoom_center[0] - new_w // 2)
            y1 = max(0, calib_zoom_center[1] - new_h // 2)
            
            orig_x = int(x1 + img_x / calib_zoom_factor)
            orig_y = int(y1 + img_y / calib_zoom_factor)
        else:
            orig_x, orig_y = img_x, img_y
            
        calib_points_img.append((orig_x, orig_y))
        
        # Draw the point on the image
        cv2.circle(calib_clicks_img, (orig_x, orig_y), 7, COLOR_CALIB_POINT, -1)
        cv2.putText(calib_clicks_img, f"P{len(calib_points_img)}", (orig_x + 10, orig_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_POINT, 2)
        print(f"🖱️ Calibration point {len(calib_points_img)}: {orig_x},{orig_y}")
        
        # Check if we've reached the maximum number of points
        if len(calib_points_img) >= max_calib_points:
            calib_step = 1
            print("✅ Maximum calibration points reached.")
            print("   Press 'L' again to enter grid information.")

def compute_and_save_calibration():
    global AFFINE_PARAMS, calib_points_img, calib_points_real, calibration_mode, calib_step
    global grid_width, grid_height, grid_spacing
    
    if len(calib_points_img) < 4:
        print("❌ Calibration failed: Need at least 4 points for grid calibration.")
        return
    
    if len(calib_points_img) != len(calib_points_real):
        print("❌ Calibration failed: Mismatch between image points and real points.")
        return
    
    # Convert to numpy arrays
    pts_img = np.array(calib_points_img, dtype=np.float32)
    pts_real = np.array(calib_points_real, dtype=np.float32)
    
    # Calculate affine transformation using least squares
    # We need to solve for the transformation matrix M in: real = M * img
    # Using homogeneous coordinates: [x_real, y_real] = M * [x_img, y_img, 1]
    
    # Add homogeneous coordinate to image points
    ones = np.ones((pts_img.shape[0], 1))
    pts_img_homogeneous = np.hstack([pts_img, ones])
    
    # Solve for transformation matrix using least squares
    M, residuals, rank, s = np.linalg.lstsq(pts_img_homogeneous, pts_real, rcond=None)
    
    # Convert to 3x3 affine matrix
    affine_matrix = np.vstack([M.T, [0, 0, 1]])
    
    AFFINE_PARAMS = affine_matrix
    save_calibration(AFFINE_PARAMS)
    calibration_mode = False
    calib_step = 0
    print(f"🎉 Grid calibration complete. Resuming normal operations.")
    if len(residuals) > 0:
        print(f"   Residual error: {np.mean(residuals):.6f}")
    
    # Show calibration results
    print("📊 Calibration Results:")
    print(f"   Number of points used: {len(calib_points_img)}")
    print(f"   Transformation matrix:")
    for i, row in enumerate(affine_matrix):
        print(f"   [{row[0]:.6f}, {row[1]:.6f}, {row[2]:.6f}]")

# ---------- Processing ----------
def process_frame(frame_bgr):
    global last_output, AFFINE_PARAMS, INVERT_BINARY, MM_CORRECTION_FACTOR, SHOW_IN_MM

    h, w = frame_bgr.shape[:2]

    roi_w = min(settings_values["roi_width"], w)
    roi_h = min(settings_values["roi_height"], h)
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

    # Display mm correction factor and unit toggle on the output image
    if AFFINE_PARAMS is not None:
        correction_text = f"Correction: {MM_CORRECTION_FACTOR:.3f}x"
        cv2.putText(output, correction_text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_MM_CORRECTION, 2)
        
        # Draw checkbox for mm/px toggle
        checkbox_text = "Show in mm"
        checkbox_x = 20
        checkbox_y = 80
        cv2.putText(output, checkbox_text, (checkbox_x + 30, checkbox_y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_TEXT, 1)
        
        # Draw checkbox
        if SHOW_IN_MM:
            cv2.rectangle(output, (checkbox_x, checkbox_y), 
                         (checkbox_x + 20, checkbox_y + 20), COLOR_CHECKBOX, -1)
        cv2.rectangle(output, (checkbox_x, checkbox_y), 
                     (checkbox_x + 20, checkbox_y + 20), COLOR_TEXT, 1)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < settings_values["min_area"]:
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

            if AFFINE_PARAMS is not None and SHOW_IN_MM:
                # Apply affine transformation to both points
                point1 = np.array([x1_full, y1_full, 1])
                point2 = np.array([x2_full, y2_full, 1])
                
                # Transform using the affine matrix
                X1 = np.dot(AFFINE_PARAMS[0, :], point1)
                Y1 = np.dot(AFFINE_PARAMS[1, :], point1)
                X2 = np.dot(AFFINE_PARAMS[0, :], point2)
                Y2 = np.dot(AFFINE_PARAMS[1, :], point2)
                
                # Calculate length in mm and apply correction factor
                length_mm = float(np.hypot(X2 - X1, Y2 - Y1)) * MM_CORRECTION_FACTOR
                label = f"{length_mm:.3f} mm"
            else:
                length_px = math.hypot(x2 - x1, y2 - y1)
                label = f"{length_px:.1f} px"

            mid_x, mid_y = int((x1_full + x2_full) * 0.5), int((y1_full + y2_full) * 0.5)
            cv2.putText(output, label, (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Resize the output to match the expected frame size
    output = cv2.resize(output, (FRAME_WIDTH, FRAME_HEIGHT))
    
    border_size = 5
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_bgr = cv2.copyMakeBorder(mask_bgr, border_size, border_size, border_size, border_size,
                                  cv2.BORDER_CONSTANT, value=(0, 0, 0))
    frame_bgr_border = cv2.copyMakeBorder(frame_bgr, border_size, border_size, border_size, border_size,
                                          cv2.BORDER_CONSTANT, value=(0, 0, 0))
    output_border = cv2.copyMakeBorder(output, border_size, border_size, border_size, border_size,
                                       cv2.BORDER_CONSTANT, value=(0, 0, 0))

    try:
        # Resize all components to ensure they match in height
        frame_bgr_border = cv2.resize(frame_bgr_border, (FRAME_WIDTH, FRAME_HEIGHT))
        mask_bgr = cv2.resize(mask_bgr, (FRAME_WIDTH, FRAME_HEIGHT))
        output_border = cv2.resize(output_border, (FRAME_WIDTH, FRAME_HEIGHT))
        
        stacked = np.hstack((frame_bgr_border, mask_bgr, output_border))
    except Exception as e:
        print(f"⚠️ Error stacking images: {e}")
        stacked = output_border
    
    # Ensure the stacked image is the correct size
    stacked = cv2.resize(stacked, (FRAME_WIDTH, FRAME_HEIGHT))
    
    last_output = output.copy()
    
    # Return all three views plus the stacked view
    return {
        "original": frame_bgr_border,
        "mask": mask_bgr,
        "processed": output_border,
        "all": stacked
    }

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

def save_with_textbox_data():
    global last_output, textbox_values
    if last_output is None:
        print("⚠️ No processed frame to save yet.")
        return None
    
    # Create filename with textbox data
    num1, num2, alpha = textbox_values
    base_name = f"{num1}-{num2}-{alpha}"
    
    # Check if file already exists and find a new name if needed
    counter = 0
    fname = f"{base_name}.png"
    
    while os.path.exists(fname):
        counter += 1
        fname = f"{base_name}_{counter}.png"
    
    cv2.imwrite(fname, last_output)
    print(f"💾 Saved: {fname}")
    
    # Reset textbox values
    textbox_values = ["", "", ""]
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
    global AFFINE_PARAMS, INVERT_BINARY, calibration_mode, calib_clicks_img
    global calib_points_img, calib_points_real, calib_zoom_factor, calib_zoom_center, calib_step
    global grid_width, grid_height, grid_spacing, max_calib_points
    global save_mode, text_input_active, current_textbox, textbox_values, error_message, error_message_time
    global MM_CORRECTION_FACTOR, SHOW_IN_MM, current_tab, settings_values, current_view

    # Load settings first (including MM correction factor)
    load_settings()
    
    # Load calibration
    AFFINE_PARAMS = load_calibration(CALIB_XML_PATH)
    if AFFINE_PARAMS is None:
        print("⚠️ No calibration data found. Press 'L' to start calibration.")

    setup_window()
    cv2.setMouseCallback(WINDOW_NAME, calibration_mouse_callback)

    try:
        with VmbSystem.get_instance() as vmb:
            cam = choose_camera_auto(vmb)
            if cam is None:
                # Save settings before exiting
                save_settings()
                return

            with cam:
                print("🎥 Camera opened. Starting stream... (press ESC to quit)")
                print("   Keys: [ESC]=Quit  [S]=Save  [R]=Reset kernel  [I]=Invert  [C]=Reload XML  [L]=Calibrate  [+/-]=Adjust mm  [M]=Toggle mm/px  [TAB]=Switch tabs  [V]=Switch views")

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
                        # Save settings before breaking
                        save_settings()
                        break

                    img_bgr = cv2.resize(img_bgr, (FRAME_WIDTH, FRAME_HEIGHT))

                    # Prepare canvas with fixed size
                    canvas = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
                    canvas[:] = COLOR_BG
                    
                    # Draw tabs at the top
                    draw_tabs(canvas)
                    
                    # Draw view selector below tabs (only in Live View tab)
                    if current_tab == 0:
                        draw_view_selector(canvas)

                    if current_tab == 0:  # Live View tab
                        if calibration_mode:
                            if calib_clicks_img is None:
                                calib_clicks_img = img_bgr.copy()
                            
                            # Apply zoom if needed
                            display_img = apply_zoom(calib_clicks_img, calib_zoom_factor, calib_zoom_center)
                            
                            # Draw instructions on the image
                            if calib_step == 0:
                                instruction1 = "Click on grid points (use mouse wheel to zoom)"
                                instruction2 = f"Points: {len(calib_points_img)}/{max_calib_points} (4 min, more=better)"
                                instruction3 = "Press 'L' when done or 'X' to cancel"
                                
                                cv2.putText(display_img, instruction1, (20, 40), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_INSTRUCTION, 2)
                                cv2.putText(display_img, instruction2, (20, 80), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_INSTRUCTION, 2)
                                cv2.putText(display_img, instruction3, (20, 120), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_INSTRUCTION, 2)
                            elif calib_step == 1:
                                instruction1 = "Press 'L' to enter grid information"
                                instruction2 = "or 'X' to cancel calibration"
                                
                                cv2.putText(display_img, instruction1, (20, 40), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_CONFIRM, 2)
                                cv2.putText(display_img, instruction2, (20, 80), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CALIB_CONFINM, 2)
                            
                            # Display zoom level
                            if calib_zoom_factor > 1.0:
                                cv2.putText(display_img, f"Zoom: {calib_zoom_factor:.1f}x", 
                                           (FRAME_WIDTH - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                           0.7, COLOR_CALIB_POINT, 2)
                            
                            # Place the image on the canvas
                            canvas[WINDOW_MARGIN + 40 + 30:WINDOW_MARGIN+FRAME_HEIGHT + 40 + 30, 
                                   WINDOW_MARGIN:WINDOW_MARGIN+FRAME_WIDTH] = display_img
                            
                        elif save_mode and text_input_active:
                            # Process the frame normally
                            processed_views = process_frame(img_bgr)
                            selected_view = processed_views["all"] if current_view == 3 else processed_views[list(processed_views.keys())[current_view]]
                            
                            # Place the processed image on the canvas
                            canvas[WINDOW_MARGIN + 40 + 30:WINDOW_MARGIN+FRAME_HEIGHT + 40 + 30, 
                                   WINDOW_MARGIN:WINDOW_MARGIN+FRAME_WIDTH] = selected_view
                            
                            # Draw textboxes
                            draw_textboxes(canvas)
                            
                        else:
                            # Normal processing mode
                            processed_views = process_frame(img_bgr)
                            
                            # Select the appropriate view based on current_view
                            if current_view == 3:  # All views
                                selected_view = processed_views["all"]
                            else:
                                view_keys = list(processed_views.keys())
                                selected_view = processed_views[view_keys[current_view]]
                            
                            # Place the selected view on the canvas
                            canvas[WINDOW_MARGIN + 40 + 30:WINDOW_MARGIN+FRAME_HEIGHT + 40 + 30, 
                                   WINDOW_MARGIN:WINDOW_MARGIN+FRAME_WIDTH] = selected_view
                        
                        # Draw UI elements (buttons, trackbars, etc.)
                        draw_buttons_and_text(canvas)
                    
                    elif current_tab == 1:  # Settings tab
                        draw_settings_tab(canvas)
                    
                    elif current_tab == 2:  # Calibration tab
                        draw_calibration_tab(canvas)
                    
                    # Display the canvas
                    cv2.imshow(WINDOW_NAME, canvas)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    
                    # Tab navigation
                    if key == 9:  # TAB key
                        current_tab = (current_tab + 1) % len(TAB_NAMES)
                        print(f"📑 Switched to tab: {TAB_NAMES[current_tab]}")
                        continue
                    
                    # View navigation (only in Live View tab)
                    if key == ord('v') and current_tab == 0:
                        current_view = (current_view + 1) % len(VIEW_NAMES)
                        settings_values["current_view"] = current_view
                        print(f"👁️ Switched to view: {VIEW_NAMES[current_view]}")
                        continue
                    
                    if key == 27:  # ESC
                        if current_tab != 0:  # If not in Live View tab, go back
                            current_tab = 0
                            print("📑 Switched to Live View tab")
                        elif calibration_mode:
                            print("❌ Calibration cancelled.")
                            calibration_mode = False
                            calib_clicks_img = None
                            calib_points_img = []
                            calib_points_real = []
                            calib_zoom_factor = 1.0
                            calib_zoom_center = (FRAME_WIDTH // 2, FRAME_HEIGHT // 2)
                            calib_step = 0
                        elif save_mode and text_input_active:
                            text_input_active = False
                            save_mode = False
                            error_message = "Save cancelled"
                            error_message_time = cv2.getTickCount()
                        else:
                            print("👋 Exiting...")
                            # Save settings before exiting
                            save_settings()
                            break
                    
                    # Handle keypress for text input
                    if handle_keypress(key):
                        continue
                    
                    # Handle other keys
                    if key == ord('s') and not calibration_mode and current_tab == 0:
                        if not save_mode:
                            save_mode = True
                            text_input_active = True
                            current_textbox = 0
                            error_message = ""
                            print("💾 Entering save mode. Fill in the textboxes and press Enter to save.")
                        else:
                            print("⚠️ Already in save mode.")
                    
                    elif key == ord('r') and current_tab == 0:
                        cv2.setTrackbarPos("Kernel Size", WINDOW_NAME, 5)
                        print("🔄 Reset kernel size to 5")
                    
                    elif key == ord('i') and current_tab == 0:
                        INVERT_BINARY = not INVERT_BINARY
                        print(f"🔄 Invert binary: {INVERT_BINARY}")
                    
                    elif key == ord('c') and current_tab == 0:
                        AFFINE_PARAMS = load_calibration(CALIB_XML_PATH)
                        if AFFINE_PARAMS is not None:
                            print("🔄 Reloaded calibration from XML")
                        else:
                            print("⚠️ Failed to reload calibration")
                    
                    elif key == ord('l') and current_tab == 0:
                        if not calibration_mode:
                            calibration_mode = True
                            calib_clicks_img = img_bgr.copy()
                            calib_points_img = []
                            calib_points_real = []
                            calib_zoom_factor = 1.0
                            calib_zoom_center = (FRAME_WIDTH // 2, FRAME_HEIGHT // 2)
                            calib_step = 0
                            print("🎯 Starting calibration mode. Click on grid points.")
                        else:
                            if calib_step == 0:
                                if len(calib_points_img) >= 4:
                                    calib_step = 1
                                    print("✅ Calibration points collected.")
                                    print("   Press 'L' again to enter grid information.")
                                else:
                                    print("❌ Need at least 4 points for calibration.")
                            elif calib_step == 1:
                                # Enter grid information
                                grid_width = 3  # Example values, you should implement proper input
                                grid_height = 3
                                grid_spacing = 10.0  # mm
                                
                                # Generate real coordinates based on grid
                                calib_points_real = []
                                for i in range(grid_height):
                                    for j in range(grid_width):
                                        if len(calib_points_real) < len(calib_points_img):
                                            x = j * grid_spacing
                                            y = i * grid_spacing
                                            calib_points_real.append((x, y))
                                
                                print(f"📊 Grid: {grid_width}x{grid_height}, spacing: {grid_spacing}mm")
                                print("   Generated real coordinates for calibration points.")
                                
                                # Compute and save calibration
                                compute_and_save_calibration()
                    
                    elif (key == ord('+') or key == ord('=')) and current_tab == 0:
                        MM_CORRECTION_FACTOR += 0.01
                        print(f"📏 MM Correction factor: {MM_CORRECTION_FACTOR:.3f}")
                        # Auto-save the correction factor
                        save_settings()
                    
                    elif (key == ord('-') or key == ord('_')) and current_tab == 0:
                        MM_CORRECTION_FACTOR = max(0.01, MM_CORRECTION_FACTOR - 0.01)
                        print(f"📏 MM Correction factor: {MM_CORRECTION_FACTOR:.3f}")
                        # Auto-save the correction factor
                        save_settings()
                    
                    elif key == ord('m') and current_tab == 0:
                        SHOW_IN_MM = not SHOW_IN_MM
                        unit = "mm" if SHOW_IN_MM else "pixels"
                        print(f"📐 Displaying measurements in {unit}")
                        # Auto-save the setting
                        save_settings()
                    
                    elif key == ord('a') and current_tab == 1:  # Apply settings
                        # Update settings from trackbars
                        settings_values["threshold_low"] = cv2.getTrackbarPos("Thresh Low", WINDOW_NAME)
                        settings_values["threshold_high"] = cv2.getTrackbarPos("Thresh High", WINDOW_NAME)
                        settings_values["kernel_size"] = cv2.getTrackbarPos("Kernel Size", WINDOW_NAME)
                        settings_values["mm_correction"] = MM_CORRECTION_FACTOR
                        settings_values["show_in_mm"] = SHOW_IN_MM
                        settings_values["current_view"] = current_view
                        
                        print("✅ Settings applied")
                        # Save settings
                        save_settings()
                        current_tab = 0  # Switch back to Live View
                        print("📑 Switched to Live View tab")

    except KeyboardInterrupt:
        print("👋 Interrupted by user.")
        # Save settings before exiting
        save_settings()
    except Exception as e:
        print("❌ Error:", e)
        import traceback
        traceback.print_exc()
        # Save settings before exiting
        save_settings()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()