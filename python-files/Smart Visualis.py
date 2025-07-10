# --- START OF COMBINED FILE ---

import ctypes
import platform
import os
import sys
import shutil
import subprocess
import stat # For Smart Folder Copier
import threading
import queue
import traceback # For Visualis error logging

# --- Attempt to set DPI awareness (Windows specific) ---
# This needs to be done BEFORE Tkinter's main window is created.
if platform.system() == "Windows":
    try:
        # awareness = ctypes.c_int() # Querying can be omitted if just setting
        # errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(1) # PROCESS_SYSTEM_DPI_AWARE
        if errorCode != 0: # S_OK is 0
            print(f"Warning: Failed to set DPI awareness via shcore (Error code: {errorCode}). Trying user32...")
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except AttributeError:
                print("Warning: Could not set DPI awareness via user32.")
            except Exception as e_user32:
                print(f"An unexpected error occurred while trying user32.SetProcessDPIAware: {e_user32}")
    except AttributeError: # shcore.dll or SetProcessDpiAwareness not found
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            print("Warning: Could not set DPI awareness. This might lead to blurry text on High DPI displays (user32 not found).")
        except Exception as e_user32_fallback:
             print(f"An unexpected error occurred while trying user32.SetProcessDPIAware as fallback: {e_user32_fallback}")
    except Exception as e_shcore:
        print(f"An unexpected error occurred while trying to set DPI awareness via shcore: {e_shcore}")

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, Listbox, END, SINGLE, Frame, Label, Radiobutton, Button, StringVar
from PIL import Image, ImageDraw, ImageFilter, ImageTk # For Visualis

# --- Attempt to import TkinterDnD2 and provide guidance if missing ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    tkinter_dnd_available = True
except ImportError:
    tkinter_dnd_available = False
# -----------------------------------------------------------------------

# --- GLOBAL CONSTANTS & CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, 'frozen', False) else __file__))

# --- Smart Folder Copier: Constants ---
COPIER_DEFAULT_EXCLUDE_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg', '.vob', '.mts', '.m2ts']
COPIER_FILE_ATTRIBUTE_READONLY = 0x01
COPIER_FILE_ATTRIBUTE_HIDDEN = 0x02
COPIER_FILE_ATTRIBUTE_SYSTEM = 0x04
# --- File Organizer: Constants ---
ORGANIZER_DEFAULT_INCLUDE_EXTENSIONS = ['.mp4', '.jpg', '.png']
# --- Visualis: Constants ---
VISUALIS_DISC_FRAME_FILE_NAME = "disc_frame_overlay.png"
VISUALIS_DISC_CONTENT_DIAMETER = 676
VISUALIS_DISC_OUTPUT_WIDTH = 750
VISUALIS_DISC_OUTPUT_HEIGHT = 750

VISUALIS_DVD_FRAME_IMAGE_FILENAME = "dvd_case.png"
VISUALIS_DVD_TARGET_X = 86
VISUALIS_DVD_TARGET_Y = 16
VISUALIS_DVD_TARGET_WIDTH = 340
VISUALIS_DVD_TARGET_HEIGHT = 480
VISUALIS_DVD_PHOTOSHOP_SHIFT_X = 16
VISUALIS_DVD_PHOTOSHOP_SHIFT_Y = -4
VISUALIS_DVD_POSTER_CORNER_RADIUS_PX = 11
VISUALIS_DVD_FINAL_OUTPUT_PADDING_LEFT = 0
VISUALIS_DVD_FINAL_OUTPUT_PADDING_RIGHT = 0
VISUALIS_DVD_FINAL_OUTPUT_PADDING_TOP = 0
VISUALIS_DVD_FINAL_OUTPUT_PADDING_BOTTOM = 0

VISUALIS_SHINY_FRAME_IMAGE_FILENAME = "shiny_case.png"
VISUALIS_SHINY_TARGET_X = 89
VISUALIS_SHINY_TARGET_Y = 20
VISUALIS_SHINY_TARGET_WIDTH = 334
VISUALIS_SHINY_TARGET_HEIGHT = 471
VISUALIS_SHINY_POSTER_CORNER_RADIUS_PX = 0
VISUALIS_SHINY_FINAL_OUTPUT_PADDING_LEFT = 0
VISUALIS_SHINY_FINAL_OUTPUT_PADDING_RIGHT = 0
VISUALIS_SHINY_FINAL_OUTPUT_PADDING_TOP = 0
VISUALIS_SHINY_FINAL_OUTPUT_PADDING_BOTTOM = 0

VISUALIS_LOG_FILE_NAME = "image_processor_error_log.txt"
VISUALIS_LOG_FILE_PATH = os.path.join(SCRIPT_DIR, VISUALIS_LOG_FILE_NAME)
# -----------------------------------------------------------------------

# --- Smart Folder Copier: Core Logic ---
def copier_set_item_attributes(item_path, log_callback, set_hidden=False, set_system=False, set_readonly=False):
    if os.name == 'nt':
        if not os.path.exists(item_path):
            return
        command = ["attrib"]
        attributes_changed = False
        if set_hidden: command.append("+H"); attributes_changed = True
        if set_system: command.append("+S"); attributes_changed = True
        if set_readonly: command.append("+R"); attributes_changed = True

        if attributes_changed:
            command.append(item_path)
            try:
                creation_flags = 0
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                     creation_flags = subprocess.CREATE_NO_WINDOW
                elif not sys.stdout: # If running without a console (e.g. pythonw.exe)
                     creation_flags = subprocess.CREATE_NO_WINDOW
                process = subprocess.run(command, check=False, capture_output=True, text=True, creationflags=creation_flags)
                if process.returncode != 0:
                    log_callback(f"Warning: 'attrib' for {item_path} returned {process.returncode}. Stderr: {process.stderr.strip()}")
            except Exception as e:
                log_callback(f"Warning: Error setting attributes for {item_path}: {e}")

