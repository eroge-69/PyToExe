import customtkinter as ctk
from customtkinter import filedialog, CTkInputDialog
from pynput import keyboard, mouse
import threading
import time
import random
import os
import json
import win32api
import win32con

# --- Global state variables ---
client_running = False
recoil_active = False
lmb_pressed = False
rmb_pressed = False

# --- Constants ---
CONFIG_DIR = "config"
MOUSE_MOVE_DELAY = 0.001

# --- Main GUI Application Class ---
class RecoilClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Recoil Client")
        self.geometry("350x450")
        self.resizable(False, False)

        # Modern dark theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Main container with subtle background
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("gray95", "gray10"))
        self.main_frame.pack(pady=15, padx=15, fill="both", expand=True)

        # Header section
        self.create_header()
        
        # Control section
        self.create_controls()
        
        # Settings section
        self.create_settings_section()
        
        # Info section
        self.create_info_section()

    def create_header(self):
        """Create the header with title and status"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", pady=(15, 25))
        header_frame.pack_propagate(False)

        # Title with modern typography
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Recoil Control", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray10", "white")
        )
        title_label.pack(pady=(10, 5))

        # Status indicator with dot
        self.status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.status_frame.pack()
        
        self.status_dot = ctk.CTkLabel(
            self.status_frame, 
            text="●", 
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        self.status_dot.pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="DISABLED", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray60")
        )
        self.status_label.pack(side="left", padx=(5, 0))

    def create_controls(self):
        """Create the main control sliders"""
        controls_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        controls_frame.pack(fill="x", pady=(0, 20), padx=10)

        # Vertical recoil
        self.create_slider_section(
            controls_frame, 
            "Vertical", 
            "vertical_strength", 
            0, 100, 0, 
            self.update_vertical_label,
            icon="↓"
        )

        # Horizontal left
        self.create_slider_section(
            controls_frame, 
            "Left Pull", 
            "horizontal_left", 
            0, 15, 0, 
            self.update_left_label,
            icon="←"
        )

        # Horizontal right
        self.create_slider_section(
            controls_frame, 
            "Right Pull", 
            "horizontal_right", 
            0, 15, 0, 
            self.update_right_label,
            icon="→"
        )

    def create_slider_section(self, parent, title, attr_name, min_val, max_val, default, callback, icon=""):
        """Create a modern slider section"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", pady=8, padx=15)

        # Header with icon and value
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 8))

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")

        icon_label = ctk.CTkLabel(
            title_frame, 
            text=icon, 
            font=ctk.CTkFont(size=14),
            width=20
        )
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(
            title_frame, 
            text=title, 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray80")
        )
        title_label.pack(side="left", padx=(5, 0))

        # Value label
        value_label = ctk.CTkLabel(
            header_frame, 
            text=str(default), 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("blue", "lightblue")
        )
        value_label.pack(side="right")

        # Slider
        slider = ctk.CTkSlider(
            section_frame, 
            from_=min_val, 
            to=max_val, 
            number_of_steps=max_val-min_val,
            height=16,
            button_color=("blue", "lightblue"),
            progress_color=("blue", "darkblue"),
            command=lambda val: callback(val, value_label)
        )
        slider.set(default)
        slider.pack(fill="x", pady=(0, 5))

        # Store references
        setattr(self, f"{attr_name}_slider", slider)
        setattr(self, f"{attr_name}_label", value_label)

    def create_settings_section(self):
        """Create save/load buttons"""
        settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 20))

        button_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        button_frame.pack()

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            width=100,
            corner_radius=8,
            command=self.save_settings
        )
        save_btn.pack(side="left", padx=(0, 10))

        # Load button
        load_btn = ctk.CTkButton(
            button_frame,
            text="📁 Load",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            width=100,
            corner_radius=8,
            command=self.load_settings
        )
        load_btn.pack(side="right", padx=(10, 0))

    def create_info_section(self):
        """Create minimalist info section"""
        info_frame = ctk.CTkFrame(self.main_frame, corner_radius=8, fg_color=("gray90", "gray15"))
        info_frame.pack(fill="x", padx=10)

        # Compact instructions
        instructions = [
            "DEL - Toggle on/off",
            "RMB + LMB - Activate recoil",
            "Uruchom jako administrator!",
            "Siła zwiększona 4x"
        ]

        for i, instruction in enumerate(instructions):
            label = ctk.CTkLabel(
                info_frame,
                text=instruction,
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray70")
            )
            label.pack(pady=(8 if i == 0 else 2, 8 if i == len(instructions)-1 else 2))

    def update_vertical_label(self, value, label):
        label.configure(text=str(int(value)))

    def update_left_label(self, value, label):
        label.configure(text=str(int(value)))

    def update_right_label(self, value, label):
        label.configure(text=str(int(value)))

    def update_status_display(self):
        """Update the status indicator"""
        if client_running:
            self.status_dot.configure(text_color="lime")
            self.status_label.configure(text="ENABLED", text_color="lime")
        else:
            self.status_dot.configure(text_color="red")
            self.status_label.configure(text="DISABLED", text_color=("gray40", "gray60"))

    def save_settings(self):
        dialog = CTkInputDialog(text="Config name:", title="Save Settings")
        filename = dialog.get_input()

        if filename:
            settings = {
                "vertical_strength": self.vertical_strength_slider.get(),
                "horizontal_left": self.horizontal_left_slider.get(),
                "horizontal_right": self.horizontal_right_slider.get()
            }
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
                
            filepath = os.path.join(CONFIG_DIR, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"Settings saved: {filename}")

    def load_settings(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            
        filepath = filedialog.askopenfilename(
            initialdir=CONFIG_DIR,
            title="Load Settings",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                v_val = settings.get("vertical_strength", 0)
                l_val = settings.get("horizontal_left", 0)
                r_val = settings.get("horizontal_right", 0)
                
                self.vertical_strength_slider.set(v_val)
                self.horizontal_left_slider.set(l_val)
                self.horizontal_right_slider.set(r_val)
                
                # Update labels
                self.vertical_strength_label.configure(text=str(int(v_val)))
                self.horizontal_left_label.configure(text=str(int(l_val)))
                self.horizontal_right_label.configure(text=str(int(r_val)))
                
                print(f"Settings loaded: {os.path.basename(filepath)}")
                
            except Exception as e:
                print(f"Error loading settings: {e}")

def check_recoil_state():
    global recoil_active
    recoil_active = client_running and lmb_pressed and rmb_pressed

def on_press(key):
    global client_running
    if key == keyboard.Key.delete:
        client_running = not client_running
        app.after(0, app.update_status_display)

def on_click(x, y, button, pressed):
    global lmb_pressed, rmb_pressed
    if button == mouse.Button.left: 
        lmb_pressed = pressed
    elif button == mouse.Button.right: 
        rmb_pressed = pressed
    check_recoil_state()

def move_mouse(dx, dy):
    """Move mouse using low-level Windows API"""
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

def recoil_thread_func():
    """Optimized recoil logic with low-level mouse control and 4x strength"""
    TICK_DELAY = 0.012
    SMOOTHING_STEPS = 5
    Y_EXPONENT = 2.0  
    X_EXPONENT = 1.8 
    MAX_Y_PIXELS_PER_TICK = 25.0 
    MAX_X_PIXELS_PER_TICK = 7.0   
    step_delay = TICK_DELAY / SMOOTHING_STEPS if SMOOTHING_STEPS > 0 else TICK_DELAY

    # Zwiększenie siły o 4x
    STRENGTH_MULTIPLIER = 4.0

    while True:
        if recoil_active:
            # Get current slider values
            y_val = app.vertical_strength_slider.get()
            x_left_val = app.horizontal_left_slider.get()
            x_right_val = app.horizontal_right_slider.get()
            
            # Calculate movements with 4x strength
            y_norm = y_val / 100.0
            total_dy = (y_norm ** Y_EXPONENT) * MAX_Y_PIXELS_PER_TICK * STRENGTH_MULTIPLIER
            
            x_left_norm = x_left_val / 15.0
            x_right_norm = x_right_val / 15.0
            effective_left = (x_left_norm ** X_EXPONENT) * MAX_X_PIXELS_PER_TICK * STRENGTH_MULTIPLIER
            effective_right = (x_right_norm ** X_EXPONENT) * MAX_X_PIXELS_PER_TICK * STRENGTH_MULTIPLIER
            total_dx = random.uniform(-effective_left, effective_right)
            
            # Apply smooth movement
            if total_dy > 0 or total_dx != 0:
                moved_dx, moved_dy = 0, 0
                for i in range(1, SMOOTHING_STEPS + 1):
                    target_dx = (total_dx * i) / SMOOTHING_STEPS
                    target_dy = (total_dy * i) / SMOOTHING_STEPS
                    move_dx = round(target_dx - moved_dx)
                    move_dy = round(target_dy - moved_dy)
                    
                    if move_dx != 0 or move_dy != 0:
                        move_mouse(move_dx, move_dy)
                        time.sleep(MOUSE_MOVE_DELAY)
                    
                    moved_dx += move_dx
                    moved_dy += move_dy
                    time.sleep(step_delay)
            else:
                time.sleep(TICK_DELAY)
        else:
            time.sleep(0.1)

# --- Main execution ---
if __name__ == "__main__":
    # Create config directory
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    # Initialize app
    app = RecoilClientApp()

    # Start listeners and threads
    keyboard_listener = keyboard.Listener(on_press=on_press, daemon=True)
    keyboard_listener.start()
    
    mouse_listener = mouse.Listener(on_click=on_click, daemon=True)
    mouse_listener.start()
    
    recoil_thread = threading.Thread(target=recoil_thread_func, daemon=True)
    recoil_thread.start()

    # Start GUI
    app.mainloop()