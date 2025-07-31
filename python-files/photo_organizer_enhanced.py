import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import threading
import time

class PhotoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Photo Organizer")
        self.root.geometry("650x500")
        self.root.resizable(True, True)

        # Variables
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.action = tk.StringVar(value="move")
        self.duplicate_action = tk.StringVar(value="rename")
        self.date_source = tk.StringVar(value="exif")
        self.preview_mode = tk.BooleanVar(value=False)
        
        # Processing control
        self.is_processing = False
        self.stop_processing = False
        
        # Statistics
        self.stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'duplicates': 0
        }

        self.create_widgets()
        self.setup_styles()

    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # Configure button styles
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        style.configure('Browse.TButton', font=('Arial', 9))

    def create_widgets(self):
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Main")

        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")

        # --- MAIN TAB ---
        self.create_main_tab(main_frame)
        
        # --- SETTINGS TAB ---
        self.create_settings_tab(settings_frame)

    def create_main_tab(self, parent):
        # Directory Selection Frame
        dir_frame = ttk.LabelFrame(parent, text="Directory Selection", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)

        # Source Directory
        source_frame = ttk.Frame(dir_frame)
        source_frame.pack(fill="x", pady=2)
        ttk.Label(source_frame, text="Source Directory:", width=18).pack(side="left")
        ttk.Entry(source_frame, textvariable=self.source_dir, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(source_frame, text="Browse", command=self.browse_source, style='Browse.TButton').pack(side="right")

        # Destination Directory
        dest_frame = ttk.Frame(dir_frame)
        dest_frame.pack(fill="x", pady=2)
        ttk.Label(dest_frame, text="Destination Directory:", width=18).pack(side="left")
        ttk.Entry(dest_frame, textvariable=self.dest_dir, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest, style='Browse.TButton').pack(side="right")

        # Action Frame
        action_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)

        action_buttons_frame = ttk.Frame(action_frame)
        action_buttons_frame.pack(fill="x")

        ttk.Radiobutton(action_buttons_frame, text="Move Files", variable=self.action, value="move").pack(side="left", padx=10)
        ttk.Radiobutton(action_buttons_frame, text="Copy Files", variable=self.action, value="copy").pack(side="left", padx=10)
        ttk.Checkbutton(action_buttons_frame, text="Preview Mode (show changes without executing)", variable=self.preview_mode).pack(side="left", padx=20)

        # Control Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing, style='Action.TButton')
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing_func, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side="right", padx=5)

        # Progress Frame
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=2)

        self.progress_label = ttk.Label(progress_frame, text="Ready to process files")
        self.progress_label.pack(pady=2)

        # Statistics Frame
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        stats_inner_frame = ttk.Frame(stats_frame)
        stats_inner_frame.pack(fill="x")

        self.processed_label = ttk.Label(stats_inner_frame, text="Processed: 0")
        self.processed_label.pack(side="left", padx=10)

        self.skipped_label = ttk.Label(stats_inner_frame, text="Skipped: 0")
        self.skipped_label.pack(side="left", padx=10)

        self.errors_label = ttk.Label(stats_inner_frame, text="Errors: 0")
        self.errors_label.pack(side="left", padx=10)

        self.duplicates_label = ttk.Label(stats_inner_frame, text="Duplicates: 0")
        self.duplicates_label.pack(side="left", padx=10)

        # Log Frame
        log_frame = ttk.LabelFrame(parent, text="Processing Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create text widget with scrollbar
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_settings_tab(self, parent):
        # Date Source Frame
        date_frame = ttk.LabelFrame(parent, text="Date Source Priority", padding=10)
        date_frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(date_frame, text="EXIF Date (recommended for photos)", variable=self.date_source, value="exif").pack(anchor="w", pady=2)
        ttk.Radiobutton(date_frame, text="File Creation Date", variable=self.date_source, value="creation").pack(anchor="w", pady=2)
        ttk.Radiobutton(date_frame, text="File Modification Date", variable=self.date_source, value="modification").pack(anchor="w", pady=2)

        # Duplicate Handling Frame
        duplicate_frame = ttk.LabelFrame(parent, text="Duplicate File Handling", padding=10)
        duplicate_frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(duplicate_frame, text="Rename duplicate files (filename_1.jpg)", variable=self.duplicate_action, value="rename").pack(anchor="w", pady=2)
        ttk.Radiobutton(duplicate_frame, text="Skip duplicate files", variable=self.duplicate_action, value="skip").pack(anchor="w", pady=2)
        ttk.Radiobutton(duplicate_frame, text="Overwrite existing files", variable=self.duplicate_action, value="overwrite").pack(anchor="w", pady=2)

        # File Extensions Frame
        ext_frame = ttk.LabelFrame(parent, text="Supported File Extensions", padding=10)
        ext_frame.pack(fill="x", padx=10, pady=5)

        extensions_text = "Photos: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .tif, .webp\nRAW: .cr2, .nef, .arw, .dng, .orf, .rw2"
        ttk.Label(ext_frame, text=extensions_text, justify="left").pack(anchor="w")

    def browse_source(self):
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_dir.set(directory)

    def browse_dest(self):
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dest_dir.set(directory)

    def get_photo_date(self, filepath):
        """Extract date from photo using multiple methods"""
        try:
            if self.date_source.get() == "exif":
                # Try EXIF first
                try:
                    with Image.open(filepath) as img:
                        exif = img._getexif()
                        if exif:
                            for tag_id, value in exif.items():
                                tag = TAGS.get(tag_id, tag_id)
                                if tag == "DateTime" or tag == "DateTimeOriginal":
                                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                except:
                    pass
                
                # Fall back to file dates if EXIF fails
                timestamp = os.path.getctime(filepath)
                return datetime.fromtimestamp(timestamp)
            
            elif self.date_source.get() == "creation":
                timestamp = os.path.getctime(filepath)
                return datetime.fromtimestamp(timestamp)
            
            elif self.date_source.get() == "modification":
                timestamp = os.path.getmtime(filepath)
                return datetime.fromtimestamp(timestamp)
                
        except Exception as e:
            self.log(f"Error getting date for {os.path.basename(filepath)}: {e}")
            return None

    def get_unique_filename(self, dest_path):
        """Generate a unique filename if file already exists"""
        if not os.path.exists(dest_path):
            return dest_path
        
        directory = os.path.dirname(dest_path)
        filename = os.path.basename(dest_path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)

    def update_stats(self):
        """Update statistics display"""
        self.processed_label.config(text=f"Processed: {self.stats['processed']}")
        self.skipped_label.config(text=f"Skipped: {self.stats['skipped']}")
        self.errors_label.config(text=f"Errors: {self.stats['errors']}")
        self.duplicates_label.config(text=f"Duplicates: {self.stats['duplicates']}")

    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {'processed': 0, 'skipped': 0, 'errors': 0, 'duplicates': 0}
        self.update_stats()

    def start_processing(self):
        """Start the file processing in a separate thread"""
        if self.is_processing:
            return
        
        source = self.source_dir.get()
        dest = self.dest_dir.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination directories.")
            return

        if not os.path.exists(source):
            messagebox.showerror("Error", "Source directory does not exist.")
            return

        if not os.path.exists(dest):
            try:
                os.makedirs(dest)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create destination directory: {e}")
                return

        # Reset for new processing
        self.reset_stats()
        self.clear_log()
        self.stop_processing = False
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self.process_files)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def stop_processing_func(self):
        """Stop the processing"""
        self.stop_processing = True
        self.log("Stop requested by user...")

    def process_files(self):
        """Process files (runs in separate thread)"""
        self.is_processing = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        try:
            source = self.source_dir.get()
            dest = self.dest_dir.get()
            action_type = self.action.get()
            is_preview = self.preview_mode.get()

            # Supported extensions
            photo_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', 
                              '.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2')

            # Count total files first
            total_files = 0
            for filename in os.listdir(source):
                filepath = os.path.join(source, filename)
                if os.path.isfile(filepath) and filename.lower().endswith(photo_extensions):
                    total_files += 1

            if total_files == 0:
                self.log("No supported photo files found in source directory.")
                messagebox.showinfo("Info", "No supported photo files found in source directory.")
                return

            self.log(f"Found {total_files} photo files to process.")
            if is_preview:
                self.log("PREVIEW MODE - No files will be moved or copied.")

            processed_files = 0

            for filename in os.listdir(source):
                if self.stop_processing:
                    self.log("Processing stopped by user.")
                    break

                filepath = os.path.join(source, filename)

                if os.path.isfile(filepath) and filename.lower().endswith(photo_extensions):
                    try:
                        date_obj = self.get_photo_date(filepath)
                        if date_obj:
                            # Format the folder name
                            folder_name = date_obj.strftime('(%Y) %A %d %B')
                            new_folder_path = os.path.join(dest, folder_name)
                            dest_file_path = os.path.join(new_folder_path, filename)

                            if is_preview:
                                self.log(f"PREVIEW: Would {action_type} {filename} to {folder_name}/")
                                self.stats['processed'] += 1
                            else:
                                # Create the new folder if it doesn't exist
                                os.makedirs(new_folder_path, exist_ok=True)

                                # Handle duplicates
                                if os.path.exists(dest_file_path):
                                    if self.duplicate_action.get() == "skip":
                                        self.log(f"Skipped {filename} (already exists)")
                                        self.stats['skipped'] += 1
                                        continue
                                    elif self.duplicate_action.get() == "rename":
                                        dest_file_path = self.get_unique_filename(dest_file_path)
                                        self.stats['duplicates'] += 1
                                        self.log(f"Duplicate found, renamed: {os.path.basename(dest_file_path)}")

                                # Perform the move or copy operation
                                if action_type == "move":
                                    shutil.move(filepath, dest_file_path)
                                    self.log(f"Moved: {filename} → {folder_name}/")
                                elif action_type == "copy":
                                    shutil.copy2(filepath, dest_file_path)
                                    self.log(f"Copied: {filename} → {folder_name}/")
                                
                                self.stats['processed'] += 1
                        else:
                            self.log(f"Could not get date for: {filename}")
                            self.stats['skipped'] += 1

                    except Exception as e:
                        self.log(f"Error processing {filename}: {e}")
                        self.stats['errors'] += 1

                    # Update progress
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"Processing: {processed_files}/{total_files} files")
                    self.update_stats()

            # Final update
            if not self.stop_processing:
                self.progress_var.set(100)
                self.progress_label.config(text="Processing complete!")
                self.log("Processing completed successfully!")
                
                mode_text = "PREVIEW" if is_preview else action_type.upper()
                messagebox.showinfo("Complete", 
                    f"{mode_text} operation completed!\n\n"
                    f"Processed: {self.stats['processed']}\n"
                    f"Skipped: {self.stats['skipped']}\n"
                    f"Errors: {self.stats['errors']}\n"
                    f"Duplicates handled: {self.stats['duplicates']}")

        except Exception as e:
            self.log(f"Fatal error during processing: {e}")
            messagebox.showerror("Error", f"An error occurred during processing: {e}")

        finally:
            self.is_processing = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            if not self.stop_processing:
                self.progress_label.config(text="Ready to process files")

# Main entry point
if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
    except ImportError:
        print("Error: PIL (Pillow) library is required for EXIF date extraction.")
        print("Please install it using: pip install Pillow")
        exit(1)

    root = tk.Tk()
    app = PhotoOrganizerApp(root)
    root.mainloop()