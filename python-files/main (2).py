import tkinter as tk
from tkinter import ttk, messagebox
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class IronSmeltingAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Iron Smelting Assistant")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # List to store added faces with their properties
        self.faces = []
        
        # Create main window layout
        self.create_main_window()
        
    def create_main_window(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Iron Smelting Assistant", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Faces display area (scrollable with edit buttons)
        self.create_faces_display(main_frame)
        
        # Bottom controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, pady=(20, 0), sticky=(tk.W, tk.E))
        controls_frame.columnconfigure(1, weight=1)
        
        # Carbon percentage input
        carbon_frame = ttk.Frame(controls_frame)
        carbon_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(carbon_frame, text="Carbon Percentage:").grid(row=0, column=0, padx=(0, 10))
        self.carbon_var = tk.StringVar()
        self.carbon_entry = ttk.Entry(carbon_frame, textvariable=self.carbon_var, width=15)
        self.carbon_entry.grid(row=0, column=1, sticky=tk.W)
        
        # K1, K2, K3, and C dropdown inputs
        dropdowns_frame = ttk.LabelFrame(controls_frame, text="Process Parameters", padding="10")
        dropdowns_frame.grid(row=1, column=0, columnspan=2, pady=(10, 10), sticky=(tk.W, tk.E))
        dropdowns_frame.columnconfigure((0, 1), weight=1)
        
        # K1 dropdown
        ttk.Label(dropdowns_frame, text="K1 Parameter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.k1_var = tk.StringVar()
        self.k1_combo = ttk.Combobox(dropdowns_frame, textvariable=self.k1_var, state="readonly", width=25, justify="center")
        self.k1_combo['values'] = [option[0] for option in self.get_k1_options()]  # ADD YOUR K1 OPTIONS HERE
        self.k1_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        if self.k1_combo['values']:
            self.k1_combo.current(0)  # Select first option by default
        
        # K2 dropdown
        ttk.Label(dropdowns_frame, text="K2 Parameter:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.k2_var = tk.StringVar()
        self.k2_combo = ttk.Combobox(dropdowns_frame, textvariable=self.k2_var, state="readonly", width=25, justify="center")
        self.k2_combo['values'] = [option[0] for option in self.get_k2_options()]  # ADD YOUR K2 OPTIONS HERE
        self.k2_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        if self.k2_combo['values']:
            self.k2_combo.current(0)
        
        # K3 dropdown
        ttk.Label(dropdowns_frame, text="K3 Parameter:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.k3_var = tk.StringVar()
        self.k3_combo = ttk.Combobox(dropdowns_frame, textvariable=self.k3_var, state="readonly", width=25, justify="center")
        self.k3_combo['values'] = [option[0] for option in self.get_k3_options()]  # ADD YOUR K3 OPTIONS HERE
        self.k3_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        if self.k3_combo['values']:
            self.k3_combo.current(0)
        
        # C dropdown
        ttk.Label(dropdowns_frame, text="Cooling Parameter (C):").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.c_var = tk.StringVar()
        self.c_combo = ttk.Combobox(dropdowns_frame, textvariable=self.c_var, state="readonly", width=25, justify="center")
        self.c_combo['values'] = [option[0] for option in self.get_c_options()]  # ADD YOUR C OPTIONS HERE
        self.c_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        if self.c_combo['values']:
            self.c_combo.current(0)
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2)
        
        # Add Face button
        self.add_face_btn = ttk.Button(buttons_frame, text="Add Face", 
                                      command=self.open_add_face_popup)
        self.add_face_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Submit button
        self.submit_btn = ttk.Button(buttons_frame, text="Submit", 
                                    command=self.submit_data)
        self.submit_btn.grid(row=0, column=1)
        
    def create_faces_display(self, parent):
        # Frame for faces display with scrollbar
        faces_frame = ttk.LabelFrame(parent, text="Added Faces", padding="10")
        faces_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        faces_frame.columnconfigure(0, weight=1)
        faces_frame.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for faces with edit buttons
        canvas = tk.Canvas(faces_frame, bg='white')
        scrollbar = ttk.Scrollbar(faces_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.canvas = canvas
        
        # Initial message
        self.update_faces_display()
        
    def update_faces_display(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.faces:
            label = tk.Label(self.scrollable_frame, text="No faces added yet. Click 'Add Face' to get started.",
                             font=("Arial", 10, "italic"), bg='white')
            label.pack(pady=20, anchor='center')
        else:
            for i, face_data in enumerate(self.faces):
                face_frame = tk.Frame(self.scrollable_frame, bg='white')
                face_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Face description
                desc = self.create_face_description(face_data['shape'], face_data['values'])
                face_label = tk.Label(face_frame, text=f"{i+1}. {desc}", bg='white', font=("Arial", 12))
                face_label.pack(side=tk.LEFT, expand=True)
                
                # Edit button
                edit_btn = ttk.Button(face_frame, text="Edit", width=8,
                                     command=lambda idx=i: self.edit_face(idx))
                edit_btn.pack(side=tk.RIGHT, padx=(10, 0))
                
                # Delete button
                delete_btn = ttk.Button(face_frame, text="Delete", width=8,
                                       command=lambda idx=i: self.delete_face(idx))
                delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def delete_face(self, index):
        if messagebox.askyesno("Delete Face", f"Are you sure you want to delete face {index + 1}?"):
            self.faces.pop(index)
            self.update_faces_display()
            
    def edit_face(self, index):
        face_data = self.faces[index]
        self.open_edit_face_popup(index, face_data)
        
    def open_edit_face_popup(self, face_index, face_data):
        # Create popup window
        self.edit_popup = tk.Toplevel(self.root)
        self.edit_popup.title(f"Edit {face_data['shape']}")
        self.edit_popup.geometry("400x300")
        self.edit_popup.resizable(False, False)
        self.edit_popup.grab_set()
        self.edit_popup.transient(self.root)
        
        # Main frame for popup
        popup_frame = ttk.Frame(self.edit_popup, padding="20")
        popup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(popup_frame, text=f"Edit {face_data['shape']}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Input fields frame
        inputs_frame = ttk.Frame(popup_frame)
        inputs_frame.pack(expand=True)
        
        # Store input variables and current face index
        self.edit_input_vars = {}
        self.edit_face_index = face_index
        
        # Create input fields with current values
        input_fields = self.get_input_fields_for_shape(face_data['shape'])
        
        for i, (label_text, var_name) in enumerate(input_fields):
            row_frame = ttk.Frame(inputs_frame)
            row_frame.pack(pady=5, fill=tk.X)
            
            ttk.Label(row_frame, text=f"{label_text}:", width=12).pack(side=tk.LEFT)
            
            var = tk.StringVar()
            var.set(str(face_data['values'][var_name]))  # Set current value
            self.edit_input_vars[var_name] = var
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
        # Buttons frame
        buttons_frame = ttk.Frame(popup_frame)
        buttons_frame.pack(side=tk.BOTTOM, pady=(20, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", 
                               command=self.edit_popup.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Submit button
        submit_btn = ttk.Button(buttons_frame, text="Submit", 
                               command=self.update_face)
        submit_btn.pack(side=tk.LEFT)
        
    def update_face(self):
        # Validate inputs
        values = {}
        for var_name, var in self.edit_input_vars.items():
            try:
                value = float(var.get())
                if value <= 0:
                    raise ValueError("Value must be positive")
                values[var_name] = value
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                   f"Please enter a valid positive number for {var_name.replace('_', ' ').title()}")
                return
                
        # Update face data
        self.faces[self.edit_face_index]['values'] = values
        
        # Update display
        self.update_faces_display()
        
        # Close popup
        self.edit_popup.destroy()
        
    # =====================================================================
    # ADD YOUR DROPDOWN OPTIONS HERE - MODIFY THESE FUNCTIONS
    # =====================================================================
    
    def get_k1_options(self):
        """
        ADD YOUR K1 OPTIONS HERE
        Return format: [("Display Text 1", value1), ("Display Text 2", value2), ...]
        Example: [("Low Temperature", 0.5), ("Medium Temperature", 1.0), ("High Temperature", 1.5)]
        """
        return [
            ("حوض المعدن المنصهر", 0.5),
            ("حوض أملاح منصهرة", 1.0),
            ("وسط غازي", 2.0)
        ]
    
    def get_k2_options(self):
        """
        ADD YOUR K2 OPTIONS HERE
        Return format: [("Display Text 1", value1), ("Display Text 2", value2), ...]
        """
        return [
            ("كرة", 1.0),
            ("المحور والمقطع الدائري", 2.0),
            ("المحور على شكل متوازي مستطيلات", 2.5),
            ("صفيحة", 4)
        ]
    
    def get_k3_options(self):
        """
        ADD YOUR K3 OPTIONS HERE
        Return format: [("Display Text 1", value1), ("Display Text 2", value2), ...]
        """
        return [
            ("تسخين من جميع الجهات", 1.0),
            ("تسخين من ثلاث جهات", 1.5),
            ("تسخين من جهة واحدة", 4)
        ]
    
    def get_c_options(self):
        """
        ADD YOUR C OPTIONS HERE
        Return format: [("Display Text 1", value1), ("Display Text 2", value2), ...]
        """
        return [
            ("18C ماء", 1800),
            ("26C ماء", 1600),
            ("50C ماء", 400),
            ("زيت معدني", 250)
        ]
    
    # =====================================================================
    
    def get_k_value(self, selected_option, options_list):
        """Helper function to get the numeric value from selected dropdown option"""
        for option_text, value in options_list:
            if option_text == selected_option:
                return value
        return 1.0  # Default value if not found
    
    def get_input_fields_for_shape(self, shape):
        """Get input fields for a specific shape"""
        shape_fields = {
            "Circle": [("Radius", "radius")],
            "Rectangle": [("Width", "width"), ("Height", "height")],
            "Triangle": [("Base", "base"), ("Height", "height")],
            "Square": [("Side", "side")],
            "Ellipse": [("Major Axis", "major_axis"), ("Minor Axis", "minor_axis")],
            "Hexagon": [("Side Length", "side_length")]
        }
        return shape_fields.get(shape, [])     
       
    def open_add_face_popup(self):
        # Create popup window
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Add Face")
        self.popup.geometry("400x300")
        self.popup.resizable(False, False)
        self.popup.grab_set()
        self.popup.transient(self.root)
        
        # Main frame for popup
        popup_frame = ttk.Frame(self.popup, padding="20")
        popup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store reference to popup frame for later updates
        self.popup_frame = popup_frame
        
        # Title
        title_label = ttk.Label(popup_frame, text="Select Shape", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Shape selection buttons
        self.create_shape_buttons()
        
    def create_shape_buttons(self):
        # Clear existing widgets except title
        for widget in self.popup_frame.winfo_children()[1:]:
            widget.destroy()
            
        shapes_frame = ttk.Frame(self.popup_frame)
        shapes_frame.pack(expand=True)
        
        # Define shapes and their buttons
        shapes = [
            ("Circle", self.show_circle_inputs),
            ("Rectangle", self.show_rectangle_inputs),
            ("Triangle", self.show_triangle_inputs),
            ("Square", self.show_square_inputs),
            ("Ellipse", self.show_ellipse_inputs),
            ("Hexagon", self.show_hexagon_inputs)
        ]
        
        # Create buttons in a grid
        for i, (shape_name, command) in enumerate(shapes):
            row = i // 2
            col = i % 2
            btn = ttk.Button(shapes_frame, text=shape_name, command=command, width=15)
            btn.grid(row=row, column=col, padx=10, pady=5)
            
    def show_circle_inputs(self):
        self.show_shape_inputs("Circle", [("Radius", "radius")])
        
    def show_rectangle_inputs(self):
        self.show_shape_inputs("Rectangle", [("Width", "width"), ("Height", "height")])
        
    def show_triangle_inputs(self):
        self.show_shape_inputs("Triangle", [("Base", "base"), ("Height", "height")])
        
    def show_square_inputs(self):
        self.show_shape_inputs("Square", [("Side", "side")])
        
    def show_ellipse_inputs(self):
        self.show_shape_inputs("Ellipse", [("Major Axis", "major_axis"), ("Minor Axis", "minor_axis")])
        
    def show_hexagon_inputs(self):
        self.show_shape_inputs("Hexagon", [("Side Length", "side_length")])
        
    def show_shape_inputs(self, shape_name, input_fields):
        # Clear existing widgets except title
        for widget in self.popup_frame.winfo_children()[1:]:
            widget.destroy()
            
        # Back button
        back_btn = ttk.Button(self.popup_frame, text="← Back", 
                             command=self.create_shape_buttons)
        back_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Shape name label
        shape_label = ttk.Label(self.popup_frame, text=f"Enter {shape_name} Properties", 
                               font=("Arial", 12, "bold"))
        shape_label.pack(pady=(0, 20))
        
        # Input fields frame
        inputs_frame = ttk.Frame(self.popup_frame)
        inputs_frame.pack(expand=True)
        
        # Store input variables
        self.input_vars = {}
        self.current_shape = shape_name
        
        # Create input fields
        for i, (label_text, var_name) in enumerate(input_fields):
            row_frame = ttk.Frame(inputs_frame)
            row_frame.pack(pady=5, fill=tk.X)
            
            ttk.Label(row_frame, text=f"{label_text}:", width=12).pack(side=tk.LEFT)
            
            var = tk.StringVar()
            self.input_vars[var_name] = var
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
        # Submit button
        submit_frame = ttk.Frame(self.popup_frame)
        submit_frame.pack(side=tk.BOTTOM, pady=(20, 0))
        
        submit_btn = ttk.Button(submit_frame, text="Submit", 
                               command=self.add_face_to_list)
        submit_btn.pack()
        
    def add_face_to_list(self):
        # Validate inputs
        values = {}
        for var_name, var in self.input_vars.items():
            try:
                value = float(var.get())
                if value <= 0:
                    raise ValueError("Value must be positive")
                values[var_name] = value
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                   f"Please enter a valid positive number for {var_name.replace('_', ' ').title()}")
                return
                
        # Add to faces list with shape and values
        face_data = {
            'shape': self.current_shape,
            'values': values
        }
        self.faces.append(face_data)
        
        # Update display
        self.update_faces_display()
        
        # Close popup
        self.popup.destroy()
        
    def create_face_description(self, shape, values):
        if shape == "Circle":
            return f"Circle - Radius: {values['radius']}"
        elif shape == "Rectangle":
            return f"Rectangle - Width: {values['width']} / Height: {values['height']}"
        elif shape == "Triangle":
            return f"Triangle - Base: {values['base']} / Height: {values['height']}"
        elif shape == "Square":
            return f"Square - Side: {values['side']}"
        elif shape == "Ellipse":
            return f"Ellipse - Major Axis: {values['major_axis']} / Minor Axis: {values['minor_axis']}"
        elif shape == "Hexagon":
            return f"Hexagon - Side Length: {values['side_length']}"
            
    def calculate_area(self, shape, values):
        """Calculate area for different shapes"""
        if shape == "Circle":
            return math.pi * (values['radius'] ** 2)
        elif shape == "Rectangle":
            return values['width'] * values['height']
        elif shape == "Triangle":
            return 0.5 * values['base'] * values['height']
        elif shape == "Square":
            return values['side'] ** 2
        elif shape == "Ellipse":
            return math.pi * values['major_axis'] * values['minor_axis'] / 4
        elif shape == "Hexagon":
            return (3 * math.sqrt(3) / 2) * (values['side_length'] ** 2)
        return 0
        
    def get_minimum_dimension(self, shape, values):
        """Get minimum dimension of a shape"""
        if shape == "Circle":
            return values['radius']
        elif shape == "Rectangle":
            return min(values['width'], values['height'])
        elif shape == "Triangle":
            return min(values['base'], values['height'])
        elif shape == "Square":
            return values['side']
        elif shape == "Ellipse":
            return min(values['major_axis'], values['minor_axis'])
        elif shape == "Hexagon":
            return values['side_length']
        return 0
        
    def get_right_temp(self, carbon):
        """Calculate temperature for carbon > 0.8%"""
        pt1 = (0.8, 723)
        pt2 = (2.0, 1147)
        length = math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
        v = ((pt2[0] - pt1[0]) / length, (pt2[1] - pt1[1]) / length)
        diff = (carbon - 0.8) / v[0]
        temperature = pt1[1] + v[1] * diff
        return temperature
        
    def get_left_temp(self, carbon):
        """Calculate temperature for carbon <= 0.8%"""
        pt1 = (0.8, 723)
        pt2 = (0.0, 910)
        length = math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
        v = ((pt2[0] - pt1[0]) / length, (pt2[1] - pt1[1]) / length)
        diff = (carbon - 0.8) / v[0]
        temperature = pt1[1] + v[1] * diff
        return temperature
        
    def submit_data(self):
        # Validate carbon percentage
        try:
            carbon_value = float(self.carbon_var.get())
            if carbon_value < 0 or carbon_value > 2.0:
                messagebox.showerror("Invalid Input", 
                                   "Carbon percentage must be between 0 and 2%")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter a valid carbon percentage (0-2%)")
            return
            
        # Check if at least one face is added
        if not self.faces:
            messagebox.showerror("No Faces", 
                               "Please add at least one face before submitting")
            return
            
        # Calculate results
        self.show_results(carbon_value)
        
    def show_results(self, carbon_value):
        # Find face with maximum area
        max_area = 0
        max_area_face = None
        
        for face_data in self.faces:
            area = self.calculate_area(face_data['shape'], face_data['values'])
            if area > max_area:
                max_area = area
                max_area_face = face_data
                
        # Calculate minimum distance
        min_distance = self.get_minimum_dimension(max_area_face['shape'], max_area_face['values'])
        
        # Calculate temperature
        if carbon_value > 0.8:
            temperature = self.get_right_temp(carbon_value)
        else:
            temperature = self.get_left_temp(carbon_value)

        temperature += 50
        
        # Get K values from dropdowns
        k1_value = self.get_k_value(self.k1_var.get(), self.get_k1_options())
        k2_value = self.get_k_value(self.k2_var.get(), self.get_k2_options())
        k3_value = self.get_k_value(self.k3_var.get(), self.get_k3_options())
        c_value = self.get_k_value(self.c_var.get(), self.get_c_options())
        
        # Calculate heating time: Th = 0.1 * D * K1 * K2 * K3
        heating_time = 0.1 * min_distance * k1_value * k2_value * k3_value
        
        # Calculate keeping time: equal to minimum distance
        keeping_time = min_distance
        
        # Calculate cooling time: Tc = (T* - 25) / C
        cooling_time = (temperature - 25) / c_value
            
        # Create results popup
        results_popup = tk.Toplevel(self.root)
        results_popup.title("Smelting Results")
        results_popup.geometry("1080x850") # Increased size to accommodate chart
        results_popup.resizable(True, True)  # Allow resizing for better chart viewing
        results_popup.grab_set()
        results_popup.transient(self.root)
        
        # Main frame with scrollbar capability
        canvas = tk.Canvas(results_popup)
        scrollbar = ttk.Scrollbar(results_popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main frame
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Iron Smelting Results", 
                            font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Results tab
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="Results")
        
        # Chart tab
        chart_tab = ttk.Frame(notebook)
        notebook.add(chart_tab, text="Temperature Chart")
        
        # Results frame (moved to results tab)
        results_frame = ttk.LabelFrame(results_tab, text="Calculations", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Input summary
        input_frame = ttk.Frame(results_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(input_frame, text=f"Carbon Percentage: {carbon_value}%", 
                font=("Arial", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(input_frame, text=f"Number of faces: {len(self.faces)}", 
                font=("Arial", 11)).pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(results_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Maximum area face info
        max_face_desc = self.create_face_description(max_area_face['shape'], max_area_face['values'])
        ttk.Label(results_frame, text="Face with Maximum Area:", 
                font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(results_frame, text=f"  {max_face_desc}", 
                font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(results_frame, text=f"  Area: {max_area:.3f}", 
                font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        # Results
        ttk.Label(results_frame, text="Results:", 
                font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Minimum Distance
        min_dist_frame = ttk.Frame(results_frame)
        min_dist_frame.pack(fill=tk.X, pady=2)
        ttk.Label(min_dist_frame, text="Minimum Distance:", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(min_dist_frame, text=f"{min_distance:.3f}", 
                font=("Arial", 11), foreground="blue").pack(side=tk.RIGHT)
        
        # Temperature
        temp_frame = ttk.Frame(results_frame)
        temp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(temp_frame, text="Required Temperature:", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(temp_frame, text=f"{temperature:.1f}°C", 
                font=("Arial", 11), foreground="red").pack(side=tk.RIGHT)
        
        # Separator for time calculations
        separator2 = ttk.Separator(results_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=10)
        
        # Time calculations header
        ttk.Label(results_frame, text="Time Calculations:", 
                font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(5, 5))
        
        # Heating Time
        heating_frame = ttk.Frame(results_frame)
        heating_frame.pack(fill=tk.X, pady=2)
        ttk.Label(heating_frame, text="Heating Time (Th):", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(heating_frame, text=f"{heating_time:.3f} minutes", 
                font=("Arial", 11), foreground="orange").pack(side=tk.RIGHT)
        
        # Keeping Time
        keeping_frame = ttk.Frame(results_frame)
        keeping_frame.pack(fill=tk.X, pady=2)
        ttk.Label(keeping_frame, text="Keeping Time:", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(keeping_frame, text=f"{keeping_time:.3f} minutes", 
                font=("Arial", 11), foreground="green").pack(side=tk.RIGHT)
        
        # Cooling Time
        cooling_frame = ttk.Frame(results_frame)
        cooling_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cooling_frame, text="Cooling Time (Tc):", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        ttk.Label(cooling_frame, text=f"{cooling_time:.3f} minutes", 
                font=("Arial", 11), foreground="purple").pack(side=tk.RIGHT)
        
        # Create the chart in the chart tab
        self.create_temperature_chart(chart_tab, heating_time, keeping_time, cooling_time, temperature)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", 
                            command=results_popup.destroy)
        close_btn.pack(pady=(10, 0))
        
        # Ask if user wants to clear data
        def on_close():
            results_popup.destroy()
            response = messagebox.askyesno("Clear Data", 
                                        "Would you like to clear all data for a new calculation?")
            if response:
                self.clear_all_data()
                
        results_popup.protocol("WM_DELETE_WINDOW", on_close)
        close_btn.configure(command=on_close)

    def create_temperature_chart(self, parent, heating_time, keeping_time, cooling_time, max_temperature):
        """Create a temperature vs time chart showing the smelting process"""
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Define the time points and temperatures
        times = [
            0,                                      # Start
            heating_time,                           # End of heating
            heating_time + keeping_time,            # End of keeping
            heating_time + keeping_time + cooling_time  # End of cooling
        ]
        
        temperatures = [
            25,              # Room temperature at start
            max_temperature, # Max temperature after heating
            max_temperature, # Same temperature during keeping
            25               # Back to room temperature after cooling
        ]
        
        # Plot the main line
        ax.plot(times, temperatures, 'b-', linewidth=3, label='Temperature Profile')
        
        # Add markers for key points
        ax.plot(times, temperatures, 'ro', markersize=8)
        
        # Color the different phases
        # Heating phase
        ax.fill_between([0, heating_time], [25, max_temperature], 
                    alpha=0.3, color='orange', label='Heating Phase')
        
        # Keeping phase
        ax.fill_between([heating_time, heating_time + keeping_time], 
                    [max_temperature, max_temperature], 
                    alpha=0.3, color='green', label='Keeping Phase')
        
        # Cooling phase
        ax.fill_between([heating_time + keeping_time, heating_time + keeping_time + cooling_time], 
                    [max_temperature, 25], 
                    alpha=0.3, color='purple', label='Cooling Phase')
        
        # Customize the plot
        ax.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
        ax.set_title('Iron Smelting Temperature Profile', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # # Add annotations for key points
        # ax.annotate('Start\n(0min, 25°C)', 
        #             xy=(0, 25), xytext=(10, 50),
        #             arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
        #             fontsize=10, ha='left')
        
        # ax.annotate(f'Max Temp\n({heating_time:.1f}min, {max_temperature:.1f}°C)', 
        #             xy=(heating_time, max_temperature), xytext=(heating_time + 10, max_temperature + 50),
        #             arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
        #             fontsize=10, ha='left')
        
        # ax.annotate(f'End\n({times[-1]:.1f}min, 25°C)', 
        #             xy=(times[-1], 25), xytext=(times[-1] - 20, 80),
        #             arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
        #             fontsize=10, ha='right')
        
        # Set axis limits with some padding
        ax.set_xlim(-max(times) * 0.05, max(times) * 1.1)
        ax.set_ylim(0, max_temperature * 1.2)
        
        # Tight layout
        fig.tight_layout()
        
        # Create canvas and add to parent
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a toolbar for zooming/panning
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()

    def clear_all_data(self):
        self.faces.clear()
        self.carbon_var.set("")
        self.update_faces_display()

def main():
    root = tk.Tk()
    IronSmeltingAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# this is a part of a GUI app in python, this function contain the output of the program, I want to add for this output a graph of chart, the chart's x axis will be the time and the y axis will be the temperature, so the graph will draw lines from (0, 25) -> (heating_time, temperature) -> (heating_time + keeping_time, temperature) -> (heating_time + keeping_time + cooling_time, 25)