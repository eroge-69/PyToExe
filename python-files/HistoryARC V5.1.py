import tkinter as tk
import tkinter.ttk as ttk
from tkinter import DISABLED, W, BooleanVar, messagebox
from tkinter.colorchooser import askcolor
from tkcalendar import Calendar
from datetime import datetime, timedelta
import webbrowser
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import AutoLocator
import numpy as np
import os
import sys
import io
from PIL import Image, ImageTk
import urllib.request
import clipboard
import threading
import warnings
import queue

print(
    f"--- Le bon interpréteur Python est ici : ---\n{sys.executable}\n-----------------------------------------")


# --- Constantes ---
CHEMIN_SERVEUR = "//srvrdcollect/RDCOLLECT"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/b/b7/Arc_Holdings_logo.png"
BG_COLOR_PRIMARY = "#325faa"
BG_COLOR_WIDGET = "white"

# --- Fonctions Utilitaires ---


def chercher_fichier(date, chemin):
    dossier_date = os.path.join(chemin, date.strftime("%Y-%m-%d"))
    if not os.path.isdir(dossier_date):
        return None
    for nom_fichier in os.listdir(dossier_date):
        if "_Releve_F" in nom_fichier and date.strftime("%d_%m_%Y") in nom_fichier:
            return os.path.join(dossier_date, nom_fichier)
    return None


def mousewheel(event, canvas):
    canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")


def update_progress_label(pb):
    return f"Chargement des données : {pb['value']}%" if pb["value"] < 100 else "Création du graphique..."


def progress(pb, pctg, lbl_chargement):
    pb["value"] = pctg
    lbl_chargement["text"] = update_progress_label(pb)


