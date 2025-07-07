import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
import win32gui
import win32con
import win32api
import win32process
import subprocess
import keyboard
import pyautogui
from PIL import Image, ImageTk
import ctypes
from ctypes import wintypes

class KeyMapper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scrcpy Key Mapper")
        self.root.geometry("800x600")
        
        # Key mappings storage
        self.key_mappings = {}
        self.config_file = "key_mappings.json"
        
        # Scrcpy window handle
        self.scrcpy_hwnd = None
        
        # Overlay window
        self.overlay_window = None
        
        # Monitoring thread
        self.monitoring = False
        self.monitor_thread = None
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Scrcpy Key Mapper", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Scrcpy controls
        scrcpy_frame = ttk.LabelFrame(main_frame, text="Scrcpy Controls", padding="10")
        scrcpy_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(scrcpy_frame, text="Launch Scrcpy", command=self.launch_scrcpy).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(scrcpy_frame, text="Find Scrcpy Window", command=self.find_scrcpy_window).grid(row=0, column=1, padx=(0, 10))
        self.scrcpy_status = ttk.Label(scrcpy_frame, text="Status: Not connected")
        self.scrcpy_status.grid(row=0, column=2, padx=(10, 0))
        
        # Key mapping frame
        mapping_frame = ttk.LabelFrame(main_frame, text="Key Mappings", padding="10")
        mapping_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Add mapping controls
        add_frame = ttk.Frame(mapping_frame)
        add_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(add_frame, text="Key:").grid(row=0, column=0, padx=(0, 5))
        self.key_entry = ttk.Entry(add_frame, width=10)
        self.key_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(add_frame, text="X:").grid(row=0, column=2, padx=(0, 5))
        self.x_entry = ttk.Entry(add_frame, width=8)
        self.x_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(add_frame, text="Y:").grid(row=0, column=4, padx=(0, 5))
        self.y_entry = ttk.Entry(add_frame, width=8)
        self.y_entry.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Button(add_frame, text="Add Mapping", command=self.add_mapping).grid(row=0, column=6, padx=(10, 0))
        ttk.Button(add_frame, text="Capture Position", command=self.capture_position).grid(row=0, column=7, padx=(10, 0))
        
        # Mappings list
        self.mappings_tree = ttk.Treeview(mapping_frame, columns=("Key", "X", "Y"), show="headings", height=8)
        self.mappings_tree.heading("Key", text="Key")
        self.mappings_tree.heading("X", text="X Position")
        self.mappings_tree.heading("Y", text="Y Position")
        self.mappings_tree.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(mapping_frame, orient=tk.VERTICAL, command=self.mappings_tree.yview)
        scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))
        self.mappings_tree.configure(yscrollcommand=scrollbar.set)
        
        # Mapping controls
        controls_frame = ttk.Frame(mapping_frame)
        controls_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(controls_frame, text="Delete Selected", command=self.delete_mapping).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(controls_frame, text="Save Config", command=self.save_config).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_frame, text="Load Config", command=self.load_config).grid(row=0, column=2, padx=(0, 10))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Key Mapping", command=self.start_mapping)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Key Mapping", command=self.stop_mapping, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="Show Overlay", command=self.show_overlay).grid(row=0, column=2, padx=(0, 10))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(1, weight=1)
        
    def launch_scrcpy(self):
        try:
            subprocess.Popen(['scrcpy'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            messagebox.showinfo("Success", "Scrcpy launched! Please wait for the window to appear, then click 'Find Scrcpy Window'.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Scrcpy not found. Please ensure scrcpy is installed and in your PATH.")
    
    def find_scrcpy_window(self):
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if 'scrcpy' in window_title.lower():
                    windows.append((hwnd, window_title))
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            self.scrcpy_hwnd = windows[0][0]
            self.scrcpy_status.config(text=f"Status: Connected to {windows[0][1]}")
            messagebox.showinfo("Success", f"Found scrcpy window: {windows[0][1]}")
        else:
            messagebox.showerror("Error", "No scrcpy window found. Please make sure scrcpy is running.")
    
    def capture_position(self):
        if not self.scrcpy_hwnd:
            messagebox.showerror("Error", "Please find scrcpy window first.")
            return
        
        messagebox.showinfo("Position Capture", "Click on the scrcpy window where you want to map the key. You have 3 seconds after clicking OK.")
        
        # Wait 3 seconds then capture mouse position
        self.root.after(3000, self._capture_mouse_position)
    
    def _capture_mouse_position(self):
        x, y = pyautogui.position()
        
        # Convert to relative position within scrcpy window
        if self.scrcpy_hwnd:
            rect = win32gui.GetWindowRect(self.scrcpy_hwnd)
            relative_x = x - rect[0]
            relative_y = y - rect[1]
            
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(relative_x))
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(relative_y))
            
            messagebox.showinfo("Position Captured", f"Position captured: ({relative_x}, {relative_y})")
    
    def add_mapping(self):
        key = self.key_entry.get().strip()
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
        except ValueError:
            messagebox.showerror("Error", "X and Y coordinates must be numbers.")
            return
        
        if not key:
            messagebox.showerror("Error", "Please enter a key.")
            return
        
        self.key_mappings[key.lower()] = (x, y)
        self.update_mappings_display()
        
        # Clear entries
        self.key_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
    
    def delete_mapping(self):
        selected = self.mappings_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mapping to delete.")
            return
        
        item = self.mappings_tree.item(selected[0])
        key = item['values'][0]
        
        if key in self.key_mappings:
            del self.key_mappings[key]
            self.update_mappings_display()
    
    def update_mappings_display(self):
        # Clear existing items
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)
        
        # Add current mappings
        for key, (x, y) in self.key_mappings.items():
            self.mappings_tree.insert("", tk.END, values=(key, x, y))
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.key_mappings, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.key_mappings = json.load(f)
                self.update_mappings_display()
                messagebox.showinfo("Success", "Configuration loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def start_mapping(self):
        if not self.scrcpy_hwnd:
            messagebox.showerror("Error", "Please find scrcpy window first.")
            return
        
        if not self.key_mappings:
            messagebox.showerror("Error", "Please add at least one key mapping.")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_keys, daemon=True)
        self.monitor_thread.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        messagebox.showinfo("Success", "Key mapping started! Press mapped keys to interact with scrcpy.")
    
    def stop_mapping(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Success", "Key mapping stopped.")
    
    def _monitor_keys(self):
        for key in self.key_mappings.keys():
            keyboard.add_hotkey(key, lambda k=key: self._handle_key_press(k))
        
        while self.monitoring:
            time.sleep(0.1)
        
        keyboard.clear_all_hotkeys()
    
    def _handle_key_press(self, key):
        if key in self.key_mappings and self.scrcpy_hwnd:
            x, y = self.key_mappings[key]
            
            # Get window position
            rect = win32gui.GetWindowRect(self.scrcpy_hwnd)
            screen_x = rect[0] + x
            screen_y = rect[1] + y
            
            # Send click to scrcpy window
            win32gui.SetForegroundWindow(self.scrcpy_hwnd)
            win32api.SetCursorPos((screen_x, screen_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
    
    def show_overlay(self):
        if not self.scrcpy_hwnd:
            messagebox.showerror("Error", "Please find scrcpy window first.")
            return
        
        if self.overlay_window:
            self.overlay_window.destroy()
        
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("Key Mapping Overlay")
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-alpha', 0.7)
        
        # Position overlay over scrcpy window
        rect = win32gui.GetWindowRect(self.scrcpy_hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        self.overlay_window.geometry(f"{width}x{height}+{rect[0]}+{rect[1]}")
        
        # Create canvas for overlay
        canvas = tk.Canvas(self.overlay_window, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw key mappings
        for key, (x, y) in self.key_mappings.items():
            canvas.create_oval(x-15, y-15, x+15, y+15, fill='red', outline='white', width=2)
            canvas.create_text(x, y, text=key.upper(), fill='white', font=('Arial', 12, 'bold'))
        
        # Add close button
        close_btn = tk.Button(self.overlay_window, text="Close Overlay", command=self.overlay_window.destroy)
        close_btn.pack(side=tk.BOTTOM, pady=5)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyMapper()
    app.run()
