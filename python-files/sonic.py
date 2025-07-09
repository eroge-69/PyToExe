import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

# Constants
IN3_TO_FT3 = 1 / 1728
IN_TO_FT = 1 / 12
PSI_TO_PSF = 144
R_air = 1716  # ft·lbf/(slug·°R)
gamma = 1.4
P0_psf = 2116  # Sea-level pressure (psf)
T0 = 518.67    # Sea-level temperature (°R)
L = 0.00356616  # Temperature lapse rate (°R/ft)

# Estimate altitude from pressure (ISA approximation)
def pressure_to_altitude(P_psf):
    return max(0.0, (1 - (P_psf / P0_psf) ** ((gamma - 1) / gamma)) * T0 / L)

# Estimate temperature from altitude
def altitude_to_temperature(h_ft):
    return T0 - L * h_ft

def simulate_sonic_decompression():
    try:
        # Inputs from GUI
        P0_psi = float(entry_p_start.get())
        Pext_psi = float(entry_p_final.get())
        V_in3 = float(entry_volume.get())
        num_holes = int(entry_holes.get())
        d_in = float(entry_diameter.get())
        Cd = float(entry_cd.get())
        t_total = float(entry_time.get())

        # Conversions
        P0_psf = P0_psi * PSI_TO_PSF
        Pext_psf = Pext_psi * PSI_TO_PSF
        V_ft3 = V_in3 * IN3_TO_FT3
        r_ft = (d_in / 2) * IN_TO_FT
        A_total_ft2 = num_holes * math.pi * r_ft ** 2

        # Estimate altitudes and corresponding temperatures
        alt0 = pressure_to_altitude(P0_psf)
        alt1 = pressure_to_altitude(Pext_psf)
        T0_ft = altitude_to_temperature(alt0)
        T1_ft = altitude_to_temperature(alt1)

        # Initial conditions
        T = T0_ft
        rho0 = P0_psf / (R_air * T)
        m = rho0 * V_ft3

        # Time steps
        dt = 0.001
        steps = int(t_total / dt)
        time = np.linspace(0, t_total, steps + 1)

        # Data lists
        P_internal, P_external, dP_list = [], [], []

        # Critical pressure ratio for choked flow
        critical_ratio = (2 / (gamma + 1)) ** (gamma / (gamma - 1))

        for t in time:
            # Linearly interpolate external pressure and temperature
            P_ext = P0_psf + (Pext_psf - P0_psf) * (t / t_total)
            T = T0_ft + (T1_ft - T0_ft) * (t / t_total)
            rho = m / V_ft3
            P_int = rho * R_air * T
            P_ratio = P_ext / P_int if P_int > 0 else 1

            # Choked vs subsonic flow
            if P_ratio <= critical_ratio:
                mdot = Cd * A_total_ft2 * P_int * math.sqrt(gamma / (R_air * T)) * \
                       ((2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1))))
            else:
                mdot = Cd * A_total_ft2 * P_int * math.sqrt(
                    2 * gamma / ((gamma - 1) * R_air * T) *
                    ((P_ratio) ** (2 / gamma) - (P_ratio) ** ((gamma + 1) / gamma))
                ) if P_ratio > 0 else 0

            # Update internal mass
            m = max(0, m - mdot * dt)

            # Record values
            P_internal.append(P_int / PSI_TO_PSF)
            P_external.append(P_ext / PSI_TO_PSF)
            dP_list.append((P_int - P_ext) / PSI_TO_PSF)

        # Find max ΔP
        max_dP = max(dP_list)
        time_max_dP = time[dP_list.index(max_dP)]
        entry_max_dP.config(state='normal')
        entry_max_dP.delete(0, tk.END)
        entry_max_dP.insert(0, f"{max_dP:.2f} psi @ {time_max_dP:.2f} s")
        entry_max_dP.config(state='readonly')

        # Clear previous plots
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Plotting
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(time, P_internal, label="Internal Pressure (psi)", color="tab:blue")
        ax.plot(time, P_external, label="External Pressure (psi)", color="tab:green")
        ax.plot(time, dP_list, '--', label="ΔP (psi)", color="tab:red")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (psi)")
        ax.grid(True)
        ax.legend(loc='upper right')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# GUI setup
root = tk.Tk()
root.title("Adiabatic Sonic Decompression Simulator")

labels = [
    ("Initial Pressure (psi):", 0),
    ("Final External Pressure (psi):", 1),
    ("Cavity Volume (in³):", 2),
    ("Number of Holes:", 3),
    ("Hole Diameter (in):", 4),
    ("Discharge Coefficient (Cd):", 5),
    ("Simulation Time (s):", 6),
]

entries = []
for text, row in labels:
    tk.Label(root, text=text).grid(row=row, column=0, sticky='e')
    e = tk.Entry(root)
    e.grid(row=row, column=1)
    entries.append(e)

(entry_p_start, entry_p_final, entry_volume,
 entry_holes, entry_diameter, entry_cd, entry_time) = entries

# Default values
entry_p_start.insert(0, "10.9")
entry_p_final.insert(0, "2.7")
entry_volume.insert(0, "360")
entry_holes.insert(0, "2")
entry_diameter.insert(0, "0.136")
entry_cd.insert(0, "0.6")
entry_time.insert(0, "15")

tk.Button(root, text="Run Simulation", command=simulate_sonic_decompression).grid(row=7, column=0, columnspan=2, pady=10)

tk.Label(root, text="Max ΔP and Time:").grid(row=8, column=0, sticky='e')
entry_max_dP = tk.Entry(root, state='readonly')
entry_max_dP.grid(row=8, column=1, sticky='ew')

plot_frame = tk.Frame(root)
plot_frame.grid(row=9, column=0, columnspan=2, sticky='nsew')
root.grid_rowconfigure(9, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