def copier_copy_directory_recursively(src_dir_current_level, dst_dir_for_current_level_contents, current_exclude_extensions, log_callback):
    source_dir_current_level_is_hidden = False
    source_dir_current_level_is_readonly_or_has_desktop_ini = False

    if os.name == 'nt':
        try:
            source_dir_attrs = os.stat(src_dir_current_level).st_file_attributes
            source_dir_current_level_is_hidden = bool(source_dir_attrs & COPIER_FILE_ATTRIBUTE_HIDDEN)
            source_dir_current_level_is_readonly_or_has_desktop_ini = \
                bool(source_dir_attrs & COPIER_FILE_ATTRIBUTE_READONLY) or \
                os.path.exists(os.path.join(src_dir_current_level, "desktop.ini"))
        except FileNotFoundError:
            log_callback(f"Warning: Could not stat source directory {src_dir_current_level} for attributes.")

    if not os.path.exists(dst_dir_for_current_level_contents):
        try:
            os.makedirs(dst_dir_for_current_level_contents)
            log_callback(f"Created target directory: {dst_dir_for_current_level_contents}")
            if source_dir_current_level_is_hidden:
                copier_set_item_attributes(dst_dir_for_current_level_contents, log_callback, set_hidden=True)
        except OSError as e:
            log_callback(f"Error creating target directory {dst_dir_for_current_level_contents}: {e}")
            return False
    elif not os.path.isdir(dst_dir_for_current_level_contents):
        log_callback(f"Error: Target path '{dst_dir_for_current_level_contents}' exists but is a file.")
        return False
    elif source_dir_current_level_is_hidden:
        try:
            dest_attrs = os.stat(dst_dir_for_current_level_contents).st_file_attributes
            if not (dest_attrs & COPIER_FILE_ATTRIBUTE_HIDDEN):
                copier_set_item_attributes(dst_dir_for_current_level_contents, log_callback, set_hidden=True)
        except FileNotFoundError:
            pass 

    try:
        for item_name in os.listdir(src_dir_current_level):
            source_item_path = os.path.join(src_dir_current_level, item_name)
            destination_item_path = os.path.join(dst_dir_for_current_level_contents, item_name)

            if os.path.isdir(source_item_path):
                if not copier_copy_directory_recursively(source_item_path, destination_item_path, current_exclude_extensions, log_callback):
                    return False
            else:
                _, file_extension = os.path.splitext(item_name)
                if file_extension.lower() not in current_exclude_extensions:
                    try:
                        shutil.copy2(source_item_path, destination_item_path)
                        log_callback(f"Copied: {source_item_path} -> {destination_item_path}")
                        if os.name == 'nt':
                            source_file_attrs = os.stat(source_item_path).st_file_attributes
                            is_src_hidden = bool(source_file_attrs & COPIER_FILE_ATTRIBUTE_HIDDEN)
                            is_src_system = bool(source_file_attrs & COPIER_FILE_ATTRIBUTE_SYSTEM)
                            if item_name.lower() == 'desktop.ini':
                                copier_set_item_attributes(destination_item_path, log_callback, set_hidden=is_src_hidden, set_system=is_src_system)
                            elif is_src_hidden:
                                 copier_set_item_attributes(destination_item_path, log_callback, set_hidden=True)
                    except Exception as e:
                        log_callback(f"Error copying/setting attributes for {source_item_path}: {e}")
                else:
                    log_callback(f"Skipped (excluded extension): {source_item_path}")
    except Exception as e:
         log_callback(f"Error processing directory contents of {src_dir_current_level}: {e}")
         return False

    if source_dir_current_level_is_readonly_or_has_desktop_ini:
        copier_set_item_attributes(dst_dir_for_current_level_contents, log_callback, set_readonly=True)
    return True
# -----------------------------------------------------------------------

# --- Visualis: Core Logic & Helper Functions ---
def visualis_make_square(img, fill_color=(0, 0, 0, 0)):
    img = img.convert("RGBA")
    width, height = img.size
    if width == height:
        return img
    short_side = min(width, height)
    left = (width - short_side) / 2
    top = (height - short_side) / 2
    right = (width + short_side) / 2
    bottom = (height + short_side) / 2
    return img.crop((left, top, right, bottom))

def visualis_apply_circular_mask(img):
    img = img.convert("RGBA")
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    img.putalpha(mask)
    return img

def visualis_apply_rounded_corners(img, corner_radius_px):
    img = img.convert("RGBA")
    width, height = img.size
    if corner_radius_px <= 0:
        return img
    upscale_factor = 4 
    hr_width = width * upscale_factor
    hr_height = height * upscale_factor
    hr_radius = corner_radius_px * upscale_factor
    mask_hr = Image.new('L', (hr_width, hr_height), 0)
    draw_hr = ImageDraw.Draw(mask_hr)
    draw_hr.rounded_rectangle((-5, -5, hr_width, hr_height), radius=hr_radius, fill=255) # Slight oversize to avoid edge artifacts
    mask = mask_hr.resize((width, height), Image.LANCZOS)
    img.putalpha(mask)
    return img

def visualis_process_disc_art(poster_path, base_disc_frame_image, log_callback):
    try:
        if not os.path.exists(poster_path):
            error_msg = f"Error: Poster image not found at {poster_path}"
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_msg + "\n")
            log_callback(error_msg)
            return

        poster_image = Image.open(poster_path)
        squared_poster = visualis_make_square(poster_image)
        resized_poster = squared_poster.resize((VISUALIS_DISC_CONTENT_DIAMETER, VISUALIS_DISC_CONTENT_DIAMETER), Image.LANCZOS)
        circular_poster = visualis_apply_circular_mask(resized_poster)
        final_canvas = Image.new("RGBA", (VISUALIS_DISC_OUTPUT_WIDTH, VISUALIS_DISC_OUTPUT_HEIGHT), (0, 0, 0, 0))
        paste_x = (VISUALIS_DISC_OUTPUT_WIDTH - VISUALIS_DISC_CONTENT_DIAMETER) // 2
        paste_y = (VISUALIS_DISC_OUTPUT_HEIGHT - VISUALIS_DISC_CONTENT_DIAMETER) // 2
        final_canvas.paste(circular_poster, (paste_x, paste_y), circular_poster)
        final_image = Image.alpha_composite(final_canvas, base_disc_frame_image)
        
        output_dir = os.path.dirname(poster_path)
        base_name, _ = os.path.splitext(os.path.basename(poster_path))
        output_filename = f"{base_name}.png" # Always output as PNG for transparency
        output_path = os.path.join(output_dir, output_filename)
        
        final_image.save(output_path)
        log_callback(f"Successfully created disc art: {output_path}")

    except Exception as e:
        error_detail = f"An error occurred while processing {poster_path} for disc art: {e}\n{traceback.format_exc()}"
        with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_detail + "\n")
        log_callback(f"Error processing {poster_path} for disc art. Check log. Error: {e}")

