import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk, ImageEnhance
import fitz  # PyMuPDF
import os
import io

class PDFStamperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        # CHANGE 2: Window title updated
        self.title("Advanced PDF Stamping Tool (Abid)")
        self.geometry("1100x750")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Class Variables
        self.pdf_document = None
        self.stamp_image_original = None
        self.stamp_image_processed = None
        self.pdf_path = ""
        self.stamp_path = ""
        self.current_preview_page = 0
        self.zoom_factor = 1.0

        # --- Manual Placement Variables ---
        self.manual_stamp_pos = {'x': 100, 'y': 100}
        self._drag_data = {'x': 0, 'y': 0, 'item': None}

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1, minsize=320)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Left Frame (Controls) ---
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_frame.pack_propagate(False)

        # File Selection
        self.select_pdf_button = ctk.CTkButton(self.controls_frame, text="Select PDF", command=self.load_pdf)
        self.select_pdf_button.pack(pady=10, padx=10, fill="x")
        self.pdf_label = ctk.CTkLabel(self.controls_frame, text="No PDF selected", wraplength=280)
        self.pdf_label.pack(pady=5, padx=10)

        self.select_stamp_button = ctk.CTkButton(self.controls_frame, text="Select Stamp/Signature", command=self.load_stamp)
        self.select_stamp_button.pack(pady=10, padx=10, fill="x")
        self.stamp_label = ctk.CTkLabel(self.controls_frame, text="No Stamp selected", wraplength=280)
        self.stamp_label.pack(pady=5, padx=10)
        
        # CHANGE 1: Author name section removed from here

        # Stamp Enhancement & Sizing
        ctk.CTkLabel(self.controls_frame, text="Stamp Adjustments", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self.controls_frame, text="Brightness:").pack()
        self.brightness_slider = ctk.CTkSlider(self.controls_frame, from_=0.5, to=1.5, command=self.update_stamp_preview)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(self.controls_frame, text="Size:").pack()
        self.size_slider = ctk.CTkSlider(self.controls_frame, from_=20, to=300, command=self.update_stamp_preview)
        self.size_slider.set(100)
        self.size_slider.pack(pady=5, padx=10, fill="x")

        # Stamp Placement
        ctk.CTkLabel(self.controls_frame, text="Stamp Placement", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.manual_mode_var = ctk.BooleanVar(value=False)
        self.manual_mode_check = ctk.CTkCheckBox(self.controls_frame, text="Enable Manual Placement", variable=self.manual_mode_var, command=self.toggle_placement_mode)
        self.manual_mode_check.pack(pady=5, padx=10, anchor="w")

        self.placement_var = ctk.StringVar(value="Bottom Right")
        placement_options = ["Top Left", "Top Center", "Top Right", "Bottom Left", "Bottom Center", "Bottom Right"]
        self.placement_menu = ctk.CTkOptionMenu(self.controls_frame, values=placement_options, variable=self.placement_var, command=lambda _: self.update_page_preview())
        self.placement_menu.pack(pady=5, padx=10, fill="x")
        
        # Pages to Stamp
        ctk.CTkLabel(self.controls_frame, text="Apply Stamp To", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.apply_pages_var = ctk.StringVar(value="All Pages")
        self.apply_pages_segmented = ctk.CTkSegmentedButton(self.controls_frame, values=["All Pages", "Current Page"], variable=self.apply_pages_var)
        self.apply_pages_segmented.pack(pady=5, padx=10, fill="x")

        # --- Right Frame (Preview) ---
        self.preview_container = ctk.CTkFrame(self)
        self.preview_container.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.preview_canvas = Canvas(self.preview_container, bg="gray", width=400, height=600)
        self.preview_canvas.pack(expand=True, padx=10, pady=10)
        
        # Bind mouse events for manual placement
        self.preview_canvas.tag_bind("stamp", "<ButtonPress-1>", self.on_stamp_press)
        self.preview_canvas.tag_bind("stamp", "<B1-Motion>", self.on_stamp_drag)

        # Page Navigation
        self.nav_frame = ctk.CTkFrame(self.preview_container)
        self.nav_frame.pack(fill="x", padx=10, pady=5)
        self.prev_button = ctk.CTkButton(self.nav_frame, text="< Previous", command=self.prev_page)
        self.prev_button.pack(side="left", padx=5)
        self.page_label = ctk.CTkLabel(self.nav_frame, text="Page: -/-")
        self.page_label.pack(side="left", expand=True)
        self.next_button = ctk.CTkButton(self.nav_frame, text="Next >", command=self.next_page)
        self.next_button.pack(side="right", padx=5)

        # Final Action Button
        self.process_button = ctk.CTkButton(self, text="Generate Stamped PDF", command=self.process_pdf, height=40)
        self.process_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.pdf_label.configure(text=os.path.basename(self.pdf_path))
            self.pdf_document = fitz.open(self.pdf_path)
            self.current_preview_page = 0
            self.update_page_preview()

    def load_stamp(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.stamp_path = path
            self.stamp_label.configure(text=os.path.basename(self.stamp_path))
            self.stamp_image_original = Image.open(self.stamp_path).convert("RGBA")
            self.update_stamp_preview()

    def update_stamp_preview(self, _=None):
        if not self.stamp_image_original: return
        
        enhancer = ImageEnhance.Brightness(self.stamp_image_original)
        img = enhancer.enhance(self.brightness_slider.get())
        
        base_width = int(self.size_slider.get())
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        self.stamp_image_processed = img.resize((base_width, h_size), Image.LANCZOS)
        
        self.update_page_preview()

    def update_page_preview(self):
        if not self.pdf_document: return
        self.preview_canvas.delete("all")

        page = self.pdf_document[self.current_preview_page]
        preview_height = 650
        self.zoom_factor = preview_height / page.rect.height
        mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        self.page_photo = ImageTk.PhotoImage(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.page_photo)
        self.preview_canvas.config(width=pix.width, height=pix.height)
        
        self.page_label.configure(text=f"Page: {self.current_preview_page + 1} / {self.pdf_document.page_count}")

        if self.stamp_image_processed:
            self.stamp_photo = ImageTk.PhotoImage(self.stamp_image_processed)
            stamp_w, stamp_h = self.stamp_image_processed.size
            page_w, page_h = pix.width, pix.height
            margin = 10
            x, y = 0, 0

            if self.manual_mode_var.get():
                x, y = self.manual_stamp_pos['x'], self.manual_stamp_pos['y']
            else:
                pos = self.placement_var.get()
                if pos == "Top Left": x, y = margin, margin
                elif pos == "Top Center": x, y = (page_w - stamp_w) / 2, margin
                elif pos == "Top Right": x, y = page_w - stamp_w - margin, margin
                elif pos == "Bottom Left": x, y = margin, page_h - stamp_h - margin
                elif pos == "Bottom Center": x, y = (page_w - stamp_w) / 2, page_h - stamp_h - margin
                elif pos == "Bottom Right": x, y = page_w - stamp_w - margin, page_h - stamp_h - margin
                self.manual_stamp_pos = {'x': x, 'y': y}
            
            self.preview_canvas.create_image(x, y, anchor="nw", image=self.stamp_photo, tags=("stamp",))

    def next_page(self):
        if self.pdf_document and self.current_preview_page < self.pdf_document.page_count - 1:
            self.current_preview_page += 1
            self.update_page_preview()
            
    def prev_page(self):
        if self.pdf_document and self.current_preview_page > 0:
            self.current_preview_page -= 1
            self.update_page_preview()

    def toggle_placement_mode(self):
        if self.manual_mode_var.get():
            self.placement_menu.configure(state="disabled")
            messagebox.showinfo("Manual Mode", "Manual placement enabled. You can now drag the stamp in the preview window.")
        else:
            self.placement_menu.configure(state="normal")
        self.update_page_preview()

    def on_stamp_press(self, event):
        self._drag_data["item"] = self.preview_canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_stamp_drag(self, event):
        if not self.manual_mode_var.get(): return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.preview_canvas.move(self._drag_data["item"], dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.manual_stamp_pos['x'] += dx
        self.manual_stamp_pos['y'] += dy

    def process_pdf(self):
        if not self.pdf_path or not self.stamp_path:
            messagebox.showerror("Error", "Please select a PDF and a Stamp image first.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], initialfile=f"stamped_{os.path.basename(self.pdf_path)}")
        if not output_path: return
            
        try:
            doc = fitz.open(self.pdf_path)
            
            # CHANGE 1: Author metadata logic removed from here

            if self.apply_pages_var.get() == "All Pages":
                pages_to_stamp = range(doc.page_count)
            else:
                pages_to_stamp = [self.current_preview_page]

            img_byte_arr = io.BytesIO()
            self.stamp_image_processed.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            stamp_w, stamp_h = self.stamp_image_processed.size

            for page_num in pages_to_stamp:
                page = doc[page_num]
                page_rect = page.rect
                
                x, y = 0, 0
                if self.manual_mode_var.get():
                    actual_x = self.manual_stamp_pos['x'] / self.zoom_factor
                    actual_y = self.manual_stamp_pos['y'] / self.zoom_factor
                    x, y = actual_x, actual_y
                else:
                    margin = 20
                    pos = self.placement_var.get()
                    if pos == "Top Left": x, y = margin, margin
                    elif pos == "Top Center": x, y = (page_rect.width - stamp_w) / 2, margin
                    elif pos == "Top Right": x, y = page_rect.width - stamp_w - margin, margin
                    elif pos == "Bottom Left": x, y = margin, page_rect.height - stamp_h - margin
                    elif pos == "Bottom Center": x, y = (page_rect.width - stamp_w) / 2, page_rect.height - stamp_h - margin
                    elif pos == "Bottom Right": x, y = page_rect.width - stamp_w - margin, page_rect.height - stamp_h - margin

                stamp_rect = fitz.Rect(x, y, x + stamp_w, y + stamp_h)
                page.insert_image(stamp_rect, stream=img_bytes, overlay=True)

            original_size = os.path.getsize(self.pdf_path)
            doc.save(output_path, garbage=4, deflate=True)
            compressed_size = os.path.getsize(output_path)
            doc.close()
            
            messagebox.showinfo("Success", 
                f"PDF saved successfully to:\n{output_path}\n\n"
                f"Original Size: {original_size / 1024:.2f} KB\n"
                f"Compressed Size: {compressed_size / 1024:.2f} KB")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = PDFStamperApp()
    app.mainloop()