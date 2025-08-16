import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from math import pi, sqrt, ceil

# --- Ide másoljuk be a számító függvényeket a konzolos verzióból (rövidítve) ---
RHO_CU_20C = 1.72e-8
TEMP_COEFF_CU = 0.00393
MU0 = 4 * pi * 1e-7

# huzaltábla (egyszerűsítve)
WIRES = [(0.5, pi*(0.25**2)), (0.63, pi*(0.315**2)), (0.8, pi*(0.4**2)),
          (1.0, pi*(0.5**2)), (1.25, pi*(0.625**2)), (1.6, pi*(0.8**2)), (2.0, pi*(1.0**2))]

def pick_wire(area_mm2):
    for d,a in WIRES:
        if a >= area_mm2:
            return d,a
    return round(sqrt(4*area_mm2/pi),2), area_mm2

def compute_transformer(V1, f, Ae_cm2, le_cm, Bmax, J, regulation, T_cu, secondaries):
    Ae = Ae_cm2*1e-4
    le = le_cm/100
    rho = RHO_CU_20C*(1+TEMP_COEFF_CU*(T_cu-20))
    N_per_V = 1/(4.44*f*Bmax*Ae)
    Np = ceil(V1*N_per_V)
    B_used = V1/(4.44*f*Np*Ae)

    results = [f"Primer menetszám Np ≈ {Np}, B = {B_used:.3f} T"]
    total_VA = 0
    for i,(Vs,Is) in enumerate(secondaries, start=1):
        Ns = ceil(Vs*(1+regulation)*N_per_V)
        Areq = Is/J
        d,a = pick_wire(Areq)
        results.append(f"S{i}: {Vs} V @ {Is} A → Ns ≈ {Ns}, huzal ≈ {d} mm")
        total_VA += Vs*Is
    results.append(f"Összes VA ≈ {total_VA:.1f}")
    return "\n".join(results)

# --- GUI ---
class TransformerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Transzformátor modellező")

        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        self.entries = {}
        params = [
            ("Primer fesz (V)", "230"),
            ("Frekvencia (Hz)", "50"),
            ("Ae (cm²)", "4.9"),
            ("le (cm)", "28"),
            ("Bmax (T)", "1.25"),
            ("Áramsűrűség J (A/mm²)", "2.5"),
            ("Ráhagyás %", "5"),
            ("Huzal T (°C)", "75")
        ]
        for i,(lab,defv) in enumerate(params):
            ttk.Label(frm, text=lab).grid(row=i, column=0, sticky="w")
            e = ttk.Entry(frm)
            e.insert(0, defv)
            e.grid(row=i, column=1)
            self.entries[lab] = e

        # szekunder lista
        ttk.Label(frm, text="Szekunder(ek)").grid(row=0, column=2, padx=10)
        self.sec_tree = ttk.Treeview(frm, columns=("V","A"), show="headings", height=5)
        self.sec_tree.heading("V", text="Fesz (V)")
        self.sec_tree.heading("A", text="Áram (A)")
        self.sec_tree.grid(row=1, column=2, rowspan=5, padx=10)

        addfrm = ttk.Frame(frm)
        addfrm.grid(row=6, column=2)
        self.secV = ttk.Entry(addfrm, width=5)
        self.secI = ttk.Entry(addfrm, width=5)
        self.secV.insert(0, "15")
        self.secI.insert(0, "1")
        self.secV.pack(side="left")
        self.secI.pack(side="left")
        ttk.Button(addfrm, text="+", command=self.add_secondary).pack(side="left")

        # gombok
        ttk.Button(frm, text="Számolás", command=self.calculate).grid(row=8, column=0, pady=10)
        ttk.Button(frm, text="Mentés JSON", command=self.save_json).grid(row=8, column=1, pady=10)

        # eredmény
        self.txt = tk.Text(frm, width=70, height=15)
        self.txt.grid(row=9, column=0, columnspan=3)

    def add_secondary(self):
        try:
            V = float(self.secV.get())
            I = float(self.secI.get())
            self.sec_tree.insert("", "end", values=(V,I))
        except:
            messagebox.showerror("Hiba","Érvénytelen szekunder adat")

    def calculate(self):
        try:
            V1 = float(self.entries["Primer fesz (V)"].get())
            f  = float(self.entries["Frekvencia (Hz)"].get())
            Ae = float(self.entries["Ae (cm²)"].get())
            le = float(self.entries["le (cm)"].get())
            B  = float(self.entries["Bmax (T)"].get())
            J  = float(self.entries["Áramsűrűség J (A/mm²)"].get())
            reg= float(self.entries["Ráhagyás %"].get())/100
            Tc = float(self.entries["Huzal T (°C)"].get())
            secs = [(float(v), float(i)) for v,i in self.sec_tree.get_children()
                    for v,i in [self.sec_tree.item(iid)["values"]]]
            result = compute_transformer(V1,f,Ae,le,B,J,reg,Tc,secs)
            self.txt.delete("1.0","end")
            self.txt.insert("end", result)
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def save_json(self):
        secs = [self.sec_tree.item(i)["values"] for i in self.sec_tree.get_children()]
        data = {lab:self.entries[lab].get() for lab in self.entries}
        data["secondaries"] = secs
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("OK", f"Elmentve: {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransformerGUI(root)
    root.mainloop()