def visualis_process_dvd_case(poster_path, base_dvd_frame_image, log_callback):
    try:
        if not os.path.exists(poster_path):
            error_msg = f"Error: Poster image not found at {poster_path}"
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_msg + "\n")
            log_callback(error_msg)
            return

        poster_image = Image.open(poster_path).convert("RGBA")
        actual_target_width = max(1, VISUALIS_DVD_TARGET_WIDTH)
        actual_target_height = max(1, VISUALIS_DVD_TARGET_HEIGHT)
        stretched_poster = poster_image.resize((actual_target_width, actual_target_height), Image.LANCZOS)
        stretched_poster = stretched_poster.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2))
        processed_poster = visualis_apply_rounded_corners(stretched_poster, corner_radius_px=VISUALIS_DVD_POSTER_CORNER_RADIUS_PX)
        
        composite_base_for_poster = Image.new("RGBA", base_dvd_frame_image.size, (0, 0, 0, 0))
        final_poster_paste_x = VISUALIS_DVD_TARGET_X + VISUALIS_DVD_PHOTOSHOP_SHIFT_X
        final_poster_paste_y = VISUALIS_DVD_TARGET_Y + VISUALIS_DVD_PHOTOSHOP_SHIFT_Y
        composite_base_for_poster.paste(processed_poster, (final_poster_paste_x, final_poster_paste_y), processed_poster)
        dvd_case_with_poster = Image.alpha_composite(composite_base_for_poster, base_dvd_frame_image)

        final_canvas_width = dvd_case_with_poster.width + VISUALIS_DVD_FINAL_OUTPUT_PADDING_LEFT + VISUALIS_DVD_FINAL_OUTPUT_PADDING_RIGHT
        final_canvas_height = dvd_case_with_poster.height + VISUALIS_DVD_FINAL_OUTPUT_PADDING_TOP + VISUALIS_DVD_FINAL_OUTPUT_PADDING_BOTTOM
        final_canvas_width = max(1, final_canvas_width)
        final_canvas_height = max(1, final_canvas_height)
        final_canvas = Image.new("RGBA", (final_canvas_width, final_canvas_height), (0, 0, 0, 0))
        paste_x_on_canvas = VISUALIS_DVD_FINAL_OUTPUT_PADDING_LEFT
        paste_y_on_canvas = VISUALIS_DVD_FINAL_OUTPUT_PADDING_TOP
        final_canvas.paste(dvd_case_with_poster, (paste_x_on_canvas, paste_y_on_canvas))
        
        output_dir = os.path.dirname(poster_path)
        base_name, _ = os.path.splitext(os.path.basename(poster_path))
        output_filename = f"{base_name}.png" # Always output as PNG
        output_path = os.path.join(output_dir, output_filename)
        
        final_canvas.save(output_path)
        log_callback(f"Successfully created DVD case art: {output_path}")

    except Exception as e:
        error_detail = f"An error occurred while processing {poster_path} for DVD case: {e}\n{traceback.format_exc()}"
        with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_detail + "\n")
        log_callback(f"Error processing {poster_path} for DVD case. Check log. Error: {e}")

def visualis_process_shiny_case(poster_path, base_shiny_frame_image, log_callback):
    try:
        if not os.path.exists(poster_path):
            error_msg = f"Error: Poster image not found at {poster_path}"
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_msg + "\n")
            log_callback(error_msg)
            return

        poster_image = Image.open(poster_path).convert("RGBA")
        actual_target_width = max(1, VISUALIS_SHINY_TARGET_WIDTH)
        actual_target_height = max(1, VISUALIS_SHINY_TARGET_HEIGHT)
        stretched_poster = poster_image.resize((actual_target_width, actual_target_height), Image.LANCZOS)
        stretched_poster = stretched_poster.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2))
        processed_poster = visualis_apply_rounded_corners(stretched_poster, corner_radius_px=VISUALIS_SHINY_POSTER_CORNER_RADIUS_PX)

        composite_base_for_poster = Image.new("RGBA", base_shiny_frame_image.size, (0, 0, 0, 0))
        final_poster_paste_x = VISUALIS_SHINY_TARGET_X
        final_poster_paste_y = VISUALIS_SHINY_TARGET_Y
        composite_base_for_poster.paste(processed_poster, (final_poster_paste_x, final_poster_paste_y), processed_poster)
        shiny_case_with_poster = Image.alpha_composite(composite_base_for_poster, base_shiny_frame_image)

        final_canvas_width = shiny_case_with_poster.width + VISUALIS_SHINY_FINAL_OUTPUT_PADDING_LEFT + VISUALIS_SHINY_FINAL_OUTPUT_PADDING_RIGHT
        final_canvas_height = shiny_case_with_poster.height + VISUALIS_SHINY_FINAL_OUTPUT_PADDING_TOP + VISUALIS_SHINY_FINAL_OUTPUT_PADDING_BOTTOM
        final_canvas_width = max(1, final_canvas_width)
        final_canvas_height = max(1, final_canvas_height)
        final_canvas = Image.new("RGBA", (final_canvas_width, final_canvas_height), (0, 0, 0, 0))
        paste_x_on_canvas = VISUALIS_SHINY_FINAL_OUTPUT_PADDING_LEFT
        paste_y_on_canvas = VISUALIS_SHINY_FINAL_OUTPUT_PADDING_TOP
        final_canvas.paste(shiny_case_with_poster, (paste_x_on_canvas, paste_y_on_canvas))
        
        output_dir = os.path.dirname(poster_path)
        base_name, _ = os.path.splitext(os.path.basename(poster_path))
        output_filename = f"{base_name}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        final_canvas.save(output_path)
        log_callback(f"Successfully created Shiny case art: {output_path}")

    except Exception as e:
        error_detail = f"An error occurred while processing {poster_path} for Shiny case: {e}\n{traceback.format_exc()}"
        with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_detail + "\n")
        log_callback(f"Error processing {poster_path} for Shiny case. Check log. Error: {e}")

