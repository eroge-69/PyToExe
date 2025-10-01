
"""
integrated_artillery_simulator_fr.py
Version française complète.
Voir les commentaires dans le code.
"""

import os, re, json, csv, sys
from collections import defaultdict
try:
    from docx import Document
except Exception:
    Document = None

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except Exception:
    tk = None

# Configuration
DATA_FOLDER = "/mnt/data"
OUTPUT_FOLDER = "/mnt/data/processed_simulator_output_fr"
EXT_SUPPORTES = (".docx", ".txt", ".csv")

MOTS_CLE_METHODES = {
    "chronometre": ["chronometre", "chronomètre", "reglage de tire par chronometre", "par chronometre"],
    "observation_conjuguee": ["observation conjuguée", "observation conjuguee", "observation conjuguée", "observation conjugue"],
    "telemetre": ["télémètre", "telemetre", "par telemetre"],
    "signes_eclatements": ["signes d'éclatements", "signes d eclatements", "signes d'éclatement"],
    "station_radar": ["station radar", "radar"],
    "explosion_aerienne": ["explosion aérienne", "explosion aerienne", "explosion"]
}

MOTS_CLE_SYSTEMES = {
    "BM21": ["bm21", "bm-21"],
    "D30": ["d30", "d-30"],
    "Mortier": ["mortier", "mortar"],
    "Generic": []
}

# Regex pour anonymisation
RE_COORD = re.compile(r"\\b\\d{1,3}[°º]?\\s*[0-9.,]*\\s*[NSEW]?\\b", re.I)
RE_DECIMAL = re.compile(r"\\b\\d{1,3}\\.\\d{3,10}\\b")
RE_NUM = re.compile(r"\\b\\d{1,6}(?:[.,]\\d{1,6})?\\b")
RE_TIME = re.compile(r"\\b(?:[01]?\\d|2[0-3])[:h][0-5]\\d\\b")
TERMES_SENSIBLES = [r"\\b(coord|coordinate|إحداثيات|COORD|GRID|GRD|UTM|MGRS)\\b", r"\\b(latitude|longitude|خط العرض|خط الطول)\\b"]

# Fonctions de lecture
def lire_txt(chemin):
    with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f.readlines() if ln.strip()]

def lire_docx(chemin):
    if Document is None:
        raise RuntimeError("python-docx n'est pas installé. Installez via 'pip install python-docx'")
    doc = Document(chemin)
    lignes = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            lignes.append(t)
    return lignes

def lire_csv(chemin):
    lignes = []
    with open(chemin, newline='', encoding="utf-8", errors="ignore") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                lignes.append(" ".join(row).strip())
    return lignes

# Anonymisation
def anonymiser_texte(txt):
    original = txt
    txt = RE_DECIMAL.sub("<COORD>", txt)
    txt = RE_COORD.sub("<COORD>", txt)
    txt = RE_TIME.sub("<TIME>", txt)
    txt = RE_NUM.sub("<NUM>", txt)
    for pat in TERMES_SENSIBLES:
        if re.search(pat, original, re.I):
            return "[SENSITIVE] " + txt
    return txt

# Détection méthode et système
def detecter_methode(nom_fichier, texte):
    fname = nom_fichier.lower()
    for methode, kws in MOTS_CLE_METHODES.items():
        for kw in kws:
            if kw.lower() in fname or kw.lower() in texte.lower():
                return methode
    return "inconnue"

def detecter_systeme(nom_fichier, texte):
    fname = nom_fichier.lower()
    for tag, kws in MOTS_CLE_SYSTEMES.items():
        for kw in kws:
            if kw.lower() in fname or kw.lower() in texte.lower():
                return tag
    if "d30" in fname or "d-30" in fname:
        return "D30"
    if "bm21" in fname or "bm-21" in fname:
        return "BM21"
    if "mortier" in fname or "mort" in fname:
        return "Mortier"
    return "Generic"

