import math
import tkinter as tk
from tkinter import ttk, messagebox

# Define the K-factor chart based on the provided image
# Key: material_category (normalized), Value: dictionary of K-factors by IR/T ratio
K_FACTOR_CHART = {
    "soft/aluminium": {
        "0-T": 0.33,
        "T-3T": 0.40,
        ">3T": 0.50
    },
    "medium/steel": {
        "0-T": 0.38,
        "T-3T": 0.43,
        ">3T": 0.50
    },
    "hard/stainless steel": {
        "0-T": 0.40,
        "T-3T": 0.45,
        ">3T": 0.50
    }
}

def get_k_factor_from_chart(material_type, material_thickness, internal_radius):
    """
    Determines the K-factor based on material type, thickness, and internal radius
    using the provided K-factor chart.

    Args:
        material_type (str): The type of material (e.g., "Mild Steel", "Aluminum").
        material_thickness (float): The material thickness (T).
        internal_radius (float): The internal bend radius (IR).

    Returns:
        float: The determined K-factor, or None if it cannot be found.
    """
    if not (isinstance(material_thickness, (int, float)) and material_thickness > 0 and
            isinstance(internal_radius, (int, float)) and internal_radius >= 0):
        # print("Error: Invalid material thickness or internal radius for K-factor lookup.") # Changed for GUI
        return None

    ir_ratio = internal_radius / material_thickness
    material_category = ""

    # Normalize material type to match chart categories
    lower_case_material_type = material_type.lower()
    if "aluminum" in lower_case_material_type or "aluminium" in lower_case_material_type or "soft" in lower_case_material_type:
        material_category = "soft/aluminium"
    elif "stainless steel" in lower_case_material_type or "hard" in lower_case_material_type:
        material_category = "hard/stainless steel"
    elif "steel" in lower_case_material_type or "medium" in lower_case_material_type or "mild steel" in lower_case_material_type or "cold-rolled steel" in lower_case_material_type:
        material_category = "medium/steel"
    else:
        # print(f"Warning: Material type '{material_type}' not directly recognized in K-factor chart.") # Changed for GUI
        return None

    if material_category not in K_FACTOR_CHART:
        return None

    k_factor = None
    if 0 <= ir_ratio < 1:  # 0 - T
        k_factor = K_FACTOR_CHART[material_category]["0-T"]
    elif 1 <= ir_ratio < 3:  # T - 3T
        k_factor = K_FACTOR_CHART[material_category]["T-3T"]
    elif ir_ratio >= 3:  # > 3T
        k_factor = K_FACTOR_CHART[material_category][">3T"]

    return k_factor

def calculate_amada_ir(material_type, die_opening):
    """
    Estimates the Internal Radius (IR) based on Die Opening (DO) and Material Type
    using common Amada press brake guidelines for air bending.

    Args:
        material_type (str): The type of material.
        die_opening (float): The V-die opening width.

    Returns:
        float: The estimated Internal Radius.
    """
    if not (isinstance(die_opening, (int, float)) and die_opening > 0):
        # print("Error: Invalid Die Opening for Amada IR calculation.") # Changed for GUI
        return None

    lower_case_material_type = material_type.lower()
    percentage = 0.16  # Default for Mild Steel (median of 15-17%)

    if "stainless steel" in lower_case_material_type:
        percentage = 0.21  # Median of 20-22%
    elif "aluminum" in lower_case_material_type or "aluminium" in lower_case_material_type:
        percentage = 0.11  # Median of 10-12%
    elif "mild steel" in lower_case_material_type or "cold-rolled steel" in lower_case_material_type:
        percentage = 0.16  # Median of 15-17%

    calculated_ir = die_opening * percentage
    return calculated_ir

