import math
import tkinter as tk
from tkinter import ttk, messagebox

# --- Conversion Factors (mg/dL <-> mmol/L) ---
TG_CONVERSION_FACTOR = 88.57
LIPID_CONVERSION_FACTOR = 38.67 # For TC, HDL, LDL

# --- Calculation Functions (Unchanged) ---

def calculate_ldl_friedewald(tc, hdl, tg, unit):
    """Calculates LDL-C using the Friedewald formula."""
    if unit.lower() == 'mg/dl':
        if tg >= 400:
            raise ValueError("TG must be < 400 mg/dL")
        ldl = tc - hdl - (tg / 5)
    else: # mmol/L
        if tg >= 4.5:
            raise ValueError("TG must be < 4.5 mmol/L")
        ldl = tc - hdl - (tg / 2.2)
    return max(ldl, 0)

def calculate_ldl_sampson(tc, hdl, tg, unit):
    """Calculates LDL-C using the NIH (Sampson) Equation 2."""
    if unit.lower() == 'mmol/l':
        tc_mgdl, hdl_mgdl, tg_mgdl = tc * LIPID_CONVERSION_FACTOR, hdl * LIPID_CONVERSION_FACTOR, tg * TG_CONVERSION_FACTOR
    else:
        tc_mgdl, hdl_mgdl, tg_mgdl = tc, hdl, tg
        
    if tg_mgdl >= 800:
        raise ValueError("Not validated for TG >= 800 mg/dL")

    non_hdl_c = tc_mgdl - hdl_mgdl
    
    ldl_mgdl = (tc_mgdl / 0.948) - (hdl_mgdl / 0.971) - \
               ((tg_mgdl / 8.56) + (tg_mgdl * non_hdl_c) / 2140 - (tg_mgdl**2) / 16100) - 9.44
               
    if unit.lower() == 'mmol/l':
        return max(ldl_mgdl / LIPID_CONVERSION_FACTOR, 0)
    else:
        return max(ldl_mgdl, 0)

def calculate_aip(tg, hdl, unit):
    """Calculates the Atherogenic Index of Plasma (AIP)."""
    if unit.lower() == 'mg/dl':
        tg_mmol, hdl_mmol = tg / TG_CONVERSION_FACTOR, hdl / LIPID_CONVERSION_FACTOR
    else:
        tg_mmol, hdl_mmol = tg, hdl

    if hdl_mmol <= 0 or tg_mmol <= 0:
        raise ValueError("HDL and TG must be positive for AIP calculation.")
        
    return math.log10(tg_mmol / hdl_mmol)

# --- Interpretation Functions (Unchanged) ---

def interpret_ldl(ldl_value, unit):
    ldl_mgdl = ldl_value if unit.lower() == 'mg/dl' else ldl_value * LIPID_CONVERSION_FACTOR
    if ldl_mgdl < 100: return ("Optimal", "green")
    elif 100 <= ldl_mgdl < 130: return ("Near Optimal", "#8FBC8F")
    elif 130 <= ldl_mgdl < 160: return ("Borderline High", "orange")
    elif 160 <= ldl_mgdl < 190: return ("High", "#FF6347")
    else: return ("Very High", "#B22222")

def interpret_aip(aip_value):
    if aip_value < 0.11: return ("Low Risk", "green")
    elif 0.11 <= aip_value <= 0.24: return ("Intermediate Risk", "orange")
    else: return ("High Risk", "#B22222")

# --- GUI Application Class ---

class AdvancedLipidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Lipid Calculator")
        self.geometry("480x620")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.configure('TLabel', font=('Helvetica', 11))
        style.configure('TButton', font=('Helvetica', 11, 'bold'))
        style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'))
        style.configure('Note.TLabel', foreground='blue', font=('Helvetica', 9, 'italic'))

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)

        self._create_input_widgets(main_frame)
        calculate_button = ttk.Button(main_frame, text="Calculate All Indices", command=self.perform_calculations)
        calculate_button.pack(pady=20)
        self._create_results_widgets(main_frame)

    def _create_input_widgets(self, parent):
        """ This method now contains the FIX for the KeyError. """
        frame = ttk.LabelFrame(parent, text="Enter Lab Values", padding="15")
        frame.pack(fill="x", pady=(0, 10))
        labels = ["Total Cholesterol:", "HDL Cholesterol:", "Triglycerides:"]
        self.entries = {}
        for i, text in enumerate(labels):
            ttk.Label(frame, text=text).grid(row=i, column=0, sticky="w", pady=4)
            entry = ttk.Entry(frame, width=15)
            entry.grid(row=i, column=1, sticky="e", pady=4)
            
            # --- THIS IS THE CORRECTED LINE ---
            # It cleans the label text to create a consistent key.
            key = text.replace(':', '').split()[0].lower()
            self.entries[key] = entry
        
        ttk.Label(frame, text="Units:").grid(row=3, column=0, sticky="w", pady=4)
        self.unit_var = tk.StringVar(value='mg/dL')
        self.unit_combo = ttk.Combobox(frame, textvariable=self.unit_var, values=['mg/dL', 'mmol/L'], state='readonly', width=13)
        self.unit_combo.grid(row=3, column=1, sticky="e", pady=4)
        
    def _create_results_widgets(self, parent):
        # This method is unchanged
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill="x", expand=True)
        
        ff_frame = ttk.LabelFrame(results_frame, text="LDL-C (Friedewald)", padding="10")
        ff_frame.pack(fill="x", pady=5)
        self.ff_value = ttk.Label(ff_frame, text="Value: -", font=('Helvetica', 11, 'bold'))
        self.ff_value.pack()
        self.ff_interp = ttk.Label(ff_frame, text="Level: -", font=('Helvetica', 11, 'bold'))
        self.ff_interp.pack()
        self.ff_note = ttk.Label(ff_frame, text="Note: Only valid for TG < 400 mg/dL", style='Note.TLabel')
        self.ff_note.pack()
        
        smp_frame = ttk.LabelFrame(results_frame, text="LDL-C (NIH Sampson)", padding="10")
        smp_frame.pack(fill="x", pady=5)
        self.smp_value = ttk.Label(smp_frame, text="Value: -", font=('Helvetica', 11, 'bold'))
        self.smp_value.pack()
        self.smp_interp = ttk.Label(smp_frame, text="Level: -", font=('Helvetica', 11, 'bold'))
        self.smp_interp.pack()
        self.smp_note = ttk.Label(smp_frame, text="Note: More accurate for higher TG levels", style='Note.TLabel')
        self.smp_note.pack()

        aip_frame = ttk.LabelFrame(results_frame, text="Atherogenic Index of Plasma (AIP)", padding="10")
        aip_frame.pack(fill="x", pady=5)
        self.aip_value = ttk.Label(aip_frame, text="Value: -", font=('Helvetica', 11, 'bold'))
        self.aip_value.pack()
        self.aip_risk = ttk.Label(aip_frame, text="Risk: -", font=('Helvetica', 11, 'bold'))
        self.aip_risk.pack()

    def perform_calculations(self):
        # This method uses the now-correct keys and remains robust
        self.clear_results()
        try:
            for key, entry in self.entries.items():
                if not entry.get():
                    messagebox.showerror("Input Error", f"The '{key.title()}' field cannot be empty.")
                    return
            unit = self.unit_var.get()
            tc = float(self.entries['total'].get())
            hdl = float(self.entries['hdl'].get())
            tg = float(self.entries['triglycerides'].get())
            if not all(v > 0 for v in [tc, hdl, tg]):
                messagebox.showerror("Input Error", "All lab values must be positive numbers.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers in all fields.")
            return
        
        try:
            ldl_ff = calculate_ldl_friedewald(tc, hdl, tg, unit)
            level, color = interpret_ldl(ldl_ff, unit)
            self.ff_value.config(text=f"Value: {ldl_ff:.1f} {unit}")
            self.ff_interp.config(text=f"Level: {level}", foreground=color)
        except ValueError as e:
            self.ff_value.config(text="Value: N/A")
            self.ff_interp.config(text=f"Invalid ({e})", foreground='blue')

        try:
            ldl_smp = calculate_ldl_sampson(tc, hdl, tg, unit)
            level, color = interpret_ldl(ldl_smp, unit)
            self.smp_value.config(text=f"Value: {ldl_smp:.1f} {unit}")
            self.smp_interp.config(text=f"Level: {level}", foreground=color)
        except ValueError as e:
            self.smp_value.config(text="Value: N/A")
            self.smp_interp.config(text=f"Invalid ({e})", foreground='blue')

        try:
            aip = calculate_aip(tg, hdl, unit)
            risk, color = interpret_aip(aip)
            self.aip_value.config(text=f"Value: {aip:.3f}")
            self.aip_risk.config(text=f"Risk: {risk}", foreground=color)
        except Exception as e:
            messagebox.showerror("AIP Error", f"Could not calculate AIP: {e}")

    def clear_results(self):
        """Resets all result labels to their default state."""
        self.ff_value.config(text="Value: -")
        self.ff_interp.config(text="Level: -", foreground='black')
        self.smp_value.config(text="Value: -")
        self.smp_interp.config(text="Level: -", foreground='black')
        self.aip_value.config(text="Value: -")
        self.aip_risk.config(text="Risk: -", foreground='black')

if __name__ == "__main__":
    app = AdvancedLipidApp()
    def on_closing():
        disclaimer = "This tool is for informational purposes and is not a substitute for professional medical advice. Always consult a healthcare provider for diagnosis and treatment. Do you want to exit?"
        if messagebox.askokcancel("Disclaimer & Exit", disclaimer):
            app.destroy()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
