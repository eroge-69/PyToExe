import sys

# แก้ปัญหา matplotlib เมื่อนำไปแปลงเป็น exe
if getattr(sys, 'frozen', False):
    import matplotlib
    matplotlib.use('Agg')

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

def calculate_and_plot():
    try:
        d = float(d_entry.get())
        D = float(D_entry.get())
        n = float(n_entry.get())
        L0 = float(L0_entry.get())
        L1 = float(L1_entry.get())
        L2 = float(L2_entry.get())
        G = float(G_entry.get())
        tensile_strength = float(ts_entry.get())
    except ValueError:
        return

    C = D / d
    kw = (4*C - 1)/(4*C - 4) + 0.615/C
    k = (G * d**4) / (8 * D**3 * n)
    F1 = k * (L0 - L1)
    F2 = k * (L0 - L2)
    tau1 = (8 * F1 * D) / (math.pi * d**3) * kw
    tau2 = (8 * F2 * D) / (math.pi * d**3) * kw
    Ls = d * (n + 2)

    tau_min = min(tau1, tau2)
    tau_max = max(tau1, tau2)
    tau_m = (tau_min + tau_max) / 2
    tau_a = (tau_max - tau_min) / 2

    tau_e = 0.35 * tensile_strength
    tau_ult = 0.67 * tensile_strength
    tau_y = 0.50 * tensile_strength

    result_text.set(f"""Spring Constant (k): {k:.2f} N/mm
Spring Index, (C): {C:.2f}
Wahl Factor, (kw): {kw:.3f}
Presetting Load, P1: {F1:.2f} N
Presetting Stress: {tau1:.2f} N/mm²
Operating Load, P2: {F2:.2f} N
Operating Stress: {tau2:.2f} N/mm²
Solid Length: {Ls:.2f} mm""")

    ax.clear()
    m_tau = np.linspace(0, tau_ult, 100)
    a_tau_goodman = tau_e * (1 - m_tau / tau_ult)
    a_tau_yield = tau_y - m_tau

    ax.plot(m_tau, a_tau_goodman, 'b-', label="Goodman Line")
    ax.plot(m_tau, a_tau_yield, 'r--', label="Yield Line")
    ax.plot(tau_m, tau_a, 'ro', label="Operating Point")

    ax.set_xlim(0, tau_ult * 1.1)
    ax.set_ylim(0, tau_e * 1.1)
    ax.set_xlabel("Mean Stress (τm) [N/mm²]")
    ax.set_ylabel("Alternating Stress (τa) [N/mm²]")
    ax.set_title("Goodman Diagram")
    ax.grid(True)
    ax.legend()

    canvas.draw()

root = tk.Tk()
root.title("Spring Goodman Diagram Calculator")

inputs = [
    ("Wire diameter, d (mm)", "1.2"),
    ("Mean diameter, D (mm)", "4.5"),
    ("Effective turns, n", "4"),
    ("Free length, L0 (mm)", "10.75"),
    ("Presetting length, L1 (mm)", "9.55"),
    ("Operating length, L2 (mm)", "7.9"),
    ("Rigidity modulus, G (N/mm²)", "78500"),
    ("Tensile strength, (N/mm²)", "1500"),
]

entries = []
for i, (label, default) in enumerate(inputs):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e")
    entry = ttk.Entry(root)
    entry.insert(0, default)
    entry.grid(row=i, column=1)
    entries.append(entry)

(d_entry, D_entry, n_entry, L0_entry, L1_entry, L2_entry, G_entry, ts_entry) = entries

ttk.Button(root, text="Calculate & Plot", command=calculate_and_plot).grid(row=len(inputs), column=0, columnspan=2, pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify="left").grid(row=len(inputs)+1, column=0, columnspan=2)

fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=2, rowspan=len(inputs)+2, padx=10)

calculate_and_plot()
root.mainloop()
