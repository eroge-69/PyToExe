import pyautogui
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

# Données aléatoires roumaines
noms = ["Popescu", "Ionescu", "Georgescu", "Stanescu", "Dumitrescu"]
prenoms = ["Andrei", "Maria", "Elena", "Ion", "Gabriela"]

coords = {
    "date_french": (100, 50),
    "date_today": (100, 100),
    "date_calc": (350, 100),
    "code": (100, 150),
    "texte1": (100, 200),
    "lettre_A": (100, 250),
    "texte3": (120, 250),
    "bloc_nom1": (100, 300),
    "bloc_nom2": (350, 300)
}

def date_en_francais(date_obj):
    mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin",
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return f"{date_obj.day} {mois_fr[date_obj.month - 1]} {date_obj.year}"

def generer_code():
    p1 = "".join(str(random.randint(1,9)) for _ in range(4))
    p2 = "".join(str(random.randint(1,9)) for _ in range(4))
    p3 = "".join(str(random.randint(1,9)) for _ in range(3))
    return f"F/{p1}/{p2}/{p3}"

def creer_bloc_nom(prenom, nom, adresse, code_postal, ville, prefixe_m=False):
    prefixe = "M. " if prefixe_m else ""
    return f"{prefixe}{prenom} {nom}\n{adresse}\n{code_postal} {ville}"

def ecrire(texte, pos):
    pyautogui.click(pos[0], pos[1])
    time.sleep(0.3)
    pyautogui.write(texte, interval=0.05)

def tester_positions():
    messagebox.showinfo("Info", "Place Paint au premier plan, outil texte actif.\nDébut dans 5 secondes...")
    time.sleep(5)
    for label, pos in coords.items():
        ecrire(f"[{label}]", pos)
        time.sleep(0.5)
    messagebox.showinfo("Test terminé", "✅ Positions testées !")

def lancer_ecriture():
    try:
        # Date aujourd’hui automatique ou manuelle
        if var_date_auto.get():
            today = datetime.today()
        else:
            today = datetime.strptime(entry_date_man.get(), "%d/%m/%Y")
    except Exception as e:
        messagebox.showerror("Erreur", f"Date invalide : {e}")
        return

    # Décalage mois
    try:
        decalage_mois = int(entry_mois.get())
        if decalage_mois not in [1, 3, 6, 12]:
            messagebox.showerror("Erreur", "Décalage mois doit être 1, 3, 6 ou 12.")
            return
    except:
        messagebox.showerror("Erreur", "Décalage mois invalide.")
        return

    # Nom/prénom
    if var_aleatoire_nom.get():
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
    else:
        prenom = entry_prenom.get().strip()
        nom = entry_nom.get().strip()
        if not prenom or not nom:
            messagebox.showerror("Erreur", "Prénom et nom doivent être remplis ou cochés aléatoire.")
            return

    # Adresse
    if var_aleatoire_adr.get():
        adresse = "121 RUE MANIN"
        cp = "75019"
        ville = "PARIS"
    else:
        adresse = entry_adresse.get().strip()
        cp = entry_cp.get().strip()
        ville = entry_ville.get().strip()
        if not adresse or not cp or not ville:
            messagebox.showerror("Erreur", "Adresse, CP et ville doivent être remplis ou cochés aléatoire.")
            return

    # Textes personnalisés
    texte1 = entry_texte1.get()
    texte3 = entry_texte3.get()

    # Calcul date + décalage - 1 jour
    date_calc = today + relativedelta(months=decalage_mois) - relativedelta(days=1)

    # Préparation textes à écrire
    date_french = f"Paris, le {date_en_francais(today)}"
    date_today_str = today.strftime("%d/%m/%Y")
    date_calc_str = date_calc.strftime("%d/%m/%Y")
    code = generer_code()
    bloc_nom_normal = creer_bloc_nom(prenom, nom, adresse, cp, ville, prefixe_m=False)
    bloc_nom_m = creer_bloc_nom(prenom, nom, adresse, cp, ville, prefixe_m=True)

    # Message de préparation
    messagebox.showinfo("Info", "Place Paint au premier plan, outil texte actif.\nDébut dans 5 secondes...")
    time.sleep(5)

    # Écriture sur Paint
    ecrire(date_french, coords["date_french"])
    ecrire(date_today_str, coords["date_today"])
    ecrire(date_calc_str, coords["date_calc"])
    ecrire(code, coords["code"])
    ecrire(texte1, coords["texte1"])
    ecrire("A", coords["lettre_A"])
    ecrire(texte3, coords["texte3"])
    ecrire(bloc_nom_normal, coords["bloc_nom1"])
    ecrire(bloc_nom_m, coords["bloc_nom2"])

    messagebox.showinfo("Terminé", "✅ Texte écrit sur Paint.")

