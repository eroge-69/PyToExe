import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class SmartDocumentCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Document Auto-Cropper")
        self.root.geometry("900x600")

        self.image_path = ""
        self.original_image = None
        self.processed_image = None

        self.create_widgets()

    def create_widgets(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Auto-Crop Document", command=self.process_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)

        image_frame = tk.Frame(self.root)
        image_frame.pack(fill=tk.BOTH, expand=True)

        self.original_label = tk.Label(image_frame, text="Original", relief=tk.SUNKEN)
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.processed_label = tk.Label(image_frame, text="Cropped", relief=tk.SUNKEN)
        self.processed_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not self.image_path:
            return

        self.original_image = cv2.imread(self.image_path)
        if self.original_image is None:
            messagebox.showerror("Error", "Could not open image.")
            return

        img_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_img = self.resize_image(pil_img, 400)
        img_tk = ImageTk.PhotoImage(pil_img)

        self.original_label.config(image=img_tk)
        self.original_label.image = img_tk

    def process_image(self):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please load an image first.")
            return

        try:
            image = self.original_image.copy()
            ratio = image.shape[0] / 500.0
            resized = cv2.resize(image, (int(image.shape[1] / ratio), 500))

            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            # Adaptive threshold for better edges
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2)
            thresh = cv2.bitwise_not(thresh)
            edged = cv2.Canny(thresh, 30, 150)

            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            screenCnt = None

            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    screenCnt = approx
                    break

            if screenCnt is None:
                # Fallback: bounding box
                messagebox.showinfo("Info", "Using fallback bounding box.")
                x, y, w, h = cv2.boundingRect(contours[0])
                screenCnt = np.array([
                    [[x, y]],
                    [[x + w, y]],
                    [[x + w, y + h]],
                    [[x, y + h]]
                ])

            warped = self.four_point_transform(self.original_image, screenCnt.reshape(4, 2) * ratio)
            self.processed_image = warped

            img_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            pil_img = self.resize_image(pil_img, 400)
            img_tk = ImageTk.PhotoImage(pil_img)

            self.processed_label.config(image=img_tk)
            self.processed_label.image = img_tk

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def four_point_transform(self, image, pts):
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def resize_image(self, image, max_size):
        w, h = image.size
        if w > h:
            new_w = max_size
            new_h = int(h * max_size / w)
        else:
            new_h = max_size
            new_w = int(w * max_size / h)
        return image.resize((new_w, new_h), Image.LANCZOS)

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No image to save.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if path:
            try:
                rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                Image.fromarray(rgb).save(path)
                messagebox.showinfo("Saved", f"Image saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartDocumentCropper(root)
    root.mainloop()
