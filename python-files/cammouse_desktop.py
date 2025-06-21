
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import sys
import traceback
from math import sqrt
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue

class CamMouseController:
    def __init__(self):
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Camera setup
        self.cap = None
        self.is_running = False

        # Gesture detection parameters
        self.cursor_smoothing = 5
        self.click_threshold = 0.05
        self.last_click_time = 0
        self.click_debounce = 0.2  # 200ms debounce

        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()

        # Previous cursor position for smoothing
        self.prev_x, self.prev_y = pyautogui.position()

        # PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

    def smooth_cursor_movement(self, x, y):
        """Apply smoothing to cursor movement"""
        smooth_x = self.prev_x + (x - self.prev_x) / self.cursor_smoothing
        smooth_y = self.prev_y + (y - self.prev_y) / self.cursor_smoothing
        self.prev_x, self.prev_y = smooth_x, smooth_y
        return int(smooth_x), int(smooth_y)

    def process_hand_landmarks(self, landmarks, image_width, image_height):
        """Process hand landmarks for gesture detection"""
        # Get key landmarks
        thumb_tip = landmarks[4]      # Thumb tip
        index_tip = landmarks[8]      # Index finger tip
        middle_tip = landmarks[12]    # Middle finger tip

        # Convert normalized coordinates to screen coordinates
        cursor_x = int((1 - index_tip.x) * self.screen_width)  # Flip horizontally
        cursor_y = int(index_tip.y * self.screen_height)

        # Apply smoothing
        smooth_x, smooth_y = self.smooth_cursor_movement(cursor_x, cursor_y)

        # Move cursor
        try:
            pyautogui.moveTo(smooth_x, smooth_y)
        except:
            pass  # Ignore any pyautogui errors

        # Detect gestures
        current_time = time.time()

        # Left click: thumb and index finger pinch
        thumb_index_distance = self.calculate_distance(thumb_tip, index_tip)
        if thumb_index_distance < self.click_threshold and            (current_time - self.last_click_time) > self.click_debounce:
            try:
                pyautogui.click()
                self.last_click_time = current_time
                return "Left Click"
            except:
                pass

        # Right click: thumb and middle finger pinch
        thumb_middle_distance = self.calculate_distance(thumb_tip, middle_tip)
        if thumb_middle_distance < self.click_threshold and            (current_time - self.last_click_time) > self.click_debounce:
            try:
                pyautogui.rightClick()
                self.last_click_time = current_time
                return "Right Click"
            except:
                pass

        return "Cursor Movement"

    def start_camera(self, camera_index=0):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera {camera_index}")
            self.is_running = True
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            return False

    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def process_frame(self):
        """Process single frame from camera"""
        if not self.cap or not self.is_running:
            return None, "Camera not active"

        ret, frame = self.cap.read()
        if not ret:
            return None, "Failed to read frame"

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = self.hands.process(rgb_frame)
        gesture_detected = "No Hand Detected"

        # Draw landmarks and detect gestures
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # Process gestures
                gesture_detected = self.process_hand_landmarks(
                    hand_landmarks.landmark, width, height
                )

        return frame, gesture_detected

