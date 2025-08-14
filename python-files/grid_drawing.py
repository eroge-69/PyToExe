#
# An advanced desktop photo editing application with a modern, clean UI
# using the ttkbootstrap library. It maintains low-resource usage for
# compatibility with older PCs (2GB DDR2 RAM, Pentium dual-core).
#
# This version includes:
# - A modern, sleek user interface with a ttkbootstrap theme.
# - Image filters: Black & White, Line Art, Sepia, Sharpen.
# - A grid overlay with customizable size.
# - A4 Portrait and Landscape display modes based on user-input DPI.
# - Efficient image processing to keep memory usage low.
#
# Author: Gemini
# Date: 2025-08-15
#

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageOps
import ttkbootstrap as ttk

class PhotoLineApp:
    def __init__(self, root):
        """Initializes the main application window and its components."""
        self.root = root
        self.root.title("Photo Line Desktop")
        
        # Use a ttkbootstrap theme for a modern look
        self.style = ttk.Style(theme='superhero') # You can change this to 'lumen', 'cosmo', etc.
        self.root.geometry("1000x800")

        # Application state variables
        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.current_mode = "color"
        self.grid_lines_visible = False
        self.current_filename = ""
        
        # A4 paper dimensions in millimeters
        self.A4_WIDTH_MM = 210
        self.A4_HEIGHT_MM = 297

      