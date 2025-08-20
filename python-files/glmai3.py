import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
import sys
import platform
import math
import json
import random
from collections import deque
import time

# Check for Pillow availability
try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    message = (
        "The Pillow library is required for the Canvas app.\n"
        "Please install it first via:\n\n"
        "python -m pip install Pillow\n\n"
        "The Canvas app will not work without Pillow installed."
    )
    print(message)
    Image = None
    ImageDraw = None
    ImageTk = None

# High-DPI awareness for Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# Cross-platform font configuration
if platform.system() == "Darwin":  # macOS
    DEFAULT_FONT = ("SF Pro Display", 14)
    TITLE_FONT = ("SF Pro Display", 28, "bold")
    BUTTON_FONT = ("SF Pro Display", 16)
elif platform.system() == "Windows":
    DEFAULT_FONT = ("Segoe UI", 14)
    TITLE_FONT = ("Segoe UI", 28, "bold")
    BUTTON_FONT = ("Segoe UI", 16)
else:  # Linux
    DEFAULT_FONT = ("Ubuntu", 14)
    TITLE_FONT = ("Ubuntu", 28, "bold")
    BUTTON_FONT = ("Ubuntu", 16)

# Color scheme
COLORS = {
    'bg_primary': '#1a1a1a',
    'bg_secondary': '#2d2d2d',
    'bg_tertiary': '#3d3d3d',
    'accent': '#007AFF',
    'accent_hover': '#0056CC',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'success': '#34C759',
    'warning': '#FF9500',
    'error': '#FF3B30'
}

# Directory to save/load data
DATA_DIR = os.path.join(os.path.expanduser("~"), ".multi_app_system")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Settings file path
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "pong_player_paddle_color": COLORS['accent'],
    "canvas_bg_color": "#000000",
    "canvas_pen_color": "#FFFFFF",
    "tetris_block_colors": [
        "#FF0D72", "#0DC2FF", "#0DFF72", "#F538FF",
        "#FF8E0D", "#FFE138", "#3877FF"
    ],
    "minesweeper_difficulty": "Medium",
    "volleyball_difficulty": "Medium"
}

# Load settings
def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_SETTINGS, **settings}
    except Exception as e:
        print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

# Save settings
def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

def apply_modern_theme(root):
    """Apply a modern dark theme to the application"""
    style = ttk.Style(root)
    
    # Use clam theme as base (works well cross-platform)
    style.theme_use("clam")
    
    # Configure button styles
    style.configure(
        "Modern.TButton",
        font=BUTTON_FONT,
        padding=(20, 12),
        relief="flat",
        background=COLORS['accent'],
        foreground=COLORS['text_primary'],
        borderwidth=0,
        focuscolor="none"
    )
    
    style.map(
        "Modern.TButton",
        background=[
            ('active', COLORS['accent_hover']),
            ('pressed', COLORS['accent_hover'])
        ],
        relief=[('pressed', 'flat')]
    )
    
    # Toolbar button style
    style.configure(
        "Toolbar.TButton",
        font=DEFAULT_FONT,
        padding=(12, 8),
        relief="flat",
        background=COLORS['bg_tertiary'],
        foreground=COLORS['text_primary'],
        borderwidth=0,
        focuscolor="none"
    )
    
    style.map(
        "Toolbar.TButton",
        background=[
            ('active', COLORS['bg_secondary']),
            ('pressed', COLORS['bg_secondary'])
        ]
    )
    
    # Entry style
    style.configure(
        "Modern.TEntry",
        padding=8,
        fieldbackground=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        borderwidth=1,
        relief="solid",
        insertcolor=COLORS['text_primary']
    )

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-App GUI System")
        self.configure(bg=COLORS['bg_primary'])
        self.minsize(600, 700)
        self.geometry("900x750")
        
        # Load settings
        self.settings = load_settings()
        
        # Apply modern theme
        apply_modern_theme(self)
        
        # Configure window for better appearance
        if platform.system() == "Darwin":
            # macOS specific configurations
            try:
                self.tk.call('tk', 'scaling', 2.0)  # Better for Retina displays
            except:
                pass
        
        self.container = tk.Frame(self, bg=COLORS['bg_primary'])
        self.container.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.frames = {}
        self.create_launcher()
    
    def create_launcher(self):
        self.clear_current_frame()
        
        launcher = tk.Frame(self.container, bg=COLORS['bg_primary'])
        launcher.pack(fill='both', expand=True)
        
        # Title with better spacing
        title_frame = tk.Frame(launcher, bg=COLORS['bg_primary'])
        title_frame.pack(fill='x', pady=(0, 40))
        
        lbl = tk.Label(
            title_frame, 
            text="App Launcher", 
            fg=COLORS['text_primary'], 
            bg=COLORS['bg_primary'], 
            font=TITLE_FONT
        )
        lbl.pack()
        
        # Subtitle
        subtitle = tk.Label(
            title_frame,
            text="Choose an application to launch",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=DEFAULT_FONT
        )
        subtitle.pack(pady=(10, 0))
        
        # Button container with better layout
        button_frame = tk.Frame(launcher, bg=COLORS['bg_primary'])
        button_frame.pack(expand=True, fill='both', padx=100)
        
        apps = [
            ("🎨 Canvas", self.show_canvas),
            ("🧮 Calculator", self.show_calculator),
            ("🏓 Pong Game", self.show_pong),
            ("🧩 Tetris", self.show_tetris),
            ("💣 Minesweeper", self.show_minesweeper),
            ("🏐 Volleyball", self.show_volleyball),
            ("📝 Notes", self.show_notes),
            ("⚙️ Settings", self.show_settings),
        ]
        
        for i, (text, command) in enumerate(apps):
            btn = ttk.Button(
                button_frame, 
                text=text, 
                command=command,
                style="Modern.TButton"
            )
            btn.pack(fill='x', pady=8)
            
            # Add hover effects
            self.add_hover_effect(btn)
        
        self.current_frame = launcher
    
    def add_hover_effect(self, widget):
        """Add subtle hover effects to buttons"""
        def on_enter(e):
            widget.configure(cursor="hand2")
        
        def on_leave(e):
            widget.configure(cursor="")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def clear_current_frame(self):
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.pack_forget()
    
    def _show_app(self, key, cls):
        self.clear_current_frame()
        # Always create a new instance for apps that need fresh state
        if key in ["pong", "tetris", "minesweeper", "volleyball"]:  # Apps that need fresh instances
            if key in self.frames:
                self.frames[key].cleanup()  # Clean up previous instance
            self.frames[key] = cls(self.container, self, self.settings)
        elif key not in self.frames:
            self.frames[key] = cls(self.container, self, self.settings)
        
        self.frames[key].pack(fill='both', expand=True)
        self.current_frame = self.frames[key]
    
    def show_canvas(self):
        self._show_app("canvas", CanvasApp)
    
    def show_calculator(self):
        self._show_app("calculator", CalculatorApp)
    
    def show_pong(self):
        self._show_app("pong", PongApp)
    
    def show_tetris(self):
        self._show_app("tetris", TetrisApp)
    
    def show_minesweeper(self):
        self._show_app("minesweeper", MinesweeperApp)
    
    def show_volleyball(self):
        self._show_app("volleyball", VolleyballApp)
    
    def show_notes(self):
        self._show_app("notes", NotesApp)
    
    def show_settings(self):
        self._show_app("settings", SettingsApp)

