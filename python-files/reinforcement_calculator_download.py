#!/usr/bin/env python3
"""
NRS Reinforcement Quantity Calculator
A professional desktop application for calculating reinforcement requirements
for construction projects with ACI standard bar sizes.

Author: NRS Construction Calculator Pro
Version: 1.0
Date: 2025
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys
import os

class ReinforcementCalculator:
    """Main application class for the NRS Reinforcement Quantity Calculator"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # ACI Standard Bar Properties (Diameter in inches, Weight in lb/ft)
        self.bar_properties = {
            2: {"diameter": 0.25, "weight": 0.25},
            3: {"diameter": 0.375, "weight": 0.376},
            4: {"diameter": 0.5, "weight": 0.668},
            5: {"diameter": 0.625, "weight": 1.043},
            6: {"diameter": 0.75, "weight": 1.502},
            7: {"diameter": 0.875, "weight": 2.044},
            8: {"diameter": 1.0, "weight": 2.670},
            9: {"diameter": 1.128, "weight": 3.400},
            10: {"diameter": 1.27, "weight": 4.303},
            11: {"diameter": 1.41, "weight": 5.313}
        }
        
        self.create_widgets()
        
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("🏗️ NRS Reinforcement Quantity Calculator v1.0")
        self.root.geometry("750x650")
        self.root.configure(bg='#f0f2f5')
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(700, 600)
        
        # Center window on screen
        self.center_window()
        
        # Configure window icon (if available)
        try:
            self.root.iconbitmap('calculator.ico')  # Optional icon file
        except:
            pass  # Continue without icon if not available
            
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f2f5')
        style.configure('Section.TLabelframe.Label', font=('Arial', 10, 'bold'))
        style.configure('Calculate.TButton', font=('Arial', 11, 'bold'), padding=(15, 8))
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#f0f2f5')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header section
        self.create_header(main_container)
        
        # Main content frame
        content_frame = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        content_frame.pack(fill='both', expand=True, pady=(8, 0))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=12, pady=12)
        
        # Create tabs
        self.create_input_tab()
        self.create_results_tab()
        self.create_about_tab()
        
    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 8))
        
        # Title
        title_label = ttk.Label(header_frame, text="🏗️ NRS Reinforcement Quantity Calculator", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Professional ACI Standard Bar Calculations", 
                                 font=('Arial', 9), bg='#f0f2f5', fg='#666')
        subtitle_label.pack(pady=(1, 0))
        
    def create_input_tab(self):
        """Create the input parameters tab"""
        # Input tab frame
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="📊 Input Parameters")
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.input_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create input sections
        self.create_area_section()
        self.create_dimensions_section()
        self.create_reinforcement_section()
        self.create_stock_section()
        self.create_bar_section()
        self.create_calculate_section()
        
    def create_area_section(self):
        """Create area input section"""
        area_frame = ttk.LabelFrame(self.scrollable_frame, text="📐 Project Area (Alternative Method)", 
                                   padding=(12, 8))
        area_frame.pack(fill='x', padx=12, pady=8)
        
        tk.Label(area_frame, text="Total Area (sq ft):", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=4)
        
        self.total_area_var = tk.StringVar()
        area_entry = tk.Entry(area_frame, textvariable=self.total_area_var, 
                             font=('Arial', 10), width=18, relief='solid', bd=1)
        area_entry.grid(row=0, column=1, sticky='w', pady=4)
        
        help_label = tk.Label(area_frame, 
                             text="💡 Leave blank to use Length × Width below, or enter total area to override",
                             font=('Arial', 8), fg='#666', wraplength=350)
        help_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(4, 0))
        
    def create_dimensions_section(self):
        """Create dimensions input section"""
        dim_frame = ttk.LabelFrame(self.scrollable_frame, text="📏 Slab Dimensions", 
                                  padding=(12, 8))
        dim_frame.pack(fill='x', padx=12, pady=8)
        
        # Length inputs
        tk.Label(dim_frame, text="Length:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=6)
        
        length_frame = tk.Frame(dim_frame)
        length_frame.grid(row=0, column=1, sticky='w', pady=6)
        
        self.length_feet_var = tk.StringVar(value="50")
        self.length_inches_var = tk.StringVar(value="0")
        
        tk.Entry(length_frame, textvariable=self.length_feet_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(length_frame, text="ft", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 6))
        tk.Entry(length_frame, textvariable=self.length_inches_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(length_frame, text="in", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 0))
        
        # Width inputs
        tk.Label(dim_frame, text="Width:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky='w', padx=(0, 8), pady=6)
        
        width_frame = tk.Frame(dim_frame)
        width_frame.grid(row=1, column=1, sticky='w', pady=6)
        
        self.width_feet_var = tk.StringVar(value="40")
        self.width_inches_var = tk.StringVar(value="0")
        
        tk.Entry(width_frame, textvariable=self.width_feet_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(width_frame, text="ft", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 6))
        tk.Entry(width_frame, textvariable=self.width_inches_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(width_frame, text="in", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 0))
        
    def create_reinforcement_section(self):
        """Create reinforcement settings section"""
        reinf_frame = ttk.LabelFrame(self.scrollable_frame, text="⚙️ Reinforcement Settings", 
                                    padding=(12, 8))
        reinf_frame.pack(fill='x', padx=12, pady=8)
        
        # Spacing inputs
        tk.Label(reinf_frame, text="Spacing:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=6)
        
        spacing_frame = tk.Frame(reinf_frame)
        spacing_frame.grid(row=0, column=1, sticky='w', pady=6)
        
        self.spacing_feet_var = tk.StringVar(value="1")
        self.spacing_inches_var = tk.StringVar(value="0")
        
        tk.Entry(spacing_frame, textvariable=self.spacing_feet_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(spacing_frame, text="ft", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 6))
        tk.Entry(spacing_frame, textvariable=self.spacing_inches_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(spacing_frame, text="in", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 0))
        
        # Lap length inputs
        tk.Label(reinf_frame, text="Lap Length:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky='w', padx=(0, 8), pady=6)
        
        lap_frame = tk.Frame(reinf_frame)
        lap_frame.grid(row=1, column=1, sticky='w', pady=6)
        
        self.lap_feet_var = tk.StringVar(value="3")
        self.lap_inches_var = tk.StringVar(value="0")
        
        tk.Entry(lap_frame, textvariable=self.lap_feet_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(lap_frame, text="ft", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 6))
        tk.Entry(lap_frame, textvariable=self.lap_inches_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(lap_frame, text="in", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 0))
        
    def create_stock_section(self):
        """Create stock length section"""
        stock_frame = ttk.LabelFrame(self.scrollable_frame, text="📦 Stock Bar Length", 
                                    padding=(12, 8))
        stock_frame.pack(fill='x', padx=12, pady=8)
        
        tk.Label(stock_frame, text="Stock Length:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=6)
        
        stock_input_frame = tk.Frame(stock_frame)
        stock_input_frame.grid(row=0, column=1, sticky='w', pady=6)
        
        self.stock_feet_var = tk.StringVar(value="30")
        self.stock_inches_var = tk.StringVar(value="0")
        
        tk.Entry(stock_input_frame, textvariable=self.stock_feet_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(stock_input_frame, text="ft", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 6))
        tk.Entry(stock_input_frame, textvariable=self.stock_inches_var, width=6, 
                font=('Arial', 9), justify='center', relief='solid', bd=1).pack(side='left')
        tk.Label(stock_input_frame, text="in", font=('Arial', 9, 'bold'), fg='#666').pack(side='left', padx=(2, 0))
        
        tk.Label(stock_frame, text="💡 Standard lengths: 20', 30', 40', 60' - adjust based on available stock",
                font=('Arial', 8), fg='#666', wraplength=350).grid(
                row=1, column=0, columnspan=2, sticky='w', pady=(4, 0))
        
    def create_bar_section(self):
        """Create bar specifications section"""
        bar_frame = ttk.LabelFrame(self.scrollable_frame, text="🔩 Bar Specifications", 
                                  padding=(12, 8))
        bar_frame.pack(fill='x', padx=12, pady=8)
        
        tk.Label(bar_frame, text="Bar Size (ACI):", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 8), pady=6)
        
        self.bar_size_var = tk.StringVar(value="4")
        bar_options = [str(size) for size in self.bar_properties.keys()]
        
        self.bar_combo = ttk.Combobox(bar_frame, textvariable=self.bar_size_var, 
                                     values=bar_options, width=20, font=('Arial', 9),
                                     state='readonly')
        self.bar_combo.grid(row=0, column=1, sticky='w', pady=6)
        
        # Bar info display
        self.bar_info_var = tk.StringVar()
        self.update_bar_info()
        
        self.bar_info_label = tk.Label(bar_frame, textvariable=self.bar_info_var,
                                      font=('Arial', 8), fg='#666', wraplength=350)
        self.bar_info_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(4, 0))
        
        # Bind selection change
        self.bar_combo.bind('<<ComboboxSelected>>', lambda e: self.update_bar_info())
        
    def create_calculate_section(self):
        """Create calculate button section"""
        calc_frame = tk.Frame(self.scrollable_frame)
        calc_frame.pack(pady=20)
        
        self.calc_button = tk.Button(calc_frame, 
                                    text="🧮 Calculate Reinforcement Quantity", 
                                    font=('Arial', 12, 'bold'), 
                                    bg='#4CAF50', fg='white',
                                    relief='raised', bd=3, 
                                    padx=25, pady=12,
                                    cursor='hand2',
                                    command=self.calculate_reinforcement)
        self.calc_button.pack()
        
        # Bind hover effects
        def on_enter(e):
            self.calc_button.config(bg='#45a049')
        def on_leave(e):
            self.calc_button.config(bg='#4CAF50')
            
        self.calc_button.bind("<Enter>", on_enter)
        self.calc_button.bind("<Leave>", on_leave)
        
    def create_results_tab(self):
        """Create results display tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📋 Results")
        
        # Results canvas for scrolling
        results_canvas = tk.Canvas(self.results_frame, bg='white', highlightthickness=0)
        results_scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", 
                                         command=results_canvas.yview)
        self.results_scrollable = ttk.Frame(results_canvas)
        
        self.results_scrollable.bind(
            "<Configure>",
            lambda e: results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        )
        
        results_canvas.create_window((0, 0), window=self.results_scrollable, anchor="nw")
        results_canvas.configure(yscrollcommand=results_scrollbar.set)
        
        results_canvas.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Initial message
        self.no_results_label = tk.Label(self.results_scrollable, 
                                        text="📊 Click 'Calculate' to see results here", 
                                        font=('Arial', 12), fg='#666')
        self.no_results_label.pack(expand=True, pady=80)
        
    def create_about_tab(self):
        """Create about/help tab"""
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text="ℹ️ About")
        
        about_text = tk.Text(about_frame, wrap='word', font=('Arial', 10), 
                            relief='flat', bg='white', fg='#333', padx=20, pady=20)
        about_scrollbar = ttk.Scrollbar(about_frame, orient="vertical", command=about_text.yview)
        about_text.configure(yscrollcommand=about_scrollbar.set)
        
        about_content = """
🏗️ NRS REINFORCEMENT QUANTITY CALCULATOR v1.0

OVERVIEW:
This professional application calculates reinforcement requirements for construction projects according to ACI standards.

FEATURES:
✓ Flexible area input (total area OR length×width)
✓ Custom stock bar length settings
✓ ACI standard bar sizes (#2 through #11)
✓ Feet & inches input format
✓ Comprehensive lap length calculations
✓ Professional results with weight calculations

HOW TO USE:

1. AREA INPUT:
   - Option 1: Enter total area in sq ft (leave length/width blank)
   - Option 2: Enter length and width separately

2. REINFORCEMENT SETTINGS:
   - Set spacing between bars (typically 12" = 1'0")
   - Set lap length for continuity (typically 3'0")

3. STOCK SETTINGS:
   - Enter your available stock bar length
   - Common lengths: 20', 30', 40', 60'

4. BAR SELECTION:
   - Choose ACI standard bar size
   - View diameter and weight specifications

5. CALCULATE:
   - Click calculate to get comprehensive results
   - View total linear feet and stock bars needed

ACI BAR SPECIFICATIONS:
#2: 1/4" diameter, 0.25 lb/ft
#3: 3/8" diameter, 0.376 lb/ft
#4: 1/2" diameter, 0.668 lb/ft
#5: 5/8" diameter, 1.043 lb/ft
#6: 3/4" diameter, 1.502 lb/ft
#7: 7/8" diameter, 2.044 lb/ft
#8: 1" diameter, 2.670 lb/ft
#9: 1-1/8" diameter, 3.400 lb/ft
#10: 1-1/4" diameter, 4.303 lb/ft
#11: 1-3/8" diameter, 5.313 lb/ft

CALCULATION METHOD:
1. Determines number of bars in each direction based on spacing
2. Calculates linear feet for both directions
3. Adds lap lengths for bar continuity
4. Determines total stock bars needed
5. Calculates total weight

TECHNICAL SUPPORT:
For technical questions or feature requests, please contact your system administrator.

COPYRIGHT:
© 2025 NRS Construction Calculator Pro. All rights reserved.
Licensed under MIT License.
        """
        
        about_text.insert('1.0', about_content)
        about_text.config(state='disabled')  # Make read-only
        
        about_text.pack(side="left", fill="both", expand=True)
        about_scrollbar.pack(side="right", fill="y")
        
    def update_bar_info(self):
        """Update bar information display"""
        try:
            bar_size = int(self.bar_size_var.get())
            props = self.bar_properties[bar_size]
            info = f"#{bar_size}: {props['diameter']}\" diameter, {props['weight']} lb/ft"
            self.bar_info_var.set(info)
        except:
            self.bar_info_var.set("Select a bar size")
            
    def feet_inches_to_decimal(self, feet_str, inches_str):
        """Convert feet and inches to decimal feet"""
        try:
            feet = float(feet_str) if feet_str.strip() else 0
            inches = float(inches_str) if inches_str.strip() else 0
            if inches >= 12:
                raise ValueError("Inches must be less than 12")
            return feet + inches / 12
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")
            
    def validate_inputs(self):
        """Validate all input fields"""
        try:
            total_area = float(self.total_area_var.get()) if self.total_area_var.get().strip() else 0
            
            if total_area > 0:
                if total_area <= 0:
                    return "Please enter a valid total area greater than zero."
            else:
                length = self.feet_inches_to_decimal(self.length_feet_var.get(), 
                                                   self.length_inches_var.get())
                width = self.feet_inches_to_decimal(self.width_feet_var.get(), 
                                                  self.width_inches_var.get())
                
                if length <= 0 or width <= 0:
                    return "Please enter valid length and width dimensions, or use total area."
                    
            spacing = self.feet_inches_to_decimal(self.spacing_feet_var.get(), 
                                                 self.spacing_inches_var.get())
            stock_length = self.feet_inches_to_decimal(self.stock_feet_var.get(), 
                                                     self.stock_inches_var.get())
            
            if spacing <= 0:
                return "Please enter valid spacing greater than zero."
            if stock_length <= 0:
                return "Please enter valid stock length greater than zero."
                
            # Validate bar size
            if not self.bar_size_var.get() or int(self.bar_size_var.get()) not in self.bar_properties:
                return "Please select a valid bar size."
                
            return None
            
        except ValueError as e:
            return f"Input error: {str(e)}"
        except Exception as e:
            return f"Validation error: {str(e)}"
            
    def calculate_reinforcement(self):
        """Main calculation function"""
        # Validate inputs
        error = self.validate_inputs()
        if error:
            messagebox.showerror("Input Error", error)
            return
            
        try:
            # Get area
            total_area_input = float(self.total_area_var.get()) if self.total_area_var.get().strip() else 0
            
            if total_area_input > 0:
                area = total_area_input
                length = width = math.sqrt(area)
                input_method = "Total Area"
            else:
                length = self.feet_inches_to_decimal(self.length_feet_var.get(), 
                                                   self.length_inches_var.get())
                width = self.feet_inches_to_decimal(self.width_feet_var.get(), 
                                                  self.width_inches_var.get())
                area = length * width
                input_method = "Length × Width"
                
            # Get other parameters
            spacing = self.feet_inches_to_decimal(self.spacing_feet_var.get(), 
                                                 self.spacing_inches_var.get())
            lap_length = self.feet_inches_to_decimal(self.lap_feet_var.get(), 
                                                   self.lap_inches_var.get())
            stock_length = self.feet_inches_to_decimal(self.stock_feet_var.get(), 
                                                     self.stock_inches_var.get())
            bar_size = int(self.bar_size_var.get())
            
            # Perform calculations
            bars_length_direction = math.ceil(width / spacing) + 1
            bars_width_direction = math.ceil(length / spacing) + 1
            
            linear_feet_length = bars_length_direction * length
            linear_feet_width = bars_width_direction * width
            total_linear_feet_before_laps = linear_feet_length + linear_feet_width
            
            # Calculate laps needed
            laps_in_length = bars_length_direction * math.floor(length / stock_length)
            laps_in_width = bars_width_direction * math.floor(width / stock_length)
            total_laps = laps_in_length + laps_in_width
            
            total_lap_length = total_laps * lap_length
            total_linear_feet_with_laps = total_linear_feet_before_laps + total_lap_length
            
            stock_bars_needed = math.ceil(total_linear_feet_with_laps / stock_length)
            
            # Get bar properties
            bar_props = self.bar_properties[bar_size]
            total_weight = total_linear_feet_with_laps * bar_props['weight']
            
            # Prepare results
            results = {
                'input_method': input_method,
                'area': area,
                'length': length,
                'width': width,
                'total_area_input': total_area_input,
                'bars_length_direction': bars_length_direction,
                'bars_width_direction': bars_width_direction,
                'linear_feet_length': linear_feet_length,
                'linear_feet_width': linear_feet_width,
                'total_linear_feet_before_laps': total_linear_feet_before_laps,
                'total_laps': total_laps,
                'total_lap_length': total_lap_length,
                'total_linear_feet_with_laps': total_linear_feet_with_laps,
                'stock_bars_needed': stock_bars_needed,
                'bar_size': bar_size,
                'bar_diameter': bar_props['diameter'],
                'bar_weight': bar_props['weight'],
                'total_weight': total_weight,
                'stock_length': stock_length,
                'spacing': spacing,
                'lap_length': lap_length
            }
            
            # Display results and switch to results tab
            self.display_results(results)
            self.notebook.select(1)  # Switch to results tab
            
            # Show success message
            messagebox.showinfo("Calculation Complete", 
                               f"Calculation completed successfully!\n\n"
                               f"Total Stock Bars Needed: {stock_bars_needed} bars\n"
                               f"Total Linear Feet: {total_linear_feet_with_laps:.2f} ft\n"
                               f"Total Weight: {total_weight:.2f} lbs")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", 
                               f"An error occurred during calculation:\n\n{str(e)}")
            
    def display_results(self, results):
        """Display comprehensive calculation results"""
        # Clear previous results
        for widget in self.results_scrollable.winfo_children():
            widget.destroy()
            
        # Main results container
        main_results_frame = tk.Frame(self.results_scrollable, bg='white')
        main_results_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title_frame = tk.Frame(main_results_frame, bg='#e8f5e8', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(title_frame, text="📊 CALCULATION RESULTS", 
                font=('Arial', 14, 'bold'), bg='#e8f5e8', fg='#155724').pack(pady=10)
        
        # Input method info
        info_frame = tk.Frame(main_results_frame, bg='#d1ecf1', relief='solid', bd=1)
        info_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(info_frame, text=f"Input Method: {results['input_method']}", 
                font=('Arial', 10, 'bold'), bg='#d1ecf1', fg='#0c5460').pack(pady=6)
        
        if results['input_method'] == "Total Area":
            tk.Label(info_frame, text=f"Calculated Dimensions: {results['length']:.2f}' × {results['width']:.2f}'", 
                    font=('Arial', 9), bg='#d1ecf1', fg='#0c5460').pack(pady=(0, 6))
        else:
            tk.Label(info_frame, text=f"Slab Dimensions: {results['length']:.2f}' × {results['width']:.2f}'", 
                    font=('Arial', 9), bg='#d1ecf1', fg='#0c5460').pack(pady=(0, 6))
        
        # Input parameters summary
        params_frame = ttk.LabelFrame(main_results_frame, text="📋 Input Parameters Used", 
                                     padding=(12, 8))
        params_frame.pack(fill='x', pady=(0, 12))
        
        params_data = [
            ("Spacing:", f"{results['spacing']:.2f} ft"),
            ("Lap Length:", f"{results['lap_length']:.2f} ft"),
            ("Stock Length:", f"{results['stock_length']:.2f} ft"),
            ("Bar Size:", f"#{results['bar_size']} ({results['bar_diameter']}\" dia)")
        ]
        
        for i, (label, value) in enumerate(params_data):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(params_frame, text=label, font=('Arial', 9), anchor='w').grid(
                row=row, column=col, sticky='w', padx=(0, 8), pady=2)
            tk.Label(params_frame, text=value, font=('Arial', 9, 'bold'), anchor='w').grid(
                row=row, column=col+1, sticky='w', padx=(0, 25), pady=2)
        
        # Detailed calculations
        calc_frame = ttk.LabelFrame(main_results_frame, text="🔢 Detailed Calculations", 
                                   padding=(12, 8))
        calc_frame.pack(fill='x', pady=(0, 12))
        
        calc_data = [
            ("Slab Area:", f"{results['area']:.2f} sq ft"),
            ("Bars in Length Direction:", f"{results['bars_length_direction']} bars"),
            ("Bars in Width Direction:", f"{results['bars_width_direction']} bars"),
            ("Linear Feet (Length Direction):", f"{results['linear_feet_length']:.2f} ft"),
            ("Linear Feet (Width Direction):", f"{results['linear_feet_width']:.2f} ft"),
            ("Total Linear Feet (before laps):", f"{results['total_linear_feet_before_laps']:.2f} ft"),
            ("Number of Laps Required:", f"{results['total_laps']} laps"),
            ("Additional Length for Laps:", f"{results['total_lap_length']:.2f} ft")
        ]
        
        for i, (label, value) in enumerate(calc_data):
            tk.Label(calc_frame, text=label, font=('Arial', 9), anchor='w').grid(
                row=i, column=0, sticky='w', padx=(0, 12), pady=3)
            tk.Label(calc_frame, text=value, font=('Arial', 9, 'bold'), anchor='e').grid(
                row=i, column=1, sticky='e', padx=(12, 0), pady=3)
                
        # Configure column weights
        calc_frame.grid_columnconfigure(0, weight=1)
        calc_frame.grid_columnconfigure(1, weight=1)
        
        # Final results (highlighted)
        final_frame = tk.Frame(main_results_frame, bg='#d4edda', relief='solid', bd=3)
        final_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(final_frame, text="🎯 FINAL RESULTS", 
                font=('Arial', 12, 'bold'), bg='#d4edda', fg='#155724').pack(pady=8)
        
        # Final results grid
        final_grid = tk.Frame(final_frame, bg='#d4edda')
        final_grid.pack(fill='x', padx=15, pady=(0, 12))
        
        final_results = [
            ("Total Linear Feet (with laps):", f"{results['total_linear_feet_with_laps']:.2f} ft", "#0d5d1a"),
            ("Total Stock Bars Required:", f"{results['stock_bars_needed']} bars", "#0d5d1a"),
            ("Total Weight:", f"{results['total_weight']:.2f} lbs", "#0d5d1a")
        ]
        
        for i, (label, value, color) in enumerate(final_results):
            tk.Label(final_grid, text=label, font=('Arial', 10, 'bold'), 
                    bg='#d4edda', fg='#155724', anchor='w').grid(
                    row=i, column=0, sticky='w', padx=(0, 15), pady=4)
            tk.Label(final_grid, text=value, font=('Arial', 10, 'bold'), 
                    bg='#d4edda', fg=color, anchor='e').grid(
                    row=i, column=1, sticky='e', pady=4)
        
        final_grid.grid_columnconfigure(0, weight=1)
        final_grid.grid_columnconfigure(1, weight=1)
        
        # Bar specifications
        bar_frame = tk.Frame(main_results_frame, bg='#fff3cd', relief='solid', bd=2)
        bar_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(bar_frame, text="🔩 Bar Specifications Summary", 
                font=('Arial', 11, 'bold'), bg='#fff3cd', fg='#856404').pack(pady=8)
        
        bar_grid = tk.Frame(bar_frame, bg='#fff3cd')
        bar_grid.pack(fill='x', padx=15, pady=(0, 12))
        
        bar_specs = [
            ("Bar Size:", f"#{results['bar_size']}"),
            ("Diameter:", f"{results['bar_diameter']}\""),
            ("Weight per Foot:", f"{results['bar_weight']} lb/ft"),
            ("Stock Length Used:", f"{results['stock_length']} ft")
        ]
        
        for i, (label, value) in enumerate(bar_specs):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(bar_grid, text=label, font=('Arial', 9), 
                    bg='#fff3cd', fg='#856404', anchor='w').grid(
                    row=row, column=col, sticky='w', padx=(0, 12), pady=2)
            tk.Label(bar_grid, text=value, font=('Arial', 9, 'bold'), 
                    bg='#fff3cd', fg='#bf6000', anchor='w').grid(
                    row=row, column=col+1, sticky='w', padx=(0, 25), pady=2)
        
        # Action buttons
        button_frame = tk.Frame(main_results_frame, bg='white')
        button_frame.pack(fill='x', pady=12)
        
        # Export button
        export_btn = tk.Button(button_frame, text="📄 Export Results", 
                              font=('Arial', 9, 'bold'), bg='#17a2b8', fg='white',
                              relief='raised', bd=2, padx=15, pady=6,
                              cursor='hand2',
                              command=lambda: self.export_results(results))
        export_btn.pack(side='left', padx=(0, 8))
        
        # New calculation button
        new_calc_btn = tk.Button(button_frame, text="🔄 New Calculation", 
                                font=('Arial', 9, 'bold'), bg='#6c757d', fg='white',
                                relief='raised', bd=2, padx=15, pady=6,
                                cursor='hand2',
                                command=self.new_calculation)
        new_calc_btn.pack(side='left')
        
    def export_results(self, results):
        """Export results to a text file"""
        try:
            from tkinter import filedialog
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Calculation Results"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write("="*60 + "\n")
                    f.write("    NRS REINFORCEMENT QUANTITY CALCULATION RESULTS\n")
                    f.write("="*60 + "\n\n")
                    
                    f.write(f"Input Method: {results['input_method']}\n")
                    f.write(f"Slab Dimensions: {results['length']:.2f}' × {results['width']:.2f}'\n")
                    f.write(f"Slab Area: {results['area']:.2f} sq ft\n\n")
                    
                    f.write("INPUT PARAMETERS:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Spacing: {results['spacing']:.2f} ft\n")
                    f.write(f"Lap Length: {results['lap_length']:.2f} ft\n")
                    f.write(f"Stock Length: {results['stock_length']:.2f} ft\n")
                    f.write(f"Bar Size: #{results['bar_size']} ({results['bar_diameter']}\" diameter)\n")
                    f.write(f"Bar Weight: {results['bar_weight']} lb/ft\n\n")
                    
                    f.write("DETAILED CALCULATIONS:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Bars in Length Direction: {results['bars_length_direction']} bars\n")
                    f.write(f"Bars in Width Direction: {results['bars_width_direction']} bars\n")
                    f.write(f"Linear Feet (Length): {results['linear_feet_length']:.2f} ft\n")
                    f.write(f"Linear Feet (Width): {results['linear_feet_width']:.2f} ft\n")
                    f.write(f"Total Linear Feet (before laps): {results['total_linear_feet_before_laps']:.2f} ft\n")
                    f.write(f"Number of Laps: {results['total_laps']}\n")
                    f.write(f"Additional Length for Laps: {results['total_lap_length']:.2f} ft\n\n")
                    
                    f.write("FINAL RESULTS:\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"Total Linear Feet (with laps): {results['total_linear_feet_with_laps']:.2f} ft\n")
                    f.write(f"Total Stock Bars Required: {results['stock_bars_needed']} bars\n")
                    f.write(f"Total Weight: {results['total_weight']:.2f} lbs\n\n")
                    
                    f.write("Generated by NRS Reinforcement Quantity Calculator v1.0\n")
                    f.write(f"Calculation Date: {self.get_current_datetime()}\n")
                
                messagebox.showinfo("Export Successful", f"Results exported successfully to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def new_calculation(self):
        """Start a new calculation"""
        response = messagebox.askyesno("New Calculation", 
                                     "Start a new calculation?\n\nThis will clear current results.")
        if response:
            # Switch back to input tab
            self.notebook.select(0)
            
            # Clear results
            for widget in self.results_scrollable.winfo_children():
                widget.destroy()
                
            # Reset to initial message
            self.no_results_label = tk.Label(self.results_scrollable, 
                                            text="📊 Click 'Calculate' to see results here", 
                                            font=('Arial', 12), fg='#666')
            self.no_results_label.pack(expand=True, pady=80)
    
    def get_current_datetime(self):
        """Get current date and time as string"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SplashScreen:
    """Splash screen for application loading"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create splash window
        self.splash = tk.Toplevel()
        self.splash.title("Loading...")
        self.splash.geometry("380x220")
        self.splash.configure(bg='#2c3e50')
        self.splash.resizable(False, False)
        
        # Remove window decorations
        self.splash.overrideredirect(True)
        
        # Center splash screen
        self.center_splash()
        
        # Create splash content
        self.create_splash_content()
        
        # Start loading simulation
        self.start_loading()
        
    def center_splash(self):
        """Center splash screen on screen"""
        self.splash.update_idletasks()
        width = self.splash.winfo_width()
        height = self.splash.winfo_height()
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_splash_content(self):
        """Create splash screen content"""
        # Title
        title_label = tk.Label(self.splash, text="🏗️", font=('Arial', 40), 
                              bg='#2c3e50', fg='#3498db')
        title_label.pack(pady=(25, 8))
        
        app_title = tk.Label(self.splash, text="NRS Reinforcement Calculator", 
                            font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        app_title.pack(pady=(0, 4))
        
        version_label = tk.Label(self.splash, text="Professional v1.0", 
                                font=('Arial', 9), bg='#2c3e50', fg='#bdc3c7')
        version_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(self.splash, length=250, mode='indeterminate')
        self.progress.pack(pady=(25, 8))
        
        # Status label
        self.status_label = tk.Label(self.splash, text="Loading application...", 
                                    font=('Arial', 9), bg='#2c3e50', fg='#ecf0f1')
        self.status_label.pack()
        
        # Copyright
        copyright_label = tk.Label(self.splash, text="© 2025 NRS Construction Calculator Pro", 
                                  font=('Arial', 8), bg='#2c3e50', fg='#7f8c8d')
        copyright_label.pack(side='bottom', pady=(0, 8))
        
    def start_loading(self):
        """Start loading simulation"""
        self.progress.start(10)
        
        # Simulate loading steps
        loading_steps = [
            ("Initializing components...", 500),
            ("Loading ACI standards...", 800),
            ("Setting up interface...", 600),
            ("Finalizing setup...", 400),
        ]
        
        self.current_step = 0
        self.loading_steps = loading_steps
        self.next_step()
        
    def next_step(self):
        """Process next loading step"""
        if self.current_step < len(self.loading_steps):
            step_text, delay = self.loading_steps[self.current_step]
            self.status_label.config(text=step_text)
            self.current_step += 1
            self.splash.after(delay, self.next_step)
        else:
            self.finish_loading()
            
    def finish_loading(self):
        """Finish loading and show main application"""
        self.progress.stop()
        self.status_label.config(text="Ready!")
        self.splash.after(500, self.close_splash)
        
    def close_splash(self):
        """Close splash screen and show main app"""
        self.splash.destroy()
        self.parent.deiconify()  # Show main window


def main():
    """Main application entry point"""
    # Create root window (hidden initially)
    root = tk.Tk()
    root.withdraw()  # Hide main window initially
    
    # Show splash screen
    splash = SplashScreen(root)
    
    # Create main application
    app = ReinforcementCalculator(root)
    
    # Configure window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the NRS Reinforcement Calculator?"):
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)