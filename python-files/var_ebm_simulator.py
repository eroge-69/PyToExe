import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VARSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("VAR & EBM Simulator")
        self.root.geometry("800x600")

        # Input Frame
        input_frame = ttk.LabelFrame(root, text="VAR Parameters")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Arc Voltage (V):").grid(row=0, column=0)
        self.arc_voltage = ttk.Entry(input_frame)
        self.arc_voltage.grid(row=0, column=1)

        ttk.Label(input_frame, text="Melt Current (A):").grid(row=1, column=0)
        self.melt_current = ttk.Entry(input_frame)
        self.melt_current.grid(row=1, column=1)

        ttk.Label(input_frame, text="Electrode Diameter (m):").grid(row=2, column=0)
        self.electrode_diam = ttk.Entry(input_frame)
        self.electrode_diam.grid(row=2, column=1)

        ttk.Button(input_frame, text="Simulate", command=self.simulate).grid(row=3, column=0, columnspan=2)

        # Output Frame
        self.output_frame = ttk.LabelFrame(root, text="Results")
        self.output_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def simulate(self):
        try:
            arc_voltage = float(self.arc_voltage.get())
            melt_current = float(self.melt_current.get())
            electrode_diam = float(self.electrode_diam.get())

            # Simplified molten pool depth calculation (based on VAR report)
            # Depth decreases with increasing arc radius (diffusive arc assumption)
            arc_radius = electrode_diam / 2
            pool_depth = 0.05 * (1000 / arc_radius) - 0.01 * melt_current / 1000  # Arbitrary scaling
            if pool_depth < 0:
                pool_depth = 0.001  # Minimum depth

            # Temperature distribution (simplified axial gradient)
            r = np.linspace(0, arc_radius, 100)
            temp_dist = 2000 * np.exp(-r**2 / (arc_radius**2))  # Gaussian decay

            # Plotting
            self.output_frame.destroy()
            self.output_frame = ttk.LabelFrame(self.root, text="Results")
            self.output_frame.pack(padx=10, pady=10, fill="both", expand=True)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.plot(r, temp_dist)
            ax1.set_title("Temperature Distribution")
            ax1.set_xlabel("Radius (m)")
            ax1.set_ylabel("Temperature (K)")

            ax2.bar(["Pool Depth"], [pool_depth])
            ax2.set_title("Molten Pool Depth")
            ax2.set_ylabel("Depth (m)")

            canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

            ttk.Label(self.output_frame, text=f"Molten Pool Depth: {pool_depth:.3f} m").pack()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VARSimulator(root)
    root.mainloop()