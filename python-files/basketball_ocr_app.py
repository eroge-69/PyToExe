import cv2
import easyocr
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import os

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Global flag
running = False

# Save file
SAVE_FILE = "results.txt"

# GUI window
root = tk.Tk()
root.title("Basketball OCR Scoreboard App")
root.geometry("400x300")

# Labels for OCR results
labels = {
    "Home": tk.StringVar(value="Home: ?"),
    "Away": tk.StringVar(value="Away: ?"),
    "Clock": tk.StringVar(value="Game Clock: ?"),
    "Shot": tk.StringVar(value="Shot Clock: ?"),
    "Quarter": tk.StringVar(value="Quarter: ?")
}

for key in labels:
    tk.Label(root, textvariable=labels[key], font=("Arial", 14)).pack(pady=5)

def save_to_file(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SAVE_FILE, 'a') as f:
        f.write(f"{timestamp} | {data}\n")

def extract_ocr(frame, rois):
    result = {}
    for key, (x, y, w, h) in rois.items():
        roi = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        text = reader.readtext(gray, detail=0)
        if text:
            val = text[0].strip()
            if key == "Quarter":
                q_map = {"1": "1st", "2": "2nd", "3": "3rd", "4": "4th"}
                val = q_map.get(val, val)
            result[key] = val
        else:
            result[key] = "?"
    return result

def select_image():
    path = filedialog.askopenfilename()
    if not path:
        return
    frame = cv2.imread(path)
    run_ocr_on_frame(frame)

def run_ocr_on_frame(frame):
    # Define ROIs manually for now (x, y, w, h)
    rois = {
        "Home": (50, 50, 100, 50),
        "Away": (200, 50, 100, 50),
        "Clock": (120, 150, 150, 50),
        "Shot": (300, 150, 60, 50),
        "Quarter": (370, 50, 50, 50)
    }
    result = extract_ocr(frame, rois)
    update_labels(result)
    save_to_file(result)

def update_labels(result):
    for key in labels:
        labels[key].set(f"{key}: {result.get(key, '?')}")

def start_webcam():
    global running
    running = True
    cap = cv2.VideoCapture(0)

    rois = {
        "Home": (50, 50, 100, 50),
        "Away": (200, 50, 100, 50),
        "Clock": (120, 150, 150, 50),
        "Shot": (300, 150, 60, 50),
        "Quarter": (370, 50, 50, 50)
    }

    def loop():
        while running:
            ret, frame = cap.read()
            if not ret:
                break
            result = extract_ocr(frame, rois)
            update_labels(result)
            save_to_file(result)
            cv2.imshow("Webcam OCR", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=loop).start()

def stop_webcam():
    global running
    running = False

tk.Button(root, text="Run on Image", command=select_image).pack(pady=10)
tk.Button(root, text="Start Webcam", command=start_webcam).pack(pady=10)
tk.Button(root, text="Stop Webcam", command=stop_webcam).pack(pady=10)

root.mainloop()
