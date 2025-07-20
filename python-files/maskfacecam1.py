import cv2
import numpy as np
from PIL import Image
import os
import time
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import sys
import math

# --- Helper function to handle resource paths for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- MediaPipe Setup (Constants) ---
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# --- Landmark indices for stable mask placement ---
STABLE_LANDMARK_IDS = {
    "LEFT_CHEEK": 234, "RIGHT_CHEEK": 454, "NOSE_TIP": 1,
    "FOREHEAD": 10, "CHIN": 152
}

# --- Global Settings Dictionary ---
APP_SETTINGS = {
    "mask_path": None, "camera_index": None,
    "smoothing_factor": 0.5, "detection_confidence": 0.5
}

def get_available_cameras():
    available_cameras = []
    for i in range(10):
        cap_test = cv2.VideoCapture(i)
        if cap_test.isOpened():
            available_cameras.append(str(i)); cap_test.release()
        else:
            cap_test.release();
            if i > 0 and len(available_cameras) > 0: break
            elif i > 0 and not available_cameras: break
    return available_cameras

def select_mask_file():
    path = filedialog.askopenfilename(
        title="Select your transparent PNG mask file",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if path:
        APP_SETTINGS["mask_path"] = path
        mask_label.config(text=f"Mask: {os.path.basename(path)}")
        print(f"Selected Mask File: {path}")

def start_preview(setup_window):
    camera_str = camera_combobox.get()
    if camera_str: APP_SETTINGS["camera_index"] = int(camera_str)
    else: messagebox.showwarning("Selection Error", "Please select a camera."); return

    if not APP_SETTINGS["mask_path"]:
        messagebox.showwarning("Selection Error", "Please select a mask image file."); return
        
    smoothing_gui_val = smoothness_slider.get()
    APP_SETTINGS["smoothing_factor"] = 1.0 - (smoothing_gui_val / 100.0) * 0.95
    
    sensitivity = sensitivity_combobox.get()
    APP_SETTINGS["detection_confidence"] = 0.35 if "High" in sensitivity else 0.5

    print("--- Starting with Settings ---")
    print(f"Camera Index: {APP_SETTINGS['camera_index']}")
    print(f"Mask Path: {APP_SETTINGS['mask_path']}")
    print(f"Smoothing Factor (Alpha): {APP_SETTINGS['smoothing_factor']:.2f}")
    print(f"Min Detection Confidence: {APP_SETTINGS['detection_confidence']}")
    print("-----------------------------")
    setup_window.destroy()

def setup_gui_screen():
    global mask_label, camera_combobox, smoothness_slider, sensitivity_combobox
    setup_window = tk.Tk()
    setup_window.title("Face Mask Setup")
    setup_window.geometry("450x400")
    setup_window.resizable(False, False)

    # --- Set Window Icon ---
    # This will use the bundled icon when run as an EXE
    try:
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        setup_window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load window icon: {e}")
        
    screen_width, screen_height = setup_window.winfo_screenwidth(), setup_window.winfo_screenheight()
    x, y = (screen_width/2)-(450/2), (screen_height/2)-(400/2)
    setup_window.geometry(f'+{int(x)}+{int(y)}')

    main_frame = ttk.Frame(setup_window, padding="20")
    main_frame.pack(expand=True, fill="both")

    ttk.Label(main_frame, text="1. Choose Mask Image:", font="-weight bold").pack(pady=(0, 5), anchor="w")
    mask_button = ttk.Button(main_frame, text="Select Mask File", command=select_mask_file)
    mask_button.pack(pady=(0, 5), fill='x')
    mask_label = ttk.Label(main_frame, text="Mask: No file selected")
    mask_label.pack(pady=(0, 15), anchor="w")

    ttk.Label(main_frame, text="2. Choose Camera:", font="-weight bold").pack(pady=(0, 5), anchor="w")
    available_cams = get_available_cameras()
    camera_combobox = ttk.Combobox(main_frame, values=available_cams, state="readonly" if available_cams else "disabled")
    if available_cams: camera_combobox.set(available_cams[0])
    else: ttk.Label(main_frame, text="No cameras found!").pack(pady=(0, 15), anchor="w")
    camera_combobox.pack(pady=(0, 15), fill='x')

    ttk.Label(main_frame, text="3. Detection Sensitivity:", font="-weight bold").pack(pady=(0, 5), anchor="w")
    sensitivity_combobox = ttk.Combobox(main_frame, values=["Normal (Recommended)", "High (For Distant Faces)"], state="readonly")
    sensitivity_combobox.set("Normal (Recommended)")
    sensitivity_combobox.pack(pady=(0, 15), fill='x')
    
    ttk.Label(main_frame, text="4. Mask Smoothness:", font="-weight bold").pack(pady=(0, 5), anchor="w")
    smoothness_frame = ttk.Frame(main_frame); smoothness_frame.pack(pady=(0, 5), fill='x')
    ttk.Label(smoothness_frame, text="Responsive").pack(side="left")
    ttk.Label(smoothness_frame, text="Super Smooth").pack(side="right")
    smoothness_slider = ttk.Scale(main_frame, from_=0, to=100, orient="horizontal")
    smoothness_slider.set(70) # Default: 1.0 - (0.7*0.95) = ~0.33 alpha
    smoothness_slider.pack(pady=(0, 15), fill='x')

    start_button = ttk.Button(main_frame, text="Start Preview", command=lambda: start_preview(setup_window))
    start_button.pack(pady=(10, 0))

    setup_window.protocol("WM_DELETE_WINDOW", sys.exit)
    setup_window.mainloop()
    return APP_SETTINGS["mask_path"] is not None

def overlay_transparent_image(background, overlay_pil, x, y, scale=1.0, angle=0.0):
    new_width, new_height = int(overlay_pil.width*scale), int(overlay_pil.height*scale)
    overlay_resized = overlay_pil.resize((new_width, new_height), Image.LANCZOS)
    overlay_rotated = overlay_resized.rotate(angle, expand=True, resample=Image.BICUBIC)
    overlay_cv = cv2.cvtColor(np.array(overlay_rotated), cv2.COLOR_RGBA2BGRA)

    h_overlay, w_overlay, _ = overlay_cv.shape
    x_tl, y_tl = x-w_overlay//2, y-h_overlay//2
    h_bg, w_bg, _ = background.shape
    y1_bg, y2_bg = max(0, y_tl), min(h_bg, y_tl+h_overlay)
    x1_bg, x2_bg = max(0, x_tl), min(w_bg, x_tl+w_overlay)
    y1_overlay, y2_overlay = max(0, -y_tl), min(h_overlay, h_bg-y_tl)
    x1_overlay, x2_overlay = max(0, -x_tl), min(w_overlay, w_bg-x_tl)

    if x1_bg >= x2_bg or y1_bg >= y2_bg or x1_overlay >= x2_overlay or y1_overlay >= y2_overlay: return background

    roi_bg = background[y1_bg:y2_bg, x1_bg:x2_bg]
    overlay_crop = overlay_cv[y1_overlay:y2_overlay, x1_overlay:x2_overlay]
    alpha_overlay = overlay_crop[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(3):
        roi_bg[:, :, c] = (alpha_overlay*overlay_crop[:, :, c] + alpha_background*roi_bg[:, :, c])
    background[y1_bg:y2_bg, x1_bg:x2_bg] = roi_bg
    return background

if __name__ == "__main__":
    if not setup_gui_screen():
        print("Setup cancelled or incomplete. Exiting application.")
        sys.exit()

    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=APP_SETTINGS["detection_confidence"],
        min_tracking_confidence=0.5)

    try: mask_img_pil = Image.open(APP_SETTINGS["mask_path"]).convert("RGBA")
    except Exception as e: messagebox.showerror("Error", f"Error loading mask image: {e}"); sys.exit()

    cap = cv2.VideoCapture(APP_SETTINGS["camera_index"])
    if not cap.isOpened():
        messagebox.showerror("Error", f"Could not open camera at index {APP_SETTINGS['camera_index']}."); sys.exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720); cap.set(cv2.CAP_PROP_FPS, 60)
    
    SMOOTHING_FACTOR = APP_SETTINGS["smoothing_factor"]
    smoothed_values = {"x": None, "y": None, "scale": None, "angle": None}

    while True:
        ret, frame = cap.read();
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            landmarks_px = {id_name: (int(landmarks[id_idx].x * w), int(landmarks[id_idx].y * h))
                            for id_name, id_idx in STABLE_LANDMARK_IDS.items()}
            
            p_left, p_right = landmarks_px["LEFT_CHEEK"], landmarks_px["RIGHT_CHEEK"]
            face_width = math.dist(p_left, p_right)
            
            current = {
                "x": landmarks_px["NOSE_TIP"][0],
                "y": int((landmarks_px["FOREHEAD"][1] + landmarks_px["CHIN"][1]) / 2.2),
                "scale": (face_width * 1.6) / mask_img_pil.width,
                "angle": -math.degrees(math.atan2(p_right[1]-p_left[1], p_right[0]-p_left[0]))
            }

            for key in smoothed_values:
                if smoothed_values[key] is None: smoothed_values[key] = current[key]
                else: smoothed_values[key] = (SMOOTHING_FACTOR * smoothed_values[key]) + ((1 - SMOOTHING_FACTOR) * current[key])

        if smoothed_values["x"] is not None:
             frame = overlay_transparent_image(frame, mask_img_pil, int(smoothed_values["x"]), int(smoothed_values["y"]),
                                               smoothed_values["scale"], smoothed_values["angle"])
       
        cv2.imshow('Face Mask Preview (Press Q to Quit)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release(); cv2.destroyAllWindows(); face_mesh.close()
    print("Application terminated successfully.")