import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from ultralytics import YOLO
import dxcam
import threading
import time
import keyboard
import win32api
import win32con
import ctypes
import torch
import sys
import math
from collections import deque

class HVHAssistant:
    def __init__(self):
        # Initialize root window first
        self.root = tk.Tk()
        
        # Initialize settings with improved defaults
        self.settings = {
            "aimbot": tk.BooleanVar(value=True),
            "triggerbot": tk.BooleanVar(value=False),
            "esp": tk.BooleanVar(value=True),
            "fov_circle": tk.BooleanVar(value=True),
            "headshot_mode": tk.BooleanVar(value=False),
            "smoothing": tk.DoubleVar(value=0.4),  # More natural smoothing
            "fov_radius": tk.IntVar(value=300),
            "min_confidence": tk.DoubleVar(value=0.5),  # Higher default confidence
            "mouse_delay": tk.IntVar(value=5),
            "debug_mode": tk.BooleanVar(value=False),
            "cs2_raw_input_bypass": tk.BooleanVar(value=True),
            "cs2_sensitivity": tk.DoubleVar(value=1.0),
            "strict_fov": tk.BooleanVar(value=True),
            "prediction": tk.BooleanVar(value=True),  # NEW: Prediction for moving targets
            "aim_key": tk.StringVar(value="alt"),  # NEW: Configurable aim key
            "humanization": tk.DoubleVar(value=0.3)  # NEW: Human-like movement factor
        }

        # CS2-Specific Optimizations
        self.cs2_mode = True
        self.require_admin()

        # Core Components with improved initialization
        self.cam = dxcam.create(output_idx=0, output_color="RGB")
        self.cam.start(target_fps=120, video_mode=True)  # Higher FPS for better tracking
        self.model = YOLO("best.pt").to('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.fuse()  # Optimize model

        # Enhanced State Management
        self.running = True
        self.current_target = None
        self.last_detection = None
        self.detection_history = deque(maxlen=10)  # Track recent detections
        self.movement_history = deque(maxlen=5)  # Track target movement
        self.last_move_time = 0
        self.aim_key_pressed = False

        # Setup UI and start threads
        self.setup_ui()
        threading.Thread(target=self.detection_thread, daemon=True).start()
        threading.Thread(target=self.mouse_thread, daemon=True).start()
        threading.Thread(target=self.status_thread, daemon=True).start()
        self.bind_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.root.mainloop()

    def require_admin(self):
        """Force admin privileges for CS2"""
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit()
        except:
            pass

    def setup_ui(self):
        """Professional UI with enhanced options"""
        self.root.title("RIFT AI - Beta")
        self.root.geometry("500x650")
        style = ttk.Style()
        style.configure('TFrame', background='#333')
        style.configure('TLabelFrame', background='#333', foreground='white')
        style.configure('TCheckbutton', background='#333', foreground='white')

        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Strict FOV Checkbox
        ttk.Checkbutton(main_frame, text="STRICT FOV Detection",
                        variable=self.settings["strict_fov"]).pack(anchor="w", pady=5)

        # NEW: Prediction Checkbox
        ttk.Checkbutton(main_frame, text="Target Prediction",
                        variable=self.settings["prediction"]).pack(anchor="w", pady=5)

        # CS2 Settings Section
        cs2_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=(10,5))
        cs2_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(cs2_frame, text="Raw Input Bypass",
                        variable=self.settings["cs2_raw_input_bypass"]).pack(anchor="w")
        ttk.Label(cs2_frame, text="In-Game Sensitivity:").pack(anchor="w")
        tk.Scale(cs2_frame, from_=0.1, to=10.0, resolution=0.1,
                 orient="horizontal",
                 variable=self.settings["cs2_sensitivity"]).pack(fill=tk.X)
        
        # NEW: Aim Key Selection
        ttk.Label(cs2_frame, text="Aim Key:").pack(anchor="w")
        key_entry = ttk.Entry(cs2_frame, textvariable=self.settings["aim_key"], width=5)
        key_entry.pack(anchor="w")

        # Main Features
        self.create_feature_toggles(main_frame)
        self.create_sliders(main_frame)

        # Status Console
        self.console = tk.Text(main_frame, height=8, bg='black', fg='white')
        self.console.pack(fill=tk.X, pady=5)
        self.log("Enhanced system initialized for HVH gameplay")

    def create_feature_toggles(self, parent):
        """Feature toggle section with improved layout"""
        frame = ttk.LabelFrame(parent, text="Features", padding=(10,5))
        frame.pack(fill=tk.X, pady=5)
        features = [
            ("Aimbot", "aimbot"),
            ("Triggerbot (F2)", "triggerbot"),
            ("ESP (F3)", "esp"),
            ("FOV Circle (F4)", "fov_circle"),
            ("Headshot Mode (F5)", "headshot_mode"),
            ("Debug View (F6)", "debug_mode")
        ]
        for text, key in features:
            cb = ttk.Checkbutton(frame, text=text, variable=self.settings[key])
            cb.pack(anchor="w", padx=5, pady=2)

    def create_sliders(self, parent):
        """Interactive sliders with proper value handling"""
        sliders = [
            ("FOV Radius", "fov_radius", 50, 500),
            ("Smoothing", "smoothing", 10, 100),
            ("Min Confidence", "min_confidence", 10, 90),
            ("Mouse Delay (ms)", "mouse_delay", 1, 20),
            ("Humanization", "humanization", 0, 100)  # NEW: Human-like movement slider
        ]
        for text, key, min_val, max_val in sliders:
            frame = ttk.LabelFrame(parent, text=f"{text} ({min_val}-{max_val})", padding=(10,5))
            frame.pack(fill=tk.X, pady=5)
            scale = tk.Scale(frame, from_=min_val, to=max_val,
                             orient="horizontal",
                             variable=self.settings[key])
            scale.pack(fill=tk.X, padx=5)

    def bind_hotkeys(self):
        """Robust hotkey binding with configurable aim key"""
        hotkeys = {
            'f2': lambda: self.toggle_setting("triggerbot"),
            'f3': lambda: self.toggle_setting("esp"),
            'f4': lambda: self.toggle_setting("fov_circle"),
            'f5': lambda: self.toggle_setting("headshot_mode"),
            'f6': lambda: self.toggle_setting("debug_mode")
        }
        
        # Configurable aim key
        def set_aim_key_state(state):
            self.aim_key_pressed = state
            if state:
                self.log(f"Aim key pressed - tracking enabled")
            else:
                self.current_target = None
                
        keyboard.on_press_key(self.settings["aim_key"].get().lower(), 
                            lambda _: set_aim_key_state(True))
        keyboard.on_release_key(self.settings["aim_key"].get().lower(), 
                              lambda _: set_aim_key_state(False))
        
        for key, func in hotkeys.items():
            try:
                keyboard.add_hotkey(key, func)
            except:
                pass

    def toggle_setting(self, key):
        """Thread-safe setting toggle"""
        current = self.settings[key].get()
        self.settings[key].set(not current)
        state = "ENABLED" if not current else "DISABLED"
        self.log(f"{key.upper()} {state}")

    def log(self, message):
        """Thread-safe logging"""
        timestamp = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: self.console.insert(tk.END, f"[{timestamp}] {message}\n"))
        self.root.after(0, self.console.see, tk.END)

    def detection_thread(self):
        """High-performance detection pipeline with enhanced target tracking"""
        while self.running:
            try:
                start_time = time.perf_counter()
                
                frame = self.cam.get_latest_frame()
                if frame is None: 
                    time.sleep(0.001)
                    continue
                    
                # Convert to RGB if needed
                frame_rgb = frame if frame.shape[2] == 3 else cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Apply FOV mask before detection if strict mode enabled
                if self.settings["strict_fov"].get():
                    h, w = frame_rgb.shape[:2]
                    center_x, center_y = w//2, h//2
                    radius = self.settings["fov_radius"].get()
                    mask = np.zeros((h, w), dtype=np.uint8)
                    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
                    masked_frame = cv2.bitwise_and(frame_rgb, frame_rgb, mask=mask)
                    results = self.model(masked_frame,
                        conf=max(0.1, min(0.9, self.settings["min_confidence"].get() / 100)),
                        verbose=False)
                else:
                    results = self.model(frame_rgb,
                        conf=max(0.1, min(0.9, self.settings["min_confidence"].get() / 100)),
                        verbose=False)
                
                # Process results
                self.process_detections(frame_rgb, results)
                
                # Debug visualization
                if self.settings["debug_mode"].get():
                    self.show_debug_view(frame_rgb, results)
                    
                # Limit FPS to prevent excessive CPU usage
                elapsed = time.perf_counter() - start_time
                if elapsed < 0.008:  # ~120fps
                    time.sleep(0.008 - elapsed)
                    
            except Exception as e:
                self.log(f"Detection Error: {str(e)}")
                time.sleep(1)

    def process_detections(self, frame, results):
        """Enhanced detection processing with prediction"""
        targets = []
        if len(results[0].boxes) > 0:
            h, w = frame.shape[:2]
            center_x, center_y = w//2, h//2
            fov_r = self.settings["fov_radius"].get()
            
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = box.conf[0].item()
                
                # Calculate center point
                if self.settings["headshot_mode"].get():
                    center = (x1 + (x2-x1)//2, y1 + int((y2-y1)*0.2))  # Head area
                else:
                    center = (x1 + (x2-x1)//2, y1 + (y2-y1)//2)  # Center mass
                
                # Verify if in FOV
                dist = np.sqrt((center[0] - center_x)**2 + (center[1] - center_y)**2)
                if dist <= fov_r:
                    targets.append((center, conf, time.time()))  # Add timestamp for prediction
                    
            # Store detection history for prediction
            if targets:
                self.detection_history.append((time.time(), targets))
                
            # Predict target movement if enabled
            predicted_targets = []
            if self.settings["prediction"].get() and len(self.detection_history) > 1:
                predicted_targets = self.predict_target_movement(targets)
                
            self.last_detection = (time.time(), targets)
            
            # Select target only if aim key is pressed
            if self.aim_key_pressed and self.settings["aimbot"].get():
                if predicted_targets:
                    self.current_target = self.select_best_target(predicted_targets)
                elif targets:
                    self.current_target = self.select_best_target(targets)
                else:
                    self.current_target = None
            else:
                self.current_target = None
        else:
            self.current_target = None

    def predict_target_movement(self, current_targets):
        """Predict target movement based on history"""
        if len(self.detection_history) < 2:
            return current_targets
            
        # Calculate movement vectors for each target
        prev_time, prev_targets = self.detection_history[-2]
        current_time = time.time()
        time_delta = current_time - prev_time
        
        predicted_targets = []
        
        for (curr_pos, curr_conf, _) in current_targets:
            # Find closest matching target in previous frame
            closest_prev = None
            min_dist = float('inf')
            
            for (prev_pos, prev_conf, _) in prev_targets:
                dist = math.sqrt((curr_pos[0]-prev_pos[0])**2 + (curr_pos[1]-prev_pos[1])**2)
                if dist < min_dist and dist < 50:  # Max movement threshold
                    min_dist = dist
                    closest_prev = prev_pos
                    
            if closest_prev:
                # Calculate velocity
                dx = curr_pos[0] - closest_prev[0]
                dy = curr_pos[1] - closest_prev[1]
                
                # Predict future position (0.1s ahead)
                predict_x = curr_pos[0] + dx * 0.1 / time_delta
                predict_y = curr_pos[1] + dy * 0.1 / time_delta
                
                predicted_targets.append(((int(predict_x), int(predict_y)), curr_conf, current_time))
            else:
                predicted_targets.append((curr_pos, curr_conf, current_time))
                
        return predicted_targets

    def select_best_target(self, targets):
        """Enhanced target selection with multiple factors"""
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        center_x, center_y = screen_w//2, screen_h//2
        fov_r = self.settings["fov_radius"].get()
        
        best_target = None
        best_score = -float('inf')
        
        for (x, y), conf, _ in targets:
            # Calculate distance to center
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # Normalize distance score (closer is better)
            dist_score = 1 - min(dist / fov_r, 1)
            
            # Confidence score
            conf_score = conf
            
            # Combined score (weighted)
            score = (dist_score * 0.6) + (conf_score * 0.4)
            
            if score > best_score and dist <= fov_r:
                best_score = score
                best_target = (x, y)
                
        return best_target

    def show_debug_view(self, frame, results):
        """Enhanced debug visualization with prediction indicators"""
        vis = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Draw FOV circle
        if self.settings["fov_circle"].get():
            cv2.circle(vis, (vis.shape[1]//2, vis.shape[0]//2),
                       self.settings["fov_radius"].get(), (0, 255, 255), 1)
        
        # Draw detections
        if self.settings["esp"].get() and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                color = (0, 0, 255) if self.settings["headshot_mode"].get() else (0, 255, 0)
                cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
                cv2.putText(vis, f"{box.conf[0].item():.2f}", (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # Draw prediction vector if enabled
                if self.settings["prediction"].get() and self.current_target:
                    center = (x1 + (x2-x1)//2, y1 + (y2-y1)//2)
                    if self.settings["headshot_mode"].get():
                        center = (center[0], y1 + int((y2-y1)*0.2))
                    cv2.arrowedLine(vis, center, self.current_target, (255, 255, 0), 2)
        
        cv2.imshow("DEBUG View", vis)
        cv2.waitKey(1)

    def mouse_thread(self):
        """Enhanced mouse control with human-like movement"""
        last_pos = None
        while self.running:
            try:
                if self.current_target and self.settings["aimbot"].get() and self.aim_key_pressed:
                    current_time = time.time()
                    time_since_last = current_time - self.last_move_time
                    
                    # Add human-like delay based on settings
                    human_delay = self.settings["humanization"].get() / 100 * 0.1
                    if time_since_last < human_delay:
                        time.sleep(human_delay - time_since_last)
                        
                    self.move_mouse_cs2(*self.current_target)
                    self.last_move_time = current_time
                    
                time.sleep(0.001)
            except Exception as e:
                self.log(f"Mouse Error: {str(e)}")
                time.sleep(0.1)

    def move_mouse_cs2(self, target_x, target_y):
        """Enhanced CS2 mouse movement with humanization"""
        screen_w, screen_h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
        center_x, center_y = screen_w//2, screen_h//2
        
        # Calculate raw movement
        dx = target_x - center_x
        dy = target_y - center_y
        
        # Apply human-like movement pattern
        human_factor = self.settings["humanization"].get() / 100
        if human_factor > 0:
            # Add slight overshoot and correction
            overshoot_x = dx * (1 + human_factor * 0.1)
            overshoot_y = dy * (1 + human_factor * 0.1)
            
            # Move to overshoot position first
            self._raw_mouse_move(int(overshoot_x), int(overshoot_y))
            time.sleep(0.01)
            
            # Correct to actual position
            dx = dx - overshoot_x * 0.3
            dy = dy - overshoot_y * 0.3
        
        # Final movement with smoothing and sensitivity
        dx = int(dx * (self.settings["smoothing"].get() / 100) * self.settings["cs2_sensitivity"].get())
        dy = int(dy * (self.settings["smoothing"].get() / 100) * self.settings["cs2_sensitivity"].get())
        
        self._raw_mouse_move(dx, dy)
        
        # Triggerbot action
        if self.settings["triggerbot"].get():
            delay = self.settings["mouse_delay"].get() / 1000
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(delay)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def _raw_mouse_move(self, dx, dy):
        """Actual mouse movement implementation"""
        if self.settings["cs2_raw_input_bypass"].get():
            # Split movement into smaller steps for smoother motion
            steps = max(1, int(math.sqrt(dx*dx + dy*dy) / 10))
            for i in range(1, steps+1):
                step_dx = int(dx * i / steps)
                step_dy = int(dy * i / steps)
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, step_dx, step_dy, 0, 0)
                time.sleep(0.001)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

    def status_thread(self):
        """Real-time status updates with performance metrics"""
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            status = "Standby"
            fps = frame_count / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
            frame_count += 1
            
            if self.last_detection:
                targets = len(self.last_detection[1])
                status = f"Tracking {targets} targets | {fps:.1f} FPS" if targets > 0 else "No targets"
                
            self.root.title(f"RIFT AI - {status}")
            
            # Reset counters every second
            if time.time() - start_time > 1:
                frame_count = 0
                start_time = time.time()
                
            time.sleep(0.5)

    def cleanup(self):
        """Safe shutdown procedure"""
        self.running = False
        try:
            self.cam.stop()
            cv2.destroyAllWindows()
            keyboard.unhook_all()
            self.root.quit()
        except:
            pass

if __name__ == "__main__":
    HVHAssistant()