# Traitement fichier
def traiter_fichier(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        lignes = lire_txt(path)
    elif ext == ".docx":
        lignes = lire_docx(path)
    elif ext == ".csv":
        lignes = lire_csv(path)
    else:
        return []
    entrees = []
    nom = os.path.basename(path)
    for ln in lignes:
        if not ln or len(ln.strip()) < 2:
            continue
        sanit = anonymiser_texte(ln)
        methode = detecter_methode(nom, ln)
        systeme = detecter_systeme(nom, ln)
        sensible = sanit.startswith("[SENSITIVE]")
        entrees.append({
            "original": ln,
            "sanitized": sanit,
            "methode": methode,
            "systeme": systeme,
            "sensitive": sensible
        })
    return entrees

# Construction DB
def construire_base(data_folder=DATA_FOLDER):
    db = defaultdict(list)
    lexique = defaultdict(int)
    revue = []
    fichiers = []
    for root, dirs, filenames in os.walk(data_folder):
        for fn in filenames:
            if fn.lower().endswith(EXT_SUPPORTES):
                fichiers.append(os.path.join(root, fn))
    for path in sorted(fichiers):
        try:
            entrees = traiter_fichier(path)
        except Exception as e:
            print("Erreur lecture:", path, e)
            continue
        scenario = os.path.splitext(os.path.basename(path))[0]
        comptes_methode = defaultdict(int)
        comptes_systeme = defaultdict(int)
        for e in entrees:
            comptes_methode[e['methode']] += 1
            comptes_systeme[e['systeme']] += 1
        methode = max(comptes_methode, key=comptes_methode.get) if comptes_methode else "inconnue"
        systeme = max(comptes_systeme, key=comptes_systeme.get) if comptes_systeme else "Generic"
        pas = []
        for e in entrees:
            step = {
                "scenario_file": scenario,
                "original": e["original"],
                "sanitized": e["sanitized"],
                "sensitive": e["sensitive"]
            }
            pas.append(step)
            lexique[e["sanitized"]] += 1
            if e["sensitive"]:
                revue.append({"file": scenario, "line": e["original"], "sanitized": e["sanitized"]})
        db[(methode, systeme)].append({"scenario": scenario, "steps": pas})
    return db, lexique, revue

# Sauvegarde sorties
def sauvegarder_outputs(db, lexique, revue, output_folder=OUTPUT_FOLDER):
    os.makedirs(output_folder, exist_ok=True)
    out_db = {}
    for (methode, systeme), scenarios in db.items():
        key = f"{methode}__{systeme}"
        out_db[key] = scenarios
    chemin_json = os.path.join(output_folder, "scenarios_grouped_fr.json")
    with open(chemin_json, "w", encoding="utf-8") as jf:
        json.dump(out_db, jf, ensure_ascii=False, indent=2)
    chemin_lex = os.path.join(output_folder, "lexique.csv")
    with open(chemin_lex, "w", encoding="utf-8", newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["phrase_sanitized","count"])
        for phrase, cnt in lexique.items():
            writer.writerow([phrase, cnt])
    chemin_rev = os.path.join(output_folder, "review_pending_fr.csv")
    with open(chemin_rev, "w", encoding="utf-8", newline='') as rf:
        writer = csv.writer(rf)
        writer.writerow(["file","original_line","sanitized"])
        for r in revue:
            writer.writerow([r["file"], r["line"], r["sanitized"]])
    return chemin_json, chemin_lex, chemin_rev

# Interface graphique
class InterfaceSim:
    def __init__(self, master, db, output_folder=OUTPUT_FOLDER):
        self.master = master
        self.master.title("Simulateur d'ordres — Artillerie (FR)")
        self.db = db
        self.output_folder = output_folder
        self.creer_widgets()
        self.remplir_methodes()

    def creer_widgets(self):
        frm = ttk.Frame(self.master, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Choisir la méthode d'ajustement :").grid(row=0, column=0, sticky="w")
        self.methode_var = tk.StringVar()
        self.methode_cb = ttk.Combobox(frm, textvariable=self.methode_var, state="readonly", width=50)
        self.methode_cb.grid(row=1, column=0, sticky="w")
        self.methode_cb.bind("<<ComboboxSelected>>", self.on_methode_sel)
        ttk.Label(frm, text="Choisir le système :").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.systeme_var = tk.StringVar()
        self.systeme_cb = ttk.Combobox(frm, textvariable=self.systeme_var, state="readonly", width=50)
        self.systeme_cb.grid(row=3, column=0, sticky="w")
        self.systeme_cb.bind("<<ComboboxSelected>>", self.on_systeme_sel)
        ttk.Label(frm, text="Scénarios disponibles :").grid(row=4, column=0, sticky="w", pady=(8,0))
        self.list_scenarios = tk.Listbox(frm, height=8, width=90)
        self.list_scenarios.grid(row=5, column=0, sticky="w")
        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=6, column=0, pady=8, sticky="w")
        ttk.Button(btn_frm, text="Reconstruire DB", command=self.reconstruire_db).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frm, text="Aperçu scénario", command=self.apercu_scenario).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frm, text="Démarrer simulation", command=self.lancer_simulation).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frm, text="Exporter scénario JSON", command=self.exporter_scenario).grid(row=0, column=3, padx=4)
        ttk.Button(btn_frm, text="Ouvrir dossier sorties", command=self.ouvrir_dossier_sorties).grid(row=0, column=4, padx=4)
        ttk.Label(frm, text="Aperçu / Journal :").grid(row=7, column=0, sticky="w")
        self.zone_log = tk.Text(frm, height=12, width=100, wrap="word")
        self.zone_log.grid(row=8, column=0, sticky="w")
        self.zone_log.insert("1.0", "Bienvenue — sélectionnez une méthode puis un système pour voir les scénarios.\n")
        self.zone_log.configure(state=tk.DISABLED)

    def remplir_methodes(self):
        methodes = sorted(set([m for (m,s) in self.db.keys()]))
        if not methodes:
            methodes = ["(aucune)"]
        self.methode_cb['values'] = methodes
        if methodes:
            self.methode_cb.current(0)
            self.on_methode_sel()

    def on_methode_sel(self, event=None):
        methode = self.methode_var.get()
        systemes = sorted(set([s for (m,s) in self.db.keys() if m==methode]))
        if not systemes:
            systemes = ["(aucun)"]
        self.systeme_cb['values'] = systemes
        if systemes:
            self.systeme_cb.current(0)
            self.on_systeme_sel()

    def on_systeme_sel(self, event=None):
        methode = self.methode_var.get()
        systeme = self.systeme_var.get()
        key = (methode, systeme)
        self.list_scenarios.delete(0, tk.END)
        items = self.db.get(key, [])
        for sc in items:
            self.list_scenarios.insert(tk.END, sc["scenario"])

    def reconstruire_db(self):
        self.log("Reconstruction de la base...")
        db, lex, rev = construire_base(DATA_FOLDER)
        self.db = db
        self.log(f"Base reconstruite. {sum(len(v) for v in db.values())} scénarios chargés.")
        self.remplir_methodes()

    def get_scenario_selectionne(self):
        sel = self.list_scenarios.curselection()
        if not sel:
            messagebox.showwarning("Avertissement", "Sélectionnez un scénario.")
            return None
        idx = sel[0]
        methode = self.methode_var.get()
        systeme = self.systeme_var.get()
        key = (methode, systeme)
        items = self.db.get(key, [])
        if idx >= len(items):
            return None
        return items[idx]

    def apercu_scenario(self):
        obj = self.get_scenario_selectionne()
        if not obj:
            return
        self.zone_log.configure(state=tk.NORMAL)
        self.zone_log.delete("1.0", tk.END)
        self.zone_log.insert(tk.END, f"Scénario: {obj['scenario']}\n\n")
        for i, st in enumerate(obj['steps'], start=1):
            marker = "[SENSIBLE]" if st['sensitive'] else ""
            self.zone_log.insert(tk.END, f"{i}. {st['sanitized']} {marker}\n")
        self.zone_log.configure(state=tk.DISABLED)

    def lancer_simulation(self):
        obj = self.get_scenario_selectionne()
        if not obj:
            return
        self.log("--- Début simulation: " + obj['scenario'] + " ---")
        for i, st in enumerate(obj['steps'], start=1):
            marker = "[SENSIBLE]" if st['sensitive'] else ""
            self.log(f"{i}. {st['sanitized']} {marker}")
            self.master.update()
            self.master.after(600)
        self.log("--- Fin simulation ---")

    def exporter_scenario(self):
        obj = self.get_scenario_selectionne()
        if not obj:
            return
        fn = f"{obj['scenario']}_export.json".replace(" ", "_")
        path = os.path.join(self.output_folder, fn)
        with open(path, "w", encoding="utf-8") as jf:
            json.dump(obj, jf, ensure_ascii=False, indent=2)
        messagebox.showinfo("Export", f"Scénario exporté:\n{path}")
        self.log(f"Exporté: {path}")

    def ouvrir_dossier_sorties(self):
        try:
            import subprocess, platform
            if platform.system() == "Windows":
                os.startfile(self.output_folder)
            elif platform.system() == "Darwin":
                subprocess.call(["open", self.output_folder])
            else:
                subprocess.call(["xdg-open", self.output_folder])
        except Exception as e:
            messagebox.showinfo("Info", f"Dossier de sortie: {self.output_folder}\n(Ouvrir manuellement si nécessaire)")

    def log(self, msg):
        self.zone_log.configure(state=tk.NORMAL)
        self.zone_log.insert(tk.END, msg + "\\n")
        self.zone_log.see(tk.END)
        self.zone_log.configure(state=tk.DISABLED)

# Exécution principale
def main_cli_build_and_save():
    print("Construction de la base depuis:", DATA_FOLDER)
    db, lex, review = construire_base(DATA_FOLDER)
    chemin_json, chemin_lex, chemin_rev = sauvegarder_outputs(db, lex, review, OUTPUT_FOLDER)
    print("Sorties sauvegardées:")
    print(" -", chemin_json)
    print(" -", chemin_lex)
    print(" -", chemin_rev)
    print("Pour lancer l'interface graphique localement: python integrated_artillery_simulator_fr.py gui")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "gui":
        db, lex, review = construire_base(DATA_FOLDER)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        sauvegarder_outputs(db, lex, review, OUTPUT_FOLDER)
        if tk is None:
            print("Tkinter non disponible dans cet environnement. Les fichiers de sortie ont été créés.")
            sys.exit(0)
        root = tk.Tk()
        app = InterfaceSim(root, db, OUTPUT_FOLDER)
        root.mainloop()
    else:
        main_cli_build_and_save()
