import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import tempfile
import fitz  # PyMuPDF
from pptx import Presentation
import webbrowser
import math

class SlideViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF/PPT Presenter in Responsive Window Tab")
        self.root.geometry("900x700")

        self.file_path = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_document = None
        self.ppt_images = None
        self.current_image = None

        # Selection variables
        self.start_x = None
        self.start_y = None
        self.sel_rect = None

        # UI
        self.canvas = tk.Canvas(self.root, bg="black", cursor="arrow")
        self.canvas.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side="bottom", pady=5)

        tk.Button(btn_frame, text="Open File", command=self.open_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Prev", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Next", command=self.next_page).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Copy Page Text", command=self.copy_page_text).pack(side="left", padx=5)

        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<Configure>", self.resize_image)

        # Mouse bindings for text selection
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def open_file(self):
        file_types = [("All supported files", "*.pdf *.pptx"), ("PDF files", "*.pdf"), ("PowerPoint files", "*.pptx")]
        path = filedialog.askopenfilename(filetypes=file_types)
        if not path:
            return
        
        # Reset state for new file
        self.file_path = path
        self.current_page = 0
        self.total_pages = 0
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
        self.ppt_images = None
        self.current_image = None
        self.canvas.delete("all")


        ext = os.path.splitext(self.file_path)[1].lower()
        try:
            if ext == ".pdf":
                self.load_pdf()
            elif ext == ".pptx":
                self.load_ppt()
            else:
                messagebox.showerror("Unsupported File", f"File type '{ext}' is not supported.")
                return
        except Exception as e:
            messagebox.showerror("Error Opening File", f"An error occurred: {e}")
            return

        self.show_page(0)

    def load_pdf(self):
        self.pdf_document = fitz.open(self.file_path)
        self.total_pages = len(self.pdf_document)

    def load_ppt(self):
        # NOTE: This part of the original code created blank images.
        # A full implementation would require a library to render PPTX slides to images,
        # which can be complex. This placeholder logic is kept.
        prs = Presentation(self.file_path)
        self.ppt_images = []
        temp_dir = tempfile.mkdtemp()

        for i, slide in enumerate(prs.slides):
            # This is a placeholder. Real rendering is more involved.
            img_path = os.path.join(temp_dir, f"slide_{i}.png")
            # Create a blank white image as a placeholder for the slide
            Image.new("RGB", (1280, 720), "white").save(img_path)
            self.ppt_images.append(Image.open(img_path))

        self.total_pages = len(self.ppt_images)

    def get_page_image(self, page_num):
        if self.file_path.lower().endswith(".pdf"):
            page = self.pdf_document[page_num]
            # Use a higher DPI for better quality on resize
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
        elif self.ppt_images:
            return self.ppt_images[page_num]
        return None

    def show_page(self, index):
        if not (0 <= index < self.total_pages):
            return
        self.current_page = index
        img = self.get_page_image(index)
        if img:
            self.current_image = img
            self.display_image(img)
            self.canvas.delete("link") # Clear old links

            # Add clickable links for the new page (PDFs only)
            if self.file_path.lower().endswith(".pdf"):
                self.add_pdf_links(index)

    def display_image(self, img):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 1 or canvas_h < 1: # Avoid division by zero if window is not ready
            return
            
        img_resized = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.tk_image, anchor="center")

    def add_pdf_links(self, page_index):
        page = self.pdf_document[page_index]
        links = page.get_links()
        page_rect = page.rect
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if page_rect.width == 0 or page_rect.height == 0:
            return

        w_ratio = canvas_w / page_rect.width
        h_ratio = canvas_h / page_rect.height

        for link in links:
            if link.get("kind") == fitz.LINK_URI:
                uri = link.get("uri")
                # The 'from' key holds the rectangle for the link area
                r = link["from"]
                x0, y0, x1, y1 = r.x0 * w_ratio, r.y0 * h_ratio, r.x1 * w_ratio, r.y1 * h_ratio
                
                # Create an invisible rectangle that will act as a button
                rect_id = self.canvas.create_rectangle(
                    x0, y0, x1, y1, outline="", fill="", tags=("link", f"link_{uri}")
                )
                # Bind the click event to open the URL
                self.canvas.tag_bind(rect_id, "<Button-1>",
                                     lambda e, url=uri: self.open_link(url))

    def open_link(self, url):
        # This function is now separate to avoid lambda scope issues and allow for confirmation
        if messagebox.askokcancel("Open Link", f"Do you want to open this URL in your browser?\n\n{url}"):
            webbrowser.open(url)

    def resize_image(self, event):
        if self.current_image:
            self.display_image(self.current_image)
            if self.file_path and self.file_path.lower().endswith(".pdf"):
                self.add_pdf_links(self.current_page)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def copy_page_text(self):
        if self.file_path and self.file_path.lower().endswith(".pdf") and self.pdf_document:
            page = self.pdf_document[self.current_page]
            text = page.get_text()
            if text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                messagebox.showinfo("Text Copied", "All text from the current page has been copied to the clipboard.")
            else:
                messagebox.showwarning("No Text Found", "No selectable text was found on this page.")

    def on_mouse_down(self, event):
        # Only start selection for PDF files
        if not (self.file_path and self.file_path.lower().endswith(".pdf")):
            return
            
        # Check if the click is on a link; if so, don't start selection
        # find_overlapping returns a tuple of item IDs
        overlapping = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in overlapping:
            if "link" in self.canvas.gettags(item):
                return # It's a link, let the link's own binding handle it.

        self.start_x, self.start_y = event.x, event.y
        if self.sel_rect:
            self.canvas.delete(self.sel_rect)
        # Create the selection rectangle
        self.sel_rect = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                     self.start_x, self.start_y,
                                                     outline="blue", fill="blue", stipple="gray25", width=1)

    def on_mouse_drag(self, event):
        # Only drag if a selection has been started
        if self.sel_rect is None:
            return
        # Update the coordinates of the selection rectangle
        self.canvas.coords(self.sel_rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        # Ensure a selection was in progress
        if self.sel_rect is None:
            return

        # Always delete the visual selection rectangle on mouse up
        self.canvas.delete(self.sel_rect)
        self.sel_rect = None

        end_x, end_y = event.x, event.y

        # *** FIX: Check if the mouse moved significantly. If not, it was a click, not a drag. ***
        # We check the distance to avoid copying text on an accidental click.
        distance = math.sqrt((end_x - self.start_x)**2 + (end_y - self.start_y)**2)
        if distance < 5:  # If moved less than 5 pixels, do nothing.
            return

        # Convert canvas selection coordinates to PDF page coordinates
        page = self.pdf_document[self.current_page]
        page_rect = page.rect
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if page_rect.width == 0 or page_rect.height == 0 or canvas_w == 0 or canvas_h == 0:
            return # Avoid division by zero

        w_ratio = page_rect.width / canvas_w
        h_ratio = page_rect.height / canvas_h

        # Ensure coordinates are ordered correctly (top-left to bottom-right)
        x0 = min(self.start_x, end_x) * w_ratio
        y0 = min(self.start_y, end_y) * h_ratio
        x1 = max(self.start_x, end_x) * w_ratio
        y1 = max(self.start_y, end_y) * h_ratio

        # Extract text from the calculated rectangle on the PDF page
        selection_rect = fitz.Rect(x0, y0, x1, y1)
        selected_text = page.get_text("text", clip=selection_rect)

        if selected_text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            messagebox.showinfo("Text Copied", f"Selected text has been copied to the clipboard.")
        # No warning message if no text is found, as it's common to select empty areas.

if __name__ == "__main__":
    root = tk.Tk()
    app = SlideViewer(root)
    root.mainloop()
