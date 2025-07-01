import os
import fitz  # PyMuPDF
from PIL import Image
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def extract_images_from_pdf(pdf_path):
    """Extract the first image from a PDF file"""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0) 
    pixmap = page.get_pixmap(dpi=300) 
    image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    width, height = image.size
    box = (0, 0, width, height // 2) 
    cropped_image_top = image.crop(box)
    return cropped_image_top

def merge_images_on_a4(cropped_image_top, cropped_image_bottom, output_path):
    """Crop top half of each image and merge onto A4-sized canvas"""
    try:
        a4_width, a4_height = 2480, 3508 
        a4_image = Image.new('RGB', (a4_width, a4_height), 'white')
        
        max_width = a4_width

        width_top, height_top = cropped_image_top.size
        width_bottom, height_bottom = cropped_image_bottom.size

        if width_top > max_width:
            aspect_ratio_top = width_top / height_top
            new_height_top = int(max_width / aspect_ratio_top)
            resized_image_top = cropped_image_top.resize((max_width, new_height_top), Image.LANCZOS)
        else:
            resized_image_top = cropped_image_top

        if width_bottom > max_width:
            aspect_ratio_bottom = width_bottom / height_bottom
            new_height_bottom = int(max_width / aspect_ratio_bottom)
            resized_image_bottom = cropped_image_bottom.resize((max_width, new_height_bottom), Image.LANCZOS)
        else:
            resized_image_bottom = cropped_image_bottom
        
        a4_image.paste(resized_image_top, (0, 0)) 
        a4_image.paste(resized_image_bottom, (100, resized_image_top.height - 100))
        
        cropped = a4_image.crop((850, 3000, 1300, 3250))
        
        a4_image.paste(cropped,(100,100))
        
        a4_image.save(output_path)
            
        return True
    
    except Exception as e:
        print(f"Error merging images: {e}")
        return False

class CourierSlipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Courier Slip Converter")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Set icon (optional)
        # self.root.iconbitmap("icon.ico")  # Add your icon file if available
        
        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        
        # Variables
        self.manifest_path = tk.StringVar()
        self.label_path = tk.StringVar()
        self.output_path = tk.StringVar(value="C:/Users/usar/Videos/courier_slip.png")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF to Courier Slip Converter", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # File selection frames
        manifest_frame = ttk.Frame(main_frame)
        manifest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(manifest_frame, text="Manifest PDF:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(manifest_frame, textvariable=self.manifest_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(manifest_frame, text="Browse...", command=self.browse_manifest).pack(side=tk.LEFT, padx=(10, 0))
        
        label_frame = ttk.Frame(main_frame)
        label_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(label_frame, text="Label PDF:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(label_frame, textvariable=self.label_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(label_frame, text="Browse...", command=self.browse_label).pack(side=tk.LEFT, padx=(10, 0))
        
        # Output file frame
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output File:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT, padx=(10, 0))
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.output_format = tk.StringVar(value="png")
        ttk.Label(options_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(options_frame, text="PNG", variable=self.output_format, value="png").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(options_frame, text="PDF", variable=self.output_format, value="pdf").pack(side=tk.LEFT, padx=10)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Generate Courier Slip", command=self.process_pdfs)
        self.process_button.pack(pady=20)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def browse_manifest(self):
        filename = filedialog.askopenfilename(
            title="Select Manifest PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.manifest_path.set(filename)
    
    def browse_label(self):
        filename = filedialog.askopenfilename(
            title="Select Label PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.label_path.set(filename)
    
    def browse_output(self):
        file_ext = "*.pdf" if self.output_format.get() == "pdf" else "*.png"
        default_ext = ".pdf" if self.output_format.get() == "pdf" else ".png"
        filename = filedialog.asksaveasfilename(
            title="Save Courier Slip As",
            filetypes=[(f"{self.output_format.get().upper()} files", file_ext), ("All files", "*.*")],
            defaultextension=default_ext
        )
        if filename:
            self.output_path.set(filename)
    
    def update_output_extension(self):
        current_path = self.output_path.get()
        if current_path:
            base_name = os.path.splitext(current_path)[0]
            new_ext = ".pdf" if self.output_format.get() == "pdf" else ".png"
            self.output_path.set(base_name + new_ext)
    
    def process_pdfs(self):
        # Check if files are selected
        if not self.manifest_path.get() or not self.label_path.get():
            messagebox.showerror("Error", "Please select both PDF files")
            return
        
        # Check if output path is set
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output file path")
            return
        
        # Update UI
        self.status_var.set("Processing...")
        self.process_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        # Run processing in a separate thread to avoid UI freezing
        threading.Thread(target=self._process_pdfs_thread, daemon=True).start()
    
    def _process_pdfs_thread(self):
        try:
            # Extract images
            self.status_var.set("Extracting images from PDFs...")
            manifest_image = extract_images_from_pdf(self.manifest_path.get())
            label_image = extract_images_from_pdf(self.label_path.get())
            
            if manifest_image is None or label_image is None:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to extract images from PDFs"))
                return
            
            # Merge images
            self.status_var.set("Merging images...")
            output_path = self.output_path.get()
            merge_result = merge_images_on_a4(manifest_image, label_image, output_path)
            
            if merge_result:
                # Success
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Process completed successfully!\nOutput saved as:\n{output_path}"))
                self.status_var.set(f"Saved to: {output_path}")
            else:
                # Error
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to merge images"))
                self.status_var.set("Error occurred during processing")
        
        except Exception as e:
            # Handle any exceptions
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.status_var.set("Error occurred")
        
        finally:
            # Reset UI
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL))

def main():
    root = tk.Tk()
    app = CourierSlipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()