import cv2
from pyzbar.pyzbar import decode
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner GUI")

        self.video_label = ttk.Label(root)
        self.video_label.pack()

        self.result_label = ttk.Label(root, text="Hasil Scan:", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

        self.result_text = tk.Text(root, height=4, width=50)
        self.result_text.pack()

        self.cap = cv2.VideoCapture(1)
        self.running = True

        self.update_frame()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            barcodes = decode(frame)
            for barcode in barcodes:
                data = barcode.data.decode('utf-8')
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, data)

                pts = barcode.polygon
                if pts:
                    pts = [(pt.x, pt.y) for pt in pts]
                    for i in range(len(pts)):
                        cv2.line(frame, pts[i], pts[(i + 1) % len(pts)], (0, 255, 0), 2)
                    cv2.putText(frame, data, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            # Convert ke format Tkinter
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def on_close(self):
        self.running = False
        self.cap.release()
        self.root.destroy()

# Jalankan Aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeScannerApp(root)
    root.mainloop()
