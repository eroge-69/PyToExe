import cv2
import pytesseract
from datetime import datetime
import os

# Global flag
running = False

# Save file
SAVE_FILE = "results.txt"

# Placeholder for labels
labels = {
    "Home": "Home: ?",
    "Away": "Away: ?",
    "Clock": "Game Clock: ?",
    "Shot": "Shot Clock: ?",
    "Quarter": "Quarter: ?"
}

def save_to_file(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SAVE_FILE, 'a') as f:
        f.write(f"{timestamp} | {data}\n")

def extract_ocr(frame, rois):
    result = {}
    for key, (x, y, w, h) in rois.items():
        roi = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 7').strip()
        if text:
            val = text.split("\n")[0]
            if key == "Quarter":
                q_map = {"1": "1st", "2": "2nd", "3": "3rd", "4": "4th"}
                val = q_map.get(val, val)
            result[key] = val
        else:
            result[key] = "?"
    return result

def run_ocr_on_frame(frame):
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
        labels[key] = f"{key}: {result.get(key, '?')}"
    print("\n".join(labels.values()))

def run_webcam():
    cap = cv2.VideoCapture(0)

    rois = {
        "Home": (50, 50, 100, 50),
        "Away": (200, 50, 100, 50),
        "Clock": (120, 150, 150, 50),
        "Shot": (300, 150, 60, 50),
        "Quarter": (370, 50, 50, 50)
    }

    while True:
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

if __name__ == '__main__':
    print("Running webcam OCR directly.")
    print("Press 'q' in the webcam window to quit.")
    run_webcam()