def calculate_bend_deduction(material_thickness, internal_radius, k_factor, bend_angle_degrees, leg_length1=None, leg_length2=None):
    """
    Calculates Bend Allowance (BA), Outside Setback (OSSB), Bend Deduction (BD),
    and optionally Flat Length.

    Args:
        material_thickness (float): Material Thickness (T).
        internal_radius (float): Internal Radius (IR).
        k_factor (float): K-Factor (K).
        bend_angle_degrees (float): Bend Angle in Degrees.
        leg_length1 (float, optional): Length of the first leg. Defaults to None.
        leg_length2 (float, optional): Length of the second leg. Defaults to None.

    Returns:
        dict: A dictionary containing 'BA', 'OSSB', 'BD', and 'Flat Length' (if calculated).
              Returns None if inputs are invalid.
    """
    # Input validation
    if not (isinstance(material_thickness, (int, float)) and material_thickness > 0):
        return "Error: Material Thickness (T) must be a positive number."
    if not (isinstance(internal_radius, (int, float)) and internal_radius >= 0):
        return "Error: Internal Radius (IR) must be a non-negative number."
    if not (isinstance(k_factor, (int, float)) and 0 <= k_factor <= 1):
        return "Error: K-Factor (K) must be between 0 and 1."
    if not (isinstance(bend_angle_degrees, (int, float)) and 0 < bend_angle_degrees <= 180):
        return "Error: Bend Angle (Degrees) must be between 0 and 180."

    bend_angle_radians = math.radians(bend_angle_degrees)

    # Calculate Bend Allowance (BA)
    # Formula: BA = (PI * (IR + K * T) * Bend Angle) / 180
    ba = (math.pi * (internal_radius + k_factor * material_thickness) * bend_angle_degrees) / 180

    # Calculate Outside Setback (OSSB)
    # Formula: OSSB = (IR + T) * tan(Bend Angle / 2)
    ossb = (internal_radius + material_thickness) * math.tan(bend_angle_radians / 2)

    # Calculate Bend Deduction (BD)
    # Formula: BD = 2 * OSSB - BA
    bd = (2 * ossb) - ba

    results = {
        "BA": ba,
        "OSSB": ossb,
        "BD": bd
    }

    # Calculate Flat Length if leg lengths are provided
    if (isinstance(leg_length1, (int, float)) and leg_length1 > 0 and
        isinstance(leg_length2, (int, float)) and leg_length2 > 0):
        flat_length = leg_length1 + leg_length2 - bd
        results["Flat Length"] = flat_length

    return results

