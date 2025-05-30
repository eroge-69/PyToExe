import tkinter as tk
from tkinter import ttk, messagebox
import math


def calculer():
    try:
        # Vérification que tous les champs sont remplis
        for key, entry in entries.items():
            if not entry.get():
                raise ValueError(f"Le champ {key} est vide")

        # Récupération des valeurs d'entrée
        ha = float(entries["ha"].get())
        bf = float(entries["bf"].get())
        Aa = float(entries["Aa"].get())
        Av = float(entries["Av"].get())
        Iy_a = float(entries["Iy_a"].get())
        fy = float(entries["fy"].get()) * 1000  # MPa -> kN/m²
        Ea = float(entries["Ea"].get()) * 1e6  # GPa -> kN/m²
        gamma_M0 = float(entries["gamma_M0"].get())

        fck = float(entries["fck"].get()) * 1000  # MPa -> kN/m²
        Ecm = float(entries["Ecm"].get()) * 1e6  # GPa -> kN/m²
        gamma_c = float(entries["gamma_c"].get())
        L = float(entries["L"].get())
        B = float(entries["B"].get())
        hc = float(entries["hc"].get())
        hp = float(entries["hp"].get())

        d = float(entries["d"].get())
        fu = float(entries["fu"].get()) * 1000  # MPa -> kN/m²
        Yv = float(entries["Yv"].get())
        alpha = float(entries["alpha"].get())
        nr = float(entries["nr"].get())
        bo = float(entries["bo"].get())

        gp = float(entries["gp"].get())
        gc = float(entries["gc"].get())
        gs = float(entries["gs"].get())
        qm = float(entries["qm"].get())

        # 1. Calcul des charges appliquées
        G = gp + gc + gs
        Q = qm
        PELU = 1.35 * G + 1.5 * Q
        PELS = G + Q

        # Mettre à jour les résultats
        resultats["gp_calc"].config(text=f"{gp:.2f}")
        resultats["gc_calc"].config(text=f"{gc:.2f}")
        resultats["gs_calc"].config(text=f"{gs:.2f}")
        resultats["qm_calc"].config(text=f"{qm:.2f}")
        resultats["PELU"].config(text=f"{PELU:.2f}")
        resultats["PELS"].config(text=f"{PELS:.2f}")

        # 2. Calcul de sollicitation
        MEd = PELU * L ** 2 / 8
        VEd = PELU * L / 2

        resultats["MEd"].config(text=f"{MEd:.2f}")
        resultats["VEd"].config(text=f"{VEd:.2f}")

        # 3. Vérification ELU
        beff = min(B, 2 * L / 8)
        fcd = fck / gamma_c
        Zpl = (fy * Aa) / (0.85 * fcd * beff)
        MplRd = (fy * Aa) * (ha / 2 + hc + hp - Zpl / 2)
        VplRd = (Av * fy / math.sqrt(3))

        # Résistance des connecteurs
        Prd1 = 0.85 * (fu / Yv) * (math.pi * d ** 2 / 4)
        Prd2 = 0.29 * alpha * d ** 2 * math.sqrt(fck * Ecm) / Yv
        Prd = min(Prd1, Prd2) / 1000  # kN

        Kt = 0.7 / nr * (bo / hp) * (ha / hp - 1)
        Nf = VEd / (Kt * Prd)

        # Mettre à jour les résultats ELU
        resultats["beff"].config(text=f"{beff:.4f}")
        resultats["Zpl"].config(text=f"{Zpl:.4f}")
        resultats["MplRd"].config(text=f"{MplRd:.2f}")
        resultats["VplRd"].config(text=f"{VplRd:.2f}")
        resultats["Prd"].config(text=f"{Prd:.2f}")
        resultats["Kt"].config(text=f"{Kt:.4f}")
        resultats["Nf"].config(text=f"{math.ceil(Nf)}")

        # 4. Vérification ELS
        n = Ea / Ecm  # Coefficient d'équivalence
        Ah = Aa + (beff * hc) / n
        Ze = (Aa * (ha / 2 + hp + hc) + (beff * hc ** 2) / (2 * n)) / Ah
        Ih = Iy_a + Aa * (Ze - ha / 2) ** 2 + (beff * hc ** 3) / (12 * n) + (beff * hc) / n * (Ze - hc / 2) ** 2

        # Calcul de la flèche
        delta = ((5 / 384) * (PELS * L ** 4) / (Ea * Ih)) * 1000  # en mm
        freq = 18 * 2 / math.sqrt(delta) if delta > 0 else 0  # Hz

        # Mettre à jour les résultats ELS
        resultats["Ah"].config(text=f"{Ah:.6f}")
        resultats["Ze"].config(text=f"{Ze:.4f}")
        resultats["Ih"].config(text=f"{Ih:.6f}")
        resultats["delta"].config(text=f"{delta:.2f} mm")
        resultats["freq"].config(text=f"{freq:.2f}")

        # 5. Vérifications finales
        verif_M = "OK" if MEd <= MplRd else "NON OK"
        verif_V = "OK" if VEd <= VplRd else "NON OK"
        verif_delta = "OK" if delta <= L * 1000 / 180 else "NON OK"
        verif_freq = "OK" if freq > 4 else "NON OK"

        # Mettre à jour avec couleurs
        resultats["verif_M"].config(text=verif_M, foreground="green" if verif_M == "OK" else "red")
        resultats["verif_V"].config(text=verif_V, foreground="green" if verif_V == "OK" else "red")
        resultats["verif_delta"].config(text=verif_delta, foreground="green" if verif_delta == "OK" else "red")
        resultats["verif_freq"].config(text=verif_freq, foreground="green" if verif_freq == "OK" else "red")

    except ValueError as ve:
        messagebox.showerror("Erreur de saisie", str(ve))
    except Exception as e:
        messagebox.showerror("Erreur de calcul", f"Une erreur est survenue:\n{str(e)}")


