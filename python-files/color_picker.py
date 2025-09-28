import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
import colorsys
import threading
import time


class ColorPicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("xsukax Color Picker")
        self.root.geometry("320x340")
        self.root.resizable(False, False)
        
        # Variables for color values
        self.current_color = "#000000"
        self.rgb_values = (0, 0, 0)
        self.hsl_values = (0, 0, 0)
        
        # Real-time tracking variables
        self.is_tracking = False
        self.tracking_thread = None
        self.tracking_overlay = None
        self.last_mouse_pos = (0, 0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Color display area
        self.color_frame = tk.Frame(main_frame, width=100, height=60, 
                                   bg=self.current_color, relief="raised", bd=2)
        self.color_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        self.color_frame.grid_propagate(False)
        
        # Mouse coordinates display
        coord_frame = ttk.Frame(main_frame)
        coord_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        ttk.Label(coord_frame, text="Position:").pack(side="left")
        self.coord_var = tk.StringVar(value="(0, 0)")
        ttk.Label(coord_frame, textvariable=self.coord_var, 
                 font=("Courier", 9)).pack(side="left", padx=(5, 0))
        
        # Control buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15), sticky="ew")
        
        self.track_btn = ttk.Button(btn_frame, text="Start Real-time Tracking", 
                                   command=self.toggle_real_time_tracking)
        self.track_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.pick_btn = ttk.Button(btn_frame, text="Pick Color", 
                                  command=self.pick_current_color)
        self.pick_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        # HEX section
        ttk.Label(main_frame, text="HEX:").grid(row=3, column=0, sticky="w", pady=2)
        self.hex_var = tk.StringVar(value=self.current_color)
        hex_entry = ttk.Entry(main_frame, textvariable=self.hex_var, width=12)
        hex_entry.grid(row=3, column=1, padx=(5, 5), pady=2, sticky="ew")
        ttk.Button(main_frame, text="Copy", width=6,
                  command=lambda: self.copy_to_clipboard(self.hex_var.get())).grid(
                      row=3, column=2, pady=2)
        
        # RGB section
        ttk.Label(main_frame, text="RGB:").grid(row=4, column=0, sticky="w", pady=2)
        self.rgb_var = tk.StringVar(value="0, 0, 0")
        rgb_entry = ttk.Entry(main_frame, textvariable=self.rgb_var, width=12)
        rgb_entry.grid(row=4, column=1, padx=(5, 5), pady=2, sticky="ew")
        ttk.Button(main_frame, text="Copy", width=6,
                  command=lambda: self.copy_to_clipboard(self.rgb_var.get())).grid(
                      row=4, column=2, pady=2)
        
        # HSL section
        ttk.Label(main_frame, text="HSL:").grid(row=5, column=0, sticky="w", pady=2)
        self.hsl_var = tk.StringVar(value="0°, 0%, 0%")
        hsl_entry = ttk.Entry(main_frame, textvariable=self.hsl_var, width=12)
        hsl_entry.grid(row=5, column=1, padx=(5, 5), pady=2, sticky="ew")
        ttk.Button(main_frame, text="Copy", width=6,
                  command=lambda: self.copy_to_clipboard(self.hsl_var.get())).grid(
                      row=5, column=2, pady=2)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready - Click 'Start Real-time Tracking' to begin")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=("Arial", 8), foreground="gray")
        status_label.grid(row=6, column=0, columnspan=3, pady=(10, 5), sticky="ew")
        
        # Branding label
        brand_label = ttk.Label(main_frame, text="xsukax Color Picker v1.0", 
                               font=("Arial", 7), foreground="#666666")
        brand_label.grid(row=7, column=0, columnspan=3, pady=(0, 0), sticky="ew")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def toggle_real_time_tracking(self):
        """Toggle real-time color tracking mode"""
        if not self.is_tracking:
            self.start_real_time_tracking()
        else:
            self.stop_real_time_tracking()
            
    def start_real_time_tracking(self):
        """Start real-time color tracking"""
        if self.is_tracking:
            return
            
        self.is_tracking = True
        self.track_btn.configure(text="Stop Tracking")
        self.pick_btn.configure(state="disabled")
        self.status_var.set("Real-time tracking active - Move mouse to see colors")
        
        # Create invisible overlay for mouse tracking
        self.create_tracking_overlay()
        
        # Start tracking thread
        self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.tracking_thread.start()
        
    def stop_real_time_tracking(self):
        """Stop real-time color tracking"""
        if not self.is_tracking:
            return
            
        self.is_tracking = False
        self.track_btn.configure(text="Start Real-time Tracking")
        self.pick_btn.configure(state="normal")
        self.status_var.set("Tracking stopped - Ready to pick colors")
        
        # Destroy overlay
        if self.tracking_overlay:
            self.tracking_overlay.destroy()
            self.tracking_overlay = None
            
        # Bring main window to front
        self.root.lift()
        self.root.focus_set()
        
    def create_tracking_overlay(self):
        """Create transparent overlay for mouse tracking"""
        self.tracking_overlay = tk.Toplevel(self.root)
        self.tracking_overlay.attributes('-fullscreen', True)
        self.tracking_overlay.attributes('-alpha', 0.01)  # Nearly invisible
        self.tracking_overlay.attributes('-topmost', True)
        self.tracking_overlay.configure(bg='black')
        
        # Bind mouse events
        self.tracking_overlay.bind('<Motion>', self.on_mouse_move)
        self.tracking_overlay.bind('<Button-1>', self.on_click_pick)
        self.tracking_overlay.bind('<Escape>', lambda e: self.stop_real_time_tracking())
        self.tracking_overlay.bind('<Button-3>', lambda e: self.stop_real_time_tracking())  # Right click to stop
        
        # Change cursor to crosshair
        self.tracking_overlay.configure(cursor="crosshair")
        
        # Add instruction label
        instruction = tk.Label(self.tracking_overlay, 
                             text="Left click to pick color | Right click or ESC to stop tracking",
                             fg="white", bg="black", font=("Arial", 12))
        instruction.place(relx=0.5, rely=0.05, anchor="center")
        
        # Focus on overlay
        self.tracking_overlay.focus_set()
        
    def on_mouse_move(self, event):
        """Handle mouse movement for real-time tracking"""
        # Get absolute coordinates
        x = self.tracking_overlay.winfo_rootx() + event.x
        y = self.tracking_overlay.winfo_rooty() + event.y
        self.last_mouse_pos = (x, y)
        
    def on_click_pick(self, event):
        """Handle click to pick current color"""
        self.pick_current_color()
        
    def tracking_loop(self):
        """Main tracking loop running in separate thread"""
        while self.is_tracking:
            try:
                x, y = self.last_mouse_pos
                
                # Capture pixel color at current mouse position
                screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                pixel_color = screenshot.getpixel((0, 0))
                
                # Update UI in main thread
                self.root.after(0, self.update_real_time_color, pixel_color, x, y)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.05)  # 20 FPS update rate
                
            except Exception as e:
                # Continue tracking even if there's an error
                time.sleep(0.1)
                
    def update_real_time_color(self, rgb_tuple, x, y):
        """Update color values in real-time (called from main thread)"""
        if not self.is_tracking:
            return
            
        # Handle different RGB tuple formats
        if len(rgb_tuple) >= 3:
            r, g, b = rgb_tuple[:3]
        else:
            r = g = b = 0
            
        self.rgb_values = (r, g, b)
        
        # Convert to HEX
        self.current_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
        h_deg = int(h * 360)
        s_percent = int(s * 100)
        l_percent = int(l * 100)
        self.hsl_values = (h_deg, s_percent, l_percent)
        
        # Update UI
        self.color_frame.configure(bg=self.current_color)
        self.hex_var.set(self.current_color.upper())
        self.rgb_var.set(f"{r}, {g}, {b}")
        self.hsl_var.set(f"{h_deg}°, {s_percent}%, {l_percent}%")
        self.coord_var.set(f"({x}, {y})")
        
    def pick_current_color(self):
        """Pick/select the current color (stops tracking and keeps the color)"""
        if self.is_tracking:
            self.stop_real_time_tracking()
            
        # Show feedback
        original_title = self.root.title()
        self.root.title("xsukax Color Picker - Color Picked!")
        self.status_var.set("Color picked and saved!")
        self.root.after(2000, lambda: self.root.title(original_title))
        self.root.after(2000, lambda: self.status_var.set("Ready - Click 'Start Real-time Tracking' to begin"))
        
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            
            # Brief visual feedback
            original_title = self.root.title()
            self.root.title("xsukax Color Picker - Copied!")
            self.root.after(1000, lambda: self.root.title(original_title))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
            
    def on_closing(self):
        """Handle application closing"""
        self.stop_real_time_tracking()
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import PIL
    except ImportError:
        print("Required dependency missing: PIL (Pillow)")
        print("Install with: pip install Pillow")
        exit(1)
    
    app = ColorPicker()
    app.run()