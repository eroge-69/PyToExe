import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy

# --- Dictionnaires pour la gestion des unités ---
STRAIN_UNITS = {
    "ε (m/m)": 1.0,
    "mε (10⁻³)": 1e-3,
    "µε (10⁻⁶)": 1e-6,
}
MODULUS_UNITS = {
    "Pa": 1.0,
    "kPa": 1e3,
    "MPa": 1e6,
    "GPa": 1e9,
}

# --- Logique de Calcul avec SymPy ---
def calculate_stresses_sympy(strain_x, strain_45, strain_y, E, v):
    epsilon_x, epsilon_y = strain_x, strain_y
    gamma_xy = 2 * strain_45 - (epsilon_x + epsilon_y)
    epsilon_avg = (epsilon_x + epsilon_y) / 2
    R_strain = sympy.sqrt(((epsilon_x - epsilon_y) / 2)**2 + (gamma_xy / 2)**2)
    epsilon_1 = epsilon_avg + R_strain
    epsilon_2 = epsilon_avg - R_strain
    theta_p_rad = sympy.S(1)/2 * sympy.atan2(gamma_xy, epsilon_x - epsilon_y)
    theta_p_deg = theta_p_rad * 180 / sympy.pi
    if abs(1 - v**2) == 0:
        return {'sigma_1': sympy.nan, 'sigma_2': sympy.nan, 'theta_p': sympy.nan}
    factor = E / (1 - v**2)
    sigma_1 = factor * (epsilon_1 + v * epsilon_2)
    sigma_2 = factor * (epsilon_2 + v * epsilon_1)
    return {'sigma_1': sigma_1, 'sigma_2': sigma_2, 'theta_p': theta_p_deg}