# ================= Enhanced Canvas App =================
class CanvasApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        
        if not (Image and ImageDraw and ImageTk):
            self.show_pillow_error()
            return
        
        self.setup_canvas()
    
    def show_pillow_error(self):
        error_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        error_frame.pack(expand=True, fill='both')
        
        icon_label = tk.Label(
            error_frame,
            text="⚠️",
            fg=COLORS['warning'],
            bg=COLORS['bg_primary'],
            font=("Arial", 48)
        )
        icon_label.pack(pady=(50, 20))
        
        label = tk.Label(
            error_frame,
            text="Pillow Library Required",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 20, "bold")
        )
        label.pack(pady=(0, 10))
        
        desc_label = tk.Label(
            error_frame,
            text="The Canvas app requires the Pillow library.\nInstall it with: python -m pip install Pillow",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=DEFAULT_FONT,
            justify="center"
        )
        desc_label.pack(pady=(0, 30))
        
        btn_back = ttk.Button(
            error_frame,
            text="← Back to Launcher",
            command=self.controller.create_launcher,
            style="Modern.TButton"
        )
        btn_back.pack()
    
    def setup_canvas(self):
        self.drawing = False
        self.old_x = self.old_y = None
        self.pen_width = 3
        self.pen_color = self.settings.get('canvas_pen_color', "#FFFFFF")
        self.eraser_mode = False
        self.canvas_width = 800
        self.canvas_height = 600
        self.bg_color = self.settings.get('canvas_bg_color', "#000000")
        self.shape_mode = "free"  # free, line, rectangle, circle
        
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
        # Modern toolbar
        toolbar = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)
        
        # Left side buttons
        left_frame = tk.Frame(toolbar, bg=COLORS['bg_secondary'])
        left_frame.pack(side="left", fill="y", padx=15, pady=10)
        
        btn_back = ttk.Button(
            left_frame,
            text="← Back",
            command=self._go_back,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=(0, 10))
        
        # Title
        title = tk.Label(
            left_frame,
            text="🎨 Canvas",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0))
        
        # Help button
        btn_help = ttk.Button(
            left_frame,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0))
        
        # Right side buttons
        right_frame = tk.Frame(toolbar, bg=COLORS['bg_secondary'])
        right_frame.pack(side="right", fill="y", padx=15, pady=10)
        
        buttons = [
            ("Clear", self.clear_canvas),
            ("Load", self.load_drawing),
            ("Save", self.save_drawing)
        ]
        
        for text, command in reversed(buttons):
            btn = ttk.Button(
                right_frame,
                text=text,
                command=command,
                style="Toolbar.TButton"
            )
            btn.pack(side="right", padx=(10, 0))
        
        # Canvas with better styling
        canvas_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        canvas_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.bg_color,
            width=self.canvas_width,
            height=self.canvas_height,
            cursor="cross",
            highlightthickness=2,
            highlightbackground=COLORS['bg_tertiary']
        )
        self.canvas.pack(expand=True)
        
        # Tools panel
        tools_frame = tk.Frame(self, bg=COLORS['bg_secondary'], height=50)
        tools_frame.pack(side="bottom", fill="x")
        tools_frame.pack_propagate(False)
        
        # Pen tool
        self.pen_btn = tk.Button(
            tools_frame,
            text="✏️ Pen",
            command=lambda: self.select_tool("pen"),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.pen_btn.pack(side="left", padx=15, pady=10)
        
        # Eraser tool
        self.eraser_btn = tk.Button(
            tools_frame,
            text="🧹 Eraser",
            command=lambda: self.select_tool("eraser"),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.eraser_btn.pack(side="left", padx=5, pady=10)
        
        # Line tool
        self.line_btn = tk.Button(
            tools_frame,
            text="📏 Line",
            command=lambda: self.select_tool("line"),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.line_btn.pack(side="left", padx=5, pady=10)
        
        # Rectangle tool
        self.rect_btn = tk.Button(
            tools_frame,
            text="⬜ Rectangle",
            command=lambda: self.select_tool("rectangle"),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.rect_btn.pack(side="left", padx=5, pady=10)
        
        # Circle tool
        self.circle_btn = tk.Button(
            tools_frame,
            text="⭕ Circle",
            command=lambda: self.select_tool("circle"),
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.circle_btn.pack(side="left", padx=5, pady=10)
        
        # Pen color picker
        self.pen_color_btn = tk.Button(
            tools_frame,
            text="🎨 Pen Color",
            command=self.pick_pen_color,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.pen_color_btn.pack(side="left", padx=5, pady=10)
        
        # Background color picker
        self.bg_color_btn = tk.Button(
            tools_frame,
            text="🖼️ Background",
            command=self.pick_bg_color,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2"
        )
        self.bg_color_btn.pack(side="left", padx=5, pady=10)
        
        # Pen width slider
        width_frame = tk.Frame(tools_frame, bg=COLORS['bg_secondary'])
        width_frame.pack(side="left", padx=15, pady=10)
        
        tk.Label(
            width_frame,
            text="Width:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT
        ).pack(side="left")
        
        self.width_slider = tk.Scale(
            width_frame,
            from_=1,
            to=20,
            orient="horizontal",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            highlightthickness=0,
            command=self.update_pen_width
        )
        self.width_slider.set(self.pen_width)
        self.width_slider.pack(side="left")
        
        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.pen_down)
        self.canvas.bind("<B1-Motion>", self.pen_move)
        self.canvas.bind("<ButtonRelease-1>", self.pen_up)
        
        # Initialize with pen selected
        self.select_tool("pen")
        
        # Key bindings
        self.bind("<Control-s>", lambda e: self.save_drawing())
        self.bind("<Control-o>", lambda e: self.load_drawing())
        self.bind("<Control-n>", lambda e: self.clear_canvas())
        self.bind("<Control-e>", lambda e: self.select_tool("eraser"))
        self.bind("<Control-p>", lambda e: self.select_tool("pen"))
        self.bind("<F1>", lambda e: self.show_help())
    
    def _go_back(self):
        # Save current settings
        self.settings['canvas_pen_color'] = self.pen_color
        self.settings['canvas_bg_color'] = self.bg_color
        save_settings(self.settings)
        self.controller.create_launcher()
    
    def select_tool(self, tool):
        # Reset all tool buttons
        self.pen_btn.config(fg=COLORS['text_secondary'])
        self.eraser_btn.config(fg=COLORS['text_secondary'])
        self.line_btn.config(fg=COLORS['text_secondary'])
        self.rect_btn.config(fg=COLORS['text_secondary'])
        self.circle_btn.config(fg=COLORS['text_secondary'])
        
        # Highlight selected tool
        if tool == "pen":
            self.pen_btn.config(fg=COLORS['text_primary'])
            self.eraser_mode = False
            self.shape_mode = "free"
            self.canvas.config(cursor="cross")
        elif tool == "eraser":
            self.eraser_btn.config(fg=COLORS['text_primary'])
            self.eraser_mode = True
            self.shape_mode = "free"
            self.canvas.config(cursor="dotbox")
        elif tool == "line":
            self.line_btn.config(fg=COLORS['text_primary'])
            self.eraser_mode = False
            self.shape_mode = "line"
            self.canvas.config(cursor="crosshair")
        elif tool == "rectangle":
            self.rect_btn.config(fg=COLORS['text_primary'])
            self.eraser_mode = False
            self.shape_mode = "rectangle"
            self.canvas.config(cursor="crosshair")
        elif tool == "circle":
            self.circle_btn.config(fg=COLORS['text_primary'])
            self.eraser_mode = False
            self.shape_mode = "circle"
            self.canvas.config(cursor="crosshair")
    
    def update_pen_width(self, value):
        self.pen_width = int(value)
    
    def pick_pen_color(self):
        color = colorchooser.askcolor(initialcolor=self.pen_color, title="Choose Pen Color")
        if color[1]:
            self.pen_color = color[1]
    
    def pick_bg_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color, title="Choose Background Color")
        if color[1]:
            self.bg_color = color[1]
            self.canvas.config(bg=self.bg_color)
            # Update the image background
            new_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
            new_image.paste(self.image)
            self.image = new_image
            self.draw = ImageDraw.Draw(self.image)
            # Redraw canvas
            self.canvas.delete("all")
            self.photo_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
    
    def pen_down(self, event):
        self.drawing = True
        self.old_x, self.old_y = event.x, event.y
        
        if self.shape_mode in ["line", "rectangle", "circle"]:
            self.start_x = event.x
            self.start_y = event.y
    
    def pen_move(self, event):
        if not self.drawing:
            return
        
        if self.shape_mode == "free":
            # Determine drawing color
            if self.eraser_mode:
                draw_color = self.bg_color
            else:
                draw_color = self.pen_color
            
            self.canvas.create_line(
                self.old_x, self.old_y, event.x, event.y,
                width=self.pen_width,
                fill=draw_color,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.draw.line([self.old_x, self.old_y, event.x, event.y], fill=draw_color, width=self.pen_width)
            self.old_x, self.old_y = event.x, event.y
        
        elif self.shape_mode in ["line", "rectangle", "circle"]:
            # For shapes, we'll draw on mouse up
            pass
    
    def pen_up(self, event):
        if not self.drawing:
            return
        
        if self.shape_mode == "free":
            self.drawing = False
            self.old_x = self.old_y = None
        
        elif self.shape_mode == "line":
            # Draw line
            self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                width=self.pen_width,
                fill=self.pen_color,
                capstyle=tk.ROUND
            )
            self.draw.line([self.start_x, self.start_y, event.x, event.y], fill=self.pen_color, width=self.pen_width)
            self.drawing = False
        
        elif self.shape_mode == "rectangle":
            # Draw rectangle
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.pen_color,
                width=self.pen_width
            )
            self.draw.rectangle([x1, y1, x2, y2], outline=self.pen_color, width=self.pen_width)
            self.drawing = False
        
        elif self.shape_mode == "circle":
            # Draw circle
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            
            # Calculate radius
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            self.canvas.create_oval(
                x1 - radius, y1 - radius, x1 + radius, y1 + radius,
                outline=self.pen_color,
                width=self.pen_width
            )
            self.draw.ellipse([x1 - radius, y1 - radius, x1 + radius, y1 + radius], outline=self.pen_color, width=self.pen_width)
            self.drawing = False
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill=self.bg_color)
    
    def save_drawing(self):
        try:
            path = filedialog.asksaveasfilename(
                initialdir=DATA_DIR,
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Save Drawing As"
            )
            if path:
                self.image.save(path)
                messagebox.showinfo("Success", f"Drawing saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving drawing:\n{e}")
    
    def load_drawing(self):
        try:
            path = filedialog.askopenfilename(
                initialdir=DATA_DIR,
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Load Drawing"
            )
            if path:
                img = Image.open(path).resize((self.canvas_width, self.canvas_height))
                self.image.paste(img)
                self.draw = ImageDraw.Draw(self.image)
                self.canvas.delete("all")
                self.photo_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
                # Update background color to match loaded image
                self.bg_color = self.image.getpixel((0, 0))
                self.canvas.config(bg=self.bg_color)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading drawing:\n{e}")
    
    def show_help(self):
        help_text = """Canvas App Help

Tools:
• Pen: Draw freely on the canvas
• Eraser: Erase parts of your drawing
• Line: Draw straight lines
• Rectangle: Draw rectangles
• Circle: Draw circles

Keyboard Shortcuts:
• Ctrl+S: Save drawing
• Ctrl+O: Load drawing
• Ctrl+N: Clear canvas
• Ctrl+E: Select eraser
• Ctrl+P: Select pen
• F1: Show this help

Tips:
• Adjust pen width with the slider
• Change pen and background colors with the color pickers
• Click and drag to draw shapes"""
        
        messagebox.showinfo("Canvas Help", help_text)

# ================= Enhanced Calculator App =================
class CalculatorApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=controller.create_launcher,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="🧮 Calculator",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Help button
        btn_help = ttk.Button(
            header,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0), pady=15)
        
        # Mode toggle
        self.scientific_mode = False
        self.mode_btn = ttk.Button(
            header,
            text="Scientific: OFF",
            command=self.toggle_mode,
            style="Toolbar.TButton"
        )
        self.mode_btn.pack(side="right", padx=15, pady=15)
        
        # Calculator body
        calc_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        calc_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        self.expression = ""
        self.input_text = tk.StringVar()
        
        # Display
        display_frame = tk.Frame(calc_frame, bg=COLORS['bg_secondary'], relief="solid", bd=1)
        display_frame.pack(fill='x', pady=(0, 20))
        
        self.entry = tk.Entry(
            display_frame,
            font=("Courier New", 24, "bold"),
            textvariable=self.input_text,
            justify="right",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            relief="flat",
            bd=10,
            insertbackground=COLORS['text_primary']
        )
        self.entry.pack(fill='x')
        
        # Button grid
        button_frame = tk.Frame(calc_frame, bg=COLORS['bg_primary'])
        button_frame.pack(expand=True, fill='both')
        
        # Standard calculator buttons
        standard_buttons = [
            ('C', 0, 0, COLORS['error']), ('+/-', 0, 1, COLORS['bg_tertiary']), ('%', 0, 2, COLORS['bg_tertiary']), ('/', 0, 3, COLORS['accent']),
            ('7', 1, 0, COLORS['bg_tertiary']), ('8', 1, 1, COLORS['bg_tertiary']), ('9', 1, 2, COLORS['bg_tertiary']), ('*', 1, 3, COLORS['accent']),
            ('4', 2, 0, COLORS['bg_tertiary']), ('5', 2, 1, COLORS['bg_tertiary']), ('6', 2, 2, COLORS['bg_tertiary']), ('-', 2, 3, COLORS['accent']),
            ('1', 3, 0, COLORS['bg_tertiary']), ('2', 3, 1, COLORS['bg_tertiary']), ('3', 3, 2, COLORS['bg_tertiary']), ('+', 3, 3, COLORS['accent']),
            ('0', 4, 0, COLORS['bg_tertiary'], 2), ('.', 4, 2, COLORS['bg_tertiary']), ('=', 4, 3, COLORS['success'])
        ]
        
        # Scientific calculator buttons
        scientific_buttons = [
            ('sin', 0, 4, COLORS['bg_tertiary']), ('cos', 1, 4, COLORS['bg_tertiary']), ('tan', 2, 4, COLORS['bg_tertiary']), ('log', 3, 4, COLORS['bg_tertiary']),
            ('π', 0, 5, COLORS['bg_tertiary']), ('e', 1, 5, COLORS['bg_tertiary']), ('x²', 2, 5, COLORS['bg_tertiary']), ('√', 3, 5, COLORS['bg_tertiary']),
            ('(', 0, 6, COLORS['bg_tertiary']), (')', 1, 6, COLORS['bg_tertiary']), ('xʸ', 2, 6, COLORS['bg_tertiary']), ('1/x', 3, 6, COLORS['bg_tertiary']),
            ('DEG', 0, 7, COLORS['bg_tertiary']), ('RAD', 1, 7, COLORS['bg_tertiary']), ('!', 2, 7, COLORS['bg_tertiary']), ('EXP', 3, 7, COLORS['bg_tertiary'])
        ]
        
        # Create standard buttons
        for btn_info in standard_buttons:
            if len(btn_info) == 4:
                text, row, col, color = btn_info
                colspan = 1
            else:
                text, row, col, color, colspan = btn_info
            
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda x=text: self.btn_click(x),
                font=(DEFAULT_FONT[0], 18, "bold"),
                bg=color,
                fg=COLORS['text_primary'],
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)
            
            # Hover effects
            def on_enter(e, btn=btn, hover_color=self.lighten_color(color)):
                btn.configure(bg=hover_color)
            
            def on_leave(e, btn=btn, orig_color=color):
                btn.configure(bg=orig_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Create scientific buttons (initially hidden)
        self.scientific_btns = []
        for btn_info in scientific_buttons:
            text, row, col, color = btn_info
            
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda x=text: self.btn_click(x),
                font=(DEFAULT_FONT[0], 16),
                bg=color,
                fg=COLORS['text_primary'],
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            btn.grid_remove()  # Hide initially
            
            # Hover effects
            def on_enter(e, btn=btn, hover_color=self.lighten_color(color)):
                btn.configure(bg=hover_color)
            
            def on_leave(e, btn=btn, orig_color=color):
                btn.configure(bg=orig_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.scientific_btns.append(btn)
        
        # Configure grid weights
        for i in range(8):
            button_frame.rowconfigure(i, weight=1)
        for j in range(5):
            button_frame.columnconfigure(j, weight=1)
        
        # Key bindings
        self.bind("<Return>", lambda e: self.btn_click('='))
        self.bind("<Escape>", lambda e: self.btn_click('C'))
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Control-s>", lambda e: self.toggle_mode())
        
        # Keyboard bindings for numbers and operators
        for key in '0123456789.+-*/()':
            self.bind(key, lambda e, k=key: self.btn_click(k))
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effect"""
        if color.startswith('#'):
            # Simple lightening by adding to each RGB component
            try:
                r = min(255, int(color[1:3], 16) + 30)
                g = min(255, int(color[3:5], 16) + 30)
                b = min(255, int(color[5:7], 16) + 30)
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                return color
        return color
    
    def toggle_mode(self):
        """Toggle between standard and scientific calculator"""
        self.scientific_mode = not self.scientific_mode
        
        if self.scientific_mode:
            self.mode_btn.config(text="Scientific: ON")
            for btn in self.scientific_btns:
                btn.grid()
        else:
            self.mode_btn.config(text="Scientific: OFF")
            for btn in self.scientific_btns:
                btn.grid_remove()
    
    def backspace(self):
        """Remove the last character from the expression"""
        if self.expression:
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
    
    def btn_click(self, key):
        if key == 'C':
            self.expression = ""
            self.input_text.set("")
        elif key == '=':
            try:
                expr = self.expression.replace('%', '/100')
                result = self.safe_eval(expr)
                self.input_text.set(result)
                self.expression = str(result)
            except Exception:
                self.input_text.set("Error")
                self.expression = ""
        elif key == '+/-':
            if self.expression.startswith('-'):
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.input_text.set(self.expression)
        elif key in ['sin', 'cos', 'tan', 'log', '√', 'x²', 'xʸ', '1/x', '!', 'EXP']:
            self.handle_scientific_function(key)
        elif key in ['π', 'e']:
            if key == 'π':
                self.expression += str(math.pi)
            else:  # e
                self.expression += str(math.e)
            self.input_text.set(self.expression)
        elif key in ['DEG', 'RAD']:
            # Toggle angle mode (not implemented in this version)
            pass
        else:
            self.expression += str(key)
            self.input_text.set(self.expression)
    
    def handle_scientific_function(self, func):
        """Handle scientific calculator functions"""
        try:
            if func == 'sin':
                self.expression = str(math.sin(float(self.expression)))
            elif func == 'cos':
                self.expression = str(math.cos(float(self.expression)))
            elif func == 'tan':
                self.expression = str(math.tan(float(self.expression)))
            elif func == 'log':
                self.expression = str(math.log10(float(self.expression)))
            elif func == '√':
                self.expression = str(math.sqrt(float(self.expression)))
            elif func == 'x²':
                self.expression = str(float(self.expression) ** 2)
            elif func == 'xʸ':
                self.expression += '**'
            elif func == '1/x':
                self.expression = str(1 / float(self.expression))
            elif func == '!':
                n = int(float(self.expression))
                self.expression = str(math.factorial(n))
            elif func == 'EXP':
                self.expression += 'e'
            
            self.input_text.set(self.expression)
        except Exception:
            self.input_text.set("Error")
            self.expression = ""
    
    def safe_eval(self, expr):
        allowed = "0123456789+-/*%.()e "
        if any(ch not in allowed for ch in expr):
            raise ValueError("Invalid input")
        
        # Replace mathematical constants and functions
        expr = expr.replace('π', str(math.pi))
        expr = expr.replace('e', str(math.e))
        
        return eval(expr, {"__builtins__": None, 
                          "sin": math.sin, 
                          "cos": math.cos, 
                          "tan": math.tan,
                          "sqrt": math.sqrt,
                          "log10": math.log10,
                          "factorial": math.factorial}, {})
    
    def show_help(self):
        help_text = """Calculator Help

Standard Mode:
• Basic arithmetic operations (+, -, *, /)
• Percentage calculations (%)
• Sign change (+/-)
• Clear (C)
• Equals (=)

Scientific Mode:
• Trigonometric functions (sin, cos, tan)
• Logarithm (log)
• Square root (√)
• Square (x²)
• Power (xʸ)
• Reciprocal (1/x)
• Factorial (!)
• Exponential (EXP)
• Constants (π, e)

Keyboard Shortcuts:
• Enter: Calculate result
• Escape: Clear
• Backspace: Delete last character
• Ctrl+S: Toggle scientific mode
• F1: Show this help

Tips:
• Use parentheses for complex expressions
• Scientific mode provides advanced functions"""
        
        messagebox.showinfo("Calculator Help", help_text)

# ================= FIXED Pong App =================
class PongApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        self.width = 800
        self.height = 600
        
        # Game state management
        self.game_running = False
        self.game_loop_id = None
        self.keys_pressed = set()
        self.paused = False
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=self._go_back,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="🏓 Pong Game",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Help button
        btn_help = ttk.Button(
            header,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0), pady=15)
        
        self.score_label = tk.Label(
            header,
            text="Player: 0  CPU: 0",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.score_label.pack(side="right", padx=15, pady=15)
        
        # Game canvas with modern styling
        canvas_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        canvas_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.width,
            height=self.height,
            bg="black",
            highlightthickness=2,
            highlightbackground=COLORS['accent']
        )
        self.canvas.pack()
        
        # Initialize game variables
        self._reset_game()
        
        # Instructions
        instructions = tk.Label(
            self,
            text="Use ↑ and ↓ arrow keys to move your paddle | Press P to pause",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=DEFAULT_FONT
        )
        instructions.pack(pady=10)
        
        # Start the game
        self._start_game()
    
    def _reset_game(self):
        """Reset all game variables to initial state"""
        self.paddle_width = 15
        self.paddle_height = 120
        self.ball_size = 20
        self.paddle_speed = 8  # Reduced for smoother movement
        self.cpu_speed = 4     # Slower CPU for smoother movement
        
        self.player_y = self.height // 2 - self.paddle_height // 2
        self.cpu_y = self.player_y
        self.cpu_target_y = self.cpu_y  # Target position for smooth CPU movement
        
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_speed_x = 8
        self.ball_speed_y = 4
        
        self.player_score = 0
        self.cpu_score = 0
        
        # Player paddle color from settings
        self.player_paddle_color = self.settings.get('pong_player_paddle_color', COLORS['accent'])
        
        # Clear any existing game objects
        self.canvas.delete("all")
    
    def _start_game(self):
        """Start the game loop"""
        self.game_running = True
        self._draw_elements()
        self._bind_events()
        self._game_loop()
    
    def _go_back(self):
        """Properly stop the game and return to launcher"""
        self.cleanup()
        self.controller.create_launcher()
    
    def cleanup(self):
        """Clean up game resources"""
        self.game_running = False
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        
        # Unbind all events
        try:
            self.unbind("<KeyPress>")
            self.unbind("<KeyRelease>")
            self.unbind("<p>")
            self.unbind("<P>")
            self.unbind("<F1>")
        except:
            pass
    
    def _draw_elements(self):
        """Draw all game elements"""
        self.canvas.delete("all")
        
        # Center line
        self.canvas.create_line(
            self.width//2, 0, self.width//2, self.height,
            fill=COLORS['bg_tertiary'], dash=(10, 10), width=2
        )
        
        # Player paddle (left side)
        self.player_paddle = self.canvas.create_rectangle(
            20, self.player_y, 20+self.paddle_width, self.player_y+self.paddle_height,
            fill=self.player_paddle_color, outline=self.player_paddle_color
        )
        
        # CPU paddle (right side)
        self.cpu_paddle = self.canvas.create_rectangle(
            self.width-20-self.paddle_width, self.cpu_y, self.width-20, self.cpu_y+self.paddle_height,
            fill=COLORS['text_primary'], outline=COLORS['text_primary']
        )
        
        # Ball
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size//2, self.ball_y - self.ball_size//2,
            self.ball_x + self.ball_size//2, self.ball_y + self.ball_size//2,
            fill=COLORS['success'], outline=COLORS['success']
        )
        
        # Pause indicator
        if self.paused:
            self.pause_text = self.canvas.create_text(
                self.width//2, self.height//2,
                text="PAUSED",
                fill=COLORS['warning'],
                font=(DEFAULT_FONT[0], 36, "bold")
            )
    
    def _bind_events(self):
        """Bind keyboard events for smooth movement"""
        self.bind("<KeyPress-Up>", self._key_press)
        self.bind("<KeyPress-Down>", self._key_press)
        self.bind("<KeyRelease-Up>", self._key_release)
        self.bind("<KeyRelease-Down>", self._key_release)
        self.bind("p", self._toggle_pause)
        self.bind("P", self._toggle_pause)
        self.bind("<F1>", lambda e: self.show_help())
        self.focus_set()
    
    def _key_press(self, event):
        """Handle key press events"""
        self.keys_pressed.add(event.keysym)
    
    def _key_release(self, event):
        """Handle key release events"""
        self.keys_pressed.discard(event.keysym)
    
    def _toggle_pause(self, event=None):
        """Toggle pause state"""
        self.paused = not self.paused
        self._draw_elements()
    
    def _update_player_movement(self):
        """Update player paddle based on pressed keys"""
        if "Up" in self.keys_pressed:
            self.player_y = max(self.player_y - self.paddle_speed, 0)
        if "Down" in self.keys_pressed:
            self.player_y = min(self.player_y + self.paddle_speed, self.height - self.paddle_height)
    
    def _update_cpu_movement(self):
        """Smooth CPU movement with target-based AI"""
        # Calculate target position (ball position with some prediction)
        ball_center_y = self.ball_y
        paddle_center_y = self.cpu_y + self.paddle_height // 2
        
        # Add some prediction based on ball direction
        if self.ball_speed_x > 0:  # Ball moving towards CPU
            prediction_time = (self.width - 20 - self.paddle_width - self.ball_x) / abs(self.ball_speed_x)
            predicted_y = self.ball_y + self.ball_speed_y * prediction_time
            self.cpu_target_y = predicted_y - self.paddle_height // 2
        else:
            # Ball moving away, move towards center
            self.cpu_target_y = self.height // 2 - self.paddle_height // 2
        
        # Smooth movement towards target
        diff = self.cpu_target_y - self.cpu_y
        if abs(diff) > self.cpu_speed:
            if diff > 0:
                self.cpu_y += self.cpu_speed
            else:
                self.cpu_y -= self.cpu_speed
        else:
            self.cpu_y = self.cpu_target_y
        
        # Keep CPU paddle within bounds
        self.cpu_y = max(0, min(self.cpu_y, self.height - self.paddle_height))
    
    def _game_loop(self):
        """Main game loop"""
        if not self.game_running:
            return
        
        if not self.paused:
            # Update player movement
            self._update_player_movement()
            
            # Move ball
            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y
            
            # Bounce off top/bottom walls
            if self.ball_y - self.ball_size//2 <= 0 or self.ball_y + self.ball_size//2 >= self.height:
                self.ball_speed_y *= -1
            
            # Collision detection with paddles
            ball_left = self.ball_x - self.ball_size//2
            ball_right = self.ball_x + self.ball_size//2
            ball_top = self.ball_y - self.ball_size//2
            ball_bottom = self.ball_y + self.ball_size//2
            
            # Player paddle collision
            player_left = 20
            player_right = 20 + self.paddle_width
            player_top = self.player_y
            player_bottom = self.player_y + self.paddle_height
            
            if (ball_left <= player_right and ball_right >= player_left and
                ball_top <= player_bottom and ball_bottom >= player_top and
                self.ball_speed_x < 0):
                self.ball_speed_x *= -1
                # Add some angle based on where ball hits paddle
                hit_pos = (self.ball_y - self.player_y) / self.paddle_height
                self.ball_speed_y = (hit_pos - 0.5) * 10
            
            # CPU paddle collision
            cpu_left = self.width - 20 - self.paddle_width
            cpu_right = self.width - 20
            cpu_top = self.cpu_y
            cpu_bottom = self.cpu_y + self.paddle_height
            
            if (ball_left <= cpu_right and ball_right >= cpu_left and
                ball_top <= cpu_bottom and ball_bottom >= cpu_top and
                self.ball_speed_x > 0):
                self.ball_speed_x *= -1
                # Add some angle based on where ball hits paddle
                hit_pos = (self.ball_y - self.cpu_y) / self.paddle_height
                self.ball_speed_y = (hit_pos - 0.5) * 10
            
            # Update CPU movement
            self._update_cpu_movement()
            
            # Scoring
            if self.ball_x < 0:
                self.cpu_score += 1
                self._reset_ball()
            elif self.ball_x > self.width:
                self.player_score += 1
                self._reset_ball()
            
            # Update display
            self._update_score()
            self._redraw_elements()
        
        # Schedule next frame
        self.game_loop_id = self.after(16, self._game_loop)  # ~60 FPS
    
    def _reset_ball(self):
        """Reset ball to center with random direction"""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_speed_x = 8 if self.ball_speed_x > 0 else -8
        self.ball_speed_y = 4
    
    def _update_score(self):
        """Update score display"""
        self.score_label.config(text=f"Player: {self.player_score}  CPU: {self.cpu_score}")
    
    def _redraw_elements(self):
        """Update positions of all game elements"""
        # Update player paddle
        self.canvas.coords(
            self.player_paddle,
            20, self.player_y,
            20 + self.paddle_width, self.player_y + self.paddle_height
        )
        
        # Update CPU paddle
        self.canvas.coords(
            self.cpu_paddle,
            self.width - 20 - self.paddle_width, self.cpu_y,
            self.width - 20, self.cpu_y + self.paddle_height
        )
        
        # Update ball
        self.canvas.coords(
            self.ball,
            self.ball_x - self.ball_size // 2, self.ball_y - self.ball_size // 2,
            self.ball_x + self.ball_size // 2, self.ball_y + self.ball_size // 2
        )
    
    def show_help(self):
        help_text = """Pong Game Help

How to Play:
• Use the ↑ and ↓ arrow keys to move your paddle
• Try to hit the ball past the CPU's paddle
• First to 7 points wins!

Controls:
• ↑ / ↓: Move paddle up/down
• P: Pause/unpause game
• F1: Show this help

Tips:
• The ball will bounce at different angles depending on where it hits your paddle
• Try to hit the ball with the edges of your paddle for sharper angles
• The CPU gets smarter as the game progresses

Settings:
• You can change your paddle color in the Settings app"""
        
        messagebox.showinfo("Pong Game Help", help_text)

# ================= Tetris App =================
class TetrisApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        
        # Game constants
        self.grid_width = 10
        self.grid_height = 20
        self.cell_size = 30
        self.game_width = self.grid_width * self.cell_size
        self.game_height = self.grid_height * self.cell_size
        
        # Tetromino shapes
        self.shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]],  # J
            [[0, 1, 1], [1, 1, 0]],  # S
            [[1, 1, 0], [0, 1, 1]]   # Z
        ]
        
        # Colors from settings
        self.colors = self.settings.get('tetris_block_colors', [
            "#FF0D72", "#0DC2FF", "#0DFF72", "#F538FF",
            "#FF8E0D", "#FFE138", "#3877FF"
        ])
        
        # Game state
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        self.current_color = 0
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.next_piece = None
        self.next_color = None
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=self._go_back,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="🧩 Tetris",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Help button
        btn_help = ttk.Button(
            header,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0), pady=15)
        
        # Game container
        game_container = tk.Frame(self, bg=COLORS['bg_primary'])
        game_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Game canvas
        canvas_frame = tk.Frame(game_container, bg=COLORS['bg_tertiary'])
        canvas_frame.pack(side="left", padx=(0, 20))
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.game_width,
            height=self.game_height,
            bg="black",
            highlightthickness=2,
            highlightbackground=COLORS['accent']
        )
        self.canvas.pack()
        
        # Info panel
        info_panel = tk.Frame(game_container, bg=COLORS['bg_secondary'], width=200)
        info_panel.pack(side="right", fill="y")
        info_panel.pack_propagate(False)
        
        # Score
        score_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        score_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            score_frame,
            text="Score",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack()
        
        self.score_label = tk.Label(
            score_frame,
            text="0",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.score_label.pack()
        
        # Level
        level_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        level_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            level_frame,
            text="Level",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack()
        
        self.level_label = tk.Label(
            level_frame,
            text="1",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.level_label.pack()
        
        # Lines
        lines_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        lines_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            lines_frame,
            text="Lines",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack()
        
        self.lines_label = tk.Label(
            lines_frame,
            text="0",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.lines_label.pack()
        
        # Next piece
        next_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        next_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            next_frame,
            text="Next",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack()
        
        self.next_canvas = tk.Canvas(
            next_frame,
            width=100,
            height=80,
            bg="black",
            highlightthickness=0
        )
        self.next_canvas.pack(pady=5)
        
        # Controls
        controls_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        controls_frame.pack(fill="x", padx=10, pady=20)
        
        tk.Label(
            controls_frame,
            text="Controls",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 14, "bold")
        ).pack(pady=(0, 10))
        
        controls_text = (
            "← → : Move\n"
            "↓ : Soft Drop\n"
            "↑ : Rotate\n"
            "Space : Hard Drop\n"
            "P : Pause"
        )
        
        tk.Label(
            controls_frame,
            text=controls_text,
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT,
            justify="left"
        ).pack()
        
        # Game over message
        self.game_over_label = tk.Label(
            self,
            text="GAME OVER",
            fg=COLORS['error'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 24, "bold")
        )
        
        # Pause message
        self.pause_label = tk.Label(
            self,
            text="PAUSED",
            fg=COLORS['warning'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 24, "bold")
        )
        
        # Start the game
        self._start_game()
    
    def _start_game(self):
        """Initialize and start the game"""
        self._reset_game()
        self._spawn_piece()
        self._bind_events()
        self._game_loop()
    
    def _reset_game(self):
        """Reset game state"""
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 500
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        
        # Update UI
        self._update_score()
        self._update_level()
        self._update_lines()
        
        # Hide messages
        self.game_over_label.pack_forget()
        self.pause_label.pack_forget()
    
    def _spawn_piece(self):
        """Spawn a new tetromino"""
        if self.next_piece is None:
            piece_idx = random.randint(0, len(self.shapes) - 1)
            self.next_piece = self.shapes[piece_idx]
            self.next_color = piece_idx
        
        self.current_piece = self.next_piece
        self.current_color = self.next_color
        self.current_rotation = 0
        self.current_x = self.grid_width // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        # Generate next piece
        piece_idx = random.randint(0, len(self.shapes) - 1)
        self.next_piece = self.shapes[piece_idx]
        self.next_color = piece_idx
        self._draw_next_piece()
        
        # Check if game over
        if not self._is_valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.game_over_label.pack(pady=20)
    
    def _bind_events(self):
        """Bind keyboard events"""
        self.bind("<Left>", lambda e: self._move(-1, 0))
        self.bind("<Right>", lambda e: self._move(1, 0))
        self.bind("<Down>", lambda e: self._move(0, 1))
        self.bind("<Up>", lambda e: self._rotate())
        self.bind("<space>", lambda e: self._hard_drop())
        self.bind("p", lambda e: self._toggle_pause())
        self.bind("P", lambda e: self._toggle_pause())
        self.bind("<F1>", lambda e: self.show_help())
        self.focus_set()
    
    def _move(self, dx, dy):
        """Move the current piece"""
        if self.game_over or self.paused:
            return
        
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if self._is_valid_position(self.current_piece, new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False
    
    def _rotate(self):
        """Rotate the current piece"""
        if self.game_over or self.paused:
            return
        
        # Create rotated piece
        rotated = []
        for i in range(len(self.current_piece[0])):
            row = []
            for j in range(len(self.current_piece) - 1, -1, -1):
                row.append(self.current_piece[j][i])
            rotated.append(row)
        
        # Check if rotation is valid
        if self._is_valid_position(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
            self.current_rotation = (self.current_rotation + 1) % 4
    
    def _hard_drop(self):
        """Drop the piece to the bottom"""
        if self.game_over or self.paused:
            return
        
        while self._move(0, 1):
            pass
        self._lock_piece()
    
    def _toggle_pause(self):
        """Toggle pause state"""
        if self.game_over:
            return
        
        self.paused = not self.paused
        if self.paused:
            self.pause_label.pack(pady=20)
        else:
            self.pause_label.pack_forget()
    
    def _is_valid_position(self, piece, x, y):
        """Check if a piece position is valid"""
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    
                    if (new_x < 0 or new_x >= self.grid_width or 
                        new_y >= self.grid_height or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def _lock_piece(self):
        """Lock the current piece in place"""
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    y = self.current_y + row_idx
                    x = self.current_x + col_idx
                    
                    if y >= 0:
                        self.grid[y][x] = self.current_color + 1  # +1 to avoid 0 index
        
        # Check for completed lines
        lines_to_clear = []
        for y in range(self.grid_height):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # Clear lines
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(self.grid_width)])
        
        # Update score
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [40, 100, 300, 1200][len(lines_to_clear) - 1] * self.level
            self._update_score()
            self._update_lines()
            
            # Update level
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(100, 500 - (self.level - 1) * 50)
                self._update_level()
        
        # Spawn new piece
        self._spawn_piece()
    
    def _update_score(self):
        """Update score display"""
        self.score_label.config(text=str(self.score))
    
    def _update_level(self):
        """Update level display"""
        self.level_label.config(text=str(self.level))
    
    def _update_lines(self):
        """Update lines display"""
        self.lines_label.config(text=str(self.lines_cleared))
    
    def _draw_next_piece(self):
        """Draw the next piece preview"""
        self.next_canvas.delete("all")
        
        if self.next_piece:
            color = self.colors[self.next_color]
            
            # Calculate offset to center the piece
            piece_width = len(self.next_piece[0]) * self.cell_size
            piece_height = len(self.next_piece) * self.cell_size
            offset_x = (100 - piece_width) // 2
            offset_y = (80 - piece_height) // 2
            
            # Draw the piece
            for row_idx, row in enumerate(self.next_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = offset_x + col_idx * self.cell_size
                        y = offset_y + row_idx * self.cell_size
                        self.next_canvas.create_rectangle(
                            x, y,
                            x + self.cell_size, y + self.cell_size,
                            fill=color, outline=""
                        )
    
    def _draw_grid(self):
        """Draw the game grid"""
        self.canvas.delete("all")
        
        # Draw placed blocks
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    color_idx = self.grid[y][x] - 1
                    color = self.colors[color_idx]
                    self.canvas.create_rectangle(
                        x * self.cell_size, y * self.cell_size,
                        (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                        fill=color, outline=""
                    )
        
        # Draw current piece
        if self.current_piece and not self.game_over:
            color = self.colors[self.current_color]
            for row_idx, row in enumerate(self.current_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = (self.current_x + col_idx) * self.cell_size
                        y = (self.current_y + row_idx) * self.cell_size
                        self.canvas.create_rectangle(
                            x, y,
                            x + self.cell_size, y + self.cell_size,
                            fill=color, outline=""
                        )
        
        # Draw grid lines
        for x in range(self.grid_width + 1):
            self.canvas.create_line(
                x * self.cell_size, 0,
                x * self.cell_size, self.game_height,
                fill=COLORS['bg_tertiary'], width=1
            )
        
        for y in range(self.grid_height + 1):
            self.canvas.create_line(
                0, y * self.cell_size,
                self.game_width, y * self.cell_size,
                fill=COLORS['bg_tertiary'], width=1
            )
    
    def _game_loop(self):
        """Main game loop"""
        if not self.game_over:
            if not self.paused:
                self.fall_time += 16  # milliseconds
                
                if self.fall_time >= self.fall_speed:
                    if not self._move(0, 1):
                        self._lock_piece()
                    self.fall_time = 0
                
                self._draw_grid()
            
            # Schedule next frame
            self.after(16, self._game_loop)  # ~60 FPS
    
    def _go_back(self):
        """Clean up and return to launcher"""
        self.unbind("<Left>")
        self.unbind("<Right>")
        self.unbind("<Down>")
        self.unbind("<Up>")
        self.unbind("<space>")
        self.unbind("p")
        self.unbind("P")
        self.unbind("<F1>")
        self.controller.create_launcher()
    
    def cleanup(self):
        """Clean up resources"""
        pass
    
    def show_help(self):
        help_text = """Tetris Help

How to Play:
• Arrange falling blocks to create complete horizontal lines
• When a line is completed, it disappears and you earn points
• The game speeds up as you progress through levels

Controls:
• ← → : Move piece left/right
• ↓ : Soft drop (faster fall)
• ↑ : Rotate piece
• Space : Hard drop (instant drop)
• P : Pause/unpause game
• F1: Show this help

Scoring:
• 1 line: 40 points × level
• 2 lines: 100 points × level
• 3 lines: 300 points × level
• 4 lines (Tetris): 1200 points × level

Tips:
• Plan your moves in advance by looking at the next piece
• Try to clear multiple lines at once for bonus points
• Keep the stack as low as possible to avoid game over
• Use the rotation wisely to fit pieces in tight spaces

Settings:
• You can customize block colors in the Settings app"""
        
        messagebox.showinfo("Tetris Help", help_text)

# ================= Minesweeper App =================
class MinesweeperApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        
        # Game constants
        self.difficulties = {
            "Easy": {"rows": 8, "cols": 8, "mines": 10},
            "Medium": {"rows": 16, "cols": 16, "mines": 40},
            "Hard": {"rows": 16, "cols": 30, "mines": 99}
        }
        
        # Get current difficulty from settings
        self.current_difficulty = self.settings.get('minesweeper_difficulty', "Medium")
        self.rows = self.difficulties[self.current_difficulty]["rows"]
        self.cols = self.difficulties[self.current_difficulty]["cols"]
        self.mine_count = self.difficulties[self.current_difficulty]["mines"]
        
        # Game state
        self.grid = []
        self.revealed = []
        self.flagged = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.timer = 0
        self.timer_running = False
        self.flags_placed = 0
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=self._go_back,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="💣 Minesweeper",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Help button
        btn_help = ttk.Button(
            header,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0), pady=15)
        
        # Difficulty selector
        diff_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        diff_frame.pack(side="right", padx=15, pady=15)
        
        tk.Label(
            diff_frame,
            text="Difficulty:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT
        ).pack(side="left", padx=(0, 5))
        
        self.diff_var = tk.StringVar(value=self.current_difficulty)
        diff_menu = ttk.OptionMenu(
            diff_frame,
            self.diff_var,
            self.current_difficulty,
            *self.difficulties.keys(),
            command=self.change_difficulty
        )
        diff_menu.pack(side="left")
        
        # New game button
        new_game_btn = ttk.Button(
            diff_frame,
            text="New Game",
            command=self.new_game,
            style="Toolbar.TButton"
        )
        new_game_btn.pack(side="left", padx=(10, 0))
        
        # Game container
        game_container = tk.Frame(self, bg=COLORS['bg_primary'])
        game_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Info panel
        info_panel = tk.Frame(game_container, bg=COLORS['bg_secondary'], height=50)
        info_panel.pack(fill="x", pady=(0, 10))
        info_panel.pack_propagate(False)
        
        # Mine counter
        mine_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        mine_frame.pack(side="left", padx=10, pady=10)
        
        tk.Label(
            mine_frame,
            text="Mines:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack(side="left", padx=(5, 0))
        
        self.mine_label = tk.Label(
            mine_frame,
            text=str(self.mine_count - self.flags_placed),
            fg=COLORS['error'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.mine_label.pack(side="left", padx=(5, 10))
        
        # Timer
        timer_frame = tk.Frame(info_panel, bg=COLORS['bg_tertiary'])
        timer_frame.pack(side="right", padx=10, pady=10)
        
        tk.Label(
            timer_frame,
            text="Time:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=DEFAULT_FONT
        ).pack(side="left", padx=(5, 0))
        
        self.timer_label = tk.Label(
            timer_frame,
            text="000",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.timer_label.pack(side="left", padx=(5, 10))
        
        # Game canvas
        canvas_frame = tk.Frame(game_container, bg=COLORS['bg_tertiary'])
        canvas_frame.pack(expand=True, fill='both')
        
        self.cell_size = min(500 // self.cols, 500 // self.rows)
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=canvas_width,
            height=canvas_height,
            bg=COLORS['bg_tertiary'],
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        
        # Game over message
        self.game_over_label = tk.Label(
            self,
            text="GAME OVER",
            fg=COLORS['error'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 24, "bold")
        )
        
        # Game won message
        self.game_won_label = tk.Label(
            self,
            text="YOU WIN!",
            fg=COLORS['success'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 24, "bold")
        )
        
        # Initialize game
        self.new_game()
    
    def new_game(self):
        """Start a new game"""
        # Reset game state
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.timer = 0
        self.timer_running = False
        self.flags_placed = 0
        
        # Update UI
        self.mine_label.config(text=str(self.mine_count - self.flags_placed))
        self.timer_label.config(text="000")
        self.game_over_label.pack_forget()
        self.game_won_label.pack_forget()
        
        # Draw grid
        self.draw_grid()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)
        self.bind("<F1>", lambda e: self.show_help())
    
    def change_difficulty(self, difficulty):
        """Change game difficulty"""
        self.current_difficulty = difficulty
        self.settings['minesweeper_difficulty'] = difficulty
        save_settings(self.settings)
        
        # Update game parameters
        self.rows = self.difficulties[difficulty]["rows"]
        self.cols = self.difficulties[difficulty]["cols"]
        self.mine_count = self.difficulties[difficulty]["mines"]
        
        # Start new game
        self.new_game()
    
    def draw_grid(self):
        """Draw the game grid"""
        self.canvas.delete("all")
        
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Determine cell color
                if self.revealed[row][col]:
                    if self.grid[row][col] == -1:  # Mine
                        color = COLORS['error']
                    else:
                        color = COLORS['bg_secondary']
                else:
                    color = COLORS['bg_tertiary']
                
                # Draw cell
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=COLORS['bg_primary'],
                    width=1
                )
                
                # Draw cell content
                if self.revealed[row][col]:
                    if self.grid[row][col] == -1:  # Mine
                        # Draw mine
                        self.canvas.create_oval(
                            x1 + self.cell_size // 4, y1 + self.cell_size // 4,
                            x2 - self.cell_size // 4, y2 - self.cell_size // 4,
                            fill=COLORS['text_primary'],
                            outline=""
                        )
                    elif self.grid[row][col] > 0:  # Number
                        # Draw number with appropriate color
                        number_colors = [
                            "",  # 0 - not used
                            COLORS['accent'],  # 1
                            COLORS['success'],  # 2
                            COLORS['error'],  # 3
                            COLORS['text_primary'],  # 4
                            COLORS['warning'],  # 5
                            COLORS['text_secondary'],  # 6
                            "#000000",  # 7
                            "#808080"  # 8
                        ]
                        
                        self.canvas.create_text(
                            (x1 + x2) // 2, (y1 + y2) // 2,
                            text=str(self.grid[row][col]),
                            fill=number_colors[self.grid[row][col]],
                            font=(DEFAULT_FONT[0], int(self.cell_size * 0.6), "bold")
                        )
                elif self.flagged[row][col]:  # Flag
                    # Draw flag
                    self.canvas.create_polygon(
                        x1 + self.cell_size // 3, y1 + self.cell_size // 4,
                        x1 + self.cell_size // 3, y1 + self.cell_size * 3 // 4,
                        x1 + self.cell_size * 2 // 3, y1 + self.cell_size // 2,
                        fill=COLORS['error'],
                        outline=""
                    )
    
    def left_click(self, event):
        """Handle left mouse click"""
        if self.game_over or self.game_won:
            return
        
        # Get cell coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        # Check if coordinates are valid
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return
        
        # Check if cell is flagged
        if self.flagged[row][col]:
            return
        
        # First click - place mines
        if self.first_click:
            self.first_click = False
            self.place_mines(row, col)
            self.start_timer()
        
        # Reveal cell
        self.reveal_cell(row, col)
        
        # Check win condition
        self.check_win()
    
    def right_click(self, event):
        """Handle right mouse click"""
        if self.game_over or self.game_won:
            return
        
        # Get cell coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        # Check if coordinates are valid
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return
        
        # Check if cell is revealed
        if self.revealed[row][col]:
            return
        
        # Toggle flag
        self.flagged[row][col] = not self.flagged[row][col]
        
        # Update flag count
        if self.flagged[row][col]:
            self.flags_placed += 1
        else:
            self.flags_placed -= 1
        
        # Update UI
        self.mine_label.config(text=str(self.mine_count - self.flags_placed))
        self.draw_grid()
    
    def place_mines(self, safe_row, safe_col):
        """Place mines randomly, avoiding the first clicked cell"""
        mines_placed = 0
        
        while mines_placed < self.mine_count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            # Don't place mine on first clicked cell or adjacent cells
            if abs(row - safe_row) <= 1 and abs(col - safe_col) <= 1:
                continue
            
            # Don't place mine if already placed
            if self.grid[row][col] == -1:
                continue
            
            # Place mine
            self.grid[row][col] = -1
            mines_placed += 1
        
        # Calculate numbers
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != -1:
                    # Count adjacent mines
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            
                            r = row + dr
                            c = col + dc
                            
                            if 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == -1:
                                count += 1
                    
                    self.grid[row][col] = count
    
    def reveal_cell(self, row, col):
        """Reveal a cell and possibly adjacent cells"""
        # Check if cell is already revealed or out of bounds
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols or self.revealed[row][col]:
            return
        
        # Reveal cell
        self.revealed[row][col] = True
        
        # Check if it's a mine
        if self.grid[row][col] == -1:
            self.game_over = True
            self.stop_timer()
            self.reveal_all_mines()
            self.game_over_label.pack(pady=20)
            return
        
        # If cell is empty, reveal adjacent cells
        if self.grid[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    
                    self.reveal_cell(row + dr, col + dc)
        
        # Update UI
        self.draw_grid()
    
    def reveal_all_mines(self):
        """Reveal all mines when game is over"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == -1:
                    self.revealed[row][col] = True
        
        self.draw_grid()
    
    def check_win(self):
        """Check if the player has won"""
        # Count unrevealed safe cells
        unrevealed_safe = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.revealed[row][col] and self.grid[row][col] != -1:
                    unrevealed_safe += 1
        
        # If no unrevealed safe cells, player wins
        if unrevealed_safe == 0:
            self.game_won = True
            self.stop_timer()
            self.game_won_label.pack(pady=20)
    
    def start_timer(self):
        """Start the game timer"""
        self.timer_running = True
        self.update_timer()
    
    def stop_timer(self):
        """Stop the game timer"""
        self.timer_running = False
    
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running:
            self.timer += 1
            self.timer_label.config(text=f"{self.timer:03d}")
            self.after(1000, self.update_timer)
    
    def _go_back(self):
        """Clean up and return to launcher"""
        self.stop_timer()
        self.unbind("<F1>")
        self.controller.create_launcher()
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_timer()
    
    def show_help(self):
        help_text = """Minesweeper Help

How to Play:
• The goal is to reveal all cells without mines
• Numbers indicate how many mines are in adjacent cells
• Use logic to determine where mines are located

Controls:
• Left Click: Reveal a cell
• Right Click: Place/remove a flag
• F1: Show this help

Tips:
• Start by clicking in the middle or corner
• If a number has the same number of flags around it, the remaining cells are safe
• If a number has the same number of unrevealed cells as its value, they are all mines
• The first click is always safe

Difficulty Levels:
• Easy: 8x8 grid with 10 mines
• Medium: 16x16 grid with 40 mines
• Hard: 16x30 grid with 99 mines

Settings:
• You can change the difficulty in the game header"""
        
        messagebox.showinfo("Minesweeper Help", help_text)

# ================= Volleyball App =================
class VolleyballApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        
        # Game constants
        self.width = 800
        self.height = 600
        self.net_height = 20
        self.net_width = 10
        self.ball_size = 20
        self.player_width = 20
        self.player_height = 80
        self.cpu_width = 20
        self.cpu_height = 80
        
        # Game state
        self.game_running = False
        self.game_loop_id = None
        self.keys_pressed = set()
        self.paused = False
        
        # Get difficulty from settings
        self.difficulty = self.settings.get('volleyball_difficulty', "Medium")
        if self.difficulty == "Easy":
            self.cpu_speed = 3
            self.ball_speed_x = 5
            self.ball_speed_y = 5
        elif self.difficulty == "Medium":
            self.cpu_speed = 5
            self.ball_speed_x = 7
            self.ball_speed_y = 7
        else:  # Hard
            self.cpu_speed = 7
            self.ball_speed_x = 9
            self.ball_speed_y = 9
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=self._go_back,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="🏐 Volleyball",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Help button
        btn_help = ttk.Button(
            header,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0), pady=15)
        
        # Score
        self.score_label = tk.Label(
            header,
            text="Player: 0  CPU: 0",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        self.score_label.pack(side="right", padx=15, pady=15)
        
        # Difficulty selector
        diff_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        diff_frame.pack(side="right", padx=15, pady=15)
        
        tk.Label(
            diff_frame,
            text="Difficulty:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT
        ).pack(side="left", padx=(0, 5))
        
        self.diff_var = tk.StringVar(value=self.difficulty)
        diff_menu = ttk.OptionMenu(
            diff_frame,
            self.diff_var,
            self.difficulty,
            "Easy", "Medium", "Hard",
            command=self.change_difficulty
        )
        diff_menu.pack(side="left")
        
        # Game canvas
        canvas_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        canvas_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.width,
            height=self.height,
            bg=COLORS['bg_tertiary'],
            highlightthickness=2,
            highlightbackground=COLORS['accent']
        )
        self.canvas.pack()
        
        # Instructions
        instructions = tk.Label(
            self,
            text="Use A/D or ←/→ to move | W or ↑ to jump | Press P to pause",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=DEFAULT_FONT
        )
        instructions.pack(pady=10)
        
        # Initialize game
        self._reset_game()
        self._start_game()
    
    def _reset_game(self):
        """Reset game state"""
        # Player position
        self.player_x = self.width // 4
        self.player_y = self.height - self.player_height - 10
        self.player_vel_y = 0
        self.player_jumping = False
        # CPU position
        self.cpu_x = 3 * self.width // 4 - self.cpu_width
        self.cpu_y = self.height - self.cpu_height - 10
        self.cpu_vel_y = 0
        self.cpu_jumping = False
        
        # Ball position
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_vel_x = self.ball_speed_x
        self.ball_vel_y = self.ball_speed_y
        
        # Score
        self.player_score = 0
        self.cpu_score = 0
        
        # Clear any existing game objects
        self.canvas.delete("all")
    
    def _start_game(self):
        """Start the game loop"""
        self.game_running = True
        self._draw_elements()
        self._bind_events()
        self._game_loop()
    
    def _go_back(self):
        """Properly stop the game and return to launcher"""
        self.cleanup()
        self.controller.create_launcher()
    
    def cleanup(self):
        """Clean up game resources"""
        self.game_running = False
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        
        # Unbind all events
        try:
            self.unbind("<KeyPress>")
            self.unbind("<KeyRelease>")
            self.unbind("<a>")
            self.unbind("<A>")
            self.unbind("<d>")
            self.unbind("<D>")
            self.unbind("<Left>")
            self.unbind("<Right>")
            self.unbind("<w>")
            self.unbind("<W>")
            self.unbind("<Up>")
            self.unbind("<p>")
            self.unbind("<P>")
            self.unbind("<F1>")
        except:
            pass
    
    def _draw_elements(self):
        """Draw all game elements"""
        self.canvas.delete("all")
        
        # Draw net
        self.canvas.create_rectangle(
            self.width // 2 - self.net_width // 2, 0,
            self.width // 2 + self.net_width // 2, self.net_height,
            fill=COLORS['text_primary'], outline=""
        )
        
        # Draw ground
        self.canvas.create_rectangle(
            0, self.height - 5,
            self.width, self.height,
            fill=COLORS['text_primary'], outline=""
        )
        
        # Draw player
        self.player = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + self.player_width, self.player_y + self.player_height,
            fill=COLORS['accent'], outline=""
        )
        
        # Draw CPU
        self.cpu = self.canvas.create_rectangle(
            self.cpu_x, self.cpu_y,
            self.cpu_x + self.cpu_width, self.cpu_y + self.cpu_height,
            fill=COLORS['text_primary'], outline=""
        )
        
        # Draw ball
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size // 2, self.ball_y - self.ball_size // 2,
            self.ball_x + self.ball_size // 2, self.ball_y + self.ball_size // 2,
            fill=COLORS['warning'], outline=""
        )
        
        # Draw pause indicator
        if self.paused:
            self.pause_text = self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="PAUSED",
                fill=COLORS['warning'],
                font=(DEFAULT_FONT[0], 36, "bold")
            )
    
    def _bind_events(self):
        """Bind keyboard events for smooth movement"""
        self.bind("<KeyPress-a>", self._key_press)
        self.bind("<KeyPress-A>", self._key_press)
        self.bind("<KeyPress-d>", self._key_press)
        self.bind("<KeyPress-D>", self._key_press)
        self.bind("<KeyPress-Left>", self._key_press)
        self.bind("<KeyPress-Right>", self._key_press)
        self.bind("<KeyPress-w>", self._key_press)
        self.bind("<KeyPress-W>", self._key_press)
        self.bind("<KeyPress-Up>", self._key_press)
        self.bind("<KeyRelease-a>", self._key_release)
        self.bind("<KeyRelease-A>", self._key_release)
        self.bind("<KeyRelease-d>", self._key_release)
        self.bind("<KeyRelease-D>", self._key_release)
        self.bind("<KeyRelease-Left>", self._key_release)
        self.bind("<KeyRelease-Right>", self._key_release)
        self.bind("<KeyRelease-w>", self._key_release)
        self.bind("<KeyRelease-W>", self._key_release)
        self.bind("<KeyRelease-Up>", self._key_release)
        self.bind("p", self._toggle_pause)
        self.bind("P", self._toggle_pause)
        self.bind("<F1>", lambda e: self.show_help())
        self.focus_set()
    
    def _key_press(self, event):
        """Handle key press events"""
        self.keys_pressed.add(event.keysym)
    
    def _key_release(self, event):
        """Handle key release events"""
        self.keys_pressed.discard(event.keysym)
    
    def _toggle_pause(self, event=None):
        """Toggle pause state"""
        self.paused = not self.paused
        self._draw_elements()
    
    def _update_player_movement(self):
        """Update player based on pressed keys"""
        # Horizontal movement
        if "a" in self.keys_pressed or "Left" in self.keys_pressed:
            self.player_x = max(self.player_x - 5, 0)
        if "d" in self.keys_pressed or "Right" in self.keys_pressed:
            self.player_x = min(self.player_x + 5, self.width // 2 - self.player_width)
        
        # Jumping
        if ("w" in self.keys_pressed or "Up" in self.keys_pressed) and not self.player_jumping:
            self.player_vel_y = -15
            self.player_jumping = True
    
    def _update_cpu_movement(self):
        """Update CPU AI"""
        # Simple AI: move towards the ball
        if self.ball_x < self.cpu_x:
            self.cpu_x = max(self.cpu_x - self.cpu_speed, self.width // 2)
        elif self.ball_x > self.cpu_x + self.cpu_width:
            self.cpu_x = min(self.cpu_x + self.cpu_speed, self.width - self.cpu_width)
        
        # Jump if ball is coming towards CPU and is at the right height
        if (self.ball_vel_x > 0 and 
            abs(self.ball_x - (self.cpu_x + self.cpu_width // 2)) < 50 and 
            self.ball_y > self.height - 150 and 
            not self.cpu_jumping):
            self.cpu_vel_y = -15
            self.cpu_jumping = True
    
    def _update_physics(self):
        """Update physics for player, CPU, and ball"""
        # Update player physics
        if self.player_jumping:
            self.player_y += self.player_vel_y
            self.player_vel_y += 0.8  # Gravity
            
            # Check if landed
            if self.player_y >= self.height - self.player_height - 10:
                self.player_y = self.height - self.player_height - 10
                self.player_vel_y = 0
                self.player_jumping = False
        
        # Update CPU physics
        if self.cpu_jumping:
            self.cpu_y += self.cpu_vel_y
            self.cpu_vel_y += 0.8  # Gravity
            
            # Check if landed
            if self.cpu_y >= self.height - self.cpu_height - 10:
                self.cpu_y = self.height - self.cpu_height - 10
                self.cpu_vel_y = 0
                self.cpu_jumping = False
        
        # Update ball physics
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y
        self.ball_vel_y += 0.5  # Gravity
        
        # Ball collision with ground
        if self.ball_y + self.ball_size // 2 >= self.height - 5:
            self.ball_y = self.height - 5 - self.ball_size // 2
            self.ball_vel_y *= -0.8  # Bounce with damping
        
        # Ball collision with ceiling
        if self.ball_y - self.ball_size // 2 <= 0:
            self.ball_y = self.ball_size // 2
            self.ball_vel_y *= -0.8  # Bounce with damping
        
        # Ball collision with walls
        if self.ball_x - self.ball_size // 2 <= 0:
            self.ball_x = self.ball_size // 2
            self.ball_vel_x *= -1  # Bounce
        elif self.ball_x + self.ball_size // 2 >= self.width:
            self.ball_x = self.width - self.ball_size // 2
            self.ball_vel_x *= -1  # Bounce
        
        # Ball collision with net
        if (self.ball_x + self.ball_size // 2 >= self.width // 2 - self.net_width // 2 and
            self.ball_x - self.ball_size // 2 <= self.width // 2 + self.net_width // 2 and
            self.ball_y - self.ball_size // 2 <= self.net_height):
            # Determine which side of the net the ball hit
            if self.ball_vel_x > 0:  # Ball moving right
                self.ball_x = self.width // 2 - self.net_width // 2 - self.ball_size // 2
            else:  # Ball moving left
                self.ball_x = self.width // 2 + self.net_width // 2 + self.ball_size // 2
            
            self.ball_vel_x *= -1  # Bounce
        
        # Ball collision with player
        if (self.ball_x + self.ball_size // 2 >= self.player_x and
            self.ball_x - self.ball_size // 2 <= self.player_x + self.player_width and
            self.ball_y + self.ball_size // 2 >= self.player_y and
            self.ball_y - self.ball_size // 2 <= self.player_y + self.player_height):
            
            # Calculate hit position on player (0 to 1)
            hit_pos = (self.ball_x - self.player_x) / self.player_width
            
            # Adjust ball velocity based on hit position
            self.ball_vel_x = 8 * (hit_pos - 0.5) * 2  # -8 to 8
            self.ball_vel_y = -abs(self.ball_vel_y) - 5  # Always bounce up
            
            # Add some of player's velocity to ball
            if self.player_jumping:
                self.ball_vel_y += self.player_vel_y * 0.5
        
        # Ball collision with CPU
        if (self.ball_x + self.ball_size // 2 >= self.cpu_x and
            self.ball_x - self.ball_size // 2 <= self.cpu_x + self.cpu_width and
            self.ball_y + self.ball_size // 2 >= self.cpu_y and
            self.ball_y - self.ball_size // 2 <= self.cpu_y + self.cpu_height):
            
            # Calculate hit position on CPU (0 to 1)
            hit_pos = (self.ball_x - self.cpu_x) / self.cpu_width
            
            # Adjust ball velocity based on hit position
            self.ball_vel_x = 8 * (hit_pos - 0.5) * 2  # -8 to 8
            self.ball_vel_y = -abs(self.ball_vel_y) - 5  # Always bounce up
            
            # Add some of CPU's velocity to ball
            if self.cpu_jumping:
                self.ball_vel_y += self.cpu_vel_y * 0.5
        
        # Scoring
        if self.ball_y + self.ball_size // 2 >= self.height - 5:
            # Ball hit the ground
            if self.ball_x < self.width // 2:
                # Ball on player's side - CPU scores
                self.cpu_score += 1
                self._reset_ball()
            else:
                # Ball on CPU's side - player scores
                self.player_score += 1
                self._reset_ball()
    
    def _reset_ball(self):
        """Reset ball to center"""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        
        # Random initial direction
        if random.random() < 0.5:
            self.ball_vel_x = self.ball_speed_x
        else:
            self.ball_vel_x = -self.ball_speed_x
        
        self.ball_vel_y = -self.ball_speed_y
        
        # Update score display
        self._update_score()
    
    def _update_score(self):
        """Update score display"""
        self.score_label.config(text=f"Player: {self.player_score}  CPU: {self.cpu_score}")
    
    def _redraw_elements(self):
        """Update positions of all game elements"""
        # Update player
        self.canvas.coords(
            self.player,
            self.player_x, self.player_y,
            self.player_x + self.player_width, self.player_y + self.player_height
        )
        
        # Update CPU
        self.canvas.coords(
            self.cpu,
            self.cpu_x, self.cpu_y,
            self.cpu_x + self.cpu_width, self.cpu_y + self.cpu_height
        )
        
        # Update ball
        self.canvas.coords(
            self.ball,
            self.ball_x - self.ball_size // 2, self.ball_y - self.ball_size // 2,
            self.ball_x + self.ball_size // 2, self.ball_y + self.ball_size // 2
        )
    
    def _game_loop(self):
        """Main game loop"""
        if not self.game_running:
            return
        
        if not self.paused:
            # Update player movement
            self._update_player_movement()
            
            # Update CPU movement
            self._update_cpu_movement()
            
            # Update physics
            self._update_physics()
            
            # Update display
            self._redraw_elements()
        
        # Schedule next frame
        self.game_loop_id = self.after(16, self._game_loop)  # ~60 FPS
    
    def change_difficulty(self, difficulty):
        """Change game difficulty"""
        self.difficulty = difficulty
        self.settings['volleyball_difficulty'] = difficulty
        save_settings(self.settings)
        
        # Update game parameters
        if difficulty == "Easy":
            self.cpu_speed = 3
            self.ball_speed_x = 5
            self.ball_speed_y = 5
        elif difficulty == "Medium":
            self.cpu_speed = 5
            self.ball_speed_x = 7
            self.ball_speed_y = 7
        else:  # Hard
            self.cpu_speed = 7
            self.ball_speed_x = 9
            self.ball_speed_y = 9
        
        # Reset game
        self._reset_game()
    
    def show_help(self):
        help_text = """Volleyball Game Help

How to Play:
• Hit the ball over the net to make it land on the opponent's side
• First to 7 points wins!

Controls:
• A/D or ←/→: Move left/right
• W or ↑: Jump
• P: Pause/unpause game
• F1: Show this help

Tips:
• Hit the ball with the edges of your player for sharper angles
• Time your jumps to hit the ball at the highest point
• The CPU gets smarter as the difficulty increases

Difficulty Levels:
• Easy: Slower CPU and ball
• Medium: Moderate CPU and ball speed
• Hard: Faster CPU and ball speed

Settings:
• You can change the difficulty in the game header"""
        
        messagebox.showinfo("Volleyball Game Help", help_text)

# ================= Enhanced Notes App =================
class NotesApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        # Left side
        left_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        left_frame.pack(side="left", fill="y", padx=15, pady=15)
        
        btn_back = ttk.Button(
            left_frame,
            text="← Back",
            command=controller.create_launcher,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left")
        
        title = tk.Label(
            left_frame,
            text="📝 Notes",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0))
        
        # Help button
        btn_help = ttk.Button(
            left_frame,
            text="❓ Help",
            command=self.show_help,
            style="Toolbar.TButton"
        )
        btn_help.pack(side="left", padx=(10, 0))
        
        # Right side buttons
        right_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        right_frame.pack(side="right", fill="y", padx=15, pady=15)
        
        buttons = [
            ("New", self.new_note),
            ("Load", self.load_note),
            ("Save", self.save_note),
            ("Print", self.print_note)
        ]
        
        for text, command in reversed(buttons):
            btn = ttk.Button(
                right_frame,
                text=text,
                command=command,
                style="Toolbar.TButton"
            )
            btn.pack(side="right", padx=(10, 0))
        
        # Text editor with modern styling
        editor_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        editor_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(editor_frame, bg=COLORS['bg_tertiary'])
        scrollbar.pack(side="right", fill="y")
        
        self.text = tk.Text(
            editor_frame,
            font=("Consolas", 14),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            relief="flat",
            bd=10,
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        self.text.pack(expand=True, fill="both")
        scrollbar.config(command=self.text.yview)
        
        # Status bar
        status_frame = tk.Frame(self, bg=COLORS['bg_tertiary'], height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Word count label
        self.word_count_label = tk.Label(
            status_frame,
            text="Words: 0 | Characters: 0",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_tertiary'],
            font=(DEFAULT_FONT[0], 10)
        )
        self.word_count_label.pack(side="right", padx=10, pady=5)
        
        self.current_file = None
        
        # Bind events for word count
        self.text.bind('<KeyRelease>', self.update_word_count)
        self.text.bind('<Button-1>', self.update_word_count)
        
        # Key bindings
        self.bind("<Control-n>", lambda e: self.new_note())
        self.bind("<Control-o>", lambda e: self.load_note())
        self.bind("<Control-s>", lambda e: self.save_note())
        self.bind("<Control-p>", lambda e: self.print_note())
        self.bind("<F1>", lambda e: self.show_help())
    
    def update_word_count(self, event=None):
        """Update word count in status bar"""
        content = self.text.get("1.0", tk.END)
        words = len([word for word in content.split() if word.strip()])
        chars = len(content) - 1  # Subtract 1 for the extra newline
        self.word_count_label.config(text=f"Words: {words} | Characters: {chars}")
    
    def new_note(self):
        if self.text.get("1.0", tk.END).strip():
            if messagebox.askyesno("New Note", "Current note will be lost. Continue?"):
                self.text.delete("1.0", tk.END)
                self.current_file = None
                self.status_label.config(text="New note created")
                self.update_word_count()
        else:
            self.text.delete("1.0", tk.END)
            self.current_file = None
            self.status_label.config(text="New note created")
    
    def save_note(self):
        try:
            if self.current_file is None:
                path = filedialog.asksaveasfilename(
                    initialdir=DATA_DIR,
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="Save Note As"
                )
            else:
                path = self.current_file
            
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    content = self.text.get("1.0", tk.END)
                    # Remove the extra newline that tkinter adds
                    if content.endswith('\n'):
                        content = content[:-1]
                    f.write(content)
                self.current_file = path
                filename = os.path.basename(path)
                self.status_label.config(text=f"Saved: {filename}")
                messagebox.showinfo("Success", f"Note saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note:\n{e}")
            self.status_label.config(text="Save failed")
    
    def load_note(self):
        try:
            path = filedialog.askopenfilename(
                initialdir=DATA_DIR,
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Load Note"
            )
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, data)
                self.current_file = path
                filename = os.path.basename(path)
                self.status_label.config(text=f"Loaded: {filename}")
                self.update_word_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load note:\n{e}")
            self.status_label.config(text="Load failed")
    
    def print_note(self):
        try:
            content = self.text.get("1.0", tk.END)
            if not content.strip():
                messagebox.showwarning("Empty Note", "There is nothing to print.")
                return
            
            # Create a temporary file for printing
            temp_file = os.path.join(DATA_DIR, "temp_print.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Print the file
            if platform.system() == "Windows":
                os.startfile(temp_file, "print")
            elif platform.system() == "Darwin":  # macOS
                os.system(f"lpr '{temp_file}'")
            else:  # Linux
                os.system(f"lpr '{temp_file}'")
            
            messagebox.showinfo("Success", "Note sent to printer!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print note:\n{e}")
    
    def show_help(self):
        help_text = """Notes App Help

Features:
• Create, edit, and save text notes
• Load existing notes from your computer
• Print notes directly from the app
• Real-time word and character count

Keyboard Shortcuts:
• Ctrl+N: Create new note
• Ctrl+O: Open existing note
• Ctrl+S: Save current note
• Ctrl+P: Print current note
• F1: Show this help

Tips:
• Your notes are saved in plain text format
• You can open and edit any text file
• The app automatically counts words and characters
• Use the status bar to see file information"""
        
        messagebox.showinfo("Notes App Help", help_text)

# ================= Enhanced Settings App =================
class SettingsApp(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.settings = settings
        
        # Modern header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        btn_back = ttk.Button(
            header,
            text="← Back",
            command=controller.create_launcher,
            style="Toolbar.TButton"
        )
        btn_back.pack(side="left", padx=15, pady=15)
        
        title = tk.Label(
            header,
            text="⚙️ Settings",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 18, "bold")
        )
        title.pack(side="left", padx=(10, 0), pady=15)
        
        # Settings content with scrollable frame
        main_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create scrollable content
        canvas = tk.Canvas(main_frame, bg=COLORS['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content_frame = scrollable_frame
        
        # Window Size Section
        size_section = self.create_section(content_frame, "🖥️ Window Settings")
        
        # Width setting
        width_frame = tk.Frame(size_section, bg=COLORS['bg_secondary'])
        width_frame.pack(fill='x', pady=5)
        
        lbl_width = tk.Label(
            width_frame,
            text="Width:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        lbl_width.pack(side='left', padx=10)
        
        self.width_var = tk.IntVar(value=self.controller.winfo_width())
        width_entry = ttk.Entry(
            width_frame,
            textvariable=self.width_var,
            width=10,
            style="Modern.TEntry"
        )
        width_entry.pack(side='left', padx=(10, 0))
        
        # Height setting
        height_frame = tk.Frame(size_section, bg=COLORS['bg_secondary'])
        height_frame.pack(fill='x', pady=5)
        
        lbl_height = tk.Label(
            height_frame,
            text="Height:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        lbl_height.pack(side='left', padx=10)
        
        self.height_var = tk.IntVar(value=self.controller.winfo_height())
        height_entry = ttk.Entry(
            height_frame,
            textvariable=self.height_var,
            width=10,
            style="Modern.TEntry"
        )
        height_entry.pack(side='left', padx=(10, 0))
        
        # Apply button
        btn_apply = ttk.Button(
            size_section,
            text="Apply Size Changes",
            command=self.apply_size,
            style="Modern.TButton"
        )
        btn_apply.pack(pady=15)
        
        # Pong Settings Section
        pong_section = self.create_section(content_frame, "🏓 Pong Settings")
        
        # Player paddle color
        paddle_frame = tk.Frame(pong_section, bg=COLORS['bg_secondary'])
        paddle_frame.pack(fill='x', pady=5)
        
        lbl_paddle = tk.Label(
            paddle_frame,
            text="Player Paddle:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        lbl_paddle.pack(side='left', padx=10)
        
        self.paddle_color_var = tk.StringVar(value=self.settings.get('pong_player_paddle_color', COLORS['accent']))
        
        paddle_color_btn = tk.Button(
            paddle_frame,
            text="Choose Color",
            command=self.choose_paddle_color,
            bg=self.paddle_color_var.get(),
            fg=COLORS['text_primary'],
            relief="flat",
            bd=0,
            font=DEFAULT_FONT,
            cursor="hand2",
            width=15
        )
        paddle_color_btn.pack(side='left', padx=(10, 0))
        
        # Tetris Settings Section
        tetris_section = self.create_section(content_frame, "🧩 Tetris Settings")
        
        # Block colors
        colors_frame = tk.Frame(tetris_section, bg=COLORS['bg_secondary'])
        colors_frame.pack(fill='x', pady=5)
        
        lbl_colors = tk.Label(
            colors_frame,
            text="Block Colors:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        lbl_colors.pack(side='left', padx=10)
        
        reset_colors_btn = ttk.Button(
            colors_frame,
            text="Reset to Default",
            command=self.reset_tetris_colors,
            style="Modern.TButton"
        )
        reset_colors_btn.pack(side='left', padx=(10, 0))
        
        # Color preview
        self.color_preview_frame = tk.Frame(tetris_section, bg=COLORS['bg_secondary'])
        self.color_preview_frame.pack(fill='x', pady=10)
        
        self.update_tetris_color_preview()
        
        # Minesweeper Settings Section
        minesweeper_section = self.create_section(content_frame, "💣 Minesweeper Settings")
        
        # Default difficulty
        diff_frame = tk.Frame(minesweeper_section, bg=COLORS['bg_secondary'])
        diff_frame.pack(fill='x', pady=5)
        
        lbl_diff = tk.Label(
            diff_frame,
            text="Default Difficulty:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        lbl_diff.pack(side='left', padx=10)
        
        self.minesweeper_diff_var = tk.StringVar(value=self.settings.get('minesweeper_difficulty', 'Medium'))
        
        diff_menu = ttk.OptionMenu(
            diff_frame,
            self.minesweeper_diff_var,
            self.minesweeper_diff_var.get(),
            "Easy", "Medium", "Hard",
            command=lambda x: self.minesweeper_diff_var.set(x)
        )
        diff_menu.pack(side='left', padx=(10, 0))
        
        # Volleyball Settings Section
        volleyball_section = self.create_section(content_frame, "🏐 Volleyball Settings")
        
        # Default difficulty
        vball_diff_frame = tk.Frame(volleyball_section, bg=COLORS['bg_secondary'])
        vball_diff_frame.pack(fill='x', pady=5)
        
        vball_lbl_diff = tk.Label(
            vball_diff_frame,
            text="Default Difficulty:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            width=15,
            anchor='w'
        )
        vball_lbl_diff.pack(side='left', padx=10)
        
        self.volleyball_diff_var = tk.StringVar(value=self.settings.get('volleyball_difficulty', 'Medium'))
        
        vball_diff_menu = ttk.OptionMenu(
            vball_diff_frame,
            self.volleyball_diff_var,
            self.volleyball_diff_var.get(),
            "Easy", "Medium", "Hard",
            command=lambda x: self.volleyball_diff_var.set(x)
        )
        vball_diff_menu.pack(side='left', padx=(10, 0))
        
        # System Info Section
        info_section = self.create_section(content_frame, "ℹ️ System Information")
        
        info_items = [
            ("Platform:", platform.system()),
            ("Python Version:", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("Tkinter Version:", str(tk.TkVersion)),
            ("Data Directory:", DATA_DIR),
            ("Minimum Size:", "600 x 700 pixels"),
            ("Current Size:", f"{self.controller.winfo_width()} x {self.controller.winfo_height()} pixels")
        ]
        
        for label, value in info_items:
            self.create_info_item(info_section, label, value)
        
        # Theme Section
        theme_section = self.create_section(content_frame, "🎨 Theme Information")
        
        theme_info = tk.Label(
            theme_section,
            text="Current theme: Modern Dark\n• Optimized for cross-platform compatibility\n• Supports high-DPI displays\n• Consistent color scheme across all apps\n• Smooth animations and hover effects",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            justify='left',
            anchor='w'
        )
        theme_info.pack(anchor='w', padx=15, pady=10)
        
        # Performance Section
        perf_section = self.create_section(content_frame, "⚡ Performance Settings")
        
        perf_info = tk.Label(
            perf_section,
            text="• Pong and Volleyball games run at ~60 FPS for smooth gameplay\n• Canvas app uses hardware acceleration when available\n• All apps are optimized for IDLE compatibility\n• Memory usage is minimized through proper cleanup",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            justify='left',
            anchor='w'
        )
        perf_info.pack(anchor='w', padx=15, pady=10)
        
        # Save settings button
        save_frame = tk.Frame(content_frame, bg=COLORS['bg_primary'])
        save_frame.pack(fill='x', pady=20)
        
        btn_save = ttk.Button(
            save_frame,
            text="Save All Settings",
            command=self.save_all_settings,
            style="Modern.TButton"
        )
        btn_save.pack()
    
    def create_section(self, parent, title):
        """Create a styled section with title"""
        section_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        section_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            section_frame,
            text=title,
            fg=COLORS['text_primary'],
            bg=COLORS['bg_primary'],
            font=(DEFAULT_FONT[0], 16, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Content area
        content_area = tk.Frame(section_frame, bg=COLORS['bg_secondary'], relief="solid", bd=1)
        content_area.pack(fill='x', padx=0)
        
        return content_area
    
    def create_info_item(self, parent, label, value):
        """Create an info item row"""
        item_frame = tk.Frame(parent, bg=COLORS['bg_secondary'])
        item_frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(
            item_frame,
            text=label,
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=(DEFAULT_FONT[0], 12, "bold"),
            width=20,
            anchor='w'
        )
        lbl.pack(side='left', padx=15, pady=5)
        
        val = tk.Label(
            item_frame,
            text=str(value),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            anchor='w'
        )
        val.pack(side='left', padx=(10, 15), pady=5)
    
    def apply_size(self):
        try:
            w = self.width_var.get()
            h = self.height_var.get()
            
            if w < 600 or h < 700:
                messagebox.showwarning(
                    "Invalid Size", 
                    "Minimum window size is 600 x 700 pixels.\nThis ensures all apps display correctly."
                )
                return
            
            if w > 2000 or h > 1500:
                if not messagebox.askyesno(
                    "Large Window Size", 
                    f"You're setting a very large window size ({w}x{h}).\nThis might not fit on smaller screens. Continue?"
                ):
                    return
            
            self.controller.geometry(f"{w}x{h}")
            messagebox.showinfo("Success", f"Window size changed to {w} x {h} pixels")
            
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers for width and height.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply size changes:\n{e}")
    
    def choose_paddle_color(self):
        color = colorchooser.askcolor(initialcolor=self.paddle_color_var.get(), title="Choose Paddle Color")
        if color[1]:
            self.paddle_color_var.set(color[1])
            # Update button background to show selected color
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for section in widget.winfo_children():
                        if isinstance(section, tk.Frame):
                            for item in section.winfo_children():
                                if isinstance(item, tk.Frame):
                                    for child in item.winfo_children():
                                        if isinstance(child, tk.Button) and child["text"] == "Choose Color":
                                            child.config(bg=color[1])
    
    def reset_tetris_colors(self):
        self.settings['tetris_block_colors'] = DEFAULT_SETTINGS['tetris_block_colors'].copy()
        self.update_tetris_color_preview()
    
    def update_tetris_color_preview(self):
        # Clear existing preview
        for widget in self.color_preview_frame.winfo_children():
            widget.destroy()
        
        # Create color preview
        preview_label = tk.Label(
            self.color_preview_frame,
            text="Block Color Preview:",
            fg=COLORS['text_primary'],
            bg=COLORS['bg_secondary'],
            font=DEFAULT_FONT,
            anchor='w'
        )
        preview_label.pack(anchor='w', padx=15, pady=(5, 10))
        
        # Create color boxes
        colors_frame = tk.Frame(self.color_preview_frame, bg=COLORS['bg_secondary'])
        colors_frame.pack(anchor='w', padx=15, pady=(0, 10))
        
        colors = self.settings.get('tetris_block_colors', DEFAULT_SETTINGS['tetris_block_colors'])
        for i, color in enumerate(colors):
            color_box = tk.Frame(
                colors_frame, 
                bg=color, 
                width=30, 
                height=30,
                relief="solid",
                bd=1
            )
            color_box.pack(side="left", padx=2)
            color_box.pack_propagate(False)
    
    def save_all_settings(self):
        try:
            # Update settings with current values
            self.settings['pong_player_paddle_color'] = self.paddle_color_var.get()
            self.settings['minesweeper_difficulty'] = self.minesweeper_diff_var.get()
            self.settings['volleyball_difficulty'] = self.volleyball_diff_var.get()
            
            # Save to file
            save_settings(self.settings)
            messagebox.showinfo("Success", "All settings have been saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
