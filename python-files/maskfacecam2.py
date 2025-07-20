import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import time
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import sys
import math
import json
from ttkthemes import ThemedTk
from pathlib import Path # NEW: Modern, cross-platform path handling

# --- Helper function to handle resource paths for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Main Application Class ---
class FaceMaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Developer Control Panel")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- NEW: Setup Application Data Folder in Documents ---
        self.APP_DATA_PATH = Path.home() / "Documents" / "FaceMaskDevEdition"
        try:
            self.APP_DATA_PATH.mkdir(parents=True, exist_ok=True)
            print(f"Application data will be stored in: {self.APP_DATA_PATH}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create application data folder in Documents: {e}")
            # Fallback to local directory if Documents is not accessible
            self.APP_DATA_PATH = Path(".")
        
        # --- Constants and Landmark Definitions ---
        self.STABLE_LANDMARK_IDS = {"LEFT_CHEEK": 234, "RIGHT_CHEEK": 454, "NOSE_TIP": 1, "FOREHEAD": 10, "CHIN": 152}
        self.DEFAULT_CONFIG_PATH = self.APP_DATA_PATH / "default_config.json"

        # --- State Variables ---
        self.is_paused = False
        self.is_mask_locked = False
        self.is_recording = False
        self.mask_img_pil = None
        self.cap = None
        self.video_writer = None
        
        # --- Smoothed value storage ---
        self.smoothed_values = {"x": None, "y": None, "scale": None, "angle": None}
        self.last_frame_time = time.time()
        self.fps = 0

        # --- Initialize MediaPipe ---
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # --- Create and layout GUI ---
        self._create_widgets()
        self._load_config(self.DEFAULT_CONFIG_PATH) # Load default settings on start

        # --- Start Camera and Main Loop ---
        self._initialize_camera()
        self._update_preview_feed()

    def _create_widgets(self):
        """Creates all GUI elements for the control panel."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")

        # --- Control Variables ---
        self.scale_var = tk.DoubleVar(value=1.0)
        self.x_offset_var = tk.DoubleVar(value=0)
        self.y_offset_var = tk.DoubleVar(value=0)
        self.angle_offset_var = tk.DoubleVar(value=0)
        self.smoothing_var = tk.DoubleVar(value=0.7)
        self.show_debug_var = tk.BooleanVar(value=False)
        self.mask_path_var = tk.StringVar(value="No mask loaded.")
        self.fps_var = tk.StringVar(value="FPS: --")

        # --- Mask Controls ---
        mask_frame = ttk.LabelFrame(main_frame, text="Mask Controls", padding="10")
        mask_frame.pack(fill="x", pady=5)
        ttk.Button(mask_frame, text="Load New Mask", command=self._select_mask).pack(fill="x")
        ttk.Label(mask_frame, textvariable=self.mask_path_var, wraplength=280).pack(fill="x", pady=5)
        
        # --- Parameter Sliders ---
        params_frame = ttk.LabelFrame(main_frame, text="Real-time Parameters", padding="10")
        params_frame.pack(fill="x", pady=5)
        self._create_slider(params_frame, "Scale", self.scale_var, 0.1, 3.0)
        self._create_slider(params_frame, "X Offset", self.x_offset_var, -100, 100)
        self._create_slider(params_frame, "Y Offset", self.y_offset_var, -100, 100)
        self._create_slider(params_frame, "Angle Offset", self.angle_offset_var, -180, 180)
        self._create_slider(params_frame, "Smoothing (α)", self.smoothing_var, 0.0, 0.98)

        # --- Actions & Debug ---
        actions_frame = ttk.LabelFrame(main_frame, text="Actions & Debugging", padding="10")
        actions_frame.pack(fill="x", pady=5)
        
        # NEW: Button sub-frame for better layout
        button_subframe = ttk.Frame(actions_frame)
        button_subframe.pack(fill="x", pady=(0, 5))
        
        self.pause_button = ttk.Button(button_subframe, text="Pause Feed", command=self._toggle_pause)
        self.pause_button.pack(side="left", expand=True, fill="x", padx=2)
        
        self.lock_button = ttk.Button(button_subframe, text="Lock Mask", command=self._toggle_lock)
        self.lock_button.pack(side="left", expand=True, fill="x", padx=2)

        # NEW: Minimize button
        ttk.Button(button_subframe, text="Minimize Controls", command=self.root.iconify).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Checkbutton(actions_frame, text="Show Debug Overlay", variable=self.show_debug_var).pack(pady=5)
        ttk.Label(actions_frame, textvariable=self.fps_var, font="-weight bold").pack(pady=5)
        
        # --- Recording Frame ---
        record_frame = ttk.LabelFrame(main_frame, text="Recording", padding="10")
        record_frame.pack(fill="x", pady=5)
        self.record_button = ttk.Button(record_frame, text="Start Recording", command=self._toggle_recording)
        self.record_button.pack(fill="x")

        # --- Profile Management ---
        profile_frame = ttk.LabelFrame(main_frame, text="Settings Profiles", padding="10")
        profile_frame.pack(fill="x", pady=5)
        ttk.Button(profile_frame, text="Save Profile", command=self._save_profile).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(profile_frame, text="Load Profile", command=self._load_profile).pack(side="left", expand=True, fill="x", padx=2)
        
    def _create_slider(self, parent, label, var, from_, to):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", expand=True, pady=2)
        ttk.Label(frame, text=label, width=12).pack(side="left")
        ttk.Scale(frame, from_=from_, to=to, variable=var, orient="horizontal").pack(side="right", expand=True, fill="x")

    def _initialize_camera(self, camera_index=0):
        if self.cap: self.cap.release()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", f"Could not open camera at index {camera_index}.")
            self._on_closing()
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera initialized at {self.width}x{self.height}")

    def _update_preview_feed(self):
        if not self.is_paused:
            ret, frame = self.cap.read()
            if not ret: self.root.after(10, self._update_preview_feed); return
            self.current_frame = cv2.flip(frame, 1)
        
        processed_frame = self._process_frame(self.current_frame.copy())
        
        now = time.time()
        time_delta = now - self.last_frame_time
        if time_delta > 0: self.fps = 1.0 / time_delta
        self.last_frame_time = now
        self.fps_var.set(f"FPS: {self.fps:.1f}")

        if self.is_recording and self.video_writer:
            self.video_writer.write(processed_frame)
            cv2.circle(processed_frame, (30, 30), 10, (0, 0, 255), -1)

        cv2.imshow("Live Mask Preview (Press 'Q' to Quit)", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): self._on_closing(); return
        self.root.after(1, self._update_preview_feed)

    def _process_frame(self, frame):
        if self.is_mask_locked or not self.mask_img_pil:
            if self.smoothed_values["x"] is not None: frame = self._overlay_mask(frame)
        else:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = self.face_mesh.process(image_rgb)
            image_rgb.flags.writeable = True

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w, _ = frame.shape
                
                landmarks_px = {id_name: (int(landmarks[id_idx].x*w), int(landmarks[id_idx].y*h)) for id_name, id_idx in self.STABLE_LANDMARK_IDS.items()}
                p_left, p_right = landmarks_px["LEFT_CHEEK"], landmarks_px["RIGHT_CHEEK"]
                face_width = math.dist(p_left, p_right)
                
                current = {"x": landmarks_px["NOSE_TIP"][0],
                           "y": int((landmarks_px["FOREHEAD"][1] + landmarks_px["CHIN"][1]) / 2.2),
                           "scale": face_width / self.mask_img_pil.width,
                           "angle": -math.degrees(math.atan2(p_right[1]-p_left[1], p_right[0]-p_left[0]))}

                alpha = 1.0 - self.smoothing_var.get()
                for key in self.smoothed_values:
                    if self.smoothed_values[key] is None: self.smoothed_values[key] = current[key]
                    else: self.smoothed_values[key] = (alpha * current[key]) + ((1 - alpha) * self.smoothed_values[key])

                if self.show_debug_var.get(): self._draw_debug_overlay(frame, landmarks_px, results.multi_face_landmarks[0])

            if self.smoothed_values["x"] is not None: frame = self._overlay_mask(frame)
        return frame

    def _overlay_mask(self, background_frame):
        final_scale = self.smoothed_values["scale"] * self.scale_var.get()
        final_x = self.smoothed_values["x"] + self.x_offset_var.get()
        final_y = self.smoothed_values["y"] + self.y_offset_var.get()
        final_angle = self.smoothed_values["angle"] + self.angle_offset_var.get()

        if not self.mask_img_pil or final_scale <= 0: return background_frame
        
        new_width, new_height = int(self.mask_img_pil.width*final_scale), int(self.mask_img_pil.height*final_scale)
        if new_width <= 0 or new_height <= 0: return background_frame
        
        overlay_resized = self.mask_img_pil.resize((new_width, new_height), Image.LANCZOS)
        overlay_rotated = overlay_resized.rotate(final_angle, expand=True, resample=Image.BICUBIC)
        overlay_cv = cv2.cvtColor(np.array(overlay_rotated), cv2.COLOR_RGBA2BGRA)

        h_overlay, w_overlay, _ = overlay_cv.shape
        x_tl, y_tl = int(final_x-w_overlay//2), int(final_y-h_overlay//2)
        h_bg, w_bg, _ = background_frame.shape
        
        y1_bg, y2_bg = max(0,y_tl), min(h_bg, y_tl+h_overlay); x1_bg, x2_bg = max(0,x_tl), min(w_bg, x_tl+w_overlay)
        y1_overlay, y2_overlay = max(0,-y_tl), min(h_overlay, h_bg-y_tl); x1_overlay, x2_overlay = max(0,-x_tl), min(w_overlay, w_bg-x_tl)
        if x1_bg >= x2_bg or y1_bg >= y2_bg: return background_frame
        
        roi_bg = background_frame[y1_bg:y2_bg, x1_bg:x2_bg]
        overlay_crop = overlay_cv[y1_overlay:y2_overlay, x1_overlay:x2_overlay]
        alpha = overlay_crop[:, :, 3] / 255.0

        for c in range(3): roi_bg[:,:,c] = (alpha * overlay_crop[:,:,c] + (1-alpha) * roi_bg[:,:,c])
        return background_frame

    def _draw_debug_overlay(self, frame, landmarks_px, face_landmarks):
        mp.solutions.drawing_utils.draw_landmarks(image=frame, landmark_list=face_landmarks, connections=self.mp_face_mesh.FACEMESH_TESSELATION, landmark_drawing_spec=None, connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
        for pos in landmarks_px.values(): cv2.circle(frame, pos, 3, (0, 255, 255), -1)
        if self.smoothed_values["x"] is not None: cv2.circle(frame, (int(self.smoothed_values["x"]), int(self.smoothed_values["y"])), 5, (255, 0, 0), -1)

    def _select_mask(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if path:
            try:
                self.mask_img_pil = Image.open(path).convert("RGBA")
                self.mask_path_var.set(os.path.basename(path))
            except Exception as e:
                messagebox.showerror("Error", f"Could not load mask image: {e}")

    def _toggle_pause(self): self.is_paused=not self.is_paused; self.pause_button.config(text="Resume" if self.is_paused else "Pause")
    def _toggle_lock(self): self.is_mask_locked=not self.is_mask_locked; self.lock_button.config(text="Unlock" if self.is_mask_locked else "Lock")
        
    def _toggle_recording(self):
        if not self.is_recording:
            path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")], initialdir=self.APP_DATA_PATH)
            if path:
                self.video_writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, (self.width, self.height))
                self.is_recording = True
                self.record_button.config(text="Stop Recording")
        else:
            if self.video_writer: self.video_writer.release()
            self.video_writer = None; self.is_recording = False
            self.record_button.config(text="Start Recording")
    
    def _get_current_profile(self):
        # Convert Path object to string for JSON serialization
        current_mask_path = self.mask_path_var.get()
        if self.mask_img_pil:
             current_mask_path = getattr(self.mask_img_pil, 'filename', current_mask_path)
             
        return {"mask_path": current_mask_path if "No mask" not in current_mask_path else "",
                "scale": self.scale_var.get(), "x_offset": self.x_offset_var.get(),
                "y_offset": self.y_offset_var.get(), "angle_offset": self.angle_offset_var.get(),
                "smoothing": self.smoothing_var.get(), "show_debug": self.show_debug_var.get()}
        
    def _save_profile(self):
        # UPDATED: File dialog now opens in the app's data folder
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], initialdir=self.APP_DATA_PATH)
        if path:
            with open(path, 'w') as f: json.dump(self._get_current_profile(), f, indent=4)
            print(f"Profile saved to {path}")

    def _load_profile(self, path=None):
        if not path:
            # UPDATED: File dialog now opens in the app's data folder
            path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], initialdir=self.APP_DATA_PATH)
        if path and os.path.exists(path):
            with open(path, 'r') as f: config = json.load(f)
            
            self.scale_var.set(config.get("scale",1.0)); self.x_offset_var.set(config.get("x_offset",0))
            self.y_offset_var.set(config.get("y_offset",0)); self.angle_offset_var.set(config.get("angle_offset",0))
            self.smoothing_var.set(config.get("smoothing",0.7)); self.show_debug_var.set(config.get("show_debug",False))
            
            mask_path = config.get("mask_path")
            if mask_path and os.path.exists(mask_path):
                 try:
                    self.mask_img_pil = Image.open(mask_path).convert("RGBA")
                    self.mask_img_pil.filename = mask_path # Store path for saving
                    self.mask_path_var.set(os.path.basename(mask_path))
                 except Exception: self.mask_path_var.set("Failed to load mask.")
            elif mask_path: self.mask_path_var.set(f"Mask not found: {os.path.basename(mask_path)}")

    def _on_closing(self):
        print("Closing application..."); self._save_config(self.DEFAULT_CONFIG_PATH) 
        if self.cap: self.cap.release()
        if self.is_recording and self.video_writer: self.video_writer.release()
        self.face_mesh.close(); cv2.destroyAllWindows(); self.root.destroy(); sys.exit()
    
    def _save_config(self, path):
        try:
            with open(path, 'w') as f: json.dump(self._get_current_profile(), f, indent=4)
            print(f"Default config saved to {path}")
        except Exception as e: print(f"Could not save default config: {e}")

    def _load_config(self, path):
        if path.exists(): self._load_profile(path)
        else: print("No default config found. Starting with defaults.")

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = FaceMaskApp(root)
    root.mainloop()