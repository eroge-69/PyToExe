import tkinter as tk
from tkinter import colorchooser, messagebox, Scale, HORIZONTAL, ttk
import asyncio
import threading
import time
from pywizlight import wizlight, PilotBuilder
import re
import json
import os
from collections import deque # For color smoothing

# Import libraries for screen capture and image processing
try:
    import mss
    import mss.tools
    from PIL import Image, ImageStat
except ImportError:
    messagebox.showerror("Missing Libraries",
                         "For Ambilight feature, please install 'mss' and 'Pillow' (PIL).\n"
                         "You can install them using: pip install mss Pillow")
    # Set to None if import fails, so the Ambilight feature can be disabled gracefully.
    mss = None
    Image = None
    ImageStat = None

# --- Configuration ---
# Your Wiz Light Bar's IP address (for the pair of bars)
WIZ_LIGHT_IP = "192.168.0.109"

WIZ_LIGHT_SETTINGS_FILE = "wiz_light_settings.json"

# Common Wiz Scene IDs that are dynamic or gradient-like
# Reduced to a more conservative list to avoid "Scene not available" errors
# as some specific light models might not support all scene IDs up to 35.
WIZ_DYNAMIC_SCENES = {
    "Ocean": 4,
    "Fireplace": 5,
    "Party": 6,
    "Forest": 7,
    "Romance": 8,
    "Sunset": 1,
    "Tropical Storm": 9,
    "Northern Lights": 10,
    "City": 11,
    "Relax": 12,
    "TV Time": 13,
}


# --- Wiz Light Controller Class ---
class WizLightController:
    """
    Manages communication with a single Wiz light device using pywizlight.
    (This device might internally control multiple physical light bars, but
    is addressed as one unit by the API).
    Runs asynchronous light operations in a separate thread.
    """
    FADE_INTERPOLATION_STEPS = 50 

    def __init__(self, ip_address, master_tk_root, app_instance, light_name="Light Bar"):
        self.ip_address = ip_address
        self.master_tk_root = master_tk_root
        self.app_instance = app_instance # Reference back to the main app for status updates etc.
        self.light_name = light_name # For better logging messages
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        print(f"WizLightController initialized for {self.light_name} at IP: {ip_address}")
        self.active_effect_task = None

    def _run_event_loop(self):
        """Runs the asyncio event loop in a dedicated thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coroutine_threadsafe(self, coro):
        """Schedules a coroutine to be run in the event loop thread."""
        if not self.loop.is_running():
            print(f"Warning: Attempted to run coroutine but {self.light_name}'s event loop is not running.")
            return None # Or raise an error
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future

    async def _get_light_instance(self):
        """Creates and returns a wizlight instance within the async loop's context."""
        return wizlight(self.ip_address)

    async def _turn_on(self):
        try:
            light = await self._get_light_instance()
            await light.turn_on()
            return True, f"{self.light_name} turned ON."
        except Exception as e:
            return False, f"Error turning ON {self.light_name}: {e}"

    async def _turn_off(self):
        try:
            light = await self._get_light_instance()
            await light.turn_off()
            return True, f"{self.light_name} turned OFF."
        except Exception as e:
            return False, f"Error turning OFF {self.light_name}: {e}"

    async def _set_rgb(self, r, g, b):
        try:
            light = await self._get_light_instance()
            await light.turn_on(PilotBuilder(rgb=(r, g, b)))
            return True, f"{self.light_name} color set to RGB({r}, {g}, {b})."
        except Exception as e:
            return False, f"Error setting {self.light_name} color: {e}"

    async def _set_brightness(self, brightness):
        try:
            light = await self._get_light_instance()
            await light.turn_on(PilotBuilder(brightness=brightness))
            return True, f"{self.light_name} brightness set to {brightness}."
        except Exception as e:
            return False, f"Error setting {self.light_name} brightness: {e}"
            
    async def _set_rgb_and_brightness(self, r, g, b, brightness):
        """Combined function to set both RGB and brightness."""
        try:
            light = await self._get_light_instance()
            await light.turn_on(PilotBuilder(rgb=(r, g, b), brightness=brightness))
            return True, f"{self.light_name} set to RGB({r}, {g}, {b}) Brightness {brightness}."
        except Exception as e:
            return False, f"Error setting {self.light_name} color/brightness: {e}"

    async def _manual_color_transition(self, light, start_color, end_color, num_steps, delay_per_step):
        for i in range(num_steps + 1):
            factor = i / num_steps 
            r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
            current_rgb_step = (r, g, b)
            
            try:
                await light.turn_on(PilotBuilder(rgb=current_rgb_step))
            except Exception as e:
                print(f"Error setting {self.light_name} step color {current_rgb_step}: {e}")
            
            if i < num_steps:
                await asyncio.sleep(delay_per_step)

    async def _run_multi_color_fade_effect(self, colors_list, duration_ms):
        if len(colors_list) < 2:
            self.master_tk_root.after(0, self.app_instance.update_status, False, f"{self.light_name} multi-color fade needs 2+ colors.")
            return

        try:
            light = await self._get_light_instance()
            time_per_step_seconds = (duration_ms / 1000.0) / self.FADE_INTERPOLATION_STEPS
            await light.turn_on(PilotBuilder(rgb=colors_list[0]))
            await asyncio.sleep(0.1)

            num_colors = len(colors_list)
            while True:
                for i in range(num_colors):
                    start_color = colors_list[i]
                    end_color = colors_list[(i + 1) % num_colors]
                    await self._manual_color_transition(light, start_color, end_color, self.FADE_INTERPOLATION_STEPS, time_per_step_seconds)
                    
        except asyncio.CancelledError:
            print(f"{self.light_name} multi-color fade effect cancelled.")
        except Exception as e:
            print(f"Error in {self.light_name} multi-color fade effect: {e}")
            self.master_tk_root.after(0, self.app_instance.update_status, False, f"{self.light_name} multi-color fade error: {e}")

    async def _run_pulsate_effect(self, colors_to_use, interval_ms):
        try:
            light = await self._get_light_instance()
            num_colors = len(colors_to_use)
            
            if num_colors == 0:
                colors_to_use = [(255, 255, 255)]
                num_colors = 1

            color_index = 0
            while True:
                current_pulsate_color = colors_to_use[color_index % num_colors]
                await light.turn_on(PilotBuilder(rgb=current_pulsate_color, brightness=255))
                await asyncio.sleep(interval_ms / 1000.0)
                await light.turn_off()
                await asyncio.sleep(interval_ms / 1000.0)
                color_index += 1
        except asyncio.CancelledError:
            print(f"{self.light_name} pulsate effect cancelled.")
        except Exception as e:
            print(f"Error in {self.light_name} pulsate effect: {e}")
            self.master_tk_root.after(0, self.app_instance.update_status, False, f"{self.light_name} pulsate effect error: {e}")

    async def _run_gradient_scene(self, scene_id, speed):
        try:
            light = await self._get_light_instance()
            await light.turn_on(PilotBuilder(scene=scene_id, speed=speed))
            while True:
                await asyncio.sleep(1) # Keep the coroutine alive
        except asyncio.CancelledError:
            print(f"{self.light_name} gradient scene effect cancelled.")
        except Exception as e:
            print(f"Error in {self.light_name} gradient scene effect: {e}")
            self.master_tk_root.after(0, self.app_instance.update_status, False, f"{self.light_name} gradient scene error: {e}")

    def _cancel_current_effect(self):
        if self.active_effect_task and not self.active_effect_task.done():
            self.active_effect_task.cancel()
            self.active_effect_task = None
            print(f"Current effect on {self.light_name} cancelled.")

    # Public methods to be called from the GUI thread or another management thread
    def turn_on(self, callback=None):
        self._cancel_current_effect()
        future = self.run_coroutine_threadsafe(self._turn_on())
        if future and callback: future.add_done_callback(lambda f: self.master_tk_root.after(0, callback, *f.result()))

    def turn_off(self, callback=None):
        self._cancel_current_effect()
        future = self.run_coroutine_threadsafe(self._turn_off())
        if future and callback: future.add_done_callback(lambda f: self.master_tk_root.after(0, callback, *f.result()))

    def set_rgb(self, r, g, b, callback=None):
        # Note: This does not cancel other effects, primarily for Ambilight where effect is managed externally
        future = self.run_coroutine_threadsafe(self._set_rgb(r, g, b))
        if future and callback: future.add_done_callback(lambda f: self.master_tk_root.after(0, callback, *f.result()))

    def set_brightness(self, brightness, callback=None):
        # Note: This does not cancel other effects, primarily for Ambilight where effect is managed externally
        future = self.run_coroutine_threadsafe(self._set_brightness(brightness))
        if future and callback: future.add_done_callback(lambda f: self.master_tk_root.after(0, callback, *f.result()))
        
    def set_rgb_and_brightness(self, r, g, b, brightness, callback=None):
        """Combined function to set both RGB and brightness."""
        # This is the primary method for Ambilight to reduce commands
        future = self.run_coroutine_threadsafe(self._set_rgb_and_brightness(r, g, b, brightness))
        if future and callback: future.add_done_callback(lambda f: self.master_tk_root.after(0, callback, *f.result()))

    def start_multi_color_fade_effect(self, colors_list, duration_ms, callback):
        self._cancel_current_effect()
        self.active_effect_task = self.run_coroutine_threadsafe(self._run_multi_color_fade_effect(colors_list, duration_ms))
        if self.active_effect_task and callback: self.active_effect_task.add_done_callback(lambda f: self.master_tk_root.after(0, callback, True, f"{self.light_name} Multi-color fade finished/cancelled."))
        self.master_tk_root.after(0, callback, True, f"{self.light_name} Multi-color fade started.")

    def start_pulsate_effect(self, colors_to_use, interval_ms, callback):
        self._cancel_current_effect()
        self.active_effect_task = self.run_coroutine_threadsafe(self._run_pulsate_effect(colors_to_use, interval_ms))
        if self.active_effect_task and callback: self.active_effect_task.add_done_callback(lambda f: self.master_tk_root.after(0, callback, True, f"{self.light_name} Pulsate effect finished/cancelled."))
        self.master_tk_root.after(0, callback, True, f"{self.light_name} Pulsate effect started.")

    def start_gradient_scene_effect(self, scene_id, speed, callback):
        self._cancel_current_effect()
        self.active_effect_task = self.run_coroutine_threadsafe(self._run_gradient_scene(scene_id, speed))
        if self.active_effect_task and callback: self.active_effect_task.add_done_callback(lambda f: self.master_tk_root.after(0, callback, True, f"{self.light_name} Gradient scene effect finished/cancelled."))
        self.master_tk_root.after(0, callback, True, f"{self.light_name} Gradient scene started.")

