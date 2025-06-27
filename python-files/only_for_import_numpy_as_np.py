import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Constants
k_B = 8.617e-5  # eV/K

class SurfaceCoverageApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Friendly Surface Coverage Calculator")

        self.create_widgets()

    def create_widgets(self):
        # Labels and inputs
        ttk.Label(self.master, text="👋 Heeko friend! Please give me the Adsorption Energies (ε) [eV, comma-separated]:").grid(row=0, column=0, sticky='w')
        self.epsilon_entry = ttk.Entry(self.master)
        self.epsilon_entry.insert(0, "-0.68,-0.75,-0.80")
        self.epsilon_entry.grid(row=0, column=1)

        ttk.Label(self.master, text="😊 You are a nice person! Please give the Temperature Range [K]:").grid(row=1, column=0, sticky='w')
        self.temp_entry = ttk.Entry(self.master)
        self.temp_entry.insert(0, "200,300,400,500,600")
        self.temp_entry.grid(row=1, column=1)

        ttk.Label(self.master, text="🧪 Chemical Potential (μ) [eV]:").grid(row=2, column=0, sticky='w')
        self.mu_entry = ttk.Entry(self.master)
        self.mu_entry.insert(0, "-0.3")
        self.mu_entry.grid(row=2, column=1)

        # Button
        self.calc_button = ttk.Button(self.master, text="Calculate & Plot", command=self.calculate_and_plot)
        self.calc_button.grid(row=3, columnspan=2, pady=10)

        # Text box for results
        self.result_text = tk.Text(self.master, height=18, width=80)
        self.result_text.grid(row=4, column=0, columnspan=2)

        # Configure color tags
        self.result_text.tag_configure("formula_header", foreground="dark blue", font=("Courier", 10, "bold"))
        self.result_text.tag_configure("equation", foreground="blue", font=("Courier", 10, "bold"))
        self.result_text.tag_configure("where", foreground="dark green", font=("Courier", 9, "italic"))
        self.result_text.tag_configure("assumptions", foreground="purple", font=("Courier", 9))

        # Canvas for plot
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.grid(row=5, column=0, columnspan=2)

    def surface_coverage(self, mu_X, epsilon_X, T):
        exponent = (mu_X - epsilon_X) / (k_B * T)
        theta_X = np.exp(exponent) / (1 + np.exp(exponent))
        return theta_X

    def calculate_and_plot(self):
        try:
            epsilons = [float(e.strip()) for e in self.epsilon_entry.get().split(',')]
            T_list = [float(t.strip()) for t in self.temp_entry.get().split(',')]
            mu_X = float(self.mu_entry.get())

            # Clear previous results and plot
            self.result_text.delete(1.0, tk.END)
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            # Insert color-coded formula explanation
            self.result_text.insert(tk.END, "📘 Surface Coverage Formula:\n", "formula_header")
            self.result_text.insert(tk.END, "    θ = exp[(μ - ε) / (k_B * T)] / [1 + exp[(μ - ε) / (k_B * T)]]\n\n", "equation")
            self.result_text.insert(tk.END,
                "📌 Where:\n"
                "    θ   = Surface coverage (dimensionless, between 0 and 1)\n"
                "    μ   = Chemical potential of the adsorbate (in eV)\n"
                "    ε   = Adsorption energy (in eV)\n"
                "    T   = Temperature (in Kelvin)\n"
                "    k_B = Boltzmann constant ≈ 8.617 × 10⁻⁵ eV/K\n\n",
                "where"
            )
            self.result_text.insert(tk.END,
                "Assumptions (Langmuir adsorption isotherm):\n"
                "  - Adsorption sites are equivalent\n"
                "  - No interaction between adsorbates\n"
                "  - Adsorption is in dynamic equilibrium\n\n",
                "assumptions"
            )

            # Create figure for plotting
            fig, ax = plt.subplots(figsize=(5, 3), dpi=70)

            # Loop over each epsilon
            for epsilon in epsilons:
                theta_values = [self.surface_coverage(mu_X, epsilon, T) for T in T_list]

                # Plot values
                ax.plot(
                    T_list,
                    theta_values,
                    marker='o',
                    linewidth=2,
                    markersize=6,
                    label=f"ε = {epsilon} eV"
                )

                # Print results
                self.result_text.insert(tk.END, f"✅ Results for ε = {epsilon} eV and μ = {mu_X} eV\n")
                for T, theta in zip(T_list, theta_values):
                    self.result_text.insert(tk.END, f"   T = {T:.1f} K → θ = {theta:.10f}\n")
                self.result_text.insert(tk.END, "\n")

            # Style the plot
            ax.set_title("Surface Coverage vs Temperature", fontsize=14)
            ax.set_xlabel("Temperature (K)", fontsize=12)
            ax.set_ylabel("Surface Coverage (θ)", fontsize=12)
            ax.tick_params(axis='both', which='major', labelsize=11)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize=10, loc='best', frameon=False)
            fig.tight_layout()

            # Save figure
            fig.savefig("surface_coverage_plot.png", dpi=300, bbox_inches='tight')

            # Display in GUI
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except ValueError:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "⚠️ Please enter valid numeric values.")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SurfaceCoverageApp(root)
    root.mainloop()