class CamMouseGUI:
    def __init__(self):
        self.controller = CamMouseController()
        self.setup_gui()
        self.frame_queue = queue.Queue()
        self.processing_thread = None

    def setup_gui(self):
        """Setup the GUI interface"""
        self.root = tk.Tk()
        self.root.title("CamMouse - Hand Gesture Cursor Control")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(
            main_frame, 
            text="CamMouse - Kontrol Kursor dengan Gesture Tangan",
            font=("Arial", 16, "bold"),
            bg='#2b2b2b',
            fg='white'
        )
        title_label.pack(pady=(0, 20))

        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Camera Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Camera selection
        camera_frame = ttk.Frame(control_frame)
        camera_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(camera_frame, text="Camera:").pack(side=tk.LEFT)
        self.camera_var = tk.StringVar(value="0")
        camera_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.camera_var,
            values=["0", "1", "2"],
            state="readonly",
            width=10
        )
        camera_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(
            button_frame,
            text="Start Camera",
            command=self.start_camera
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(
            button_frame,
            text="Stop Camera",
            command=self.stop_camera,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="Camera: Stopped | Hand: Not Detected | Gesture: None",
            bg='#2b2b2b',
            fg='white'
        )
        self.status_label.pack()

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Cursor smoothing
        smoothing_frame = ttk.Frame(settings_frame)
        smoothing_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(smoothing_frame, text="Cursor Smoothing:").pack(side=tk.LEFT)
        self.smoothing_var = tk.IntVar(value=5)
        smoothing_scale = ttk.Scale(
            smoothing_frame,
            from_=1,
            to=10,
            variable=self.smoothing_var,
            orient=tk.HORIZONTAL,
            command=self.update_smoothing
        )
        smoothing_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Click threshold
        threshold_frame = ttk.Frame(settings_frame)
        threshold_frame.pack(fill=tk.X)

        ttk.Label(threshold_frame, text="Click Sensitivity:").pack(side=tk.LEFT)
        self.threshold_var = tk.DoubleVar(value=0.05)
        threshold_scale = ttk.Scale(
            threshold_frame,
            from_=0.02,
            to=0.1,
            variable=self.threshold_var,
            orient=tk.HORIZONTAL,
            command=self.update_threshold
        )
        threshold_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding=10)
        instructions_frame.pack(fill=tk.BOTH, expand=True)

        instructions_text = tk.Text(
            instructions_frame,
            height=8,
            wrap=tk.WORD,
            bg='#3b3b3b',
            fg='white',
            state=tk.DISABLED
        )
        instructions_text.pack(fill=tk.BOTH, expand=True)

        instructions = """
        Cara Menggunakan CamMouse:

        1. Pilih kamera yang akan digunakan
        2. Klik "Start Camera" untuk memulai
        3. Posisikan tangan di depan kamera
        4. Gunakan gesture berikut:
           • Telunjuk: Menggerakkan kursor
           • Jempol + Telunjuk (pinch): Klik kiri
           • Jempol + Jari tengah (pinch): Klik kanan
        5. Sesuaikan pengaturan sesuai kebutuhan

        Tips:
        - Pastikan pencahayaan cukup
        - Jaga jarak 30-60 cm dari kamera
        - Gerakkan tangan perlahan untuk kontrol yang lebih baik
        """

        instructions_text.config(state=tk.NORMAL)
        instructions_text.insert(tk.END, instructions)
        instructions_text.config(state=tk.DISABLED)

    def update_smoothing(self, value):
        """Update cursor smoothing setting"""
        self.controller.cursor_smoothing = int(float(value))

    def update_threshold(self, value):
        """Update click threshold setting"""
        self.controller.click_threshold = float(value)

    def start_camera(self):
        """Start camera processing"""
        camera_index = int(self.camera_var.get())
        if self.controller.start_camera(camera_index):
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # Start processing thread
            self.processing_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.processing_thread.start()

            # Start GUI update
            self.update_gui()

    def stop_camera(self):
        """Stop camera processing"""
        self.controller.stop_camera()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("Camera: Stopped | Hand: Not Detected | Gesture: None")

    def camera_loop(self):
        """Camera processing loop"""
        while self.controller.is_running:
            frame, gesture = self.controller.process_frame()
            if frame is not None:
                # Put frame data in queue for GUI update
                self.frame_queue.put(gesture)

                # Show frame (optional - can be disabled for performance)
                cv2.imshow("CamMouse - Hand Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(0.033)  # ~30 FPS

    def update_gui(self):
        """Update GUI with latest data"""
        if self.controller.is_running:
            try:
                gesture = self.frame_queue.get_nowait()
                hand_status = "Detected" if gesture != "No Hand Detected" else "Not Detected"
                status_text = f"Camera: Running | Hand: {hand_status} | Gesture: {gesture}"
                self.update_status(status_text)
            except queue.Empty:
                pass

            # Schedule next update
            self.root.after(100, self.update_gui)

    def update_status(self, text):
        """Update status label"""
        self.status_label.config(text=text)

    def run(self):
        """Run the GUI application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {str(e)}")

    def on_closing(self):
        """Handle application closing"""
        self.controller.stop_camera()
        self.root.destroy()

def main():
    """Main application entry point"""
    try:
        app = CamMouseGUI()
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
