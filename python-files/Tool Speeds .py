import tkinter as tk
from tkinter import ttk

def calculate():
    try:
        diameter = float(diameter_entry.get())
        flutes = int(flutes_entry.get())
        rpm = int(rpm_entry.get())
        material = material_var.get()
        tool_type = tool_type_var.get()

        chip_loads = {
            "Wood": 0.05,
            "Plywood": 0.045,
            "MDF": 0.04,
            "Acrylic": 0.025,
            "Aluminum": 0.015
        }
        chip_load = chip_loads.get(material, 0.05)

        feed_rate = flutes * chip_load * rpm
        plunge_rate = feed_rate * 0.12
        stepdown = diameter * 0.35
        stepover = diameter * 0.4

        result = (
            f"Tool Type: {tool_type}\n"
            f"Feed Rate: {int(feed_rate)} mm/min\n"
            f"Plunge Rate: {int(plunge_rate)} mm/min\n"
            f"Stepdown: {stepdown:.2f} mm/pass\n"
            f"Stepover: {stepover:.2f} mm (roughing)\n"
            f"Chip Load: {chip_load} mm/tooth"
        )
        result_var.set(result)
    except Exception as e:
        result_var.set(f"Error: {e}")

root = tk.Tk()
root.title("CNC Feed & Plunge Rate Calculator")
root.geometry('400x650')

# Use ttk style for modern look
style = ttk.Style(root)
style.theme_use('vista')

# Fonts
font_label = ('Segoe UI', 14)
font_entry = ('Segoe UI', 14)
font_result = ('Segoe UI', 16, 'bold')

# Tool type at the top
label_tool_type = ttk.Label(root, text="Tool Type:", font=font_label)
label_tool_type.grid(row=0, column=0, sticky='e', padx=20, pady=14)
tool_type_var = tk.StringVar()
tool_type_combo = ttk.Combobox(root, textvariable=tool_type_var, state="readonly", font=font_entry, width=12)
tool_type_combo['values'] = ("Endmill", "Ball Nose", "V-Bit", "Slot Cutter", "Drill Bit")
tool_type_combo.current(0)
tool_type_combo.grid(row=0, column=1, padx=20, pady=14)

label_diameter = ttk.Label(root, text="Tool Diameter (mm):", font=font_label)
label_diameter.grid(row=1, column=0, sticky='e', padx=20, pady=14)
diameter_entry = ttk.Entry(root, font=font_entry, width=14)
diameter_entry.insert(0, "2.5")
diameter_entry.grid(row=1, column=1, padx=20, pady=14)

label_flutes = ttk.Label(root, text="Number of Flutes:", font=font_label)
label_flutes.grid(row=2, column=0, sticky='e', padx=20, pady=14)
flutes_entry = ttk.Entry(root, font=font_entry, width=14)
flutes_entry.insert(0, "2")
flutes_entry.grid(row=2, column=1, padx=20, pady=14)

label_rpm = ttk.Label(root, text="Spindle Speed (rpm):", font=font_label)
label_rpm.grid(row=3, column=0, sticky='e', padx=20, pady=14)
rpm_entry = ttk.Entry(root, font=font_entry, width=14)
rpm_entry.insert(0, "18000")
rpm_entry.grid(row=3, column=1, padx=20, pady=14)

label_material = ttk.Label(root, text="Material:", font=font_label)
label_material.grid(row=4, column=0, sticky='e', padx=20, pady=14)
material_var = tk.StringVar()
material_combo = ttk.Combobox(root, textvariable=material_var, state="readonly", font=font_entry, width=12)
material_combo['values'] = ("Wood", "Plywood", "MDF", "Acrylic", "Aluminum")
material_combo.current(0)
material_combo.grid(row=4, column=1, padx=20, pady=14)

# Calculate button with custom style
style.configure('TButton', font=('Segoe UI', 14, 'bold'), padding=10)
calc_button = ttk.Button(root, text="Calculate", command=calculate, style='TButton')
calc_button.grid(row=5, column=0, columnspan=2, pady=24, padx=20, sticky='ew')

# Result label with border and background
result_var = tk.StringVar()
result_label = ttk.Label(
    root, textvariable=result_var, font=font_result,
    foreground="#004080", justify="left",
    background="#e6f0ff", borderwidth=2, relief="groove"
)
result_label.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

root.mainloop()
