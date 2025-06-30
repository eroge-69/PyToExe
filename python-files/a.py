
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import pandas as pd

results = []

def unit_to_multiplier(unit):
    unit_multipliers = {
        'V': 1, 'kV': 1000,
        'Ω': 1, 'kΩ': 1000, 'MΩ': 1e6,
        'A': 1, 'mA': 0.001,
        'Hz': 1, 'kHz': 1000,
        'μF': 1, 'nF': 0.001
    }
    return unit_multipliers[unit]

def calculate_capacitive():
    try:
        V_rms = float(entry_vrms.get()) * unit_to_multiplier(vrms_unit.get())
        V_tol = float(entry_vrms_tol.get()) / 100
        freq = float(entry_freq.get()) * unit_to_multiplier(freq_unit.get())
        freq_tol = float(entry_freq_tol.get()) / 100
        capacitance = float(entry_cap.get()) * unit_to_multiplier(cap_unit.get())
        cap_tol = float(entry_cap_tol.get()) / 100
        R_s = float(entry_rs.get()) * unit_to_multiplier(rs_unit.get())
        R_s_tol = float(entry_rs_tol.get()) / 100
        R_b = float(entry_rb.get()) * unit_to_multiplier(rb_unit.get())
        R_b_tol = float(entry_rb_tol.get()) / 100

        V_peak = V_rms * math.sqrt(2)
        X_C = 1 / (2 * math.pi * freq * capacitance * 1e-6)
        Y_b = 1 / R_b
        Y_C = 1 / (complex(0, X_C))
        Y_total = Y_b + Y_C
        Z_parallel = 1 / abs(Y_total)
        Z_total = math.sqrt(R_s ** 2 + Z_parallel ** 2)
        I_peak = V_peak / Z_total
        I_avg = (2 * I_peak) / math.pi

        result_capacitive.set(
            f"Peak Voltage: {V_peak:.2f} V\n"
            f"Capacitive Reactance: {X_C:.2f} Ω\n"
            f"Total Impedance: {Z_total:.2f} Ω\n"
            f"Peak Current: {I_peak:.4f} A\n"
            f"Average Current: {I_avg:.4f} A"
        )

        results.append({
            'Type': 'Capacitive Dropper',
            'V_peak (V)': V_peak,
            'X_C (Ω)': X_C,
            'Z_total (Ω)': Z_total,
            'I_peak (A)': I_peak,
            'I_avg (A)': I_avg
        })

    except Exception as e:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

def calculate_resistive():
    try:
        V_rms_res = float(entry_vrms_res.get()) * unit_to_multiplier(vrms_res_unit.get())
        I_target = float(entry_current.get()) * unit_to_multiplier(current_unit.get())
        num_resistors = int(entry_num_resistors.get())
        thermal_resistance = float(entry_thermal_res.get())
        tolerance = float(entry_tolerance.get()) / 100

        V_peak_res = V_rms_res * math.sqrt(2)
        R_total = V_peak_res / I_target
        R_each = R_total / num_resistors
        P_total = I_target ** 2 * R_total
        P_each = P_total / num_resistors
        temp_rise = P_each * thermal_resistance
        I_avg = (2 * I_target) / math.pi

        R_min = R_total * (1 - tolerance)
        R_max = R_total * (1 + tolerance)
        I_peak_max = V_peak_res / R_min
        I_peak_min = V_peak_res / R_max

        result_resistive.set(
            f"Peak Voltage: {V_peak_res:.2f} V\n"
            f"Total Resistance: {R_total:.2f} Ω\n"
            f"Resistance per Resistor: {R_each:.2f} Ω\n"
            f"Power per Resistor: {P_each:.2f} W\n"
            f"Temperature Rise per Resistor: {temp_rise:.2f} °C\n"
            f"Average Current: {I_avg:.4f} A\n"
            f"Max Peak Current: {I_peak_max:.4f} A\n"
            f"Min Peak Current: {I_peak_min:.4f} A"
        )

        results.append({
            'Type': 'Resistive Dropper',
            'V_peak (V)': V_peak_res,
            'R_total (Ω)': R_total,
            'R_each (Ω)': R_each,
            'P_each (W)': P_each,
            'Temp Rise (°C)': temp_rise,
            'I_avg (A)': I_avg,
            'I_peak_max (A)': I_peak_max,
            'I_peak_min (A)': I_peak_min
        })

    except Exception as e:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

def clear_capacitive_inputs():
    for entry in [
        entry_vrms, entry_vrms_tol, entry_freq, entry_freq_tol,
        entry_cap, entry_cap_tol, entry_rs, entry_rs_tol,
        entry_rb, entry_rb_tol
    ]:
        entry.delete(0, tk.END)
    result_capacitive.set("")

def clear_resistive_inputs():
    for entry in [
        entry_vrms_res, entry_current, entry_num_resistors,
        entry_thermal_res, entry_tolerance
    ]:
        entry.delete(0, tk.END)
    result_resistive.set("")

def export_to_excel():
    if not results:
        messagebox.showwarning("Export Error", "No results to export.")
        return
    df = pd.DataFrame(results)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Export Complete", f"Results exported to {file_path}")

# GUI setup
root = tk.Tk()
root.title("Complete Capacitor and Resistor Dropper Calculator")

tab_control = ttk.Notebook(root)

