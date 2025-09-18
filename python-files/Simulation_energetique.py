import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

def sim_conso(strat, puis, plg_h=None, tx_occ=None):
    h_sem = 168
    p_inst = np.full(h_sem, puis[1])
    p100, p_v = puis

    if strat == 1:
        p_inst.fill(p100)
    
    elif strat in [2, 3] and plg_h:
        for j in range(7):
            deb, fin = plg_h[j]
            if fin > deb:
                idx = range(j * 24 + deb, j * 24 + min(fin, 24))
                
                if strat == 2:
                    p_inst[list(idx)] = p100
                else:
                    nb_h = int(round(len(idx) * tx_occ / 100))
                    h_occ = random.sample(list(idx), nb_h)
                    p_inst[h_occ] = p100

    return p_inst, np.cumsum(p_inst) / 1000

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulation Énergétique de la Ventilation - STI2D EE")
        self.geometry("1200x850")
        
        self._cr_lay()
        self._cr_ctrl()
        self._cr_plot()
        self.upd_ui()

    def _cr_lay(self):
        self.bot_f = ttk.Frame(self, height=50)
        self.ctrl_f = ttk.Frame(self, padding="10", width=300)
        self.res_f = ttk.Frame(self, padding="10")
        
        self.bot_f.pack(side="bottom", fill="x", pady=10)
        self.bot_f.pack_propagate(False)
        self.ctrl_f.pack(side="left", fill="y")
        self.res_f.pack(side="right", fill="both", expand=True)

        ttk.Button(self.bot_f, text="Réinitialiser", 
                  command=self.reset).pack(side='left', padx=(20, 10))
        ttk.Button(self.bot_f, text="Lancer la Simulation", 
                  command=self.lance).pack(expand=True, ipady=5)

    def _cr_ctrl(self):
        # Stratégies
        str_f = ttk.LabelFrame(self.ctrl_f, text="1. Choix de la Stratégie", padding="10")
        str_f.pack(fill="x", pady=5)
        self.str_v = tk.IntVar(value=1)
        strats = [("Fixe (100% en continu)", 1), ("Programmation Horaire", 2), ("Détecteur de Présence", 3)]
        for txt, val in strats:
            ttk.Radiobutton(str_f, text=txt, variable=self.str_v, 
                           value=val, command=self.upd_ui).pack(anchor="w")

        # Puissances
        p_f = ttk.LabelFrame(self.ctrl_f, text="2. Puissances (W)", padding="10")
        p_f.pack(fill="x", pady=5)
        self.p100_v = tk.DoubleVar(value=0)
        self.pv_v = tk.DoubleVar(value=0)
        
        ttk.Label(p_f, text="Régime 100%:").grid(row=0, column=0, sticky="w")
        ttk.Entry(p_f, textvariable=self.p100_v, width=10).grid(row=0, column=1)
        ttk.Label(p_f, text="Régime Veille:").grid(row=1, column=0, sticky="w")
        ttk.Entry(p_f, textvariable=self.pv_v, width=10).grid(row=1, column=1)

        # Plages horaires
        self.h_f = ttk.LabelFrame(self.ctrl_f, text="3. Plages horaires", padding="10")
        self.plg_v = []
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        for jr in jours:
            fj = ttk.Frame(self.h_f)
            fj.pack(fill='x', pady=2)
            ttk.Label(fj, text=f"{jr}:", width=10).pack(side='left')
            
            deb_v = tk.IntVar(value=0)
            fin_v = tk.IntVar(value=0)
            
            ttk.Label(fj, text="de").pack(side='left')
            ttk.Spinbox(fj, from_=0, to=24, width=4, textvariable=deb_v).pack(side='left', padx=5)
            ttk.Label(fj, text="à").pack(side='left')
            ttk.Spinbox(fj, from_=0, to=24, width=4, textvariable=fin_v).pack(side='left', padx=5)
            self.plg_v.append((deb_v, fin_v))

        # Détecteur
        self.pres_f = ttk.LabelFrame(self.ctrl_f, text="4. Détecteur", padding="10")
        self.tx_v = tk.IntVar(value=0)
        ttk.Label(self.pres_f, text="Taux d'occupation (%):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(self.pres_f, from_=0, to=100, width=8, 
                   textvariable=self.tx_v).grid(row=0, column=1, pady=2, padx=5)

    def _cr_plot(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        self.canv = FigureCanvasTkAgg(self.fig, master=self.res_f)
        self.canv.get_tk_widget().pack(fill="both", expand=True)
        
        self.res_txt = tk.StringVar()
        ttk.Label(self.res_f, textvariable=self.res_txt, 
                 font=("Helvetica", 12), justify="left", padding="10").pack(fill="x")
        
        self._vide()

    def _vide(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_title('Puissance Instantanée sur une semaine')
        self.ax1.set_ylabel('Puissance (W)')
        self.ax1.grid(True, linestyle='--', alpha=0.6)
        self.ax2.set_title('Énergie Consommée Cumulée')
        self.ax2.set_ylabel('Énergie (kWh)')
        self.ax2.set_xlabel('Jours de la semaine')
        self.ax2.grid(True, linestyle='--', alpha=0.6)
        self.fig.tight_layout()
        self.canv.draw()

    def reset(self):
        self.str_v.set(1)
        self.p100_v.set(0)
        self.pv_v.set(0)
        self.tx_v.set(0)
        
        for deb_v, fin_v in self.plg_v:
            deb_v.set(0)
            fin_v.set(0)
        
        self.res_txt.set("")
        self._vide()
        self.upd_ui()

    def upd_ui(self):
        strat = self.str_v.get()
        if strat == 1:
            self.h_f.pack_forget()
            self.pres_f.pack_forget()
        elif strat == 2:
            self.h_f.pack(fill="x", pady=5)
            self.pres_f.pack_forget()
        elif strat == 3:
            self.h_f.pack(fill="x", pady=5)
            self.pres_f.pack(fill="x", pady=5)

    def lance(self):
        try:
            strat = self.str_v.get()
            puis = (self.p100_v.get(), self.pv_v.get())
            plg_h = [(d.get(), f.get()) for d, f in self.plg_v]
            tx_occ = self.tx_v.get() if strat == 3 else None

            p_inst, e_cum = sim_conso(strat, puis, plg_h, tx_occ)

            self._vide()
            temps = np.arange(len(p_inst))

            self.ax1.step(temps, p_inst, color='tab:blue', where='post')
            self.ax1.set_ylim(bottom=0)

            self.ax2.plot(temps, e_cum, color='tab:red')
            self.ax2.set_ylim(bottom=0)

            jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            pos = np.arange(12, 168, 24)
            
            for ax in [self.ax1, self.ax2]:
                ax.set_xticks(pos)
                ax.set_xticklabels(jours, rotation=0)

            self.fig.tight_layout()
            self.canv.draw()

            conso = e_cum[-1]
            self.res_txt.set(
                f"Consommation semaine : {conso:.2f} kWh\n"
                f"Estimation annuelle : {conso * 47:.2f} kWh")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur simulation : {e}")

if __name__ == "__main__":
    App().mainloop()

# sim_conso = fonction de simulation de consommation
# strat = stratégie choisie (1,2 ou 3)
# puis = tuple des puissances (100%, veille)
# plg_h = plages horaires de fonctionnement
# tx_occ = taux d'occupation en pourcentage
# h_sem = heures dans une semaine (168)
# p_inst = puissance instantanée par heure
# p100 = puissance à 100% (W)
# p_v = puissance en veille (W)
# j = compteur de jour
# deb = heure de début
# fin = heure de fin
# idx = indices des heures de fonctionnement
# nb_h = nombre d'heures occupées
# h_occ = heures occupées choisies aléatoirement
# bot_f = cadre du bas (boutons)
# ctrl_f = cadre de controle (paramètres)
# res_f = cadre des résultats (graphiques)
# str_f = cadre stratégies
# str_v = variable stratégie
# strats = liste des stratégies disponibles
# txt = texte du bouton radio
# val = valeur du bouton radio
# p_f = cadre puissances
# p100_v = variable puissance 100%
# pv_v = variable puissance veille
# h_f = cadre horaires
# deb_v = variable heure début
# fin_v = variable heure fin
# pres_f = cadre présence
# tx_v = variable taux occupation
# fig = figure matplotlib
# ax1 = axe graphique puissance
# ax2 = axe graphique énergie
# canv = canvas matplotlib
# res_txt = texte des résultats
# e_cum = énergie cumulée
# conso = consommation hebdomadaire
