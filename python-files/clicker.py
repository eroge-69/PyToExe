import tkinter as tk
import pyautogui
import time
import os
from threading import Thread
from datetime import datetime

class DraggableMarker:
    def __init__(self, app, parent, label, color, initial_pos):
        self.app = app
        self.parent = parent
        self.label_text = label
        
        # Create a toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Marker {label}")
        
        # Make window floating, frameless and always on top
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.8)
        
        # Calculate size
        self.size = 40
        
        # Create a circular frame with the marker label
        self.frame = tk.Frame(self.window, width=self.size, height=self.size, bg=color, bd=2, relief=tk.RAISED)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Add label in the center
        self.label = tk.Label(self.frame, text=label, font=("Arial", 12, "bold"), bg=color, fg="white")
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Position the window
        self.window.geometry(f"{self.size}x{self.size}+{initial_pos['x']}+{initial_pos['y']}")
        
        # Bind events for dragging
        self.frame.bind("<ButtonPress-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.on_drag)
        self.frame.bind("<ButtonRelease-1>", self.end_drag)
        
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
    def start_drag(self, event):
        self.dragging = True
        # Record the initial position of the mouse relative to the window
        self.drag_start_x = event.x_root - self.window.winfo_x()
        self.drag_start_y = event.y_root - self.window.winfo_y()
        
    def on_drag(self, event):
        if self.dragging:
            # Calculate new position
            new_x = event.x_root - self.drag_start_x
            new_y = event.y_root - self.drag_start_y
            
            # Move the window
            self.window.geometry(f"+{new_x}+{new_y}")
            
            # Update position in the app
            center_x = new_x + self.size//2
            center_y = new_y + self.size//2
            self.app.update_marker_position(self.label_text, center_x, center_y)
            
    def end_drag(self, event):
        self.dragging = False
        
    def get_position(self):
        x = self.window.winfo_x() + self.size//2
        y = self.window.winfo_y() + self.size//2
        return {"x": x, "y": y}
        
    def hide(self):
        self.window.withdraw()
        
    def show(self):
        self.window.deiconify()

class TradingAutoClickerBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Auto Clicker Bot - Buy/Sell")
        self.root.geometry("1000x900")  # Reduced height since we removed position C
        self.root.resizable(False, False)
        
        # Set default positions (only Buy and Sell now)
        self.click_positions = [
            {"x": 100, "y": 100},  # Buy position
            {"x": 200, "y": 200}   # Sell position
        ]
        
        self.is_running = False
        self.is_monitoring = False
        self.click_thread = None
        self.monitor_thread = None
        self.markers = {}
        
        # File monitoring variables
        self.file_path = ""
        self.last_modified_time = 0
        self.last_content = ""
        
        # Initialize position_labels dictionary
        self.position_labels = {}
        
        # Create UI
        self.create_widgets()
        
        # Create floating markers after a small delay
        self.root.after(100, self.create_markers)
    
    def create_widgets(self):
        # Title label
        title_label = tk.Label(self.root, text="Trading Auto Clicker Bot - Buy/Sell", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, text="Set file path and positions. Bot will click based on last line in file.", 
                               font=("Arial", 10), wraplength=600)
        instructions.pack(pady=5)
        
        # File selection frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(file_frame, text="Trading Signal File Path:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        file_input_frame = tk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X, pady=5)
        
        self.file_path_entry = tk.Entry(file_input_frame, font=("Arial", 9))
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.file_path_entry.insert(0, "C:\\Users\\YourUsername\\Desktop\\trading_signals.txt")
        
        browse_button = tk.Button(file_input_frame, text="Browse", command=self.browse_file,
                                bg="#2196F3", fg="white", font=("Arial", 9))
        browse_button.pack(side=tk.RIGHT)
        
        # File status frame
        file_status_frame = tk.Frame(file_frame)
        file_status_frame.pack(fill=tk.X, pady=5)
        
        self.file_status_label = tk.Label(file_status_frame, text="No file selected", 
                                        font=("Arial", 9), fg="red")
        self.file_status_label.pack(side=tk.LEFT)
        
        self.create_file_button = tk.Button(file_status_frame, text="Create Sample File", 
                                          command=self.create_sample_file,
                                          bg="#FF9800", fg="white", font=("Arial", 9))
        self.create_file_button.pack(side=tk.RIGHT)
        
        # File content display
        content_frame = tk.Frame(file_frame)
        content_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(content_frame, text="Last line in file:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.last_line_label = tk.Label(content_frame, text="(no content)", 
                                      font=("Arial", 9), fg="gray", bg="lightgray", 
                                      relief=tk.SUNKEN, padx=5, pady=2)
        self.last_line_label.pack(fill=tk.X, pady=2)
        
        # Position display frame
        position_display_frame = tk.Frame(self.root)
        position_display_frame.pack(pady=10)
        
        tk.Label(position_display_frame, text="Click Positions:", font=("Arial", 10, "bold")).pack()
        
        # Create position display labels for Buy and Sell
        for label in ["BUY", "SELL"]:
            idx = 0 if label == "BUY" else 1
            pos = self.click_positions[idx]
            pos_label = tk.Label(
                position_display_frame, 
                text=f"{label}: ({pos['x']}, {pos['y']})",
                font=("Arial", 9)
            )
            pos_label.pack(pady=2)
            self.position_labels[label] = pos_label
        
        # Click positions frame
        positions_frame = tk.Frame(self.root)
        positions_frame.pack(pady=10)
        
        # Position BUY
        pos_buy_frame = tk.Frame(positions_frame)
        pos_buy_frame.pack(pady=2)
        
        tk.Label(pos_buy_frame, text="BUY Position:", font=("Arial", 9, "bold"), fg="green").grid(row=0, column=0, padx=5)
        tk.Label(pos_buy_frame, text="X:").grid(row=0, column=1, padx=2)
        self.pos_buy_x = tk.Entry(pos_buy_frame, width=5)
        self.pos_buy_x.insert(0, str(self.click_positions[0]["x"]))
        self.pos_buy_x.grid(row=0, column=2, padx=2)
        
        tk.Label(pos_buy_frame, text="Y:").grid(row=0, column=3, padx=2)
        self.pos_buy_y = tk.Entry(pos_buy_frame, width=5)
        self.pos_buy_y.insert(0, str(self.click_positions[0]["y"]))
        self.pos_buy_y.grid(row=0, column=4, padx=2)
        
        # Position SELL
        pos_sell_frame = tk.Frame(positions_frame)
        pos_sell_frame.pack(pady=2)
        
        tk.Label(pos_sell_frame, text="SELL Position:", font=("Arial", 9, "bold"), fg="red").grid(row=0, column=0, padx=5)
        tk.Label(pos_sell_frame, text="X:").grid(row=0, column=1, padx=2)
        self.pos_sell_x = tk.Entry(pos_sell_frame, width=5)
        self.pos_sell_x.insert(0, str(self.click_positions[1]["x"]))
        self.pos_sell_x.grid(row=0, column=2, padx=2)
        
        tk.Label(pos_sell_frame, text="Y:").grid(row=0, column=3, padx=2)
        self.pos_sell_y = tk.Entry(pos_sell_frame, width=5)
        self.pos_sell_y.insert(0, str(self.click_positions[1]["y"]))
        self.pos_sell_y.grid(row=0, column=4, padx=2)
        
        # Update button
        update_button = tk.Button(positions_frame, text="Update Markers", command=self.update_from_entries, 
                                bg="#4CAF50", fg="white", font=("Arial", 9))
        update_button.pack(pady=5)
        
        # Marker visibility toggle
        marker_frame = tk.Frame(self.root)
        marker_frame.pack(pady=5)
        
        self.show_markers_var = tk.BooleanVar(value=True)
        self.show_markers_checkbox = tk.Checkbutton(
            marker_frame, 
            text="Show position markers", 
            variable=self.show_markers_var,
            command=self.toggle_markers,
            font=("Arial", 10)
        )
        self.show_markers_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Click delay setting
        delay_frame = tk.Frame(self.root)
        delay_frame.pack(pady=5)
        
        tk.Label(delay_frame, text="Click delay (seconds):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.delay_entry = tk.Entry(delay_frame, width=5)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.pack(side=tk.LEFT, padx=5)
        
        # Control buttons section
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20, padx=10, fill=tk.X)
        
        # Control label
        control_label = tk.Label(control_frame, text="CONTROLS", font=("Arial", 12, "bold"), fg="navy")
        control_label.pack(pady=5)
        
        # First row of buttons - Marker visibility
        marker_button_frame = tk.Frame(control_frame)
        marker_button_frame.pack(pady=5)
        
        self.hide_show_button = tk.Button(marker_button_frame, text="Hide Markers", 
                                        command=self.toggle_markers_visibility, 
                                        bg="#2196F3", fg="white", width=15, height=2, 
                                        font=("Arial", 10, "bold"))
        self.hide_show_button.pack()
        
        # Second row of buttons - Start/Stop monitoring
        action_button_frame = tk.Frame(control_frame)
        action_button_frame.pack(pady=10)
        
        self.start_monitor_button = tk.Button(action_button_frame, text="▶ START MONITORING", 
                                            command=self.start_monitoring, 
                                            bg="#4CAF50", fg="white", width=20, height=2, 
                                            font=("Arial", 12, "bold"))
        self.start_monitor_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_monitor_button = tk.Button(action_button_frame, text="⏹ STOP MONITORING", 
                                           command=self.stop_monitoring, 
                                           bg="#f44336", fg="white", width=20, height=2, 
                                           font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.stop_monitor_button.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready - Set file path and start monitoring", 
                                   font=("Arial", 10), fg="blue", wraplength=600)
        self.status_label.pack(pady=10)
        
        # Instructions label
        instructions_text = ("Instructions:\n"
                           "1. Set the path to your trading signal file\n"
                           "2. Position the BUY and SELL markers where you want clicks\n"
                           "3. Start monitoring\n"
                           "4. Write 'buy' or 'sell' as the last line in your file to trigger clicks")
        
        instructions_label = tk.Label(self.root, text=instructions_text, 
                                    font=("Arial", 9), fg="darkgreen", 
                                    justify=tk.LEFT, wraplength=600)
        instructions_label.pack(pady=10)
    
    def browse_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select trading signal file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.check_file_status()
    
    def create_sample_file(self):
        sample_path = os.path.join(os.path.expanduser("~"), "Desktop", "trading_signals.txt")
        try:
            with open(sample_path, 'w') as f:
                f.write("# Trading Signal Control File\n")
                f.write("# Write 'buy' or 'sell' on the last line to trigger clicks\n")
                f.write("# Example:\n")
                f.write("buy\n")
            
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, sample_path)
            self.check_file_status()
            self.status_label.config(text=f"Sample file created at: {sample_path}", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error creating sample file: {str(e)}", fg="red")
    
    def check_file_status(self):
        file_path = self.file_path_entry.get().strip()
        if not file_path:
            self.file_status_label.config(text="No file path specified", fg="red")
            return False
        
        if os.path.exists(file_path):
            self.file_status_label.config(text="✓ File exists", fg="green")
            self.file_path = file_path
            self.read_file_content()
            return True
        else:
            self.file_status_label.config(text="✗ File not found", fg="red")
            return False
    
    def read_file_content(self):
        try:
            if os.path.exists(self.file_path):
                # Try different encodings to handle various file types
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'ascii']
                
                for encoding in encodings:
                    try:
                        with open(self.file_path, 'r', encoding=encoding) as f:
                            lines = f.readlines()
                        break  # If successful, exit the loop
                    except UnicodeDecodeError:
                        continue  # Try next encoding
                else:
                    # If all encodings fail, try reading as binary and ignore errors
                    with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                
                if lines:
                    last_line = lines[-1].strip()
                    self.last_line_label.config(text=last_line if last_line else "(empty line)")
                    return last_line
                else:
                    self.last_line_label.config(text="(file is empty)")
                    return ""
        except Exception as e:
            self.last_line_label.config(text=f"Error reading file: {str(e)}")
            return ""
    
    def monitor_file(self):
        """Monitor file for changes and execute clicks"""
        while self.is_monitoring:
            try:
                if os.path.exists(self.file_path):
                    # Check if file was modified
                    current_modified_time = os.path.getmtime(self.file_path)
                    
                    if current_modified_time > self.last_modified_time:
                        self.last_modified_time = current_modified_time
                        
                        # Read the last line
                        last_line = self.read_file_content()
                        
                        # Debug: Show what we read
                        print(f"DEBUG: Read line: '{last_line}' (length: {len(last_line) if last_line else 0})")
                        
                        if last_line:
                            last_line_clean = last_line.lower().strip()
                            print(f"DEBUG: Cleaned line: '{last_line_clean}'")
                            
                            if last_line_clean in ['buy', 'sell']:
                                print(f"DEBUG: Executing click for: {last_line_clean}")
                                self.execute_click(last_line_clean)
                            else:
                                print(f"DEBUG: Line '{last_line_clean}' not recognized as buy/sell command")
                                # Update status to show what was read
                                self.status_label.config(
                                    text=f"Read: '{last_line_clean}' - Expected 'buy' or 'sell'", 
                                    fg="orange"
                                )
                                self.root.update()
                
                time.sleep(0.5)  # Check every 0.5 seconds
                
            except Exception as e:
                print(f"Error monitoring file: {e}")
                self.status_label.config(text=f"Monitor error: {str(e)}", fg="red")
                self.root.update()
                time.sleep(1)
    
    def execute_click(self, command):
        """Execute click based on command (buy or sell)"""
        try:
            delay = float(self.delay_entry.get())
        except:
            delay = 0.1
        
        # Map command to position index
        position_map = {'buy': 0, 'sell': 1}
        idx = position_map.get(command.lower())
        
        if idx is not None and idx < len(self.click_positions):
            position = self.click_positions[idx]
            label = command.upper()
            
            # Update status
            self.status_label.config(
                text=f"Executing {label} click at: ({position['x']}, {position['y']}) - {datetime.now().strftime('%H:%M:%S')}", 
                fg="green"
            )
            self.root.update()
            
            # Perform the click
            pyautogui.click(position["x"], position["y"])
            
            # Brief pause
            time.sleep(delay)
    
    def start_monitoring(self):
        if not self.check_file_status():
            self.status_label.config(text="Error: Please set a valid file path", fg="red")
            return
        
        # Update marker positions
        for label, marker in self.markers.items():
            if label == "BUY":
                idx = 0
            else:  # SELL
                idx = 1
            pos = marker.get_position()
            self.click_positions[idx] = pos
            self.position_labels[label].config(text=f"{label}: ({pos['x']}, {pos['y']})")
        
        self.is_monitoring = True
        self.last_modified_time = os.path.getmtime(self.file_path) if os.path.exists(self.file_path) else 0
        
        self.start_monitor_button.config(state=tk.DISABLED)
        self.stop_monitor_button.config(state=tk.NORMAL)
        self.hide_show_button.config(state=tk.DISABLED)
        
        # Start monitoring in a separate thread
        self.monitor_thread = Thread(target=self.monitor_file)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.status_label.config(text="Monitoring file for changes... Write 'buy' or 'sell' in the file to trigger clicks", fg="blue")
    
    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_monitor_button.config(state=tk.NORMAL)
        self.stop_monitor_button.config(state=tk.DISABLED)
        self.hide_show_button.config(state=tk.NORMAL)
        self.status_label.config(text="Monitoring stopped", fg="blue")
    
    def update_from_entries(self):
        """Update marker positions from entry fields"""
        try:
            # Update click positions from entries
            new_positions = [
                {"x": int(self.pos_buy_x.get()), "y": int(self.pos_buy_y.get())},
                {"x": int(self.pos_sell_x.get()), "y": int(self.pos_sell_y.get())}
            ]
            
            # Update click positions
            self.click_positions = new_positions
            
            # Update markers
            for idx, label in enumerate(["BUY", "SELL"]):
                if label in self.markers:
                    x, y = new_positions[idx]["x"], new_positions[idx]["y"]
                    
                    # Update marker position (center of the marker)
                    self.markers[label].window.geometry(f"+{x-20}+{y-20}")
                    
                    # Update position label
                    self.position_labels[label].config(text=f"{label}: ({x}, {y})")
            
            self.status_label.config(text="Marker positions updated from coordinates", fg="green")
            return True
            
        except ValueError:
            self.status_label.config(text="Error: Positions must be valid numbers", fg="red")
            return False
    
    def create_markers(self):
        marker_colors = {"BUY": "#4CAF50", "SELL": "#f44336"}  # Green for buy, red for sell
        
        for idx, label in enumerate(["BUY", "SELL"]):
            marker = DraggableMarker(
                self, 
                self.root, 
                label, 
                marker_colors[label], 
                {"x": self.click_positions[idx]["x"] - 20, "y": self.click_positions[idx]["y"] - 20}
            )
            self.markers[label] = marker
    
    def update_marker_position(self, label, x, y):
        # Find the index for the label
        if label == "BUY":
            idx = 0
        else:  # SELL
            idx = 1
        
        if 0 <= idx < len(self.click_positions):
            self.click_positions[idx]["x"] = x
            self.click_positions[idx]["y"] = y
            
            # Update entry fields
            if label == "BUY":
                self.pos_buy_x.delete(0, tk.END)
                self.pos_buy_x.insert(0, str(x))
                self.pos_buy_y.delete(0, tk.END)
                self.pos_buy_y.insert(0, str(y))
            elif label == "SELL":
                self.pos_sell_x.delete(0, tk.END)
                self.pos_sell_x.insert(0, str(x))
                self.pos_sell_y.delete(0, tk.END)
                self.pos_sell_y.insert(0, str(y))
            
            # Update position display label
            self.position_labels[label].config(text=f"{label}: ({x}, {y})")
    
    def toggle_markers(self):
        if self.show_markers_var.get():
            for marker in self.markers.values():
                marker.show()
        else:
            for marker in self.markers.values():
                marker.hide()
                
    def toggle_markers_visibility(self):
        current_state = self.show_markers_var.get()
        self.show_markers_var.set(not current_state)
        self.toggle_markers()
        
        # Update button text
        if self.show_markers_var.get():
            self.hide_show_button.config(text="Hide Markers")
        else:
            self.hide_show_button.config(text="Show Markers")

if __name__ == "__main__":
    # Check for required dependencies
    try:
        import pyautogui
    except ImportError:
        print("PyAutoGUI is not installed. Installing it now...")
        import subprocess
        subprocess.call(['pip', 'install', 'pyautogui'])
        import pyautogui
    
    # Create and run the application
    root = tk.Tk()
    app = TradingAutoClickerBot(root)
    root.mainloop()