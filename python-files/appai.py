import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import pyautogui
from PIL import Image
import os
import threading
import time
from queue import Queue

class FixedHighPerformanceESP:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP Overlay with Confidence Control")
        self.detection_active = False
        self.templates = []
        self.target_fps = 120
        self.frame_queue = Queue(maxsize=2)
        
        # Detection parameters
        self.confidence_threshold = 0.75  # Default confidence level
        self.screen_scale = 0.5
        self.min_matches = 15
        
        # Initialize detector (using ORB for speed)
        self.detector = cv2.ORB_create(nfeatures=2000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Create UI with confidence control
        self.create_ui()
        
        # Overlay window
        self.overlay_window = None
        self.overlay_canvas = None
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
        self.detection_thread.start()
        
        # Start overlay update loop
        self.root.after(10, self.update_overlay)
    
    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()
        
        # Template controls
        tk.Label(main_frame, text="Template Images:").grid(row=0, column=0, sticky="w")
        self.template_list = tk.Listbox(main_frame, height=5, width=40)
        self.template_list.grid(row=1, column=0, columnspan=2, pady=5)
        
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Button(btn_frame, text="Add Templates", command=self.add_templates).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear Templates", command=self.clear_templates).pack(side=tk.LEFT, padx=5)
        
        # Confidence control
        tk.Label(main_frame, text="Confidence Threshold:").grid(row=3, column=0, sticky="w", pady=(10,0))
        self.confidence_slider = tk.Scale(main_frame, from_=0.1, to=1.0, resolution=0.05,
                                        orient=tk.HORIZONTAL, command=self.update_confidence)
        self.confidence_slider.set(self.confidence_threshold)
        self.confidence_slider.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        # Min matches control
        tk.Label(main_frame, text="Minimum Matches:").grid(row=5, column=0, sticky="w", pady=(10,0))
        self.min_matches_slider = tk.Scale(main_frame, from_=5, to=50, orient=tk.HORIZONTAL)
        self.min_matches_slider.set(self.min_matches)
        self.min_matches_slider.grid(row=6, column=0, columnspan=2, sticky="ew")
        
        # Start/stop button
        self.detect_btn = tk.Button(main_frame, text="START ESP", command=self.toggle_detection,
                                  bg="red", fg="white", font=('Arial', 12, 'bold'))
        self.detect_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Status: Idle", fg="gray")
        self.status_label.grid(row=8, column=0, columnspan=2)
        
        # FPS control
        tk.Label(main_frame, text="Target FPS:").grid(row=9, column=0, sticky="w", pady=(10,0))
        self.fps_slider = tk.Scale(main_frame, from_=30, to=144, orient=tk.HORIZONTAL)
        self.fps_slider.set(self.target_fps)
        self.fps_slider.grid(row=10, column=0, columnspan=2, sticky="ew")
    
    def create_overlay_window(self):
        """Create transparent overlay window"""
        if self.overlay_window:
            self.overlay_window.destroy()
            
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.attributes('-fullscreen', True)
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-transparentcolor', 'white')
        self.overlay_window.overrideredirect(True)
        
        screen_width = self.overlay_window.winfo_screenwidth()
        screen_height = self.overlay_window.winfo_screenheight()
        self.overlay_canvas = tk.Canvas(self.overlay_window, width=screen_width, height=screen_height,
                                      bg='white', highlightthickness=0)
        self.overlay_canvas.pack()
    
    def add_templates(self):
        file_paths = filedialog.askopenfilenames(
            title="Select template images",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        
        for path in file_paths:
            try:
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Resize template for consistent detection
                    img = cv2.resize(img, (0,0), fx=self.screen_scale, fy=self.screen_scale)
                    kp, des = self.detector.detectAndCompute(img, None)
                    if des is not None:
                        self.templates.append({
                            'path': os.path.basename(path),
                            'kp': kp,
                            'des': des,
                            'shape': img.shape
                        })
                        self.template_list.insert(tk.END, os.path.basename(path))
            except Exception as e:
                print(f"Error loading template {path}: {e}")
    
    def clear_templates(self):
        self.templates = []
        self.template_list.delete(0, tk.END)
    
    def update_confidence(self, val):
        self.confidence_threshold = float(val)
    
    def toggle_detection(self):
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.detect_btn.config(text="STOP ESP", bg="green")
            self.status_label.config(text="Status: Running", fg="green")
            if not self.overlay_window:
                self.create_overlay_window()
        else:
            self.detect_btn.config(text="START ESP", bg="red")
            self.status_label.config(text="Status: Idle", fg="gray")
            self.clear_overlay()
    
    def detection_worker(self):
        """Worker thread for detection"""
        while True:
            if self.detection_active and self.templates:
                try:
                    start_time = time.time()
                    
                    # Update parameters from sliders
                    self.target_fps = self.fps_slider.get()
                    self.min_matches = self.min_matches_slider.get()
                    
                    # Capture screen
                    screenshot = pyautogui.screenshot()
                    screen = np.array(screenshot)
                    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
                    
                    # Resize for performance
                    h, w = screen_gray.shape
                    new_h, new_w = int(h * self.screen_scale), int(w * self.screen_scale)
                    screen_resized = cv2.resize(screen_gray, (new_w, new_h))
                    
                    # Find keypoints
                    kp_screen, des_screen = self.detector.detectAndCompute(screen_resized, None)
                    
                    detections = []
                    if des_screen is not None:
                        for template in self.templates:
                            if template['des'] is not None:
                                matches = self.bf.match(template['des'], des_screen)
                                matches = sorted(matches, key=lambda x: x.distance)
                                
                                # Filter matches by confidence
                                good_matches = []
                                for m in matches:
                                    if m.distance < (1 - self.confidence_threshold) * 100:  # Convert confidence to distance threshold
                                        good_matches.append(m)
                                
                                if len(good_matches) >= self.min_matches:
                                    src_pts = np.float32([template['kp'][m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
                                    dst_pts = np.float32([kp_screen[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
                                    
                                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                                    if M is not None:
                                        h_t, w_t = template['shape']
                                        pts = np.float32([[0,0], [0,h_t-1], [w_t-1,h_t-1], [w_t-1,0]]).reshape(-1,1,2)
                                        dst = cv2.perspectiveTransform(pts, M)
                                        dst[:,:,0] = dst[:,:,0] / self.screen_scale
                                        dst[:,:,1] = dst[:,:,1] / self.screen_scale
                                        detections.append({
                                            'points': [(int(p[0][0]), int(p[0][1])) for p in dst],
                                            'name': template['path'],
                                            'confidence': len(good_matches)/len(template['kp'])  # Simple confidence metric
                                        })
                    
                    # Put detections in queue
                    if not self.frame_queue.full():
                        self.frame_queue.put(detections)
                    
                    # Maintain target FPS
                    processing_time = time.time() - start_time
                    target_frame_time = 1.0 / self.target_fps
                    sleep_time = max(0, target_frame_time - processing_time)
                    time.sleep(sleep_time)
                    
                except Exception as e:
                    print(f"Detection error: {e}")
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    def update_overlay(self):
        """Update overlay from main thread"""
        try:
            if not self.frame_queue.empty():
                detections = self.frame_queue.get_nowait()
                self.overlay_canvas.delete("all")
                
                for detection in detections:
                    points = detection['points']
                    # Draw bounding box
                    self.overlay_canvas.create_polygon(
                        points[0][0], points[0][1],
                        points[1][0], points[1][1],
                        points[2][0], points[2][1],
                        points[3][0], points[3][1],
                        outline='red', width=2, fill=''
                    )
                    # Draw confidence text
                    conf_text = f"{detection['name']} ({detection['confidence']:.1%})"
                    self.overlay_canvas.create_text(
                        points[0][0], points[0][1] - 10,
                        text=conf_text,
                        fill='yellow', anchor=tk.SW, font=('Arial', 8)
                    )
        except:
            pass
        
        self.root.after(1, self.update_overlay)
    
    def clear_overlay(self):
        if self.overlay_canvas:
            self.overlay_canvas.delete("all")
    
    def cleanup(self):
        self.detection_active = False
        if self.overlay_window:
            self.overlay_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    esp = FixedHighPerformanceESP(root)
    root.mainloop()