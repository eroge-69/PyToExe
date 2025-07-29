import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import time
import os
import sys

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HKS's PDF VIEWER")
        self.root.geometry("900x700")

        # Set icon if available
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), "eye.png")
        if os.path.exists(icon_path):
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print("Icon load error:", e)

        self.zoom = 1.5
        self.min_zoom = 0.5
        self.max_zoom = 4.0
        self.doc = None
        self.page_num = 0
        self.last_zoom_time = 0

        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        control_frame = tk.Frame(self.root)
        control_frame.pack(side="bottom", pady=5)
        tk.Button(control_frame, text="Open PDF", command=self.load_pdf).pack(side="left", padx=5)

        self.root.bind("<Left>", self.prev_page)
        self.root.bind("<Right>", self.next_page)
        self.root.bind("<Configure>", self.resize)
        self.canvas.bind("<Control-MouseWheel>", self.ctrl_mouse_zoom)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.show_page()

    def show_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_num)
        matrix = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.image = self.photo  # Keep reference

    def next_page(self, event=None):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def prev_page(self, event=None):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def resize(self, event):
        self.show_page()

    def ctrl_mouse_zoom(self, event):
        now = time.time()
        if now - self.last_zoom_time < 0.15:
            return  # debounce to limit frequency
        self.last_zoom_time = now

        if event.delta > 0 and self.zoom < self.max_zoom:
            self.zoom *= 1.2
        elif event.delta < 0 and self.zoom > self.min_zoom:
            self.zoom /= 1.2
        self.show_page()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()
