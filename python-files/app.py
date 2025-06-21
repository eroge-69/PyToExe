import tkinter as tk
from tkinter import Label, Frame
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
from scipy.signal import find_peaks
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HeartRateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HRM: Heart Rate Measurement")
        self.root.geometry("800x500")

        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)

        # UI Components
        self.create_widgets()

        # OpenCV Video Capture
        self.cap = cv2.VideoCapture(0)

        # Signal Processing
        self.frame_rate = 30  # Assume 30 FPS
        self.buffer_size = self.frame_rate * 60  # 1-minute buffer
        self.signal_buffer = []
        self.time_buffer = []
        self.start_time = None
        self.measuring = False

        # Start Update Loops
        self.update_camera()
        self.update_graph()

    def create_widgets(self):
        """Creates the UI components for the app."""

        # Camera Feed Frame
        self.camera_frame = Frame(self.root, width=350, height=350, relief="solid", borderwidth=1)
        self.camera_frame.place(x=20, y=50)

        self.camera_label = Label(self.camera_frame, text="CAMERA", font=("Arial", 20))
        self.camera_label.place(relx=0.5, rely=0.5, anchor="center")

        # Graph Frame
        self.graph_frame = Frame(self.root, width=300, height=250, relief="solid", borderwidth=1)
        self.graph_frame.place(x=420, y=50)

        self.figure, self.ax = plt.subplots(figsize=(3, 2.5))
        self.ax.set_title("Heart Rate Over Time")
        self.ax.set_xlabel("Time (sec)")
        self.ax.set_ylabel("Signal")
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 120)

        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack()

        # Heart Rate Display
        self.heart_rate_label = Label(self.root, text="Heart Rate :\n0 BPM", font=("Arial", 30, "bold"), fg="black")
        self.heart_rate_label.place(x=450, y=350)

        # Start Button
        self.start_button = tk.Button(self.root, text="START", font=("Arial", 12), command=self.start_measurement)
        self.start_button.place(x=150, y=420)

    def update_camera(self):
        """Fetches the video feed and processes face detection."""
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)

            if results.detections and self.measuring:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)

                    # Extract forehead region
                    forehead = frame[y:y + h // 5, x:x + w]
                    if forehead.size > 0:
                        hsv = cv2.cvtColor(forehead, cv2.COLOR_BGR2HSV)
                        saturation_channel = np.mean(hsv[:, :, 1])  # S channel from HSV
                        self.signal_buffer.append(saturation_channel)
                        self.time_buffer.append(time.time() - self.start_time)

            # Display camera feed
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.root.after(10, self.update_camera)

    def update_graph(self):
        """Updates the heart rate graph dynamically."""
        self.ax.clear()
        self.ax.set_title("Heart Rate Over Time")
        self.ax.set_xlabel("Time (sec)")
        self.ax.set_ylabel("Signal")
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 120)

        if len(self.signal_buffer) > self.frame_rate * 5:  # At least 5 seconds of data
            signal_array = np.array(self.signal_buffer)
            peaks, _ = find_peaks(signal_array, distance=self.frame_rate // 2)

            # Compute Heart Rate
            duration = len(signal_array) / self.frame_rate
            heart_rate = (len(peaks) / duration) * 60

            self.heart_rate_label.config(text=f"Heart Rate :\n{int(heart_rate)} BPM", fg="black")
            self.ax.plot(self.time_buffer, self.signal_buffer, color="cyan")

        self.canvas.draw()
        self.root.after(1000, self.update_graph)

    def start_measurement(self):
        """Starts measurement and automatically stops after 60 seconds."""
        self.signal_buffer.clear()
        self.time_buffer.clear()
        self.start_time = time.time()
        self.measuring = True
        self.heart_rate_label.config(text="Measuring...", fg="blue")
        self.root.after(60000, self.stop_measurement)

    def stop_measurement(self):
        """Stops measurement and resets reading."""
        self.measuring = False
        self.heart_rate_label.config(text="Heart Rate :\n-- BPM", fg="black")

    def on_close(self):
        """Releases resources on closing the app."""
        self.cap.release()
        self.root.destroy()

# Run the Application
root = tk.Tk()
app = HeartRateApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
