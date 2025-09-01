import tkinter as tk
from tkinter import ttk
import xraylib
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import re

# ---------- توابع ----------
def parse_formula(formula):
    pattern = '([A-Z][a-z]*)([0-9]*)'
    matches = re.findall(pattern, formula)
    elem_counts = {}
    for (elem, count) in matches:
        count = int(count) if count else 1
        elem_counts[elem] = elem_counts.get(elem,0) + count
    return elem_counts

def compute_mass_fraction(elem_counts):
    total_mass = sum(xraylib.AtomicWeight(xraylib.SymbolToAtomicNumber(elem))*count
                     for elem,count in elem_counts.items())
    mass_fractions = {elem: xraylib.AtomicWeight(xraylib.SymbolToAtomicNumber(elem))*count/total_mass
                     for elem,count in elem_counts.items()}
    return mass_fractions

def compute_composite_density(densities, weights):
    sum_term = sum(w/rho for w,rho in zip(weights,densities))
    return 1/sum_term

# ---------- GUI ----------
class AttenuationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gamma Ray Attenuation Multi-Composite")
        self.root.geometry("1000x600")

        # ---------- Styles ----------
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='white', background='#007ACC')
        style.map('TButton', background=[('active', '#005A9C')])
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('Treeview', font=('Helvetica', 10), rowheight=25)

        # ---------- Frame: Table ----------
        table_frame = ttk.LabelFrame(root, text="Composites Table")
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("Formula", "Density", "Mass_percent")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=300, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)

        self.scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Bind double-click for cell editing
        self.tree.bind("<Double-1>", self.edit_cell)

        # ---------- Buttons to modify table ----------
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="Add Row", command=self.add_row).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Row", command=self.delete_row).pack(side='left', padx=5)

        # ---------- Energies ----------
        energy_frame = ttk.LabelFrame(root, text="Energies (keV)")
        energy_frame.pack(fill='x', padx=10, pady=5)
        self.energies_entry = ttk.Entry(energy_frame, width=80)
        self.energies_entry.insert(0, "20,40,60,80,100,140,511,662")
        self.energies_entry.pack(padx=5, pady=5)

        # ---------- Checkboxes ----------
        param_frame = ttk.LabelFrame(root, text="Parameters to Compute")
        param_frame.pack(fill='x', padx=10, pady=5)
        self.param_mu_rho = tk.IntVar(value=1)
        self.param_mu = tk.IntVar(value=1)
        self.param_HVL = tk.IntVar(value=1)
        ttk.Checkbutton(param_frame, text="µ/ρ", variable=self.param_mu_rho).pack(side='left', padx=5)
        ttk.Checkbutton(param_frame, text="µ", variable=self.param_mu).pack(side='left', padx=5)
        ttk.Checkbutton(param_frame, text="HVL", variable=self.param_HVL).pack(side='left', padx=5)

        # ---------- Compute Button ----------
        self.compute_btn = ttk.Button(root, text="Compute & Plot", command=self.compute_plot)
        self.compute_btn.pack(pady=10)

        # ---------- Status Label ----------
        self.status_label = ttk.Label(root, text="", foreground='red')
        self.status_label.pack(fill='x', padx=10)

        # ---------- Initialize with 2 rows ----------
        self.add_row()
        self.add_row()

    # ---------- Add/Delete Rows ----------
    def add_row(self):
        self.tree.insert('', 'end', values=("C2H3Cl,Bi2O3,SnO2", "1.4,8.9,7.0", "30,40,30"))

    def delete_row(self):
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    # ---------- Edit Cell ----------
    def edit_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, col)
        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            self.tree.set(row_id, col, entry.get())
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    # ---------- Compute & Plot ----------
    def compute_plot(self):
        self.status_label.config(text="")
        try:
            energies = [float(e.strip()) for e in self.energies_entry.get().split(',')]
        except:
            self.status_label.config(text="Invalid energies")
            return

        active_params = []
        if self.param_mu_rho.get(): active_params.append('Mu_over_rho_cm2_g')
        if self.param_mu.get(): active_params.append('Mu_cm-1')
        if self.param_HVL.get(): active_params.append('HVL_cm')
        if not active_params:
            self.status_label.config(text="No parameters selected")
            return

        fig = make_subplots(rows=len(active_params), cols=1, shared_xaxes=True,
                            subplot_titles=[f"{p} vs Energy" for p in active_params])

        for idx, row in enumerate(self.tree.get_children()):
            comp_name = f"Composite {idx+1}"
            formula_str, density_str, mass_str = self.tree.item(row)['values']
            formulas = [f.strip() for f in formula_str.split(',')]
            try:
                densities = [float(d.strip()) for d in density_str.split(',')]
                weights = [float(w.strip())/100 for w in mass_str.split(',')]
            except:
                self.status_label.config(text=f"Invalid densities or weights for {comp_name}")
                continue
            if len(formulas)!=len(densities) or len(formulas)!=len(weights):
                self.status_label.config(text=f"Mismatch in {comp_name}")
                continue

            rho_composite = compute_composite_density(densities, weights)
            composite_mass_fraction = {}
            for f, w_frac in zip(formulas, weights):
                elem_counts = parse_formula(f)
                elem_mass_frac = compute_mass_fraction(elem_counts)
                for elem,mf in elem_mass_frac.items():
                    composite_mass_fraction[elem] = composite_mass_fraction.get(elem,0) + mf*w_frac

            # Compute data
            data=[]
            for E in energies:
                mu_rho = 0
                for sym,w in composite_mass_fraction.items():
                    Z = xraylib.SymbolToAtomicNumber(sym)
                    try:
                        mu_rho += w * xraylib.CS_Total(Z,E)
                    except ValueError:
                        mu_rho = float('nan')
                mu = mu_rho * rho_composite
                HVL = math.log(2)/mu if mu>0 else float('nan')
                data.append({'Energy_keV':E, 'Mu_over_rho_cm2_g':mu_rho, 'Mu_cm-1':mu, 'HVL_cm':HVL})

            df = pd.DataFrame(data)
            df.to_excel(f'attenuation_{idx+1}.xlsx', index=False)

            for i, param in enumerate(active_params):
                fig.add_trace(go.Scatter(x=df['Energy_keV'], y=df[param],
                                         mode='lines+markers', name=comp_name), row=i+1, col=1)

        fig.update_layout(height=300*len(active_params), width=900, title_text="Gamma Ray Attenuation Multi-Composite")
        fig.update_xaxes(title_text="Energy (keV)", row=len(active_params), col=1)
        y_titles = {'Mu_over_rho_cm2_g':'µ/ρ (cm²/g)', 'Mu_cm-1':'µ (cm⁻¹)', 'HVL_cm':'HVL (cm)'}
        for i, param in enumerate(active_params):
            fig.update_yaxes(title_text=y_titles[param], row=i+1, col=1)

        pio.show(fig)
        pio.write_html('attenuation_multi_composites_plot.html', include_plotlyjs='cdn')
        self.status_label.config(text="Computation and plotting done! Files saved.")

# ---------- Run ----------
root = tk.Tk()
app = AttenuationApp(root)
root.mainloop()