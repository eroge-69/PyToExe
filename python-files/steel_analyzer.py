# steel_analyzer.py
# Prototype steel axial capacity checker (IS 800:2007 - Limit State)
# Requires: Python 3.8+ (no external packages)

import csv
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

GAMMA_M0 = 1.10
GAMMA_M1 = 1.25
E = 205000.0

def load_sections(csvfile='sections.csv'):
    sections = {}
    try:
        with open(csvfile, newline='') as f:
            reader = csv.DictReader(f)
            for r in reader:
                name = r['name']
                sections[name] = {
                    'Ag': float(r['Ag_mm2']),
                    'r_z': float(r.get('r_z_mm', r.get('rxx_mm', 0) or 0)),
                    'r_y': float(r.get('r_y_mm', r.get('ryy_mm', 0) or 0)),
                    'Anet': float(r.get('Anet_mm2', r.get('Anet', r.get('Ag_mm2', r.get('Ag', 0)))) )
                }
    except Exception as e:
        print("Warning: couldn't read sections.csv:", e)
    return sections

def euler_buckling_stress(KL_over_r):
    if KL_over_r <= 0:
        return float('inf')
    return (math.pi**2 * E) / (KL_over_r**2)

def nondim_slenderness(fy, fcc):
    if fcc <= 0:
        return 0.0
    return math.sqrt(fy / fcc)

def phi_lambda(alpha, lam):
    return 0.5 * (1.0 + alpha * (lam - 0.2) + lam**2)

def chi_from_phi_lambda(phi, lam):
    val = math.sqrt(max(phi*phi - lam*lam, 0.0))
    denom = phi + val
    if denom == 0:
        return 0.0
    return 1.0 / denom

def design_compressive_stress(fy, KL_over_r, alpha):
    fcc = euler_buckling_stress(KL_over_r)
    lam = nondim_slenderness(fy, fcc)
    phi = phi_lambda(alpha, lam)
    chi = chi_from_phi_lambda(phi, lam)
    fcd = (chi * fy) / GAMMA_M0
    fcd = min(fcd, fy / GAMMA_M0)
    return {'fcc': fcc, 'lambda': lam, 'phi': phi, 'chi': chi, 'fcd': fcd}

def tension_yield_capacity(Ag, fy):
    return Ag * fy / GAMMA_M0

class SteelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Steel Axial Capacity - IS 800:2007 (Prototype)")
        self.geometry("760x520")
        self.sections = load_sections('sections.csv')
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Section:").grid(row=0, column=0, sticky='w')
        self.sec_var = tk.StringVar()
        sec_list = list(self.sections.keys()) or ['(no sections loaded)']
        self.sec_cb = ttk.Combobox(frm, textvariable=self.sec_var, values=sec_list, width=40)
        self.sec_cb.grid(row=0, column=1, columnspan=3, sticky='w')
        if sec_list:
            self.sec_cb.current(0)

        ttk.Button(frm, text="Load CSV...", command=self.load_csv_dialog).grid(row=0, column=4)

        ttk.Label(frm, text="Member length L (mm):").grid(row=1, column=0, sticky='w')
        self.L_ent = ttk.Entry(frm); self.L_ent.grid(row=1, column=1, sticky='w'); self.L_ent.insert(0, "3000")

        ttk.Label(frm, text="K_major (Kz):").grid(row=1, column=2, sticky='w')
        self.Kz_ent = ttk.Entry(frm); self.Kz_ent.grid(row=1, column=3, sticky='w'); self.Kz_ent.insert(0, "1.0")

        ttk.Label(frm, text="K_minor (Ky):").grid(row=1, column=4, sticky='w')
        self.Ky_ent = ttk.Entry(frm); self.Ky_ent.grid(row=1, column=5, sticky='w'); self.Ky_ent.insert(0, "1.0")

        ttk.Label(frm, text="Steel fy (MPa):").grid(row=2, column=0, sticky='w')
        self.fy_ent = ttk.Entry(frm); self.fy_ent.grid(row=2, column=1, sticky='w'); self.fy_ent.insert(0, "250")

        ttk.Label(frm, text="Imperfection factor α (pick from table):").grid(row=2, column=2, sticky='w')
        self.alpha_ent = ttk.Entry(frm); self.alpha_ent.grid(row=2, column=3, sticky='w'); self.alpha_ent.insert(0, "0.49")

        ttk.Label(frm, text="Applied axial load Pu (kN):").grid(row=2, column=4, sticky='w')
        self.Pu_ent = ttk.Entry(frm); self.Pu_ent.grid(row=2, column=5, sticky='w'); self.Pu_ent.insert(0, "0")

        ttk.Button(frm, text="Calculate", command=self.calculate).grid(row=3, column=0, pady=10)

        self.out = tk.Text(frm, width=90, height=20)
        self.out.grid(row=4, column=0, columnspan=6, pady=6)

        ttk.Label(frm, text="Note: Prototype. Verify with IS 800:2007 before use.").grid(row=5, column=0, columnspan=6, sticky='w')

    def load_csv_dialog(self):
        fname = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if fname:
            try:
                self.sections = load_sections(fname)
                values = list(self.sections.keys())
                self.sec_cb['values'] = values
                if values:
                    self.sec_cb.current(0)
                messagebox.showinfo("Loaded", f"Loaded {len(values)} sections from {fname}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def calculate(self):
        secname = self.sec_var.get()
        if secname not in self.sections:
            messagebox.showerror("Error", "Pick a valid section.")
            return
        sec = self.sections[secname]
        try:
            L = float(self.L_ent.get())
            Kz = float(self.Kz_ent.get())
            Ky = float(self.Ky_ent.get())
            fy = float(self.fy_ent.get())
            alpha = float(self.alpha_ent.get())
            Pu = float(self.Pu_ent.get()) * 1000.0
        except Exception as e:
            messagebox.showerror("Input error", str(e))
            return

        Ag = sec['Ag']
        r_z = sec['r_z']
        r_y = sec['r_y']
        Anet = sec.get('Anet', Ag)

        KLz_over_rz = (Kz * L) / r_z if r_z>0 else 1e9
        res_z = design_compressive_stress(fy, KLz_over_rz, alpha)
        Pd_z = Ag * res_z['fcd']

        KLy_over_ry = (Ky * L) / r_y if r_y>0 else 1e9
        res_y = design_compressive_stress(fy, KLy_over_ry, alpha)
        Pd_y = Ag * res_y['fcd']

        T_yield = tension_yield_capacity(Ag, fy)
        T_rupture = Anet * fy / GAMMA_M1

        self.out.delete(1.0, tk.END)
        self.out.insert(tk.END, f"Section: {secname}\n")
        self.out.insert(tk.END, f"Ag = {Ag:,.1f} mm², r_z = {r_z:.2f} mm, r_y = {r_y:.2f} mm\n\n")

        self.out.insert(tk.END, "=== Compression (major axis / z-z) ===\n")
        self.out.insert(tk.END, f"K L / r_z = {KLz_over_rz:,.2f}\n")
        self.out.insert(tk.END, f"Euler buckling stress f_cc = {res_z['fcc']:.2f} MPa\n")
        self.out.insert(tk.END, f"Non-dim slenderness λ = {res_z['lambda']:.4f}\n")
        self.out.insert(tk.END, f"phi = {res_z['phi']:.4f}, chi = {res_z['chi']:.4f}\n")
        self.out.insert(tk.END, f"Design compressive stress f_cd = {res_z['fcd']:.2f} MPa\n")
        self.out.insert(tk.END, f"Design compressive strength P_d (major) = {Pd_z/1000.0:,.2f} kN\n\n")

        self.out.insert(tk.END, "=== Compression (minor axis / y-y) ===\n")
        self.out.insert(tk.END, f"K L / r_y = {KLy_over_ry:,.2f}\n")
        self.out.insert(tk.END, f"Euler buckling stress f_cc = {res_y['fcc']:.2f} MPa\n")
        self.out.insert(tk.END, f"Non-dim slenderness λ = {res_y['lambda']:.4f}\n")
        self.out.insert(tk.END, f"phi = {res_y['phi']:.4f}, chi = {res_y['chi']:.4f}\n")
        self.out.insert(tk.END, f"Design compressive stress f_cd = {res_y['fcd']:.2f} MPa\n")
        self.out.insert(tk.END, f"Design compressive strength P_d (minor) = {Pd_y/1000.0:,.2f} kN\n\n")

        self.out.insert(tk.END, "=== Tension ===\n")
        self.out.insert(tk.END, f"Tensile capacity (yielding of gross section) T_d_yield = {T_yield/1000.0:,.2f} kN (using γ_m0={GAMMA_M0})\n")
        self.out.insert(tk.END, f"Tensile capacity (rupture, net) approx T_d_rupture = {T_rupture/1000.0:,.2f} kN (using γ_m1={GAMMA_M1})\n\n")

        self.out.insert(tk.END, "=== Summary check (compare with applied Pu) ===\n")
        if Pu>0:
            self.out.insert(tk.END, f"Applied Pu = {Pu/1000.0:,.2f} kN\n")
            self.out.insert(tk.END, f"Utilization major = {100.0 * (Pu / Pd_z):.1f}%\n")
            self.out.insert(tk.END, f"Utilization minor = {100.0 * (Pu / Pd_y):.1f}%\n")
        else:
            self.out.insert(tk.END, "No applied Pu entered (set Pu > 0 to compare).\n")

if __name__ == '__main__':
    app = SteelApp()
    app.mainloop()