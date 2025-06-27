
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox

input_dir = "εισοδος"
output_dir = "εξοδος"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def auto_crop_image(image_path, save_path):
    img = cv2.imread(image_path)
    if img is None:
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if np.mean(gray[thresh == 255]) > 127:
        thresh = cv2.bitwise_not(thresh)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    cropped = img[y:y+h, x:x+w]
    cv2.imwrite(save_path, cropped)

processed = 0

for filename in os.listdir(input_dir):
    if filename.lower().endswith((".jpg", ".jpeg")):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        auto_crop_image(input_path, output_path)
        processed += 1

root = tk.Tk()
root.withdraw()
if processed > 0:
    messagebox.showinfo("Ολοκληρώθηκε", f"Η επεξεργασία ολοκληρώθηκε για {processed} φωτογραφίες.")
else:
    messagebox.showwarning("Καμία φωτογραφία", "Δεν βρέθηκαν εικόνες στον φάκελο 'εισοδος'.")