def reinitialiser():
    # Réinitialiser les champs d'entrée
    for entry in entries.values():
        entry.delete(0, tk.END)

    # Réinitialiser les résultats
    for result in resultats.values():
        result.config(text="", foreground="black")


# Création de la fenêtre principale
root = tk.Tk()
root.title("DIMENSIONNEMENT DES POUTRES MIXTES ACIER-BÉTON ISOSTATIQUES")
root.geometry("1400x900")  # Augmentation de la hauteur pour accommoder tous les résultats
root.configure(bg="#f0f8ff")

# Style
style = ttk.Style()
style.theme_use('clam')

# Configuration des styles
style.configure(".", background="#f0f8ff")
style.configure("TFrame", background="#f0f8ff")
style.configure("TLabel", background="#f0f8ff", font=("Arial", 10))
style.configure("Bold.TLabel", font=("Arial", 10, "bold"), background="#f0f8ff")
style.configure("Title.TLabel", font=("Arial", 14, "bold"), background="#f0f8ff", foreground="#0066cc")
style.configure("TButton", font=("Arial", 10), padding=5)
style.configure("TNotebook", background="#f0f8ff")
style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=6)

# Style des entrées
style.configure("TEntry", padding=5, width=15, font=("Arial", 10), fieldbackground="white", relief="solid",
                borderwidth=1)
style.map("TEntry",
          fieldbackground=[("active", "white"), ("!disabled", "white")],
          foreground=[("!disabled", "black")])

# Style des cadres de paramètres
style.configure("Param.TFrame", background="#ffffff", relief="solid", borderwidth=1, bordercolor="#99c2ff")
style.configure("Param.TLabel", background="#ffffff", font=("Arial", 10))

# Style des résultats
style.configure("Result.TFrame", background="#ffffff", relief="solid", borderwidth=1, bordercolor="#cccccc")
style.configure("Result.TLabel", background="#ffffff", relief="solid", borderwidth=1,
                padding=5, font=("Arial", 10), width=20, anchor="center")

