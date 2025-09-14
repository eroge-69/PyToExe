import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Try to import TkinterDnD for drag and drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES

    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False

from tkinter import simpledialog
import sqlite3
import os
import threading
import sys
import shutil
import time  # Added for connection caching
import re  # For regex pattern matching
import uuid  # For generating unique IDs
import socket  # For hostname identification
import psycopg2  # For PostgreSQL connection
import binascii  # For hex conversion
import subprocess  # For running external commands
import hashlib  # For hashing
from typing import List, Dict  # For type hints

# Try to import netifaces for MAC address detection
try:
    import netifaces

    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False

# Database Configuration
DB_HOST = '195.35.44.135'  # MySQL server IP
DB_USER = 'u634980388_fccinward'  # MySQL username
DB_PASSWORD = 'Vikash@0120'  # MySQL password
DB_NAME = 'u634980388_inward'  # Database name
LOCAL_DB_PATH = 'model_offsets.db'  # Local SQLite database

# PostgreSQL database configuration (using environment variables)
PG_HOST = os.environ.get('PGHOST', 'localhost')
PG_PORT = os.environ.get('PGPORT', '5432')
PG_USER = os.environ.get('PGUSER', 'postgres')
PG_PASSWORD = os.environ.get('PGPASSWORD', '')
PG_DATABASE = os.environ.get('PGDATABASE', 'postgres')
PG_CONNECTION_STRING = os.environ.get('DATABASE_URL',
                                      f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}')

# Global setting for online mode
ONLINE_MODE_ENABLED = True

# Create a flag for sound support
SOUND_SUPPORTED = False
try:
    if sys.platform == 'win32':
        import winsound

        SOUND_SUPPORTED = True
except ImportError:
    pass  # Sound will be disabled if winsound is not available

# Import MySQL conditionally to handle environments where it might not be available
MYSQL_AVAILABLE = False
# Cache variables for connection status to improve performance
MYSQL_CONNECTION_CACHE = None  # Cache for MySQL connection status
MYSQL_CACHE_TIME = 0  # Last time the connection was checked
try:
    import mysql.connector as mysql_connector

    MYSQL_AVAILABLE = True
except ImportError:
    pass  # MySQL functionality will be disabled if not available


# BIOS Unlocker Tool Functions
def convert_hex_to_bytes(hex_string):
    """Convert hex string to byte array"""
    try:
        return bytes.fromhex(hex_string)
    except binascii.Error as e:
        return None


def bytes_to_hex_string(byte_array):
    """Convert byte array to hex string without separators"""
    return byte_array.hex().upper()


def find_intel_signature(data, signature_bytes):
    """Find Intel signature in the first 0x1000 bytes"""
    for i in range(min(0x1000, len(data) - len(signature_bytes))):
        if data[i:i + len(signature_bytes)] == signature_bytes:
            return i
    return -1


def find_pattern_matches(data, pattern_regex):
    """Find all matches of the regex pattern in the data, but only up to offset 0x160000"""
    matches = []

    max_offset = min(0x160000, len(data))
    for i in range(max_offset):
        chunk_size = min(20, len(data) - i)
        if chunk_size < 6:
            continue

        chunk = data[i:i + chunk_size]
        hex_chunk = bytes_to_hex_string(chunk)

        match = re.match(pattern_regex, hex_chunk)
        if match:
            matches.append(i)

    return matches


