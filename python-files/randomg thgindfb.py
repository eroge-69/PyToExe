import torch
import cv2
import numpy as np
from pynput.keyboard import Key, Controller
import pyautogui
import time
import random

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
device = torch.device('cpu')
model.to(device)

# Start video capture
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Perform inference
    results = model(frame)

    # Get detection results
    detections = results.xyxy[0]  # tensor [x1, y1, x2, y2, confidence, class]

    # Print the coordinates and labels
    for *box, conf, cls in detections:
        x1, y1, x2, y2 = [int(coord.item()) for coord in box]
        label = model.names[int(cls.item())]
        print(f'Detected {label} at [{x1}, {y1}, {x2}, {y2}] with confidence {conf:.2f}')

    # Render results (draws bounding boxes and labels on the frame)
    rendered_frame = np.squeeze(results.render())

    # Display the frame
    cv2.imshow('YOLOv5 Real-time Detection', rendered_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    
cap.release()
cv2.destroyAllWindows()


