import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os
import subprocess
import win32print
import win32ui
from PIL import ImageWin

class PVCCardPrinter:
    def __init__(self, root):
        self.root = root
        self.root.title("PVC Card Printer - Epson L3250")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Center the window on screen
        self.center_window()
        
        # Current design elements
        self.elements = []
        self.selected_element = None
        self.current_tool = None
        
        # Card dimensions (standard CR80 card size)
        self.card_width = 852  # pixels (3.375 inches at 300 DPI)
        self.card_height = 540  # pixels (2.125 inches at 300 DPI)
        
        # Colors
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.accent_color = "#e74c3c"
        
        # Fonts
        self.title_font = ("Arial", 16, "bold")
        self.header_font = ("Arial", 12, "bold")
        self.normal_font = ("Arial", 10)
        
        # Printer settings
        self.printer_name = self.get_epson_l3250_printer()
        
        self.setup_ui()
        self.create_new_design()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2)