# --- Classe de l'Application GUI ---
class RosetteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur de Rosette (Haute Précision)")
        self.geometry("1050x700")
        self.minsize(950, 650)
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'))
        style.configure('TEntry', font=('Helvetica', 10))
        style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'))

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, padding="10", width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.vars = {
            'strain_x': tk.StringVar(value="1000"), 'strain_45': tk.StringVar(value="-200"),
            'strain_y': tk.StringVar(value="500"), 'strain_unit': tk.StringVar(value="µε (10⁻⁶)"),
            'E': tk.StringVar(value="200"), 'modulus_unit': tk.StringVar(value="GPa"),
            'v': tk.StringVar(value="0.3"), 'sigma_1': tk.StringVar(value="---"),
            'sigma_2': tk.StringVar(value="---"), 'theta_p': tk.StringVar(value="---"),
            'stress_unit': tk.StringVar(value="---")
        }

        self.create_input_widgets(left_frame)
        self.create_results_widgets(left_frame)
        self.create_plot_widget(right_frame)
        self.update_plot()

    def create_input_widgets(self, parent):
        strain_frame = ttk.LabelFrame(parent, text=" Données de Déformation ", padding="10")
        strain_frame.pack(fill=tk.X, pady=10)
        strain_frame.grid_columnconfigure(1, weight=1)

        labels = ["Déformation à 0° (εx) :", "Déformation à 45° :", "Déformation à 90° (εy) :"]
        vars_keys = ['strain_x', 'strain_45', 'strain_y']
        for i, (label, key) in enumerate(zip(labels, vars_keys)):
            ttk.Label(strain_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(strain_frame, textvariable=self.vars[key], width=15).grid(row=i, column=1, sticky="ew", padx=5)
        
        unit_combo = ttk.Combobox(strain_frame, textvariable=self.vars['strain_unit'], values=list(STRAIN_UNITS.keys()), state="readonly", width=12)
        unit_combo.grid(row=0, column=2, rowspan=3, sticky="w", padx=(5,0))
        unit_combo.set("µε (10⁻⁶)")

        material_frame = ttk.LabelFrame(parent, text=" Propriétés du Matériau ", padding="10")
        material_frame.pack(fill=tk.X, pady=10)
        material_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(material_frame, text="Module d'Young (E) :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(material_frame, textvariable=self.vars['E'], width=15).grid(row=0, column=1, sticky="ew", padx=5)
        mod_unit_combo = ttk.Combobox(material_frame, textvariable=self.vars['modulus_unit'], values=list(MODULUS_UNITS.keys()), state="readonly", width=12)
        mod_unit_combo.grid(row=0, column=2, sticky="w", padx=(5,0))
        mod_unit_combo.set("GPa")

        ttk.Label(material_frame, text="Coeff. de Poisson (ν) :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(material_frame, textvariable=self.vars['v']).grid(row=1, column=1, sticky="ew", padx=5)

        calc_button = ttk.Button(parent, text="Calculer les Contraintes", command=self.on_calculate)
        calc_button.pack(fill=tk.X, pady=20, ipady=5)

    def create_results_widgets(self, parent):
        results_frame = ttk.LabelFrame(parent, text=" Résultats ", padding="10")
        results_frame.pack(fill=tk.X, pady=10)
        results_frame.grid_columnconfigure(1, weight=1)
        results_labels = [("Contrainte max (σ₁) :", 'sigma_1'), ("Contrainte min (σ₂) :", 'sigma_2'), ("Angle principal (θp) :", 'theta_p')]
        for i, (label_text, key) in enumerate(results_labels):
            ttk.Label(results_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            ttk.Label(results_frame, textvariable=self.vars[key], font=('Helvetica', 11, 'bold'), foreground="#007acc").grid(row=i, column=1, sticky="w", padx=5)
            if 'sigma' in key:
                 ttk.Label(results_frame, textvariable=self.vars['stress_unit']).grid(row=i, column=2, sticky="w", padx=5)
            else:
                 ttk.Label(results_frame, text="° (degrés)").grid(row=i, column=2, sticky="w", padx=5)
    
    def on_calculate(self):
        try:
            strain_factor = sympy.S(str(STRAIN_UNITS[self.vars['strain_unit'].get()]))
            modulus_factor = sympy.S(str(MODULUS_UNITS[self.vars['modulus_unit'].get()]))
            inputs_sympy = {
                'strain_x': sympy.S(self.vars['strain_x'].get()) * strain_factor,
                'strain_45': sympy.S(self.vars['strain_45'].get()) * strain_factor,
                'strain_y': sympy.S(self.vars['strain_y'].get()) * strain_factor,
                'E': sympy.S(self.vars['E'].get()) * modulus_factor,
                'v': sympy.S(self.vars['v'].get())
            }
            results_exact = calculate_stresses_sympy(**inputs_sympy)
            if any(v == sympy.nan for v in results_exact.values()):
                raise ValueError("Calcul invalide (NaN). Vérifiez le coefficient de Poisson.")
            
            sigma_1_val_Pa = results_exact['sigma_1'].evalf()
            sigma_2_val_Pa = results_exact['sigma_2'].evalf()
            theta_p_val = float(results_exact['theta_p'].evalf())

            output_unit_str = "MPa"
            output_unit_factor = 1e6

            sigma_1_display_MPa = sigma_1_val_Pa / output_unit_factor
            sigma_2_display_MPa = sigma_2_val_Pa / output_unit_factor

            self.vars['sigma_1'].set(f"{sigma_1_display_MPa:.4g}")
            self.vars['sigma_2'].set(f"{sigma_2_display_MPa:.4g}")
            self.vars['theta_p'].set(f"{theta_p_val:.2f}")
            self.vars['stress_unit'].set(output_unit_str)
            self.update_plot(theta_p_val)

        except (ValueError, SyntaxError, KeyError) as e:
            messagebox.showerror("Erreur de Saisie ou de Calcul", f"Veuillez vérifier vos entrées.\n{e}")
            for key in ['sigma_1', 'sigma_2', 'theta_p', 'stress_unit']: self.vars[key].set("---")
            self.update_plot()
        except Exception as e:
            messagebox.showerror("Erreur Inconnue", f"Une erreur est survenue: {e}")

    def create_plot_widget(self, parent):
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.tight_layout()

    def update_plot(self, theta_p=None):
        self.ax.clear()
        self.ax.plot([0, 1], [0, 0], 'k-', lw=1.5, label='Jauge 0° (εx)')
        self.ax.plot([0, np.cos(np.pi/4)], [0, np.sin(np.pi/4)], 'k--', lw=1.5, label='Jauge 45°')
        self.ax.plot([0, 0], [0, 1], 'k-.', lw=1.5, label='Jauge 90° (εy)')
        if theta_p is not None and not np.isnan(theta_p):
            theta_rad = np.radians(theta_p)
            self.ax.arrow(0, 0, 1.2 * np.cos(theta_rad), 1.2 * np.sin(theta_rad), head_width=0.05, head_length=0.1, fc='r', ec='r', lw=2, label=f'σ_max (à {theta_p:.1f}°)')
            self.ax.arrow(0, 0, -1.2 * np.cos(theta_rad), -1.2 * np.sin(theta_rad), head_width=0.05, head_length=0.1, fc='r', ec='r', lw=2)
            theta_2_rad = theta_rad + np.pi / 2
            self.ax.arrow(0, 0, 0.8 * np.cos(theta_2_rad), 0.8 * np.sin(theta_2_rad), head_width=0.05, head_length=0.1, fc='b', ec='b', lw=2, label='σ_min')
            self.ax.arrow(0, 0, -0.8 * np.cos(theta_2_rad), -0.8 * np.sin(theta_2_rad), head_width=0.05, head_length=0.1, fc='b', ec='b', lw=2)
            arc = np.linspace(0, theta_rad, 50)
            self.ax.plot(0.4 * np.cos(arc), 0.4 * np.sin(arc), 'r-')
            self.ax.text(0.5 * np.cos(theta_rad / 2), 0.5 * np.sin(theta_rad / 2), f'θp={theta_p:.1f}°', fontsize=10, color='red')
        self.ax.set_xlim(-1.5, 1.5); self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_aspect('equal', adjustable='box'); self.ax.grid(True, linestyle=':')
        self.ax.set_title("Orientation des Contraintes Principales"); self.ax.set_xlabel("Axe X"); self.ax.set_ylabel("Axe Y")
        self.ax.legend(loc='upper right', fontsize='small'); self.fig.tight_layout(); self.canvas.draw()

if __name__ == "__main__":
    app = RosetteApp()
    app.mainloop()