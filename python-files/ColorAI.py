
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox # Import messagebox
import os # Import os for os.execl

# Check if running as a bundled executable
IS_FROZEN = getattr(sys, 'frozen', False)

# Define target colors (HEX to RGB)
COLORS = {
    "Purple": {"hex": "#AD00C8", "rgb": (173, 0, 200)},
    "Yellow": {"hex": "#FFE500", "rgb": (255, 229, 0)},
    "Red":    {"hex": "#FF2D00", "rgb": (255, 45, 0)},
}

# Screen resolution (fixed as per requirement)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# --- Dependency Check and Installation (placed before any main imports) ---
REQUIRED_PACKAGES = ['pyautogui', 'Pillow', 'pynput']

def check_and_install_dependencies():
    # Create a dummy root window just for messagebox
    temp_root = tk.Tk()
    temp_root.withdraw() # Hide the root window

    missing_packages = []
    for package in REQUIRED_PACKAGES:
        try:
            # Try to import each package
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        # Warn if running from an exe, as auto-install might not work as expected
        if IS_FROZEN:
            messagebox.showwarning(
                "Dependency Warning (EXE)",
                "This application is running as an executable.\n"
                "Auto-installation of dependencies might not work correctly if you don't have Python/pip installed globally or lack permissions.\n"
                f"Missing: {', '.join(missing_packages)}\n"
                "Please ensure you have Python and pip set up, or rebuild the EXE with all dependencies bundled."
            )
            # For a frozen executable, if dependencies are truly missing,
            # it indicates a build problem, and attempting pip install inside
            # might not fix it and could lead to more confusion.
            # It's better to just exit and let the user know.
            messagebox.showerror(
                "Missing Dependencies",
                f"The following required packages are missing: {', '.join(missing_packages)}.\n"
                "This executable cannot run without them. Please install them manually "
                "or ensure your PyInstaller build includes them.\n"
                "The application will now close."
            )
            temp_root.destroy()
            sys.exit(1)
        else: # Not frozen (running as .py script)
            msg = f"Missing packages detected: {', '.join(missing_packages)}.\n" \
                  "Attempting to install them. This may require administrative privileges."
            messagebox.showinfo("Dependency Installation", msg)
            
            try:
                # Use sys.executable to ensure pip installs into the correct environment
                pip_executable = [sys.executable, "-m", "pip", "install", "--upgrade"] + missing_packages
                process = subprocess.run(pip_executable, capture_output=True, text=True, check=False)

                if process.returncode != 0:
                    error_msg = f"ERROR: Failed to install packages: {', '.join(missing_packages)}.\n" \
                                f"Please install them manually using: pip install {' '.join(missing_packages)}\n" \
                                f"Installation Output:\n{process.stdout}\nErrors:\n{process.stderr}"
                    messagebox.showerror("Installation Failed", error_msg)
                    temp_root.destroy()
                    sys.exit(1)
                else:
                    messagebox.showinfo("Installation Success", "Packages installed successfully. The application will now restart to load them.")
                    temp_root.destroy()
                    # Re-execute the script after installation for clean imports
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
            except Exception as e:
                messagebox.showerror("Installation Error", f"An unexpected error occurred during dependency installation: {e}")
                temp_root.destroy()
                sys.exit(1)
    else:
        messagebox.showinfo("Dependency Check", "All required packages are already installed.")
    
    temp_root.destroy() # Destroy the temporary root window

# Call the dependency check function
check_and_install_dependencies()

# Now, after checks and potential restarts, import the core modules
# These imports must be AFTER check_and_install_dependencies()
import pyautogui
from PIL import ImageGrab
import threading
import time
from pynput import keyboard # pynput is already imported, but re-import here for clarity with the logic flow

