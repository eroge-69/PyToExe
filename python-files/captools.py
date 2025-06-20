#!/usr/bin/env python3
"""
Cap to Images Converter - Extract JPEG images from .cap files
Usage: 
    GUI mode: python cap_to_images.py
    CLI mode: python cap_to_images.py input_file.cap [output_directory]
"""

import os
import sys
import argparse
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class CapToImagesConverter:
    """Core image extraction functionality"""
    
    @staticmethod
    def extract_images_from_cap(input_file, output_dir=None, progress_callback=None):
        """
        Extract JPEG images from a .cap file
        
        Args:
            input_file (str): Path to the .cap file
            output_dir (str): Output directory (optional)
            progress_callback (function): Callback for progress updates
        
        Returns:
            int: Number of images extracted
        """
        
        # Validate input file
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Set up output directory
        if output_dir is None:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_dir = os.path.join(os.path.dirname(input_file), base_name)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if progress_callback:
            progress_callback(f"Output directory: {output_dir}")
        
        # Read the file
        if progress_callback:
            progress_callback(f"Reading file: {input_file}")
        
        with open(input_file, 'rb') as file:
            data = file.read()
        
        file_size = len(data)
        if progress_callback:
            progress_callback(f"File size: {file_size:,} bytes")
        
        # Find JPEG headers and extract images
        jpeg_count = 0
        start_index = 0
        
        # JPEG header signature: FF D8 FF E0
        jpeg_header = b'\xFF\xD8\xFF\xE0'
        
        if progress_callback:
            progress_callback("Searching for JPEG headers...")
        
        for i in range(file_size - 3):
            # Check for JPEG header
            if data[i:i+4] == jpeg_header:
                if start_index == 0:
                    # First JPEG found
                    start_index = i
                    if progress_callback:
                        progress_callback(f"Found first JPEG header at position {i}")
                else:
                    # Extract the previous image
                    image_data = data[start_index:i-1]
                    saved_path = CapToImagesConverter.save_image(image_data, output_dir, jpeg_count)
                    
                    if progress_callback:
                        progress_callback(f"Extracted image {jpeg_count} ({len(image_data):,} bytes)")
                    
                    # Update for next image
                    start_index = i
                    jpeg_count += 1
                    
                    # Yield image data for preview (GUI mode)
                    yield image_data, saved_path
        
        # Handle the last image (if any)
        if start_index > 0:
            image_data = data[start_index:]
            saved_path = CapToImagesConverter.save_image(image_data, output_dir, jpeg_count)
            
            if progress_callback:
                progress_callback(f"Extracted image {jpeg_count} ({len(image_data):,} bytes)")
            
            jpeg_count += 1
            yield image_data, saved_path
        
        if progress_callback:
            progress_callback(f"Extraction complete! {jpeg_count} images saved")
    
    @staticmethod
    def save_image(image_data, output_dir, index):
        """
        Save image data as a JPEG file
        
        Args:
            image_data (bytes): Raw image data
            output_dir (str): Output directory
            index (int): Image index for filename
            
        Returns:
            str: Path to saved file
        """
        output_path = os.path.join(output_dir, f"{index}.jpg")
        
        if PIL_AVAILABLE:
            try:
                # Validate image data by opening it with PIL
                image = Image.open(io.BytesIO(image_data))
                image.save(output_path, "JPEG")
                return output_path
            except Exception as e:
                print(f"Warning: Could not save image {index} with PIL: {str(e)}")
        
        # Fallback: save raw data
        try:
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return output_path
        except Exception as e:
            print(f"Error: Could not save image {index}: {str(e)}")
            return None


class CapToImagesGUI:
    """GUI interface using tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Generator - Cap to Images")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Preview image label
        self.image_label = ttk.Label(main_frame, text="No image selected", 
                                   relief="solid", width=30, anchor="center")
        self.image_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), 
                            sticky=(tk.W, tk.E))
        
        # Open file button
        self.open_button = ttk.Button(main_frame, text="Open Cap File", 
                                    command=self.open_cap_file)
        self.open_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                         pady=10)
        
        # Status text area
        self.status_text = tk.Text(main_frame, height=8, width=50, wrap=tk.WORD)
        self.status_text.grid(row=3, column=0, columnspan=2, pady=5, 
                            sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        self.log_message("Ready - Click 'Open Cap File' to start")
    
    def log_message(self, message):
        """Add message to status text area"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def open_cap_file(self):
        """Open and process a .cap file"""
        file_path = filedialog.askopenfilename(
            title="Open Cap File",
            filetypes=[("Cap files", "*.cap"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.extract_images(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.log_message(f"Error: {str(e)}")
            self.progress.stop()
    
    def extract_images(self, file_path):
        """Extract JPEG images from the cap file"""
        self.progress.start()
        self.status_text.delete(1.0, tk.END)
        
        try:
            count = 0
            for image_data, saved_path in CapToImagesConverter.extract_images_from_cap(
                file_path, progress_callback=self.log_message
            ):
                count += 1
                self.update_preview(image_data)
            
            self.progress.stop()
            if count > 0:
                messagebox.showinfo("Success", f"Successfully extracted {count} images!")
            else:
                messagebox.showwarning("No Images", "No JPEG images found in the file.")
                
        except Exception as e:
            self.progress.stop()
            raise e
    
    def update_preview(self, image_data):
        """Update the preview with the current image"""
        if not PIL_AVAILABLE:
            self.image_label.configure(text="Preview unavailable\n(PIL not installed)")
            return
            
        try:
            import io
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Resize for preview (maintain aspect ratio)
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Update the label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.log_message(f"Warning: Could not update preview: {str(e)}")


def run_cli(input_file, output_dir=None):
    """Run in command-line mode"""
    import io
    
    def print_progress(message):
        print(message)
    
    try:
        print("=== Cap to Images Converter ===")
        print()
        
        count = 0
        for image_data, saved_path in CapToImagesConverter.extract_images_from_cap(
            input_file, output_dir, print_progress
        ):
            count += 1
            if saved_path and PIL_AVAILABLE:
                try:
                    image = Image.open(io.BytesIO(image_data))
                    print(f"  └─ Saved: {os.path.basename(saved_path)} "
                          f"({image.width}x{image.height} pixels)")
                except:
                    print(f"  └─ Saved: {os.path.basename(saved_path)}")
        
        print()
        if count > 0:
            print(f"✓ Successfully extracted {count} images!")
        else:
            print("✗ No JPEG images found in the file.")
            
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


def run_gui():
    """Run in GUI mode"""
    if not GUI_AVAILABLE:
        print("Error: tkinter not available. GUI mode not supported.")
        print("Try running in CLI mode: python cap_to_images.py input_file.cap")
        sys.exit(1)
    
    root = tk.Tk()
    app = CapToImagesGUI(root)
    root.mainloop()


def main():
    """Main function - determines whether to run CLI or GUI"""
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # CLI mode
        parser = argparse.ArgumentParser(
            description="Extract JPEG images from .cap files",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python cap_to_images.py                    # GUI mode
  python cap_to_images.py images.cap         # CLI mode
  python cap_to_images.py images.cap /output # CLI with custom output
            """
        )
        
        parser.add_argument('input_file', 
                           help='Input .cap file')
        parser.add_argument('output_dir', 
                           nargs='?', 
                           help='Output directory (optional)')
        
        args = parser.parse_args()
        run_cli(args.input_file, args.output_dir)
    else:
        # GUI mode (default)
        run_gui()


if __name__ == "__main__":
    main()