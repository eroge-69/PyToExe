import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math


class SnellsLawGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snell's Law Calculator - מגישים יהב קליינמן,יהב בלומנפלד ונועם כהן ")
        self.root.geometry("1900x1700")
        self.root.configure(bg='#f0f0f0')

        # Set minimum window size
        self.root.minsize(1200, 700)

        # Configure modern styling
        self.setup_styles()

        # Material list to store (name, refractive_index) tuples
        self.materials = []

        # Common materials dictionary with enhanced organization and original choices
        self.common_materials = {
            # Basic Materials (Original)
            'Air': 1.000,
            'Water': 1.333,
            'Glass (typical)': 1.5,
            'Diamond': 2.42,
            'Ice': 1.31,
            'Quartz': 1.54,
            'Plastic (acrylic)': 1.49,
            'Oil (typical)': 1.5,
            'Crown Glass': 1.52,
            'Flint Glass': 1.6,
            'Sapphire': 1.77,
            'Silicon': 3.4,

            # Professional Materials (Enhanced)
            'Air (Standard 20°C)': 1.000293,
            'Vacuum': 1.000000,
            'Water (20°C)': 1.333,
            'Water (0°C)': 1.333,
            'Crown Glass (BK7)': 1.5168,
            'Flint Glass (SF10)': 1.728,
            'Fused Silica': 1.458,
            'Quartz Crystal': 1.544,
            'Acrylic (PMMA)': 1.491,
            'Polycarbonate': 1.586,
            'Germanium': 4.00,
            'Glycerol': 1.473,
            'Ethanol': 1.361,
            'Benzene': 1.501,

            # Additional Useful Materials
            'Pyrex Glass': 1.474,
            'Window Glass': 1.52,
            'Optical Glass': 1.61,
            'Zinc Crown Glass': 1.517,
            'Dense Flint Glass': 1.66,
            'Lanthanum Glass': 1.90,
            'Titanium Dioxide': 2.61,
            'Zinc Sulfide': 2.37,
            'Calcium Fluoride': 1.43,
            'Magnesium Fluoride': 1.38,
            'Sodium Chloride': 1.54,
            'Potassium Bromide': 1.56,
            'Cesium Iodide': 1.79,
            'Aluminum Oxide': 1.76
        }

        # Organize materials by categories for better UI - keeping only basic materials
        self.material_categories = {
            'Basic Materials': [
                ('Air', 1.000),
                ('Water', 1.333),
                ('Glass (typical)', 1.5),
                ('Diamond', 2.42),
                ('Ice', 1.31),
                ('Quartz', 1.54),
                ('Plastic (acrylic)', 1.49),
                ('Oil (typical)', 1.5),
                ('Crown Glass', 1.52),
                ('Flint Glass', 1.6),
                ('Sapphire', 1.77),
                ('Silicon', 3.4)
            ]
        }

        # Basic materials list for direct dropdown (no categories)
        self.basic_materials = [
            ('Air', 1.000),
            ('Water', 1.333),
            ('Glass (typical)', 1.5),
            ('Diamond', 2.42),
            ('Ice', 1.31),
            ('Quartz', 1.54),
            ('Plastic (acrylic)', 1.49),
            ('Oil (typical)', 1.5),
            ('Crown Glass', 1.52),
            ('Flint Glass', 1.6),
            ('Sapphire', 1.77),
            ('Silicon', 3.4)
        ]

        self.setup_ui()

        # Add window icon simulation with colored title
        self.setup_header()

    def setup_styles(self):
        """Configure professional styling"""
        style = ttk.Style()

        # Configure modern theme
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Define more subtle but still colorful scheme
        self.colors = {
            'primary': '#4F46E5',  # Softer Indigo
            'secondary': '#DB2777',  # Softer Pink
            'success': '#059669',  # Softer Emerald
            'warning': '#D97706',  # Softer Amber
            'error': '#DC2626',  # Softer Red
            'info': '#2563EB',  # Softer Blue
            'background': '#F8FAFC',  # Very Light Blue-Gray
            'surface': '#FFFFFF',  # White
            'surface_light': '#F1F5F9',  # Light Gray-Blue
            'text': '#1E293B',  # Dark Blue-Gray
            'text_light': '#64748B',  # Medium Gray
            'border': '#CBD5E1',  # Light Border
            'accent1': '#7C3AED',  # Softer Purple
            'accent2': '#0891B2',  # Softer Cyan
            'accent3': '#65A30D',  # Softer Lime
            'accent4': '#EA580C',  # Softer Orange
            'accent5': '#DC2626',  # Softer Red
            'accent6': '#92400E'  # Softer Brown
        }

        # Softer gradient colors for materials
        self.material_gradient_colors = [
            '#EEF2FF',  # Very Light Indigo
            '#FDF2F8',  # Very Light Pink
            '#ECFDF5',  # Very Light Emerald
            '#FFFBEB',  # Very Light Amber
            '#FEF2F2',  # Very Light Red
            '#EFF6FF',  # Very Light Blue
            '#F5F3FF',  # Very Light Purple
            '#F0FDFA',  # Very Light Teal
            '#F7FEE7',  # Very Light Lime
            '#FFF7ED'  # Very Light Orange
        ]

        # Configure custom styles with vibrant colors
        style.configure('Title.TLabel',
                        font=('Segoe UI', 20, 'bold'),
                        foreground=self.colors['primary'],
                        background=self.colors['background'])

        style.configure('Subtitle.TLabel',
                        font=('Segoe UI', 12),
                        foreground=self.colors['text'],
                        background=self.colors['background'])

        style.configure('Header.TLabel',
                        font=('Segoe UI', 14, 'bold'),
                        foreground=self.colors['text'],
                        background=self.colors['surface'])

        style.configure('Professional.TFrame',
                        background=self.colors['surface'],
                        relief='flat',
                        borderwidth=1)

        style.configure('Card.TLabelframe',
                        background=self.colors['surface'],
                        relief='solid',
                        borderwidth=2,
                        bordercolor=self.colors['accent2'],
                        labelmargins=[15, 8, 15, 8])

        style.configure('Card.TLabelframe.Label',
                        font=('Segoe UI', 12, 'bold'),
                        foreground=self.colors['primary'],
                        background=self.colors['surface'])

        style.configure('Primary.TButton',
                        font=('Segoe UI', 12, 'bold'),
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none')

        style.map('Primary.TButton',
                  background=[('active', self.colors['accent1']), ('!active', self.colors['primary'])],
                  relief=[('pressed', 'flat'), ('!pressed', 'raised')])

        style.configure('Secondary.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0,
                        focuscolor='none')

        style.map('Secondary.TButton',
                  background=[('active', self.colors['accent2']), ('!active', self.colors['info'])],
                  foreground=[('active', 'white'), ('!active', 'white')])

        style.configure('Success.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0,
                        focuscolor='none')

        style.map('Success.TButton',
                  background=[('active', '#059669'), ('!active', self.colors['success'])],
                  foreground=[('active', 'white'), ('!active', 'white')])

        style.configure('Warning.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0,
                        focuscolor='none')

        style.map('Warning.TButton',
                  background=[('active', '#D97706'), ('!active', self.colors['warning'])],
                  foreground=[('active', 'white'), ('!active', 'white')])

        style.configure('Professional.TEntry',
                        font=('Segoe UI', 10),
                        fieldbackground='white',
                        borderwidth=2,
                        relief='solid')

        style.map('Professional.TEntry',
                  bordercolor=[('focus', self.colors['accent2']), ('!focus', self.colors['border'])])

        style.configure('Professional.TCombobox',
                        font=('Segoe UI', 10),
                        borderwidth=2,
                        relief='solid')

        style.map('Professional.TCombobox',
                  bordercolor=[('focus', self.colors['accent2']), ('!focus', self.colors['border'])])

        # Configure separator with color
        style.configure('Colorful.TSeparator',
                        background=self.colors['accent2'])

    def setup_header(self):
        """Create softer colorful professional header"""
        # Create header with softer gradient-like effect
        header_main = tk.Frame(self.root, bg=self.colors['primary'], height=100)
        header_main.grid(row=0, column=0, sticky='ew')
        header_main.grid_propagate(False)

        # Add subtle accent stripe
        accent_stripe = tk.Frame(header_main, bg=self.colors['accent2'], height=3)
        accent_stripe.pack(fill='x', side='bottom')

        # Header content
        header_content = tk.Frame(header_main, bg=self.colors['primary'])
        header_content.pack(expand=True, fill='both', padx=20, pady=15)

        # Left side - Title and subtitle with softer colors
        left_content = tk.Frame(header_content, bg=self.colors['primary'])
        left_content.pack(side='left', anchor='w')

        # Application title with softer emoji
        title_label = tk.Label(left_content,
                               text="🔬 Snell's Law Calculator",
                               font=('Segoe UI', 24, 'bold'),
                               fg='white',
                               bg=self.colors['primary'])
        title_label.pack(anchor='w')

        # Softer subtitle
        subtitle_label = tk.Label(left_content,
                                  text="Optical Analysis Tool",
                                  font=('Segoe UI', 12, 'bold'),
                                  fg='#E0E7FF',
                                  bg=self.colors['primary'])
        subtitle_label.pack(anchor='w')

        # Project credits with softer color
        credits_label = tk.Label(left_content,
                                 text="👥 Project by: Noam Cohen, Yahav .K. & Yahav .B.",
                                 font=('Segoe UI', 10, 'italic'),
                                 fg='#C7D2FE',
                                 bg=self.colors['primary'])
        credits_label.pack(anchor='w', pady=(2, 0))

        # Right side - Version and info with softer styling
        right_content = tk.Frame(header_content, bg=self.colors['primary'])
        right_content.pack(side='right', anchor='e')

        # Softer version badge
        version_frame = tk.Frame(right_content, bg=self.colors['accent1'], relief='raised', bd=1)
        version_frame.pack(anchor='e', pady=(0, 5))

        version_label = tk.Label(version_frame,
                                 text="Explanations",
                                 font=('Segoe UI', 11, 'bold'),
                                 fg='white',
                                 bg=self.colors['accent1'],
                                 padx=12, pady=4)
        version_label.pack()

        # Button container for about and explanation buttons
        button_container = tk.Frame(right_content, bg=self.colors['primary'])
        button_container.pack(anchor='e')

        # Explanation button
        explanation_btn = tk.Button(button_container,
                                    text="Snell's law explanation",
                                    font=('Segoe UI', 10, 'bold'),
                                    fg='white',
                                    bg=self.colors['accent4'],
                                    activebackground=self.colors['warning'],
                                    activeforeground='white',
                                    relief='raised',
                                    bd=1,
                                    padx=15,
                                    pady=6,
                                    command=self.show_explanation,
                                    cursor='hand2')
        explanation_btn.pack(side='left', padx=(0, 5))

        # About button
        about_btn = tk.Button(button_container,
                              text="💡 About",
                              font=('Segoe UI', 10, 'bold'),
                              fg='white',
                              bg=self.colors['accent3'],
                              activebackground=self.colors['success'],
                              activeforeground='white',
                              relief='raised',
                              bd=1,
                              padx=15,
                              pady=6,
                              command=self.show_about,
                              cursor='hand2')
        about_btn.pack(side='left')

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        main_container.columnconfigure(0, weight=2)
        main_container.columnconfigure(1, weight=3)
        main_container.rowconfigure(0, weight=1)

        # Left panel - Controls
        self.setup_control_panel(main_container)

        # Right panel - Visualization
        self.setup_visualization_panel(main_container)

    def setup_control_panel(self, parent):
        """Create the control panel with professional styling"""
        control_panel = tk.Frame(parent, bg=self.colors['background'])
        control_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        control_panel.columnconfigure(0, weight=1)

        # Input Parameters Card with colorful styling
        params_frame = ttk.LabelFrame(control_panel, text="🎯 Input Parameters", style='Card.TLabelframe', padding=20)
        params_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        params_frame.columnconfigure(1, weight=1)

        # Colorful parameter input
        angle_label = ttk.Label(params_frame, text="🔥 Incident Angle:", font=('Segoe UI', 11, 'bold'))
        angle_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        angle_input_frame = tk.Frame(params_frame, bg=self.colors['surface'])
        angle_input_frame.grid(row=0, column=1, sticky='ew', pady=(0, 10))

        self.angle_var = tk.StringVar(value="30.0")
        angle_entry = ttk.Entry(angle_input_frame, textvariable=self.angle_var,
                                width=15, style='Professional.TEntry', font=('Segoe UI', 11, 'bold'))
        angle_entry.pack(side='left', padx=(0, 8))

        degree_label = tk.Label(angle_input_frame, text="📐 degrees",
                                font=('Segoe UI', 10, 'bold'),
                                fg=self.colors['accent1'], bg=self.colors['surface'])
        degree_label.pack(side='left')

        # Materials Management Card with softer colors
        materials_frame = ttk.LabelFrame(control_panel, text="🔬 Materials Library & Selection",
                                         style='Card.TLabelframe', padding=20)
        materials_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        materials_frame.columnconfigure(1, weight=1)
        control_panel.rowconfigure(1, weight=1)

        # Softer material library browser - simplified without categories
        library_label = tk.Label(materials_frame, text="📚 Material Library Browser:",
                                 font=('Segoe UI', 11, 'bold'),
                                 fg=self.colors['accent1'], bg=self.colors['surface'])
        library_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))

        # Material selection with softer styling - direct selection without categories
        material_frame = tk.Frame(materials_frame, bg=self.colors['accent3'], relief='solid', bd=1, padx=12, pady=6)
        material_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        material_label = tk.Label(material_frame, text="🔬 Material:",
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='white', bg=self.colors['accent3'])
        material_label.pack(side='left', padx=(0, 10))

        self.common_material_var = tk.StringVar()
        self.material_combo = ttk.Combobox(material_frame, textvariable=self.common_material_var,
                                           state="readonly", style='Professional.TCombobox',
                                           width=25, font=('Segoe UI', 10, 'bold'))
        self.material_combo.pack(side='left', padx=(0, 10))
        self.material_combo.bind('<<ComboboxSelected>>', self.on_common_material_selected)

        # Softer quick add button
        quick_add_btn = ttk.Button(material_frame, text="⚡ Quick Add",
                                   command=self.quick_add_material, style='Success.TButton')
        quick_add_btn.pack(side='left', padx=(10, 0))

        # Initialize material list
        self.update_material_list()

        # Custom material input section with softer styling
        custom_header = tk.Frame(materials_frame, bg=self.colors['warning'], relief='solid', bd=1, padx=15, pady=6)
        custom_header.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        custom_label = tk.Label(custom_header, text="🔧 Custom Material Designer:",
                                font=('Segoe UI', 11, 'bold'),
                                fg='white', bg=self.colors['warning'])
        custom_label.pack()

        # Enhanced input fields with softer layout
        input_frame = tk.Frame(materials_frame, bg=self.colors['surface_light'], relief='solid', bd=1, padx=15, pady=12)
        input_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # Softer material name input
        name_label = tk.Label(input_frame, text="🏷️ Name:",
                              font=('Segoe UI', 10, 'bold'),
                              fg=self.colors['accent1'], bg=self.colors['surface_light'])
        name_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=(0, 8))

        self.material_name_var = tk.StringVar()
        name_entry = ttk.Entry(input_frame, textvariable=self.material_name_var,
                               style='Professional.TEntry', font=('Segoe UI', 10, 'bold'))
        name_entry.grid(row=0, column=1, sticky='ew', padx=(0, 20), pady=(0, 8))

        # Softer refractive index input
        index_label = tk.Label(input_frame, text="🔢 n =",
                               font=('Segoe UI', 10, 'bold'),
                               fg=self.colors['accent4'], bg=self.colors['surface_light'])
        index_label.grid(row=0, column=2, sticky='w', padx=(0, 10), pady=(0, 8))

        self.refractive_index_var = tk.StringVar()
        index_entry = ttk.Entry(input_frame, textvariable=self.refractive_index_var,
                                style='Professional.TEntry', font=('Segoe UI', 10, 'bold'), width=15)
        index_entry.grid(row=0, column=3, sticky='ew', pady=(0, 8))

        # NEW: Buttons and Material Stack Showcase - side by side layout
        buttons_showcase_section = tk.Frame(materials_frame, bg=self.colors['surface'])
        buttons_showcase_section.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        buttons_showcase_section.columnconfigure(0, weight=1)
        buttons_showcase_section.columnconfigure(1, weight=2)  # Give more space to showcase

        # Left side - Action buttons in 2x2 grid
        self.setup_action_buttons(buttons_showcase_section, column=0)

        # Right side - Material Stack Showcase
        self.setup_material_showcase(buttons_showcase_section, column=1)

        # Below - Traditional Listbox (full width)
        self.setup_materials_listbox(materials_frame, row=6)

        # Analysis Data section with detailed numerical display
        analysis_frame = ttk.LabelFrame(control_panel, text="📈 Analysis Data", style='Card.TLabelframe', padding=15)
        analysis_frame.grid(row=2, column=0, sticky='ew', pady=(15, 15))
        analysis_frame.columnconfigure(0, weight=1)

        # Create notebook for tabbed data display
        self.data_notebook = ttk.Notebook(analysis_frame)
        self.data_notebook.grid(row=0, column=0, sticky='ew', pady=(5, 0))

        # Summary tab
        summary_frame = tk.Frame(self.data_notebook, bg='white', padx=10, pady=8)
        self.data_notebook.add(summary_frame, text="📊 Summary")

        self.summary_text = tk.Text(summary_frame, height=6, width=50,
                                    font=('Segoe UI', 9),
                                    bg='#F8FAFC',
                                    fg=self.colors['text'],
                                    relief='flat',
                                    borderwidth=1,
                                    wrap='word')
        self.summary_text.pack(fill='both', expand=True)

        # Angles tab
        angles_frame = tk.Frame(self.data_notebook, bg='white', padx=10, pady=8)
        self.data_notebook.add(angles_frame, text="📐 Angles")

        self.angles_text = tk.Text(angles_frame, height=6, width=50,
                                   font=('Consolas', 9),
                                   bg='#F8FAFC',
                                   fg=self.colors['text'],
                                   relief='flat',
                                   borderwidth=1,
                                   wrap='word')
        self.angles_text.pack(fill='both', expand=True)

        # Materials tab
        materials_data_frame = tk.Frame(self.data_notebook, bg='white', padx=10, pady=8)
        self.data_notebook.add(materials_data_frame, text="🔬 Materials")

        self.materials_data_text = tk.Text(materials_data_frame, height=6, width=50,
                                           font=('Consolas', 9),
                                           bg='#F8FAFC',
                                           fg=self.colors['text'],
                                           relief='flat',
                                           borderwidth=1,
                                           wrap='word')
        self.materials_data_text.pack(fill='both', expand=True)

        # Initialize with empty data
        self.update_analysis_data()

        # Results section with softer styling
        results_frame = ttk.LabelFrame(control_panel, text="📄 Detailed Report", style='Card.TLabelframe', padding=15)
        results_frame.grid(row=3, column=0, sticky='nsew')
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        control_panel.rowconfigure(3, weight=1)

        # Softer results text area
        results_container = tk.Frame(results_frame, bg=self.colors['accent1'], relief='solid', bd=2, padx=2, pady=2)
        results_container.grid(row=0, column=0, sticky='nsew')
        results_container.columnconfigure(0, weight=1)
        results_container.rowconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_container,
                                                      wrap='word',
                                                      height=10,
                                                      font=('Consolas', 9, 'bold'),
                                                      bg='#FAFBFC',
                                                      fg=self.colors['text'],
                                                      insertbackground=self.colors['primary'],
                                                      relief='flat',
                                                      borderwidth=0)
        self.results_text.grid(row=0, column=0, sticky='nsew')

    def setup_action_buttons(self, parent, column=0):
        """Create the action buttons in a 2x2 grid on the left side"""

        # Left side container for buttons
        button_container = tk.Frame(parent, bg=self.colors['surface'])
        button_container.grid(row=0, column=column, sticky='nsew', padx=(0, 10))
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1)

        # Button header
        button_header = tk.Frame(button_container, bg=self.colors['primary'], relief='solid', bd=1, padx=15, pady=4)
        button_header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))

        button_label = tk.Label(button_header, text="⚡ Actions",
                                font=('Segoe UI', 10, 'bold'),
                                fg='white', bg=self.colors['primary'])
        button_label.pack()

        # 2x2 Button Grid
        add_btn = ttk.Button(button_container, text="🎨 Add Custom",
                             command=self.add_material, style='Primary.TButton')
        add_btn.grid(row=1, column=0, padx=(0, 3), pady=(0, 3), sticky='ew', ipady=8)

        # Calculate button
        calculate_btn = tk.Button(button_container,
                                  text="🚀 Calculate",
                                  command=self.calculate,
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='white',
                                  bg=self.colors['success'],
                                  activebackground=self.colors['accent3'],
                                  activeforeground='white',
                                  relief='raised',
                                  bd=2,
                                  pady=8,
                                  cursor='hand2')
        calculate_btn.grid(row=1, column=1, padx=(3, 0), pady=(0, 3), sticky='ew')

        remove_btn = ttk.Button(button_container, text="🗑️ Remove",
                                command=self.remove_material, style='Warning.TButton')
        remove_btn.grid(row=2, column=0, padx=(0, 3), pady=(3, 0), sticky='ew', ipady=8)

        clear_btn = ttk.Button(button_container, text="🔄 Clear All",
                               command=self.clear_materials, style='Secondary.TButton')
        clear_btn.grid(row=2, column=1, padx=(3, 0), pady=(3, 0), sticky='ew', ipady=8)

    def setup_material_showcase(self, parent, column=1):
        """Create an enhanced visual showcase for the material stack in vertical column layout"""

        # Right side container for showcase
        showcase_container = tk.Frame(parent, bg=self.colors['surface'])
        showcase_container.grid(row=0, column=column, sticky='nsew', padx=(10, 0))
        showcase_container.columnconfigure(0, weight=1)

        # Showcase header
        showcase_header = tk.Frame(showcase_container, bg=self.colors['accent5'], relief='solid', bd=1, padx=15, pady=4)
        showcase_header.grid(row=0, column=0, sticky='ew', pady=(0, 5))

        showcase_label = tk.Label(showcase_header, text="🎭 Material Stack Showcase",
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='white', bg=self.colors['accent5'])
        showcase_label.pack()

        # Showcase frame with enhanced styling
        showcase_main = tk.Frame(showcase_container, bg=self.colors['surface'], relief='solid', bd=2, padx=3, pady=3)
        showcase_main.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        showcase_main.columnconfigure(0, weight=1)

        # Create canvas for showcase - smaller height for vertical layout
        self.showcase_canvas = tk.Canvas(showcase_main, height=140, bg='#FAFBFF',
                                         highlightthickness=0, relief='flat')
        self.showcase_canvas.grid(row=0, column=0, sticky='ew', padx=2, pady=2)

        # Vertical scrollbar for showcase
        showcase_scrollbar = ttk.Scrollbar(showcase_main, orient='vertical',
                                           command=self.showcase_canvas.yview)
        showcase_scrollbar.grid(row=0, column=1, sticky='ns')
        self.showcase_canvas.configure(yscrollcommand=showcase_scrollbar.set)

        # Info label with light path direction
        info_label = tk.Label(showcase_container, text="🌊 Light travels top→bottom | Stack arranged vertically",
                              font=('Segoe UI', 8, 'italic'),
                              fg=self.colors['accent2'], bg=self.colors['surface'])
        info_label.grid(row=2, column=0, sticky='w', pady=(0, 0))

        # Initialize showcase
        self.update_material_showcase()

    def update_material_showcase(self):
        """Update the visual material showcase in vertical column layout"""
        # Clear canvas
        self.showcase_canvas.delete("all")

        if not self.materials:
            # Show empty state
            self.showcase_canvas.create_text(100, 70,
                                             text="🌟 Add materials to see\nthe stack showcase!",
                                             font=('Segoe UI', 11, 'bold'),
                                             fill=self.colors['text_light'],
                                             justify='center')
            return

        # Calculate dimensions for vertical layout
        canvas_width = 200  # Fixed width for vertical layout
        layer_width = 160  # Layer width
        layer_height = 40  # Increased height for better visibility
        spacing = 8  # Vertical spacing between layers
        start_x = 20  # Left margin
        start_y = 15  # Top margin

        # Material type colors and icons
        material_type_info = {
            'Air': {'color': '#E3F2FD', 'icon': '💨', 'border': '#2196F3'},
            'Gas': {'color': '#E8F5E8', 'icon': '🌪️', 'border': '#4CAF50'},
            'Liquid': {'color': '#E1F5FE', 'icon': '💧', 'border': '#00BCD4'},
            'Glass': {'color': '#FFF3E0', 'icon': '🪟', 'border': '#FF9800'},
            'Crystal': {'color': '#F3E5F5', 'icon': '💎', 'border': '#9C27B0'},
            'Semiconductor': {'color': '#FFEBEE', 'icon': '⚡', 'border': '#F44336'},
            'Polymer': {'color': '#F1F8E9', 'icon': '🧪', 'border': '#8BC34A'},
            'Default': {'color': '#F5F5F5', 'icon': '🔬', 'border': '#9E9E9E'}
        }

        # Start with Air layer at the top
        air_info = material_type_info['Air']
        current_y = start_y

        # Air layer (top)
        self.showcase_canvas.create_rectangle(start_x, current_y, start_x + layer_width, current_y + layer_height,
                                              fill=air_info['color'], outline=air_info['border'], width=2)
        self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 12,
                                         text=f"{air_info['icon']} Air",
                                         font=('Segoe UI', 9, 'bold'),
                                         fill=self.colors['text'])
        self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 26,
                                         text="n = 1.000",
                                         font=('Segoe UI', 8, 'bold'),
                                         fill=self.colors['text_light'])

        current_y += layer_height + spacing

        # Draw materials in vertical column
        for i, (name, n) in enumerate(self.materials):
            # Determine material type
            mat_type = self.get_material_type(n)
            mat_info = material_type_info.get(mat_type, material_type_info['Default'])

            # Create material layer with gradient effect
            self.showcase_canvas.create_rectangle(start_x, current_y, start_x + layer_width, current_y + layer_height,
                                                  fill=mat_info['color'], outline=mat_info['border'], width=3)

            # Add subtle inner border for depth
            self.showcase_canvas.create_rectangle(start_x + 2, current_y + 2,
                                                  start_x + layer_width - 2, current_y + layer_height - 2,
                                                  fill='', outline='white', width=1)

            # Material name (truncated if needed)
            display_name = name[:12] + "..." if len(name) > 12 else name
            self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 10,
                                             text=f"{mat_info['icon']} {display_name}",
                                             font=('Segoe UI', 9, 'bold'),
                                             fill=self.colors['text'])

            # Refractive index
            self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 22,
                                             text=f"n = {n:.3f}",
                                             font=('Segoe UI', 8, 'bold'),
                                             fill=self.colors['text_light'])

            # Material type
            self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 32,
                                             text=mat_type,
                                             font=('Segoe UI', 7),
                                             fill=self.colors['accent1'])

            # Draw light path arrow pointing down
            if i < len(self.materials) - 1 or True:  # Always show arrow for light direction
                arrow_x = start_x + layer_width + 10
                arrow_y = current_y + layer_height // 2
                arrow_end_y = current_y + layer_height + spacing // 2

                # Create downward arrow
                self.showcase_canvas.create_line(arrow_x, arrow_y, arrow_x, arrow_end_y,
                                                 fill=self.colors['warning'], width=3,
                                                 arrow=tk.LAST, arrowshape=(6, 8, 3))

                # Add interface label
                interface_x = arrow_x + 15
                interface_y = arrow_y + (arrow_end_y - arrow_y) // 2
                self.showcase_canvas.create_text(interface_x, interface_y,
                                                 text=f"I{i + 1}",
                                                 font=('Segoe UI', 7, 'bold'),
                                                 fill=self.colors['accent4'])

            current_y += layer_height + spacing

        # Add final Air layer at the bottom
        self.showcase_canvas.create_rectangle(start_x, current_y, start_x + layer_width, current_y + layer_height,
                                              fill=air_info['color'], outline=air_info['border'], width=2)
        self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 12,
                                         text=f"{air_info['icon']} Air",
                                         font=('Segoe UI', 9, 'bold'),
                                         fill=self.colors['text'])
        self.showcase_canvas.create_text(start_x + layer_width // 2, current_y + 26,
                                         text="n = 1.000",
                                         font=('Segoe UI', 8, 'bold'),
                                         fill=self.colors['text_light'])

        # Add title and statistics at the top
        title_text = f"📊 Stack: {len(self.materials)} layers"
        self.showcase_canvas.create_text(start_x, 5,
                                         text=title_text,
                                         font=('Segoe UI', 8, 'bold'),
                                         fill=self.colors['primary'], anchor='w')

        # Add statistics at the bottom
        if self.materials:
            n_values = [n for _, n in self.materials]
            stats_y = current_y + layer_height + 15
            stats_text = f"Range: {min(n_values):.2f}-{max(n_values):.2f}"
            self.showcase_canvas.create_text(start_x, stats_y,
                                             text=stats_text,
                                             font=('Segoe UI', 7),
                                             fill=self.colors['text_light'], anchor='w')

            avg_text = f"Average: {sum(n_values) / len(n_values):.2f}"
            self.showcase_canvas.create_text(start_x, stats_y + 12,
                                             text=avg_text,
                                             font=('Segoe UI', 7),
                                             fill=self.colors['text_light'], anchor='w')

        # Update scroll region for vertical scrolling
        total_height = current_y + layer_height + 30
        self.showcase_canvas.configure(scrollregion=(0, 0, canvas_width, total_height))

    def get_material_type(self, n):
        """Determine material type based on refractive index"""
        if n < 1.1:
            return "Gas"
        elif n < 1.4:
            return "Liquid"
        elif n < 2.0:
            return "Glass"
        elif n < 3.0:
            return "Crystal"
        elif n >= 3.0:
            return "Semiconductor"
        else:
            return "Default"

    def setup_materials_listbox(self, parent, row=7):
        """Create the materials listbox below the buttons and showcase"""

        # Full width container for listbox
        listbox_container = tk.Frame(parent, bg=self.colors['surface'])
        listbox_container.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(10, 10))
        listbox_container.columnconfigure(0, weight=1)

        # Listbox header
        listbox_header = tk.Frame(listbox_container, bg=self.colors['accent2'], relief='solid', bd=1, padx=15, pady=4)
        listbox_header.grid(row=0, column=0, sticky='ew', pady=(0, 3))

        listbox_label = tk.Label(listbox_header, text="📋 Material Stack List - Click to Select for Removal",
                                 font=('Segoe UI', 10, 'bold'),
                                 fg='white', bg=self.colors['accent2'])
        listbox_label.pack()

        # Traditional listbox for compact view
        list_frame = tk.Frame(listbox_container, bg=self.colors['accent2'], relief='solid', bd=2, padx=2, pady=2)
        list_frame.grid(row=1, column=0, sticky='ew', pady=(0, 0))
        list_frame.columnconfigure(0, weight=1)

        self.materials_listbox = tk.Listbox(list_frame, height=4,
                                            font=('Segoe UI', 9, 'bold'),
                                            bg='#F8FAFC',
                                            fg=self.colors['text'],
                                            selectbackground=self.colors['accent1'],
                                            selectforeground='white',
                                            relief='flat',
                                            borderwidth=0,
                                            activestyle='none')
        self.materials_listbox.grid(row=0, column=0, sticky='ew', padx=1, pady=1)

        # Horizontal scrollbar for listbox
        listbox_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.materials_listbox.xview)
        listbox_scrollbar.grid(row=1, column=0, sticky='ew')
        self.materials_listbox.configure(xscrollcommand=listbox_scrollbar.set)

    def update_analysis_data(self, path_data=None, initial_angle=None):
        """Update the analysis data display with current calculation results"""

        # Check if the UI elements exist yet
        if not hasattr(self, 'summary_text'):
            return

        # Clear all data displays
        self.summary_text.config(state='normal')
        self.angles_text.config(state='normal')
        self.materials_data_text.config(state='normal')

        self.summary_text.delete(1.0, tk.END)
        self.angles_text.delete(1.0, tk.END)
        self.materials_data_text.delete(1.0, tk.END)

        if path_data is None or initial_angle is None:
            # Show empty state
            self.summary_text.insert(tk.END, "📊 ANALYSIS SUMMARY\n\n")
            self.summary_text.insert(tk.END, "No calculation performed yet.\n")
            self.summary_text.insert(tk.END,
                                     "Configure materials and click 'Calculate Light Path' to see analysis data.")

            self.angles_text.insert(tk.END, "📐 ANGLE DATA\n\n")
            self.angles_text.insert(tk.END, "Waiting for calculation...")

            self.materials_data_text.insert(tk.END, "🔬 MATERIAL PROPERTIES\n\n")
            if self.materials:
                self.materials_data_text.insert(tk.END, f"Materials configured: {len(self.materials)}\n\n")
                for i, (name, n) in enumerate(self.materials):
                    self.materials_data_text.insert(tk.END, f"Layer {i + 1}: {name}\n")
                    self.materials_data_text.insert(tk.END, f"  n = {n:.6f}\n\n")
            else:
                self.materials_data_text.insert(tk.END, "No materials configured.")

            # Make text widgets read-only
            self.summary_text.config(state='disabled')
            self.angles_text.config(state='disabled')
            self.materials_data_text.config(state='disabled')
            return

        # Summary Data
        summary_data = []
        summary_data.append("📊 CALCULATION SUMMARY")
        summary_data.append("=" * 30)
        summary_data.append(f"Initial Angle: {initial_angle:.3f}°")
        summary_data.append(f"Number of Materials: {len(self.materials)}")

        if path_data['success']:
            if 'exit_angle' in path_data:
                exit_angle = path_data['exit_angle']
                summary_data.append(f"Final Exit Angle: {exit_angle:.3f}°")

                total_deviation = abs(exit_angle - initial_angle)
                summary_data.append(f"Total Deviation: {total_deviation:.3f}°")

                if total_deviation < 1.0:
                    summary_data.append("Deviation Level: Minimal")
                elif total_deviation < 5.0:
                    summary_data.append("Deviation Level: Low")
                elif total_deviation < 15.0:
                    summary_data.append("Deviation Level: Moderate")
                else:
                    summary_data.append("Deviation Level: High")

                summary_data.append(f"Status: ✅ Success")
        else:
            summary_data.append("Status: ❌ Total Internal Reflection")
            if 'tir_interface' in path_data:
                tir_interface = path_data['tir_interface']
                summary_data.append(f"TIR at Interface: {tir_interface}")

        # Calculate path statistics
        if len(path_data['x_coords']) > 1:
            x_coords = path_data['x_coords']
            y_coords = path_data['y_coords']

            # Calculate total path length
            total_length = 0
            for i in range(len(x_coords) - 1):
                dx = x_coords[i + 1] - x_coords[i]
                dy = y_coords[i + 1] - y_coords[i]
                total_length += math.sqrt(dx * dx + dy * dy)

            summary_data.append(f"Total Path Length: {total_length:.4f} units")
            summary_data.append(f"Horizontal Displacement: {abs(x_coords[-1] - x_coords[0]):.4f} units")

        self.summary_text.insert(tk.END, "\n".join(summary_data))

        # Angles Data
        angles_data = []
        angles_data.append("📐 ANGLE PROGRESSION")
        angles_data.append("=" * 25)
        angles_data.append(f"{'Interface':<12} {'Incident':<10} {'Refracted':<10} {'Deviation':<10}")
        angles_data.append("-" * 50)

        current_angle = initial_angle
        current_n = 1.000293

        angles_data.append(f"{'Initial':<12} {'--':<10} {current_angle:<10.3f} {'--':<10}")

        for i, (material_name, n2) in enumerate(self.materials):
            refracted_angle = self.snells_law(current_angle, current_n, n2)

            if refracted_angle is None:
                critical_angle = math.degrees(math.asin(n2 / current_n)) if n2 < current_n else None
                angles_data.append(f"{f'→{material_name[:8]}':<12} {current_angle:<10.3f} {'TIR':<10} {'--':<10}")
                if critical_angle:
                    angles_data.append(f"{'Critical:':<12} {critical_angle:<10.3f} {'--':<10} {'--':<10}")
                break
            else:
                deviation = abs(refracted_angle - current_angle)
                angles_data.append(
                    f"{f'→{material_name[:8]}':<12} {current_angle:<10.3f} {refracted_angle:<10.3f} {deviation:<10.3f}")
                current_angle = refracted_angle
                current_n = n2

        # Exit to air
        if refracted_angle is not None:
            exit_angle = self.snells_law(current_angle, current_n, 1.000293)
            if exit_angle is None:
                critical_angle = math.degrees(math.asin(1.000293 / current_n))
                angles_data.append(f"{'→Air':<12} {current_angle:<10.3f} {'TIR':<10} {'--':<10}")
                angles_data.append(f"{'Critical:':<12} {critical_angle:<10.3f} {'--':<10} {'--':<10}")
            else:
                deviation = abs(exit_angle - current_angle)
                angles_data.append(f"{'→Air':<12} {current_angle:<10.3f} {exit_angle:<10.3f} {deviation:<10.3f}")

        self.angles_text.insert(tk.END, "\n".join(angles_data))

        # Materials Data
        materials_data = []
        materials_data.append("🔬 MATERIAL PROPERTIES")
        materials_data.append("=" * 25)
        materials_data.append(f"{'Layer':<6} {'Material':<15} {'n':<10} {'Type':<10}")
        materials_data.append("-" * 45)

        materials_data.append(f"{'0':<6} {'Air':<15} {'1.000293':<10} {'Gas':<10}")

        for i, (name, n) in enumerate(self.materials):
            # Classify material type based on refractive index
            mat_type = self.get_material_type(n)

            materials_data.append(f"{i + 1:<6} {name[:15]:<15} {n:<10.6f} {mat_type:<10}")

        materials_data.append(f"{len(self.materials) + 1:<6} {'Air':<15} {'1.000293':<10} {'Gas':<10}")

        # Add material statistics
        if self.materials:
            materials_data.append("\n📈 STATISTICS")
            materials_data.append("-" * 20)
            n_values = [n for _, n in self.materials]
            materials_data.append(f"Min n: {min(n_values):.6f}")
            materials_data.append(f"Max n: {max(n_values):.6f}")
            materials_data.append(f"Avg n: {sum(n_values) / len(n_values):.6f}")

            # Calculate contrast ratios
            air_n = 1.000293
            max_contrast = max(max(n_values) / air_n, air_n / min(n_values))
            materials_data.append(f"Max contrast: {max_contrast:.3f}:1")

        self.materials_data_text.insert(tk.END, "\n".join(materials_data))

        # Make text widgets read-only
        self.summary_text.config(state='disabled')
        self.angles_text.config(state='disabled')
        self.materials_data_text.config(state='disabled')

    def setup_visualization_panel(self, parent):
        """Create the visualization panel"""
        viz_panel = tk.Frame(parent, bg=self.colors['background'])
        viz_panel.grid(row=0, column=1, sticky='nsew')
        viz_panel.columnconfigure(0, weight=1)
        viz_panel.rowconfigure(0, weight=1)

        # Visualization card with vibrant styling
        viz_frame = ttk.LabelFrame(viz_panel, text="🎨 Light Path Visualization", style='Card.TLabelframe', padding=15)
        viz_frame.grid(row=0, column=0, sticky='nsew')
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)

        # Canvas frame with colorful border
        canvas_frame = tk.Frame(viz_frame, bg=self.colors['accent2'], relief='raised', bd=4, padx=4, pady=4)
        canvas_frame.grid(row=0, column=0, sticky='nsew', pady=(10, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        # Create colorful canvas
        self.canvas = tk.Canvas(canvas_frame,
                                width=700,
                                height=600,
                                bg='#FAFBFF',
                                highlightthickness=0,
                                relief='flat')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # Add colorful scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Initialize visualization
        self.initialize_plot()

        # Update analysis data display
        self.update_analysis_data()

    def initialize_plot(self):
        """Initialize professional-looking empty plot"""
        self.canvas.delete("all")

        canvas_width = 700
        canvas_height = 600

        # Professional colorful grid
        grid_color = '#E1E7F5'
        major_grid_color = self.colors['accent2']

        # Minor grid
        for i in range(0, canvas_width, 20):
            self.canvas.create_line(i, 0, i, canvas_height, fill=grid_color, width=1)
        for i in range(0, canvas_height, 20):
            self.canvas.create_line(0, i, canvas_width, i, fill=grid_color, width=1)

        # Major grid
        for i in range(0, canvas_width, 100):
            self.canvas.create_line(i, 0, i, canvas_height, fill=major_grid_color, width=2, dash=(5, 3))
        for i in range(0, canvas_height, 100):
            self.canvas.create_line(0, i, canvas_width, i, fill=major_grid_color, width=2, dash=(5, 3))

        # Colorful center reference line
        center_x = canvas_width // 2
        self.canvas.create_line(center_x, 0, center_x, canvas_height,
                                fill=self.colors['accent1'], width=3, dash=(10, 5))

        # Vibrant welcome message with gradient-like background
        welcome_frame_x = canvas_width // 2
        welcome_frame_y = canvas_height // 2

        # Colorful background layers for depth effect
        self.canvas.create_rectangle(welcome_frame_x - 220, welcome_frame_y - 100,
                                     welcome_frame_x + 220, welcome_frame_y + 100,
                                     fill=self.colors['accent1'], outline='', width=0)

        self.canvas.create_rectangle(welcome_frame_x - 210, welcome_frame_y - 90,
                                     welcome_frame_x + 210, welcome_frame_y + 90,
                                     fill=self.colors['accent2'], outline='', width=0)

        self.canvas.create_rectangle(welcome_frame_x - 200, welcome_frame_y - 80,
                                     welcome_frame_x + 200, welcome_frame_y + 80,
                                     fill='white', outline=self.colors['primary'], width=3)

        # Colorful welcome text
        self.canvas.create_text(welcome_frame_x, welcome_frame_y - 40,
                                text='🌈 Optical Analysis',
                                font=('Segoe UI', 18, 'bold'),
                                fill=self.colors['primary'])

        self.canvas.create_text(welcome_frame_x, welcome_frame_y - 10,
                                text='🔬 Configure materials and parameters',
                                font=('Segoe UI', 12, 'bold'),
                                fill=self.colors['accent1'])

        self.canvas.create_text(welcome_frame_x, welcome_frame_y + 20,
                                text='⚡ then click "Calculate Light Path"',
                                font=('Segoe UI', 12, 'bold'),
                                fill=self.colors['accent4'])

        self.canvas.create_text(welcome_frame_x, welcome_frame_y + 50,
                                text='✨ by Noam Cohen Yahav .K. & Yahav .B.',
                                font=('Segoe UI', 10, 'italic'),
                                fill=self.colors['accent5'])

    def plot_light_path(self, path_data):
        """Professional light path visualization"""
        self.canvas.delete("all")

        if not path_data['success'] and 'tir_interface' not in path_data:
            self.initialize_plot()
            return

        canvas_width = 700
        canvas_height = 600
        margin = 60

        # Extract data
        x_coords = path_data['x_coords']
        y_coords = path_data['y_coords']
        interfaces = path_data['interfaces']
        material_names = path_data['material_names']
        angles = path_data['angles']

        # Professional color scheme for materials
        material_colors = [
            '#E3F2FD',  # Light Blue
            '#E8F5E8',  # Light Green
            '#FFF3E0',  # Light Orange
            '#F3E5F5',  # Light Purple
            '#E0F2F1',  # Light Teal
            '#FFF8E1',  # Light Yellow
            '#FCE4EC',  # Light Pink
            '#F1F8E9'  # Light Lime
        ]

        # Calculate scaling
        x_range = max(abs(min(x_coords)), abs(max(x_coords))) + 1
        y_range = max(y_coords) - min(y_coords) + 1

        scale_x = (canvas_width - 2 * margin) / (2 * x_range)
        scale_y = (canvas_height - 2 * margin) / y_range
        scale = min(scale_x, scale_y) * 0.8  # Add some padding

        center_x = canvas_width // 2
        center_y = margin + (max(y_coords) * scale)

        def transform_coords(x, y):
            canvas_x = center_x + (x * scale)
            canvas_y = center_y - (y * scale)
            return canvas_x, canvas_y

        # Draw professional grid
        grid_color = '#F0F0F0'
        for i in range(int(-x_range), int(x_range) + 1):
            if i != 0:  # Skip center line for now
                grid_x = transform_coords(i, 0)[0]
                self.canvas.create_line(grid_x, 0, grid_x, canvas_height,
                                        fill=grid_color, width=1)

        # Draw material regions with very subtle backgrounds only
        for i in range(len(interfaces) - 1):
            y_top = interfaces[i]
            y_bottom = interfaces[i + 1]

            x1, y1 = transform_coords(-x_range, y_top)
            x2, y2 = transform_coords(x_range, y_bottom)

            # Very subtle background color, almost transparent
            color = self.material_gradient_colors[i % len(self.material_gradient_colors)]
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=color, outline='', width=0)

            # Clean interface line without heavy styling
            line_y = transform_coords(0, y_top)[1]
            interface_color = self.colors['accent1'] if i % 2 == 0 else self.colors['accent4']
            self.canvas.create_line(x1, line_y, x2, line_y,
                                    fill=interface_color, width=2)

            # Simple material label without background squares
            if i < len(material_names) - 1:
                label_x = 40
                label_y = (y1 + y2) // 2

                # Just the text label, no background rectangles
                self.canvas.create_text(label_x, label_y,
                                        text=f"{material_names[i]}",
                                        font=('Segoe UI', 10, 'bold'),
                                        anchor='w',
                                        fill=self.colors['text'])

        # Draw light ray with softer rainbow effect
        if len(x_coords) >= 2:
            canvas_coords = []
            for x, y in zip(x_coords, y_coords):
                canvas_x, canvas_y = transform_coords(x, y)
                canvas_coords.extend([canvas_x, canvas_y])

            # Create softer glow effect layers
            glow_colors = ['#FCA5A5', '#FB7185', '#F87171', '#EF4444']
            glow_widths = [10, 7, 4, 2]

            for glow_color, glow_width in zip(glow_colors, glow_widths):
                self.canvas.create_line(canvas_coords,
                                        fill=glow_color,
                                        width=glow_width,
                                        smooth=False,
                                        capstyle='round')

            # Main softer light ray
            self.canvas.create_line(canvas_coords,
                                    fill='#FCD34D',  # Softer yellow center
                                    width=3,
                                    smooth=False,
                                    capstyle='round')

        # Vibrant arrows and annotations
        for i in range(len(x_coords) - 1):
            x1, y1 = transform_coords(x_coords[i], y_coords[i])
            x2, y2 = transform_coords(x_coords[i + 1], y_coords[i + 1])

            # Colorful directional arrow
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)

            if length > 30:
                dx /= length
                dy /= length

                arrow_size = 15
                arrow_x1 = mid_x + dx * arrow_size
                arrow_y1 = mid_y + dy * arrow_size
                arrow_x2 = mid_x + dx * arrow_size / 2 - dy * arrow_size / 2.5
                arrow_y2 = mid_y + dy * arrow_size / 2 + dx * arrow_size / 2.5
                arrow_x3 = mid_x + dx * arrow_size / 2 + dy * arrow_size / 2.5
                arrow_y3 = mid_y + dy * arrow_size / 2 - dx * arrow_size / 2.5

                # Rainbow arrow colors
                arrow_colors = [self.colors['accent3'], self.colors['warning'], self.colors['accent4']]
                arrow_color = arrow_colors[i % len(arrow_colors)]

                self.canvas.create_polygon([arrow_x1, arrow_y1, arrow_x2, arrow_y2, arrow_x3, arrow_y3],
                                           fill=arrow_color, outline='white', width=2)

            # Vibrant angle annotations
            if i < len(angles) and i < len(interfaces) - 1:
                angle_x = x1 + 50
                angle_y = y1 - 30

                # Colorful angle badge with multiple layers
                badge_colors = [self.colors['primary'], self.colors['accent1'], self.colors['accent2']]
                badge_color = badge_colors[i % len(badge_colors)]

                # Create layered circular badge
                self.canvas.create_oval(angle_x - 25, angle_y - 18,
                                        angle_x + 25, angle_y + 18,
                                        fill=badge_color, outline='white', width=3)

                self.canvas.create_oval(angle_x - 22, angle_y - 15,
                                        angle_x + 22, angle_y + 15,
                                        fill='white', outline=badge_color, width=2)

                self.canvas.create_text(angle_x, angle_y,
                                        text=f'{angles[i]:.1f}°',
                                        font=('Segoe UI', 9, 'bold'),
                                        fill=badge_color)

        # Clean axis labels without depth reference
        self.canvas.create_text(canvas_width // 2, canvas_height - 25,
                                text='🌈 Horizontal Distance (relative units)',
                                font=('Segoe UI', 14, 'bold'),
                                fill=self.colors['accent1'])

        # Vibrant title with status indication
        if not path_data['success']:
            title_text = "🚫 Light Ray Analysis - Total Internal Reflection Detected"
            title_color = self.colors['error']
            # Add warning background
            self.canvas.create_rectangle(canvas_width // 2 - 300, 10,
                                         canvas_width // 2 + 300, 50,
                                         fill='#FEE2E2', outline=self.colors['error'], width=2)
        else:
            title_text = "✨ Light Ray Propagation Analysis - Success"
            title_color = self.colors['success']
            # Add success background
            self.canvas.create_rectangle(canvas_width // 2 - 300, 10,
                                         canvas_width // 2 + 300, 50,
                                         fill='#D1FAE5', outline=self.colors['success'], width=2)

        self.canvas.create_text(canvas_width // 2, 30,
                                text=title_text,
                                font=('Segoe UI', 16, 'bold'),
                                fill=title_color)

    def update_material_list(self):
        """Update the material dropdown with basic materials only"""
        materials = [f"{name} (n = {index})" for name, index in self.basic_materials]
        self.material_combo['values'] = materials
        self.material_combo.set('')  # Clear selection

    def quick_add_material(self):
        """Quickly add a material from the library"""
        selected = self.common_material_var.get()
        if not selected:
            messagebox.showwarning("No Selection",
                                   "Please select a material from the library first.",
                                   icon='warning')
            return

        # Parse the selected material
        if " (n = " in selected:
            name = selected.split(" (n = ")[0]
            n_value = float(selected.split(" (n = ")[1].rstrip(")"))
        else:
            messagebox.showerror("Error", "Invalid material format selected.")
            return

        # Check if material already exists
        for existing_name, existing_n in self.materials:
            if existing_name == name:
                result = messagebox.askyesno("Duplicate Material",
                                             f"'{name}' is already in your material stack.\n"
                                             "Add it again anyway?",
                                             icon='question')
                if not result:
                    return
                break

        # Add to materials list
        self.materials.append((name, n_value))

        # Update listbox with vibrant formatting
        sparkle_icons = ['✨', '⭐', '🌟', '💫', '🔥', '⚡', '💎', '🌈']
        icon = sparkle_icons[len(self.materials) % len(sparkle_icons)]
        display_text = f"{icon} {name} (n = {n_value:.4f})"
        self.materials_listbox.insert(tk.END, display_text)

        # Clear selection and show success
        self.common_material_var.set("")
        self.materials_listbox.selection_clear(0, tk.END)
        self.materials_listbox.selection_set(tk.END)
        self.materials_listbox.see(tk.END)

        # Update the showcase
        self.update_material_showcase()

    def on_common_material_selected(self, event=None):
        """Auto-fill material from library selection"""
        selected = self.common_material_var.get()
        if not selected:
            return

        # Parse the selected material
        if " (n = " in selected:
            name = selected.split(" (n = ")[0]
            n_value = selected.split(" (n = ")[1].rstrip(")")

            # Auto-fill custom material fields
            self.material_name_var.set(name)
            self.refractive_index_var.set(n_value)

    def add_material(self):
        """Add material with professional validation"""
        name = self.material_name_var.get().strip()
        refractive_index_str = self.refractive_index_var.get().strip()

        if not name:
            messagebox.showerror("Input Error",
                                 "Please enter a material name.",
                                 icon='error')
            return

        try:
            refractive_index = float(refractive_index_str)
            if refractive_index <= 0:
                messagebox.showerror("Invalid Value",
                                     "Refractive index must be positive.",
                                     icon='error')
                return
            if refractive_index > 10:
                result = messagebox.askyesno("High Refractive Index",
                                             f"Refractive index {refractive_index} is unusually high.\n"
                                             "Are you sure this is correct?",
                                             icon='warning')
                if not result:
                    return
        except ValueError:
            messagebox.showerror("Invalid Format",
                                 "Please enter a valid numeric refractive index.",
                                 icon='error')
            return

        # Add to materials list
        self.materials.append((name, refractive_index))

        # Update listbox with vibrant formatting and icons
        icon_colors = ['🔹', '🔸', '🔺', '🔻', '◆', '◇', '●', '○']
        icon = icon_colors[len(self.materials) % len(icon_colors)]
        display_text = f"{icon} {name} (n = {refractive_index:.4f})"
        self.materials_listbox.insert(tk.END, display_text)

        # Clear input fields
        self.material_name_var.set("")
        self.refractive_index_var.set("")
        self.common_material_var.set("")

        # Show success feedback
        self.materials_listbox.selection_clear(0, tk.END)
        self.materials_listbox.selection_set(tk.END)

        # Update the showcase
        self.update_material_showcase()

    def remove_material(self):
        """Remove selected material"""
        selection = self.materials_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Please select a material to remove.",
                                   icon='warning')
            return

        index = selection[0]
        material_name = self.materials[index][0]

        result = messagebox.askyesno("Confirm Removal",
                                     f"Remove '{material_name}' from the material stack?",
                                     icon='question')
        if result:
            self.materials.pop(index)
            self.materials_listbox.delete(index)
            # Update analysis data display and showcase
            self.update_analysis_data()
            self.update_material_showcase()

    def clear_materials(self):
        """Clear all materials with confirmation"""
        if not self.materials:
            return

        result = messagebox.askyesno("Clear All Materials",
                                     "Remove all materials from the stack?\n"
                                     "This action cannot be undone.",
                                     icon='question')
        if result:
            self.materials.clear()
            self.materials_listbox.delete(0, tk.END)
            # Update analysis data display and showcase
            self.update_analysis_data()
            self.update_material_showcase()

    def snells_law(self, angle_in_degrees, n1, n2):
        """Calculate refracted angle using Snell's law"""
        if angle_in_degrees >= 90:
            return None

        angle_in_radians = math.radians(angle_in_degrees)
        sin_theta2 = (n1 * math.sin(angle_in_radians)) / n2

        if sin_theta2 > 1:
            return None  # Total internal reflection

        theta2_radians = math.asin(sin_theta2)
        return math.degrees(theta2_radians)

    def calculate_path_coordinates(self, initial_angle, materials):
        """Calculate light path coordinates with professional precision"""
        x_coords = [0]
        y_coords = [1]
        angles = [initial_angle]
        interfaces = [0]
        material_names = ['Air']

        current_angle = initial_angle
        current_n = 1.000293  # More precise air refractive index
        current_x = 0
        current_y = 1

        # Interface positions
        for i in range(len(materials)):
            interfaces.append(-(i + 1))
            material_names.append(materials[i][0])

        interfaces.append(-(len(materials) + 1))
        material_names.append('Air')

        # Calculate through each material
        for i, (material_name, n2) in enumerate(materials):
            interface_y = interfaces[i + 1]
            depth_to_travel = current_y - interface_y

            if abs(current_angle - 90) < 1e-10:
                horizontal_distance = 0
            else:
                horizontal_distance = depth_to_travel * math.tan(math.radians(current_angle))

            current_x += horizontal_distance
            current_y = interface_y
            x_coords.append(current_x)
            y_coords.append(current_y)

            refracted_angle = self.snells_law(current_angle, current_n, n2)

            if refracted_angle is None:
                return {
                    'success': False,
                    'x_coords': x_coords,
                    'y_coords': y_coords,
                    'interfaces': interfaces[:i + 2],
                    'material_names': material_names[:i + 2],
                    'angles': angles,
                    'tir_interface': i + 1
                }

            current_angle = refracted_angle
            current_n = n2
            angles.append(current_angle)

        # Exit to air
        exit_interface_y = interfaces[-1]
        depth_to_travel = current_y - exit_interface_y

        if abs(current_angle - 90) < 1e-10:
            horizontal_distance = 0
        else:
            horizontal_distance = depth_to_travel * math.tan(math.radians(current_angle))

        current_x += horizontal_distance
        current_y = exit_interface_y
        x_coords.append(current_x)
        y_coords.append(current_y)

        exit_angle = self.snells_law(current_angle, current_n, 1.000293)

        if exit_angle is None:
            return {
                'success': False,
                'x_coords': x_coords,
                'y_coords': y_coords,
                'interfaces': interfaces,
                'material_names': material_names,
                'angles': angles,
                'tir_interface': len(materials) + 1
            }

        angles.append(exit_angle)

        # Final segment
        final_segment_length = 0.5
        if abs(exit_angle - 90) < 1e-10:
            final_horizontal = 0
        else:
            final_horizontal = final_segment_length * math.tan(math.radians(exit_angle))

        x_coords.append(current_x + final_horizontal)
        y_coords.append(current_y - final_segment_length)

        return {
            'success': True,
            'x_coords': x_coords,
            'y_coords': y_coords,
            'interfaces': interfaces,
            'material_names': material_names,
            'angles': angles,
            'exit_angle': exit_angle
        }

    def calculate(self):
        """Professional calculation with comprehensive validation"""
        # Validate input
        try:
            initial_angle = float(self.angle_var.get())
            if not (0 <= initial_angle < 90):
                messagebox.showerror("Invalid Angle",
                                     "Incident angle must be between 0° and 90° (exclusive).",
                                     icon='error')
                return
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter a valid numeric angle value.",
                                 icon='error')
            return

        if not self.materials:
            messagebox.showerror("No Materials",
                                 "Please add at least one material to analyze.",
                                 icon='error')
            return

        # Clear and prepare results
        self.results_text.delete(1.0, tk.END)

        # Calculate path
        path_data = self.calculate_path_coordinates(initial_angle, self.materials)

        # Update visualization
        self.plot_light_path(path_data)

        # Update analysis data display
        self.update_analysis_data(path_data, initial_angle)

        # Generate professional report
        self.generate_professional_report(initial_angle, path_data)

    def generate_professional_report(self, initial_angle, path_data):
        """Generate comprehensive professional analysis report"""
        report = []

        # Header
        report.append("=" * 70)
        report.append("🔬 OPTICAL ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"📅 Analysis Date: 2025-06-28")
        report.append(f"👥 Project by: Noam Cohen, Yahav .K. & Yahav .B.")
        report.append(f"📐 Initial Incident Angle: {initial_angle:.3f}°")
        report.append(f"🌍 Initial Medium: Air (n = 1.000293)")
        report.append(f"📊 Number of Materials: {len(self.materials)}")
        report.append("")

        # Material stack summary
        report.append("📋 MATERIAL STACK CONFIGURATION")
        report.append("-" * 50)
        for i, (name, n) in enumerate(self.materials):
            report.append(f"   Layer {i + 1}: {name} (n = {n:.6f})")
        report.append("")

        # Ray tracing analysis
        report.append("🔍 RAY TRACING ANALYSIS")
        report.append("-" * 50)

        current_angle = initial_angle
        current_n = 1.000293
        refracted_angle = None

        for i, (material_name, n2) in enumerate(self.materials):
            report.append(f"Interface {i + 1}: Air → {material_name}")
            report.append(f"   ↳ Incident Angle: {current_angle:.3f}°")
            report.append(f"   ↳ n₁ = {current_n:.6f}, n₂ = {n2:.6f}")

            refracted_angle = self.snells_law(current_angle, current_n, n2)

            if refracted_angle is None:
                critical_angle = math.degrees(math.asin(n2 / current_n)) if n2 < current_n else None
                report.append(f"   ❌ TOTAL INTERNAL REFLECTION OCCURRED!")
                if critical_angle:
                    report.append(f"   ↳ Critical Angle: {critical_angle:.3f}°")
                    report.append(f"   ↳ Incident angle {current_angle:.3f}° > Critical angle")
                report.append("   ↳ Light cannot propagate further")
                break
            else:
                report.append(f"   ✅ Refracted Angle: {refracted_angle:.3f}°")

                # Calculate angle deviation
                deviation = abs(refracted_angle - current_angle)
                report.append(f"   ↳ Angular Deviation: {deviation:.3f}°")

                # Determine bending direction
                if refracted_angle < current_angle:
                    report.append("   ↳ Light bends toward normal (denser medium)")
                elif refracted_angle > current_angle:
                    report.append("   ↳ Light bends away from normal (rarer medium)")
                else:
                    report.append("   ↳ No bending (same refractive index)")

                current_angle = refracted_angle
                current_n = n2

            report.append("")

        # Exit analysis
        if refracted_angle is not None:
            report.append(f"Final Interface: {self.materials[-1][0]} → Air")
            report.append(f"   ↳ Incident Angle: {current_angle:.3f}°")
            report.append(f"   ↳ n₁ = {current_n:.6f}, n₂ = 1.000293")

            exit_angle = self.snells_law(current_angle, current_n, 1.000293)

            if exit_angle is None:
                critical_angle = math.degrees(math.asin(1.000293 / current_n))
                report.append(f"   ❌ TOTAL INTERNAL REFLECTION at exit!")
                report.append(f"   ↳ Critical Angle: {critical_angle:.3f}°")
            else:
                report.append(f"   ✅ Exit Angle: {exit_angle:.3f}°")
                report.append("")

                # Summary statistics
                report.append("📊 SUMMARY STATISTICS")
                report.append("-" * 50)
                report.append(f"✅ Ray successfully transmitted through all materials")
                report.append(f"📐 Final Exit Angle: {exit_angle:.3f}°")

                total_deviation = abs(exit_angle - initial_angle)
                report.append(f"📏 Total Angular Deviation: {total_deviation:.3f}°")

                if total_deviation < 1.0:
                    report.append("   ↳ Minimal deviation (< 1°)")
                elif total_deviation < 5.0:
                    report.append("   ↳ Low deviation (< 5°)")
                elif total_deviation < 15.0:
                    report.append("   ↳ Moderate deviation (< 15°)")
                else:
                    report.append("   ↳ High deviation (≥ 15°)")

                # Calculate lateral displacement if materials are parallel
                if len(self.materials) == 1:
                    thickness = 1.0  # Assume unit thickness
                    lateral_displacement = thickness * math.sin(math.radians(current_angle - initial_angle)) / math.cos(
                        math.radians(refracted_angle))
                    report.append(f"📍 Lateral Displacement: {lateral_displacement:.4f} units")

        # Display report
        report_text = "\n".join(report)
        self.results_text.insert(tk.END, report_text)

        # Scroll to top
        self.results_text.see("1.0")

    def show_explanation(self):
        """Show explanation dialog with how-to-use information"""
        explanation_window = tk.Toplevel(self.root)
        explanation_window.title("Snell's Law Explanation")
        explanation_window.geometry("1000x900")
        explanation_window.configure(bg='white')
        explanation_window.resizable(True, True)

        # Center the explanation window
        explanation_window.transient(self.root)
        explanation_window.grab_set()

        # Center the window on the parent
        explanation_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (explanation_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (explanation_window.winfo_height() // 2)
        explanation_window.geometry(f"+{x}+{y}")

        # Header
        header_frame = tk.Frame(explanation_window, bg=self.colors['accent4'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame,
                                text="📖Snell's Law Explanation📖",
                                font=('Segoe UI', 18, 'bold'),
                                fg='white',
                                bg=self.colors['accent4'])
        header_label.pack(expand=True)

        # Scrollable content frame
        canvas = tk.Canvas(explanation_window, bg='white')
        scrollbar = ttk.Scrollbar(explanation_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Content
        content_frame = tk.Frame(scrollable_frame, bg='white', padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)

        # Explanation guide with Hebrew content (properly formatted for RTL with fixed punctuation)
        guide_text = """
    אופטיקה גאומטרית היא תחום בפיזיקה שמסביר כי אור מתנהג בצורה פשוטה׃
    כאילו הוא נע בקווים ישרים׃
    במקום לחשוב על האור כגלים ‏(כמו בגלי קול‏)‏, אנו מתייחסים אליו כאל קרניים –
    מין חצים של אור שנעים בקו ישר׃ קופצים ממשטחים ‏(החזרה‏)‏, או משנים כיוון כשהם נכנסים לחומר אחר ‏(שבירה‏)׃
    אחת התופעות הנפוצות באופטיקה גאומטרית היא שבירת אור׃
    שבירה מתרחשת כשהאור עובר מחומר אחד לחומר אחר – לדוגמה׃ מאוויר למים – ואז הוא משנה את כיוון התנועה שלו׃
    זה קורה כי האור נע במהירות שונה בכל חומר׃
    באוויר הוא נע מהר יותר מאשר במים׃ ולכן כשהוא נכנס לחומר צפוף יותר׃ הקרן "מתכופפת"׃
    תופעה זו מסבירה למשל למה כפית בתוך כוס מים נראית עקומה – האור שעובר מהמכסה של הכוס למים ואז לעין שלנו נשבר ומשנה את כיוונו׃
    כדי להבין בדיוק איך מתרחשת השבירה וכמה הקרן מתכופפת׃ משתמשים בחוק סנל׃
    החוק הזה מתאר את הקשר בין זווית הפגיעה של קרן האור לבין זווית השבירה שלה׃ והוא נראה כך׃

    n₁⋅sin‏(θ₁‏) = n₂⋅sin‏(θ₂‏)

    כאן n₁ ו־n₂ הם מקדמי השבירה של שני החומרים ‏(למשל אוויר ומים‏)‏,
    ו־θ₁ וθ₂ הן הזוויות שהאור יוצר עם הקו הניצב לפני ואחרי שהוא עובר את הגבול בין החומרים׃
    בעזרת חוק זה׃ ניתן לחשב ולחזות את כיוון האור בכל מצב שבו הוא עובר מחומר אחד לשני׃
            """

        info_label = tk.Label(content_frame,
                              text=guide_text.strip(),
                              font=('Segoe UI', 12),
                              fg=self.colors['text'],
                              bg='white',
                              justify='right',
                              anchor='ne',
                              wraplength=700)
        info_label.pack(fill='both', expand=True)

        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Close button frame
        close_frame = tk.Frame(explanation_window, bg='white', pady=10)
        close_frame.pack(fill='x')

        close_btn = tk.Button(close_frame,
                              text="Got it! 👍",
                              font=('Segoe UI', 11, 'bold'),
                              fg='white',
                              bg=self.colors['accent4'],
                              relief='flat',
                              padx=30,
                              pady=8,
                              command=explanation_window.destroy,
                              cursor='hand2')
        close_btn.pack()

        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

    def show_about(self):
        """Show about dialog with project information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Snell's Law Calculator")
        about_window.geometry("700x700")
        about_window.configure(bg='white')
        about_window.resizable(False, False)

        # Center the about window
        about_window.transient(self.root)
        about_window.grab_set()

        # Center the window on the parent
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (about_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")

        # Header
        header_frame = tk.Frame(about_window, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame,
                                text="⚡ Snell's Law Calculator ⚡",
                                font=('Segoe UI', 18, 'bold'),
                                fg='white',
                                bg=self.colors['primary'])
        header_label.pack(expand=True)

        # Content frame
        content_frame = tk.Frame(about_window, bg='white', padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)

        # Project information
        info_text = """
🎓 PROJECT INFORMATION

Project Title: Snell's Law Calculator
תאריך הגשה : 2025

👥 מגישים: 
• Noam Cohen
• Yahav Kleinman  
• Yahav Blumenfeld


⚖️ SNELL'S LAW
n₁ × sin(θ₁) = n₂ × sin(θ₂)


📧 Contact: For questions or suggestions, please contact one of our developers, Yahav .K., enjoy.
        yahav.kleinman@gmail.com

        """

        info_label = tk.Label(content_frame,
                              text=info_text.strip(),
                              font=('Segoe UI', 10),
                              fg=self.colors['text'],
                              bg='white',
                              justify='left',
                              anchor='nw')
        info_label.pack(fill='both', expand=True)

        # Close button
        close_frame = tk.Frame(about_window, bg='white', pady=10)
        close_frame.pack(fill='x')

        close_btn = tk.Button(close_frame,
                              text="Close",
                              font=('Segoe UI', 11, 'bold'),
                              fg='white',
                              bg=self.colors['primary'],
                              relief='flat',
                              padx=30,
                              pady=8,
                              command=about_window.destroy,
                              cursor='hand2')
        close_btn.pack()


def main():
    """Launch the professional Snell's Law Calculator"""
    root = tk.Tk()

    # Set application icon (if available)
    try:
        root.iconbitmap('icon.ico')  # Add an icon file if available
    except:
        pass

    # Create application
    app = SnellsLawGUI(root)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    # Start application
    root.mainloop()


if __name__ == "__main__":
    main()