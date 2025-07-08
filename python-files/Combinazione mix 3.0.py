import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product

oggetti = [
    {"nome": "KN2", "costo": 0.0760, "SCT": 2.21},
    {"nome": "PB4", "costo": 0.1301, "SCT": 2.74},
    {"nome": "KB3", "costo": 0.1014, "SCT": 2.46},
    {"nome": "K2", "costo": 0.0825, "SCT": 2.28},
    {"nome": "S4", "costo": 0.0775, "SCT": 2.54},
    {"nome": "K5", "costo": 0.1024, "SCT": 3.18},
    {"nome": "S9", "costo": 0.1080, "SCT": 3.64},
]

carte_da_escludere = {"KB3", "PB4"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generatore combinazioni")
        self.geometry("1100x700")

        self.dati = []
        self.ordina_direzione = {}
        self.tree = None
        self.usa_onde_var = tk.BooleanVar(value=False)

        self.crea_campi_input()
        self.aggiorna_coefficienti()

    def crea_campi_input(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        # Campi di input
        entries = [
            ("Target (ECT):", "10", "target_ECT_entry"),
            ("Target (€):", "0.4829", "target_entry"),
            ("Copertina:", "KB3", "copertina_entry"),
            ("Copertina Int:", "K5", "copertina_int_entry")
        ]
        for idx, (label, default, attr) in enumerate(entries):
            tk.Label(frame, text=label).grid(row=0, column=idx, padx=20)
            entry = tk.Entry(frame, width=10)
            entry.insert(0, default)
            entry.grid(row=1, column=idx, padx=10)
            setattr(self, attr, entry)

        # Profilo + coefficienti
        tk.Label(frame, text="Onda:").grid(row=0, column=4, padx=20)
        self.profilo_var = tk.StringVar()
        self.profilo_combo = ttk.Combobox(frame, textvariable=self.profilo_var, state="readonly", width=8)
        self.profilo_combo['values'] = ("EB", "BC", "C", "B", "E")
        self.profilo_combo.current(0)
        self.profilo_combo.grid(row=1, column=4, padx=5)
        self.profilo_combo.bind("<<ComboboxSelected>>", self.aggiorna_coefficienti)

        tk.Label(frame, text="Coeff. 2°:").grid(row=0, column=5, padx=20)
        self.coeff2_entry = tk.Entry(frame, width=6, state="readonly")
        self.coeff2_entry.grid(row=1, column=5, padx=2)

        tk.Label(frame, text="Coeff. 4°:").grid(row=0, column=6, padx=20)
        self.coeff4_entry = tk.Entry(frame, width=6, state="readonly")
        self.coeff4_entry.grid(row=1, column=6, padx=2)

        tk.Button(frame, text="Calcola Target €", command=self.calcola_costi).grid(row=0, column=7, padx=30, pady=15)
        tk.Button(frame, text="Calcola Target ECT", command=self.calcola_ECT).grid(row=1, column=7, padx=30)

        tk.Checkbutton(frame, text="Esplora onde automaticamente", variable=self.usa_onde_var, wraplength=100).grid(row=0, column=8, rowspan=3, pady=5)

        
    def aggiorna_coefficienti(self, event=None):
        profilo = self.profilo_var.get()
        profili_5 = {"EB": (1.25, 1.37), "BC": (1.37, 1.46)}
        profili_3 = {"C": 1.46, "B": 1.37, "E": 1.25}

        if profilo in profili_5:
            coeff2, coeff4 = profili_5[profilo]
            self.lunghezza_combinazione = 5
        else:
            coeff2 = profili_3.get(profilo, 1.0)
            coeff4 = None
            self.lunghezza_combinazione = 3

        self.coeff2_entry.config(state="normal")
        self.coeff2_entry.delete(0, tk.END)
        self.coeff2_entry.insert(0, str(coeff2))
        self.coeff2_entry.config(state="readonly")

        self.coeff4_entry.config(state="normal")
        self.coeff4_entry.delete(0, tk.END)
        self.coeff4_entry.insert(0, str(coeff4) if coeff4 is not None else "-")
        self.coeff4_entry.config(state="readonly")

    def calcola_combinazioni(self, target, is_ECT=False):
        try:
            coeff_2 = float(self.coeff2_entry.get())
            coeff_4 = float(self.coeff4_entry.get()) if self.coeff4_entry.get().replace(".", "", 1).isdigit() else None
            carta_fissa = next(o for o in oggetti if o["nome"] == self.copertina_entry.get().strip())
            carta_int = next(o for o in oggetti if o["nome"] == self.copertina_int_entry.get().strip())
        except (ValueError, StopIteration):
            messagebox.showerror("Errore", "Controlla input numerici o nomi oggetti.")
            return []

        combinazioni = []
        for comb in product(oggetti, repeat=self.lunghezza_combinazione - 2):
            if any(x["nome"] in carte_da_escludere for x in comb):
                continue

            completa = (carta_fissa,) + comb + (carta_int,)
            costo, ect = 0, 0
            for i, item in enumerate(completa):
                coeff = coeff_2 if i == 1 else coeff_4 if i == 3 and coeff_4 else 1
                costo += item["costo"] * coeff
                ect += item["SCT"] * coeff

            valore = ect if is_ECT else costo
            diff = abs(target - valore)
            val = "****" if diff < 0.0001 else "+" if (target - valore) < 0 else "-"
            if coeff_2 == 1.25 :
                if coeff_4 == 1.37 :
                    Onda = "EB"
                else :
                    Onda = "E"
            elif coeff_2 == 1.37 :
                if coeff_4 == 1.46 :
                    Onda = "BC"
                else :
                    Onda = "B"
            else :
                Onda = "C"


            combinazioni.append({
                "delta": diff,
                "costo": costo,
                "ECT": ect,
                "val": val,
                "onda": Onda,
                "oggetti": ', '.join(x["nome"] for x in completa),
            })

        ordinamento = (lambda x: (x["delta"], -x["ECT"])) if not is_ECT else (lambda x: (x["delta"], x["costo"]))
        return sorted(combinazioni, key=ordinamento)[:20]
    
    def calcola_combinazioni_Onda(self, target, is_ECT=False):
        try:
            carta_fissa = next(o for o in oggetti if o["nome"] == self.copertina_entry.get().strip())
            carta_int = next(o for o in oggetti if o["nome"] == self.copertina_int_entry.get().strip())
        except (ValueError, StopIteration):
            messagebox.showerror("Errore", "Controlla input numerici o nomi oggetti.")
            return []
        
        combinazioni = []
        for profilo in self.profilo_combo['values'] :  

            if profilo == "EB":
                coeff_22 = 1.25
                coeff_44 = 1.37
                Onda = "EB"
                lunghezza_combinazione = 5
            elif profilo == "BC":
                coeff_22 = 1.37
                coeff_44 = 1.46
                Onda = "BC"
                lunghezza_combinazione = 5
            elif profilo == "EC":
                coeff_22 = 1.25
                coeff_44 = 1.46
                Onda = "EC"
                lunghezza_combinazione = 5
            elif profilo == "B":
                coeff_22 = 1.37
                coeff_44 = None
                Onda = "B"
                lunghezza_combinazione = 3
            elif profilo == "C":
                coeff_22 = 1.46
                coeff_44 = None
                Onda = "C"
                lunghezza_combinazione = 3
            elif profilo == "E":
                coeff_22 = 1.25
                coeff_44 = None
                Onda = "E"
                lunghezza_combinazione = 3

            
            for comb in product(oggetti, repeat=lunghezza_combinazione - 2):
                if any(x["nome"] in carte_da_escludere for x in comb):
                    continue

                completa = (carta_fissa,) + comb + (carta_int,)
                costo, ect = 0, 0
                for i, item in enumerate(completa):
                    coeff = coeff_22 if i == 1 else coeff_44 if i == 3 and coeff_44 else 1
                    costo += item["costo"] * coeff
                    ect += item["SCT"] * coeff

                valore = ect if is_ECT else costo
                diff = abs(target - valore)
                val = "****" if diff < 0.0001 else "+" if (target - valore) < 0 else "-"
                
                combinazioni.append({
                    "delta": diff,
                    "costo": costo,
                    "ECT": ect,
                    "val": val,
                    "onda": Onda,
                    "oggetti": ', '.join(x["nome"] for x in completa),
                })

        ordinamento = (lambda x: (x["delta"], -x["ECT"])) if not is_ECT else (lambda x: (x["delta"], x["costo"]))
        return sorted(combinazioni, key=ordinamento)[:20]

    def calcola_costi(self):
        try:
            target = float(self.target_entry.get())
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un valore numerico valido per il target €.")
            return

        if self.usa_onde_var.get():
            self.dati = self.calcola_combinazioni_Onda(target, is_ECT=False)
        else:
            self.dati = self.calcola_combinazioni(target, is_ECT=False)
        
        self.mostra_tabella("costi")

    def calcola_ECT(self):
        try:
            target = float(self.target_ECT_entry.get())
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un valore numerico valido per il target ECT.")
            return

        if self.usa_onde_var.get():
            self.dati = self.calcola_combinazioni_Onda(target, is_ECT=True)
        else:
            self.dati = self.calcola_combinazioni(target, is_ECT=True)

        self.mostra_tabella("ECT")

    def mostra_tabella(self, tipo):
        if self.tree:
            self.tree.destroy()

        self.tree = ttk.Treeview(self, show="headings")
        colonne = {
            "costi": [("costo", "Costo Totale"), ("val", "Scost"), ("delta", "Delta (€)"), ("ECT", "ECT (kN/m)"), ("onda","Onda"), ("oggetti", "Carte")],
            "ECT": [("ECT", "ECT (kN/m)"), ("val", "Scost"), ("delta", "Delta (kN/m)"), ("costo", "Costo Totale"), ("onda","Onda"), ("oggetti", "Carte")]
        }[tipo]

        self.tree["columns"] = [c[0] for c in colonne]
        for col, title in colonne:
            self.tree.heading(col, text=title, command=lambda c=col: self.ordina_colonna(c, tipo))
            self.tree.column(col, width=130 if col != "oggetti" else 450, anchor="center")

        style = ttk.Style(self)
        style.configure("Treeview", font=("Helvetica", 12))
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
        self.tree.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)

        self.popola_tabella(tipo)

    def popola_tabella(self, tipo):
        self.tree.delete(*self.tree.get_children())
        for i, d in enumerate(self.dati, 1):
            self.tree.insert("", "end", iid=i, values=(
                f"{d['costo']:.4f}" if tipo == "costi" else f"{d['ECT']:.4f}",
                d["val"],
                f"{d['delta']:.4f}",
                f"{d['ECT']:.2f}" if tipo == "costi" else f"{d['costo']:.2f}",
                d["onda"],
                d["oggetti"]
            ))

    def ordina_colonna(self, col, tipo):
        reverse = not self.ordina_direzione.get(col, False)
        self.ordina_direzione[col] = reverse
        self.dati.sort(key=lambda x: x[col] if isinstance(x[col], (int, float)) else x[col].lower(), reverse=reverse)
        self.popola_tabella(tipo)


if __name__ == "__main__":
    app = App()
    app.mainloop()