def visualis_main_orchestrator_gui(poster_paths, mode, log_callback):
    log_callback(f"Visualis: Starting processing in '{mode}' mode for {len(poster_paths)} image(s).")
    
    if mode == "disc":
        frame_file_path = os.path.join(SCRIPT_DIR, VISUALIS_DISC_FRAME_FILE_NAME)
        if not os.path.exists(frame_file_path):
            error_message = f"Error: Disc frame image '{VISUALIS_DISC_FRAME_FILE_NAME}' not found at {frame_file_path}."
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_message + "\n")
            log_callback(error_message)
            return False

        base_frame_image = Image.open(frame_file_path).convert("RGBA")
        if base_frame_image.size != (VISUALIS_DISC_OUTPUT_WIDTH, VISUALIS_DISC_OUTPUT_HEIGHT):
            warning_message = (f"Warning: Disc frame dimensions ({base_frame_image.size}) "
                               f"mismatch expected ({VISUALIS_DISC_OUTPUT_WIDTH}, {VISUALIS_DISC_OUTPUT_HEIGHT}). Resizing.")
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(warning_message + "\n")
            log_callback(warning_message)
            base_frame_image = base_frame_image.resize((VISUALIS_DISC_OUTPUT_WIDTH, VISUALIS_DISC_OUTPUT_HEIGHT), Image.LANCZOS)
        
        for poster_path in poster_paths:
            visualis_process_disc_art(poster_path, base_frame_image, log_callback)

    elif mode == "dvd":
        frame_file_path = os.path.join(SCRIPT_DIR, VISUALIS_DVD_FRAME_IMAGE_FILENAME)
        if not os.path.exists(frame_file_path):
            error_message = f"Error: DVD frame image '{VISUALIS_DVD_FRAME_IMAGE_FILENAME}' not found at {frame_file_path}."
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_message + "\n")
            log_callback(error_message)
            return False
        
        base_frame_image = Image.open(frame_file_path).convert("RGBA")
        for poster_path in poster_paths:
            visualis_process_dvd_case(poster_path, base_frame_image, log_callback)

    elif mode == "shiny":
        frame_file_path = os.path.join(SCRIPT_DIR, VISUALIS_SHINY_FRAME_IMAGE_FILENAME)
        if not os.path.exists(frame_file_path):
            error_message = f"Error: Shiny frame image '{VISUALIS_SHINY_FRAME_IMAGE_FILENAME}' not found at {frame_file_path}."
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_message + "\n")
            log_callback(error_message)
            return False
        
        base_frame_image = Image.open(frame_file_path).convert("RGBA")
        for poster_path in poster_paths:
            visualis_process_shiny_case(poster_path, base_frame_image, log_callback)

    else:
        log_callback(f"Visualis: Invalid mode: {mode}. This should not happen.")
        return False
    return True
# -----------------------------------------------------------------------