class BendDeductionApp:
    def __init__(self, master):
        self.master = master
        master.title("Bend Deduction Calculator for Amada")
        master.geometry("700x600") # Set a default window size
        master.resizable(True, True) # Allow resizing

        # Configure grid for responsiveness
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(0, weight=0) # Title row
        master.grid_rowconfigure(1, weight=1) # Main content row
        master.grid_rowconfigure(2, weight=0) # Button row
        master.grid_rowconfigure(3, weight=0) # Results row

        # --- Frames for layout ---
        self.main_frame = ttk.Frame(master, padding="15")
        self.main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.material_params_frame = ttk.LabelFrame(self.main_frame, text="Material & Bend Parameters", padding="10")
        self.material_params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.material_params_frame.grid_columnconfigure(1, weight=1)

        self.tooling_lengths_frame = ttk.LabelFrame(self.main_frame, text="Tooling & Leg Lengths (Optional)", padding="10")
        self.tooling_lengths_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.tooling_lengths_frame.grid_columnconfigure(1, weight=1)

        self.results_frame = ttk.LabelFrame(master, text="Calculation Results", padding="15")
        self.results_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="ew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, weight=1)

        # --- Variables ---
        self.material_thickness_var = tk.DoubleVar(value=1.5)
        self.internal_radius_var = tk.DoubleVar(value=1.5)
        self.k_factor_var = tk.DoubleVar(value=0.446)
        self.bend_angle_var = tk.DoubleVar(value=90.0)
        self.material_type_var = tk.StringVar(value="Mild Steel")
        self.punch_radius_var = tk.DoubleVar(value=1.5)
        self.die_opening_var = tk.DoubleVar(value=12.0)
        self.leg_length1_var = tk.DoubleVar()
        self.leg_length2_var = tk.DoubleVar()
        self.ir_source_var = tk.StringVar(value="manual")

        # Result variables
        self.ba_result_var = tk.StringVar()
        self.ossb_result_var = tk.StringVar()
        self.bd_result_var = tk.StringVar()
        self.flat_length_result_var = tk.StringVar()

        # --- Widgets for Material & Bend Parameters ---
        self.create_input_row(self.material_params_frame, "Material Thickness (T):", self.material_thickness_var, row=0, info_term="Material Thickness")
        
        ttk.Label(self.material_params_frame, text="Internal Radius (IR) Source:").grid(row=1, column=0, sticky="w", pady=2)
        self.ir_source_combobox = ttk.Combobox(self.material_params_frame, textvariable=self.ir_source_var,
                                               values=["manual", "amada-auto"], state="readonly")
        self.ir_source_combobox.grid(row=1, column=1, sticky="ew", pady=2)
        self.ir_source_combobox.bind("<<ComboboxSelected>>", self.update_ir_input_state)

        self.internal_radius_label = ttk.Label(self.material_params_frame, text="Internal Radius (IR):")
        self.internal_radius_label.grid(row=2, column=0, sticky="w", pady=2)
        self.internal_radius_entry = ttk.Entry(self.material_params_frame, textvariable=self.internal_radius_var)
        self.internal_radius_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.ir_hint_label = ttk.Label(self.material_params_frame, text="This is the radius *after* bending, often approximated by the punch radius.", font=('Inter', 8))
        self.ir_hint_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        
        self.create_input_row(self.material_params_frame, "Material Type:", self.material_type_var, row=4)
        self.suggest_k_factor_btn = ttk.Button(self.material_params_frame, text="Suggest K-Factor (from chart)", command=self.update_k_factor_from_chart)
        self.suggest_k_factor_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.create_input_row(self.material_params_frame, "K-Factor (K):", self.k_factor_var, row=6, info_term="K-Factor", readonly=True)
        self.k_factor_hint_label = ttk.Label(self.material_params_frame, text="This value is automatically set from the K-Factor chart.", font=('Inter', 8))
        self.k_factor_hint_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=5)

        self.create_input_row(self.material_params_frame, "Bend Angle (Degrees):", self.bend_angle_var, row=8, info_term="Bend Angle")

        # --- Widgets for Tooling & Leg Lengths ---
        self.punch_radius_label = ttk.Label(self.tooling_lengths_frame, text="Punch Radius (PR):")
        self.punch_radius_label.grid(row=0, column=0, sticky="w", pady=2)
        self.punch_radius_entry = ttk.Entry(self.tooling_lengths_frame, textvariable=self.punch_radius_var)
        self.punch_radius_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.tooling_lengths_frame, text="Used to approximate Internal Radius (IR) when IR Source is Manual.", font=('Inter', 8)).grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
        self.punch_radius_var.trace_add("write", self.on_punch_radius_change)

        self.die_opening_label = ttk.Label(self.tooling_lengths_frame, text="Die Opening (DO):")
        self.die_opening_label.grid(row=2, column=0, sticky="w", pady=2)
        self.die_opening_entry = ttk.Entry(self.tooling_lengths_frame, textvariable=self.die_opening_var)
        self.die_opening_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.die_opening_hint_label = ttk.Label(self.tooling_lengths_frame, text="The V-die opening width. Typically 6-8 times material thickness.", font=('Inter', 8))
        self.die_opening_hint_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        self.die_opening_var.trace_add("write", self.on_die_opening_change)

        self.create_input_row(self.tooling_lengths_frame, "Leg Length 1 (L1):", self.leg_length1_var, row=4)
        self.create_input_row(self.tooling_lengths_frame, "Leg Length 2 (L2):", self.leg_length2_var, row=5)

        # --- Calculate Button ---
        self.calculate_button = ttk.Button(master, text="Calculate Bend Deduction", command=self.calculate_gui)
        self.calculate_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew", padx=15)

        # --- Results Display ---
        ttk.Label(self.results_frame, text="Bend Allowance (BA):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(self.results_frame, textvariable=self.ba_result_var, font=('Inter', 10, 'bold')).grid(row=0, column=1, sticky="e", pady=2)

        ttk.Label(self.results_frame, text="Outside Setback (OSSB):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self.results_frame, textvariable=self.ossb_result_var, font=('Inter', 10, 'bold')).grid(row=1, column=1, sticky="e", pady=2)

        ttk.Label(self.results_frame, text="Bend Deduction (BD):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self.results_frame, textvariable=self.bd_result_var, font=('Inter', 10, 'bold')).grid(row=2, column=1, sticky="e", pady=2)

        self.flat_length_label = ttk.Label(self.results_frame, text="Flat Length:")
        self.flat_length_label.grid(row=3, column=0, sticky="w", pady=2)
        self.flat_length_result_display = ttk.Label(self.results_frame, textvariable=self.flat_length_result_var, font=('Inter', 10, 'bold'))
        self.flat_length_result_display.grid(row=3, column=1, sticky="e", pady=2)

        # Initial state setup
        self.update_ir_input_state()
        self.update_k_factor_from_chart()
        self.calculate_gui() # Perform initial calculation on load

        # Trace changes to inputs to trigger K-factor update and recalculation
        self.material_thickness_var.trace_add("write", self.on_input_change)
        self.internal_radius_var.trace_add("write", self.on_input_change)
        self.material_type_var.trace_add("write", self.on_input_change)
        self.bend_angle_var.trace_add("write", self.on_input_change)

    def create_input_row(self, parent_frame, label_text, tk_var, row, info_term=None, readonly=False):
        """Helper function to create a label and entry field."""
        label_frame = ttk.Frame(parent_frame)
        label_frame.grid(row=row, column=0, sticky="w", pady=2)
        ttk.Label(label_frame, text=label_text).pack(side="left")
        if info_term:
            info_button = ttk.Button(label_frame, text="ⓘ", width=2, command=lambda t=info_term: self.show_info(t))
            info_button.pack(side="left", padx=5)

        entry = ttk.Entry(parent_frame, textvariable=tk_var)
        entry.grid(row=row, column=1, sticky="ew", pady=2)
        if readonly:
            entry.config(state="readonly")
        return entry # Return the entry widget in case it needs further configuration

    def show_info(self, term):
        """Displays an information message box for a given term."""
        explanations = {
            "Material Thickness": "The thickness of the sheet metal being bent. Denoted as 'T'.",
            "Internal Radius": "The radius of the bend on the inside surface of the material after bending. Denoted as 'IR'.",
            "K-Factor": "A ratio representing the location of the neutral axis within the material's thickness during bending. It's crucial for accurate bend allowance calculations. Typically ranges from 0.33 to 0.5.",
            "Bend Angle": "The angle formed by the two legs of the bent part. For example, a right-angle bend is 90 degrees.",
            "Punch Radius": "The radius of the punch tool used in the press brake. Often approximates the internal radius of the bend.",
            "Die Opening": "The width of the V-shaped die opening. It influences the resulting internal bend radius in air bending."
        }
        messagebox.showinfo(f"Info: {term}", explanations.get(term, "Explanation not available for this term."))

    def on_input_change(self, *args):
        """Callback for variable changes to trigger K-factor update and recalculation."""
        self.update_k_factor_from_chart()
        self.calculate_gui()

    def on_punch_radius_change(self, *args):
        """Callback for punch radius change to auto-fill IR if source is manual."""
        if self.ir_source_var.get() == 'manual':
            try:
                pr_value = self.punch_radius_var.get()
                if pr_value is not None and pr_value != 0.0: # Check for non-zero or actual value
                    self.internal_radius_var.set(pr_value)
                else:
                    # If punch radius is cleared or 0, don't clear IR unless explicitly desired
                    pass
            except tk.TclError:
                # Handle cases where input is not a valid float (e.g., empty string)
                pass
        self.update_k_factor_from_chart() # Update K-factor after IR might have changed
        self.calculate_gui()

    def on_die_opening_change(self, *args):
        """Callback for die opening change to auto-calculate IR if source is amada-auto."""
        if self.ir_source_var.get() == 'amada-auto':
            self.calculate_amada_ir_gui()
        self.update_k_factor_from_chart() # Update K-factor after IR might have changed
        self.calculate_gui()

    def update_ir_input_state(self, *args):
        """Updates the state (read-only/editable) of the IR input and visibility of PR/DO."""
        selected_source = self.ir_source_var.get()
        if selected_source == 'manual':
            self.internal_radius_entry.config(state="normal")
            self.internal_radius_entry.config(bg="white") # Reset background color
            self.ir_hint_label.config(text='This is the radius *after* bending, often approximated by the punch radius.')
            self.punch_radius_label.grid() # Show
            self.punch_radius_entry.grid() # Show
            self.die_opening_label.grid() # Show
            self.die_opening_entry.grid() # Show
            self.die_opening_hint_label.config(text='The V-die opening width. Typically 6-8 times material thickness.')
        else: # amada-auto
            self.internal_radius_entry.config(state="readonly")
            self.internal_radius_entry.config(bg="lightgray") # Indicate read-only
            self.ir_hint_label.config(text='Internal Radius is auto-calculated based on Die Opening and Material Type (Amada guideline).')
            self.punch_radius_label.grid_remove() # Hide
            self.punch_radius_entry.grid_remove() # Hide
            self.die_opening_label.grid() # Ensure visible
            self.die_opening_entry.grid() # Ensure visible
            self.die_opening_hint_label.config(text='Die Opening is required for Amada Auto-Calculate of Internal Radius.')
            self.calculate_amada_ir_gui() # Recalculate IR when mode changes
        self.update_k_factor_from_chart() # Always update K-Factor after IR source change
        self.calculate_gui() # Recalculate main results

    def calculate_amada_ir_gui(self):
        """Calculates and sets Internal Radius based on Amada guidelines for GUI."""
        try:
            T = self.material_thickness_var.get()
            DO = self.die_opening_var.get()
            material_type = self.material_type_var.get()

            if DO <= 0:
                self.internal_radius_var.set(0.0) # Set to 0 or clear if invalid
                messagebox.showerror("Input Error", "Please enter a valid Die Opening (DO) greater than 0 for Amada Auto-Calculate.")
                return

            calculated_ir = calculate_amada_ir(material_type, DO)
            if calculated_ir is not None:
                self.internal_radius_var.set(round(calculated_ir, 4))
                self.ir_hint_label.config(text=f'IR auto-calculated as {round(calculated_ir/DO*100)}% of DO ({DO}) for {material_type} (IR = {calculated_ir:.4f}).')
            else:
                self.internal_radius_var.set(0.0)
                messagebox.showerror("Calculation Error", "Could not auto-calculate Internal Radius. Check Die Opening and Material Type.")
        except tk.TclError:
            self.internal_radius_var.set(0.0) # Set to 0 or clear if input is invalid
            # messagebox.showerror("Input Error", "Invalid numerical input for Die Opening or Material Thickness.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during Amada IR calculation: {e}")

    def update_k_factor_from_chart(self, *args):
        """Updates the K-Factor based on chart lookup for GUI."""
        try:
            T = self.material_thickness_var.get()
            IR = self.internal_radius_var.get()
            material_type = self.material_type_var.get()

            suggested_k = get_k_factor_from_chart(material_type, T, IR)

            if suggested_k is not None:
                self.k_factor_var.set(round(suggested_k, 3))
            else:
                # Fallback if chart lookup fails, keep current K-factor or set a default
                # messagebox.showwarning("K-Factor Warning", "Could not determine K-Factor from chart for the given inputs. Using default 0.446.")
                if self.k_factor_var.get() == 0.0: # Only set default if it's currently 0 or not set
                    self.k_factor_var.set(0.446)
        except tk.TclError:
            # Handle cases where inputs are not valid numbers yet
            pass
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during K-Factor update: {e}")

    def calculate_gui(self):
        """Performs the bend deduction calculation and updates GUI results."""
        try:
            T = self.material_thickness_var.get()
            IR = self.internal_radius_var.get()
            K = self.k_factor_var.get()
            bend_angle_degrees = self.bend_angle_var.get()
            
            # Get leg lengths, handling empty inputs as None
            L1 = None
            try:
                l1_val = self.leg_length1_var.get()
                if l1_val != 0.0: # Tkinter DoubleVar defaults to 0.0 for empty
                    L1 = l1_val
            except tk.TclError:
                pass # L1 remains None if input is not a valid float

            L2 = None
            try:
                l2_val = self.leg_length2_var.get()
                if l2_val != 0.0:
                    L2 = l2_val
            except tk.TclError:
                pass # L2 remains None

            results = calculate_bend_deduction(T, IR, K, bend_angle_degrees, L1, L2)

            if isinstance(results, str): # Check if an error message was returned
                messagebox.showerror("Calculation Error", results)
                self.clear_results()
            elif results:
                self.ba_result_var.set(f"{results['BA']:.4f}")
                self.ossb_result_var.set(f"{results['OSSB']:.4f}")
                self.bd_result_var.set(f"{results['BD']:.4f}")
                if "Flat Length" in results:
                    self.flat_length_result_var.set(f"{results['Flat Length']:.4f}")
                    self.flat_length_label.grid() # Show label
                    self.flat_length_result_display.grid() # Show result
                else:
                    self.flat_length_result_var.set("")
                    self.flat_length_label.grid_remove() # Hide label
                    self.flat_length_result_display.grid_remove() # Hide result
            else:
                self.clear_results()
                messagebox.showerror("Calculation Error", "Calculation failed. Please check your inputs.")

        except tk.TclError:
            messagebox.showerror("Input Error", "Please ensure all numerical fields have valid numbers.")
            self.clear_results()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.clear_results()

    def clear_results(self):
        """Clears all result display variables."""
        self.ba_result_var.set("")
        self.ossb_result_var.set("")
        self.bd_result_var.set("")
        self.flat_length_result_var.set("")
        self.flat_length_label.grid_remove()
        self.flat_length_result_display.grid_remove()


if __name__ == "__main__":
    root = tk.Tk()
    app = BendDeductionApp(root)
    root.mainloop()
