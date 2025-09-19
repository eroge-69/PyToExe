import tkinter as tk
from tkinter import filedialog, messagebox
from customtkinter import CTkImage
import customtkinter as ctk
from PIL import Image, ImageGrab, ImageTk
import pytesseract
import os
import threading
import tempfile
import sys
import base64
import io

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Function to load embedded image for PyInstaller
def load_image(image_path):
    # If we're running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # We'll embed the image as base64 to include it in the executable
        # For now, we'll try to load from the temporary directory
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, image_path)

class Image2TextConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Image2Text - Image to Text Converter")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Try to set the window icon
        try:
            icon_path = load_image("logo.ico")
            self.iconbitmap(icon_path)
        except:
            pass  # Continue without icon if there's an error
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create custom font
        self.title_font = ctk.CTkFont(family="Comic Sans MS", size=24, weight="bold")
        self.button_font = ctk.CTkFont(family="Chalkboard", size=14, weight="bold")
        self.text_font = ctk.CTkFont(family="Courier New", size=12)
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Try to add logo
        try:
            logo_path = load_image("logo.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((40, 40), Image.LANCZOS)
            logo_photo = CTkImage(light_image=logo_image, dark_image=logo_image, size=(40, 40))
            
            logo_label = ctk.CTkLabel(self.header_frame, image=logo_photo, text="")
            logo_label.image = logo_photo  # Keep a reference
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except Exception as e:
            print(f"Logo loading error: {e}")
            # Create a placeholder if logo can't be loaded
            logo_label = ctk.CTkLabel(self.header_frame, text="📷", font=ctk.CTkFont(size=24))
            logo_label.grid(row=0, column=0, padx=(0, 10))
        
        # Title label with neon effect
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Image2Text - Image to Text Converter",
            font=self.title_font,
            text_color="#00ffff"  # Cyan neon color
        )
        self.title_label.grid(row=0, column=1, pady=10, sticky="w")
        
        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create button frame
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Upload button with neon effect
        self.upload_btn = ctk.CTkButton(
            self.button_frame,
            text="📁 Upload Images",
            command=self.upload_images,
            font=self.button_font,
            fg_color="#2b2b2b",
            border_width=2,
            border_color="#00ffff",
            hover_color="#00ffff",
            text_color="#00ffff"
        )
        self.upload_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Paste from clipboard button with neon effect
        self.paste_btn = ctk.CTkButton(
            self.button_frame,
            text="📋 Paste from Clipboard",
            command=self.paste_from_clipboard,
            font=self.button_font,
            fg_color="#2b2b2b",
            border_width=2,
            border_color="#ff00ff",
            hover_color="#ff00ff",
            text_color="#ff00ff"
        )
        self.paste_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Clear button with neon effect
        self.clear_btn = ctk.CTkButton(
            self.button_frame,
            text="🗑️ Clear",
            command=self.clear_text,
            font=self.button_font,
            fg_color="#2b2b2b",
            border_width=2,
            border_color="#ff5555",
            hover_color="#ff5555",
            text_color="#ff5555"
        )
        self.clear_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Copy button with neon effect
        self.copy_btn = ctk.CTkButton(
            self.button_frame,
            text="📋 Copy Text",
            command=self.copy_to_clipboard,
            font=self.button_font,
            fg_color="#2b2b2b",
            border_width=2,
            border_color="#55ff55",
            hover_color="#55ff55",
            text_color="#55ff55"
        )
        self.copy_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Configure button frame columns
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)
        
        # Create text output frame
        self.text_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.text_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)
        
        # Text output box with scrollbar
        self.text_output = ctk.CTkTextbox(
            self.text_frame, 
            font=self.text_font,
            fg_color="#1a1a1a",
            text_color="#ffffff",
            border_width=2,
            border_color="#444444",
            wrap="word"
        )
        self.text_output.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar
        self.scrollbar = ctk.CTkScrollbar(self.text_frame, command=self.text_output.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_output.configure(yscrollcommand=self.scrollbar.set)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Ready to convert images to text",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.status_bar.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Add a welcome message
        self.text_output.insert("1.0", "Welcome to Image2Text!\n\n")
        self.text_output.insert("end", "• Click 'Upload Images' to select image files\n")
        self.text_output.insert("end", "• Click 'Paste from Clipboard' to extract text from a screenshot\n")
        self.text_output.insert("end", "• Use 'Copy Text' to copy the extracted text\n")
        self.text_output.insert("end", "• Use 'Clear' to reset the text area\n")
        
        # Configure tesseract path (if needed)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def is_image_file(self, filename):
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp']
        return any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    def upload_images(self):
        filetypes = (
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp"),
            ("All files", "*.*")
        )
        
        filenames = filedialog.askopenfilenames(
            title="Select images to convert",
            filetypes=filetypes
        )
        
        if filenames:
            self.process_images(filenames)
    
    def paste_from_clipboard(self):
        try:
            # Try to get image from clipboard
            image = ImageGrab.grabclipboard()
            
            if image is None:
                messagebox.showinfo("No Image", "No image found in clipboard.")
                return
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temporary file and process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_path = temp_file.name
                image.save(temp_path, "JPEG")
            
            self.process_images([temp_path])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process clipboard image: {str(e)}")
    
    def process_images(self, image_paths):
        # Show processing status
        self.status_bar.configure(text="Processing images...")
        self.text_output.delete("1.0", "end")
        self.text_output.insert("end", "Extracting text from images...\n\n")
        
        # Process in a separate thread to avoid freezing the UI
        thread = threading.Thread(target=self.ocr_process, args=(image_paths,))
        thread.daemon = True
        thread.start()
    
    def ocr_process(self, image_paths):
        try:
            full_text = ""
            
            for i, image_path in enumerate(image_paths):
                # Update status
                self.after(0, lambda: self.status_bar.configure(
                    text=f"Processing image {i+1} of {len(image_paths)}: {os.path.basename(image_path)}"
                ))
                
                try:
                    # Open and process the image
                    image = Image.open(image_path)
                    
                    # Perform OCR
                    text = pytesseract.image_to_string(image)
                    
                    # Add to result
                    if len(image_paths) > 1:
                        full_text += f"--- Text from {os.path.basename(image_path)} ---\n\n"
                    
                    full_text += text + "\n\n"
                    
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(image_path)}: {str(e)}\n\n"
                    full_text += error_msg
            
            # Update the text box in the main thread
            self.after(0, lambda: self.display_results(full_text, image_paths))
            
        except Exception as e:
            self.after(0, lambda: self.display_error(f"Error during OCR processing: {str(e)}"))
    
    def display_results(self, text, image_paths):
        self.text_output.delete("1.0", "end")
        self.text_output.insert("end", text)
        
        # Clean up temporary files
        for path in image_paths:
            if path.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(path)
                except:
                    pass
        
        self.status_bar.configure(text=f"Successfully processed {len(image_paths)} image(s)")
    
    def display_error(self, error_msg):
        self.text_output.delete("1.0", "end")
        self.text_output.insert("end", f"Error: {error_msg}")
        self.status_bar.configure(text="Error occurred during processing")
    
    def clear_text(self):
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", "Welcome to Image2Text!\n\n")
        self.text_output.insert("end", "• Click 'Upload Images' to select image files\n")
        self.text_output.insert("end", "• Click 'Paste from Clipboard' to extract text from a screenshot\n")
        self.text_output.insert("end", "• Use 'Copy Text' to copy the extracted text\n")
        self.text_output.insert("end", "• Use 'Clear' to reset the text area\n")
        self.status_bar.configure(text="Text cleared")
    
    def copy_to_clipboard(self):
        text = self.text_output.get("1.0", "end-1c")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_bar.configure(text="Text copied to clipboard")
        else:
            messagebox.showinfo("No Text", "No text to copy.")

if __name__ == "__main__":
    app = Image2TextConverter()
    app.mainloop()
