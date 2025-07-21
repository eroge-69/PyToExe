import cv2
import numpy as np
import pyautogui
import mss
from ultralytics import YOLO
import keyboard
import time

model = YOLO('yolov8n.pt')  # lightweight YOLOv8

aimbot_enabled = False

def detect_targets(frame):
    results = model(frame, verbose=False)[0]
    return results.boxes

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR), monitor

def box_area(box):
    x1, y1, x2, y2 = box.xyxy[0]
    return (x2 - x1) * (y2 - y1)

def aim_at_box(box, monitor):
    x1, y1, x2, y2 = box.xyxy[0]
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)

    center_x = monitor["width"] // 2
    center_y = monitor["height"] // 2

    dx = cx - center_x
    dy = cy - center_y

    pyautogui.moveRel(dx / 15, dy / 15, duration=0.01)

def main():
    global aimbot_enabled
    print("Press F to toggle aimbot ON/OFF")
    time.sleep(2)

    while True:
        if keyboard.is_pressed('f'):
            aimbot_enabled = not aimbot_enabled
            print(f"Aimbot enabled: {aimbot_enabled}")
            time.sleep(0.5)  # debounce

        if aimbot_enabled:
            frame, monitor = capture_screen()
            boxes = detect_targets(frame)
            if boxes:
                biggest = max(boxes, key=box_area)
                aim_at_box(biggest, monitor)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