# --- GUI Application Class ---
class LightControlApp:
    """
    Tkinter GUI application for controlling the Wiz light bar.
    """
    def __init__(self, master):
        self.master = master
        master.title("Wiz Light Bar Controller")
        master.geometry("1400x1000") # Wider to accommodate new column
        master.resizable(False, False)
        
        # --- Modern Sleek Styling ---
        self.style = ttk.Style()
        
        # Define a modern dark theme color palette
        self.bg_color = "#282C34"       # Deep charcoal background
        self.frame_bg_color = "#3E4452"   # Slightly lighter for main content areas
        self.accent_color = "#61AFEF"   # Vibrant blue for interactive elements
        self.text_color = "#ABB2BF"     # Soft white for primary text
        self.status_ok_color = "#98C379"  # Green for success
        self.status_error_color = "#E06C75" # Red for error
        self.entry_bg_color = "#4B5263"   # Darker grey for entry fields
        self.border_color = "#323642"   # Very subtle dark border for separation

        master.config(bg=self.bg_color)

        # Use the 'clam' theme as a base, as it's easier to customize
        self.style.theme_use('clam') 

        # Configure global styles
        self.style.configure('.',
            font=("Inter", 10),
            background=self.bg_color,
            foreground=self.text_color,
            bordercolor=self.border_color,
            focusthickness=0 # Remove dotted focus border
        )
        self.style.map('.',
            background=[('active', self.bg_color)], # Ensure root background stays consistent
            foreground=[('active', self.text_color)]
        )

        # TFrame (for general containers)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('AppBackground.TFrame', background=self.bg_color) # Specific for root frame
        self.style.configure('Section.TFrame', background=self.frame_bg_color) # For content inside labelframes

        # TButton
        self.style.configure('TButton',
            background=self.accent_color,
            foreground="white",
            font=("Inter", 10, "bold"), # Slightly smaller font for buttons
            padding=[15, 8], # Reduced padding for buttons
            relief="flat", # Flat design
            focusthickness=0, 
            bordercolor=self.accent_color,
            borderwidth=0 # No border
        )
        self.style.map('TButton',
            background=[('active', self.accent_color), ('disabled', self.frame_bg_color)], # Darken accent on hover, gray out when disabled
            foreground=[('active', 'white'), ('disabled', self.text_color)]
        )

        # TLabelFrame - Make it truly flat with internal padding
        self.style.configure('TLabelframe',
            background=self.frame_bg_color,
            foreground=self.text_color,
            font=("Inter", 12, "bold"), # Slightly smaller font for titles
            relief="flat", # No border on the frame itself
            padding=[10, 10, 10, 15], # Reduced internal padding (L, T, R, B) from 15 to 10
            borderwidth=0
        )
        self.style.configure('TLabelframe.Label',
            background=self.frame_bg_color,
            foreground=self.text_color,
            font=("Inter", 12, "bold"),
            padding=[0, 0, 0, 8] # Reduced padding below the title
        )

        # TLabel
        self.style.configure('TLabel',
            background=self.frame_bg_color, # Match frame background for labels within frames
            foreground=self.text_color,
            font=("Inter", 9) # Slightly smaller font for labels
        )
        self.style.configure('AppBackground.TLabel', # For status bar
            background=self.bg_color,
            foreground=self.text_color
        )

        # TEntry
        self.style.configure('TEntry',
            fieldbackground=self.entry_bg_color,
            foreground=self.text_color,
            insertcolor=self.text_color,
            bordercolor=self.border_color,
            borderwidth=1, # Subtle border
            focusthickness=1,
            focuscolor=self.accent_color, # Accent color on focus
            selectbackground=self.accent_color,
            selectforeground="white",
            padding=[4, 4] # Reduced internal padding
        )

        # TScale (Horizontal) - Modernize slider look
        self.style.configure('Horizontal.TScale',
            background=self.accent_color, # Set slider thumb color directly here
            troughcolor=self.border_color, # Dark trough background
            sliderrelief="flat",
            sliderthickness=18, # Slightly smaller slider
            sliderheight=13, # Shorter and wider
            bordercolor=self.border_color, # Border around the whole scale widget
            borderwidth=0,
            focusthickness=0 
        )
        self.style.map('Horizontal.TScale',
            background=[('active', self.accent_color)], 
            troughcolor=[('active', self.accent_color)], # Trough lights up on active
        )


        # TCheckbutton
        self.style.configure('TCheckbutton',
            background=self.frame_bg_color,
            foreground=self.text_color,
            font=("Inter", 9), # Smaller font
            focusthickness=0,
            indicatorbackground=self.entry_bg_color, # Box color
            indicatorforeground=self.accent_color, # Checkmark color
            padding=[0, 3] # Reduced padding
        )
        self.style.map('TCheckbutton',
            background=[('active', self.frame_bg_color)], 
            foreground=[('active', self.text_color)],
            indicatorbackground=[('selected', self.accent_color)], # Checkbox fill when selected
            indicatorrelief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )

        # TCombobox
        self.style.configure('TCombobox',
            fieldbackground=self.entry_bg_color,
            background=self.accent_color, # Button part of combobox
            foreground=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white",
            arrowcolor="white",
            bordercolor=self.border_color,
            focusthickness=1,
            padding=[4, 4] # Reduced padding
        )
        self.style.map('TCombobox',
            fieldbackground=[('readonly', self.entry_bg_color)],
            selectbackground=[('readonly', self.accent_color)],
            selectforeground=[('readonly', 'white')],
            background=[('readonly', self.accent_color)],
            foreground=[('readonly', 'white')],
        )
        master.option_add('*TCombobox*Listbox*Background', self.entry_bg_color)
        master.option_add('*TCombobox*Listbox*Foreground', self.text_color)
        master.option_add('*TCombobox*Listbox*selectBackground', self.accent_color)
        master.option_add('*TCombobox*Listbox*selectForeground', "white")
        master.option_add('*TCombobox*Listbox*Font', ("Inter", 9)) # Smaller font


        self.light_controller = None
        self._brightness_update_job = None
        self.current_rgb = (255, 255, 255)
        self.custom_fade_colors = []
        self.is_light_on = True # Tracks GUI state, not necessarily actual light state

        # Ambilight specific variables
        self.ambilight_running = False
        self.ambilight_thread = None
        self.ambilight_stop_event = threading.Event()
        self.prev_avg_rgb = None # For color smoothing
        self.prev_avg_brightness = None # For brightness smoothing (less critical but good practice)

        # --- Main Layout Frames ---
        self.content_frame = ttk.Frame(master, style='AppBackground.TFrame')
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20) # Reduced overall padding

        self.content_frame.grid_columnconfigure(0, weight=1, uniform="group1") # Left Control
        self.content_frame.grid_columnconfigure(1, weight=1, uniform="group1") # Middle Effects
        self.content_frame.grid_columnconfigure(2, weight=1, uniform="group1") # NEW Right Ambilight
        self.content_frame.grid_rowconfigure(0, weight=1) 
        self.content_frame.grid_rowconfigure(1, weight=0)

        # Left Control Column
        self.control_column_frame = ttk.Frame(self.content_frame, style='AppBackground.TFrame')
        self.control_column_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0) # Reduced padx
        self.control_column_frame.grid_columnconfigure(0, weight=1)
        self.control_column_frame.grid_rowconfigure(0, weight=0) # Device Connection
        self.control_column_frame.grid_rowconfigure(1, weight=0) # Power Control
        self.control_column_frame.grid_rowconfigure(2, weight=0) # Color & Brightness
        # Removed grid_rowconfigure(3, weight=1) for Ambilight, as it's moving

        # Middle Effects Column
        self.effects_column_frame = ttk.Frame(self.content_frame, style='AppBackground.TFrame')
        self.effects_column_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=0) # Reduced padx
        self.effects_column_frame.grid_columnconfigure(0, weight=1)
        # Shifted row configurations since Ambilight control buttons moved
        self.effects_column_frame.grid_rowconfigure(0, weight=0) # Stop button (now at row 0)
        self.effects_column_frame.grid_rowconfigure(1, weight=0) # Multi-color fade (shifted)
        self.effects_column_frame.grid_rowconfigure(2, weight=0) # Pulsate (shifted)
        self.effects_column_frame.grid_rowconfigure(3, weight=1) # Gradient Scene (expands, shifted)

        # NEW Ambilight Column (Rightmost)
        self.ambilight_column_frame = ttk.Frame(self.content_frame, style='AppBackground.TFrame')
        self.ambilight_column_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=0)
        self.ambilight_column_frame.grid_columnconfigure(0, weight=1)
        self.ambilight_column_frame.grid_rowconfigure(0, weight=0) # Ambilight Control (buttons)
        self.ambilight_column_frame.grid_rowconfigure(1, weight=1) # Ambilight Settings (allow to expand)


        # --- Widgets in Left Control Column ---
        current_row = 0

        # Device Connection Section
        ip_frame = ttk.LabelFrame(self.control_column_frame, text="Device Connection", style='TLabelframe')
        ip_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15)) # Reduced pady
        ip_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(ip_frame, text="Device IP Address:", style='TLabel').grid(row=0, column=0, pady=(0,3), padx=0, sticky="w") # Adjust pady for label
        self.ip_var = tk.StringVar(value=WIZ_LIGHT_IP)
        self.ip_entry = ttk.Entry(ip_frame, textvariable=self.ip_var, width=25, style='TEntry')
        self.ip_entry.grid(row=1, column=0, pady=3, padx=0, sticky="ew")

        self.set_ip_button = ttk.Button(ip_frame, text="Set Device IP", command=self.set_device_ip, style='TButton')
        self.set_ip_button.grid(row=2, column=0, pady=(10,0), padx=0, sticky="ew")
        current_row += 1

        # Power Control Section
        power_frame = ttk.LabelFrame(self.control_column_frame, text="Power Control", style='TLabelframe')
        power_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15)) # Reduced pady
        power_frame.grid_columnconfigure(0, weight=1)
        self.on_button = ttk.Button(power_frame, text="Turn ON", command=self.turn_on_light, style='TButton')
        self.on_button.grid(row=0, column=0, pady=(0,8), padx=0, sticky="ew") # Reduced pady
        self.off_button = ttk.Button(power_frame, text="Turn OFF", command=self.turn_off_light, style='TButton')
        self.off_button.grid(row=1, column=0, pady=0, padx=0, sticky="ew")
        current_row += 1

        # Color & Brightness Section
        self.color_brightness_frame = ttk.LabelFrame(self.control_column_frame, text="Color & Brightness", style='TLabelframe')
        self.color_brightness_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15)) # Reduced pady
        self.color_brightness_frame.grid_columnconfigure(0, weight=1)
        
        self.color_button = ttk.Button(self.color_brightness_frame, text="Select Main Color", command=self.select_main_color, style='TButton')
        self.color_button.grid(row=0, column=0, pady=(0,8), padx=0, sticky="ew") # Reduced pady
        
        self.color_preview = tk.Canvas(self.color_brightness_frame, width=50, height=25, bg="white", highlightthickness=1, highlightbackground=self.border_color, relief="solid")
        self.color_preview.grid(row=1, column=0, pady=3, padx=0, sticky="n") # Reduced pady
        
        self.master.after_idle(lambda: self.color_preview.grid_configure(
            sticky="nsew",
            ipadx=max(0, (self.color_brightness_frame.winfo_width() - 50) // 2)
        )) 
        self.master.bind("<Configure>", lambda e: self.color_preview.grid_configure(
            sticky="nsew",
            ipadx=max(0, (self.color_brightness_frame.winfo_width() - 50) // 2)
        ) if e.widget == self.master else None)

        ttk.Label(self.color_brightness_frame, text="Brightness:", style='TLabel').grid(row=2, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.brightness_slider = ttk.Scale(self.color_brightness_frame, from_=0, to=255, orient=HORIZONTAL,
                                        command=self.debounce_brightness_update, style='Horizontal.TScale')
        self.brightness_slider.set(255) 
        self.brightness_slider.grid(row=3, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        
        self.brightness_value_label = ttk.Label(self.color_brightness_frame, text="255", style='TLabel')
        self.brightness_value_label.grid(row=4, column=0, pady=(0,0), padx=0, sticky="e")
        self.brightness_slider.bind("<Motion>", self._update_brightness_label) # Update on drag
        self.brightness_slider.bind("<ButtonRelease-1>", self._update_brightness_label) # Update on release
        self.brightness_slider.bind("<Leave>", self._update_brightness_label) # Update when mouse leaves

        # The control_column_frame now simply ends here, no expand for this column specifically, the main content frame handles overall expansion

        # --- Widgets in Middle Effects Column ---

        # Stop Current Effect Button (now at row 0)
        self.stop_effect_button = ttk.Button(self.effects_column_frame, text="Stop Current Effect", command=self.stop_current_effect, style='TButton')
        self.stop_effect_button.grid(row=0, column=0, pady=(0,15), padx=0, sticky="ew") 

        # Multi-Color Fade Section (shifted down to row 1)
        self.multi_fade_frame = ttk.LabelFrame(self.effects_column_frame, text="Multi-Color Fade", style='TLabelframe')
        self.multi_fade_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15)) # Shifted row, reduced pady
        self.multi_fade_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.multi_fade_frame, text="Duration (ms) per segment:", style='TLabel').grid(row=0, column=0, pady=(0, 3), padx=0, sticky="w") # Reduced pady
        self.fade_duration_var = tk.StringVar(value="1000")
        self.fade_duration_entry = ttk.Entry(self.multi_fade_frame, textvariable=self.fade_duration_var, width=10, style='TEntry')
        self.fade_duration_entry.grid(row=1, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.fade_duration_entry.bind("<FocusOut>", lambda e: self.save_settings()) # FIX: Added lambda e:

        self.custom_color_frames = ttk.Frame(self.multi_fade_frame, style='Section.TFrame') # Use Section.TFrame
        self.custom_color_frames.grid(row=2, column=0, pady=(8,0), padx=0, sticky="ew") # Reduced pady
        self.custom_color_frames.grid_columnconfigure(0, weight=1) # Allow color frames to expand

        self.add_color_frame = ttk.Frame(self.multi_fade_frame, style='Section.TFrame')
        self.add_color_frame.grid(row=3, column=0, pady=(10,3), padx=0, sticky="ew") # Reduced pady
        self.add_color_frame.grid_columnconfigure(0, weight=1)

        self.add_custom_color_button = ttk.Button(self.add_color_frame, text="Add Custom Color", command=self.add_custom_fade_color, style='TButton')
        self.add_custom_color_button.grid(row=0, column=0, sticky="ew")

        self.clear_custom_colors_button = ttk.Button(self.multi_fade_frame, text="Clear Custom Colors", command=self.clear_custom_fade_colors, style='TButton')
        self.clear_custom_colors_button.grid(row=4, column=0, pady=(8,8), padx=0, sticky="ew") # Reduced pady

        self.start_multi_fade_button = ttk.Button(self.multi_fade_frame, text="Start Multi-Color Fade", command=self.start_multi_color_fade_gui, style='TButton')
        self.start_multi_fade_button.grid(row=5, column=0, pady=(0,0), padx=0, sticky="ew")

        # Pulsate Effect Section (shifted down to row 2)
        self.pulsate_frame = ttk.LabelFrame(self.effects_column_frame, text="Pulsate Effect", style='TLabelframe')
        self.pulsate_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15)) # Shifted row, reduced pady
        self.pulsate_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.pulsate_frame, text="Interval (ms):", style='TLabel').grid(row=0, column=0, pady=(0, 3), padx=0, sticky="w") # Reduced pady
        self.pulsate_interval_var = tk.StringVar(value="500")
        self.pulsate_interval_entry = ttk.Entry(self.pulsate_frame, textvariable=self.pulsate_interval_var, width=10, style='TEntry')
        self.pulsate_interval_entry.grid(row=1, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.pulsate_interval_entry.bind("<FocusOut>", lambda e: self.save_settings()) # FIX: Added lambda e:

        self.pulsate_use_custom_colors_var = tk.BooleanVar(value=False)
        self.pulsate_colors_checkbox = ttk.Checkbutton(self.pulsate_frame, text="Pulsate with Custom Fade Colors", variable=self.pulsate_use_custom_colors_var, style='TCheckbutton')
        self.pulsate_colors_checkbox.grid(row=2, column=0, pady=(8,8), padx=0, sticky="w") # Reduced pady
        self.pulsate_colors_checkbox.bind("<ButtonRelease-1>", lambda e: self.save_settings())

        self.start_pulsate_button = ttk.Button(self.pulsate_frame, text="Start Pulsate Effect", command=self.start_pulsate_effect_gui, style='TButton')
        self.start_pulsate_button.grid(row=3, column=0, pady=(0,0), padx=0, sticky="ew")

        # Gradient Scene Effect Section (shifted down to row 3, and now expands)
        self.gradient_scene_frame = ttk.LabelFrame(self.effects_column_frame, text="Gradient Scene Effect", style='TLabelframe')
        self.gradient_scene_frame.grid(row=3, column=0, sticky="nsew", pady=(0,0)) # Shifted row, make it expand vertically
        self.gradient_scene_frame.grid_columnconfigure(0, weight=1)
        self.gradient_scene_frame.grid_rowconfigure(5, weight=1) # Allow extra space at the bottom

        ttk.Label(self.gradient_scene_frame, text="Select Scene:", style='TLabel').grid(row=0, column=0, pady=(0, 3), padx=0, sticky="w") # Reduced pady
        self.scene_names = list(WIZ_DYNAMIC_SCENES.keys())
        self.selected_scene_var = tk.StringVar(value=self.scene_names[0] if self.scene_names else "")
        self.scene_dropdown = ttk.Combobox(self.gradient_scene_frame, textvariable=self.selected_scene_var, values=self.scene_names, state="readonly", style='TCombobox')
        self.scene_dropdown.grid(row=1, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.scene_dropdown.set(self.scene_names[0] if self.scene_names else "")
        self.scene_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_settings()) # FIX: Added lambda e:

        ttk.Label(self.gradient_scene_frame, text="Scene Speed (20-200):", style='TLabel').grid(row=2, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.scene_speed_var = tk.StringVar(value="100")
        self.scene_speed_entry = ttk.Entry(self.gradient_scene_frame, textvariable=self.scene_speed_var, width=10, style='TEntry')
        self.scene_speed_entry.grid(row=3, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.scene_speed_entry.bind("<FocusOut>", lambda e: self.save_settings()) # FIX: Added lambda e:

        self.start_gradient_button = ttk.Button(self.gradient_scene_frame, text="Start Gradient Scene", command=self.start_gradient_scene_gui, style='TButton')
        self.start_gradient_button.grid(row=4, column=0, pady=(10,0), padx=0, sticky="ew")


        # --- Widgets in NEW Right Ambilight Column ---

        # Ambilight Control Section (buttons only, MOVED to new Ambilight column)
        self.ambilight_control_frame = ttk.LabelFrame(self.ambilight_column_frame, text="Ambilight Control", style='TLabelframe')
        self.ambilight_control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15)) 
        self.ambilight_control_frame.grid_columnconfigure(0, weight=1)

        self.start_ambilight_button = ttk.Button(self.ambilight_control_frame, text="Start Ambilight", command=self.start_ambilight_gui, style='TButton')
        self.start_ambilight_button.grid(row=0, column=0, pady=(0,8), padx=0, sticky="ew")
        self.stop_ambilight_button = ttk.Button(self.ambilight_control_frame, text="Stop Ambilight", command=self.stop_ambilight_gui, style='TButton')
        self.stop_ambilight_button.grid(row=1, column=0, pady=0, padx=0, sticky="ew")
        self.stop_ambilight_button.config(state=tk.DISABLED) # Start disabled

        # Ambilight Settings Section (MOVED to new Ambilight column, now expands)
        self.ambilight_frame = ttk.LabelFrame(self.ambilight_column_frame, text="Ambilight Effect (Uniform Color)", style='TLabelframe')
        self.ambilight_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0)) 
        self.ambilight_frame.grid_columnconfigure(0, weight=1)

        # Monitor Selection
        ttk.Label(self.ambilight_frame, text="Select Monitor:", style='TLabel').grid(row=0, column=0, pady=(0, 3), padx=0, sticky="w") # Reduced pady
        self.monitor_names = []
        self.selected_monitor_var = tk.StringVar()
        self.monitor_dropdown = ttk.Combobox(self.ambilight_frame, textvariable=self.selected_monitor_var, values=self.monitor_names, state="readonly", style='TCombobox')
        self.monitor_dropdown.grid(row=1, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.monitor_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_settings()) # FIX: Added lambda e:
        self.populate_monitors_dropdown() # Populate on startup
        
        # Ambilight Interval
        ttk.Label(self.ambilight_frame, text="Update Interval (ms):", style='TLabel').grid(row=2, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.ambilight_interval_var = tk.StringVar(value="100") # Default to 100ms
        self.ambilight_interval_entry = ttk.Entry(self.ambilight_frame, textvariable=self.ambilight_interval_var, width=10, style='TEntry')
        self.ambilight_interval_entry.grid(row=3, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.ambilight_interval_entry.bind("<FocusOut>", lambda e: self.save_settings()) # FIX: Added lambda e:

        # Brightness Threshold
        ttk.Label(self.ambilight_frame, text="Min Screen Brightness Threshold (%):", style='TLabel').grid(row=4, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.min_screen_brightness_threshold = ttk.Scale(self.ambilight_frame, from_=0, to=100, orient=HORIZONTAL, style='Horizontal.TScale')
        self.min_screen_brightness_threshold.set(5) # Default to 5%
        self.min_screen_bright_label = ttk.Label(self.ambilight_frame, text=f"{int(self.min_screen_brightness_threshold.get())}%", style='TLabel')
        self.min_screen_brightness_threshold.config(command=lambda v: self.min_screen_bright_label.config(text=f"{int(float(v))}%"))
        self.min_screen_brightness_threshold.grid(row=5, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.min_screen_bright_label.grid(row=6, column=0, pady=(0,0), padx=0, sticky="e")
        self.min_screen_brightness_threshold.bind("<ButtonRelease-1>", lambda e: self.save_settings())

        # Minimum Light Brightness
        ttk.Label(self.ambilight_frame, text="Minimum Light Brightness (0-255):", style='TLabel').grid(row=7, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.min_light_brightness = ttk.Scale(self.ambilight_frame, from_=0, to=255, orient=HORIZONTAL, style='Horizontal.TScale')
        self.min_light_brightness.set(20) # Default to 20
        self.min_light_bright_label = ttk.Label(self.ambilight_frame, text=str(int(self.min_light_brightness.get())), style='TLabel')
        self.min_light_brightness.config(command=lambda v: self.min_light_bright_label.config(text=str(int(float(v)))))
        self.min_light_brightness.grid(row=8, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.min_light_bright_label.grid(row=9, column=0, pady=(0,0), padx=0, sticky="e")
        self.min_light_brightness.bind("<ButtonRelease-1>", lambda e: self.save_settings())

        # Maximum Light Brightness
        ttk.Label(self.ambilight_frame, text="Maximum Light Brightness (0-255):", style='TLabel').grid(row=10, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.max_light_brightness = ttk.Scale(self.ambilight_frame, from_=0, to=255, orient=HORIZONTAL, style='Horizontal.TScale')
        self.max_light_brightness.set(255) # Default to 255
        self.max_light_bright_label = ttk.Label(self.ambilight_frame, text=str(int(self.max_light_brightness.get())), style='TLabel')
        self.max_light_brightness.config(command=lambda v: self.max_light_bright_label.config(text=str(int(float(v)))))
        self.max_light_brightness.grid(row=11, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.max_light_bright_label.grid(row=12, column=0, pady=(0,0), padx=0, sticky="e")
        self.max_light_brightness.bind("<ButtonRelease-1>", lambda e: self.save_settings())

        # Color Smoothing Factor
        ttk.Label(self.ambilight_frame, text="Color Smoothing Factor (0-10):", style='TLabel').grid(row=13, column=0, pady=(10, 3), padx=0, sticky="w") # Reduced pady
        self.smoothing_factor_slider = ttk.Scale(self.ambilight_frame, from_=0, to=10, orient=HORIZONTAL, style='Horizontal.TScale')
        self.smoothing_factor_slider.set(5) # Default smoothing
        self.smoothing_factor_label = ttk.Label(self.ambilight_frame, text=str(int(self.smoothing_factor_slider.get())), style='TLabel')
        self.smoothing_factor_slider.config(command=lambda v: self.smoothing_factor_label.config(text=str(int(float(v)))))
        self.smoothing_factor_slider.grid(row=14, column=0, pady=3, padx=0, sticky="ew") # Reduced pady
        self.smoothing_factor_label.grid(row=15, column=0, pady=(0,10), padx=0, sticky="e") # Reduced pady
        self.smoothing_factor_slider.bind("<ButtonRelease-1>", lambda e: self.save_settings())


        # Status Label (placed at the bottom of the content_frame)
        self.status_label = ttk.Label(self.content_frame, text="Ready", style='AppBackground.TLabel', anchor="center")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(15, 0), sticky="ew") # Column span adjusted to 3

        # Load settings on startup, then initialize controller
        self.load_settings()
        self.set_device_ip(initial_load=True) # Initialize controller based on loaded IP
        # Set protocol for window closing to save settings
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_status(self, is_success, message):
        """Updates the status bar message and color."""
        if is_success:
            self.status_label.config(foreground=self.status_ok_color, text=message)
        else:
            self.status_label.config(foreground=self.status_error_color, text=f"Error: {message}")
        self.master.after(5000, lambda: self.status_label.config(foreground=self.text_color, text="Ready"))

    def set_device_ip(self, initial_load=False):
        ip = self.ip_var.get()
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            self.update_status(False, "Invalid IP Address format.")
            return

        if self.light_controller:
            # If already initialized, just update IP
            self.light_controller.ip_address = ip
            self.update_status(True, f"Device IP updated to {ip}.")
        else:
            # First time initialization
            self.light_controller = WizLightController(ip, self.master, self)
            self.update_status(True, f"Connected to light at {ip}.")
        
        if not initial_load: # Only save settings if it's a manual change, not initial load
            self.save_settings()

    def turn_on_light(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        self.stop_ambilight_gui() # Ensure Ambilight is off
        self.is_light_on = True
        self.light_controller.turn_on(callback=self.update_status)

    def turn_off_light(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        self.stop_ambilight_gui() # Ensure Ambilight is off
        self.is_light_on = False
        self.light_controller.turn_off(callback=self.update_status)

    def select_main_color(self):
        color_code = colorchooser.askcolor(title="Choose Light Color", initialcolor=self.rgb_to_hex(self.current_rgb))
        if color_code[0] is not None:
            r, g, b = [int(c) for c in color_code[0]]
            self.current_rgb = (r, g, b)
            hex_color = self.rgb_to_hex(self.current_rgb)
            self.color_preview.config(bg=hex_color)
            if self.is_light_on: # Only set if light is on
                # Use combined set_rgb_and_brightness for efficiency
                current_brightness = int(self.brightness_slider.get())
                self.light_controller.set_rgb_and_brightness(r, g, b, current_brightness, callback=self.update_status)
            self.save_settings()

    def _update_brightness_label(self, event=None):
        value = int(self.brightness_slider.get())
        self.brightness_value_label.config(text=str(value))

    def debounce_brightness_update(self, value):
        # Cancel previous scheduled update if it exists
        if self._brightness_update_job:
            self.master.after_cancel(self._brightness_update_job)
        # Schedule a new update after a short delay (e.g., 200ms)
        self._brightness_update_job = self.master.after(200, self._apply_brightness_change, int(float(value)))

    def _apply_brightness_change(self, brightness):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        if self.is_light_on: # Only set if light is on
            # Use combined set_rgb_and_brightness for efficiency
            r, g, b = self.current_rgb
            self.light_controller.set_rgb_and_brightness(r, g, b, brightness, callback=self.update_status)
        self.save_settings()
        self._brightness_update_job = None # Reset the job ID


    def stop_current_effect(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        self.light_controller._cancel_current_effect()
        self.update_status(True, "Current effect stopped.")
        # Reapply current GUI color/brightness state
        if self.is_light_on:
            r, g, b = self.current_rgb
            brightness = int(self.brightness_slider.get())
            self.light_controller.set_rgb_and_brightness(r,g,b,brightness, callback=self.update_status)
        else:
            self.light_controller.turn_off(callback=self.update_status)

    def add_custom_fade_color(self):
        color_code = colorchooser.askcolor(title="Add Custom Fade Color", initialcolor=self.rgb_to_hex(self.current_rgb))
        if color_code[0] is not None:
            r, g, b = [int(c) for c in color_code[0]]
            self.custom_fade_colors.append((r, g, b))
            self.update_custom_color_display()
            self.save_settings()

    def remove_custom_fade_color(self, index): # FIX: Added this method
        if 0 <= index < len(self.custom_fade_colors):
            del self.custom_fade_colors[index]
            self.update_custom_color_display()
            self.save_settings()

    def update_custom_color_display(self):
        # Clear existing color display frames
        for widget in self.custom_color_frames.winfo_children():
            widget.destroy()

        if not self.custom_fade_colors:
            ttk.Label(self.custom_color_frames, text="No custom colors added.", style='TLabel').pack(pady=5)
            return

        for i, color in enumerate(self.custom_fade_colors):
            color_frame = ttk.Frame(self.custom_color_frames, style='Section.TFrame') # Use Section.TFrame
            color_frame.pack(fill="x", pady=2, padx=5) # Reduced padx
            color_frame.grid_columnconfigure(0, weight=1)
            color_frame.grid_columnconfigure(1, weight=0) # For the remove button

            hex_color = self.rgb_to_hex(color)
            color_preview = tk.Canvas(color_frame, width=20, height=20, bg=hex_color, highlightthickness=1, highlightbackground=self.border_color, relief="solid")
            color_preview.grid(row=0, column=0, sticky="w", padx=(0,5))

            color_label = ttk.Label(color_frame, text=f"RGB: {color}", style='TLabel')
            color_label.grid(row=0, column=0, padx=(30, 0), sticky="w") # Offset label to the right of canvas

            remove_button = ttk.Button(color_frame, text="X", command=lambda idx=i: self.remove_custom_fade_color(idx), style='TButton')
            remove_button.grid(row=0, column=1, sticky="e")

    def clear_custom_fade_colors(self):
        self.custom_fade_colors = []
        self.update_custom_color_display()
        self.save_settings()

    def start_multi_color_fade_gui(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        if not self.custom_fade_colors or len(self.custom_fade_colors) < 2:
            self.update_status(False, "Please add at least 2 custom colors for multi-color fade.")
            return
        try:
            duration_ms = int(self.fade_duration_var.get())
            if duration_ms <= 0:
                raise ValueError("Duration must be a positive number.")
        except ValueError as e:
            self.update_status(False, f"Invalid duration: {e}")
            return
        
        self.stop_ambilight_gui()
        self.light_controller.start_multi_color_fade_effect(self.custom_fade_colors, duration_ms, self.update_status)
        self.is_light_on = True # Assume light will be on

    def start_pulsate_effect_gui(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        try:
            interval_ms = int(self.pulsate_interval_var.get())
            if interval_ms <= 0:
                raise ValueError("Interval must be a positive number.")
        except ValueError as e:
            self.update_status(False, f"Invalid interval: {e}")
            return
        
        colors_to_use = self.custom_fade_colors if self.pulsate_use_custom_colors_var.get() and self.custom_fade_colors else [(255, 255, 255)]
        
        self.stop_ambilight_gui()
        self.light_controller.start_pulsate_effect(colors_to_use, interval_ms, self.update_status)
        self.is_light_on = True # Assume light will be on

    def start_gradient_scene_gui(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        selected_scene_name = self.selected_scene_var.get()
        scene_id = WIZ_DYNAMIC_SCENES.get(selected_scene_name)
        if scene_id is None:
            self.update_status(False, "Invalid scene selected.")
            return
        try:
            speed = int(self.scene_speed_var.get())
            if not (20 <= speed <= 200):
                raise ValueError("Speed must be between 20 and 200.")
        except ValueError as e:
            self.update_status(False, f"Invalid speed: {e}")
            return

        self.stop_ambilight_gui()
        self.light_controller.start_gradient_scene_effect(scene_id, speed, self.update_status)
        self.is_light_on = True # Assume light will be on

    # Ambilight Features
    def populate_monitors_dropdown(self):
        if mss:
            with mss.mss() as sct:
                self.monitor_names = [f"Monitor {i+1} ({mon['width']}x{mon['height']})" for i, mon in enumerate(sct.monitors[1:])]
                if self.monitor_names:
                    self.monitor_dropdown['values'] = self.monitor_names
                    if not self.selected_monitor_var.get() or self.selected_monitor_var.get() not in self.monitor_names:
                        self.selected_monitor_var.set(self.monitor_names[0])
                else:
                    self.monitor_dropdown['values'] = ["No monitors found"]
                    self.selected_monitor_var.set("No monitors found")
                    self.start_ambilight_button.config(state=tk.DISABLED)
                    self.update_status(False, "No additional monitors detected for Ambilight.")
        else:
            self.monitor_dropdown['values'] = ["MSS/Pillow not installed"]
            self.selected_monitor_var.set("MSS/Pillow not installed")
            self.start_ambilight_button.config(state=tk.DISABLED)
            self.update_status(False, "Ambilight feature disabled: 'mss' or 'Pillow' not installed.")
    
    def start_ambilight_gui(self):
        if not self.light_controller:
            self.update_status(False, "Light controller not initialized. Set IP first.")
            return
        if not mss:
            self.update_status(False, "Ambilight feature not available. 'mss' or 'Pillow' not installed.")
            return

        if self.ambilight_running:
            self.update_status(False, "Ambilight is already running.")
            return

        selected_monitor_text = self.selected_monitor_var.get()
        if "No monitors found" in selected_monitor_text or "MSS/Pillow not installed" in selected_monitor_text:
            self.update_status(False, "Cannot start Ambilight: No valid monitor selected or libraries missing.")
            return

        try:
            interval_ms = int(self.ambilight_interval_var.get())
            if interval_ms <= 0:
                raise ValueError("Update Interval must be a positive number.")
            min_screen_brightness_threshold_percent = float(self.min_screen_brightness_threshold.get())
            min_light_brightness_val = int(self.min_light_brightness.get())
            max_light_brightness_val = int(self.max_light_brightness.get())
            smoothing_factor = int(self.smoothing_factor_slider.get())

            if not (0 <= min_screen_brightness_threshold_percent <= 100):
                raise ValueError("Min Screen Brightness Threshold must be between 0 and 100.")
            if not (0 <= min_light_brightness_val <= 255):
                raise ValueError("Minimum Light Brightness must be between 0 and 255.")
            if not (0 <= max_light_brightness_val <= 255):
                raise ValueError("Maximum Light Brightness must be between 0 and 255.")
            if min_light_brightness_val > max_light_brightness_val:
                raise ValueError("Minimum Light Brightness cannot be greater than Maximum Light Brightness.")
            if not (0 <= smoothing_factor <= 10):
                raise ValueError("Color Smoothing Factor must be between 0 and 10.")

        except ValueError as e:
            self.update_status(False, f"Ambilight configuration error: {e}")
            return
        
        # Determine the monitor index
        monitor_index = -1
        if "Monitor " in selected_monitor_text:
            try:
                # Extract the number, then convert to 0-based index for sct.monitors[1:]
                monitor_number = int(selected_monitor_text.split(' ')[1])
                monitor_index = monitor_number - 1 # Adjust to 0-based for list indexing
            except (ValueError, IndexError):
                pass # Fallback to default if parsing fails
        
        if monitor_index == -1:
             self.update_status(False, "Could not determine selected monitor. Please re-select.")
             return

        self.ambilight_stop_event.clear()
        self.ambilight_running = True
        self.stop_ambilight_button.config(state=tk.NORMAL)
        self.start_ambilight_button.config(state=tk.DISABLED)
        self.light_controller._cancel_current_effect() # Ensure other effects are stopped
        self.is_light_on = True # Ambilight will turn light on

        # Pass parameters to the ambilight thread
        self.ambilight_thread = threading.Thread(target=self._run_ambilight_effect, args=(
            interval_ms, monitor_index, min_screen_brightness_threshold_percent, 
            min_light_brightness_val, max_light_brightness_val, smoothing_factor
        ))
        self.ambilight_thread.daemon = True
        self.ambilight_thread.start()
        self.update_status(True, "Ambilight started.")

    def stop_ambilight_gui(self):
        if self.ambilight_running:
            self.ambilight_stop_event.set()
            if self.ambilight_thread and self.ambilight_thread.is_alive():
                self.ambilight_thread.join(timeout=1) # Wait for the thread to finish
            self.ambilight_running = False
            self.stop_ambilight_button.config(state=tk.DISABLED)
            self.start_ambilight_button.config(state=tk.NORMAL)
            self.update_status(True, "Ambilight stopped.")
            # Restore previous non-ambilight state
            if self.is_light_on:
                r, g, b = self.current_rgb
                brightness = int(self.brightness_slider.get())
                self.light_controller.set_rgb_and_brightness(r,g,b,brightness, callback=self.update_status)
            else:
                self.light_controller.turn_off(callback=self.update_status)

    def _run_ambilight_effect(self, interval_ms, monitor_idx, min_screen_brightness_threshold_percent, min_light_brightness_val, max_light_brightness_val, smoothing_factor):
        sct = None
        try:
            sct = mss.mss()
            target_monitor = sct.monitors[monitor_idx + 1] # +1 because sct.monitors[0] is all monitors
            
            # Initialize moving average for smoothing
            # Use deque to store last 'smoothing_factor' colors
            color_history = deque(maxlen=max(1, smoothing_factor)) # Ensure at least 1 for no smoothing
            
            self.prev_avg_rgb = None # Reset smoothing history on start

            while not self.ambilight_stop_event.is_set():
                # Capture the screen
                sct_img = sct.grab(target_monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

                # Calculate the average color of the screen
                stat = ImageStat.Stat(img)
                avg_rgb = [int(c) for c in stat.mean[:3]] # [R, G, B]

                # Calculate perceived brightness (luminance)
                # Using Rec. 709 luminance formula
                luminance = (0.2126 * avg_rgb[0] + 0.7152 * avg_rgb[1] + 0.0722 * avg_rgb[2]) / 255.0

                # Apply smoothing
                if smoothing_factor > 0:
                    color_history.append(avg_rgb)
                    # Calculate average from history
                    smoothed_r = sum(c[0] for c in color_history) // len(color_history)
                    smoothed_g = sum(c[1] for c in color_history) // len(color_history)
                    smoothed_b = sum(c[2] for c in color_history) // len(color_history)
                    avg_rgb = (smoothed_r, smoothed_g, smoothed_b)

                # Adjust brightness based on screen luminance and thresholds
                screen_brightness_percent = luminance * 100
                target_brightness = int(self.brightness_slider.get()) # Use the GUI slider as base
                
                if screen_brightness_percent < min_screen_brightness_threshold_percent:
                    # If screen is very dark, turn light off or set to min_light_brightness_val
                    current_light_brightness = min_light_brightness_val 
                    if min_light_brightness_val == 0:
                        # Schedule turn off if min brightness is 0
                        self.master.after(0, self.light_controller.turn_off)
                        time.sleep(interval_ms / 1000.0)
                        continue # Skip setting color if light is off
                else:
                    # Map screen brightness to light brightness within min/max range
                    # Scale (screen_brightness_percent - min_threshold) from (0 to 100 - min_threshold)
                    # to (min_light_brightness_val to max_light_brightness_val)
                    screen_range = 100.0 - min_screen_brightness_threshold_percent
                    light_range = max_light_brightness_val - min_light_brightness_val

                    if screen_range > 0:
                        mapped_brightness = min_light_brightness_val + (screen_brightness_percent - min_screen_brightness_threshold_percent) / screen_range * light_range
                    else: # If screen_range is 0, it means min_threshold is 100, so always max brightness or min
                        mapped_brightness = max_light_brightness_val if screen_brightness_percent >= min_screen_brightness_threshold_percent else min_light_brightness_val
                    
                    current_light_brightness = int(max(min_light_brightness_val, min(max_light_brightness_val, mapped_brightness)))

                # Send command to light (rate-limited by interval_ms)
                # Using set_rgb_and_brightness to send a single command
                r,g,b = avg_rgb
                self.master.after(0, self.light_controller.set_rgb_and_brightness, r, g, b, current_light_brightness)
                
                time.sleep(interval_ms / 1000.0)

        except Exception as e:
            print(f"Ambilight effect error: {e}")
            self.master.after(0, self.update_status, False, f"Ambilight effect stopped due to error: {e}")
            self.master.after(0, self.stop_ambilight_gui) # Stop GUI elements if error occurs
        finally:
            if sct:
                sct.close()

    # Helper function to convert RGB to Hex for color preview
    def rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def load_settings(self):
        if os.path.exists(WIZ_LIGHT_SETTINGS_FILE):
            try:
                with open(WIZ_LIGHT_SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    self.ip_var.set(settings.get("ip_address", WIZ_LIGHT_IP))
                    self.current_rgb = tuple(settings.get("current_rgb", (255, 255, 255)))
                    self.color_preview.config(bg=self.rgb_to_hex(self.current_rgb))
                    self.brightness_slider.set(settings.get("brightness", 255))
                    self._update_brightness_label() # Update label after setting slider
                    self.custom_fade_colors = [tuple(c) for c in settings.get("custom_fade_colors", [])]
                    self.update_custom_color_display()
                    self.is_light_on = settings.get("is_light_on", True)
                    self.fade_duration_var.set(settings.get("fade_duration", "1000"))
                    self.pulsate_interval_var.set(settings.get("pulsate_interval", "500"))
                    self.pulsate_use_custom_colors_var.set(settings.get("pulsate_use_custom_colors", False))
                    
                    # Ensure selected scene is still valid after WIZ_DYNAMIC_SCENES might have changed
                    loaded_scene = settings.get("selected_scene", self.scene_names[0] if self.scene_names else "")
                    if loaded_scene not in self.scene_names and self.scene_names:
                        loaded_scene = self.scene_names[0] # Default to first available if loaded is no longer present
                    self.selected_scene_var.set(loaded_scene)

                    self.scene_speed_var.set(settings.get("scene_speed", "100"))
                    self.selected_monitor_var.set(settings.get("selected_monitor", self.monitor_names[0] if self.monitor_names else ""))
                    self.ambilight_interval_var.set(settings.get("ambilight_interval", "100"))
                    self.min_screen_brightness_threshold.set(settings.get("min_screen_brightness_threshold", 5))
                    self.min_light_brightness.set(settings.get("min_light_brightness", 20))
                    self.max_light_brightness.set(settings.get("max_light_brightness", 255))
                    self.smoothing_factor_slider.set(settings.get("smoothing_factor", 5))
                    self.update_status(True, "Settings loaded successfully.")

            except Exception as e:
                self.update_status(False, f"Error loading settings: {e}. Using default GUI settings.")
        else:
            print("Settings file not found. Using default GUI settings.")
            self.update_status(True, "Settings file not found. Using default GUI settings.")
            # Ensure GUI state reflects defaults
            self.ip_var.set(WIZ_LIGHT_IP)
            self.brightness_slider.set(255)
            self._update_brightness_label()
            self.current_rgb = (255, 255, 255)
            self.custom_fade_colors = []
            self.color_preview.config(bg="#FFFFFF")
            self.update_custom_color_display() # Ensure empty display
            self.is_light_on = True # Default light state if no settings file


    def save_settings(self):
        settings = {
            "ip_address": self.ip_var.get(),
            "current_rgb": self.current_rgb,
            "brightness": int(self.brightness_slider.get()),
            "custom_fade_colors": self.custom_fade_colors,
            "is_light_on": self.is_light_on,
            "fade_duration": self.fade_duration_var.get(),
            "pulsate_interval": self.pulsate_interval_var.get(),
            "pulsate_use_custom_colors": self.pulsate_use_custom_colors_var.get(),
            "selected_scene": self.selected_scene_var.get(),
            "scene_speed": self.scene_speed_var.get(),
            "selected_monitor": self.selected_monitor_var.get(),
            "ambilight_interval": self.ambilight_interval_var.get(),
            "min_screen_brightness_threshold": self.min_screen_brightness_threshold.get(),
            "min_light_brightness": self.min_light_brightness.get(),
            "max_light_brightness": self.max_light_brightness.get(),
            "smoothing_factor": self.smoothing_factor_slider.get(),
        }
        try:
            with open(WIZ_LIGHT_SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            self.update_status(True, "Settings saved.")
        except Exception as e:
            self.update_status(False, f"Error saving settings: {e}")

    def on_closing(self):
        """Handles application shutdown, including saving settings and stopping threads."""
        self.save_settings()
        self.stop_ambilight_gui() # Ensure ambilight thread is stopped

        # Stop the asyncio loop in the background thread of the light controller
        if self.light_controller and self.light_controller.loop.is_running():
            self.light_controller.loop.call_soon_threadsafe(self.light_controller.loop.stop)
            self.light_controller.thread.join(timeout=1) # Wait for the thread to finish

        print("Application closed and background threads stopped.")
        self.master.destroy() # Close the Tkinter window


# --- Main execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LightControlApp(root)
    root.mainloop()