# --- Interface graphique

root = tk.Tk()
root.title("Script écriture automatique Paint")

# Décalage mois
tk.Label(root, text="Décalage en mois (1,3,6,12) :").grid(row=0, column=0, sticky="e")
entry_mois = tk.Entry(root)
entry_mois.grid(row=0, column=1)
entry_mois.insert(0, "3")

# Texte 1
tk.Label(root, text="Texte A (personnalisé) :").grid(row=1, column=0, sticky="e")
entry_texte1 = tk.Entry(root)
entry_texte1.grid(row=1, column=1)
entry_texte1.insert(0, "Texte personnalisable A")

# Texte 3
tk.Label(root, text="Texte B (personnalisé) :").grid(row=2, column=0, sticky="e")
entry_texte3 = tk.Entry(root)
entry_texte3.grid(row=2, column=1)
entry_texte3.insert(0, "Texte personnalisé B")

# Nom/prénom
var_aleatoire_nom = tk.IntVar()
chk_nom = tk.Checkbutton(root, text="Utiliser nom/prénom aléatoires", variable=var_aleatoire_nom)
chk_nom.grid(row=3, column=0, columnspan=2, sticky="w")

tk.Label(root, text="Prénom :").grid(row=4, column=0, sticky="e")
entry_prenom = tk.Entry(root)
entry_prenom.grid(row=4, column=1)

tk.Label(root, text="Nom :").grid(row=5, column=0, sticky="e")
entry_nom = tk.Entry(root)
entry_nom.grid(row=5, column=1)

# Adresse
var_aleatoire_adr = tk.IntVar()
chk_adr = tk.Checkbutton(root, text="Utiliser adresse aléatoire (121 RUE MANIN, 75019 PARIS)", variable=var_aleatoire_adr)
chk_adr.grid(row=6, column=0, columnspan=2, sticky="w")

tk.Label(root, text="Adresse :").grid(row=7, column=0, sticky="e")
entry_adresse = tk.Entry(root)
entry_adresse.grid(row=7, column=1)
entry_adresse.insert(0, "121 RUE MANIN")

tk.Label(root, text="Code postal :").grid(row=8, column=0, sticky="e")
entry_cp = tk.Entry(root)
entry_cp.grid(row=8, column=1)
entry_cp.insert(0, "75019")

tk.Label(root, text="Ville :").grid(row=9, column=0, sticky="e")
entry_ville = tk.Entry(root)
entry_ville.grid(row=9, column=1)
entry_ville.insert(0, "PARIS")

# Date aujourd’hui auto ou manuelle
var_date_auto = tk.IntVar(value=1)
chk_date = tk.Checkbutton(root, text="Date d’aujourd’hui automatique", variable=var_date_auto)
chk_date.grid(row=10, column=0, columnspan=2, sticky="w")

tk.Label(root, text="Ou date manuelle (JJ/MM/AAAA) :").grid(row=11, column=0, sticky="e")
entry_date_man = tk.Entry(root)
entry_date_man.grid(row=11, column=1)

# Boutons
btn_tester = tk.Button(root, text="Tester positions dans Paint", command=tester_positions)
btn_tester.grid(row=12, column=0, pady=10)

btn_lancer = tk.Button(root, text="Lancer écriture sur Paint", command=lancer_ecriture)
btn_lancer.grid(row=12, column=1, pady=10)

root.mainloop()

