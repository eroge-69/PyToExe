import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # pymupdf


class PDFRedactorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Redactor")
        self.doc = None
        self.filename = None
        self.page_index = 0
        self.zoom = 2.0  # render scale (change if you want higher resolution)
        self.photo = None
        self.image_id = None

        # store rectangles per page in image pixel coordinates: {page_index: [ (x0,y0,x1,y1), ... ]}
        self.rects = {}

        # UI
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(control_frame, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Prev", command=self.prev_page).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Next", command=self.next_page).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Clear selections", command=self.clear_page_rects).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Apply redactions", command=self.apply_redactions).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Save As...", command=self.save_as).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Overwrite original", command=self.overwrite_original).pack(side=tk.LEFT)

        self.page_label = tk.Label(control_frame, text="No file loaded")
        self.page_label.pack(side=tk.LEFT, padx=10)

        # Canvas for page display + drawing rectangles
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse drawing state
        self.start_x = None
        self.start_y = None
        self.current_rect_id = None

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Configure>", self.on_resize)

    # ---------- File / Document management ----------
    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        try:
            doc = fitz.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open PDF:\n{e}")
            return
        self.doc = doc
        self.filename = path
        self.page_index = 0
        self.rects = {}
        self.render_page()

    def save_as(self):
        if not self.doc:
            messagebox.showinfo("Info", "Open a PDF first.")
            return
        out_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not out_path:
            return
        try:
            self._apply_and_save(out_path)
            messagebox.showinfo("Saved", f"Redacted PDF saved to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def overwrite_original(self):
        if not self.doc or not self.filename:
            messagebox.showinfo("Info", "Open a PDF first.")
            return
        resp = messagebox.askyesno(
            "Overwrite original?",
            "This will overwrite the original file with the redacted version. This is irreversible.\nProceed?"
        )
        if not resp:
            return
        tmp_path = self.filename + ".redacted.tmp.pdf"
        try:
            self._apply_and_save(tmp_path)
            # replace
            os.replace(tmp_path, self.filename)
            messagebox.showinfo("Overwritten", f"Original file overwritten:\n{self.filename}")
        except Exception as e:
            # cleanup tmp if exists
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            messagebox.showerror("Error", f"Failed to overwrite original:\n{e}")

    # ---------- Page navigation ----------
    def prev_page(self):
        if not self.doc:
            return
        if self.page_index > 0:
            self.page_index -= 1
            self.render_page()

    def next_page(self):
        if not self.doc:
            return
        if self.page_index < len(self.doc) - 1:
            self.page_index += 1
            self.render_page()

    def render_page(self):
        if not self.doc:
            self.page_label.config(text="No file loaded")
            self.canvas.delete("all")
            return

        page = self.doc[self.page_index]
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # store image size for coordinate mapping
        self.current_image_size = (pix.width, pix.height)

        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        # Keep image_id to allow proper resizing handling
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.page_label.config(text=f"{os.path.basename(self.filename)} — page {self.page_index + 1}/{len(self.doc)}")

        # draw saved rects on this page
        for rect in self.rects.get(self.page_index, []):
            self._draw_rect_on_canvas(rect)

    # ---------- Mouse drawing ----------
    def on_mouse_down(self, event):
        if not self.doc:
            return
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # create a temporary rectangle
        self.current_rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_mouse_drag(self, event):
        if not self.doc or self.current_rect_id is None:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.current_rect_id, self.start_x, self.start_y, x, y)

    def on_mouse_up(self, event):
        if not self.doc or self.current_rect_id is None:
            return
        x_end = self.canvas.canvasx(event.x)
        y_end = self.canvas.canvasy(event.y)
        x0, y0 = self.start_x, self.start_y
        x1, y1 = x_end, y_end
        # normalize
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))

        # minimal size check
        if abs(x1 - x0) < 5 or abs(y1 - y0) < 5:
            # remove tiny rectangle
            self.canvas.delete(self.current_rect_id)
            self.current_rect_id = None
            return

        rect = (x0, y0, x1, y1)
        self.rects.setdefault(self.page_index, []).append(rect)
        # ensure the rectangle is a permanent rectangle on canvas (redraw with solid)
        self.canvas.delete(self.current_rect_id)
        self.current_rect_id = None
        self._draw_rect_on_canvas(rect)

    def _draw_rect_on_canvas(self, rect):
        # rect in image pixel coords: (x0,y0,x1,y1)
        x0, y0, x1, y1 = rect
        # semi-transparent fill is not trivial in Tk canvas; keep outlined with cross-hatch look
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", width=2)
        # cross lines to indicate redaction box
        self.canvas.create_line(x0, y0, x1, y1, fill="black")
        self.canvas.create_line(x0, y1, x1, y0, fill="black")

    def clear_page_rects(self):
        if not self.doc:
            return
        if self.page_index in self.rects:
            del self.rects[self.page_index]
        self.render_page()

    def on_resize(self, event):
        # Keep the displayed image anchored; we won't re-render the PDF on window resize to avoid heavy work.
        pass

    # ---------- Redaction application ----------
    def apply_redactions(self):
        if not self.doc:
            messagebox.showinfo("Info", "Open a PDF first.")
            return
        total = sum(len(v) for v in self.rects.values())
        if total == 0:
            messagebox.showinfo("Info", "No redaction boxes drawn.")
            return
        resp = messagebox.askyesno("Apply redactions", f"Apply {total} redaction(s) to the document now? This will permanently remove content when saved.")
        if not resp:
            return

        # Apply redactions in memory and save to a temporary file (user chooses save later).
        try:
            # We will mark redaction annotations on a copy of self.doc in memory, then user can save.
            # To avoid modifying user's original until they save/overwrite, we work on the loaded doc but remember to keep ability to save.
            # NOTE: fitz modifies the document object; to revert you'd need to re-open original. We choose to modify the in-memory doc
            # so the "Save As" or "Overwrite original" will operate on redacted doc. If you want to keep original untouched, re-open it before changes.
            for pno, rect_list in self.rects.items():
                page = self.doc[pno]
                for (x0, y0, x1, y1) in rect_list:
                    # convert image pixel coords to PDF points by dividing by zoom
                    r = fitz.Rect(x0 / self.zoom, y0 / self.zoom, x1 / self.zoom, y1 / self.zoom)
                    # Add redact annot - fill black
                    page.add_redact_annot(r, fill=(0, 0, 0))
                # apply redactions on that page (removes the text/contents in the rect)
                page.apply_redactions()
            # after applying, clear our rectangle store because they are now applied
            self.rects = {}
            # re-render current page to show effect
            self.render_page()
            messagebox.showinfo("Done", "Redactions applied in memory. Save the document to make them permanent on disk.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply redactions:\n{e}")

    def _apply_and_save(self, out_path):
        """
        Save the current in-memory document (which may already have had apply_redactions applied to pages)
        to out_path. Use garbage collect to clean unused objects.
        """
        # Save. PyMuPDF's save will write the current doc state. Use garbage=4 to clean unreferenced objects.
        self.doc.save(out_path, garbage=4, deflate=True)

        # Optionally, re-open saved file into memory so the app now points to saved file.
        # We'll switch the app to reference the new saved file so the user can continue editing if they want.
        self.doc.close()
        self.doc = fitz.open(out_path)
        self.filename = out_path
        self.page_index = min(self.page_index, len(self.doc) - 1)
        self.render_page()


def main():
    root = tk.Tk()
    app = PDFRedactorApp(root)
    root.geometry("900x700")
    root.mainloop()


if __name__ == "__main__":
    main()