def formater_equation(p):
    """Formate un objet polynôme numpy en une jolie chaîne de caractères avec des exposants."""
    superscripts = {"0": "⁰", "1": "¹", "2": "²", "3": "³",
                    "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    equation_parts = []

    for i, coeff in enumerate(p.coeffs):
        power = p.order - i

        # Ignore les termes avec un coefficient quasi-nul
        if np.isclose(coeff, 0):
            continue

        # Gère le signe (+ ou -)
        sign = ""
        if len(equation_parts) > 0:
            sign = " + " if coeff > 0 else " - "
        elif coeff < 0:
            sign = "-"

        # Gère le coefficient (on n'affiche pas 1.00 si ce n'est pas le terme constant)
        coeff_val = abs(coeff)
        coeff_str = ""
        if not np.isclose(coeff_val, 1) or power == 0:
            coeff_str = f"{coeff_val:.2f}"

        # Gère la variable x et son exposant
        if power > 0:
            var_str = "x"
            if power > 1:
                for digit in str(power):
                    var_str += superscripts.get(digit, '')
            equation_parts.append(f"{sign}{coeff_str}{var_str}")
        else:  # Terme constant
            equation_parts.append(f"{sign}{coeff_str}")

    return "y = " + "".join(equation_parts)


def acquisition_donnees_graphe(
    donnees_a_tracer,
    chemin_pour_graphe,
    datetime_debut,
    datetime_fin,
    frequence,
    intervalle,
    unite_x,
    q,
    nom_donnee_x,
):
    donnees_a_tracer_flat = [
        item for sublist in donnees_a_tracer for item in sublist]
    colonnes_a_lire = list(
        set(donnees_a_tracer_flat + ([nom_donnee_x] if nom_donnee_x else [])))

    # 1. On charge toutes les données brutes de la période dans une liste de DataFrames
    jours_a_parcourir = pd.date_range(
        datetime_debut.date(), datetime_fin.date()).to_pydatetime().tolist()
    total = len(jours_a_parcourir) if jours_a_parcourir else 1
    liste_dfs = []
    for i, jour in enumerate(jours_a_parcourir):
        pctg = int((i + 1) * 100 / total)
        q.put(pctg)
        fichier_path = chercher_fichier(jour, chemin_pour_graphe)
        if not fichier_path:
            continue
        with open(fichier_path, "r", encoding='utf-8') as file:
            try:
                df_jour = pd.read_csv(file, sep=";")
                if 'Heure' in df_jour.columns:
                    # On spécifie le format de la date
                    df_jour['timestamp'] = pd.to_datetime(
                        jour.strftime("%d/%m/%Y") + ' ' + df_jour['Heure'],
                        format='%d/%m/%Y %H:%M',
                        errors='coerce'
                    )
                    liste_dfs.append(df_jour)
            except Exception:
                continue

    if not liste_dfs:
        return {}, {}, []

    # 2. On assemble tout en un seul grand DataFrame
    df_complet = pd.concat(liste_dfs, ignore_index=True)
    df_complet.dropna(subset=['timestamp'], inplace=True)
    df_complet = df_complet[(df_complet['timestamp'] >= datetime_debut) & (
        df_complet['timestamp'] <= datetime_fin)]

    if df_complet.empty:  # Vérification ajoutée après le filtrage
        return {}, {}, []

    df_complet.set_index('timestamp', inplace=True)

    # 3. On convertit toutes les colonnes de données en numérique
    for col in colonnes_a_lire:
        if col in df_complet.columns:
            df_complet[col] = pd.to_numeric(df_complet[col].astype(
                str).str.replace(',', '.'), errors='coerce')

    # 4. On effectue le rééchantillonnage (resampling)
    freq_map = {'minute(s)': 'T', 'heure(s)': 'H', 'jour(s)': 'D'}
    rule = f"{intervalle}{freq_map[frequence]}"
    df_resampled = df_complet[colonnes_a_lire].resample(rule).mean()

    # 5. On prépare les dictionnaires de retour
    donnees_a_tracer_axe1, donnees_a_tracer_axe2 = donnees_a_tracer
    DONNEES_GRAPHE_AXE1 = {donnee: [] for donnee in donnees_a_tracer_axe1}
    DONNEES_GRAPHE_AXE1["x"] = []
    DONNEES_GRAPHE_AXE2 = {donnee: [] for donnee in donnees_a_tracer_axe2}
    DONNEES_GRAPHE_AXE2["x"] = []

    if unite_x == "Donnee":
        DONNEES_GRAPHE_AXE1['x'] = df_resampled[nom_donnee_x].tolist()
        DONNEES_GRAPHE_AXE2['x'] = df_resampled[nom_donnee_x].tolist()

    for donnee in donnees_a_tracer_axe1:
        if donnee in df_resampled.columns:
            DONNEES_GRAPHE_AXE1[donnee] = df_resampled[donnee].tolist()

    for donnee in donnees_a_tracer_axe2:
        if donnee in df_resampled.columns:
            DONNEES_GRAPHE_AXE2[donnee] = df_resampled[donnee].tolist()

    date_format = "%d/%m/%Y\n%H:%M" if frequence != 'jour(s)' else "%d/%m/%Y"
    lst_lbl_x = [d.strftime(date_format) for d in df_resampled.index]

    return DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2, lst_lbl_x


class MyCalendar(Calendar):
    def __init__(self, master=None, **kw):
        self._disabled_dates = []
        super().__init__(master, **kw)

    def disable_date(self, date):
        self._disabled_dates.append(date)
        mi, mj = self._get_day_coords(date)
        if mi is not None:
            self._calendar[mi][mj].state(["disabled"])

    def _display_calendar(self):
        super()._display_calendar()
        for date in self._disabled_dates:
            mi, mj = self._get_day_coords(date)
            if mi is not None:
                self._calendar[mi][mj].state(["disabled"])


class Tooltip:
    """
    Crée une bulle d'aide (tooltip) qui apparaît au survol d'un widget.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        # Ne rien faire si le texte est vide
        if not self.text:
            return

        # Création de la fenêtre Toplevel
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 15
        y += self.widget.winfo_rooty() - 15

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Ajout du label avec le texte complet
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma 8 normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None


class Onglet(tk.Frame):
    def __init__(self, parent, app, nom_onglet):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.nom = nom_onglet
        self.dates: list = []
        self.lst_donnees: list = []
        self.vars1_donnees: list = []
        self.vars2_donnees: list = []
        self.chks1_donnees: list = []
        self.chks2_donnees: list = []
        self.labels_donnees: list = []
        self.courbes_graphe: dict = {}
        # Le cache pour les données du graphique actuellement affiché
        self.donnees_graphique_actuel = {}
        self.zones_analyse = []  # Liste pour stocker les zones d'analyse créées
        self.moyenne_info = {}
        self.tendance_info = {}
        self.fig = Figure()
        self.canvas = None
        self.toolbar = None
        self.stop_polling = False
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._creer_widgets()

    def _update_row_style(self, index, hover=False):
        """Met à jour le style d'une ligne de la liste de données."""
        # On récupère les 3 widgets de la ligne
        label = self.labels_donnees[index]
        chk1 = self.chks1_donnees[index]
        chk2 = self.chks2_donnees[index]
        widgets = [label, chk1, chk2]

        # On définit les couleurs
        selected_color = "#e5f3ff"  # Bleu clair
        hover_color = "#f0f0f0"     # Gris clair
        normal_color = "white"

        is_selected = self.vars1_donnees[index].get(
        ) or self.vars2_donnees[index].get()

        # On choisit la couleur finale
        if is_selected:
            final_color = selected_color
        elif hover:
            final_color = hover_color
        else:
            final_color = normal_color

        # On applique la couleur aux 3 widgets
        for widget in widgets:
            widget.config(bg=final_color)

    def redessiner_zones_analyse(self):
        """Efface et redessine toutes les zones d'analyse et les lignes de moyenne."""
        # On vide le dictionnaire de suivi des moyennes
        self.moyenne_info.clear()
        # On supprime les anciens rectangles, lignes et textes
        artistes_a_verifier = []
        for ax in self.fig.axes:
            artistes_a_verifier.extend(ax.patches)
            artistes_a_verifier.extend(ax.collections)
            artistes_a_verifier.extend(ax.texts)
        for artist in list(artistes_a_verifier):
            if hasattr(artist, 'is_zone_analyse'):
                artist.remove()

        # On identifie sur quel axe se trouve chaque courbe de données
        ax1 = self.fig.axes[0]
        ax2 = self.fig.axes[1] if len(self.fig.axes) > 1 else None
        courbes_sur_axe1 = [l.get_label() for l in ax1.lines]

        intitules_styles = ["Aucun", "______",
                            "..........", "------", "-.-.-.-."]
        styles_matplotlib = ["None", "-", ":", "--", "-."]

        # On redessine les nouveaux
        for zone in self.zones_analyse:
            # Création des rectangles
            rect = ax1.axvspan(
                zone['debut'],
                zone['fin'],
                facecolor=zone['couleur'],
                alpha=1 - zone['alpha']/100,
                edgecolor=None,
                zorder=0,
            )
            rect.is_zone_analyse = True  # On marque l'objet pour pouvoir le retrouver plus tard

            # Création des textes (noms)
            nom_zone = zone.get('nom')
            position_nom = zone.get('position_nom', 'Aucun')
            if nom_zone and position_nom != 'Aucun':
                # Position horizontale : au centre de la zone
                x_pos = (zone['debut'] + zone['fin']) / 2
                # Position verticale : en haut ou en bas
                if position_nom == 'Haut':
                    y_pos, va = 0.98, 'top'
                else:  # Bas
                    y_pos, va = 0.02, 'bottom'
                # On utilise ax.text avec des coordonnées relatives à l'axe pour la hauteur
                texte_artiste = ax1.text(
                    x_pos,
                    y_pos,
                    nom_zone,
                    transform=ax1.get_xaxis_transform(),
                    ha='center',
                    va=va,
                    fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.6,
                              edgecolor='none', boxstyle='round,pad=0.2'),
                )
                texte_artiste.is_zone_analyse = True

            # Création des droites de moyenne
            for nom_courbe, info_moyenne in zone.get('moyennes', {}).items():
                style_ligne = info_moyenne.get('style')
                if style_ligne != "Aucun":
                    # On détermine sur quel axe on doit tracer la ligne de moyenne
                    axe_a_utiliser = ax1 if nom_courbe in courbes_sur_axe1 else ax2
                    line = axe_a_utiliser.hlines(
                        info_moyenne['valeur'],
                        zone['debut'],
                        zone['fin'],
                        color=info_moyenne['couleur'],
                        linestyle=styles_matplotlib[intitules_styles.index(
                            style_ligne)],
                        linewidth=info_moyenne.get('epaisseur'),
                        picker=2,
                    )
                    line.is_zone_analyse = True  # On marque l'objet pour pouvoir le retrouver plus tard
                    # On stocke les infos de la ligne de moyenne
                    unite_x = self.varGr_x.get()
                    if unite_x == "Temps":
                        debut_dt = mdates.num2date(zone['debut'])
                        debut_str = debut_dt.strftime('%d/%m/%Y %H:%M')
                        fin_dt = mdates.num2date(zone['fin'])
                        fin_str = fin_dt.strftime('%d/%m/%Y %H:%M')
                    else:
                        debut_str = f"{zone['debut']:.2f}"
                        fin_str = f"{zone['fin']:.2f}"
                    info_texte = f"{nom_courbe}\nDe : {debut_str}\nA : {fin_str}\nValeur moyenne : {info_moyenne['valeur']:.2f}"
                    self.moyenne_info[line] = info_texte

        self.canvas.draw_idle()

    def _update_x_axis_controls(self):
        """Met à jour l'état des contrôles de l'axe X en fonction du Radiobutton sélectionné."""
        if self.varGr_x.get() == "Temps":
            self.lbl_choix_x_donnee.config(state="disabled", bg="#f0f0f0")
        else:  # "Donnee"
            self.lbl_choix_x_donnee.config(state="normal", bg="white")

    def _creer_widgets(self):
        lblframe_x = tk.LabelFrame(
            self, text="Paramètres axe x", font="bold", labelanchor="n", bg=BG_COLOR_WIDGET)
        lblframe_x.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        # --- Widgets pour la période ---
        frame_periode = tk.Frame(lblframe_x, bg="white")
        frame_periode.grid(column=0, row=0, sticky="ew")
        tk.Label(frame_periode, text="Choix de la période :", bg=BG_COLOR_WIDGET).grid(
            column=0, row=0, columnspan=5, pady=2, sticky="w")
        # Ligne pour la date et l'heure de DÉBUT
        # DATE
        tk.Label(frame_periode, text="Début :", bg=BG_COLOR_WIDGET).grid(
            column=0, row=1, sticky="w")
        self.lbl_debut = tk.Label(
            frame_periode, bg="#f0f0f0", relief="groove", width=10)
        self.lbl_debut.grid(column=1, row=1, sticky="w")
        # HEURE
        self.lbl_h_debut = tk.Label(
            frame_periode, relief="groove", width=2, state="disabled", bg="#f0f0f0")
        self.lbl_m_debut = tk.Label(
            frame_periode, relief="groove", width=2, state="disabled", bg="#f0f0f0")
        self.lbl_h_debut.grid(row=1, column=2, padx=(5, 0))
        tk.Label(frame_periode, text=":",
                 bg=BG_COLOR_WIDGET).grid(row=1, column=3)
        self.lbl_m_debut.grid(row=1, column=4)
        # Ligne pour la date et l'heure de FIN
        # DATE
        tk.Label(frame_periode, text="Fin :", bg=BG_COLOR_WIDGET).grid(
            column=0, row=2, pady=5, sticky="w")
        self.lbl_fin = tk.Label(
            frame_periode, bg="#f0f0f0", relief="groove", width=10)
        self.lbl_fin.grid(column=1, row=2, pady=5, sticky="w")
        # HEURE
        self.lbl_h_fin = tk.Label(
            frame_periode, relief="groove", width=2, state="disabled", bg="#f0f0f0")
        self.lbl_m_fin = tk.Label(
            frame_periode, relief="groove", width=2, state="disabled", bg="#f0f0f0")
        self.lbl_h_fin.grid(row=2, column=2, pady=5, padx=(5, 0))
        tk.Label(frame_periode, text=":",
                 bg=BG_COLOR_WIDGET).grid(row=2, column=3)
        self.lbl_m_fin.grid(row=2, column=4, pady=5)

        # --- Widgets pour la donnée en axe x ---
        frame_donnee = tk.Frame(lblframe_x, bg="white")
        frame_donnee.columnconfigure(1, weight=1)
        frame_donnee.grid(column=0, row=1, sticky="ew")
        tk.Label(frame_donnee, text="Tracer en fonction du :", bg=BG_COLOR_WIDGET).grid(
            column=0, row=0, columnspan=3, sticky="w")
        self.varGr_x = tk.StringVar(value="Temps")
        # 1. On crée un Frame pour contenir les RadioButton et la liste déroulante
        self.choix_x1 = tk.Radiobutton(
            frame_donnee, text="Temps", variable=self.varGr_x, value="Temps", bg=BG_COLOR_WIDGET, state="disabled", command=self._update_x_axis_controls,
        )
        self.choix_x1.grid(column=0, row=1)
        # 2. Le nouveau RadioButton, qui appelle la fonction de mise à jour
        self.choix_x2 = tk.Radiobutton(
            frame_donnee, variable=self.varGr_x, value="Donnee", bg=BG_COLOR_WIDGET, state="disabled", command=self._update_x_axis_controls,
        )
        self.choix_x2.grid(column=1, row=1, padx=0, sticky="e")
        # 3. Le Label qui servira de liste déroulante
        self.lbl_choix_x_donnee = tk.Label(
            frame_donnee, text="- Autre donnée -", relief="groove", width=15, state="disabled", anchor="w")
        self.lbl_choix_x_donnee.grid(column=2, row=1)

        # --- Widgets pour la fréquence d'échantillonnage ---
        frame_frequence = tk.Frame(lblframe_x, bg="white")
        frame_frequence.grid(row=2, column=0, sticky="ew")
        tk.Label(frame_frequence, text="Afficher une valeur toutes les :",
                 bg=BG_COLOR_WIDGET).grid(column=0, row=0, columnspan=2, sticky="w")
        self.interval_var = tk.StringVar(value="1")
        self.frequence_entry = tk.Entry(frame_frequence, textvariable=self.interval_var, width=4,
                                        justify='right', state="disabled")
        self.frequence_entry.grid(column=0, row=1, padx=2, pady=5, sticky="e")
        self.combo_x = ttk.Combobox(frame_frequence, values=(
            "minute(s)", "heure(s)", "jour(s)"), width=10, state="disabled")
        self.combo_x.grid(column=1, row=1, pady=5, sticky="w")
        self.combo_x.set("minute(s)")

        lblframe_y = tk.LabelFrame(
            self, text="Données disponibles", font="bold", labelanchor="n", bg=BG_COLOR_WIDGET)
        lblframe_y.grid(column=0, row=1, sticky="nsew", padx=5)
        lblframe_y.columnconfigure(0, weight=1)
        lblframe_y.rowconfigure(2, weight=1)

        tk.Label(lblframe_y, text="Données", font="Arial 10 bold",
                 bg=BG_COLOR_WIDGET).grid(column=0, row=0, sticky="w")
        tk.Label(lblframe_y, text="Axe 1", font="Arial 10 bold",
                 fg="blue", bg=BG_COLOR_WIDGET).grid(column=1, row=0)
        tk.Label(lblframe_y, text="Axe 2", font="Arial 10 bold",
                 fg="red", bg=BG_COLOR_WIDGET).grid(column=2, row=0)
        tk.Label(lblframe_y, text="Effacer sélection", font="Arial 8 italic",
                 bg="#f0f0f0", anchor="w").grid(column=0, row=1, sticky="nsew")

        self.var_axe1 = BooleanVar()
        self.var_axe2 = BooleanVar()
        self.chk_axe1 = tk.Checkbutton(lblframe_y, variable=self.var_axe1,
                                       state=DISABLED, bg="#f0f0f0", command=self._deselectionner_axe1)
        self.chk_axe1.grid(column=1, row=1, sticky="nsew")
        self.chk_axe2 = tk.Checkbutton(lblframe_y, variable=self.var_axe2,
                                       state=DISABLED, bg="#f0f0f0", command=self._deselectionner_axe2)
        self.chk_axe2.grid(column=2, row=1, sticky="nsew")

        vscroll = tk.Scrollbar(lblframe_y, orient="vertical")

        self.update_idletasks()
        canvas_width = lblframe_y.winfo_width() - vscroll.winfo_width()
        self.canvas_donnees = tk.Canvas(
            lblframe_y, bg=BG_COLOR_WIDGET, highlightthickness=0, yscrollcommand=vscroll.set, width=canvas_width)

        self.canvas_donnees.grid(column=0, row=2, columnspan=3, sticky="nsew")
        vscroll.config(command=self.canvas_donnees.yview)
        vscroll.grid(column=3, row=2, sticky="ns")

        self.frame_donnees = tk.Frame(self.canvas_donnees, bg=BG_COLOR_WIDGET)
        self.frame_donnees.columnconfigure(0, weight=1)

        window_id = self.canvas_donnees.create_window(
            (0, 0), window=self.frame_donnees, anchor="nw")
        def on_canvas_configure(event): self.canvas_donnees.itemconfig(
            window_id, width=event.width)
        self.canvas_donnees.bind("<Configure>", on_canvas_configure)

        self.btn_graphique = tk.Button(
            self, text="Tracer graphique", bg="#d2d3d4", state=DISABLED, command=self.lancer_creation_graphique)
        self.btn_graphique.grid(column=0, row=2, padx=5, pady=5, sticky="ew")

    def mettre_a_jour_donnees(self, dates, donnees):
        self.dates = dates
        self.lst_donnees = donnees
        for widget in self.frame_donnees.winfo_children():
            widget.destroy()
        # On vide toutes les listes de widgets
        self.vars1_donnees.clear()
        self.vars2_donnees.clear()
        self.chks1_donnees.clear()
        self.chks2_donnees.clear()
        self.labels_donnees.clear()

        for i, nom_donnee_val in enumerate(self.lst_donnees):
            var1, var2 = tk.IntVar(value=0), tk.IntVar(value=0)
            self.vars1_donnees.append(var1)
            self.vars2_donnees.append(var2)
            lbl = tk.Label(self.frame_donnees, text=nom_donnee_val,
                           bg=BG_COLOR_WIDGET, anchor="w", justify="left")
            lbl.grid(column=0, row=i, sticky="nsew")
            self.labels_donnees.append(lbl)
            # On attache une bulle d'aide au label
            tooltip = Tooltip(widget=lbl, text=nom_donnee_val)
            chk1 = tk.Checkbutton(self.frame_donnees, bg=BG_COLOR_WIDGET, variable=var1,
                                  width=2, command=lambda i=i: self._cocher(self.vars1_donnees, i))
            chk1.grid(column=1, row=i)
            self.chks1_donnees.append(chk1)
            chk2 = tk.Checkbutton(self.frame_donnees, bg=BG_COLOR_WIDGET, variable=var2,
                                  width=2, command=lambda i=i: self._cocher(self.vars2_donnees, i))
            chk2.grid(column=2, row=i)
            self.chks2_donnees.append(chk2)

            def on_enter_row(event, index=i, tip=tooltip):
                self._update_row_style(index, hover=True)
                tip.show_tip()  # On appelle manuellement l'affichage de la bulle

            def on_leave_row(event, index=i, tip=tooltip):
                self._update_row_style(index, hover=False)
                tip.hide_tip()  # On appelle manuellement pour cacher la bulle

            for widget in (lbl, chk1, chk2):
                widget.bind("<MouseWheel>", lambda e: mousewheel(
                    e, self.canvas_donnees))
                # Quand la souris entre, on appelle on_enter_row en mode "survol"
                widget.bind("<Enter>", on_enter_row)
                # Quand la souris sort, on appelle on_leave_row en mode "normal"
                widget.bind("<Leave>", on_leave_row)
        self.frame_donnees.bind(
            "<MouseWheel>", lambda e: mousewheel(e, self.canvas_donnees))

        self.canvas_donnees.update_idletasks()
        self.canvas_donnees.config(
            scrollregion=self.canvas_donnees.bbox("all"))
        self.canvas_donnees.yview_moveto(0)

    def _cocher(self, vars_actives_list, index):
        if vars_actives_list is self.vars1_donnees and self.vars2_donnees[index].get():
            self.vars2_donnees[index].set(0)
            self._verifier_etat_axe(
                self.vars2_donnees, self.var_axe2, self.chk_axe2)
        elif vars_actives_list is self.vars2_donnees and self.vars1_donnees[index].get():
            self.vars1_donnees[index].set(0)
            self._verifier_etat_axe(
                self.vars1_donnees, self.var_axe1, self.chk_axe1)
        vars_axe_actifs = self.var_axe1 if vars_actives_list is self.vars1_donnees else self.var_axe2
        chk_axe_actifs = self.chk_axe1 if vars_actives_list is self.vars1_donnees else self.chk_axe2
        self._verifier_etat_axe(
            vars_actives_list, vars_axe_actifs, chk_axe_actifs)
        self._update_row_style(index)

    def _verifier_etat_axe(self, vars_donnees, var_axe, chk_axe):
        if any(var.get() for var in vars_donnees):
            var_axe.set(True)
            chk_axe.config(state="normal")
        else:
            var_axe.set(False)
            chk_axe.config(state="disable")

    def _deselectionner_axe1(self):
        self.var_axe1.set(False)
        self.chk_axe1.config(state=DISABLED)
        for chk_var in self.vars1_donnees:
            chk_var.set(0)
        for i in range(len(self.labels_donnees)):
            self._update_row_style(i)

    def _deselectionner_axe2(self):
        self.var_axe2.set(False)
        self.chk_axe2.config(state=DISABLED)
        for chk_var in self.vars2_donnees:
            chk_var.set(0)
        for i in range(len(self.labels_donnees)):
            self._update_row_style(i)

    def reinitialiser_affichage(self):
        self.lbl_debut.config(text="", bg="#f0f0f0")
        self.lbl_fin.config(text="", bg="#f0f0f0")
        self.lbl_debut.unbind("<Button-1>")
        self.lbl_fin.unbind("<Button-1>")
        self.lbl_h_debut.config(text="", state="disabled", bg="#f0f0f0")
        self.lbl_m_debut.config(text="", state="disabled", bg="#f0f0f0")
        self.lbl_h_debut.unbind("<Button-1>")
        self.lbl_m_debut.unbind("<Button-1>")
        self.lbl_h_fin.config(text="", state="disabled", bg="#f0f0f0")
        self.lbl_m_fin.config(text="", state="disabled", bg="#f0f0f0")
        self.lbl_h_fin.unbind("<Button-1>")
        self.lbl_m_fin.unbind("<Button-1>")
        self.varGr_x.set("Temps")
        self.lbl_choix_x_donnee.config(
            text="- Autre donnée -", state="disabled", bg="#f0f0f0")
        self.lbl_choix_x_donnee.unbind("<Button-1>")
        self.interval_var.set("1")
        self.frequence_entry.config(state="disabled")
        self.combo_x.set("minute(s)")
        self.combo_x.config(state="disabled")
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        # self.fig.clf()
        self.choix_x1.config(state=DISABLED)
        self.choix_x2.config(state=DISABLED)
        self.btn_graphique.config(state=DISABLED)
        self.combo_x.config(state=DISABLED)
        if self.var_axe1.get():
            self._deselectionner_axe1()
        if self.var_axe2.get():
            self._deselectionner_axe2()
        self.chk_axe1.config(state=DISABLED)
        self.chk_axe2.config(state=DISABLED)

    def activer_controles(self):
        self.btn_graphique.config(state="normal")

        self.lbl_debut.config(
            bg="white", text=self.dates[-1].strftime("%d/%m/%Y"))
        self.lbl_fin.config(
            bg="white", text=self.dates[-1].strftime("%d/%m/%Y"))
        self.lbl_debut.bind(
            "<Button-1>", lambda e: self.app.afficher_calendrier(e, self.lbl_debut, self.dates))
        self.lbl_fin.bind(
            "<Button-1>", lambda e: self.app.afficher_calendrier(e, self.lbl_fin, self.dates))
        self.lbl_h_debut.bind(
            "<Button-1>", lambda e: self.app.fenetre_choix(self.lbl_h_debut, np.arange(0, 24)))
        self.lbl_m_debut.bind(
            "<Button-1>", lambda e: self.app.fenetre_choix(self.lbl_m_debut, np.arange(0, 60)))
        self.lbl_h_debut.config(state="normal", bg="white", text="00")
        self.lbl_m_debut.config(state="normal", bg="white", text="00")
        self.lbl_h_fin.bind(
            "<Button-1>", lambda e: self.app.fenetre_choix(self.lbl_h_fin, np.arange(0, 24)))
        self.lbl_m_fin.bind(
            "<Button-1>", lambda e: self.app.fenetre_choix(self.lbl_m_fin, np.arange(0, 60)))
        self.lbl_h_fin.config(state="normal", bg="white", text="23")
        self.lbl_m_fin.config(state="normal", bg="white", text="59")
        self.lbl_choix_x_donnee.bind("<Button-1>",
                                     lambda e: self.app.fenetre_choix(
                                         self.lbl_choix_x_donnee, self.lst_donnees) if self.lbl_choix_x_donnee.cget('state') == 'normal' else None
                                     )
        self.choix_x1.config(state="normal")
        self.choix_x2.config(state="normal")
        self.frequence_entry.config(state="normal")
        self.combo_x.config(state="readonly")

    def _get_parametres(self):
        donnees_axe1 = [self.lst_donnees[i]
                        for i, var in enumerate(self.vars1_donnees) if var.get()]
        donnees_axe2 = [self.lst_donnees[i]
                        for i, var in enumerate(self.vars2_donnees) if var.get()]
        date_debut_str, date_fin_str = self.lbl_debut.cget(
            "text"), self.lbl_fin.cget("text")
        # if not self.dates: return [], "", "", [], []
        if not date_debut_str and not date_fin_str:
            date_debut = date_fin = self.dates[-1]
            self.lbl_debut.config(text=date_debut.strftime("%d/%m/%Y"))
            self.lbl_fin.config(text=date_fin.strftime("%d/%m/%Y"))
        elif not date_fin_str:
            date_debut = date_fin = datetime.strptime(
                date_debut_str, "%d/%m/%Y")
            self.lbl_fin.config(text=date_debut_str)
        elif not date_debut_str:
            date_debut = date_fin = datetime.strptime(date_fin_str, "%d/%m/%Y")
            self.lbl_debut.config(text=date_fin_str)
        else:
            date_debut = datetime.strptime(date_debut_str, "%d/%m/%Y")
            date_fin = datetime.strptime(date_fin_str, "%d/%m/%Y")
            if date_fin < date_debut:
                date_fin = date_debut
                self.lbl_fin.config(text=date_debut.strftime("%d/%m/%Y"))
        # On lit la valeur directement depuis le texte des labels
        datetime_debut = date_debut.replace(hour=int(self.lbl_h_debut.cget(
            "text")), minute=int(self.lbl_m_debut.cget("text")))
        datetime_fin = date_fin.replace(hour=int(self.lbl_h_fin.cget(
            "text")), minute=int(self.lbl_m_fin.cget("text")))
        if datetime_fin < datetime_debut:
            messagebox.showerror(
                "Erreur", "L'horaire de fin doit être après l'horaire de début.")
            return None

        unite_x = self.varGr_x.get()
        nom_donnee_x = None
        if unite_x == "Donnee":
            nom_donnee_x = self.lbl_choix_x_donnee.cget("text")
            if not nom_donnee_x or nom_donnee_x == "- Autre donnée -":
                messagebox.showerror(
                    "Erreur", "Veuillez choisir une donnée pour l'axe X.")
                return None  # On retourne None pour indiquer une erreur

        # Récupération de l'intervalle d'échantillonnage
        try:
            intervalle = int(self.interval_var.get())
            if intervalle <= 0:
                # On s'assure que le nombre est positif
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Erreur de Saisie", "L'intervalle doit être un nombre entier positif.", parent=self.app)
            return None  # On arrête le processus si la valeur est invalide
        # Récupération de la fréquence d'échantillonnage (minute(s) / heure(s) / jour(s))
        frequence = self.combo_x.get()

        return datetime_debut, datetime_fin, unite_x, nom_donnee_x, frequence, intervalle, donnees_axe1, donnees_axe2

    def lancer_creation_graphique(self):
        self.stop_polling = False
        # On ferme toutes les fenêtres potentiellement ouvertes
        for child in self.app.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()

        frame_chargement = tk.Frame(self, bg="white")
        frame_chargement.grid(column=1, row=0, rowspan=3,
                              padx=5, pady=5, sticky="nsew")
        frame_chargement.columnconfigure(0, weight=1)
        frame_chargement.rowconfigure(0, weight=1)
        frame_chargement.rowconfigure(1, weight=1)
        pb = ttk.Progressbar(
            frame_chargement, orient='horizontal', mode='determinate', length=280)
        lbl_chargement = tk.Label(
            frame_chargement, text="Chargement des données : 0%", font="Arial 28", bg="white")
        lbl_chargement.grid(column=0, row=0, pady=5, sticky="s")
        pb.grid(column=0, row=1, pady=5, sticky="n")
        # 1. On crée la boîte aux lettres
        progress_queue = queue.Queue()
        # 2. On lance le thread de travail en lui donnant la boîte aux lettres
        thread = threading.Thread(
            target=self._acquisition_et_creation,
            args=(progress_queue, frame_chargement),
            name="_acquisition_et_creation"  # Ajout d'un nom pour le débogage
        )
        thread.start()
        # 3. On lance une fonction qui va vérifier la boîte aux lettres toutes les 100ms
        self.after(100, self._check_progress_queue, progress_queue,
                   pb, lbl_chargement, frame_chargement)
        self.app.update_idletasks()

    def _check_progress_queue(self, q, pb, lbl, frame_chargement):
        """Vérifie la boîte aux lettres pour les mises à jour de la progression
        et se reprogramme tant que le thread de travail est actif.
        """
        if self.stop_polling:
            return
        # On essaie de lire tous les messages en attente dans la queue
        try:
            while True:
                message = q.get_nowait()
                progress(pb, message, lbl)
        except queue.Empty:
            # La queue est vide, c'est normal.
            pass

        # On se reprogramme uniquement si le drapeau n'est pas levé
        if not self.stop_polling:
            self.after(100, self._check_progress_queue,
                       q, pb, lbl, frame_chargement)

    def _acquisition_et_creation(self, q, frame_chargement):
        try:
            params = self._get_parametres()
            if params is None:  # Si l'utilisateur n'a pas choisi de donnée
                frame_chargement.destroy()
                return

            datetime_debut, datetime_fin, unite_x, nom_donnee_x, frequence, intervalle, donnees_axe1, donnees_axe2 = params
            if not donnees_axe1 and not donnees_axe2:
                messagebox.showwarning(
                    "Attention", "Veuillez sélectionner au moins une donnée à tracer.")
                if frame_chargement.winfo_exists():
                    frame_chargement.destroy()
                return
            donnees_a_tracer = [donnees_axe1, donnees_axe2]
            chemin_pour_graphe = os.path.join(
                CHEMIN_SERVEUR, self.app.nom_four_selectionne, "Fusion", self.nom)

            DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2, lst_lbl_x = acquisition_donnees_graphe(
                donnees_a_tracer,
                chemin_pour_graphe,
                datetime_debut,
                datetime_fin,
                frequence,
                intervalle,
                unite_x,
                q,
                nom_donnee_x,
            )

            # Mise en cache des données
            self.donnees_graphique_actuel = {
                **DONNEES_GRAPHE_AXE1, **DONNEES_GRAPHE_AXE2}
            # On stocke aussi les labels
            self.donnees_graphique_actuel['valeurs_x_labels'] = lst_lbl_x

            if not lst_lbl_x:
                messagebox.showinfo(
                    "Information", "Aucune donnée trouvée pour la période sélectionnée.")
                if frame_chargement.winfo_exists():
                    frame_chargement.destroy()
                return
            self.app.after(0, self._finaliser_creation_graphique, DONNEES_GRAPHE_AXE1,
                           DONNEES_GRAPHE_AXE2, lst_lbl_x, frequence, unite_x, frame_chargement)
        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Une erreur est survenue lors de la création du graphique :\n{e}")
            if frame_chargement.winfo_exists():
                frame_chargement.destroy()

    def _finaliser_creation_graphique(self, DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2, lst_lbl_x, frequence, unite_x, frame_chargement):
        # On lève le drapeau d'arrêt
        self.stop_polling = True

        if frame_chargement.winfo_exists():
            frame_chargement.destroy()
        self._creation_graphique(
            DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2, lst_lbl_x, frequence, unite_x)

    def _creation_graphique(self, DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2, lst_lbl_x, frequence, unite_x):
        # 1. Nettoyage
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        if self.fig:
            plt.close(self.fig)
        self.fig = Figure()
        self.zones_analyse = []

        axe1 = self.fig.add_subplot(111)
        axe2 = axe1.twinx() if len(DONNEES_GRAPHE_AXE2) > 1 else None
        self.courbes_graphe.clear()

        # 2. Traçage des courbes
        lst_couleurs = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        couleur_idx = 0

        for axe, donnees_graphe in zip([axe1, axe2], [DONNEES_GRAPHE_AXE1, DONNEES_GRAPHE_AXE2]):
            if not axe or len(donnees_graphe) <= 1:
                continue
            for key, y_values in donnees_graphe.items():
                if key == 'x':
                    continue
                y = y_values

                date_format = "%d/%m/%Y\n%H:%M" if lst_lbl_x and "\n" in lst_lbl_x[0] else "%d/%m/%Y"
                x = [datetime.strptime(
                    d, date_format) for d in lst_lbl_x] if unite_x == "Temps" else donnees_graphe['x']

                marqueur = "o" if len(x) == 1 or unite_x == "Donnee" else ""
                trait = "" if len(x) == 1 or unite_x == "Donnee" else "solid"
                axe.plot(x, y, color=lst_couleurs[couleur_idx % len(
                    lst_couleurs)], label=key, marker=marqueur, linestyle=trait)
                self.courbes_graphe[key] = [mdates.date2num(
                    x) if unite_x == "Temps" else x, y]
                couleur_idx += 1
        self.courbes_graphe["valeurs_x"] = lst_lbl_x

        # 3. Style des axes et légendes
        if unite_x == "Temps":
            formatter = mdates.DateFormatter(
                '%d/%m/%Y\n%H:%M' if frequence != 'jour(s)' else '%d/%m/%Y')
            axe1.xaxis.set_major_formatter(formatter)
        else:  # Donnée
            nom_axe_x = self.lbl_choix_x_donnee.cget("text")
            axe1.set_xlabel(nom_axe_x, fontsize=11)
        # self.fig.autofmt_xdate(rotation=45, ha='right')
        # plt.setp(axe1.get_xticklabels(), rotation_mode="anchor")
        axe1.xaxis.set_major_locator(AutoLocator())
        plt.setp(axe1.get_xticklabels(), rotation=45,
                 ha="right", rotation_mode="anchor")

        if len(DONNEES_GRAPHE_AXE1) > 1:
            axe1.spines["left"].set_color("blue")
            axe1.tick_params(axis='y', colors='blue')
            axe1.grid(axis='y', linestyle='--', alpha=0.7)
            pos_legend_1 = (0.5, 1.18) if axe2 else (0.5, 1.1)
            axe1.legend(edgecolor="blue", loc="upper center",
                        bbox_to_anchor=pos_legend_1, fancybox=True, ncol=5)
        else:
            axe1.get_yaxis().set_visible(False)
            axe2.grid(axis='y', linestyle='--', alpha=0.7)

        if axe2 and len(DONNEES_GRAPHE_AXE2) > 1:
            axe2.spines["right"].set_color("red")
            if len(DONNEES_GRAPHE_AXE1) > 1:
                axe2.spines["left"].set_color("blue")
            axe2.tick_params(axis='y', colors='red')
            pos_legend_2 = (0.5, 1.1)
            axe2.legend(edgecolor="red", loc="upper center",
                        bbox_to_anchor=pos_legend_2, fancybox=True, ncol=5)

        # box = axe1.get_position()
        # if unite_x == "Temps":
        #     axe1.set_position(
        #         [box.x0*0.5, box.y0 * 0.75,
        #          box.width * 1.12, box.height * 1.05]
        #     )
        # else:
        #     axe1.set_position(
        #         [box.x0*0.5, box.y0 * 0.55,
        #          box.width * 1.12, box.height * 1.1]
        #     )
        self.fig.tight_layout(pad=0.3)

        # 4. Intégration dans Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=1, row=0, rowspan=2,
                                         sticky="nsew")
        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(column=1, row=2, sticky="w", padx=5)

        # On désactive le label de coordonnées natif de la toolbar
        self.toolbar.set_message = lambda x: ""

        # 5. Curseur interactif
        if self.courbes_graphe:
            # On initialise les dictionnaires de suivi sur l'objet onglet
            self.tendance_info = getattr(self, 'tendance_info', {})
            self.moyenne_info = getattr(self, 'moyenne_info', {})

            # Le curseur et l'annotation vivent TOUJOURS sur l'axe 1 pour la cohérence
            xmin, xmax = axe1.get_xlim()
            ymin = axe1.get_ylim()[0]
            linev = axe1.axvline(xmin, color="black",
                                 linewidth=0.8, animated=True, visible=False)
            lineh = axe1.axhline(ymin, color="black",
                                 linewidth=0.8, animated=True, visible=False)
            # On crée deux annotations avec des décalages fixes
            annot_props = dict(boxstyle="round,pad=0.5",
                               fc="lightyellow", alpha=0.75)
            annot_right = axe1.annotate("", xy=(xmin, ymin), xytext=(10, 15), textcoords="offset points",
                                        bbox=annot_props, animated=True, visible=False)
            xytext_left = (-120, 15) if unite_x == "Temps" else (-80, 15)
            annot_left = axe1.annotate("", xy=(xmin, ymin), xytext=xytext_left, textcoords="offset points",
                                       bbox=annot_props, animated=True, visible=False)
            annot_info = axe1.annotate(
                "",
                # Position en % : 2% du bord gauche, 98% du bas (en haut à gauche)
                xy=(0.01, 0.975),
                xycoords='axes fraction',
                va="top",
                ha="left",
                bbox=dict(boxstyle="round,pad=0.5",
                          fc="white", alpha=0.75),
                animated=True,
                visible=False,
            )

            self.canvas.draw()
            background = self.canvas.copy_from_bbox(self.fig.bbox)

            def on_draw(event):
                nonlocal background
                background = self.canvas.copy_from_bbox(self.fig.bbox)

            def _on_move(event):
                if background is None:
                    return

                # 1. On cherche d'abord une courbe de tendance
                tendance_survolee = None
                for line in self.tendance_info:
                    contains, _ = line.contains(event)
                    if contains:
                        tendance_survolee = line
                        break

                # 2. Si pas de tendance, on cherche une ligne de moyenne
                moyenne_survolee = None
                if not tendance_survolee:
                    for line in self.moyenne_info:
                        contains, _ = line.contains(event)
                        if contains:
                            moyenne_survolee = line
                            break

                # --- Cas 1 : On survole une courbe de tendance ---
                if tendance_survolee:
                    # On cache le curseur de coordonnées s'il était visible
                    if linev.get_visible():
                        linev.set_visible(False)
                        lineh.set_visible(False)
                        annot_right.set_visible(False)
                        annot_left.set_visible(False)

                    # On met à jour et affiche l'info de la tendance
                    info = self.tendance_info[tendance_survolee]
                    texte = f"{info['nom']}\n{info['equation']}"
                    couleur = tendance_survolee.get_color()
                    annot_info.set_text(texte)
                    annot_info.set_color(couleur)
                    annot_info.get_bbox_patch().set_edgecolor(couleur)
                    annot_info.set_visible(True)

                # --- Cas 2 : On survole une froite moyenne ---
                elif moyenne_survolee:
                    # On cache le curseur de coordonnées s'il était visible
                    if linev.get_visible():
                        linev.set_visible(False)
                        lineh.set_visible(False)
                        annot_right.set_visible(False)
                        annot_left.set_visible(False)

                    # On met à jour et affiche l'info de la moyenne
                    texte = self.moyenne_info[moyenne_survolee]
                    couleur = moyenne_survolee.get_color()
                    if isinstance(couleur, (list, np.ndarray)) and len(couleur) > 0:
                        couleur = couleur[0]
                    annot_info.set_text(texte)
                    annot_info.set_color(couleur)
                    annot_info.get_bbox_patch().set_edgecolor(couleur)
                    annot_info.set_visible(True)

                # --- Cas 2 : On est sur le graphique, mais pas sur une tendance ---
                elif event.inaxes:
                    # On cache l'info de tendance si elle était visible
                    if annot_info.get_visible():
                        annot_info.set_visible(False)

                    # On affiche et met à jour le curseur de coordonnées
                    if not linev.get_visible():
                        linev.set_visible(True)
                        lineh.set_visible(True)

                    x_coord, y_coord = event.xdata, event.ydata
                    y_on_axe1 = y_coord if event.inaxes is axe1 else axe1.transData.inverted(
                    ).transform((event.x, event.y))[1]
                    if axe2:
                        y_on_axe2 = y_coord if event.inaxes is axe2 else axe2.transData.inverted(
                        ).transform((event.x, event.y))[1]

                    linev.set_xdata(x_coord)
                    lineh.set_ydata(y_on_axe1)
                    annot_right.xy = (x_coord, y_on_axe1)
                    annot_left.xy = (x_coord, y_on_axe1)

                    # Mise à jour du texte
                    message = f"x = {mdates.num2date(x_coord).strftime('%d/%m/%Y %H:%M') if unite_x == 'Temps' else f'{x_coord:.2f}'}"
                    if len(DONNEES_GRAPHE_AXE1) > 1:
                        message += f"\ny1 = {y_on_axe1:.2f}"
                        if len(DONNEES_GRAPHE_AXE2) > 1:
                            message += f"\ny2 = {y_on_axe2:.2f}"
                    elif len(DONNEES_GRAPHE_AXE2) > 1:
                        message += f"\ny2 = {y_on_axe2:.2f}"
                    annot_right.set_text(message)
                    annot_left.set_text(message)

                    # On affiche la bonne annotation
                    if x_coord > xmin + (xmax - xmin) * 0.75:
                        annot_left.set_visible(True)
                        annot_right.set_visible(False)
                    else:
                        annot_left.set_visible(False)
                        annot_right.set_visible(True)

                # --- Cas 3 : On est en dehors du graphique ---
                else:
                    if linev.get_visible() or annot_info.get_visible():
                        linev.set_visible(False)
                        lineh.set_visible(False)
                        annot_right.set_visible(False)
                        annot_left.set_visible(False)
                        annot_info.set_visible(False)

                # Blitting : on restaure le fond et on dessine tous les artistes
                # (ceux qui sont invisibles sont ignorés par draw_artist)
                self.canvas.restore_region(background)
                axe1.draw_artist(annot_right)
                axe1.draw_artist(annot_left)
                axe1.draw_artist(annot_info)
                axe1.draw_artist(linev)
                axe1.draw_artist(lineh)
                self.canvas.blit(self.fig.bbox)

            self.canvas.mpl_connect("draw_event", on_draw)
            self.canvas.mpl_connect("motion_notify_event", _on_move)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.nom_four_selectionne = ""
        self.logo = None
        self.lst_four = [f for f in os.listdir(
            CHEMIN_SERVEUR) if f.startswith("Four")]
        self._setup_main_window()
        self._creer_widgets_principaux()
        self._creer_menu()
        self._creer_onglets()

    def _setup_main_window(self):
        self.title("HistoryARC")
        self.attributes("-fullscreen", True)
        self.configure(bg=BG_COLOR_PRIMARY)
        # La colonne 0 contiendra le Notebook et prendra tout l'espace
        self.columnconfigure(0, weight=1)
        # La ligne 1 (celle du Notebook) prendra tout l'espace vertical
        self.rowconfigure(1, weight=1)

    def _creer_widgets_principaux(self):
        top_bar_frame = tk.Frame(self, bg=BG_COLOR_PRIMARY)
        top_bar_frame.grid(row=0, column=0, sticky="ew")

        try:
            # On simule un navigateur pour le téléchargement
            # 1. On prépare un en-tête qui imite un navigateur web
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            # 2. On crée une requête avec l'URL et l'en-tête
            req = urllib.request.Request(LOGO_URL, headers=headers)
            # 3. On ouvre une connexion à l'URL et on lit les données binaires de l'image
            with urllib.request.urlopen(req) as response:
                image_data = response.read()
            # 2. On ouvre ces données binaires comme un fichier en mémoire
            image_stream = io.BytesIO(image_data)
            # 3. On ouvre cette image en mémoire avec Pillow (PIL)
            img = Image.open(image_stream)
            # 4. On redimensionne et on crée l'objet PhotoImage
            w, h = img.size
            resize_img = img.resize((int(w * 0.15), int(h * 0.15)))
            self.logo = ImageTk.PhotoImage(resize_img)
        except Exception as e:
            self.logo = None

        tk.Label(top_bar_frame, image=self.logo, text="  HistoryARC", font=(
            "Arial", 28, "bold"), compound="left", fg=BG_COLOR_PRIMARY, bg="white").pack(side="left", padx=3)

        tk.Button(top_bar_frame, text="Valider", command=self.valider_choix_four).pack(
            side="right", padx=5, pady=2)
        self.combo_four = ttk.Combobox(
            top_bar_frame, values=self.lst_four, state="readonly")
        if self.lst_four:
            self.combo_four.current(0)
        self.combo_four.pack(side="right", padx=5, pady=2)

        self.lbl_nom_four = tk.Label(
            top_bar_frame, font="Calibri 28 bold", fg="white", bg=BG_COLOR_PRIMARY)
        self.lbl_nom_four.pack(side="left", expand=True, fill="x", padx=20)

    def _creer_menu(self):
        menu_bar = tk.Menu(self)

        menu_fichier = tk.Menu(menu_bar, tearoff=0)
        menu_fichier.add_command(
            label="Copier les données", command=self.copier_donnees_actives)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=self.destroy)
        menu_bar.add_cascade(label="Fichier", menu=menu_fichier)

        menu_affichage = tk.Menu(menu_bar, tearoff=0)
        menu_affichage.add_command(
            label="Configurer les axes", command=self.configurer_axes)
        menu_affichage.add_command(
            label="Mettre en forme les séries de données", command=self.configurer_donnees)
        menu_bar.add_cascade(label="Affichage", menu=menu_affichage)

        menu_outils = tk.Menu(menu_bar, tearoff=0)
        menu_outils.add_command(label="Calculatrice",
                                command=self.lancer_calculatrice)
        menu_outils.add_command(
            label="Courbes de tendance", command=self.tracer_tendance)
        menu_outils.add_command(label="Zones d'analyse",
                                command=self.gerer_zones_analyse)
        menu_bar.add_cascade(label="Outils", menu=menu_outils)

        menu_help = tk.Menu(menu_bar, tearoff=0)
        menu_help.add_command(label="Aide", command=lambda: webbrowser.open(
            "https://drive.google.com/file/d/1URMpis23QOSWAK97AbuoZYYj0NwB1qR9/view"))
        menu_help.add_command(label="A propos...", command=self.a_propos)
        menu_bar.add_cascade(label="?", menu=menu_help)

        self.config(menu=menu_bar)

    def _creer_onglets(self):
        style = ttk.Style()
        style.configure(".", font=("Arial", "12", "bold"))
        style.configure("Treeview", font=("Arial", "10"))
        self.tabControl = ttk.Notebook(self)
        self.tabControl.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.onglet_four = Onglet(self.tabControl, self, "Four")
        self.onglet_feeder = Onglet(self.tabControl, self, "Feeder")
        self.tabControl.add(self.onglet_four, text="Four")
        self.tabControl.add(self.onglet_feeder, text="Feeder")

    def _get_active_onglet(self):
        try:
            nom_onglet_actif = self.tabControl.tab(
                self.tabControl.select(), "text")
            return self.onglet_four if nom_onglet_actif == "Four" else self.onglet_feeder
        except tk.TclError:
            return None

    def a_propos(self):
        """
        Ouvre une fenêtre d'information sur le logiciel.
        """
        # Création de la fenêtre Toplevel, avec la fenêtre principale (self) comme parent
        about_frame = tk.Toplevel(self)
        about_frame.title("A propos")
        # La fenêtre reste au-dessus de la fenêtre principale
        about_frame.transient(self)
        about_frame.grab_set()  # Bloque les interactions avec la fenêtre principale
        about_frame.resizable(False, False)

        # On crée le Label qui doit afficher l'image
        logo_label = tk.Label(about_frame, image=self.logo, bg="white")
        logo_label.grid(column=0, row=0, rowspan=2,
                        padx=5, pady=5, sticky="nsew")
        # On attache la référence de l'image directement à la fenêtre pour empêcher Python de la supprimer de la mémoire.
        about_frame.image = self.logo

        tk.Label(about_frame, text="HistoryARC", font="Arial 10 bold", justify="left").grid(
            column=1, row=0, padx=5, pady=5, sticky="w"
        )
        tk.Label(about_frame, text="Version 5.1", justify="left").grid(
            column=1, row=1, padx=5, sticky="w"
        )
        tk.Label(
            about_frame,
            text="HistoryARC est libre d'utilisation\nà condition d'avoir un accès au\nserveur //srvrdcollect/RDCOLLECT",
            justify="left",
        ).grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky="ew")

        tk.Label(
            about_frame,
            text="antoine.belhoste@arc-intl.com\nalain.guffroy@arc-intl.com",
            fg="blue",
            font=("Arial", 8, "underline"),
        ).grid(column=0, row=3, columnspan=2, padx=5, pady=5, sticky="ew")

        about_frame.bind("<Escape>", lambda e: about_frame.destroy())

    def copier_donnees_actives(self):
        """
        Copie les données du graphique de l'onglet actif dans le presse-papiers.
        """
        onglet_actif = self._get_active_onglet()

        if not onglet_actif or not onglet_actif.courbes_graphe or "valeurs_x" not in onglet_actif.courbes_graphe:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        donnees_a_copier = onglet_actif.courbes_graphe
        choix_unite = onglet_actif.varGr_x.get()

        headers = []
        colonnes_de_donnees = []

        # 1. On prépare la colonne X
        if choix_unite == "Temps":
            is_detailed_time = "\n" in str(donnees_a_copier["valeurs_x"][0])
            headers.append("Date & Heure" if is_detailed_time else "Date")
            # Pour le temps, les labels sont les données X
            labels_x_formatte = [str(d).replace('\n', ' ')
                                 for d in donnees_a_copier["valeurs_x"]]
            colonnes_de_donnees.append(labels_x_formatte)
        elif choix_unite == "Donnee":
            nom_axe_x = onglet_actif.lbl_choix_x_donnee.cget("text")
            headers.append(nom_axe_x)
            # Les données X sont dans la première partie de n'importe quelle courbe
            first_key = next(
                (k for k in donnees_a_copier if k != "valeurs_x"), None)
            if first_key:
                colonnes_de_donnees.append(donnees_a_copier[first_key][0])

        # 2. On prépare les colonnes Y
        cles_y = [key for key in donnees_a_copier if key != "valeurs_x"]
        for key in cles_y:
            headers.append(key)
            colonnes_de_donnees.append(donnees_a_copier[key][1])

        # 3. On assemble la chaîne de caractères
        try:
            # En-tête
            donnees_graphe_str = "\t".join(headers) + "\n"

            # Lignes de données
            nb_lignes = len(colonnes_de_donnees[0])
            for i in range(nb_lignes):
                ligne = [str(colonne[i]) for colonne in colonnes_de_donnees]
                donnees_graphe_str += "\t".join(ligne) + "\n"
        except IndexError:
            messagebox.showerror(
                "Erreur", "Une erreur est survenue lors de la préparation des données à copier.", parent=self)
            return

        # 4. Finalisation et copie
        donnees_graphe_str = donnees_graphe_str.replace(
            ".", ",").replace("nan", "")
        clipboard.copy(donnees_graphe_str)
        messagebox.showinfo(
            "Copier données", "Les données du graphique ont été copiées dans le presse-papiers.", parent=self)

    def fenetre_choix(self, lbl, lst_choix):
        """
        Crée une fenêtre popup pour sélectionner une valeur dans une liste.
        """
        def valider_choix(event, text_btn):
            lbl.config(text=text_btn)
            frame_choix.destroy()

        self.update_idletasks()
        position_x, position_y = lbl.winfo_rootx(), lbl.winfo_rooty()
        taille_x = lbl.winfo_width()
        position_x += taille_x

        frame_choix = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        frame_choix.geometry(f"+{position_x}+{position_y}")
        frame_choix.overrideredirect(True)
        frame_choix.focus_set()
        frame_choix.grab_set()

        hauteur_max = 150
        cnv_btn = tk.Canvas(frame_choix, height=hauteur_max,
                            highlightthickness=0)
        cnv_btn.grid(column=0, row=0)
        emplacement = tk.Frame(cnv_btn)
        vScroll = tk.Scrollbar(
            frame_choix, orient="vertical", command=cnv_btn.yview)
        vScroll.grid(column=1, row=0, sticky="ns")
        cnv_btn.configure(yscrollcommand=vScroll.set)

        window_id = cnv_btn.create_window(
            (0, 0), anchor="nw", window=emplacement)

        # Fonction pour mettre à jour la zone de défilement chaque fois que la taille du contenu change
        def on_frame_configure(event):
            cnv_btn.configure(scrollregion=cnv_btn.bbox("all"))
        emplacement.bind("<Configure>", on_frame_configure)

        # Fonction pour forcer le contenu à prendre la largeur du canvas
        def on_canvas_configure(event):
            cnv_btn.itemconfig(window_id, width=event.width)
        cnv_btn.bind("<Configure>", on_canvas_configure)

        # Ajout des événements de survol
        selected_color = "#e5f3ff"  # Un bleu très clair si déjà une sélection
        hover_color = "#f0f0f0"  # Un gris clair pour le survol
        normal_color = "white"

        valeur_actuelle = lbl.cget("text")
        lst_btn = []
        nb_digits = 1
        for choix in lst_choix:
            if len(str(choix)) > nb_digits:
                nb_digits = len(str(choix))
        for choix in lst_choix:
            if isinstance(choix, int) or isinstance(choix, np.int32):
                text_btn = "{num:0{width}}".format(num=choix, width=nb_digits)
            else:
                text_btn = choix
            btn = tk.Label(emplacement, text=text_btn,
                           bg="white", padx=5, anchor="w")
            if text_btn == valeur_actuelle:
                # Si le choix est celui déjà sélectionné, on le met en surbrillance
                btn.config(bg=selected_color)
            else:
                # Sinon, on lie l'entrée de la souris au changement de couleur
                btn.bind("<Enter>", lambda event,
                         b=btn: b.config(bg=hover_color))
                # On lie la sortie de la souris au retour à la couleur normale
                btn.bind("<Leave>", lambda event,
                         b=btn: b.config(bg=normal_color))
            # On lie le clic gauche à la validation
            btn.bind("<Button-1>", lambda e, t=text_btn: valider_choix(e, t))
            btn.pack(fill="x", expand=True)
            lst_btn.append(btn)

        # On force la mise à jour pour que la taille du contenu (emplacement) soit calculée
        emplacement.update_idletasks()

        # On récupère les dimensions du contenu
        hauteur_contenu = emplacement.winfo_reqheight()
        largeur_contenu = emplacement.winfo_reqwidth()

        # On cherche le widget correspondant à la valeur actuelle
        target_widget = None
        for widget in lst_btn:
            if widget.cget("text") == valeur_actuelle:
                target_widget = widget
                break

        # Si on l'a trouvé et que la liste est assez grande pour défiler
        if target_widget:
            hauteur_canvas = cnv_btn.winfo_height()

            if hauteur_contenu > hauteur_canvas:
                # On calcule la position relative du widget (de 0.0 à 1.0)
                position_y_widget = target_widget.winfo_y()
                scroll_fraction = position_y_widget / hauteur_contenu
                # On demande au canvas de défiler à cette position
                cnv_btn.yview_moveto(scroll_fraction)

        # On ajuste la hauteur du canvas si le contenu est plus petit que la hauteur max
        if hauteur_contenu < hauteur_max:
            cnv_btn.config(height=hauteur_contenu)
            vScroll.grid_remove()  # On cache la scrollbar si inutile

        # On ajuste la largeur du canvas à la largeur du contenu
        cnv_btn.config(width=largeur_contenu)

        # On définit manuellement la zone de défilement à la taille réelle du contenu
        cnv_btn.config(scrollregion=cnv_btn.bbox("all"))

        if hauteur_contenu > hauteur_max:
            emplacement.bind("<MouseWheel>", lambda e: mousewheel(e, cnv_btn))
            for btn in lst_btn:
                btn.bind("<MouseWheel>", lambda e: mousewheel(e, cnv_btn))

        frame_choix.bind("<Escape>", lambda e: frame_choix.destroy())

    def configurer_axes(self):
        """
        Ouvre une fenêtre de configuration pour modifier les limites des axes du graphique.
        """
        onglet_actif = self._get_active_onglet()
        if not onglet_actif or not onglet_actif.fig.axes:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        # S'il y a une fenêtre de configuration déjà ouverte, elle est détruite
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel):
                if child.title() == "Configuration des axes":
                    child.destroy()

        ax_list = onglet_actif.fig.axes
        unite_x = onglet_actif.varGr_x.get()

        config_frame = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        config_frame.title("Configuration des axes")
        config_frame.focus_force()
        config_frame.resizable(False, False)

        # --- Fonctions imbriquées pour la logique interne ---
        def valider_changements():
            try:
                # Récupération et validation des valeurs
                if donnees_axe1:
                    y1_min, y1_max, y1_grad = y1min_var.get(), y1max_var.get(), y1grad_var.get()
                    if y1_min + y1_grad > y1_max:
                        y1_grad = y1_max - y1_min
                    if y1_max <= y1_min or y1_grad <= 0:
                        raise ValueError(
                            "Limites ou intervalle invalide(s) pour l'axe 1")
                    ax_list[0].set_ylim(y1_min, y1_max)
                    y1_ticks = np.arange(y1_min, y1_max + y1_grad, y1_grad)
                    if y1_ticks[-1] > y1_max:
                        y1_ticks = y1_ticks[0:-1]
                    ax_list[0].yaxis.set_ticks(y1_ticks)

                if donnees_axe2:
                    y2_min, y2_max, y2_grad = y2min_var.get(), y2max_var.get(), y2grad_var.get()
                    if y2_min + y2_grad > y2_max:
                        y2_grad = y2_max - y2_min
                    if y2_max <= y2_min or y2_grad <= 0:
                        raise ValueError(
                            "Limites ou intervalle invalide(s) pour l'axe 2")
                    ax_list[1].set_ylim(y2_min, y2_max)
                    y2_ticks = np.arange(y2_min, y2_max + y2_grad, y2_grad)
                    if y2_ticks[-1] > y2_max:
                        y2_ticks = y2_ticks[0:-1]
                    ax_list[1].yaxis.set_ticks(y2_ticks)

                # Gestion de l'axe X
                if unite_x == "Temps":
                    # Reconstruire les dates à partir des labels
                    xmin_dt = datetime.strptime(
                        f"{xdatemin_lbl.cget('text')} {xhmin_lbl.cget('text')}:{xmnmin_lbl.cget('text')}", "%d/%m/%Y %H:%M")
                    xmax_dt = datetime.strptime(
                        f"{xdatemax_lbl.cget('text')} {xhmax_lbl.cget('text')}:{xmnmax_lbl.cget('text')}", "%d/%m/%Y %H:%M")
                    j_grad = int(j_lbl.cget("text"))
                    h_grad = int(h_lbl.cget("text"))
                    min_grad = int(mn_lbl.cget("text"))
                    delta = timedelta(
                        days=j_grad, hours=h_grad, minutes=min_grad)
                    if xmin_dt + delta > xmax_dt:
                        delta = xmax_dt - xmin_dt
                    if xmax_dt <= xmin_dt or delta <= timedelta(days=0, hours=0, minutes=0):
                        raise ValueError(
                            "Limites ou intervalle invalide(s) pour l'axe x")
                    ax_list[0].set_xlim(xmin_dt, xmax_dt)
                    x_ticks = np.arange(
                        xmin_dt, xmax_dt + delta, delta).astype(datetime)
                    if x_ticks[-1] > xmax_dt:
                        x_ticks = x_ticks[0:-1]
                else:  # Tonnage
                    x_min, x_max, x_grad = xmin_var.get(), xmax_var.get(), xgraduation_var.get()
                    if x_min + x_grad > x_max:
                        x_grad = x_max - x_min
                    if x_max <= x_min or x_grad <= 0:
                        raise ValueError(
                            "Limites ou intervalle invalide(s) pour l'axe x")
                    ax_list[0].set_xlim(x_min, x_max)
                    x_ticks = np.arange(x_min, x_max + x_grad, x_grad)
                    if x_ticks[-1] > x_max:
                        x_ticks = x_ticks[0:-1]
                ax_list[0].xaxis.set_ticks(x_ticks)
                plt.setp(ax_list[0].get_xticklabels(), rotation_mode="anchor")

                onglet_actif.fig.canvas.draw_idle()
                config_frame.destroy()
            except Exception as e:
                messagebox.showerror("Erreur de Saisie",
                                     str(e), parent=config_frame)

        def reinitialiser():
            for ax in ax_list:
                ax.autoscale()
            onglet_actif.fig.canvas.draw_idle()
            config_frame.destroy()

        # --- Construction de l'interface de la fenêtre ---
        tableau = tk.Frame(config_frame)
        tableau.grid(column=0, row=0, padx=1, pady=1)
        tk.Label(
            tableau, text="Axe x", font="Arial 10 bold", width=10, bg="white",
        ).grid(column=1, row=0, padx=1, pady=1, sticky="ew")
        tk.Label(
            tableau, text="Axe 1", font="Arial 10 bold", fg="blue", width=10, bg="white",
        ).grid(column=2, row=0, padx=1, pady=1, sticky="ew")
        tk.Label(
            tableau, text="Axe 2", font="Arial 10 bold", fg="red", width=10, bg="white",
        ).grid(column=3, row=0, padx=1, pady=1, sticky="ew")

        tk.Label(
            tableau, text="Minimum", height=2, bg="white",
        ).grid(row=1, column=0, padx=1, pady=1, sticky="nsew")
        tk.Label(
            tableau, text="Maximum", height=2, bg="white",
        ).grid(row=2, column=0, padx=1, pady=1, sticky="nsew")
        tk.Label(
            tableau, text="Intervalle\ngraduations", height=2, bg="white",
        ).grid(row=3, column=0, padx=1, pady=1, sticky="nsew")

        # --- Widgets pour l'axe x ---
        xmin, xmax = ax_list[0].get_xlim()
        if unite_x == "Temps":
            dt = mdates.num2date(xmin).date()
            lst_dt = []
            while dt != mdates.num2date(xmax).date():
                lst_dt.append(dt)
                dt += timedelta(days=1)
            lst_dt.append(mdates.num2date(xmax).date())
        xticks = ax_list[0].get_xticks()

        xmin_frame = tk.Frame(tableau, bg="white")
        xmin_frame.columnconfigure(0, weight=1)
        xmin_frame.columnconfigure(2, weight=1)
        xmin_frame.grid(column=1, row=1, padx=1, pady=1, sticky="nsew")
        xmax_frame = tk.Frame(tableau, bg="white")
        xmax_frame.columnconfigure(0, weight=1)
        xmax_frame.columnconfigure(2, weight=1)
        xmax_frame.grid(column=1, row=2, padx=1, pady=1, sticky="nsew")
        xgraduation_frame = tk.Frame(tableau, bg="white")
        xgraduation_frame.columnconfigure(0, weight=1)
        xgraduation_frame.columnconfigure(3, weight=1)
        xgraduation_frame.grid(column=1, row=3, padx=1, pady=1, sticky="nsew")
        if unite_x == "Temps":
            xdatemin_lbl = tk.Label(xmin_frame, bg="white")
            xdatemin_lbl.bind(
                "<Button-1>",
                lambda e: self.afficher_calendrier(e, xdatemin_lbl, lst_dt),
            )
            xhmin_lbl = tk.Label(
                xmin_frame, justify="right", bg="white", padx=0)
            xhmin_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(xhmin_lbl, np.arange(0, 24)),
            )
            xmnmin_lbl = tk.Label(
                xmin_frame, justify="left", bg="white", padx=0)
            xmnmin_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(xmnmin_lbl, np.arange(0, 60)),
            )
            xdatemin_lbl.grid(column=0, row=0, columnspan=3)
            xhmin_lbl.grid(column=0, row=1, sticky="e")
            tk.Label(xmin_frame, text=":", bg="white",
                     padx=0, bd=0).grid(column=1, row=1)
            xmnmin_lbl.grid(column=2, row=1, sticky="w")
            xmin_var = None

            xdatemax_lbl = tk.Label(xmax_frame, bg="white")
            xdatemax_lbl.bind(
                "<Button-1>",
                lambda e: self.afficher_calendrier(e, xdatemax_lbl, lst_dt),
            )
            xhmax_lbl = tk.Label(
                xmax_frame, justify="right", bg="white", padx=0)
            xhmax_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(xhmax_lbl, np.arange(0, 24)),
            )
            xmnmax_lbl = tk.Label(
                xmax_frame, justify="left", bg="white", padx=0)
            xmnmax_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(xmnmax_lbl, np.arange(0, 60)),
            )
            xdatemax_lbl.grid(column=0, row=0, columnspan=3)
            xhmax_lbl.grid(column=0, row=1, sticky="e")
            tk.Label(xmax_frame, text=":", bg="white",
                     padx=0, bd=0).grid(column=1, row=1)
            xmnmax_lbl.grid(column=2, row=1, sticky="w")
            xmax_var = None

            j_lbl = tk.Label(xgraduation_frame, bg="white")
            h_lbl = tk.Label(xgraduation_frame, bg="white")
            h_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(h_lbl, np.arange(0, 24)),
            )
            mn_lbl = tk.Label(xgraduation_frame, bg="white")
            mn_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(mn_lbl, np.arange(0, 60)),
            )
            j_lbl.grid(column=0, row=0, columnspan=2, sticky="e")
            tk.Label(xgraduation_frame, text="jour(s)", bg="white", padx=0, bd=0).grid(
                column=2, row=0, columnspan=2, sticky="w")
            h_lbl.grid(column=0, row=1, sticky="e")
            tk.Label(xgraduation_frame, text="h", bg="white", padx=0, bd=0).grid(
                column=1, row=1)
            mn_lbl.grid(column=2, row=1)
            tk.Label(xgraduation_frame, text="min", bg="white", padx=0, bd=0).grid(
                column=3, row=1, sticky="w")
            xgraduation_var = None
        else:
            xmin_var = tk.DoubleVar()
            xmin_frame.rowconfigure(0, weight=1)
            xmin_entry = tk.Entry(
                xmin_frame, width=10, justify="center", relief="flat")
            xmin_entry.grid(column=0, row=0, sticky="nsew")
            xmax_var = tk.DoubleVar()
            xmax_frame.rowconfigure(0, weight=1)
            xmax_entry = tk.Entry(
                xmax_frame, width=10, justify="center", relief="flat")
            xmax_entry.grid(column=0, row=0, sticky="nsew")
            xgraduation_var = tk.DoubleVar()
            xgraduation_frame.rowconfigure(0, weight=1)
            xgraduation_entry = tk.Entry(
                xgraduation_frame, width=10, justify="center", relief="flat")
            xgraduation_entry.grid(column=0, row=0, sticky="nsew")

        if unite_x == "Temps":
            date_min = mdates.num2date(xmin)
            xdatemin_lbl.configure(text=date_min.strftime("%d/%m/%Y"))
            xhmin_lbl.configure(text=date_min.strftime("%H"))
            xmnmin_lbl.configure(text=date_min.strftime("%M"))

            date_max = mdates.num2date(xmax)
            xdatemax_lbl.configure(text=date_max.strftime("%d/%m/%Y"))
            xhmax_lbl.configure(text=date_max.strftime("%H"))
            xmnmax_lbl.configure(text=date_max.strftime("%M"))

            delta_temps = mdates.num2date(
                xticks[1]) - mdates.num2date(xticks[0])
            nb_jours, nb_secondes = delta_temps.days, delta_temps.seconds
            nb_heures = nb_secondes // 3600
            nb_minutes = (nb_secondes % 3600) // 60

            j_max = int(xmax) - int(xmin)
            lst_jours = [i for i in range(0, j_max+1)]
            nb_digits = len(str(j_max))
            text_jours = "{num:0{width}}".format(num=nb_jours, width=nb_digits)
            j_lbl.configure(text=text_jours)
            j_lbl.bind(
                "<Button-1>",
                lambda e: self.fenetre_choix(j_lbl, lst_jours),
            )
            h_lbl.configure(text="{:02d}".format(nb_heures))
            mn_lbl.configure(text="{:02d}".format(nb_minutes))
        else:
            xmin_var.set(round(xmin, 1))
            xmax_var.set(round(xmax, 1))
            xgraduation = xticks[1] - xticks[0]
            xgraduation_var.set(round(xgraduation, 1))
            xmin_entry.configure(textvariable=xmin_var)
            xmax_entry.configure(textvariable=xmax_var)
            xgraduation_entry.configure(textvariable=xgraduation_var)

        _, _, _, _, _, _, donnees_axe1, donnees_axe2 = onglet_actif._get_parametres()

        # --- Widgets pour l'Axe 1 (Y) ---
        if donnees_axe1:
            y1min, y1max = ax_list[0].get_ylim()
            y1_ticks = ax_list[0].get_yticks()
            y1_interval = y1_ticks[1] - y1_ticks[0] if len(y1_ticks) > 1 else 1
            y1min_var = tk.DoubleVar(value=round(y1min, 2))
            y1max_var = tk.DoubleVar(value=round(y1max, 2))
            y1grad_var = tk.DoubleVar(value=round(y1_interval, 2))
            state = "normal"
        else:
            y1min_var = ""
            y1max_var = ""
            y1grad_var = ""
            state = "disabled"
        tk.Entry(
            tableau, textvariable=y1min_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=1, column=2, padx=1, pady=1, sticky="nsew")
        tk.Entry(
            tableau, textvariable=y1max_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=2, column=2, padx=1, pady=1, sticky="nsew")
        tk.Entry(
            tableau, textvariable=y1grad_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=3, column=2, padx=1, pady=1, sticky="nsew")

        # --- Widgets pour l'Axe 2 (Y) ---
        if donnees_axe2:
            y2min, y2max = ax_list[1].get_ylim()
            y2_ticks = ax_list[1].get_yticks()
            y2_interval = y2_ticks[1] - y2_ticks[0] if len(y2_ticks) > 1 else 1
            y2min_var = tk.DoubleVar(value=round(y2min, 2))
            y2max_var = tk.DoubleVar(value=round(y2max, 2))
            y2grad_var = tk.DoubleVar(value=round(y2_interval, 2))
            state = "normal"
        else:
            y2min_var = ""
            y2max_var = ""
            y2grad_var = ""
            state = "disabled"
        tk.Entry(
            tableau, textvariable=y2min_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=1, column=3, padx=1, pady=1, sticky="nsew")
        tk.Entry(
            tableau, textvariable=y2max_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=2, column=3, padx=1, pady=1, sticky="nsew")
        tk.Entry(
            tableau, textvariable=y2grad_var, width=10, justify="center", bd=0, state=state, disabledbackground="#d2d3d4",
        ).grid(row=3, column=3, padx=1, pady=1, sticky="nsew")

        # Boutons de commande
        btn_frame = tk.Frame(config_frame, bg="white")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        tk.Button(btn_frame, text="Réinitialiser axes",
                  command=reinitialiser).grid(column=0, row=0, pady=2)
        tk.Button(btn_frame, text="Valider", command=valider_changements).grid(
            column=1, row=0, pady=2)
        tk.Button(btn_frame, text="Annuler", command=config_frame.destroy).grid(
            column=2, row=0, padx=2, pady=2)

        config_frame.bind("<Return>", lambda e: valider_changements())
        config_frame.bind("<Escape>", lambda e: config_frame.destroy())

    def choix_style(self, lbl):
        """Ouvre une fenêtre pour choisir un style de ligne."""
        lst_styles = ["Aucun", "______", "..........", "------", "-.-.-.-."]
        self.fenetre_choix(lbl, lst_styles)

    def choix_couleur(self, parent_window, lbl):
        """Ouvre le sélecteur de couleur."""
        couleur_init = lbl.cget("bg")
        couleur = askcolor(parent=parent_window,
                           color=couleur_init, title="Choix de couleur")
        if couleur and couleur[1]:
            lbl.configure(bg=couleur[1])

    def choix_marqueur(self, lbl):
        """Ouvre une fenêtre pour choisir un style de marqueur."""
        lst_marqueurs = ["Aucun", "Rond", "Carré",
                         "Triangle", "Losange", "x", "+", "-"]
        self.fenetre_choix(lbl, lst_marqueurs)

    def configurer_donnees(self):
        """
        Ouvre une fenêtre de configuration pour modifier le style des séries de données.
        """
        onglet_actif = self._get_active_onglet()
        if not onglet_actif or not onglet_actif.fig.axes:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        # S'il y a une fenêtre de configuration déjà ouverte, elle est détruite
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel):
                if child.title() == "Mise en forme des séries de données":
                    child.destroy()

        fig = onglet_actif.fig
        ax_list = fig.axes
        keys = [k for k in onglet_actif.courbes_graphe.keys() if k !=
                'valeurs_x']

        # Création de la fenêtre Toplevel
        fenetre = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        fenetre.title("Mise en forme des séries de données")
        # fenetre.transient(self)
        # fenetre.grab_set()
        fenetre.focus_force()
        fenetre.resizable(False, False)

        # Listes pour stocker les widgets de chaque ligne
        lst_widgets = []
        intitules_styles = ["Aucun", "______",
                            "..........", "------", "-.-.-.-."]
        styles_matplotlib = ["None", "-", ":", "--", "-."]
        intitules_marqueurs = ["Aucun", "Rond", "Carré",
                               "Triangle", "Losange", "x", "+", "-"]
        marqueurs_matplotlib = ["", "o", "s", "^", "D", "x", "+", "_"]

        def valider_changements():
            # Logique de l'ancienne fonction 'configure_donnees_2'
            try:
                for i, line in enumerate([l for axe in ax_list for l in axe.lines if l.get_label() in keys]):
                    widgets_ligne = lst_widgets[i]

                    # Style et couleur du trait
                    style_str = widgets_ligne['style_trait'].cget("text")
                    line.set_linestyle(
                        styles_matplotlib[intitules_styles.index(style_str)])
                    line.set_color(widgets_ligne['couleur_trait'].cget("bg"))
                    line.set_linewidth(
                        float(widgets_ligne['epaisseur_trait'].get()))

                    # Forme, couleur et taille du marqueur
                    marqueur_str = widgets_ligne['forme_marqueur'].cget("text")
                    line.set_marker(
                        marqueurs_matplotlib[intitules_marqueurs.index(marqueur_str)])
                    line.set_markerfacecolor(
                        widgets_ligne['couleur_marqueur'].cget("bg"))
                    line.set_markeredgecolor(
                        widgets_ligne['couleur_marqueur'].cget("bg"))
                    line.set_markersize(
                        float(widgets_ligne['taille_marqueur'].get()))

                # Mettre à jour les légendes
                axe1 = ax_list[0]
                axe2 = ax_list[1] if len(ax_list) > 1 else None

                if axe1.get_legend():
                    pos_legend_1 = (0.5, 1.18) if axe2 else (0.5, 1.1)
                    axe1.legend(edgecolor="blue", loc="upper center",
                                bbox_to_anchor=pos_legend_1, fancybox=True, ncol=5)
                if axe2 and axe2.get_legend():
                    pos_legend_2 = (0.5, 1.1)
                    axe2.legend(edgecolor="red", loc="upper center",
                                bbox_to_anchor=pos_legend_2, fancybox=True, ncol=5)

                fig.canvas.draw_idle()
                fenetre.destroy()

            except ValueError:
                messagebox.showerror(
                    "Erreur de Saisie", "L'épaisseur et la taille doivent être des nombres valides.", parent=fenetre)
            except Exception as e:
                messagebox.showerror(
                    "Erreur", f"Une erreur est survenue : {e}", parent=fenetre)

        # --- Construction de l'interface de la fenêtre ---
        frame_widget = tk.Frame(fenetre)
        frame_widget.grid(row=0, column=0, padx=1, pady=1)

        hauteur_max = 150
        # 1. On crée le Canvas principal et la Scrollbar
        canvas_principal = tk.Canvas(
            frame_widget, height=hauteur_max, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            frame_widget, orient="vertical", command=canvas_principal.yview)
        # Le frame qui contiendra les widgets
        frame_contenu = tk.Frame(canvas_principal)

        canvas_principal.configure(yscrollcommand=scrollbar.set)

        scrollbar.grid(row=2, column=7, sticky="ns")
        canvas_principal.grid(row=2, column=0, columnspan=7, sticky="nsew")

        canvas_principal.create_window(
            (0, 0), window=frame_contenu, anchor="nw")

        def on_frame_configure(event):
            canvas_principal.configure(
                scrollregion=canvas_principal.bbox("all"))

        frame_contenu.bind("<Configure>", on_frame_configure)

        # En-têtes
        tk.Label(frame_widget, width=25).grid(
            row=0, column=0, rowspan=2, padx=1, pady=1, sticky="nsew")
        tk.Label(
            frame_widget, text="Configuration du trait", font="Arial 10 bold", fg="white", bg="#325faa",
        ).grid(row=0, column=1, columnspan=3, sticky="ew", padx=1, pady=1)
        tk.Label(
            frame_widget, text="Configuration des marqueurs", font="Arial 10 bold", fg="white", bg="#325faa",
        ).grid(row=0, column=4, columnspan=3, sticky="ew", padx=1, pady=1)
        tk.Label(frame_widget, text="Style", width=10, bg="#dfe7f5").grid(
            column=1, row=1, padx=1, pady=1)
        tk.Label(frame_widget, text="Couleur", width=10,
                 bg="#dfe7f5").grid(column=2, row=1, padx=1, pady=1)
        tk.Label(frame_widget, text="Epaisseur", width=10,
                 bg="#dfe7f5").grid(column=3, row=1, padx=1, pady=1)
        tk.Label(frame_widget, text="Forme", width=10, bg="#dfe7f5").grid(
            column=4, row=1, padx=1, pady=1)
        tk.Label(frame_widget, text="Couleur", width=10,
                 bg="#dfe7f5").grid(column=5, row=1, padx=1, pady=1)
        tk.Label(frame_widget, text="Taille", width=10, bg="#dfe7f5").grid(
            column=6, row=1, padx=1, pady=1)

        # Création des widgets pour chaque courbe
        lignes_a_configurer = [
            line for axe in ax_list for line in axe.lines if line.get_label() in keys]

        lst_noms_fonds = []
        for i, line in enumerate(lignes_a_configurer):
            nom = line.get_label()

            widgets_ligne = {}
            nom_lbl = tk.Label(frame_contenu, text=nom,
                               anchor='w', width=25, bg="white")
            nom_lbl.grid(row=i, column=0, padx=1, pady=1, sticky='ns')
            lst_noms_fonds.append(nom_lbl)

            # Widgets pour le trait
            style_actuel = intitules_styles[styles_matplotlib.index(
                line.get_linestyle() or 'None')]
            lbl_style = tk.Label(
                frame_contenu, text=style_actuel, bg='white', width=10)
            lbl_style.bind("<Button-1>", lambda e,
                           l=lbl_style: self.choix_style(l))
            lbl_style.grid(row=i, column=1, padx=1, pady=1, sticky="ns")
            widgets_ligne['style_trait'] = lbl_style

            fond_trait = tk.Frame(frame_contenu, bg="white")
            fond_trait.grid(row=i, column=2, padx=1,
                            pady=1, sticky="nsew", ipadx=28)
            fond_trait.columnconfigure(0, weight=1)
            fond_trait.rowconfigure(0, weight=1)
            lbl_couleur_trait = tk.Label(
                fond_trait, bg=line.get_color(), relief="groove", width=2)
            lbl_couleur_trait.bind(
                "<Button-1>", lambda e, l=lbl_couleur_trait: self.choix_couleur(fenetre, l))
            lbl_couleur_trait.grid(row=0, column=0)
            widgets_ligne['couleur_trait'] = lbl_couleur_trait
            lst_noms_fonds.append(fond_trait)

            entry_epaisseur = tk.Entry(
                frame_contenu, bg="white", width=12, justify='center', bd=0)
            entry_epaisseur.insert(0, line.get_linewidth())
            entry_epaisseur.grid(row=i, column=3, padx=1,
                                 pady=1, sticky="ns", ipadx=1)
            widgets_ligne['epaisseur_trait'] = entry_epaisseur

            # Widgets pour le marqueur
            marqueur_actuel = intitules_marqueurs[marqueurs_matplotlib.index(
                line.get_marker() or '')]
            lbl_marqueur = tk.Label(
                frame_contenu, text=marqueur_actuel, bg='white', width=10, anchor="center")
            lbl_marqueur.bind("<Button-1>", lambda e,
                              l=lbl_marqueur: self.choix_marqueur(l))
            lbl_marqueur.grid(row=i, column=4, padx=1, pady=1, sticky="ns")
            widgets_ligne['forme_marqueur'] = lbl_marqueur

            fond_marqueur = tk.Frame(frame_contenu, bg="white")
            fond_marqueur.grid(row=i, column=5, padx=1,
                               pady=1, sticky="nsew", ipadx=28)
            fond_marqueur.columnconfigure(0, weight=1)
            fond_marqueur.rowconfigure(0, weight=1)
            lbl_couleur_marqueur = tk.Label(
                fond_marqueur, bg=line.get_markerfacecolor(), relief='groove', width=2)
            lbl_couleur_marqueur.bind(
                "<Button-1>", lambda e, l=lbl_couleur_marqueur: self.choix_couleur(fenetre, l))
            lbl_couleur_marqueur.grid(column=0, row=0)
            widgets_ligne['couleur_marqueur'] = lbl_couleur_marqueur
            lst_noms_fonds.append(fond_marqueur)

            entry_taille = tk.Entry(
                frame_contenu, bg="white", width=12, justify='center', bd=0)
            entry_taille.insert(0, line.get_markersize())
            entry_taille.grid(row=i, column=6, padx=1,
                              pady=1, sticky="ns", ipadx=1)
            widgets_ligne['taille_marqueur'] = entry_taille

            lst_widgets.append(widgets_ligne)

        frame_contenu.update()

        hauteur_contenu = frame_contenu.winfo_reqheight()

        if hauteur_contenu < hauteur_max:
            canvas_principal.config(height=hauteur_contenu)
            scrollbar.grid_remove()

        canvas_principal.configure(scrollregion=canvas_principal.bbox("all"))

        if hauteur_contenu > hauteur_max:
            frame_contenu.bind(
                "<MouseWheel>", lambda e: mousewheel(e, canvas_principal))
            for dic in lst_widgets:
                for widget in dic.values():
                    widget.bind("<MouseWheel>", lambda e: mousewheel(
                        e, canvas_principal))
            for widget in lst_noms_fonds:
                widget.bind("<MouseWheel>", lambda e: mousewheel(
                    e, canvas_principal))

        # Boutons de commande
        frame_btn = tk.Frame(fenetre, bg="white")
        frame_btn.columnconfigure(0, weight=1)
        frame_btn.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        btn_valider = tk.Button(frame_btn, text="Valider",
                                command=valider_changements)
        btn_valider.grid(row=0, column=0, pady=2, sticky="e")
        tk.Button(frame_btn, text="Annuler", command=fenetre.destroy).grid(
            row=0, column=1, padx=2, pady=2)
        fenetre.bind("<Return>", lambda event: btn_valider.invoke())
        fenetre.bind("<Escape>", lambda e: fenetre.destroy())

    def tracer_tendance(self):
        """
        Ouvre une fenêtre pour sélectionner et tracer des courbes de tendance.
        """
        onglet_actif = self._get_active_onglet()
        if not onglet_actif or not onglet_actif.fig.axes:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        fig = onglet_actif.fig
        ax_list = fig.axes

        # S'assure de fermer une fenêtre de tendance potentiellement déjà ouverte
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel) and child.title() == "Gestion des courbes de tendance":
                child.destroy()

        # Récupère les noms des courbes depuis le graphique
        keys = [k for k in onglet_actif.courbes_graphe.keys() if k !=
                'valeurs_x']
        if not keys:
            messagebox.showinfo(
                "Information", "Aucune courbe de données n'a été trouvée.", parent=self)
            return

        fenetre_tendance = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        fenetre_tendance.title("Gestion des courbes de tendance")
        # fenetre_tendance.transient(self)
        # fenetre_tendance.grab_set()
        fenetre_tendance.focus_force()
        fenetre_tendance.resizable(False, False)

        # On initialise ou on vide le dictionnaire des tendances sur l'onglet actif
        if not hasattr(onglet_actif, 'tendance_info'):
            onglet_actif.tendance_info = {}

        # Logique imbriquée pour tracer les tendances
        def selectionner(var, spin_box, style, couleur, fond, epaisseur):
            if var.get():
                spin_box.config(state="readonly")
                style.bind("<Button-1>", lambda e,
                           l=style: self.choix_style(l))
                style.config(bg="white")
                couleur.bind("<Button-1>", lambda e,
                             l=couleur: self.choix_couleur(fenetre_tendance, l))
                fond.config(bg="white")
                epaisseur.config(state="normal")
            else:
                spin_box.config(state="disabled")
                style.unbind("<Button-1>")
                style.config(bg="#d2d3d4")
                couleur.unbind("<Button-1>")
                fond.config(bg="#d2d3d4")
                epaisseur.config(state="disabled")

        def valider_tendances(list_vars, list_spinbox, list_style, list_couleur, list_epaisseur):
            # On supprime d'abord toutes les anciennes courbes de tendances
            for line_artist in list(onglet_actif.tendance_info.keys()):
                try:
                    line_artist.remove()
                except (ValueError, KeyError):
                    pass  # L'artiste a peut-être déjà été supprimé

            # On vide complètement le dictionnaire de suivi
            onglet_actif.tendance_info.clear()
            choix_unite = onglet_actif.varGr_x.get()
            courbes_axe1 = ax_list[0].get_legend_handles_labels()[1]
            courbes_axe2 = ax_list[1].get_legend_handles_labels()[
                1] if len(ax_list) > 1 else []

            intitules_styles = ["Aucun", "______",
                                "..........", "------", "-.-.-.-."]
            styles_matplotlib = ["None", "-", ":", "--", "-."]

            try:
                for i, var in enumerate(list_vars):
                    if var.get() == 1:
                        nom_courbe = keys[i]
                        degre = int(list_spinbox[i].get())
                        style = list_style[i].cget("text")
                        style = styles_matplotlib[intitules_styles.index(
                            style)]
                        couleur = list_couleur[i].cget("bg")
                        epaisseur = float(list_epaisseur[i].get())

                        # Sélectionne le bon axe pour tracer la tendance
                        axe_a_utiliser = ax_list[0] if nom_courbe in courbes_axe1 else (
                            ax_list[1] if nom_courbe in courbes_axe2 else None)
                        if not axe_a_utiliser:
                            continue

                        x_data = onglet_actif.courbes_graphe[nom_courbe][0]
                        y_data = onglet_actif.courbes_graphe[nom_courbe][1]

                        # Filtre les valeurs non valides (NaN)
                        valid_indices = ~np.isnan(y_data)
                        if np.count_nonzero(valid_indices) < degre + 1:
                            continue  # Pas assez de points pour calculer la tendance

                        x_valid = np.array(x_data)[valid_indices]
                        y_valid = np.array(y_data)[valid_indices]

                        with warnings.catch_warnings():
                            warnings.filterwarnings(
                                'ignore', category=np.RankWarning)

                            if choix_unite != "Temps":
                                # 1. On trie les points par ordre croissant
                                sort_indices = np.argsort(x_valid)
                                x_sorted = x_valid[sort_indices]
                                y_sorted = y_valid[sort_indices]
                                # 2. On calcule la tendance sur les points triés
                                coefficients = np.polyfit(
                                    x_sorted, y_sorted, degre)
                                polynome = np.poly1d(coefficients)
                                # 3. On trace la courbe sur l'axe trié pour un affichage lisse
                                tendance_line, = axe_a_utiliser.plot(x_sorted, polynome(
                                    x_sorted), linestyle=style, color=couleur, linewidth=epaisseur, picker=2)
                            else:
                                coefficients = np.polyfit(
                                    x_valid, y_valid, degre)
                                polynome = np.poly1d(coefficients)
                                tendance_line, = axe_a_utiliser.plot(x_valid, polynome(
                                    x_valid), linestyle=style, color=couleur, linewidth=epaisseur, picker=2)

                        # On stocke tous les paramètres de la tendance DANS L'ONGLET
                        equation_formatee = formater_equation(polynome)
                        onglet_actif.tendance_info[tendance_line] = {
                            'nom': nom_courbe,
                            'equation': equation_formatee,
                            'degre': degre,
                            'style': style,
                            'couleur': couleur,
                            'epaisseur': epaisseur
                        }

                fig.canvas.draw_idle()
                fenetre_tendance.destroy()

            except ValueError:
                messagebox.showerror(
                    "Erreur de Saisie", "L'épaisseur doivent être un nombre valide.", parent=fenetre_tendance)
            except Exception as e:
                messagebox.showerror(
                    "Erreur", f"Une erreur est survenue : {e}", parent=fenetre_tendance)

        # --- Construction de l'interface de la fenêtre ---
        tableau = tk.Frame(fenetre_tendance)
        tableau.grid(column=0, row=0, padx=1, pady=1)
        tableau.columnconfigure(0, weight=1)

        # En-têtes
        tk.Label(tableau, text="Degré\npolynôme", font="Arial 10 bold", fg="white", bg="#325faa",
                 justify="center").grid(column=1, row=0, rowspan=2, padx=1, pady=1, sticky="nsew")

        tk.Label(
            tableau, text="Configuration du trait", font="Arial 10 bold", fg="white", bg="#325faa",
        ).grid(row=0, column=2, columnspan=3, sticky="ew", padx=1, pady=1)
        tk.Label(tableau, text="Style", width=10, bg="#dfe7f5").grid(
            column=2, row=1, padx=1, pady=1)
        tk.Label(tableau, text="Couleur", width=10, bg="#dfe7f5").grid(
            column=3, row=1, padx=1, pady=1)
        tk.Label(tableau, text="Epaisseur", width=10, bg="#dfe7f5").grid(
            column=4, row=1, padx=1, pady=1)

        # Canvas scrollable pour la liste des courbes
        hauteur_max = 150
        cnv_tendance = tk.Canvas(
            tableau, height=hauteur_max, width=500, highlightthickness=0)
        cnv_tendance.grid(row=2, column=0, columnspan=5, sticky="nsew")

        frame_scrollable = tk.Frame(cnv_tendance)
        frame_scrollable.columnconfigure(0, weight=1)

        vscroll = tk.Scrollbar(tableau, orient="vertical",
                               command=cnv_tendance.yview)
        vscroll.grid(row=2, column=5, sticky="ns")

        tableau.update()
        cnv_tendance.configure(yscrollcommand=vscroll.set)
        cnv_tendance.create_window(
            cnv_tendance.winfo_rootx(),
            cnv_tendance.winfo_rooty(),
            anchor="nw",
            window=frame_scrollable,
            width=cnv_tendance.winfo_width(),
        )
        cnv_tendance.configure(scrollregion=cnv_tendance.bbox("all"))
        cnv_tendance.yview("moveto", 0.0)

        list_vars = []
        list_chk_btn = []
        list_spinbox = []
        list_style = []
        list_couleur = []
        list_epaisseur = []
        list_cmde = []

        all_lines = ax_list[0].lines + \
            (ax_list[1].lines if len(ax_list) > 1 else [])

        intitules_styles = ["Aucun", "______",
                            "..........", "------", "-.-.-.-."]
        styles_matplotlib = ["None", "-", ":", "--", "-."]

        for i, nom_courbe in enumerate(keys):
            var = tk.IntVar(value=0)
            list_vars.append(var)

            line_color = ""
            for line in all_lines:
                if line.get_label() == nom_courbe:
                    line_color = line.get_color()
                    break

            chk_btn = tk.Checkbutton(
                frame_scrollable, text=nom_courbe, variable=var, anchor="w", fg=line_color, bg="#d2d3d4",
            )
            chk_btn.grid(column=0, row=i, sticky="nsew", padx=1, pady=1)
            list_chk_btn.append(chk_btn)

            spin_box = tk.Spinbox(
                frame_scrollable,
                justify="center",
                width=9,
                from_=1,
                to=9,
                increment=1,
                readonlybackground="white",
                disabledbackground="#d2d3d4",
                bd=0,
                state="disabled",
            )
            spin_box.grid(column=1, row=i, ipadx=1,
                          padx=1, pady=1, sticky="nsew")
            list_spinbox.append(spin_box)

            lbl_style = tk.Label(
                frame_scrollable, text="------", bg="#d2d3d4", width=10)
            lbl_style.grid(row=i, column=2, padx=1, pady=1, sticky="ns")
            list_style.append(lbl_style)

            fond = tk.Frame(frame_scrollable, bg="#d2d3d4")
            fond.grid(row=i, column=3, padx=1, pady=1, sticky="nsew", ipadx=28)
            fond.columnconfigure(0, weight=1)
            fond.rowconfigure(0, weight=1)
            lbl_couleur = tk.Label(fond, bg=line_color,
                                   relief="groove", width=2)
            lbl_couleur.grid(row=0, column=0)
            list_couleur.append(lbl_couleur)

            epaisseur = tk.Entry(
                frame_scrollable,
                bg="white",
                disabledbackground="#d2d3d4",
                width=12,
                justify='center',
                bd=0,
            )
            epaisseur.insert(0, line.get_linewidth())
            epaisseur.config(state="disabled")
            epaisseur.grid(row=i, column=4, padx=1,
                           pady=1, sticky="ns", ipadx=1)
            list_epaisseur.append(epaisseur)

            # On vérifie si une tendance existe déjà
            tendance_existante_info = None
            for info in onglet_actif.tendance_info.values():
                if info['nom'] == nom_courbe:
                    tendance_existante_info = info
                    break

            if tendance_existante_info:
                var.set(1)  # Coche la case
                chk_btn.config(bg="white")

                # Active les widgets de style
                spin_box.config(state="normal")
                lbl_style.config(bg="white")
                lbl_style.bind("<Button-1>", lambda e,
                               l=lbl_style: self.choix_style(l))
                fond.config(bg="white")
                lbl_couleur.bind(
                    "<Button-1>", lambda e, l=lbl_couleur: self.choix_couleur(fenetre_tendance, l))
                epaisseur.config(state="normal")

                # Pré-remplit les champs avec les infos sauvegardées
                spin_box.delete(0, "end")
                spin_box.insert(0, tendance_existante_info['degre'])
                spin_box.config(state="readonly")
                lbl_style.config(text=intitules_styles[styles_matplotlib.index(
                    tendance_existante_info['style'])])
                lbl_couleur.config(bg=tendance_existante_info['couleur'])
                epaisseur.delete(0, "end")
                epaisseur.insert(0, tendance_existante_info['epaisseur'])

            def cmde(chk=chk_btn, v=var, s=spin_box, lbl_s=lbl_style, lbl_c=lbl_couleur, f=fond, e=epaisseur): return (
                selectionner(v, s, lbl_s, lbl_c, f, e),
                chk.config(bg="white") if v.get(
                ) else chk.config(bg="#d2d3d4"),
            )
            chk_btn.config(command=cmde)
            list_cmde.append(cmde)

        frame_scrollable.update()

        hauteur_contenu = frame_scrollable.winfo_reqheight()

        if hauteur_contenu < hauteur_max:
            cnv_tendance.config(height=hauteur_contenu)
            vscroll.grid_remove()

        cnv_tendance.configure(scrollregion=cnv_tendance.bbox("all"))

        if hauteur_contenu > hauteur_max:
            frame_scrollable.bind(
                "<MouseWheel>", lambda e: mousewheel(e, cnv_tendance))
            for chk_btn, spin_box, style, couleur, epaisseur in zip(list_chk_btn, list_spinbox, list_style, list_couleur, list_epaisseur):
                chk_btn.bind("<MouseWheel>",
                             lambda e: mousewheel(e, cnv_tendance))
                spin_box.bind("<MouseWheel>",
                              lambda e: mousewheel(e, cnv_tendance))
                style.bind("<MouseWheel>",
                           lambda e: mousewheel(e, cnv_tendance))
                couleur.bind("<MouseWheel>",
                             lambda e: mousewheel(e, cnv_tendance))
                epaisseur.bind(
                    "<MouseWheel>", lambda e: mousewheel(e, cnv_tendance))

        # Boutons de commande
        frame_btn = tk.Frame(fenetre_tendance, bg="white")
        frame_btn.columnconfigure(0, weight=1)
        frame_btn.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        btn_valider = tk.Button(frame_btn, text="Valider", command=lambda: valider_tendances(
            list_vars, list_spinbox, list_style, list_couleur, list_epaisseur))
        btn_valider.grid(row=0, column=0, pady=2, sticky="e")
        tk.Button(frame_btn, text="Annuler", command=fenetre_tendance.destroy).grid(
            row=0, column=1, padx=2, pady=2)
        fenetre_tendance.bind("<Return>", lambda event: btn_valider.invoke())
        fenetre_tendance.bind("<Escape>", lambda e: fenetre_tendance.destroy())

    def lancer_calculatrice(self):
        """
        Affiche un écran de chargement puis ouvre la calculatrice de données.
        """
        onglet_actif = self._get_active_onglet()
        if not onglet_actif or not onglet_actif.fig.axes:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        # S'assure de fermer une fenêtre Calculatrice potentiellement déjà ouverte
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel) and child.title() == "Calculatrice":
                child.destroy()

        # On récupère les données directement depuis le cache de l'onglet
        VARIABLES = onglet_actif.donnees_graphique_actuel
        lst_lbl_x = VARIABLES.get('valeurs_x_labels', [])
        donnees_a_tracer = [key for key in VARIABLES.keys() if key not in [
            'x', 'valeurs_x_labels']]
        _, _, unite_x, _, frequence, _, _, _ = onglet_actif._get_parametres()

        # --- Création de la fenêtre de la calculatrice (sans chargement) ---
        fenetre_operation = tk.Toplevel(self, bg="white")
        fenetre_operation.title("Calculatrice")
        # fenetre_operation.transient(self)
        # fenetre_operation.grab_set()
        fenetre_operation.focus_force()
        fenetre_operation.resizable(False, False)
        fenetre_operation.columnconfigure(0, weight=1)

        lst_formule = []

        # --- Fonctions imbriquées pour la calculatrice ---
        def affichage_formule():
            texte_a_afficher = ""
            operateurs = {'+', '-', '*', '/', '(', ')'}
            for elmt in lst_formule:
                if elmt in operateurs:
                    texte_a_afficher += f" {elmt} "
                elif elmt in VARIABLES:
                    texte_a_afficher += f" {elmt} "
                else:
                    texte_a_afficher += str(elmt)
            # Remplace les opérateurs Python par des versions plus lisibles
            texte_a_afficher = texte_a_afficher.replace(
                '*', 'x').replace('/', '÷').replace('.', ',')
            lbl_formule.config(text=" ".join(texte_a_afficher.split()))
            # On force la mise à jour puis on re-calcule la zone de défilement
            cnv_formule.update_idletasks()
            cnv_formule.config(scrollregion=cnv_formule.bbox("all"))
            cnv_formule.xview_moveto(1.0)

        def command_btn_operation(elmt):
            if elmt == ',':
                elmt = '.'
            if elmt == 'x':
                elmt = '*'
            if elmt == '÷':
                elmt = '/'
            lst_formule.append(elmt)
            affichage_formule()

        def supprimer_dernier():
            if lst_formule:
                lst_formule.pop()
                affichage_formule()

        def supprimer_tout():
            if lst_formule:
                lst_formule.clear()
                affichage_formule()

        def executer_calcul():
            if not lst_formule:
                return

            formule_test = ""
            operateurs = {'+', '-', '*', '/', '(', ')'}
            # Variable pour savoir si l'élément précédent était un nom de variable
            element_precedent_etait_variable = False

            for elmt in lst_formule:
                elmt_str = str(elmt)

                # Cas 1 : C'est un nom de variable
                if elmt_str in VARIABLES:
                    # Si l'élément d'avant était aussi une variable, on ajoute un espace pour créer une erreur
                    if element_precedent_etait_variable:
                        formule_test += " "
                    formule_test += "1"  # On remplace les variables par 1 pour le test
                    element_precedent_etait_variable = True
                # Cas 2 : C'est un opérateur
                elif elmt in operateurs:
                    formule_test += f" {elmt} "
                    element_precedent_etait_variable = False
                # Cas 3 : C'est un chiffre ou un point
                else:
                    formule_test += elmt_str
                    element_precedent_etait_variable = False

            try:
                # On essaie d'EVALUER la formule test une fois.
                eval(formule_test, {"__builtins__": None}, {})
            except Exception as e:  # On attrape toutes les erreurs possibles
                messagebox.showerror(
                    "Erreur de Formule", f"La formule est invalide :\n{e}", parent=fenetre_operation)
                return  # On arrête l'exécution

            nom_formule = lbl_formule.cget("text")
            RESULTAT = {"x": VARIABLES.get("x", []), nom_formule: []}

            safe_globals = {"__builtins__": None}
            safe_locals = {"np": np, "nan": np.nan}
            operateurs = {'+', '-', '*', '/', '(', ')'}

            for i in range(len(lst_lbl_x)):
                formule_str_pour_eval = ""
                valeurs_presentes = True

                for elmt in lst_formule:
                    elmt_str = str(elmt)

                    if elmt_str in VARIABLES:
                        variable_data = VARIABLES[elmt_str]
                        if i < len(variable_data):
                            valeur = variable_data[i]
                            if pd.isna(valeur):
                                valeurs_presentes = False
                                break
                            formule_str_pour_eval += str(valeur)
                        else:
                            valeurs_presentes = False
                            break
                    else:
                        if elmt in operateurs:
                            formule_str_pour_eval += f" {elmt} "
                        else:
                            formule_str_pour_eval += elmt_str

                if valeurs_presentes:
                    try:
                        valeur_calculee = eval(
                            formule_str_pour_eval, safe_globals, safe_locals)
                        RESULTAT[nom_formule].append(valeur_calculee)
                    except:
                        RESULTAT[nom_formule].append(np.nan)
                else:
                    RESULTAT[nom_formule].append(np.nan)

            onglet_actif._creation_graphique(
                RESULTAT, {}, lst_lbl_x, frequence, unite_x)
            fenetre_operation.destroy()

        # --- Interface de la calculatrice (reprise de l'original) ---
        lblframe_formule = tk.LabelFrame(fenetre_operation, bg="black")
        lblframe_formule.grid(row=0, column=0, columnspan=2,
                              padx=5, pady=5, sticky="we")
        cnv_formule = tk.Canvas(
            lblframe_formule, height=50, width=350, bg="white", highlightthickness=0)
        cnv_formule.grid(row=0, column=0)
        hscroll_formule = tk.Scrollbar(
            lblframe_formule, orient="horizontal", command=cnv_formule.xview)
        hscroll_formule.grid(row=1, column=0, sticky="we")
        cnv_formule.configure(xscrollcommand=hscroll_formule.set)
        frame_formule = tk.Frame(cnv_formule, bg="white")
        lbl_formule = tk.Label(frame_formule, height=3, bg="white", anchor="w")
        lbl_formule.pack()
        cnv_formule.create_window((0, 0), window=frame_formule, anchor="nw")

        lblframe_variable = tk.LabelFrame(
            fenetre_operation, text="Variables", bg="white")
        lblframe_variable.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        canvas_variable = tk.Canvas(lblframe_variable, highlightthickness=0)
        vscroll_variable = tk.Scrollbar(
            lblframe_variable, orient="vertical", command=canvas_variable.yview)
        frame_variable = tk.Frame(canvas_variable)
        canvas_variable.configure(yscrollcommand=vscroll_variable.set)
        vscroll_variable.pack(side="right", fill="y")
        canvas_variable.pack(side="left", fill="both", expand=True)
        # On garde l'ID de l'objet créé pour pouvoir le modifier plus tard
        window_id = canvas_variable.create_window(
            (0, 0), window=frame_variable, anchor="nw")

        # Fonction pour lier la largeur de la Frame interne à celle du Canvas
        def on_canvas_configure(event):
            canvas_variable.itemconfig(window_id, width=event.width)
        canvas_variable.bind("<Configure>", on_canvas_configure)

        # Fonction pour mettre à jour la zone de défilement
        def on_frame_configure(event):
            canvas_variable.configure(scrollregion=canvas_variable.bbox("all"))
        frame_variable.bind("<Configure>", on_frame_configure)

        # Ajout du contenu dans la Frame interne
        lst_btn_variable = []
        for key in donnees_a_tracer:
            btn_variable = tk.Button(
                frame_variable,
                text=key,
                anchor="w",
                bg="white",
                relief="groove",
                command=lambda k=key: command_btn_operation(k),
            )
            btn_variable.pack(fill="x", padx=1, pady=1)
            lst_btn_variable.append(btn_variable)

        lblframe_operateurs = tk.LabelFrame(
            fenetre_operation, text="Opérateurs", bg="white")
        lblframe_operateurs.grid(row=1, column=1, padx=5, pady=5)

        police = "Arial 12"
        police_bold = "Arial 12 bold"

        buttons = [
            ('C', 0, 0, "black", "light grey", police), ('(', 0, 1, "black", "light grey", police), (')',
                                                                                                     0, 2, "black", "light grey", police), ('÷', 0, 3, "white", "grey", police_bold),
            ('7', 1, 0, "black", "white", police), ('8', 1, 1, "black", "white", police), ('9',
                                                                                           1, 2, "black", "white", police), ('x', 1, 3, "white", "grey", police_bold),
            ('4', 2, 0, "black", "white", police), ('5', 2, 1, "black", "white", police), ('6',
                                                                                           2, 2, "black", "white", police), ('-', 2, 3, "white", "grey", police_bold),
            ('1', 3, 0, "black", "white", police), ('2', 3, 1, "black", "white", police), ('3',
                                                                                           3, 2, "black", "white", police), ('+', 3, 3, "white", "grey", police_bold),
            ('<', 4, 0, "white", "red", police_bold), ('0', 4, 1, "black",
                                                       "white", police), (',', 4, 2, "black", "white", police)
        ]

        for (text, r, c, fg_color, bg_color, txt_font) in buttons:
            if text == '<':
                btn = tk.Button(
                    lblframe_operateurs,
                    text=text,
                    font=txt_font,
                    width=2,
                    fg=fg_color,
                    bg=bg_color,
                    relief="groove",
                    command=supprimer_dernier,
                )
            elif text == 'C':
                btn = tk.Button(
                    lblframe_operateurs,
                    text=text,
                    font=txt_font,
                    width=2,
                    fg=fg_color,
                    bg=bg_color,
                    relief="groove",
                    command=supprimer_tout,
                )
            else:
                btn = tk.Button(
                    lblframe_operateurs,
                    text=text,
                    font=txt_font,
                    width=2,
                    fg=fg_color,
                    bg=bg_color,
                    relief="groove",
                    command=lambda t=text: command_btn_operation(t),
                )
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        btn_calcul = tk.Button(
            lblframe_operateurs,
            text="=",
            font=police_bold,
            fg="white",
            bg=BG_COLOR_PRIMARY,
            relief="groove",
            command=executer_calcul,
        )
        btn_calcul.grid(row=4, column=3, columnspan=2,
                        sticky="nsew", padx=1, pady=1)

        fenetre_operation.update_idletasks()
        hauteur_reference = lblframe_operateurs.winfo_height()
        lblframe_variable.config(height=hauteur_reference)
        lblframe_variable.pack_propagate(False)

        lblframe_variable.update_idletasks()
        if vscroll_variable.get() != (0.0, 1.0):
            frame_variable.bind(
                "<MouseWheel>", lambda e: mousewheel(e, canvas_variable))
            for btn in lst_btn_variable:
                btn.bind("<MouseWheel>", lambda e: mousewheel(
                    e, canvas_variable))

        fenetre_operation.bind("<Return>", lambda e: executer_calcul())
        fenetre_operation.bind(
            "<Escape>", lambda e: fenetre_operation.destroy())

    def gerer_zones_analyse(self):
        """
        Ouvre une fenêtre de gestion complète pour les zones d'analyse (Ajouter/Modifier/Supprimer).
        """
        onglet_actif = self._get_active_onglet()
        if not onglet_actif or not onglet_actif.fig.axes:
            messagebox.showerror(
                "Erreur", "Veuillez d'abord tracer un graphique.", parent=self)
            return

        # S'assure de fermer une fenêtre Calculatrice potentiellement déjà ouverte
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel) and child.title() == "Gestion des Zones d'Analyse":
                child.destroy()

        # --- FENÊTRE PRINCIPALE DE GESTION ---
        fenetre_gestion = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        fenetre_gestion.title("Gestion des Zones d'Analyse")
        # fenetre_gestion.transient(self)
        # fenetre_gestion.grab_set()
        fenetre_gestion.focus_force()
        fenetre_gestion.resizable(False, False)

        # --- Fonctions internes de la fenêtre de gestion ---

        def rafraichir_liste():
            for i in tree.get_children():
                tree.delete(i)
            unite_x = onglet_actif.varGr_x.get()
            for i, zone in enumerate(onglet_actif.zones_analyse):
                nom_zone = zone.get('nom')
                debut = zone['debut']
                fin = zone['fin']
                if unite_x == "Temps":
                    debut_str = mdates.num2date(
                        debut).strftime('%d/%m/%Y %H:%M')
                    fin_str = mdates.num2date(fin).strftime('%d/%m/%Y %H:%M')
                else:
                    debut_str = f"{debut:.2f}"
                    fin_str = f"{fin:.2f}"
                # On insère les valeurs dans les bonnes colonnes
                tree.insert('', tk.END, iid=i, values=(
                    nom_zone, debut_str, fin_str))

        def supprimer_zone():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Aucune sélection", "Veuillez sélectionner une zone à supprimer.", parent=fenetre_gestion)
                return

            index = int(selection[0])
            nom_zone = onglet_actif.zones_analyse[index].get('nom')
            if messagebox.askyesno("Confirmer", f"Voulez-vous vraiment supprimer la zone '{nom_zone}' ?", parent=fenetre_gestion):
                onglet_actif.zones_analyse.pop(index)
                onglet_actif.redessiner_zones_analyse()
                rafraichir_liste()

        def modifier_zone():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Aucune sélection", "Veuillez sélectionner une zone à modifier.", parent=fenetre_gestion)
                return
            ouvrir_editeur_zone(int(selection[0]))

        def ouvrir_editeur_zone(zone_index=None):
            # S'assure de fermer une fenêtre Calculatrice potentiellement déjà ouverte
            for child in fenetre_gestion.winfo_children():
                if isinstance(child, tk.Toplevel) and child.title() == "Éditeur de Zone":
                    child.destroy()
            # Ouvre la fenêtre d'édition pour une zone (None pour ajout, un index pour modification)
            fenetre_editeur = tk.Toplevel(
                fenetre_gestion, bg=BG_COLOR_PRIMARY, bd=1)
            fenetre_editeur.title("Éditeur de Zone")
            fenetre_editeur.transient(fenetre_gestion)
            # fenetre_editeur.grab_set()
            fenetre_editeur.focus_force()
            fenetre_editeur.resizable(False, False)

            unite_x = onglet_actif.varGr_x.get()
            widgets_moyenne = {}
            position_nom_var = tk.StringVar(value="Aucun")

            def sauvegarder_zone():
                try:
                    nom_zone = entry_nom.get()
                    if not nom_zone:  # On s'assure que le nom n'est pas vide
                        messagebox.showerror(
                            "Erreur", "Le nom de la zone ne peut pas être vide.", parent=fenetre_editeur)
                        return
                    if unite_x == "Temps":
                        date_debut = lbl_debut_dt.cget("text")
                        h_debut = lbl_debut_h.cget("text")
                        min_debut = lbl_debut_min.cget("text")
                        debut_var = f"{date_debut} {h_debut}:{min_debut}"
                        date_fin = lbl_fin_dt.cget("text")
                        h_fin = lbl_fin_h.cget("text")
                        min_fin = lbl_fin_min.cget("text")
                        fin_var = f"{date_fin} {h_fin}:{min_fin}"
                        debut = mdates.date2num(
                            datetime.strptime(debut_var, '%d/%m/%Y %H:%M'))
                        fin = mdates.date2num(
                            datetime.strptime(fin_var, '%d/%m/%Y %H:%M'))
                    else:
                        debut_var = entry_debut.get().replace(",", ".")
                        fin_var = entry_fin.get().replace(",", ".")
                        debut = float(debut_var)
                        fin = float(fin_var)

                    if debut >= fin:
                        messagebox.showerror(
                            "Erreur", "La valeur de début doit être inférieure à la valeur de fin.", parent=fenetre_editeur)
                        return

                    # Calcul des moyennes
                    moyennes_calculees = {}
                    cles_y = [k for k in onglet_actif.courbes_graphe.keys() if k not in [
                        'x', 'valeurs_x']]
                    for i, nom_courbe in enumerate(cles_y):
                        # On récupère les widgets pour cette courbe
                        widgets_ligne = widgets_moyenne[nom_courbe]
                        if widgets_ligne['var'].get() == 1:
                            x_data = np.array(
                                onglet_actif.courbes_graphe[nom_courbe][0])
                            y_data = np.array(
                                onglet_actif.courbes_graphe[nom_courbe][1])

                            indices_dans_zone = (x_data >= debut) & (
                                x_data <= fin) & ~np.isnan(y_data)
                            valeur_moyenne = np.mean(y_data[indices_dans_zone])

                            moyennes_calculees[nom_courbe] = {
                                'valeur': valeur_moyenne,
                                'couleur': widgets_ligne['couleur'].cget("bg"),
                                'style': widgets_ligne['style'].cget("text"),
                                'epaisseur': float(widgets_ligne['epaisseur'].get())
                            }
                    # On sauvegarde la zone avec toutes les infos
                    nouvelle_zone = {
                        'nom': nom_zone,
                        'debut': debut,
                        'fin': fin,
                        'couleur': lbl_couleur_apercu.cget("bg"),
                        'alpha': alpha_scale.get(),
                        'position_nom': position_nom_var.get(),
                        'moyennes': moyennes_calculees,
                    }
                    if zone_index is None:  # Ajout
                        onglet_actif.zones_analyse.append(nouvelle_zone)
                    else:  # Modification
                        onglet_actif.zones_analyse[zone_index] = nouvelle_zone

                    onglet_actif.redessiner_zones_analyse()
                    rafraichir_liste()
                    fenetre_editeur.destroy()

                except ValueError:
                    messagebox.showerror(
                        "Erreur de Saisie", f"Veuillez entrer des valeurs valides.", parent=fenetre_editeur)

            # --- Interface de la fenêtre d'édition ---
            frame_param = tk.Frame(fenetre_editeur, bg=BG_COLOR_WIDGET)
            frame_param.columnconfigure(1, weight=1)
            frame_param.grid(row=0, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(frame_param, text="Nom de la zone :", bg=BG_COLOR_WIDGET).grid(
                row=0, column=0, padx=5, pady=2, sticky='w')
            frame_entry = tk.Frame(frame_param, relief="groove", bd=2)
            frame_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            entry_nom = tk.Entry(frame_entry, width=25, bd=0)
            entry_nom.grid(row=0, column=0)
            tk.Label(frame_param, text="Début :", bg=BG_COLOR_WIDGET).grid(
                row=1, column=0, padx=5, pady=2, sticky='w')
            tk.Label(frame_param, text="Fin :", bg=BG_COLOR_WIDGET).grid(
                row=2, column=0, padx=5, pady=2, sticky='w')
            if onglet_actif.varGr_x.get() == "Temps":
                # Ligne début
                frame_date_debut = tk.Frame(frame_param, bg=BG_COLOR_WIDGET)
                frame_date_debut.grid(row=1, column=1, sticky="w")
                frame_date_debut.columnconfigure(0, weight=1)
                lbl_debut_dt = tk.Label(
                    frame_date_debut, width=10, bg="white", relief="groove")
                lbl_debut_dt.grid(row=0, column=0, padx=5, pady=2, sticky="w")
                lbl_debut_dt.bind("<Button 1>", lambda e: self.afficher_calendrier(
                    e, lbl_debut_dt, onglet_actif.dates))
                lbl_debut_h = tk.Label(
                    frame_date_debut, width=2, bg="white", relief="groove")
                lbl_debut_h.bind(
                    "<Button-1>", lambda e: self.fenetre_choix(lbl_debut_h, np.arange(0, 24)))
                lbl_debut_min = tk.Label(
                    frame_date_debut, width=2, bg="white", relief="groove")
                lbl_debut_min.bind(
                    "<Button-1>", lambda e: self.fenetre_choix(lbl_debut_min, np.arange(0, 60)))
                lbl_debut_h.grid(row=0, column=1, sticky="w")
                tk.Label(frame_date_debut, text=":",
                         bg=BG_COLOR_WIDGET).grid(row=0, column=2, sticky="w")
                lbl_debut_min.grid(row=0, column=3, sticky="w")
                # Ligne fin
                frame_date_fin = tk.Frame(frame_param, bg=BG_COLOR_WIDGET)
                frame_date_fin.grid(row=2, column=1, sticky="w")
                frame_date_fin.columnconfigure(0, weight=1)
                lbl_fin_dt = tk.Label(
                    frame_date_fin, width=10, bg="white", relief="groove")
                lbl_fin_dt.grid(row=0, column=0, padx=5, pady=2, sticky="w")
                lbl_fin_dt.bind("<Button 1>", lambda e: self.afficher_calendrier(
                    e, lbl_fin_dt, onglet_actif.dates))
                lbl_fin_h = tk.Label(
                    frame_date_fin, width=2, bg="white", relief="groove")
                lbl_fin_h.bind(
                    "<Button-1>", lambda e: self.fenetre_choix(lbl_fin_h, np.arange(0, 24)))
                lbl_fin_min = tk.Label(
                    frame_date_fin, width=2, bg="white", relief="groove")
                lbl_fin_min.bind(
                    "<Button-1>", lambda e: self.fenetre_choix(lbl_fin_min, np.arange(0, 60)))
                lbl_fin_h.grid(row=0, column=1)
                tk.Label(frame_date_fin, text=":",
                         bg=BG_COLOR_WIDGET).grid(row=0, column=2)
                lbl_fin_min.grid(row=0, column=3)

            else:
                frame_entry_debut = tk.Frame(
                    frame_param, relief="groove", bd=2)
                frame_entry_debut.grid(
                    row=1, column=1, padx=5, pady=2, sticky="w")
                entry_debut = tk.Entry(frame_entry_debut, bd=0)
                entry_debut.grid(row=0, column=0)
                frame_entry_fin = tk.Frame(
                    frame_param, relief="groove", bd=2)
                frame_entry_fin.grid(
                    row=2, column=1, padx=5, pady=2, sticky="w")
                entry_fin = tk.Entry(frame_entry_fin, bd=0)
                entry_fin.grid(row=0, column=0)

            tk.Label(frame_param, text="Couleur zone :", bg=BG_COLOR_WIDGET).grid(
                row=3, column=0, padx=5, pady=2, sticky='w')
            lbl_couleur_apercu = tk.Label(
                frame_param, width=2, bg="#a6d8a6", relief='groove')
            lbl_couleur_apercu.grid(row=3, column=1, sticky='w', padx=5)
            lbl_couleur_apercu.bind(
                "<Button-1>", lambda e, w=fenetre_editeur, l=lbl_couleur_apercu: self.choix_couleur(w, l))
            tk.Label(frame_param, text="Transparence :", bg=BG_COLOR_WIDGET).grid(
                row=4, column=0, padx=5, pady=2, sticky='w')
            frame_alpha = tk.Frame(frame_param, bg=BG_COLOR_WIDGET)
            frame_alpha.grid(row=4, column=1, padx=5, pady=2, sticky="w")
            alpha_var = tk.StringVar()
            alpha_scale = tk.Scale(
                frame_alpha,
                variable=alpha_var,
                showvalue=0,
                from_=0,
                to=100,
                resolution=1,
                length=250,
                orient='horizontal',
                bg=BG_COLOR_WIDGET,
            )
            alpha_scale.set(65)
            alpha_scale.grid(row=0, column=0)
            tk.Label(frame_alpha, textvariable=alpha_var, width=4,
                     bg=BG_COLOR_WIDGET, bd=0, anchor="e").grid(row=0, column=1)
            tk.Label(frame_alpha, text="%", bg=BG_COLOR_WIDGET, bd=0).grid(
                row=0, column=2)
            tk.Label(frame_param, text="Affichage du nom", bg=BG_COLOR_WIDGET).grid(
                row=5, column=0, padx=5, pady=2, sticky="w")
            aff_nom_frame = tk.Frame(frame_param, bg=BG_COLOR_WIDGET)
            aff_nom_frame.grid(row=5, column=1, padx=5, pady=2, sticky="w")
            tk.Radiobutton(aff_nom_frame, text="Aucun", variable=position_nom_var, value="Aucun", bg=BG_COLOR_WIDGET).grid(
                row=0, column=0)
            tk.Radiobutton(aff_nom_frame, text="Haut", variable=position_nom_var, value="Haut", bg=BG_COLOR_WIDGET).grid(
                row=0, column=1, padx=5)
            tk.Radiobutton(aff_nom_frame, text="Bas", variable=position_nom_var, value="Bas", bg=BG_COLOR_WIDGET).grid(
                row=0, column=2)

            if zone_index is None:  # Pré remplissage en mode "Ajout"
                if unite_x == "Temps":
                    # On lit les valeurs des widgets du panneau principal de l'onglet
                    lbl_debut_dt.configure(
                        text=onglet_actif.lbl_debut.cget("text"))
                    lbl_debut_h.configure(
                        text=onglet_actif.lbl_h_debut.cget("text"))
                    lbl_debut_min.configure(
                        text=onglet_actif.lbl_m_debut.cget("text"))
                    lbl_fin_dt.configure(
                        text=onglet_actif.lbl_fin.cget("text"))
                    lbl_fin_h.configure(
                        text=onglet_actif.lbl_h_fin.cget("text"))
                    lbl_fin_min.configure(
                        text=onglet_actif.lbl_m_fin.cget("text"))
            elif zone_index is not None:  # Pré remplissage en mode "Modification"
                zone = onglet_actif.zones_analyse[zone_index]
                position_nom_var.set(zone.get('position_nom', 'Aucun'))
                entry_nom.insert(0, zone['nom'])
                if unite_x == "Temps":
                    dt_debut = mdates.num2date(zone['debut'])
                    lbl_debut_dt.configure(text=dt_debut.strftime('%d/%m/%Y'))
                    lbl_debut_h.configure(text=dt_debut.strftime('%H'))
                    lbl_debut_min.configure(text=dt_debut.strftime('%M'))
                    dt_fin = mdates.num2date(zone['fin'])
                    lbl_fin_dt.configure(text=dt_fin.strftime('%d/%m/%Y'))
                    lbl_fin_h.configure(text=dt_fin.strftime('%H'))
                    lbl_fin_min.configure(text=dt_fin.strftime('%M'))
                else:
                    entry_debut.insert(0, zone['debut'])
                    entry_fin.insert(0, zone['fin'])
                lbl_couleur_apercu.config(bg=zone['couleur'])
                alpha_scale.set(zone['alpha'])

            # Frame pour la sélection des moyennes
            frame_lblFrame = tk.Frame(fenetre_editeur, bg=BG_COLOR_WIDGET)
            frame_lblFrame.grid(row=6, column=0, padx=1,
                                pady=1, sticky="ew")
            moyenne_frame = tk.LabelFrame(
                frame_lblFrame, text="Tracer la moyenne pour :", bg=BG_COLOR_WIDGET)
            moyenne_frame.grid(row=0, column=0, padx=2, pady=2, sticky='ew')
            # En-têtes pour les options des moyennes
            frame_entetes = tk.Frame(moyenne_frame)
            frame_entetes.columnconfigure(0, weight=1)
            tk.Label(frame_entetes, text="Style", width=10, bg="#dfe7f5").grid(
                row=0, column=1, padx=1, pady=1)
            tk.Label(frame_entetes, text="Couleur", width=10,
                     bg="#dfe7f5").grid(row=0, column=2, padx=1, pady=1)
            tk.Label(frame_entetes, text="Épaisseur", width=10,
                     bg="#dfe7f5").grid(row=0, column=3, padx=1, pady=1)
            frame_entetes.grid(row=0, column=0, sticky="ew")

            # Canvas scrollable pour la liste des données disponibles
            hauteur_max = 150
            cnv_moyenne = tk.Canvas(
                moyenne_frame, height=hauteur_max, width=500, highlightthickness=0)
            cnv_moyenne.grid(row=1, column=0, sticky="nsew")

            frame_scrollable = tk.Frame(cnv_moyenne)
            frame_scrollable.columnconfigure(0, weight=1)

            vscroll = tk.Scrollbar(
                moyenne_frame, orient="vertical", command=cnv_moyenne.yview)
            vscroll.grid(row=1, column=1, sticky="ns")

            moyenne_frame.update()
            cnv_moyenne.configure(yscrollcommand=vscroll.set)
            cnv_moyenne.create_window(
                cnv_moyenne.winfo_rootx(),
                cnv_moyenne.winfo_rooty(),
                anchor="nw",
                window=frame_scrollable,
                width=cnv_moyenne.winfo_width(),
            )
            cnv_moyenne.configure(scrollregion=cnv_moyenne.bbox("all"))
            cnv_moyenne.yview("moveto", 0.0)

            cles_y = [k for k in onglet_actif.courbes_graphe.keys() if k not in [
                'x', 'valeurs_x']]
            lst_widgets = []
            for i, nom_courbe in enumerate(cles_y):
                var = tk.IntVar()
                toutes_les_courbes = onglet_actif.fig.axes[0].lines
                if len(onglet_actif.fig.axes) > 1:
                    toutes_les_courbes = toutes_les_courbes + \
                        onglet_actif.fig.axes[1].lines
                couleur_defaut = next(
                    (l.get_color() for l in toutes_les_courbes if l.get_label() == nom_courbe), "black")
                # On crée les widgets pour chaque droite de moyenne
                # Case à cocher
                chk = tk.Checkbutton(
                    frame_scrollable, text=nom_courbe, variable=var, bg=BG_COLOR_WIDGET, anchor="w")
                chk.grid(row=i, column=0, padx=1, pady=1, sticky='ew')
                lst_widgets.append(chk)
                # Style de ligne
                lbl_style = tk.Label(
                    frame_scrollable, text="______", width=10, bg=BG_COLOR_WIDGET)
                lbl_style.grid(row=i, column=1, padx=1,
                               pady=1, sticky='nsew')
                lbl_style.bind("<Button-1>", lambda e,
                               l=lbl_style: self.choix_style(l))
                lst_widgets.append(lbl_style)
                # Couleur
                fond = tk.Frame(frame_scrollable, bg=BG_COLOR_WIDGET)
                fond.grid(row=i, column=2, padx=1,
                          pady=1, ipadx=28, sticky="nsew")
                fond.columnconfigure(0, weight=1)
                fond.rowconfigure(0, weight=1)
                lst_widgets.append(fond)
                lbl_couleur = tk.Label(
                    fond, bg=couleur_defaut, relief="groove", width=2)
                lbl_couleur.grid(row=0, column=0)
                lbl_couleur.bind("<Button 1>", lambda e, w=fenetre_editeur,
                                 l=lbl_couleur: self.choix_couleur(w, l))
                # Épaisseur
                entry_epaisseur = tk.Entry(
                    frame_scrollable, width=12, justify='center', bd=0)
                entry_epaisseur.insert(0, "2")
                entry_epaisseur.grid(
                    row=i, column=3, padx=1, pady=1, sticky='nsew')
                lst_widgets.append(entry_epaisseur)

                # On stocke tous les widgets de la ligne
                widgets_moyenne[nom_courbe] = {
                    'var': var, 'couleur': lbl_couleur, 'style': lbl_style, 'epaisseur': entry_epaisseur}

                # On pré-remplit si on est en mode modification
                if zone_index is not None and nom_courbe in zone.get('moyennes', {}):
                    chk.select()
                    info_moyenne_existante = zone['moyennes'][nom_courbe]
                    lbl_couleur.config(
                        bg=info_moyenne_existante.get('couleur'))
                    lbl_style.config(
                        text=info_moyenne_existante.get('style'))
                    entry_epaisseur.delete(0, 'end')
                    entry_epaisseur.insert(
                        0, info_moyenne_existante.get('epaisseur'))

            frame_scrollable.update_idletasks()
            hauteur_contenu = frame_scrollable.winfo_reqheight()

            if hauteur_contenu < hauteur_max:
                cnv_moyenne.config(height=hauteur_contenu)
                vscroll.grid_remove()
            cnv_moyenne.config(scrollregion=cnv_moyenne.bbox("all"))

            if hauteur_contenu > hauteur_max:
                frame_scrollable.bind(
                    "<MouseWheel>", lambda e: mousewheel(e, cnv_moyenne))
                for widget in lst_widgets:
                    widget.bind(
                        "<MouseWheel>", lambda e: mousewheel(e, cnv_moyenne))

            frame_btn = tk.Frame(fenetre_editeur, bg=BG_COLOR_WIDGET)
            frame_btn.columnconfigure(0, weight=1)
            frame_btn.grid(row=7, column=0, padx=1, pady=1, sticky="ew")
            tk.Button(frame_btn, text="Sauvegarder", command=sauvegarder_zone).grid(
                row=0, column=0, pady=2, sticky="e")
            tk.Button(frame_btn, text="Annuler", command=fenetre_editeur.destroy).grid(
                row=0, column=1, padx=2, pady=2)
            fenetre_editeur.bind("<Return>", lambda e: sauvegarder_zone())
            fenetre_editeur.bind(
                "<Escape>", lambda e: fenetre_editeur.destroy())

        # --- Interface de la fenêtre de gestion principale ---
        # On crée un conteneur pour le Treeview et sa scrollbar
        tree_frame = tk.Frame(fenetre_gestion)
        tree_frame.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        # On définit les colonnes
        colonnes = ('nom', 'debut', 'fin')
        tree = ttk.Treeview(tree_frame, columns=colonnes,
                            show='headings', height=10)
        # On définit les en-têtes
        tree.heading('nom', text='Nom de la Zone')
        tree.heading('debut', text='Début')
        tree.heading('fin', text='Fin')
        # On ajuste la largeur des colonnes
        tree.column('nom', width=150)
        tree.column('debut', width=120, anchor='center')
        tree.column('fin', width=120, anchor='center')
        # Ajout de la scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(fenetre_gestion, bg=BG_COLOR_WIDGET)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.grid(row=1, column=0, padx=1, pady=1, sticky="ew")

        tk.Button(btn_frame, text="Ajouter", width=10, command=ouvrir_editeur_zone).grid(
            row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="Modifier", width=10, command=modifier_zone).grid(
            row=0, column=1, pady=2)
        tk.Button(btn_frame, text="Supprimer", width=10, command=supprimer_zone).grid(
            row=0, column=2, padx=2, pady=2, sticky="w")
        tk.Button(btn_frame, text="Fermer", width=10,
                  command=fenetre_gestion.destroy).grid(row=0, column=3, padx=2, pady=2)
        fenetre_gestion.bind("<Escape>", lambda e: fenetre_gestion.destroy())

        rafraichir_liste()

    def valider_choix_four(self):
        nom_four = self.combo_four.get()
        if not nom_four or nom_four == self.nom_four_selectionne:
            return
        self.nom_four_selectionne = nom_four
        self.lbl_nom_four.config(text=nom_four)
        self.onglet_four.reinitialiser_affichage()
        self.onglet_feeder.reinitialiser_affichage()
        dates_four, donnees_four = self._charger_meta_donnees("Four")
        dates_feeder, donnees_feeder = self._charger_meta_donnees("Feeder")
        self.onglet_four.mettre_a_jour_donnees(dates_four, donnees_four)
        self.onglet_feeder.mettre_a_jour_donnees(dates_feeder, donnees_feeder)
        self.onglet_four.activer_controles()
        self.onglet_feeder.activer_controles()

    def _charger_meta_donnees(self, type_onglet):
        chemin_specifique = os.path.join(
            CHEMIN_SERVEUR, self.nom_four_selectionne, "Fusion", type_onglet)
        if not os.path.exists(chemin_specifique):
            return [], []
        dossiers = [d.name for d in os.scandir(
            chemin_specifique) if d.is_dir() and d.name != "dernierFichier"]
        dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in dossiers])
        donnees = []
        if dates:
            dernier_fichier_path = chercher_fichier(
                dates[-1], chemin_specifique)
            if dernier_fichier_path:
                with open(dernier_fichier_path, "r", encoding='utf-8') as f:
                    donnees = pd.read_csv(f, sep=";").columns[2:].tolist()
        return dates, donnees

    def afficher_calendrier(self, event, lbl, lst_dates):
        if not lst_dates:
            return

        def vaider_date():
            lbl.config(text=cal.get_date())
            top.destroy()

        def selectionner_aujourdhui():
            """Sélectionne la date du jour ou la date disponible la plus récente."""
            aujourdhui = datetime.now().date()

            # On convertit la liste de datetime en une liste de date pour la comparaison
            dates_valides_date = {d.date() for d in lst_dates}
            date_max_date = lst_dates[-1].date()

            # On vérifie si la date d'aujourd'hui est dans la liste des dates valides
            if aujourdhui in dates_valides_date:
                cal.selection_set(aujourdhui)
            else:
                # Sinon, on sélectionne la dernière date disponible et on prévient l'utilisateur
                cal.selection_set(date_max_date)
                messagebox.showinfo(
                    "Date non disponible",
                    "Les données pour aujourd'hui ne sont pas encore disponibles.\nLa dernière date disponible a été sélectionnée.",
                    parent=top,
                )

        root_x, root_y, width = lbl.winfo_rootx(), lbl.winfo_rooty(), lbl.winfo_width()
        top = tk.Toplevel(self, bg=BG_COLOR_PRIMARY, bd=1)
        top.overrideredirect(True)
        top.geometry(f"+{root_x + width}+{root_y}")
        top.grab_set()
        top.focus_force()
        date_min, date_max = lst_dates[0], lst_dates[-1]
        # On récupère la date déjà sélectionnée, si elle existe
        date_selectionnee = None
        try:
            date_selectionnee = datetime.strptime(lbl.cget("text"), "%d/%m/%Y")
        except ValueError:
            # Le label est vide ou ne contient pas une date valide, on ignore
            pass
        # On choisit la date à afficher à l'ouverture : la date déjà sélectionnée, ou la date max par défaut
        date_initiale = date_selectionnee or date_max
        cal = MyCalendar(
            top,
            selectmode="day",
            date_pattern="dd/mm/yyyy",
            mindate=date_min,
            maxdate=date_max,
            background="#325faa",
            headersbackground="#8c9193",
            weekendbackground="white",
            weekendforeground="black",
            locale="fr_FR",
            year=date_initiale.year, month=date_initiale.month, day=date_initiale.day,
        )
        available_dates = set(lst_dates)
        current_date = date_min
        while current_date <= date_max:
            if current_date not in available_dates:
                cal.disable_date(current_date)
            current_date += timedelta(days=1)
        cal.grid(row=0, column=0)

        frame_btn = tk.Frame(top, bg="white")
        frame_btn.columnconfigure(0, weight=1)
        frame_btn.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        tk.Button(frame_btn, text="Aujourd'hui", command=selectionner_aujourdhui).grid(
            row=1, column=0, pady=2)
        tk.Button(frame_btn, text="Valider", command=vaider_date).grid(
            row=1, column=1, pady=2)
        tk.Button(frame_btn, text="Annuler", command=top.destroy).grid(
            row=1, column=2, padx=2, pady=2)
        top.bind("<Escape>", lambda e: top.destroy())


if __name__ == "__main__":
    if not os.access(CHEMIN_SERVEUR, os.F_OK):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erreur", f"Accès au serveur '{CHEMIN_SERVEUR}' refusé")
        sys.exit()

    app = Application()
    app.mainloop()
