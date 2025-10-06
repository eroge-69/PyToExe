"""
Dragclickable v1.0 - With Draggable Circles
"""

import cv2
import numpy as np
import pyautogui
import time
import threading
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import keyboard

class DraggableCircle:
    def __init__(self, canvas, x, y, radius=20, color="red", number=1):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.number = number
        self.is_dragging = False
        
        # Create circle with grey background
        self.circle = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="grey", outline="white", width=2
        )
        
        # Create number label with white text
        self.label = self.canvas.create_text(
            x, y, text=str(number), fill="white", font=("Arial", 12, "bold")
        )
        
        # Bind events
        self.canvas.tag_bind(self.circle, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.circle, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.circle, "<ButtonRelease-1>", self.stop_drag)
        
        self.canvas.tag_bind(self.label, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.label, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.label, "<ButtonRelease-1>", self.stop_drag)
    
    def start_drag(self, event):
        self.is_dragging = True
        self.canvas.configure(cursor="hand2")
    
    def drag(self, event):
        if self.is_dragging:
            # Update position
            self.x = event.x
            self.y = event.y
            
            # Move circle and label
            self.canvas.coords(self.circle, 
                             self.x - self.radius, self.y - self.radius,
                             self.x + self.radius, self.y + self.radius)
            self.canvas.coords(self.label, self.x, self.y)
    
    def stop_drag(self, event):
        self.is_dragging = False
        self.canvas.configure(cursor="")
    
    def get_position(self):
        return self.x, self.y

