import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import time
import threading
from datetime import datetime

class PixelDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Color Detection & Click Automation")
        self.root.geometry("800x600")
        
        # State variables
        self.selected_color = None
        self.click_position = None
        self.tolerance = 10
        self.actions = []
        self.is_recording = False
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Disable pyautogui failsafe for smooth operation
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Color Detection Tab
        color_frame = ttk.Frame(notebook)
        notebook.add(color_frame, text="Color Detection")
        self.setup_color_tab(color_frame)
        
        # Action Recording Tab
        action_frame = ttk.Frame(notebook)
        notebook.add(action_frame, text="Action Recording")
        self.setup_action_tab(action_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)
        
    def setup_color_tab(self, parent):
        # Color selection section
        color_section = ttk.LabelFrame(parent, text="Color Selection", padding=10)
        color_section.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(color_section, text="Select Color from Screen", 
                  command=self.select_color_from_screen).pack(side=tk.LEFT, padx=5)
        
        self.color_display = tk.Canvas(color_section, width=50, height=30, bg='white')
        self.color_display.pack(side=tk.LEFT, padx=10)
        
        self.color_info = tk.Label(color_section, text="No color selected")
        self.color_info.pack(side=tk.LEFT, padx=10)
        
        # Click position section
        click_section = ttk.LabelFrame(parent, text="Click Position", padding=10)
        click_section.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(click_section, text="Select Click Position", 
                  command=self.select_click_position).pack(side=tk.LEFT, padx=5)
        
        self.position_info = tk.Label(click_section, text="No position selected")
        self.position_info.pack(side=tk.LEFT, padx=10)
        
        # Tolerance section
        tolerance_section = ttk.LabelFrame(parent, text="Color Tolerance", padding=10)
        tolerance_section.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(tolerance_section, text="Tolerance:").pack(side=tk.LEFT)
        self.tolerance_var = tk.IntVar(value=self.tolerance)
        tolerance_scale = tk.Scale(tolerance_section, from_=0, to=50, orient=tk.HORIZONTAL,
                                 variable=self.tolerance_var, command=self.update_tolerance)
        tolerance_scale.pack(side=tk.LEFT, padx=5)
        
        # Monitor section
        monitor_section = ttk.LabelFrame(parent, text="Monitoring", padding=10)
        monitor_section.pack(fill=tk.X, padx=5, pady=5)
        
        self.monitor_btn = ttk.Button(monitor_section, text="Start Monitoring", 
                                     command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(monitor_section, text="Status: Idle", fg="blue")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Results section
        results_section = ttk.LabelFrame(parent, text="Detection Results", padding=10)
        results_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_section, height=10)
        scrollbar = ttk.Scrollbar(results_section, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_action_tab(self, parent):
        # Recording controls
        record_section = ttk.LabelFrame(parent, text="Action Recording", padding=10)
        record_section.pack(fill=tk.X, padx=5, pady=5)
        
        self.record_btn = ttk.Button(record_section, text="Start Recording", 
                                    command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(record_section, text="Clear Actions", 
                  command=self.clear_actions).pack(side=tk.LEFT, padx=5)
        
        self.record_status = tk.Label(record_section, text="Not recording", fg="red")
        self.record_status.pack(side=tk.LEFT, padx=10)
        
        # Playback controls
        playback_section = ttk.LabelFrame(parent, text="Action Playback", padding=10)
        playback_section.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(playback_section, text="Play Actions", 
                  command=self.play_actions).pack(side=tk.LEFT, padx=5)
        
        tk.Label(playback_section, text="Delay (seconds):").pack(side=tk.LEFT, padx=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        delay_spin = tk.Spinbox(playback_section, from_=0.1, to=10.0, increment=0.1, 
                               textvariable=self.delay_var, width=5)
        delay_spin.pack(side=tk.LEFT, padx=5)
        
        # Save/Load controls
        file_section = ttk.LabelFrame(parent, text="Save/Load Actions", padding=10)
        file_section.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_section, text="Save Actions", 
                  command=self.save_actions).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_section, text="Load Actions", 
                  command=self.load_actions).pack(side=tk.LEFT, padx=5)
        
        # Actions list
        actions_section = ttk.LabelFrame(parent, text="Recorded Actions", padding=10)
        actions_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.actions_tree = ttk.Treeview(actions_section, columns=('Type', 'Details', 'Time'), show='headings')
        self.actions_tree.heading('Type', text='Action Type')
        self.actions_tree.heading('Details', text='Details')
        self.actions_tree.heading('Time', text='Timestamp')
        
        actions_scrollbar = ttk.Scrollbar(actions_section, orient="vertical", command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=actions_scrollbar.set)
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        actions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_settings_tab(self, parent):
        # General settings
        general_section = ttk.LabelFrame(parent, text="General Settings", padding=10)
        general_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Click behavior
        tk.Label(general_section, text="Click Type:").grid(row=0, column=0, sticky='w', pady=2)
        self.click_type = tk.StringVar(value="left")
        click_combo = ttk.Combobox(general_section, textvariable=self.click_type, 
                                  values=["left", "right", "double"], width=10)
        click_combo.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Detection frequency
        tk.Label(general_section, text="Check Frequency (ms):").grid(row=1, column=0, sticky='w', pady=2)
        self.frequency_var = tk.IntVar(value=100)
        frequency_spin = tk.Spinbox(general_section, from_=50, to=2000, increment=50,
                                   textvariable=self.frequency_var, width=10)
        frequency_spin.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Hotkeys section
        hotkey_section = ttk.LabelFrame(parent, text="Hotkeys", padding=10)
        hotkey_section.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(hotkey_section, text="• Press ESC to stop any running operation").pack(anchor='w')
        tk.Label(hotkey_section, text="• Press SPACE while selecting to confirm").pack(anchor='w')
        tk.Label(hotkey_section, text="• Move mouse to top-left corner to emergency stop").pack(anchor='w')
        
    def select_color_from_screen(self):
        """Allow user to select a color from anywhere on screen"""
        self.root.withdraw()  # Hide main window
        messagebox.showinfo("Color Selection", "Click anywhere on the screen to select a color.\nPress ESC to cancel.")
        
        # Wait for click
        try:
            time.sleep(1)  # Give user time to read message
            x, y = pyautogui.position()
            
            # Capture screenshot and get color at position
            screenshot = pyautogui.screenshot()
            rgb_color = screenshot.getpixel((x, y))
            
            self.selected_color = rgb_color
            self.update_color_display()
            
            self.log(f"Selected color RGB{rgb_color} at position ({x}, {y})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select color: {e}")
        finally:
            self.root.deiconify()  # Show main window again
            
    def select_click_position(self):
        """Allow user to select where to click when color is detected"""
        self.root.withdraw()
        messagebox.showinfo("Position Selection", "Click where you want the automated click to occur.\nPress ESC to cancel.")
        
        try:
            time.sleep(1)
            x, y = pyautogui.position()
            
            self.click_position = (x, y)
            self.position_info.config(text=f"Click at: ({x}, {y})")
            
            self.log(f"Set click position to ({x}, {y})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select position: {e}")
        finally:
            self.root.deiconify()
            
    def update_color_display(self):
        """Update the color display canvas"""
        if self.selected_color:
            rgb = self.selected_color
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.color_display.config(bg=hex_color)
            self.color_info.config(text=f"RGB{rgb} | {hex_color}")
            
    def update_tolerance(self, value):
        """Update color tolerance"""
        self.tolerance = int(value)
        
    def color_matches(self, color1, color2, tolerance):
        """Check if two colors match within tolerance"""
        return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))
        
    def toggle_monitoring(self):
        """Start/stop color monitoring"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
            
    def start_monitoring(self):
        """Start monitoring for the selected color"""
        if not self.selected_color or not self.click_position:
            messagebox.showwarning("Warning", "Please select both a color and click position first.")
            return
            
        self.is_monitoring = True
        self.monitor_btn.config(text="Stop Monitoring")
        self.status_label.config(text="Status: Monitoring...", fg="green")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log("Started color monitoring")
        
    def stop_monitoring(self):
        """Stop color monitoring"""
        self.is_monitoring = False
        self.monitor_btn.config(text="Start Monitoring")
        self.status_label.config(text="Status: Stopped", fg="red")
        self.log("Stopped color monitoring")
        
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Take screenshot
                screenshot = pyautogui.screenshot()
                
                # Convert to numpy array for faster processing
                img_array = np.array(screenshot)
                
                # Find pixels matching the target color
                matches = self.find_color_matches(img_array, self.selected_color, self.tolerance)
                
                if len(matches) > 0:
                    self.log(f"Color detected! Found {len(matches)} matching pixels")
                    self.perform_click()
                    
                    if self.is_recording:
                        self.record_action("color_detection", {
                            "color": self.selected_color,
                            "matches": len(matches),
                            "click_position": self.click_position
                        })
                    
                    # Brief pause to avoid rapid clicking
                    time.sleep(0.5)
                    
                time.sleep(self.frequency_var.get() / 1000.0)  # Convert ms to seconds
                
            except Exception as e:
                self.log(f"Error during monitoring: {e}")
                break
                
    def find_color_matches(self, img_array, target_color, tolerance):
        """Find all pixels that match the target color within tolerance"""
        # Create a mask for pixels within tolerance
        diff = np.abs(img_array.astype(int) - np.array(target_color))
        mask = np.all(diff <= tolerance, axis=2)
        
        # Get coordinates of matching pixels
        matches = np.argwhere(mask)
        return matches
        
    def perform_click(self):
        """Perform the configured click action"""
        if self.click_position:
            x, y = self.click_position
            click_type = self.click_type.get()
            
            if click_type == "left":
                pyautogui.click(x, y)
            elif click_type == "right":
                pyautogui.rightClick(x, y)
            elif click_type == "double":
                pyautogui.doubleClick(x, y)
                
            self.log(f"Performed {click_type} click at ({x}, {y})")
            
    def toggle_recording(self):
        """Start/stop action recording"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Start recording actions"""
        self.is_recording = True
        self.record_btn.config(text="Stop Recording")
        self.record_status.config(text="Recording...", fg="green")
        self.log("Started action recording")
        
    def stop_recording(self):
        """Stop recording actions"""
        self.is_recording = False
        self.record_btn.config(text="Start Recording")
        self.record_status.config(text="Not recording", fg="red")
        self.log("Stopped action recording")
        
    def record_action(self, action_type, details):
        """Record an action with timestamp"""
        action = {
            "type": action_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.actions.append(action)
        self.update_actions_display()
        
    def update_actions_display(self):
        """Update the actions tree view"""
        # Clear existing items
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
            
        # Add all actions
        for i, action in enumerate(self.actions):
            details_str = str(action["details"])
            if len(details_str) > 50:
                details_str = details_str[:47] + "..."
                
            self.actions_tree.insert("", "end", values=(
                action["type"],
                details_str,
                action["timestamp"]
            ))
            
    def clear_actions(self):
        """Clear all recorded actions"""
        self.actions.clear()
        self.update_actions_display()
        self.log("Cleared all recorded actions")
        
    def play_actions(self):
        """Play back recorded actions"""
        if not self.actions:
            messagebox.showwarning("Warning", "No actions to play")
            return
            
        delay = self.delay_var.get()
        
        def play_thread():
            for action in self.actions:
                if action["type"] == "color_detection":
                    details = action["details"]
                    if "click_position" in details:
                        x, y = details["click_position"]
                        pyautogui.click(x, y)
                        self.log(f"Replayed click at ({x}, {y})")
                        
                time.sleep(delay)
                
        threading.Thread(target=play_thread, daemon=True).start()
        self.log(f"Playing {len(self.actions)} actions with {delay}s delay")
        
    def save_actions(self):
        """Save actions to a JSON file"""
        if not self.actions:
            messagebox.showwarning("Warning", "No actions to save")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        "actions": self.actions,
                        "settings": {
                            "selected_color": self.selected_color,
                            "click_position": self.click_position,
                            "tolerance": self.tolerance
                        }
                    }, f, indent=2)
                    
                messagebox.showinfo("Success", f"Actions saved to {filename}")
                self.log(f"Saved {len(self.actions)} actions to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save actions: {e}")
                
    def load_actions(self):
        """Load actions from a JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                self.actions = data.get("actions", [])
                settings = data.get("settings", {})
                
                # Restore settings if available
                if "selected_color" in settings and settings["selected_color"]:
                    self.selected_color = tuple(settings["selected_color"])
                    self.update_color_display()
                    
                if "click_position" in settings and settings["click_position"]:
                    self.click_position = tuple(settings["click_position"])
                    self.position_info.config(text=f"Click at: {self.click_position}")
                    
                if "tolerance" in settings:
                    self.tolerance = settings["tolerance"]
                    self.tolerance_var.set(self.tolerance)
                    
                self.update_actions_display()
                messagebox.showinfo("Success", f"Loaded {len(self.actions)} actions from {filename}")
                self.log(f"Loaded {len(self.actions)} actions from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load actions: {e}")
                
    def log(self, message):
        """Add a message to the results log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.results_text.insert(tk.END, log_message)
        self.results_text.see(tk.END)  # Scroll to bottom
        
    def on_closing(self):
        """Handle application closing"""
        self.is_monitoring = False
        self.is_recording = False
        self.root.destroy()

if __name__ == "__main__":
    # Check for required packages
    try:
        import pyautogui
        import cv2
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install pyautogui opencv-python pillow")
        exit(1)
        
    root = tk.Tk()
    app = PixelDetectorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    