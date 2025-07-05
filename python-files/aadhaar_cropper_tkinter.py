import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
import fitz  # PyMuPDF
import numpy as np
from pdf2image import convert_from_bytes
import threading
import tempfile
from PIL import Image, ImageTk
import shutil

class AadhaarCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aadhaar PDF Auto Cropper")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.selected_file = tk.StringVar()
        self.password_var = tk.StringVar()
        self.processing = False
        
        # Create output directory
        self.output_dir = "cropped_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 Aadhaar PDF Auto Cropper", 
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Upload Aadhaar PDF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=1)
        
        # Password field
        ttk.Label(main_frame, text="🔒 PDF Password (if required):").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="✂️ Crop Aadhaar Front and Back", 
                                     command=self.process_pdf, style="Accent.TButton")
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to process PDF")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        self.results_frame.grid_remove()  # Hide initially
        
        # Configure results frame grid
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(1, weight=1)
        
        # Front image
        front_frame = ttk.Frame(self.results_frame)
        front_frame.grid(row=0, column=0, padx=5)
        ttk.Label(front_frame, text="Front Side", font=("Segoe UI", 12, "bold")).pack()
        self.front_image_label = ttk.Label(front_frame, text="No image")
        self.front_image_label.pack(pady=5)
        self.front_download_btn = ttk.Button(front_frame, text="Download Front", 
                                            command=lambda: self.download_image("01_Aadhaar_Front.png"))
        self.front_download_btn.pack(pady=5)
        
        # Back image
        back_frame = ttk.Frame(self.results_frame)
        back_frame.grid(row=0, column=1, padx=5)
        ttk.Label(back_frame, text="Back Side", font=("Segoe UI", 12, "bold")).pack()
        self.back_image_label = ttk.Label(back_frame, text="No image")
        self.back_image_label.pack(pady=5)
        self.back_download_btn = ttk.Button(back_frame, text="Download Back", 
                                           command=lambda: self.download_image("02_Aadhaar_Back.png"))
        self.back_download_btn.pack(pady=5)
        
        # Process another button
        self.process_another_btn = ttk.Button(self.results_frame, text="Process Another PDF", 
                                             command=self.reset_ui)
        self.process_another_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Configure main frame grid weights
        main_frame.rowconfigure(6, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Aadhaar PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
            
    def cm_to_px(self, cm, dpi=600):
        return int((cm / 2.54) * dpi)
        
    def process_pdf(self):
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
            
        if self.processing:
            return
            
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Processing PDF...")
        
        # Run processing in a separate thread
        thread = threading.Thread(target=self.process_pdf_thread)
        thread.daemon = True
        thread.start()
        
    def process_pdf_thread(self):
        try:
            file_path = self.selected_file.get()
            password = self.password_var.get()
            
            # Read PDF
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()

            doc = fitz.open("pdf", pdf_bytes)

            if doc.needs_pass and not doc.authenticate(password):
                self.root.after(0, lambda: messagebox.showerror("Error", "Incorrect password"))
                return

            pdf_data = doc.write()
            images = convert_from_bytes(pdf_data, dpi=600, first_page=1, last_page=1)
            img = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)

            h, w, _ = img.shape

            # Front crop
            f_top = self.cm_to_px(20.3)
            f_bottom = self.cm_to_px(2.03)
            f_left = self.cm_to_px(1.8)
            f_right = self.cm_to_px(11.0)
            front = img[f_top:h - f_bottom, f_left:w - f_right]

            # Back crop
            b_top = self.cm_to_px(20.3)
            b_bottom = self.cm_to_px(2.03)
            b_left = self.cm_to_px(11.0)
            b_right = self.cm_to_px(1.8)
            back = img[b_top:h - b_bottom, b_left:w - b_right]

            front_path = os.path.join(self.output_dir, '01_Aadhaar_Front.png')
            back_path = os.path.join(self.output_dir, '02_Aadhaar_Back.png')
            
            cv2.imwrite(front_path, front)
            cv2.imwrite(back_path, back)

            # Update UI in main thread
            self.root.after(0, lambda: self.show_results(front_path, back_path))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error processing file: {str(e)}"))
        finally:
            self.root.after(0, self.processing_finished)
            
    def processing_finished(self):
        self.processing = False
        self.process_btn.config(state="normal")
        self.progress.stop()
        self.status_label.config(text="Ready to process PDF")
        
    def show_results(self, front_path, back_path):
        # Display images
        try:
            # Front image
            front_img = Image.open(front_path)
            front_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            front_photo = ImageTk.PhotoImage(front_img)
            self.front_image_label.config(image=front_photo, text="")
            self.front_image_label.image = front_photo
            
            # Back image
            back_img = Image.open(back_path)
            back_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            back_photo = ImageTk.PhotoImage(back_img)
            self.back_image_label.config(image=back_photo, text="")
            self.back_image_label.image = back_photo
            
            # Show results
            self.results_frame.grid()
            self.status_label.config(text="Processing completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying results: {str(e)}")
            
    def download_image(self, filename):
        source_path = os.path.join(self.output_dir, filename)
        if os.path.exists(source_path):
            save_path = filedialog.asksaveasfilename(
                title=f"Save {filename}",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialname=filename
            )
            if save_path:
                try:
                    shutil.copy2(source_path, save_path)
                    messagebox.showinfo("Success", f"File saved to: {save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error saving file: {str(e)}")
        else:
            messagebox.showerror("Error", "Image file not found")
            
    def reset_ui(self):
        self.selected_file.set("")
        self.password_var.set("")
        self.results_frame.grid_remove()
        self.status_label.config(text="Ready to process PDF")
        self.front_image_label.config(image="", text="No image")
        self.back_image_label.config(image="", text="No image")

def main():
    root = tk.Tk()
    app = AadhaarCropperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 