
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import os
import sys

# Check if required packages are available
def check_requirements():
    """Check if all required packages are installed"""
    missing = []
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        missing.append("ultralytics")
    
    if missing:
        print("Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False
    
    return True

class CurrencyDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Indian Currency Detector v1.0")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Currency denominations (matching your data.yaml order)
        # ['10', '100', '20', '200', '2000', '50', '500']
        self.currencies = [10, 100, 20, 200, 2000, 50, 500]
        self.currency_colors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#3498db', '#9b59b6', '#1abc9c']
        self.detection_percentages = [0.0] * len(self.currencies)
        
        # Initialize variables
        self.model = None
        self.cap = None
        self.running = False
        self.detection_thread = None
        
        # Load model and setup
        self.load_model()
        self.setup_ui()
        self.initialize_camera()
        
        if self.model and self.cap:
            self.start_detection()
    
    def load_model(self):
        """Load the trained YOLO model"""
        model_paths = [
            'runs/detect/currency_detection/weights/best.pt',
            'runs/detect/currency_detection/weights/last.pt',
            'currency_dec/runs/detect/currency_detection/weights/best.pt'
        ]
        
        try:
            from ultralytics import YOLO
            
            for path in model_paths:
                if os.path.exists(path):
                    print(f"Loading model from: {path}")
                    self.model = YOLO(path)
                    print("✓ Model loaded successfully!")
                    return
            
            # If no trained model found, show error
            messagebox.showerror("Model Error", 
                               "Trained model not found!\n\n" +
                               "Please run 'python train_model.py' first to train the model.\n\n" +
                               "Expected model location:\n" +
                               "runs/detect/currency_detection/weights/best.pt")
            
        except Exception as e:
            messagebox.showerror("Model Error", f"Error loading model: {str(e)}")
    
    def initialize_camera(self):
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                # Try different camera indices
                for i in range(1, 4):
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        break
                
                if not self.cap.isOpened():
                    messagebox.showerror("Camera Error", 
                                       "Cannot access camera!\n\n" +
                                       "Please check if:\n" +
                                       "1. Camera is connected\n" +
                                       "2. Camera is not used by another application\n" +
                                       "3. Camera permissions are granted")
                    return
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print("✓ Camera initialized successfully!")
            
        except Exception as e:
            messagebox.showerror("Camera Error", f"Error initializing camera: {str(e)}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frames
        self.left_frame = tk.Frame(self.root, width=600, height=700, bg='#34495e')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_frame = tk.Frame(self.root, width=600, height=700, bg='#ecf0f1')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Camera section
        self.setup_camera_section()
        
        # Right frame - Graph section
        self.setup_graph_section()
    
    def setup_camera_section(self):
        """Setup camera preview section"""
        # Title
        title_label = tk.Label(self.left_frame, text="📹 Live Camera Feed", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#34495e')
        title_label.pack(pady=10)
        
        # Camera frame
        self.camera_frame = tk.Frame(self.left_frame, bg='black', relief=tk.RIDGE, bd=2)
        self.camera_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Video label
        self.video_label = tk.Label(self.camera_frame, bg='black', 
                                   text="Initializing camera...", fg='white', font=('Arial', 12))
        self.video_label.pack(expand=True)
        
        # Status section
        status_frame = tk.Frame(self.left_frame, bg='#34495e')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(status_frame, text="Status:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(anchor=tk.W)
        
        self.status_label = tk.Label(status_frame, text="Ready to detect...", 
                                   font=('Arial', 11), fg='#2ecc71', bg='#34495e')
        self.status_label.pack(anchor=tk.W)
        
        # Detection info
        tk.Label(status_frame, text="Last Detection:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(anchor=tk.W, pady=(10,0))
        
        self.detection_label = tk.Label(status_frame, text="No currency detected", 
                                      font=('Arial', 11), fg='#e74c3c', bg='#34495e')
        self.detection_label.pack(anchor=tk.W)
    
    def setup_graph_section(self):
        """Setup graph section"""
        # Title
        title_label = tk.Label(self.right_frame, text="📊 Detection Confidence", 
                              font=('Arial', 16, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        title_label.pack(pady=10)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 8), dpi=80, facecolor='#ecf0f1')
        self.ax = self.fig.add_subplot(111)
        
        # Initial bar chart
        self.bars = self.ax.bar(range(len(self.currencies)), self.detection_percentages, 
                               color=self.currency_colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Customize the plot
        self.ax.set_xlabel('Currency Denominations (₹)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Detection Confidence (%)', fontsize=12, fontweight='bold')
        self.ax.set_title('Real-time Currency Detection Confidence', fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xticks(range(len(self.currencies)))
        self.ax.set_xticklabels([f'₹{c}' for c in self.currencies], fontsize=10, fontweight='bold')
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.3, axis='y')
        self.ax.set_facecolor('#f8f9fa')
        
        # Add value labels on bars
        self.value_labels = []
        for i, bar in enumerate(self.bars):
            label = self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                               f'{self.detection_percentages[i]:.1f}%',
                               ha='center', va='bottom', fontsize=9, fontweight='bold')
            self.value_labels.append(label)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add legend
        legend_frame = tk.Frame(self.right_frame, bg='#ecf0f1')
        legend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(legend_frame, text="💡 Tip: Hold currency notes in front of camera for detection", 
                font=('Arial', 10, 'italic'), fg='#7f8c8d', bg='#ecf0f1').pack()
    
    def detect_currency(self, frame):
        """Detect currency in the frame"""
        if self.model is None:
            return frame, "Model not loaded", "No currency detected"
        
        try:
            # Run inference
            results = self.model(frame, conf=0.25, verbose=False)
            
            # Reset percentages
            self.detection_percentages = [0.0] * len(self.currencies)
            
            detected_currency = "No currency detected"
            status = "Scanning..."
            max_confidence = 0
            
            # Process detections
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        # Get class name and confidence
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Map class_id to currency
                        if 0 <= class_id < len(self.currencies):
                            self.detection_percentages[class_id] = max(
                                self.detection_percentages[class_id], confidence * 100
                            )
                            
                            if confidence > max_confidence:
                                max_confidence = confidence
                                detected_currency = f"₹{self.currencies[class_id]}"
                                status = f"Detected: ₹{self.currencies[class_id]} ({confidence*100:.1f}%)"
                            
                            # Draw bounding box
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            color = (0, 255, 0) if confidence > 0.5 else (0, 255, 255)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                            
                            # Draw label with background
                            label = f"₹{self.currencies[class_id]} {confidence*100:.1f}%"
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                            cv2.rectangle(frame, (x1, y1-label_size[1]-10), 
                                        (x1+label_size[0], y1), color, -1)
                            cv2.putText(frame, label, (x1, y1-5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            return frame, status, detected_currency
            
        except Exception as e:
            return frame, f"Detection error: {str(e)}", "Error"
    
    def update_graph(self):
        """Update the confidence graph"""
        try:
            # Update bar heights and colors
            for i, (bar, percentage) in enumerate(zip(self.bars, self.detection_percentages)):
                bar.set_height(percentage)
                
                # Change color intensity based on confidence
                alpha = 0.4 + (percentage / 100) * 0.6
                color = self.currency_colors[i]
                bar.set_color(color)
                bar.set_alpha(alpha)
                
                # Update labels
                self.value_labels[i].set_position((bar.get_x() + bar.get_width()/2, percentage + 2))
                self.value_labels[i].set_text(f'{percentage:.1f}%')
                
                # Highlight the highest confidence
                if percentage == max(self.detection_percentages) and percentage > 0:
                    bar.set_edgecolor('red')
                    bar.set_linewidth(3)
                else:
                    bar.set_edgecolor('black')
                    bar.set_linewidth(1)
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Graph update error: {e}")
    
    def start_detection(self):
        """Start the detection loop in a separate thread"""
        self.running = True
        
        def detection_loop():
            while self.running:
                try:
                    if self.cap and self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if ret:
                            # Resize frame for processing
                            frame = cv2.resize(frame, (640, 480))
                            
                            # Detect currency
                            processed_frame, status, detection = self.detect_currency(frame)
                            
                            # Convert to RGB for display
                            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(rgb_frame)
                            photo = ImageTk.PhotoImage(image=img)
                            
                            # Update UI in main thread
                            self.root.after(0, self.update_ui, photo, status, detection)
                    
                    time.sleep(0.1)  # Control frame rate
                    
                except Exception as e:
                    print(f"Detection loop error: {e}")
                    time.sleep(1)
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
        self.detection_thread.start()
    
    def update_ui(self, photo, status, detection):
        """Update the UI elements"""
        try:
            # Update video display
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo
            
            # Update status
            self.status_label.configure(text=status)
            
            # Update detection info
            if "No currency" in detection:
                self.detection_label.configure(text=detection, fg='#e74c3c')
            else:
                self.detection_label.configure(text=detection, fg='#27ae60')
            
            # Update graph
            self.update_graph()
            
        except Exception as e:
            print(f"UI update error: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1)
        
        self.root.destroy()

def main():
    """Main function"""
    print("Indian Currency Detector v1.0")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\nPlease install required packages and try again.")
        return
    
    # Create and run app
    try:
        root = tk.Tk()
        app = CurrencyDetectorApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✓ Application started successfully!")
        print("✓ Use the camera preview to detect Indian currency notes")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()