# Boutons spéciaux
style.configure("Default.TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))  # Vert
style.configure("Calc.TButton", background="#2196F3", foreground="white", font=("Arial", 10, "bold"))  # Bleu
style.configure("Quit.TButton", background="#f44336", foreground="white", font=("Arial", 10, "bold"))  # Rouge

# Header
header_frame = ttk.Frame(root, style="TFrame")
header_frame.pack(fill="x", padx=10, pady=10)

title_label = ttk.Label(header_frame,
                        text="DIMENSIONNEMENT DES POUTRES MIXTES ACIER-BÉTON ISOSTATIQUES",
                        style="Title.TLabel")
title_label.pack()

# Boutons placés juste en dessous du titre
btn_frame_top = ttk.Frame(root, style="TFrame")
btn_frame_top.pack(fill="x", padx=10, pady=(0, 10))

ttk.Button(btn_frame_top, text="Calculer", command=calculer, style="Calc.TButton", width=15).pack(side="left", padx=20,
                                                                                                  pady=5)
ttk.Button(btn_frame_top, text="Réinitialiser", command=reinitialiser, style="Default.TButton", width=15).pack(
    side="left", padx=20, pady=5)
ttk.Button(btn_frame_top, text="Quitter", command=root.destroy, style="Quit.TButton", width=15).pack(side="right",
                                                                                                     padx=20, pady=5)

# Création des onglets
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=5)

# Onglet pour les paramètres d'entrée
input_tab = ttk.Frame(notebook, style="TFrame")
notebook.add(input_tab, text="Paramètres d'entrée")

# Onglet pour les résultats
result_tab = ttk.Frame(notebook, style="TFrame")
notebook.add(result_tab, text="Résultats")

# --- CONTENU ONGLET PARAMÈTRES ---
input_frame = ttk.Frame(input_tab, style="TFrame")
input_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Colonnes pour les paramètres (3 colonnes)
param_col1 = ttk.Frame(input_frame, style="TFrame")
param_col1.pack(side="left", fill="both", expand=True, padx=10)

param_col2 = ttk.Frame(input_frame, style="TFrame")
param_col2.pack(side="left", fill="both", expand=True, padx=10)

param_col3 = ttk.Frame(input_frame, style="TFrame")
param_col3.pack(side="left", fill="both", expand=True, padx=10)

# --- DONNÉES D'ENTRÉE ---
entries = {}


def create_param_frame(parent, text, key):
    frame = ttk.Frame(parent, style="Param.TFrame")
    frame.pack(fill="x", pady=3)

    label = ttk.Label(frame, text=text, style="Param.TLabel", width=25)
    label.pack(side="left", padx=5)

    entry = ttk.Entry(frame, width=15, style="TEntry")
    entry.pack(side="right", padx=5)

    entries[key] = entry
    return frame


# Profil acier (Colonne 1)
profil_frame = ttk.LabelFrame(param_col1, text="Profilé acier", padding=10, style="TFrame")
profil_frame.pack(fill="both", expand=True, pady=5)

params_profil = [
    ("Hauteur ha [m]", "ha"), ("Largeur bf [m]", "bf"),
    ("Épaisseur tw [m]", "tw"), ("Épaisseur tf [m]", "tf"),
    ("Rayon r [m]", "r"), ("Aire Aa [m²]", "Aa"),
    ("Aire Av [m²]", "Av"), ("Inertie Iy,a [m⁴]", "Iy_a"),
    ("Inertie Iz,a [m⁴]", "Iz_a"), ("Rayon iz,a [m]", "iz_a"),
    ("Limite fy [MPa]", "fy"), ("Module Ea [GPa]", "Ea"),
    ("Coeff. γM0", "gamma_M0")
]

for text, key in params_profil:
    create_param_frame(profil_frame, text, key)

# Béton (Colonne 2)
beton_frame = ttk.LabelFrame(param_col2, text="Béton", padding=10, style="TFrame")
beton_frame.pack(fill="both", expand=True, pady=5)

params_beton = [
    ("Résistance fck [MPa]", "fck"), ("Module Ecm [GPa]", "Ecm"),
    ("Coeff. γc", "gamma_c"), ("Longueur L [m]", "L"),
    ("Largeur B [m]", "B"), ("Épaisseur hc [m]", "hc"),
    ("Hauteur hp [m]", "hp")
]

for text, key in params_beton:
    create_param_frame(beton_frame, text, key)

