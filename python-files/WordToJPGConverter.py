import os
import sys
import subprocess
import requests
import zipfile
import shutil
import time
import tempfile
import comtypes.client
from pathlib import Path
from pdf2image import convert_from_path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from threading import Thread
import webbrowser

# Poppler version for Windows
POPPLER_VERSION = "24.08.0"
POPPLER_URL = f"https://github.com/oschwartz10612/poppler-windows/releases/download/v{POPPLER_VERSION}-0/Release-{POPPLER_VERSION}-0.zip"

class WordToJPGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Word to JPG Converter")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Font settings
        self.font = ("Tahoma", 10)
        self.title_font = ("Tahoma", 12, "bold")
        
        # UI variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Ready to start")
        self.progress_value = tk.IntVar(value=0)
        
        # Create UI
        self.create_widgets()
        
        # Set color theme
        self.root.tk_setPalette(background="#f0f0f0", foreground="#333")
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Convert Microsoft Word Files to JPG Images", 
            font=self.title_font,
            anchor=tk.CENTER
        )
        title_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Input File", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        # File input
        ttk.Label(input_frame, text="Word File (.docx):", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        input_entry = ttk.Entry(input_frame, textvariable=self.input_file, width=50, font=self.font)
        input_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        browse_input_btn = ttk.Button(
            input_frame, 
            text="Browse File", 
            command=self.browse_input_file,
            width=12
        )
        browse_input_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Folder", padding=10)
        output_frame.pack(fill=tk.X, pady=5)
        
        # Output directory
        ttk.Label(output_frame, text="Save Images To:", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50, font=self.font)
        output_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        browse_output_btn = ttk.Button(
            output_frame, 
            text="Browse Folder", 
            command=self.browse_output_dir,
            width=12
        )
        browse_output_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar
        progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_value, 
            maximum=100, 
            mode='determinate'
        )
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Status
        status_label = ttk.Label(
            progress_frame, 
            textvariable=self.status, 
            font=self.font,
            anchor=tk.CENTER
        )
        status_label.pack(fill=tk.X, pady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            font=("Tahoma", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Convert button
        convert_btn = ttk.Button(
            button_frame, 
            text="Start Conversion", 
            command=self.start_conversion,
            width=15
        )
        convert_btn.pack(side=tk.LEFT, padx=5)
        
        # Open output button
        open_output_btn = ttk.Button(
            button_frame, 
            text="Open Output Folder", 
            command=self.open_output_dir,
            width=15
        )
        open_output_btn.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_btn = ttk.Button(
            button_frame, 
            text="Exit", 
            command=self.root.destroy,
            width=15
        )
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configure columns for resizing
        input_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(1, weight=1)
        
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Word File",
            filetypes=[("Word Files", "*.docx"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)
            
            # Set default output directory
            if not self.output_dir.get():
                output_path = os.path.join(os.path.dirname(file_path), "Output_Images")
                self.output_dir.set(output_path)
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Folder")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_status(self, message, progress=None):
        self.status.set(message)
        if progress is not None:
            self.progress_value.set(progress)
        self.log_message(message)
        self.root.update()
    
    def open_output_dir(self):
        output_dir = self.output_dir.get()
        if output_dir and os.path.exists(output_dir):
            try:
                if sys.platform == "win32":
                    os.startfile(output_dir)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", output_dir])
                else:
                    subprocess.Popen(["xdg-open", output_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Error opening folder: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Output folder doesn't exist or not selected")
    
    def start_conversion(self):
        input_file = self.input_file.get()
        output_dir = self.output_dir.get()
        
        # Validate inputs
        if not input_file:
            messagebox.showwarning("Warning", "Please select a Word file")
            return
        
        if not output_dir:
            messagebox.showwarning("Warning", "Please select an output folder")
            return
        
        if not input_file.endswith(".docx"):
            messagebox.showwarning("Warning", "Selected file must be a .docx file")
            return
        
        # Start conversion in a new thread
        self.log_message("-" * 50)
        self.log_message(f"Starting conversion: {os.path.basename(input_file)}")
        self.log_message(f"Output folder: {output_dir}")
        
        thread = Thread(target=self.convert_docx_to_jpg, args=(input_file, output_dir), daemon=True)
        thread.start()
    
    def install_poppler(self):
        """Automatically install Poppler for different OS"""
        try:
            self.update_status("Checking Poppler...", 10)
            
            if sys.platform == 'win32':
                # Poppler installation path
                poppler_dir = Path.home() / "poppler"
                poppler_dir.mkdir(exist_ok=True, parents=True)
                
                # ZIP file path
                zip_path = poppler_dir / "poppler.zip"
                
                # Download file
                self.update_status(f"Downloading Poppler version {POPPLER_VERSION}...", 20)
                response = requests.get(POPPLER_URL, stream=True)
                with open(zip_path, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    chunk_size = 8192
                    downloaded = 0
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = 20 + int(50 * downloaded / total_size)
                        self.update_status(f"Downloading Poppler: {downloaded//1024}KB/{total_size//1024}KB", progress)
                
                # Extract ZIP file
                self.update_status(f"Extracting Poppler to {poppler_dir}...", 70)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(poppler_dir)
                
                # Delete ZIP file
                os.remove(zip_path)
                
                # Final Poppler path
                poppler_bin = poppler_dir / f"poppler-{POPPLER_VERSION}" / "Library" / "bin"
                self.update_status("Poppler installed successfully", 90)
                return poppler_bin
            
            elif sys.platform == 'linux':
                # Install Poppler for Linux
                self.update_status("Installing poppler-utils for Linux...", 30)
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "poppler-utils"], check=True)
                self.update_status("poppler-utils installed successfully", 90)
                return None
            
            elif sys.platform == 'darwin':
                # Install Poppler for Mac
                self.update_status("Installing poppler for Mac...", 30)
                subprocess.run(["brew", "install", "poppler"], check=True)
                self.update_status("poppler installed successfully", 90)
                return None
        
        except Exception as e:
            self.log_message(f"Error installing Poppler: {str(e)}")
            return None
    
    def get_poppler_path(self):
        """Automatically find Poppler path"""
        try:
            self.update_status("Searching for Poppler...", 5)
            
            # Check if Poppler is in PATH
            if sys.platform == 'win32':
                check_cmd = ["where", "pdftoppm"]
            else:
                check_cmd = ["which", "pdftoppm"]
            
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message(f"Poppler found at: {result.stdout.strip()}")
                return None
        
        except:
            pass
        
        # Search common paths
        common_paths = {
            'win32': [
                Path.home() / "poppler" / f"poppler-{POPPLER_VERSION}" / "Library" / "bin",
                Path("C:") / "poppler" / f"poppler-{POPPLER_VERSION}" / "Library" / "bin",
                Path("C:") / "Program Files" / "poppler" / "bin"
            ],
            'linux': [
                Path("/usr/bin"),
                Path("/usr/local/bin")
            ],
            'darwin': [
                Path("/opt/homebrew/bin"),
                Path("/usr/local/bin")
            ]
        }
        
        for path in common_paths.get(sys.platform, []):
            bin_path = path / "pdftoppm.exe" if sys.platform == 'win32' else path / "pdftoppm"
            if bin_path.exists():
                self.log_message(f"Poppler found at system path: {path}")
                return str(path)
        
        # Auto-install if not found
        self.log_message("Poppler not found. Installing automatically...")
        return self.install_poppler()
    
    def convert_docx_to_pdf(self, input_docx, output_pdf):
        """Convert DOCX to PDF using Microsoft Word"""
        try:
            self.log_message("Starting Microsoft Word...")
            word = comtypes.client.CreateObject("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            
            self.log_message(f"Opening document: {input_docx}")
            doc = word.Documents.Open(os.path.abspath(input_docx))
            
            self.log_message(f"Saving as PDF: {output_pdf}")
            doc.SaveAs(os.path.abspath(output_pdf), FileFormat=17)  # 17 = PDF format
            
            self.log_message("Closing document...")
            doc.Close()
            
            self.log_message("Quitting Word...")
            word.Quit()
            
            # Delay to ensure Word closes completely
            time.sleep(2)
            
            # Release COM resources
            del word
            del doc
            
            return True
        except Exception as e:
            self.log_message(f"Error converting DOCX to PDF: {str(e)}")
            return False
    
    def convert_docx_to_jpg(self, input_docx, output_folder):
        """Convert Word file to JPG images"""
        try:
            # Create output folder if it doesn't exist
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Convert DOCX to PDF
            pdf_path = output_path / "temp_conversion.pdf"
            self.update_status("Converting DOCX to PDF...", 10)
            self.log_message(f"Input: {input_docx}")
            self.log_message(f"Temporary PDF: {pdf_path}")
            
            # Use Microsoft Word for conversion
            if not self.convert_docx_to_pdf(input_docx, str(pdf_path)):
                self.update_status("PDF conversion error", 100)
                messagebox.showerror("Error", "DOCX to PDF conversion failed")
                return []
            
            self.update_status("PDF conversion successful", 30)
            
            # Find Poppler path
            self.update_status("Preparing PDF converter...", 35)
            poppler_path = self.get_poppler_path()
            self.log_message(f"Poppler path: {poppler_path}")
            
            # Convert PDF to JPG
            self.update_status("Converting PDF to JPG images...", 40)
            images = convert_from_path(
                str(pdf_path),
                dpi=300,
                fmt='jpeg',
                jpegopt={"quality": 95},
                poppler_path=str(poppler_path) if poppler_path else None
            )
            
            # Save images
            base_name = Path(input_docx).stem
            output_files = []
            
            self.update_status(f"Saving {len(images)} images...", 70)
            for i, image in enumerate(images):
                img_path = output_path / f"{base_name}_page_{i+1}.jpg"
                image.save(img_path, "JPEG")
                output_files.append(str(img_path))
                self.log_message(f"Page {i+1} saved: {os.path.basename(img_path)}")
                progress = 70 + int(30 * (i+1) / len(images))
                self.update_status(f"Saving page {i+1}/{len(images)}", progress)
            
            # Delete temporary PDF
            try:
                pdf_path.unlink()
                self.log_message("Temporary PDF deleted")
            except Exception as e:
                self.log_message(f"Error deleting PDF file: {str(e)}")
            
            self.update_status("Conversion completed successfully!", 100)
            messagebox.showinfo(
                "Success", 
                f"Conversion completed successfully!\n\n{len(output_files)} images created in output folder"
            )
            
            return output_files
        
        except Exception as e:
            self.log_message(f"File conversion error: {str(e)}")
            self.update_status("Conversion error", 100)
            messagebox.showerror(
                "Error", 
                f"File conversion error:\n\n{str(e)}\n\nPlease check details in log"
            )
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = WordToJPGConverter(root)
    root.mainloop()