import os
import cv2
import pytesseract
import re
import tkinter.messagebox

# Ścieżka do Tesseract – dostosuj jeśli inna
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Folder ze zdjęciami
folder = r'C:\Users\mrzadeczka\Desktop\ELEKTRYKI'

zmienione = 0
pominiete = 0

for filename in os.listdir(folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(folder, filename)
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Detekcja krawędzi i konturów
        edged = cv2.Canny(gray, 30, 200)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        plate_img = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                plate_img = gray[y:y + h, x:x + w]
                break

        roi = plate_img if plate_img is not None else gray
        text = pytesseract.image_to_string(roi)
        text = text.replace(" ", "").upper()

        match = re.search(r'[A-Z]{1,3}[0-9]{1,4}[A-Z]{0,2}', text)

        if match:
            plate = match.group(0)
            ext = os.path.splitext(filename)[1]
            new_filename = f"{plate}_RZ2{ext}"
            new_path = os.path.join(folder, new_filename)

            if not os.path.exists(new_path):
                os.rename(path, new_path)
                zmienione += 1
        else:
            pominiete += 1

# Podsumowanie
tkinter.messagebox.showinfo("Gotowe", f"✅ Zmieniono nazw: {zmienione}\n❌ Pominięto: {pominiete}")