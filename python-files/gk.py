import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import random
import pytz
import os
import subprocess
import sys
from pathlib import Path

def check_and_install_modules():
    """Check and install required modules if not available"""
    required_modules = {
        'pyexiv2': 'pyexiv2'
    }
    
    missing_modules = []
    
    # Check each required module
    for module_name, install_name in required_modules.items():
        try:
            __import__(module_name)
            print(f"✓ {module_name} is already installed")
        except ImportError:
            missing_modules.append((module_name, install_name))
            print(f"✗ {module_name} is not installed")
    
    # Install missing modules
    if missing_modules:
        print("\nInstalling missing modules...")
        for module_name, install_name in missing_modules:
            try:
                print(f"Installing {module_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])
                print(f"✓ {module_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {module_name}: {e}")
                messagebox.showerror(
                    "Installation Error", 
                    f"Failed to install {module_name}. Please install it manually using:\npip install {install_name}"
                )
                return False
    else:
        print("All required modules are already installed.")
    
    return True

# Check and install modules before importing
if not check_and_install_modules():
    sys.exit(1)

# Now import the module that might have been just installed
try:
    import pyexiv2
except ImportError:
    messagebox.showerror(
        "Import Error", 
        "Failed to import pyexiv2 after installation. Please restart the application."
    )
    sys.exit(1)

class ImageMetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Metadata Updater")
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(520, 600)
        
        # Style configuration
        self.style = ttk.Style()
        
        # Configure consistent padding and spacing
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', padding=5, font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10), padding=(0, 5))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('TLabelframe', padding=(20, 10))
        self.style.configure('TLabelframe.Label', padding=(0, 10))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with consistent 20px padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Header
        header_label = ttk.Label(
            main_frame, 
            text="Image Metadata Updater", 
            style='Header.TLabel'
        )
        header_label.pack(pady=(0, 20))
        
        # Input Frame
        input_label = ttk.Label(main_frame, text="Input Settings", padding=(15, 5))
        input_frame = ttk.LabelFrame(main_frame, labelwidget=input_label)
        input_frame.pack(fill='x', pady=(10, 20))
        
        # Keywords Input
        keyword_frame = ttk.Frame(input_frame)
        keyword_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(keyword_frame, text="Keywords:").pack(side='left', padx=(0, 10))
        self.keywords_entry = ttk.Entry(keyword_frame)
        self.keywords_entry.pack(side='left', fill='x', expand=True)
        
        # Domain Input
        domain_frame = ttk.Frame(input_frame)
        domain_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(domain_frame, text="Domain:").pack(side='left', padx=(0, 10))
        self.domain_entry = ttk.Entry(domain_frame)
        self.domain_entry.insert(0, "kohkono.com")  # Default value
        self.domain_entry.pack(side='left', fill='x', expand=True)
        
        # Author Input
        author_frame = ttk.Frame(input_frame)
        author_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(author_frame, text="Author:").pack(side='left', padx=(0, 10))
        self.author_entry = ttk.Entry(author_frame)
        self.author_entry.insert(0, "Ganden Kohkono")  # Default value
        self.author_entry.pack(side='left', fill='x', expand=True)
        
        # Email Input
        email_frame = ttk.Frame(input_frame)
        email_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(email_frame, text="Email:").pack(side='left', padx=(0, 10))
        self.email_entry = ttk.Entry(email_frame)
        self.email_entry.insert(0, "gandenkohkono@gmail.com")  # Default value
        self.email_entry.pack(side='left', fill='x', expand=True)
        
        # Photoshop Version Dropdown
        version_frame = ttk.Frame(input_frame)
        version_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(version_frame, text="Photoshop Version:").pack(side='left', padx=(0, 10))
        self.version_var = tk.StringVar()
        version_options = [
            "Random (Acak)",
            "Lightroom 5.7.1 (Windows)",
            "CS5.1 Macintosh",
            "Lightroom 6.8 (Macintosh)",
            "CS6 (Windows)",
            "CS5 (12.0)",
            "CS6 (13.0)",
            "CC (14.0 - 22.0)",
        ]
        self.version_combo = ttk.Combobox(version_frame, textvariable=self.version_var, 
                                         values=version_options, state="readonly")
        self.version_combo.set(version_options[0])  # Default to Random
        self.version_combo.pack(side='left', fill='x', expand=True)
        
        # Instructions Input
        instruction_frame = ttk.Frame(input_frame)
        instruction_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(instruction_frame, text="Instructions:").pack(anchor='w', padx=(0, 10))
        self.instruction_text = tk.Text(instruction_frame, height=3, wrap=tk.WORD)
        self.instruction_text.insert('1.0', "Dilarang menggunakan gambar ini untuk tujuan komersial tanpa izin dari #domain#.")
        self.instruction_text.pack(fill='x', pady=(5, 0))
        
        # Folder Selection
        folder_frame = ttk.Frame(input_frame)
        folder_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(folder_frame, text="Input Folder:").pack(side='left', padx=(0, 10))
        self.folder_path_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path_var)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side='right')
        
        # Process Button - centered
        process_btn = ttk.Button(
            main_frame,
            text="Update Metadata",
            command=self.process_images,
            style='TButton'
        )
        process_btn.pack(pady=20)
        
        # Progress Frame
        progress_label = ttk.Label(main_frame, text="Progress", padding=(15, 5))
        progress_frame = ttk.LabelFrame(main_frame, labelwidget=progress_label)
        progress_frame.pack(fill='x')
        
        # Progress Label and Bar - centered
        self.progress_var = tk.StringVar(value="Ready to process...")
        progress_label = ttk.Label(
            progress_frame, 
            textvariable=self.progress_var,
            anchor='center',
            justify='center'
        )
        progress_label.pack(padx=20, pady=10, fill='x')
        
        # Progress Bar - centered with consistent width
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            length=440
        )
        self.progress_bar.pack(padx=20, pady=(0, 10))
        
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_var.set(folder_path)
            
    def process_images(self):
        folder_path = self.folder_path_var.get()
        keywords = self.keywords_entry.get()
        domain = self.domain_entry.get()
        author = self.author_entry.get()
        email = self.email_entry.get()
        version = self.version_var.get()
        instructions = self.instruction_text.get('1.0', tk.END).strip()
        
        if not folder_path or not keywords or not domain or not author or not email:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
            
        try:
            jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]
            if not jpg_files:
                messagebox.showinfo("Info", "No JPG files found in the selected folder")
                return
                
            self.progress_bar['maximum'] = len(jpg_files)
            self.progress_bar['value'] = 0
            
            # Generate timestamps
            zona_id = pytz.timezone('Asia/Jakarta')
            w_id = datetime.now(zona_id)
            w_skrg = w_id.strftime('%Y-%m-%dT%H:%M:%S').split('T')
            rilis_tgl = w_skrg[0]
            rilis_jam = w_skrg[1]+'+02:00'

            w_mundur = random.randint(3, 7)
            w_mundur_obj = w_id - timedelta(days=w_mundur)
            w_mundur_str = w_mundur_obj.strftime('%Y-%m-%dT%H:%M:%S').split('T')
            imgrilis_date = w_mundur_str[0]
            imgrilis_time = w_mundur_str[1]+'+02:00'
            
            for idx, filename in enumerate(jpg_files):
                full_path = os.path.join(folder_path, filename)
                jpg_filename = os.path.splitext(filename)[0]
                
                self.progress_var.set(f"Processing: {filename}")
                self.root.update()
                
                # Only update metadata
                self.set_custom_iptc(
                    full_path, 
                    imgrilis_date, 
                    imgrilis_time, 
                    rilis_tgl, 
                    rilis_jam, 
                    jpg_filename, 
                    keywords, 
                    jpg_filename,
                    domain,
                    author,
                    email,
                    version,
                    instructions
                )
                
                self.progress_bar['value'] = idx + 1
                self.root.update()
                
            self.progress_var.set("Metadata update complete!")
            messagebox.showinfo("Success", "Image metadata updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.progress_var.set("Processing failed!")
            
    def set_custom_iptc(self, image_path, tahun_created, jam_created, tahun_rilis, 
                       jam_rilis, file_name, kata_kunci, judul_post, domain, 
                       sengmoto, email, versi_photoshop, instruksi):
        
        website = f'https://www.{domain}'
        
        # Handle random version selection
        if versi_photoshop == "Random (Acak)":
            version_options = [
                "Lightroom 5.7.1 (Windows)",
                "CS5.1 Macintosh",
                "Lightroom 6.8 (Macintosh)",
                "CS6 (Windows)",
                "CS5 (12.0)",
                "CS6 (13.0)",
                "CC (14.0 - 22.0)",
            ]
            versi_photoshop = random.choice(version_options)
        
        # Replace #domain# placeholder in instructions
        izin = instruksi.replace('#domain#', domain)
        
        metadata = pyexiv2.Image(image_path)

        kata_kunci = kata_kunci.split(',')
        kata_kunci = [item.strip() for item in kata_kunci]
        random.shuffle(kata_kunci)
        kata_kunci = ', '.join(kata_kunci)
        
        iptc_data = {
            "Iptc.Application2.ObjectName": file_name,
            "Iptc.Application2.Headline": file_name,
            "Iptc.Application2.Keywords": kata_kunci,
            "Iptc.Application2.Caption": judul_post,
            "Iptc.Application2.DateCreated": tahun_created,
            "Iptc.Application2.TimeCreated": jam_created,
            "Iptc.Application2.ReleaseDate": tahun_rilis,
            "Iptc.Application2.ReleaseTime": jam_rilis,
            "Iptc.Application2.Copyright": domain,
            "Iptc.Application2.Byline": sengmoto,
            "Iptc.Application2.BylineTitle": "Owner",
            "Iptc.Application2.Credit": domain,
            "Iptc.Application2.Source": website,
            "Iptc.Application2.Contact": email,
            "Iptc.Application2.Program": "Adobe Photoshop",
            "Iptc.Application2.ProgramVersion": versi_photoshop,
            "Iptc.Application2.SpecialInstructions": izin
        }
        metadata.modify_iptc(iptc_data)
        metadata.close()

def main():
    root = tk.Tk()
    app = ImageMetadataApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()