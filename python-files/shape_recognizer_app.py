import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import csv
from collections import Counter

class ShapeRecognizerApp:
    def __init__(self, window):
        self.window = window
        self.window.title("🔵 Shape Recognizer")
        self.window.geometry("1024x720")
        self.window.configure(bg="#f0f0f0")
        self.window.resizable(True, True)

        self.running = False
        self.cap = None
        self.frame = None
        self.shapes = []

        # Title
        title = tk.Label(self.window, text="Shape Recognizer", font=("Segoe UI", 16, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        # Canvas frame (fixed size)
        self.canvas_frame = tk.Frame(self.window, width=960, height=540)
        self.canvas_frame.pack(pady=5)
        self.canvas_frame.pack_propagate(False)  # prevent auto resize

        self.canvas = tk.Label(self.canvas_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Controls frame (always visible)
        self.controls_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.controls_frame.pack(pady=10)

        self.btn_start = tk.Button(self.controls_frame, text="Start Camera", command=self.start_camera, width=15)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = tk.Button(self.controls_frame, text="Stop Camera", command=self.stop_camera, width=15)
        self.btn_stop.grid(row=0, column=1, padx=5)

        self.btn_screenshot = tk.Button(self.controls_frame, text="Screenshot", command=self.save_screenshot, width=15)
        self.btn_screenshot.grid(row=0, column=2, padx=5)

        self.btn_export = tk.Button(self.controls_frame, text="Export CSV", command=self.export_csv, width=15)
        self.btn_export.grid(row=0, column=3, padx=5)

        # Shape Counter
        self.shape_label = tk.Label(self.window, text="Shapes Detected: 0", font=("Segoe UI", 11), bg="#f0f0f0")
        self.shape_label.pack(pady=5)

    def start_camera(self):
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam")
            return
        self.running = True
        self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.canvas.config(image='')
        self.shape_label.config(text="Shapes Detected: 0")

    def update_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        self.frame = frame.copy()
        shape_frame, self.shapes = self.detect_shapes(frame)

        resized = cv2.resize(shape_frame, (960, 540))
        img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.config(image=imgtk)

        self.update_shape_counter()
        self.window.after(30, self.update_frame)  # ~30 FPS

    def detect_shapes(self, frame):
        shapes = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue

            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            x, y, w, h = cv2.boundingRect(approx)

            shape = None
            if len(approx) == 3:
                shape = "Triangle"
            elif len(approx) == 4:
                aspect_ratio = w / float(h)
                shape = "Square" if 0.95 < aspect_ratio < 1.05 else "Rectangle"
            else:
                perimeter = cv2.arcLength(cnt, True)
                circularity = 4 * 3.1416 * (area / (perimeter * perimeter + 1e-5))
                if circularity > 0.7:
                    shape = "Circle"

            if shape:
                cv2.putText(frame, shape, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                shapes.append(shape)

        return frame, shapes

    def update_shape_counter(self):
        if not self.shapes:
            self.shape_label.config(text="Shapes Detected: 0")
        else:
            total = len(self.shapes)
            counter = Counter(self.shapes)
            breakdown = ", ".join(f"{v} {k}" for k, v in counter.items())
            self.shape_label.config(text=f"Shapes Detected: {total} ({breakdown})")

    def save_screenshot(self):
        if self.frame is None:
            messagebox.showwarning("Warning", "No frame to save.")
            return
        filename = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        cv2.imwrite(filename, self.frame)
        messagebox.showinfo("Saved", f"Screenshot saved as {filename}")

    def export_csv(self):
        if not self.shapes:
            messagebox.showwarning("Warning", "No shapes detected.")
            return
        filename = datetime.datetime.now().strftime("shapes_%Y%m%d_%H%M%S.csv")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Shape"])
            for shape in self.shapes:
                writer.writerow([datetime.datetime.now().isoformat(), shape])
        messagebox.showinfo("Exported", f"CSV saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShapeRecognizerApp(root)
    root.mainloop()