class ColorFinderApp:
    def __init__(self, master):
        self.master = master
        master.title("Crane") # New title as requested
        master.geometry("400x550")
        master.resizable(False, False)
        master.configure(bg='black') # Set main window background to black

        # Configure ttk styles for black background and red accents
        style = ttk.Style()
        style.theme_use('clam') # Use a theme that allows for easier color modification

        # General background and foreground for most widgets
        style.configure('.', background='black', foreground='white')
        
        # LabelFrame styling
        style.configure('TLabelFrame', background='black', foreground='white')
        style.configure('TLabelFrame.Label', background='black', foreground='white', font=('Arial', 10, 'bold')) # Title of the frame

        # Label styling
        style.configure('TLabel', background='black', foreground='white')

        # Button styling
        style.configure('TButton', background='red', foreground='white', borderwidth=0, relief='flat')
        style.map('TButton', background=[('active', 'darkred')]) # Darker red on hover/press

        # Scale (Slider) styling
        style.configure('TScale', background='black', troughcolor='red', sliderrelief='flat')
        style.configure('Horizontal.TScale', background='black', troughcolor='red', sliderrelief='flat')

        # Checkbutton styling
        style.configure('TCheckbutton', background='black', foreground='white', relief='flat', 
                        padding=5, indicatoron=False) # Make it look more like a button
        style.map('TCheckbutton', background=[('active', 'gray20'), ('selected', 'red'), ('!selected', 'black')],
                                 foreground=[('selected', 'white'), ('!selected', 'white')])

        # OptionMenu (Dropdown) styling
        style.configure('TMenubutton', background='red', foreground='white', relief='flat')
        style.map('TMenubutton', background=[('active', 'darkred')])
        style.configure('TMenu', background='black', foreground='white', borderwidth=0, relief='flat')
        style.map('TMenu', background=[('active', 'darkred')], foreground=[('active', 'white')])


        # Variables
        self.selected_color_name = tk.StringVar(value="Red") # Default selected color
        self.target_rgb = COLORS["Red"]["rgb"]

        self.horizontal_speed = tk.IntVar(value=10) # Default speed
        self.vertical_speed = tk.IntVar(value=10)
        
        self.detection_square_size = tk.IntVar(value=300) # Default square size
        self.show_outline = tk.BooleanVar(value=True) # Default to show outline

        self.is_running = False
        self.detection_thread = None
        self.outline_window = None # To hold the Toplevel window for the outline

        # --- GUI Elements ---

        # Color Selection
        color_frame = ttk.LabelFrame(master, text="1. Select Target Color")
        color_frame.pack(pady=10, padx=10, fill="x")
        
        color_names = list(COLORS.keys())
        color_menu = ttk.OptionMenu(color_frame, self.selected_color_name, self.selected_color_name.get(), *color_names, command=self.update_target_color)
        color_menu.pack(pady=5, padx=10)
        
        self.current_hex_label = ttk.Label(color_frame, text=f"Current HEX: {COLORS['Red']['hex']}")
        self.current_hex_label.pack(pady=2)

        # Mouse Speed Sliders
        speed_frame = ttk.LabelFrame(master, text="2. Mouse Movement Speed (1=Fast, 25=Slow)")
        speed_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(speed_frame, text="Horizontal Speed:").pack(pady=2, padx=10, anchor="w")
        self.h_speed_slider = ttk.Scale(speed_frame, from_=1, to=25, orient="horizontal", variable=self.horizontal_speed, length=300)
        self.h_speed_slider.pack(pady=5, padx=10)
        self.h_speed_label = ttk.Label(speed_frame, text=f"Value: {self.horizontal_speed.get()}")
        self.h_speed_label.pack(pady=2)
        self.horizontal_speed.trace_add("write", lambda *args: self.h_speed_label.config(text=f"Value: {self.horizontal_speed.get()}"))

        ttk.Label(speed_frame, text="Vertical Speed:").pack(pady=2, padx=10, anchor="w")
        self.v_speed_slider = ttk.Scale(speed_frame, from_=1, to=25, orient="horizontal", variable=self.vertical_speed, length=300)
        self.v_speed_slider.pack(pady=5, padx=10)
        self.v_speed_label = ttk.Label(speed_frame, text=f"Value: {self.vertical_speed.get()}")
        self.v_speed_label.pack(pady=2)
        self.vertical_speed.trace_add("write", lambda *args: self.v_speed_label.config(text=f"Value: {self.vertical_speed.get()}"))

        # Detection Square Size
        square_frame = ttk.LabelFrame(master, text="3. Detection Square Size (50x50 to 1920x1080)")
        square_frame.pack(pady=10, padx=10, fill="x")

        self.size_slider = ttk.Scale(square_frame, from_=50, to=1080, orient="horizontal", variable=self.detection_square_size, length=300, command=self.update_outline_position)
        self.size_slider.pack(pady=5, padx=10)
        self.size_label = ttk.Label(square_frame, text=f"Size: {self.detection_square_size.get()}x{self.detection_square_size.get()}")
        self.size_label.pack(pady=2)
        self.detection_square_size.trace_add("write", lambda *args: self.size_label.config(text=f"Size: {self.detection_square_size.get()}x{self.detection_square_size.get()}"))

        self.outline_checkbox = ttk.Checkbutton(square_frame, text="Show White Outline", variable=self.show_outline, command=self.toggle_outline)
        self.outline_checkbox.pack(pady=5)

        # Control Buttons
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Detection", command=self.start_detection)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Status Label
        self.status_label = ttk.Label(master, text="Status: Ready", foreground="blue")
        self.status_label.pack(pady=5)

        # Initialize outline window
        self.create_outline_window()
        self.update_outline_position()
        self.toggle_outline() # Apply initial visibility based on default checkbox state

        # Setup key listener
        self._setup_key_listener()
        
        # Handle window closing protocol
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_target_color(self, *args):
        """Updates the target RGB based on the selected color name."""
        selected_name = self.selected_color_name.get()
        self.target_rgb = COLORS[selected_name]["rgb"]
        self.current_hex_label.config(text=f"Current HEX: {COLORS[selected_name]['hex']}")
        self.status_label.config(text=f"Status: Color set to {selected_name}")

    def map_speed_to_duration(self, speed_value):
        """Maps slider speed (1-25) to pyautogui duration (seconds).
        1 = fast (duration ~0.0), 25 = very slow (duration ~1.0)
        """
        # Duration will be between 0 (instant) and 1.0 (1 second).
        # Linear mapping: (speed_value - min_speed) / (max_speed - min_speed) * max_duration
        return (speed_value - 1) / (25 - 1) * 1.0 # Max duration of 1 second for 25

    def get_square_coordinates(self):
        """Calculates the top-left coordinates and size of the detection square."""
        size = self.detection_square_size.get()
        # Center the square on the screen
        x1 = (SCREEN_WIDTH - size) // 2
        y1 = (SCREEN_HEIGHT - size) // 2
        x2 = x1 + size
        y2 = y1 + size
        return x1, y1, x2, y2, size

    def create_outline_window(self):
        """Creates a transparent, always-on-top window for the outline."""
        if self.outline_window is None:
            self.outline_window = tk.Toplevel(self.master)
            self.outline_window.wm_attributes("-alpha", 0.2)  # Transparency
            self.outline_window.wm_attributes("-topmost", True) # Always on top
            self.outline_window.overrideredirect(True) # No title bar/borders
            self.outline_canvas = tk.Canvas(self.outline_window, bg='black', highlightthickness=0)
            self.outline_canvas.pack(fill="both", expand=True)
            self.outline_rect = self.outline_canvas.create_rectangle(0, 0, 0, 0, outline='white', width=3)
            self.outline_window.withdraw() # Hide initially

    def update_outline_position(self, *args):
        """Updates the position and size of the outline window."""
        if self.outline_window:
            x1, y1, x2, y2, size = self.get_square_coordinates()
            self.outline_window.geometry(f"{size}x{size}+{x1}+{y1}")
            self.outline_canvas.coords(self.outline_rect, 0, 0, size, size)
            # Ensure outline visibility matches checkbox only if detection is not running
            # When detection starts, we might want to force hide it if not checked.
            # When detection stops, always hide.
            if self.show_outline.get() and not self.is_running:
                 self.outline_window.deiconify() # Show
            elif self.show_outline.get() and self.is_running:
                 self.outline_window.deiconify() # Show outline even if running
            else:
                 self.outline_window.withdraw() # Hide


    def toggle_outline(self):
        """Shows or hides the outline window."""
        if self.outline_window:
            if self.show_outline.get():
                self.update_outline_position() # Ensure it's correctly positioned before showing
                self.outline_window.deiconify() # Show
            else:
                self.outline_window.withdraw() # Hide

    def _setup_key_listener(self):
        """Sets up the global keyboard listener for the 'Insert' key."""
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.daemon = True # Allow the program to exit even if listener is running
        self.keyboard_listener.start()

    def _on_key_press(self, key):
        """Callback for keyboard press events."""
        try:
            if key == keyboard.Key.insert:
                # Schedule the GUI update on the main Tkinter thread
                self.master.after(0, self._toggle_menu_visibility)
        except AttributeError:
            # Handle special keys that don't have a 'char' attribute
            pass

    def _toggle_menu_visibility(self):
        """Toggles the visibility of the main application window and the outline."""
        if self.master.winfo_viewable(): # Check if the window is currently visible
            self.master.withdraw() # Hide the main window
            if self.outline_window:
                self.outline_window.withdraw() # Also hide the outline window
        else:
            self.master.deiconify() # Show the main window
            if self.show_outline.get(): # Only show outline if checkbox is checked
                self.outline_window.deiconify() # Also show the outline window

    def start_detection(self):
        """Starts the color detection process in a separate thread."""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Detecting...", foreground="green")
            
            # Ensure outline is visible if checkbox is ticked when detection starts
            if self.show_outline.get():
                self.outline_window.deiconify()

            # Start the detection loop in a new thread
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()

    def stop_detection(self):
        """Stops the color detection process."""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="Status: Stopped", foreground="red")
            if self.outline_window:
                # Hide outline only if it was showing due to detection
                # If the checkbox is still ticked, it should remain visible
                if not self.show_outline.get():
                    self.outline_window.withdraw()
                self.update_outline_position() # Ensure it reflects checkbox state

    def on_closing(self):
        """Handles window closing by stopping the detection and destroying windows."""
        self.stop_detection()
        if self.keyboard_listener:
            self.keyboard_listener.stop() # Stop the keyboard listener
        if self.outline_window:
            self.outline_window.destroy()
        self.master.destroy()
        sys.exit() # Ensure all threads exit

    def detection_loop(self):
        """The main loop for color detection and mouse movement."""
        while self.is_running:
            try:
                x1, y1, x2, y2, _ = self.get_square_coordinates()
                
                # Capture the screen region defined by the square
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                
                found_color_pos = None
                for x in range(screenshot.width):
                    for y in range(screenshot.height):
                        pixel_color = screenshot.getpixel((x, y))
                        if pixel_color == self.target_rgb:
                            found_color_pos = (x1 + x, y1 + y) # Convert to absolute screen coordinates
                            break
                    if found_color_pos:
                        break

                if found_color_pos:
                    target_x = found_color_pos[0]
                    target_y = found_color_pos[1] + 115 # 115 pixels beneath it

                    h_duration = self.map_speed_to_duration(self.horizontal_speed.get())
                    v_duration = self.map_speed_to_duration(self.vertical_speed.get())
                    
                    # For simplicity, using one duration for both axes.
                    # pyautogui.moveTo handles the speed of the overall movement.
                    # If truly independent H/V speed is needed, it would require
                    # custom interpolation (not directly supported by pyautogui.moveTo's duration).
                    # Here, the larger duration will dictate the overall slower movement.
                    move_duration = max(h_duration, v_duration) 
                    
                    pyautogui.moveTo(target_x, target_y, duration=move_duration)
                    
                    self.master.after(0, lambda: self.status_label.config(
                        text=f"Status: Color found at ({found_color_pos[0]}, {found_color_pos[1]}). Mouse moved to ({target_x}, {target_y})", 
                        foreground="green"
                    ))
                else:
                    self.master.after(0, lambda: self.status_label.config(
                        text="Status: Searching for color...", 
                        foreground="blue"
                    ))

            except Exception as e:
                self.master.after(0, lambda: self.status_label.config(
                    text=f"Error: {e}", 
                    foreground="red"
                ))
            
            time.sleep(0.1) # Small delay to reduce CPU usage and allow GUI updates

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorFinderApp(root)
    root.mainloop()