# Connecteurs et Charges (Colonne 3)
connect_frame = ttk.LabelFrame(param_col3, text="Connecteurs", padding=10, style="TFrame")
connect_frame.pack(fill="both", expand=True, pady=5)

params_connect = [
    ("Diamètre d [m]", "d"), ("Hauteur hsc [m]", "hsc"),
    ("Résistance fu [MPa]", "fu"), ("Coeff. γv", "Yv"),
    ("Coeff. α", "alpha"), ("Nb rangées nr", "nr"),
    ("Distance bo [m]", "bo")
]

for text, key in params_connect:
    create_param_frame(connect_frame, text, key)

charge_frame = ttk.LabelFrame(param_col3, text="Charges [kN/m]", padding=10, style="TFrame")
charge_frame.pack(fill="both", expand=True, pady=5)

params_charge = [
    ("Poids solive gp", "gp"), ("Poids dalle gc", "gc"),
    ("Finition gf", "gs"), ("Exploitation q", "qm")
]

for text, key in params_charge:
    create_param_frame(charge_frame, text, key)

# --- CONTENU ONGLET RÉSULTATS ---
result_frame = ttk.Frame(result_tab, style="TFrame")
result_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Colonnes pour les résultats (2 colonnes)
result_col1 = ttk.Frame(result_frame, style="TFrame")
result_col1.pack(side="left", fill="both", expand=True, padx=10)

result_col2 = ttk.Frame(result_frame, style="TFrame")
result_col2.pack(side="left", fill="both", expand=True, padx=10)

# --- RÉSULTATS ---
resultats = {}


def create_result_frame(parent, text, key):
    frame = ttk.Frame(parent, style="Result.TFrame")
    frame.pack(fill="x", pady=3)

    label = ttk.Label(frame, text=text, style="Param.TLabel", width=30)
    label.pack(side="left", padx=5)

    result = ttk.Label(frame, text="", style="Result.TLabel", width=20)
    result.pack(side="right", padx=5, fill="x", expand=True)

    resultats[key] = result
    return frame


# Résultats ELU (Colonne 1)
elu_frame = ttk.LabelFrame(result_col1, text="Résultats ELU", padding=10, style="TFrame")
elu_frame.pack(fill="both", expand=True, pady=5)

results_elu = [
    ("Poids solive gp [kN/m]", "gp_calc"),
    ("Poids dalle gc [kN/m]", "gc_calc"),
    ("Finition gf [kN/m]", "gs_calc"),
    ("Exploitation q [kN/m]", "qm_calc"),
    ("Charge PELU [kN/m]", "PELU"),
    ("Charge PELS [kN/m]", "PELS"),
    ("Moment MEd [kN.m]", "MEd"),
    ("Effort tranchant VEd [kN]", "VEd"),
    ("Largeur efficace beff [m]", "beff"),
    ("Hauteur Zpl [m]", "Zpl"),
    ("Moment résistant MplRd [kN.m]", "MplRd"),
    ("Effort tranchant résistant VplRd [kN]", "VplRd"),
    ("Résistance connecteur Prd [kN]", "Prd"),
    ("Coefficient Kt", "Kt"),
    ("Nombre de connecteurs Nf", "Nf")
]

for text, key in results_elu:
    create_result_frame(elu_frame, text, key)

# Résultats ELS (Colonne 2)
els_frame = ttk.LabelFrame(result_col2, text="Résultats ELS", padding=10, style="TFrame")
els_frame.pack(fill="both", expand=True, pady=5)

results_els = [
    ("Aire homogénéisée Ah [m²]", "Ah"),
    ("Axe neutre Ze [m]", "Ze"),
    ("Inertie homogénéisée Ih [m⁴]", "Ih"),
    ("Flèche δ [mm]", "delta"),
    ("Fréquence propre f [Hz]", "freq"),
    ("Vérif. moment MEd ≤ MplRd", "verif_M"),
    ("Vérif. effort tranchant VEd ≤ VplRd", "verif_V"),
    ("Vérif. flèche δ ≤ L/250", "verif_delta"),
    ("Vérif. fréquence f > 4Hz", "verif_freq")
]

for text, key in results_els:
    create_result_frame(els_frame, text, key)

root.mainloop()

