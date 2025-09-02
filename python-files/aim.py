import torch
import ultralytics  # Import ajouté ici
torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])

from ultralytics import YOLO
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import mss
import pyautogui
import cv2
import threading
import time

# YOLOv8n (léger, rapide)
model = YOLO("yolov8n")

# Capture écran principal
sct = mss.mss()
monitor = sct.monitors[1]  # Écran principal

# Création fenêtre overlay transparente
root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.attributes('-transparentcolor', 'black')
root.config(bg='black')
canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill="both", expand=True)

overlay_img = None

def move_mouse_smoothly_to(x, y, steps=15):
    current_x, current_y = pyautogui.position()
    for i in range(1, steps + 1):
        new_x = int(current_x + (x - current_x) * i / steps)
        new_y = int(current_y + (y - current_y) * i / steps)
        pyautogui.moveTo(new_x, new_y, duration=0.005)

def detection_loop():
    global overlay_img
    while True:
        # Capture écran
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

        results = model(frame, verbose=False)[0]
        people = []

        overlay = np.zeros((monitor['height'], monitor['width'], 4), dtype=np.uint8)  # Transparent

        if results.boxes is not None:
            for box in results.boxes:
                if int(box.cls[0]) == 0:  # Classe "personne"
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    people.append((cx, cy, x1, y1, x2, y2))
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255, 255), 2)

        # Déplacer la souris
        if people:
            screen_cx = monitor['width'] // 2
            screen_cy = monitor['height'] // 2
            closest = min(people, key=lambda p: (p[0] - screen_cx)**2 + (p[1] - screen_cy)**2)
            move_mouse_smoothly_to(closest[0], closest[1])

        # Convertir en image pour overlay tkinter
        pil_img = Image.fromarray(overlay)
        overlay_img = ImageTk.PhotoImage(image=pil_img)

        # Affichage overlay sur le canvas
        canvas.delete("all")
        canvas.create_image(0, 0, image=overlay_img, anchor='nw')

        time.sleep(0.01)

# Thread pour ne pas bloquer tkinter
threading.Thread(target=detection_loop, daemon=True).start()

# Lancer l’overlay
root.mainloop()

