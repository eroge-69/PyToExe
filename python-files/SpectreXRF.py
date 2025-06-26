# XRF Simulator – interface complète avec Tool ID, MFM310A, Save, Reset
import numpy as np
import pandas as pd
import xraylib as xrl
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
from scipy.ndimage import gaussian_filter1d
import os
from Table_energy import TRANSITIONS_TABLE3, Table_Energy
from projects.XRF.Functions import xrlib


# --- Classes ---
class SourceRX:
    def __init__(self, type_source='monochromatic', energie=None,
                 fichier_spectre=None):
        self.type_source = type_source
        self.energie = float(energie) if energie else None
        self.fichier_spectre = fichier_spectre


class Couche:
    def __init__(self, formule, epaisseur=None, densite=None):
        self.formule = formule
        self.epaisseur = float(epaisseur) if epaisseur else None
        self.densite = float(densite) if densite else None


class Echantillon:
    def __init__(self, type_echantillon='bulk', couches=None, substrat=None):
        self.type_echantillon = type_echantillon
        self.couches = couches or []
        self.substrat = substrat


class Detecteur:
    def __init__(self, distance_air=4.2, resolution_fixe=120,
                 resolution_variable=False, fichier_resolution=None,
                 modele=None):
        self.distance_air = float(distance_air)
        self.resolution_fixe = float(resolution_fixe)
        self.resolution_variable = resolution_variable
        self.fichier_resolution = fichier_resolution
        self.modele = modele


# --- Fonction de simulation ---
def simuler_spectre_xrf_massif(source, echantillon, detecteur, E_min=0.5,
                               E_max=35, pas=0.002):
    excitation_energy = source.energie
    couche = echantillon.couches[0]
    formule = couche.formule
    densite = couche.densite

    composition = xrl.CompoundParser(formule)
    energy_range = np.arange(E_min, E_max + pas, pas)
    spectrum = np.zeros_like(energy_range)
    contributions = {}

    for i in range(composition['nElements']):
        Z = composition['Elements'][i]
        w = composition['massFractions'][i]
        symbol = xrl.AtomicNumberToSymbol(Z)
        intensite = np.zeros_like(energy_range)
        for trans_name in xrlib.line_list:
            line = xrlib.Index(trans_name).line
            try:
                E = xrl.LineEnergy(Z, line)
                if E < E_min or E > E_max:
                    continue
                cs = xrl.CS_FluorLine_Kissel_Cascade(Z, line, excitation_energy)
                idx = np.searchsorted(energy_range, E)
                if idx < len(energy_range):
                    intensite[idx] += cs * w * densite
                print(
                    f"{symbol}_{trans_name}    cs={cs}    w={w}     densite="
                    f"{densite}     prod={cs * w * densite}     A[{idx}]="
                    f"{intensite[idx]}")
            except:
                continue

        spectrum += intensite
        contributions[symbol] = intensite

    if detecteur.modele == "MFM310A":
        spectrum_conv = np.zeros_like(spectrum)
        for i, E in enumerate(energy_range):
            sigma_keV = np.sqrt(0.00052825 * E + 0.00101)
            w = int(5 * sigma_keV / pas)
            idx_min = max(0, i - w)
            idx_max = min(len(spectrum), i + w + 1)
            x = energy_range[idx_min:idx_max] - E
            gauss = np.exp(-x ** 2 / (2 * sigma_keV ** 2))
            gauss /= gauss.sum()
            spectrum_conv[i] = np.sum(spectrum[idx_min:idx_max] * gauss)
        spectrum = spectrum_conv

        for symbol in contributions:
            base = contributions[symbol]
            conv = np.zeros_like(base)
            for i, E in enumerate(energy_range):
                sigma_keV = np.sqrt(0.00052825 * E + 0.00101)
                w = int(5 * sigma_keV / pas)
                idx_min = max(0, i - w)
                idx_max = min(len(base), i + w + 1)
                x = energy_range[idx_min:idx_max] - E
                gauss = np.exp(-x ** 2 / (2 * sigma_keV ** 2))
                gauss /= gauss.sum()
                conv[i] = np.sum(base[idx_min:idx_max] * gauss)
            contributions[symbol] = conv

    else:
        resolution = detecteur.resolution_fixe / 1000.0
        sigma_keV = resolution / 2.355
        sigma_points = sigma_keV / pas
        spectrum = gaussian_filter1d(spectrum, sigma_points)
        for symbol in contributions:
            contributions[symbol] = gaussian_filter1d(contributions[symbol],
                                                      sigma_points)

    return pd.DataFrame(
        {'Energie_keV': energy_range, 'Intensite': spectrum}), contributions


