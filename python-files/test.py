Python 3.12.8 (tags/v3.12.8:2dc476b, Dec  3 2024, 19:30:04) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import cv2
import numpy as np
import imutils
from tkinter import filedialog, Tk, Button, Label, Text, Scrollbar, RIGHT, Y, END, messagebox

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def process_omr(image_path, output_text):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)

        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        docCnt = None

        if len(cnts) > 0:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    docCnt = approx
                    break

        if docCnt is None:
            messagebox.showerror("Error", "OMR sheet not detected.")
            return

        warped = four_point_transform(gray, docCnt.reshape(4, 2))
        thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        num_rows = 10
        num_cols = 5
        bubble_height = thresh.shape[0] // num_rows
        bubble_width = thresh.shape[1] // num_cols

        results = []
        for row in range(num_rows):
            row_data = []
            for col in range(num_cols):
                y1 = row * bubble_height
                y2 = (row + 1) * bubble_height
                x1 = col * bubble_width
                x2 = (col + 1) * bubble_width
                cell = thresh[y1:y2, x1:x2]
...                 total = cv2.countNonZero(cell)
...                 row_data.append(total)
...             max_val = max(row_data)
...             selected = row_data.index(max_val) if max_val > 1000 else None
...             results.append(selected)
... 
...         output_text.delete("1.0", END)
...         for idx, ans in enumerate(results):
...             output_text.insert(END, f"Q{idx+1}: Option {chr(65+ans) if ans is not None else 'Not marked'}\n")
... 
...     except Exception as e:
...         messagebox.showerror("Error", str(e))
... 
... def select_image(output_text):
...     path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
...     if path:
...         process_omr(path, output_text)
... 
... def create_gui():
...     root = Tk()
...     root.title("OMR Scanner")
...     root.geometry("400x500")
... 
...     Label(root, text="OMR Sheet Scanner", font=("Arial", 14)).pack(pady=10)
...     Button(root, text="Upload OMR Image", command=lambda: select_image(output_text)).pack(pady=5)
... 
...     scrollbar = Scrollbar(root)
...     scrollbar.pack(side=RIGHT, fill=Y)
... 
...     output_text = Text(root, height=20, width=45, yscrollcommand=scrollbar.set)
...     output_text.pack(padx=10, pady=10)
...     scrollbar.config(command=output_text.yview)
... 
...     root.mainloop()
... 
... create_gui()