# --- Smart Folder Copier: Tkinter Frame Class ---
class CopierFrame(tk.Frame):
    def __init__(self, master, dnd_enabled=False, **kwargs):
        super().__init__(master, **kwargs)
        self.dnd_enabled = dnd_enabled
        self.log_queue = queue.Queue()
        self.current_exclude_extensions = list(COPIER_DEFAULT_EXCLUDE_EXTENSIONS)

        self._setup_ui()
        self.process_log_queue()

        if not self.dnd_enabled:
            self.log_message_to_gui("Note: Drag and Drop for copier is disabled ('tkinterdnd2' not found).\n"
                                    "Use 'Browse...' buttons.\n")

    def _setup_ui(self):
        tk.Label(self, text="Source Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.source_var = tk.StringVar()
        self.source_entry = tk.Entry(self, textvariable=self.source_var, width=70)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Browse...", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)
        if self.dnd_enabled:
            self.source_entry.drop_target_register(DND_FILES)
            self.source_entry.dnd_bind('<<Drop>>', lambda event: self.handle_drop(event, self.source_var))

        tk.Label(self, text="Base Destination Directory:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dest_var = tk.StringVar()
        self.dest_entry = tk.Entry(self, textvariable=self.dest_var, width=70)
        self.dest_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Browse...", command=self.browse_dest).grid(row=1, column=2, padx=5, pady=5)
        if self.dnd_enabled:
            self.dest_entry.drop_target_register(DND_FILES)
            self.dest_entry.dnd_bind('<<Drop>>', lambda event: self.handle_drop(event, self.dest_var))

        exclude_frame = tk.LabelFrame(self, text="Exclude File Extensions", padx=5, pady=5)
        exclude_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

        self.exclude_listbox = Listbox(exclude_frame, height=5, selectmode=SINGLE, exportselection=False)
        self.exclude_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self._populate_exclude_listbox()

        exclude_buttons_frame = tk.Frame(exclude_frame)
        exclude_buttons_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.new_extension_var = tk.StringVar()
        new_ext_entry = tk.Entry(exclude_buttons_frame, textvariable=self.new_extension_var, width=10)
        new_ext_entry.pack(padx=5, pady=(0,5), fill=tk.X)
        tk.Button(exclude_buttons_frame, text="Add (.ext)", command=self.add_extension).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(exclude_buttons_frame, text="Remove Selected", command=self.remove_selected_extension).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(exclude_buttons_frame, text="Reset to Defaults", command=self.reset_exclusions).pack(fill=tk.X, padx=5, pady=2)
        
        exclude_frame.grid_columnconfigure(0, weight=1)

        self.start_button = tk.Button(self, text="Start Copy", command=self.start_copy_thread)
        self.start_button.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

        tk.Label(self, text="Copier Log:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.log_text = scrolledtext.ScrolledText(self, width=80, height=12, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

    def _populate_exclude_listbox(self):
        self.exclude_listbox.delete(0, END)
        for ext in sorted(self.current_exclude_extensions):
            self.exclude_listbox.insert(END, ext)

    def add_extension(self):
        new_ext = self.new_extension_var.get().strip().lower()
        if not new_ext:
            messagebox.showwarning("Input Error", "Extension cannot be empty.", parent=self)
            return
        if not new_ext.startswith('.'):
            new_ext = '.' + new_ext
        
        if new_ext in self.current_exclude_extensions:
            messagebox.showinfo("Info", f"Extension '{new_ext}' is already in the list.", parent=self)
        else:
            self.current_exclude_extensions.append(new_ext)
            self._populate_exclude_listbox()
            self.log_message_to_gui(f"Added '{new_ext}' to exclude list.")
        self.new_extension_var.set("")

    def remove_selected_extension(self):
        selected_indices = self.exclude_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select an extension to remove.", parent=self)
            return
        
        selected_ext = self.exclude_listbox.get(selected_indices[0])
        if selected_ext in self.current_exclude_extensions:
            self.current_exclude_extensions.remove(selected_ext)
            self._populate_exclude_listbox()
            self.log_message_to_gui(f"Removed '{selected_ext}' from exclude list.")
        else:
            messagebox.showerror("Error", "Selected extension not found in internal list.", parent=self)

    def reset_exclusions(self):
        self.current_exclude_extensions = list(COPIER_DEFAULT_EXCLUDE_EXTENSIONS)
        self._populate_exclude_listbox()
        self.log_message_to_gui("Exclude list reset to defaults.")

    def handle_drop(self, event, target_var):
        if not self.dnd_enabled: return
        # On Windows, paths with spaces might be wrapped in {}.
        # event.data could be a single path or multiple (less likely for entry).
        # We use tk.splitlist which is designed to handle this.
        raw_path_list = self.tk.splitlist(event.data)
        dropped_path = ""
        if raw_path_list:
            for p in raw_path_list:
                p_cleaned = p.strip('{}') # Remove braces if any
                if os.path.isdir(p_cleaned):
                    dropped_path = p_cleaned
                    break # Use the first valid directory found
            if dropped_path:
                 target_var.set(dropped_path)
            elif raw_path_list and os.path.isfile(raw_path_list[0].strip('{}')):
                parent_dir = os.path.dirname(raw_path_list[0].strip('{}'))
                target_var.set(parent_dir)
                self.log_message_to_gui(f"Note: Dropped a file, using its parent directory: {parent_dir}")
            else:
                self.log_message_to_gui(f"Warning: Dropped item is not a valid directory: {event.data}")


    def browse_source(self):
        directory = filedialog.askdirectory(title="Select Source Directory", parent=self)
        if directory:
            self.source_var.set(directory)

    def browse_dest(self):
        directory = filedialog.askdirectory(title="Select Base Destination Directory", parent=self)
        if directory:
            self.dest_var.set(directory)

    def log_message_to_gui(self, message, end="\n"):
        self.log_queue.put(message + end)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue) # Use self.after for frames

    def start_copy_thread(self):
        source_dir = self.source_var.get()
        dest_base_dir = self.dest_var.get()

        if not source_dir or not dest_base_dir:
            messagebox.showerror("Input Error", "Please select both source and destination directories.", parent=self)
            return
        if not os.path.isdir(source_dir):
            messagebox.showerror("Input Error", f"Source path is not a valid directory:\n{source_dir}", parent=self)
            return
        if os.path.exists(dest_base_dir) and not os.path.isdir(dest_base_dir):
            messagebox.showerror("Input Error", f"Destination base path exists and is a file:\n{dest_base_dir}", parent=self)
            return

        abs_source_dir = os.path.abspath(source_dir)
        abs_dest_base_dir = os.path.abspath(dest_base_dir)

        if abs_source_dir == abs_dest_base_dir:
            messagebox.showerror("Path Error", "Source and base destination directories cannot be the same.", parent=self)
            return
        if abs_dest_base_dir.startswith(abs_source_dir + os.sep): # Important: os.sep for cross-platform
            messagebox.showerror("Path Error", "Base destination directory cannot be a subdirectory of the source directory.", parent=self)
            return

        source_folder_name = os.path.basename(abs_source_dir)
        actual_copy_target_path = os.path.join(abs_dest_base_dir, source_folder_name)

        current_exclusions_str = ", ".join(sorted(self.current_exclude_extensions)) if self.current_exclude_extensions else "None"
        confirmation_message = (
            f"Source: {abs_source_dir}\n"
            f"Destination Base: {abs_dest_base_dir}\n"
            f"The folder '{source_folder_name}' will be copied to: {actual_copy_target_path}\n\n"
            f"Exclude extensions: {current_exclusions_str}\n\n"
            "Proceed with copy?"
        )
        if not messagebox.askyesno("Confirm Copy Operation", confirmation_message, parent=self):
            self.log_message_to_gui("Operation cancelled by user.")
            return

        self.log_text.delete(1.0, tk.END)
        self.log_message_to_gui("Starting copy operation...\n")
        self.start_button.config(state=tk.DISABLED)
        exclusions_to_use = list(self.current_exclude_extensions)

        thread = threading.Thread(
            target=self._execute_copy,
            args=(abs_source_dir, actual_copy_target_path, exclusions_to_use, self.log_message_to_gui),
            daemon=True
        )
        thread.start()

    def _execute_copy(self, src, dst, exclusions, log_callback_gui):
        try:
            if copier_copy_directory_recursively(src, dst, exclusions, log_callback_gui):
                log_callback_gui("\nCopy operation completed successfully.")
                self.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", "Copy operation completed successfully!\nYou may need to refresh Explorer to see icon changes.", parent=self))
            else:
                log_callback_gui("\nCopy operation encountered an error or did not complete successfully.")
                self.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", "Copy operation failed. Check log for details.", parent=self))
        except Exception as e:
            log_callback_gui(f"\nAn unexpected error occurred during the operation: {e}")
            self.winfo_toplevel().after(0, lambda: messagebox.showerror("Critical Error", f"An unexpected error occurred: {e}", parent=self))
        finally:
            self.winfo_toplevel().after(0, lambda: self.start_button.config(state=tk.NORMAL))
# -----------------------------------------------------------------------
# --- File Organizer: Tkinter Frame Class ---
class OrganizerFrame(tk.Frame):
    def __init__(self, master, dnd_enabled=False, **kwargs):
        super().__init__(master, **kwargs)
        self.dnd_enabled = dnd_enabled
        self.log_queue = queue.Queue()
        self.included_extensions = list(ORGANIZER_DEFAULT_INCLUDE_EXTENSIONS)
        self.create_folder_var = tk.BooleanVar(value=True)

        self._setup_ui()
        self.process_log_queue()

        if not self.dnd_enabled:
            self.log_message_to_gui("Note: Drag and Drop for organizer is disabled ('tkinterdnd2' not found).\n"
                                    "Use the 'Browse...' button.\n")

    def _setup_ui(self):
        tk.Label(self, text="Target Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.target_dir_var = tk.StringVar()
        self.target_dir_entry = tk.Entry(self, textvariable=self.target_dir_var, width=70)
        self.target_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Browse...", command=self.browse_target_directory).grid(row=0, column=2, padx=5, pady=5)
        if self.dnd_enabled:
            self.target_dir_entry.drop_target_register(DND_FILES)
            self.target_dir_entry.dnd_bind('<<Drop>>', lambda event: self.handle_drop(event, self.target_dir_var))

        include_frame = tk.LabelFrame(self, text="Included File Formats (will be moved)", padx=5, pady=5)
        include_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

        self.include_listbox = Listbox(include_frame, height=5, selectmode=SINGLE, exportselection=False)
        self.include_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self._populate_include_listbox()

        include_buttons_frame = tk.Frame(include_frame)
        include_buttons_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.new_extension_var = tk.StringVar()
        new_ext_entry = tk.Entry(include_buttons_frame, textvariable=self.new_extension_var, width=10)
        new_ext_entry.pack(padx=5, pady=(0, 5), fill=tk.X)
        tk.Button(include_buttons_frame, text="Add (.ext)", command=self.add_extension).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(include_buttons_frame, text="Remove Selected", command=self.remove_selected_extension).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(include_buttons_frame, text="Reset to Defaults", command=self.reset_extensions).pack(fill=tk.X, padx=5, pady=2)

        include_frame.grid_columnconfigure(0, weight=1)

        create_folder_check = tk.Checkbutton(self, text="Create folder if it doesn't exist for a matching file", variable=self.create_folder_var)
        create_folder_check.grid(row=2, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="w")

        self.start_button = tk.Button(self, text="Start Organizing", command=self.start_organizing_thread)
        self.start_button.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

        tk.Label(self, text="Organizer Log:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.log_text = scrolledtext.ScrolledText(self, width=80, height=14, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

    def _populate_include_listbox(self):
        self.include_listbox.delete(0, END)
        for ext in sorted(self.included_extensions):
            self.include_listbox.insert(END, ext)

    def add_extension(self):
        new_ext = self.new_extension_var.get().strip().lower()
        if not new_ext:
            messagebox.showwarning("Input Error", "Extension cannot be empty.", parent=self)
            return
        if not new_ext.startswith('.'):
            new_ext = '.' + new_ext

        if new_ext in self.included_extensions:
            messagebox.showinfo("Info", f"Extension '{new_ext}' is already in the list.", parent=self)
        else:
            self.included_extensions.append(new_ext)
            self._populate_include_listbox()
            self.log_message_to_gui(f"Added '{new_ext}' to include list.")
        self.new_extension_var.set("")

    def remove_selected_extension(self):
        selected_indices = self.include_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select an extension to remove.", parent=self)
            return

        selected_ext = self.include_listbox.get(selected_indices[0])
        if selected_ext in self.included_extensions:
            self.included_extensions.remove(selected_ext)
            self._populate_include_listbox()
            self.log_message_to_gui(f"Removed '{selected_ext}' from include list.")
        else:
            messagebox.showerror("Error", "Selected extension not found in internal list.", parent=self)

    def reset_extensions(self):
        self.included_extensions = list(ORGANIZER_DEFAULT_INCLUDE_EXTENSIONS)
        self._populate_include_listbox()
        self.log_message_to_gui("Include list reset to defaults.")

    def handle_drop(self, event, target_var):
        if not self.dnd_enabled: return
        raw_path_list = self.tk.splitlist(event.data)
        dropped_path = ""
        if raw_path_list:
            p_cleaned = raw_path_list[0].strip('{}')
            if os.path.isdir(p_cleaned):
                dropped_path = p_cleaned
            elif os.path.isfile(p_cleaned):
                dropped_path = os.path.dirname(p_cleaned)
                self.log_message_to_gui(f"Note: Dropped a file, using its parent directory: {dropped_path}")
            
            if dropped_path:
                target_var.set(dropped_path)
            else:
                self.log_message_to_gui(f"Warning: Dropped item is not a valid directory: {event.data}")

    def browse_target_directory(self):
        directory = filedialog.askdirectory(title="Select Target Directory to Organize", parent=self)
        if directory:
            self.target_dir_var.set(directory)

    def log_message_to_gui(self, message, end="\n"):
        self.log_queue.put(message + end)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def start_organizing_thread(self):
        target_dir = self.target_dir_var.get()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Input Error", f"Please select a valid target directory.", parent=self)
            return

        abs_target_dir = os.path.abspath(target_dir)
        included_formats_str = ", ".join(sorted(self.included_extensions)) if self.included_extensions else "None"
        create_folder_if_missing = self.create_folder_var.get()
        
        confirmation_message = (
            f"Target Directory: {abs_target_dir}\n\n"
            f"Included formats: {included_formats_str}\n"
            f"Create folder if missing: {'Yes' if create_folder_if_missing else 'No'}\n\n"
            "Example: 'Movie.mp4' will be moved into a folder named 'Movie'.\n\n"
            "Proceed with organization?"
        )
        if not messagebox.askyesno("Confirm Organization", confirmation_message, parent=self):
            self.log_message_to_gui("Operation cancelled by user.")
            return

        self.log_text.delete(1.0, tk.END)
        self.log_message_to_gui("Starting organization...\n")
        self.start_button.config(state=tk.DISABLED)
        extensions_to_use = list(self.included_extensions)

        thread = threading.Thread(
            target=self._execute_organization,
            args=(abs_target_dir, extensions_to_use, create_folder_if_missing, self.log_message_to_gui),
            daemon=True
        )
        thread.start()

    def _execute_organization(self, target_dir, extensions, create_folder_if_missing, log_callback_gui):
        moved_count = 0
        try:
            script_name = os.path.basename(sys.argv[0] if getattr(sys, 'frozen', False) else __file__)
            log_callback_gui(f"Scanning directory: {target_dir}")
            log_callback_gui(f"Included extensions: {', '.join(extensions)}")
            log_callback_gui(f"Create folder if missing: {'Yes' if create_folder_if_missing else 'No'}")
            log_callback_gui(f"Ignoring script file: {script_name}\n")
            
            items_in_dir = os.listdir(target_dir)

            for item_name in items_in_dir:
                source_item_path = os.path.join(target_dir, item_name)

                if item_name.lower() == script_name.lower():
                    continue

                if os.path.isfile(source_item_path):
                    base_name, file_ext = os.path.splitext(item_name)
                    
                    if file_ext.lower() in extensions:
                        destination_folder_path = os.path.join(target_dir, base_name)
                        
                        should_move = False
                        if os.path.isdir(destination_folder_path):
                            should_move = True
                        elif create_folder_if_missing and not os.path.exists(destination_folder_path):
                            try:
                                os.makedirs(destination_folder_path)
                                log_callback_gui(f"Created folder: '{base_name}'")
                                should_move = True
                            except Exception as e:
                                log_callback_gui(f"ERROR creating folder for '{item_name}': {e}")
                        
                        if should_move:
                            try:
                                shutil.move(source_item_path, destination_folder_path)
                                log_callback_gui(f"Moved: '{item_name}' -> '{base_name}/'")
                                moved_count += 1
                            except Exception as e:
                                log_callback_gui(f"ERROR moving '{item_name}': {e}")
                        else:
                            if os.path.exists(destination_folder_path):
                                log_callback_gui(f"Skipped '{item_name}': Path '{base_name}' exists but is not a directory.")
                            else:
                                log_callback_gui(f"Skipped '{item_name}': Folder '{base_name}' not found and 'Create folder' is off.")
            
            log_callback_gui(f"\nOrganization attempt complete. Total files moved: {moved_count}.")
            self.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", f"Organization complete!\n\nFiles moved: {moved_count}", parent=self))

        except Exception as e:
            log_callback_gui(f"\nAn unexpected error occurred: {e}")
            self.winfo_toplevel().after(0, lambda: messagebox.showerror("Critical Error", f"An unexpected error occurred: {e}", parent=self))
        finally:
            self.winfo_toplevel().after(0, lambda: self.start_button.config(state=tk.NORMAL))
# -----------------------------------------------------------------------
# --- Visualis: Tkinter Frame Class ---
class VisualisFrame(tk.Frame):
    def __init__(self, master, dnd_enabled=False, **kwargs):
        super().__init__(master, **kwargs)
        self.dnd_enabled = dnd_enabled
        self.selected_files = []
        self.log_queue = queue.Queue()
        self.processing_mode = StringVar(value="dvd") 
        self.disc_icon_tk = None
        self.dvd_icon_tk = None
        self.shiny_icon_tk = None
        
        self._load_frame_icons()
        self._setup_ui()
        self.process_log_queue()

        self.log_message_to_gui(f"Visualis log file will be saved to: {VISUALIS_LOG_FILE_PATH}\n"
                                f"Ensure '{VISUALIS_DISC_FRAME_FILE_NAME}', '{VISUALIS_DVD_FRAME_IMAGE_FILENAME}', and '{VISUALIS_SHINY_FRAME_IMAGE_FILENAME}' are in: {SCRIPT_DIR}\n")
        if not self.dnd_enabled:
            self.log_message_to_gui("TIP: Install 'tkinterdnd2' for Drag & Drop support (pip install tkinterdnd2)\n")
        else:
            self.log_message_to_gui("Drag & Drop image files into the list above.\n")


    def _load_frame_icons(self):
        icon_size = (64, 64) 
        try:
            disc_img_path = os.path.join(SCRIPT_DIR, VISUALIS_DISC_FRAME_FILE_NAME)
            if os.path.exists(disc_img_path):
                img = Image.open(disc_img_path)
                img.thumbnail(icon_size, Image.LANCZOS)
                self.disc_icon_tk = ImageTk.PhotoImage(img)
            else:
                self.log_message_to_gui(f"Warning: Disc frame icon not found: {disc_img_path}")
        except Exception as e:
            self.log_message_to_gui(f"Error loading disc icon: {e}")

        try:
            dvd_img_path = os.path.join(SCRIPT_DIR, VISUALIS_DVD_FRAME_IMAGE_FILENAME)
            if os.path.exists(dvd_img_path):
                img = Image.open(dvd_img_path)
                img.thumbnail(icon_size, Image.LANCZOS)
                self.dvd_icon_tk = ImageTk.PhotoImage(img)
            else:
                self.log_message_to_gui(f"Warning: DVD frame icon not found: {dvd_img_path}")
        except Exception as e:
            self.log_message_to_gui(f"Error loading DVD icon: {e}")
            
        try:
            shiny_img_path = os.path.join(SCRIPT_DIR, VISUALIS_SHINY_FRAME_IMAGE_FILENAME)
            if os.path.exists(shiny_img_path):
                img = Image.open(shiny_img_path)
                img.thumbnail(icon_size, Image.LANCZOS)
                self.shiny_icon_tk = ImageTk.PhotoImage(img)
            else:
                self.log_message_to_gui(f"Warning: Shiny frame icon not found: {shiny_img_path}")
        except Exception as e:
            self.log_message_to_gui(f"Error loading Shiny icon: {e}")

    def _setup_ui(self):
        # File selection frame
        file_frame = Frame(self, padx=10, pady=10)
        file_frame.pack(fill=tk.X)

        Label(file_frame, text="Poster Images:").pack(side=tk.LEFT)
        Button(file_frame, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=5)
        Button(file_frame, text="Remove Selected", command=self.remove_selected_file).pack(side=tk.LEFT, padx=5)
        Button(file_frame, text="Clear All", command=self.clear_all_files).pack(side=tk.LEFT, padx=5)

        self.file_listbox = Listbox(self, selectmode=SINGLE, height=6)
        self.file_listbox.pack(fill=tk.X, padx=10, pady=5)

        if self.dnd_enabled:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.handle_drop)
            dnd_info_text = "Drag & Drop image files into the list above."
            dnd_info_fg = "grey"
        else:
            dnd_info_text = "Drag & Drop disabled (tkinterdnd2 not found). Use 'Add Files...'"
            dnd_info_fg = "red"
        Label(self, text=dnd_info_text, font=("Segoe UI", 8), fg=dnd_info_fg).pack(fill=tk.X, padx=10, pady=(0,5))
        
        # Mode selection frame
        mode_outer_frame = Frame(self, padx=10, pady=5)
        mode_outer_frame.pack(fill=tk.X)
        Label(mode_outer_frame, text="Processing Mode:").pack(side=tk.LEFT, anchor='n', pady=(10 if self.dvd_icon_tk else 0))

        mode_selection_area = Frame(mode_outer_frame) # New frame to center radio buttons
        mode_selection_area.pack(expand=True) # This will allow centering

        dvd_radio_frame = Frame(mode_selection_area)
        dvd_radio_frame.pack(side=tk.LEFT, padx=15)
        if self.dvd_icon_tk:
            Label(dvd_radio_frame, image=self.dvd_icon_tk).pack()
        Radiobutton(dvd_radio_frame, text="DVD Case Art", variable=self.processing_mode, value="dvd").pack()

        shiny_radio_frame = Frame(mode_selection_area)
        shiny_radio_frame.pack(side=tk.LEFT, padx=15)
        if self.shiny_icon_tk:
            Label(shiny_radio_frame, image=self.shiny_icon_tk).pack()
        Radiobutton(shiny_radio_frame, text="Shiny Case Art", variable=self.processing_mode, value="shiny").pack()

        disc_radio_frame = Frame(mode_selection_area)
        disc_radio_frame.pack(side=tk.LEFT, padx=15)
        if self.disc_icon_tk:
            Label(disc_radio_frame, image=self.disc_icon_tk).pack()
        Radiobutton(disc_radio_frame, text="Disc Art", variable=self.processing_mode, value="disc").pack()

        self.start_button = Button(self, text="Start Processing", command=self.start_processing_thread, height=2)
        self.start_button.pack(pady=10, fill=tk.X, padx=10)

        log_label = Label(self, text="Visualis Log:")
        log_label.pack(anchor='w', padx=10, pady=(5,0))
        self.log_text = scrolledtext.ScrolledText(self, height=8, wrap=tk.WORD) # Adjusted height
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.log_text.configure(state='disabled')

    def log_message_to_gui(self, message, end="\n"):
        self.log_queue.put(message + end)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue) # Use self.after

    def _add_files_to_list(self, file_paths):
        added_count = 0
        for f_path in file_paths:
            f_path_norm = os.path.normpath(f_path)
            ext = os.path.splitext(f_path_norm)[1].lower()
            valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
            
            if ext not in valid_extensions:
                self.log_message_to_gui(f"Skipped non-image file: {os.path.basename(f_path_norm)}")
                continue

            if f_path_norm not in self.selected_files:
                self.selected_files.append(f_path_norm)
                # Display only basename in listbox for brevity if path is long
                display_name = os.path.basename(f_path_norm)
                if len(f_path_norm) > 60 : # Arbitrary length check
                    display_name += f" (...{os.path.basename(os.path.dirname(f_path_norm))})"
                else:
                    display_name = f_path_norm # Show full if short
                self.file_listbox.insert(END, display_name)
                added_count += 1
        if added_count > 0:
            self.log_message_to_gui(f"Added {added_count} file(s). Total: {len(self.selected_files)}")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Poster Image(s)",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")),
            parent=self
        )
        if files:
            self._add_files_to_list(files)

    def handle_drop(self, event):
        if not self.dnd_enabled: return
        raw_path_list = self.tk.splitlist(event.data)
        files_to_add = []
        for p in raw_path_list:
            cleaned_path = p.strip('{}')
            if os.path.isfile(cleaned_path):
                files_to_add.append(cleaned_path)
            elif os.path.isdir(cleaned_path):
                self.log_message_to_gui(f"Scanning directory for images: {cleaned_path}...")
                for root, _, files in os.walk(cleaned_path):
                    for name in files:
                        files_to_add.append(os.path.join(root, name))
        
        if files_to_add:
            self._add_files_to_list(files_to_add)

    def remove_selected_file(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a file to remove.", parent=self)
            return
        
        # Remove from listbox and internal list, iterating backwards
        for index in sorted(selected_indices, reverse=True):
            self.file_listbox.delete(index)
            removed_file_path = self.selected_files.pop(index) # This is the full path
            self.log_message_to_gui(f"Removed: {os.path.basename(removed_file_path)}")


    def clear_all_files(self):
        self.selected_files.clear()
        self.file_listbox.delete(0, END)
        self.log_message_to_gui("Cleared all selected files.")

    def start_processing_thread(self):
        if not self.selected_files:
            messagebox.showerror("Input Error", "Please add at least one image file.", parent=self)
            return
        mode = self.processing_mode.get()
        if not mode: # Should not happen with radio buttons
            messagebox.showerror("Input Error", "Please select a processing mode.", parent=self)
            return

        self.start_button.config(state=tk.DISABLED, text="Processing...")
        self.log_message_to_gui("--- Visualis processing started ---")
        files_to_process = list(self.selected_files) # Use a copy

        thread = threading.Thread(
            target=self._execute_processing,
            args=(files_to_process, mode, self.log_message_to_gui),
            daemon=True
        )
        thread.start()

    def _execute_processing(self, file_paths, mode, log_callback_gui):
        try:
            # Clear Visualis log file for this session part if desired, or append.
            # Current Visualis code appends to its log file.
            success = visualis_main_orchestrator_gui(file_paths, mode, log_callback_gui)
            if success:
                log_callback_gui("--- Visualis processing completed successfully ---")
                self.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", "Image processing completed successfully!", parent=self))
            else:
                log_callback_gui("--- Visualis processing completed with errors ---")
                self.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", "Image processing encountered errors. Check the log for details.", parent=self))
        except Exception as e:
            error_detail = f"An unexpected critical error in Visualis: {e}\n{traceback.format_exc()}"
            with open(VISUALIS_LOG_FILE_PATH, "a", encoding="utf-8") as f: f.write(error_detail + "\n")
            log_callback_gui(f"VISUALIS CRITICAL ERROR: {e}. Check log.")
            self.winfo_toplevel().after(0, lambda: messagebox.showerror("Critical Error", f"An unexpected critical error in Visualis: {e}", parent=self))
        finally:
             self.winfo_toplevel().after(0, lambda: self.start_button.config(state=tk.NORMAL, text="Start Processing"))
# -----------------------------------------------------------------------

# --- Main Application Class ---
class MainApplication:
    def __init__(self, root, dnd_enabled):
        self.root = root
        self.root.title("Ultimate Toolbox")
        self.root.geometry("800x750") # Adjusted size for new tab

        self.notebook = ttk.Notebook(self.root)

        self.copier_tab = CopierFrame(self.notebook, dnd_enabled=dnd_enabled)
        self.organizer_tab = OrganizerFrame(self.notebook, dnd_enabled=dnd_enabled)
        self.visualis_tab = VisualisFrame(self.notebook, dnd_enabled=dnd_enabled)

        self.notebook.add(self.visualis_tab, text="Visualis Image Processor")
        self.notebook.add(self.copier_tab, text="Smart Folder Copier")
        self.notebook.add(self.organizer_tab, text="File Organizer")
        
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Initial message if TkinterDnD is not available
        if not dnd_enabled:
             messagebox.showwarning(
                "Drag & Drop Disabled",
                "The 'tkinterdnd2' library is not found.\n\n"
                "Drag and Drop functionality will be disabled in all tabs.\n"
                "To enable it, install the library (e.g., 'pip install tkinterdnd2') and restart the application.",
                parent=self.root 
            )

# --- Entry Point ---
if __name__ == "__main__":
    # Initialize Visualis log file for the session
    try:
        with open(VISUALIS_LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(f"Visualis Log - Session started at {platform.node()} {sys.platform}\n")
            f.write("="*30 + "\n")
    except IOError as e:
        print(f"Warning: Could not initialize Visualis log file: {e}")

    if tkinter_dnd_available:
        main_window = TkinterDnD.Tk()
    else:
        main_window = tk.Tk()
    
    app = MainApplication(main_window, tkinter_dnd_available)
    main_window.mainloop()

# --- END OF COMBINED FILE ---