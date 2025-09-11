import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import cv2
from PIL import Image, ImageTk
import requests
import threading
import time
from pyzbar import pyzbar
import json
from datetime import datetime

class QRScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Scanner - Telegram Bot")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Telegram bot configuration
        self.bot_token = "8437229955:AAGAx-PuQQbBzymwEYpiVUOyb6VVcV1gkeo"
        self.chat_id = "7851208948"
        
        # Camera and scanning variables
        self.cap = None
        self.scanning = False
        self.scanned_codes = set()  # To track unique QR codes
        self.scanned_list = []  # To display in GUI
        
        # Threading control
        self.camera_thread = None
        self.stop_thread = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="QR Code Scanner", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Left panel - Camera feed
        camera_frame = ttk.LabelFrame(main_frame, text="Camera Feed", padding="5")
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.camera_label = ttk.Label(camera_frame, text="Camera not started", 
                                     background="black", foreground="white")
        self.camera_label.pack(expand=True, fill="both")
        
        # Right panel - Controls and QR codes list
        control_frame = ttk.LabelFrame(main_frame, text="Controls & Scanned QR Codes", padding="5")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(2, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self.start_button = ttk.Button(button_frame, text="Start Scanning", 
                                      command=self.start_scanning)
        self.start_button.grid(row=0, column=0, padx=2, sticky=(tk.W, tk.E))
        
        self.reset_button = ttk.Button(button_frame, text="Reset List", 
                                      command=self.reset_codes)
        self.reset_button.grid(row=0, column=1, padx=2, sticky=(tk.W, tk.E))
        
        self.exit_button = ttk.Button(button_frame, text="Exit", 
                                     command=self.on_closing)
        self.exit_button.grid(row=0, column=2, padx=2, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Ready to scan", 
                                     foreground="blue")
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # QR codes list
        list_frame = ttk.LabelFrame(control_frame, text="Scanned QR Codes", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.codes_text = scrolledtext.ScrolledText(list_frame, height=15, width=40)
        self.codes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def start_scanning(self):
        """Start or stop the camera scanning"""
        if not self.scanning:
            if self.initialize_camera():
                self.scanning = True
                self.stop_thread = False
                self.start_button.config(text="Stop Scanning")
                self.status_label.config(text="Status: Scanning for QR codes...", foreground="green")
                
                # Start camera thread
                self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
                self.camera_thread.start()
            else:
                messagebox.showerror("Error", "Failed to initialize camera. Please check if a camera is connected.")
        else:
            self.stop_scanning()
    
    def stop_scanning(self):
        """Stop the camera scanning"""
        self.scanning = False
        self.stop_thread = True
        self.start_button.config(text="Start Scanning")
        self.status_label.config(text="Status: Scanning stopped", foreground="red")
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear camera display
        self.camera_label.config(image="", text="Camera stopped")
    
    def initialize_camera(self):
        """Initialize the camera"""
        try:
            # Try different camera indices (0, 1, 2) to find available camera
            for i in range(3):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    # Set camera properties for better performance
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    return True
                self.cap.release()
            return False
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False
    
    def camera_loop(self):
        """Main camera loop running in separate thread"""
        while self.scanning and not self.stop_thread:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Detect QR codes
                self.detect_qr_codes(frame)
                
                # Convert frame for Tkinter display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (400, 300))
                
                # Convert to PIL Image and then to PhotoImage
                pil_image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update GUI in main thread
                self.root.after(0, self.update_camera_display, photo)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Camera loop error: {e}")
                break
    
    def update_camera_display(self, photo):
        """Update camera display in main thread"""
        if self.scanning:
            self.camera_label.config(image=photo, text="")
            self.camera_label.image = photo  # Keep a reference
    
    def detect_qr_codes(self, frame):
        """Detect QR codes in the frame"""
        try:
            # Decode QR codes
            qr_codes = pyzbar.decode(frame)
            
            for qr_code in qr_codes:
                # Get QR code data
                qr_data = qr_code.data.decode('utf-8')
                
                # Check if this QR code is new
                if qr_data not in self.scanned_codes:
                    self.scanned_codes.add(qr_data)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Add to display list
                    entry = f"[{timestamp}] {qr_data}"
                    self.scanned_list.append(entry)
                    
                    # Update GUI in main thread
                    self.root.after(0, self.update_codes_display)
                    
                    # Send to Telegram in separate thread
                    telegram_thread = threading.Thread(
                        target=self.send_to_telegram, 
                        args=(qr_data, timestamp), 
                        daemon=True
                    )
                    telegram_thread.start()
                    
        except Exception as e:
            print(f"QR detection error: {e}")
    
    def update_codes_display(self):
        """Update the QR codes display"""
        self.codes_text.delete(1.0, tk.END)
        for entry in reversed(self.scanned_list):  # Show newest first
            self.codes_text.insert(tk.END, entry + "\n")
    
    def send_to_telegram(self, qr_data, timestamp):
        """Send QR code data to Telegram bot"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            message = f"🔍 New QR Code Detected!\n\n📅 Time: {timestamp}\n📄 Data: {qr_data}"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Successfully sent to Telegram: {qr_data}")
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Status: Sent QR code to Telegram ✓", foreground="green"))
            else:
                print(f"Failed to send to Telegram: {response.status_code}")
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Status: Failed to send to Telegram ✗", foreground="red"))
                
        except Exception as e:
            print(f"Telegram send error: {e}")
            self.root.after(0, lambda: self.status_label.config(
                text=f"Status: Telegram error - {str(e)[:30]}...", foreground="red"))
    
    def reset_codes(self):
        """Reset the scanned codes list"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all scanned QR codes?"):
            self.scanned_codes.clear()
            self.scanned_list.clear()
            self.codes_text.delete(1.0, tk.END)
            self.status_label.config(text="Status: QR codes list cleared", foreground="blue")
    
    def on_closing(self):
        """Handle application closing"""
        if self.scanning:
            self.stop_scanning()
        
        # Wait a moment for threads to finish
        if self.camera_thread and self.camera_thread.is_alive():
            self.stop_thread = True
            self.camera_thread.join(timeout=1)
        
        self.root.destroy()

def main():
    """Main function to run the application"""
    # Check if required packages are available
    try:
        import cv2
        import pyzbar
        import requests
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install opencv-python pyzbar[scripts] requests pillow")
        return
    
    # Create and run the application
    root = tk.Tk()
    app = QRScannerApp(root)
    
    print("QR Scanner Application Started")
    print("Make sure you have a USB camera connected")
    print("The application will send detected QR codes to your Telegram bot")
    
    root.mainloop()

if __name__ == "__main__":
    main()