class AQWPSClickerV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragclickable")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Set application icon
        try:
            icon_path = "dragclickable_icon.png"
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Variables
        self.circles = []
        self.is_clicking = False
        self.target_clicks = 0
        self.current_screen = None
        self.screen_width = 0
        self.screen_height = 0
        self.canvas_width = 800
        self.canvas_height = 600
        
        # GUI variables
        self.canvas = None
        self.status_text = None
        self.click_entry = None
        self.start_button = None
        self.stop_button = None
        self.capture_button = None
        
        self.setup_gui()
        self.setup_global_hotkeys()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg="#3b3b3b", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Screen capture controls
        capture_frame = tk.LabelFrame(left_panel, text="Screen Capture", 
                                     fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        capture_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.capture_button = tk.Button(capture_frame, text="Capture Screen", 
                                       command=self.capture_screen,
                                       bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.capture_button.pack(pady=5)
        
        # Circle controls
        circle_frame = tk.LabelFrame(left_panel, text="Circle Controls", 
                                    fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        circle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create circles button
        create_button = tk.Button(circle_frame, text="Create 5 Circles", 
                                 command=self.create_circles,
                                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        create_button.pack(pady=5)
        
        # Clear circles button
        clear_button = tk.Button(circle_frame, text="Clear Circles", 
                                command=self.clear_circles,
                                bg="#ff9800", fg="white", font=("Arial", 10, "bold"))
        clear_button.pack(pady=5)
        
        # Load/Save positions buttons
        load_save_frame = tk.Frame(circle_frame, bg="#3b3b3b")
        load_save_frame.pack(fill=tk.X, pady=5)
        
        load_button = tk.Button(load_save_frame, text="Load Positions", 
                               command=self.load_positions,
                               bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
        load_button.pack(side=tk.LEFT, padx=2)
        
        save_button = tk.Button(load_save_frame, text="Save Positions", 
                               command=self.save_positions,
                               bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
        save_button.pack(side=tk.RIGHT, padx=2)
        
        # Add extra circle button
        add_circle_button = tk.Button(circle_frame, text="Add Extra Circle", 
                                     command=self.add_extra_circle,
                                     bg="#FF5722", fg="white", font=("Arial", 10, "bold"))
        add_circle_button.pack(pady=5)
        
        # Default positions button
        default_button = tk.Button(circle_frame, text="Load Default Positions", 
                                  command=self.load_default_positions,
                                  bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
        default_button.pack(pady=5)
        
        # Clicking controls
        click_frame = tk.LabelFrame(left_panel, text="Auto Clicking", 
                                   fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        click_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Click count input
        click_input_frame = tk.Frame(click_frame, bg="#3b3b3b")
        click_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(click_input_frame, text="Click Count:", 
                fg="white", bg="#3b3b3b").pack(side=tk.LEFT)
        
        self.click_entry = tk.Entry(click_input_frame, width=10, font=("Arial", 10))
        self.click_entry.pack(side=tk.RIGHT)
        self.click_entry.insert(0, "5")
        
        # Click settings
        settings_frame = tk.LabelFrame(click_frame, text="Click Settings", 
                                     fg="white", bg="#3b3b3b", font=("Arial", 10, "bold"))
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Double click checkbox
        self.double_click_var = tk.BooleanVar()
        double_click_check = tk.Checkbutton(settings_frame, text="Double Click", 
                                          variable=self.double_click_var,
                                          fg="white", bg="#3b3b3b", 
                                          selectcolor="#2b2b2b", font=("Arial", 9))
        double_click_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # Click speed setting
        speed_frame = tk.Frame(settings_frame, bg="#3b3b3b")
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(speed_frame, text="Click Speed (ms):", 
                fg="white", bg="#3b3b3b", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.click_speed_entry = tk.Entry(speed_frame, width=8, font=("Arial", 9))
        self.click_speed_entry.pack(side=tk.RIGHT)
        self.click_speed_entry.insert(0, "200")
        
        # Keybind inputs
        keybind_frame = tk.Frame(click_frame, bg="#3b3b3b")
        keybind_frame.pack(fill=tk.X, pady=5)
        
        # Keybinds button
        keybinds_button = tk.Button(keybind_frame, text="Keybinds", 
                                   command=self.open_keybinds_window,
                                   bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        keybinds_button.pack(pady=5)
        
        # Click buttons
        button_frame = tk.Frame(click_frame, bg="#3b3b3b")
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = tk.Button(button_frame, text="Start Clicking", 
                                    command=self.start_clicking,
                                    bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = tk.Button(button_frame, text="Stop", 
                                   command=self.stop_clicking,
                                   bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                                   state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT)
        
        
        # Status display
        status_frame = tk.LabelFrame(left_panel, text="Status", 
                                   fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, 
                                                   bg="#1e1e1e", fg="white", 
                                                   font=("Consolas", 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Canvas
        right_panel = tk.Frame(main_frame, bg="#3b3b3b", relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Canvas display
        canvas_frame = tk.LabelFrame(right_panel, text="Drag Circles to Position", 
                                   fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1e1e1e", 
                               width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instructions
        instructions = tk.Label(canvas_frame, 
                               text="1. Capture Screen 2. Create Circles 3. Drag to position 4. Start Clicking",
                               fg="white", bg="#3b3b3b", font=("Arial", 10))
        instructions.pack(pady=5)
        
    def log_message(self, message):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        
    def capture_screen(self):
        """Capture the current screen"""
        self.log_message("Capturing screen...")
        
        # Capture screen
        screenshot = pyautogui.screenshot()
        self.current_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Get screen dimensions
        self.screen_width, self.screen_height = screenshot.size
        
        # Create display image
        display_image = self.current_screen.copy()
        
        # Convert to PIL Image and display
        display_image_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(display_image_rgb)
        
        # Resize to fit canvas
        pil_image = pil_image.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # Display on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        self.log_message(f"Screen captured! Size: {self.screen_width}x{self.screen_height}")
        self.log_message("Now create circles and drag them to your desired positions")
    
    def create_circles(self):
        """Create 5 draggable circles"""
        if not hasattr(self, 'photo'):
            messagebox.showwarning("Warning", "Please capture screen first!")
            return
        
        # Clear existing circles
        self.clear_circles()
        
        # Create 5 circles with grey background
        # Default screen coordinates: (739, 954), (801, 954), (864, 954), (924, 952), (984, 954)
        screen_coords = [
            (739, 954), (801, 954), (864, 954), (924, 952), (984, 954)
        ]
        
        for i in range(5):
            screen_x, screen_y = screen_coords[i]
            # Convert screen coordinates to canvas coordinates
            canvas_x, canvas_y = self.screen_to_canvas_coords(screen_x, screen_y)
            circle = DraggableCircle(
                self.canvas, canvas_x, canvas_y, 
                radius=15, 
                color="grey",  # All circles are grey now
                number=i+1
            )
            self.circles.append(circle)
        
        self.log_message("Created 5 draggable circles. Drag them to your desired positions!")
    
    def clear_circles(self):
        """Clear all circles"""
        for circle in self.circles:
            self.canvas.delete(circle.circle)
            self.canvas.delete(circle.label)
        self.circles = []
        self.log_message("Circles cleared")
    
    def add_extra_circle(self):
        """Add an extra circle to the canvas"""
        if not hasattr(self, 'photo'):
            messagebox.showwarning("Warning", "Please capture screen first!")
            return
        
        # Calculate position for new circle (to the right of existing ones)
        if self.circles:
            # Find the rightmost circle and place new one to its right
            max_x = max(circle.x for circle in self.circles)
            new_x = max_x + 80  # 80 pixels to the right
            new_y = self.circles[0].y  # Same Y as first circle
        else:
            # If no circles, place at center
            new_x = self.canvas_width // 2
            new_y = self.canvas_height // 2
        
        # Create new circle
        circle_number = len(self.circles) + 1
        circle = DraggableCircle(
            self.canvas, new_x, new_y,
            radius=15,
            color="grey",  # All circles are grey now
            number=circle_number
        )
        self.circles.append(circle)
        
        self.log_message(f"Added circle {circle_number}. Total circles: {len(self.circles)}")
    
    def save_positions(self):
        """Save current circle positions to JSON file"""
        if not self.circles:
            messagebox.showwarning("Warning", "No circles to save!")
            return
        
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Circle Positions"
        )
        
        if not file_path:
            return
        
        try:
            # Collect circle positions
            positions = []
            for i, circle in enumerate(self.circles):
                canvas_x, canvas_y = circle.get_position()
                screen_x, screen_y = self.canvas_to_screen_coords(canvas_x, canvas_y)
                positions.append({
                    "circle_number": i + 1,
                    "screen_x": screen_x,
                    "screen_y": screen_y,
                    "canvas_x": canvas_x,
                    "canvas_y": canvas_y
                })
            
            # Save to JSON
            with open(file_path, 'w') as f:
                json.dump(positions, f, indent=2)
            
            self.log_message(f"Circle positions saved to: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save positions: {str(e)}")
            self.log_message(f"Save error: {str(e)}")
    
    def load_positions(self):
        """Load circle positions from JSON file"""
        # Get file path from user
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Circle Positions"
        )
        
        if not file_path:
            return
        
        try:
            # Load JSON data
            with open(file_path, 'r') as f:
                positions = json.load(f)
            
            # Clear existing circles
            self.clear_circles()
            
            # Create circles at loaded positions (no limit on number)
            for i, pos_data in enumerate(positions):
                # Use screen coordinates if available, otherwise canvas coordinates
                if "screen_x" in pos_data and "screen_y" in pos_data:
                    screen_x = pos_data["screen_x"]
                    screen_y = pos_data["screen_y"]
                    canvas_x, canvas_y = self.screen_to_canvas_coords(screen_x, screen_y)
                else:
                    canvas_x = pos_data["canvas_x"]
                    canvas_y = pos_data["canvas_y"]
                
                # Create circle with grey background
                circle = DraggableCircle(
                    self.canvas, canvas_x, canvas_y,
                    radius=15,
                    color="grey",  # All circles are grey now
                    number=i + 1
                )
                self.circles.append(circle)
            
            self.log_message(f"Loaded {len(self.circles)} circle positions from: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load positions: {str(e)}")
            self.log_message(f"Load error: {str(e)}")
    
    def load_default_positions(self):
        """Load default circle positions from default_positions.json"""
        default_file = "default_positions.json"
        
        if not os.path.exists(default_file):
            messagebox.showerror("Error", f"Default positions file not found: {default_file}")
            self.log_message(f"Default file not found: {default_file}")
            return
        
        try:
            # Load JSON data
            with open(default_file, 'r') as f:
                positions = json.load(f)
            
            # Clear existing circles
            self.clear_circles()
            
            # Create circles at default positions
            for i, pos_data in enumerate(positions):
                # Use screen coordinates
                screen_x = pos_data["screen_x"]
                screen_y = pos_data["screen_y"]
                canvas_x, canvas_y = self.screen_to_canvas_coords(screen_x, screen_y)
                
                # Create circle with grey background
                circle = DraggableCircle(
                    self.canvas, canvas_x, canvas_y,
                    radius=15,
                    color="grey",  # All circles are grey now
                    number=i + 1
                )
                self.circles.append(circle)
            
            self.log_message(f"Loaded default positions for {len(self.circles)} circles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default positions: {str(e)}")
            self.log_message(f"Default load error: {str(e)}")
    
    def open_keybinds_window(self):
        """Open keybinds settings window"""
        keybinds_window = tk.Toplevel(self.root)
        keybinds_window.title("Keybinds Settings")
        keybinds_window.geometry("300x200")
        keybinds_window.configure(bg='#2b2b2b')
        keybinds_window.resizable(False, False)
        
        # Center the window
        keybinds_window.transient(self.root)
        keybinds_window.grab_set()
        
        # Title
        title_label = tk.Label(keybinds_window, text="Keybinds Settings", 
                              font=("Arial", 14, "bold"), 
                              fg="white", bg="#2b2b2b")
        title_label.pack(pady=10)
        
        # Keybinds frame
        keybinds_frame = tk.Frame(keybinds_window, bg="#3b3b3b", relief=tk.RAISED, bd=2)
        keybinds_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Start key
        start_frame = tk.Frame(keybinds_frame, bg="#3b3b3b")
        start_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(start_frame, text="Start Key:", 
                fg="white", bg="#3b3b3b", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        start_key_label = tk.Label(start_frame, text="Y", 
                                  fg="#4CAF50", bg="#3b3b3b", font=("Arial", 12, "bold"))
        start_key_label.pack(side=tk.RIGHT)
        
        # Stop key
        stop_frame = tk.Frame(keybinds_frame, bg="#3b3b3b")
        stop_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stop_frame, text="Stop Key:", 
                fg="white", bg="#3b3b3b", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        stop_key_label = tk.Label(stop_frame, text="N", 
                                 fg="#f44336", bg="#3b3b3b", font=("Arial", 12, "bold"))
        stop_key_label.pack(side=tk.RIGHT)
        
        # Info text
        info_text = tk.Text(keybinds_frame, height=4, width=30, 
                           bg="#1e1e1e", fg="white", font=("Arial", 9),
                           wrap=tk.WORD, state=tk.DISABLED)
        info_text.pack(padx=10, pady=5)
        
        info_content = """• Press 'Y' key to start auto-clicking
• Press 'N' key to stop auto-clicking
• Hotkeys work system-wide (even when window not focused)"""
        
        info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(keybinds_window, text="Close", 
                                command=keybinds_window.destroy,
                                bg="#666666", fg="white", font=("Arial", 10, "bold"))
        close_button.pack(pady=10)
    
    def canvas_to_screen_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to screen coordinates"""
        scale_x = self.screen_width / self.canvas_width
        scale_y = self.screen_height / self.canvas_height
        
        screen_x = int(canvas_x * scale_x)
        screen_y = int(canvas_y * scale_y)
        
        return screen_x, screen_y
    
    def screen_to_canvas_coords(self, screen_x, screen_y):
        """Convert screen coordinates to canvas coordinates"""
        scale_x = self.canvas_width / self.screen_width
        scale_y = self.canvas_height / self.screen_height
        
        canvas_x = int(screen_x * scale_x)
        canvas_y = int(screen_y * scale_y)
        
        return canvas_x, canvas_y
    
    
    def start_clicking(self):
        """Start auto-clicking on circle positions"""
        try:
            self.target_clicks = int(self.click_entry.get())
            if self.target_clicks <= 0:
                messagebox.showerror("Error", "Click count must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        if not self.circles:
            messagebox.showwarning("Warning", "No circles created. Create circles first.")
            return
        
        self.is_clicking = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        
        # Get click settings
        double_click = self.double_click_var.get()
        try:
            click_speed = int(self.click_speed_entry.get())
        except ValueError:
            click_speed = 200
            self.log_message("Invalid click speed, using default 200ms")
        
        self.log_message(f"Starting auto-clicking: {self.target_clicks} cycles of {len(self.circles)} circles each")
        self.log_message(f"Settings: {'Double click' if double_click else 'Single click'}, {click_speed}ms speed")
        self.log_message("Press 'n' key to stop auto-clicking at any time")
        
        # Make sure window stays focused for key detection
        self.root.focus_force()
        self.root.lift()
        
        # Start clicking thread
        clicking_thread = threading.Thread(target=self.clicking_loop, daemon=True)
        clicking_thread.start()
    
    def clicking_loop(self):
        """Auto-clicking loop running in separate thread"""
        cycle_count = 0
        total_clicks = 0
        
        while self.is_clicking and cycle_count < self.target_clicks:
            try:
                cycle_count += 1
                self.log_message(f"Starting cycle {cycle_count}/{self.target_clicks}")
                
                # Click on each circle in order
                for i, circle in enumerate(self.circles):
                    if not self.is_clicking:
                        break
                    
                    canvas_x, canvas_y = circle.get_position()
                    screen_x, screen_y = self.canvas_to_screen_coords(canvas_x, canvas_y)
                    
                    # Get click settings
                    double_click = self.double_click_var.get()
                    try:
                        click_speed = int(self.click_speed_entry.get()) / 1000.0  # Convert to seconds
                    except ValueError:
                        click_speed = 0.2
                    
                    # Move mouse and click
                    if double_click:
                        pyautogui.doubleClick(screen_x, screen_y)
                        total_clicks += 2
                        self.log_message(f"Cycle {cycle_count}: Double clicked circle {i+1} at screen({screen_x}, {screen_y}) - Total clicks: {total_clicks}")
                    else:
                        pyautogui.click(screen_x, screen_y)
                        total_clicks += 1
                        self.log_message(f"Cycle {cycle_count}: Clicked circle {i+1} at screen({screen_x}, {screen_y}) - Total clicks: {total_clicks}")
                    
                    # Delay between clicks
                    time.sleep(click_speed)
                
                self.log_message(f"Completed cycle {cycle_count}/{self.target_clicks}")
                
                # Delay between cycles
                if cycle_count < self.target_clicks:
                    time.sleep(0.5)
                
            except Exception as e:
                self.log_message(f"Clicking error: {str(e)}")
                time.sleep(1)
        
        # Clicking finished
        self.root.after(0, lambda: self.clicking_finished(total_clicks))
    
    def clicking_finished(self, total_clicks):
        """Called when clicking is finished"""
        self.is_clicking = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.log_message(f"Auto-clicking completed: {total_clicks} total clicks performed")
    
    def stop_clicking(self):
        """Stop auto-clicking"""
        self.is_clicking = False
        self.log_message("Stopped auto-clicking")
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
    
    
    def setup_global_hotkeys(self):
        """Setup global hotkey detection"""
        try:
            keyboard.add_hotkey('n', self.global_n_key_press)
            keyboard.add_hotkey('y', self.global_y_key_press)
            self.log_message("Global hotkeys 'n' (stop) and 'y' (start) registered successfully")
        except Exception as e:
            self.log_message(f"Could not register global hotkeys: {e}")
    
    def global_n_key_press(self):
        """Handle global N key press (stop) - works even when window not focused"""
        if self.is_clicking:
            self.log_message("Global N key pressed - stopping auto-clicking")
            self.stop_clicking()
    
    def global_y_key_press(self):
        """Handle global Y key press (start) - works even when window not focused"""
        if not self.is_clicking:
            self.log_message("Global Y key pressed - starting auto-clicking")
            self.start_clicking()
    

def main():
    root = tk.Tk()
    app = AQWPSClickerV2(root)
    
    # Handle window closing
    def on_closing():
        app.is_clicking = False
        try:
            keyboard.unhook_all()  # Clean up global hotkeys
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
