import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import os
import json

class DefectReporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Production Line Defect Reporter")
        self.root.geometry("1000x700")
        
        # Configuration
        self.data_file = "defect_records.csv"
        self.config_file = "defect_config.json"
        
        # Initialize UI and data
        self.load_config()
        self.setup_ui()
        self.initialize_data_file()

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
                "DefectCategory", "DefectType", "Count", "Notes"
            ]
            pd.DataFrame(columns=columns).to_csv(self.data_file, index=False)

    def setup_ui(self):
        """Build the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(
            main_frame, 
            text="DAILY LINE DEFECTS REPORTING SYSTEM",
            font=('Helvetica', 14, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=10)

        # Form fields
        ttk.Label(main_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame)
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(main_frame, text="Shift Incharge:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.inspector_var = tk.StringVar()
        self.inspector_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.inspector_var,
            values=self.config["inspectors"]
        )
        self.inspector_dropdown.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.model_var,
            values=self.config["models"]
        )
        self.model_dropdown.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Shift:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.shift_var = tk.StringVar()
        self.shift_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.shift_var,
            values=self.config["shifts"]
        )
        self.shift_dropdown.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Defect Category:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.category_var,
            values=list(self.config["defect_categories"].keys())
        )
        self.category_dropdown.grid(row=5, column=1, sticky=tk.W, pady=5)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.update_defect_types)

        ttk.Label(main_frame, text="Defect Type:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.defect_var = tk.StringVar()
        self.defect_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.defect_var
        )
        self.defect_dropdown.grid(row=6, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Count:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.count_spinbox = ttk.Spinbox(main_frame, from_=1, to=100, width=5)
        self.count_spinbox.grid(row=7, column=1, sticky=tk.W, pady=5)
        self.count_spinbox.set(1)

        ttk.Label(main_frame, text="Notes:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        self.notes_text.grid(row=8, column=1, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        submit_btn = ttk.Button(
            button_frame, 
            text="Submit Defect", 
            command=self.submit_defect
        )
        submit_btn.pack(side=tk.LEFT, padx=10)

        clear_btn = ttk.Button(
            button_frame, 
            text="Clear Form", 
            command=self.clear_form
        )
        clear_btn.pack(side=tk.LEFT, padx=10)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to record defects")
        status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN
        )
        status_label.grid(row=10, column=0, columnspan=2, sticky=tk.W+tk.E)

    def update_defect_types(self, event=None):
        """Update defect types based on selected category"""
        category = self.category_var.get()
        if category in self.config["defect_categories"]:
            self.defect_dropdown["values"] = self.config["defect_categories"][category]
        else:
            self.defect_dropdown["values"] = []

    def submit_defect(self):
        """Save defect record to CSV"""
        try:
            # Validate inputs
            if not all([
                self.date_entry.get(),
                self.inspector_var.get(),
                self.model_var.get(),
                self.shift_var.get(),
                self.category_var.get(),
                self.defect_var.get()
            ]):
                messagebox.showwarning("Input Error", "Please fill all required fields")
                return

            # Create new record
            new_record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Date": self.date_entry.get(),
                "Shift Incharge": self.inspector_var.get(),
                "Model": self.model_var.get(),
                "Shift": self.shift_var.get(),
                "DefectCategory": self.category_var.get(),
                "DefectType": self.defect_var.get(),
                "Count": int(self.count_spinbox.get()),
                "Notes": self.notes_text.get("1.0", tk.END).strip()
            }

            # Append to CSV
            pd.DataFrame([new_record]).to_csv(
                self.data_file, 
                mode='a', 
                header=False, 
                index=False
            )

            self.status_var.set(f"Defect recorded at {new_record['Timestamp']}")
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save defect: {str(e)}")

    def clear_form(self):
        """Reset form fields"""
        self.model_var.set('')
        self.shift_var.set('')
        self.category_var.set('')
        self.defect_var.set('')
        self.count_spinbox.set(1)
        self.notes_text.delete("1.0", tk.END)
        self.model_dropdown.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = DefectReporter(root)
    root.mainloop()