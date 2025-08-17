import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
import os
import json
import shutil
import uuid
from PIL import Image, ImageTk


class DefectReporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Production Line Defect Reporter")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Configuration
        self.data_file = "defect_record.csv"
        self.config_file = "defect_config.json"
        self.images_dir = "defect_images"

        # Create images directory if not exists
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        # Initialize UI and data
        self.load_config()
        self.setup_ui()
        self.initialize_data_file()

        # Initialize image path
        self.image_path = None
        self.image_preview = None

    def load_config(self):
        """Load configuration from JSON or create default"""
        try:
            with open(self.config_file) as f:
                self.config = json.load(f)
        except:
            self.config = {
                "models": ["CD70", "Pridor", "CG-125", "KYHS", "K4AA"],
                "shifts": ["A", "B", "C", "R"],
                "inspectors": ["John", "Sarah", "Mike", "Admin"],
                "defect_categories": {
                    "Soldering NG": [
                        "Wire soldering NG",
                        "Charge coil soldering NG",
                        "Sensor soldering NG",
                        "Extra Soldering NG",
                        "Neutral wire Soldering NG",
                        "Armature Soldering NG"
                    ],
                    "Damage": [
                        "Core Assy. Damage",
                        "Dent on Base Plate",
                        "Rotor Dent",
                        "Core dent",
                        "Nuetral Wire Damage",
                        "Connector damage",
                        "Sensor damage",
                        "Wire Damage",
                        "Magnet damage",
                        "Charge coil terminal damage",
                        "Wire Ground"
                    ],
                    "Part Missing": [
                        "Grommet Miss",
                        "Tape vinyl miss",
                        "Clip cord miss",
                        "Oring miss",
                        "Rivet miss",
                        "M4 screw miss",
                        "Oil seal spring miss",
                        "Sensor spring miss",
                        "Sensor clip miss",
                        "Oil seal miss"
                    ],
                    "Process missing": [
                        "Black wire no soldering cutting",
                        "Wire soldering miss",
                        "Armature soldering miss",
                        "Sensor soldering miss",
                        "Charge coil soldering miss",
                        "Adhesive material miss",
                        "Extra wire",
                        "No wire cutting",
                        "Soldering Cutting miss",
                        "Armature caulking miss",
                        "Sensor caulking miss",
                        "Wire assy caulking miss",
                        "Armature date stamping miss",
                        "Charge coil Cemedine material miss",
                        "Rotor date stamping miss"
                    ],
                    "Process NG": [
                        "Boss rotor thread NG",
                        "Terminal no press",
                        "Soldering Cutting NG",
                        "Peeling NG",
                        "Winding NG",
                        "Wire Cutting NG",
                        "Winding Wire loose",
                        "Charge coil Terminal Band",
                        "M4 screw Loose",
                        "M4 screw NG",
                        "M6 screw NG",
                        "Cord height NG",
                        "Armature caulking",
                        "Sensor caulking",
                        "Wire assy caulking",
                        "Adhesive material on rotor",
                        "Rotor Chamfer NG",
                        "Charge coil tape extra",
                        "Armature date stamping NG",
                        "Rivet no press",
                        "Cemedine bubble on charge coil",
                        "Boss Rotor Rust",
                        "Rotor burr inside",
                        "Sensor burr",
                        "Sensor spring not proper clamp",
                        "Pole magnet caulking NG",
                        "Burr on oring",
                        "Black Wire root NG",
                        "Rust on Core W/Insulator",
                        "Rotor double date stamping",
                        "Rotor in side m4 screw",
                        "Charge coil silicone not proper",
                        "Rust on armature",
                        "Yellow wire core inside",
                        "Armature golden clip height",
                        "Tape NG",
                        "Rust on rotor assy",
                        "Charge coil tape NG",
                        "Rotor Burr",
                        "Boss rotor Burr inside & outside",
                        "Charge coil wire loose",
                        "Oil seal height",
                        "Adhesive material on core"
                    ],
                    "Part NG": [
                        "Base plate NG",
                        "Oil Seal NG",
                        "Rotor Date NG",
                        "Boss rotor NG"
                    ]
                }
            }
            self.save_config()

    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def initialize_data_file(self):
        """Create CSV file with headers if missing"""
        if not os.path.exists(self.data_file):
            columns = [
                "Timestamp", "Date", "Shift Incharge", "Model", "Shift",
                "DefectCategory", "DefectType", "Count", "Notes", "ImagePath"
            ]
            pd.DataFrame(columns=columns).to_csv(self.data_file, index=False)

    def setup_ui(self):
        """Build the user interface"""
        # Style configuration
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Header.TLabel", background="#4a6baf",
                        foreground="white", font=("Arial", 14, "bold"))
        style.configure("Section.TLabel", background="#d9e1f2",
                        font=("Arial", 11, "bold"))

        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=4,
                          sticky="ew", pady=(0, 20))
        header = ttk.Label(
            header_frame,
            text="DAILY LINE DEFECTS REPORTING SYSTEM",
            style="Header.TLabel",
            anchor="center"
        )
        header.pack(fill=tk.BOTH, padx=10, pady=10)

        # Form container
        form_frame = ttk.LabelFrame(
            main_frame, text="Defect Information", padding="15")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Form fields
        fields = [
            ("Date:", "date_entry", self.add_date_field, 1),
            ("Shift Incharge:", "inspector_dropdown", self.add_inspector_field, 2),
            ("Model:", "model_dropdown", self.add_model_field, 3),
            ("Shift:", "shift_dropdown", self.add_shift_field, 4),
            ("Defect Category:", "category_dropdown", self.add_category_field, 5),
            ("Defect Type:", "defect_dropdown", self.add_defect_field, 6),
            ("Count:", "count_spinbox", self.add_count_field, 7),
            ("Notes:", "notes_text", self.add_notes_field, 8),
        ]

        for label_text, widget_name, method, row in fields:
            ttk.Label(form_frame, text=label_text).grid(
                row=row, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            method(form_frame, row)

        # Image upload section
        image_frame = ttk.LabelFrame(
            main_frame, text="Defect Image", padding="15")
        image_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        # Image preview
        self.image_label = ttk.Label(
            image_frame, text="No image selected", anchor="center")
        self.image_label.pack(fill=tk.BOTH, expand=True, pady=10)

        # Upload button
        upload_btn = ttk.Button(
            image_frame,
            text="Upload Image",
            command=self.upload_image
        )
        upload_btn.pack(pady=10)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

        submit_btn = ttk.Button(
            button_frame,
            text="Submit Defect",
            command=self.submit_defect,
            style="Accent.TButton"
        )
        submit_btn.pack(side=tk.LEFT, padx=10, ipadx=15)

        clear_btn = ttk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form
        )
        clear_btn.pack(side=tk.LEFT, padx=10, ipadx=15)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to record defects")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.grid(row=3, column=0, columnspan=2,
                          sticky=tk.EW, pady=(10, 0))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Create accent style for submit button
        style.configure("Accent.TButton", background="#4CAF50",
                        foreground="white")

    def add_date_field(self, parent, row):
        self.date_entry = ttk.Entry(parent)
        self.date_entry.grid(row=row, column=1, sticky=tk.EW, pady=8)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def add_inspector_field(self, parent, row):
        self.inspector_var = tk.StringVar()
        self.inspector_dropdown = ttk.Combobox(
            parent,
            textvariable=self.inspector_var,
            values=self.config["inspectors"]
        )
        self.inspector_dropdown.grid(row=row, column=1, sticky=tk.EW, pady=8)

    def add_model_field(self, parent, row):
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            parent,
            textvariable=self.model_var,
            values=self.config["models"]
        )
        self.model_dropdown.grid(row=row, column=1, sticky=tk.EW, pady=8)

    def add_shift_field(self, parent, row):
        self.shift_var = tk.StringVar()
        self.shift_dropdown = ttk.Combobox(
            parent,
            textvariable=self.shift_var,
            values=self.config["shifts"]
        )
        self.shift_dropdown.grid(row=row, column=1, sticky=tk.EW, pady=8)

    def add_category_field(self, parent, row):
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            parent,
            textvariable=self.category_var,
            values=list(self.config["defect_categories"].keys())
        )
        self.category_dropdown.grid(row=row, column=1, sticky=tk.EW, pady=8)
        self.category_dropdown.bind(
            "<<ComboboxSelected>>", self.update_defect_types)

    def add_defect_field(self, parent, row):
        self.defect_var = tk.StringVar()
        self.defect_dropdown = ttk.Combobox(
            parent,
            textvariable=self.defect_var
        )
        self.defect_dropdown.grid(row=row, column=1, sticky=tk.EW, pady=8)

    def add_count_field(self, parent, row):
        self.count_spinbox = ttk.Spinbox(parent, from_=1, to=100, width=5)
        self.count_spinbox.grid(row=row, column=1, sticky=tk.W, pady=8)
        self.count_spinbox.set(1)

    def add_notes_field(self, parent, row):
        notes_frame = ttk.Frame(parent)
        notes_frame.grid(row=row, column=1, sticky=tk.EW, pady=8)

        self.notes_text = tk.Text(
            notes_frame, width=30, height=5, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(notes_frame, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=scrollbar.set)

        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_defect_types(self, event=None):
        """Update defect types based on selected category"""
        category = self.category_var.get()
        if category in self.config["defect_categories"]:
            self.defect_dropdown["values"] = self.config["defect_categories"][category]
        else:
            self.defect_dropdown["values"] = []

    def upload_image(self):
        """Open file dialog to select and preview image"""
        file_path = filedialog.askopenfilename(
            title="Select Defect Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )

        if file_path:
            try:
                # Generate unique filename
                file_ext = os.path.splitext(file_path)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                self.image_path = os.path.join(
                    self.images_dir, unique_filename)

                # Copy image to defect_images directory
                shutil.copy(file_path, self.image_path)

                # Display preview
                self.show_image_preview(file_path)

                self.status_var.set(
                    f"Image uploaded: {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror(
                    "Image Error", f"Failed to upload image: {str(e)}")
                self.image_path = None

    def show_image_preview(self, image_path):
        """Display a preview of the selected image"""
        try:
            # Open and resize image
            img = Image.open(image_path)
            img.thumbnail((300, 300))  # Resize to fit in preview area

            # Convert to PhotoImage
            self.image_preview = ImageTk.PhotoImage(img)

            # Update label with image
            self.image_label.configure(image=self.image_preview, text="")
        except Exception as e:
            self.image_label.configure(text=f"Preview error: {str(e)}")
            self.image_path = None

    def submit_defect(self):
        """Save defect record to CSV"""
        try:
            # Validate inputs
            required_fields = {
                "Date": self.date_entry.get(),
                "Shift Incharge": self.inspector_var.get(),
                "Model": self.model_var.get(),
                "Shift": self.shift_var.get(),
                "Defect Category": self.category_var.get(),
                "Defect Type": self.defect_var.get()
            }

            missing = [field for field,
                       value in required_fields.items() if not value]
            if missing:
                messagebox.showwarning(
                    "Input Error",
                    f"Please fill all required fields:\n{', '.join(missing)}"
                )
                return

            # Create new record
            new_record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Date": required_fields["Date"],
                "Shift Incharge": required_fields["Shift Incharge"],
                "Model": required_fields["Model"],
                "Shift": required_fields["Shift"],
                "DefectCategory": required_fields["Defect Category"],
                "DefectType": required_fields["Defect Type"],
                "Count": int(self.count_spinbox.get()),
                "Notes": self.notes_text.get("1.0", tk.END).strip(),
                "ImagePath": self.image_path if self.image_path else ""
            }

            # Append to CSV
            pd.DataFrame([new_record]).to_csv(
                self.data_file,
                mode='a',
                header=False,
                index=False
            )

            self.status_var.set(
                f"Defect recorded at {new_record['Timestamp']}")
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save defect: {str(e)}")

    def clear_form(self):
        """Reset form fields and image preview"""
        self.model_var.set('')
        self.shift_var.set('')
        self.category_var.set('')
        self.defect_var.set('')
        self.count_spinbox.set(1)
        self.notes_text.delete("1.0", tk.END)

        # Clear image
        self.image_path = None
        self.image_label.configure(image='', text="No image selected")
        self.image_preview = None

        self.model_dropdown.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = DefectReporter(root)
    root.mainloop()
