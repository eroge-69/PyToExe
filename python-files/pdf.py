import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.colorchooser import askcolor
import os
import sys
from collections import deque

class PDFAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Annotation Tool")
        self.root.geometry("800x600")
        
        self.current_file = None
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.start_x = None
        self.start_y = None
        self.shape_type = "circle"
        self.annotation_color = (1, 0, 0)  # Red
        
        # Undo functionality
        self.annotation_history = deque(maxlen=100)  # Stores last 100 actions
        self.current_annotations = []  # Tracks annotations on current page
        
        self.create_widgets()
        
    def create_widgets(self):
        # Menu
        menubar = tk.Menu(self.root)
        
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open PDF", command=self.open_pdf)
        filemenu.add_command(label="Save PDF", command=self.save_pdf)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # Shapes menu
        shapemenu = tk.Menu(menubar, tearoff=0)
        shapemenu.add_command(label="Circle", command=lambda: self.set_shape("circle"))
        shapemenu.add_command(label="Rectangle", command=lambda: self.set_shape("rectangle"))
        menubar.add_cascade(label="Shapes", menu=shapemenu)
        
        # Color menu
        colormenu = tk.Menu(menubar, tearoff=0)
        colormenu.add_command(label="Change Color", command=self.change_color)
        menubar.add_cascade(label="Color", menu=colormenu)
        
        # Edit menu (with undo)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo_last_annotation, accelerator="Ctrl+Z")
        menubar.add_cascade(label="Edit", menu=editmenu)
        
        self.root.config(menu=menubar)
        
        # Bind keyboard shortcut for undo
        self.root.bind_all("<Control-z>", lambda event: self.undo_last_annotation())
        
        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.prev_btn = tk.Button(toolbar, text="Previous", command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.next_btn = tk.Button(toolbar, text="Next", command=self.next_page)
        self.next_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.page_label = tk.Label(toolbar, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.undo_btn = tk.Button(toolbar, text="Undo", command=self.undo_last_annotation)
        self.undo_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        self.undo_btn.config(state=tk.DISABLED)
        
        # Canvas for PDF display
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.current_file = file_path
            try:
                self.doc = fitz.open(file_path)
                self.total_pages = len(self.doc)
                self.current_page = 0
                self.annotation_history.clear()
                self.current_annotations.clear()
                self.display_page()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
    
    def save_pdf(self):
        if self.doc and self.current_file:
            try:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF Files", "*.pdf")],
                    initialfile=os.path.basename(self.current_file)
                )
                if save_path:
                    self.doc.save(save_path)
                    messagebox.showinfo("Success", "PDF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF: {str(e)}")
    
    def display_page(self):
        if not self.doc:
            return
            
        self.canvas.delete("all")
        page = self.doc.load_page(self.current_page)
        zoom = 1.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert pixmap to PhotoImage
        img_data = pix.tobytes("ppm")
        self.img = tk.PhotoImage(data=img_data)
        
        # Display the image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        self.page_label.config(text=f"Page: {self.current_page + 1}/{self.total_pages}")
        
        # Enable/disable navigation buttons
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)
        
        # Update undo button state
        self.update_undo_button_state()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.current_annotations.clear()
            self.display_page()
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.current_annotations.clear()
            self.display_page()
    
    def set_shape(self, shape_type):
        self.shape_type = shape_type
    
    def change_color(self):
        color = askcolor(title="Choose annotation color")
        if color[0]:
            self.annotation_color = (color[0][0]/255, color[0][1]/255, color[0][2]/255)
    
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_shape = None
        
        if self.shape_type == "circle":
            self.current_shape = self.canvas.create_oval(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="red", width=2
            )
        elif self.shape_type == "rectangle":
            self.current_shape = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="red", width=2
            )
    
    def on_mouse_drag(self, event):
        if self.current_shape:
            if self.shape_type == "circle":
                self.canvas.coords(
                    self.current_shape,
                    self.start_x, self.start_y, event.x, event.y
                )
            elif self.shape_type == "rectangle":
                self.canvas.coords(
                    self.current_shape,
                    self.start_x, self.start_y, event.x, event.y
                )
    
    def on_mouse_up(self, event):
        if self.current_shape and self.doc and self.start_x and self.start_y:
            page = self.doc.load_page(self.current_page)
            
            # Get PDF coordinates
            pdf_width = page.rect.width
            pdf_height = page.rect.height
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Scale factors
            scale_x = pdf_width / canvas_width
            scale_y = pdf_height / canvas_height
            
            # Convert coordinates
            x1 = self.start_x * scale_x
            y1 = self.start_y * scale_y
            x2 = event.x * scale_x
            y2 = event.y * scale_y
            
            # Create annotation
            if self.shape_type == "circle":
                rect = fitz.Rect(x1, y1, x2, y2)
                annot = page.add_circle_annot(rect)
            elif self.shape_type == "rectangle":
                rect = fitz.Rect(x1, y1, x2, y2)
                annot = page.add_rect_annot(rect)
            
            # Set annotation properties
            annot.set_colors(stroke=self.annotation_color)
            annot.set_border(width=1)
            annot.update()
            
            # Store annotation info for undo
            annotation_info = {
                "page_num": self.current_page,
                "annot": annot,
                "rect": rect,
                "type": self.shape_type
            }
            self.annotation_history.append(annotation_info)
            self.current_annotations.append(annotation_info)
            
            self.update_undo_button_state()
            
        self.current_shape = None
        self.start_x = None
        self.start_y = None
    
    def undo_last_annotation(self):
        if not self.annotation_history:
            return
            
        # Get the last annotation
        last_annotation = self.annotation_history.pop()
        
        # Remove from current annotations if it's on this page
        if last_annotation in self.current_annotations:
            self.current_annotations.remove(last_annotation)
        
        # Get the page and annotation
        page = self.doc.load_page(last_annotation["page_num"])
        annot = last_annotation["annot"]
        
        # Delete the annotation
        page.delete_annot(annot)
        
        # Redraw the page
        if last_annotation["page_num"] == self.current_page:
            self.display_page()
        
        self.update_undo_button_state()
    
    def update_undo_button_state(self):
        if self.annotation_history:
            self.undo_btn.config(state=tk.NORMAL)
        else:
            self.undo_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = PDFAnnotator(root)
    root.mainloop()

if __name__ == "__main__":
    main()