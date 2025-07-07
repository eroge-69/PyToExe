import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

# --- Constants ---
COPPER_RESISTIVITY = 1.68e-8  # Ohm·m
ALUMINUM_RESISTIVITY = 2.82e-8

# === PMDC motor calculations ===
def calculate_motor():
    try:
        V = float(entry_voltage.get())
        P = float(entry_power.get())
        N = float(entry_speed.get())
        Ra = float(entry_resistance.get())
        eta = float(entry_efficiency.get()) / 100

        Ia = P / (V * eta)
        Eb = V - Ia * Ra
        omega = 2 * np.pi * N / 60
        Ke = Eb / omega
        Torque = P / omega

        motor_output.set(
            f"Armature Current (Ia): {Ia:.2f} A\n"
            f"Back EMF (Eb): {Eb:.2f} V\n"
            f"Angular Speed (ω): {omega:.2f} rad/s\n"
            f"Torque (T): {Torque:.2f} Nm\n"
            f"Motor Constant (Ke): {Ke:.4f} Vs/rad"
        )

        plot_torque_speed(V, Ra, Ke)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for motor parameters.")

# === Torque-Speed plot ===
def plot_torque_speed(V, Ra, Ke):
    speeds = np.linspace(0, 3000, 100)
    omega = 2 * np.pi * speeds / 60
    Eb = Ke * omega
    Ia = (V - Eb) / Ra
    torque = Ke * Ia
    torque = np.where(Ia > 0, torque, 0)

    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(speeds, torque, color='blue')
    ax.set_title('Torque vs Speed')
    ax.set_xlabel('Speed (RPM)')
    ax.set_ylabel('Torque (Nm)')
    ax.grid(True)
    canvas.draw()

# === Winding resistance calculation ===
def calculate_resistance():
    try:
        material = material_var.get()

        # Calculate resistivity
        rho = COPPER_RESISTIVITY if material == "Copper" else ALUMINUM_RESISTIVITY

        # Either manual wire length input OR calculate from coil parameters
        if var_use_calc_length.get():
            # Calculate wire length from turns and mean turn length
            turns = float(entry_turns.get())
            mean_turn_length = float(entry_turn_length.get())  # in meters
            length = turns * mean_turn_length
        else:
            # Manual input
            length = float(entry_wire_length.get())

        diameter_mm = float(entry_wire_diameter.get())
        diameter_m = diameter_mm / 1000
        area = math.pi * (diameter_m / 2) ** 2

        resistance = rho * length / area

        resistance_output.set(f"Winding Resistance: {resistance:.4f} Ω\nWire Length: {length:.2f} m")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for resistance calculation.")

# === Toggle wire length input method ===
def toggle_length_input():
    if var_use_calc_length.get():
        entry_wire_length.config(state='disabled')
        entry_turns.config(state='normal')
        entry_turn_length.config(state='normal')
    else:
        entry_wire_length.config(state='normal')
        entry_turns.config(state='disabled')
        entry_turn_length.config(state='disabled')

# --- GUI Setup ---
root = tk.Tk()
root.title("PMDC Motor Design & Winding Resistance Calculator")

# --- PMDC Motor Parameters Frame ---
frame_motor = tk.LabelFrame(root, text="PMDC Motor Parameters", padx=10, pady=10)
frame_motor.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

labels_motor = ["Voltage (V):", "Power (W):", "Speed (RPM):", "Armature Resistance (Ω):", "Efficiency (%):"]
entries_motor = []

for i, label in enumerate(labels_motor):
    tk.Label(frame_motor, text=label).grid(row=i, column=0, sticky="e", pady=2)
    entry = tk.Entry(frame_motor)
    entry.grid(row=i, column=1, pady=2)
    entries_motor.append(entry)

entry_voltage, entry_power, entry_speed, entry_resistance, entry_efficiency = entries_motor

btn_calculate_motor = tk.Button(frame_motor, text="Calculate Motor Parameters", command=calculate_motor)
btn_calculate_motor.grid(row=5, column=0, columnspan=2, pady=8)

motor_output = tk.StringVar()
tk.Label(frame_motor, textvariable=motor_output, justify="left", fg="darkgreen", font=("Courier", 10)).grid(row=6, column=0, columnspan=2, sticky="w")

# --- Torque-Speed Plot ---
fig = plt.Figure(figsize=(6, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

# --- Winding Resistance Frame ---
frame_resistance = tk.LabelFrame(root, text="Winding Resistance Calculation", padx=10, pady=10)
frame_resistance.grid(row=0, column=1, padx=10, pady=10, sticky="n")

# Material selection
tk.Label(frame_resistance, text="Wire Material:").grid(row=0, column=0, sticky="e", pady=2)
material_var = tk.StringVar(frame_resistance)
material_var.set("Copper")
tk.OptionMenu(frame_resistance, material_var, "Copper", "Aluminum").grid(row=0, column=1, pady=2)

# Wire diameter
tk.Label(frame_resistance, text="Wire Diameter (mm):").grid(row=1, column=0, sticky="e", pady=2)
entry_wire_diameter = tk.Entry(frame_resistance)
entry_wire_diameter.grid(row=1, column=1, pady=2)

# Select length input method
var_use_calc_length = tk.BooleanVar()
var_use_calc_length.set(False)
chk_length_method = tk.Checkbutton(frame_resistance, text="Calculate wire length from turns & mean turn length", variable=var_use_calc_length, command=toggle_length_input)
chk_length_method.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

# Manual wire length input
tk.Label(frame_resistance, text="Wire Length (m):").grid(row=3, column=0, sticky="e", pady=2)
entry_wire_length = tk.Entry(frame_resistance)
entry_wire_length.grid(row=3, column=1, pady=2)

# Number of turns input (disabled initially)
tk.Label(frame_resistance, text="Number of Turns:").grid(row=4, column=0, sticky="e", pady=2)
entry_turns = tk.Entry(frame_resistance, state='disabled')
entry_turns.grid(row=4, column=1, pady=2)

# Mean turn length input (meters) (disabled initially)
tk.Label(frame_resistance, text="Mean Turn Length (m):").grid(row=5, column=0, sticky="e", pady=2)
entry_turn_length = tk.Entry(frame_resistance, state='disabled')
entry_turn_length.grid(row=5, column=1, pady=2)

btn_calculate_resistance = tk.Button(frame_resistance, text="Calculate Resistance", command=calculate_resistance)
btn_calculate_resistance.grid(row=6, column=0, columnspan=2, pady=8)

resistance_output = tk.StringVar()
tk.Label(frame_resistance, textvariable=resistance_output, fg="darkblue", font=("Courier", 10)).grid(row=7, column=0, columnspan=2)

# Start GUI mainloop
root.mainloop()
