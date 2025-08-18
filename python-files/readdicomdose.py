import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import re
import os

# Check for required packages and provide helpful error messages
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError as e:
    error_msg = f"""
Required package 'matplotlib' is not installed.

To install it, run:
    pip install matplotlib

Error details: {str(e)}
"""
    print(error_msg)
    if 'tkinter' in globals():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Package", error_msg)
        root.destroy()
    exit(1)

try:
    import pydicom
except ImportError as e:
    error_msg = f"""
Required package 'pydicom' is not installed.

To install it, run:
    pip install pydicom

Error details: {str(e)}
"""
    print(error_msg)
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Package", error_msg)
    root.destroy()
    exit(1)

import os

class DICOMDoseProfileViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM RT Dose Profile Viewer - X & Z Profiles")
        
        # Set window size and center it on screen
        window_width = 1400
        window_height = 1000
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry with size and position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set minimum window size to prevent it from becoming too small
        self.root.minsize(1000, 700)
        
        # Initialize variables
        self.dose_data = None
        self.dose_grid_scaling = None
        self.pixel_spacing = None
        self.slice_thickness = None
        self.grid_frame_offset_vector = None
        self.number_of_frames = None
        self.rows = None
        self.columns = None
        
        # Second DICOM dose variables
        self.dose_data_2 = None
        self.dose_grid_scaling_2 = None
        self.pixel_spacing_2 = None
        self.slice_thickness_2 = None
        self.grid_frame_offset_vector_2 = None
        self.number_of_frames_2 = None
        self.rows_2 = None
        self.columns_2 = None
        self.dose_image_position_2 = None
        self.dose_image_orientation_2 = None
        
        # RT Plan and isocenter variables
        self.rt_plan_data = None
        self.isocenter_position = None
        self.dose_image_position = None
        self.dose_image_orientation = None
        
        # Second RT Plan and isocenter variables
        self.rt_plan_data_2 = None
        self.isocenter_position_2 = None
        
        # Measurement data variables
        self.measurement_data = None
        self.crossplane_measurement = None
        self.inplane_measurement = None
        
        # Second measurement data variables
        self.measurement_data_2 = None
        self.crossplane_measurement_2 = None
        self.inplane_measurement_2 = None
        
        # Zoom control variables (needed for update_profiles method)
        self.zoom_enabled_var = tk.BooleanVar(value=False)
        self.zoom_x_center_var = tk.StringVar(value="0.0")
        self.zoom_x_range_var = tk.StringVar(value="10.0")
        self.zoom_z_center_var = tk.StringVar(value="0.0")
        self.zoom_z_range_var = tk.StringVar(value="10.0")
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Close All Files & Restart", command=self.restart_application, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Restart", command=self.show_restart_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts_help)
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-r>", lambda e: self.restart_application())
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        file_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(2, weight=1)
        
        # Column 1 - DICOM 1
        ttk.Label(file_frame, text="DICOM 1", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 2), padx=(0, 10))
        
        # DICOM Dose file 1 selection
        ttk.Label(file_frame, text="Dose File:").grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        dose_frame_1 = ttk.Frame(file_frame)
        dose_frame_1.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        dose_frame_1.columnconfigure(1, weight=1)
        
        ttk.Button(dose_frame_1, text="Select", 
                  command=self.select_dose_file).grid(row=0, column=0, padx=(0, 5))
        self.dose_file_label = ttk.Label(dose_frame_1, text="No file selected", font=('TkDefaultFont', 8))
        self.dose_file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # DICOM RT Plan file 1 selection
        ttk.Label(file_frame, text="RT Plan:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        plan_frame_1 = ttk.Frame(file_frame)
        plan_frame_1.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        plan_frame_1.columnconfigure(1, weight=1)
        
        ttk.Button(plan_frame_1, text="Select", 
                  command=self.select_plan_file).grid(row=0, column=0, padx=(0, 5))
        self.plan_file_label = ttk.Label(plan_frame_1, text="No file selected", font=('TkDefaultFont', 8))
        self.plan_file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Column 2 - DICOM 2
        ttk.Label(file_frame, text="DICOM 2", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, pady=(0, 2), padx=(0, 10))
        
        # DICOM Dose file 2 selection
        ttk.Label(file_frame, text="Dose File:").grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        dose_frame_2 = ttk.Frame(file_frame)
        dose_frame_2.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        dose_frame_2.columnconfigure(1, weight=1)
        
        ttk.Button(dose_frame_2, text="Select", 
                  command=self.select_dose_file_2).grid(row=0, column=0, padx=(0, 5))
        self.dose_file_label_2 = ttk.Label(dose_frame_2, text="No file selected", font=('TkDefaultFont', 8))
        self.dose_file_label_2.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # DICOM RT Plan file 2 selection
        ttk.Label(file_frame, text="RT Plan:").grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        plan_frame_2 = ttk.Frame(file_frame)
        plan_frame_2.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        plan_frame_2.columnconfigure(1, weight=1)
        
        ttk.Button(plan_frame_2, text="Select", 
                  command=self.select_plan_file_2).grid(row=0, column=0, padx=(0, 5))
        self.plan_file_label_2 = ttk.Label(plan_frame_2, text="No file selected", font=('TkDefaultFont', 8))
        self.plan_file_label_2.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Column 3 - Measurements
        ttk.Label(file_frame, text="Measurements", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, pady=(0, 2))
        
        # Measurement file 1 selection
        ttk.Label(file_frame, text="Measurement 1:").grid(row=1, column=2, sticky=tk.W, pady=(2, 0))
        meas_frame_1 = ttk.Frame(file_frame)
        meas_frame_1.grid(row=2, column=2, sticky=(tk.W, tk.E))
        meas_frame_1.columnconfigure(1, weight=1)
        
        ttk.Button(meas_frame_1, text="Select", 
                  command=self.select_measurement_file).grid(row=0, column=0, padx=(0, 5))
        self.measurement_file_label = ttk.Label(meas_frame_1, text="No file selected", font=('TkDefaultFont', 8))
        self.measurement_file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Measurement file 2 selection
        ttk.Label(file_frame, text="Measurement 2:").grid(row=3, column=2, sticky=tk.W, pady=(5, 0))
        meas_frame_2 = ttk.Frame(file_frame)
        meas_frame_2.grid(row=4, column=2, sticky=(tk.W, tk.E))
        meas_frame_2.columnconfigure(1, weight=1)
        
        ttk.Button(meas_frame_2, text="Select", 
                  command=self.select_measurement_file_2).grid(row=0, column=0, padx=(0, 5))
        self.measurement_file_label_2 = ttk.Label(meas_frame_2, text="No file selected", font=('TkDefaultFont', 8))
        self.measurement_file_label_2.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Profile Controls", padding="5")
        controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Position controls in a single compact row
        pos_frame = ttk.Frame(controls_frame)
        pos_frame.grid(row=0, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(pos_frame, text="Position (mm):").grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=1, padx=(0, 2))
        self.x_var = tk.StringVar(value="0.0")
        self.x_entry = ttk.Entry(pos_frame, textvariable=self.x_var, width=8)
        self.x_entry.grid(row=0, column=2, padx=(0, 10))
        self.x_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Label(pos_frame, text="Z:").grid(row=0, column=3, padx=(0, 2))
        self.z_var = tk.StringVar(value="0.0")
        self.z_entry = ttk.Entry(pos_frame, textvariable=self.z_var, width=8)
        self.z_entry.grid(row=0, column=4, padx=(0, 10))
        self.z_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=5, padx=(0, 2))
        self.y_var = tk.StringVar(value="0.0")
        self.y_entry = ttk.Entry(pos_frame, textvariable=self.y_var, width=8)
        self.y_entry.grid(row=0, column=6, padx=(0, 10))
        self.y_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(pos_frame, text="Update Profiles", 
                  command=self.update_profiles).grid(row=0, column=7, padx=(10, 0))
        
        # Add coordinate system info
        self.coord_info_label = ttk.Label(controls_frame, text="Coordinates: Grid origin", font=('TkDefaultFont', 8))
        self.coord_info_label.grid(row=1, column=0, columnspan=7, sticky=tk.W)
        
        # Combined controls frame with normalization and measurement shifts side by side
        combined_frame = ttk.Frame(controls_frame)
        combined_frame.grid(row=2, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(5, 0))
        combined_frame.columnconfigure(0, weight=1)
        combined_frame.columnconfigure(1, weight=1)
        
        # Normalization controls (left side)
        norm_frame = ttk.LabelFrame(combined_frame, text="Normalization Controls", padding="3")
        norm_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # First row: DICOM normalizations
        # DICOM 1 normalization
        ttk.Label(norm_frame, text="DICOM 1 Max:").grid(row=0, column=0, padx=(0, 3))
        self.dicom_norm_var = tk.StringVar()
        self.dicom_norm_entry = ttk.Entry(norm_frame, textvariable=self.dicom_norm_var, width=8)
        self.dicom_norm_entry.grid(row=0, column=1, padx=(0, 3))
        self.dicom_norm_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(norm_frame, text="Auto", command=self.auto_dicom_norm).grid(row=0, column=2, padx=(0, 8))
        
        # DICOM 2 normalization
        ttk.Label(norm_frame, text="DICOM 2 Max:").grid(row=1, column=0, padx=(0, 3), pady=(3, 0))
        self.dicom_norm_var_2 = tk.StringVar()
        self.dicom_norm_entry_2 = ttk.Entry(norm_frame, textvariable=self.dicom_norm_var_2, width=8)
        self.dicom_norm_entry_2.grid(row=1, column=1, padx=(0, 3), pady=(3, 0))
        self.dicom_norm_entry_2.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(norm_frame, text="Auto", command=self.auto_dicom_norm_2).grid(row=1, column=2, padx=(0, 8), pady=(3, 0))
        
        # Second row: Measurement normalizations
        # Measurement 1 normalization
        ttk.Label(norm_frame, text="Meas 1 Max:").grid(row=2, column=0, padx=(0, 3), pady=(3, 0))
        self.meas_norm_var = tk.StringVar()
        self.meas_norm_entry = ttk.Entry(norm_frame, textvariable=self.meas_norm_var, width=8)
        self.meas_norm_entry.grid(row=2, column=1, padx=(0, 3), pady=(3, 0))
        self.meas_norm_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(norm_frame, text="Auto", command=self.auto_meas_norm).grid(row=2, column=2, padx=(0, 8), pady=(3, 0))
        
        # Measurement 2 normalization
        ttk.Label(norm_frame, text="Meas 2 Max:").grid(row=3, column=0, padx=(0, 3), pady=(3, 0))
        self.meas_norm_var_2 = tk.StringVar()
        self.meas_norm_entry_2 = ttk.Entry(norm_frame, textvariable=self.meas_norm_var_2, width=8)
        self.meas_norm_entry_2.grid(row=3, column=1, padx=(0, 3), pady=(3, 0))
        self.meas_norm_entry_2.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(norm_frame, text="Auto", command=self.auto_meas_norm_2).grid(row=3, column=2, padx=(0, 8), pady=(3, 0))
        
        # Control buttons for normalization
        button_frame_norm = ttk.Frame(norm_frame)
        button_frame_norm.grid(row=4, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame_norm, text="Update Norms", command=self.update_profiles, 
                  style="Accent.TButton").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        ttk.Button(button_frame_norm, text="Reset All Norms", command=self.reset_normalizations).grid(row=0, column=1, sticky=tk.W)
        
        # Coordinate shift controls for measurements (right side)
        shift_frame = ttk.LabelFrame(combined_frame, text="Measurement Coordinate Shifts", padding="3")
        shift_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # First row: Measurement 1 shifts
        ttk.Label(shift_frame, text="Meas 1 X Shift:").grid(row=0, column=0, padx=(0, 3))
        self.x_shift_var = tk.StringVar(value="0.0")
        self.x_shift_entry = ttk.Entry(shift_frame, textvariable=self.x_shift_var, width=6)
        self.x_shift_entry.grid(row=0, column=1, padx=(0, 5))
        self.x_shift_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Label(shift_frame, text="Z Shift:").grid(row=0, column=2, padx=(0, 3))
        self.z_shift_var = tk.StringVar(value="0.0")
        self.z_shift_entry = ttk.Entry(shift_frame, textvariable=self.z_shift_var, width=6)
        self.z_shift_entry.grid(row=0, column=3, padx=(0, 5))
        self.z_shift_entry.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(shift_frame, text="Auto Align", command=self.auto_align_profiles).grid(row=0, column=4)
        
        # Second row: Measurement 2 shifts
        ttk.Label(shift_frame, text="Meas 2 X Shift:").grid(row=1, column=0, padx=(0, 3), pady=(3, 0))
        self.x_shift_var_2 = tk.StringVar(value="0.0")
        self.x_shift_entry_2 = ttk.Entry(shift_frame, textvariable=self.x_shift_var_2, width=6)
        self.x_shift_entry_2.grid(row=1, column=1, padx=(0, 5), pady=(3, 0))
        self.x_shift_entry_2.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Label(shift_frame, text="Z Shift:").grid(row=1, column=2, padx=(0, 3), pady=(3, 0))
        self.z_shift_var_2 = tk.StringVar(value="0.0")
        self.z_shift_entry_2 = ttk.Entry(shift_frame, textvariable=self.z_shift_var_2, width=6)
        self.z_shift_entry_2.grid(row=1, column=3, padx=(0, 5), pady=(3, 0))
        self.z_shift_entry_2.bind('<Return>', lambda e: self.update_profiles())
        
        ttk.Button(shift_frame, text="Auto Align", command=self.auto_align_profiles_2).grid(row=1, column=4, pady=(3, 0))
        
        # Control buttons for shifts
        button_frame_shift = ttk.Frame(shift_frame)
        button_frame_shift.grid(row=2, column=0, columnspan=5, pady=(5, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame_shift, text="Reset All Shifts", command=self.reset_shifts).grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        ttk.Button(button_frame_shift, text="Update Shifts", 
                  command=self.update_profiles,
                  style="Accent.TButton").grid(row=0, column=1, sticky=tk.W)
        
        # Plot frame
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add toolbar for plot interaction
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Add custom zoom controls
        zoom_frame = ttk.Frame(plot_frame)
        zoom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(zoom_frame, text="Zoom Controls:").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(zoom_frame, text="Auto Scale", command=self.auto_scale).grid(row=0, column=4, padx=(0, 5))
        
        # Add separator and restart button
        ttk.Separator(zoom_frame, orient='vertical').grid(row=0, column=5, sticky=(tk.N, tk.S), padx=(10, 10))
        ttk.Button(zoom_frame, text="Close All Files & Restart", 
                  command=self.restart_application, 
                  style="Accent.TButton").grid(row=0, column=6, padx=(0, 5))
        
        # Enable mouse wheel zoom
        self.canvas.get_tk_widget().bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.get_tk_widget().bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.canvas.get_tk_widget().bind("<Button-5>", self.on_mouse_wheel)  # Linux
        
    def select_dose_file(self):
        """Open file dialog to select DICOM Dose file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        tps_dicom_dir = os.path.join(initial_dir, "TPSDICOM1mm")
        if os.path.exists(tps_dicom_dir):
            initial_dir = tps_dicom_dir
            
        file_path = filedialog.askopenfilename(
            title="Select DICOM RT Dose File",
            initialdir=initial_dir,
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_dicom_file(file_path)
            
    def select_dose_file_2(self):
        """Open file dialog to select second DICOM Dose file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        tps_dicom_dir = os.path.join(initial_dir, "TPSDICOM1mm")
        if os.path.exists(tps_dicom_dir):
            initial_dir = tps_dicom_dir
            
        file_path = filedialog.askopenfilename(
            title="Select Second DICOM RT Dose File",
            initialdir=initial_dir,
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_dicom_file_2(file_path)
            
    def select_plan_file(self):
        """Open file dialog to select DICOM RT Plan file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        tps_dicom_dir = os.path.join(initial_dir, "TPSDICOM1mm")
        if os.path.exists(tps_dicom_dir):
            initial_dir = tps_dicom_dir
            
        file_path = filedialog.askopenfilename(
            title="Select DICOM RT Plan File 1",
            initialdir=initial_dir,
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_rt_plan_file(file_path)
            
    def select_plan_file_2(self):
        """Open file dialog to select second DICOM RT Plan file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        tps_dicom_dir = os.path.join(initial_dir, "TPSDICOM1mm")
        if os.path.exists(tps_dicom_dir):
            initial_dir = tps_dicom_dir
            
        file_path = filedialog.askopenfilename(
            title="Select DICOM RT Plan File 2",
            initialdir=initial_dir,
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_rt_plan_file_2(file_path)
            
    def select_measurement_file(self):
        """Open file dialog to select measurement (.mcc) file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        measurements_dir = os.path.join(initial_dir, "Measurements")  # Note: Capital M
        if os.path.exists(measurements_dir):
            initial_dir = measurements_dir
            
        file_path = filedialog.askopenfilename(
            title="Select Measurement File (.mcc)",
            initialdir=initial_dir,
            filetypes=[("MCC files", "*.mcc"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_measurement_file(file_path)
            
    def select_measurement_file_2(self):
        """Open file dialog to select second measurement (.mcc) file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        measurements_dir = os.path.join(initial_dir, "Measurements")  # Note: Capital M
        if os.path.exists(measurements_dir):
            initial_dir = measurements_dir
            
        file_path = filedialog.askopenfilename(
            title="Select Second Measurement File (.mcc)",
            initialdir=initial_dir,
            filetypes=[("MCC files", "*.mcc"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_measurement_file_2(file_path)

    def select_file(self):
        """Legacy method - redirect to dose file selection"""
        self.select_dose_file()
        
    def load_rt_plan_file(self, file_path):
        """Load and parse DICOM RT Plan file to extract isocenter"""
        try:
            # Read RT Plan file
            ds = None
            error_messages = []
            
            # Try multiple reading methods
            try:
                ds = pydicom.dcmread(file_path)
            except Exception as e:
                error_messages.append(f"Normal read failed: {str(e)}")
            
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True)
                except Exception as e:
                    error_messages.append(f"Force read failed: {str(e)}")
            
            if ds is None:
                error_msg = "Failed to read RT Plan file:\n" + "\n".join(error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Verify it's an RT Plan file
            is_rtplan = False
            try:
                if hasattr(ds, 'Modality'):
                    is_rtplan = ds.Modality == 'RTPLAN'
                elif hasattr(ds, 'SOPClassUID'):
                    # RT Plan Storage SOP Class UID
                    is_rtplan = str(ds.SOPClassUID) == '1.2.840.10008.5.1.4.1.1.481.5'
            except:
                pass
            
            if not is_rtplan and hasattr(ds, 'Modality'):
                response = messagebox.askyesno("Warning", 
                    f"File modality is '{ds.Modality}', not 'RTPLAN'. Continue anyway?")
                if not response:
                    return
            
            # Extract isocenter position from beam sequence
            self.isocenter_position = None
            try:
                if hasattr(ds, 'BeamSequence') and ds.BeamSequence:
                    # Get isocenter from first beam
                    beam = ds.BeamSequence[0]
                    if hasattr(beam, 'ControlPointSequence') and beam.ControlPointSequence:
                        control_point = beam.ControlPointSequence[0]
                        if hasattr(control_point, 'IsocenterPosition'):
                            self.isocenter_position = [float(x) for x in control_point.IsocenterPosition]
                            print(f"Isocenter position found: {self.isocenter_position} mm")
                        elif hasattr(beam, 'IsocenterPosition'):
                            self.isocenter_position = [float(x) for x in beam.IsocenterPosition]
                            print(f"Isocenter position found (beam level): {self.isocenter_position} mm")
                
                if self.isocenter_position is None:
                    # Try alternative locations
                    if hasattr(ds, 'PatientSetupSequence') and ds.PatientSetupSequence:
                        setup = ds.PatientSetupSequence[0]
                        if hasattr(setup, 'IsocenterPosition'):
                            self.isocenter_position = [float(x) for x in setup.IsocenterPosition]
                            print(f"Isocenter position found (setup): {self.isocenter_position} mm")
                
            except Exception as e:
                print(f"Error extracting isocenter: {str(e)}")
            
            if self.isocenter_position is None:
                messagebox.showwarning("Warning", 
                    "No isocenter position found in RT Plan file. Using dose grid center as origin.")
                self.isocenter_position = None
            else:
                # Store RT Plan data
                self.rt_plan_data = ds
                self.plan_file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                
                # Update coordinate system and reset to isocenter
                if self.dose_data is not None:
                    self.x_var.set("0.0")      # Crossplane
                    self.z_var.set("0.0")      # Inplane
                    self.y_var.set("0.0")      # Depth
                    self.coord_info_label.config(text="Coordinates: Relative to isocenter")
                    self.update_profiles()
                
                messagebox.showinfo("Success", 
                    f"RT Plan loaded successfully!\nIsocenter: {self.isocenter_position}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load RT Plan file:\n{str(e)}")
            
    def load_rt_plan_file_2(self, file_path):
        """Load and parse second DICOM RT Plan file to extract isocenter"""
        try:
            # Read RT Plan file
            ds = None
            error_messages = []
            
            # Try multiple reading methods
            try:
                ds = pydicom.dcmread(file_path)
            except Exception as e:
                error_messages.append(f"Normal read failed: {str(e)}")
            
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True)
                except Exception as e:
                    error_messages.append(f"Force read failed: {str(e)}")
            
            if ds is None:
                error_msg = "Failed to read second RT Plan file:\n" + "\n".join(error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Verify it's an RT Plan file
            is_rtplan = False
            try:
                if hasattr(ds, 'Modality'):
                    is_rtplan = ds.Modality == 'RTPLAN'
                elif hasattr(ds, 'SOPClassUID'):
                    # RT Plan Storage SOP Class UID
                    is_rtplan = str(ds.SOPClassUID) == '1.2.840.10008.5.1.4.1.1.481.5'
            except:
                pass
            
            if not is_rtplan and hasattr(ds, 'Modality'):
                response = messagebox.askyesno("Warning", 
                    f"Second file modality is '{ds.Modality}', not 'RTPLAN'. Continue anyway?")
                if not response:
                    return
            
            # Extract isocenter position from beam sequence
            self.isocenter_position_2 = None
            try:
                if hasattr(ds, 'BeamSequence') and ds.BeamSequence:
                    # Get isocenter from first beam
                    beam = ds.BeamSequence[0]
                    if hasattr(beam, 'ControlPointSequence') and beam.ControlPointSequence:
                        control_point = beam.ControlPointSequence[0]
                        if hasattr(control_point, 'IsocenterPosition'):
                            self.isocenter_position_2 = [float(x) for x in control_point.IsocenterPosition]
                            print(f"Second isocenter position found: {self.isocenter_position_2} mm")
                        elif hasattr(beam, 'IsocenterPosition'):
                            self.isocenter_position_2 = [float(x) for x in beam.IsocenterPosition]
                            print(f"Second isocenter position found (beam level): {self.isocenter_position_2} mm")
                
                if self.isocenter_position_2 is None:
                    # Try alternative locations
                    if hasattr(ds, 'PatientSetupSequence') and ds.PatientSetupSequence:
                        setup = ds.PatientSetupSequence[0]
                        if hasattr(setup, 'IsocenterPosition'):
                            self.isocenter_position_2 = [float(x) for x in setup.IsocenterPosition]
                            print(f"Second isocenter position found (setup): {self.isocenter_position_2} mm")
                
            except Exception as e:
                print(f"Error extracting second isocenter: {str(e)}")
            
            if self.isocenter_position_2 is None:
                messagebox.showwarning("Warning", 
                    "No isocenter position found in second RT Plan file. Using dose grid center as origin for file 2.")
                self.isocenter_position_2 = None
            else:
                # Store RT Plan data
                self.rt_plan_data_2 = ds
                self.plan_file_label_2.config(text=f"Loaded: {os.path.basename(file_path)}")
                
                # Update profiles if dose data is available
                if self.dose_data_2 is not None:
                    self.update_profiles()
                
                messagebox.showinfo("Success", 
                    f"Second RT Plan loaded successfully!\nIsocenter: {self.isocenter_position_2}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load second RT Plan file:\n{str(e)}")
            
    def load_measurement_file(self, file_path):
        """Load and parse measurement (.mcc) file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
            # Initialize measurement data
            self.crossplane_measurement = None
            self.inplane_measurement = None
            
            # Split content into sections (each scan) - look for BEGIN_SCAN...END_SCAN blocks
            scan_pattern = r'BEGIN_SCAN\s+\d+(.*?)END_SCAN\s+\d+'
            scan_matches = re.findall(scan_pattern, content, re.DOTALL)
            
            print(f"Found {len(scan_matches)} scan sections in measurement file")
            
            for i, section in enumerate(scan_matches):
                print(f"Processing scan section {i+1}...")
                
                # Check if this section contains profile data
                if 'SCAN_CURVETYPE=' in section and 'BEGIN_DATA' in section and 'END_DATA' in section:
                    
                    # Find and print the curve type for debugging
                    curvetype_match = None
                    for line in section.split('\n'):
                        if 'SCAN_CURVETYPE=' in line:
                            curvetype_match = line.strip()
                            print(f"Found curve type: {curvetype_match}")
                            break
                    
                    # Determine profile type - look for the exact pattern
                    if 'SCAN_CURVETYPE=CROSSPLANE_PROFILE' in section:
                        profile_type = 'crossplane'
                        print("Identified as crossplane profile")
                    elif 'SCAN_CURVETYPE=INPLANE_PROFILE' in section:
                        profile_type = 'inplane'
                        print("Identified as inplane profile")
                    else:
                        print(f"Skipping section - unknown profile type: {curvetype_match}")
                        continue  # Skip unknown profile types
                    
                    # Extract data between BEGIN_DATA and END_DATA
                    try:
                        start_idx = section.find('BEGIN_DATA')
                        end_idx = section.find('END_DATA')
                        
                        if start_idx == -1 or end_idx == -1:
                            continue
                            
                        data_section = section[start_idx + len('BEGIN_DATA'):end_idx]
                        
                        # Parse data lines
                        positions = []
                        values = []
                        
                        for line in data_section.strip().split('\n'):
                            line = line.strip()
                            if not line or line.startswith('#') or line.startswith('%'):
                                continue
                                
                            try:
                                # Split line and get first two values
                                # Handle both tab and space separation
                                parts = line.replace('\t', ' ').split()
                                if len(parts) >= 2:
                                    position = float(parts[0])
                                    # Handle scientific notation like 12.600E-03
                                    value_str = parts[1].replace('E-', 'e-').replace('E+', 'e+')
                                    value = float(value_str)
                                    positions.append(position)
                                    values.append(value)
                            except (ValueError, IndexError):
                                print(f"Skipping malformed line: {line}")
                                continue  # Skip malformed lines
                        
                        if positions and values:
                            # Convert to numpy arrays
                            positions = np.array(positions)
                            values = np.array(values)
                            
                            # Store the measurement data
                            if profile_type == 'crossplane':
                                self.crossplane_measurement = {'positions': positions, 'values': values}
                                print(f"Loaded crossplane measurement: {len(positions)} points")
                            elif profile_type == 'inplane':
                                self.inplane_measurement = {'positions': positions, 'values': values}
                                print(f"Loaded inplane measurement: {len(positions)} points")
                                
                    except Exception as e:
                        print(f"Error parsing profile data: {str(e)}")
                        continue
            
            # Update GUI
            self.measurement_file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            
            # Check what was loaded
            loaded_profiles = []
            if self.crossplane_measurement is not None:
                loaded_profiles.append("crossplane")
            if self.inplane_measurement is not None:
                loaded_profiles.append("inplane")
                
            if loaded_profiles:
                messagebox.showinfo("Success", 
                    f"Measurement file loaded successfully!\nProfiles found: {', '.join(loaded_profiles)}")
                
                # Set default position values if they're empty (for measurement-only mode)
                if not self.x_var.get():
                    self.x_var.set("0.0")
                if not self.z_var.get():
                    self.z_var.set("0.0")
                if not self.y_var.get():
                    self.y_var.set("0.0")
                
                # Update profiles (now works even without DICOM data)
                self.update_profiles()
            else:
                messagebox.showwarning("Warning", 
                    "No valid profile data found in the measurement file.\nLooking for CROSSPLANE_PROFILE or INPLANE_PROFILE sections.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load measurement file:\n{str(e)}")
            
    def load_dicom_file_2(self, file_path):
        """Load and parse second DICOM RT Dose file"""
        try:
            # Read DICOM file with multiple fallback methods
            ds = None
            error_messages = []
            
            # Method 1: Normal reading
            try:
                ds = pydicom.dcmread(file_path)
            except Exception as e:
                error_messages.append(f"Normal read failed: {str(e)}")
            
            # Method 2: Force reading
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True)
                except Exception as e:
                    error_messages.append(f"Force read failed: {str(e)}")
            
            # Method 3: Force reading with stop_before_pixels=False
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True, stop_before_pixels=False)
                except Exception as e:
                    error_messages.append(f"Force read (no stop) failed: {str(e)}")
            
            # Method 4: Read with defer_size and force
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True, defer_size="1 KB")
                except Exception as e:
                    error_messages.append(f"Deferred read failed: {str(e)}")
            
            if ds is None:
                error_msg = "All DICOM reading methods failed:\n" + "\n".join(error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Check if it's likely an RT Dose file (more flexible check)
            is_rtdose = False
            try:
                if hasattr(ds, 'Modality'):
                    is_rtdose = ds.Modality == 'RTDOSE'
                elif hasattr(ds, 'SOPClassUID'):
                    # RT Dose Storage SOP Class UID
                    is_rtdose = str(ds.SOPClassUID) == '1.2.840.10008.5.1.4.1.1.481.2'
                elif hasattr(ds, 'pixel_array'):
                    # If it has pixel data, assume it could be a dose file
                    is_rtdose = True
            except:
                # If we can't determine the modality, just proceed
                is_rtdose = True
            
            if not is_rtdose and hasattr(ds, 'Modality'):
                # Only show error if we're sure it's not an RT Dose file
                response = messagebox.askyesno("Warning", 
                    f"File modality is '{ds.Modality}', not 'RTDOSE'. Continue anyway?")
                if not response:
                    return
                
            # Extract dose data with multiple approaches
            self.dose_data_2 = None
            pixel_error_messages = []
            
            # Method 1: Direct pixel_array access
            try:
                self.dose_data_2 = ds.pixel_array.astype(np.float32)
            except Exception as e:
                pixel_error_messages.append(f"Direct pixel_array failed: {str(e)}")
            
            # Method 2: Access PixelData directly and convert
            if self.dose_data_2 is None:
                try:
                    if hasattr(ds, 'PixelData'):
                        # Get basic image info
                        rows = getattr(ds, 'Rows', 512)
                        columns = getattr(ds, 'Columns', 512)
                        frames = getattr(ds, 'NumberOfFrames', 1)
                        bits_allocated = getattr(ds, 'BitsAllocated', 16)
                        
                        # Convert pixel data based on bits allocated
                        if bits_allocated == 16:
                            dtype = np.uint16
                        elif bits_allocated == 32:
                            dtype = np.uint32
                        else:
                            dtype = np.uint8
                            
                        # Convert bytes to numpy array
                        pixel_bytes = ds.PixelData
                        pixel_array = np.frombuffer(pixel_bytes, dtype=dtype)
                        
                        # Reshape to 3D
                        if frames > 1:
                            self.dose_data_2 = pixel_array.reshape(frames, rows, columns).astype(np.float32)
                        else:
                            self.dose_data_2 = pixel_array.reshape(rows, columns).astype(np.float32)
                            # Add frame dimension if missing
                            if len(self.dose_data_2.shape) == 2:
                                self.dose_data_2 = self.dose_data_2[np.newaxis, :, :]
                                
                except Exception as e:
                    pixel_error_messages.append(f"Manual PixelData conversion failed: {str(e)}")
            
            if self.dose_data_2 is None:
                error_msg = "All pixel data extraction methods failed:\n" + "\n".join(pixel_error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Get scaling factor with fallback
            try:
                if hasattr(ds, 'DoseGridScaling'):
                    self.dose_grid_scaling_2 = float(ds.DoseGridScaling)
                else:
                    self.dose_grid_scaling_2 = 1.0
                    messagebox.showwarning("Warning", "No DoseGridScaling found for file 2, using 1.0")
            except:
                self.dose_grid_scaling_2 = 1.0
                messagebox.showwarning("Warning", "Error reading DoseGridScaling for file 2, using 1.0")
                
            # Scale the dose data
            try:
                self.dose_data_2 *= self.dose_grid_scaling_2
            except:
                messagebox.showwarning("Warning", "Error scaling dose data for file 2")
            
            # Get spatial information with fallbacks
            try:
                if hasattr(ds, 'PixelSpacing'):
                    self.pixel_spacing_2 = [float(x) for x in ds.PixelSpacing]
                else:
                    self.pixel_spacing_2 = [1.0, 1.0]
                    messagebox.showwarning("Warning", "No PixelSpacing found for file 2, using [1.0, 1.0] mm")
            except:
                self.pixel_spacing_2 = [1.0, 1.0]
                messagebox.showwarning("Warning", "Error reading PixelSpacing for file 2, using [1.0, 1.0] mm")
                
            try:
                if hasattr(ds, 'SliceThickness') and ds.SliceThickness is not None:
                    self.slice_thickness_2 = float(ds.SliceThickness)
                elif hasattr(ds, 'GridFrameOffsetVector') and ds.GridFrameOffsetVector is not None:
                    # Calculate slice thickness from frame offset vector
                    offsets = [float(x) for x in ds.GridFrameOffsetVector]
                    if len(offsets) > 1:
                        self.slice_thickness_2 = abs(offsets[1] - offsets[0])
                        print(f"Calculated slice thickness for file 2 from GridFrameOffsetVector: {self.slice_thickness_2:.2f} mm")
                    else:
                        self.slice_thickness_2 = 1.0
                        print("GridFrameOffsetVector for file 2 has only one element, using default 1.0 mm")
                elif hasattr(ds, 'SpacingBetweenSlices') and ds.SpacingBetweenSlices is not None:
                    self.slice_thickness_2 = float(ds.SpacingBetweenSlices)
                else:
                    self.slice_thickness_2 = 1.0
                    print(f"No slice thickness information found in second DICOM file. Using default: 1.0 mm")
            except Exception as e:
                self.slice_thickness_2 = 1.0
                print(f"Error reading slice thickness for file 2 ({str(e)}), using 1.0 mm")
                
            # Get grid frame offset vector if available
            try:
                if hasattr(ds, 'GridFrameOffsetVector'):
                    self.grid_frame_offset_vector_2 = [float(x) for x in ds.GridFrameOffsetVector]
                else:
                    self.grid_frame_offset_vector_2 = None
            except:
                self.grid_frame_offset_vector_2 = None
                
            # Get image position and orientation for coordinate transformation
            try:
                if hasattr(ds, 'ImagePositionPatient'):
                    self.dose_image_position_2 = [float(x) for x in ds.ImagePositionPatient]
                    print(f"Second dose image position: {self.dose_image_position_2}")
                else:
                    self.dose_image_position_2 = [0.0, 0.0, 0.0]
                    print("No ImagePositionPatient found for file 2, using [0, 0, 0]")
            except:
                self.dose_image_position_2 = [0.0, 0.0, 0.0]
                print("Error reading ImagePositionPatient for file 2, using [0, 0, 0]")
                
            try:
                if hasattr(ds, 'ImageOrientationPatient'):
                    self.dose_image_orientation_2 = [float(x) for x in ds.ImageOrientationPatient]
                    print(f"Second dose image orientation: {self.dose_image_orientation_2}")
                else:
                    # Default orientation: [1,0,0,0,1,0] (standard axial)
                    self.dose_image_orientation_2 = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                    print("No ImageOrientationPatient found for file 2, using default axial orientation")
            except:
                self.dose_image_orientation_2 = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                print("Error reading ImageOrientationPatient for file 2, using default")
                
            # Get dimensions
            if len(self.dose_data_2.shape) == 3:
                self.number_of_frames_2, self.rows_2, self.columns_2 = self.dose_data_2.shape
            else:
                messagebox.showerror("Error", "Unexpected dose data dimensions for file 2")
                return
                
            # Update GUI
            self.dose_file_label_2.config(text=f"Loaded: {os.path.basename(file_path)}")
            
            # Check coordinate system compatibility if both files are loaded
            if self.dose_data is not None:
                self.check_coordinate_compatibility()
            
            # Update profiles
            self.update_profiles()
            
            messagebox.showinfo("Success", f"Second DICOM file loaded successfully!\nDimensions: {self.columns_2} x {self.rows_2} x {self.number_of_frames_2}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load second DICOM file:\n{str(e)}")
            
    def load_measurement_file_2(self, file_path):
        """Load and parse second measurement (.mcc) file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
            # Initialize second measurement data
            self.crossplane_measurement_2 = None
            self.inplane_measurement_2 = None
            
            # Split content into sections (each scan) - look for BEGIN_SCAN...END_SCAN blocks
            scan_pattern = r'BEGIN_SCAN\s+\d+(.*?)END_SCAN\s+\d+'
            scan_matches = re.findall(scan_pattern, content, re.DOTALL)
            
            print(f"Found {len(scan_matches)} scan sections in second measurement file")
            
            for i, section in enumerate(scan_matches):
                print(f"Processing scan section {i+1} from file 2...")
                
                # Check if this section contains profile data
                if 'SCAN_CURVETYPE=' in section and 'BEGIN_DATA' in section and 'END_DATA' in section:
                    
                    # Find and print the curve type for debugging
                    curvetype_match = None
                    for line in section.split('\n'):
                        if 'SCAN_CURVETYPE=' in line:
                            curvetype_match = line.strip()
                            print(f"Found curve type in file 2: {curvetype_match}")
                            break
                    
                    # Determine profile type - look for the exact pattern
                    if 'SCAN_CURVETYPE=CROSSPLANE_PROFILE' in section:
                        profile_type = 'crossplane'
                        print("Identified as crossplane profile (file 2)")
                    elif 'SCAN_CURVETYPE=INPLANE_PROFILE' in section:
                        profile_type = 'inplane'
                        print("Identified as inplane profile (file 2)")
                    else:
                        print(f"Skipping section - unknown profile type: {curvetype_match}")
                        continue  # Skip unknown profile types
                    
                    # Extract data between BEGIN_DATA and END_DATA
                    try:
                        start_idx = section.find('BEGIN_DATA')
                        end_idx = section.find('END_DATA')
                        
                        if start_idx == -1 or end_idx == -1:
                            continue
                            
                        data_section = section[start_idx + len('BEGIN_DATA'):end_idx]
                        
                        # Parse data lines
                        positions = []
                        values = []
                        
                        for line in data_section.strip().split('\n'):
                            line = line.strip()
                            if not line or line.startswith('#') or line.startswith('%'):
                                continue
                                
                            try:
                                # Split line and get first two values
                                # Handle both tab and space separation
                                parts = line.replace('\t', ' ').split()
                                if len(parts) >= 2:
                                    position = float(parts[0])
                                    # Handle scientific notation like 12.600E-03
                                    value_str = parts[1].replace('E-', 'e-').replace('E+', 'e+')
                                    value = float(value_str)
                                    positions.append(position)
                                    values.append(value)
                            except (ValueError, IndexError):
                                print(f"Skipping malformed line in file 2: {line}")
                                continue  # Skip malformed lines
                        
                        if positions and values:
                            # Convert to numpy arrays
                            positions = np.array(positions)
                            values = np.array(values)
                            
                            # Store the measurement data
                            if profile_type == 'crossplane':
                                self.crossplane_measurement_2 = {'positions': positions, 'values': values}
                                print(f"Loaded crossplane measurement from file 2: {len(positions)} points")
                            elif profile_type == 'inplane':
                                self.inplane_measurement_2 = {'positions': positions, 'values': values}
                                print(f"Loaded inplane measurement from file 2: {len(positions)} points")
                                
                    except Exception as e:
                        print(f"Error parsing profile data from file 2: {str(e)}")
                        continue
            
            # Update GUI
            self.measurement_file_label_2.config(text=f"Loaded: {os.path.basename(file_path)}")
            
            # Check what was loaded
            loaded_profiles = []
            if self.crossplane_measurement_2 is not None:
                loaded_profiles.append("crossplane")
            if self.inplane_measurement_2 is not None:
                loaded_profiles.append("inplane")
                
            if loaded_profiles:
                messagebox.showinfo("Success", 
                    f"Second measurement file loaded successfully!\nProfiles found: {', '.join(loaded_profiles)}")
                
                # Set default position values if they're empty (for measurement-only mode)
                if not self.x_var.get():
                    self.x_var.set("0.0")
                if not self.z_var.get():
                    self.z_var.set("0.0")
                if not self.y_var.get():
                    self.y_var.set("0.0")
                
                # Update profiles (now works even without DICOM data)
                self.update_profiles()
            else:
                messagebox.showwarning("Warning", 
                    "No valid profile data found in the second measurement file.\nLooking for CROSSPLANE_PROFILE or INPLANE_PROFILE sections.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load second measurement file:\n{str(e)}")
            
    def load_dicom_file(self, file_path):
        """Load and parse DICOM RT Dose file"""
        try:
            # Read DICOM file with multiple fallback methods
            ds = None
            error_messages = []
            
            # Method 1: Normal reading
            try:
                ds = pydicom.dcmread(file_path)
            except Exception as e:
                error_messages.append(f"Normal read failed: {str(e)}")
            
            # Method 2: Force reading
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True)
                except Exception as e:
                    error_messages.append(f"Force read failed: {str(e)}")
            
            # Method 3: Force reading with stop_before_pixels=False
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True, stop_before_pixels=False)
                except Exception as e:
                    error_messages.append(f"Force read (no stop) failed: {str(e)}")
            
            # Method 4: Read with defer_size and force
            if ds is None:
                try:
                    ds = pydicom.dcmread(file_path, force=True, defer_size="1 KB")
                except Exception as e:
                    error_messages.append(f"Deferred read failed: {str(e)}")
            
            if ds is None:
                error_msg = "All DICOM reading methods failed:\n" + "\n".join(error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Check if it's likely an RT Dose file (more flexible check)
            is_rtdose = False
            try:
                if hasattr(ds, 'Modality'):
                    is_rtdose = ds.Modality == 'RTDOSE'
                elif hasattr(ds, 'SOPClassUID'):
                    # RT Dose Storage SOP Class UID
                    is_rtdose = str(ds.SOPClassUID) == '1.2.840.10008.5.1.4.1.1.481.2'
                elif hasattr(ds, 'pixel_array'):
                    # If it has pixel data, assume it could be a dose file
                    is_rtdose = True
            except:
                # If we can't determine the modality, just proceed
                is_rtdose = True
            
            if not is_rtdose and hasattr(ds, 'Modality'):
                # Only show error if we're sure it's not an RT Dose file
                response = messagebox.askyesno("Warning", 
                    f"File modality is '{ds.Modality}', not 'RTDOSE'. Continue anyway?")
                if not response:
                    return
                
            # Extract dose data with multiple approaches
            self.dose_data = None
            pixel_error_messages = []
            
            # Method 1: Direct pixel_array access
            try:
                self.dose_data = ds.pixel_array.astype(np.float32)
            except Exception as e:
                pixel_error_messages.append(f"Direct pixel_array failed: {str(e)}")
            
            # Method 2: Access PixelData directly and convert
            if self.dose_data is None:
                try:
                    if hasattr(ds, 'PixelData'):
                        # Get basic image info
                        rows = getattr(ds, 'Rows', 512)
                        columns = getattr(ds, 'Columns', 512)
                        frames = getattr(ds, 'NumberOfFrames', 1)
                        bits_allocated = getattr(ds, 'BitsAllocated', 16)
                        
                        # Convert pixel data based on bits allocated
                        if bits_allocated == 16:
                            dtype = np.uint16
                        elif bits_allocated == 32:
                            dtype = np.uint32
                        else:
                            dtype = np.uint8
                            
                        # Convert bytes to numpy array
                        pixel_bytes = ds.PixelData
                        pixel_array = np.frombuffer(pixel_bytes, dtype=dtype)
                        
                        # Reshape to 3D
                        if frames > 1:
                            self.dose_data = pixel_array.reshape(frames, rows, columns).astype(np.float32)
                        else:
                            self.dose_data = pixel_array.reshape(rows, columns).astype(np.float32)
                            # Add frame dimension if missing
                            if len(self.dose_data.shape) == 2:
                                self.dose_data = self.dose_data[np.newaxis, :, :]
                                
                except Exception as e:
                    pixel_error_messages.append(f"Manual PixelData conversion failed: {str(e)}")
            
            if self.dose_data is None:
                error_msg = "All pixel data extraction methods failed:\n" + "\n".join(pixel_error_messages)
                messagebox.showerror("Error", error_msg)
                return
            
            # Get scaling factor with fallback
            try:
                if hasattr(ds, 'DoseGridScaling'):
                    self.dose_grid_scaling = float(ds.DoseGridScaling)
                else:
                    self.dose_grid_scaling = 1.0
                    messagebox.showwarning("Warning", "No DoseGridScaling found, using 1.0")
            except:
                self.dose_grid_scaling = 1.0
                messagebox.showwarning("Warning", "Error reading DoseGridScaling, using 1.0")
                
            # Scale the dose data
            try:
                self.dose_data *= self.dose_grid_scaling
            except:
                messagebox.showwarning("Warning", "Error scaling dose data")
            
            # Get spatial information with fallbacks
            try:
                if hasattr(ds, 'PixelSpacing'):
                    self.pixel_spacing = [float(x) for x in ds.PixelSpacing]
                else:
                    self.pixel_spacing = [1.0, 1.0]
                    messagebox.showwarning("Warning", "No PixelSpacing found, using [1.0, 1.0] mm")
            except:
                self.pixel_spacing = [1.0, 1.0]
                messagebox.showwarning("Warning", "Error reading PixelSpacing, using [1.0, 1.0] mm")
                
            try:
                if hasattr(ds, 'SliceThickness') and ds.SliceThickness is not None:
                    self.slice_thickness = float(ds.SliceThickness)
                elif hasattr(ds, 'GridFrameOffsetVector') and ds.GridFrameOffsetVector is not None:
                    # Calculate slice thickness from frame offset vector
                    offsets = [float(x) for x in ds.GridFrameOffsetVector]
                    if len(offsets) > 1:
                        self.slice_thickness = abs(offsets[1] - offsets[0])
                        print(f"Calculated slice thickness from GridFrameOffsetVector: {self.slice_thickness:.2f} mm")
                    else:
                        self.slice_thickness = 1.0
                        print("GridFrameOffsetVector has only one element, using default 1.0 mm")
                elif hasattr(ds, 'SpacingBetweenSlices') and ds.SpacingBetweenSlices is not None:
                    self.slice_thickness = float(ds.SpacingBetweenSlices)
                elif hasattr(ds, 'ImagePositionPatient'):
                    # Try to calculate from ImagePositionPatient if it's a sequence
                    try:
                        if hasattr(ds.ImagePositionPatient, '__len__') and len(ds.ImagePositionPatient) >= 3:
                            # For single slice, use a default
                            self.slice_thickness = 1.0
                        else:
                            self.slice_thickness = 1.0
                    except:
                        self.slice_thickness = 1.0
                elif hasattr(ds, 'ImageOrientationPatient') and hasattr(ds, 'ImagePositionPatient'):
                    # Try to extract from geometric information
                    self.slice_thickness = 1.0  # Default if we can't calculate
                else:
                    self.slice_thickness = 1.0
                    print(f"No slice thickness information found in DICOM file. Using default: 1.0 mm")
            except Exception as e:
                self.slice_thickness = 1.0
                print(f"Error reading slice thickness ({str(e)}), using 1.0 mm")
                
            # Get grid frame offset vector if available
            try:
                if hasattr(ds, 'GridFrameOffsetVector'):
                    self.grid_frame_offset_vector = [float(x) for x in ds.GridFrameOffsetVector]
                else:
                    self.grid_frame_offset_vector = None
            except:
                self.grid_frame_offset_vector = None
                
            # Get image position and orientation for coordinate transformation
            try:
                if hasattr(ds, 'ImagePositionPatient'):
                    self.dose_image_position = [float(x) for x in ds.ImagePositionPatient]
                    print(f"Dose image position: {self.dose_image_position}")
                else:
                    self.dose_image_position = [0.0, 0.0, 0.0]
                    print("No ImagePositionPatient found, using [0, 0, 0]")
            except:
                self.dose_image_position = [0.0, 0.0, 0.0]
                print("Error reading ImagePositionPatient, using [0, 0, 0]")
                
            try:
                if hasattr(ds, 'ImageOrientationPatient'):
                    self.dose_image_orientation = [float(x) for x in ds.ImageOrientationPatient]
                    print(f"Dose image orientation: {self.dose_image_orientation}")
                else:
                    # Default orientation: [1,0,0,0,1,0] (standard axial)
                    self.dose_image_orientation = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                    print("No ImageOrientationPatient found, using default axial orientation")
            except:
                self.dose_image_orientation = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                print("Error reading ImageOrientationPatient, using default")
                
            # Get dimensions
            if len(self.dose_data.shape) == 3:
                self.number_of_frames, self.rows, self.columns = self.dose_data.shape
            else:
                messagebox.showerror("Error", "Unexpected dose data dimensions")
                return
                
            # Update GUI
            self.dose_file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            
            # Set default values based on coordinate system
            iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset()
            
            if iso_x_offset is not None:
                # Set defaults relative to isocenter (center of field)
                self.x_var.set("0.0")      # Isocenter X (crossplane)
                self.z_var.set("0.0")      # Isocenter Z (inplane)  
                self.y_var.set("0.0")      # Isocenter Y (depth)
                self.coord_info_label.config(text="Coordinates: Relative to isocenter")
            else:
                # Set defaults relative to dose grid center
                center_x_mm = (self.columns // 2) * self.pixel_spacing[1]   # Crossplane
                center_z_mm = (self.number_of_frames // 2) * self.slice_thickness  # Inplane  
                center_y_mm = (self.rows // 2) * self.pixel_spacing[0]      # Depth
                
                self.x_var.set(f"{center_x_mm:.1f}")
                self.z_var.set(f"{center_z_mm:.1f}")
                self.y_var.set(f"{center_y_mm:.1f}")
                self.coord_info_label.config(text="Coordinates: Relative to dose grid origin")
            
            # Remove slice thickness entry field update (no longer needed)
            # if hasattr(self, 'slice_thickness_var') and self.slice_thickness_var:
            #     self.slice_thickness_var.set(str(self.slice_thickness))
            
            # Show diagnostic info about spatial attributes
            self.show_spatial_diagnostic_info(ds)
            
            # Update profiles
            self.update_profiles()
            
            messagebox.showinfo("Success", f"DICOM file loaded successfully!\nDimensions: {self.columns} x {self.rows} x {self.number_of_frames}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load DICOM file:\n{str(e)}")
            
    def show_spatial_diagnostic_info(self, ds):
        """Show diagnostic information about spatial DICOM attributes"""
        print("\n=== DICOM Spatial Attributes Diagnostic ===")
        
        spatial_attrs = [
            'SliceThickness', 'SpacingBetweenSlices', 'PixelSpacing',
            'GridFrameOffsetVector', 'ImagePositionPatient', 'ImageOrientationPatient',
            'Rows', 'Columns', 'NumberOfFrames', 'DoseGridScaling'
        ]
        
        for attr in spatial_attrs:
            if hasattr(ds, attr):
                try:
                    value = getattr(ds, attr)
                    print(f"✓ {attr}: {value}")
                except Exception as e:
                    print(f"✗ {attr}: Error reading - {str(e)}")
            else:
                print(f"- {attr}: Not present")
        
        # Show isocenter info if available
        if self.isocenter_position is not None:
            print(f"✓ Isocenter Position: {self.isocenter_position}")
            iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset()
            if iso_x_offset is not None:
                print(f"✓ Isocenter Offset (voxels): X={iso_x_offset:.2f}, Y={iso_y_offset:.2f}, Z={iso_z_offset:.2f}")
        else:
            print("- Isocenter Position: Not available")
        
        print("=" * 50)
            
    def check_coordinate_compatibility(self):
        """Check if the two DICOM files have compatible coordinate systems and warn if not"""
        if self.dose_data is None or self.dose_data_2 is None:
            return
            
        # Check pixel spacing differences
        pixel_diff_x = abs(self.pixel_spacing[0] - self.pixel_spacing_2[0])
        pixel_diff_y = abs(self.pixel_spacing[1] - self.pixel_spacing_2[1])
        slice_diff = abs(self.slice_thickness - self.slice_thickness_2)
        
        # Define tolerance (10% difference)
        x_tolerance = 0.1 * self.pixel_spacing[0]
        y_tolerance = 0.1 * self.pixel_spacing[1]
        z_tolerance = 0.1 * self.slice_thickness
        
        warnings = []
        
        if pixel_diff_x > x_tolerance:
            warnings.append(f"Row pixel spacing differs significantly: {self.pixel_spacing[0]:.3f}mm vs {self.pixel_spacing_2[0]:.3f}mm")
        
        if pixel_diff_y > y_tolerance:
            warnings.append(f"Column pixel spacing differs significantly: {self.pixel_spacing[1]:.3f}mm vs {self.pixel_spacing_2[1]:.3f}mm")
        
        if slice_diff > z_tolerance:
            warnings.append(f"Slice thickness differs significantly: {self.slice_thickness:.3f}mm vs {self.slice_thickness_2:.3f}mm")
        
        # Check field of view differences
        if self.isocenter_position is not None and self.isocenter_position_2 is not None:
            fov_x_1 = self.columns * self.pixel_spacing[1]
            fov_y_1 = self.rows * self.pixel_spacing[0]
            fov_z_1 = self.number_of_frames * self.slice_thickness
            
            fov_x_2 = self.columns_2 * self.pixel_spacing_2[1]
            fov_y_2 = self.rows_2 * self.pixel_spacing_2[0]
            fov_z_2 = self.number_of_frames_2 * self.slice_thickness_2
            
            fov_diff_threshold = 50.0  # 50mm difference is significant
            
            if abs(fov_x_1 - fov_x_2) > fov_diff_threshold:
                warnings.append(f"X field of view differs: {fov_x_1:.1f}mm vs {fov_x_2:.1f}mm")
            if abs(fov_y_1 - fov_y_2) > fov_diff_threshold:
                warnings.append(f"Y field of view differs: {fov_y_1:.1f}mm vs {fov_y_2:.1f}mm")
            if abs(fov_z_1 - fov_z_2) > fov_diff_threshold:
                warnings.append(f"Z field of view differs: {fov_z_1:.1f}mm vs {fov_z_2:.1f}mm")
        
        if warnings:
            warning_msg = "Coordinate system differences detected:\n\n" + "\n".join(warnings)
            warning_msg += "\n\nThis may affect profile comparison accuracy. Consider using files with similar resolution for better comparison."
            messagebox.showwarning("Coordinate System Warning", warning_msg)
            
    def calculate_isocenter_offset(self):
        """Calculate the offset of isocenter in dose grid coordinates"""
        if self.isocenter_position is None or self.dose_image_position is None:
            return None, None, None
            
        try:
            # Convert isocenter position to dose grid coordinates
            # DICOM coordinates are in mm, need to convert to voxel indices
            
            # Calculate the offset in mm from dose grid origin
            dx_mm = self.isocenter_position[0] - self.dose_image_position[0]
            dy_mm = self.isocenter_position[1] - self.dose_image_position[1]
            dz_mm = self.isocenter_position[2] - self.dose_image_position[2]
            
            # Convert to voxel coordinates
            x_offset_voxels = dx_mm / self.pixel_spacing[1]  # Column direction
            y_offset_voxels = dy_mm / self.pixel_spacing[0]  # Row direction
            
            # For Z offset, use slice thickness or grid frame offset
            if self.grid_frame_offset_vector and len(self.grid_frame_offset_vector) > 1:
                # Use actual frame positions
                z_offset_voxels = dz_mm / self.slice_thickness
            else:
                z_offset_voxels = dz_mm / self.slice_thickness
            
            print(f"Isocenter offset in voxels: X={x_offset_voxels:.2f}, Y={y_offset_voxels:.2f}, Z={z_offset_voxels:.2f}")
            
            return x_offset_voxels, y_offset_voxels, z_offset_voxels
            
        except Exception as e:
            print(f"Error calculating isocenter offset: {str(e)}")
            return None, None, None
        
    def calculate_isocenter_offset_2(self):
        """Calculate the offset of second isocenter in second dose grid coordinates"""
        if self.isocenter_position_2 is None or self.dose_image_position_2 is None:
            return None, None, None
            
        try:
            # Convert isocenter position to dose grid coordinates
            # DICOM coordinates are in mm, need to convert to voxel indices
            
            # Calculate the offset in mm from dose grid origin
            dx_mm = self.isocenter_position_2[0] - self.dose_image_position_2[0]
            dy_mm = self.isocenter_position_2[1] - self.dose_image_position_2[1]
            dz_mm = self.isocenter_position_2[2] - self.dose_image_position_2[2]
            
            # Convert to voxel coordinates
            x_offset_voxels = dx_mm / self.pixel_spacing_2[1]  # Column direction
            y_offset_voxels = dy_mm / self.pixel_spacing_2[0]  # Row direction
            
            # For Z offset, use slice thickness or grid frame offset
            if self.grid_frame_offset_vector_2 and len(self.grid_frame_offset_vector_2) > 1:
                # Use actual frame positions
                z_offset_voxels = dz_mm / self.slice_thickness_2
            else:
                z_offset_voxels = dz_mm / self.slice_thickness_2
            
            print(f"Second isocenter offset in voxels: X={x_offset_voxels:.2f}, Y={y_offset_voxels:.2f}, Z={z_offset_voxels:.2f}")
            
            return x_offset_voxels, y_offset_voxels, z_offset_voxels
            
        except Exception as e:
            print(f"Error calculating second isocenter offset: {str(e)}")
            return None, None, None
        
    def update_profiles(self):
        """Update the dose profiles based on current settings"""
        # Check if we have any data to plot (DICOM or measurements)
        has_dicom_data = self.dose_data is not None or self.dose_data_2 is not None
        has_measurement_data = (self.crossplane_measurement is not None or 
                               self.inplane_measurement is not None or
                               self.crossplane_measurement_2 is not None or 
                               self.inplane_measurement_2 is not None)
        
        if not has_dicom_data and not has_measurement_data:
            return
            
        try:
            # Get current positions in mm - set defaults if empty
            try:
                x_str = self.x_var.get().strip()
                z_str = self.z_var.get().strip() 
                y_str = self.y_var.get().strip()
                
                # Set defaults for empty fields
                if not x_str:
                    x_str = "0.0"
                    self.x_var.set("0.0")
                if not z_str:
                    z_str = "0.0"
                    self.z_var.set("0.0")
                if not y_str:
                    y_str = "0.0"
                    self.y_var.set("0.0")
                
                x_mm = float(x_str)      # Crossplane
                z_mm = float(z_str)      # Inplane  
                y_mm = float(y_str)      # Depth
            except ValueError:
                # Set all to defaults and show helpful message
                self.x_var.set("0.0")
                self.z_var.set("0.0")
                self.y_var.set("0.0")
                messagebox.showerror("Error", "Invalid position values detected. Reset to defaults (0.0, 0.0, 0.0)")
                x_mm = z_mm = y_mm = 0.0
            
            # Calculate isocenter offset (using first file for reference if available)
            iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset() if self.dose_data is not None else (None, None, None)
            
            # Clear previous plots
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)
            
            # Determine coordinate label based on available isocenters
            iso_x_offset_2, iso_y_offset_2, iso_z_offset_2 = self.calculate_isocenter_offset_2() if self.dose_data_2 is not None else (None, None, None)
            
            if iso_x_offset is not None and iso_x_offset_2 is not None:
                coordinate_label = "from Respective Isocenters"
            elif iso_x_offset is not None:
                coordinate_label = "from Isocenter (File 1)"
            elif iso_x_offset_2 is not None:
                coordinate_label = "from Isocenter (File 2)"
            else:
                coordinate_label = "from Measurement Coordinates"
            
            # Debug information for coordinate systems
            if self.dose_data is not None and self.dose_data_2 is not None:
                print(f"\n=== COORDINATE SYSTEM DEBUG ===")
                print(f"File 1 - Pixel spacing: {self.pixel_spacing}, Slice thickness: {self.slice_thickness}")
                print(f"File 2 - Pixel spacing: {self.pixel_spacing_2}, Slice thickness: {self.slice_thickness_2}")
                print(f"Position request: X={x_mm}mm, Y={y_mm}mm, Z={z_mm}mm")
                if iso_x_offset is not None:
                    print(f"File 1 isocenter offset: X={iso_x_offset:.2f}, Y={iso_y_offset:.2f}, Z={iso_z_offset:.2f} voxels")
                if iso_x_offset_2 is not None:
                    print(f"File 2 isocenter offset: X={iso_x_offset_2:.2f}, Y={iso_y_offset_2:.2f}, Z={iso_z_offset_2:.2f} voxels")
            
            # Process first DICOM file if available
            if self.dose_data is not None:
                # Convert mm coordinates to voxel indices
                if iso_x_offset is not None:
                    x_pos = int(round((x_mm / self.pixel_spacing[1]) + iso_x_offset))
                    y_pos = int(round((y_mm / self.pixel_spacing[0]) + iso_y_offset))
                    z_idx = int(round((z_mm / self.slice_thickness) + iso_z_offset))
                else:
                    x_pos = int(round(x_mm / self.pixel_spacing[1]))
                    y_pos = int(round(y_mm / self.pixel_spacing[0]))
                    z_idx = int(round(z_mm / self.slice_thickness))
                
                # Validate indices
                x_pos = max(0, min(x_pos, self.columns - 1))
                y_pos = max(0, min(y_pos, self.rows - 1))
                z_idx = max(0, min(z_idx, self.number_of_frames - 1))
                
                print(f"File 1 voxel indices: x={x_pos}, y={y_pos}, z={z_idx}")
                
                # Extract profiles
                x_profile = self.dose_data[z_idx, y_pos, :]
                z_profile = self.dose_data[:, y_pos, x_pos]
                
                # Calculate position arrays
                if iso_x_offset is not None:
                    x_positions = (np.arange(self.columns) - iso_x_offset) * self.pixel_spacing[1]
                    z_positions = (np.arange(self.number_of_frames) - iso_z_offset) * self.slice_thickness
                else:
                    x_positions = np.arange(self.columns) * self.pixel_spacing[1]
                    z_positions = np.arange(self.number_of_frames) * self.slice_thickness
                
                # Apply normalization for first DICOM file
                dicom_norm_factor = 1.0
                if self.dicom_norm_var.get():
                    try:
                        dicom_norm_value = float(self.dicom_norm_var.get())
                        current_dicom_max = max(np.max(x_profile), np.max(z_profile))
                        if current_dicom_max > 0:
                            dicom_norm_factor = dicom_norm_value / current_dicom_max
                    except (ValueError, ZeroDivisionError):
                        pass
                
                x_profile_normalized = x_profile * dicom_norm_factor
                z_profile_normalized = z_profile * dicom_norm_factor
                
                # Plot first DICOM profiles
                ax1.plot(x_positions, x_profile_normalized, 'b--', linewidth=2, label='DICOM 1')
                ax2.plot(z_positions, z_profile_normalized, 'b--', linewidth=2, label='DICOM 1')
            
            # Process second DICOM file if available
            if self.dose_data_2 is not None:
                # Calculate isocenter offset for second file
                iso_x_offset_2, iso_y_offset_2, iso_z_offset_2 = self.calculate_isocenter_offset_2()
                
                # Convert mm coordinates to voxel indices for second file
                if iso_x_offset_2 is not None:
                    x_pos_2 = int(round((x_mm / self.pixel_spacing_2[1]) + iso_x_offset_2))
                    y_pos_2 = int(round((y_mm / self.pixel_spacing_2[0]) + iso_y_offset_2))
                    z_idx_2 = int(round((z_mm / self.slice_thickness_2) + iso_z_offset_2))
                else:
                    x_pos_2 = int(round(x_mm / self.pixel_spacing_2[1]))
                    y_pos_2 = int(round(y_mm / self.pixel_spacing_2[0]))
                    z_idx_2 = int(round(z_mm / self.slice_thickness_2))
                
                # Validate indices for second file
                x_pos_2 = max(0, min(x_pos_2, self.columns_2 - 1))
                y_pos_2 = max(0, min(y_pos_2, self.rows_2 - 1))
                z_idx_2 = max(0, min(z_idx_2, self.number_of_frames_2 - 1))
                
                print(f"File 2 voxel indices: x={x_pos_2}, y={y_pos_2}, z={z_idx_2}")
                
                # Extract profiles from second file
                x_profile_2 = self.dose_data_2[z_idx_2, y_pos_2, :]
                z_profile_2 = self.dose_data_2[:, y_pos_2, x_pos_2]
                
                # Calculate position arrays for second file
                if iso_x_offset_2 is not None:
                    x_positions_2 = (np.arange(self.columns_2) - iso_x_offset_2) * self.pixel_spacing_2[1]
                    z_positions_2 = (np.arange(self.number_of_frames_2) - iso_z_offset_2) * self.slice_thickness_2
                else:
                    x_positions_2 = np.arange(self.columns_2) * self.pixel_spacing_2[1]
                    z_positions_2 = np.arange(self.number_of_frames_2) * self.slice_thickness_2
                
                print(f"File 2 position ranges: X=[{x_positions_2[0]:.1f}, {x_positions_2[-1]:.1f}], Z=[{z_positions_2[0]:.1f}, {z_positions_2[-1]:.1f}]")
                
                # Apply independent normalization for second DICOM file
                dicom_norm_factor_2 = 1.0
                if hasattr(self, 'dicom_norm_var_2') and self.dicom_norm_var_2.get():
                    try:
                        dicom_norm_value_2 = float(self.dicom_norm_var_2.get())
                        current_dicom_max_2 = max(np.max(x_profile_2), np.max(z_profile_2))
                        if current_dicom_max_2 > 0:
                            dicom_norm_factor_2 = dicom_norm_value_2 / current_dicom_max_2
                    except (ValueError, ZeroDivisionError):
                        pass
                
                x_profile_2_normalized = x_profile_2 * dicom_norm_factor_2
                z_profile_2_normalized = z_profile_2 * dicom_norm_factor_2
                
                # Plot second DICOM profiles
                ax1.plot(x_positions_2, x_profile_2_normalized, 'g--', linewidth=2, label='DICOM 2')
                ax2.plot(z_positions_2, z_profile_2_normalized, 'g--', linewidth=2, label='DICOM 2')
            
            # Determine normalization factors for measurements (independent for each file)
            meas_norm_factor = 1.0
            meas_norm_factor_2 = 1.0
            
            # Normalization for first measurement file
            try:
                if self.meas_norm_var.get():
                    meas_norm_value = float(self.meas_norm_var.get())
                    
                    # Find current measurement maximum for first dataset
                    current_meas_max = 0.0
                    if self.crossplane_measurement is not None:
                        current_meas_max = max(current_meas_max, np.max(self.crossplane_measurement['values']))
                    if self.inplane_measurement is not None:
                        current_meas_max = max(current_meas_max, np.max(self.inplane_measurement['values']))
                    
                    if current_meas_max > 0:
                        meas_norm_factor = meas_norm_value / current_meas_max
            except (ValueError, ZeroDivisionError):
                pass
            
            # Normalization for second measurement file
            try:
                if hasattr(self, 'meas_norm_var_2') and self.meas_norm_var_2.get():
                    meas_norm_value_2 = float(self.meas_norm_var_2.get())
                    
                    # Find current measurement maximum for second dataset
                    current_meas_max_2 = 0.0
                    if self.crossplane_measurement_2 is not None:
                        current_meas_max_2 = max(current_meas_max_2, np.max(self.crossplane_measurement_2['values']))
                    if self.inplane_measurement_2 is not None:
                        current_meas_max_2 = max(current_meas_max_2, np.max(self.inplane_measurement_2['values']))
                    
                    if current_meas_max_2 > 0:
                        meas_norm_factor_2 = meas_norm_value_2 / current_meas_max_2
            except (ValueError, ZeroDivisionError):
                pass
            
            # Add measurement overlay for first crossplane if available
            if self.crossplane_measurement is not None:
                meas_pos = self.crossplane_measurement['positions']
                
                # Apply coordinate shift
                shift_x = 0.0
                try:
                    shift_x = float(self.x_shift_var.get())
                except ValueError:
                    pass
                
                meas_pos_shifted = meas_pos + shift_x
                meas_val = self.crossplane_measurement['values'] * meas_norm_factor
                
                ax1.plot(meas_pos_shifted, meas_val, linestyle=':', color='red', marker='o', 
                        linewidth=2, markersize=4, alpha=0.7, label='Measurement 1')
            
            # Add measurement overlay for second crossplane if available
            if self.crossplane_measurement_2 is not None:
                meas_pos_2 = self.crossplane_measurement_2['positions']
                
                # Apply independent coordinate shift for measurement 2
                shift_x_2 = 0.0
                try:
                    shift_x_2 = float(self.x_shift_var_2.get())
                except ValueError:
                    pass
                
                meas_pos_shifted_2 = meas_pos_2 + shift_x_2
                meas_val_2 = self.crossplane_measurement_2['values'] * meas_norm_factor_2
                
                ax1.plot(meas_pos_shifted_2, meas_val_2, linestyle=':', color='magenta', marker='o', 
                        linewidth=2, markersize=4, alpha=0.7, label='Measurement 2')
            
            # Set labels and title for X profile
            ax1.set_xlabel(f'Crossplane Position (mm) {coordinate_label}')
            y_label = 'Dose' if has_dicom_data else 'Signal'
            ax1.set_ylabel(y_label)
            if has_dicom_data:
                title_parts = [f'Crossplane Profile at Z={z_mm:.1f}mm, Y={y_mm:.1f}mm']
                if self.dose_data is not None and self.dose_data_2 is not None:
                    title_parts.append(f'Resolutions: {self.pixel_spacing[1]:.2f}mm vs {self.pixel_spacing_2[1]:.2f}mm')
                ax1.set_title('\n'.join(title_parts))
            else:
                ax1.set_title('Crossplane Measurement Profiles')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Add measurement overlay for first inplane if available
            if self.inplane_measurement is not None:
                meas_pos = self.inplane_measurement['positions']
                
                # Apply coordinate shift
                shift_z = 0.0
                try:
                    shift_z = float(self.z_shift_var.get())
                except ValueError:
                    pass
                
                meas_pos_shifted = meas_pos + shift_z
                meas_val = self.inplane_measurement['values'] * meas_norm_factor
                
                ax2.plot(meas_pos_shifted, meas_val, linestyle=':', color='red', marker='o', 
                        linewidth=2, markersize=4, alpha=0.7, label='Measurement 1')
            
            # Add measurement overlay for second inplane if available
            if self.inplane_measurement_2 is not None:
                meas_pos_2 = self.inplane_measurement_2['positions']
                
                # Apply independent coordinate shift for measurement 2
                shift_z_2 = 0.0
                try:
                    shift_z_2 = float(self.z_shift_var_2.get())
                except ValueError:
                    pass
                
                meas_pos_shifted_2 = meas_pos_2 + shift_z_2
                meas_val_2 = self.inplane_measurement_2['values'] * meas_norm_factor_2
                
                ax2.plot(meas_pos_shifted_2, meas_val_2, linestyle=':', color='magenta', marker='o', 
                        linewidth=2, markersize=4, alpha=0.7, label='Measurement 2')
            
            # Set labels and title for Z profile
            ax2.set_xlabel(f'Inplane Position (mm) {coordinate_label}')
            ax2.set_ylabel(y_label)
            if has_dicom_data:
                title_parts = [f'Inplane Profile at X={x_mm:.1f}mm, Y={y_mm:.1f}mm']
                if self.dose_data is not None and self.dose_data_2 is not None:
                    title_parts.append(f'Slice thickness: {self.slice_thickness:.2f}mm vs {self.slice_thickness_2:.2f}mm')
                ax2.set_title('\n'.join(title_parts))
            else:
                ax2.set_title('Inplane Measurement Profiles')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Apply zoom if enabled
            if self.zoom_enabled_var.get():
                try:
                    x_center = float(self.zoom_x_center_var.get())
                    x_range = float(self.zoom_x_range_var.get())
                    ax1.set_xlim(x_center - x_range/2, x_center + x_range/2)
                except ValueError:
                    pass
                
                try:
                    z_center = float(self.zoom_z_center_var.get())
                    z_range = float(self.zoom_z_range_var.get())
                    ax2.set_xlim(z_center - z_range/2, z_center + z_range/2)
                except ValueError:
                    pass
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update profiles:\n{str(e)}")
    
    def zoom_in(self):
        """Zoom in on both plots"""
        if hasattr(self, 'figure') and self.figure.get_axes():
            for ax in self.figure.get_axes():
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                # Zoom in by 25%
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                x_range = (xlim[1] - xlim[0]) * 0.75 / 2
                y_range = (ylim[1] - ylim[0]) * 0.75 / 2
                
                ax.set_xlim(x_center - x_range, x_center + x_range)
                ax.set_ylim(y_center - y_range, y_center + y_range)
            
            self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out on both plots"""
        if hasattr(self, 'figure') and self.figure.get_axes():
            for ax in self.figure.get_axes():
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                # Zoom out by 25%
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                x_range = (xlim[1] - xlim[0]) * 1.25 / 2
                y_range = (ylim[1] - ylim[0]) * 1.25 / 2
                
                ax.set_xlim(x_center - x_range, x_center + x_range)
                ax.set_ylim(y_center - y_range, y_center + y_range)
            
            self.canvas.draw()
    
    def reset_zoom(self):
        """Reset zoom to show full data range"""
        if hasattr(self, 'figure') and self.figure.get_axes():
            for ax in self.figure.get_axes():
                ax.relim()
                ax.autoscale()
            
            self.canvas.draw()
    
    def restart_application(self):
        """Reset all data and clear the interface"""
        # Ask for confirmation
        response = messagebox.askyesno("Restart Application", 
            "This will close all files and reset the application to its initial state.\n\nAre you sure you want to continue?")
        
        if not response:
            return
        
        try:
            # Clear all DICOM data variables
            self.dose_data = None
            self.dose_grid_scaling = None
            self.pixel_spacing = None
            self.slice_thickness = None
            self.grid_frame_offset_vector = None
            self.number_of_frames = None
            self.rows = None
            self.columns = None
            self.dose_image_position = None
            self.dose_image_orientation = None
            
            # Clear second DICOM dose variables
            self.dose_data_2 = None
            self.dose_grid_scaling_2 = None
            self.pixel_spacing_2 = None
            self.slice_thickness_2 = None
            self.grid_frame_offset_vector_2 = None
            self.number_of_frames_2 = None
            self.rows_2 = None
            self.columns_2 = None
            self.dose_image_position_2 = None
            self.dose_image_orientation_2 = None
            
            # Clear RT Plan and isocenter variables
            self.rt_plan_data = None
            self.isocenter_position = None
            self.rt_plan_data_2 = None
            self.isocenter_position_2 = None
            
            # Clear measurement data variables
            self.measurement_data = None
            self.crossplane_measurement = None
            self.inplane_measurement = None
            self.measurement_data_2 = None
            self.crossplane_measurement_2 = None
            self.inplane_measurement_2 = None
            
            # Reset all GUI controls to default values
            self.x_var.set("0.0")
            self.y_var.set("0.0")
            self.z_var.set("0.0")
            
            # Reset normalization controls
            self.dicom_norm_var.set("")
            self.dicom_norm_var_2.set("")
            self.meas_norm_var.set("")
            self.meas_norm_var_2.set("")
            
            # Reset shift controls
            self.x_shift_var.set("0.0")
            self.z_shift_var.set("0.0")
            self.x_shift_var_2.set("0.0")
            self.z_shift_var_2.set("0.0")
            
            # Reset zoom controls
            self.zoom_enabled_var.set(False)
            self.zoom_x_center_var.set("0.0")
            self.zoom_x_range_var.set("10.0")
            self.zoom_z_center_var.set("0.0")
            self.zoom_z_range_var.set("10.0")
            
            # Reset file labels
            self.dose_file_label.config(text="No file selected")
            self.dose_file_label_2.config(text="No file selected")
            self.plan_file_label.config(text="No file selected")
            self.plan_file_label_2.config(text="No file selected")
            self.measurement_file_label.config(text="No file selected")
            self.measurement_file_label_2.config(text="No file selected")
            
            # Reset coordinate info label
            self.coord_info_label.config(text="Coordinates: Grid origin")
            
            # Clear the plot
            self.figure.clear()
            self.canvas.draw()
            
            messagebox.showinfo("Restart Complete", "Application has been reset successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during restart:\n{str(e)}")
    
    def show_restart_help(self):
        """Show help information about the restart functionality"""
        help_text = """Close All Files & Restart

This function will:
• Close all loaded DICOM dose files
• Close all loaded RT Plan files  
• Close all loaded measurement files
• Reset all position coordinates to default (0.0, 0.0, 0.0)
• Clear all normalization values
• Reset all coordinate shifts to zero
• Clear the plot display
• Reset the interface to its initial state

This is useful when you want to start fresh with a new set of files or if you encounter any issues with the current data.

You can access this function through:
• File menu → Close All Files & Restart
• Keyboard shortcut: Ctrl+R
• Button in the zoom controls area"""
        
        messagebox.showinfo("Restart Help", help_text)
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """Keyboard Shortcuts

File Operations:
• Ctrl+R: Close All Files & Restart
• Ctrl+Q: Exit application

Profile Controls:
• Enter key in position fields: Update profiles
• Enter key in normalization fields: Update profiles
• Enter key in shift fields: Update profiles

Navigation:
• Mouse wheel: Zoom in/out on plots
• Click and drag: Pan plots (when using matplotlib toolbar)"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def auto_scale(self):
        """Auto scale to fit data with some padding"""
        if hasattr(self, 'figure') and self.figure.get_axes():
            for ax in self.figure.get_axes():
                ax.relim()
                ax.autoscale()
                
                # Add 5% padding
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                x_padding = (xlim[1] - xlim[0]) * 0.05
                y_padding = (ylim[1] - ylim[0]) * 0.05
                
                ax.set_xlim(xlim[0] - x_padding, xlim[1] + x_padding)
                ax.set_ylim(ylim[0] - y_padding, ylim[1] + y_padding)
            
            self.canvas.draw()
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom"""
        if hasattr(self, 'figure') and self.figure.get_axes():
            # Determine zoom direction
            if event.delta > 0 or event.num == 4:  # Zoom in
                scale_factor = 0.9
            else:  # Zoom out
                scale_factor = 1.1
            
            # Get mouse position in data coordinates
            for ax in self.figure.get_axes():
                # Check if mouse is over this axes
                if ax.contains_point([event.x, event.y]):
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    
                    # Get mouse position in data coordinates
                    try:
                        inv = ax.transData.inverted()
                        mouse_x, mouse_y = inv.transform([event.x, event.y])
                    except:
                        # Fallback to center if transformation fails
                        mouse_x = (xlim[0] + xlim[1]) / 2
                        mouse_y = (ylim[0] + ylim[1]) / 2
                    
                    # Calculate new limits centered on mouse position
                    x_range = (xlim[1] - xlim[0]) * scale_factor / 2
                    y_range = (ylim[1] - ylim[0]) * scale_factor / 2
                    
                    ax.set_xlim(mouse_x - x_range, mouse_x + x_range)
                    ax.set_ylim(mouse_y - y_range, mouse_y + y_range)
                    
                    self.canvas.draw()
                    break
    
    def auto_dicom_norm(self):
        """Automatically set DICOM normalization to current profile maximum"""
        if self.dose_data is not None:
            try:
                # Get current positions and extract profiles
                x_mm = float(self.x_var.get()) if self.x_var.get() else 0.0
                z_mm = float(self.z_var.get()) if self.z_var.get() else 0.0
                y_mm = float(self.y_var.get()) if self.y_var.get() else 0.0
                
                # Calculate isocenter offset
                iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset()
                
                # Convert to voxel indices
                if iso_x_offset is not None:
                    x_pos = int(round((x_mm / self.pixel_spacing[1]) + iso_x_offset))
                    y_pos = int(round((y_mm / self.pixel_spacing[0]) + iso_y_offset))
                    z_idx = int(round((z_mm / self.slice_thickness) + iso_z_offset))
                else:
                    x_pos = int(round(x_mm / self.pixel_spacing[1]))
                    y_pos = int(round(y_mm / self.pixel_spacing[0]))
                    z_idx = int(round(z_mm / self.slice_thickness))
                
                # Validate indices
                x_pos = max(0, min(x_pos, self.columns - 1))
                y_pos = max(0, min(y_pos, self.rows - 1))
                z_idx = max(0, min(z_idx, self.number_of_frames - 1))
                
                # Get maximum from both profiles
                x_profile = self.dose_data[z_idx, y_pos, :]
                z_profile = self.dose_data[:, y_pos, x_pos]
                max_dose = max(np.max(x_profile), np.max(z_profile))
                
                self.dicom_norm_var.set(f"{max_dose:.3f}")
                self.update_profiles()
                
            except (ValueError, AttributeError):
                # If there's an error, use overall maximum
                max_dose = np.max(self.dose_data)
                self.dicom_norm_var.set(f"{max_dose:.3f}")
                self.update_profiles()
    
    def auto_dicom_norm_2(self):
        """Automatically set DICOM 2 normalization to current profile maximum"""
        if self.dose_data_2 is not None:
            try:
                # Get current positions and extract profiles
                x_mm = float(self.x_var.get()) if self.x_var.get() else 0.0
                z_mm = float(self.z_var.get()) if self.z_var.get() else 0.0
                y_mm = float(self.y_var.get()) if self.y_var.get() else 0.0
                
                # Calculate isocenter offset for second file
                iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset_2()
                
                # Convert to voxel indices
                if iso_x_offset is not None:
                    x_pos = int(round((x_mm / self.pixel_spacing_2[1]) + iso_x_offset))
                    y_pos = int(round((y_mm / self.pixel_spacing_2[0]) + iso_y_offset))
                    z_idx = int(round((z_mm / self.slice_thickness_2) + iso_z_offset))
                else:
                    x_pos = int(round(x_mm / self.pixel_spacing_2[1]))
                    y_pos = int(round(y_mm / self.pixel_spacing_2[0]))
                    z_idx = int(round(z_mm / self.slice_thickness_2))
                
                # Validate indices
                x_pos = max(0, min(x_pos, self.columns_2 - 1))
                y_pos = max(0, min(y_pos, self.rows_2 - 1))
                z_idx = max(0, min(z_idx, self.number_of_frames_2 - 1))
                
                # Get maximum from both profiles
                x_profile = self.dose_data_2[z_idx, y_pos, :]
                z_profile = self.dose_data_2[:, y_pos, x_pos]
                max_dose = max(np.max(x_profile), np.max(z_profile))
                
                self.dicom_norm_var_2.set(f"{max_dose:.3f}")
                self.update_profiles()
                
            except (ValueError, AttributeError):
                # If there's an error, use overall maximum
                max_dose = np.max(self.dose_data_2)
                self.dicom_norm_var_2.set(f"{max_dose:.3f}")
                self.update_profiles()
        else:
            messagebox.showwarning("Warning", "No DICOM 2 data loaded")

    def auto_meas_norm(self):
        """Automatically set measurement normalization to current measurement maximum"""
        max_val = 0.0
        
        if self.crossplane_measurement is not None:
            max_val = max(max_val, np.max(self.crossplane_measurement['values']))
            
        if self.inplane_measurement is not None:
            max_val = max(max_val, np.max(self.inplane_measurement['values']))
        
        if max_val > 0:
            self.meas_norm_var.set(f"{max_val:.3f}")
            self.update_profiles()
        else:
            messagebox.showwarning("Warning", "No measurement data loaded")
    
    def auto_meas_norm_2(self):
        """Automatically set measurement 2 normalization to current measurement maximum"""
        max_val = 0.0
        
        if self.crossplane_measurement_2 is not None:
            max_val = max(max_val, np.max(self.crossplane_measurement_2['values']))
            
        if self.inplane_measurement_2 is not None:
            max_val = max(max_val, np.max(self.inplane_measurement_2['values']))
        
        if max_val > 0:
            self.meas_norm_var_2.set(f"{max_val:.3f}")
            self.update_profiles()
        else:
            messagebox.showwarning("Warning", "No measurement 2 data loaded")

    def reset_normalizations(self):
        """Reset all normalization values to empty"""
        self.dicom_norm_var.set("")
        self.meas_norm_var.set("")
        if hasattr(self, 'dicom_norm_var_2'):
            self.dicom_norm_var_2.set("")
        if hasattr(self, 'meas_norm_var_2'):
            self.meas_norm_var_2.set("")
        self.update_profiles()
    
    def reset_shifts(self):
        """Reset all coordinate shifts to zero"""
        self.x_shift_var.set("0.0")
        self.z_shift_var.set("0.0")
        if hasattr(self, 'x_shift_var_2'):
            self.x_shift_var_2.set("0.0")
        if hasattr(self, 'z_shift_var_2'):
            self.z_shift_var_2.set("0.0")
        self.update_profiles()
    
    def auto_align_profiles(self):
        """Automatically align measurement profiles with DICOM profiles using cross-correlation"""
        if self.dose_data is None:
            messagebox.showwarning("Warning", "No DICOM data loaded")
            return
        
        try:
            # Get current positions and extract DICOM profiles
            x_mm = float(self.x_var.get()) if self.x_var.get() else 0.0
            z_mm = float(self.z_var.get()) if self.z_var.get() else 0.0
            y_mm = float(self.y_var.get()) if self.y_var.get() else 0.0
            
            # Calculate isocenter offset
            iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset()
            
            # Convert to voxel indices
            if iso_x_offset is not None:
                x_pos = int(round((x_mm / self.pixel_spacing[1]) + iso_x_offset))
                y_pos = int(round((y_mm / self.pixel_spacing[0]) + iso_y_offset))
                z_idx = int(round((z_mm / self.slice_thickness) + iso_z_offset))
            else:
                x_pos = int(round(x_mm / self.pixel_spacing[1]))
                y_pos = int(round(y_mm / self.pixel_spacing[0]))
                z_idx = int(round(z_mm / self.slice_thickness))
            
            # Validate indices
            x_pos = max(0, min(x_pos, self.columns - 1))
            y_pos = max(0, min(y_pos, self.rows - 1))
            z_idx = max(0, min(z_idx, self.number_of_frames - 1))
            
            # Extract DICOM profiles
            x_profile = self.dose_data[z_idx, y_pos, :]
            z_profile = self.dose_data[:, y_pos, x_pos]
            
            # Calculate position arrays
            if iso_x_offset is not None:
                x_positions = (np.arange(self.columns) - iso_x_offset) * self.pixel_spacing[1]
                z_positions = (np.arange(self.number_of_frames) - iso_z_offset) * self.slice_thickness
            else:
                x_positions = np.arange(self.columns) * self.pixel_spacing[1]
                z_positions = np.arange(self.number_of_frames) * self.slice_thickness
            
            shifts_calculated = []
            
            # Auto-align X profile (crossplane)
            if self.crossplane_measurement is not None:
                meas_pos = self.crossplane_measurement['positions']
                meas_val = self.crossplane_measurement['values']
                
                # Find the center of mass (centroid) of both profiles
                # For measurement profile
                meas_normalized = meas_val / np.max(meas_val)
                meas_centroid = np.sum(meas_pos * meas_normalized) / np.sum(meas_normalized)
                
                # For DICOM profile - interpolate to higher resolution first
                x_interp = np.linspace(x_positions[0], x_positions[-1], len(x_positions) * 5)
                x_profile_interp = np.interp(x_interp, x_positions, x_profile)
                dicom_normalized = x_profile_interp / np.max(x_profile_interp)
                dicom_centroid = np.sum(x_interp * dicom_normalized) / np.sum(dicom_normalized)
                
                # Calculate shift as difference between centroids
                x_shift = dicom_centroid - meas_centroid
                self.x_shift_var.set(f"{x_shift:.1f}")
                shifts_calculated.append(f"X: {x_shift:.1f} mm")
            
            # Auto-align Z profile (inplane)
            if self.inplane_measurement is not None:
                meas_pos = self.inplane_measurement['positions']
                meas_val = self.inplane_measurement['values']
                
                # Find the center of mass (centroid) of both profiles
                # For measurement profile
                meas_normalized = meas_val / np.max(meas_val)
                meas_centroid = np.sum(meas_pos * meas_normalized) / np.sum(meas_normalized)
                
                # For DICOM profile - interpolate to higher resolution first
                z_interp = np.linspace(z_positions[0], z_positions[-1], len(z_positions) * 5)
                z_profile_interp = np.interp(z_interp, z_positions, z_profile)
                dicom_normalized = z_profile_interp / np.max(z_profile_interp)
                dicom_centroid = np.sum(z_interp * dicom_normalized) / np.sum(dicom_normalized)
                
                # Calculate shift as difference between centroids
                z_shift = dicom_centroid - meas_centroid
                self.z_shift_var.set(f"{z_shift:.1f}")
                shifts_calculated.append(f"Z: {z_shift:.1f} mm")
            
            if shifts_calculated:
                messagebox.showinfo("Auto Alignment", 
                    f"Calculated shifts for Measurement 1:\n{chr(10).join(shifts_calculated)}")
                self.update_profiles()
            else:
                messagebox.showwarning("Warning", "No measurement 1 data available for alignment")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to auto-align measurement 1 profiles:\n{str(e)}")
    
    def auto_align_profiles_2(self):
        """Automatically align measurement 2 profiles with DICOM profiles using cross-correlation"""
        if self.dose_data is None:
            messagebox.showwarning("Warning", "No DICOM data loaded")
            return
        
        try:
            # Get current positions and extract DICOM profiles
            x_mm = float(self.x_var.get()) if self.x_var.get() else 0.0
            z_mm = float(self.z_var.get()) if self.z_var.get() else 0.0
            y_mm = float(self.y_var.get()) if self.y_var.get() else 0.0
            
            # Calculate isocenter offset
            iso_x_offset, iso_y_offset, iso_z_offset = self.calculate_isocenter_offset()
            
            # Convert to voxel indices
            if iso_x_offset is not None:
                x_pos = int(round((x_mm / self.pixel_spacing[1]) + iso_x_offset))
                y_pos = int(round((y_mm / self.pixel_spacing[0]) + iso_y_offset))
                z_idx = int(round((z_mm / self.slice_thickness) + iso_z_offset))
            else:
                x_pos = int(round(x_mm / self.pixel_spacing[1]))
                y_pos = int(round(y_mm / self.pixel_spacing[0]))
                z_idx = int(round(z_mm / self.slice_thickness))
            
            # Validate indices
            x_pos = max(0, min(x_pos, self.columns - 1))
            y_pos = max(0, min(y_pos, self.rows - 1))
            z_idx = max(0, min(z_idx, self.number_of_frames - 1))
            
            # Extract DICOM profiles
            x_profile = self.dose_data[z_idx, y_pos, :]
            z_profile = self.dose_data[:, y_pos, x_pos]
            
            # Calculate position arrays
            if iso_x_offset is not None:
                x_positions = (np.arange(self.columns) - iso_x_offset) * self.pixel_spacing[1]
                z_positions = (np.arange(self.number_of_frames) - iso_z_offset) * self.slice_thickness
            else:
                x_positions = np.arange(self.columns) * self.pixel_spacing[1]
                z_positions = np.arange(self.number_of_frames) * self.slice_thickness
            
            shifts_calculated = []
            
            # Auto-align X profile (crossplane) for measurement 2
            if self.crossplane_measurement_2 is not None:
                meas_pos = self.crossplane_measurement_2['positions']
                meas_val = self.crossplane_measurement_2['values']
                
                # Find the center of mass (centroid) of both profiles
                # For measurement profile
                meas_normalized = meas_val / np.max(meas_val)
                meas_centroid = np.sum(meas_pos * meas_normalized) / np.sum(meas_normalized)
                
                # For DICOM profile - interpolate to higher resolution first
                x_interp = np.linspace(x_positions[0], x_positions[-1], len(x_positions) * 5)
                x_profile_interp = np.interp(x_interp, x_positions, x_profile)
                dicom_normalized = x_profile_interp / np.max(x_profile_interp)
                dicom_centroid = np.sum(x_interp * dicom_normalized) / np.sum(dicom_normalized)
                
                # Calculate shift as difference between centroids
                x_shift = dicom_centroid - meas_centroid
                self.x_shift_var_2.set(f"{x_shift:.1f}")
                shifts_calculated.append(f"X: {x_shift:.1f} mm")
            
            # Auto-align Z profile (inplane) for measurement 2
            if self.inplane_measurement_2 is not None:
                meas_pos = self.inplane_measurement_2['positions']
                meas_val = self.inplane_measurement_2['values']
                
                # Find the center of mass (centroid) of both profiles
                # For measurement profile
                meas_normalized = meas_val / np.max(meas_val)
                meas_centroid = np.sum(meas_pos * meas_normalized) / np.sum(meas_normalized)
                
                # For DICOM profile - interpolate to higher resolution first
                z_interp = np.linspace(z_positions[0], z_positions[-1], len(z_positions) * 5)
                z_profile_interp = np.interp(z_interp, z_positions, z_profile)
                dicom_normalized = z_profile_interp / np.max(z_profile_interp)
                dicom_centroid = np.sum(z_interp * dicom_normalized) / np.sum(dicom_normalized)
                
                # Calculate shift as difference between centroids
                z_shift = dicom_centroid - meas_centroid
                self.z_shift_var_2.set(f"{z_shift:.1f}")
                shifts_calculated.append(f"Z: {z_shift:.1f} mm")
            
            if shifts_calculated:
                messagebox.showinfo("Auto Alignment", 
                    f"Calculated shifts for Measurement 2:\n{chr(10).join(shifts_calculated)}")
                self.update_profiles()
            else:
                messagebox.showwarning("Warning", "No measurement 2 data available for alignment")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to auto-align measurement 2 profiles:\n{str(e)}")

def main():
    root = tk.Tk()
    app = DICOMDoseProfileViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()