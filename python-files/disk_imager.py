import os
import sys
import time
import ftplib
import gzip
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from cryptography.fernet import Fernet
from concurrent.futures import ThreadPoolExecutor

class DiskImagerFTP:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Disk Imager with FTP")
        self.root.geometry("800x600")
        
        # Encryption key
        self.encryption_key = None
        self.encryption_enabled = tk.BooleanVar(value=False)
        self.compression_enabled = tk.BooleanVar(value=True)
        self.split_files_enabled = tk.BooleanVar(value=False)
        self.split_size = tk.IntVar(value=1024)  # MB
        
        # Setup logging
        self.setup_logging()
        self.create_widgets()
        
        # Thread control
        self.is_running = False
        self.cancel_requested = False
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='disk_imager.log',
            filemode='a'
        )
        self.logger = logging.getLogger()
    
    def create_widgets(self):
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Disk Imaging")
        
        # Drive selection
        ttk.Label(main_frame, text="Select Drive:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.drive_combobox = ttk.Combobox(main_frame, state="readonly")
        self.drive_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.refresh_drives()
        
        # Output file
        ttk.Label(main_frame, text="Output File:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_entry = ttk.Entry(main_frame)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Checkbutton(options_frame, text="Enable Compression", variable=self.compression_enabled).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Enable Encryption", variable=self.encryption_enabled, command=self.toggle_encryption).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Split Files", variable=self.split_files_enabled).grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(options_frame, text="Split Size (MB):").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.split_size, width=8).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # FTP Settings
        ftp_frame = ttk.LabelFrame(main_frame, text="FTP Settings")
        ftp_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(ftp_frame, text="Server:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.ftp_server_entry = ttk.Entry(ftp_frame)
        self.ftp_server_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(ftp_frame, text="Username:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.ftp_user_entry = ttk.Entry(ftp_frame)
        self.ftp_user_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(ftp_frame, text="Password:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.ftp_pass_entry = ttk.Entry(ftp_frame, show="*")
        self.ftp_pass_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(ftp_frame, text="Remote Path:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        self.ftp_path_entry = ttk.Entry(ftp_frame)
        self.ftp_path_entry.grid(row=3, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=tk.E)
        
        ttk.Button(button_frame, text="Start", command=self.start_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_process).pack(side=tk.LEFT, padx=5)
        
        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redirect logging to GUI
        self.setup_log_redirect()
    
    def setup_log_redirect(self):
        class LogRedirect:
            def __init__(self, text_widget, logger):
                self.text_widget = text_widget
                self.logger = logger
            
            def write(self, message):
                if message.strip():
                    self.text_widget.configure(state=tk.NORMAL)
                    self.text_widget.insert(tk.END, message)
                    self.text_widget.see(tk.END)
                    self.text_widget.configure(state=tk.DISABLED)
                    self.logger.info(message.strip())
            
            def flush(self):
                pass
        
        sys.stdout = LogRedirect(self.log_text, self.logger)
        sys.stderr = LogRedirect(self.log_text, self.logger)
    
    def refresh_drives(self):
        drives = self.get_available_drives()
        self.drive_combobox['values'] = drives
        if drives:
            self.drive_combobox.current(0)
    
    def get_available_drives(self):
        if sys.platform == 'win32':
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            return [d for d in drives if os.path.isdir(d)]
        else:
            return ['/']
    
    def browse_output(self):
        default_name = f"disk_image_{time.strftime('%Y%m%d%H%M%S')}.img"
        if self.compression_enabled.get():
            default_name += ".gz"
        
        file = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".img.gz" if self.compression_enabled.get() else ".img",
            filetypes=[
                ("Disk Images", "*.img"),
                ("Compressed Images", "*.img.gz"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file)
    
    def toggle_encryption(self):
        if self.encryption_enabled.get():
            key = simpledialog.askstring("Encryption Key", "Enter encryption key (leave empty to generate new):")
            if key is None:  # User cancelled
                self.encryption_enabled.set(False)
                return
            
            if not key:
                key = Fernet.generate_key().decode()
                messagebox.showinfo("Encryption Key", f"New encryption key generated:\n\n{key}\n\nSave this key to decrypt the image later!")
            
            self.encryption_key = key
    
    def start_process(self):
        if self.is_running:
            return
        
        drive = self.drive_combobox.get()
        output_file = self.output_entry.get()
        
        if not drive or not output_file:
            messagebox.showerror("Error", "Please select a drive and output file!")
            return
        
        ftp_server = self.ftp_server_entry.get()
        ftp_user = self.ftp_user_entry.get()
        ftp_pass = self.ftp_pass_entry.get()
        ftp_path = self.ftp_path_entry.get()
        
        self.is_running = True
        self.cancel_requested = False
        self.status_var.set("Starting...")
        
        # Run in separate thread
        threading.Thread(
            target=self.run_process,
            args=(drive, output_file, ftp_server, ftp_user, ftp_pass, ftp_path),
            daemon=True
        ).start()
    
    def cancel_process(self):
        if self.is_running:
            self.cancel_requested = True
            self.status_var.set("Cancelling...")
    
    def run_process(self, drive, output_file, ftp_server, ftp_user, ftp_pass, ftp_path):
        try:
            # Create image
            self.status_var.set("Creating disk image...")
            image_files = self.create_disk_image(drive, output_file)
            
            if not image_files or self.cancel_requested:
                return
            
            # Upload to FTP if configured
            if ftp_server:
                self.status_var.set("Uploading to FTP...")
                for file in image_files:
                    if self.cancel_requested:
                        break
                    self.upload_to_ftp(file, ftp_server, ftp_user, ftp_pass, ftp_path)
            
            if not self.cancel_requested:
                self.status_var.set("Completed successfully!")
                messagebox.showinfo("Success", "Disk imaging and upload completed successfully!")
            else:
                self.status_var.set("Cancelled by user")
        except Exception as e:
            self.logger.error(f"Error in process: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
        finally:
            self.is_running = False
            self.progress_var.set(0)
    
    def create_disk_image(self, drive, output_file):
        try:
            # Prepare output files
            if self.split_files_enabled.get():
                base_name, ext = os.path.splitext(output_file)
                if self.compression_enabled.get() and not ext.endswith('.gz'):
                    ext += '.gz'
                output_files = [f"{base_name}.part{num:03d}{ext}" for num in range(1000)]
            else:
                output_files = [output_file]
            
            # Open source device
            with open(r'\\.\%s' % drive.replace('\\', ''), 'rb') as source:
                # Get device size
                source.seek(0, os.SEEK_END)
                total_size = source.tell()
                source.seek(0)
                
                current_file_index = 0
                bytes_written_total = 0
                bytes_written_file = 0
                split_size = self.split_size.get() * 1024 * 1024  # Convert MB to bytes
                
                # Open first output file
                current_file = output_files[current_file_index]
                os.makedirs(os.path.dirname(current_file) or '.', exist_ok=True)
                
                # Prepare output stream with optional compression
                if self.compression_enabled.get():
                    out_file = gzip.open(current_file, 'wb')
                else:
                    out_file = open(current_file, 'wb')
                
                # Optional encryption
                if self.encryption_enabled.get():
                    cipher = Fernet(self.encryption_key.encode())
                
                buffer_size = 1024 * 1024  # 1MB buffer
                start_time = time.time()
                
                while True:
                    if self.cancel_requested:
                        out_file.close()
                        return None
                    
                    # Read data
                    data = source.read(buffer_size)
                    if not data:
                        break
                    
                    # Encrypt if enabled
                    if self.encryption_enabled.get():
                        data = cipher.encrypt(data)
                    
                    # Write data
                    out_file.write(data)
                    
                    # Update progress
                    bytes_written_total += len(data)
                    bytes_written_file += len(data)
                    
                    # Update progress bar
                    progress = (bytes_written_total / total_size) * 100
                    self.progress_var.set(progress)
                    self.status_var.set(
                        f"Creating image: {bytes_written_total//(1024*1024)}/{total_size//(1024*1024)} MB "
                        f"({progress:.1f}%) - File {current_file_index+1}/{len(output_files)}"
                    )
                    
                    # Split files if enabled and size reached
                    if (self.split_files_enabled.get() and 
                        bytes_written_file >= split_size and 
                        current_file_index < len(output_files) - 1):
                        out_file.close()
                        current_file_index += 1
                        bytes_written_file = 0
                        current_file = output_files[current_file_index]
                        
                        if self.compression_enabled.get():
                            out_file = gzip.open(current_file, 'wb')
                        else:
                            out_file = open(current_file, 'wb')
                
                out_file.close()
                
                # Return only the files that were actually written
                return output_files[:current_file_index+1]
        
        except Exception as e:
            self.logger.error(f"Error creating disk image: {str(e)}")
            raise
    
    def upload_to_ftp(self, file_path, server, username, password, remote_path):
        try:
            self.logger.info(f"Starting FTP upload of {file_path}")
            
            with ftplib.FTP(server, username, password) as ftp:
                ftp.set_pasv(True)  # Passive mode for better compatibility
                
                # Create remote directory if needed
                try:
                    ftp.cwd(remote_path)
                except ftplib.error_perm:
                    try:
                        ftp.mkd(remote_path)
                        ftp.cwd(remote_path)
                    except ftplib.error_perm as e:
                        self.logger.error(f"Failed to create remote directory: {str(e)}")
                        raise
                
                # Get file size for progress
                file_size = os.path.getsize(file_path)
                uploaded = 0
                start_time = time.time()
                
                # Custom callback for progress
                def callback(data):
                    nonlocal uploaded
                    uploaded += len(data)
                    
                    # Update progress every second to avoid GUI lag
                    if time.time() - start_time >= 1:
                        progress = (uploaded / file_size) * 100
                        self.progress_var.set(progress)
                        self.status_var.set(
                            f"Uploading {os.path.basename(file_path)}: "
                            f"{uploaded//(1024*1024)}/{file_size//(1024*1024)} MB ({progress:.1f}%)"
                        )
                        start_time = time.time()
                    
                    if self.cancel_requested:
                        raise ftplib.Error("Upload cancelled by user")
                
                # Start upload
                with open(file_path, 'rb') as f:
                    ftp.storbinary(f'STOR {os.path.basename(file_path)}', f, blocksize=1024*1024, callback=callback)
                
                self.logger.info(f"Successfully uploaded {file_path}")
        
        except Exception as e:
            self.logger.error(f"FTP upload failed: {str(e)}")
            raise

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskImagerFTP(root)
    root.mainloop()