# Capacitor Dropper Tab
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Capacitor Dropper')

tk.Label(tab1, text="Input RMS Voltage:").grid(row=0, column=0)
entry_vrms = tk.Entry(tab1)
entry_vrms.grid(row=0, column=1)
vrms_unit = ttk.Combobox(tab1, values=['V', 'kV'], width=5)
vrms_unit.current(0)
vrms_unit.grid(row=0, column=2)
tk.Label(tab1, text="Tolerance (%)").grid(row=0, column=3)
entry_vrms_tol = tk.Entry(tab1, width=5)
entry_vrms_tol.grid(row=0, column=4)

tk.Label(tab1, text="Frequency:").grid(row=1, column=0)
entry_freq = tk.Entry(tab1)
entry_freq.grid(row=1, column=1)
freq_unit = ttk.Combobox(tab1, values=['Hz', 'kHz'], width=5)
freq_unit.current(0)
freq_unit.grid(row=1, column=2)
tk.Label(tab1, text="Tolerance (%)").grid(row=1, column=3)
entry_freq_tol = tk.Entry(tab1, width=5)
entry_freq_tol.grid(row=1, column=4)

tk.Label(tab1, text="Capacitance:").grid(row=2, column=0)
entry_cap = tk.Entry(tab1)
entry_cap.grid(row=2, column=1)
cap_unit = ttk.Combobox(tab1, values=['μF', 'nF'], width=5)
cap_unit.current(0)
cap_unit.grid(row=2, column=2)
tk.Label(tab1, text="Tolerance (%)").grid(row=2, column=3)
entry_cap_tol = tk.Entry(tab1, width=5)
entry_cap_tol.grid(row=2, column=4)

tk.Label(tab1, text="Series Resistance:").grid(row=3, column=0)
entry_rs = tk.Entry(tab1)
entry_rs.grid(row=3, column=1)
rs_unit = ttk.Combobox(tab1, values=['Ω', 'kΩ', 'MΩ'], width=5)
rs_unit.current(0)
rs_unit.grid(row=3, column=2)
tk.Label(tab1, text="Tolerance (%)").grid(row=3, column=3)
entry_rs_tol = tk.Entry(tab1, width=5)
entry_rs_tol.grid(row=3, column=4)

tk.Label(tab1, text="Bleeder Resistance:").grid(row=4, column=0)
entry_rb = tk.Entry(tab1)
entry_rb.grid(row=4, column=1)
rb_unit = ttk.Combobox(tab1, values=['Ω', 'kΩ', 'MΩ'], width=5)
rb_unit.current(0)
rb_unit.grid(row=4, column=2)
tk.Label(tab1, text="Tolerance (%)").grid(row=4, column=3)
entry_rb_tol = tk.Entry(tab1, width=5)
entry_rb_tol.grid(row=4, column=4)

calc_button1 = tk.Button(tab1, text="Calculate", command=calculate_capacitive)
calc_button1.grid(row=5, column=0, columnspan=2, pady=10)

clear_button1 = tk.Button(tab1, text="Clear", command=clear_capacitive_inputs)
clear_button1.grid(row=5, column=2, columnspan=2, pady=10)

result_capacitive = tk.StringVar()
tk.Label(tab1, textvariable=result_capacitive, justify='left').grid(row=6, column=0, columnspan=5)

# Resistive Dropper Tab
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text='Resistor Dropper')

tk.Label(tab2, text="Input RMS Voltage:").grid(row=0, column=0)
entry_vrms_res = tk.Entry(tab2)
entry_vrms_res.grid(row=0, column=1)
vrms_res_unit = ttk.Combobox(tab2, values=['V', 'kV'], width=5)
vrms_res_unit.current(0)
vrms_res_unit.grid(row=0, column=2)

tk.Label(tab2, text="Target Current:").grid(row=1, column=0)
entry_current = tk.Entry(tab2)
entry_current.grid(row=1, column=1)
current_unit = ttk.Combobox(tab2, values=['A', 'mA'], width=5)
current_unit.current(0)
current_unit.grid(row=1, column=2)

tk.Label(tab2, text="Number of Resistors:").grid(row=2, column=0)
entry_num_resistors = tk.Entry(tab2)
entry_num_resistors.grid(row=2, column=1)

tk.Label(tab2, text="Thermal Resistance (°C/W):").grid(row=3, column=0)
entry_thermal_res = tk.Entry(tab2)
entry_thermal_res.grid(row=3, column=1)

tk.Label(tab2, text="Tolerance (%):").grid(row=4, column=0)
entry_tolerance = tk.Entry(tab2)
entry_tolerance.grid(row=4, column=1)

calc_button2 = tk.Button(tab2, text="Calculate", command=calculate_resistive)
calc_button2.grid(row=5, column=0, columnspan=2, pady=10)

clear_button2 = tk.Button(tab2, text="Clear", command=clear_resistive_inputs)
clear_button2.grid(row=5, column=2, pady=10)

result_resistive = tk.StringVar()
tk.Label(tab2, textvariable=result_resistive, justify='left').grid(row=6, column=0, columnspan=4)

tab_control.pack(expand=1, fill='both')

export_button = tk.Button(root, text="Export to Excel", command=export_to_excel)
export_button.pack(pady=10)

root.mainloop()
