import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from datetime import datetime
import threading
import json

class DentalCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dental Camera DOHA CLINIC")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Application state
        self.cap = None
        self.is_recording = False
        self.current_frame = None
        self.patient_info = {}
        self.save_directory = os.path.expanduser("~/Documents/DentalCamera")
        
        # Create save directory
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        
        # Initialize UI
        self.create_ui()
        
        # Load settings
        self.load_settings()
        
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🦷  GODS OWN AI (Dental)",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Top control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Patient info section
        patient_frame = ttk.LabelFrame(control_frame, text="Patient Information", padding=10)
        patient_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(patient_frame, text="Patient Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.patient_name_var = tk.StringVar()
        ttk.Entry(patient_frame, textvariable=self.patient_name_var, width=20).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(patient_frame, text="Patient ID:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.patient_id_var = tk.StringVar()
        ttk.Entry(patient_frame, textvariable=self.patient_id_var, width=20).grid(row=1, column=1, sticky=tk.W)
        
        # Camera controls
        camera_frame = ttk.LabelFrame(control_frame, text="Camera Controls", padding=10)
        camera_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(camera_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(camera_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.capture_btn = ttk.Button(camera_frame, text="📸 Capture", command=self.capture_image, state=tk.DISABLED)
        self.capture_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.record_btn = ttk.Button(camera_frame, text="🎥 Record", command=self.toggle_recording, state=tk.DISABLED)
        self.record_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Camera display
        camera_frame = ttk.LabelFrame(content_frame, text="Camera View", padding=10)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.camera_label = ttk.Label(camera_frame, text="Camera Not Started\nClick 'Start Camera' to begin", 
                                     font=('Arial', 12), anchor=tk.CENTER,
                                     background='black', foreground='white')
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Right panel with controls and settings
        right_panel = ttk.Frame(content_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Image enhancement controls
        enhance_frame = ttk.LabelFrame(right_panel, text="Image Enhancement", padding=10)
        enhance_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Brightness
        ttk.Label(enhance_frame, text="Brightness:").pack(anchor=tk.W)
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = ttk.Scale(enhance_frame, from_=0.5, to=2.0, variable=self.brightness_var, 
                                   orient=tk.HORIZONTAL, command=self.update_enhancements)
        brightness_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Contrast
        ttk.Label(enhance_frame, text="Contrast:").pack(anchor=tk.W)
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = ttk.Scale(enhance_frame, from_=0.5, to=2.0, variable=self.contrast_var,
                                 orient=tk.HORIZONTAL, command=self.update_enhancements)
        contrast_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Sharpness
        ttk.Label(enhance_frame, text="Sharpness:").pack(anchor=tk.W)
        self.sharpness_var = tk.DoubleVar(value=1.0)
        sharpness_scale = ttk.Scale(enhance_frame, from_=0.0, to=2.0, variable=self.sharpness_var,
                                  orient=tk.HORIZONTAL, command=self.update_enhancements)
        sharpness_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Reset button
        ttk.Button(enhance_frame, text="Reset", command=self.reset_enhancements).pack()
        
        # Settings frame
        settings_frame = ttk.LabelFrame(right_panel, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Camera selection
        ttk.Label(settings_frame, text="Camera:").pack(anchor=tk.W)
        self.camera_var = tk.StringVar(value="0")
        camera_combo = ttk.Combobox(settings_frame, textvariable=self.camera_var, values=["0", "1", "2"], width=10)
        camera_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Resolution
        ttk.Label(settings_frame, text="Resolution:").pack(anchor=tk.W)
        self.resolution_var = tk.StringVar(value="640x480")
        resolution_combo = ttk.Combobox(settings_frame, textvariable=self.resolution_var, 
                                      values=["640x480", "800x600", "1024x768", "1280x720", "1920x1080"])
        resolution_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Save directory
        ttk.Button(settings_frame, text="Change Save Directory", command=self.change_save_directory).pack(fill=tk.X)
        
        # File management
        files_frame = ttk.LabelFrame(right_panel, text="Recent Files", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # File listbox with scrollbar
        listbox_frame = ttk.Frame(files_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_listbox = tk.Listbox(listbox_frame, height=10)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File management buttons
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(file_btn_frame, text="Open", command=self.open_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_btn_frame, text="Delete", command=self.delete_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_btn_frame, text="Refresh", command=self.refresh_file_list).pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Initialize file list
        self.refresh_file_list()
        
    def start_camera(self):
        try:
            camera_index = int(self.camera_var.get())
            self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
                
            # Set resolution
            resolution = self.resolution_var.get().split('x')
            width, height = int(resolution[0]), int(resolution[1])
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Update button states
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.capture_btn.config(state=tk.NORMAL)
            self.record_btn.config(state=tk.NORMAL)
            
            # Start camera feed
            self.update_camera_feed()
            self.status_var.set("Camera started successfully")
            
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to start camera: {str(e)}")
            
    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Update button states
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.capture_btn.config(state=tk.DISABLED)
        self.record_btn.config(state=tk.DISABLED)
        
        # Clear camera display
        self.camera_label.config(image='', text="Camera Stopped\nClick 'Start Camera' to begin")
        self.status_var.set("Camera stopped")
        
    def update_camera_feed(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Apply enhancements
                enhanced_frame = self.apply_enhancements(frame)
                
                # Convert to PIL Image
                rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Resize to fit display
                display_size = (640, 480)
                pil_image = pil_image.resize(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update display
                self.camera_label.config(image=photo, text='')
                self.camera_label.image = photo
                
            # Schedule next update
            self.root.after(30, self.update_camera_feed)
            
    def apply_enhancements(self, frame):
        # Convert to PIL for enhancements
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # Apply brightness
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(self.brightness_var.get())
        
        # Apply contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(self.contrast_var.get())
        
        # Apply sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(self.sharpness_var.get())
        
        # Convert back to OpenCV format
        enhanced_frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return enhanced_frame
        
    def update_enhancements(self, *args):
        # Enhancements are applied in real-time through update_camera_feed
        pass
        
    def reset_enhancements(self):
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.sharpness_var.set(1.0)
        
    def capture_image(self):
        if self.current_frame is not None:
            try:
                # Apply enhancements to the captured image
                enhanced_frame = self.apply_enhancements(self.current_frame)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                patient_name = self.patient_name_var.get() or "Unknown"
                filename = f"{patient_name}_{timestamp}.jpg"
                filepath = os.path.join(self.save_directory, filename)
                
                # Save image
                cv2.imwrite(filepath, enhanced_frame)
                
                # Save metadata
                metadata = {
                    'patient_name': self.patient_name_var.get(),
                    'patient_id': self.patient_id_var.get(),
                    'timestamp': timestamp,
                    'filename': filename,
                    'brightness': self.brightness_var.get(),
                    'contrast': self.contrast_var.get(),
                    'sharpness': self.sharpness_var.get()
                }
                
                metadata_file = filepath.replace('.jpg', '_metadata.json')
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                self.status_var.set(f"Image captured: {filename}")
                self.refresh_file_list()
                
            except Exception as e:
                messagebox.showerror("Capture Error", f"Failed to capture image: {str(e)}")
                
    def toggle_recording(self):
        # Placeholder for video recording functionality
        # This would require additional implementation for video recording
        messagebox.showinfo("Recording", "Video recording feature - Implementation needed")
        
    def change_save_directory(self):
        new_directory = filedialog.askdirectory(initialdir=self.save_directory)
        if new_directory:
            self.save_directory = new_directory
            self.refresh_file_list()
            self.status_var.set(f"Save directory changed to: {new_directory}")
            
    def refresh_file_list(self):
        self.files_listbox.delete(0, tk.END)
        try:
            files = [f for f in os.listdir(self.save_directory) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            files.sort(reverse=True)  # Newest first
            
            for file in files[:20]:  # Show last 20 files
                self.files_listbox.insert(tk.END, file)
                
        except Exception as e:
            self.status_var.set(f"Error reading files: {str(e)}")
            
    def open_selected_file(self):
        selection = self.files_listbox.curselection()
        if selection:
            filename = self.files_listbox.get(selection[0])
            filepath = os.path.join(self.save_directory, filename)
            try:
                os.startfile(filepath)  # Windows specific
            except Exception as e:
                messagebox.showerror("File Error", f"Could not open file: {str(e)}")
                
    def delete_selected_file(self):
        selection = self.files_listbox.curselection()
        if selection:
            filename = self.files_listbox.get(selection[0])
            if messagebox.askyesno("Delete File", f"Are you sure you want to delete {filename}?"):
                try:
                    filepath = os.path.join(self.save_directory, filename)
                    os.remove(filepath)
                    
                    # Also remove metadata file if exists
                    metadata_file = filepath.replace('.jpg', '_metadata.json')
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
                        
                    self.refresh_file_list()
                    self.status_var.set(f"Deleted: {filename}")
                    
                except Exception as e:
                    messagebox.showerror("Delete Error", f"Could not delete file: {str(e)}")
                    
    def load_settings(self):
        # Load application settings from a config file
        config_file = os.path.join(self.save_directory, 'config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    self.camera_var.set(settings.get('camera', '0'))
                    self.resolution_var.set(settings.get('resolution', '640x480'))
        except:
            pass  # Use defaults if loading fails
            
    def save_settings(self):
        # Save application settings
        config_file = os.path.join(self.save_directory, 'config.json')
        settings = {
            'camera': self.camera_var.get(),
            'resolution': self.resolution_var.get(),
            'save_directory': self.save_directory
        }
        try:
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except:
            pass  # Fail silently
            
    def on_closing(self):
        self.save_settings()
        if self.cap:
            self.cap.release()
        self.root.destroy()

# Import numpy after the class definition
import numpy as np

def main():
    # Check for required packages
    required_packages = ['opencv-python', 'Pillow', 'numpy']
    missing_packages = []
    
    try:
        import cv2
        import PIL
        import numpy
    except ImportError as e:
        missing_packages.append(str(e))
    
    if missing_packages:
        print("Missing required packages. Please install:")
        print("pip install opencv-python Pillow numpy")
        return
    
    # Create and run the application
    root = tk.Tk()
    
    # Windows 11 style
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass  # Use default theme if azure theme not available
    
    app = DentalCameraApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (800 // 2)
    root.geometry(f"1200x800+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()