# --- Interface ---
def lancer_interface():
    root = tk.Tk()
    root.title("XRF Simulator")
    root.geometry("1200x720")

    spectra_superposes = []
    global contributions
    contributions = {}

    frame_left = tk.Frame(root)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

    # Bloc Sample
    frame_sample = tk.LabelFrame(frame_left, text="Sample", padx=10, pady=10)
    frame_sample.pack(fill="x", pady=5)
    tk.Label(frame_sample, text="Chemical formula:").grid(row=0, column=0,
                                                          sticky="w")
    entry_formula = tk.Entry(frame_sample)
    entry_formula.insert(0, "MoS2")
    entry_formula.grid(row=0, column=1)

    tk.Label(frame_sample, text="Density (g/cm³):").grid(row=1, column=0,
                                                         sticky="w")
    entry_density = tk.Entry(frame_sample)
    entry_density.insert(0, "5.06")
    entry_density.grid(row=1, column=1)

    label_compo = tk.Label(frame_sample, text="", font=("Arial", 9))
    label_compo.grid(row=2, column=0, columnspan=2, pady=4)

    def update_composition(event=None):
        try:
            f = entry_formula.get()
            comp = xrl.CompoundParser(f)
            txt = ""
            for i in range(comp['nElements']):
                Z = comp['Elements'][i]
                atfrac = comp['nAtoms'][i] / sum(comp['nAtoms'])
                symbol = xrl.AtomicNumberToSymbol(Z)
                txt += f"{symbol} (at%) {100 * atfrac:.2f}    "
            label_compo.config(text=txt.strip())
        except:
            label_compo.config(text="Invalid formula")

    entry_formula.bind("<FocusOut>", update_composition)
    entry_formula.bind("<Return>", update_composition)
    update_composition()

    # --- Bouton Table_E ---
    def call_table_energy():
        try:
            formule = entry_formula.get()
            energie = float(entry_energy.get())
            if formule and energie > 0:
                Table_Energy(formule, energie)
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate XRF table:\n{e}")

    btn_table_e = tk.Button(frame_sample, text="Table_E",
                            command=call_table_energy)
    btn_table_e.grid(row=0, column=2, padx=5, pady=2)

    # Bloc Source
    frame_source = tk.LabelFrame(frame_left, text="X-ray Source", padx=10,
                                 pady=10)
    frame_source.pack(fill="x", pady=5)
    tk.Label(frame_source, text="Energy (keV):").grid(row=0, column=0,
                                                      sticky="w")
    entry_energy = tk.Entry(frame_source)
    entry_energy.insert(0, "20.0")
    entry_energy.grid(row=0, column=1)

    # Bloc Detector
    frame_detector = tk.LabelFrame(frame_left, text="Detector", padx=10,
                                   pady=10)
    frame_detector.pack(fill="x", pady=5)
    tk.Label(frame_detector, text="Resolution (eV):").grid(row=0, column=0,
                                                           sticky="w")
    entry_resolution = tk.Entry(frame_detector)
    entry_resolution.insert(0, "120")
    entry_resolution.grid(row=0, column=1)

    var_tool_det = tk.BooleanVar()
    cb_det = tk.Checkbutton(frame_detector, text="Use Tool ID",
                            variable=var_tool_det)
    cb_det.grid(row=1, column=0, columnspan=2, sticky="w")

    model_combo = ttk.Combobox(frame_detector, values=["MFM310A"])
    model_combo.current(0)
    model_combo.grid(row=2, column=0, columnspan=2)
    model_combo.config(state="disabled")

    def toggle_model(*args):
        state = "readonly" if var_tool_det.get() else "disabled"
        model_combo.config(state=state)

    var_tool_det.trace_add("write", toggle_model)

    var_parametric = tk.BooleanVar()
    cb_param = tk.Checkbutton(frame_left, text="Parametric study",
                              variable=var_parametric)
    cb_param.pack(pady=5)

    # Bloc Graphe
    var_norm = tk.BooleanVar()
    cb_norm = tk.Checkbutton(frame_left, text="Norm", variable=var_norm)
    cb_norm.pack(pady=2)

    frame_right = tk.Frame(root)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    canvas = FigureCanvasTkAgg(fig, master=frame_right)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    toolbar = NavigationToolbar2Tk(canvas, frame_right)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    def simulate():
        global contributions
        formule = entry_formula.get()
        densite = float(entry_density.get())
        energie = float(entry_energy.get())
        resolution = float(entry_resolution.get())
        source = SourceRX(energie=energie)
        couche = Couche(formule=formule, densite=densite)
        echantillon = Echantillon(couches=[couche])
        modele = model_combo.get() if var_tool_det.get() else None
        detecteur = Detecteur(resolution_fixe=resolution, modele=modele)

        df, contributions = simuler_spectre_xrf_massif(source, echantillon,
                                                       detecteur)
        if var_parametric.get() and var_norm.get():
            df['Intensite'] /= df['Intensite'].max()
        if var_parametric.get() and var_norm.get():
            df['Intensite'] /= df['Intensite'].max()

        if not var_parametric.get():
            ax.clear()
            spectra_superposes.clear()

            # Affichage des contributions uniquement si Parametric study est
            # désactivé
            for i, (element, data) in enumerate(contributions.items()):
                ax.plot(df['Energie_keV'], data,
                        label=f"{element} contribution", linewidth=1.5)

            ax.clear()
            spectra_superposes.clear()

        nom = simpledialog.askstring("Spectrum label",
                                     "Enter a name for this spectrum:") if \
            var_parametric.get() else "XRF Spectra"

        if not spectra_superposes:
            # Afficher les contributions uniquement si Parametric study est
            # désactivée
            if not var_parametric.get():
                for i, (element, data) in enumerate(contributions.items()):
                    ax.plot(df['Energie_keV'], data,
                            label=f"{element} contribution", linewidth=1.5)

        ax.plot(df['Energie_keV'], df['Intensite'], label=nom, linewidth=2.5,
                alpha=0.5)
        spectra_superposes.append(df)
        ax.set_xlabel("Energy (keV)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("Simulated XRF Spectrum")
        ax.grid(True)
        ax.legend()
        canvas.draw()

    def save_spectrum(normalise=False):
        if not spectra_superposes:
            # Afficher les contributions uniquement si Parametric study est
            # désactivée
            if not var_parametric.get():
                for i, (element, data) in enumerate(contributions.items()):
                    ax.plot(df['Energie_keV'], data,
                            label=f"{element} contribution", linewidth=1.5)
            messagebox.showwarning("Warning", "No spectrum to save.")
            return

        dossier = filedialog.askdirectory(title="Select folder to save")
        if not dossier:
            return

        nom = simpledialog.askstring("Filename",
                                     "Enter base filename (without extension):")
        if not nom:
            return

        image_path = os.path.join(dossier, nom + ".jpeg")
        data_path = os.path.join(dossier, nom + ".txt")
        superposed_path = os.path.join(dossier, nom + "_superposed.txt")
        contrib_path = os.path.join(dossier, nom + "_contributions.txt")

        fig.savefig(image_path, dpi=600)

        df = spectra_superposes[-1]
        df.to_csv(data_path, sep="\t", index=False,
                  header=["Energy (keV)", "XRF intensity"])

        if len(spectra_superposes) > 1:
            all_df = pd.DataFrame(
                {'Energy (keV)': spectra_superposes[0]['Energie_keV']})
            for i, df_i in enumerate(spectra_superposes):
                label = f"Spectrum_{i + 1}"
                intensite = df_i['Intensite']
                if var_norm.get() or normalise:
                    intensite = intensite / intensite.max()
                all_df[label] = intensite
                intensite = df_i['Intensite']
                if var_norm.get():
                    intensite = intensite / intensite.max()
                all_df[label] = intensite
                label = f"Spectrum_{i + 1}"
                all_df[label] = df_i['Intensite']
            all_df.to_csv(superposed_path, sep="\t", index=False)

        if 'contributions' in globals():
            contrib_df = pd.DataFrame({'Energy (keV)': df['Energie_keV']})
            for element, data in contributions.items():
                contrib_df[element] = data
            contrib_df.to_csv(contrib_path, sep="\t", index=False)

        messagebox.showinfo("Saved", f"Saved:\n- {image_path}\n- {data_path}\n"
                                     f"{'- ' + superposed_path if len(spectra_superposes) > 1 else ''}\n"
                                     f"- {contrib_path}")

    def reset_interface():
        entry_formula.delete(0, tk.END)
        entry_formula.insert(0, "MoS2")
        entry_density.delete(0, tk.END)
        entry_density.insert(0, "5.06")
        entry_energy.delete(0, tk.END)
        entry_energy.insert(0, "20.0")
        entry_resolution.delete(0, tk.END)
        entry_resolution.insert(0, "120")
        var_tool_det.set(False)
        var_parametric.set(False)
        update_composition()
        ax.clear()
        canvas.draw()
        spectra_superposes.clear()

    tk.Button(frame_left, text="Simulate", command=simulate).pack(pady=10)
    tk.Button(frame_left, text="Save spectrum", command=save_spectrum).pack(
        pady=10)
    tk.Button(frame_left, text="Save (normalized)",
              command=lambda: save_spectrum(normalise=True)).pack(pady=5)
    tk.Button(frame_left, text="Reset", command=reset_interface).pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    lancer_interface()