# Main Application Class
class FCCToolsApp:
    def __init__(self, root):
        # If tkinterdnd2 is available, use the TkinterDnD version of the root
        if TKDND_AVAILABLE:
            # Convert root to TkinterDnD Tk if it's a normal Tk
            if not isinstance(root, TkinterDnD.Tk):
                print("Converting root to TkinterDnD.Tk")
                # Get existing attributes that need to be transferred
                title = root.title()
                geometry = root.geometry()
                # Destroy the old root
                root.destroy()
                # Create a new TkinterDnD.Tk root
                root = TkinterDnD.Tk()
                # Restore attributes
                root.title(title)
                root.geometry(geometry)
                # Update the root reference
                self.root = root
            else:
                self.root = root
        else:
            self.root = root

        self.root.title("FCC Repair Tools Pro")
        self.root.geometry("1100x750")  # Adjusted window size for better layout
        self.root.minsize(1000, 700)  # Set minimum window size for better usability

        # Flag to track if registration form is showing
        self.registration_form_active = False

        # Flag to track if user is registered
        self.user_registered = False

        # Flag to track if user has skipped registration
        self.registration_skipped = False

        # Set app icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Continue if icon file doesn't exist

        # Set up custom ttk styles first
        self.setup_styles()

        # Try to set icon if available
        try:
            self.root.iconbitmap("logo.ico")
        except tk.TclError:
            pass  # Skip if icon not found or not supported

        # Initialize variables for selected model
        self.selected_model_name = None
        self.selected_start_offset = None
        self.selected_end_offset = None

        # Create a notebook (tabbed interface)
        # Create main container frame for the entire application layout
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the notebook (tabbed interface) in the main container with enhanced interactivity
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Enable tab navigation with keyboard shortcuts
        self.notebook.enable_traversal()

        # Bind tab change event for better interactivity
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Create the tabs
        self.tab1 = ttk.Frame(self.notebook)  # Model Offsets Database Tab
        self.tab2 = ttk.Frame(self.notebook)  # Flash Descriptor Tool Tab
        self.tab3 = ttk.Frame(self.notebook)  # User Profile Tab
        self.tab4 = ttk.Frame(self.notebook)  # Dell 8FC8 Unlocker Tab

        # Add tabs to notebook
        self.notebook.add(self.tab1, text="Model Offsets Database")
        self.notebook.add(self.tab2, text="Flash Descriptor Tool")
        self.notebook.add(self.tab3, text="User Profile")

        # Create the repair tool interface (matching the image)
        self.main_frame = ttk.Frame(self.tab2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create common status and info area below the notebook (visible for both tabs)
        self.common_status_frame = ttk.Frame(self.main_container)
        self.common_status_frame.pack(fill=tk.X, padx=10, pady=5)

        # Status frame (shared between both tabs)
        self.status_frame = ttk.LabelFrame(self.common_status_frame, text="Status")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="Ready", style="Success.TLabel")
        self.status_label.pack(fill=tk.X, padx=10, pady=10)

        # Process information frame (shared between both tabs)
        self.info_frame = ttk.LabelFrame(self.common_status_frame, text="Process Information", style="Info.TLabelframe")
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Use console style from theme colors
        self.info_text = scrolledtext.ScrolledText(
            self.info_frame,
            height=10,
            bg=self.console_bg,  # Theme-based background
            fg=self.console_fg,  # Theme-based text color
            font=("Consolas", 9),  # Monospace font for console look
            relief="flat",  # Flat border for modern appearance
            borderwidth=0,  # No border
            padx=5,  # Padding for better text display
            pady=5
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create left and right panels
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create sections for the left panel (similar to image)
        self.tool_title = ttk.Label(self.left_panel, text="Flash Descriptor Tool", font=("Arial", 16))
        self.tool_title.pack(pady=10)

        # Source Binary File section
        self.source_frame = ttk.LabelFrame(self.left_panel, text="Source Binary File", style="Info.TLabelframe")
        self.source_frame.pack(fill=tk.X, padx=10, pady=5)

        source_file_frame = ttk.Frame(self.source_frame)
        source_file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(source_file_frame, text="Source File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.source_file_var = tk.StringVar()
        ttk.Entry(source_file_frame, textvariable=self.source_file_var, width=40).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(source_file_frame, text="Browse", command=self.browse_source_file).grid(row=0, column=2, padx=5,
                                                                                           pady=2)

        # Target Binary File section
        self.target_frame = ttk.LabelFrame(self.left_panel, text="Target Binary File", style="Info.TLabelframe")
        self.target_frame.pack(fill=tk.X, padx=10, pady=5)

        target_file_frame = ttk.Frame(self.target_frame)
        target_file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(target_file_frame, text="Target File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.target_file_var = tk.StringVar()
        ttk.Entry(target_file_frame, textvariable=self.target_file_var, width=40).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(target_file_frame, text="Browse", command=self.browse_target_file).grid(row=0, column=2, padx=5,
                                                                                           pady=2)

        # Action buttons section with checkboxes
        self.action_frame = ttk.Frame(self.left_panel)
        self.action_frame.pack(fill=tk.X, padx=10, pady=15)

        # Checkboxes for different modes (mutually exclusive)
        mode_frame = ttk.Frame(self.action_frame)
        mode_frame.pack(side=tk.LEFT, padx=5)

        # Create a column frame for mode selection checkboxes
        mode_options_column = ttk.Frame(mode_frame)
        mode_options_column.pack(side=tk.TOP, fill=tk.X, padx=0, pady=2)

        # Create a StringVar to track the selected mode (one at a time)
        self.selected_mode = tk.StringVar(value="flash_descriptor")

        # Define command for checkbox change
        def on_flash_checkbox_change():
            if self.flash_descriptor_var.get():
                self.window_key_var.set(False)
                self.dell_8fc8_var.set(False)
                self.selected_mode.set("flash_descriptor")
            elif not (self.window_key_var.get() or self.dell_8fc8_var.get()):
                # If nothing is selected, keep Flash Descriptor selected
                self.flash_descriptor_var.set(True)

        def on_window_key_checkbox_change():
            if self.window_key_var.get():
                self.flash_descriptor_var.set(False)
                self.dell_8fc8_var.set(False)
                self.selected_mode.set("window_key")
            elif not (self.flash_descriptor_var.get() or self.dell_8fc8_var.get()):
                # If nothing is selected, keep Window Key selected
                self.window_key_var.set(True)

        def on_dell_8fc8_checkbox_change():
            if self.dell_8fc8_var.get():
                self.flash_descriptor_var.set(False)
                self.window_key_var.set(False)
                self.selected_mode.set("dell_8fc8")
                # Launch Dell 8FC8 unlocker immediately when checkbox is ticked
                self.launch_dell_8fc8_unlocker()
            elif not (self.flash_descriptor_var.get() or self.window_key_var.get()):
                # If nothing is selected, keep Dell 8FC8 selected
                self.dell_8fc8_var.set(True)

        # Initialize boolean variables for checkbox states
        self.flash_descriptor_var = tk.BooleanVar(value=True)
        self.window_key_var = tk.BooleanVar(value=False)
        self.dell_8fc8_var = tk.BooleanVar(value=False)

        # Create Flash Descriptor checkbox
        self.flash_checkbox = ttk.Checkbutton(
            mode_options_column,  # Using the column frame
            text="Flash Descriptor Mode",
            variable=self.flash_descriptor_var,
            command=on_flash_checkbox_change
        )
        self.flash_checkbox.pack(side=tk.TOP, padx=10, pady=5,
                                 anchor="w")  # TOP for column layout, anchor west for left alignment

        self.window_key_checkbox = ttk.Checkbutton(
            mode_options_column,  # Using the column frame
            text="Window Key Mode",
            variable=self.window_key_var,
            command=on_window_key_checkbox_change
        )
        self.window_key_checkbox.pack(side=tk.TOP, padx=10, pady=5,
                                      anchor="w")  # TOP for column layout, anchor west for left alignment

        self.dell_8fc8_checkbox = ttk.Checkbutton(
            mode_options_column,  # Using the column frame
            text="Dell 8FC8",
            variable=self.dell_8fc8_var,
            command=on_dell_8fc8_checkbox_change
        )
        self.dell_8fc8_checkbox.pack(side=tk.TOP, padx=10, pady=5,
                                     anchor="w")  # TOP for column layout, anchor west for left alignment

        # The model selection list has been removed as requested
        self.selected_model = tk.StringVar(value="")  # Keep this for compatibility with existing code

        # Action button
        button_frame = ttk.Frame(self.action_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)

        # No need to create button style here - it will be managed by the theme system

        self.execute_button = ttk.Button(
            button_frame,
            text="Execute Action",
            command=self.execute_action,
            style="ExecuteBtn.TButton"
        )
        self.execute_button.pack(side=tk.TOP, padx=10, pady=5)

        # Right panel is now used for additional tools or information that may be needed
        # No need for duplicate status and info frames as they're shared in the common area below tabs

        # Initialize variables needed for tools functionality
        self.fd_filename_var = tk.StringVar()
        self.fd_offset_var = tk.StringVar(value="0")
        self.fd_size_var = tk.StringVar(value="4096")
        self.fd_model_var = tk.StringVar()
        self.wk_filename_var = tk.StringVar()
        self.wk_current_key_var = tk.StringVar()
        self.wk_new_key_var = tk.StringVar()

        # No Dell 8FC8 functionality

        # Helper function for better status updates with styles
        def update_status(text, status_type):
            """Update status label with text and appropriate style
            status_type can be: 'success', 'error', 'warning', 'info', or 'waiting'
            """
            style_map = {
                'success': 'Success.TLabel',
                'error': 'Danger.TLabel',
                'warning': 'Warning.TLabel',
                'info': 'Info.TLabel',
                'waiting': 'Waiting.TLabel'
            }
            # Use the appropriate style or default to normal if not found
            style = style_map.get(status_type.lower(), 'TLabel')
            self.status_label.config(text=text, style=style)

        # Attach the function to the instance
        self.update_status = update_status

        # Initialize database tab
        self.init_tab1()

        # Initialize user profile tab
        self.init_user_profile_tab()

        # Initialize the database
        self.create_local_db()

        # Show registration form if no user is registered
        self.check_and_show_registration()

        # Update model count display after initialization
        self.update_model_count()
        self.update_model_list()

        # Update status indicator after initialization
        self.update_connection_status()

        # Enable tab reordering with drag and drop (after all UI elements are initialized)
        self.enable_tab_reordering()

        # Add the theme toggle button at the very end of initialization
        # to ensure it appears on top of all other elements
        self.create_theme_toggle()

    def enable_tab_reordering(self):
        """Enable drag and drop functionality for tabs"""
        # Variables to track dragging state
        self._drag_tab = None
        self._drop_tab = None

        # Bind mouse events for tab dragging
        self.notebook.bind("<ButtonPress-1>", self._on_tab_press)
        self.notebook.bind("<B1-Motion>", self._on_tab_motion)
        self.notebook.bind("<ButtonRelease-1>", self._on_tab_release)

        # Log that tab reordering is enabled
        self.add_info("Tab reordering enabled - drag tabs to reorder")

    def _on_tab_press(self, event):
        """Handle mouse button press on tabs"""
        # Get clicked tab
        try:
            clicked_tab = self.notebook.identify(event.x, event.y)
            if "tab" in clicked_tab:  # Make sure we clicked on a tab
                self._drag_tab = self.notebook.index(f"@{event.x},{event.y}")
        except:
            # Not on a tab or error occurred
            self._drag_tab = None

    def _on_tab_motion(self, event):
        """Handle mouse motion while dragging a tab"""
        if self._drag_tab is not None:
            # Identify where the mouse is now
            try:
                position = self.notebook.index(f"@{event.x},{event.y}")
                # Store potential drop location
                self._drop_tab = position
                # Visual feedback could be added here
            except:
                pass

    def _on_tab_release(self, event):
        """Handle mouse release to complete tab drag and drop"""
        if self._drag_tab is not None and self._drop_tab is not None:
            if self._drag_tab != self._drop_tab:
                # Get tab name
                tab_name = self.notebook.tab(self._drag_tab, "text")
                # Move the tab to new position
                self._move_tab(self._drag_tab, self._drop_tab)
                # Log the action
                self.add_info(f"Moved tab '{tab_name}' to position {self._drop_tab + 1}")

        # Reset drag and drop variables
        self._drag_tab = None
        self._drop_tab = None

    def _move_tab(self, from_index, to_index):
        """Move a tab from one position to another using a more direct approach"""
        # Get all tabs and their info
        tabs = self.notebook.tabs()

        # We can't move beyond the number of tabs
        if to_index >= len(tabs):
            to_index = len(tabs) - 1

        # No need to move if source and destination are the same
        if from_index == to_index:
            return

        # Save the tab we're moving
        tab_widget = tabs[from_index]
        tab_text = self.notebook.tab(tab_widget, "text")

        # Remember all tab info for restoration
        tab_info = []
        for tab in tabs:
            if tab != tab_widget:  # Skip the one we're moving
                tab_info.append((tab, self.notebook.tab(tab, "text")))

        # Clear all tabs
        for tab in tabs:
            self.notebook.forget(tab)

        # Add tabs back in the new order
        inserted = False
        for i, (tab, text) in enumerate(tab_info):
            if (not inserted) and (i == to_index):
                # Insert the moved tab at this position
                self.notebook.add(tab_widget, text=tab_text)
                inserted = True

            # Add the original tab
            self.notebook.add(tab, text=text)

        # If we haven't inserted yet (moving to the end)
        if not inserted:
            self.notebook.add(tab_widget, text=tab_text)

        # Select the tab we moved
        self.notebook.select(tab_widget)

    def on_tab_changed(self, event):
        """Handle tab change events for improved user experience"""
        # Get the current selected tab
        selected_tab = self.notebook.select()
        tab_index = self.notebook.index(selected_tab)

        # Update status message to indicate active tab
        tab_names = ["Model Offsets Database", "Dell 8FC8 Unlocker", "Flash Descriptor Tool", "User Profile"]
        tab_name = self.notebook.tab(selected_tab, "text")  # Get actual tab name
        self.add_info(f"Switched to {tab_name} tab")

        # Refresh the content of the tab that is now visible (if needed)
        # Use the tab name instead of index for more reliability after reordering
        if "Model Offsets Database" in tab_name:
            self.update_model_list()
        elif "User Profile" in tab_name:
            self.load_user_profile()
        elif "Dell 8FC8 Unlocker" in tab_name:
            # Initialize Dell 8FC8 tab if not already initialized
            if not hasattr(self, 'dell_8fc8_tab_initialized'):
                self.init_dell_8fc8_tab()
                self.dell_8fc8_tab_initialized = True

        # Force update to ensure proper rendering
        self.root.update_idletasks()

    def setup_styles(self):
        """Configure styles with only light theme as requested"""
        style = ttk.Style()

        # Always use light theme - dark mode removed as requested
        self.current_theme = "classic"  # Use only classic/light theme as requested

        # Try to set a configurable theme as base
        try:
            style.theme_use('clam')  # A more configurable base theme
        except:
            pass  # Continue with default theme if 'clam' is not available

        # Define light theme colors - Dark theme has been removed as requested
        # Classic/Light theme colors - even lighter colors, minimal blue
        self.theme_colors = {
            'primary': "#FFFFFF",  # Pure white background
            'secondary': "#F9F9F9",  # Very light gray background
            'tertiary': "#F2F2F2",  # Slightly darker than secondary
            'accent': "#CCCCCC",  # Light gray instead of blue
            'accent_dark': "#AAAAAA",  # Darker gray for pressed states
            'accent_light': "#DDDDDD",  # Lighter gray for hover states
            'success': "#90EE90",  # Light green
            'warning': "#FFFFE0",  # Light yellow
            'danger': "#FFC0CB",  # Pink (lighter than red)
            'console_bg': "#F9F9F9",  # Very light gray console background
            'console_fg': "#2E8B57",  # Sea green for console text
            'text_primary': "#424242",  # Softer dark gray text (lighter than before)
            'text_secondary': "#757575",  # Medium gray text
            'text_disabled': "#BDBDBD",  # Light gray for disabled text
            'border': "#E0E0E0",  # Very light border color
            'selection_bg': "#F0F0F0",  # Very light gray selection background
            'input_bg': "#FFFFFF",  # White background for input fields
            'hover_bg': "#F5F5F5",  # Light hover background color
            'button_bg': "#F0F0F0",  # Light button background (lighter)
            'button_hover': "#E0E0E0",  # Button hover state (lighter)
            'name': "Light"  # Theme name for display
        }

        # Light theme is already set as default theme

        # Method to apply the current theme
        self.apply_theme(style)

    def create_theme_toggle(self):
        """Theme toggle functionality removed as requested - only light theme used"""
        # Set console colors from theme
        self.console_bg = self.theme_colors['console_bg']
        self.console_fg = self.theme_colors['console_fg']

        # Update any console / text widgets with the theme colors
        if hasattr(self, 'info_text'):
            self.info_text.config(bg=self.console_bg, fg=self.console_fg)
        if hasattr(self, 'log_text'):
            self.log_text.config(bg=self.console_bg, fg=self.console_fg)

        # Update models canvas background if it exists
        if hasattr(self, 'models_canvas'):
            self.models_canvas.config(bg=self.theme_colors['secondary'])

    def toggle_theme(self):
        """Theme toggle removed - only light theme is available as requested"""
        pass

    def apply_theme(self, style=None):
        """Apply the current theme to all widgets"""
        if style is None:
            style = ttk.Style()

        # Get the current theme colors for reference
        tc = self.theme_colors

        # Configure root window with theme background
        self.root.configure(background=tc['primary'])

        # Configure default style settings
        style.configure(".",
                        font=("Segoe UI", 10),  # More modern font
                        background=tc['primary'],
                        foreground=tc['text_primary'],
                        troughcolor=tc['tertiary'],
                        focuscolor=tc['accent'],
                        selectbackground=tc['selection_bg'],
                        selectforeground=tc['text_primary'])

        # Apply the theme to all standard widgets

        # Notebook (tabs) appearance
        style.configure("TNotebook",
                        background=tc['primary'],
                        borderwidth=0)

        # Tab styling
        style.configure("TNotebook.Tab",
                        padding=[16, 8],
                        font=("Segoe UI", 10),
                        background=tc['secondary'],
                        foreground=tc['text_secondary'],
                        borderwidth=0,
                        relief="flat")

        # Tab state mapping
        style.map("TNotebook.Tab",
                  background=[
                      ("selected", tc['accent']),
                      ("active", tc['tertiary'])
                  ],
                  foreground=[
                      ("selected", tc['text_primary']),
                      ("active", tc['text_primary'])
                  ],
                  expand=[("selected", [1, 1, 1, 0])],
                  padding=[("selected", [18, 10])]
                  )

        # Frames
        style.configure("TFrame", background=tc['primary'])
        style.configure("Secondary.TFrame", background=tc['secondary'])
        style.configure("Tertiary.TFrame", background=tc['tertiary'])

        # LabelFrame styling - light theme only
        style.configure("TLabelframe",
                        background=tc['secondary'],
                        bordercolor=tc['border'],  # Lighter border color for light theme
                        borderwidth=1,
                        relief="solid")
        style.configure("TLabelframe.Label",
                        font=("Segoe UI", 10),  # Normal font, not bold
                        background=tc['primary'],
                        foreground=tc['text_primary'])  # Darker text for better readability

        # Special style for info frame - no background color
        style.configure("Info.TLabelframe",
                        background=tc['secondary'],
                        bordercolor=tc['border'],  # Use regular border color
                        borderwidth=1,
                        relief="solid")
        style.configure("Info.TLabelframe.Label",
                        font=("Segoe UI", 10),  # Normal font, not bold
                        background=tc['primary'],  # No background color
                        foreground=tc['text_primary'])  # Regular text color

        # Button styling - light theme only
        style.configure("TButton",
                        padding=8,
                        font=("Segoe UI", 10),  # Normal font, not bold
                        relief="flat",
                        background=tc['button_bg'],
                        foreground=tc['text_primary'],
                        borderwidth=1,
                        bordercolor=tc['border'])
        style.map("TButton",
                  background=[("pressed", tc['tertiary']), ("active", tc['button_hover'])],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # Accent button - transparent for theme toggle in dark mode
        style.configure("Accent.TButton",
                        background=tc['primary'],  # Use primary color for transparency
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat",
                        borderwidth=0)
        style.map("Accent.TButton",
                  background=[("pressed", tc['primary']), ("active", tc['primary'])],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # Labels
        style.configure("TLabel",
                        background=tc['primary'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10))

        # Header label
        style.configure("Header.TLabel",
                        font=("Segoe UI", 14),  # Removed bold
                        background=tc['primary'],
                        foreground=tc['text_primary'])  # Changed color to regular text

        # Subheader label
        style.configure("Subheader.TLabel",
                        font=("Segoe UI", 12),  # Removed bold
                        background=tc['primary'],
                        foreground=tc['text_primary'])

        # Entry fields
        style.configure("TEntry",
                        padding=8,
                        fieldbackground=tc['input_bg'],
                        foreground=tc['text_primary'],
                        insertcolor=tc['text_primary'],
                        bordercolor=tc['border'],
                        lightcolor=tc['border'],
                        darkcolor=tc['border'],
                        relief="flat")

        # Combobox
        style.configure("TCombobox",
                        padding=8,
                        fieldbackground=tc['input_bg'],
                        background=tc['input_bg'],
                        foreground=tc['text_primary'],
                        arrowcolor=tc['text_primary'],
                        bordercolor=tc['border'],
                        relief="flat")
        style.map("TCombobox",
                  fieldbackground=[("readonly", tc['input_bg'])],
                  background=[("readonly", tc['input_bg'])],
                  foreground=[("readonly", tc['text_primary'])])

        # Spinbox
        style.configure("TSpinbox",
                        padding=8,
                        fieldbackground=tc['input_bg'],
                        background=tc['input_bg'],
                        foreground=tc['text_primary'],
                        arrowcolor=tc['text_primary'],
                        bordercolor=tc['border'],
                        relief="flat")

        # Checkbutton
        style.configure("TCheckbutton",
                        background=tc['primary'],
                        foreground=tc['text_primary'],
                        focuscolor=tc['accent'])

        # Radiobutton
        style.configure("TRadiobutton",
                        background=tc['primary'],
                        foreground=tc['text_primary'],
                        focuscolor=tc['accent'])

        # Treeview
        style.configure("Treeview",
                        background=tc['secondary'],
                        fieldbackground=tc['secondary'],
                        foreground=tc['text_primary'],
                        bordercolor=tc['border'])
        style.map("Treeview",
                  background=[("selected", tc['selection_bg'])],
                  foreground=[("selected", tc['text_primary'])])

        # Treeview headings
        style.configure("Treeview.Heading",
                        background=tc['tertiary'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", tc['hover_bg'])])

        # Scrollbar
        style.configure("TScrollbar",
                        background=tc['secondary'],
                        troughcolor=tc['primary'],
                        bordercolor=tc['primary'],
                        arrowcolor=tc['text_primary'],
                        relief="flat",
                        arrowsize=20,
                        width=16)
        style.map("TScrollbar",
                  background=[("active", tc['tertiary']), ("pressed", tc['accent'])])

        # Progress bar
        style.configure("TProgressbar",
                        background=tc['accent'],
                        troughcolor=tc['tertiary'],
                        bordercolor=tc['primary'],
                        lightcolor=tc['primary'],
                        darkcolor=tc['primary'])

        # Status indicators - removed background colors, text-only colors
        style.configure("Success.TLabel",
                        foreground="#28A745",  # Green text
                        background=tc['primary'],  # Use theme background
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")

        style.configure("Warning.TLabel",
                        foreground="#FFC107",  # Yellow/amber text
                        background=tc['primary'],  # Use theme background
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")

        style.configure("Danger.TLabel",
                        foreground="#DC3545",  # Red text
                        background=tc['primary'],  # Use theme background
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")

        style.configure("Info.TLabel",
                        foreground="#0D6EFD",  # Blue text
                        background=tc['primary'],  # Use theme background
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")

        style.configure("Waiting.TLabel",
                        foreground="#6C757D",  # Gray text
                        background=tc['primary'],  # Use theme background
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")

        # Action button variants
        style.configure("Success.TButton",
                        background=tc['success'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Success.TButton",
                  background=[("pressed", "#1A9E4B"), ("active", "#28D068")],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        style.configure("Warning.TButton",
                        background=tc['warning'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Warning.TButton",
                  background=[("pressed", "#D18409"), ("active", "#F7B53B")],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        style.configure("Danger.TButton",
                        background=tc['danger'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Danger.TButton",
                  background=[("pressed", "#C72B35"), ("active", "#FF5A65")],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # Task progress
        style.configure("TaskProgress.Horizontal.TProgressbar",
                        thickness=20,
                        background=tc['accent'],
                        troughcolor=tc['tertiary'],
                        borderwidth=0)

        # Execute button
        style.configure("ExecuteBtn.TButton",
                        background=tc['accent'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 11, "bold"),
                        relief="flat",
                        borderwidth=0)
        style.map("ExecuteBtn.TButton",
                  background=[("pressed", tc['accent_dark']), ("active", tc['accent_light'])],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # ActionButton
        style.configure("ActionButton.TButton",
                        background=tc['tertiary'],
                        foreground=tc['text_primary'],
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        relief="flat")
        style.map("ActionButton.TButton",
                  background=[("pressed", tc['accent_dark']), ("active", tc['hover_bg'])],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # Special light theme toggle button style - transparent background (still needed for compatibility)
        style.configure("LightThemeToggle.TButton",
                        background=tc['primary'],  # Use the theme primary color for transparency
                        foreground=tc['text_primary'],  # Use theme text color
                        font=("Segoe UI", 10, "bold"),
                        relief="flat",
                        borderwidth=0)
        style.map("LightThemeToggle.TButton",
                  background=[("pressed", tc['primary']), ("active", tc['primary'])],
                  foreground=[("pressed", tc['text_primary']), ("active", tc['text_primary'])])

        # Text colored buttons
        style.configure("GreenText.TButton",
                        foreground=tc['success'],
                        background=tc['tertiary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("GreenText.TButton",
                  foreground=[("active", "#28D068")],
                  background=[("active", tc['hover_bg'])])

        style.configure("RedText.TButton",
                        foreground=tc['danger'],
                        background=tc['tertiary'],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("RedText.TButton",
                  foreground=[("active", "#FF5A65")],
                  background=[("active", tc['hover_bg'])])

        # Section headers
        style.configure("Section.TLabel",
                        font=("Segoe UI", 12),  # Removed bold
                        foreground=tc['text_primary'],  # Changed to regular text color
                        background=tc['primary'])

        style.configure("Title.TLabel",
                        font=("Segoe UI", 16),  # Removed bold
                        foreground=tc['text_primary'],  # Changed to regular text color
                        background=tc['primary'])

        style.configure("Subtitle.TLabel",
                        font=("Segoe UI", 11),  # Removed bold
                        foreground=tc['text_secondary'],
                        background=tc['primary'])

        # Scrolled text
        self.scrolled_text_config = {
            "bg": tc['console_bg'],
            "fg": tc['console_fg'],
            "insertbackground": tc['console_fg'],
            "selectbackground": tc['selection_bg'],
            "selectforeground": tc['text_primary'],
            "font": ("Consolas", 9),
            "borderwidth": 0,
            "padx": 5,
            "pady": 5
        }

        # Store console colors for later use
        self.console_bg = tc['console_bg']
        self.console_fg = tc['console_fg']

    # ---------- Tab 3: User Profile Tab ----------
    def init_user_profile_tab(self):
        """Initialize the User Profile tab with user data from database"""
        main_frame = ttk.Frame(self.tab3, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="User Profile", font=("Arial", 16))  # Removed bold
        title_label.pack(pady=(0, 20))

        # Create a frame for user information with the info style
        info_frame = ttk.LabelFrame(main_frame, text="User Information", style="Info.TLabelframe")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Create a table-like view using a Frame and Grid layout
        table_frame = ttk.Frame(info_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define column headings to match the reference image exactly
        headings = ["S/n", "Full Name", "Mobile Number", "City", "Mac Address", "Registration Date", "User Type",
                    "Action"]

        # Configure style for the table cells - adapting to theme
        style = ttk.Style()
        # Set header style based on current theme
        if self.current_theme == "classic":  # Light theme
            style.configure("TableHeader.TLabel",
                            font=("Arial", 10),  # Removed bold
                            background="#CCCCCC",  # Light gray (matching accent color)
                            foreground="#424242",  # Dark gray text for better contrast
                            padding=8,
                            relief="flat",
                            borderwidth=1)
            style.configure("TableCell.TLabel",
                            font=("Arial", 10),
                            background="white",
                            padding=8,
                            relief="solid",
                            borderwidth=1,
                            bordercolor="#DEE2E6")  # Light border color
        else:  # Dark theme
            style.configure("TableHeader.TLabel",
                            font=("Arial", 10, "bold"),
                            background="#4B9CD3",  # Matching accent color from dark theme
                            foreground="#FAFAFA",  # Off-white text (matching text_primary)
                            padding=8,
                            relief="flat",
                            borderwidth=1)
            style.configure("TableCell.TLabel",
                            font=("Arial", 10),
                            background="#252526",  # Matching secondary color
                            foreground="#D4D4D4",  # Light gray text (matching text_secondary)
                            padding=8,
                            relief="solid",
                            borderwidth=1,
                            bordercolor="#444444")  # Matching border color

        # Create table header row
        for col, heading in enumerate(headings):
            header_label = ttk.Label(table_frame, text=heading, style="TableHeader.TLabel")
            header_label.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)
            # Configure column width appropriately
            if heading == "S/n":
                table_frame.columnconfigure(col, weight=1)
            elif heading in ["Full Name", "Registration Date"]:
                table_frame.columnconfigure(col, weight=4)
            elif heading == "Mobile Number":
                table_frame.columnconfigure(col, weight=3)
            else:
                table_frame.columnconfigure(col, weight=2)

        # Create empty rows for data (20 rows like in the image)
        self.user_rows = []
        for row in range(1, 21):  # 20 rows
            row_data = []
            for col, heading in enumerate(headings):
                cell = ttk.Label(table_frame, text="", style="TableCell.TLabel")
                cell.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
                row_data.append(cell)
            self.user_rows.append(row_data)

            # Configure all rows to have equal height
            table_frame.rowconfigure(row, weight=1)

        # Add a refresh button
        refresh_frame = ttk.Frame(main_frame)
        refresh_frame.pack(pady=20)
        ttk.Button(refresh_frame, text="Refresh Profile", command=self.load_user_profile).pack()

        # Note: Button styles already defined in setup_styles method

        # Load user profile data when tab is created
        self.load_user_profile()

    # ---------- User Profile Tab Functionality ----------

    def init_task_scheduler_tab(self):
        """Task Scheduler removed as requested"""
        # This is now an empty stub function since the Task Scheduler tab was removed
        pass

    def populate_sample_tasks(self):
        """Task Scheduler removed as requested"""
        pass

    def on_task_select(self, event):
        """Task Scheduler removed as requested"""
        pass

    def schedule_new_task(self):
        """Task Scheduler removed as requested"""
        pass

    def clear_scheduler_form(self):
        """Task Scheduler removed as requested"""
        pass

    def run_selected_task(self):
        """Task Scheduler removed as requested"""
        pass

    def delete_scheduled_task(self):
        """Task Scheduler removed as requested"""
        pass

    def toggle_task_status(self):
        """Task Scheduler removed as requested"""
        pass

    def check_and_show_registration(self):
        """Check if any user is registered, and show registration form if not"""
        # Check if registration is already shown or skipped
        if self.registration_form_active or self.registration_skipped or self.user_registered:
            return

        # Check if a user is already registered
        conn = get_db_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()

                # Determine the type of database
                is_sqlite = 'sqlite3.Connection' in str(type(conn))

                if is_sqlite:
                    cursor.execute("SELECT COUNT(*) FROM app_users")
                else:
                    cursor.execute("SELECT COUNT(*) FROM app_users")

                result = cursor.fetchone()
                if result and len(result) > 0:
                    count = result[0]

                    if count > 0:
                        # User exists, mark as registered
                        self.user_registered = True
                        return

            except Exception as e:
                self.add_info(f"Error checking registration: {str(e)}")
                # Continue to show registration form if there's an error
            finally:
                if cursor:
                    if hasattr(cursor, 'close'):
                        cursor.close()
                conn.close()

        # If we reach here, show the registration form
        self.show_registration_form()

    def show_registration_form(self):
        """Display a registration form as a modal dialog"""
        self.registration_form_active = True

        # Create a modal dialog window
        self.reg_window = tk.Toplevel(self.root)
        self.reg_window.title("User Registration")
        self.reg_window.grab_set()  # Make window modal
        self.reg_window.focus_set()

        # Set window size and position it in the center
        window_width = 500
        window_height = 400
        screen_width = self.reg_window.winfo_screenwidth()
        screen_height = self.reg_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.reg_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.reg_window.resizable(False, False)

        # Main frame
        main_frame = ttk.Frame(self.reg_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="User Registration", font=("Arial", 16))
        title_label.pack(pady=(0, 20))

        # Registration form
        form_frame = ttk.LabelFrame(main_frame, text="Registration Form", style="Info.TLabelframe")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Form fields
        form_fields = ttk.Frame(form_frame)
        form_fields.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Name field
        ttk.Label(form_fields, text="Full Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.reg_name_var = tk.StringVar()
        ttk.Entry(form_fields, textvariable=self.reg_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5,
                                                                              pady=5)

        # Mobile field
        ttk.Label(form_fields, text="Mobile Number:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.reg_mobile_var = tk.StringVar()
        ttk.Entry(form_fields, textvariable=self.reg_mobile_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5,
                                                                                pady=5)

        # City field
        ttk.Label(form_fields, text="City:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.reg_city_var = tk.StringVar()
        ttk.Entry(form_fields, textvariable=self.reg_city_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5,
                                                                              pady=5)

        # User type field
        ttk.Label(form_fields, text="User Type:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.reg_user_type_var = tk.StringVar(value="Regular")
        user_type_combo = ttk.Combobox(form_fields, textvariable=self.reg_user_type_var, values=["Regular", "Admin"],
                                       width=28, state="readonly")
        user_type_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # MAC Address info (get automatically)
        mac_address = get_mac_address()
        ttk.Label(form_fields, text="MAC Address:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_fields, text=mac_address or "Unknown").grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Register button
        register_btn = ttk.Button(button_frame, text="Register", command=self.register_user, style="TButton")
        register_btn.pack(side=tk.LEFT, padx=10)

        # Skip button
        skip_btn = ttk.Button(button_frame, text="Skip Registration", command=self.skip_registration, style="TButton")
        skip_btn.pack(side=tk.RIGHT, padx=10)

        # Handle window close event
        self.reg_window.protocol("WM_DELETE_WINDOW", self.skip_registration)

    def register_user(self):
        """Register a new user and close the form"""
        # Get form values
        name = self.reg_name_var.get().strip()
        mobile = self.reg_mobile_var.get().strip()
        city = self.reg_city_var.get().strip()
        user_type = self.reg_user_type_var.get()
        mac_address = get_mac_address() or "Unknown"

        # Validate form - name is required
        if not name:
            messagebox.showwarning("Warning", "Please enter your name to register", parent=self.reg_window)
            return

        # Save user to database
        conn = get_db_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()

                # Check if the status field exists
                is_sqlite = 'sqlite3.Connection' in str(type(conn))

                if is_sqlite:
                    cursor.execute("PRAGMA table_info(app_users)")
                    columns = [col[1].lower() for col in cursor.fetchall()]
                else:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'app_users'
                    """)
                    columns = [col[0].lower() for col in cursor.fetchall()]

                # Add status field if it doesn't exist
                has_status = 'status' in columns
                if not has_status:
                    if is_sqlite:
                        cursor.execute("ALTER TABLE app_users ADD COLUMN status TEXT DEFAULT 'Enabled'")
                    else:
                        cursor.execute("ALTER TABLE app_users ADD COLUMN status VARCHAR(20) DEFAULT 'Enabled'")

                # Insert user data
                import datetime
                reg_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if is_sqlite:
                    cursor.execute("""
                        INSERT INTO app_users (full_name, mobile_number, city, mac_address, registration_date, user_type, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, mobile, city, mac_address, reg_date, user_type, 'Enabled'))
                else:
                    cursor.execute("""
                        INSERT INTO app_users (full_name, mobile_number, city, mac_address, registration_date, user_type, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (name, mobile, city, mac_address, reg_date, user_type, 'Enabled'))

                conn.commit()
                self.user_registered = True
                self.add_info(f"User {name} registered successfully")

                # Refresh user profile display
                self.load_user_profile()

            except Exception as e:
                self.add_info(f"Error registering user: {str(e)}")
                messagebox.showerror("Registration Error", f"Could not register user: {str(e)}", parent=self.reg_window)
            finally:
                if cursor:
                    if hasattr(cursor, 'close'):
                        cursor.close()
                conn.close()

        # Close the registration form
        self.close_registration_form()

    def skip_registration(self):
        """Skip registration and close the form"""
        self.registration_skipped = True
        self.close_registration_form()
        self.add_info("Registration skipped - you can register later in User Profile tab")

    def close_registration_form(self):
        """Close the registration form window"""
        if hasattr(self, 'reg_window') and self.reg_window:
            self.reg_window.grab_release()
            self.reg_window.destroy()
        self.registration_form_active = False

    def toggle_user_status(self, user_id, button, row_index):
        """Toggle the user status between Enabled and Disabled"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()

                # First check the current status
                status_text = button.cget("text")

                # Toggle button text and row color
                if status_text == "Enable":
                    # Changing from "Enable" to "Disable" (user is being activated)
                    new_status = "Disable"
                    # Theme-dependent row color for active status
                    if self.current_theme == "classic":  # Light theme
                        row_color = "#E8F5E9"  # Very light green for light theme
                    else:  # Dark theme
                        row_color = "#1B5E20"  # Dark green for dark theme
                    button.config(text=new_status, style="RedText.TButton")
                    status_value = "active"
                else:
                    # Changing from "Disable" to "Enable" (user is being deactivated)
                    new_status = "Enable"
                    # Theme-dependent row color for inactive status
                    if self.current_theme == "classic":  # Light theme
                        row_color = "#FFEBEE"  # Very light red for light theme
                    else:  # Dark theme
                        row_color = "#4A2833"  # Dark red for dark theme
                    button.config(text=new_status, style="GreenText.TButton")
                    status_value = "inactive"

                # Update the row color based on status
                for col in range(len(self.user_rows[row_index])):
                    if col != 7:  # Skip the action button
                        self.user_rows[row_index][col].config(background=row_color)

                # Get MAC address to identify user (we're using row index to get the MAC address from the table)
                mac_address = self.user_rows[row_index][4].cget("text")

                # Determine if we're using SQLite or PostgreSQL
                is_sqlite = 'sqlite3.Connection' in str(type(conn))

                # Use the correct placeholder style depending on database type
                placeholder = '?' if is_sqlite else '%s'

                # Get all column names first
                if is_sqlite:
                    cursor.execute("PRAGMA table_info(app_users)")
                    columns = cursor.fetchall()
                    column_names = [column[1] for column in
                                    columns]  # Column name is at index 1 in SQLite PRAGMA result
                else:
                    # For PostgreSQL
                    cursor.execute(
                        "SELECT column_name FROM information_schema.columns WHERE table_name='app_users' ORDER BY ordinal_position")
                    columns = cursor.fetchall()
                    column_names = [column[0] for column in columns]

                print(f"Column names in toggle_user_status: {column_names}")

                # Check if status column exists using case-insensitive matching
                has_status_column = False
                for col_name in column_names:
                    if col_name.lower() == 'status':
                        has_status_column = True
                        break

                # Add status column if it doesn't exist
                if not has_status_column:
                    print(f"Status column not found, adding it. Current columns: {column_names}")
                    if is_sqlite:
                        cursor.execute("ALTER TABLE app_users ADD COLUMN status TEXT DEFAULT 'active'")
                    else:
                        cursor.execute("ALTER TABLE app_users ADD COLUMN status TEXT DEFAULT 'active'")

                    # Refresh column list after adding the status column
                    if is_sqlite:
                        cursor.execute("PRAGMA table_info(app_users)")
                        columns = cursor.fetchall()
                        column_names = [column[1] for column in columns]
                    else:
                        cursor.execute(
                            "SELECT column_name FROM information_schema.columns WHERE table_name='app_users' ORDER BY ordinal_position")
                        columns = cursor.fetchall()
                        column_names = [column[0] for column in columns]

                    print(f"After adding status column, columns are: {column_names}")

                # Update the status in the database
                # Both SQLite and PostgreSQL use the same column name for status
                update_query = f"UPDATE app_users SET status = {placeholder} WHERE mac_address = {placeholder}"
                cursor.execute(update_query, (status_value, mac_address))
                conn.commit()

                cursor.close()
                conn.close()

                # Update status message - "Enabled" or "Disabled"
                status_msg = "enabled" if new_status == "Disable" else "disabled"
                self.update_status(f"User {mac_address} status changed to {status_msg}", "success")
            else:
                messagebox.showerror("Database Error", "Could not connect to database to update user status")
        except Exception as e:
            self.update_status(f"Error changing user status: {str(e)}", "error")
            messagebox.showerror("Error", f"Could not change user status: {str(e)}")

    def change_user_type(self, user_id, combobox, row_index):
        """Change user type when dropdown selection changes"""
        try:
            new_type = combobox.get()
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()

                # Get MAC address to identify user (we're using row index to get the MAC address from the table)
                mac_address = self.user_rows[row_index][4].cget("text")

                # Debug information
                print(f"Database connection type: {type(conn)}")
                print(f"Changing user type to: {new_type} for MAC: {mac_address}")

                # Determine if we're using SQLite or PostgreSQL
                is_sqlite = 'sqlite3.Connection' in str(type(conn))

                # Use the correct placeholder style depending on database type
                placeholder = '?' if is_sqlite else '%s'

                # Get all column names first for dynamic column handling
                if is_sqlite:
                    cursor.execute("PRAGMA table_info(app_users)")
                    columns = cursor.fetchall()
                    column_names = [column[1] for column in
                                    columns]  # Column name is at index 1 in SQLite PRAGMA result
                else:
                    # For PostgreSQL
                    cursor.execute(
                        "SELECT column_name FROM information_schema.columns WHERE table_name='app_users' ORDER BY ordinal_position")
                    columns = cursor.fetchall()
                    column_names = [column[0] for column in columns]

                print(f"Column names in change_user_type: {column_names}")

                # Check if user_type column exists using case-insensitive matching
                has_user_type_column = False
                for col_name in column_names:
                    if col_name.lower() == 'user_type':
                        has_user_type_column = True
                        break

                if not has_user_type_column:
                    print(f"Error: user_type column not found in database. Found columns: {column_names}")
                    messagebox.showerror("Database Error", "User type column not found in database")
                    cursor.close()
                    conn.close()
                    return

                # Update the user type in the database
                try:
                    table_name = "app_users"
                    update_query = f"UPDATE {table_name} SET user_type = {placeholder} WHERE mac_address = {placeholder}"
                    print(f"Executing query: {update_query} with values ({new_type}, {mac_address})")
                    cursor.execute(update_query, (new_type, mac_address))
                    conn.commit()
                except Exception as sql_error:
                    print(f"SQL Error updating user type: {sql_error}")
                    messagebox.showerror("Database Error", f"Could not update user type: {sql_error}")
                    cursor.close()
                    conn.close()
                    return
                cursor.close()
                conn.close()

                self.update_status(f"User {mac_address} type changed to {new_type}", "success")
            else:
                messagebox.showerror("Database Error", "Could not connect to database to update user type")
        except Exception as e:
            self.update_status(f"Error changing user type: {str(e)}", "error")
            messagebox.showerror("Error", f"Could not change user type: {str(e)}")

    def load_user_profile(self):
        """Load and display all users from the database"""
        # Clear all rows first and remove any existing buttons/comboboxes
        for row in self.user_rows:
            for col, cell in enumerate(row):
                if col == 6:  # User Type column
                    # If a combobox was placed here, destroy it
                    for widget in cell.master.winfo_children():
                        if isinstance(widget, ttk.Combobox) and widget.grid_info()['row'] == cell.grid_info()['row'] and \
                                widget.grid_info()['column'] == 6:
                            widget.destroy()
                elif col == 7:  # Action column
                    # If a button was placed here, destroy it
                    for widget in cell.master.winfo_children():
                        if isinstance(widget, ttk.Button) and widget.grid_info()['row'] == cell.grid_info()['row'] and \
                                widget.grid_info()['column'] == 7:
                            widget.destroy()
                # Reset all cell texts with theme-appropriate background
                if self.current_theme == "classic":
                    cell.config(text="", background="white")
                else:
                    cell.config(text="", background="#252526", foreground="#FFFFFF")

        conn = get_db_connection()
        current_mac_address = get_mac_address()

        if conn:
            try:
                cursor = conn.cursor()

                # Check if status column exists
                # Determine if we're using SQLite or PostgreSQL
                is_sqlite = 'sqlite3.Connection' in str(type(conn))

                if is_sqlite:
                    cursor.execute("PRAGMA table_info(app_users)")
                    columns = [col[1].lower() for col in
                               cursor.fetchall()]  # Convert to lowercase for case-insensitive matching
                    has_status_column = 'status' in columns
                else:
                    # For PostgreSQL, check if status column exists - more flexible with case
                    cursor.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='app_users' AND LOWER(column_name)='status'
                        """)
                    has_status_column = cursor.fetchone() is not None

                # Get all column names first
                if is_sqlite:
                    cursor.execute("PRAGMA table_info(app_users)")
                    columns = cursor.fetchall()
                    column_names = [column[1] for column in
                                    columns]  # Column name is at index 1 in SQLite PRAGMA result
                    date_column_name = "registration_date"
                else:
                    # For PostgreSQL
                    cursor.execute(
                        "SELECT column_name FROM information_schema.columns WHERE table_name='app_users' ORDER BY ordinal_position")
                    columns = cursor.fetchall()
                    column_names = [column[0] for column in columns]
                    date_column_name = "created_at"

                # Find column indexes for key fields
                # Handle column name differences between SQLite and PostgreSQL
                try:
                    username_idx = column_names.index('username')
                    mobile_idx = column_names.index('mobile')
                    city_idx = column_names.index('city')
                    user_type_idx = column_names.index('user_type')
                    mac_idx = column_names.index('mac_address')
                    date_idx = column_names.index(date_column_name)
                    # Find status index using case-insensitive matching
                    status_idx = -1
                    for i, col_name in enumerate(column_names):
                        if col_name.lower() == 'status':
                            status_idx = i
                            break
                    print(f"Column indexes: username={username_idx}, mobile={mobile_idx}, city={city_idx}, " +
                          f"user_type={user_type_idx}, mac={mac_idx}, date={date_idx}, status={status_idx}")
                except ValueError as e:
                    print(f"Error finding column indexes: {e}")
                    # Set default indexes as fallback (this ensures the code still works)
                    username_idx, mobile_idx, city_idx, user_type_idx, mac_idx, date_idx, status_idx = 0, 1, 2, 3, 4, 5, 6

                # Query to fetch all users
                columns_str = '*'  # Select all columns, we'll use the indexes to access what we need

                # Order by date column (either registration_date or created_at)
                order_by = f"ORDER BY {date_column_name} DESC"

                # Build and execute query
                select_query = f"SELECT {columns_str} FROM app_users {order_by}"
                print(f"Executing query: {select_query}")
                cursor.execute(select_query)
                all_users = cursor.fetchall()
                print(f"Found {len(all_users)} users")

                if all_users:
                    # Display users in the table, row by row
                    for i, user in enumerate(all_users):
                        if i < len(self.user_rows):  # Make sure we don't go beyond our created rows
                            # Apply row coloring based on status if available
                            if status_idx >= 0 and len(user) > status_idx:
                                status = user[status_idx]
                                if status == 'active':
                                    # Theme-dependent row color for active users
                                    if self.current_theme == "classic":  # Light theme
                                        row_color = "#E8F5E9"  # Very light green for light theme
                                    else:  # Dark theme
                                        row_color = "#1B5E20"  # Dark green for dark theme
                                elif status == 'inactive':
                                    # Theme-dependent row color for inactive users
                                    if self.current_theme == "classic":  # Light theme
                                        row_color = "#FFEBEE"  # Very light red for light theme
                                    else:  # Dark theme
                                        row_color = "#4A2833"  # Dark red for dark theme
                                else:
                                    # Default color based on theme
                                    if self.current_theme == "classic":
                                        row_color = "white"  # White for light theme
                                    else:
                                        row_color = "#252526"  # Dark background for dark theme
                            else:
                                # Fallback to default behavior if status not available
                                if i == 0:
                                    # Theme-dependent row color for first row (active user)
                                    if self.current_theme == "classic":  # Light theme
                                        row_color = "#E8F5E9"  # Very light green for light theme
                                    else:  # Dark theme
                                        row_color = "#1B5E20"  # Dark green for dark theme
                                elif i == 1:
                                    # Theme-dependent row color for second row (inactive user)
                                    if self.current_theme == "classic":  # Light theme
                                        row_color = "#FFEBEE"  # Very light red for light theme
                                    else:  # Dark theme
                                        row_color = "#4A2833"  # Dark red for dark theme
                                else:
                                    # Default color based on theme
                                    if self.current_theme == "classic":
                                        row_color = "white"  # White for light theme
                                    else:
                                        row_color = "#252526"  # Dark background for dark theme

                            # S/n (Serial Number)
                            self.user_rows[i][0].config(text=str(i + 1), background=row_color)

                            # Name - use username_idx to get correct value
                            self.user_rows[i][1].config(
                                text=user[username_idx] if len(user) > username_idx and user[username_idx] else "",
                                background=row_color)

                            # Mobile - use mobile_idx to get correct value
                            self.user_rows[i][2].config(
                                text=user[mobile_idx] if len(user) > mobile_idx and user[mobile_idx] else "",
                                background=row_color)

                            # City - use city_idx to get correct value
                            self.user_rows[i][3].config(
                                text=user[city_idx] if len(user) > city_idx and user[city_idx] else "",
                                background=row_color)

                            # Mac Address - use mac_idx to get correct value
                            mac = user[mac_idx] if len(user) > mac_idx and user[mac_idx] else "Unknown"
                            self.user_rows[i][4].config(text=mac, background=row_color)

                            # Format date - use date_idx to get correct value
                            reg_date = user[date_idx] if len(user) > date_idx and user[date_idx] else "Unknown"
                            if isinstance(reg_date, str):
                                # Already a string, use as is
                                formatted_date = reg_date
                            else:
                                # Format datetime object
                                try:
                                    formatted_date = reg_date.strftime('%d.%m.%y')  # Short date format like in image
                                except:
                                    formatted_date = str(reg_date)

                            self.user_rows[i][5].config(text=formatted_date, background=row_color)

                            # User Type - use user_type_idx to get correct value
                            user_type = user[user_type_idx] if len(user) > user_type_idx and user[
                                user_type_idx] else "user"

                            # Remove the label and replace with combobox
                            self.user_rows[i][6].config(text="")
                            user_type_combo = ttk.Combobox(self.user_rows[i][6].master, values=["user", "admin"],
                                                           state="readonly", width=10)
                            user_type_combo.set(user_type)
                            user_type_combo.grid(row=i + 1, column=6, sticky="nsew", padx=0, pady=0)
                            user_type_combo.bind("<<ComboboxSelected>>",
                                                 lambda event, user_id=i + 1, combo=user_type_combo,
                                                        row=i: self.change_user_type(user_id, combo, row))

                            # Action button (position 7)
                            self.user_rows[i][7].config(text="")
                            # Set button text and color based on status
                            # We need to check both light and dark theme colors for active state
                            if status_idx >= 0 and len(user) > status_idx:
                                status = user[status_idx]
                                if status == 'active':
                                    action_text = "Disable"
                                    button_style = "RedText.TButton"  # Red text for Disable action
                                else:
                                    action_text = "Enable"
                                    button_style = "GreenText.TButton"  # Green text for Enable action
                            else:
                                # Fallback based on row index if status is not available
                                if i == 0:  # First row is typically active
                                    action_text = "Disable"
                                    button_style = "RedText.TButton"
                                else:
                                    action_text = "Enable"
                                    button_style = "GreenText.TButton"

                            action_btn = ttk.Button(
                                self.user_rows[i][7].master,
                                text=action_text,
                                style=button_style,
                                command=lambda user_id=i + 1, btn=None, row=i: self.toggle_user_status(user_id, btn,
                                                                                                       row)
                            )
                            action_btn.grid(row=i + 1, column=7, sticky="nsew", padx=0, pady=0)
                            # Update the command after the button is created to reference itself
                            action_btn.config(
                                command=lambda user_id=i + 1, btn=action_btn, row=i: self.toggle_user_status(user_id,
                                                                                                             btn, row)
                            )

                else:
                    # No users found in database
                    self.user_rows[0][0].config(text="1")
                    self.user_rows[0][1].config(text="No users found in database")
                    self.user_rows[0][4].config(text=current_mac_address)  # MAC Address

                    # Add a dummy dropdown and button
                    user_type_combo = ttk.Combobox(self.user_rows[0][6].master, values=["user", "admin"],
                                                   state="readonly", width=10)
                    user_type_combo.set("user")
                    user_type_combo.grid(row=1, column=6, sticky="nsew", padx=0, pady=0)

                    action_btn = ttk.Button(self.user_rows[0][7].master, text="Enable", style="GreenText.TButton")
                    action_btn.grid(row=1, column=7, sticky="nsew", padx=0, pady=0)

                # Close cursor and connection
                cursor.close()
                conn.close()

                # Update status to show success
                self.update_status("User profiles loaded successfully", "success")

            except Exception as e:
                # Handle database error
                self.log_message(f"Error loading user profiles: {str(e)}")
                if conn:
                    conn.close()

                # Set error state in UI for first row
                self.user_rows[0][0].config(text="1")
                self.user_rows[0][1].config(text="Error loading profiles")
                self.user_rows[0][2].config(text="Database error")
                self.user_rows[0][4].config(text=current_mac_address)  # MAC Address

                # Add a dummy dropdown and button
                user_type_combo = ttk.Combobox(self.user_rows[0][6].master, values=["user", "admin"], state="readonly",
                                               width=10)
                user_type_combo.set("user")
                user_type_combo.grid(row=1, column=6, sticky="nsew", padx=0, pady=0)

                action_btn = ttk.Button(self.user_rows[0][7].master, text="Enable", style="GreenText.TButton")
                action_btn.grid(row=1, column=7, sticky="nsew", padx=0, pady=0)

                # Update status to show error
                self.update_status("Error loading user profiles", "error")
        else:
            # No database connection - show error in first row
            self.user_rows[0][0].config(text="1")
            self.user_rows[0][1].config(text="Database connection failed")
            self.user_rows[0][2].config(text="No connection")
            self.user_rows[0][4].config(text=current_mac_address)  # MAC Address

            # Add a dummy dropdown and button
            user_type_combo = ttk.Combobox(self.user_rows[0][6].master, values=["user", "admin"], state="readonly",
                                           width=10)
            user_type_combo.set("user")
            user_type_combo.grid(row=1, column=6, sticky="nsew", padx=0, pady=0)

            action_btn = ttk.Button(self.user_rows[0][7].master, text="Enable", style="GreenText.TButton")
            action_btn.grid(row=1, column=7, sticky="nsew", padx=0, pady=0)

            # Update status to show connection error
            self.update_status("Database connection failed", "error")

        # ---------- Tab 1: Model Offsets Database ----------

    def init_tab1(self):
        # Create frames for organization with the info frame style for headers
        control_frame = ttk.LabelFrame(self.tab1, text="Database Controls", style="Info.TLabelframe")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        search_frame = ttk.LabelFrame(self.tab1, text="Search & Model List", style="Info.TLabelframe")
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        model_frame = ttk.LabelFrame(self.tab1, text="Model Details", style="Info.TLabelframe")
        model_frame.pack(fill=tk.X, padx=10, pady=5)

        log_frame = ttk.LabelFrame(self.tab1, text="Log", style="Info.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Control Frame Components
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(btn_frame, text="Sync Databases", command=self.sync_databases).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Import Excel", command=self.import_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Excel", command=self.export_excel).pack(side=tk.LEFT, padx=5)

        # Add Dell Master Password button (Dell 8FC8 moved to tab)
        ttk.Button(btn_frame, text="Dell Master Password", command=self.dell_master_password_action).pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Online/Offline toggle button
        initial_text = "Switch to Offline Mode" if ONLINE_MODE_ENABLED else "Switch to Online Mode"
        self.online_mode_btn = ttk.Button(btn_frame, text=initial_text, command=self.toggle_online_mode)
        self.online_mode_btn.pack(side=tk.LEFT, padx=5)

        # Empty space for layout
        spacer_frame = ttk.Frame(control_frame)
        spacer_frame.pack(side=tk.LEFT, padx=20, pady=5)

        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        ttk.Label(status_frame, text="Connection Status:").pack(side=tk.LEFT)
        self.status_indicator = ttk.Label(status_frame, text="Checking...", style="Warning.TLabel")
        self.status_indicator.pack(side=tk.LEFT, padx=5)

        self.model_count_label = ttk.Label(status_frame, text="Models: 0")
        self.model_count_label.pack(side=tk.LEFT, padx=20)

        # Search Frame Components
        search_control = ttk.Frame(search_frame)
        search_control.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_control, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_model_list())
        ttk.Entry(search_control, textvariable=self.search_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Model List
        list_frame = ttk.Frame(search_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.model_listbox = tk.Listbox(list_frame)
        self.model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        self.model_listbox.bind('<Double-Button-1>', self.on_model_double_click)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.model_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, ipadx=7)  # ipadx makes the scrollbar wider
        self.model_listbox.config(yscrollcommand=scrollbar.set)

        # Model Details Frame
        details_frame = ttk.Frame(model_frame)
        details_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(details_frame, text="Model Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.model_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.model_name_var, width=30).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(details_frame, text="Start Offset:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.start_offset_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.start_offset_var, width=15).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(details_frame, text="End Offset:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        self.end_offset_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.end_offset_var, width=15).grid(row=0, column=5, padx=5, pady=2)

        ttk.Button(details_frame, text="Save", command=self.save_model).grid(row=0, column=6, padx=5, pady=2)
        ttk.Button(details_frame, text="Delete", command=self.delete_model).grid(row=0, column=7, padx=5, pady=2)

        # Log Frame
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            bg=self.console_bg,
            fg=self.console_fg,
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            padx=5,
            pady=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

    # ---------- Flash Descriptor & Window Key Functions ----------
    def execute_action(self):
        """Execute the selected action based on checkboxes and selected files"""
        # Validate file selection first
        source_file = self.source_file_var.get()
        target_file = self.target_file_var.get()

        if not source_file:
            self.update_status("No Source File Selected", "error")
            messagebox.showwarning("Input Error", "Please select a source file.")
            return

        # Determine the selected mode based on checkbox states
        if self.flash_descriptor_var.get():
            self.selected_mode.set("flash_descriptor")
        elif self.window_key_var.get():
            self.selected_mode.set("window_key")
        elif self.dell_8fc8_var.get():
            self.selected_mode.set("dell_8fc8")

        # Get the selected mode from StringVar
        selected_mode = self.selected_mode.get()

        if not self.flash_descriptor_var.get() and not self.window_key_var.get() and not self.dell_8fc8_var.get():
            self.update_status("No Mode Selected", "error")
            messagebox.showwarning("Mode Selection",
                                   "Please select a mode (Flash Descriptor, Window Key, or Dell 8FC8).")
            return

        # If a target file is selected, check if file sizes match
        if target_file:
            try:
                source_size = os.path.getsize(source_file)
                target_size = os.path.getsize(target_file)

                # Format sizes in MB + KB
                def format_size(size_bytes):
                    mb = size_bytes // (1024 * 1024)
                    kb = (size_bytes % (1024 * 1024)) // 1024
                    return f"{mb}MB + {kb}KB"

                source_size_formatted = format_size(source_size)
                target_size_formatted = format_size(target_size)

                # Check if sizes are different
                if source_size != target_size:
                    self.update_status("File Size Mismatch", "warning")
                    error_message = (
                        f"Source and target files have different sizes:\n"
                        f"Source: {source_size_formatted} ({source_size} bytes)\n"
                        f"Target: {target_size_formatted} ({target_size} bytes)\n\n"
                        f"This may cause issues in operation. Do you want to continue anyway?"
                    )

                    if not messagebox.askyesno("Size Mismatch Warning", error_message):
                        return

                    # Add warning to info text if user continues
                    self.add_info("WARNING: File size mismatch detected:")
                    self.add_info(f"Source: {source_size_formatted} ({source_size} bytes)")
                    self.add_info(f"Target: {target_size_formatted} ({target_size} bytes)")

            except Exception as e:
                self.update_status("File Size Check Error", "error")
                messagebox.showwarning("File Check Error", f"Error checking file sizes: {str(e)}")
                return

        # Update status and clear info text before starting
        self.update_status("Processing...", "info")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)

        # Add info about the operation
        self.add_info("Starting execution with the following settings:")
        self.add_info(f"Source file: {source_file}")
        if target_file:
            self.add_info(f"Target file: {target_file}")

        # Get the selected mode from StringVar
        selected_mode = self.selected_mode.get()

        # Get the selected model (if any)
        selected_model = self.selected_model.get()
        selected_models = []

        # Add the selected model to the list if one is selected
        if selected_model:
            selected_models = [selected_model]

        # Log selected model if any
        if selected_models and selected_mode == "window_key":
            self.add_info(f"Selected model: {selected_model}")

        if selected_mode == "flash_descriptor":
            self.add_info("Mode: Flash Descriptor")
            self.add_info("-" * 50)
            self.execute_flash_descriptor(selected_models)
        elif selected_mode == "window_key":
            self.add_info("Mode: Window Key Replacement")
            self.add_info("-" * 50)
            self.execute_window_key(selected_models)
        elif selected_mode == "dell_8fc8":
            self.add_info("Mode: Dell 8FC8 Unlocker")
            self.add_info("-" * 50)
            self.launch_dell_8fc8_unlocker()

    def execute_flash_descriptor(self, selected_models=None):
        """Execute Flash Descriptor extraction/replacement based on selected files"""
        # Skip if mode is disabled
        if not self.flash_descriptor_var.get():
            return

        # Log selected models (for future functionality)
        if selected_models and len(selected_models) > 0:
            self.add_info(f"Flash Descriptor: Model selection is not used in this mode")
            self.add_info(f"Selected models ignored: {', '.join(selected_models)}")

        source_file = self.source_file_var.get()
        target_file = self.target_file_var.get()

        if not source_file:
            self.update_status("No Source File Selected", "error")
            messagebox.showwarning("Input Error", "Please select a source file.")
            return

        if not target_file:
            # If no target file is selected, we assume we're just extracting
            self.update_status("Extracting Flash Descriptor...", "info")
            self.add_info("Extracting Flash Descriptor from source file.")

            # Set the necessary vars and execute extraction
            self.fd_filename_var.set(source_file)
            threading.Thread(target=self._execute_fd_extract, daemon=True).start()
        else:
            # If target file is selected, we're replacing
            self.update_status("Replacing Flash Descriptor...", "info")
            self.add_info(f"Replacing Flash Descriptor from {source_file} to {target_file}")

            # Set the necessary vars and execute replacement
            self.fd_filename_var.set(source_file)
            threading.Thread(target=self._execute_fd_replace, daemon=True).start()

    def _execute_fd_extract(self):
        """Thread function to execute Flash Descriptor extraction"""
        try:
            # Read the source file
            with open(self.fd_filename_var.get(), 'rb') as f:
                bios_data = f.read()

            # Get FD offset and size
            offset = int(self.fd_offset_var.get(), 0)
            size = int(self.fd_size_var.get(), 0)

            # Extract the Flash Descriptor
            if offset + size <= len(bios_data):
                fd_data = bios_data[offset:offset + size]

                # Save to a temporary file
                fd_file = self.fd_filename_var.get() + ".fd"
                with open(fd_file, 'wb') as f:
                    f.write(fd_data)

                # Update UI
                self.root.after(0, lambda: self.update_status("Flash Descriptor Extracted Successfully", "success"))
                self.root.after(0, lambda: self.add_info(f"Flash Descriptor extracted and saved to: {fd_file}"))
                self.root.after(0, lambda: self.add_info(f"Size: {len(fd_data)} bytes ({len(fd_data) / 1024:.2f} KB)"))
                self.root.after(0, lambda: self.add_info(f"Start Address: 0x{offset:X}"))
                self.root.after(0, lambda: self.add_info(f"End Address: 0x{offset + size - 1:X}"))

            else:
                self.root.after(0, lambda: self.update_status("Extraction Failed - Invalid Range", "error"))
                self.root.after(0, lambda: self.add_info("Error: The specified offset and size exceed the file size."))

        except Exception as e:
            self.root.after(0, lambda: self.update_status("Extraction Failed", "error"))
            self.root.after(0, lambda: self.add_info(f"Error: {str(e)}"))

    def _execute_fd_replace(self):
        """Thread function to execute Flash Descriptor replacement"""
        try:
            source_file = self.source_file_var.get()
            target_file = self.target_file_var.get()

            # Read the source file to get Flash Descriptor
            with open(source_file, 'rb') as f:
                source_data = f.read()

            # Read the target file where FD will be inserted
            with open(target_file, 'rb') as f:
                target_data = f.read()

            # Get FD offset and size
            offset = int(self.fd_offset_var.get(), 0)
            size = int(self.fd_size_var.get(), 0)

            # Extract Flash Descriptor from source
            if offset + size <= len(source_data):
                fd_data = source_data[offset:offset + size]

                # Create the modified target data
                if offset + size <= len(target_data):
                    new_data = target_data[:offset] + fd_data + target_data[offset + size:]

                    # Use the same directory as the target file
                    output_dir = os.path.dirname(target_file)

                    # Get just the filename without the path
                    base_filename = os.path.basename(target_file)
                    file_name, file_ext = os.path.splitext(base_filename)
                    patched_file = os.path.join(output_dir, f"{file_name}_patch{file_ext}")

                    # Check if output location is writable before proceeding
                    try:
                        # Quick test to see if we can write to this location
                        with open(patched_file, 'wb') as test_write:
                            pass
                        # If successful, remove the empty file
                        os.remove(patched_file)

                        # Now save the actual patched file
                        with open(patched_file, 'wb') as f:
                            f.write(new_data)

                        # Update UI with simplified message
                        self.root.after(0, lambda: self.update_status(
                            f"Flash Descriptor Patched: {os.path.basename(patched_file)}", "success"))
                        self.root.after(0, lambda: self.add_info(f"Patched file created: {patched_file}"))

                    except (PermissionError, OSError) as e:
                        self.root.after(0, lambda: self.update_status("Patching Failed - Permission Error", "error"))
                        self.root.after(0, lambda: self.add_info(f"Error creating patched file: {str(e)}"))
                        self.root.after(0, lambda: self.add_info(
                            "Try running the application with administrator privileges or use a different directory."))
                    self.root.after(0, lambda: self.add_info(
                        f"Copied data size: {len(fd_data)} bytes ({len(fd_data) / 1024:.2f} KB)"))
                    self.root.after(0, lambda: self.add_info(f"Start Address: 0x{offset:X}"))
                    self.root.after(0, lambda: self.add_info(f"End Address: 0x{offset + size - 1:X}"))

                else:
                    self.root.after(0, lambda: self.update_status("Replacement Failed - Target Too Small", "error"))
                    self.root.after(0,
                                    lambda: self.add_info("Error: The target file is smaller than the required size."))
            else:
                self.root.after(0, lambda: self.update_status("Replacement Failed - Invalid Range", "error"))
                self.root.after(0, lambda: self.add_info(
                    "Error: The specified offset and size exceed the source file size."))

        except Exception as e:
            self.root.after(0, lambda: self.update_status("Replacement Failed", "error"))
            self.root.after(0, lambda: self.add_info(f"Error: {str(e)}"))

    def execute_window_key(self, selected_models=None):
        """Execute Window Key operations based on selected files and models"""
        # Update status
        if not self.window_key_var.get():
            self.update_status("Window Key Mode Disabled", "warning")
            return

        source_file = self.source_file_var.get()
        target_file = self.target_file_var.get()

        if not source_file:
            self.update_status("No Source File Selected", "error")
            messagebox.showwarning("Input Error", "Please select a source file.")
            return

        # Log selected models if provided
        if selected_models and len(selected_models) > 0:
            self.add_info(f"Limiting Window Key operations to models: {', '.join(selected_models)}")
        else:
            self.add_info("Applying Window Key operations to all model types")

        # For Window Key mode, first find the key
        self.update_status("Searching for Windows Key...", "info")
        self.add_info("Searching for Windows Key in source file.")

        # Set the necessary vars and execute search
        self.wk_filename_var.set(source_file)
        threading.Thread(target=self._execute_wk_find, daemon=True).start()

    def _execute_wk_find(self):
        """Thread function to search for Windows key"""
        try:
            # Read the source file
            with open(self.wk_filename_var.get(), 'rb') as f:
                bios_data = f.read()

            # Define common Windows key patterns (simplified)
            key_pattern = rb'([A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5})'

            # Search for the key
            matches = re.findall(key_pattern, bios_data)

            if matches:
                # Take the first match as the key
                found_key = matches[0].decode('ascii')
                self.wk_current_key_var.set(found_key)

                # Update UI
                self.root.after(0, lambda: self.update_status("Windows Key Found", "success"))
                self.root.after(0, lambda: self.add_info(f"Found Windows Key: {found_key}"))

                # If we're replacing (target file specified), prompt for new key
                if self.target_file_var.get():
                    self.root.after(0, lambda: self.prompt_for_new_key())
            else:
                self.root.after(0, lambda: self.update_status("No Windows Key Found", "error"))
                self.root.after(0, lambda: self.add_info("No Windows key found in the BIOS file."))

        except Exception as e:
            self.root.after(0, lambda: self.update_status("Key Search Failed", "error"))
            self.root.after(0, lambda: self.add_info(f"Error: {str(e)}"))

    def prompt_for_new_key(self):
        """Prompt the user for a new Windows key"""
        # Create a dialog to get the new key
        new_key = simpledialog.askstring("New Windows Key",
                                         "Enter the new Windows key (format: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX):",
                                         initialvalue=self.wk_current_key_var.get())

        if new_key:
            self.wk_new_key_var.set(new_key)
            self.add_info(f"New key set: {new_key}")

            # Proceed directly with the replacement
            self.update_status("Replacing Windows Key...", "info")
            threading.Thread(target=self._execute_wk_replace, daemon=True).start()

    def _execute_wk_replace(self):
        """Thread function to replace the Windows key"""
        try:
            source_file = self.source_file_var.get()
            target_file = self.target_file_var.get()
            current_key = self.wk_current_key_var.get()
            new_key = self.wk_new_key_var.get()

            # If no target file is explicitly set, use the source file as the base
            if not target_file:
                target_file = source_file

            # Read the source file
            with open(source_file, 'rb') as f:
                bios_data = f.read()

            # Replace the key
            new_data = bios_data.replace(current_key.encode('ascii'), new_key.encode('ascii'))

            # Use the same directory as the target file
            output_dir = os.path.dirname(target_file)

            # Get just the filename without the path
            base_filename = os.path.basename(target_file)
            file_name, file_ext = os.path.splitext(base_filename)
            patched_file = os.path.join(output_dir, f"{file_name}_wk_patch{file_ext}")

            # Check if output location is writable before proceeding
            try:
                # Quick test to see if we can write to this location
                with open(patched_file, 'wb') as test_write:
                    pass
                # If successful, remove the empty file
                os.remove(patched_file)

                # Now save the actual patched file
                with open(patched_file, 'wb') as f:
                    f.write(new_data)

                # Update UI with simplified message
                self.root.after(0, lambda: self.update_status(f"Windows Key Patched: {os.path.basename(patched_file)}",
                                                              "success"))
                self.root.after(0, lambda: self.add_info(f"Patched file created: {patched_file}"))
                # Show a simple success message
                self.root.after(0, lambda: messagebox.showinfo("Success", "Windows key replaced successfully!"))

            except (PermissionError, OSError) as e:
                self.root.after(0, lambda: self.update_status("Patching Failed - Permission Error", "error"))
                self.root.after(0, lambda: self.add_info(f"Error creating patched file: {str(e)}"))
                self.root.after(0, lambda: self.add_info(
                    "Try running the application with administrator privileges or use a different directory."))
            self.root.after(0, lambda: self.add_info(f"Old key: {current_key}"))
            self.root.after(0, lambda: self.add_info(f"New key: {new_key}"))

        except Exception as e:
            self.root.after(0, lambda: self.update_status("Key Replacement Failed", "error"))
            self.root.after(0, lambda: self.add_info(f"Error: {str(e)}"))

        # Dell 8FC8 functionality removed

    def add_info(self, message):
        """Add a message to the info text area"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)  # Scroll to the end
        self.info_text.config(state=tk.DISABLED)

    def browse_source_file(self):
        """Browse for a source file"""
        file_path = filedialog.askopenfilename(
            title="Select Source File",
            filetypes=[("BIOS files", "*.bin *.rom"), ("All files", "*.*")]
        )

        if file_path:
            self.source_file_var.set(file_path)
            self.add_info(f"Selected source file: {file_path}")

            # Update the tool-specific variables
            self.fd_filename_var.set(file_path)
            self.wk_filename_var.set(file_path)

    def browse_target_file(self):
        """Browse for a target file"""
        file_path = filedialog.askopenfilename(
            title="Select Target File",
            filetypes=[("BIOS files", "*.bin *.rom"), ("All files", "*.*")]
        )

        if file_path:
            self.target_file_var.set(file_path)
            self.add_info(f"Selected target file: {file_path}")

    # ---------- Model Offsets Database Methods ----------

    def create_local_db(self):
        """Create the local SQLite database if it doesn't exist"""
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()

        # Create model_offsets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_offsets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE,
                start_offset TEXT,
                end_offset TEXT
            )
            ''')

        # Create app_users table for user registration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                mobile_number TEXT,
                city TEXT,
                mac_address TEXT,
                registration_date TEXT,
                user_type TEXT,
                status TEXT DEFAULT 'Enabled'
            )
            ''')

        conn.commit()
        conn.close()

        self.log_message("Local database initialized.")

    def update_connection_status(self):
        """Update the connection status indicator"""
        global MYSQL_CONNECTION_CACHE, MYSQL_CACHE_TIME

        # Use cached connection status if recent (less than 10 seconds old)
        current_time = time.time()
        if MYSQL_CONNECTION_CACHE is not None and current_time - MYSQL_CACHE_TIME < 10:
            if MYSQL_CONNECTION_CACHE:
                self.status_indicator.config(text="Online", style="Success.TLabel")
                self.update_model_count()  # Update model count when online
            else:
                self.status_indicator.config(text="Offline", style="Danger.TLabel")
            return

        # Online mode is disabled or MySQL is not available
        if not ONLINE_MODE_ENABLED or not MYSQL_AVAILABLE:
            self.status_indicator.config(text="Offline", style="Danger.TLabel")
            MYSQL_CONNECTION_CACHE = False
            MYSQL_CACHE_TIME = current_time
            return

        # Check MySQL connection in a separate thread to avoid freezing UI
        def check_connection():
            global MYSQL_CONNECTION_CACHE, MYSQL_CACHE_TIME

            # Verify mysql_connector is actually available before trying to use it
            if 'mysql_connector' not in globals():
                MYSQL_CONNECTION_CACHE = False
                MYSQL_CACHE_TIME = time.time()
                self.status_indicator.config(text="Offline", style="Danger.TLabel")
                return

            try:
                conn = mysql_connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )
                conn.close()
                MYSQL_CONNECTION_CACHE = True
                MYSQL_CACHE_TIME = time.time()
                self.status_indicator.config(text="Online", style="Success.TLabel")
            except Exception as e:
                MYSQL_CONNECTION_CACHE = False
                MYSQL_CACHE_TIME = time.time()
                self.status_indicator.config(text="Offline", style="Danger.TLabel")

        # Run the connection check in a separate thread
        threading.Thread(target=check_connection, daemon=True).start()

    def update_model_count(self):
        """Update the model count display"""
        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM model_offsets")
            count = cursor.fetchone()[0]
            conn.close()

            self.model_count_label.config(text=f"Models: {count}")
        except Exception as e:
            self.log_message(f"Error updating model count: {str(e)}")

    def update_model_list(self):
        """Update the listbox with models matching the search criteria"""
        search_term = self.search_var.get().lower()

        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()

            if search_term:
                cursor.execute("SELECT model_name FROM model_offsets WHERE LOWER(model_name) LIKE ?",
                               (f'%{search_term}%',))
            else:
                cursor.execute("SELECT model_name FROM model_offsets ORDER BY model_name")

            models = cursor.fetchall()
            conn.close()

            # Clear and repopulate the listbox
            self.model_listbox.delete(0, tk.END)
            for model in models:
                self.model_listbox.insert(tk.END, model[0])

        except Exception as e:
            self.log_message(f"Error updating model list: {str(e)}")

    def on_model_select(self, event):
        """Handle model selection from the listbox"""
        selection = self.model_listbox.curselection()
        if not selection:
            return

        model_name = self.model_listbox.get(selection[0])

        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT model_name, start_offset, end_offset FROM model_offsets WHERE model_name = ?",
                           (model_name,))
            model_data = cursor.fetchone()
            conn.close()

            if model_data:
                self.selected_model_name = model_data[0]
                self.selected_start_offset = model_data[1]
                self.selected_end_offset = model_data[2]

                # Update the detail fields
                self.model_name_var.set(model_data[0])
                self.start_offset_var.set(model_data[1])
                self.end_offset_var.set(model_data[2])

                self.log_message(f"Selected model: {model_data[0]}")
        except Exception as e:
            self.log_message(f"Error retrieving model details: {str(e)}")

    def on_model_double_click(self, event):
        """Handle double-click on a model in the listbox to directly modify binary file with selected offsets"""
        # First get the selected model details
        self.on_model_select(event)

        if self.selected_model_name and self.selected_start_offset and self.selected_end_offset:
            # Ask user to select a binary file to apply the offsets to
            binary_file = filedialog.askopenfilename(
                title=f"Select Binary File to Modify with '{self.selected_model_name}' Offsets",
                filetypes=[("BIOS files", "*.bin *.rom"), ("All files", "*.*")]
            )

            if not binary_file:
                return

            try:
                # Convert offsets with proper hex handling
                start_offset = int(self.selected_start_offset, 0) if self.selected_start_offset.lower().startswith(
                    '0x') else int(self.selected_start_offset)
                end_offset = int(self.selected_end_offset, 0) if self.selected_end_offset.lower().startswith(
                    '0x') else int(self.selected_end_offset)
                size = end_offset - start_offset

                # Check file size
                binary_size = os.path.getsize(binary_file)

                if start_offset >= binary_size:
                    messagebox.showerror("Error",
                                         f"Start offset ({start_offset}) exceeds binary file size ({binary_size})")
                    return

                if end_offset > binary_size:
                    messagebox.showerror("Error", f"End offset ({end_offset}) exceeds binary file size ({binary_size})")
                    return

                # Use the same directory as the binary file
                output_dir = os.path.dirname(binary_file)

                # Get just the filename without the path
                base_filename = os.path.basename(binary_file)
                file_name, file_ext = os.path.splitext(base_filename)
                patch_file = os.path.join(output_dir, f"{file_name}_patch{file_ext}")

                # Check if output location is writable before proceeding
                try:
                    # Quick test to see if we can write to this location
                    with open(patch_file, 'wb') as test_write:
                        pass
                    # If successful, remove the empty file
                    os.remove(patch_file)
                except PermissionError:
                    messagebox.showerror(
                        "Permission Error",
                        f"Cannot write to '{patch_file}'. Permission denied.\n\n"
                        f"Please try running the application with administrator privileges or "
                        f"choose a different location for the output file."
                    )
                    return
                except OSError as e:
                    messagebox.showerror(
                        "File Access Error",
                        f"Error accessing output location: {str(e)}\n\n"
                        f"Please ensure the directory is accessible and not write-protected."
                    )
                    return

                # Proceed directly without confirmation

                try:
                    # Copy the original file to the new patch file
                    with open(binary_file, 'rb') as src_file, open(patch_file, 'wb') as dst_file:
                        # Copy all content from original file
                        dst_file.write(src_file.read())

                    # Now modify the new patch file
                    with open(patch_file, 'r+b') as patch_file_handle:
                        # Here you would normally modify the bytes at the specified offsets
                        # Since we're just demonstrating the functionality, let's add a placeholder
                        # In a real scenario, you would modify with real data specific to the model
                        patch_file_handle.seek(start_offset)

                        # Fill the entire range with 0xFF bytes as requested
                        modification_data = bytes([0xFF] * size)

                        # Write the FF bytes to the patched file
                        patch_file_handle.write(modification_data)  # Size already matches exactly
                except PermissionError:
                    messagebox.showerror(
                        "Permission Error",
                        f"Cannot write to '{patch_file}'. Permission denied.\n\n"
                        f"Please try running the application with administrator privileges."
                    )
                    return
                except OSError as e:
                    messagebox.showerror(
                        "File Access Error",
                        f"Error accessing the file: {str(e)}"
                    )
                    return

                # Show success message
                self.update_status(f"Created Patched File: {os.path.basename(patch_file)}", "success")
                self.add_info(f"Patched file created: {patch_file}")
                self.add_info(
                    f"Model '{self.selected_model_name}' offsets applied: {self.selected_start_offset} - {self.selected_end_offset}")

                # Show a simple success message
                messagebox.showinfo(
                    "Success",
                    f"Patched file created successfully!"
                )

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create patched file: {str(e)}")
                self.update_status("Patch Creation Failed", "error")
                self.add_info(f"ERROR: {str(e)}")

    def save_model(self):
        """Save or update a model in the database"""
        model_name = self.model_name_var.get().strip()
        start_offset = self.start_offset_var.get().strip()
        end_offset = self.end_offset_var.get().strip()

        if not model_name or not start_offset or not end_offset:
            messagebox.showwarning("Input Error", "All fields must be filled")
            return

        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()

            # Check if model exists
            cursor.execute("SELECT id FROM model_offsets WHERE model_name = ?", (model_name,))
            existing = cursor.fetchone()

            if existing:
                # Update existing model
                cursor.execute(
                    "UPDATE model_offsets SET start_offset = ?, end_offset = ? WHERE model_name = ?",
                    (start_offset, end_offset, model_name)
                )
                self.log_message(f"Updated model: {model_name}")
            else:
                # Insert new model
                cursor.execute(
                    "INSERT INTO model_offsets (model_name, start_offset, end_offset) VALUES (?, ?, ?)",
                    (model_name, start_offset, end_offset)
                )
                self.log_message(f"Added new model: {model_name}")

            conn.commit()
            conn.close()

            # Update display
            self.update_model_count()
            self.update_model_list()

            # Play confirmation sound if available
            self.play_sound("save")

        except Exception as e:
            self.log_message(f"Error saving model: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to save model: {str(e)}")

    def delete_model(self):
        """Delete the selected model from the database"""
        model_name = self.model_name_var.get().strip()

        if not model_name:
            messagebox.showwarning("Selection Error", "No model selected")
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{model_name}'?"):
            return

        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM model_offsets WHERE model_name = ?", (model_name,))
            conn.commit()
            conn.close()

            self.log_message(f"Deleted model: {model_name}")

            # Clear entry fields
            self.model_name_var.set("")
            self.start_offset_var.set("")
            self.end_offset_var.set("")

            # Update display
            self.update_model_count()
            self.update_model_list()

            # Play confirmation sound if available
            self.play_sound("delete")

        except Exception as e:
            self.log_message(f"Error deleting model: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to delete model: {str(e)}")

    def sync_databases(self):
        """Synchronize the local database with the remote MySQL database"""
        if not MYSQL_AVAILABLE:
            messagebox.showwarning("Sync Error", "MySQL support is not available.")
            return

        if not ONLINE_MODE_ENABLED:
            messagebox.showwarning("Sync Error", "Cannot sync in offline mode.")
            return

        # Verify mysql_connector is available at runtime
        if 'mysql_connector' not in globals():
            messagebox.showwarning("Sync Error", "MySQL connector module is not available.")
            return

        try:
            # Check if we can connect to MySQL
            mysql_conn = mysql_connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            # Get models from MySQL
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute("SELECT model_name, start_offset, end_offset FROM model_offsets")
            mysql_models = mysql_cursor.fetchall()
            mysql_conn.close()

            # Get models from SQLite
            sqlite_conn = sqlite3.connect(LOCAL_DB_PATH)
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT model_name, start_offset, end_offset FROM model_offsets")
            sqlite_models = {model[0]: (model[1], model[2]) for model in sqlite_cursor.fetchall()}

            # Track sync statistics
            added = 0
            updated = 0

            # Update SQLite with MySQL data
            for model in mysql_models:
                model_name, start_offset, end_offset = model

                if model_name in sqlite_models:
                    # Model exists in SQLite, update if different
                    if sqlite_models[model_name] != (start_offset, end_offset):
                        sqlite_cursor.execute(
                            "UPDATE model_offsets SET start_offset = ?, end_offset = ? WHERE model_name = ?",
                            (start_offset, end_offset, model_name)
                        )
                        updated += 1
                else:
                    # Model doesn't exist in SQLite, add it
                    sqlite_cursor.execute(
                        "INSERT INTO model_offsets (model_name, start_offset, end_offset) VALUES (?, ?, ?)",
                        (model_name, start_offset, end_offset)
                    )
                    added += 1

            sqlite_conn.commit()
            sqlite_conn.close()

            # Update UI
            self.update_model_count()
            self.update_model_list()

            self.log_message(f"Database sync complete. Added: {added}, Updated: {updated}")
            messagebox.showinfo("Sync Complete", f"Database sync complete\nAdded: {added}\nUpdated: {updated}")

        except Exception as e:
            self.log_message(f"Error syncing databases: {str(e)}")
            messagebox.showerror("Sync Error", f"Failed to sync databases: {str(e)}")

    def import_excel(self):
        """Import model offsets from an Excel file"""
        # Try to import pandas at function level to localize the import error
        pd = None
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Import Error", "Pandas is not available. Cannot import Excel files.")
            return

        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Read Excel file
            df = pd.read_excel(file_path)

            # Validate column names
            required_columns = ['model_name', 'start_offset', 'end_offset']
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Import Error",
                                     "Excel file must contain columns: model_name, start_offset, end_offset")
                return

            # Connect to SQLite database
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()

            # Track import statistics
            added = 0
            updated = 0
            errors = 0

            # Process each row
            for index, row in df.iterrows():
                try:
                    model_name = str(row['model_name']).strip()
                    start_offset = str(row['start_offset']).strip()
                    end_offset = str(row['end_offset']).strip()

                    if not model_name:
                        continue  # Skip empty model names

                    # Check if model exists
                    cursor.execute("SELECT id FROM model_offsets WHERE model_name = ?", (model_name,))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing model
                        cursor.execute(
                            "UPDATE model_offsets SET start_offset = ?, end_offset = ? WHERE model_name = ?",
                            (start_offset, end_offset, model_name)
                        )
                        updated += 1
                    else:
                        # Insert new model
                        cursor.execute(
                            "INSERT INTO model_offsets (model_name, start_offset, end_offset) VALUES (?, ?, ?)",
                            (model_name, start_offset, end_offset)
                        )
                        added += 1
                except Exception as e:
                    errors += 1
                    self.log_message(f"Error importing row {index}: {str(e)}")

            conn.commit()
            conn.close()

            # Update UI
            self.update_model_count()
            self.update_model_list()

            self.log_message(f"Excel import complete. Added: {added}, Updated: {updated}, Errors: {errors}")
            messagebox.showinfo("Import Complete",
                                f"Excel import complete\nAdded: {added}\nUpdated: {updated}\nErrors: {errors}")

        except Exception as e:
            self.log_message(f"Error importing Excel file: {str(e)}")
            messagebox.showerror("Import Error", f"Failed to import Excel file: {str(e)}")

    def export_excel(self):
        """Export model offsets to an Excel file"""
        # Try to import pandas at function level to localize the import error
        pd = None
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Export Error", "Pandas is not available. Cannot export to Excel.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Fetch all models from the database
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT model_name, start_offset, end_offset FROM model_offsets ORDER BY model_name")
            models = cursor.fetchall()
            conn.close()

            if not models:
                messagebox.showinfo("Export", "No models to export.")
                return

            # Create DataFrame
            df = pd.DataFrame(models, columns=['model_name', 'start_offset', 'end_offset'])

            # Export to Excel
            df.to_excel(file_path, index=False)

            self.log_message(f"Exported {len(models)} models to {file_path}")
            messagebox.showinfo("Export Complete", f"Successfully exported {len(models)} models to Excel file.")

        except Exception as e:
            self.log_message(f"Error exporting to Excel: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export to Excel: {str(e)}")

    def toggle_online_mode(self):
        """Toggle between online and offline mode"""
        global ONLINE_MODE_ENABLED

        if ONLINE_MODE_ENABLED:
            ONLINE_MODE_ENABLED = False
            self.online_mode_btn.config(text="Switch to Online Mode")
            self.log_message("Switched to offline mode")
        else:
            ONLINE_MODE_ENABLED = True
            self.online_mode_btn.config(text="Switch to Offline Mode")
            self.log_message("Switched to online mode")

        # Update connection status
        self.update_connection_status()

    def init_dell_8fc8_tab(self):
        """Initialize the Dell 8FC8 Unlocker tab with a simple button"""
        import os
        import sys
        import subprocess

        # Create a centered frame for the button
        self.dell_main_frame = ttk.Frame(self.tab4, padding=20)
        self.dell_main_frame.pack(fill=tk.BOTH, expand=True)

        # Add Dell logo and header
        header_frame = ttk.Frame(self.dell_main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 30))

        dell_label = ttk.Label(header_frame, text="DELL",
                               font=("Arial", 24, "bold"), foreground="#0078D7")
        dell_label.pack(side=tk.LEFT)

        title_label = ttk.Label(header_frame, text="8FC8 BIOS Unlocker",
                                font=("Arial", 18))
        title_label.pack(side=tk.LEFT, padx=10)

        # Button frame in the center
        button_frame = ttk.Frame(self.dell_main_frame)
        button_frame.pack(expand=True, pady=20)

        # Create the button
        dell_button = ttk.Button(button_frame,
                                 text="Dell 8FC8",
                                 command=self.launch_dell_8fc8_unlocker,
                                 style="Large.TButton",
                                 width=20)
        dell_button.pack(pady=10, ipady=10)

        # Add information text
        info_frame = ttk.LabelFrame(self.dell_main_frame, text="About Dell 8FC8 Unlocker")
        info_frame.pack(fill=tk.X, pady=20, padx=20)

        info_text = """The Dell 8FC8 BIOS Unlocker tool allows you to patch Dell BIOS files to unlock hidden settings.

    It searches for and modifies Dell 8FC8 and FD8 patterns to enable advanced BIOS menus, providing access to advanced configuration options.

    Warning: Use at your own risk. Modifying your BIOS may void warranty or damage your device."""

        info_label = ttk.Label(info_frame, text=info_text, wraplength=550,
                               justify=tk.LEFT, padding=10)
        info_label.pack(fill=tk.X)

        # Set up a special button style
        style = ttk.Style()
        style.configure("Large.TButton",
                        font=("Arial", 14, "bold"),
                        padding=10,
                        background="#0078D7")

        # Add this to main logging
        self.log_message("Dell 8FC8 Unlocker tab initialized with button interface")

    def launch_dell_8fc8_unlocker(self):
        """Launch the Dell 8FC8 Unlocker as a separate window without showing console"""
        try:
            # Define the path to dell_8fc8_unlocker.py
            unlocker_script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "dell_8fc8_unlocker.py")

            # Check if the script exists
            if not os.path.exists(unlocker_script):
                self.log_message("Error: Dell 8FC8 BIOS Unlocker script not found")
                messagebox.showerror("Error",
                                     "The Dell 8FC8 BIOS Unlocker script was not found.")
                return

            # Launch as a separate process without showing console
            self.log_message(f"Starting Dell 8FC8 BIOS Unlocker")

            # Use subprocess to run the script with no console window
            python_exe = sys.executable

            # Different flags for Windows vs other platforms
            if os.name == 'nt':  # Windows
                # CREATE_NO_WINDOW flag (0x08000000) hides the console window
                self.dell_process = subprocess.Popen([python_exe, unlocker_script],
                                                     creationflags=0x08000000)
            else:  # Other platforms
                # Redirect output to /dev/null to hide console output
                with open(os.devnull, 'w') as devnull:
                    self.dell_process = subprocess.Popen([python_exe, unlocker_script],
                                                         stdout=devnull,
                                                         stderr=devnull)

            # Update status directly in the UI instead of showing a popup
            self.update_status("Dell 8FC8 BIOS Unlocker launched successfully.", "success")
            self.log_message("Dell 8FC8 BIOS Unlocker launched successfully.")

        except Exception as e:
            self.log_message(f"Error launching Dell 8FC8 BIOS Unlocker: {str(e)}")
            # Display error in the interface instead of as a messagebox
            self.update_status(f"Failed to launch Dell 8FC8 BIOS Unlocker: {str(e)}", "error")

    # The Dell 8FC8 Unlocker automatically launches as a separate window when the tab is selected
    # This keeps the original dell_8fc8_unlocker.py code untouched

    def dell_master_password_action(self):
        """Handle Dell Master Password button action"""
        # Update status directly in the UI instead of showing a popup
        self.update_status("Dell Master Password feature will be implemented in the next update.", "info")
        self.log_message("Dell Master Password feature accessed (not implemented yet)")
        self.log_message("This function will provide Dell BIOS master password generation capabilities.")

    def log_message(self, message):
        """Add a message to the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.log_text.config(state=tk.DISABLED)

    def play_sound(self, sound_type="default"):
        """Play a notification sound if available"""
        # SOUND_SUPPORTED is set at the module level when winsound is available
        if not SOUND_SUPPORTED:
            return

        try:
            # This block will only execute on Windows systems with winsound available
            if sys.platform == 'win32':
                if sound_type == "save":
                    winsound.MessageBeep(winsound.MB_ICONINFORMATION)
                elif sound_type == "delete":
                    winsound.MessageBeep(winsound.MB_ICONWARNING)
                elif sound_type == "error":
                    winsound.MessageBeep(winsound.MB_ICONERROR)
                else:
                    winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            # Just log the sound error but don't interrupt the flow
            pass

    # Helper function to get MAC address


def get_mac_address():
    """Get the MAC address of the primary network interface"""
    try:
        # Check if we want to use a default MAC address (for testing/demo purposes)
        # This helps with testing so you don't need to worry about the actual MAC address
        use_default_mac = True  # Set to True to always use the default MAC
        if use_default_mac:
            return "DE:FA:UL:T0:MA:C0"  # Default MAC address for testing

        if NETIFACES_AVAILABLE:
            # Get the list of network interfaces
            interfaces = netifaces.interfaces()

            # Filter out loopback interfaces
            for interface in interfaces:
                if interface != 'lo' and netifaces.AF_LINK in netifaces.ifaddresses(interface):
                    # Get the MAC address for this interface
                    mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
                    return mac

        # Fallback method for getting MAC address if netifaces is not available
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        mac = uuid.getnode()
        mac_address = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])
        return mac_address
    except Exception as e:
        print(f"Error retrieving MAC address: {e}")
        return "00:00:00:00:00:00"  # Return a dummy MAC if we can't get the real one

    # Database connection function


def get_db_connection():
    """Get a connection to the appropriate database"""
    # Check if the environment is set up for PostgreSQL
    if os.environ.get('DATABASE_URL'):
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(PG_CONNECTION_STRING)
            print("Connected to PostgreSQL database")
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            # Fall back to SQLite if PostgreSQL fails
            try:
                sqlite_conn = sqlite3.connect(LOCAL_DB_PATH)
                print("Connected to SQLite database as fallback")
                return sqlite_conn
            except Exception as e:
                print(f"Error connecting to SQLite fallback: {e}")
                return None
    else:
        # Use SQLite if no PostgreSQL environment variables are set
        try:
            sqlite_conn = sqlite3.connect(LOCAL_DB_PATH)
            print("Connected to SQLite database")
            return sqlite_conn
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return None


# Application startup
if __name__ == "__main__":
    # Use TkinterDnD if available
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
        print("Using TkinterDnD for drag and drop support")
    else:
        # Fall back to standard Tk
        root = tk.Tk()
        print("TkinterDnD not available, using standard Tk without drag and drop")

    # Start the main application
    app = FCCToolsApp(root)
    root.mainloop()