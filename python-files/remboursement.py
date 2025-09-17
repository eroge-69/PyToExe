import tkinter as tk
from tkinter import ttk
import math

# ---------- Utils ----------
def parse_float(s: str) -> float:
    s = (s or "").strip().replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return 0.0

def arrondi_selon_regle(valeur: float) -> float:
    """
    Arrondi demandé :
      - décimales < 0.50 -> X,00
      - décimales >= 0.50 -> X+1,00
    Exemples : 1,42 -> 1,00 ; 1,65 -> 2,00
    """
    entier = math.floor(valeur)
    frac = valeur - entier
    return float(entier if frac < 0.5 else entier + 1)

# ---------- App ----------
root = tk.Tk()
root.title("Calculateur de dédommagement")
root.resizable(False, False)

# Thème / Style
style = ttk.Style()
try:
    style.theme_use("clam")
except:
    pass

style.configure("TFrame", padding=10)
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("Result.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("TButton", padding=(10, 6))
style.configure("Card.TLabelframe", padding=12)
style.configure("Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

container = ttk.Frame(root)
container.grid(row=0, column=0, padx=12, pady=12)

title = ttk.Label(container, text="Calculateur de dédommagement", style="Header.TLabel")
title.grid(row=0, column=0, sticky="w", pady=(0,8))

nb = ttk.Notebook(container)
nb.grid(row=1, column=0, sticky="nsew")

# ===== Onglet 1 : Dédos 5/15/30 =====
tab_partial = ttk.Frame(nb)
nb.add(tab_partial, text="Dédos 5/15/30")

frm_p_inputs = ttk.Labelframe(tab_partial, text="Paramètres", style="Card.TLabelframe")
frm_p_inputs.grid(row=0, column=0, sticky="nsew", padx=4, pady=6)

ttk.Label(frm_p_inputs, text="Total commande (€)").grid(row=0, column=0, sticky="e", padx=6, pady=6)
p_total = ttk.Entry(frm_p_inputs, width=18); p_total.grid(row=0, column=1, padx=6, pady=6)

ttk.Label(frm_p_inputs, text="Frais de livraison (€)").grid(row=1, column=0, sticky="e", padx=6, pady=6)
p_fdl = ttk.Entry(frm_p_inputs, width=18); p_fdl.grid(row=1, column=1, padx=6, pady=6)

ttk.Label(frm_p_inputs, text="Déduction").grid(row=2, column=0, sticky="e", padx=6, pady=6)
p_pct = ttk.Combobox(frm_p_inputs, values=["5%", "15%", "30%"], state="readonly", width=15)
p_pct.current(0); p_pct.grid(row=2, column=1, padx=6, pady=6)

frm_p_actions = ttk.Frame(tab_partial)
frm_p_actions.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
p_btn = ttk.Button(frm_p_actions, text="Calculer")
p_btn.grid(row=0, column=0, pady=2)

frm_p_out = ttk.Labelframe(tab_partial, text="Résultat", style="Card.TLabelframe")
frm_p_out.grid(row=2, column=0, sticky="nsew", padx=4, pady=6)
p_result = ttk.Label(frm_p_out, text="Remboursement : - €", style="Result.TLabel")
p_result.grid(row=0, column=0, sticky="w", padx=4, pady=4)

def calculer_partial(event=None):
    total_cmd = parse_float(p_total.get())
    fdl = parse_float(p_fdl.get())
    pct = float(p_pct.get().replace("%", ""))

    base_pct = (total_cmd + fdl) * (pct / 100.0)
    montant = arrondi_selon_regle(base_pct)
    if montant < 0:
        montant = 0.0
    p_result.config(text=f"Remboursement : {montant:.2f} €")

p_btn.config(command=calculer_partial)
for w in (p_total, p_fdl, p_pct):
    w.bind("<Return>", calculer_partial)

# Valeurs par défaut
p_total.insert(0, "0"); p_fdl.insert(0, "0")

# ===== Onglet 2 : Dédo 100% (sans FDL) =====
tab_full = ttk.Frame(nb)
nb.add(tab_full, text="Dédo 100%")

frm_f_inputs = ttk.Labelframe(tab_full, text="Paramètres", style="Card.TLabelframe")
frm_f_inputs.grid(row=0, column=0, sticky="nsew", padx=4, pady=6)

ttk.Label(frm_f_inputs, text="Total commande (€)").grid(row=0, column=0, sticky="e", padx=6, pady=6)
f_total = ttk.Entry(frm_f_inputs, width=18); f_total.grid(row=0, column=1, padx=6, pady=6)

ttk.Label(frm_f_inputs, text="Codes promo activés (€)").grid(row=1, column=0, sticky="e", padx=6, pady=6)
f_codes = ttk.Entry(frm_f_inputs, width=18); f_codes.grid(row=1, column=1, padx=6, pady=6)

ttk.Label(frm_f_inputs, text="Avoirs utilisés (€)").grid(row=2, column=0, sticky="e", padx=6, pady=6)
f_avoirs = ttk.Entry(frm_f_inputs, width=18); f_avoirs.grid(row=2, column=1, padx=6, pady=6)

frm_f_actions = ttk.Frame(tab_full)
frm_f_actions.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
f_btn = ttk.Button(frm_f_actions, text="Calculer")
f_btn.grid(row=0, column=0, pady=2)

frm_f_out = ttk.Labelframe(tab_full, text="Résultat", style="Card.TLabelframe")
frm_f_out.grid(row=2, column=0, sticky="nsew", padx=4, pady=6)
f_result = ttk.Label(frm_f_out, text="Remboursement : - €", style="Result.TLabel")
f_result.grid(row=0, column=0, sticky="w", padx=4, pady=4)

def calculer_full(event=None):
    total_cmd = parse_float(f_total.get())
    codes = parse_float(f_codes.get())
    avoirs = parse_float(f_avoirs.get())

    # FDL ignorés en 100%
    base = total_cmd
    if total_cmd <= 75:
        base += codes  # on rembourse "comme sans remise" si total <= 75 €
    montant = base - avoirs  # on déduit les avoirs
    if montant < 0:
        montant = 0.0
    # pas d'arrondi en 100%
    f_result.config(text=f"Remboursement : {montant:.2f} €")

f_btn.config(command=calculer_full)
for w in (f_total, f_codes, f_avoirs):
    w.bind("<Return>", calculer_full)

# Valeurs par défaut
f_total.insert(0, "0"); f_codes.insert(0, "0"); f_avoirs.insert(0, "0")

# Petit footer
footer = ttk.Label(container, text="Règles : 5/15/30 → (Total+FDL)×% puis arrondi spécial | 100% → Total (+codes si ≤75) – avoirs, sans arrondi.")
footer.grid(row=2, column=0, sticky="w", pady=(6,0))

root.mainloop()
